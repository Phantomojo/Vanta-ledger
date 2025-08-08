#!/bin/bash

# Script to ensure only one Cursor window is open at any time
# This prevents multiple Cursor windows from opening during Python execution

echo "🖥️  Cursor Single Window Manager"
echo "================================"

# kill_all_cursor terminates all running Cursor application processes, first attempting a graceful shutdown and then forcefully killing any remaining instances.
kill_all_cursor() {
    echo "🔄 Killing all Cursor processes..."
    
    # Kill all cursor processes
    pkill -f "cursor.AppImage" 2>/dev/null
    pkill -f "cursor" 2>/dev/null
    
    # Wait a moment for processes to terminate
    sleep 2
    
    # Force kill any remaining processes
    pkill -9 -f "cursor" 2>/dev/null
    
    echo "✅ All Cursor processes terminated"
}

# is_cursor_running checks if any Cursor process is currently running and returns success if found, failure otherwise.
is_cursor_running() {
    pgrep -f "cursor.AppImage" >/dev/null 2>&1
    return $?
}

# start_cursor_single ensures only one Cursor process is running by terminating existing instances and launching Cursor in single instance mode.
start_cursor_single() {
    echo "🚀 Starting Cursor in single instance mode..."
    
    # Kill any existing Cursor processes first
    kill_all_cursor
    
    # Start Cursor with single instance flag
    /home/phantomojo/Applications/cursor.AppImage --single-instance &
    
    echo "✅ Cursor started in single instance mode"
}

# monitor_cursor continuously checks for multiple running Cursor processes and enforces a single instance by terminating extras and restarting Cursor if needed.
monitor_cursor() {
    echo "👁️  Monitoring Cursor processes..."
    
    while true; do
        # Count Cursor processes
        cursor_count=$(pgrep -f "cursor" | wc -l)
        
        if [ "$cursor_count" -gt 1 ]; then
            echo "⚠️  Multiple Cursor processes detected ($cursor_count), killing extras..."
            kill_all_cursor
            sleep 1
            start_cursor_single
        fi
        
        # Sleep for 5 seconds before next check
        sleep 5
    done
}

# create_systemd_service creates and starts a systemd user service to monitor and enforce a single instance of the Cursor application.
create_systemd_service() {
    echo "🔧 Creating systemd user service for Cursor management..."
    
    # Create service file
    cat > ~/.config/systemd/user/cursor-single.service << EOF
[Unit]
Description=Cursor Single Window Manager
After=graphical-session.target

[Service]
Type=simple
ExecStart=$PWD/scripts/cursor_single_window.sh --monitor
Restart=always
RestartSec=5

[Install]
WantedBy=graphical-session.target
EOF

    # Enable and start the service
    systemctl --user enable cursor-single.service
    systemctl --user start cursor-single.service
    
    echo "✅ Systemd service created and started"
    echo "   To stop: systemctl --user stop cursor-single.service"
    echo "   To disable: systemctl --user disable cursor-single.service"
}

# show_status displays the number and PIDs of running Cursor processes, indicating whether none, one, or multiple instances are active.
show_status() {
    echo ""
    echo "📊 Current Cursor Status:"
    echo "========================="
    
    cursor_processes=$(pgrep -f "cursor")
    cursor_count=$(echo "$cursor_processes" | wc -l)
    
    if [ "$cursor_count" -eq 0 ]; then
        echo "✅ No Cursor processes running"
    elif [ "$cursor_count" -eq 1 ]; then
        echo "✅ Single Cursor process running (PID: $cursor_processes)"
    else
        echo "⚠️  Multiple Cursor processes running ($cursor_count):"
        echo "$cursor_processes" | while read pid; do
            echo "   PID: $pid"
        done
    fi
    
    echo ""
}

# create_desktop_shortcut creates a desktop shortcut that launches the Cursor application in single instance mode using this script.
create_desktop_shortcut() {
    echo "🔧 Creating desktop shortcut for single instance Cursor..."
    
    cat > ~/Desktop/Cursor-Single.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Cursor (Single Instance)
Comment=Start Cursor with single instance mode
Exec=$PWD/scripts/cursor_single_window.sh --start
Icon=/home/phantomojo/Applications/cursor.AppImage
Terminal=false
Categories=Development;IDE;
EOF

    chmod +x ~/Desktop/Cursor-Single.desktop
    
    echo "✅ Desktop shortcut created: ~/Desktop/Cursor-Single.desktop"
}

# create_python_wrapper creates a shell script that wraps Python execution to prevent Cursor windows by terminating Cursor processes before and after running a Python script.
create_python_wrapper() {
    echo "🐍 Creating Python wrapper to prevent Cursor windows..."
    
    cat > scripts/safe_python.sh << 'EOF'
#!/bin/bash

# Safe Python wrapper that prevents Cursor windows
# Usage: ./scripts/safe_python.sh <script.py>

# Kill any Cursor processes before running Python
pkill -f "cursor.AppImage" 2>/dev/null

# Use system Python explicitly
/usr/bin/python3 "$@"

# Kill any Cursor processes that might have started
pkill -f "cursor.AppImage" 2>/dev/null
EOF

    chmod +x scripts/safe_python.sh
    
    echo "✅ Python wrapper created: scripts/safe_python.sh"
    echo "   Usage: ./scripts/safe_python.sh <script.py>"
}

# add_to_bashrc configures the user's .bashrc to enforce single-instance Cursor protection and safe Python execution in new terminal sessions.
add_to_bashrc() {
    echo "🔧 Adding Cursor protection to .bashrc..."
    
    # Check if already added
    if ! grep -q "cursor_single_window.sh" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# Cursor Single Window Protection" >> ~/.bashrc
        echo "alias python='$PWD/scripts/safe_python.sh'" >> ~/.bashrc
        echo "alias python3='$PWD/scripts/safe_python.sh'" >> ~/.bashrc
        echo "source $PWD/scripts/cursor_single_window.sh --protect" >> ~/.bashrc
        
        echo "✅ Added to .bashrc - protection will be active in new terminals"
    else
        echo "✅ Already configured in .bashrc"
    fi
}

# protect_session kills all running Cursor processes and sets up aliases in the current shell session to ensure Python commands use a wrapper that prevents multiple Cursor windows.
protect_session() {
    echo "🛡️  Protecting current session from multiple Cursor windows..."
    
    # Kill existing Cursor processes
    kill_all_cursor
    
    # Create aliases for this session
    alias python="$PWD/scripts/safe_python.sh"
    alias python3="$PWD/scripts/safe_python.sh"
    
    echo "✅ Session protected - Python commands will use safe wrapper"
}

# main parses command-line options and executes the corresponding Cursor management function or setup action.
main() {
    case "${1:-}" in
        "--kill")
            kill_all_cursor
            ;;
        "--start")
            start_cursor_single
            ;;
        "--monitor")
            monitor_cursor
            ;;
        "--status")
            show_status
            ;;
        "--setup")
            create_systemd_service
            create_desktop_shortcut
            create_python_wrapper
            add_to_bashrc
            ;;
        "--protect")
            protect_session
            ;;
        "--help"|"-h"|"")
            echo "Usage: $0 [OPTION]"
            echo ""
            echo "Options:"
            echo "  --kill     Kill all Cursor processes"
            echo "  --start    Start Cursor in single instance mode"
            echo "  --monitor  Monitor and maintain single instance"
            echo "  --status   Show current Cursor status"
            echo "  --setup    Setup complete single instance system"
            echo "  --protect  Protect current session"
            echo "  --help     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --kill      # Kill all Cursor windows"
            echo "  $0 --start     # Start single Cursor instance"
            echo "  $0 --setup     # Complete setup for single instance"
            echo ""
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "   Use --help for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 