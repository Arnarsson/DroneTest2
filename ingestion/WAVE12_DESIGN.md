# Wave 12: Source Verification System - Architecture Design

**Date**: October 14, 2025
**Status**: Design Phase
**Target**: Automated monitoring for 77 RSS feeds

---

## Executive Summary

Build an automated source verification system that continuously monitors all 77 RSS feeds, detects failures, and alerts when sources break. Uses parallel processing for efficient verification of all sources simultaneously.

**Key Requirements**:
- Verify all 77 RSS feeds (HTTP status + RSS parsing)
- Detect broken/changed feeds automatically
- Alert on feed failures
- Parallel verification for speed
- Detailed reporting and logging

---

## Architecture Overview

### 1. Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                   Source Verification System                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Parallel   │───▶│   RSS Feed   │───▶│   Alerting   │      │
│  │  Verificat   │    │   Parser     │    │   System     │      │
│  │      ion     │    │              │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              Status Database (JSON)                   │       │
│  │  - Last check timestamp                               │       │
│  │  - HTTP status codes                                  │       │
│  │  - Parse success/failure                              │       │
│  │  - Failure history                                     │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Verification Workflow

```
┌────────────┐
│   Start    │
└──────┬─────┘
       │
       ▼
┌────────────────────────────┐
│ Load 77 sources from       │
│ config.py                  │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ Create parallel tasks       │
│ (10 workers)               │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ For each source:           │
│ 1. HTTP GET request        │
│ 2. Check status code       │
│ 3. Parse RSS feed          │
│ 4. Record result           │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ Aggregate results:         │
│ - Success count            │
│ - Failure count            │
│ - Broken feeds list        │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ Generate report:           │
│ - Markdown summary         │
│ - Failure details          │
│ - Recommended actions      │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ Alert if failures:         │
│ - Console output           │
│ - Log file                 │
│ - Optional: Email/Slack    │
└──────┬─────────────────────┘
       │
       ▼
┌────────────┐
│    End     │
└────────────┘
```

---

## Component Details

### 1. Parallel Verification Engine

**File**: `ingestion/source_verifier.py`

**Purpose**: Core verification logic with parallel processing

**Key Features**:
- Async/await for parallel HTTP requests
- Configurable worker count (default: 10 concurrent)
- Request timeout (10 seconds per source)
- Retry logic (3 attempts with exponential backoff)
- User-Agent header to avoid bot blocking

**Verification Steps**:
1. **HTTP Check**: Send GET request, verify 200 OK status
2. **Content-Type Check**: Validate RSS content type (text/xml, application/rss+xml, application/xml)
3. **RSS Parse Check**: Parse with feedparser, verify valid RSS structure
4. **Entry Count Check**: Ensure feed has at least 1 entry
5. **Timestamp Check**: Verify feed has been updated recently (< 90 days)

**Return Value**: `VerificationResult` object
```python
@dataclass
class VerificationResult:
    source_name: str
    url: str
    http_status: int
    content_type: str
    parse_success: bool
    entry_count: int
    last_updated: Optional[datetime]
    error_message: Optional[str]
    verification_time: float  # seconds
    success: bool  # Overall success flag
```

### 2. RSS Feed Parser

**File**: `ingestion/source_verifier.py` (integrated)

**Purpose**: Validate RSS feed structure and content

**Key Features**:
- Uses `feedparser` library (robust RSS/Atom parsing)
- Handles malformed feeds gracefully
- Extracts key metadata (title, last updated, entry count)
- Detects common RSS issues (empty feeds, invalid XML)

**Validation Criteria**:
- Feed has valid `bozo` flag (feedparser's well-formedness check)
- Feed has `entries` array
- At least 1 entry present
- Entries have required fields (title, link, published date)

### 3. Alerting System

**File**: `ingestion/alerting.py`

**Purpose**: Notify when sources fail verification

**Alert Levels**:
- **INFO**: 1-2 sources failed (minor, log only)
- **WARNING**: 3-9 sources failed (medium, console output)
- **CRITICAL**: 10+ sources failed (severe, full report + email option)

**Alert Channels**:
1. **Console Output**: Colorized terminal output with status
2. **Log File**: `logs/source_verification.log` with full details
3. **Markdown Report**: `logs/verification_report_YYYYMMDD_HHMMSS.md`
4. **Optional Email**: SMTP integration (configurable)
5. **Optional Slack**: Webhook integration (configurable)

**Alert Content**:
- Failed source count
- List of broken URLs
- HTTP status codes
- Error messages
- Recommended actions (retry, contact source, replace feed)

### 4. Status Database

**File**: `logs/source_status.json`

**Purpose**: Track source health over time

**Schema**:
```json
{
  "last_check": "2025-10-14T15:30:00Z",
  "sources": {
    "dr_news": {
      "url": "https://www.dr.dk/nyheder/service/feeds/allenyheder",
      "status": "ok",
      "http_status": 200,
      "last_success": "2025-10-14T15:30:00Z",
      "last_failure": null,
      "failure_count": 0,
      "consecutive_failures": 0,
      "average_response_time": 0.45,
      "entry_count": 50,
      "last_updated": "2025-10-14T14:00:00Z"
    },
    "broken_feed": {
      "url": "https://example.com/broken",
      "status": "failed",
      "http_status": 404,
      "last_success": "2025-10-10T10:00:00Z",
      "last_failure": "2025-10-14T15:30:00Z",
      "failure_count": 12,
      "consecutive_failures": 4,
      "error_message": "HTTP 404 Not Found"
    }
  },
  "summary": {
    "total_sources": 77,
    "working": 75,
    "failed": 2,
    "success_rate": 97.4
  }
}
```

**Features**:
- Historical tracking (last 30 days of checks)
- Failure patterns (consecutive failures, total failure count)
- Performance metrics (average response time)
- Trend analysis (improving vs degrading sources)

---

## Implementation Plan

### Phase 1: Core Verification (Day 1)

**Files to Create**:
1. `ingestion/source_verifier.py` - Main verification engine
2. `ingestion/alerting.py` - Alert system
3. `ingestion/verify_sources.py` - CLI script

**Tasks**:
- ✅ Async HTTP client with parallel processing
- ✅ RSS feed parsing with feedparser
- ✅ Result aggregation and reporting
- ✅ Basic console output

**Testing**:
```bash
cd ingestion
python3 verify_sources.py --verbose
```

Expected output:
```
Source Verification Report
==========================
Total Sources: 77
✅ Working: 75 (97.4%)
❌ Failed: 2 (2.6%)

Broken Sources:
  1. example_feed (HTTP 404)
     URL: https://example.com/broken
     Error: Not Found

  2. another_feed (Parse Error)
     URL: https://example.com/invalid
     Error: Invalid XML structure

Verification completed in 8.5 seconds
```

### Phase 2: Status Tracking (Day 2)

**Files to Create**:
1. `logs/source_status.json` - Status database
2. `ingestion/status_tracker.py` - Historical tracking

**Tasks**:
- ✅ JSON database for source history
- ✅ Trend analysis (failure patterns)
- ✅ Performance metrics (response times)
- ✅ Automatic cleanup (remove old data > 30 days)

**Testing**:
```bash
python3 verify_sources.py --check-history
```

Expected output:
```
Source Health Trends (Last 7 Days)
===================================
dr_news: ✅✅✅✅✅✅✅ (100% uptime)
svt_nyheter: ✅✅✅✅✅✅✅ (100% uptime)
broken_feed: ❌❌❌❌✅✅✅ (57% uptime, degrading)
```

### Phase 3: Alerting Integration (Day 3)

**Files to Create**:
1. `ingestion/alerting.py` - Alert logic
2. `config/alert_config.json` - Alert configuration

**Tasks**:
- ✅ Multi-channel alerting (console, log, markdown)
- ✅ Alert level thresholds (INFO, WARNING, CRITICAL)
- ✅ Optional integrations (email, Slack)
- ✅ Alert deduplication (don't spam on consecutive failures)

**Configuration** (`config/alert_config.json`):
```json
{
  "alert_levels": {
    "info": {
      "min_failures": 1,
      "max_failures": 2,
      "channels": ["log"]
    },
    "warning": {
      "min_failures": 3,
      "max_failures": 9,
      "channels": ["log", "console"]
    },
    "critical": {
      "min_failures": 10,
      "channels": ["log", "console", "markdown", "email"]
    }
  },
  "email": {
    "enabled": false,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from": "dronewatch@example.com",
    "to": ["admin@example.com"]
  },
  "slack": {
    "enabled": false,
    "webhook_url": "https://hooks.slack.com/..."
  }
}
```

### Phase 4: Automation & Scheduling (Day 4)

**Files to Create**:
1. `scripts/cron_verify_sources.sh` - Cron wrapper
2. `.github/workflows/verify_sources.yml` - GitHub Actions

**Tasks**:
- ✅ Cron job setup (hourly verification)
- ✅ GitHub Actions integration (daily verification on CI)
- ✅ Log rotation (keep last 30 days only)
- ✅ Automatic recovery testing (retry failed sources)

**Cron Setup** (`crontab -e`):
```bash
# Verify sources every hour
0 * * * * cd /path/to/DroneWatch2.0/ingestion && python3 verify_sources.py >> logs/cron_verify.log 2>&1
```

**GitHub Actions** (`.github/workflows/verify_sources.yml`):
```yaml
name: Source Verification

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd ingestion
          pip install -r requirements.txt
      - name: Verify sources
        run: |
          cd ingestion
          python3 verify_sources.py --github-actions
      - name: Upload report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: verification-report
          path: ingestion/logs/verification_report_*.md
```

---

## Testing Strategy

### Unit Tests

**File**: `ingestion/test_source_verifier.py`

**Test Cases**:
1. `test_http_success_200()` - Valid RSS feed returns success
2. `test_http_failure_404()` - Broken URL returns failure
3. `test_http_failure_timeout()` - Slow source times out correctly
4. `test_rss_parse_valid()` - Valid RSS XML parses successfully
5. `test_rss_parse_invalid()` - Invalid XML returns parse error
6. `test_parallel_verification()` - 77 sources verified in < 20 seconds
7. `test_retry_logic()` - Failed requests retry 3 times
8. `test_status_tracking()` - Status database updates correctly

### Integration Tests

**File**: `ingestion/test_verify_sources_integration.py`

**Test Scenarios**:
1. Verify all 77 production sources
2. Check for any broken feeds
3. Validate status database integrity
4. Test alert generation (mock failures)
5. Verify markdown report format

### Performance Benchmarks

**Target Metrics**:
- Verify 77 sources in < 20 seconds (3.8 sources/sec with 10 workers)
- Average response time < 2 seconds per source
- Memory usage < 100 MB
- CPU usage < 50% (parallel processing)

---

## Error Handling

### Common Failures

1. **HTTP 404 Not Found**
   - **Cause**: Feed URL moved or deleted
   - **Action**: Check source website, find new RSS URL, update config.py

2. **HTTP 403 Forbidden**
   - **Cause**: Bot blocking, User-Agent check
   - **Action**: Update User-Agent header, add retry delay

3. **HTTP 410 Gone**
   - **Cause**: Feed permanently discontinued
   - **Action**: Remove from config.py, find alternative source

4. **Timeout (>10s)**
   - **Cause**: Slow server, network issues
   - **Action**: Increase timeout, check network, contact source

5. **Parse Error (Invalid XML)**
   - **Cause**: Malformed RSS, server error, non-RSS content
   - **Action**: Check Content-Type, validate XML, contact source

6. **Empty Feed (0 entries)**
   - **Cause**: Feed not updated, server issue
   - **Action**: Wait 24h, check if temporary, contact source

### Retry Strategy

**Exponential Backoff**:
- Attempt 1: Immediate
- Attempt 2: Wait 2 seconds
- Attempt 3: Wait 4 seconds
- Give up after 3 attempts

**Permanent vs Temporary Failures**:
- **Temporary**: 503 Service Unavailable, timeouts → Retry
- **Permanent**: 404 Not Found, 410 Gone → Don't retry, log immediately

---

## Monitoring Dashboard

### CLI Output

```
╔══════════════════════════════════════════════════════════════╗
║            DroneWatch Source Verification Report             ║
╠══════════════════════════════════════════════════════════════╣
║ Timestamp: 2025-10-14 15:30:00 UTC                          ║
║ Duration: 8.5 seconds                                        ║
╠══════════════════════════════════════════════════════════════╣
║ Total Sources:     77                                        ║
║ ✅ Working:         75 (97.4%)                               ║
║ ❌ Failed:          2  (2.6%)                                ║
║ ⚠️ Degraded:        3  (3.9%)                                ║
╠══════════════════════════════════════════════════════════════╣
║ Performance:                                                 ║
║   Average Response Time: 1.8s                                ║
║   Fastest: dr_news (0.3s)                                    ║
║   Slowest: example_feed (9.8s)                               ║
╠══════════════════════════════════════════════════════════════╣
║ Failed Sources:                                              ║
║   1. broken_feed                                             ║
║      URL: https://example.com/broken                         ║
║      Error: HTTP 404 Not Found                               ║
║      Last Success: 4 days ago                                ║
║                                                              ║
║   2. timeout_feed                                            ║
║      URL: https://example.com/slow                           ║
║      Error: Request timeout (>10s)                           ║
║      Last Success: 2 hours ago                               ║
╠══════════════════════════════════════════════════════════════╣
║ Degraded Sources (slow but working):                        ║
║   • slow_feed_1 (8.5s)                                       ║
║   • slow_feed_2 (7.2s)                                       ║
║   • slow_feed_3 (6.8s)                                       ║
╠══════════════════════════════════════════════════════════════╣
║ Recommendations:                                             ║
║   • Update broken_feed URL in config.py                      ║
║   • Increase timeout for timeout_feed                        ║
║   • Monitor degraded sources for performance issues          ║
╚══════════════════════════════════════════════════════════════╝
```

### Markdown Report

**File**: `logs/verification_report_20251014_153000.md`

```markdown
# Source Verification Report

**Date**: October 14, 2025 15:30:00 UTC
**Duration**: 8.5 seconds
**Status**: ⚠️ WARNING - 2 sources failed

---

## Summary

| Metric | Value |
|--------|-------|
| Total Sources | 77 |
| ✅ Working | 75 (97.4%) |
| ❌ Failed | 2 (2.6%) |
| ⚠️ Degraded | 3 (3.9%) |
| Average Response Time | 1.8s |

---

## Failed Sources

### 1. broken_feed

- **URL**: https://example.com/broken
- **Error**: HTTP 404 Not Found
- **Last Success**: 4 days ago (October 10, 2025)
- **Failure Count**: 12 consecutive failures
- **Recommended Action**: Update RSS URL in config.py or remove source

### 2. timeout_feed

- **URL**: https://example.com/slow
- **Error**: Request timeout (exceeded 10 seconds)
- **Last Success**: 2 hours ago (October 14, 2025 13:30 UTC)
- **Failure Count**: 2 consecutive failures
- **Recommended Action**: Increase timeout or check network connectivity

---

## Degraded Sources

These sources are working but responding slowly (>5 seconds):

| Source | Response Time | Status |
|--------|---------------|--------|
| slow_feed_1 | 8.5s | ⚠️ Slow |
| slow_feed_2 | 7.2s | ⚠️ Slow |
| slow_feed_3 | 6.8s | ⚠️ Slow |

---

## Performance Breakdown

**Fastest Sources**:
1. dr_news (0.3s)
2. svt_nyheter (0.4s)
3. nrk_news (0.5s)

**Slowest Sources**:
1. slow_feed_1 (8.5s)
2. slow_feed_2 (7.2s)
3. slow_feed_3 (6.8s)

---

## Recommendations

1. **Immediate Actions**:
   - Update broken_feed URL in `ingestion/config.py`
   - Investigate timeout_feed network issues

2. **Monitoring**:
   - Watch degraded sources for further performance degradation
   - Set up alerts for consecutive failures (>3)

3. **Long-term**:
   - Consider adding backup sources for critical feeds
   - Implement automatic source rotation on repeated failures

---

**Next Verification**: Hourly (via cron)
**Generated by**: DroneWatch Source Verification System v1.0
```

---

## Success Criteria

### Functional Requirements

- ✅ Verify all 77 RSS feeds successfully
- ✅ Detect broken feeds within 1 hour of failure
- ✅ Generate detailed reports (console + markdown)
- ✅ Track source health over time (30-day history)
- ✅ Alert on critical failures (10+ sources down)
- ✅ Complete verification in < 20 seconds

### Non-Functional Requirements

- ✅ Parallel processing (10 concurrent workers)
- ✅ Robust error handling (graceful failures)
- ✅ Low resource usage (< 100 MB RAM)
- ✅ Automated scheduling (hourly cron)
- ✅ No false positives (accurate failure detection)

---

## Dependencies

**Python Libraries** (add to `ingestion/requirements.txt`):
```
aiohttp==3.9.0        # Async HTTP client
feedparser==6.0.10    # RSS/Atom parser
colorama==0.4.6       # Terminal colors
tabulate==0.9.0       # Table formatting
```

**System Requirements**:
- Python 3.11+
- Network access (HTTP/HTTPS)
- Disk space for logs (~ 100 MB)

---

## Deployment Checklist

- [ ] Create `ingestion/source_verifier.py`
- [ ] Create `ingestion/alerting.py`
- [ ] Create `ingestion/verify_sources.py` CLI script
- [ ] Add dependencies to `requirements.txt`
- [ ] Create `logs/` directory
- [ ] Test with subset of sources (10 feeds)
- [ ] Test with all 77 sources
- [ ] Set up cron job (hourly)
- [ ] Set up GitHub Actions (daily)
- [ ] Document in CLAUDE.md
- [ ] Commit and push to production

---

**Design Complete**: Ready for implementation
**Estimated Development Time**: 2-3 days
**Priority**: High (prevent broken sources from degrading data quality)
