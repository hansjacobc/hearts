import json
import random

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


def deal_hands(num_players: int, player_ids: list[str]):
    """Deal out even sized hands of all cards and keep track of left over cards"""
    suits = ["spades", "hearts", "diamonds", "clubs"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    deck = [f"{rank}_{suit}" for suit in suits for rank in ranks]
    random.shuffle(deck)

    hand_size = 52 // num_players
    hands = {}
    for player_id in player_ids:
        hands[player_id] = deck[:hand_size]
        deck = deck[hand_size:]
    return hands, deck


def find_trick_loser(lead_suit: str, trick: dict):
    losing_player_id = ""
    highest_rank = 15
    for p_id, card in trick.items():
        rank, suit = card.split("_")
        if suit != lead_suit:
            continue
        if rank in ["A", "K", "Q", "J"]:
            if rank == "A":
                rank = 14
            if rank == "K":
                rank = 13
            if rank == "Q":
                rank = 12
            if rank == "J":
                rank = 11
        rank = int(rank)
        if rank > highest_rank:
            highest_rank = rank
            losing_player_id = p_id

    return losing_player_id
