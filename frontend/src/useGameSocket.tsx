import { useEffect, useState } from "react";

export function useGameSocket(roomId: string, playerId: string) {
  const [status, setStatus] = useState("connecting");

  useEffect(() => {
    if (!roomId || !playerId) return;

    const url = `${import.meta.env.VITE_WS_BASE}/${roomId}/${playerId}`;
    const ws = new WebSocket(url);

    ws.onopen = () => setStatus("connected");
    ws.onclose = () => setStatus("disconnected");
    ws.onerror = () => setStatus("error");
    ws.onmessage = (event) => {
      console.log("received:", event.data);
    };

    return () => ws.close();
  }, [roomId, playerId]);

  return status;
}