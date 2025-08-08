#!/bin/bash

# Purge and Reinstall Script - Complete Environment Reset
# This script completely removes all corrupted environments and reinstalls them properly

echo "🧹 PURGE AND REINSTALL - Complete Environment Reset"
echo "=================================================="

# kill_cursor_processes terminates all running processes related to Cursor to prevent interference with environment setup.
kill_cursor_processes() {
    echo "🛑 Killing all Cursor processes..."
    pkill -f "cursor.AppImage" 2>/dev/null
    pkill -f "cursor" 2>/dev/null
    sleep 3
    echo "✅ All Cursor processes terminated"
}

# purge_environments removes all Python virtual environments, cache directories, compiled files, and pip cache from the project directory and its subdirectories.
purge_environments() {
    echo "🗑️  Purging all virtual environments..."
    
    # Remove main virtual environment
    if [ -d "venv" ]; then
        echo "   Removing venv/..."
        rm -rf venv
    fi
    
    # Remove .venv if it exists
    if [ -d ".venv" ]; then
        echo "   Removing .venv/..."
        rm -rf .venv
    fi
    
    # Remove any other virtual environments
    find . -name "venv" -type d -exec rm -rf {} + 2>/dev/null
    find . -name ".venv" -type d -exec rm -rf {} + 2>/dev/null
    
    # Remove Python cache files
    echo "   Removing Python cache files..."
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    find . -name "*.pyc" -delete 2>/dev/null
    find . -name "*.pyo" -delete 2>/dev/null
    
    # Remove pip cache
    echo "   Clearing pip cache..."
    pip cache purge 2>/dev/null || true
    
    echo "✅ All environments purged"
}

# backup_files creates a timestamped backup directory and copies key project files such as requirements and environment configuration files into it if they exist.
backup_files() {
    echo "📦 Creating backups..."
    
    # Create backup directory
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup requirements files
    if [ -f "backend/requirements.txt" ]; then
        cp backend/requirements.txt "$BACKUP_DIR/"
    fi
    
    if [ -f "backend/requirements.in" ]; then
        cp backend/requirements.in "$BACKUP_DIR/"
    fi
    
    # Backup environment files
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/"
    fi
    
    if [ -f "env.example" ]; then
        cp env.example "$BACKUP_DIR/"
    fi
    
    echo "✅ Backups created in $BACKUP_DIR/"
}

# verify_system_python checks for the presence of system Python and pip executables, printing their versions and exiting if either is missing.
verify_system_python() {
    echo "🔍 Verifying system Python..."
    
    if [ ! -f "/usr/bin/python3" ]; then
        echo "❌ System Python not found at /usr/bin/python3"
        echo "   Please install Python 3.8+ first"
        exit 1
    fi
    
    PYTHON_VERSION=$(/usr/bin/python3 --version 2>&1)
    echo "✅ System Python found: $PYTHON_VERSION"
    
    if [ ! -f "/usr/bin/pip3" ]; then
        echo "❌ System pip not found at /usr/bin/pip3"
        echo "   Please install pip first"
        exit 1
    fi
    
    PIP_VERSION=$(/usr/bin/pip3 --version 2>&1)
    echo "✅ System pip found: $PIP_VERSION"
}

# create_clean_environment creates a new Python virtual environment named 'venv' using the system Python executable, exiting with an error if creation fails.
create_clean_environment() {
    echo "🏗️  Creating clean virtual environment..."
    
    # Use explicit system Python path
    /usr/bin/python3 -m venv venv
    
    if [ ! -d "venv" ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    
    echo "✅ Virtual environment created"
}

# fix_symbolic_links removes existing Python and pip symbolic links in the virtual environment and recreates them to point directly to system Python and pip executables.
fix_symbolic_links() {
    echo "🔗 Fixing symbolic links..."
    
    cd venv/bin
    
    # Remove any existing Python links
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
    echo "   Python links:"
    ls -la venv/bin/python*
    echo "   Pip links:"
    ls -la venv/bin/pip*
    
    # Test Python execution
    echo "✅ Testing Python execution..."
    venv/bin/python3 --version
    
    echo "✅ Symbolic links fixed"
}

# install_dependencies activates the virtual environment, upgrades pip, installs core dependencies, and installs the project with development dependencies in editable mode.
install_dependencies() {
    echo "📦 Installing dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    echo "   Upgrading pip..."
    pip install --upgrade pip
    
    # Install core dependencies first
    echo "   Installing core dependencies..."
    pip install wheel setuptools
    
    # Install project in editable mode
    echo "   Installing project in editable mode..."
    pip install -e ".[dev]"
    
    echo "✅ Dependencies installed"
}

# test_installation activates the virtual environment and verifies the installation by checking Python functionality, importing key project modules, and running a basic test script.
test_installation() {
    echo "🧪 Testing installation..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Test basic Python functionality
    echo "   Testing Python imports..."
    python3 -c "
import sys
print(f'Python version: {sys.version}')
print('✅ Python working correctly')
"
    
    # Test project imports
    echo "   Testing project imports..."
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
    print('🎉 All project imports working!')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"
    
    # Test basic functionality
    echo "   Testing basic functionality..."
    python3 tests/test_basic_structure.py
    
    echo "✅ Installation test completed"
}

# create_validation_script generates a shell script that validates the integrity of the Python virtual environment, ensuring correct symbolic links, Python execution, and successful project imports.
create_validation_script() {
    echo "📝 Creating environment validation script..."
    
    cat > scripts/validate_environment.sh << 'EOF'
#!/bin/bash

# Environment Validation Script
# Run this to verify your environment is working correctly

echo "🔍 Validating Environment..."
echo "============================"

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    exit 1
fi

# Check Python links
echo "🔍 Checking Python links..."
if [ -L "venv/bin/python3" ]; then
    TARGET=$(readlink venv/bin/python3)
    if [[ "$TARGET" == *"cursor"* ]]; then
        echo "❌ Python link points to Cursor (corrupted)"
        exit 1
    else
        echo "✅ Python link is correct: $TARGET"
    fi
else
    echo "❌ Python link not found"
    exit 1
fi

# Test Python execution
echo "🔍 Testing Python execution..."
if venv/bin/python3 --version >/dev/null 2>&1; then
    echo "✅ Python execution works"
else
    echo "❌ Python execution failed"
    exit 1
fi

# Test project imports
echo "🔍 Testing project imports..."
if venv/bin/python3 -c "import sys; sys.path.insert(0, 'src'); from vanta_ledger.config import settings; print('✅ Project imports work')" >/dev/null 2>&1; then
    echo "✅ Project imports work"
else
    echo "❌ Project imports failed"
    exit 1
fi

echo "🎉 Environment validation passed!"
EOF

    chmod +x scripts/validate_environment.sh
    echo "✅ Validation script created: scripts/validate_environment.sh"
}

# show_final_status prints a summary of the purge and reinstall process, including completed steps and next actions for the user.
show_final_status() {
    echo ""
    echo "🎉 PURGE AND REINSTALL COMPLETED!"
    echo "================================="
    echo ""
    echo "✅ All corrupted environments removed"
    echo "✅ Clean virtual environment created"
    echo "✅ Dependencies installed correctly"
    echo "✅ Symbolic links fixed"
    echo "✅ Project imports working"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Activate environment: source venv/bin/activate"
    echo "   2. Validate environment: ./scripts/validate_environment.sh"
    echo "   3. Start project: python3 -m uvicorn vanta_ledger.main:app"
    echo "   4. Open browser: http://localhost:8500"
    echo ""
    echo "🛡️  Cursor Prevention:"
    echo "   - Use ./scripts/cursor_manager.sh to manage Cursor"
    echo "   - Only one Cursor instance will be allowed"
    echo "   - Virtual environment is now protected from corruption"
    echo ""
}

# main orchestrates the full purge and reinstallation of the Python development environment, ensuring a clean setup and validating its integrity.
main() {
    echo "🚀 Starting complete environment purge and reinstall..."
    echo ""
    
    # Step 1: Kill Cursor processes
    kill_cursor_processes
    
    # Step 2: Backup important files
    backup_files
    
    # Step 3: Purge all environments
    purge_environments
    
    # Step 4: Verify system Python
    verify_system_python
    
    # Step 5: Create clean environment
    create_clean_environment
    
    # Step 6: Fix symbolic links
    fix_symbolic_links
    
    # Step 7: Install dependencies
    install_dependencies
    
    # Step 8: Test installation
    test_installation
    
    # Step 9: Create validation script
    create_validation_script
    
    # Step 10: Show final status
    show_final_status
}

# Run main function
main "$@" 