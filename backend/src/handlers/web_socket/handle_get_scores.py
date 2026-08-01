from redis.asyncio import Redis
from src.handlers.web_socket.connections import broadcast


# pylint: disable=unused-argument
async def handle_get_scores(room_id: str, player_id: str, message: dict, redis: Redis):
    scores = {}
    player_ids = list(await redis.smembers(f"room:{room_id}:players"))
    for p_id in player_ids:
        score = await redis.hgetall(f"room:{room_id}:score:{p_id}")
        scores[p_id] = score
    await broadcast(
        room_id,
        {
            "type": "scores",
            "reason": "info",
            "scores": scores,
        },
    )
