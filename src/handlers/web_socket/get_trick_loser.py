from redis.asyncio import Redis
from src.handlers.web_socket.connections import broadcast
from src.handlers.web_socket.helpers import deserialize_state
from src.rooms import GamePhase


# pylint: disable=unused-argument
async def handle_get_trick_loser(room_id: str, player_id: str, message: dict, redis: Redis):
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

    losing_player_id = ""
    highest_rank = 15
    lead_suit = current_state["lead_suit"]
    for p_id, card in trick.items():
        rank, suit = card.split("_")
        if suit != lead_suit:
            continue
        if rank in ["A", "K", "Q", "J"]:
            if rank == "A":
                rank = 14
            if rank == "K":
                rank = 13
            if rank == "Q":
                rank = 12
            if rank == "J":
                rank = 11
        rank = int(rank)
        if rank > highest_rank:
            highest_rank = rank
            losing_player_id = p_id

    player = await redis.hgetall(f"player:{player_id}")
    nickname = player.get("nickname", "Anon")

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
