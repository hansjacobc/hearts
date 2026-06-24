import json

from src.rooms import GamePhase


def deserialize_state(raw: dict) -> dict:
    return {
        "card_pile": json.loads(raw["card_pile"]),
        "turn_number": int(raw["turn_number"]),
        "round_number": int(raw["round_number"]),
        "game_number": int(raw["game_number"]),
        "current_turn_player_id": raw["current_turn_player_id"],
        "is_hearts_broken": bool(int(raw["is_hearts_broken"])),
        "last_action": raw["last_action"],
        "last_action_player_id": raw["last_action_player_id"],
        "lead_suit": raw["lead_suit"],
        "phase": GamePhase(raw["phase"]),
        "starting_card": raw["starting_card"],
        "total_players": int(raw["total_players"]),
    }

async def trick():
    """
    random trick ops, prob won't need this function and can just add player cards to
    trick as part of advance game state once they've added the card to the pile
    ALSO need to deal with updating and adding player score in a per round and total game scope
    """
    # player plays a card
    await redis_client.hset(f"room:{room_id}:trick", player_id, card)

    # read all played cards for the trick { player_id: card }
    trick = await redis_client.hgetall(f"room:{room_id}:trick")

    # check if a specific player has played
    card = await redis_client.hget(f"room:{room_id}:trick", player_id)

    # how many cards have been played this trick
    count = await redis_client.hlen(f"room:{room_id}:trick")

    # clear the trick once it's been won
    await redis_client.delete(f"room:{room_id}:trick")


async def determine_losing_player_and_add_score():
    """
    The losing player is the player who played the highest value card of the lead suit.
    Cards played not in the lead suit cannot win the round.
    """
