import { useEffect } from "react";
import { useGame } from "../context/GameContext";
import { useGameSocket } from "../useGameSocket";
import Hand from "../components/Hand";
import Trick from "../components/Trick";
import Scoreboard from "../components/Scoreboard";
import { useNavigate } from "react-router-dom";

function parseCard(cardId: string): { rank: string; suit: string } {
  const [rank, suit] = cardId.split("_");
  return { rank, suit };
}

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

  if (!hasIdentity) return null;

  const hand = state.hand.map(parseCard);

  return (
    <div className="min-h-screen bg-green-900 text-white p-6 flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-bold">Hearts — {state.lobbyId}</h1>
        <span className="text-sm opacity-70">Socket: {status}</span>
      </div>

      <Scoreboard players={state.players} />
      <Trick cards={[]} />
      <Hand cards={hand} />
    </div>
  );
}