#!/bin/bash

# Function to kill child processes on exit
cleanup() {
  echo "Stopping VantaLedger backend and frontend..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
  echo "Stopped."
  exit 0
}

trap cleanup SIGINT SIGTERM

echo "Starting VantaLedger backend..."
PYTHONPATH=./src uvicorn vanta_ledger.main:app --reload --port 8000 &
BACKEND_PID=$!

sleep 3

if ps -p $BACKEND_PID > /dev/null
then
  echo "Backend started successfully with PID $BACKEND_PID"
else
  echo "Backend failed to start"
  exit 1
fi

echo "Starting frontend server on port 8001..."
cd frontend
python3 -m http.server 8001 &
FRONTEND_PID=$!

sleep 3

if ps -p $FRONTEND_PID > /dev/null
then
  echo "Frontend server started successfully with PID $FRONTEND_PID"
else
  echo "Frontend server failed to start"
  kill $BACKEND_PID
  exit 1
fi

echo "VantaLedger is running."
echo "Backend: http://localhost:8000/docs"
echo "Frontend: http://localhost:8001"

echo "Press Ctrl+C to stop."

wait $BACKEND_PID $FRONTEND_PID

