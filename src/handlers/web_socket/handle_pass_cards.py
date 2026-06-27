from redis.asyncio import Redis
from src.handlers.web_socket.connections import broadcast
from src.handlers.helpers import deserialize_state
from src.rooms import GamePhase


async def handle_pass_cards(room_id: str, player_id: str, message: dict, redis: Redis):
    """
    Determines passing direction from current game number and has
    each player pass 3 cards. Assumes that cards are already dealt to each player
    """

    current_state = deserialize_state(await redis.hgetall(f"room:{room_id}:state"))

    if current_state != GamePhase.PASSING:
        await broadcast(
            room_id,
            {
                "type": "error",
                "reason": "not_currently_passing",
                "message": "You can't pass right now!",
            },
        )

    game_number = current_state["game_number"]
    if game_number % 3 == 1:
        direction = "LEFT"
    elif game_number % 3 == 2:
        direction = "RIGHT"
    else:
        direction = "KEEP"

    # early exit for keep since we don't need to deal with passing cards
    if direction == "KEEP":
        await redis.hset(f"room:{room_id}:state", "phase", GamePhase.PLAYING)
        await broadcast(
            room_id,
            {"type": "pass_cards", "player_id": player_id, "message": "done_passing"},
        )

    turn_order = await redis.lrange(f"room:{room_id}:turn_order", 0, -1)
    current_index = turn_order.index(player_id)
    i = -1 if direction == "LEFT" else 1
    pass_to_index = (current_index + i) % len(turn_order)
    player_id_pass_to = turn_order[pass_to_index]
    cards_to_pass = message.get("cards_to_pass")

    # remove cards from current players hand
    await redis.srem(f"room:{room_id}:hand:{player_id}", *cards_to_pass)

    # add cards to other players hand
    await redis.sadd(f"room:{room_id}:hand:{player_id_pass_to}", *cards_to_pass)

    # update game state
    await redis.hset(f"room:{room_id}:state", "phase", GamePhase.PLAYING)
    await broadcast(
        room_id,
        {"type": "pass_cards", "player_id": player_id, "message": "done_passing"},
    )
