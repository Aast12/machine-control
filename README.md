# Machine Control Panel

This project showcases a machine control system to monitor and manage remote (simulated) sensors and actuators.

The system consists of a FastAPI WebSocket based application and a React frontend.

## Docker Setup

1. Create `.env` file. The system uses [OpenWeatherMap API](https://openweathermap.org/) to simulate a temperature sensor.
   Sign up for a free API key and add it to the `.env` file as follows:

   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

2. Run docker compose:

   ```bash
   docker-compose up --build
   ```

3. Docker will spin up the backend and frontend server, accessible at `http://localhost:3000`.
