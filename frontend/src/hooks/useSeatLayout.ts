interface Player {
  id: string;
  name: string;
  isHost: boolean;
}

export interface Seat {
  player: Player;
  xPct: number;
  yPct: number;
  angleDeg: number; // 0 = right, 90 = bottom, 180 = left, 270 = top
  isSelf: boolean;
}

export function useSeatLayout(
  players: Player[],
  turnOrder: string[],
  selfId: string,
  radiusX = 42,
  radiusY = 36
): Seat[] {
  // Fall back to lobby roster order if turnOrder hasn't arrived yet (e.g. mid-lobby).
  const order = turnOrder.length === players.length ? turnOrder : players.map((p) => p.id);

  const selfIndex = order.indexOf(selfId);
  const rotated =
    selfIndex >= 0 ? [...order.slice(selfIndex), ...order.slice(0, selfIndex)] : order;

  const n = rotated.length || 1;

  return rotated.map((id, i) => {
    const player = players.find((p) => p.id === id) ?? { id, name: id, isHost: false };
    const angleDeg = 90 + (360 / n) * i; // i = 0 (self) starts at bottom, goes clockwise
    const rad = (angleDeg * Math.PI) / 180;
    return {
      player,
      xPct: 50 + radiusX * Math.cos(rad),
      yPct: 50 + radiusY * Math.sin(rad),
      angleDeg,
      isSelf: id === selfId,
    };
  });
}