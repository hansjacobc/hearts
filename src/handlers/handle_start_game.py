import json
import random

from redis.asyncio import Redis
from src.handlers.helpers import deal_hands, find_starting_player
from src.rooms import ONE_HOUR_TTL, GamePhase, RoomStatus
from src.schemas import StartGameRequest, StartGameResponse


async def handle_start_game(
    room_id: str, request: StartGameRequest, redis: Redis
) -> StartGameResponse:
    # Validate room exists
    room_data = await redis.hgetall(f"room:{room_id}")
    if not room_data:
        raise ValueError("Room does not exist")

    # Validate caller is host
    if request.player_id != room_data["host_player_id"]:
        raise ValueError("Only the host can start the game")

    # Validate game has not started
    if room_data["status"] != RoomStatus.WAITING:
        raise ValueError("Game already started")

    # Verify player count
    player_ids = list(await redis.smembers(f"room:{room_id}:players"))
    num_players = len(player_ids)
    max_players = int(room_data["max_players"])
    if num_players < 3:
        raise ValueError("Not enough players to start")

    if num_players > max_players or num_players > 8:
        raise ValueError("Too many players to start")

    # Deal hands
    hands, left_over_deck = deal_hands(num_players, player_ids)

    # Find starting player
    starting_player_id, starting_card = find_starting_player(hands, left_over_deck)

    random.shuffle(player_ids)
    turn_order = player_ids

    # Persist updated state and set initial scoes
    pipe = redis.pipeline()
    for player_id, hand in hands.items():
        # hands
        await pipe.sadd(f"room:{room_id}:hand:{player_id}", *hand)
        await pipe.expire(f"room:{room_id}:hand:{player_id}", ONE_HOUR_TTL)

        # scores
        await pipe.hset(
            f"room:{room_id}:score:{player_id}",
            mapping={
                "round_score": 0,
                "game_score": 0,
            },
        )

    # remaining cards in the deck
    await pipe.rpush(f"room:{room_id}:deck", *left_over_deck)
    await pipe.expire(f"room:{room_id}:deck", ONE_HOUR_TTL)

    # establish turn order
    await pipe.rpush(f"room:{room_id}:turn_order", *turn_order)
    await pipe.expire(f"room:{room_id}:turn_order", ONE_HOUR_TTL)

    # set initial scores

    # set game state
    await pipe.hset(
        f"room:{room_id}:state",
        mapping={
            "current_turn_player_id": starting_player_id,
            "turn_number": 1,
            "round_number": 1,
            "game_number": 1,
            "card_pile": json.dumps([]),
            "is_hearts_broken": 0,
            "phase": GamePhase.PASSING,
            "last_action": "",
            "last_action_player_id": "",
            "starting_card": starting_card,
            "lead_suit": "clubs",
            "total_players": num_players,
        },
    )

    await pipe.hset(
        f"room:{room_id}",
        mapping={
            "status": RoomStatus.IN_PROGRESS,
        },
    )
    await pipe.expire(f"room:{room_id}", ONE_HOUR_TTL)

    await pipe.execute()

    return StartGameResponse(
        room_id=room_id,
        status=RoomStatus.IN_PROGRESS,
        starting_player_id=starting_player_id,
        turn_order=turn_order,
    )
