# Wave 12 Source Verification - Cron Setup

## Automated Hourly Source Monitoring

This guide explains how to set up automated hourly verification of all 77 RSS feeds.

---

## Prerequisites

1. **Virtual Environment**:
   ```bash
   cd /home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Test Manual Run**:
   ```bash
   ./cron_verify_sources.sh
   ```
   Should complete successfully and create log in `logs/cron_verify.log`

---

## Cron Installation

### Option 1: Hourly Verification (Recommended)

```bash
# Edit crontab
crontab -e

# Add this line (runs at minute 0 of every hour)
0 * * * * /home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion/cron_verify_sources.sh
```

**Schedule**: Every hour on the hour (00:00, 01:00, 02:00, etc.)

### Option 2: Custom Schedule

```bash
# Every 30 minutes
*/30 * * * * /home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion/cron_verify_sources.sh

# Every 6 hours
0 */6 * * * /home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion/cron_verify_sources.sh

# Daily at 6 AM
0 6 * * * /home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion/cron_verify_sources.sh
```

### Option 3: Systemd Timer (Advanced)

For more control and better logging, use systemd:

1. Create service file: `/etc/systemd/system/dronewatch-verify.service`
   ```ini
   [Unit]
   Description=DroneWatch Source Verification
   After=network.target

   [Service]
   Type=oneshot
   User=svenni
   WorkingDirectory=/home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion
   ExecStart=/home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion/cron_verify_sources.sh
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   ```

2. Create timer file: `/etc/systemd/system/dronewatch-verify.timer`
   ```ini
   [Unit]
   Description=Run DroneWatch Source Verification Hourly
   Requires=dronewatch-verify.service

   [Timer]
   OnBootSec=5min
   OnUnitActiveSec=1h
   Unit=dronewatch-verify.service

   [Install]
   WantedBy=timers.target
   ```

3. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable dronewatch-verify.timer
   sudo systemctl start dronewatch-verify.timer
   sudo systemctl status dronewatch-verify.timer
   ```

---

## What the Cron Job Does

1. **Activates Python virtual environment** (if exists)
2. **Runs source verification** on all 77 feeds
3. **Logs output** to `logs/cron_verify.log`
4. **Generates markdown reports** when failures detected
5. **Rotates old logs** (keeps last 30 days)
6. **Returns exit code** for monitoring

---

## Monitoring

### Check Last Run

```bash
# View recent cron runs
tail -n 50 ~/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion/logs/cron_verify.log

# Check for failures
grep "⚠️" ~/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion/logs/cron_verify.log

# View latest markdown report
ls -lt ~/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion/logs/verification_report_*.md | head -1
```

### Cron Status

```bash
# Check if cron job is scheduled
crontab -l | grep verify_sources

# View cron execution logs (system-wide)
grep CRON /var/log/syslog | grep verify_sources

# Systemd timer status (if using systemd)
sudo systemctl status dronewatch-verify.timer
sudo journalctl -u dronewatch-verify.service -f
```

---

## Alert Integration (Optional)

### Email Alerts on Failure

Add to cron job:
```bash
MAILTO=your-email@example.com
0 * * * * /path/to/cron_verify_sources.sh || echo "DroneWatch source verification failed" | mail -s "Alert: Source Verification Failure" your-email@example.com
```

### Slack Integration

Modify `cron_verify_sources.sh` to add at the end:
```bash
if [ $EXIT_CODE -ne 0 ]; then
    curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"⚠️ DroneWatch source verification found failures\"}" \
    https://hooks.slack.com/services/YOUR/WEBHOOK/URL
fi
```

---

## Troubleshooting

### Cron Job Not Running

**Check**:
1. Cron service status: `sudo systemctl status cron`
2. User permissions: Script must be executable (`chmod +x cron_verify_sources.sh`)
3. Path correctness: Use absolute paths in crontab
4. Cron environment: Cron has limited PATH, specify full paths

**Debug**:
```bash
# Test script manually
cd ingestion
./cron_verify_sources.sh

# Check cron logs
grep CRON /var/log/syslog | tail -20
```

### Python Environment Issues

**Error**: `ModuleNotFoundError: No module named 'aiohttp'`

**Solution**:
```bash
cd ingestion
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Denied

**Error**: `Permission denied: ./cron_verify_sources.sh`

**Solution**:
```bash
chmod +x ingestion/cron_verify_sources.sh
```

---

## Logs and Reports

**Log Files** (in `ingestion/logs/`):
- `cron_verify.log` - Cron execution history
- `source_verification.log` - Detailed verification results
- `verification_report_YYYYMMDD_HHMMSS.md` - Markdown reports (when failures occur)

**Log Rotation**:
- Automatic cleanup after 30 days
- Manual cleanup: `find logs/ -type f -mtime +30 -delete`

---

## Performance

**Expected Execution Time**: 3-6 seconds for 77 sources
**Resource Usage**: ~50 MB RAM, negligible CPU
**Network**: ~1-2 MB traffic per run

---

## Uninstall

```bash
# Remove from crontab
crontab -e
# Delete the line with verify_sources

# Or disable systemd timer
sudo systemctl stop dronewatch-verify.timer
sudo systemctl disable dronewatch-verify.timer
```

---

## Summary

✅ **Hourly verification** of all 77 RSS feeds
✅ **Automatic alerts** when sources fail
✅ **Detailed reports** with failure analysis
✅ **Log rotation** (30-day retention)
✅ **Low resource usage** (~3-6 seconds per run)

**Recommended Schedule**: Hourly (`0 * * * *`)

---

**Last Updated**: October 14, 2025
**Version**: Wave 12 v1.0
**Maintained by**: DroneWatch Development Team
