import { useEffect, useMemo, useRef, useState } from "react";
import { useGame } from "../context/GameContext";
import { useGameSocket } from "../useGameSocket";
import Hand from "../components/Hand";
import Trick from "../components/Trick";
import Scoreboard from "../components/Scoreboard";
import Table from "../components/Table";
import { useSeatLayout } from "../hooks/useSeatLayout";
import { mapTableState, mapScores, type RawTableState, mapGameScoresOnly } from "../utils/mapServerState";
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

  const [passedPlayerIds, setPassedPlayerIds] = useState<Set<string>>(new Set());
  const passingRoundRef = useRef<number | null>(null); // which round_number we've already handled KEEP-autosend for

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
      case "pass_cards": {
        if (msg.message === "done_passing") {
          setPassedPlayerIds((prev) => new Set(prev).add(msg.player_id as string));
        }
        break;
      }
      case "cards_received": {
        if (Array.isArray(msg.cards)) {
          dispatch({ type: "ADD_CARDS_TO_HAND", cards: msg.cards as string[] });
        }
        break;
      }
      case "deal_over": {
        dispatch({
          type: "SET_SCORES",
          scores: mapGameScoresOnly(msg.scores as Record<string, number>, state.scores),
        });
        break;
      }
      case "error": {
        if (msg.reason === "invalid_play" || msg.reason === "invalid_pass") {
          setPlayError((msg.message as string) ?? "That's not allowed right now.");
          send({ type: "get_my_hand" }); // resync in case an optimistic update was wrong
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

  // Reset the "who's passed" tracker whenever we enter a fresh passing round.
  useEffect(() => {
    if (state.table?.phase === "PASSING") {
      setPassedPlayerIds(new Set());
    }
  }, [state.table?.roundNumber, state.table?.gameNumber, state.table?.phase]);

  // KEEP rounds need no card selection — auto-send once per round so the
  // phase can advance without requiring a pointless click.
  useEffect(() => {
    if (state.table?.phase !== "PASSING") return;
    if (state.table.direction !== "KEEP") return;
    if (passingRoundRef.current === state.table.roundNumber) return;
    passingRoundRef.current = state.table.roundNumber;
    send({ type: "pass_cards", cards_to_pass: [] });
  }, [state.table?.phase, state.table?.direction, state.table?.roundNumber]);

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

  const prevPhaseRef = useRef<string | null>(null);

  // Passing is a multi-party operation — trust the server's final hand
  // rather than trying to reconstruct it from cards_received/optimistic
  // removal, which only need to be "roughly right" for the pass UI itself.
  useEffect(() => {
    const prevPhase = prevPhaseRef.current;
    const currentPhase = state.table?.phase ?? null;
    if (prevPhase === "PASSING" && currentPhase === "PLAYING") {
      send({ type: "get_my_hand" });
    }
    if (prevPhase === "DEAL_END" && currentPhase === "PASSING") {
      send({ type: "get_my_hand" });
    }
    prevPhaseRef.current = currentPhase;
  }, [state.table?.phase]);

  const seats = useSeatLayout(state.players, state.turnOrder, state.userId);

  const handCounts = useMemo(() => {
    const playedIds = new Set(trickCards.map((p) => p.playerId));
    const selfPlayed = playedIds.has(state.userId);
    const baseline = state.hand.length + (selfPlayed ? 1 : 0);
    const counts: Record<string, number> = {};
    for (const p of state.players) counts[p.id] = baseline - (playedIds.has(p.id) ? 1 : 0);
    return counts;
  }, [state.players, state.userId, state.hand.length, trickCards]);

  const gameScores = useMemo(() => {
    const out: Record<string, number> = {};
    for (const [id, s] of Object.entries(state.scores)) out[id] = s.gameScore;
    return out;
  }, [state.scores]);

  const isPassing = state.table?.phase === "PASSING";
  const isMyTurn =
    state.table?.currentTurnPlayerId === state.userId && state.table?.phase === "PLAYING";
  const hasPassed = passedPlayerIds.has(state.userId);

  function handlePlayCard(cards: string[]) {
    const [cardId] = cards;
    dispatch({ type: "REMOVE_CARDS_FROM_HAND", cards: [cardId] }); // optimistic
    send({ type: "play_card", card: cardId });
  }

  function handlePassCards(cards: string[]) {
    dispatch({ type: "REMOVE_CARDS_FROM_HAND", cards }); // optimistic
    send({ type: "pass_cards", cards_to_pass: cards });
  }

  const isDealOver = state.table?.phase === "DEAL_END";
  const isHost = state.players.find((p) => p.id === state.userId)?.isHost ?? false;

  function handleDealAgain() {
    send({ type: "shuffle_and_deal" });
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
        <div className="absolute bottom-[220px] left-1/2 -translate-x-1/2 z-50 bg-red-500/90 text-white text-sm px-4 py-2 rounded-lg shadow-lg whitespace-nowrap">
          {playError}
        </div>
      )}

      <div
        className={`absolute bottom-4 left-1/2 -translate-x-1/2 rounded-2xl px-2 py-2 transition-shadow ${
          isMyTurn ? "shadow-[0_0_24px_6px_rgba(250,204,21,0.35)]" : ""
        }`}
      >
        {isDealOver ? (
          <div className="flex flex-col items-center gap-3 py-6">
            <span className="text-white/80 text-sm">Deal over — final scores are in.</span>
            {isHost ? (
              <button
                onClick={handleDealAgain}
                className="px-5 py-2 rounded-full font-semibold bg-yellow-400 text-green-950 hover:bg-yellow-300 transition-colors"
              >
                Deal again
              </button>
            ) : (
              <span className="text-white/50 text-xs">Waiting for the host to deal again…</span>
            )}
          </div>
        ) : isPassing ? (
          state.table?.direction === "KEEP" ? (
            <div className="text-center text-white/70 text-sm py-6">
              No passing this round — waiting for everyone to be ready…
            </div>
          ) : (
            <Hand
              cards={state.hand}
              onConfirm={handlePassCards}
              confirmLabel={`Pass ${state.table?.direction?.toLowerCase() ?? ""}`}
              maxSelected={3}
              requireExact
              disabled={hasPassed}
              helperText={
                hasPassed
                  ? `Waiting on ${state.players.length - passedPlayerIds.size} more…`
                  : undefined
              }
            />
          )
        ) : (
          <Hand
            cards={state.hand}
            onConfirm={handlePlayCard}
            confirmLabel="Play card"
            maxSelected={1}
            disabled={!isMyTurn}
          />
        )}
      </div>
    </div>
  );
}