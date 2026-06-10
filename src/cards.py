import itertools
import random

from src.card_enums import Card, Ranks, Suits
from src.errors import DeckNotDivisibleException
from src.player import Player


class DeckOfCards:
    """Class to create a deck of cards"""

    deck: list[Card]

    def __init__(self):
        self.deck = []

    def create_deck(self, shuffled: bool = False, num_decks: int = 1) -> None:
        for _ in range(num_decks):
            for suit in Suits:
                for rank in Ranks:
                    card = Card(suit=suit, rank=rank)
                    self.deck.append(card)

        if shuffled:
            self.shuffle_deck()

    def shuffle_deck(self) -> None:
        random.shuffle(self.deck)

    def deal_out_deck(self, players: list[Player]) -> list[Card]:
        """
        Deals out a deck given players and returns player object with updated hand
        attribute and also a list of leftover cards.
        """
        num_players = len(players)
        len_deck = len(self.deck)
        num_left_over = len_deck % num_players
        left_over = [self.deck.pop(0) for _ in range(num_left_over)]

        if not len(self.deck) % num_players == 0:
            raise DeckNotDivisibleException(
                num_players=num_players, len_deck=len(self.deck)
            )

        player_cycle = itertools.cycle(players)

        while self.deck:
            player = next(player_cycle)
            card = self.deck.pop(0)
            player.add_card_to_hand(card)

        return left_over
