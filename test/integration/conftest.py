# pylint: disable=W0621
import pytest
import pytest_asyncio
from app.dependencies import get_redis
from app.main import app
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis


@pytest_asyncio.fixture
async def redis_client():
    redis = Redis(
        host="localhost",
        port=6379,
        db=15,
        decode_responses=True,
    )

    await redis.flushdb()

    yield redis

    await redis.flushdb()
    await redis.aclose()


@pytest.fixture
def test_app() -> FastAPI:
    return app


@pytest_asyncio.fixture
async def app_with_redis(test_app, redis_client):
    test_app.dependency_overrides[get_redis] = lambda: redis_client

    yield test_app

    test_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app_with_redis):
    transport = ASGITransport(app=app_with_redis)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client
