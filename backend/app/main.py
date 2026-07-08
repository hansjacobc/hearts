import logging

from app.dependencies import get_redis, get_redis_ws
from app.lifespan import lifespan
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from src.handlers.handle_create_player import handle_create_player
from src.handlers.handle_create_room import handle_create_room
from src.handlers.handle_get_user import handle_get_player
from src.handlers.handle_health import handle_health
from src.handlers.handle_join_room import handle_join_room
from src.handlers.handle_start_game import handle_start_game
from src.handlers.web_socket.connections import (
    broadcast,
    register_web_socket,
    unregister_web_socket,
)
from src.handlers.web_socket.websocket_handler import handle_websocket_action
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

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return await handle_health()


# In-memory registry: which sockets are live for which room.
room_connections: dict[str, dict[str, WebSocket]] = {}


@app.websocket("/ws/{room_id}/{player_id}")
async def game_socket(
    websocket: WebSocket,
    room_id: str,
    player_id: str,
    redis: Redis = Depends(get_redis_ws),
):
    await websocket.accept()
    register_web_socket(room_id, player_id, websocket)

    try:
        while True:
            message = await websocket.receive_json()
            try:
                await handle_websocket_action(room_id, player_id, message, redis)
            except Exception as e:
                logger.exception(
                    "Exception caught handling message:%s\nException: %s",
                    message,
                    e,
                )
                raise
    except WebSocketDisconnect:
        unregister_web_socket(room_id, player_id)
        await broadcast(
            room_id, {"type": "player_disconnected", "player_id": player_id}
        )


@app.get("/players/{player_id}", response_model=CreatePlayerResponse)
async def get_player(player_id: str, redis: Redis = Depends(get_redis)):
    return await handle_get_player(player_id, redis)


@app.post("/players", response_model=CreatePlayerResponse)
async def create_player(
    request: CreatePlayerRequest, redis: Redis = Depends(get_redis)
):
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
