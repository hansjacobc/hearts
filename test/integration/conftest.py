# pylint: disable=W0621
import json

import pytest
import pytest_asyncio
from app.dependencies import get_redis
from app.main import app
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from src.rooms import GamePhase


@pytest_asyncio.fixture
async def redis_client():
    redis = Redis(
        host="localhost",
        port=6379,
        db=15,
        decode_responses=True,
    )

    await redis.flushdb()

    yield redis

    await redis.flushdb()
    await redis.aclose()


@pytest.fixture
def test_app() -> FastAPI:
    return app


@pytest_asyncio.fixture
async def app_with_redis(test_app, redis_client):
    test_app.dependency_overrides[get_redis] = lambda: redis_client

    yield test_app

    test_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app_with_redis):
    transport = ASGITransport(app=app_with_redis)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture
def make_room_state(redis_client):
    """
    Factory fixture for setting up a room's state and a player's hand in Redis.

    Usage:
        await make_room_state(room_id, player_id, hand=["2_clubs", "A_spades"])
        await make_room_state(room_id, player_id, hand=[...], phase=GamePhase.PASSING)
    """

    # pylint: disable=too-many-arguments
    async def _make_room_state(
        room_id: str,
        player_id: str,
        hand: list[str],
        *,
        current_turn_player_id: str | None = None,
        turn_number: int = 1,
        card_pile: list[str] | None = None,
        is_hearts_broken: int = 0,
        phase: GamePhase = GamePhase.PLAYING,
        last_action: str = "",
        last_action_player_id: str = "",
        round_number: int = 1,
        starting_card: str = "2_clubs",
        lead_suit: str = "clubs",
        total_players: int = 5,
        game_number: int = 1,
    ):
        await redis_client.hset(
            f"room:{room_id}:state",
            mapping={
                "current_turn_player_id": current_turn_player_id or player_id,
                "turn_number": turn_number,
                "card_pile": json.dumps(card_pile or []),
                "is_hearts_broken": is_hearts_broken,
                "phase": phase,
                "last_action": last_action,
                "last_action_player_id": last_action_player_id,
                "round_number": round_number,
                "starting_card": starting_card,
                "lead_suit": lead_suit,
                "total_players": total_players,
                "game_number": game_number,
            },
        )
        if hand:
            await redis_client.rpush(f"room:{room_id}:hand:{player_id}", *hand)

    return _make_room_state
