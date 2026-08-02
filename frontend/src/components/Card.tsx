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
  disabled?: boolean; // fully non-interactive (used for trick display cards)
  selected?: boolean;
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
  selected = false,
}: CardProps) {
  const src = faceDown ? "/cards/basic/card_back.svg" : `/cards/basic/${rank}_${suit}.svg`;
  const canHover = !faceDown && !disabled;
  const canClick = !faceDown && !disabled && Boolean(onClick);
  const liftY = translateY - 14;

  return (
    <motion.img
      layoutId={layoutId}
      src={src}
      alt={faceDown ? "card back" : `${rank} of ${suit}`}
      onClick={canClick ? onClick : undefined}
      initial={false}
      animate={{ rotate, y: selected ? liftY : translateY }}
      whileHover={canHover && !selected ? { y: liftY, zIndex: 20 } : undefined}
      transition={{ type: "spring", stiffness: 300, damping: 24 }}
      className={`${SIZE_CLASSES[size]} select-none drop-shadow-md rounded-sm ${
        canClick ? "cursor-pointer" : ""
      } ${selected ? "ring-4 ring-yellow-400 rounded-md" : ""}`}
      draggable={false}
    />
  );
}