import Card from "./Card";

interface HandProps {
  cards: { suit: string; rank: string }[];
}

export default function Hand({ cards }: HandProps) {
  return (
    <div className="flex gap-2 justify-center">
      {cards.map((c, i) => (
        <Card key={i} suit={c.suit} rank={c.rank} onClick={() => console.log("play", c)} />
      ))}
    </div>
  );
}