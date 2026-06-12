from unittest.mock import AsyncMock, patch

import pytest
from src.handlers.handle_create_room import handle_create_room
from src.rooms import RoomStatus
from src.schemas import CreateRoomRequest


@pytest.mark.asyncio
@patch("src.handlers.handle_create_room.secrets.token_urlsafe")
async def test_handle_create_room(mock_token):
    mock_token.return_value = "fake_room_id"

    redis = AsyncMock()

    request = CreateRoomRequest(
        host_player_id="player1",
        num_players=4,
    )

    response = await handle_create_room(request, redis)

    assert response.host_player_id == "player1"
    assert response.num_players == 4
    assert response.room_id == "fake_room_id"


@pytest.mark.asyncio
async def test_handle_create_room_redis_calls():
    redis = AsyncMock()

    request = CreateRoomRequest(
        host_player_id="player1",
        num_players=4,
    )

    response = await handle_create_room(request, redis)
    room_key = f"room:{response.room_id}"
    players_key = f"{room_key}:players"

    redis.hset.assert_awaited_once_with(
        room_key,
        mapping={
            "host_player_id": "player1",
            "max_players": "4",
            "status": RoomStatus.WAITING,
        },
    )

    redis.sadd.assert_awaited_once_with(
        players_key,
        "player1",
    )

    assert redis.expire.await_count == 2
    redis.expire.assert_any_await(room_key, 3600)
    redis.expire.assert_any_await(players_key, 3600)
