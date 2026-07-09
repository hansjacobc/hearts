import { createContext, useContext, useReducer, type ReactNode } from "react";

interface Player {
  id: string;
  name: string;
  isHost: boolean;
}

interface GameState {
  username: string;
  userId: string;
  lobbyId: string;
  players: Player[];
}

type Action =
  | { type: "SET_USER"; username: string; userId: string }
  | { type: "SET_LOBBY"; lobbyId: string; players: Player[] }
  | { type: "RESET" };

const initialState: GameState = {
  username: "",
  userId: "",
  lobbyId: "",
  players: [],
};

function reducer(state: GameState, action: Action): GameState {
  switch (action.type) {
    case "SET_USER":
      return { ...state, username: action.username, userId: action.userId };
    case "SET_LOBBY":
      return { ...state, lobbyId: action.lobbyId, players: action.players };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

const GameContext = createContext<
  { state: GameState; dispatch: React.Dispatch<Action> } | undefined
>(undefined);

export function GameProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    <GameContext.Provider value={{ state, dispatch }}>
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  const ctx = useContext(GameContext);
  if (!ctx) throw new Error("useGame must be used within GameProvider");
  return ctx;
}