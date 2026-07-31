from redis.asyncio import Redis
from src.handlers.web_socket.connections import send_to_player


# pylint: disable=unused-argument
async def handle_get_my_hand(room_id: str, player_id: str, message: dict, redis: Redis):
    hand = await redis.smembers(f"room:{room_id}:hand:{player_id}")
    await send_to_player(
        room_id,
        player_id,
        {
            "type": "your_hand",
            "hand": list(hand),
        },
    )
