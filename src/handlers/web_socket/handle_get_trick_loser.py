from redis.asyncio import Redis
from src.handlers.helpers import deserialize_state, find_trick_loser
from src.handlers.web_socket.connections import broadcast
from src.rooms import GamePhase


# pylint: disable=unused-argument
async def handle_get_trick_loser(
    room_id: str, player_id: str, message: dict, redis: Redis
):
    """Returns player id of the loser of the trick and clears the trick"""

    # read all played cards for the trick { player_id: card }
    trick = await redis.hgetall(f"room:{room_id}:trick")

    current_state = deserialize_state(await redis.hgetall(f"room:{room_id}:state"))

    if current_state != GamePhase.ROUND_END:
        await broadcast(
            room_id,
            {
                "type": "error",
                "reason": "round_not_over",
                "message": "You can't end the trick before the round is over!",
            },
        )

    losing_player_id = find_trick_loser(current_state["lead_suit"], trick)

    player = await redis.hgetall(f"player:{player_id}")
    nickname = player.get("nickname", "Anon")

    # get round total points
    score = 0
    for card in trick.values():
        if card == "Q_spades":
            score += 13
        if card.split[1] == "hearts":
            score += 1

    # check if there is a leftover deck and count toward player score if hearts in it
    left_over_cards = await redis.lrange(f"room:{room_id}:deck", 0, -1)
    if left_over_cards:
        for card in left_over_cards:
            if card.split[1] == "hearts":
                score += 1

        # delete deck once dealt out
        await redis.delete(f"room:{room_id}:deck")

    # updates round score
    round_score = await redis.hget(
        f"room:{room_id}:score:{losing_player_id}", "round_score"
    )

    await redis.hset(
        f"room:{room_id}:score:{losing_player_id}",
        mapping={
            "round_score": round_score + score,
        },
    )
    # clear the trick
    await redis.delete(f"room:{room_id}:trick")

    # set phase in game state to passing
    await redis.hset(f"room:{room_id}:state", "phase", GamePhase.PASSING)

    await broadcast(
        room_id,
        {
            "type": "trick_loser",
            "player_id": player_id,
            "losing_player_id": losing_player_id,
            "nickname": nickname,
        },
    )
