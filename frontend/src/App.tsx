import "./App.css";
import { useControl } from "@/hooks/useControl";
import { ReadyState } from "react-use-websocket";
import { Button } from "@/components/ui/button";
import { UpdateWidget } from "@/components/widget";
import { Slider } from "@/components/ui/slider";
import { useEffect, useState } from "react";
import Layout from "@/components/layout";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

const MAX_MOTOR_SPEED = 5000;
const MIN_MOTOR_SPEED = 0;

function App() {
  const { currentState, sendUpdate, readyState, error } = useControl({
    serverUrl: "ws://localhost:8000/ws",
  });

  const [motorSpeed, setMotorSpeed] = useState(0);

  useEffect(() => {
    console.log(error);
    if (error !== null) {
      toast(error);
    }
  }, [error]);

  if (
    currentState === null &&
    readyState in
      [ReadyState.CONNECTING, ReadyState.UNINSTANTIATED, ReadyState.OPEN]
  ) {
    return (
      <Layout>
        <div className="flex md:flex-row flex-col gap-4">
          <Skeleton className="h-[125px] w-[250px] rounded-xl" />
        </div>
      </Layout>
    );
  }

  // websocket closed without sending state
  if (currentState === null) {
    return (
      <Layout>
        <div className="flex flex-col gap-4">
          <p className="text-red-500">Error connecting to server.</p>
        </div>
      </Layout>
    );
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
          value={currentState.valveState ? "Open" : "Closed"}
        >
          <Button
            className="w-full"
            onClick={() =>
              sendUpdate({
                ...currentState,
                valveState: !currentState.valveState,
              })
            }
          >
            {currentState.valveState ? "Close" : "Open"} valve
          </Button>
        </UpdateWidget>
        <UpdateWidget
          name="Motor Control"
          className="md:w-sm"
          value={`${currentState.motorSpeed} RPM`}
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
              disabled={motorSpeed === currentState.motorSpeed}
              onClick={() =>
                sendUpdate({
                  ...currentState,
                  motorSpeed,
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
