from time import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import logging
import os

from app.core import ControlManager, MachineState
from app.core.temperature import fetch_temperature_sensor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ORIGIN = "http://localhost:3000"
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
TEMPERATURE_UPDATE_INTERVAL = 15  # seconds
INITIAL_MACHINE_STATE = MachineState(
    motor_speed=0.0, valve_state=False, temperature=0.0
)

control_manager: ControlManager | None = None


async def initialize_state(api_key: str) -> MachineState:
    current_temp = await fetch_temperature_sensor(api_key)
    initial_state = MachineState(**INITIAL_MACHINE_STATE)
    initial_state["temperature"] = current_temp

    return initial_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes machine state and startes periodic temperature updates."""
    global control_manager

    logging.info("Starting up...")

    if WEATHER_API_KEY is None or WEATHER_API_KEY.strip() == "":
        raise RuntimeError("WEATHER_API_KEY environment variable not set")

    api_key = WEATHER_API_KEY.strip()

    initial_state = await initialize_state(api_key)
    control_manager = ControlManager(initial_state)
    scheduler = AsyncIOScheduler()

    async def periodic_update():
        """Fetch temperature and update state periodically (every TEMPERATURE_UPDATE_INTERVAL seconds)."""
        if control_manager is None:
            logging.error("ControlManager not initialized in periodic update")
            return

        cm: ControlManager = control_manager
        new_temp = await fetch_temperature_sensor(api_key)
        logging.info(f"Fetched new temperature: {new_temp}")

        await cm.update_temperature(new_temp)

    scheduler.add_job(periodic_update, "interval", seconds=TEMPERATURE_UPDATE_INTERVAL)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN],
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

    await control_manager.connect(websocket)

    while True:
        try:
            await control_manager.process_message(websocket)
        except WebSocketDisconnect as e:
            logger.info(f"WebSocket disconnected: {e}")
            await control_manager.disconnect(websocket)
            break
        except Exception as e:
            # await control_manager.disconnect(websocket)
            logger.error(f"Error processing WebSocket message: {e}")
            break
