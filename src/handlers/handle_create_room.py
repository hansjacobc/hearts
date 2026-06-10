import secrets

from src.schemas import CreateRoomRequest, CreateRoomResponse


def handle_create_room(request: CreateRoomRequest) -> CreateRoomResponse:
    room_id = secrets.token_hex(2)
    return CreateRoomResponse(
        room_id=room_id,
        host_player_id=request.host_player_id,
        num_players=request.num_players,
    )
