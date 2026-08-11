import { createContext, useContext, useEffect, useReducer, type ReactNode } from "react";
import type { TableState, PlayerScore } from "../utils/mapServerState";

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
  table: TableState | null;
  scores: Record<string, PlayerScore>;
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
  | { type: "SET_STATUS"; status: "waiting" | "in_progress" }
  | { type: "SET_TABLE_STATE"; table: TableState }
  | { type: "TRICK_RESOLVED"; losingPlayerId: string }
  | { type: "DEAL_ENDED" }
  | { type: "SET_SCORES"; scores: Record<string, PlayerScore> }
  | { type: "REMOVE_CARDS_FROM_HAND"; cards: string[] }
  | { type: "ADD_CARDS_TO_HAND"; cards: string[] };

const initialState: GameState = {
  username: "",
  userId: "",
  lobbyId: "",
  players: [],
  turnOrder: [],
  startingPlayerId: "",
  hand: [],
  status: "",
  table: null,
  scores: {},
};

function mergePlayers(existing: Player[], incoming: Player[]): Player[] {
  const byId = new Map(existing.map((p) => [p.id, p]));
  for (const p of incoming) byId.set(p.id, p);
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
    case "SET_TABLE_STATE":
      return { ...state, table: action.table };
    case "TRICK_RESOLVED":
      return state.table
        ? {
            ...state,
            table: {
              ...state.table,
              currentTurnPlayerId: action.losingPlayerId,
              phase: "PLAYING",
              leadSuit: "OPEN",
            },
          }
        : state;
    case "DEAL_ENDED":
      return state.table ? { ...state, table: { ...state.table, phase: "DEAL_END", leadSuit: "OPEN" } } : state;
    case "SET_SCORES":
      return { ...state, scores: action.scores };
    case "REMOVE_CARDS_FROM_HAND": {
      const removeSet = new Set(action.cards);
      return { ...state, hand: state.hand.filter((c) => !removeSet.has(c)) };
    }
    case "ADD_CARDS_TO_HAND":
      return { ...state, hand: [...state.hand, ...action.cards] };
    default:
      return state;
  }
}

const GameContext = createContext<{ state: GameState; dispatch: React.Dispatch<Action> } | undefined>(
  undefined
);

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

  return <GameContext.Provider value={{ state, dispatch }}>{children}</GameContext.Provider>;
}

export function useGame() {
  const ctx = useContext(GameContext);
  if (!ctx) throw new Error("useGame must be used within GameProvider");
  return ctx;
}