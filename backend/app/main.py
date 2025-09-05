from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import logging
import os

from app.core import ControlManager, MissingPayloadKeys, BadState, MachineState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


origin = "http://localhost:3000"
API_KEY = os.environ.get("WEATHER_API_KEY")


control_manager: ControlManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global control_manager
    logging.info("Starting up...")

    if not API_KEY:
        raise RuntimeError("WEATHER_API_KEY environment variable not set")

    initial_state = MachineState()
    control_manager = ControlManager(initial_state, API_KEY)
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
