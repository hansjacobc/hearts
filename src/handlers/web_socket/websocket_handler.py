from redis.asyncio import Redis
from src.handlers.web_socket.connections import broadcast, get_room_lock


# TODO: make the handler generic and distribute
#  logic for each action into a different file
async def handle_websocket_action(
    room_id: str, player_id: str, message: dict, redis: Redis
) -> None:
    """
    Generic handler for all websocket action, each message type has its own function
    to handle game flow logic and updating redis keys
    There is a lock per room to ensure no race condition for each active game room.
    """
    async with get_room_lock(room_id):
        action = message.get("type")

        if action == "play_card":
            card = message["card"]
            # validate turn, mutate Redis (lrem hand, advance turn state)...
            await broadcast(
                room_id,
                {
                    "type": "card_played",
                    "player_id": player_id,
                    "card": card,
                },
            )
