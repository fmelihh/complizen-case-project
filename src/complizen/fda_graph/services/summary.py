import re
import time
import pytesseract
from loguru import logger
from pdf2image import convert_from_bytes

from ..db.postgres import get_session
from ..db.minio import MinioFileStorage
from ..models.fda_records import FDARecordsModel


class SummaryParserService:
    def __init__(self):
        self._minio = None

    @property
    def minio(self) -> MinioFileStorage:
        if self._minio is None:
            self._minio = MinioFileStorage()
        return self._minio

    @staticmethod
    def _parse_pdf(pdf: bytes) -> str:
        images = convert_from_bytes(pdf)
        extracted_text = "\n".join(
            [pytesseract.image_to_string(image) for image in images]
        )
        return extracted_text

    @staticmethod
    def _extract_k_number(pdf: str) -> list[str]:
        k_number_pattern = r"\bK\d{6}\b"
        k_numbers = re.findall(k_number_pattern, pdf)
        return k_numbers

    @staticmethod
    def _clear_exists_k_number(
        file_name: str, k_numbers: list[str]
    ) -> tuple[str, list[str]]:
        exists_k_number = file_name.split("-")[0].strip()
        if exists_k_number in k_numbers:
            k_numbers.pop(k_numbers.index(exists_k_number))
        return exists_k_number, k_numbers

    @staticmethod
    def update_the_record(exists_k_number: str, k_numbers: list[str]):
        with get_session() as session:
            session.query(FDARecordsModel).filter(
                FDARecordsModel.k_number == exists_k_number
            ).update({FDARecordsModel.predicate_devices: k_numbers})

    def parse(self):
        bucket_name = "fda-summary"
        for file_name in self.minio.list_file_keys(bucket_name=bucket_name):
            try:
                pdf_bytes = self.minio.get_file(
                    bucket_name=bucket_name, file_name=file_name
                )
                pdf_string = self._parse_pdf(pdf=pdf_bytes)
                k_numbers = self._extract_k_number(pdf=pdf_string)
                exists_k_number, k_numbers = self._clear_exists_k_number(
                    file_name=file_name, k_numbers=k_numbers
                )
                if len(k_numbers) == 0:
                    raise ValueError(f"Cannot be parsed k number")

                self.update_the_record(
                    exists_k_number=exists_k_number, k_numbers=k_numbers
                )
                logger.info(
                    f"Successfully parsed k number, {exists_k_number}, k_numbers: {k_numbers}"
                )
            except Exception as e:
                logger.exception(f"Failed to parse {file_name}: {e}")
                time.sleep(1.5)
