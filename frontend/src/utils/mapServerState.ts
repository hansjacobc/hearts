export interface RawTableState {
  phase: string;
  turn_number: number;
  round_number: number;
  game_number: number;
  current_turn_player_id: string;
  is_hearts_broken: boolean;
  lead_suit: string;
  last_action: string;
  last_action_player_id: string;
  direction: "LEFT" | "RIGHT" | "KEEP";
  card_pile?: { player_id: string; card: string }[];
}

export interface TableState {
  phase: string;
  turnNumber: number;
  roundNumber: number;
  gameNumber: number;
  currentTurnPlayerId: string;
  isHeartsBroken: boolean;
  leadSuit: string;
  lastAction: string;
  lastActionPlayerId: string;
  direction: "LEFT" | "RIGHT" | "KEEP";
}

export function mapTableState(raw: RawTableState): TableState {
  return {
    phase: raw.phase,
    turnNumber: raw.turn_number,
    roundNumber: raw.round_number,
    gameNumber: raw.game_number,
    currentTurnPlayerId: raw.current_turn_player_id,
    isHeartsBroken: raw.is_hearts_broken,
    leadSuit: raw.lead_suit,
    lastAction: raw.last_action,
    lastActionPlayerId: raw.last_action_player_id,
    direction: raw.direction,
  };
}

export interface PlayerScore {
  roundScore: number;
  gameScore: number;
}

export function mapScores(
  raw: Record<string, { round_score?: string; game_score?: string }>
): Record<string, PlayerScore> {
  const result: Record<string, PlayerScore> = {};
  for (const [playerId, s] of Object.entries(raw)) {
    result[playerId] = {
      roundScore: Number(s.round_score ?? 0),
      gameScore: Number(s.game_score ?? 0),
    };
  }
  return result;
}

export function mapGameScoresOnly(
  raw: Record<string, number>,
  existing: Record<string, PlayerScore>
): Record<string, PlayerScore> {
  const result: Record<string, PlayerScore> = { ...existing };
  for (const [playerId, gameScore] of Object.entries(raw)) {
    result[playerId] = { roundScore: 0, gameScore };
  }
  return result;
}