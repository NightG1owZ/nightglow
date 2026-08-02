from typing import Optional

import redis.asyncio as redis

from app.config import settings

redis_client: Optional[redis.Redis] = None

async def init_redis():
    global redis_client
    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()