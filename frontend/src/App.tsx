import { useState, useEffect, useCallback } from "react";
import "./App.css";
import useWebSocket from "react-use-websocket";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

type MachineState = {
  motorSpeed: number;
  valveState: boolean;
  temperature: number;
};

const parseIntoPayload = (data: MachineState) => {
  return {
    motor_speed: data.motorSpeed,
    valve_state: data.valveState,
    temperature: data.temperature,
  };
};

const parseFromPayload = (data: object): MachineState => {
  return {
    motorSpeed: data.motor_speed,
    valveState: data.valve_state,
    temperature: data.temperature,
  };
};

function App() {
  const [count, setCount] = useState(0);
  const [currentState, setCurrentState] = useState<MachineState>(null);

  const { lastJsonMessage, sendJsonMessage } = useWebSocket(
    "ws://localhost:8000/ws",
  );

  const sendUpdate = useCallback(
    (newState) => {
      const original_state = parseIntoPayload(currentState);
      const new_state = parseIntoPayload(newState);

      console.log("Sending new state to server: ", new_state);
      console.log("Using old state to server: ", original_state);

      sendJsonMessage({
        original_state,
        new_state,
      });
    },
    [currentState],
  );

  useEffect(() => {
    if (lastJsonMessage !== null) {
      console.log("Message from server ", lastJsonMessage);
      setCurrentState(parseFromPayload(lastJsonMessage));
    }
  }, [lastJsonMessage]);

  if (!currentState) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <div>
        <div className="flex items-center space-x-2">
          <Switch
            checked={currentState.valveState}
            id="valve-state"
            onCheckedChange={() => {
              console.log(
                "Toggling valve state",
                currentState.valveState,
                !currentState.valveState,
              );
              sendUpdate({
                ...currentState,
                valveState: !currentState.valveState,
              });
            }}
          />
          <Label htmlFor="valve-state">Valve State</Label>
        </div>
      </div>
    </>
  );
}

export default App;
