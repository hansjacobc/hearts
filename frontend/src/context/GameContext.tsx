import { createContext, useContext, useEffect, useReducer, type ReactNode } from "react";

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
  turnOrder: string[];
  startingPlayerId: string;
  hand: string[];
  status: string;
}


type Action =
  | { type: "SET_USER"; username: string; userId: string }
  | { type: "SET_LOBBY_ID"; lobbyId: string }
  | { type: "MERGE_PLAYERS"; players: Player[] }
  | { type: "PLAYER_LEFT"; playerId: string }
  | { type: "GAME_STARTED"; turnOrder: string[]; startingPlayerId: string }
  | { type: "SET_HAND"; hand: string[] }
  | { type: "RESET" }
  | { type: "SET_PLAYERS"; players: Player[] }
  | { type: "SET_STATUS"; status: "waiting" | "in_progress" };


const initialState: GameState = {
  username: "",
  userId: "",
  lobbyId: "",
  players: [],
  turnOrder: [],
  startingPlayerId: "",
  hand: [],
  status: "",
};

function mergePlayers(existing: Player[], incoming: Player[]): Player[] {
  const byId = new Map(existing.map((p) => [p.id, p]));
  for (const p of incoming) {
    byId.set(p.id, p); // incoming wins on conflict (REST/socket data is authoritative)
  }
  return Array.from(byId.values());
}

function reducer(state: GameState, action: Action): GameState {
  switch (action.type) {
    case "SET_USER":
      return { ...state, username: action.username, userId: action.userId };
    case "SET_LOBBY_ID":
      return { ...state, lobbyId: action.lobbyId };
    case "MERGE_PLAYERS":
      return { ...state, players: mergePlayers(state.players, action.players) };
    case "PLAYER_LEFT":
      return { ...state, players: state.players.filter((p) => p.id !== action.playerId) };
    case "RESET":
      return initialState;
    case "GAME_STARTED":
      return { ...state, turnOrder: action.turnOrder, startingPlayerId: action.startingPlayerId };
    case "SET_HAND":
      return { ...state, hand: action.hand };
    case "SET_PLAYERS":
      return { ...state, players: action.players };
    case "SET_STATUS":
      return { ...state, status: action.status };
    default:
      return state;
  }
}

const GameContext = createContext
  <{ state: GameState; dispatch: React.Dispatch<Action> } | undefined
>(undefined);


const STORAGE_KEY = "hearts_session";

function loadInitialState(): GameState {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return initialState;
    const saved = JSON.parse(raw);
    return {
      ...initialState,
      username: saved.username ?? "",
      userId: saved.userId ?? "",
      lobbyId: saved.lobbyId ?? "",
      // players/hand/turnOrder intentionally NOT restored from storage —
      // they're re-fetched fresh via room_state once the socket reconnects,
      // since a stale cached roster could be wrong (someone left while we were gone)
    };
  } catch {
    return initialState;
  }
}

export function GameProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, undefined, loadInitialState);

  useEffect(() => {
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ username: state.username, userId: state.userId, lobbyId: state.lobbyId })
    );
  }, [state.username, state.userId, state.lobbyId]);

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