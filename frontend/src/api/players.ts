const API_BASE = import.meta.env.VITE_API_BASE;

export interface CreatePlayerResponse {
  nickname: string;
  player_id: string;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function createPlayer(nickname: string): Promise<CreatePlayerResponse> {
  const res = await fetch(`${API_BASE}/players`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nickname }),
  });

  if (!res.ok) {
    if (res.status === 409) {
      throw new ApiError("That username is taken.", res.status);
    }
    throw new ApiError("Something went wrong. Please try again.", res.status);
  }

  return res.json();
}