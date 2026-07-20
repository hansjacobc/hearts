import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useGame } from "../context/GameContext";
import CardsBackdrop from "../components/CardsBackdrop";
import { createPlayer, ApiError } from "../api/players";

export default function Welcome() {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const { dispatch } = useGame();
  const navigate = useNavigate();

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim() || submitting) return;
    setError(null);
    setSubmitting(true);

    try {
      const { player_id, nickname } = await createPlayer(name.trim());
      dispatch({ type: "SET_USER", username: nickname, userId: player_id });
      navigate("/lobby");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Couldn't reach the server. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="relative h-screen w-screen flex items-center justify-center bg-green-900 overflow-hidden">
      <CardsBackdrop />

      <form
        onSubmit={handleSubmit}
        className="relative z-10 bg-white rounded-xl p-8 shadow-lg flex flex-col gap-4 w-[clamp(280px,25vw,420px)]"
      >
        <h1 className="text-2xl font-bold text-center">Hearts</h1>
        <input
          className="border rounded px-3 py-2"
          placeholder="Enter a username"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
          disabled={submitting}
        />
        {error && <p className="text-red-600 text-sm -mt-2">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="bg-green-700 text-white rounded px-3 py-2 font-semibold hover:bg-green-800 disabled:opacity-50"
        >
          {submitting ? "Joining..." : "Continue"}
        </button>
      </form>
    </div>
  );
}