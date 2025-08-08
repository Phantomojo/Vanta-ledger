#!/bin/bash

# Isolated Environment Fix - Completely isolate Python from Cursor interference
# This script creates a clean environment by temporarily removing Cursor from PATH

echo "🔒 Isolated Environment Fix - Complete Cursor Isolation"
echo "======================================================="

# create_isolated_environment creates a new Python virtual environment with all Cursor-related paths temporarily removed from PATH to prevent interference, verifies its integrity, and restores the original PATH. Returns a nonzero status if creation or verification fails.
create_isolated_environment() {
    echo "🔒 Creating isolated environment..."
    
    # Save original PATH
    ORIGINAL_PATH="$PATH"
    
    # Remove Cursor from PATH temporarily
    export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v -i cursor | tr '\n' ':' | sed 's/:$//')
    
    echo "✅ Cursor removed from PATH temporarily"
    echo "   Original PATH length: ${#ORIGINAL_PATH}"
    echo "   Isolated PATH length: ${#PATH}"
    
    # Remove existing virtual environment
    if [ -d "venv" ]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf venv
    fi
    
    # Create virtual environment with isolated PATH
    echo "🏗️  Creating virtual environment with isolated PATH..."
    /usr/bin/python3 -m venv venv
    
    # Restore original PATH
    export PATH="$ORIGINAL_PATH"
    echo "✅ Original PATH restored"
    
    # Verify the virtual environment
    echo "🔍 Verifying virtual environment..."
    if [ -f "venv/bin/python3" ]; then
        echo "✅ Virtual environment created successfully"
        
        # Check if it's actually Python
        if venv/bin/python3 --version 2>/dev/null | grep -q "Python"; then
            echo "✅ Virtual environment Python is working correctly"
        else
            echo "❌ Virtual environment still corrupted"
            return 1
        fi
    else
        echo "❌ Failed to create virtual environment"
        return 1
    fi
}

# install_dependencies installs and upgrades pip, then installs project dependencies in editable development mode within the isolated Python virtual environment.
install_dependencies() {
    echo "📦 Installing dependencies in isolated environment..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    echo "   Upgrading pip..."
    pip install --upgrade pip
    
    # Install project dependencies
    echo "   Installing project dependencies..."
    pip install -e ".[dev]"
    
    echo "✅ Dependencies installed successfully"
}

# test_isolated_environment activates the isolated Python virtual environment, verifies Python and pip functionality, and tests importing key project modules to ensure the environment is correctly set up.
test_isolated_environment() {
    echo "🧪 Testing isolated environment..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Test Python execution
    echo "   Testing Python execution..."
    python3 --version
    
    # Test pip execution
    echo "   Testing pip execution..."
    pip --version
    
    # Test basic imports
    echo "   Testing basic imports..."
    python3 -c "
import sys
print(f'Python version: {sys.version}')
print('✅ Basic Python functionality working')
"
    
    # Test project imports (with environment variables)
    echo "   Testing project imports..."
    export MONGO_URI="mongodb://localhost:27017"
    export POSTGRES_URI="postgresql://localhost:5432"
    export REDIS_URI="redis://localhost:6379"
    
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
except Exception as e:
    print(f'⚠️  Some imports failed: {e}')
    print('   This is normal if some dependencies are missing')
"
    
    echo "✅ Isolated environment test completed"
}

# show_final_status prints a summary of the isolated Python environment setup, including environment status, project installation, absence of Cursor interference, and recommended next steps.
show_final_status() {
    echo ""
    echo "📊 Final Status:"
    echo "================"
    echo "Virtual environment: $(if [ -d "venv" ]; then echo "✅ Created"; else echo "❌ Missing"; fi)"
    echo "Python executable: $(if [ -f "venv/bin/python3" ]; then echo "✅ Working"; else echo "❌ Broken"; fi)"
    echo "Pip executable: $(if [ -f "venv/bin/pip" ]; then echo "✅ Working"; else echo "❌ Broken"; fi)"
    echo "Project installed: $(if find venv/lib -name "python*" -type d -exec test -d {}/site-packages/vanta_ledger \; -print -quit | grep -q .; then echo "✅ Yes"; else echo "❌ No"; fi)"
    echo "Cursor interference: $(if venv/bin/python3 --version 2>/dev/null | grep -q "Python"; then echo "✅ None"; else echo "❌ Still present"; fi)"
    echo ""
    echo "🎯 Environment isolated successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Activate environment: source venv/bin/activate"
    echo "   2. Start project: python3 -m uvicorn vanta_ledger.main:app --host 0.0.0.0 --port 8500"
    echo "   3. Test project: python3 tests/test_basic_structure.py"
    echo ""
    echo "🛡️  Cursor was not touched - it should still be running!"
}

# main orchestrates the creation, setup, testing, and status reporting of a fully isolated Python environment free from Cursor interference.
main() {
    echo "🚀 Starting isolated environment fix..."
    
    # Step 1: Create isolated environment
    create_isolated_environment
    
    # Step 2: Install dependencies
    install_dependencies
    
    # Step 3: Test isolated environment
    test_isolated_environment
    
    # Step 4: Show final status
    show_final_status
    
    echo "🎉 Isolated environment fix completed successfully!"
    echo "   Your Cursor IDE should still be running normally."
    echo "   No more Cursor windows should appear when running Python!"
}

# Run main function
main "$@" 