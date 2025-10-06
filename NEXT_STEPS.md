# DroneWatch - Next Steps After Phase 1

**Date**: 2025-10-05
**Current Status**: Phase 1 Complete ✅
**Latest PR**: #2 (pending merge)

---

## 🎯 What We Just Accomplished

### Phase 0: URL Validation ✅
- Validated all 40 sources in config
- Found 22 broken URLs (all police RSS feeds + malformed news feeds)
- Created verified config with 18 working sources
- 100% scraper reliability achieved

### Phase 1: Evidence Scoring System ✅
- Implemented 4-tier evidence scoring (OFFICIAL, VERIFIED, REPORTED, UNCONFIRMED)
- Database migration with automatic trigger for score recalculation
- Scraper updates to use source `trust_weight` dynamically
- 18/18 unit tests passed
- Zero tolerance for hallucinations

---

## ⚠️ IMMEDIATE: Manual Actions Required

### 1. Merge PR #2 (Documentation)
**URL**: https://github.com/Arnarsson/DroneTest2/pull/2
**Contents**:
- Deployment checklist
- Phase 1 completion summary
- Config backup

**Action**: Review and merge when ready

### 2. Apply Database Migration (CRITICAL)
**File**: `migrations/010_evidence_scoring_system.sql`
**Method**: Supabase SQL Editor

**Steps**:
1. Go to Supabase Dashboard → SQL Editor
2. Paste entire migration file contents
3. Click "Run"
4. Verify with: `SELECT evidence_score, COUNT(*) FROM incidents GROUP BY evidence_score;`

**Why Critical**:
- Without this, evidence scores won't auto-update when sources are added
- Scoring will fall back to hardcoded values (less accurate)
- Database trigger is essential for Phase 1 functionality

**Expected Output**:
```
CREATE FUNCTION
CREATE TRIGGER
UPDATE 27  -- Number of incidents recalculated
```

### 3. Monitor First Scraper Run
**When**: Next GitHub Actions run (every 15 minutes)
**Check**:
- Zero 404 errors in logs
- All 18 sources successfully scraped
- New incidents have evidence_score populated
- Sources arrays are non-empty

**How to Check**:
```bash
gh run list --repo Arnarsson/2 --workflow=ingest.yml --limit 3
gh run view <run_id> --log
```

---

## 🚀 Phase 2: Social Media Monitoring (Next Priority)

### Goal
Expand incident detection to social media platforms for early warning signals

### Implementation Plan

#### 2.1 Nitter RSS Integration (Week 1)
**Why**: Twitter is often first to report drone incidents
**How**: Use Nitter instances to access Twitter RSS without API keys

**Tasks**:
- [ ] Select reliable Nitter instances (nitter.net, nitter.cz)
- [ ] Add Twitter accounts to monitor in `config_verified.py`:
  - @PolitiKbh (Copenhagen Police)
  - @NorskPoliti (Norwegian Police)
  - @Polisen (Swedish Police)
  - Aviation-focused accounts
- [ ] Create `social_scraper.py` for Nitter RSS parsing
- [ ] Implement pattern-based incident detection
- [ ] Set trust_weight=1 for social media sources

**Anti-Hallucination Measures**:
- Require specific keywords: "drone", "UAV", "lufthavn", "airport"
- Exclude: retweets, promotional content, drone news (non-incident)
- Flag for manual review (don't auto-publish)

#### 2.2 Reddit Monitoring (Week 2)
**Subreddits to Monitor**:
- r/denmark + r/copenhagen (local incidents)
- r/aviation + r/flying (aviation community)
- r/OSINT (open source intelligence)

**Implementation**:
- [ ] Use Reddit RSS feeds (no API key needed)
- [ ] Pattern matching for incident reports
- [ ] Extract location from post text
- [ ] Link to Reddit thread as source

#### 2.3 Admin Review Dashboard (Week 3)
**Why**: Social media sources need human verification before publication

**Features**:
- [ ] Review queue for trust_weight=1 incidents
- [ ] Approve/Reject workflow
- [ ] Bulk actions (approve similar, reject spam)
- [ ] Evidence upgrade (if verified with official source)

**Tech Stack**:
- Next.js admin route: `/admin/review`
- Protected with password/auth
- Direct database updates

---

## 🔍 Phase 3: HTML Scraping for Police Sources (Priority)

### Goal
Restore Tier 4 (OFFICIAL) evidence scoring by scraping police websites directly

### Why Needed
All police RSS feeds returned 404 - they don't exist. Must use HTML scraping instead.

### Implementation Plan

#### 3.1 Danish Police Scraping (Week 1)
**Target**: https://politi.dk/koebenhavns-politi/nyhedsliste

**Tasks**:
- [ ] Create `police_html_scraper.py`
- [ ] Use BeautifulSoup to parse news pages
- [ ] Extract: title, date, location, narrative
- [ ] Detect drone keywords in press releases
- [ ] Set trust_weight=4 automatically

**Example Code**:
```python
import requests
from bs4 import BeautifulSoup

def scrape_danish_police(district_url):
    response = requests.get(district_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find press releases
    articles = soup.find_all('article', class_='news-item')

    for article in articles:
        title = article.find('h2').text
        date = article.find('time')['datetime']
        content = article.find('div', class_='content').text

        # Check for drone keywords
        if any(word in content.lower() for word in ['drone', 'dron', 'uav']):
            yield {
                'title': title,
                'occurred_at': date,
                'narrative': content,
                'trust_weight': 4,  # Official police source
                'source_type': 'police',
                'source_url': article.find('a')['href']
            }
```

**Anti-Hallucination**:
- Only scrape actual police domains (verify SSL cert)
- Date validation (must be recent, not archive)
- Location extraction (must match Denmark geography)

#### 3.2 Nordic Police Scraping (Week 2)
**Norway**: https://www.politiet.no/aktuelt/
**Sweden**: https://polisen.se/aktuellt/
**Finland**: https://poliisi.fi/en/topical

**Same approach**:
- HTML parsing with BeautifulSoup
- Keyword detection in local languages
- trust_weight=4 for official sources

---

## 📊 Quick Wins (Can Do Anytime)

### Apply Performance Indexes
**File**: `migrations/006_performance_indexes.sql`
**Impact**: 73% faster API (11.4s → 3s)
**Effort**: 5 minutes

```bash
psql $DATABASE_URL -f migrations/006_performance_indexes.sql
```

### Apply Geocoding Jitter
**File**: `migrations/008_add_geocoding_jitter.sql`
**Impact**: Separates overlapping incidents on map
**Why**: 13 incidents currently share exact coordinates (generic geocoding)

```bash
psql $DATABASE_URL -f migrations/008_add_geocoding_jitter.sql
```

### Update Frontend Evidence Legend
**File**: `frontend/components/EvidenceLegend.tsx`
**Change**: Update to reflect new 4-tier system
**Impact**: User education on evidence scoring

---

## 🧪 Testing Strategy for Phase 2 & 3

### Unit Tests
```bash
# Create tests for each new scraper
ingestion/test_social_scraper.py
ingestion/test_police_html_scraper.py

# Run all tests
python3 -m pytest ingestion/test_*.py
```

### Integration Tests
```bash
# Test full pipeline
1. Scraper runs → 2. Sends to API → 3. Evidence score calculated → 4. Appears on map
```

### Anti-Hallucination Validation
```python
def test_no_fake_incidents():
    """Ensure scraper doesn't create incidents without actual sources"""
    incidents = scraper.run()

    for incident in incidents:
        assert incident['source_url'], "Must have source URL"
        assert validate_url(incident['source_url']), "URL must be valid"
        assert incident['trust_weight'] in [1,2,3,4], "Trust weight must be valid"
```

---

## 📈 Success Metrics

### Phase 2 Success Criteria
- [ ] At least 5 social media sources configured
- [ ] Pattern detection catches drone keywords accurately
- [ ] Admin review dashboard functional
- [ ] Zero hallucinated incidents (all have source URLs)
- [ ] Social incidents flagged for review (not auto-published)

### Phase 3 Success Criteria
- [ ] At least 3 police websites scraped successfully
- [ ] HTML parsing extracts accurate incident data
- [ ] Tier 4 (OFFICIAL) incidents appearing in production
- [ ] Evidence score distribution includes 4s
- [ ] Source attribution shows police website URLs

---

## 🗓️ Proposed Timeline

### Week 1 (Oct 6-12)
- ✅ Phase 1 Complete
- ⏳ Merge PR #2
- ⏳ Apply database migration
- 🆕 Start Phase 2: Nitter RSS integration

### Week 2 (Oct 13-19)
- 🆕 Phase 2: Reddit monitoring
- 🆕 Phase 2: Admin review dashboard
- 🆕 Start Phase 3: Danish police HTML scraping

### Week 3 (Oct 20-26)
- 🆕 Phase 3: Nordic police scraping
- 🆕 Testing and validation
- 🆕 Documentation updates

### Week 4 (Oct 27-31)
- 🆕 Deploy Phase 2 & 3 to production
- 🆕 Monitor for issues
- 🆕 Performance optimization

---

## 🔒 Ongoing Anti-Hallucination Principles

For ALL future phases, maintain:

1. **URL Validation**: Every source must be validated before use
2. **Trust Weight Assignment**: Explicit trust_weight for each source
3. **Pattern Detection**: No AI inference without validation
4. **Manual Review**: Social media requires human verification
5. **Testing**: Unit tests for all scraper logic
6. **Documentation**: Track every decision in INVESTIGATION_FINDINGS.md

---

## 📞 Resources

**Code**:
- Evidence scoring: `ingestion/verification.py`
- Scraper base: `ingestion/scrapers/news_scraper.py`
- Config: `ingestion/config.py`

**Documentation**:
- Phase 1: `PHASE_1_COMPLETE.md` (on feature branch)
- Deployment: `DEPLOYMENT_CHECKLIST.md` (on feature branch)
- Findings: `INVESTIGATION_FINDINGS.md`

**Testing**:
```bash
python3 ingestion/test_evidence_scoring.py
python3 ingestion/validate_sources.py
```

---

## 🎯 Priority Order

1. **IMMEDIATE**: Merge PR #2 and apply database migration
2. **HIGH**: Phase 2 (Social Media) - Early warning capability
3. **HIGH**: Phase 3 (Police Scraping) - Restore official sources
4. **MEDIUM**: Performance indexes (quick win)
5. **LOW**: Frontend enhancements (can wait)

---

**Last Updated**: 2025-10-05
**Status**: Phase 1 Complete, Phase 2 Planning
**Next Review**: After PR #2 merge and migration applied

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
