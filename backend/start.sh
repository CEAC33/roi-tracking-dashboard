#!/bin/bash

# Start the FastAPI application in the background
uvicorn api:app --host 0.0.0.0 --port 8000 &

# Store the PID of the backend process
BACKEND_PID=$!

# Wait for the backend to be ready and then load the data
python /app/scripts/load_data.py

# Keep the container running with the backend process
wait $BACKEND_PID 