import Card from "./Card";
import type { Seat } from "../hooks/useSeatLayout";

interface TableProps {
  seats: Seat[];
  handCounts: Record<string, number>;
  currentTurnPlayerId?: string;
}

const MAX_SPREAD_DEG = 40;
const ARC_DROP = 1;
const OVERLAP = 14;

export default function Table({ seats, handCounts, currentTurnPlayerId }: TableProps) {
  const opponents = seats.filter((s) => !s.isSelf);

  return (
    <>
      {opponents.map((seat) => {
        const count = handCounts[seat.player.id] ?? 0;
        const isTurn = seat.player.id === currentTurnPlayerId;

        // Same "toward center" logic as the seat itself: rotate the whole
        // fan so its bulge always points at the table, whichever side
        // this player is sitting on.
        const fanRotation = seat.angleDeg - 90;
        const mid = (count - 1) / 2;
        const stepDeg = count > 1 ? Math.min(MAX_SPREAD_DEG / (count - 1), 8) : 0;

        return (
          <div
            key={seat.player.id}
            className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-1"
            style={{ left: `${seat.xPct}%`, top: `${seat.yPct}%` }}
          >
            <div
              className={`px-2 py-0.5 rounded-full text-xs whitespace-nowrap z-10 ${
                isTurn ? "bg-yellow-400 text-green-950 font-semibold" : "bg-black/30 text-white/90"
              }`}
            >
              {seat.player.name}
              {seat.player.isHost ? " ♛" : ""}
            </div>

            <div style={{ transform: `rotate(${fanRotation}deg)` }}>
              <div className="flex items-center" style={{ height: 50 }}>
                {Array.from({ length: count }).map((_, i) => {
                  const offset = i - mid;
                  return (
                    <div key={i} style={{ marginLeft: i === 0 ? 0 : -OVERLAP }}>
                      <Card
                        faceDown
                        size="sm"
                        rotate={offset * stepDeg}
                        translateY={ARC_DROP * offset * offset}
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        );
      })}
    </>
  );
}