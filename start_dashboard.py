#!/usr/bin/env python3
"""
Vanta Ledger Dashboard Startup Script
Launches the backend API and web dashboard together
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

def run_backend():
    """Run the backend API"""
    print("🚀 Starting Backend API...")
    try:
        subprocess.run([sys.executable, "backend_api.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend API stopped")
    except Exception as e:
        print(f"❌ Backend API error: {e}")

def run_frontend():
    """Run the React frontend"""
    print("🌐 Starting Web Dashboard...")
    try:
        os.chdir("frontend-web")
        subprocess.run(["npm", "run", "dev"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Web Dashboard stopped")
    except Exception as e:
        print(f"❌ Web Dashboard error: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check if frontend-web directory exists
    if not Path("frontend-web").exists():
        print("❌ frontend-web directory not found")
        return False
    
    # Check if node_modules exists
    if not Path("frontend-web/node_modules").exists():
        print("📦 Installing frontend dependencies...")
        try:
            os.chdir("frontend-web")
            subprocess.run(["npm", "install"], check=True)
            os.chdir("..")
        except Exception as e:
            print(f"❌ Failed to install frontend dependencies: {e}")
            return False
    
    # Check Python dependencies
    required_packages = ['flask', 'flask-cors', 'requests']
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"📦 Installing {package}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            except Exception as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
    
    print("✅ All dependencies ready")
    return True

def main():
    """Main startup function"""
    print("🎯 Vanta Ledger Dashboard Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing dependencies.")
        sys.exit(1)
    
    print("\n🚀 Starting services...")
    print("📊 Backend API: http://localhost:5000")
    print("🌐 Web Dashboard: http://localhost:5173")
    print("📄 Paperless-ngx: http://localhost:8000")
    print("\nPress Ctrl+C to stop all services")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 