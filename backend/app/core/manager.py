from typing import Any
from fastapi import WebSocket
import requests
import logging


import random

from app.core.errors import BadState, MissingPayloadKeys
from app.core.state import MachineState, is_json_valid_state

logger = logging.getLogger(__name__)

LOCAL_LATITUDE = 25.747057669386194
LOCAL_LONGITUDE = -100.43502377290577


class ControlManager:
    state: MachineState
    active_connections: list[WebSocket] = []

    def __init__(self, initial_state: MachineState, weather_api_key: str):
        self.weather_api_key = weather_api_key
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
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={LOCAL_LATITUDE}&lon={LOCAL_LONGITUDE}&appid={self.weather_api_key}&units=metric"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data["main"]["temp"]
        else:
            logging.error(
                f"Failed to fetch weather data: [{response.status_code}] {response.text}"
            )
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
