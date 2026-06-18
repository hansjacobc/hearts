import json
import random

from redis.asyncio import Redis
from src.rooms import ONE_HOUR_TTL, GamePhase, RoomStatus
from src.schemas import StartGameRequest, StartGameResponse

SUITS = ["spades", "hearts", "diamonds", "clubs"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def deal_hands(num_players: int, player_ids: list[str]):
    """Deal out even sized hands of all cards and keep track of left over cards"""

    deck = [f"{rank}_{suit}" for suit in SUITS for rank in RANKS]
    random.shuffle(deck)

    hand_size = 52 // num_players
    hands = {}
    for player_id in player_ids:
        hands[player_id] = deck[:hand_size]
        deck = deck[hand_size:]
    return hands, deck


def find_starting_player(
    hands: dict[str, list[str]], left_over_deck: list[str]
) -> tuple[str, str]:
    """
    Want to find the player with 2 of clubs since they start.
    Also have to account for the fact that the 2 of clubs can be in the leftover pile.
    """
    starting_player_id = ""
    starting_card = "2_clubs"
    for i in range(3, 7):
        if starting_card in left_over_deck:
            starting_card = f"{i}_clubs"
    for player_id, hand in hands.items():
        if starting_card in hand:
            starting_player_id = player_id
    return starting_player_id, starting_card


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

    # Persist updated state
    pipe = redis.pipeline()
    for player_id, hand in hands.items():
        await pipe.rpush(f"room:{room_id}:hand:{player_id}", *hand)
        await pipe.expire(f"room:{room_id}:hand:{player_id}", ONE_HOUR_TTL)

    # remaining cards in the deck
    await pipe.rpush(f"room:{room_id}:deck", *left_over_deck)
    await pipe.expire(f"room:{room_id}:deck", ONE_HOUR_TTL)

    # establish turn order
    await pipe.rpush(f"room:{room_id}:turn_order", *turn_order)
    await pipe.expire(f"room:{room_id}:turn_order", ONE_HOUR_TTL)

    # set game state
    await pipe.hset(
        f"room:{room_id}:state",
        mapping={
            "current_turn_player_id": starting_player_id,
            "turn_number": 1,
            "card_pile": json.dumps([]),
            "is_hearts_broken": 0,
            "phase": GamePhase.PASSING,
            "last_action": "",
            "last_action_player_id": "",
            "round_number": 1,
            "starting_card": starting_card,
            "lead_suit": "clubs",
        },
    )

    await pipe.hset(
        f"room:{room_id}",
        mapping={
            "status": RoomStatus.PLAYING,
        },
    )
    await pipe.expire(f"room:{room_id}", ONE_HOUR_TTL)

    await pipe.execute()

    return StartGameResponse(
        room_id=room_id,
        status=RoomStatus.PLAYING,
        starting_player_id=starting_player_id,
        turn_order=turn_order,
    )
