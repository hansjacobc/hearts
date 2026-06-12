from redis.asyncio import Redis
from src.schemas import JoinRoomRequest, JoinRoomResponse


async def handle_join_room(request: JoinRoomRequest, redis: Redis) -> JoinRoomResponse:
    """
    Validate room exists.
    Validate room is not full.
    Add player to room.
    Persist updated state.

    Key:

    room:{room_id}:players

    Type:

    SET

    Example:

    room:X7KP:players

    Contents:

    player1
    player2
    player3
    player4

    Benefits:

    No duplicates.
    Fast membership checks.
    Easy player counting.
    """
    pass
