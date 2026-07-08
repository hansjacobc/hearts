import pytest
from src.handlers.handle_create_room import handle_create_room
from src.handlers.handle_join_room import handle_join_room
from src.schemas import CreateRoomRequest, JoinRoomRequest


@pytest.mark.asyncio
async def test_join_room_redis(redis_client):
    # set up a room
    request = CreateRoomRequest(
        host_player_id="player1",
        num_players=4,
    )
    create_room_resp = await handle_create_room(
        request=request,
        redis=redis_client,
    )

    # join the room
    request = JoinRoomRequest(
        player_id="player2",
    )

    response = await handle_join_room(
        room_id=create_room_resp.room_id,
        request=request,
        redis=redis_client,
    )

    room_members = await redis_client.smembers(f"room:{response.room_id}:players")

    assert room_members == {"player1", "player2"}


@pytest.mark.asyncio
async def test_join_room_endpoint(client):
    create_room_resp = await client.post(
        "/rooms",
        json={
            "host_player_id": "player1",
            "num_players": 4,
        },
    )

    assert create_room_resp.status_code == 200
    room_id = create_room_resp.json()["room_id"]

    join_room_resp = await client.post(
        f"/rooms/{room_id}/join",
        json={
            "player_id": "player2",
        },
    )

    resp = join_room_resp.json()
    assert resp["player_id"] == "player2"
