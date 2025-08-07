#!/bin/bash

# Script to prevent Cursor windows from opening during fixes
# This temporarily modifies the environment to avoid Cursor interference

echo "🛡️  Preventing Cursor windows from opening..."
echo "=============================================="

# Function to temporarily disable Cursor in PATH
disable_cursor_in_path() {
    # Save original PATH
    export ORIGINAL_PATH="$PATH"
    
    # Remove Cursor directories from PATH
    export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v -i cursor | tr '\n' ':' | sed 's/:$//')
    
    echo "✅ Temporarily disabled Cursor in PATH"
    echo "   Original PATH length: ${#ORIGINAL_PATH}"
    echo "   Modified PATH length: ${#PATH}"
}

# Function to restore original PATH
restore_path() {
    if [ ! -z "$ORIGINAL_PATH" ]; then
        export PATH="$ORIGINAL_PATH"
        echo "✅ Restored original PATH"
    fi
}

# Function to use system Python explicitly
use_system_python() {
    export PYTHON_EXECUTABLE="/usr/bin/python3"
    export PYTHON3_EXECUTABLE="/usr/bin/python3"
    export PIP_EXECUTABLE="/usr/bin/pip3"
    
    echo "✅ Set explicit system Python paths:"
    echo "   PYTHON_EXECUTABLE: $PYTHON_EXECUTABLE"
    echo "   PYTHON3_EXECUTABLE: $PYTHON3_EXECUTABLE"
    echo "   PIP_EXECUTABLE: $PIP_EXECUTABLE"
}

# Function to create safe Python aliases
create_safe_aliases() {
    alias python="/usr/bin/python3"
    alias python3="/usr/bin/python3"
    alias pip="/usr/bin/pip3"
    alias pip3="/usr/bin/pip3"
    
    echo "✅ Created safe Python aliases"
}

# Function to verify system Python
verify_system_python() {
    echo "🔍 Verifying system Python..."
    
    if [ -f "/usr/bin/python3" ]; then
        echo "✅ System Python found: /usr/bin/python3"
        /usr/bin/python3 --version
    else
        echo "❌ System Python not found at /usr/bin/python3"
        return 1
    fi
    
    if [ -f "/usr/bin/pip3" ]; then
        echo "✅ System pip found: /usr/bin/pip3"
        /usr/bin/pip3 --version
    else
        echo "❌ System pip not found at /usr/bin/pip3"
        return 1
    fi
}

# Function to check for Cursor processes
check_cursor_processes() {
    echo "🔍 Checking for Cursor processes..."
    
    cursor_processes=$(pgrep -f "cursor" 2>/dev/null | wc -l)
    if [ "$cursor_processes" -gt 0 ]; then
        echo "⚠️  Found $cursor_processes Cursor processes running"
        echo "   Consider running: pkill -f cursor"
    else
        echo "✅ No Cursor processes found"
    fi
}

# Function to show current environment status
show_status() {
    echo ""
    echo "📊 Current Environment Status:"
    echo "=============================="
    echo "System Python: $(which python3)"
    echo "System pip: $(which pip3)"
    echo "Virtual env Python: $(which python 2>/dev/null || echo 'Not in venv')"
    echo "PATH contains cursor: $(echo $PATH | grep -i cursor >/dev/null && echo 'YES' || echo 'NO')"
    echo ""
}

# Main execution
main() {
    echo "🚀 Starting Cursor prevention mode..."
    
    # Disable Cursor in PATH
    disable_cursor_in_path
    
    # Use system Python explicitly
    use_system_python
    
    # Create safe aliases
    create_safe_aliases
    
    # Verify system Python
    verify_system_python
    
    # Check for Cursor processes
    check_cursor_processes
    
    # Show status
    show_status
    
    echo "🎯 Environment prepared for safe Python operations"
    echo ""
    echo "📋 Available commands:"
    echo "   python3 <script.py>  - Run Python scripts safely"
    echo "   pip3 install <package>  - Install packages safely"
    echo "   restore_path  - Restore original PATH"
    echo ""
    echo "⚠️  Remember to run 'restore_path' when done!"
}

# Run main function
main "$@"

# Keep shell open with functions available
exec bash 