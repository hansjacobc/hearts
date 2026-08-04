import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import Card from "./Card";
import type { Seat } from "../hooks/useSeatLayout";

interface DealAnimationProps {
  active: boolean;
  seats: Seat[];
  durationMs?: number; // total time for the whole deal, default 2s
}

interface Flight {
  id: string;
  seat: Seat;
  delaySec: number;
}

const DEFAULT_DURATION_MS = 2000;
const FLIGHT_DURATION_MS = 260; // how long a single card takes to travel
const DEFAULT_CARDS_PER_PLAYER = 13; // standard Hearts hand size (52 / 4 players)

function hash(str: string): number {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) | 0;
  return Math.abs(h);
}

export default function DealAnimation({ active, seats, durationMs = DEFAULT_DURATION_MS }: DealAnimationProps) {
  const [flights, setFlights] = useState<Flight[]>([]);

  const seatKey = seats.map((s) => s.player.id).join(",");

  useEffect(() => {
    if (!active || seats.length === 0) {
      setFlights([]);
      return;
    }

    const cardsPerPlayer = Math.max(1, Math.floor(52 / seats.length)) || DEFAULT_CARDS_PER_PLAYER;
    const totalFlights = cardsPerPlayer * seats.length;
    // Spread every flight's start time evenly across the animation window so
    // the whole deal — no matter how many cards — takes ~durationMs total.
    const interval = totalFlights > 1 ? (durationMs - FLIGHT_DURATION_MS) / (totalFlights - 1) : 0;

    const built: Flight[] = [];
    let i = 0;
    for (let round = 0; round < cardsPerPlayer; round++) {
      // One card to each seat per round, in turn order — same rhythm as a real dealer going around the table.
      for (const seat of seats) {
        built.push({ id: `${round}-${seat.player.id}`, seat, delaySec: (i * interval) / 1000 });
        i++;
      }
    }
    setFlights(built);
    // seats itself is a fresh array reference every render (useSeatLayout isn't
    // memoized) — key off a stable string instead, or this restarts mid-flight
    // on every unrelated parent re-render while the animation is active.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active, seatKey, durationMs]);

  if (!active || flights.length === 0) return null;

  return (
    <div className="absolute inset-0 pointer-events-none z-30">
      {/* Static stack at center representing the deck being dealt from */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="absolute" style={{ transform: `translate(${i}px, ${-i}px)` }}>
            <Card faceDown size="md" disabled />
          </div>
        ))}
      </div>

      <AnimatePresence>
        {flights.map((f) => {
          const h = hash(f.id);
          const settleRotate = (h % 40) - 20;
          return (
            <motion.div
              key={f.id}
              className="absolute"
              initial={{ left: "50%", top: "50%", opacity: 0, scale: 0.9, rotate: 0 }}
              animate={{
                left: `${f.seat.xPct}%`,
                top: `${f.seat.yPct}%`,
                opacity: [0, 1, 1, 0],
                scale: 1,
                rotate: settleRotate,
              }}
              transition={{ duration: FLIGHT_DURATION_MS / 1000, delay: f.delaySec, ease: "easeOut" }}
            >
              <div className="-translate-x-1/2 -translate-y-1/2">
                <Card faceDown size="sm" disabled />
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}