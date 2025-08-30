#!/usr/bin/env python3
"""
Test backend server startup
"""
import os
import time
import requests
import subprocess
import threading

# Override MongoDB URI to work without authentication
os.environ["MONGO_URI"] = "mongodb://localhost:27017/vanta_ledger"

def start_backend_server():
    """Start the backend server in a separate thread"""
    try:
        from src.vanta_ledger.main import app
        import uvicorn
        
        print("🚀 Starting backend server...")
        uvicorn.run(app, host="127.0.0.1", port=8500, log_level="info")
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")

def test_server_health():
    """Test if the server is responding"""
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:8500/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server is responding!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Waiting for server to start... (attempt {attempt + 1}/{max_attempts})")
        time.sleep(2)
    
    print("❌ Server failed to start within expected time")
    return False

if __name__ == "__main__":
    print("🔍 Testing Backend Server Startup...")
    print("=" * 50)
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_backend_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(3)
    
    # Test server health
    if test_server_health():
        print("🎉 Backend server test successful!")
    else:
        print("⚠️ Backend server test failed")
    
    print("🛑 Test complete - server will continue running in background")
