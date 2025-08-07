#!/bin/bash

# 🛡️ PERMANENT CURSOR FIX SCRIPT
# This script implements permanent system-level fixes to prevent Cursor IDE
# from interfering with Python virtual environments

set -e

echo "🛡️  PERMANENT CURSOR FIX - System Level Configuration"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root (needed for some operations)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root - this is fine for system-level changes"
    else
        print_status "Running as user - some changes may require sudo"
    fi
}

# Backup original configuration
backup_config() {
    print_status "Creating backup of current configuration..."
    
    BACKUP_DIR="$HOME/.cursor_fix_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup shell configuration files
    if [ -f "$HOME/.bashrc" ]; then
        cp "$HOME/.bashrc" "$BACKUP_DIR/"
    fi
    
    if [ -f "$HOME/.zshrc" ]; then
        cp "$HOME/.zshrc" "$BACKUP_DIR/"
    fi
    
    if [ -f "$HOME/.profile" ]; then
        cp "$HOME/.profile" "$BACKUP_DIR/"
    fi
    
    # Backup PATH environment
    echo "$PATH" > "$BACKUP_DIR/path_backup.txt"
    
    print_success "Backup created at: $BACKUP_DIR"
}

# Method 1: Fix shell configuration to prioritize system Python
fix_shell_config() {
    print_status "Method 1: Fixing shell configuration..."
    
    # Determine which shell configuration file to use
    SHELL_CONFIG=""
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        SHELL_CONFIG="$HOME/.bashrc"
    else
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    print_status "Using shell config: $SHELL_CONFIG"
    
    # Create backup of shell config
    if [ -f "$SHELL_CONFIG" ]; then
        cp "$SHELL_CONFIG" "${SHELL_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Add Python PATH prioritization to shell config
    cat >> "$SHELL_CONFIG" << 'EOF'

# 🛡️ CURSOR FIX: Prioritize system Python over Cursor
# This ensures system Python is found before Cursor's Python
export PATH="/usr/bin:/usr/local/bin:$PATH"

# 🛡️ CURSOR FIX: Function to create isolated Python environments
create_isolated_venv() {
    local venv_name="${1:-venv}"
    local python_path="${2:-/usr/bin/python3}"
    
    echo "🔧 Creating isolated virtual environment: $venv_name"
    
    # Save original PATH
    local original_path="$PATH"
    
    # Remove Cursor from PATH temporarily
    export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v -i cursor | tr '\n' ':' | sed 's/:$//')
    
    # Create virtual environment with explicit Python path
    "$python_path" -m venv "$venv_name"
    
    # Restore original PATH
    export PATH="$original_path"
    
    echo "✅ Isolated virtual environment created: $venv_name"
    echo "   Activate with: source $venv_name/bin/activate"
}

# 🛡️ CURSOR FIX: Function to check for Cursor interference
check_cursor_interference() {
    if [ -d "venv" ] && [ -L "venv/bin/python3" ]; then
        local target=$(readlink venv/bin/python3)
        if [[ "$target" == *"cursor"* ]]; then
            echo "❌ CORRUPTED: Virtual environment links to Cursor"
            echo "   Target: $target"
            return 1
        else
            echo "✅ OK: Virtual environment links to system Python"
            echo "   Target: $target"
            return 0
        fi
    else
        echo "ℹ️  No virtual environment found or Python is not a symbolic link"
        return 0
    fi
}

# 🛡️ CURSOR FIX: Function to fix corrupted virtual environment
fix_corrupted_venv() {
    if [ -d "venv" ]; then
        echo "🔧 Fixing corrupted virtual environment..."
        
        # Backup dependencies if possible
        if [ -f "venv/bin/pip" ]; then
            venv/bin/pip freeze > requirements_backup_$(date +%Y%m%d_%H%M%S).txt
        fi
        
        # Remove corrupted environment
        rm -rf venv
        
        # Create new isolated environment
        create_isolated_venv "venv"
        
        echo "✅ Virtual environment fixed!"
    else
        echo "ℹ️  No virtual environment found to fix"
    fi
}

# 🛡️ CURSOR FIX: Alias for quick environment creation
alias venv='create_isolated_venv'
alias check-venv='check_cursor_interference'
alias fix-venv='fix_corrupted_venv'
EOF

    print_success "Shell configuration updated"
    print_status "New functions available:"
    print_status "  - create_isolated_venv [name] [python_path]"
    print_status "  - check_cursor_interference"
    print_status "  - fix_corrupted_venv"
    print_status "  - venv (alias for create_isolated_venv)"
    print_status "  - check-venv (alias for check_cursor_interference)"
    print_status "  - fix-venv (alias for fix_corrupted_venv)"
}

# Method 2: Create system-wide Python wrapper
create_python_wrapper() {
    print_status "Method 2: Creating system-wide Python wrapper..."
    
    # Create wrapper script
    sudo tee /usr/local/bin/python3-safe > /dev/null << 'EOF'
#!/bin/bash

# 🛡️ PYTHON SAFE WRAPPER
# This wrapper ensures system Python is used instead of Cursor

# Check if we're in a virtual environment creation context
if [[ "$1" == "-m" && "$2" == "venv" ]]; then
    # For virtual environment creation, use system Python directly
    exec /usr/bin/python3 "$@"
else
    # For other operations, check if we're in a corrupted venv
    if [[ "$VIRTUAL_ENV" != "" && -L "$VIRTUAL_ENV/bin/python3" ]]; then
        TARGET=$(readlink "$VIRTUAL_ENV/bin/python3")
        if [[ "$TARGET" == *"cursor"* ]]; then
            echo "⚠️  WARNING: Virtual environment is corrupted (links to Cursor)"
            echo "   Run 'fix-venv' to fix this issue"
            echo "   Target: $TARGET"
        fi
    fi
    
    # Execute with system Python
    exec /usr/bin/python3 "$@"
fi
EOF

    # Make wrapper executable
    sudo chmod +x /usr/local/bin/python3-safe
    
    # Create symlinks
    sudo ln -sf /usr/local/bin/python3-safe /usr/local/bin/python-safe
    
    print_success "Python wrapper created at /usr/local/bin/python3-safe"
    print_status "Use 'python3-safe' instead of 'python3' for guaranteed system Python"
}

# Method 3: Configure Cursor IDE settings
configure_cursor_settings() {
    print_status "Method 3: Configuring Cursor IDE settings..."
    
    # Find Cursor settings directory
    CURSOR_SETTINGS_DIRS=(
        "$HOME/.config/Cursor/User"
        "$HOME/Library/Application Support/Cursor/User"
        "$APPDATA/Cursor/User"
    )
    
    for settings_dir in "${CURSOR_SETTINGS_DIRS[@]}"; do
        if [ -d "$settings_dir" ]; then
            print_status "Found Cursor settings at: $settings_dir"
            
            # Backup existing settings
            if [ -f "$settings_dir/settings.json" ]; then
                cp "$settings_dir/settings.json" "$settings_dir/settings.json.backup.$(date +%Y%m%d_%H%M%S)"
            fi
            
            # Create or update settings.json
            cat > "$settings_dir/settings.json" << 'EOF'
{
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "python.terminal.activateEnvironment": false,
    "python.terminal.activateEnvInCurrentTerminal": false,
    "python.autoDetect": false,
    "python.venvPath": "",
    "python.venvFolders": [],
    "terminal.integrated.env.linux": {
        "PATH": "/usr/bin:/usr/local/bin:${env:PATH}"
    },
    "terminal.integrated.env.osx": {
        "PATH": "/usr/bin:/usr/local/bin:${env:PATH}"
    },
    "terminal.integrated.env.windows": {
        "PATH": "C:\\Python3;C:\\Python3\\Scripts;${env:PATH}"
    }
}
EOF
            
            print_success "Cursor settings configured"
            break
        fi
    done
}

# Method 4: Create system-wide environment isolation
create_system_isolation() {
    print_status "Method 4: Creating system-wide environment isolation..."
    
    # Create system-wide script for environment creation
    sudo tee /usr/local/bin/create-venv-safe > /dev/null << 'EOF'
#!/bin/bash

# 🛡️ SYSTEM-WIDE SAFE VENV CREATION
# This script creates virtual environments without Cursor interference

set -e

VENV_NAME="${1:-venv}"
PYTHON_PATH="${2:-/usr/bin/python3}"

echo "🔧 Creating isolated virtual environment: $VENV_NAME"

# Save original PATH
ORIGINAL_PATH="$PATH"

# Remove Cursor from PATH temporarily
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v -i cursor | tr '\n' ':' | sed 's/:$//')

# Create virtual environment with explicit Python path
"$PYTHON_PATH" -m venv "$VENV_NAME"

# Restore original PATH
export PATH="$ORIGINAL_PATH"

echo "✅ Isolated virtual environment created: $VENV_NAME"
echo "   Activate with: source $VENV_NAME/bin/activate"
echo "   Verify with: ls -la $VENV_NAME/bin/python*"
EOF

    # Make script executable
    sudo chmod +x /usr/local/bin/create-venv-safe
    
    print_success "System-wide venv creation script created"
    print_status "Use 'create-venv-safe [name] [python_path]' for safe environment creation"
}

# Method 5: Create monitoring and auto-fix system
create_monitoring_system() {
    print_status "Method 5: Creating monitoring and auto-fix system..."
    
    # Create monitoring script
    cat > "$HOME/.local/bin/monitor-cursor-interference" << 'EOF'
#!/bin/bash

# 🛡️ CURSOR INTERFERENCE MONITOR
# Monitors and automatically fixes Cursor interference

MONITOR_LOG="$HOME/.cursor_monitor.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$MONITOR_LOG"
}

check_current_directory() {
    if [ -d "venv" ] && [ -L "venv/bin/python3" ]; then
        TARGET=$(readlink venv/bin/python3)
        if [[ "$TARGET" == *"cursor"* ]]; then
            log_message "CORRUPTION DETECTED in $(pwd): $TARGET"
            echo "❌ CORRUPTION DETECTED in $(pwd)"
            echo "   Target: $TARGET"
            return 1
        fi
    fi
    return 0
}

# Check current directory
check_current_directory

# If corruption detected and auto-fix is enabled
if [ $? -ne 0 ] && [ "$AUTO_FIX_CURSOR" = "true" ]; then
    log_message "Auto-fixing corruption in $(pwd)"
    fix_corrupted_venv
fi
EOF

    # Make monitoring script executable
    chmod +x "$HOME/.local/bin/monitor-cursor-interference"
    
    # Create auto-fix environment variable
    echo 'export AUTO_FIX_CURSOR="true"' >> "$HOME/.bashrc"
    echo 'export AUTO_FIX_CURSOR="true"' >> "$HOME/.zshrc"
    
    print_success "Monitoring system created"
    print_status "Auto-fix enabled: Set AUTO_FIX_CURSOR=true to auto-fix corruption"
}

# Method 6: Create comprehensive documentation
create_documentation() {
    print_status "Method 6: Creating comprehensive documentation..."
    
    # Create user documentation
    cat > "$HOME/.local/share/cursor-fix/README.md" << 'EOF'
# 🛡️ Cursor Fix - Permanent Solution

## Overview
This directory contains the permanent fix for Cursor IDE interference with Python virtual environments.

## Quick Commands
- `create-venv-safe [name]` - Create isolated virtual environment
- `python3-safe` - Use system Python (guaranteed)
- `check-venv` - Check for Cursor interference
- `fix-venv` - Fix corrupted virtual environment
- `venv` - Quick alias for create_isolated_venv

## Prevention Methods
1. **Always use isolated environment creation**
2. **Use system Python wrapper (python3-safe)**
3. **Check environments before use**
4. **Enable auto-fix monitoring**

## Troubleshooting
If you encounter Cursor interference:
1. Run `check-venv` to diagnose
2. Run `fix-venv` to repair
3. Use `create-venv-safe` for new environments
4. Check Cursor settings if issues persist

## Configuration Files
- Shell config: ~/.bashrc or ~/.zshrc
- Cursor settings: ~/.config/Cursor/User/settings.json
- System wrapper: /usr/local/bin/python3-safe
- Monitoring: ~/.local/bin/monitor-cursor-interference
EOF

    mkdir -p "$HOME/.local/share/cursor-fix"
    
    print_success "Documentation created at $HOME/.local/share/cursor-fix/README.md"
}

# Main execution
main() {
    echo "🛡️  Starting permanent Cursor fix installation..."
    echo ""
    
    check_root
    backup_config
    fix_shell_config
    create_python_wrapper
    configure_cursor_settings
    create_system_isolation
    create_monitoring_system
    create_documentation
    
    echo ""
    echo "🎉 PERMANENT CURSOR FIX INSTALLATION COMPLETE!"
    echo "=============================================="
    echo ""
    echo "✅ System-level fixes applied:"
    echo "   - Shell configuration updated"
    echo "   - System Python wrapper created"
    echo "   - Cursor IDE settings configured"
    echo "   - Environment isolation system installed"
    echo "   - Monitoring and auto-fix system created"
    echo "   - Comprehensive documentation created"
    echo ""
    echo "🔄 To apply changes, restart your terminal or run:"
    echo "   source ~/.bashrc  # or source ~/.zshrc"
    echo ""
    echo "📋 New commands available:"
    echo "   - create-venv-safe [name] [python_path]"
    echo "   - python3-safe"
    echo "   - check-venv"
    echo "   - fix-venv"
    echo "   - venv"
    echo ""
    echo "📚 Documentation: $HOME/.local/share/cursor-fix/README.md"
    echo ""
    echo "🛡️  Cursor interference is now permanently prevented!"
}

# Run main function
main "$@" 