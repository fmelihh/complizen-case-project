from typing import Any
from pydantic import BaseModel


class GraphResponse(BaseModel):
    dag_list: list[list[str]]
    device_hashmap: dict[str, dict[str, Any]]
