from dataclasses import asdict
import random
import time
from fastapi import WebSocket
import logging


from app.core.errors import BadState, MissingPayloadKeys
from app.core.state import MachineState
from app.core.messages import (
    ErrorMessage,
    SendUpdateMessage,
    parse_receive_update,
)

logger = logging.getLogger(__name__)

LOCAL_LATITUDE = 25.747057669386194
LOCAL_LONGITUDE = -100.43502377290577


class ControlManager:
    state: MachineState
    active_connections: list[WebSocket] = []
    last_temp_update: float = 0.0

    def __init__(self, initial_state: MachineState):
        self.state = initial_state
        self.last_temp_update = time.time()

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            await self._send_state(websocket)
            logging.info(f"WebSocket connected: {websocket.client}")
            self.active_connections.append(websocket)
        except Exception as e:
            # await self.disconnect(websocket)
            logging.error(f"Error accepting websocket connection: {e}")

    async def disconnect(self, websocket: WebSocket):
        logging.info(f"Disconnecting websocket: {websocket.client}")
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        await websocket.close()

    async def _send_error(self, websocket: WebSocket, error: Exception):
        try:
            await websocket.send_json(
                asdict(ErrorMessage(data={"message": str(error)}))
            )
        except Exception as e:
            logging.error(f"Error sending error message to {websocket.client}: {e}")
            await self.disconnect(websocket)

    async def _send_state(self, websocket: WebSocket):
        try:
            await websocket.send_json(
                asdict(
                    SendUpdateMessage(
                        data=self.state, last_temp_update=self.last_temp_update
                    )
                )
            )
        except Exception as e:
            logging.error(f"Error sending state to {websocket.client}: {e}")
            await self.disconnect(websocket)

    async def _broadcast(self):
        for connection in self.active_connections:
            await self._send_state(connection)

    async def update_temperature(self, new_tremperature: float):
        """
        Updates state and broadcasts to all connected clients.
        """
        self.state["temperature"] = new_tremperature
        self.last_temp_update = time.time()

        await self._broadcast()

    async def update(self, new_state: MachineState):
        """
        Update all connected clients with the new state.
        """
        # client should not be able to change temperature directly
        current_temperature = self.state["temperature"]
        self.state = MachineState(**new_state)
        # add noise for showcase purposes
        self.state["temperature"] = current_temperature + random.random() * 0.1

        logger.info(f"State updated to: {self.state}")
        await self._broadcast()

    async def process_message(self, websocket: WebSocket):
        """Handle an incoming message from a client.
        Raises ValueError if message type is not present, or not an update
        Raises TypeError if keys are missing or types are wrong
        """
        data = await websocket.receive_json()

        try:
            update_data = parse_receive_update(data)
            update_data = update_data.data
        except Exception as e:
            await self._send_error(websocket, e)
            return

        # todo: mismatch original state
        await self.update(update_data["new_state"])
