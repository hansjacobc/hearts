import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    redis = Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )

    try:
        await redis.ping()
        logger.info("Successfully connected to Redis")
    except Exception:
        logger.exception("Failed to connect to Redis")
        raise

    app.state.redis = redis

    yield

    await redis.close()
