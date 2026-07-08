from redis.asyncio import Redis
from src.schemas import CreatePlayerResponse


async def handle_get_player(player_id, redis: Redis) -> CreatePlayerResponse:
    player_mapping = redis.hgetall(f"player:{player_id}")
    nickname = player_mapping.get("nickname")
    if not nickname:
        raise ValueError("Player ID does not exist")
    return CreatePlayerResponse(nickname=nickname, player_id=player_id)
