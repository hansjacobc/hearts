import pytest
from src.handlers.handle_create_room import handle_create_room
from src.handlers.handle_join_room import handle_join_room
from src.handlers.handle_start_game import handle_start_game
from src.schemas import CreateRoomRequest, JoinRoomRequest, StartGameRequest


@pytest.mark.asyncio
async def test_start_room_redis(redis_client):
    # set up a room
    request = CreateRoomRequest(
        host_player_id="player1",
        num_players=5,
    )
    create_room_resp = await handle_create_room(
        request=request,
        redis=redis_client,
    )
    room_id = create_room_resp.room_id
    # have 4 players join the room for 5 total
    for i in range(2, 6):
        request = JoinRoomRequest(
            player_id=f"player{i}",
        )

        await handle_join_room(
            room_id=room_id,
            request=request,
            redis=redis_client,
        )

    room_members = await redis_client.smembers(f"room:{room_id}:players")

    assert len(room_members) == 5

    request = StartGameRequest(player_id="player1")
    start_game_resp = await handle_start_game(
        room_id=create_room_resp.room_id,
        request=request,
        redis=redis_client,
    )

    assert start_game_resp.room_id == create_room_resp.room_id
    assert start_game_resp.status == "PLAYING"
    assert start_game_resp.starting_player_id != ""
    assert start_game_resp.turn_order
    for i in range(1, 6):
        player_hand = await redis_client.lrange(f"room:{room_id}:hand:player{i}", 0, -1)
        assert len(player_hand) == 10

    left_over_cards = await redis_client.lrange(f"room:{room_id}:deck", 0, -1)
    assert len(left_over_cards) == 2

    turn_order = await redis_client.lrange(f"room:{room_id}:turn_order", 0, -1)
    assert len(turn_order) == 5

    state = await redis_client.hgetall(f"room:{room_id}:state")
    assert state == {
        "current_turn_player_id": start_game_resp.starting_player_id,
        "last_action": "",
        "last_action_player_id": "",
        "phase": "PASSING",
        "round": "1",
        "turn_number": "1",
    }
    room = await redis_client.hgetall(f"room:{room_id}")
    assert room == {
        "host_player_id": "player1",
        "max_players": "5",
        "status": "PLAYING",
    }


@pytest.mark.asyncio
async def test_start_room_endpoint(client):
    create_room_resp = await client.post(
        "/rooms",
        json={
            "host_player_id": "player1",
            "num_players": 5,
        },
    )

    assert create_room_resp.status_code == 200
    room_id = create_room_resp.json()["room_id"]
    # have 4 players join the room for 5 total
    for i in range(2, 6):
        join_room_resp = await client.post(
            f"/rooms/{room_id}/join",
            json={
                "player_id": f"player{i}",
            },
        )
        assert join_room_resp.status_code == 200

    start_room_resp = await client.post(
        f"/rooms/{room_id}/start",
        json={
            "player_id": "player1",
        },
    )
    resp_json = start_room_resp.json()
    assert resp_json["status"] == "PLAYING"
    assert resp_json["starting_player_id"] == "player1"
    assert len(resp_json["turn_order"]) == 5
