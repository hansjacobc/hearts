import { useEffect, useMemo, useState } from "react";
import { useGame } from "../context/GameContext";
import { useGameSocket } from "../useGameSocket";
import Hand from "../components/Hand";
import Trick from "../components/Trick";
import Scoreboard from "../components/Scoreboard";
import Table from "../components/Table";
import { useSeatLayout } from "../hooks/useSeatLayout";
import { useNavigate } from "react-router-dom";

export default function Game() {
  const { state, dispatch } = useGame();
  const navigate = useNavigate();

  function handleSocketMessage(data: unknown) {
    if (typeof data !== "object" || data === null || !("type" in data)) return;
    const msg = data as { type: string; [key: string]: unknown };

    if (msg.type === "your_hand" && Array.isArray(msg.hand)) {
      dispatch({ type: "SET_HAND", hand: msg.hand as string[] });
    }
  }

  const hasIdentity = Boolean(state.username && state.lobbyId);

  const { status, send } = useGameSocket(
    hasIdentity ? state.lobbyId : "",
    hasIdentity ? state.userId : "",
    handleSocketMessage
  );

  useEffect(() => {
    if (!hasIdentity) {
      navigate("/");
      return;
    }
    if (status === "connected") {
      send({ type: "get_my_hand" });
    }
  }, [hasIdentity, status]);

  const seats = useSeatLayout(state.players, state.turnOrder, state.userId);

  // No trick data from the server yet — Trick renders correctly once
  // real { playerId, card } plays start flowing in over the socket.
  const [demoPlays] = useState<{ playerId: string; card: string }[]>([]);

  // Baseline = hand size at the *start* of the current trick, derived from
  // your own real count plus whether you've already played this trick.
  // Everyone shares that baseline except players who've already played,
  // who are down by 1 — this stays correct once `demoPlays` is replaced
  // with real per-trick play data from the socket.
  const handCounts = useMemo(() => {
    const playedIds = new Set(demoPlays.map((p) => p.playerId));
    const selfPlayed = playedIds.has(state.userId);
    const baseline = state.hand.length + (selfPlayed ? 1 : 0);

    const counts: Record<string, number> = {};
    for (const p of state.players) {
      counts[p.id] = baseline - (playedIds.has(p.id) ? 1 : 0);
    }
    return counts;
  }, [state.players, state.userId, state.hand.length, demoPlays]);



  if (!hasIdentity) return null;

  return (
    <div className="relative min-h-screen w-screen bg-green-900 text-white overflow-hidden">
      <div className="absolute top-4 left-4 flex items-center gap-3">
        <h1 className="text-lg font-bold">Hearts — {state.lobbyId}</h1>
        <span className="text-xs opacity-60">Socket: {status}</span>
      </div>

      <Scoreboard players={state.players} />

      <div className="absolute inset-0">
        <div
          className="absolute rounded-[50%] border-4 border-green-950/40 bg-green-800/60 shadow-inner"
          style={{ left: "8%", right: "8%", top: "14%", bottom: "26%" }}
        />
        <Table seats={seats} handCounts={handCounts} />
        <Trick plays={demoPlays} seats={seats} />
      </div>

      <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
        <Hand
          cards={state.hand}
          onPlay={(cardId) => console.log("would play:", cardId, "— play_card isn't wired server-side yet")}
        />
      </div>
    </div>
  );
}