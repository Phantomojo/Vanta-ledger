#!/bin/bash
# 🚀 Vanta Ledger - Quick Launch Script

echo "🚀 Vanta Ledger - Complete System Launcher"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "launch_vanta_ledger.py" ]; then
    echo "❌ Please run this script from the Vanta-ledger directory"
    exit 1
fi

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment and run the launcher
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

echo "🚀 Starting Vanta Ledger (Backend + Frontend)..."
python launch_vanta_ledger.py