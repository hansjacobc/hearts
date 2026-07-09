import Card from "./Card";

interface TrickProps {
  cards: { suit: string; rank: string; playedBy: string }[];
}

export default function Trick({ cards }: TrickProps) {
  return (
    <div className="flex gap-2 justify-center min-h-32 items-center border-2 border-dashed border-white/20 rounded-lg">
      {cards.length === 0 && <span className="opacity-50">No cards played yet</span>}
      {cards.map((c, i) => (
        <Card key={i} suit={c.suit} rank={c.rank} />
      ))}
    </div>
  );
}