import secrets

from fastapi import HTTPException
from redis.asyncio import Redis
from src.rooms import TWO_HOUR_TTL
from src.schemas import CreatePlayerRequest, CreatePlayerResponse


async def handle_create_player(request: CreatePlayerRequest, redis: Redis):
    nickname = request.nickname

    # nx=True only sets if key doesn't exist
    is_unique = await redis.set(
        f"nickname:{nickname}", "__reserved__", nx=True, ex=TWO_HOUR_TTL
    )
    if not is_unique:
        raise HTTPException(
            status_code=409,
            detail={"code": "NICKNAME_TAKEN", "message": "Nickname already taken"},
        )

    player_id = secrets.token_hex(3)

    pipe = redis.pipeline()
    await pipe.hset(f"player:{player_id}", mapping={"nickname": nickname})
    await pipe.expire(f"player:{player_id}", TWO_HOUR_TTL)

    # overwrite the reservation with the real player_id
    await pipe.set(f"nickname:{nickname}", player_id, ex=TWO_HOUR_TTL)
    await pipe.execute()

    return CreatePlayerResponse(nickname=nickname, player_id=player_id)
