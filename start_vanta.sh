#!/bin/bash

# Vanta Ledger Quick Start Script
set -e

echo "🚀 Starting Vanta Ledger..."

# Kill existing processes
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 2

# Start Backend
cd backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8500 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 5
if ! curl -s http://localhost:8500/health > /dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

# Start Frontend
cd frontend/frontend-web
nohup npm run dev > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

# Wait for frontend
sleep 10
FRONTEND_PORT=$(grep "Local:" frontend.log | tail -1 | sed 's/.*http:\/\/localhost:\([0-9]*\).*/\1/' 2>/dev/null || echo "5173")

if ! curl -s http://localhost:$FRONTEND_PORT > /dev/null; then
    echo "❌ Frontend failed to start"
    exit 1
fi

# Save PIDs
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "✅ Vanta Ledger running:"
echo "   Backend:  http://localhost:8500"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Login: admin/admin123" 