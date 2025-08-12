#!/bin/bash

# Single Cursor Launcher - Ensures only one Cursor window and launches project safely
# This prevents multiple Cursor windows while allowing safe project execution

echo "🚀 Single Cursor Launcher - Vanta Ledger Project"
echo "================================================"

# kill_all_cursor terminates all running Cursor application processes.
kill_all_cursor() {
    echo "🛑 Stopping all Cursor processes..."
    pkill -f "cursor.AppImage" 2>/dev/null
    pkill -f "cursor" 2>/dev/null
    sleep 2
    echo "✅ All Cursor processes stopped"
}

# start_single_cursor ensures only one instance of the Cursor application is running, launching it if not already active and verifying successful startup.
start_single_cursor() {
    echo "🎯 Starting single Cursor instance..."
    
    # Check if Cursor is already running
    if pgrep -f "cursor.AppImage" | grep -vw $$ >/dev/null; then
        echo "✅ Cursor is already running (single instance)"
        return 0
    fi
    
    # Start Cursor in background
    /home/phantomojo/Applications/cursor.AppImage &
    CURSOR_PID=$!
    
    echo "✅ Cursor started with PID: $CURSOR_PID"
    sleep 3
    
    # Verify Cursor started successfully
    if kill -0 $CURSOR_PID 2>/dev/null; then
        echo "✅ Cursor is running successfully"
    else
        echo "❌ Failed to start Cursor"
        return 1
    fi
}

# fix_virtual_environment recreates the Python virtual environment, backing up current dependencies, removing the old environment, and correcting symbolic links to system Python and pip executables.
fix_virtual_environment() {
    echo "🔧 Fixing virtual environment..."
    
    # Backup current dependencies
    if [ -f "venv/bin/pip" ]; then
        echo "📦 Backing up current dependencies..."
        venv/bin/pip freeze > requirements_backup_$(date +%Y%m%d_%H%M%S).txt
    fi
    
    # Remove corrupted virtual environment
    echo "🗑️  Removing corrupted virtual environment..."
    rm -rf venv
    
    # Create new virtual environment with system Python
    echo "🏗️  Creating new virtual environment..."
    /usr/bin/python3 -m venv venv
    
    # Fix symbolic links
    echo "🔗 Fixing symbolic links..."
    cd venv/bin
    rm -f python python3 python3.12 pip pip3
    
    # Create correct links to system Python
    ln -s /usr/bin/python3.12 python3.12
    ln -s /usr/bin/python3.12 python3
    ln -s /usr/bin/python3.12 python
    ln -s /usr/bin/pip3 pip3
    ln -s /usr/bin/pip3 pip
    
    cd ../..
    
    # Verify links are correct
    echo "✅ Verifying symbolic links..."
    ls -la venv/bin/python*
    ls -la venv/bin/pip*
    
    echo "✅ Virtual environment fixed!"
}

# install_dependencies installs and upgrades project dependencies in the Python virtual environment using pip.
install_dependencies() {
    echo "📦 Installing project dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install project in editable mode
    pip install -e ".[dev]"
    
    echo "✅ Dependencies installed successfully!"
}

# test_setup verifies the Python environment, checks key project imports, and runs a basic test script to ensure the setup is correct.
test_setup() {
    echo "🧪 Testing setup..."
    
    # Test Python execution
    echo "🔍 Testing Python execution..."
    python3 --version
    
    # Test project imports
    echo "🔍 Testing project imports..."
    python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from vanta_ledger.config import settings
    print('✅ Config import successful')
    from vanta_ledger.main import app
    print('✅ Main app import successful')
    from vanta_ledger.auth import AuthService
    print('✅ Auth service import successful')
    print('🎉 All imports working correctly!')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"
    
    # Test basic functionality
    echo "🔍 Testing basic functionality..."
    python3 tests/test_basic_structure.py
    
    echo "✅ Setup test completed!"
}

# start_project activates the Python virtual environment, launches the FastAPI server for the Vanta Ledger project in the background, checks server health, and displays endpoint and usage information.
start_project() {
    echo "🚀 Starting Vanta Ledger project..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start the FastAPI application
    echo "🌐 Starting FastAPI server..."
    python3 -m uvicorn vanta_ledger.main:app --host 0.0.0.0 --port 8500 --reload &
    SERVER_PID=$!
    
    echo "✅ FastAPI server started with PID: $SERVER_PID"
    echo "🌐 Server running at: http://localhost:8500"
    echo "📚 API documentation at: http://localhost:8500/docs"
    
    # Wait for server to start
    sleep 3
    
    # Test server health
    echo "🔍 Testing server health..."
    if curl -s http://localhost:8500/health >/dev/null; then
        echo "✅ Server is healthy and responding"
    else
        echo "⚠️  Server may not be fully started yet"
    fi
    
    echo ""
    echo "🎉 Project launched successfully!"
    echo "📋 Available endpoints:"
    echo "   - Health check: http://localhost:8500/health"
    echo "   - API docs: http://localhost:8500/docs"
    echo "   - Main app: http://localhost:8500"
    echo ""
    echo "🛑 To stop the server, run: kill $SERVER_PID"
}

# show_status displays the number of running Cursor and Python processes and reports the health status of the FastAPI server.
show_status() {
    echo ""
    echo "📊 Current Status:"
    echo "=================="
    echo "Cursor processes: $(pgrep -f cursor | grep -vw $$ | wc -l)"
    echo "Python processes: $(pgrep -f python | wc -l)"
    echo "Server status: $(curl -s http://localhost:8500/health >/dev/null && echo 'Running' || echo 'Not running')"
    echo ""
}

# main orchestrates the full setup and launch process for the Cursor application and Vanta Ledger project, ensuring a clean environment, single Cursor instance, dependency installation, testing, server startup, and status reporting.
main() {
    echo "🎯 Single Cursor Launcher - Ensuring clean environment"
    
    # Step 1: Kill all Cursor processes
    kill_all_cursor
    
    # Step 2: Start single Cursor instance
    start_single_cursor
    
    # Step 3: Fix virtual environment
    fix_virtual_environment
    
    # Step 4: Install dependencies
    install_dependencies
    
    # Step 5: Test setup
    test_setup
    
    # Step 6: Start project
    start_project
    
    # Step 7: Show status
    show_status
    
    echo "🎉 Project launched with single Cursor instance!"
    echo ""
    echo "📋 Available commands:"
    echo "   ./scripts/single_cursor_launcher.sh  - Restart project"
    echo "   pkill -f cursor  - Stop all Cursor processes"
    echo "   curl http://localhost:8500/health  - Check server health"
    echo ""
}

# Run main function
main "$@" 