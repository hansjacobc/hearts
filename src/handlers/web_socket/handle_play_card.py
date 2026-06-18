from redis.asyncio import Redis
from src.handlers.web_socket.advance_game_state import advance_game_state
from src.handlers.web_socket.connections import broadcast, send_to_player
from src.handlers.web_socket.helpers import deserialize_state
from src.rooms import GamePhase


# pylint:disable=too-many-return-statements
async def is_valid_play(room_id: str, player_id: str, card: str, redis: Redis):
    state = deserialize_state(await redis.hgetall(f"room:{room_id}:state"))

    # check that game state is playing
    if state.get("phase") != GamePhase.PLAYING:
        return False

    # check for their turn
    current_player_turn = state.get("current_turn_player_id")
    if player_id != current_player_turn:
        return False

    # Check that the card is in their hand
    player_hand = await redis.lrange(f"room:{room_id}:hand:{player_id}", 0, -1)
    if card not in player_hand:
        return False

    # Check that the card is a valid play
    turn_number = state.get("turn_number")
    is_hearts_broken = state.get("is_hearts_broken", 0)
    starting_card = state.get("starting_card")
    round_number = state.get("round_number")
    lead_suit = state.get("lead_suit")
    suit = card.split("_")[1]

    # for turn 1, round 1, make sure the starting card is played
    if turn_number == 1 and round_number == 1:
        if card != starting_card:
            return False

    # turn start logic for empty pile, can't start with hearts if
    # hearts not broken and can't play queen of spades
    if turn_number == 1:
        if card == "Q_spades":
            return False
        if not is_hearts_broken and suit == "hearts":
            return False

    # validate card played follows suit if they have a card of that suit
    # if start of round suit is open, we already checked if hearts are broken
    if lead_suit != "OPEN":
        has_suit_in_hand = False
        for c in player_hand:
            if c.split("_")[1] == lead_suit:
                has_suit_in_hand = True
        if has_suit_in_hand and suit != lead_suit:
            return False

    return True


async def handle_play_card(room_id: str, player_id: str, message: dict, redis: Redis):
    card = message.get("card")

    # 1. is it this player's turn? (check room:{id}:state current_turn_player_id)
    # 2. is this card actually in their hand? (check room:{id}:hand:{player_id})
    # 3. does it follow suit-leading / hearts-broken rules?

    if not is_valid_play(room_id, player_id, card, redis):
        await send_to_player(
            room_id,
            player_id,
            {
                "type": "error",
                "reason": "invalid_play",
                "message": "You can't play that card!",
            },
        )
        return

    # remove card from players hand
    await redis.lrem(f"room:{room_id}:hand:{player_id}", 0, card)

    # advance game state
    player = await redis.hgetall(f"player:{player_id}")
    nickname = player.get("nickname", "Anon")
    await advance_game_state(room_id, player_id, card, nickname, redis)

    await broadcast(
        room_id,
        {
            "type": "card_played",
            "player_id": player_id,
            "card": card,
            "nickname": nickname,
        },
    )
