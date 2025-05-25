import tqdm
import lxml
import lxml.etree
from io import BytesIO
from typing import Generator, Optional

from .base import BaseCrawler
from ..db.postgres import get_session
from ..db.minio import MinioFileStorage
from ..models.fda_records import FDARecordsModel


class Db510kCrawler(BaseCrawler):
    DEFAULT_BUCKET_NAME = "fda-summary"
    DEFAULT_FILE_NAME_FORMAT = "{k_number}-summary.pdf"

    def __init__(self):
        self._minio_file_storage = None

    @property
    def minio_file_storage(self):
        if self._minio_file_storage is None:
            self._minio_file_storage = MinioFileStorage()
        return self._minio_file_storage

    def retrieve_k_numbers_without_predicate(
        self,
    ) -> Generator[list[FDARecordsModel], None, None]:
        page = 1
        page_size = 50

        while 1:
            offset = (page - 1) * page_size
            with get_session() as session:
                results = (
                    session.query(FDARecordsModel)
                    .filter(FDARecordsModel.predicate_device.is_(None))
                    .limit(page_size)
                    .offset(offset)
                    .all()
                )
                if not results:
                    break

                k_numbers = [
                    result.k_number
                    for result in tqdm.tqdm(
                        results,
                        total=len(results),
                        desc=f"Retrieving k numbers records page: {page}, total: {len(results)}",
                    )
                    if not self.check_summary_is_exist(k_number=result.k_number)
                ]

            for k_number in k_numbers:
                yield k_number

            page += 1

    def extract_summary(self, k_number: str) -> Optional[str]:
        url = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={k_number}"
        response = self.call_api(url=url)
        dom = lxml.etree.HTML(response.text)
        result = dom.xpath('//th[text() = "Summary"]/../td/a')
        if len(result) == 0:
            return

        pdf_link = result[0].get("href")
        return pdf_link

    def check_summary_is_exist(self, k_number: str) -> bool:
        return self.minio_file_storage.is_exist(
            bucket_name=self.DEFAULT_BUCKET_NAME,
            file_name=self.DEFAULT_FILE_NAME_FORMAT.format(k_number=k_number),
        )

    def parse_pdf_summary_to_minio(self, k_number: str, pdf_link: str):
        response = self.call_api(url=pdf_link)
        pdf_bytes = BytesIO(response.content)
        self.minio_file_storage.upload_file(
            bucket_name=self.DEFAULT_BUCKET_NAME,
            filename=self.DEFAULT_FILE_NAME_FORMAT.format(k_number=k_number),
            file_bytes=pdf_bytes,
            file_content_type="application/pdf",
        )

    def crawl(self):
        for k_number in self.retrieve_k_numbers_without_predicate():
            pdf_link = self.extract_summary(k_number=k_number)
            if not pdf_link:
                continue

            self.parse_pdf_summary_to_minio(k_number=k_number, pdf_link=pdf_link)
