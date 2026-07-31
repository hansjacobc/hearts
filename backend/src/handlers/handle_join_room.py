from redis.asyncio import Redis
from src.handlers.web_socket.connections import broadcast
from src.rooms import RoomStatus
from src.schemas import JoinRoomRequest, JoinRoomResponse, PlayerInfo


async def handle_join_room(
    room_id: str, request: JoinRoomRequest, redis: Redis
) -> JoinRoomResponse:
    """
    Validate room exists.
    Validate game has not started.
    Validate room is not full.
    Validate player is not already in room.
    Persist updated state.
    """

    # Validate room exists
    room_exists = await redis.exists(f"room:{room_id}")
    if not room_exists:
        raise ValueError("Room does not exist")

    # Validate game has not started
    room_data = await redis.hgetall(f"room:{room_id}")
    if room_data["status"] != RoomStatus.WAITING:
        raise ValueError("Game already started")
    max_players = int(room_data["max_players"])

    # Validate room is not full
    current_players = await redis.smembers(f"room:{room_id}:players")
    if len(current_players) >= max_players:
        raise ValueError("Room is full")

    # Validate player is not already in room
    already_in_room = await redis.sismember(
        f"room:{room_id}:players",
        request.player_id,
    )
    if already_in_room:
        raise ValueError("Player already in room")

    await redis.sadd(f"room:{room_id}:players", request.player_id)

    players_in_room = []
    host_id = await redis.hget(f"room:{room_id}", "host_player_id")
    for player_id in current_players:
        is_host = host_id == player_id
        nickname = await redis.hget(f"player:{player_id}", "nickname")
        players_in_room.append(PlayerInfo(id=player_id, name=nickname, is_host=is_host))

    nickname = await redis.hget(f"player:{request.player_id}", "nickname")
    players_in_room.append(
        PlayerInfo(id=request.player_id, name=nickname, is_host=False)
    )
    await broadcast(
        room_id,
        {
            "type": "player_joined",
            "player": {"id": request.player_id, "name": nickname, "is_host": False},
        },
    )

    return JoinRoomResponse(
        room_id=room_id, player_id=request.player_id, players_in_room=players_in_room
    )
