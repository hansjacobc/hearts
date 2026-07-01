import pytest

from test.integration.conftest import open_ws


@pytest.mark.asyncio
async def test_websocket_broadcasts_disconnect(ws_transport, make_room_state):
    await make_room_state("room1", "player1", hand=["2_clubs"])

    async with open_ws(ws_transport, "/ws/room1/player1") as ws:
        await ws.send_json({"type": "some_action"})
        response = await ws.receive_json()

    a = []