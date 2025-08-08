#!/bin/bash

# ⏰ Setup Automated Security Monitoring Cron Jobs

CRON_FILE="/tmp/vanta_security_cron"

# Create cron jobs
cat > $CRON_FILE << 'CRON_JOBS'
# Vanta Ledger Security Monitoring Cron Jobs
# Generated: $(date)

# Daily security scan at 6 AM
0 6 * * * cd /home/phantomojo/Vanta-ledger && ./security_monitor.sh >> /home/phantomojo/Vanta-ledger/logs/cron.log 2>&1

# Weekly security report every Sunday at 8 AM
0 8 * * 0 cd /home/phantomojo/Vanta-ledger && ./weekly_security_report.sh >> /home/phantomojo/Vanta-ledger/logs/cron.log 2>&1

# Monthly dependency update check on 1st of month at 10 AM
0 10 1 * * cd /home/phantomojo/Vanta-ledger && ./security_fix.sh >> /home/phantomojo/Vanta-ledger/logs/cron.log 2>&1
CRON_JOBS

echo "🔒 Security cron jobs created:"
echo "----------------------------------------"
cat $CRON_FILE
echo ""
echo "To install these cron jobs, run:"
echo "crontab $CRON_FILE"
echo ""
echo "To view current cron jobs:"
echo "crontab -l"
echo ""
echo "To remove cron jobs:"
echo "crontab -r"
