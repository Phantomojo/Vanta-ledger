#!/bin/bash

# Script to use system Python instead of the problematic virtual environment
# This prevents Cursor windows from opening when running Python commands

echo "🐍 Using System Python (avoiding Cursor virtual environment)"
echo "=========================================================="

# Set environment variable to use system Python
export PYTHON_EXECUTABLE="/usr/bin/python3"

# Function to run Python commands with system Python
run_python() {
    /usr/bin/python3 "$@"
}

# Function to run pip commands with system Python
run_pip() {
    /usr/bin/python3 -m pip "$@"
}

echo "✅ System Python is now available as:"
echo "   - run_python <script.py>  (to run Python scripts)"
echo "   - run_pip <command>        (to run pip commands)"
echo ""
echo "Examples:"
echo "   run_python test_minimal.py"
echo "   run_pip install requests"
echo "   run_python -c \"import torch; print('PyTorch:', torch.__version__)\""
echo ""
echo "Or use the test_all.sh script which now uses system Python automatically."
echo ""

# Keep the shell open with the functions available
exec bash 