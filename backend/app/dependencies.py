from fastapi import Request
from redis.asyncio import Redis
from starlette.websockets import WebSocket


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


def get_redis_ws(websocket: WebSocket) -> Redis:
    return websocket.app.state.redis
