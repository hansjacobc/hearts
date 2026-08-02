from redis.asyncio import Redis
from src.handlers.helpers import deserialize_state
from src.handlers.web_socket.connections import broadcast, send_to_player
from src.rooms import GamePhase


# pylint: disable=too-many-locals
async def handle_pass_cards(room_id: str, player_id: str, message: dict, redis: Redis):
    current_state = deserialize_state(await redis.hgetall(f"room:{room_id}:state"))

    if current_state["phase"] != GamePhase.PASSING:
        await send_to_player(
            room_id,
            player_id,
            {
                "type": "error",
                "reason": "not_currently_passing",
                "message": "You can't pass right now!",
            },
        )
        return

    game_number = current_state["game_number"]
    if game_number % 3 == 1:
        direction = "LEFT"
    elif game_number % 3 == 2:
        direction = "RIGHT"
    else:
        direction = "KEEP"

    await redis.hset(f"room:{room_id}:state", mapping={"direction": direction})

    if direction != "KEEP":
        cards_to_pass = message.get("cards_to_pass")
        if not cards_to_pass or len(cards_to_pass) != 3:
            await send_to_player(
                room_id,
                player_id,
                {
                    "type": "error",
                    "reason": "invalid_pass",
                    "message": "You must pass exactly 3 cards.",
                },
            )
            return

        player_hand = await redis.smembers(f"room:{room_id}:hand:{player_id}")
        if not all(c in player_hand for c in cards_to_pass):
            await send_to_player(
                room_id,
                player_id,
                {
                    "type": "error",
                    "reason": "invalid_pass",
                    "message": "You can only pass cards you hold.",
                },
            )
            return

        turn_order = await redis.lrange(f"room:{room_id}:turn_order", 0, -1)
        current_index = turn_order.index(player_id)
        i = -1 if direction == "LEFT" else 1
        pass_to_index = (current_index + i) % len(turn_order)
        player_id_pass_to = turn_order[pass_to_index]

        await redis.srem(f"room:{room_id}:hand:{player_id}", *cards_to_pass)
        await redis.sadd(f"room:{room_id}:hand:{player_id_pass_to}", *cards_to_pass)

        await send_to_player(
            room_id,
            player_id_pass_to,
            {
                "type": "cards_received",
                "cards": cards_to_pass,
            },
        )

    await redis.sadd(f"room:{room_id}:passed_players", player_id)
    passed_count = await redis.scard(f"room:{room_id}:passed_players")

    await broadcast(
        room_id,
        {"type": "pass_cards", "player_id": player_id, "message": "done_passing"},
    )

    if passed_count >= current_state["total_players"]:
        await redis.delete(f"room:{room_id}:passed_players")

        starting_player_id = await find_starting_card_holder(
            room_id, current_state["starting_card"], redis
        )

        await redis.hset(
            f"room:{room_id}:state",
            mapping={
                "phase": GamePhase.PLAYING,
                "current_turn_player_id": starting_player_id,
                "turn_number": 1,
                "lead_suit": "OPEN",
                "is_hearts_broken": 0,
            },
        )
        new_state = deserialize_state(await redis.hgetall(f"room:{room_id}:state"))
        await broadcast(
            room_id, {"type": "state", "reason": "info", "state": new_state}
        )


async def find_starting_card_holder(
    room_id: str, starting_card: str, redis: Redis
) -> str:
    player_ids = await redis.smembers(f"room:{room_id}:players")
    for pid in player_ids:
        if await redis.sismember(f"room:{room_id}:hand:{pid}", starting_card):
            return pid
    raise RuntimeError(f"No player holds {starting_card} in room {room_id}")
