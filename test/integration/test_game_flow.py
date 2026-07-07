import pytest


@pytest.mark.asyncio
async def test_game_flow_basic(
    redis_client, ws_action, make_room_state, setup_players_hands
):
    await make_room_state("room1", "player1")
    await setup_players_hands(
        "room1",
        {
            "player1": ["2_clubs"],
            "player2": ["3_clubs"],
            "player3": ["4_clubs"],
            "player4": ["5_clubs"],
            "player5": ["6_clubs"],
        },
    )

    response1 = await ws_action(
        "room1", "player1", {"type": "play_card", "card": "2_clubs"}
    )

    cards_in_hand = await redis_client.smembers("room:room1:hand:player1")
    assert cards_in_hand == set()
    assert response1 == {
        "card": "2_clubs",
        "nickname": "Anon",
        "player_id": "player1",
        "type": "card_played",
    }

    response2 = await ws_action(
        "room1", "player2", {"type": "play_card", "card": "3_clubs"}
    )

    cards_in_hand2 = await redis_client.smembers("room:room1:hand:player2")
    assert cards_in_hand2 == set()
    assert response2 == {
        "card": "3_clubs",
        "nickname": "Anon",
        "player_id": "player2",
        "type": "card_played",
    }


# pylint: disable=line-too-long
@pytest.mark.asyncio
async def test_game_flow_giga_test(
    redis_client, ws_action, make_room_state, setup_players_hands
):
    """
    Testing the happy path of an entire game flow to make sure
    everything is updated accordingly
    """
    await make_room_state("room1", "player1")
    # fmt: off
    await setup_players_hands(
        "room1",
        {
            "player1": ["10_spades", "2_clubs", "3_hearts", "3_spades", "4_diamonds", "7_clubs", "7_hearts", "A_clubs", "A_spades", "Q_clubs"],  # noqa: E501
            "player2": ["10_clubs", "10_diamonds", "5_spades", "6_hearts", "6_spades", "7_diamonds", "8_clubs", "J_clubs", "J_spades", "Q_hearts"],  # noqa: E501
            "player3": ["3_clubs", "4_hearts", "6_clubs", "8_hearts", "9_clubs", "9_hearts", "9_spades", "J_diamonds", "J_hearts", "Q_diamonds"],  # noqa: E501
            "player4": ["4_clubs", "2_diamonds", "2_hearts", "2_spades", "3_diamonds", "5_diamonds", "6_diamonds", "7_spades", "8_diamonds", "K_spades"],  # noqa: E501
            "player5": ["4_spades", "5_clubs", "5_hearts", "8_spades", "A_diamonds", "A_hearts", "K_clubs", "K_diamonds", "K_hearts", "Q_spades"],  # noqa: E501
        },
    )
    # fmt: on

    left_over = ["9_diamonds", "10_hearts"]
    await redis_client.rpush("room:room1:deck", *left_over)

    # set players scores
    for player_id in ["player1", "player2", "player3", "player4", "player5"]:
        await redis_client.hset(
            f"room:room1:score:{player_id}",
            mapping={
                "round_score": 0,
                "game_score": 0,
            },
        )

    # player 1 plays
    await ws_action("room1", "player1", {"type": "play_card", "card": "2_clubs"})
    state_resp = await ws_action("room1", "player5", {"type": "get_state"})
    assert state_resp["state"] == {
        "card_pile": ["2_clubs"],
        "current_turn_player_id": "player2",
        "game_number": 1,
        "is_hearts_broken": False,
        "last_action": "Anon played 2_clubs",
        "last_action_player_id": "player1",
        "lead_suit": "clubs",
        "phase": "PLAYING",
        "round_number": 1,
        "starting_card": "2_clubs",
        "total_players": 5,
        "turn_number": 2,
    }

    # player 2 plays
    await ws_action("room1", "player2", {"type": "play_card", "card": "10_clubs"})
    state_resp = await ws_action("room1", "player5", {"type": "get_state"})
    assert state_resp["state"] == {
        "card_pile": ["2_clubs", "10_clubs"],
        "current_turn_player_id": "player3",
        "game_number": 1,
        "is_hearts_broken": False,
        "last_action": "Anon played 10_clubs",
        "last_action_player_id": "player2",
        "lead_suit": "clubs",
        "phase": "PLAYING",
        "round_number": 1,
        "starting_card": "2_clubs",
        "total_players": 5,
        "turn_number": 3,
    }

    # player 3 plays
    await ws_action("room1", "player3", {"type": "play_card", "card": "3_clubs"})
    state_resp = await ws_action("room1", "player5", {"type": "get_state"})
    assert state_resp["state"] == {
        "card_pile": ["2_clubs", "10_clubs", "3_clubs"],
        "current_turn_player_id": "player4",
        "game_number": 1,
        "is_hearts_broken": False,
        "last_action": "Anon played 3_clubs",
        "last_action_player_id": "player3",
        "lead_suit": "clubs",
        "phase": "PLAYING",
        "round_number": 1,
        "starting_card": "2_clubs",
        "total_players": 5,
        "turn_number": 4,
    }

    # player 4 plays
    await ws_action("room1", "player4", {"type": "play_card", "card": "4_clubs"})
    state_resp = await ws_action("room1", "player5", {"type": "get_state"})
    assert state_resp["state"] == {
        "card_pile": ["2_clubs", "10_clubs", "3_clubs", "4_clubs"],
        "current_turn_player_id": "player5",
        "game_number": 1,
        "is_hearts_broken": False,
        "last_action": "Anon played 4_clubs",
        "last_action_player_id": "player4",
        "lead_suit": "clubs",
        "phase": "PLAYING",
        "round_number": 1,
        "starting_card": "2_clubs",
        "total_players": 5,
        "turn_number": 5,
    }

    # player 5 plays, last player
    await ws_action("room1", "player5", {"type": "play_card", "card": "5_clubs"})
    state_resp = await ws_action("room1", "player5", {"type": "get_state"})
    assert state_resp["state"] == {
        "card_pile": [],
        "current_turn_player_id": "",
        "game_number": 1,
        "is_hearts_broken": False,
        "last_action": "Anon played 5_clubs",
        "last_action_player_id": "player5",
        "lead_suit": "clubs",
        "phase": "TRICK_END",
        "round_number": 2,
        "starting_card": "2_clubs",
        "total_players": 5,
        "turn_number": 1,
    }

    await ws_action("room1", "player5", {"type": "get_trick_loser"})
    state_resp = await ws_action("room1", "player5", {"type": "get_state"})
    assert state_resp["state"] == {
        "card_pile": [],
        "current_turn_player_id": "player2",
        "game_number": 1,
        "is_hearts_broken": False,
        "last_action": "Anon played 5_clubs",
        "last_action_player_id": "player5",
        "lead_suit": "OPEN",
        "phase": "PLAYING",
        "round_number": 2,
        "starting_card": "2_clubs",
        "total_players": 5,
        "turn_number": 1,
    }
