import { motion, AnimatePresence } from "motion/react";
import Card from "./Card";
import type { Seat } from "../hooks/useSeatLayout";

interface PlayedCard {
  playerId: string;
  card: string; // "rank_suit"
}

interface TrickProps {
  plays: PlayedCard[];
  seats: Seat[];
  winnerId?: string | null; // when set, cards exit toward this player's seat (trick/deal collected)
}

function hash(str: string): number {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) | 0;
  return Math.abs(h);
}

export default function Trick({ plays, seats, winnerId }: TrickProps) {
  const seatById = new Map(seats.map((s) => [s.player.id, s]));
  const winnerSeat = winnerId ? seatById.get(winnerId) : undefined;

  return (
    <div className="relative w-full h-full">
      {plays.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center text-white/40 text-sm">
          No cards played yet
        </div>
      )}
      <AnimatePresence>
        {plays.map(({ playerId, card }) => {
          const seat = seatById.get(playerId);
          if (!seat) return null;

          const h1 = hash(card + playerId);
          const h2 = hash(playerId + card);
          const towardX = (seat.xPct - 50) * 0.35;
          const towardY = (seat.yPct - 50) * 0.35;
          const jitterX = ((h1 % 100) / 100 - 0.5) * 18;
          const jitterY = ((h2 % 100) / 100 - 0.5) * 18;
          const destXPct = 50 + towardX + jitterX;
          const destYPct = 50 + towardY + jitterY;
          const settleRotate = ((h1 % 60) - 30) / 2;

          // Collected exit: cards sweep toward the trick winner's seat and
          // shrink away as if being scooped into their hand. Falls back to
          // the old fade-in-place if we ever don't have a winner seat.
          const exit = winnerSeat
            ? {
                left: `${winnerSeat.xPct}%`,
                top: `${winnerSeat.yPct}%`,
                opacity: 0,
                scale: 0.4,
                rotate: settleRotate,
              }
            : { opacity: 0, scale: 0.7 };

          return (
            <motion.div
              key={card + playerId}
              className="absolute"
              initial={{ left: `${seat.xPct}%`, top: `${seat.yPct}%`, opacity: 0, scale: 0.6 }}
              animate={{
                left: `${destXPct}%`,
                top: `${destYPct}%`,
                opacity: 1,
                scale: 1,
                rotate: settleRotate,
              }}
              exit={exit}
              transition={{ type: "spring", stiffness: 220, damping: 20 }}
            >
              <div className="-translate-x-1/2 -translate-y-1/2">
                <Card rank={card.split("_")[0]} suit={card.split("_")[1]} size="lg" disabled />
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}