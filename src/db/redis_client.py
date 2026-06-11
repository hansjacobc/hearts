import os

from redis.asyncio import Redis

redis_client = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)


async def verify_connection():
    await redis_client.ping()
