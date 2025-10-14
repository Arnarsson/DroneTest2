#!/bin/bash
# Cron wrapper for Wave 12 Source Verification System
# Add to crontab: 0 * * * * /path/to/cron_verify_sources.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set timestamp for log file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# Run verification and capture output
echo "=== Source Verification Run: $(date) ===" >> "$LOG_DIR/cron_verify.log"
python3 verify_sources_cli.py --github-actions 2>&1 | tee -a "$LOG_DIR/cron_verify.log"

# Check exit code
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -ne 0 ]; then
    echo "⚠️ Source verification found failures (exit code: $EXIT_CODE)" >> "$LOG_DIR/cron_verify.log"
else
    echo "✅ Source verification completed successfully" >> "$LOG_DIR/cron_verify.log"
fi

echo "" >> "$LOG_DIR/cron_verify.log"

# Rotate logs (keep last 30 days)
find "$LOG_DIR" -name "cron_verify.log" -type f -mtime +30 -delete
find "$LOG_DIR" -name "verification_report_*.md" -type f -mtime +30 -delete
find "$LOG_DIR" -name "source_verification.log" -type f -mtime +30 -delete

exit $EXIT_CODE
