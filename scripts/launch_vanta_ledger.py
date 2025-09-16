#!/usr/bin/env python3
"""
🚀 Vanta Ledger - Complete System Launcher
Launches both backend API and frontend dashboard in one command
"""

import os
import sys
import subprocess
import signal
import time
import threading
import webbrowser
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

class VantaLedgerLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = Path(__file__).parent
        self.frontend_dir = self.base_dir / "frontend" / "frontend-web"
        
    def setup_environment(self):
        """Set up environment variables"""
        logger.info("🔧 Setting up environment variables...")
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
        logger.info("✅ Environment configured")

    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        logger.info("🔍 Checking prerequisites...")
        
        # Check if virtual environment exists
        venv_path = self.base_dir / ".venv"
        if not venv_path.exists():
            logger.info("❌ Virtual environment not found. Please run: python -m venv .venv")
            return False
            
        # Check if frontend directory exists
        if not self.frontend_dir.exists():
            logger.info("❌ Frontend directory not found at:")
            return False
            
        # Check if package.json exists
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            logger.info("❌ Frontend package.json not found")
            return False
            
        logger.info("✅ All prerequisites met")
        return True

    def test_backend_import(self):
        """Test if the backend can be imported"""
        logger.info("🧪 Testing backend import...")
        try:
            # Activate venv and test import
            if sys.platform == "win32":
                python_exe = self.base_dir / ".venv" / "Scripts" / "python.exe"
            else:
                python_exe = self.base_dir / ".venv" / "bin" / "python"
                
            result = subprocess.run([
                str(python_exe), "-c", 
                "from src.vanta_ledger.main import app; logger.info("Backend import successful")"
            ], cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Backend imports successfully")
                return True
            else:
                logger.error("❌ Backend import failed:")
                logger.info(result.stderr)
                return False
        except Exception as e:
            logger.error(f"❌ Backend test failed: {e}")
            return False

    def install_frontend_deps(self):
        """Install frontend dependencies if needed"""
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            logger.info("📦 Installing frontend dependencies...")
            try:
                result = subprocess.run(
                    ["npm", "install"], 
                    cwd=self.frontend_dir,
                    check=True
                )
                logger.info("✅ Frontend dependencies installed")
                return True
            except subprocess.CalledProcessError:
                logger.error("❌ Failed to install frontend dependencies")
                return False
        else:
            logger.info("✅ Frontend dependencies already installed")
            return True

    def start_backend(self):
        """Start the backend server"""
        logger.info("🔥 Starting backend server...")
        try:
            if sys.platform == "win32":
                python_exe = self.base_dir / ".venv" / "Scripts" / "python.exe"
            else:
                python_exe = self.base_dir / ".venv" / "bin" / "python"
                
            cmd = [
                str(python_exe), "-m", "uvicorn",
                "src.vanta_ledger.main:app",
                "--host", "127.0.0.1",
                "--port", "8500",
                "--reload"
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                env=os.environ.copy()
            )
            
            logger.info("✅ Backend server starting on http://localhost:8500")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            return False

    def start_frontend(self):
        """Start the frontend development server"""
        logger.info("🎨 Starting frontend development server...")
        try:
            cmd = ["npm", "run", "dev"]
            
            self.frontend_process = subprocess.Popen(
                cmd,
                cwd=self.frontend_dir
            )
            
            logger.info("✅ Frontend server starting on http://localhost:5173")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            return False

    def wait_for_services(self):
        """Wait for services to be ready"""
        logger.info("⏳ Waiting for services to start...")
        
        # Wait a bit for startup
        time.sleep(5)
        
        # Check if backend is responding
        try:
            import requests
            response = requests.get("http://localhost:8500/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Backend is ready!")
            else:
                logger.info("⚠️ Backend may not be fully ready yet")
        except:
            logger.error("⚠️ Backend health check failed, but it may still be starting...")
            
        logger.info("🌐 Services should be available at:")
        logger.info("   📡 Backend API: http://localhost:8500")
        logger.info("   📚 API Docs: http://localhost:8500/docs")
        logger.info("   🎨 Frontend: http://localhost:5173")

    def open_browser(self):
        """Open browser to the frontend"""
        logger.info("🌍 Opening browser...")
        try:
            webbrowser.open("http://localhost:5173")
        except:
            logger.info("⚠️ Could not open browser automatically")

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("\n🛑 Shutting down Vanta Ledger...")
        self.stop_services()
        sys.exit(0)

    def stop_services(self):
        """Stop all services"""
        if self.backend_process:
            logger.info("🔥 Stopping backend server...")
            self.backend_process.terminate()
            self.backend_process.wait()
            
        if self.frontend_process:
            logger.info("🎨 Stopping frontend server...")
            self.frontend_process.terminate()
            self.frontend_process.wait()
            
        logger.info("✅ All services stopped")

    def run(self):
        """Main run method"""
        logger.info("🚀 Vanta Ledger - Complete System Launcher")
        logger.info("=")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        
        # Run all checks
        if not self.check_prerequisites():
            sys.exit(1)
            
        self.setup_environment()
        
        if not self.test_backend_import():
            logger.info("❌ Cannot start due to backend issues")
            sys.exit(1)
            
        if not self.install_frontend_deps():
            logger.info("❌ Cannot start due to frontend dependency issues")
            sys.exit(1)
        
        # Start services
        if not self.start_backend():
            sys.exit(1)
            
        if not self.start_frontend():
            self.stop_services()
            sys.exit(1)
        
        # Wait and show status
        self.wait_for_services()
        
        # Open browser
        self.open_browser()
        
        logger.info("\n🎉 Vanta Ledger is now running!")
        logger.info("📱 Use the web interface at: http://localhost:5173")
        logger.info("🔧 Backend API available at: http://localhost:8500")
        logger.info("📖 API documentation: http://localhost:8500/docs")
        logger.info("\n⌨️  Press Ctrl+C to stop all services")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    logger.info("❌ Backend process died unexpectedly")
                    break
                if self.frontend_process and self.frontend_process.poll() is not None:
                    logger.info("❌ Frontend process died unexpectedly")
                    break
        except KeyboardInterrupt:
            pass
        
        self.stop_services()

if __name__ == "__main__":
    launcher = VantaLedgerLauncher()
    launcher.run()

