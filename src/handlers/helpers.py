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
