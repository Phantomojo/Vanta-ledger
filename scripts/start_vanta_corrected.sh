#!/bin/bash

# Vanta Ledger Corrected Quick Start Script
set -e

echo "🚀 Starting Vanta Ledger (Corrected)..."

# Kill existing processes
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 2

# Activate virtual environment
source venv/bin/activate

# Start Backend with correct module path
echo "🌐 Starting Backend..."
cd src
nohup python -m uvicorn vanta_ledger.main:app --host 0.0.0.0 --port 8500 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend
echo "⏳ Waiting for backend to start..."
sleep 10
if ! curl -s http://localhost:8500/health > /dev/null; then
    echo "❌ Backend failed to start. Check backend.log for details."
    echo "📋 Backend log:"
    tail -20 backend.log
    exit 1
fi

echo "✅ Backend is running at http://localhost:8500"

# Check if frontend directory exists
if [ -d "frontend/frontend-web" ]; then
    echo "🌐 Starting Frontend..."
    cd frontend/frontend-web
    nohup npm run dev > ../../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ../..
    
    # Wait for frontend
    sleep 10
    FRONTEND_PORT=$(grep "Local:" frontend.log | tail -1 | sed 's/.*http:\/\/localhost:\([0-9]*\).*/\1/' 2>/dev/null || echo "5173")
    
    if ! curl -s http://localhost:$FRONTEND_PORT > /dev/null; then
        echo "⚠️  Frontend may not be fully started yet"
    else
        echo "✅ Frontend is running at http://localhost:$FRONTEND_PORT"
    fi
else
    echo "⚠️  Frontend directory not found, skipping frontend startup"
fi

# Save PIDs
echo $BACKEND_PID > .backend.pid
if [ ! -z "$FRONTEND_PID" ]; then
    echo $FRONTEND_PID > .frontend.pid
fi

echo ""
echo "🎉 Vanta Ledger is running!"
echo "   Backend:  http://localhost:8500"
echo "   API Docs: http://localhost:8500/docs"
if [ ! -z "$FRONTEND_PORT" ]; then
    echo "   Frontend: http://localhost:$FRONTEND_PORT"
fi
echo "   Login: <username>/<password> (see documentation or environment variables)"
echo ""
echo "📋 To stop the services:"
echo "   pkill -f uvicorn"
echo "   pkill -f 'npm run dev'" 