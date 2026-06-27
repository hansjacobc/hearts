from redis.asyncio import Redis
from src.handlers.web_socket.connections import broadcast
from src.handlers.web_socket.helpers import deserialize_state


# pylint: disable=unused-argument
async def handle_get_state(room_id: str, player_id: str, message: dict, redis: Redis):
    state = deserialize_state(await redis.hgetall(f"room:{room_id}:state"))
    await broadcast(
        room_id,
        {
            "type": "state",
            "reason": "info",
            "state": state,
        },
    )
