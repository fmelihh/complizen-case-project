import os
from loguru import logger
from typing import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base


POSTGRESQL_URL = os.getenv(
    "POSTGRESQL_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(
    POSTGRESQL_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

PostgresBase = declarative_base()


@contextmanager
def get_session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.exception(f"Session rollback because of exception: {e}")
        db.rollback()
        raise
    finally:
        db.close()


__all__ = ["get_session", "PostgresBase", "engine"]
