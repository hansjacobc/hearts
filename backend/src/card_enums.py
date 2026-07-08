from enum import Enum


class Suits(Enum):
    """Enum for card suits"""

    CLUBS = "CLUBS"
    DIAMONDS = "DIAMONDS"
    HEARTS = "HEARTS"
    SPADES = "SPADES"


class Ranks(Enum):
    """Enum for card ranks"""

    ACE = "ACE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"
    SIX = "SIX"
    SEVEN = "SEVEN"
    EIGHT = "EIGHT"
    NINE = "NINE"
    TEN = "TEN"
    JACK = "JACK"
    QUEEN = "QUEEN"
    KING = "KING"


class Card:
    """Class to encapsulate card suits and ranks."""

    def __init__(self, suit: Suits, rank: Ranks):
        self.suit = suit
        self.rank = rank

    def get_rank_value(self) -> int:
        value_map = {
            "TWO": 2,
            "THREE": 3,
            "FOUR": 4,
            "FIVE": 5,
            "SIX": 6,
            "SEVEN": 7,
            "EIGHT": 8,
            "NINE": 9,
            "TEN": 10,
            "JACK": 11,
            "QUEEN": 12,
            "KING": 13,
            "ACE": 13,
        }
        return value_map[self.rank.value]
