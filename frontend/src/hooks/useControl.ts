import { useState, useEffect, useCallback } from "react";
import useWebSocket from "react-use-websocket";
import type { GetUpdateMessage, MachineState } from "@/types";

export function useControl({ serverUrl }: { serverUrl: string }) {
  const [currentState, setCurrentState] = useState<MachineState | null>(null);

  const { lastJsonMessage, sendJsonMessage, readyState } =
    useWebSocket<GetUpdateMessage>(serverUrl);

  const sendUpdate = useCallback(
    (newState: MachineState) => {
      if (currentState === null) return;

      sendJsonMessage({
        original_state: currentState,
        new_state: newState,
      });
    },
    [sendJsonMessage, currentState],
  );

  useEffect(() => {
    if (lastJsonMessage !== null) {
      setCurrentState(lastJsonMessage);
    }
  }, [lastJsonMessage]);

  return { readyState, currentState, sendUpdate };
}
