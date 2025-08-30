#!/bin/bash

# 📊 Security Dashboard for Vanta Ledger
# Real-time security status and metrics

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

clear
echo -e "${PURPLE}🔒 Vanta Ledger Security Dashboard${NC}"
echo "=========================================="
echo ""

# Current status
echo -e "${BLUE}📊 Current Security Status:${NC}"
echo "----------------------------------------"

# Run quick security scan
if command -v safety &> /dev/null; then
    echo "Running security scan..."
    SCAN_OUTPUT=$(safety scan --policy-file .safety-policy.yml 2>/dev/null || echo "Scan failed")
    
    # Extract vulnerability counts
    CRITICAL=$(echo "$SCAN_OUTPUT" | grep -c "CRITICAL" || echo "0")
    HIGH=$(echo "$SCAN_OUTPUT" | grep -c "HIGH" || echo "0")
    MEDIUM=$(echo "$SCAN_OUTPUT" | grep -c "MEDIUM" || echo "0")
    LOW=$(echo "$SCAN_OUTPUT" | grep -c "LOW" || echo "0")
    
    echo -e "Critical: ${RED}$CRITICAL${NC}"
    echo -e "High: ${YELLOW}$HIGH${NC}"
    echo -e "Medium: ${YELLOW}$MEDIUM${NC}"
    echo -e "Low: ${GREEN}$LOW${NC}"
else
    echo -e "${RED}Safety CLI not available${NC}"
fi

echo ""
echo -e "${BLUE}📦 Package Status:${NC}"
echo "----------------------------------------"

# Check package status
if [ -d "venv" ]; then
    source venv/bin/activate
    TOTAL_PACKAGES=$(pip list | wc -l)
    OUTDATED_PACKAGES=$(pip list --outdated | wc -l)
    
    echo "Total packages: $TOTAL_PACKAGES"
    echo -e "Outdated packages: ${YELLOW}$OUTDATED_PACKAGES${NC}"
else
    echo "Virtual environment not found"
fi

echo ""
echo -e "${BLUE}🔍 Recent Security Events:${NC}"
echo "----------------------------------------"

# Show recent security logs
if [ -f "logs/security_monitor.log" ]; then
    echo "Recent security events:"
    tail -5 logs/security_monitor.log | while read line; do
        echo "  $line"
    done
else
    echo "No security logs found"
fi

echo ""
echo -e "${BLUE}🎯 Quick Actions:${NC}"
echo "----------------------------------------"
echo "1. Run full security scan: ./security_monitor.sh"
echo "2. Generate weekly report: ./weekly_security_report.sh"
echo "3. Update dependencies: ./security_fix.sh"
echo "4. View security dashboard: ./security_dashboard.sh"

echo ""
echo -e "${GREEN}✅ Security Dashboard Complete${NC}"
