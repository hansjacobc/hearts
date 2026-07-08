from pydantic import BaseModel, Field
from src.rooms import RoomStatus


class CreatePlayerRequest(BaseModel):
    """Take in a nickname to create a player"""

    nickname: str


class CreatePlayerResponse(BaseModel):
    """Given a nickname return a nickname and player id"""

    nickname: str
    player_id: str


class CreateRoomRequest(BaseModel):
    """Requires a player id from the host and number of players"""

    host_player_id: str
    num_players: int = Field(ge=3, le=8)


class CreateRoomResponse(BaseModel):
    """Given a host's player id and number of players return a room id"""

    room_id: str
    host_player_id: str
    num_players: int = Field(ge=3, le=8)


class JoinRoomRequest(BaseModel):
    """Join a room with a player id"""

    player_id: str


class JoinRoomResponse(BaseModel):
    """Verifies that the user has joined the room successfully"""

    room_id: str
    player_id: str


class StartGameRequest(BaseModel):
    """Take in a host player id"""

    player_id: str


class StartGameResponse(BaseModel):
    """Confirm the game has started"""

    room_id: str
    status: RoomStatus
    starting_player_id: str
    turn_order: list[str]
