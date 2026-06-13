from redis.asyncio import Redis

from src.rooms import RoomStatus
from src.schemas import JoinRoomRequest, JoinRoomResponse


async def handle_join_room(request: JoinRoomRequest, redis: Redis) -> JoinRoomResponse:
    """
    Validate room exists.
    Validate game has not started.
    Validate room is not full.
    Validate player is not already in room.
    Persist updated state.
    """
    room_key = f"room:{request.room_id}"
    players_key = f"{room_key}:players"

    # Validate room exists
    room_exists = await redis.exists(room_key)
    if not room_exists:
        raise ValueError("Room does not exist")

    # Validate game has not started
    room_data = await redis.hgetall(room_key)
    if room_data["status"] != RoomStatus.WAITING:
        raise ValueError("Game already started")
    max_players = int(room_data["max_players"])

    # Validate room is not full
    current_players = await redis.scard(players_key)
    if current_players >= max_players:
        raise ValueError("Room is full")

    # Validate player is not already in room
    already_in_room = await redis.sismember(
        players_key,
        request.player_id,
    )
    if already_in_room:
        raise ValueError("Player already in room")

    await redis.sadd(players_key, request.player_id)

    return JoinRoomResponse(
        room_id=request.room_id,
        player_id=request.player_id,
    )
