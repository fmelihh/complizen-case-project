import datetime
from loguru import logger
from typing import Optional, Any

import pendulum.parsing
from pydantic import BaseModel, Field, field_validator


class OpenFDA(BaseModel):
    registration_number: Optional[list[str]] = Field(default=None)
    fei_number: Optional[list[str]] = Field(default=None)
    medical_specialty_description: Optional[str] = Field(default=None)
    regulation_number: Optional[str] = Field(default=None)
    device_class: Optional[str] = Field(default=None)


class FDARecord(BaseModel):
    k_number: str

    third_party_flag: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    advisory_committee_description: Optional[str] = Field(default=None)
    address_1: Optional[str] = Field(default=None)
    address_2: Optional[str] = Field(default=None)
    statement_or_summary: Optional[str] = Field(default=None)
    product_code: Optional[str] = Field(default=None)
    openfda: Optional[OpenFDA] = Field(default=None)
    zip_code: Optional[str] = Field(default=None)
    applicant: Optional[str] = Field(default=None)
    decision_date: Optional[str | datetime.datetime] = Field(default=None)
    decision_code: Optional[str] = Field(default=None)
    country_code: Optional[str] = Field(default=None)
    device_name: Optional[str] = Field(default=None)
    advisory_committee: Optional[str] = Field(default=None)
    contact: Optional[str] = Field(default=None)
    expedited_review_flag: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)
    date_received: Optional[str | datetime.datetime] = Field(default=None)
    review_advisory_committee: Optional[str] = Field(default=None)
    postal_code: Optional[str] = Field(default=None)
    decision_description: Optional[str] = Field(default=None)
    clearance_type: Optional[str] = Field(default=None)

    @field_validator("date_received", "decision_date")
    @classmethod
    def validate_date_records(
        cls, v: Optional[str | datetime.datetime]
    ) -> Optional[datetime.datetime]:
        try:
            v = pendulum.parse(v)
            v = datetime.datetime(
                year=v.year,
                month=v.month,
                day=v.day,
                hour=v.hour,
                minute=v.minute,
                second=v.second,
            )
            return v
        except pendulum.parsing.ParserError:
            logger.exception(f"An error occurred while parsing the date: {v}")
            return None

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        record = super().model_dump(*args, **kwargs)
        openfda_column = record.pop("openfda")
        return {**record, **openfda_column}


__all__ = ["FDARecord"]
