import { useEffect, useState } from "react";
import Card from "./Card";
import { sortCardIds, type SortMode } from "../utils/sortHand";

interface HandProps {
  cards: string[];
  onPlay?: (cardId: string) => void;
  disabled?: boolean;
}

const MAX_SPREAD_DEG = 34;
const ARC_DROP = 1;

export default function Hand({ cards, onPlay, disabled = false }: HandProps) {
  const [sortMode, setSortMode] = useState<SortMode>("rank");
  const [ordered, setOrdered] = useState<string[]>(() => sortCardIds(cards, "rank"));

  useEffect(() => {
    setOrdered(sortCardIds(cards, sortMode));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cards]);

  function applySort(mode: SortMode) {
    setSortMode(mode);
    setOrdered(sortCardIds(cards, mode));
  }

  const n = ordered.length;
  const mid = (n - 1) / 2;
  const stepDeg = n > 1 ? Math.min(MAX_SPREAD_DEG / (n - 1), 6) : 0;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="flex gap-2 text-xs">
        {(["suit", "rank", "random"] as SortMode[]).map((mode) => (
          <button
            key={mode}
            onClick={() => applySort(mode)}
            className={`px-3 py-1 rounded-full border transition-colors ${
              sortMode === mode
                ? "bg-white text-green-900 border-white"
                : "border-white/30 text-white/70 hover:border-white/60"
            }`}
          >
            {mode === "suit" ? "Suit" : mode === "rank" ? "Rank" : "Shuffle"}
          </button>
        ))}
      </div>

      <div className="flex items-end" style={{ height: 130 }}>
        {ordered.map((id, i) => {
          const [rank, suit] = id.split("_");
          const offset = i - mid;
          return (
            <div key={id} style={{ marginLeft: i === 0 ? 0 : -18 }}>
              <Card
                layoutId={id}
                rank={rank}
                suit={suit}
                rotate={offset * stepDeg}
                translateY={ARC_DROP * offset * offset}
                onClick={() => onPlay?.(id)}
                disabled={disabled}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}