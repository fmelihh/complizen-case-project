import os
import json
from typing import Any
from redis.asyncio import Redis as AsyncRedis

from ..utils.json_formatter import DateTimeEncoder, datetime_parser


class AioRedisCache:
    def __init__(self) -> None:
        self.client = AsyncRedis(
            db=9,
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True,
            socket_timeout=15,
        )

    async def get(self, key: str) -> dict[str, Any]:
        value = await self.client.get(key)
        if value is None:
            return

        return json.loads(value, object_hook=datetime_parser)

    async def set(self, key: str, value: dict[str, Any], ttl: int = 60 * 60 * 3):
        if value is None:
            raise ValueError(f"{key} cannot be None in AioRedisCache")

        await self.client.set(
            key,
            json.dumps(value, ensure_ascii=False, cls=DateTimeEncoder).encode("utf-8"),
            ex=ttl,
        )


redis_cache = AioRedisCache()
