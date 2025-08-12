import redis.asyncio as ioredis
from core.settings import get_settings

redis = None

async def get_redis():
    global redis
    if redis is None:
        settings = get_settings()
        redis = await ioredis.from_url(settings.scheduler_redisdb_url, decode_responses=True)
    return redis
