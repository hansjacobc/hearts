import pytest
from src.handlers.handle_create_room import handle_create_room
from src.schemas import CreateRoomRequest


@pytest.mark.asyncio
async def test_create_room_redis(redis_client):
    request = CreateRoomRequest(
        host_player_id="player1",
        num_players=4,
    )

    response = await handle_create_room(
        request=request,
        redis=redis_client,
    )

    room = await redis_client.hgetall(f"room:{response.room_id}")

    assert room["host_player_id"] == "player1"
    assert room["max_players"] == "4"
    assert room["status"] == "WAITING"


@pytest.mark.asyncio
async def test_create_room_endpoint(client):
    response = await client.post(
        "/rooms",
        json={
            "host_player_id": "player1",
            "num_players": 4,
        },
    )

    assert response.status_code == 200

    resp = response.json()
    assert resp["host_player_id"] == "player1"
    assert resp["num_players"] == 4
    assert len(resp["room_id"]) == 4
