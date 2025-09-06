# Machine Control Panel

This project showcases a machine control system to monitor and manage remote (simulated) sensors and actuators.

The system consists of a FastAPI WebSocket based application and a React frontend.

## Docker Setup (Recommended)

1. Create `.env` file. The system uses [OpenWeatherMap API](https://openweathermap.org/) to simulate a temperature sensor.
   Sign up for a free API key and add it to the `.env` file as follows:

   ```
   WEATHER_API_KEY=your_api_key_here
   ```

2. Run docker compose:

   ```bash
   docker-compose up --build
   ```

## Manual Setup

If you prefer to run the services manually without Docker, follow these steps:

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- [uv](https://docs.astral.sh/uv/) package manager (for Python)

### Backend Setup

1. **Navigate to the backend directory:**

   ```bash
   cd backend
   ```

2. **Install dependencies using uv:**

   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root (not in the backend directory) and add your OpenWeatherMap API key:

   ```
   WEATHER_API_KEY=your_api_key_here
   ```

4. **Run the backend server:**

   ```bash
   uv run --env-file .env fastapi dev --port 8000 --host 0.0.0.0
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Open a new terminal and navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

### Verification

After starting both services:

- Backend health check: Visit `http://localhost:8000/health` - you should see `{"message": "OK"}`
- Frontend: Visit `http://localhost:3000` - you should see the Machine Control Panel interface
