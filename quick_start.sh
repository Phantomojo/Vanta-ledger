#!/bin/bash

# Vanta Ledger Quick Start Script
# This script sets up Vanta Ledger for development or basic production use

set -e  # Exit on any error

echo "🚀 Vanta Ledger Quick Start"
echo "=========================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python and pip found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp env.example .env
    echo "✅ Environment file created. Please edit .env with your settings."
fi

# Create uploads directory
if [ ! -d "uploads" ]; then
    echo "📁 Creating uploads directory..."
    mkdir -p uploads
fi

# Setup database and initial data
echo "🗄️ Setting up database..."
python setup_initial_data.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: python run_backend.py"
echo "3. Access the API at: http://localhost:8500"
echo "4. View documentation at: http://localhost:8500/docs"
echo ""
echo "🔐 Default users:"
echo "   - Admin: admin / admin123"
echo "   - Auntie Nyaruai: auntie_nyaruai / auntie123"
echo ""
echo "⚠️  Remember to change default passwords in production!" 