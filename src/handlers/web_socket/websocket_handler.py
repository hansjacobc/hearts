from typing import Awaitable, Callable

from redis.asyncio import Redis
from src.handlers.web_socket.connections import get_room_lock, send_to_player
from src.handlers.web_socket.get_trick_loser import handle_get_trick_loser
from src.handlers.web_socket.handle_pass_cards import handle_pass_cards
from src.handlers.web_socket.handle_play_card import handle_play_card

ActionHandler = Callable[[str, str, dict, Redis], Awaitable[None]]

ACTION_HANDLERS: dict[str, ActionHandler] = {
    "play_card": handle_play_card,
    "get_trick_loser": handle_get_trick_loser,
    "pass_cards": handle_pass_cards,
    # "leave_room": handle_leave_room,
}


async def handle_websocket_action(
    room_id: str, player_id: str, message: dict, redis: Redis
) -> None:
    action = message.get("type")
    handler = ACTION_HANDLERS.get(action)

    if handler is None:
        await send_to_player(
            room_id,
            player_id,
            {
                "type": "error",
                "message": f"unknown action type: {action}",
            },
        )
        return

    async with get_room_lock(room_id):
        await handler(room_id, player_id, message, redis)
