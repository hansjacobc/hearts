import { useRef, useEffect } from "react";
import { motion, useMotionValue, useAnimationFrame } from "motion/react";

type CardSpec = { rank: string; suit: "hearts" | "spades" };

const HEARTS: CardSpec[] = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"].map(
  (rank) => ({ rank, suit: "hearts" as const })
);
const CARDS: CardSpec[] = [...HEARTS, { rank: "Q", suit: "spades" }];

const SPEED = 100; // px/s — identical for every card
const MARGIN = 120; // spawn buffer outside the viewport
const DESPAWN_MARGIN = MARGIN * 2;

function randomSpawn(w: number, h: number) {
  const edge = Math.floor(Math.random() * 4); // 0 top, 1 right, 2 bottom, 3 left
  const spread = (Math.PI / 180) * 50; // ±50° off the inward normal, so it actually crosses the screen
  let x = 0,
    y = 0,
    angle = 0;

  switch (edge) {
    case 0:
      x = Math.random() * w;
      y = -MARGIN;
      angle = Math.PI / 2 + (Math.random() * 2 - 1) * spread;
      break;
    case 1:
      x = w + MARGIN;
      y = Math.random() * h;
      angle = Math.PI + (Math.random() * 2 - 1) * spread;
      break;
    case 2:
      x = Math.random() * w;
      y = h + MARGIN;
      angle = -Math.PI / 2 + (Math.random() * 2 - 1) * spread;
      break;
    default:
      x = -MARGIN;
      y = Math.random() * h;
      angle = (Math.random() * 2 - 1) * spread;
  }

  const vx = Math.cos(angle) * SPEED;
  const vy = Math.sin(angle) * SPEED;
  // Card artwork's "top" (short edge) faces up by default (angle -90°).
  // Rotate so that top edge points along the direction of travel.
  const rotation = (Math.atan2(vy, vx) * 180) / Math.PI + 90;

  return { x, y, vx, vy, rotation };
}

function FloatingCard({ card }: { card: CardSpec }) {
  const bounds = useRef({ w: window.innerWidth, h: window.innerHeight });
  const state = useRef(randomSpawn(bounds.current.w, bounds.current.h));
  const reducedMotion = useRef(
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false
  );

  const x = useMotionValue(state.current.x);
  const y = useMotionValue(state.current.y);
  const rotate = useMotionValue(state.current.rotation);

  useEffect(() => {
    const onResize = () => {
      bounds.current = { w: window.innerWidth, h: window.innerHeight };
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  useAnimationFrame((_, delta) => {
    if (reducedMotion.current) return;

    const dt = Math.min(delta, 50) / 1000;
    const s = state.current;
    s.x += s.vx * dt;
    s.y += s.vy * dt;

    const { w, h } = bounds.current;
    const offscreen =
      s.x < -DESPAWN_MARGIN || s.x > w + DESPAWN_MARGIN || s.y < -DESPAWN_MARGIN || s.y > h + DESPAWN_MARGIN;

    if (offscreen) {
      state.current = randomSpawn(w, h);
      rotate.set(state.current.rotation);
    }

    // Always sync the DOM position to current state, whether this frame
    // just respawned the card or kept moving it — no more frozen frame.
    x.set(state.current.x);
    y.set(state.current.y);
  });

  return (
    <motion.img
      src={`/cards/basic/${card.rank}_${card.suit}.svg`}
      alt=""
      aria-hidden="true"
      className="absolute w-16 h-auto opacity-100 select-none pointer-events-none drop-shadow-md"
      style={{ x, y, rotate }}
    />
  );
}

export default function CardsBackdrop() {
  return (
    <div className="absolute inset-0 overflow-hidden" aria-hidden="true">
      {CARDS.map((card, i) => (
        <FloatingCard key={`${card.rank}-${card.suit}-${i}`} card={card} />
      ))}
    </div>
  );
}