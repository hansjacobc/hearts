import secrets

from redis.asyncio import Redis
from src.schemas import CreatePlayerRequest, CreatePlayerResponse


async def handle_create_player(request: CreatePlayerRequest, redis: Redis):
    nickname = request.nickname

    # nx=True only sets if key doesn't exist
    is_unique = await redis.set(
        f"nickname:{nickname}", "__reserved__", nx=True, ex=3600
    )
    if not is_unique:
        raise ValueError("Nickname already taken")

    player_id = secrets.token_hex(3)

    pipe = redis.pipeline()
    await pipe.hset(f"player:{player_id}", mapping={"nickname": nickname})
    await pipe.expire(f"player:{player_id}", 3600)

    # overwrite the reservation with the real player_id
    await pipe.set(f"nickname:{nickname}", player_id, ex=3600)
    await pipe.execute()

    return CreatePlayerResponse(nickname=nickname, player_id=player_id)
