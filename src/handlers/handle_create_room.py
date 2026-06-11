import secrets

from src.db.redis_client import redis_client
from src.rooms import RoomStatus
from src.schemas import CreateRoomRequest, CreateRoomResponse


# TODO: write test and handle redis dependency injection
async def handle_create_room(request: CreateRoomRequest) -> CreateRoomResponse:
    room_id = secrets.token_urlsafe(3).lower()

    room_key = f"room:{room_id}"
    await redis_client.hset(
        room_key,
        mapping={
            "host_player_id": request.host_player_id,
            "max_players": str(request.num_players),
            "status": RoomStatus.WAITING,
        },
    )
    await redis_client.expire(room_key, 3600)

    players_key = f"{room_key}:players"
    await redis_client.sadd(players_key, request.host_player_id)
    await redis_client.expire(players_key, 3600)

    return CreateRoomResponse(
        room_id=room_id,
        host_player_id=request.host_player_id,
        num_players=request.num_players,
    )
