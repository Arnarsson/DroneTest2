# Fix Missing Sources - Belgium Incident

**Date**: October 14, 2025
**Issue**: Belgium drone plot incident (ID: `80094858-1eb6-46bd-917c-302268edf8bf`) has no sources

---

## Root Cause

The Belgium incident was ingested on **October 9, 2025** BEFORE **migration 011** (`source_verification.sql`) was executed.

Migration 011 creates:
- `public.sources` table
- `public.incident_sources` junction table
- Automatic evidence score recalculation triggers

**Status**: Migration 011 has **NOT been executed** on production database yet.

---

## Solution Options

### Option 1: Execute Migration 011 (RECOMMENDED)

This is the proper long-term fix that will:
- Create the multi-source schema
- Enable automatic evidence score upgrades
- Support source consolidation

**File**: `migrations/011_source_verification.sql`

**Execute**:
```bash
psql "postgresql://[USER]:[PASSWORD]@[HOST]:5432/postgres" \
  -f migrations/011_source_verification.sql
```

**After Migration**: Re-ingest the Belgium incident to populate sources automatically.

---

### Option 2: Manual SQL Fix (TEMPORARY)

If you can't run migration 011 right now, use this temporary fix:

**File**: `/tmp/fix_belgium_incident_source.sql`

**Execute**:
```bash
psql "postgresql://[USER]:[PASSWORD]@[HOST]:5432/postgres" \
  -f /tmp/fix_belgium_incident_source.sql
```

This will:
1. Add France24 Europe as a source
2. Link it to the Belgium incident
3. Verify the fix worked

---

## Verification

After applying either fix, verify sources appear:

```bash
curl -s "https://www.dronemap.cc/api/incidents" | \
  jq '.[] | select(.id == "80094858-1eb6-46bd-917c-302268edf8bf") | {title, sources}'
```

**Expected**:
```json
{
  "title": "Belgium says it foiled suspected drone plot to attack prime minister",
  "sources": [
    {
      "name": "France24 Europe News",
      "url": "https://www.france24.com/en/europe/...",
      "type": "verified_media"
    }
  ]
}
```

---

## Long-Term Prevention

**Migration 011 MUST be executed** to prevent this issue for future incidents.

Once executed:
- All new incidents will automatically have sources tracked
- Evidence scores will upgrade when multiple sources are consolidated
- Source verification will work as designed

---

## Current Status

**Incidents with sources**: 8/9 (88.9%)
**Incidents without sources**: 1/9 (11.1%)

**Missing sources**:
- Belgium drone plot (Oct 9, 2025)

**Cause**: Migration 011 not yet executed

**Fix**: Execute migration 011 OR apply temporary SQL fix

---

**Priority**: MEDIUM (only affects 1 incident, but migration 011 is critical for multi-source system)
