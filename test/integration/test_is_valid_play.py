import pytest
from src.handlers.web_socket.handle_play_card import is_valid_play
from src.rooms import GamePhase


@pytest.mark.asyncio
async def test_is_valid_basic(redis_client, make_room_state):
    room_id = "abcd"
    player_id = "1234"

    await make_room_state(room_id, player_id, hand=["2_clubs", "A_spades"])

    is_valid = await is_valid_play(room_id, player_id, "2_clubs", redis_client)
    assert is_valid is True


@pytest.mark.asyncio
async def test_is_valid_game_phase_not_playing(redis_client, make_room_state):
    room_id = "abcd"
    player_id = "1234"

    await make_room_state(
        room_id, player_id, hand=["2_clubs", "A_spades"], phase=GamePhase.TRICK_END
    )

    is_valid = await is_valid_play(room_id, player_id, "2_clubs", redis_client)
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_valid_not_their_turn(redis_client, make_room_state):
    room_id = "abcd"
    player_id = "1234"

    await make_room_state(
        room_id, player_id, hand=["2_clubs", "A_spades"], current_turn_player_id="efgh"
    )

    is_valid = await is_valid_play(room_id, player_id, "2_clubs", redis_client)
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_valid_doesnt_have_card(redis_client, make_room_state):
    room_id = "abcd"
    player_id = "1234"

    await make_room_state(room_id, player_id, hand=["2_clubs", "A_spades"])

    is_valid = await is_valid_play(room_id, player_id, "3_clubs", redis_client)
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_valid_doesnt_play_starting_card(redis_client, make_room_state):
    room_id = "abcd"
    player_id = "1234"

    await make_room_state(room_id, player_id, hand=["2_clubs", "A_spades"])

    is_valid = await is_valid_play(room_id, player_id, "A_spades", redis_client)
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_valid_hearts_not_broken(redis_client, make_room_state):
    room_id = "abcd"
    player_id = "1234"

    await make_room_state(
        room_id,
        player_id,
        hand=["2_clubs", "A_spades", "A_hearts", "Q_spades"],
        round_number=2,
    )

    is_valid = await is_valid_play(room_id, player_id, "Q_spades", redis_client)
    assert is_valid is False

    is_valid = await is_valid_play(room_id, player_id, "A_hearts", redis_client)
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_valid_follow_suit(redis_client, make_room_state):
    room_id = "abcd"
    player_id = "1234"

    await make_room_state(
        room_id,
        player_id,
        hand=["A_clubs", "A_spades", "A_hearts", "Q_spades"],
        turn_number=2,
        lead_suit="spades",
    )

    is_valid = await is_valid_play(room_id, player_id, "A_clubs", redis_client)
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_valid_lead_suit_is_open(redis_client, make_room_state):
    room_id = "abcd"
    player_id = "1234"

    await make_room_state(
        room_id,
        player_id,
        hand=["A_clubs", "A_spades", "A_hearts", "Q_spades"],
        round_number=2,
        lead_suit="OPEN",
    )

    is_valid = await is_valid_play(room_id, player_id, "A_clubs", redis_client)
    assert is_valid is True
