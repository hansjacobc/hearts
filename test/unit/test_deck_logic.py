from src.cards import DeckOfCards
from src.handlers.handle_start_game import deal_hands, find_starting_player
from src.player import Player


def test_deal_out_deck():
    players = [Player(player) for player in ["Hans", "Ryan", "Dylan", "Gavin", "Scran"]]

    deck = DeckOfCards()
    deck.create_deck(shuffled=True)

    left_overs = deck.deal_out_deck(players)

    for player in players:
        assert len(player.hand) == 10

    assert len(left_overs) == 2

def test_deal_hands_3_ppl():
    num_players = 3
    hands, deck = deal_hands(num_players, ["p1", "p2", "p3"])
    assert len(hands) == num_players
    for hand in hands.values():
        assert len(hand) == 17
    assert len(deck) == 1

def test_deal_hands_4_ppl():
    num_players = 4
    hands, deck = deal_hands(num_players, ["p1", "p2", "p3", "p4"])
    assert len(hands) == num_players
    for hand in hands.values():
        assert len(hand) == 13
    assert len(deck) == 0

def test_deal_hands_5_ppl():
    num_players = 5
    hands, deck = deal_hands(num_players, ["p1", "p2", "p3", "p4", "p5"])
    assert len(hands) == num_players
    for hand in hands.values():
        assert len(hand) == 10
    assert len(deck) == 2

def test_deal_hands_6_ppl():
    num_players = 6
    hands, deck = deal_hands(num_players, ["p1", "p2", "p3", "p4", "p5", "p6"])
    assert len(hands) == num_players
    for hand in hands.values():
        assert len(hand) == 8
    assert len(deck) == 4

def test_deal_hands_7_ppl():
    num_players = 7
    hands, deck = deal_hands(num_players, ["p1", "p2", "p3", "p4", "p5", "p6", "p7"])
    assert len(hands) == num_players
    for hand in hands.values():
        print(hand)
        assert len(hand) == 7
    assert len(deck) == 3

def test_deal_hands_8_ppl():
    num_players = 8
    hands, deck = deal_hands(num_players, ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"])
    assert len(hands) == num_players
    for hand in hands.values():
        assert len(hand) == 6
    assert len(deck) == 4


def test_find_starting_player():
    hands = {
        "p1": ["2_clubs"],
        "p2": ["3_clubs"],
        "p3": ["4_clubs"],
        "p4": ["5_clubs"],
    }
    left_over_deck = []
    starting_player_id = find_starting_player(hands, left_over_deck)
    assert starting_player_id == "p1"

def test_find_starting_player_2_clubs_in_deck():
    hands = {
        "p1": ["A_clubs"],
        "p2": ["3_clubs"],
        "p3": ["4_clubs"],
        "p4": ["5_clubs"],
    }
    left_over_deck = ["2_clubs"]
    starting_player_id = find_starting_player(hands, left_over_deck)
    assert starting_player_id == "p2"

def test_find_starting_player_giga_edge_case():
    hands = {
        "p1": ["A_clubs"],
        "p2": ["K_clubs"],
        "p3": ["6_clubs"],
        "p4": ["7_clubs"],
    }
    left_over_deck = ["2_clubs", "3_clubs", "4_clubs", "5_clubs"]
    starting_player_id = find_starting_player(hands, left_over_deck)
    assert starting_player_id == "p3"