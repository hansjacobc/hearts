import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useGame } from "../context/GameContext";
import CardsBackdrop from "../components/CardsBackdrop";

export default function Welcome() {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { dispatch } = useGame();
  const navigate = useNavigate();

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setError(null);

    // TODO: replace with real backend call, e.g.
    // const res = await fetch(`${import.meta.env.VITE_API_BASE}/users`, { method: "POST", body: JSON.stringify({ name }) });
    // if (res.status === 409) { setError("That username is taken."); return; }
    // const { userId } = await res.json();
    const fakeUserId = crypto.randomUUID();

    dispatch({ type: "SET_USER", username: name, userId: fakeUserId });
    navigate("/lobby");
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
        />
        {error && <p className="text-red-600 text-sm -mt-2">{error}</p>}
        <button
          type="submit"
          className="bg-green-700 text-white rounded px-3 py-2 font-semibold hover:bg-green-800"
        >
          Continue
        </button>
      </form>
    </div>
  );
}