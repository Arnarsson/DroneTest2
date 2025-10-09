# Verification System Deployment Guide

**Phase 1: Historical Incidents & Source Verification**

---

## Quick Start (5 Minutes)

```bash
# 1. Set your database URL
export DATABASE_URL='your-postgresql-connection-string-here'

# 2. Run deployment script
./deploy-verification.sh

# 3. Push to production
git add .
git commit -m "feat: deploy verification system"
git push

# Done! ✅
```

---

## What This Deploys

### Database Changes
- ✅ Verification workflow tables and functions
- ✅ Review queue for manual approval
- ✅ Audit trail for all verification actions
- ✅ Confidence scoring fields

### Application Changes
- ✅ Auto-verification logic (Police sources → instant publish)
- ✅ API filtering (only verified incidents shown to public)
- ✅ Enhanced logging with verification status

### Result
- **High-quality sources** (police, official) → Publish immediately
- **Low-quality sources** → Hidden until manually verified
- **No more false positives** on the website

---

## Step-by-Step Instructions

### Step 1: Run Database Migration

**Option A: Using the script (easiest)**
```bash
export DATABASE_URL='your-connection-string'
./deploy-verification.sh
```

**Option B: Manual SQL**
```bash
psql "$DATABASE_URL" -f migrations/003_verification_workflow.sql
```

**Option C: Supabase Dashboard**
1. Go to https://supabase.com/dashboard
2. Select your project
3. Click "SQL Editor"
4. Copy contents of `migrations/003_verification_workflow.sql`
5. Paste and click "Run"

### Step 2: Verify Migration Worked

```sql
-- Check tables exist
SELECT COUNT(*) FROM public.incident_review_queue;
SELECT COUNT(*) FROM public.verification_audit;

-- Check view exists
SELECT * FROM public.v_verification_stats;
```

Should return results with no errors.

### Step 3: Deploy to Production

```bash
# Commit changes
git add .
git commit -m "feat: deploy verification infrastructure"

# Push (triggers Vercel deployment automatically)
git push origin terragon/scraper-improvements
```

### Step 4: Set GitHub Secret (if not already done)

Add `DATABASE_URL` to GitHub Actions secrets:
1. Go to: https://github.com/Arnarsson/2/settings/secrets/actions
2. Click "New repository secret"
3. Name: `DATABASE_URL`
4. Value: Your PostgreSQL connection string
5. Save

### Step 5: Test It Works

**Wait for next scraper run** (happens every 15 minutes automatically)

**Check the logs:**
```bash
gh run list --workflow=ingest.yml --limit 1
gh run view <run-id> --log
```

**Look for:**
```
✓ Auto-verified: Drones over Copenhagen Airport (confidence: 0.95)
⚠️ Pending review: Suspicious incident - Low trust source (priority: 2)
```

---

## How to Use the Verification System

### View Incidents Needing Review

**SQL:**
```sql
SELECT * FROM public.v_review_queue
ORDER BY priority ASC, queued_at ASC
LIMIT 20;
```

### Verify (Approve) an Incident

**SQL:**
```sql
SELECT public.complete_review(
  'incident-uuid-here',
  'verify',
  'your-name@email.com',
  'Confirmed with official police source'
);
```

### Reject an Incident

**SQL:**
```sql
SELECT public.complete_review(
  'incident-uuid-here',
  'reject',
  'your-name@email.com',
  'Commercial drone delivery, not a security incident'
);
```

### Check Verification Stats

**SQL:**
```sql
SELECT * FROM public.v_verification_stats;
```

Returns:
- How many pending/verified/rejected
- Average confidence score
- Average evidence score

### View Audit Trail

**SQL:**
```sql
SELECT
  created_at,
  action,
  performed_by,
  notes
FROM public.verification_audit
WHERE incident_id = 'incident-uuid-here'
ORDER BY created_at DESC;
```

---

## Verification Rules (Auto vs Manual)

### Auto-Verified ✅ (Publishes Immediately)

**Level 4 Sources:**
- Danish Police (all districts)
- NOTAM
- Aviation Authority
- Defense/Military

**Level 3 with Official Quotes:**
- DR Nyheder (if quotes police/officials)
- TV2 News (if quotes police/officials)
- Berlingske (if quotes police/officials)
- Reuters, AFP (if quotes officials)

### Manual Review ⚠️ (Hidden Until Approved)

**Level 3 without Official Quotes:**
- Major media without official confirmation

**Level 2 Sources:**
- Regional news (TV2 Lorry, TV2 Nord, etc.)
- Local newspapers

**Level 1 Sources:**
- Social media
- Unverified reports
- Unknown sources

---

## Troubleshooting

### Migration fails with "relation already exists"

**Solution:** Tables already exist. Either:
1. Drop and recreate: `DROP TABLE IF EXISTS incident_review_queue CASCADE;`
2. Or skip migration (already deployed)

### API still shows unverified incidents

**Check:**
1. Did migration run? `SELECT COUNT(*) FROM public.incident_review_queue;`
2. Is API code updated? Check `frontend/api/db.py` line 80
3. Did Vercel redeploy? Check https://vercel.com/deployments

**Fix:** Trigger redeploy by pushing a commit.

### Scraper not logging verification decisions

**Check:**
1. Is `DATABASE_URL` set in GitHub secrets?
2. Is `ingestion/verification.py` present?
3. Check scraper logs: `gh run view <run-id> --log`

**Fix:** Re-run deployment script to ensure all files committed.

### All incidents going to review queue (none auto-verified)

**Check source configuration:**
```python
# ingestion/config.py
"copenhagen_police": {
    "trust_weight": 4,  # Should be 4 for police
    "type": "police",   # Should be "police"
}
```

---

## Rollback Instructions

If something goes wrong, you can rollback:

### Rollback Database

```sql
-- Remove verification tables
DROP TABLE IF EXISTS public.incident_review_queue CASCADE;
DROP TABLE IF EXISTS public.verification_audit CASCADE;
DROP VIEW IF EXISTS public.v_review_queue CASCADE;
DROP VIEW IF EXISTS public.v_verification_stats CASCADE;

-- Remove verification columns from incidents
ALTER TABLE public.incidents
  DROP COLUMN IF EXISTS confidence_score,
  DROP COLUMN IF EXISTS requires_review,
  DROP COLUMN IF EXISTS review_notes,
  DROP COLUMN IF EXISTS last_reviewed_at,
  DROP COLUMN IF EXISTS review_count;
```

### Rollback API

```bash
# Restore backup
cp frontend/api/db.py.backup frontend/api/db.py

# Or manually remove the verification filter
# Edit frontend/api/db.py line 80, remove:
# AND (i.verification_status IN ('verified', 'auto_verified')
#      OR i.verification_status IS NULL)
```

### Rollback Ingester

```bash
git revert <commit-hash>
git push
```

---

## Next Phase: Admin Interface

After Phase 1 is deployed and working, you can build an admin dashboard:

**Features:**
- Web UI to view review queue
- One-click approve/reject buttons
- Edit incident details
- View audit history
- Batch operations

**ETA:** Week 3-4 of implementation plan

---

## Support

**Documentation:** `HISTORICAL_INCIDENTS_PLAN.md`
**Issues:** https://github.com/Arnarsson/2/issues

---

**Deployment Version:** Phase 1
**Last Updated:** 2025-09-30