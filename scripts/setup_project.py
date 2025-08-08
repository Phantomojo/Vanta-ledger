#!/usr/bin/env python3
"""
Vanta Ledger Project Setup Script
=================================

This script helps set up the Vanta Ledger system for development and production use.
Follows modern Python practices and works with the new src/ layout.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """
    Execute a shell command and report its success or failure.
    
    Parameters:
        command (str): The shell command to execute.
        description (str): A brief description of the command's purpose, used in status messages.
    
    Returns:
        bool: True if the command executes successfully, False otherwise.
    """
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
    """
    Verify that the current Python interpreter is version 3.8 or higher.
    
    Returns:
        bool: True if the Python version is at least 3.8, False otherwise.
    """
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_directories():
    """
    Create required directories for logs and data storage if they do not already exist.
    
    This function ensures that all necessary directory structures for logs and data are present, creating them as needed.
    """
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
    """
    Create a Python virtual environment in the project directory if one does not already exist.
    
    Returns:
        bool: True if the virtual environment exists or is created successfully, False otherwise.
    """
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
    """
    Install project dependencies in editable mode with development extras using pip.
    
    Returns:
        bool: True if dependencies are installed successfully, False otherwise.
    """
    # Determine the correct pip command
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    
    # Install the project in editable mode with development dependencies
    print("🔄 Installing project in editable mode...")
    if run_command(f"{pip_cmd} install -e .[dev]", "Installing project with dev dependencies"):
        print("✅ Project installed successfully")
        return True
    return False

def setup_environment_file():
    """
    Ensure a `.env` environment configuration file exists, creating it from `env.example` if available.
    
    If `.env` does not exist and an `env.example` template is present, copies the template to create `.env` and prompts the user to edit it. If no template is found, instructs the user to create `.env` manually. Prints status messages indicating the outcome.
    """
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
    """
    Display instructions for manually setting up the required PostgreSQL and MongoDB databases for the project.
    
    Prints step-by-step guidance for installing database systems, creating the `vanta_ledger` database, updating environment credentials, and running initialization scripts.
    """
    print("📋 Database Setup Instructions:")
    print("1. Install PostgreSQL and MongoDB")
    print("2. Create database 'vanta_ledger'")
    print("3. Update .env file with database credentials")
    print("4. Run database initialization scripts")

def setup_frontend():
    """
    Installs frontend dependencies using npm if a frontend package.json file is present.
    
    If the frontend directory contains a package.json file, this function changes to the frontend directory, runs `npm install` to install dependencies, and then returns to the original directory. If no package.json is found, it skips the frontend setup and notifies the user.
    """
    if Path("frontend/package.json").exists():
        print("🔄 Installing frontend dependencies...")
        os.chdir("frontend")
        run_command("npm install", "Installing frontend dependencies")
        os.chdir("..")
    else:
        print("ℹ️  No frontend package.json found, skipping frontend setup")

def run_tests():
    """
    Run the project's test suite using pytest and report the results.
    """
    print("🧪 Running basic tests...")
    if run_command("pytest tests/ -v", "Running tests"):
        print("✅ Tests completed successfully")
    else:
        print("⚠️  Some tests failed - check the output above")

def main():
    """
    Orchestrates the full setup process for the Vanta Ledger project, including environment validation, directory creation, virtual environment setup, dependency installation, environment file configuration, database instructions, frontend setup, and test execution. Exits on critical failures and prints next-step instructions upon completion.
    """
    print("🚀 Vanta Ledger Setup (Modern Python Layout)")
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
    if not install_dependencies():
        sys.exit(1)
    
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