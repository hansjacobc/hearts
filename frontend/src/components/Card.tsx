import { motion } from "motion/react";

interface CardProps {
  suit?: string;
  rank?: string;
  faceDown?: boolean;
  onClick?: () => void;
  rotate?: number;
  translateY?: number;
  size?: "sm" | "md" | "lg";
  layoutId?: string;
  disabled?: boolean;
}

const SIZE_CLASSES: Record<string, string> = {
  sm: "w-10 h-14",
  md: "w-16 h-24",
  lg: "w-20 h-30",
};

export default function Card({
  suit,
  rank,
  faceDown = false,
  onClick,
  rotate = 0,
  translateY = 0,
  size = "md",
  layoutId,
  disabled = false,
}: CardProps) {
  const src = faceDown ? "/cards/basic/card_back.svg" : `/cards/basic/${rank}_${suit}.svg`;
  const interactive = !faceDown && !disabled;

  return (
    <motion.img
      layoutId={layoutId}
      src={src}
      alt={faceDown ? "card back" : `${rank} of ${suit}`}
      onClick={interactive ? onClick : undefined}
      initial={false}
      animate={{ rotate, y: translateY }}
      whileHover={interactive ? { y: translateY - 14, zIndex: 20 } : undefined}
      transition={{ type: "spring", stiffness: 300, damping: 24 }}
      className={`${SIZE_CLASSES[size]} select-none drop-shadow-md rounded-sm ${
        interactive ? "cursor-pointer" : ""
      }`}
      draggable={false}
    />
  );
}