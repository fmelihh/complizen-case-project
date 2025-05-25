import inspect
from loguru import logger
from sqlalchemy import inspect as sqlalchemy_inspect

# noinspection PyUnresolvedReferences
from src.complizen.fda_graph.models import *
from src.complizen.fda_graph.db.postgres import get_session

from src.complizen.fda_graph.db.postgres import PostgresBase, engine


def create_tables():
    with get_session() as session:
        inspector = sqlalchemy_inspect(engine)

        for name, obj in globals().items():
            if not inspect.isclass(obj):
                continue

            if (
                not issubclass(obj, PostgresBase)
                or obj == PostgresBase
                or inspector.has_table(obj.__tablename__)
            ):
                continue

            obj.__table__.create(engine)
            logger.info(f"{name} PostgresBase Table Created.")


if __name__ == "__main__":
    create_tables()
