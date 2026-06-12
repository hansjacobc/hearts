from redis.asyncio import Redis
from src.schemas import JoinRoomRequest, JoinRoomResponse


async def handle_join_room(request: JoinRoomRequest, redis: Redis) -> JoinRoomResponse:
    """
    Validate room exists.
    Validate room is not full.
    Add player to room.
    Persist updated state.
    """
    pass
