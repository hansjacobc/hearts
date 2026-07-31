const API_BASE = import.meta.env.VITE_API_BASE;

export interface CreateRoomResponse {
  room_id: string;
  host_player_id: string;
  num_players: number;
}

export interface PlayerInfo {
  id: string;
  name: string;
  is_host: boolean;
}

export interface JoinRoomResponse {
  room_id: string;
  player_id: string;
  players_in_room: PlayerInfo[]
}

export interface StartGameResponse {
  room_id: string;
  status: string;
  starting_player_id: string;
  turn_order: string[];
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function handleResponse<T>(res: Response, notFoundMsg: string): Promise<T> {
  if (!res.ok) {
    if (res.status === 404) throw new ApiError(notFoundMsg, res.status);
    throw new ApiError("Something went wrong. Please try again.", res.status);
  }
  return res.json();
}

export async function createRoom(
  hostPlayerId: string,
  numPlayers: number
): Promise<CreateRoomResponse> {
  const res = await fetch(`${API_BASE}/rooms`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ host_player_id: hostPlayerId, num_players: numPlayers }),
  });
  return handleResponse(res, "Couldn't create the lobby.");
}

export async function joinRoom(roomId: string, playerId: string): Promise<JoinRoomResponse> {
  const res = await fetch(`${API_BASE}/rooms/${roomId}/join`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_id: playerId }),
  });
  return handleResponse(res, "Lobby not found. Check the code and try again.");
}

export async function startGame(roomId: string, playerId: string): Promise<StartGameResponse> {
  const res = await fetch(`${API_BASE}/rooms/${roomId}/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_id: playerId }),
  });
  return handleResponse(res, "Room not found.");
}