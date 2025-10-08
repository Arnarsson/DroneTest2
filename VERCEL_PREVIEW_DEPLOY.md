# Vercel Preview Deployment Guide

## Quick Deploy (Recommended)

Deploy the `feature/senior-ux-redesign` branch to Vercel preview for browser testing.

### Option 1: Deploy via Vercel Dashboard

1. **Login to Vercel**:
   ```bash
   vercel login
   ```

2. **Deploy from feature branch**:
   ```bash
   cd /Users/sven/Desktop/MCP/DroneTest2/frontend
   vercel --prod=false
   ```

3. **Vercel will**:
   - Detect Next.js 14.2.33
   - Install dependencies
   - Build production bundle
   - Deploy Python API functions
   - Return preview URL

4. **Expected output**:
   ```
   🔍  Inspect: https://vercel.com/arnarssons-projects/dronetest/...
   ✅  Preview: https://dronetest-git-feature-senior-ux-redesign-arnarssons-projects.vercel.app
   ```

### Option 2: Deploy via Git Push (Auto-Deploy)

1. **Push feature branch to GitHub**:
   ```bash
   cd /Users/sven/Desktop/MCP/DroneTest2
   git push origin feature/senior-ux-redesign
   ```

2. **Vercel auto-deploys preview**:
   - GitHub webhook triggers Vercel
   - Preview URL created automatically
   - Check Vercel dashboard for URL

---

## Browser Testing Checklist

### 1. Evidence Legend Testing
**URL**: `https://[preview-url].vercel.app`

- [ ] Legend displays in bottom-left corner
- [ ] Shows correct counts: `OFFICIAL (0)`, `VERIFIED (0)`, `REPORTED (6)`, `UNCONFIRMED (0)`
- [ ] Auto-opens on first visit (desktop only)
- [ ] "Learn more" link works
- [ ] Collapsible expand/collapse animation smooth
- [ ] Counts update when filters applied

**Expected Behavior**:
- 6 incidents total (all Score 2 = REPORTED)
- Legend updates in real-time as filters change

### 2. Popup Testing
**Test each of 6 production incidents**:

#### Aalborg Airport Incidents (4 incidents - should consolidate)
**Locations**:
- 57.0928°N, 9.8492°E (Aalborg Airport)

**Test Cases**:
1. Click marker → popup opens
2. **Source display**:
   - [ ] Quote shown FIRST (blockquoted if exists)
   - [ ] Source name SECOND (e.g., "Nordjyske")
   - [ ] "View Source" button THIRD (external link)
   - [ ] Trust weight badge correct (e.g., `VERIFIED MEDIA 75%`)
3. **Date display**:
   - [ ] Shows relative time (e.g., "3 days ago")
   - [ ] Shows absolute date after `·` (e.g., "05 Oct 2024 14:30")
4. **Action buttons**:
   - [ ] "Copy Embed Code" button works
   - [ ] "Report Issue" button works
   - [ ] Both have icons
5. **Evidence badge**:
   - [ ] Shows correct color (Orange = REPORTED)
   - [ ] Shows correct emoji (🟠)
   - [ ] Tooltip displays on hover

#### Copenhagen Airport Incidents (2 incidents - should consolidate)
**Location**: 55.618°N, 12.6476°E (Copenhagen Airport)

**Test Cases**: Same as Aalborg

### 3. Cluster Modal Testing
**If 2+ incidents cluster at same facility**:

- [ ] Click cluster → modal opens
- [ ] Modal title shows facility + count (e.g., "✈️ Aalborg Airport (4 incidents)")
- [ ] Each incident card clickable
- [ ] Chevron indicator (→) visible
- [ ] Click card → navigates to incident detail
- [ ] Close button (X) works
- [ ] Outside click closes modal

### 4. Filter Testing
**Apply filters and verify legend counts update**:

1. **Evidence Score Filter**:
   - [ ] Set min evidence = 3 → Legend shows 0 incidents
   - [ ] Set min evidence = 2 → Legend shows 6 incidents
   - [ ] Set min evidence = 1 → Legend shows 6 incidents

2. **Country Filter**:
   - [ ] Select Denmark → Legend shows ~4 incidents
   - [ ] Select All → Legend shows 6 incidents

3. **Asset Type Filter**:
   - [ ] Select Airport → Legend shows ~6 incidents
   - [ ] Select All → Legend shows 6 incidents

---

## Consolidation Testing (After GitHub Actions Deployed)

Once hourly ingestion is running, test consolidation with new incidents:

### Scenario 1: Same Location + Time → MERGE
**Setup**: Wait for scraper to find duplicate incidents
**Expected**:
- 2 news sources report same incident
- Consolidation merges them
- Popup shows 2 sources
- Evidence score upgrades if applicable

### Scenario 2: Different Locations → SEPARATE
**Setup**: Incidents at different airports
**Expected**:
- 2 separate markers on map
- Each has own popup
- Legend counts update correctly

### Scenario 3: Evidence Score Upgrade
**Setup**: Media source + Police source for same incident
**Expected**:
- Evidence score upgrades from 2 (REPORTED) → 4 (OFFICIAL)
- Legend counts shift: REPORTED -1, OFFICIAL +1
- Badge color changes Orange → Green

---

## Performance Testing

### Load Time Targets
- [ ] **Initial page load**: < 3s on 3G
- [ ] **API response**: < 500ms
- [ ] **Map render**: < 1s
- [ ] **Filter update**: < 200ms

### Bundle Size Check
```bash
cd frontend
npm run build

# Check output:
# ✓ Route (app)                              ~147 kB
# ✓ /_not-found                              867 B
# + First Load JS shared by all              167 kB
```

**Targets**:
- Initial bundle: < 200 KB ✅ (currently 167 KB)
- Route bundle: < 150 KB ✅ (currently 147 KB)

---

## Known Issues to Watch For

### Issue 1: date-fns Import Error
**Symptom**: Build fails with "barrel loader" error
**Cause**: Incorrect date-fns imports
**Fix**: All imports use specific paths (e.g., `'date-fns/format'`)
**Status**: ✅ FIXED in this branch

### Issue 2: PostGIS Query Timeout
**Symptom**: API returns empty array or timeout error
**Cause**: Supabase pooler connection issue
**Fix**: Already using port 6543 (transaction pooler)
**Status**: ✅ WORKING (verified in production)

### Issue 3: Legend Counts Mismatch
**Symptom**: Legend shows 0 for all levels
**Cause**: `incidents` prop not passed
**Fix**: Added `incidents={incidents || []}` in page.tsx
**Status**: ✅ FIXED in this branch

---

## Rollback Plan

If preview testing reveals critical issues:

### Option 1: Quick Fix
```bash
# Make fix in feature branch
git add .
git commit -m "fix: [issue description]"
git push origin feature/senior-ux-redesign

# Vercel auto-redeploys preview
```

### Option 2: Rollback to Main
```bash
# Don't merge feature branch yet
# Production stays on main branch (working)
# Continue fixing in feature branch
```

---

## Deployment Checklist

Before merging to main:

- [ ] All 6 production incidents tested
- [ ] Legend counts correct
- [ ] Popup enhancements working
- [ ] Cluster modal functional
- [ ] Filters update legend
- [ ] No console errors
- [ ] Load time < 3s
- [ ] Bundle size < 200 KB
- [ ] Mobile responsive (test on phone)
- [ ] Dark mode working

---

## Post-Deployment Monitoring

After merging to main:

1. **Check Production URL**: https://www.dronemap.cc
2. **Monitor Vercel Logs**: Look for errors
3. **Check Database**: Verify consolidation working
4. **Test All Features**: Run checklist again
5. **Monitor Performance**: Check Core Web Vitals

---

## Next Steps After Testing

1. **If all tests pass**:
   ```bash
   cd /Users/sven/Desktop/MCP/DroneTest2
   git checkout main
   git merge feature/senior-ux-redesign
   git push origin main
   ```

2. **If issues found**:
   - Document issues
   - Create fix commits
   - Re-test preview
   - Merge when stable

3. **Phase 2: GitHub Actions**:
   - Implement hourly ingestion workflow
   - Test consolidation with real scraped data
   - Monitor for merge rate and evidence upgrades

---

**Version**: 2.3.0
**Branch**: feature/senior-ux-redesign
**Last Updated**: October 7, 2025
