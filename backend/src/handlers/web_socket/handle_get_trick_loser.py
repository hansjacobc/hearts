from redis.asyncio import Redis
from src.handlers.helpers import deserialize_state, find_trick_loser
from src.handlers.web_socket.connections import broadcast
from src.rooms import GamePhase


# pylint: disable=unused-argument, too-many-locals
async def handle_get_trick_loser(
    room_id: str, player_id: str, message: dict, redis: Redis
):
    """Returns player id of the loser of the trick and clears the trick"""

    # read all played cards for the trick { player_id: card }
    trick = await redis.hgetall(f"room:{room_id}:trick")

    current_state = deserialize_state(await redis.hgetall(f"room:{room_id}:state"))

    if current_state["phase"] != GamePhase.TRICK_END or not trick:
        await broadcast(
            room_id,
            {
                "type": "error",
                "reason": "round_not_over",
                "message": "You can't end the trick before it's over!",
            },
        )
        return

    losing_player_id = find_trick_loser(current_state["lead_suit"], trick)

    player = await redis.hgetall(f"player:{player_id}")
    nickname = player.get("nickname", "Anon")

    # get round total points
    score = 0
    for card in trick.values():
        if card == "Q_spades":
            score += 13
        if card.split("_")[1] == "hearts":
            score += 1

    # check if there is a leftover deck and count toward player score if hearts in it
    left_over_cards = await redis.lrange(f"room:{room_id}:deck", 0, -1)
    if left_over_cards:
        for card in left_over_cards:
            if card.split("_")[1] == "hearts":
                score += 1

        # delete deck once dealt out
        await redis.delete(f"room:{room_id}:deck")

    # update round score
    round_score = await redis.hget(
        f"room:{room_id}:score:{losing_player_id}", "round_score"
    )
    round_score = int(round_score)
    await redis.hset(
        f"room:{room_id}:score:{losing_player_id}",
        mapping={"round_score": round_score + score},
    )

    await redis.delete(f"room:{room_id}:trick")

    # A trick ending doesn't necessarily mean the deal ended — only check
    # for that once this specific trick's cleanup is done.
    player_ids = list(await redis.smembers(f"room:{room_id}:players"))
    deal_over = True
    for pid in player_ids:
        if await redis.scard(f"room:{room_id}:hand:{pid}") > 0:
            deal_over = False
            break

    if deal_over:
        game_scores = {}
        for pid in player_ids:
            scores = await redis.hgetall(f"room:{room_id}:score:{pid}")
            round_total = int(scores.get("round_score", 0))
            new_game_total = int(scores.get("game_score", 0)) + round_total
            await redis.hset(
                f"room:{room_id}:score:{pid}",
                mapping={"round_score": 0, "game_score": new_game_total},
            )
            game_scores[pid] = new_game_total

        await redis.hset(
            f"room:{room_id}:state",
            mapping={"phase": GamePhase.DEAL_END, "lead_suit": "OPEN"},
        )
        await broadcast(
            room_id,
            {
                "type": "deal_over",
                "losing_player_id": losing_player_id,
                "nickname": nickname,
                "scores": game_scores,
            },
        )
        return

    await redis.hset(
        f"room:{room_id}:state",
        mapping={
            "current_turn_player_id": losing_player_id,
            "phase": GamePhase.PLAYING,
            "lead_suit": "OPEN",
        },
    )
    await broadcast(
        room_id,
        {
            "type": "trick_loser",
            "player_id": player_id,
            "losing_player_id": losing_player_id,
            "nickname": nickname,
        },
    )
