#!/bin/bash
# Simple script to run the backend and frontend for VantaLedger and check for errors
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
echo "Starting VantaLedger backend..."
uvicorn src.vanta_ledger.main:app --reload &
BACKEND_PID=$!

sleep 3

if ps -p $BACKEND_PID > /dev/null
then
  echo "Backend started successfully with PID $BACKEND_PID"
else
  echo "Backend failed to start"
  exit 1
fi

echo "Starting frontend server on port 8000..."
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
echo "Frontend: http://localhost:8000"

echo "Press Ctrl+C to stop."

wait $BACKEND_PID $FRONTEND_PID
