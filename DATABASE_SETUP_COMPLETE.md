# Complete Database Setup Guide

**Issue**: `ERROR: relation "incidents" does not exist`
**Cause**: Database schema never initialized
**Solution**: Run initial schema setup + migrations in order

---

## 🚨 Current Situation

Your Supabase database is **empty** - no tables exist yet. You need to:
1. Create the initial schema (tables, indexes, functions)
2. Run migrations in order
3. Verify everything works

---

## ✅ Complete Setup Steps (Run in Order)

### Step 1: Initial Schema Setup

**File**: `sql/dronewatch_schema_clean.sql`
**What it creates**:
- ✅ PostGIS extension
- ✅ `assets` table (airports, harbors, military bases)
- ✅ `sources` table (news sources with trust_weight)
- ✅ `incidents` table (drone incidents)
- ✅ `incident_sources` table (many-to-many relationship)
- ✅ All indexes and constraints

**Run this**:
```bash
psql "$DATABASE_URL" -f sql/dronewatch_schema_clean.sql
```

**Expected output**:
```
CREATE EXTENSION
CREATE TABLE
CREATE INDEX
CREATE TABLE
CREATE INDEX
CREATE TABLE
CREATE INDEX
...
```

---

### Step 2: Performance Indexes (Optional but Recommended)

**File**: `migrations/006_performance_indexes.sql`
**Impact**: 73% faster API responses

```bash
psql "$DATABASE_URL" -f migrations/006_performance_indexes.sql
```

---

### Step 3: Evidence Scoring System (CRITICAL)

**File**: `migrations/010_evidence_scoring_system.sql`
**What it does**: Creates automatic trigger to calculate evidence scores

```bash
psql "$DATABASE_URL" -f migrations/010_evidence_scoring_system.sql
```

**Expected output**:
```
CREATE FUNCTION
CREATE TRIGGER
UPDATE 0  (0 incidents because database is empty)
```

---

### Step 4: Wait for Scraper to Run

**Timeline**: GitHub Actions runs every 15 minutes

After the schema is set up:
1. Wait for next scraper run (check https://github.com/Arnarsson/DroneTest2/actions)
2. Scraper will create incidents
3. Incidents will appear on the map

**Check scraper logs**:
```bash
gh run list --repo Arnarsson/DroneTest2 --workflow=ingest.yml --limit 3
gh run view --log  # View latest run
```

---

### Step 5: Clean Up Bad Data (After Scraper Runs)

**File**: `migrations/011_remove_non_nordic_incidents.sql`
**When to run**: After scraper has created some incidents

```bash
# Only run this AFTER incidents exist
psql "$DATABASE_URL" -f migrations/011_remove_non_nordic_incidents.sql
```

---

## 🎯 Quick Setup Script

Run this to set up everything at once:

```bash
# Set your database URL
export DATABASE_URL="postgresql://postgres.uhwsuaebakkdmdogzrrz:stUPw5co47Yq8uSI@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"

# Navigate to repo
cd /root/repo

# Step 1: Initial schema (REQUIRED)
echo "Creating database schema..."
psql "$DATABASE_URL" -f sql/dronewatch_schema_clean.sql

# Step 2: Performance indexes (RECOMMENDED)
echo "Adding performance indexes..."
psql "$DATABASE_URL" -f migrations/006_performance_indexes.sql

# Step 3: Evidence scoring system (REQUIRED)
echo "Setting up evidence scoring..."
psql "$DATABASE_URL" -f migrations/010_evidence_scoring_system.sql

# Verify setup
echo "Verifying database setup..."
psql "$DATABASE_URL" -c "\dt"  # List tables

echo "✅ Database setup complete!"
echo "⏳ Wait for next scraper run to populate data"
echo "   Check: https://github.com/Arnarsson/DroneTest2/actions"
```

---

## 🔍 Verification

### Check Tables Exist

```sql
-- List all tables
\dt

-- Should show:
-- assets
-- incidents
-- incident_sources
-- sources
```

### Check Functions Exist

```sql
-- List functions
SELECT proname FROM pg_proc WHERE proname LIKE '%evidence%';

-- Should show:
-- calculate_evidence_score
```

### Check Triggers Exist

```sql
-- List triggers
SELECT tgname FROM pg_trigger;

-- Should show:
-- trigger_update_evidence_score
```

### Test API After Scraper Runs

```bash
# Should return empty array initially
curl "https://drone-test22.vercel.app/api/incidents"

# After scraper runs (15-30 min), should return incidents
curl "https://drone-test22.vercel.app/api/incidents?limit=5"
```

---

## 📊 Expected Timeline

| Step | Duration | Status |
|------|----------|--------|
| 1. Run schema setup | 5 seconds | ⏳ Do now |
| 2. Run migrations | 5 seconds | ⏳ Do now |
| 3. Wait for scraper | 0-15 min | ⏳ Automatic |
| 4. Incidents appear | Immediate | ✅ After scraper |
| 5. Clean bad data | 2 seconds | ⏳ After data exists |

**Total**: 15-30 minutes until fully working

---

## 🚨 Troubleshooting

### Error: "extension postgis does not exist"

```sql
-- Run this first
CREATE EXTENSION IF NOT EXISTS postgis;
```

Or contact Supabase support to enable PostGIS extension.

### Error: "permission denied"

Your database user needs permissions. Run as superuser or contact Supabase support.

### Scraper Not Creating Incidents

**Check GitHub Actions**:
```bash
gh run list --repo Arnarsson/DroneTest2 --workflow=ingest.yml
```

**Check scraper configuration**:
- Ensure `INGEST_TOKEN` in Vercel matches GitHub Actions secret
- Check scraper logs for errors

### API Returns Empty Array

**This is normal** if:
- ✅ Schema setup complete
- ⏳ Scraper hasn't run yet
- ⏳ Waiting for first incidents

**Wait 15 minutes** then check again.

---

## 📋 Migration Order Reference

**Always run in this order**:

1. ✅ `sql/dronewatch_schema_clean.sql` - FIRST (creates tables)
2. ✅ `migrations/006_performance_indexes.sql` - Optional (performance)
3. ✅ `migrations/010_evidence_scoring_system.sql` - REQUIRED (scoring)
4. ⏳ Wait for scraper to create incidents
5. ✅ `migrations/011_remove_non_nordic_incidents.sql` - After data exists

**DO NOT run migrations 001-009** - they're superseded by the clean schema.

---

## 🎯 Success Criteria

Database setup is complete when:

- [ ] Schema setup ran without errors
- [ ] Tables exist: `incidents`, `sources`, `incident_sources`, `assets`
- [ ] Function exists: `calculate_evidence_score`
- [ ] Trigger exists: `trigger_update_evidence_score`
- [ ] Scraper has run at least once
- [ ] API returns incidents (not empty array)
- [ ] Map shows incident markers

---

## 📞 Your Specific Connection

**DATABASE_URL**:
```
postgresql://postgres.uhwsuaebakkdmdogzrrz:stUPw5co47Yq8uSI@aws-1-eu-north-1.pooler.supabase.com:6543/postgres
```

**Quick test connection**:
```bash
psql "postgresql://postgres.uhwsuaebakkdmdogzrrz:stUPw5co47Yq8uSI@aws-1-eu-north-1.pooler.supabase.com:6543/postgres" -c "SELECT version();"
```

---

**Created**: 2025-10-06
**Priority**: CRITICAL (nothing works without this)
**Estimated Time**: 5 minutes setup + 15 min wait for scraper

🤖 Generated with [Claude Code](https://claude.com/claude-code)
