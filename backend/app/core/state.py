from dataclasses import dataclass
from typing import Any


@dataclass
class MachineState:
    motor_speed: float = 0.0
    valve_state: bool = False
    temperature: float = 25.0


def is_json_valid_state(data: Any) -> MachineState | None:
    try:
        state_data = MachineState(**data)
        return state_data
    except (TypeError, ValueError) as e:
        return None
