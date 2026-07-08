from src.card_enums import Card


class Player:
    """Class for player data"""

    def __init__(self, name: str):
        self.name = name
        self.score = 0
        self.hand = []

    def add_score(self, round_score: int):
        self.score += round_score

    def set_hand(self, cards: list[Card]):
        self.hand = cards

    def add_card_to_hand(self, card: Card):
        self.hand.append(card)
