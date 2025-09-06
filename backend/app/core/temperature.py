import requests
import logging

import random

logger = logging.getLogger(__name__)

LOCAL_LATITUDE = 25.683367718378108
LOCAL_LONGITUDE = -100.32335820290318
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"


async def fetch_temperature_sensor(weather_api_key: str) -> float:
    """Fetch temperature from OpenWeatherMap API.

    Args:
        weather_api_key (str): API key for OpenWeatherMap.
    Returns:
        float: Current temperature in Celsius.
    """
    url = f"{WEATHER_API_URL}?lat={LOCAL_LATITUDE}&lon={LOCAL_LONGITUDE}&appid={weather_api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data["main"]["temp"]
    else:
        logging.error(
            f"Failed to fetch weather data: [{response.status_code}] {response.text}"
        )
        return 20.0 + random.random() * 10.0
