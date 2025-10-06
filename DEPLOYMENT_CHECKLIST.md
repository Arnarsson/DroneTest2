# Phase 1 Deployment Checklist

**Date**: 2025-10-05
**Status**: Code deployed to main, database migration pending
**Next**: Apply database migration

---

## ✅ Completed Steps

### 1. Code Changes - DONE ✅
- **Commit**: `eb7d533` - feat(evidence-scoring): implement automatic 4-tier evidence scoring system
- **Merged**: PR #1 merged to main (`c7e0c9f`)
- **Files Changed**: 12 files, +1980 lines
- **Tests**: 18/18 tests passed
- **Branch**: `origin/main` is up to date

**Verification**:
```bash
git log origin/main --oneline -3
# c7e0c9f Merge pull request #1
# eb7d533 feat(evidence-scoring): implement automatic 4-tier evidence scoring system
# 4fc3bca feat(ingestion): add URL validation and verified config
```

### 2. Vercel Deployment - AUTO-DEPLOYED ✅
- **Status**: Vercel auto-deploys from main branch
- **Expected**: Frontend changes already live
- **Site**: https://www.dronemap.cc
- **API**: https://www.dronemap.cc/api/incidents

**Verification**:
```bash
curl -s "https://www.dronemap.cc/api/incidents?limit=1" | jq '.incidents[0] | {title, evidence_score}'
```

---

## ⏳ Pending Steps (MANUAL ACTION REQUIRED)

### 3. Apply Database Migration - CRITICAL ⚠️

The database migration **MUST be applied manually** via Supabase SQL Editor.

**Why**: The code expects the database trigger and function to exist. Without migration:
- Evidence scores won't auto-update when sources are added
- New incidents will use hardcoded scores (less accurate)
- Source-driven scoring won't work

**How to Apply**:

#### Option A: Supabase Dashboard (Recommended)
1. Go to https://supabase.com
2. Open your DroneWatch project
3. Navigate to **SQL Editor**
4. Click **New Query**
5. Copy the entire contents of `migrations/010_evidence_scoring_system.sql`
6. Paste into SQL Editor
7. Click **Run**

#### Option B: Command Line (Requires DATABASE_URL)
```bash
# Get DATABASE_URL from Vercel
# Dashboard → Project → Settings → Environment Variables

# Apply migration
psql $DATABASE_URL -f migrations/010_evidence_scoring_system.sql

# Verify
psql $DATABASE_URL -c "SELECT COUNT(*) FROM incidents WHERE evidence_score >= 1;"
```

**Expected Output**:
```
CREATE FUNCTION
CREATE TRIGGER
UPDATE 27  -- Number of incidents updated
```

**Verification Query**:
```sql
-- Check evidence score distribution
SELECT
  evidence_score,
  COUNT(*) as count,
  ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 1) as percentage
FROM incidents
GROUP BY evidence_score
ORDER BY evidence_score DESC;
```

**Expected Result**:
```
evidence_score | count | percentage
---------------+-------+-----------
             4 |     0 |       0.0   -- No police sources (RSS feeds broken)
             3 |     8 |      29.6   -- Multi-source or quoted
             2 |    17 |      63.0   -- Single credible source
             1 |     2 |       7.4   -- Low trust
```

---

### 4. Update Scraper Config - RECOMMENDED

**Current**: `ingestion/config.py` contains 54 sources (34 broken, 20 working)
**Available**: `ingestion/config_verified.py` contains only 20 verified working sources

**Why Update**:
- Eliminates 404 errors and failed scrapes
- Improves scraper reliability
- Reduces noise in logs

**How to Apply**:
```bash
cd /root/repo/ingestion

# Backup current config
cp config.py config.py.backup

# Use verified config
cp config_verified.py config.py

# Commit change
git add config.py
git commit -m "chore: switch to verified sources only (20 working sources)

- Removed 34 broken URLs (404 errors, malformed RSS)
- All remaining sources validated 2025-10-05
- See source_validation_report.json for details"
git push origin main
```

**Impact**:
- Next scraper run (every 15 minutes) will use only working sources
- GitHub Actions will pick up the change automatically
- No deployment needed

---

### 5. Monitor Production - ONGOING

After migration is applied, monitor for:

#### A. Evidence Score Distribution
```bash
curl -s "https://www.dronemap.cc/api/incidents?country=all" \
  | jq '[.incidents[].evidence_score] | group_by(.) | map({score: .[0], count: length})'
```

**Expected**: Scores 1-4 based on source trust_weight

#### B. Source Attribution
```bash
curl -s "https://www.dronemap.cc/api/incidents?limit=5" \
  | jq '.incidents[] | {title: .title[:50], sources: .sources | length}'
```

**Expected**: Most incidents should have 1+ sources

#### C. Scraper Logs (GitHub Actions)
```bash
gh run list --repo Arnarsson/2 --workflow=ingest.yml --limit 5
```

**Expected**: No 404 errors after config update

---

## 🎯 Success Criteria

Migration is successful when:
- [ ] `calculate_evidence_score()` function exists in database
- [ ] `trigger_update_evidence_score` trigger is active
- [ ] All existing incidents have recalculated evidence_score
- [ ] New incidents auto-update scores when sources added
- [ ] Evidence score distribution matches source trust weights

Config update is successful when:
- [ ] Scraper runs without 404 errors
- [ ] All incidents have non-empty sources arrays
- [ ] GitHub Actions logs show "20 sources configured"

---

## 🚨 Rollback Plan (If Issues)

### Rollback Code Changes
```bash
# Revert to previous main
git revert c7e0c9f  # Reverts the merge commit
git push origin main
```

### Rollback Database Migration
```sql
-- Remove trigger
DROP TRIGGER IF EXISTS trigger_update_evidence_score ON incident_sources;

-- Remove function
DROP FUNCTION IF EXISTS calculate_evidence_score(uuid);

-- Optional: Reset evidence scores to original values
-- (Only if you have a backup)
```

### Rollback Config Changes
```bash
cp config.py.backup config.py
git add config.py
git commit -m "revert: restore original config"
git push origin main
```

---

## 📞 Support

**Issues**: https://github.com/Arnarsson/2/issues
**Docs**:
- `PHASE_1_DEPLOYMENT.md` - Full deployment guide
- `INVESTIGATION_FINDINGS.md` - Context and rationale
- `CLAUDE.md` - Project overview

**Testing**:
```bash
cd /root/repo/ingestion
python3 test_evidence_scoring.py
# Should output: ✅ ALL TESTS PASSED
```

---

## 📋 Next Steps After Deployment

1. **Monitor for 24 hours**
   - Check evidence score distribution
   - Verify source attribution working
   - Watch for scraper errors

2. **Phase 2: Social Media Monitoring**
   - Implement Nitter (Twitter) RSS scraping
   - Pattern-based incident detection
   - Admin review dashboard

3. **Phase 3: HTML Scraping**
   - Danish police website scraping (no RSS available)
   - Norwegian/Swedish police parsing
   - Restore Tier 4 official sources

---

**Last Updated**: 2025-10-05
**Status**: ⏳ Awaiting database migration
**Deployed Commit**: `c7e0c9f` (main)
