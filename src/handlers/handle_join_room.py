from redis.asyncio import Redis
from src.rooms import RoomStatus
from src.schemas import JoinRoomRequest, JoinRoomResponse


async def handle_join_room(
    room_id: str, request: JoinRoomRequest, redis: Redis
) -> JoinRoomResponse:
    """
    Validate room exists.
    Validate game has not started.
    Validate room is not full.
    Validate player is not already in room.
    Persist updated state.
    """

    # Validate room exists
    room_exists = await redis.exists(f"room:{room_id}")
    if not room_exists:
        raise ValueError("Room does not exist")

    # Validate game has not started
    room_data = await redis.hgetall(f"room:{room_id}")
    if room_data["status"] != RoomStatus.WAITING:
        raise ValueError("Game already started")
    max_players = int(room_data["max_players"])

    # Validate room is not full
    current_players = await redis.scard(f"room:{room_id}:players")
    if current_players >= max_players:
        raise ValueError("Room is full")

    # Validate player is not already in room
    already_in_room = await redis.sismember(
        f"room:{room_id}:players",
        request.player_id,
    )
    if already_in_room:
        raise ValueError("Player already in room")

    await redis.sadd(f"room:{room_id}:players", request.player_id)

    return JoinRoomResponse(
        room_id=room_id,
        player_id=request.player_id,
    )
