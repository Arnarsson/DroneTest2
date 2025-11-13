# DroneWatch Source Verification - Automated Cron Setup
**Wave 12 Implementation | Version 1.1.0**

---

## Overview

Automated hourly monitoring of all 77 RSS feeds with critical failure alerting.

**Features**:
- ✅ Hourly verification of all RSS sources
- ✅ Automatic alerting on critical failures (10+ sources down)
- ✅ Log rotation (7-day retention)
- ✅ Multi-channel alert support (email, Slack, file-based)
- ✅ Virtual environment auto-activation
- ✅ Exit code monitoring for CI/CD integration

---

## Quick Start

### 1. Prerequisites

**Install Python dependencies**:
```bash
cd /path/to/DroneWatch2.0/ingestion
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Verify script is executable**:
```bash
chmod +x verify_sources_cron.sh
```

**Test manual run**:
```bash
./verify_sources_cron.sh
```

Expected output in `logs/cron_verify.log`:
```
========================================
Source Verification Run: 2025-10-14 12:00:00
========================================
✅ SUCCESS: All sources verified successfully
Exit code: 0
========================================
```

---

## Installation

### Option 1: Crontab (Recommended)

**Add hourly verification**:
```bash
# Edit your crontab
crontab -e

# Add this line (replace /path/to/ with your actual path)
0 * * * * /path/to/DroneWatch2.0/ingestion/verify_sources_cron.sh

# Example with absolute path:
# 0 * * * * /home/user/DroneWatch2.0/ingestion/verify_sources_cron.sh
```

**Schedule Options**:
```bash
# Every hour on the hour (recommended)
0 * * * * /path/to/verify_sources_cron.sh

# Every 30 minutes (more frequent monitoring)
*/30 * * * * /path/to/verify_sources_cron.sh

# Every 6 hours (less frequent, lower resource usage)
0 */6 * * * /path/to/verify_sources_cron.sh

# Daily at 6 AM only
0 6 * * * /path/to/verify_sources_cron.sh
```

**Verify installation**:
```bash
# List your cron jobs
crontab -l

# Check cron service is running
sudo systemctl status cron
```

---

### Option 2: Systemd Timer (Advanced)

For more control and better logging integration.

**1. Create service file**:
```bash
sudo nano /etc/systemd/system/dronewatch-verify.service
```

```ini
[Unit]
Description=DroneWatch Source Verification
After=network.target

[Service]
Type=oneshot
User=YOUR_USERNAME
WorkingDirectory=/path/to/DroneWatch2.0/ingestion
ExecStart=/path/to/DroneWatch2.0/ingestion/verify_sources_cron.sh
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dronewatch-verify

[Install]
WantedBy=multi-user.target
```

**2. Create timer file**:
```bash
sudo nano /etc/systemd/system/dronewatch-verify.timer
```

```ini
[Unit]
Description=Run DroneWatch Source Verification Hourly
Requires=dronewatch-verify.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h
Unit=dronewatch-verify.service
AccuracySec=1min

[Install]
WantedBy=timers.target
```

**3. Enable and start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dronewatch-verify.timer
sudo systemctl start dronewatch-verify.timer
sudo systemctl status dronewatch-verify.timer
```

**Monitor execution**:
```bash
# View timer status
sudo systemctl list-timers | grep dronewatch

# View service logs
sudo journalctl -u dronewatch-verify.service -f

# View last run
sudo journalctl -u dronewatch-verify.service -n 50
```

---

## Alert Configuration

The script supports three alert mechanisms for critical failures (10+ sources down):

### 1. Email Alerts

**Configure email**:
```bash
# Edit verify_sources_cron.sh
nano verify_sources_cron.sh

# Uncomment and configure these lines (around line 57):
ALERT_EMAIL="your-email@example.com"
echo "$ALERT_MSG" | mail -s "DroneWatch Alert: Source Verification Failed" "$ALERT_EMAIL"
```

**Prerequisites**:
- `mail` or `mailx` must be installed and configured
- SMTP server configured on the system

### 2. Slack Notifications

**Configure Slack webhook**:
```bash
# Edit verify_sources_cron.sh
nano verify_sources_cron.sh

# Uncomment and configure these lines (around line 63):
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"$ALERT_MSG\"}" \
  "$SLACK_WEBHOOK_URL" 2>/dev/null
```

**Setup Slack webhook**:
1. Go to https://api.slack.com/apps
2. Create new app → Incoming Webhooks
3. Activate webhooks and add to workspace
4. Copy webhook URL

### 3. File-Based Alerts (Default)

**Always enabled** - writes to `logs/ALERT_CRITICAL_FAILURE.txt`

External monitoring systems can watch this file:
```bash
# Example: Monitor for alerts
watch -n 60 'cat logs/ALERT_CRITICAL_FAILURE.txt 2>/dev/null | tail -5'
```

---

## Monitoring

### View Recent Runs

```bash
cd /path/to/DroneWatch2.0/ingestion

# Last 50 lines of cron log
tail -n 50 logs/cron_verify.log

# Last 100 lines of detailed verification log
tail -n 100 logs/source_verification.log

# Search for failures
grep "⚠️" logs/cron_verify.log

# Search for critical alerts
grep "🚨" logs/cron_verify.log

# View latest markdown report (if failures occurred)
ls -lt logs/verification_report_*.md | head -1
cat $(ls -t logs/verification_report_*.md | head -1)
```

### Check Cron Status

```bash
# Verify cron job is scheduled
crontab -l | grep verify_sources

# View cron execution logs (Debian/Ubuntu)
grep CRON /var/log/syslog | grep verify_sources | tail -20

# View cron execution logs (RHEL/CentOS)
grep CRON /var/log/cron | grep verify_sources | tail -20

# Check for systemd timer (if using systemd)
sudo systemctl status dronewatch-verify.timer
sudo systemctl list-timers | grep dronewatch
```

### Performance Metrics

```bash
# Count successful runs in last 24 hours
grep "✅ SUCCESS" logs/cron_verify.log | grep "$(date +%Y-%m-%d)" | wc -l

# Count failed runs in last 24 hours
grep "⚠️  FAILURE" logs/cron_verify.log | grep "$(date +%Y-%m-%d)" | wc -l

# View critical alerts
cat logs/ALERT_CRITICAL_FAILURE.txt 2>/dev/null
```

---

## Logs and Reports

### Log Files

All logs stored in `ingestion/logs/`:

| File | Purpose | Retention |
|------|---------|-----------|
| `cron_verify.log` | Cron execution history | 7 days |
| `source_verification.log` | Detailed verification output | 7 days |
| `verification_report_YYYYMMDD_HHMMSS.md` | Failure reports | 7 days |
| `ALERT_CRITICAL_FAILURE.txt` | Critical failure alerts | 7 days |

### Log Rotation

**Automatic**: Runs after each verification
- Deletes files older than 7 days
- Keeps directory size manageable

**Manual cleanup**:
```bash
# Delete all logs older than 7 days
find logs/ -type f -mtime +7 -delete

# Delete all logs (fresh start)
rm -f logs/*.log logs/*.md logs/*.txt
```

---

## Troubleshooting

### Cron Job Not Running

**Symptoms**:
- No new entries in `logs/cron_verify.log`
- No recent timestamps

**Solutions**:

1. **Check cron service**:
   ```bash
   sudo systemctl status cron  # Debian/Ubuntu
   sudo systemctl status crond # RHEL/CentOS
   ```

2. **Verify crontab entry**:
   ```bash
   crontab -l | grep verify_sources
   ```

3. **Check script permissions**:
   ```bash
   ls -l verify_sources_cron.sh
   # Should show: -rwxr-xr-x (executable)
   ```

4. **Test manual execution**:
   ```bash
   cd /path/to/DroneWatch2.0/ingestion
   ./verify_sources_cron.sh
   ```

5. **Check cron logs**:
   ```bash
   grep CRON /var/log/syslog | tail -20  # Debian/Ubuntu
   grep CRON /var/log/cron | tail -20    # RHEL/CentOS
   ```

---

### Python Environment Issues

**Error**: `ModuleNotFoundError: No module named 'aiohttp'`

**Solution**:
```bash
cd /path/to/DroneWatch2.0/ingestion
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Error**: `python3: command not found`

**Solution**: Install Python 3 or specify full path in script
```bash
# Option 1: Install Python 3
sudo apt-get install python3 python3-venv  # Debian/Ubuntu
sudo yum install python3                    # RHEL/CentOS

# Option 2: Modify script to use full path
which python3  # Find Python location
# Edit script and replace 'python3' with full path
```

---

### Permission Denied

**Error**: `Permission denied: ./verify_sources_cron.sh`

**Solution**:
```bash
chmod +x verify_sources_cron.sh
```

**Error**: `Permission denied: logs/cron_verify.log`

**Solution**:
```bash
# Ensure log directory is writable
mkdir -p logs
chmod 755 logs
```

---

### Cron Environment Issues

**Problem**: Script works manually but fails in cron

**Cause**: Cron has minimal PATH environment

**Solution**: Use absolute paths in script (already implemented)

**Debug**:
```bash
# Add to crontab for debugging
* * * * * env > /tmp/cron-env.txt

# Compare to your shell environment
env > /tmp/shell-env.txt
diff /tmp/cron-env.txt /tmp/shell-env.txt
```

---

## Performance Expectations

| Metric | Value |
|--------|-------|
| **Execution Time** | 3-6 seconds |
| **Sources Verified** | 77 RSS feeds |
| **Memory Usage** | ~50 MB |
| **CPU Usage** | Negligible (<1%) |
| **Network Traffic** | ~1-2 MB per run |
| **Disk I/O** | ~10 KB (logs) |

**Hourly Resource Usage**:
- 24 runs per day
- ~150 seconds total execution time
- ~50 MB traffic per day
- Minimal impact on system performance

---

## Uninstall

### Remove Cron Job

```bash
# Edit crontab
crontab -e

# Delete the line with verify_sources_cron.sh
# Save and exit
```

### Remove Systemd Timer

```bash
sudo systemctl stop dronewatch-verify.timer
sudo systemctl disable dronewatch-verify.timer
sudo rm /etc/systemd/system/dronewatch-verify.service
sudo rm /etc/systemd/system/dronewatch-verify.timer
sudo systemctl daemon-reload
```

### Clean Up Logs

```bash
cd /path/to/DroneWatch2.0/ingestion
rm -rf logs/
```

---

## Advanced Configuration

### Custom Log Retention

Edit `verify_sources_cron.sh`:
```bash
RETENTION_DAYS=7  # Change to desired number of days
```

### Custom Verification Schedule

```bash
# Edit verify_sources_cli.py arguments in cron script
python3 verify_sources_cli.py --github-actions --workers 20 --timeout 15
```

### Integration with External Monitoring

**Prometheus exporter** (example):
```bash
# Parse logs and expose metrics
cat logs/source_verification.log | grep "Working:" | tail -1 | \
  awk '{print "dronewatch_sources_working " $2}'
```

**Nagios/Icinga check** (example):
```bash
#!/bin/bash
# Check if verification ran in last 2 hours
LAST_RUN=$(stat -c %Y logs/cron_verify.log)
NOW=$(date +%s)
AGE=$((NOW - LAST_RUN))

if [ $AGE -gt 7200 ]; then
    echo "CRITICAL: Last verification run $((AGE / 3600)) hours ago"
    exit 2
else
    echo "OK: Last verification $((AGE / 60)) minutes ago"
    exit 0
fi
```

---

## Summary

✅ **Automated Monitoring**: Hourly verification of all 77 RSS feeds  
✅ **Smart Alerting**: Multi-channel notifications on critical failures  
✅ **Log Management**: 7-day retention with automatic cleanup  
✅ **Low Resource Usage**: 3-6 seconds per run, minimal impact  
✅ **Production Ready**: Battle-tested error handling and recovery  

**Recommended Configuration**:
- **Schedule**: Hourly (`0 * * * *`)
- **Alerts**: Enable at least one channel (email or Slack)
- **Monitoring**: Check logs weekly for trends

---

## Support

**Issues**: Check logs first (`logs/cron_verify.log`)  
**Documentation**: See `WAVE12_DESIGN.md` for architecture details  
**Testing**: Run `./verify_sources_cron.sh` manually to debug  

---

**Last Updated**: 2025-11-13  
**Version**: Wave 12 v1.1.0  
**Maintained by**: DroneWatch Development Team  
**Repository**: https://github.com/Arnarsson/DroneWatch2.0
