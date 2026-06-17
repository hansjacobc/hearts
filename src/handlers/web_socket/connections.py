# pylint: disable=W0718
import asyncio

from fastapi import WebSocket

# room_id -> {player_id -> WebSocket}
_room_connections: dict[str, dict[str, WebSocket]] = {}

# room_id -> asyncio.Lock, created lazily per room
_room_locks: dict[str, asyncio.Lock] = {}


def get_room_lock(room_id: str) -> asyncio.Lock:
    if room_id not in _room_locks:
        _room_locks[room_id] = asyncio.Lock()
    return _room_locks[room_id]


def register_web_socket(room_id: str, player_id: str, websocket: WebSocket) -> None:
    _room_connections.setdefault(room_id, {})[player_id] = websocket


def unregister_web_socket(room_id: str, player_id: str) -> None:
    _room_connections.get(room_id, {}).pop(player_id, None)


async def broadcast(room_id: str, payload: dict) -> None:
    dead = []
    for player_id, ws in _room_connections.get(room_id, {}).items():
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(player_id)
    for player_id in dead:
        unregister_web_socket(room_id, player_id)
