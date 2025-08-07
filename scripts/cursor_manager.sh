#!/bin/bash

# Cursor Process Manager - Ensures only one Cursor instance runs
# Usage: ./scripts/cursor_manager.sh [start|stop|status|restart]

CURSOR_APP="/home/phantomojo/Applications/cursor.AppImage"
LOCK_FILE="/tmp/cursor_single_instance.lock"

# Function to check if Cursor is running
is_cursor_running() {
    pgrep -f "cursor.AppImage" >/dev/null
}

# Function to get Cursor PID
get_cursor_pid() {
    pgrep -f "cursor.AppImage"
}

# Function to start Cursor (single instance)
start_cursor() {
    if is_cursor_running; then
        echo "✅ Cursor is already running (PID: $(get_cursor_pid))"
        return 0
    fi
    
    echo "🚀 Starting Cursor..."
    $CURSOR_APP &
    CURSOR_PID=$!
    
    # Create lock file
    echo $CURSOR_PID > $LOCK_FILE
    
    sleep 2
    
    if is_cursor_running; then
        echo "✅ Cursor started successfully (PID: $CURSOR_PID)"
    else
        echo "❌ Failed to start Cursor"
        rm -f $LOCK_FILE
        return 1
    fi
}

# Function to stop Cursor
stop_cursor() {
    if ! is_cursor_running; then
        echo "ℹ️  Cursor is not running"
        rm -f $LOCK_FILE
        return 0
    fi
    
    echo "🛑 Stopping Cursor..."
    pkill -f "cursor.AppImage"
    sleep 2
    
    # Kill any remaining Cursor processes
    if is_cursor_running; then
        echo "🔄 Force killing remaining Cursor processes..."
        pkill -9 -f "cursor.AppImage"
    fi
    
    rm -f $LOCK_FILE
    echo "✅ Cursor stopped"
}

# Function to restart Cursor
restart_cursor() {
    echo "🔄 Restarting Cursor..."
    stop_cursor
    sleep 1
    start_cursor
}

# Function to show status
show_status() {
    echo "📊 Cursor Status:"
    echo "================="
    
    if is_cursor_running; then
        echo "✅ Status: Running"
        echo "🆔 PID: $(get_cursor_pid)"
        echo "🔗 Lock file: $LOCK_FILE"
    else
        echo "❌ Status: Not running"
        echo "🔗 Lock file: $(if [ -f "$LOCK_FILE" ]; then echo "Exists (stale)"; else echo "Not found"; fi)"
    fi
    
    echo ""
    echo "📋 Available commands:"
    echo "   $0 start    - Start Cursor (single instance)"
    echo "   $0 stop     - Stop Cursor"
    echo "   $0 restart  - Restart Cursor"
    echo "   $0 status   - Show status"
}

# Function to clean up stale lock files
cleanup_lock() {
    if [ -f "$LOCK_FILE" ]; then
        LOCK_PID=$(cat $LOCK_FILE)
        if ! kill -0 $LOCK_PID 2>/dev/null; then
            echo "🧹 Cleaning up stale lock file..."
            rm -f $LOCK_FILE
        fi
    fi
}

# Main execution
main() {
    # Clean up stale lock files
    cleanup_lock
    
    case "${1:-status}" in
        start)
            start_cursor
            ;;
        stop)
            stop_cursor
            ;;
        restart)
            restart_cursor
            ;;
        status)
            show_status
            ;;
        *)
            echo "❌ Unknown command: $1"
            echo "Usage: $0 [start|stop|status|restart]"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 