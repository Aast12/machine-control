import { useState, useEffect, useCallback } from "react";
import useWebSocket from "react-use-websocket";
import type {
  GetUpdateMessage,
  MachineState,
  SendUpdateMessage,
} from "@/types";

function buildUpdateMessage(
  originalState: MachineState,
  newState: MachineState,
): SendUpdateMessage {
  return {
    type: "update",
    data: {
      original_state: {
        motor_speed: originalState.motorSpeed,
        valve_state: originalState.valveState,
        temperature: originalState.temperature,
      },
      new_state: {
        motor_speed: newState.motorSpeed,
        valve_state: newState.valveState,
        temperature: newState.temperature,
      },
    },
  };
}

export function useControl({ serverUrl }: { serverUrl: string }) {
  const [currentState, setCurrentState] = useState<MachineState | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { lastJsonMessage, sendJsonMessage, readyState } =
    useWebSocket<GetUpdateMessage>(serverUrl);

  const sendUpdate = useCallback(
    (newState: MachineState) => {
      if (currentState === null) return;
      sendJsonMessage(buildUpdateMessage(currentState, newState));
    },
    [sendJsonMessage, currentState],
  );

  useEffect(() => {
    if (lastJsonMessage !== null) {
      if (lastJsonMessage.type === "update") {
        setCurrentState({
          lastTempUpdate: new Date(lastJsonMessage.last_temp_update * 1000),
          temperature: lastJsonMessage.data.temperature,
          valveState: lastJsonMessage.data.valve_state,
          motorSpeed: lastJsonMessage.data.motor_speed,
          lastUpdate: new Date(),
        });
        setError(null);
      }
      if (lastJsonMessage.type === "error") {
        setError(lastJsonMessage.data.message);
      }
    }
  }, [lastJsonMessage]);

  return { readyState, currentState, sendUpdate, error };
}
