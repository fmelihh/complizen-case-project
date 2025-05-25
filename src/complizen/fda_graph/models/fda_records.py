from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, DateTime

from ..db.postgres import PostgresBase


class FDARecordsModel(PostgresBase):
    __tablename__ = "fda_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    third_party_flag = Column(String, nullable=True)
    city = Column(String, nullable=True)
    advisory_committee_description = Column(String, nullable=True)
    address_1 = Column(String, nullable=True)
    address_2 = Column(String, nullable=True)
    statement_or_summary = Column(String, nullable=True)
    product_code = Column(String, nullable=True)
    openfda = Column(JSONB, nullable=True)
    zip_code = Column(String, nullable=True)
    applicant = Column(String, nullable=True)
    decision_date = Column(DateTime, nullable=True)
    decision_code = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    device_name = Column(String, nullable=True)
    advisory_committee = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    expedited_review_flag = Column(String, nullable=True)
    k_number = Column(String, unique=True, nullable=False)
    predicate_devices = Column(JSONB, nullable=True)
    state = Column(String, nullable=True)
    date_received = Column(DateTime, nullable=True)
    review_advisory_committee = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    decision_description = Column(String, nullable=True)
    clearance_type = Column(String, nullable=True)

    registration_number = Column(JSONB, nullable=True)
    fei_number = Column(JSONB, nullable=True)
    medical_specialty_description = Column(String, nullable=True)
    regulation_number = Column(String, nullable=True)
    device_class = Column(String, nullable=True)
