import "./App.css";
import { useControl } from "@/hooks/useControl";
import { Button } from "@/components/ui/button";
import { UpdateWidget } from "@/components/widget";
import { Slider } from "@/components/ui/slider";
import { useState } from "react";
import Layout from "@/components/layout";

const MAX_MOTOR_SPEED = 5000;
const MIN_MOTOR_SPEED = 0;

function App() {
  const { currentState, sendUpdate } = useControl({
    serverUrl: "ws://localhost:8000/ws",
  });

  const [motorSpeed, setMotorSpeed] = useState(0);

  if (!currentState) {
    return <div>Loading...</div>;
  }

  return (
    <Layout>
      <div className="flex md:flex-row flex-col gap-4">
        <UpdateWidget
          name="Temperature"
          className="md:w-sm"
          value={`${currentState.temperature.toFixed(2)} °C`}
        >
          <div className="flex flex-col gap-4"></div>
        </UpdateWidget>
        <UpdateWidget
          name="Valve Control"
          className="md:w-sm"
          value={currentState.valve_state ? "Open" : "Closed"}
        >
          <Button
            className="w-full"
            onClick={() =>
              sendUpdate({
                ...currentState,
                valve_state: !currentState.valve_state,
              })
            }
          >
            {currentState.valve_state ? "Close" : "Open"} valve
          </Button>
        </UpdateWidget>
        <UpdateWidget
          name="Motor Control"
          className="md:w-sm"
          value={`${currentState.motor_speed} RPM`}
        >
          <div className="flex flex-col gap-4">
            <Slider
              value={[motorSpeed]}
              min={MIN_MOTOR_SPEED}
              max={MAX_MOTOR_SPEED}
              step={1}
              onValueChange={(value) => {
                setMotorSpeed(value[0]);
              }}
            ></Slider>
            <Button
              className="w-full"
              onClick={() =>
                sendUpdate({
                  ...currentState,
                  motor_speed: motorSpeed,
                })
              }
            >
              Update speed to {motorSpeed} RPM
            </Button>
          </div>
        </UpdateWidget>
      </div>
    </Layout>
  );
}

export default App;
