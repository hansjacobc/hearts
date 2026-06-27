from redis.asyncio import Redis


# pylint: disable=unused-argument
async def handle_shuffle_and_deal(room_id: str, player_id: str, message: dict, redis: Redis):
    current_state