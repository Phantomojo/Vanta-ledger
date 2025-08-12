#!/bin/bash

# Vanta Ledger System Upgrade Script
# ===================================

echo "🎯 Vanta Ledger System Upgrade"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -d "database" ]; then
    echo "❌ Error: Please run this script from the Vanta-ledger directory"
    exit 1
fi

echo "📋 Upgrade Summary:"
echo "  • Backup existing system"
echo "  • Remove old files and scripts"
echo "  • Install enhanced system (29 companies)"
echo "  • Update dependencies"
echo "  • Migrate database schema"
echo ""

# Ask for confirmation
read -p "Do you want to proceed with the upgrade? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Upgrade cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting upgrade process..."
echo "=============================="

# Run the upgrade
cd database
python3 vanta_ledger_system_upgrade.py

# Check if upgrade was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Upgrade completed successfully!"
    echo ""
    echo "📁 Files created:"
    echo "  • vanta_ledger_upgrade_report.json"
    echo "  • vanta_ledger_upgrade.log"
    echo "  • backup_YYYYMMDD_HHMMSS/ (your old system backup)"
    echo ""
    echo "🚀 Next steps:"
    echo "  1. Review the upgrade report"
    echo "  2. Run: python3 vanta_ledger_integration_master.py"
    echo "  3. Explore the new enhanced features"
    echo ""
    echo "✅ Your Vanta Ledger system now supports:"
    echo "  • 29 companies (was 10)"
    echo "  • AI-powered document processing"
    echo "  • Network analysis capabilities"
    echo "  • Enhanced analytics dashboard"
    echo "  • Comprehensive business intelligence"
else
    echo ""
    echo "❌ Upgrade failed!"
    echo "Check the logs for detailed error information."
    echo "Your backup is available for restoration if needed."
    exit 1
fi 