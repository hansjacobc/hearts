from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from src.db.redis_client import verify_connection
from src.handlers.handle_create_player import handle_create_player
from src.handlers.handle_create_room import handle_create_room
from src.handlers.handle_get_user import handle_get_user
from src.handlers.handle_health import handle_health
from src.schemas import (
    CreatePlayerRequest,
    CreatePlayerResponse,
    CreateRoomRequest,
    CreateRoomResponse,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await verify_connection()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return await handle_health()


@app.get("/players/{player_id}", response_model=CreatePlayerResponse)
async def get_user(player_id: str):
    return await handle_get_user(player_id)


@app.post("/players", response_model=CreatePlayerResponse)
async def create_player(request: CreatePlayerRequest):
    return await handle_create_player(request)


@app.post("/rooms", response_model=CreateRoomResponse)
async def create_room(request: CreateRoomRequest):
    return await handle_create_room(request)
