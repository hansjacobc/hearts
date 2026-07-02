from test.integration.conftest import open_ws

import pytest


@pytest.mark.asyncio
async def test_game_flow_basic(redis_client, ws_transport, make_room_state, setup_players_hands):
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

    async with open_ws(ws_transport, "/ws/room1/player1") as ws:
        await ws.send_json({"type": "play_card", "card": "2_clubs"})
        response = await ws.receive_json()

    cards_in_hand = await redis_client.smembers(f"room:room1:hand:player1")
    assert cards_in_hand == set()
    assert response == {
        "card": "2_clubs",
        "nickname": "Anon",
        "player_id": "player1",
        "type": "card_played",
    }

    async with open_ws(ws_transport, "/ws/room1/player2") as ws:
        await ws.send_json({"type": "play_card", "card": "3_clubs"})
        response = await ws.receive_json()

    cards_in_hand2 = await redis_client.smembers(f"room:room1:hand:player2")
    assert cards_in_hand2 == set()
    assert response == {
        "card": "3_clubs",
        "nickname": "Anon",
        "player_id": "player2",
        "type": "card_played",
    }

@pytest.mark.asyncio
async def test_game_flow_giga_test(redis_client, ws_transport, make_room_state, setup_players_hands):
