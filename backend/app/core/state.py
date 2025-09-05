import typing


class MachineState(typing.TypedDict):
    motor_speed: float
    valve_state: bool
    temperature: float


def is_json_valid_state(data: typing.Any) -> MachineState | None:
    try:
        state_data = MachineState(**data)
        return state_data
    except (TypeError, ValueError) as e:
        return None


def is_valid_state(data: MachineState) -> bool:
    return 0 <= data["motor_speed"] <= 100
