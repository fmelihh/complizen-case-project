from typing import Any
import sqlalchemy as sa
from sqlalchemy.inspection import inspect

from ..db.postgres import get_session
from ..db.redis_cache import redis_cache
from ..schemas.graph import GraphResponse
from ..models.fda_records import FDARecordsModel


class GraphService:
    @staticmethod
    async def _retrieve_dag_list(k_number: str, depth: int = 5) -> list[list[str]]:
        query = f"""
            WITH RECURSIVE device_graph AS (
                SELECT
                    fr.k_number AS source_k_number,
                    pred AS target_k_number,
                    1 as depth
                FROM
                    fda_records fr,
                    jsonb_array_elements_text(fr.predicate_devices) AS pred
                WHERE k_number = '{k_number}' AND k_number != ANY(ARRAY[pred])

                UNION ALL

                SELECT
                    fr.k_number AS source_k_number,
                    pred AS target_k_number,
                    depth + 1
                FROM
                    device_graph dg JOIN fda_records fr ON fr.k_number = dg.target_k_number,
                    jsonb_array_elements_text(fr.predicate_devices) AS pred
                WHERE
                   depth <= {depth}
            )
            SELECT f.source_k_number, f.target_k_number FROM (
                SELECT DISTINCT * FROM device_graph ORDER BY depth
            ) f
        """

        with get_session() as session:
            result = session.execute(sa.text(query))
            result = result.fetchall()

        return result

    @staticmethod
    async def _retrieve_device_hashmap(
        dag_list: list[str],
    ) -> dict[str, dict[str, Any]]:
        devices = dict()
        missing_nodes = []

        for dag in dag_list:
            for node in dag:
                device = await redis_cache.get(node)
                if device:
                    devices[device["k_number"]] = device
                else:
                    missing_nodes.append(node)

        missing_nodes = list(set(missing_nodes))
        if len(missing_nodes) == 0:
            return devices

        with get_session() as session:
            db_devices = (
                session.query(FDARecordsModel)
                .filter(FDARecordsModel.k_number.in_(missing_nodes))
                .all()
            )
            for db_device in db_devices:
                db_device = {
                    c.key: getattr(db_device, c.key)
                    for c in inspect(db_device).mapper.column_attrs
                }
                devices[db_device["k_number"]] = db_device
                await redis_cache.set(db_device["k_number"], db_device)

        return devices

    @staticmethod
    async def build_graph(k_number: str, depth: int = 5) -> GraphResponse:
        dag_list = await GraphService._retrieve_dag_list(k_number=k_number, depth=depth)
        device_hashmap = await GraphService._retrieve_device_hashmap(dag_list=dag_list)

        return GraphResponse(
            dag_list=dag_list,
            device_hashmap=device_hashmap,
        )
