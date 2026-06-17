import secrets

from redis.asyncio import Redis
from src.rooms import ONE_HOUR_TTL, RoomStatus
from src.schemas import CreateRoomRequest, CreateRoomResponse


async def handle_create_room(
    request: CreateRoomRequest, redis: Redis
) -> CreateRoomResponse:
    room_id = secrets.token_urlsafe(3).lower()

    room_key = f"room:{room_id}"
    await redis.hset(
        room_key,
        mapping={
            "host_player_id": request.host_player_id,
            "max_players": str(request.num_players),
            "status": RoomStatus.WAITING,
        },
    )
    await redis.expire(room_key, ONE_HOUR_TTL)

    players_key = f"{room_key}:players"
    await redis.sadd(players_key, request.host_player_id)
    await redis.expire(players_key, ONE_HOUR_TTL)

    return CreateRoomResponse(
        room_id=room_id,
        host_player_id=request.host_player_id,
        num_players=request.num_players,
    )
