import { useEffect, useRef, useState } from "react";

type SocketStatus = "connecting" | "connected" | "disconnected" | "error";

export function useGameSocket(
  roomId: string,
  playerId: string,
  onMessage: (data: unknown) => void
) {
  const [status, setStatus] = useState<SocketStatus>("connecting");
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!roomId || !playerId) return;

    setStatus("connecting");
    const url = `${import.meta.env.VITE_WS_BASE}/${roomId}/${playerId}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

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

    return () => {
      wsRef.current = null;
      ws.close();
    };
  }, [roomId, playerId]);

  function send(payload: unknown) {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    }
  }

  return { status, send };
}