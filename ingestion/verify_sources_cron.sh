#!/bin/bash
###############################################################################
# DroneWatch Source Verification - Cron Wrapper Script
# Wave 12 Implementation
# 
# Purpose: Automated hourly verification of all 77 RSS feeds
# Schedule: Add to crontab: 0 * * * * /path/to/verify_sources_cron.sh
#
# Author: DroneWatch Development Team
# Date: 2025-10-14
# Version: 1.1.0
###############################################################################

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Configuration
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/source_verification.log"
CRON_LOG="$LOG_DIR/cron_verify.log"
RETENTION_DAYS=7  # Keep logs for 7 days

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
fi

# Start logging
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "========================================" >> "$CRON_LOG"
echo "Source Verification Run: $TIMESTAMP" >> "$CRON_LOG"
echo "========================================" >> "$CRON_LOG"

# Run verification with GitHub Actions mode (exits 1 on critical failures)
python3 verify_sources_cli.py --github-actions >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Log results
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ SUCCESS: All sources verified successfully" >> "$CRON_LOG"
    echo "✅ SUCCESS: All sources verified successfully" >> "$LOG_FILE"
else
    echo "⚠️  FAILURE: Source verification detected issues (exit code: $EXIT_CODE)" >> "$CRON_LOG"
    echo "⚠️  FAILURE: Source verification detected issues (exit code: $EXIT_CODE)" >> "$LOG_FILE"
    
    # ALERT: Send notification on critical failures (10+ sources down)
    # This indicates a systemic issue that needs immediate attention
    if [ $EXIT_CODE -eq 1 ]; then
        ALERT_MSG="CRITICAL: DroneWatch source verification failed with $EXIT_CODE failures. Check logs: $LOG_FILE"
        
        # Log the alert
        echo "🚨 ALERT: $ALERT_MSG" >> "$CRON_LOG"
        
        # Option 1: Send email alert (requires mail/mailx to be configured)
        # Uncomment and configure ALERT_EMAIL to enable
        # ALERT_EMAIL="your-email@example.com"
        # echo "$ALERT_MSG" | mail -s "DroneWatch Alert: Source Verification Failed" "$ALERT_EMAIL"
        
        # Option 2: Send Slack notification (requires SLACK_WEBHOOK_URL)
        # Uncomment and configure SLACK_WEBHOOK_URL to enable
        # SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
        # curl -X POST -H 'Content-type: application/json' \
        #   --data "{\"text\":\"$ALERT_MSG\"}" \
        #   "$SLACK_WEBHOOK_URL" 2>/dev/null
        
        # Option 3: Write alert file for external monitoring systems
        ALERT_FILE="$LOG_DIR/ALERT_CRITICAL_FAILURE.txt"
        echo "$TIMESTAMP: $ALERT_MSG" >> "$ALERT_FILE"
    fi
fi

echo "" >> "$CRON_LOG"
echo "Exit code: $EXIT_CODE" >> "$CRON_LOG"
echo "" >> "$CRON_LOG"

# Log rotation - Keep last 7 days only
echo "Running log rotation (keeping last $RETENTION_DAYS days)..." >> "$CRON_LOG"

# Delete old log files
find "$LOG_DIR" -name "cron_verify.log" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null
find "$LOG_DIR" -name "source_verification.log" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null
find "$LOG_DIR" -name "verification_report_*.md" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null
find "$LOG_DIR" -name "ALERT_*.txt" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null

echo "Log rotation complete" >> "$CRON_LOG"
echo "========================================" >> "$CRON_LOG"
echo "" >> "$CRON_LOG"

# Exit with the verification script's exit code
# This allows cron/systemd to detect failures
exit $EXIT_CODE
