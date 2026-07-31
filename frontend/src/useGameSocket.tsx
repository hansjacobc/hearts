import { useEffect, useRef, useState } from "react";

type SocketStatus = "connecting" | "connected" | "disconnected" | "error";

export function useGameSocket(
  roomId: string,
  playerId: string,
  onMessage: (data: unknown) => void
) {
  const [status, setStatus] = useState<SocketStatus>("connecting");
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage; // keeps effect deps stable if caller passes a new fn each render

  useEffect(() => {
    if (!roomId || !playerId) return;

    setStatus("connecting");
    const url = `${import.meta.env.VITE_WS_BASE}/${roomId}/${playerId}`;
    const ws = new WebSocket(url);

    ws.onopen = () => setStatus("connected");
    ws.onclose = () => setStatus("disconnected");
    ws.onerror = () => setStatus("error");
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessageRef.current(data);
      } catch {
        console.error("Failed to parse socket message:", event.data);
      }
    };

    return () => ws.close();
  }, [roomId, playerId]);

  return status;
}