import io
import json
import zipfile
from loguru import logger
from typing import Any, Optional
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert

from .base import BaseCrawler
from ..db.postgres import get_session
from ..schemas.openfda import FDARecord
from ..models.fda_records import FDARecordsModel


class OpenFDACrawler(BaseCrawler):
    @staticmethod
    def parse_response_as_pydantic(records: dict[str, Any]) -> list[FDARecord]:
        results = []
        for record in records:
            if not isinstance(record, dict):
                continue

            try:
                record = FDARecord(**record)
                results.append(record)
            except ValidationError as e:
                logger.exception(e)
                logger.warning(f"validation error occurred with record: {record}")

        return results

    @staticmethod
    def insert_records_to_database(records: list[FDARecord]):
        batch_size = 10_000

        for i in range(0, len(records), batch_size):
            sub_records = records[i : i + batch_size]
            stmt = insert(FDARecordsModel.__table__).values(
                [record.model_dump() for record in sub_records]
            )
            stmt = stmt.on_conflict_do_nothing(index_elements=["k_number"])

            with get_session() as session:
                session.execute(stmt)

            logger.info(f"inserted {len(sub_records)} records. {i}, {i + batch_size}")

    def retrieve_records_from_openfda(self) -> Optional[list[dict[str, Any]]]:
        url = "https://download.open.fda.gov/device/510k/device-510k-0001-of-0001.json.zip"
        response = self.call_api(url=url)

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            name_list = zip_ref.namelist()
            if len(name_list) == 0:
                return

            json_filename = name_list[0]
            with zip_ref.open(json_filename) as json_file:
                data = json.load(json_file)

        if not isinstance(data, dict):
            return

        data = data.get("results", [])
        return data

    def crawl(self):
        records = self.retrieve_records_from_openfda()
        if not records:
            return

        records = self.parse_response_as_pydantic(records=records)
        self.insert_records_to_database(records=records)
