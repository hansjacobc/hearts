from app.dependencies import get_redis
from app.lifespan import lifespan
from fastapi import Depends, FastAPI
from redis.asyncio import Redis
from src.handlers.handle_create_player import handle_create_player
from src.handlers.handle_create_room import handle_create_room
from src.handlers.handle_get_user import handle_get_user
from src.handlers.handle_health import handle_health
from src.handlers.handle_join_room import handle_join_room
from src.handlers.handle_start_game import handle_start_game
from src.schemas import (
    CreatePlayerRequest,
    CreatePlayerResponse,
    CreateRoomRequest,
    CreateRoomResponse,
    JoinRoomRequest,
    JoinRoomResponse,
    StartGameRequest,
    StartGameResponse,
)

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return await handle_health()


@app.get("/players/{player_id}", response_model=CreatePlayerResponse)
async def get_user(player_id: str):
    return await handle_get_user(player_id)


@app.post("/players", response_model=CreatePlayerResponse)
async def create_player(request: CreatePlayerRequest, redis: Redis = Depends(get_redis)):
    return await handle_create_player(request, redis)


@app.post("/rooms", response_model=CreateRoomResponse)
async def create_room(request: CreateRoomRequest, redis: Redis = Depends(get_redis)):
    return await handle_create_room(request, redis)


@app.post("/rooms/{room_id}/join", response_model=JoinRoomResponse)
async def join_room(
    room_id: str, request: JoinRoomRequest, redis: Redis = Depends(get_redis)
):
    return await handle_join_room(room_id, request, redis)


@app.post("/rooms/{room_id}/start", response_model=StartGameResponse)
async def start_game(
    room_id: str, request: StartGameRequest, redis: Redis = Depends(get_redis)
):
    return await handle_start_game(room_id, request, redis)
