import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGame } from "../context/GameContext";
import CardsBackdrop from "../components/CardsBackdrop";
import { createRoom, joinRoom, startGame, ApiError } from "../api/rooms";

export default function Lobby() {
  const { state, dispatch } = useGame();
  const [joinCode, setJoinCode] = useState("");
  const [numPlayers, setNumPlayers] = useState(4);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const isHost = state.players[0]?.id === state.userId;

  async function handleCreate() {
    if (submitting) return;
    setError(null);
    setSubmitting(true);
    try {
      const { room_id } = await createRoom(state.userId, numPlayers);
      dispatch({
        type: "SET_LOBBY",
        lobbyId: room_id,
        // TODO: other players will arrive via the socket once roster sync is wired up
        players: [{ id: state.userId, name: state.username, isHost: true }],
      });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't reach the server. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleJoin() {
    if (!joinCode.trim() || submitting) return;
    setError(null);
    setSubmitting(true);
    try {
      const { room_id } = await joinRoom(joinCode.trim(), state.userId);
      dispatch({
        type: "SET_LOBBY",
        lobbyId: room_id,
        // TODO: existing players in the room will arrive via the socket
        players: [{ id: state.userId, name: state.username, isHost: false }],
      });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't reach the server. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStart() {
    if (submitting) return;
    setError(null);
    setSubmitting(true);
    try {
      // TODO: starting_player_id / turn_order will matter once Game.tsx is wired up
      await startGame(state.lobbyId, state.userId);
      navigate("/game");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't reach the server. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!state.username) {
    navigate("/");
    return null;
  }

  return (
    <div className="relative h-screen w-screen flex items-center justify-center bg-green-900 overflow-hidden">
      <CardsBackdrop />
      <div className="relative z-10 bg-white rounded-xl p-8 shadow-lg w-96 flex flex-col gap-4">
        <h2 className="text-xl font-bold">Welcome, {state.username}</h2>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        {!state.lobbyId ? (
          <>
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-600">Players</label>
              <select
                className="border rounded px-2 py-1"
                value={numPlayers}
                onChange={(e) => setNumPlayers(Number(e.target.value))}
              >
                {[3, 4, 5, 6, 7, 8].map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </div>
            <button
              onClick={handleCreate}
              disabled={submitting}
              className="bg-green-700 text-white rounded px-3 py-2 font-semibold hover:bg-green-800 disabled:opacity-50"
            >
              {submitting ? "Creating..." : "Create Lobby"}
            </button>
            <div className="flex gap-2">
              <input
                className="border rounded px-3 py-2 flex-1"
                placeholder="Lobby code"
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value)}
                disabled={submitting}
              />
              <button
                onClick={handleJoin}
                disabled={submitting}
                className="bg-blue-700 text-white rounded px-3 py-2 font-semibold hover:bg-blue-800 disabled:opacity-50"
              >
                {submitting ? "Joining..." : "Join"}
              </button>
            </div>
          </>
        ) : (
          <>
            <p className="text-sm text-gray-500">
              Lobby code: <span className="font-mono font-bold">{state.lobbyId}</span>
            </p>
            <ul className="flex flex-col gap-1">
              {state.players.map((p) => (
                <li key={p.id} className="flex justify-between">
                  <span>{p.name}</span>
                  {p.isHost && <span className="text-xs text-gray-400">host</span>}
                </li>
              ))}
            </ul>
            {isHost && (
              <button
                onClick={handleStart}
                disabled={submitting}
                className="bg-green-700 text-white rounded px-3 py-2 font-semibold hover:bg-green-800 disabled:opacity-50"
              >
                {submitting ? "Starting..." : "Start Game"}
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
}