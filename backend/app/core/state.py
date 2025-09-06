import typing


class MachineState(typing.TypedDict):
    motor_speed: float
    valve_state: bool
    temperature: float
