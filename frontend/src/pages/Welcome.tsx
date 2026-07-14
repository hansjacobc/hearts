import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGame } from "../context/GameContext";

export default function Welcome() {
  const [name, setName] = useState("");
  const { dispatch } = useGame();
  const navigate = useNavigate();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;

    // TODO: replace with real backend call, e.g.
    // const res = await fetch(`${import.meta.env.VITE_API_BASE}/users`, { method: "POST", body: JSON.stringify({ name }) });
    // const { userId } = await res.json();
    const fakeUserId = crypto.randomUUID();

    dispatch({ type: "SET_USER", username: name, userId: fakeUserId });
    navigate("/lobby");
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-green-900">
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-xl p-8 shadow-lg flex flex-col gap-4 w-80"
      >
        <h1 className="text-2xl font-bold text-center">Hearts</h1>
        <input
          className="border rounded px-3 py-2"
          placeholder="Enter a username"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
        />
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