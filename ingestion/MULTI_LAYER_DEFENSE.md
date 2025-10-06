# Multi-Layer Defense System

**Version 2.1.0** - Deployed October 6, 2025

## 🎯 Problem Solved

**Before:** Foreign incidents (Ukrainian drone attacks, German incidents, etc.) were appearing at Nordic coordinates because:
1. News articles mentioned Nordic locations in context ("Danish officials comment in Copenhagen")
2. Location extraction picked up Nordic coords from these context mentions
3. Binary geographic filter only checked coordinates, not text content
4. Manual cleanup was reactive and error-prone

**After:** Multi-layer defense system with 4 independent validation layers + automated monitoring.

---

## 🛡️ The 4 Layers of Defense

### **Layer 1: Database Trigger** (CRITICAL)
**File**: `migrations/014_geographic_validation_trigger.sql`

PostgreSQL trigger that validates EVERY incident BEFORE insertion.

**What it does:**
- Validates coordinates are in Nordic region (54-71°N, 4-31°E)
- Checks title for foreign location keywords
- Rejects foreign incidents with clear error messages
- **Works even if scrapers use old code**

**Test:**
```sql
INSERT INTO incidents (title, location, ...)
VALUES ('Russisk droneangrep over Ukraina', ST_Point(12.65, 55.62)::geography, ...);
-- ERROR: Geographic validation failed: Foreign incident detected (keyword: "ukraina")
```

**Status:** ✅ Active and tested

---

### **Layer 2: Python Filter with Confidence Scoring**
**File**: `ingestion/geographic_analyzer.py`

Smart geographic analysis with context detection.

**What it does:**
- Checks text for foreign keywords BEFORE coordinates
- Detects Nordic responses to foreign events
- Confidence scoring (0.0-1.0) for borderline cases
- Returns detailed flags and reasoning

**Features:**
- 60+ foreign keywords with adjective forms ("russisk", "ukrainsk", "tysk")
- Nordic context detection ("Denmark responds to...")
- Whitelist of 50+ Nordic cities for confidence boost
- Backwards compatible with old `is_nordic_incident()` function

**Example:**
```python
from geographic_analyzer import analyze_incident_geography

analysis = analyze_incident_geography(
    title="Massivt russisk droneangrep over Ukraina",
    content="Danish officials comment from Copenhagen",
    lat=55.618, lon=12.6476
)

# Result: {'is_nordic': False, 'confidence': 1.0,
#          'reason': 'Foreign incident detected: ukraina, russisk',
#          'flags': ['foreign_incident', 'keyword:ukraina', 'keyword:russisk']}
```

**Status:** ✅ Integrated into ingest.py v2.1.0

---

### **Layer 3: Automated Cleanup Job**
**File**: `ingestion/cleanup_foreign_incidents.py`

Hourly background job that scans for and removes foreign incidents.

**What it does:**
- Scans database for suspicious foreign keywords
- Re-validates with enhanced analyzer
- Auto-removes foreign incidents
- Logs all removals with detailed reasoning
- Alerts if >5 incidents found (scraper broken)

**Run manually:**
```bash
export DATABASE_URL="postgresql://..."
python3 cleanup_foreign_incidents.py
```

**Cron setup** (runs hourly):
```bash
0 * * * * cd /path/to/ingestion && python3 cleanup_foreign_incidents.py
```

**Output:**
```
Found 1 suspicious incidents to analyze
🗑️  REMOVING FOREIGN INCIDENT:
   ID: e2c89791-a010-406c-a14b-a3dbc434547f
   Title: Massivt russisk droneangrep over hele Ukraina
   Reason: Foreign incident detected: ukraina, russisk
   Confidence: 1.0
================================================================================
CLEANUP COMPLETE
Scanned: 1 incidents
Removed: 1 foreign incidents
```

**Status:** ✅ Tested and working

---

### **Layer 4: Version Tracking & Monitoring**
**Files**:
- `ingestion/monitoring.py` - Real-time dashboard
- `migrations/015_version_tracking.sql` - Database schema

**What it does:**
- Tracks scraper version for each incident
- Records validation confidence scores
- Monitors ingestion rate and filter effectiveness
- Real-time dashboard showing system health

**Run dashboard:**
```bash
export DATABASE_URL="postgresql://..."
python3 monitoring.py
```

**Output:**
```
================================================================================
DRONEWATCH INGESTION PIPELINE MONITORING
================================================================================

Status: ✅ HEALTHY

Total Incidents: 17
Last Hour: 3
Last 24h: 17
Average Confidence: 0.95
Trigger Enabled: ✓

Scraper Versions:
  2.1.0: 5 incidents
  2.0.1: 12 incidents

Confidence Distribution:
  0.9-1.0 (High): 4 incidents
  0.7-0.9 (Medium-High): 1 incident
```

**Status:** ✅ Tested and working

---

## 📊 Database Schema Changes

### New Columns in `incidents` table:
```sql
-- Track which scraper version ingested the incident
scraper_version VARCHAR(20)

-- Geographic validation confidence score (0.00-1.00)
validation_confidence DECIMAL(3,2)

-- When incident was added to database
ingested_at TIMESTAMPTZ DEFAULT NOW()
```

### Indexes:
```sql
CREATE INDEX idx_incidents_scraper_version ON incidents(scraper_version);
CREATE INDEX idx_incidents_ingested_at ON incidents(ingested_at DESC);
```

---

## 🚀 Deployment Guide

### 1. Run Database Migrations
```bash
# Migration 014: Geographic validation trigger
psql "postgresql://..." -f migrations/014_geographic_validation_trigger.sql

# Migration 015: Version tracking columns
psql "postgresql://..." -f migrations/015_version_tracking.sql
```

### 2. Deploy Updated Scraper
```bash
# ingest.py now includes:
# - Version tracking (SCRAPER_VERSION = "2.1.0")
# - Enhanced geographic analyzer
# - Confidence scoring

# The updated code will:
# - Block foreign incidents at ingestion time
# - Add validation_confidence, scraper_version, ingested_at
```

### 3. Setup Cron Job (Optional but Recommended)
```bash
# Edit crontab
crontab -e

# Add hourly cleanup job
0 * * * * cd /path/to/ingestion && export DATABASE_URL="postgresql://..." && python3 cleanup_foreign_incidents.py >> cleanup.log 2>&1
```

### 4. Monitor System Health
```bash
# Run monitoring dashboard daily
python3 monitoring.py

# Check cleanup log
tail -f cleanup.log
```

---

## 🧪 Testing

### Test Layer 1 (Database Trigger):
```sql
INSERT INTO public.incidents (title, narrative, location, occurred_at, evidence_score, status)
VALUES (
    'Russisk droneangrep over Ukraina',
    'Ukrainian drone attack',
    ST_SetSRID(ST_MakePoint(12.6476, 55.618), 4326)::geography,
    NOW(),
    3,
    'active'
);
-- Expected: ERROR: Geographic validation failed: Foreign incident detected (keyword: "ukraina")
```

### Test Layer 2 (Python Filter):
```python
from geographic_analyzer import analyze_incident_geography

# Test foreign incident blocking
analysis = analyze_incident_geography(
    "Massivt russisk droneangrep over Ukraina",
    "Multiple drone attacks across Ukraine",
    55.618, 12.6476
)
print(analysis)
# Expected: {'is_nordic': False, 'confidence': 1.0, ...}
```

### Test Layer 3 (Cleanup Job):
```bash
export DATABASE_URL="postgresql://..."
python3 cleanup_foreign_incidents.py
# Expected: Scans database, removes foreign incidents, logs results
```

### Test Layer 4 (Monitoring):
```bash
export DATABASE_URL="postgresql://..."
python3 monitoring.py
# Expected: Dashboard with real-time metrics
```

---

## 📈 Success Metrics

**Before Multi-Layer Defense:**
- ❌ 6 foreign incidents in database
- ❌ Manual cleanup required every time
- ❌ No visibility into filter effectiveness
- ❌ Reactive problem-solving

**After Multi-Layer Defense:**
- ✅ 0 foreign incidents in database
- ✅ Automated cleanup every hour
- ✅ Real-time monitoring dashboard
- ✅ Version tracking for deployments
- ✅ Confidence scoring for validation
- ✅ 4 independent defense layers

---

## 🔧 Troubleshooting

### Foreign incidents still appearing?

1. **Check Layer 1 (Trigger):**
   ```sql
   SELECT tgname, tgenabled FROM pg_trigger
   WHERE tgrelid = 'public.incidents'::regclass;
   ```
   If disabled: Re-run `014_geographic_validation_trigger.sql`

2. **Check Layer 2 (Python Filter):**
   ```bash
   python3 -c "from geographic_analyzer import analyze_incident_geography; print(analyze_incident_geography('Ukraina', '', 55.6, 12.6))"
   ```
   Should return `{'is_nordic': False, ...}`

3. **Check Layer 3 (Cleanup):**
   ```bash
   python3 cleanup_foreign_incidents.py
   ```
   Should find and remove foreign incidents

4. **Check scraper version:**
   ```sql
   SELECT scraper_version, COUNT(*) FROM incidents
   GROUP BY scraper_version;
   ```
   Should show `2.1.0` for new incidents

### Low confidence scores?

Check monitoring dashboard:
```bash
python3 monitoring.py
```

If average confidence < 0.7:
- Review recent incidents
- Adjust confidence thresholds in `geographic_analyzer.py`
- Add more Nordic cities to whitelist

---

## 📝 Files Reference

### New Files:
- `migrations/014_geographic_validation_trigger.sql` - Database trigger
- `migrations/015_version_tracking.sql` - Schema changes
- `ingestion/geographic_analyzer.py` - Smart filter with confidence scoring
- `ingestion/cleanup_foreign_incidents.py` - Automated cleanup job
- `ingestion/monitoring.py` - Real-time monitoring dashboard
- `ingestion/MULTI_LAYER_DEFENSE.md` - This file

### Modified Files:
- `ingestion/ingest.py` - Version tracking, enhanced validation
- `ingestion/utils.py` - Backwards compatible wrapper (existing code works)
- `CLAUDE.md` - Updated with new system documentation

---

## 🎓 Key Learnings

1. **Defense in Depth**: Single layer is not enough - need multiple independent layers
2. **Automation > Manual**: Automated cleanup is essential for scale
3. **Monitoring is Critical**: Can't fix what you can't measure
4. **Version Tracking**: Must know which code version is running
5. **Confidence Scoring**: Binary True/False isn't smart enough for edge cases

---

**Questions or issues?** Check logs in `cleanup.log` or run monitoring dashboard.

**Version:** 2.1.0
**Last Updated:** October 6, 2025
**Status:** ✅ Production Ready
