#!/usr/bin/env python3
"""
Vanta Ledger Backend Startup Script
"""

import os
import sys
import subprocess
import signal
import time
import logging
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up environment variables"""
    # Use environment variables or set defaults for development
    if not os.environ.get("GITHUB_TOKEN"):
        logger.warning("⚠️  Warning: GITHUB_TOKEN environment variable not set")
        logger.info("   Set it with: export GITHUB_TOKEN=")
    if not os.environ.get("SECRET_KEY"):
        os.environ["SECRET_KEY"] = "dev-secret-key-change-in-production"
    if not os.environ.get("DEBUG"):
        os.environ["DEBUG"] = "True"
    if not os.environ.get("MONGO_URI"):
        os.environ["MONGO_URI"] = "mongodb://localhost:27017/vanta_ledger"
    if not os.environ.get("POSTGRES_URI"):
        os.environ["POSTGRES_URI"] = "postgresql://vanta_user:password@localhost:5432/vanta_ledger"
    if not os.environ.get("REDIS_URI"):
        os.environ["REDIS_URI"] = "redis://localhost:6379/0"

def test_import():
    """Test if the application can be imported"""
    try:
        from src.vanta_ledger.main import app
        logger.info("✅ Backend application imports successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Backend import failed: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    logger.info("🚀 Starting Vanta Ledger Backend Server...")
    logger.info("📡 Server will be available at: http://localhost:8500")
    logger.info("📚 API Documentation: http://localhost:8500/docs")
    logger.info("🔄 Press Ctrl+C to stop the server")
    
    try:
        # Start uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "src.vanta_ledger.main:app",
            "--host", "127.0.0.1",
            "--port", "8500",
            "--reload"
        ]
        
        process = subprocess.Popen(cmd)
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping server...")
        process.terminate()
        process.wait()
        logger.info("✅ Server stopped successfully!")

if __name__ == "__main__":
    logger.info("🔧 Setting up environment...")
    setup_environment()
    
    logger.info("🧪 Testing application import...")
    if not test_import():
        logger.error("❌ Cannot start server due to import errors")
        sys.exit(1)
    
    logger.info("🌟 All checks passed! Starting server...")
    start_server()

