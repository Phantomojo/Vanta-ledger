#!/bin/bash

# 🔒 Automated Security Monitor for Vanta Ledger
# Runs daily security scans and generates reports

set -e

# Configuration
PROJECT_DIR="/home/phantomojo/Vanta-ledger"
LOG_DIR="$PROJECT_DIR/logs"
REPORT_DIR="$PROJECT_DIR/security_reports"
DATE=$(date +%Y%m%d_%H%M%S)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Create directories
mkdir -p "$LOG_DIR"
mkdir -p "$REPORT_DIR"

# Function to log messages
log_message() {
    echo "[$(date)] $1" | tee -a "$LOG_DIR/security_monitor.log"
}

# Function to send alert
send_alert() {
    local message="$1"
    local level="$2"
    
    case $level in
        "critical")
            echo -e "${RED}🚨 CRITICAL ALERT: $message${NC}"
            ;;
        "high")
            echo -e "${YELLOW}⚠️ HIGH ALERT: $message${NC}"
            ;;
        "medium")
            echo -e "${YELLOW}⚠️ MEDIUM ALERT: $message${NC}"
            ;;
        *)
            echo -e "${GREEN}ℹ️ INFO: $message${NC}"
            ;;
    esac
    
    log_message "[$level] $message"
}

# Start security scan
log_message "Starting daily security scan..."

cd "$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run safety scan
log_message "Running Safety security scan..."
if safety scan --policy-file .safety-policy.yml --output json > "$REPORT_DIR/security_scan_$DATE.json"; then
    send_alert "Security scan completed successfully" "info"
else
    send_alert "Security scan failed or found new vulnerabilities" "high"
fi

# Generate human-readable report
log_message "Generating security report..."
safety scan --policy-file .safety-policy.yml --output screen > "$REPORT_DIR/security_report_$DATE.txt"

# Check for new vulnerabilities
log_message "Checking for new vulnerabilities..."
if grep -q "vulnerabilities found" "$REPORT_DIR/security_report_$DATE.txt"; then
    VULN_COUNT=$(grep -o "[0-9]* vulnerabilities found" "$REPORT_DIR/security_report_$DATE.txt" | head -1 | grep -o "[0-9]*")
    send_alert "Found $VULN_COUNT vulnerabilities in scan" "medium"
else
    send_alert "No new vulnerabilities detected" "info"
fi

# Check for critical vulnerabilities
if grep -q "CRITICAL" "$REPORT_DIR/security_report_$DATE.txt"; then
    send_alert "CRITICAL vulnerabilities detected - immediate action required" "critical"
fi

# Clean up old reports (keep last 30 days)
find "$REPORT_DIR" -name "security_*" -mtime +30 -delete

log_message "Daily security scan completed"
