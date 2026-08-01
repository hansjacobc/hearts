interface ScoreboardPlayer {
  id: string;
  name: string;
  isHost: boolean;
}

interface ScoreboardProps {
  players: ScoreboardPlayer[];
  scores?: Record<string, number>;
}

export default function Scoreboard({ players, scores = {} }: ScoreboardProps) {
  return (
    <div className="absolute top-4 right-4 bg-black/30 backdrop-blur-sm rounded-lg overflow-hidden text-sm">
      <table className="border-collapse">
        <thead>
          <tr className="text-white/60 text-xs uppercase tracking-wide">
            <th className="text-left px-3 py-1.5 font-medium">Player</th>
            <th className="text-right px-3 py-1.5 font-medium">Pts</th>
          </tr>
        </thead>
        <tbody>
          {players.map((p) => (
            <tr key={p.id} className="border-t border-white/10">
              <td className="text-left px-3 py-1.5 whitespace-nowrap">
                {p.name}
                {p.isHost ? " ♛" : ""}
              </td>
              <td className="text-right px-3 py-1.5 tabular-nums">{scores[p.id] ?? 0}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}