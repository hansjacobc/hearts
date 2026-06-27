# pylint: disable=duplicate-code
import json

from redis.asyncio import Redis
from src.handlers.helpers import deal_hands, find_starting_player
from src.rooms import ONE_HOUR_TTL, GamePhase


# pylint: disable=unused-argument
async def handle_shuffle_and_deal(
    room_id: str, player_id: str, message: dict, redis: Redis
):
    player_ids = list(await redis.smembers(f"room:{room_id}:players"))
    num_players = len(player_ids)

    # Deal hands
    hands, left_over_deck = deal_hands(num_players, player_ids)

    # Find starting player
    starting_player_id, starting_card = find_starting_player(hands, left_over_deck)

    # Persist updated state
    pipe = redis.pipeline()
    for p_id, hand in hands.items():
        await pipe.sadd(f"room:{room_id}:hand:{p_id}", *hand)
        await pipe.expire(f"room:{room_id}:hand:{p_id}", ONE_HOUR_TTL)

    # remaining cards in the deck
    await pipe.rpush(f"room:{room_id}:deck", *left_over_deck)
    await pipe.expire(f"room:{room_id}:deck", ONE_HOUR_TTL)

    # set game state
    await pipe.hset(
        f"room:{room_id}:state",
        mapping={
            "current_turn_player_id": starting_player_id,
            "turn_number": 1,
            "round_number": 1,
            "card_pile": json.dumps([]),
            "is_hearts_broken": 0,
            "phase": GamePhase.PASSING,
            "starting_card": starting_card,
            "lead_suit": "clubs",
        },
    )
