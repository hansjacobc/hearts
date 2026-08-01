export type SortMode = "suit" | "rank" | "random";

const RANK_ORDER = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"];
const SUIT_ORDER = ["spades", "hearts", "clubs", "diamonds"];

function rankValue(rank: string) {
  return RANK_ORDER.indexOf(rank);
}
function suitValue(suit: string) {
  return SUIT_ORDER.indexOf(suit);
}

export function sortCardIds(cardIds: string[], mode: SortMode): string[] {
  const cards = [...cardIds];

  if (mode === "random") {
    for (let i = cards.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [cards[i], cards[j]] = [cards[j], cards[i]];
    }
    return cards;
  }

  return cards.sort((a, b) => {
    const [rankA, suitA] = a.split("_");
    const [rankB, suitB] = b.split("_");
    if (mode === "suit") {
      const suitDiff = suitValue(suitA) - suitValue(suitB);
      return suitDiff !== 0 ? suitDiff : rankValue(rankA) - rankValue(rankB);
    }
    const rankDiff = rankValue(rankA) - rankValue(rankB);
    return rankDiff !== 0 ? rankDiff : suitValue(suitA) - suitValue(suitB);
  });
}