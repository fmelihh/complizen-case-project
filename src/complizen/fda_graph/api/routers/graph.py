from fastapi import APIRouter

from ...services.graph import GraphService
from ...schemas.graph import GraphResponse

graph_router = APIRouter()


@graph_router.get("/device-dag")
async def retrieve_device_dag(k_number: str, depth: int = 5) -> GraphResponse:
    result = await GraphService.build_graph(k_number=k_number, depth=depth)
    return result
