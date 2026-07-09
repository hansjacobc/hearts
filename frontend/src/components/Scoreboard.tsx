interface ScoreboardProps {
  players: { id: string; name: string }[];
}

export default function Scoreboard({ players }: ScoreboardProps) {
  return (
    <div className="flex gap-4 justify-center text-sm">
      {players.map((p) => (
        <div key={p.id} className="bg-white/10 rounded px-3 py-1">
          {p.name}: 0 pts
        </div>
      ))}
    </div>
  );
}