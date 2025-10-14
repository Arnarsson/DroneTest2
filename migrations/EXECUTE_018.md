# Execute Migration 018: Create Sources Tables

## Problem
Sources aren't showing on the frontend because the `sources` and `incident_sources` tables don't exist in the production database.

## Solution
Execute migration 018 to create these tables.

## Instructions

### Step 1: Verify migration hasn't been executed
```bash
psql "postgresql://...@...pooler.supabase.com:5432/postgres" \
  -c "SELECT * FROM public.check_migration_executed('018');"
```

Expected output: Should show migration 018 NOT executed

### Step 2: Execute migration
```bash
psql "postgresql://...@...pooler.supabase.com:5432/postgres" \
  -f migrations/018_create_sources_tables.sql
```

**IMPORTANT**: Use port 5432 (direct connection) NOT 6543 (transaction pooler) for migrations!

### Step 3: Verify execution
```bash
psql "postgresql://...@...pooler.supabase.com:5432/postgres" \
  -c "SELECT version, description, executed_at FROM public.schema_migrations WHERE version = '018';"
```

Expected output: Should show migration 018 with execution timestamp

### Step 4: Verify tables exist
```bash
psql "postgresql://...@...pooler.supabase.com:5432/postgres" \
  -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('sources', 'incident_sources');"
```

Expected output:
```
     table_name
---------------------
 sources
 incident_sources
```

### Step 5: Test API
```bash
curl -s "https://www.dronemap.cc/api/incidents?limit=1" | jq '.[0].sources'
```

**Before migration**: Empty array `[]`
**After migration**: Still empty array `[]` (no sources ingested yet)

### Step 6: Re-run ingestion to populate sources
```bash
cd ingestion
python3 ingest.py
```

This will re-ingest recent incidents and populate the sources tables.

### Step 7: Verify sources showing
```bash
curl -s "https://www.dronemap.cc/api/incidents?limit=1" | jq '.[0].sources'
```

Expected output: Array with source objects like:
```json
[
  {
    "source_url": "https://politi.dk/...",
    "source_type": "police",
    "source_name": "Politiets Nyhedsliste",
    "source_title": "...",
    "source_quote": "...",
    "trust_weight": 4
  }
]
```

## What This Migration Does

1. **Creates `sources` table**: Stores information about news sources (police, media, aviation authorities)
2. **Creates `incident_sources` table**: Many-to-many relationship between incidents and sources
3. **Creates evidence scoring trigger**: Automatically recalculates evidence_score when sources change
4. **Adds indexes**: For performance on common queries

## Evidence Score Logic

After this migration, evidence scores will be calculated automatically:

- **Score 4 (OFFICIAL)**: ANY official source (police/military/NOTAM/aviation, trust_weight=4)
- **Score 3 (VERIFIED)**: 2+ media sources (trust_weight≥2) WITH official quote detection
- **Score 2 (REPORTED)**: Single credible source (trust_weight ≥ 2)
- **Score 1 (UNCONFIRMED)**: Low trust sources (trust_weight < 2)

## Rollback (if needed)

If something goes wrong, you can rollback:

```sql
DROP TRIGGER IF EXISTS trigger_update_evidence_score ON public.incident_sources;
DROP FUNCTION IF EXISTS update_evidence_score();
DROP TABLE IF EXISTS public.incident_sources CASCADE;
DROP TABLE IF EXISTS public.sources CASCADE;
DELETE FROM public.schema_migrations WHERE version = '018';
```

## Next Steps

After executing this migration:
1. Re-run ingestion pipeline to populate sources
2. Verify sources showing on frontend (www.dronemap.cc)
3. Check evidence scores are being calculated correctly
