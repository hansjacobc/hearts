import { useGame } from "../context/GameContext";
import { useGameSocket } from "../useGameSocket";
import Hand from "../components/Hand";
import Trick from "../components/Trick";
import Scoreboard from "../components/Scoreboard";

const dummyHand = [
  { suit: "hearts", rank: "2" },
  { suit: "spades", rank: "Q" },
  { suit: "clubs", rank: "10" },
];

export default function Game() {
  const { state } = useGame();
  const status = useGameSocket(state.lobbyId, state.userId);

  return (
    <div className="min-h-screen bg-green-900 text-white p-6 flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-bold">Hearts — {state.lobbyId}</h1>
        <span className="text-sm opacity-70">Socket: {status}</span>
      </div>

      <Scoreboard players={state.players} />
      <Trick cards={[]} />
      <Hand cards={dummyHand} />
    </div>
  );
}