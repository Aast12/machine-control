export type MachineState = {
  motor_speed: number;
  valve_state: boolean;
  temperature: number;
};

export type GetUpdateMessage = MachineState;
