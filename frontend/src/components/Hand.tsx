import { useEffect, useState } from "react";
import Card from "./Card";
import { sortCardIds, type SortMode } from "../utils/sortHand";

interface HandProps {
  cards: string[];
  onConfirm: (cards: string[]) => void;
  confirmLabel: string;
  maxSelected?: number;   // 1 for playing a card, 3 for passing
  requireExact?: boolean; // true for passing: must select exactly maxSelected
  disabled?: boolean;     // true when action isn't currently allowed
  helperText?: string;    // e.g. "Waiting on 2 of 3 players to pass..."
}

const MAX_SPREAD_DEG = 34;
const ARC_DROP = 1;

export default function Hand({
  cards,
  onConfirm,
  confirmLabel,
  maxSelected = 1,
  requireExact = false,
  disabled = false,
  helperText,
}: HandProps) {
  const [sortMode, setSortMode] = useState<SortMode>("rank");
  const [ordered, setOrdered] = useState<string[]>(() => sortCardIds(cards, "rank"));
  const [selected, setSelected] = useState<string[]>([]);

  useEffect(() => {
    setOrdered(sortCardIds(cards, sortMode));
    setSelected((prev) => prev.filter((c) => cards.includes(c)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cards]);

  function applySort(mode: SortMode) {
    setSortMode(mode);
    setOrdered(sortCardIds(cards, mode));
  }

  function toggleSelect(cardId: string) {
    setSelected((prev) => {
      if (prev.includes(cardId)) return prev.filter((c) => c !== cardId);
      if (maxSelected === 1) return [cardId]; // single-select replaces
      if (prev.length >= maxSelected) return prev; // multi-select caps out
      return [...prev, cardId];
    });
  }

  function handleConfirm() {
    if (disabled) return;
    const ready = requireExact ? selected.length === maxSelected : selected.length >= 1;
    if (!ready) return;
    onConfirm(selected);
    setSelected([]);
  }

  const canConfirm =
    !disabled && (requireExact ? selected.length === maxSelected : selected.length >= 1);

  const n = ordered.length;
  const mid = (n - 1) / 2;
  const stepDeg = n > 1 ? Math.min(MAX_SPREAD_DEG / (n - 1), 6) : 0;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="flex items-center gap-3 text-xs">
        <div className="flex gap-2">
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

        {helperText && <span className="text-white/60">{helperText}</span>}

        <button
          onClick={handleConfirm}
          disabled={!canConfirm}
          className={`px-4 py-1 rounded-full font-semibold transition-colors ${
            canConfirm
              ? "bg-yellow-400 text-green-950 hover:bg-yellow-300"
              : "bg-white/10 text-white/30 cursor-not-allowed"
          }`}
        >
          {confirmLabel}
          {maxSelected > 1 ? ` (${selected.length}/${maxSelected})` : ""}
        </button>
      </div>

      <div className="flex items-end" style={{ height: 130 }}>
        {ordered.map((id, i) => {
          const [rank, suit] = id.split("_");
          const offset = i - mid;
          const isSelected = selected.includes(id);
          return (
            <div key={id} style={{ marginLeft: i === 0 ? 0 : -18, zIndex: isSelected ? 30 : i }}>
              <Card
                layoutId={id}
                rank={rank}
                suit={suit}
                rotate={offset * stepDeg}
                translateY={ARC_DROP * offset * offset}
                onClick={() => toggleSelect(id)}
                selected={isSelected}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}