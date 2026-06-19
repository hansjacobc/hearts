import json

from redis.asyncio import Redis
from src.handlers.web_socket.helpers import deserialize_state
from src.rooms import GamePhase


async def get_next_player(room_id: str, current_player_id: str, redis: Redis) -> str:
    turn_order = await redis.lrange(f"room:{room_id}:turn_order", 0, -1)
    current_index = turn_order.index(current_player_id)
    next_index = (current_index + 1) % len(turn_order)
    return turn_order[next_index]


def get_next_turn_number(current_state: dict) -> int:
    turn_number = current_state["turn_number"]
    num_players = current_state["num_players"]
    turn_number += 1
    if turn_number == num_players:
        turn_number = 1
    return turn_number


async def get_card_pile(current_state: dict, card: str, end_of_round: bool, redis: Redis) -> list[str]:
    """
    Not end of round -> add card to pile
    End of round -> give pile to player and add their points up
    """
    card_pile = current_state["card_pile"]
    if end_of_round:
        # TODO: new function for adding cards to losing players pile and dealing
        # them leftover pile if they got the first hearts maybe separate from this function
        return []
    card_pile.append(card)
    return card_pile


def is_broken(current_state: dict, card: str) -> int:
    """
    current_state is serialized to bool values, but updating the state
    requires giving redis 1 for True, 0 for False
    """
    is_hearts_broken = current_state["is_hearts_broken"]
    if is_hearts_broken:
        return 1
    if card.split("_")[1] == "hearts":
        return 1
    return 0


def get_round_and_game_number(current_state: dict, end_of_round: bool):
    round_number = current_state["round_number"]
    game_number = current_state["game_number"]
    if end_of_round:
        round_number = 1
        game_number += 1

    return round_number, game_number


def get_lead_suit(current_state: dict, end_of_round: bool) -> str:
    """If end of round, set lead suit to OPEN. If not keep current lead suit"""
    if end_of_round:
        return "OPEN"
    return current_state["lead_suit"]


async def advance_game_state(
    room_id: str, player_id: str, card: str, nickname: str, redis: Redis
):
    end_of_round = False
    current_state = deserialize_state(await redis.hgetall(f"room:{room_id}:state"))
    next_player = await get_next_player(room_id, player_id, redis)
    turn_number = get_next_turn_number(current_state)
    if turn_number == 1:
        end_of_round = True
    card_pile = await get_card_pile(current_state, card, end_of_round, redis)
    is_hearts_broken = is_broken(current_state, card)
    game_phase = GamePhase.ROUND_END if end_of_round else GamePhase.PLAYING
    round_number, game_number = get_round_and_game_number(current_state, end_of_round)
    lead_suit = get_lead_suit(current_state, end_of_round)
    # set new state
    await redis.hset(
        f"room:{room_id}:state",
        mapping={
            "current_turn_player_id": next_player,
            "turn_number": turn_number,
            "round_number": round_number,
            "game_number": game_number,
            "card_pile": json.dumps(card_pile),
            "is_hearts_broken": is_hearts_broken,
            "phase": game_phase,
            "last_action": f"{nickname} played {card}",
            "last_action_player_id": current_state.get("current_turn_player_id"),
            "lead_suit": lead_suit,
        },
    )
