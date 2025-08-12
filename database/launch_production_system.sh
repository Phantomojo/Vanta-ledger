#!/bin/bash

# Vanta Ledger Production AI System Launcher
# ==========================================

echo "🚀 Vanta Ledger Production AI System Launcher"
echo "============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "production_ai_system.py" ]; then
    echo "❌ Error: production_ai_system.py not found!"
    echo "Please run this script from the database directory"
    exit 1
fi

# Check if system monitor exists
if [ ! -f "system_monitor.py" ]; then
    echo "❌ Error: system_monitor.py not found!"
    echo "Please ensure the system monitor is available"
    exit 1
fi

# Check if psutil is installed (required for monitoring)
python3 -c "import psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: psutil not installed. Installing now..."
    pip install psutil
fi

# Create logs directory
mkdir -p logs

# Function to cleanup processes
cleanup() {
    echo ""
    echo "🛑 Shutting down production system..."
    
    # Kill AI system processes
    pkill -f "production_ai_system.py"
    
    # Kill monitor processes
    pkill -f "system_monitor.py"
    
    echo "✅ Production system stopped"
    exit 0
}

# Setup signal handlers
trap cleanup SIGINT SIGTERM

echo "📋 System Configuration:"
echo "  • AI System: production_ai_system.py"
echo "  • Monitor: system_monitor.py"
echo "  • Workers: 4 concurrent"
echo "  • Batch Size: 10 documents"
echo "  • Check Interval: 60 seconds"
echo "  • Max Restarts: 3"
echo ""

# Ask for confirmation
read -p "Do you want to start the production AI system with monitoring? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Launch cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting Production AI System..."
echo "=================================="

# Start the system monitor in background
echo "🔄 Starting system monitor..."
python3 system_monitor.py > logs/system_monitor.log 2>&1 &
MONITOR_PID=$!

echo "✅ System monitor started (PID: $MONITOR_PID)"

# Wait a moment for monitor to initialize
sleep 5

# Start the production AI system
echo "🔄 Starting production AI system..."
python3 production_ai_system.py > logs/production_ai.log 2>&1 &
AI_PID=$!

echo "✅ Production AI system started (PID: $AI_PID)"
echo ""

echo "🎉 Production System Launched Successfully!"
echo "=========================================="
echo "📊 System Status:"
echo "  • AI System PID: $AI_PID"
echo "  • Monitor PID: $MONITOR_PID"
echo "  • Logs: logs/production_ai.log"
echo "  • Monitor Logs: logs/system_monitor.log"
echo ""
echo "📈 Monitoring Features:"
echo "  • CPU/Memory/Disk monitoring"
echo "  • Database connectivity checks"
echo "  • Automatic crash detection"
echo "  • Auto-restart on failure"
echo "  • Performance alerts"
echo "  • Health snapshots"
echo ""
echo "🔍 To monitor the system:"
echo "  • Watch AI logs: tail -f logs/production_ai.log"
echo "  • Watch monitor logs: tail -f logs/system_monitor.log"
echo "  • Check alerts: ls -la alert_*.json"
echo "  • View health snapshots: ls -la health_snapshot_*.json"
echo ""
echo "🛑 To stop the system: Press Ctrl+C or run:"
echo "   pkill -f 'production_ai_system.py' && pkill -f 'system_monitor.py'"
echo ""

# Wait for processes
wait $AI_PID $MONITOR_PID

echo ""
echo "✅ Production system completed" 