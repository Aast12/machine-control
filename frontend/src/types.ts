export type MachineState = {
  motorSpeed: number;
  valveState: boolean;
  temperature: number;
  lastTempUpdate: Date;
  lastUpdate: Date;
};

export type MachineStateResponse = {
  motor_speed: number;
  valve_state: boolean;
  temperature: number;
};

export type SendUpdateMessage = {
  type: "update";
  data: {
    original_state: MachineStateResponse;
    new_state: MachineStateResponse;
  };
};

export type RcvUpdateMessage = {
  type: "update";
  data: MachineStateResponse;
  last_temp_update: number;
};

export type RcvErrorMessage = {
  type: "error";
  data: {
    message: string;
  };
};

export type GetUpdateMessage = RcvUpdateMessage | RcvErrorMessage;
