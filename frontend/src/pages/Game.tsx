import { useEffect, useMemo, useRef, useState } from "react";
import { useGame } from "../context/GameContext";
import { useGameSocket } from "../useGameSocket";
import Hand from "../components/Hand";
import Trick from "../components/Trick";
import Scoreboard from "../components/Scoreboard";
import Table from "../components/Table";
import { useSeatLayout } from "../hooks/useSeatLayout";
import { mapTableState, mapScores, type RawTableState } from "../utils/mapServerState";
import { useNavigate } from "react-router-dom";

interface TrickCard {
  playerId: string;
  card: string;
}

export default function Game() {
  const { state, dispatch } = useGame();
  const navigate = useNavigate();

  const [trickCards, setTrickCards] = useState<TrickCard[]>([]);
  const [playError, setPlayError] = useState<string | null>(null);
  const trickEndHandledRef = useRef<string | null>(null);

  function handleSocketMessage(data: unknown) {
    if (typeof data !== "object" || data === null || !("type" in data)) return;
    const msg = data as { type: string; [key: string]: unknown };

    switch (msg.type) {
      case "your_hand": {
        if (Array.isArray(msg.hand)) dispatch({ type: "SET_HAND", hand: msg.hand as string[] });
        break;
      }
      case "state": {
        const raw = msg.state as RawTableState;
        dispatch({ type: "SET_TABLE_STATE", table: mapTableState(raw) });
        if (Array.isArray(raw.card_pile) && raw.card_pile.length > 0) {
          setTrickCards(raw.card_pile.map((p) => ({ playerId: p.player_id, card: p.card })));
        }
        break;
      }
      case "card_played": {
        const playerId = msg.player_id as string;
        const card = msg.card as string;
        setTrickCards((prev) =>
          prev.some((p) => p.playerId === playerId) ? prev : [...prev, { playerId, card }]
        );
        break;
      }
      case "trick_loser": {
        dispatch({ type: "TRICK_RESOLVED", losingPlayerId: msg.losing_player_id as string });
        send({ type: "get_scores" });
        // Leave the resolved trick visible for a beat before sweeping it.
        setTimeout(() => setTrickCards([]), 900);
        break;
      }
      case "scores": {
        dispatch({
          type: "SET_SCORES",
          scores: mapScores(msg.scores as Record<string, { round_score?: string; game_score?: string }>),
        });
        break;
      }
      case "error": {
        if (msg.reason === "invalid_play") {
          setPlayError((msg.message as string) ?? "You can't play that card.");
          send({ type: "get_my_hand" }); // resync in case optimistic removal was wrong
        }
        break;
      }
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
      send({ type: "get_state" });
      send({ type: "get_scores" });
    }
  }, [hasIdentity, status]);

  // Only the player who played the trick-ending card requests the resolution —
  // deterministic, so no race between clients is possible.
  useEffect(() => {
    if (!state.table) return;
    if (state.table.phase !== "TRICK_END") return;
    if (state.table.lastActionPlayerId !== state.userId) return;

    const key = `${state.table.lastAction}-${state.table.lastActionPlayerId}`;
    if (trickEndHandledRef.current === key) return;
    trickEndHandledRef.current = key;

    send({ type: "get_trick_loser" });
  }, [state.table, state.userId]);

  useEffect(() => {
    if (!playError) return;
    const t = setTimeout(() => setPlayError(null), 3000);
    return () => clearTimeout(t);
  }, [playError]);

  const seats = useSeatLayout(state.players, state.turnOrder, state.userId);

  const handCounts = useMemo(() => {
    const playedIds = new Set(trickCards.map((p) => p.playerId));
    const selfPlayed = playedIds.has(state.userId);
    const baseline = state.hand.length + (selfPlayed ? 1 : 0);

    const counts: Record<string, number> = {};
    for (const p of state.players) {
      counts[p.id] = baseline - (playedIds.has(p.id) ? 1 : 0);
    }
    return counts;
  }, [state.players, state.userId, state.hand.length, trickCards]);

  const gameScores = useMemo(() => {
    const out: Record<string, number> = {};
    for (const [id, s] of Object.entries(state.scores)) out[id] = s.gameScore;
    return out;
  }, [state.scores]);

  const isMyTurn =
    state.table?.currentTurnPlayerId === state.userId && state.table?.phase !== "TRICK_END";

  function handlePlayCard(cardId: string) {
    if (!isMyTurn) return;
    dispatch({ type: "REMOVE_CARD_FROM_HAND", card: cardId }); // optimistic
    send({ type: "play_card", card: cardId });
  }

  if (!hasIdentity) return null;

  return (
    <div className="relative min-h-screen w-screen bg-green-900 text-white overflow-hidden">
      <div className="absolute top-4 left-4 flex items-center gap-3">
        <h1 className="text-lg font-bold">Hearts — {state.lobbyId}</h1>
        <span className="text-xs opacity-60">Socket: {status}</span>
      </div>

      <Scoreboard players={state.players} scores={gameScores} />

      <div className="absolute inset-0">
        <div
          className="absolute rounded-[50%] border-4 border-green-950/40 bg-green-800/60 shadow-inner"
          style={{ left: "8%", right: "8%", top: "14%", bottom: "26%" }}
        />
        <Table seats={seats} handCounts={handCounts} currentTurnPlayerId={state.table?.currentTurnPlayerId} />
        <Trick plays={trickCards} seats={seats} />
      </div>

      {playError && (
        <div className="absolute bottom-40 left-1/2 -translate-x-1/2 bg-red-500/90 text-white text-sm px-4 py-2 rounded-lg shadow-lg">
          {playError}
        </div>
      )}

      <div
        className={`absolute bottom-4 left-1/2 -translate-x-1/2 rounded-2xl px-2 py-2 transition-shadow ${
          isMyTurn ? "shadow-[0_0_24px_6px_rgba(250,204,21,0.35)]" : ""
        }`}
      >
        <Hand cards={state.hand} onPlay={handlePlayCard} disabled={!isMyTurn} />
      </div>
    </div>
  );
}