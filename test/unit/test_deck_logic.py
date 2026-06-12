from src.cards import DeckOfCards
from src.player import Player


def test_deal_out_deck():
    players = [Player(player) for player in ["Hans", "Ryan", "Dylan", "Gavin", "Scran"]]

    deck = DeckOfCards()
    deck.create_deck(shuffled=True)

    left_overs = deck.deal_out_deck(players)

    for player in players:
        assert len(player.hand) == 10

    assert len(left_overs) == 2
