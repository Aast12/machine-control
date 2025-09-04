from dataclasses import dataclass
from typing import Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import logging

import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


origin = "http://localhost:3000"


@dataclass
class MachineState:
    motor_speed: float = 0.0
    valve_state: bool = False
    temperature: float = 25.0


class MissingPayloadKeys(Exception):
    pass


class BadState(Exception):
    pass


def is_json_valid_state(data: Any) -> MachineState | None:
    try:
        state_data = MachineState(**data)
        return state_data
    except (TypeError, ValueError) as e:
        return None


class ControlManager:
    state: MachineState
    active_connections: list[WebSocket] = []

    def __init__(self, initial_state: MachineState):
        self.state = initial_state

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        await self.send_state(websocket)
        logging.info(f"WebSocket connected: {websocket.client}")
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        logging.info(f"Disconnecting websocket: {websocket.client}")
        self.active_connections.remove(websocket)
        await websocket.close()

    async def send_state(self, websocket: WebSocket):
        try:
            await websocket.send_json(self.state.__dict__)
        except Exception as e:
            logging.error(f"Error sending state to {websocket.client}: {e}")
            await self.disconnect(websocket)

    async def broadcast(self):
        for connection in self.active_connections:
            await self.send_state(connection)

    async def update(self, new_state: MachineState):
        """
        Update all connected clients with the new state.
        """
        self.state = new_state
        logger.info(f"State updated to: {self.state}")
        await self.broadcast()

    async def fetch_temperature_sensor(self):
        return 20.0 + random.random() * 10.0

    def parse_update_request(
        self, data: dict[str, Any]
    ) -> tuple[MachineState, MachineState]:
        if "original_state" not in data:
            raise MissingPayloadKeys("'original_state' field is required.")
        if "new_state" not in data:
            raise MissingPayloadKeys("'new_state' field is required.")

        original_state = is_json_valid_state(data.get("original_state"))
        new_state = is_json_valid_state(data.get("new_state"))

        if original_state is None:
            raise BadState(f"Invalid original state data. {data.get('original_state')}")
        if new_state is None:
            raise BadState(f"Invalid new state data. {data.get('new_state')}")

        return original_state, new_state


control_manager: ControlManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global control_manager

    logging.info("Starting up...")
    initial_state = MachineState()
    control_manager = ControlManager(initial_state)
    scheduler = AsyncIOScheduler()

    async def periodic_update():
        if control_manager is None:
            logging.error("ControlManager not initialized in periodic update")
            return

        cm: ControlManager = control_manager
        new_temp = await cm.fetch_temperature_sensor()
        logging.info(f"Fetched new temperature: {new_temp}")

        new_state = MachineState(
            motor_speed=cm.state.motor_speed,
            valve_state=cm.state.valve_state,
            temperature=new_temp,
        )

        await cm.update(new_state)

    scheduler.add_job(periodic_update, "interval", seconds=6 * 5)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"message": "OK"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if control_manager is None:
        raise RuntimeError("ControlManager not initialized")

    try:
        await control_manager.connect(websocket)
    except Exception as e:
        print("WebSocket connection error:", e)
        return

    while True:
        try:
            data = await websocket.receive_json()

            try:
                original_state, new_state = control_manager.parse_update_request(data)
            except (MissingPayloadKeys, BadState) as e:
                await websocket.send_text(f"Error: {e}")
                continue

            print("Received state update request:", original_state, new_state)
            # todo: mismatch original state
            await control_manager.update(new_state)
        except WebSocketDisconnect as e:
            print("WebSocket disconnected:", e)
            await control_manager.disconnect(websocket)
            break
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")
            break
