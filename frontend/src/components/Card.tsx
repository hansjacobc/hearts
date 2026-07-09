interface CardProps {
  suit: string;
  rank: string;
  onClick?: () => void;
}

export default function Card({ suit, rank, onClick }: CardProps) {
  const src = `/cards/basic/${rank}_${suit}.svg`;

  return (
    <img
      src={src}
      alt={`${rank}_${suit}`}
      onClick={onClick}
      className="w-16 h-24 cursor-pointer hover:-translate-y-2 transition-transform"
    />
  );
}