from fastapi import FastAPI
from src.handlers.handle_create_player import handle_create_player
from src.handlers.handle_create_room import handle_create_room
from src.handlers.handle_get_user import handle_get_user
from src.handlers.handle_health import handle_health
from src.schemas import (
    CreatePlayerRequest,
    CreatePlayerResponse,
    CreateRoomRequest,
    CreateRoomResponse,
)

app = FastAPI()


@app.get("/health")
def health():
    return handle_health()


@app.get("/players/{player_id}", response_model=CreatePlayerResponse)
def get_user(player_id: str):
    return handle_get_user(player_id)


@app.post("/players", response_model=CreatePlayerResponse)
def create_player(request: CreatePlayerRequest):
    return handle_create_player(request)


@app.post("/rooms", response_model=CreateRoomResponse)
def create_room(request: CreateRoomRequest):
    return handle_create_room(request)
