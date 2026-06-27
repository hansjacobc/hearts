from redis.asyncio import Redis

from src.handlers.helpers import deserialize_state


# pylint: disable=unused-argument
async def handle_shuffle_and_deal(room_id: str, player_id: str, message: dict, redis: Redis):
    current_state = deserialize_state(await redis.hgetall(f"room:{room_id}:state"))