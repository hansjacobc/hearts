import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGame } from "../context/GameContext";
import CardsBackdrop from "../components/CardsBackdrop";

export default function Lobby() {
  const { state, dispatch } = useGame();
  const [joinCode, setJoinCode] = useState("");
  const navigate = useNavigate();

  const isHost = state.players[0]?.id === state.userId;

  function handleCreate() {
    // TODO: replace with real backend call to create a lobby
    const fakeLobbyId = Math.random().toString(36).slice(2, 8).toUpperCase();
    dispatch({
      type: "SET_LOBBY",
      lobbyId: fakeLobbyId,
      players: [{ id: state.userId, name: state.username, isHost: true }],
    });
  }

  function handleJoin() {
    if (!joinCode.trim()) return;
    // TODO: replace with real backend call to join a lobby
    dispatch({
      type: "SET_LOBBY",
      lobbyId: joinCode.toUpperCase(),
      players: [
        { id: state.userId, name: state.username, isHost: false },
        { id: "dummy-1", name: "Alice", isHost: true },
      ],
    });
  }

  function handleStart() {
    // TODO: send "start game" message over the socket
    navigate("/game");
  }

  if (!state.username) {
    navigate("/");
    return null;
  }

  return (
    <div className="relative h-screen w-screen flex items-center justify-center bg-green-900 overflow-hidden">
      <CardsBackdrop />
        <div className="relative z-10 bg-white rounded-xl p-8 shadow-lg w-96 flex flex-col gap-4">          <h2 className="text-xl font-bold">Welcome, {state.username}</h2>
          {!state.lobbyId ? (
            <>
              <button
                onClick={handleCreate}
                className="bg-green-700 text-white rounded px-3 py-2 font-semibold hover:bg-green-800"
              >
                Create Lobby
              </button>
              <div className="flex gap-2">
                <input
                  className="border rounded px-3 py-2 flex-1"
                  placeholder="Lobby code"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value)}
                />
                <button
                  onClick={handleJoin}
                  className="bg-blue-700 text-white rounded px-3 py-2 font-semibold hover:bg-blue-800"
                >
                  Join
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
                  className="bg-green-700 text-white rounded px-3 py-2 font-semibold hover:bg-green-800"
                >
                  Start Game
                </button>
              )}
            </>
          )}
        </div>
    </div>
  );
}