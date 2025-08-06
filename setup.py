#!/usr/bin/env python3
"""
Vanta Ledger Setup Script
=========================

This script helps set up the Vanta Ledger system for development and production use.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data/uploads",
        "data/processed_documents",
        "backend/logs",
        "database/logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_virtual_environment():
    """Set up Python virtual environment"""
    if not Path("venv").exists():
        print("🔄 Creating virtual environment...")
        if run_command("python3 -m venv venv", "Creating virtual environment"):
            print("✅ Virtual environment created")
            return True
        return False
    else:
        print("✅ Virtual environment already exists")
        return True

def install_dependencies():
    """Install Python dependencies"""
    # Determine the correct pip command
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    
    # Install backend dependencies
    if Path("backend/requirements-hybrid.txt").exists():
        run_command(f"{pip_cmd} install -r backend/requirements-hybrid.txt", "Installing backend dependencies")
    
    # Install additional dependencies
    additional_deps = [
        "psutil",
        "pytest",
        "black",
        "flake8",
        "mypy"
    ]
    
    for dep in additional_deps:
        run_command(f"{pip_cmd} install {dep}", f"Installing {dep}")

def setup_environment_file():
    """Set up environment configuration file"""
    if not Path(".env").exists():
        if Path("env.example").exists():
            shutil.copy("env.example", ".env")
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your actual configuration")
        else:
            print("⚠️  No env.example found, please create .env file manually")
    else:
        print("✅ .env file already exists")

def setup_database():
    """Set up database configuration"""
    print("📋 Database Setup Instructions:")
    print("1. Install PostgreSQL and MongoDB")
    print("2. Create database 'vanta_ledger'")
    print("3. Update .env file with database credentials")
    print("4. Run database initialization scripts")

def setup_frontend():
    """Set up frontend dependencies"""
    if Path("frontend/package.json").exists():
        print("🔄 Installing frontend dependencies...")
        os.chdir("frontend")
        run_command("npm install", "Installing frontend dependencies")
        os.chdir("..")
    else:
        print("ℹ️  No frontend package.json found, skipping frontend setup")

def run_tests():
    """Run basic tests"""
    print("🧪 Running basic tests...")
    if Path("backend").exists():
        os.chdir("backend")
        run_command("python -m pytest tests/ -v", "Running backend tests")
        os.chdir("..")

def main():
    """Main setup function"""
    print("🚀 Vanta Ledger Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Setup environment file
    setup_environment_file()
    
    # Setup database
    setup_database()
    
    # Setup frontend
    setup_frontend()
    
    # Run tests
    run_tests()
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your configuration")
    print("2. Set up databases (PostgreSQL and MongoDB)")
    print("3. Start the system:")
    print("   - Production: ./database/launch_production_system.sh")
    print("   - Backend: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8500")
    print("   - Frontend: cd frontend && npm run dev")
    print("\n📖 Documentation: README.md")
    print("🔗 API Docs: http://localhost:8500/docs (when backend is running)")

if __name__ == "__main__":
    main() 