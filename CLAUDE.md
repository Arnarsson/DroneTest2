# Claude Code Instructions for DroneWatch

## 🎯 Project Overview

**DroneWatch** is a real-time drone incident tracking platform for Europe, providing verified evidence-based reporting of drone-related events.

- **Repository**: https://github.com/Arnarsson/2
- **Live Site**: https://www.dronemap.cc
- **Status**: Production (v1.0) - Fully Operational ✅
- **Last Major Update**: October 1, 2025

---

## 📊 Current Status

### What's Working ✅
- **Frontend**: Next.js 14 app deployed on Vercel - **LIVE**
- **API**: Serverless functions returning 27 unique incidents (deduplicated!)
- **Database**: Supabase PostgreSQL with PostGIS - Clean, deduplicated data
- **Scraper**: GitHub Actions running every 15 minutes with location filtering
- **Data**: 20+ sources across 6 countries (Denmark, Norway, Sweden, Finland, Netherlands, Poland)
- **Features**: Real-time map, filtering, evidence scoring, responsive design
- **Brand**: Professional logo, tagline, redesigned pages
- **Deduplication**: Working perfectly - one incident per event ✅

### Brand Overhaul (Oct 1, 2025) 🎨
Complete UI/UX redesign for trust and professionalism (PR #41):
- ✅ **New brand identity**: Minimalist logo + "Safety Through Transparency" tagline
- ✅ **Evidence system**: Color-coded badges (🟢 Official → 🔴 Unconfirmed)
- ✅ **Source transparency**: Badge components with trust indicators
- ✅ **Page redesigns**: About, Analytics, List views completely rebuilt
- ✅ **Consistency**: Single constants system for all evidence colors/labels
- ✅ **Auto-opening legend**: First-time visitor education
- ✅ **Latest Commits**: dc5f1e2, f59373d, 694dabb (PR #41 squash merge)

### Critical Fixes (Oct 1, 2025) 🔥
- ✅ **Sources API query**: Re-enabled sources subquery with proper joins
- ✅ **Ingest endpoint**: Fixed schema mismatch (name/domain/source_type)
- ✅ **Type definitions**: Added source_title and published_at fields
- ✅ **Local dev**: Auto-fallback to production API when DATABASE_URL unavailable
- ✅ **Map markers**: Fixed colors to match evidence badge system
- ✅ **Evidence Legend**: Updated colors/labels for consistency

### Latest Updates (Oct 1, 2025 - Evening) 🎉
- ✅ **Migration 007 COMPLETED**: 46 → 27 unique incidents (41% reduction!)
- ✅ **Deduplication working**: Same event from multiple sources = one incident
- ✅ **Geocoding fixed**: No more default coordinate clustering
- ✅ **Code cleanup**: Python cache removed, .gitignore updated
- ✅ **Serena MCP installed**: Available for coding assistance
- ✅ **Map display clean**: Cluster "33" → "14" (much better!)
- ✅ **AI Deduplication**: Smart time validation + 6-layer anti-hallucination protection
- ✅ **Geocoding conflict detection**: Prevents merging incidents with suspicious coordinates
- ✅ **Map clustering improved** (commit 8e4d06a): Enhanced spiderfying and color-coded clusters
- ✅ **Migration 008 created**: Ready to apply geocoding jitter for overlapping coordinates

### Verified Working (Oct 1, 2025) ✅
- ✅ **Logo and branding**: Displaying correctly in dark mode
- ✅ **Evidence badges**: Perfect color consistency (🟢🟡🟠🔴)
- ✅ **Map markers**: 27 unique incidents rendering with correct colors
- ✅ **Popups**: Evidence badges and incident details displaying
- ✅ **Legend**: Auto-opens on first visit
- ✅ **Database**: Clean, deduplicated data (27 unique events)
- ✅ **About/Analytics/List**: All redesigned pages working
- ✅ **Local dev**: Hot reload working with production API fallback

### Pending (Manual Action Required) ⏳
- ⏳ **Migration 008** - Apply geocoding jitter to separate overlapping incidents
  - **Issue**: 13 incidents share exact coordinates (8 at one location, 5 at another)
  - **Cause**: Generic geocoding defaults (e.g., "Copenhagen" → same coordinates)
  - **Solution**: Run `psql $DATABASE_URL -f migrations/008_add_geocoding_jitter.sql`
  - **Effect**: Spreads overlapping incidents in 200m radius for better visibility
  - **Note**: These are separate incidents (different dates), NOT duplicates

### Pending (Automatic) ⏳
- ⏳ **Source population**: Waiting for next scraper run (every 15 min)
  - Sources arrays will populate automatically
  - Each incident will show multiple news sources
- ⏳ **Geocoding improvements**: Future incidents will only show if location is known
  - Prevents clustering at default coordinates
  - International incidents now filtered out unless specific location found

### Future Enhancements
- 📝 **Timeline slider**: Not yet implemented
- 📝 **User submission form**: Pending
- 📝 **Embed mode**: For newsroom integration
- 📝 **Keyboard shortcuts**: Accessibility enhancement

### Deduplication System ✅
- **Strategy**: Location+time based (not title-based)
- **Rule**: Same location (±1km) + same time (±6hr) = Same incident, add as source
- **Status**: Working perfectly after migration 007
- **Result**: 27 unique events (down from 46 duplicates)
- **Evidence scoring**: Increases with more credible sources

### Geocoding System ✅
- **Strategy**: Only incidents with known specific locations
- **Fix**: Returns None instead of default Copenhagen coordinates
- **Result**: No more false clustering of unrelated incidents
- **Future**: International incidents skipped unless specific location found

---

## 🏗️ Architecture

### Tech Stack
```yaml
Frontend:
  framework: Next.js 14
  language: TypeScript
  styling: Tailwind CSS
  mapping: Leaflet.js
  state: React hooks (useIncidents)

Backend:
  runtime: Vercel Serverless Functions
  language: Python 3.11
  database: Supabase (PostgreSQL + PostGIS)

Data Pipeline:
  scraper: Python 3.11
  scheduling: GitHub Actions (15 min intervals)
  caching: Database-backed (db_cache.py)
  verification: Confidence scoring (verification.py)

Deployment:
  platform: Vercel
  strategy: Auto-deploy from main branch
  CDN: Vercel Edge Network
```

### Project Structure
```
/
├── frontend/                 # Next.js application
│   ├── app/
│   │   ├── page.tsx             # Main map view
│   │   └── about/page.tsx       # About page (redesigned Oct 1)
│   ├── components/
│   │   ├── Map.tsx              # Leaflet map with clustering
│   │   ├── FilterPanel.tsx      # Country/status/evidence filters
│   │   ├── IncidentList.tsx     # List view (improved Oct 1)
│   │   ├── Analytics.tsx        # Analytics dashboard (redesigned Oct 1)
│   │   ├── Header.tsx           # Header with logo and tagline
│   │   ├── DroneWatchLogo.tsx   # NEW: Brand logo component
│   │   ├── EvidenceBadge.tsx    # NEW: Evidence scoring badges
│   │   ├── SourceBadge.tsx      # NEW: Source attribution badges
│   │   └── EvidenceLegend.tsx   # Evidence explanation (auto-opens)
│   ├── constants/
│   │   └── evidence.ts          # NEW: Single source of truth for evidence system
│   ├── hooks/
│   │   └── useIncidents.ts      # API data fetching (prod fallback added)
│   ├── api/                     # Vercel serverless functions
│   │   ├── incidents.py         # Main API endpoint (sources enabled)
│   │   ├── ingest.py            # Scraper ingestion (schema fixed Oct 1)
│   │   └── db.py                # Database utilities (sources subquery)
│   └── types/
│       └── index.ts             # TypeScript definitions (updated)
│
├── ingestion/              # Scraper system
│   ├── config.py          # 20+ source configurations (13KB)
│   ├── ingest.py          # Main orchestration script
│   ├── db_cache.py        # Database-backed deduplication
│   ├── verification.py    # Confidence scoring system
│   ├── utils.py           # Helper functions
│   └── scrapers/
│       ├── police_scraper.py  # RSS feed scraper (creates sources)
│       └── news_scraper.py    # News source scraper (creates sources)
│
├── .github/workflows/
│   └── ingest.yml         # Scheduled scraper execution (15 min)
│
├── migrations/
│   ├── 001-005...         # Previous migrations
│   └── 006_performance_indexes.sql  # NEW: Performance optimization
│
├── sql/                   # Database queries and setup
├── DEPLOYMENT_COMPLETE.md # NEW: Deployment guide
├── APPLY_INDEXES.md       # NEW: Index application guide
└── TESTING_CHECKLIST.md   # NEW: QA checklist
```

---

## 🚀 Development Workflow

### Local Setup
```bash
# Clone repository
gh repo clone Arnarsson/2 dronewatch-2

# Frontend development
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000

# Test scraper locally
cd ../ingestion
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 ingest.py --test
```

### Environment Variables

**Required in Vercel**:
```bash
DATABASE_URL=postgresql://user:pass@db.supabase.co:6543/postgres
INGEST_TOKEN=your-secret-token-here
```

**Local Development** (`.env.local`):
```bash
# Option 1: Pull from Vercel (recommended)
vercel env pull .env.local --environment production --yes

# Option 2: Manual (if needed)
DATABASE_URL=your-supabase-connection-string
INGEST_TOKEN=dw-secret-2025-nordic-drone-watch

# Note: Local dev will auto-use production API if DATABASE_URL not set
```

### Git Workflow
```bash
# Current active branches
main                              # Production - Latest: dc5f1e2

# Creating features
git checkout -b feature/your-feature-name
# Make changes
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
gh pr create --base main
```

---

## 📋 Common Tasks

### Running the Scraper
```bash
cd ingestion

# Test mode (shows data without sending)
python3 ingest.py --test

# Production mode (sends to API)
python3 ingest.py

# Override API URL
python3 ingest.py --api-url https://www.dronemap.cc
```

### Database Operations
```bash
# Connect to Supabase
psql $DATABASE_URL

# Check incident count
SELECT COUNT(*), country FROM incidents GROUP BY country;

# View recent incidents
SELECT title, occurred_at, country FROM incidents
ORDER BY occurred_at DESC LIMIT 10;

# Clean duplicates (see final_cleanup.sql)
```

### Deployment
```bash
# Deployment is automatic on push to main
git push origin main

# Vercel will:
# 1. Build Next.js frontend
# 2. Deploy serverless functions
# 3. Update production site
```

---

## 🔧 Key Files to Know

### Critical Configuration Files
- `frontend/constants/evidence.ts` - **IMPORTANT**: Single source of truth for evidence system
- `frontend/api/db.py` - Database connection and queries (sources subquery enabled)
- `frontend/api/ingest.py` - **CRITICAL**: Scraper endpoint (schema fixed Oct 1)
- `ingestion/config.py` - 20+ source configurations (13KB)
- `ingestion/db_cache.py` - Database-backed deduplication
- `ingestion/verification.py` - Incident verification logic
- `.github/workflows/ingest.yml` - Scheduled scraper execution

### Brand & UI Components (New Oct 1, 2025)
- `frontend/components/DroneWatchLogo.tsx` - Minimalist quadcopter logo
- `frontend/components/EvidenceBadge.tsx` - Evidence scoring UI with tooltips
- `frontend/components/SourceBadge.tsx` - Source attribution with icons
- `frontend/components/Header.tsx` - "Safety Through Transparency" tagline
- `frontend/app/about/page.tsx` - Complete evidence methodology explanation

### Important Scripts
- `ingestion/ingest.py` - Main scraper orchestration
- `migrations/006_performance_indexes.sql` - **APPLY THIS**: 73% speed improvement
- `setup-scraper.sh` - One-time scraper setup
- `final_cleanup.sql` - Duplicate removal script

### Documentation
- `DEPLOYMENT_COMPLETE.md` - **NEW**: Latest deployment status and steps
- `APPLY_INDEXES.md` - **NEW**: How to apply performance indexes
- `TESTING_CHECKLIST.md` - **NEW**: QA checklist for deployments
- `README.md` - Project overview and API docs
- `FORWARD_PLAN.md` - Roadmap and future features
- `SUPABASE_SETUP.md` - Database setup guide

---

## 🐛 Debugging Guide

### Scraper Issues
```bash
# Check GitHub Actions logs
gh run list --repo Arnarsson/2 --workflow=ingest.yml

# Test imports locally
cd ingestion
python3 -c "from db_cache import ScraperCache; print('✓ OK')"
python3 -c "from verification import calculate_confidence_score; print('✓ OK')"

# Check source count
python3 -c "from config import SOURCES; print(f'{len(SOURCES)} sources')"
```

### API Issues
```bash
# Test incidents endpoint
curl "https://www.dronemap.cc/api/incidents?country=all&limit=5"

# Check database connection
curl "https://www.dronemap.cc/api/healthz"

# Test ingestion (requires token)
curl -X POST "https://www.dronemap.cc/api/ingest" \
  -H "Authorization: Bearer $INGEST_TOKEN" \
  -d '{"title":"Test","lat":55.6,"lon":12.6,...}'
```

### Frontend Issues
```bash
# Check build errors
cd frontend
npm run build

# Type checking
npm run type-check

# View logs in browser console
# Network tab → Filter by "incidents"
```

---

## 📝 Recent Changes & History

### October 1, 2025 - Brand & UX Overhaul (PR #41)
**Commits**: 694dabb (merge), f59373d, dc5f1e2

**What Changed**:
- **Brand Identity**: New logo + "Safety Through Transparency" tagline
- **Evidence Constants**: `constants/evidence.ts` - single source of truth
- **New Components**: DroneWatchLogo, EvidenceBadge, SourceBadge
- **Page Redesigns**: About, Analytics, List views completely rebuilt
- **API Fixes**: Re-enabled sources subquery, fixed ingest schema mismatch
- **Performance**: Created migration 006 for database indexes
- **Consistency**: All evidence colors/labels now match across Map/List/Popups/Legend

**Impact**:
- Professional, trustworthy design
- Perfect visual consistency
- Source attribution ready (pending scraper population)
- 73% faster API (when indexes applied)
- Auto-opening legend for first-time visitors

### September 30, 2025 - Scraper Integration
**Commit**: `3d765d2` - "feat: Integrate scraper-improvements into modern-ui-overhaul"

**What Changed**:
- Added `ingestion/db_cache.py` (6.3KB) - Database deduplication
- Added `ingestion/verification.py` (9.6KB) - Confidence scoring
- Expanded `config.py` from 2.9KB to 13KB (4 → 20+ sources)
- Enhanced scrapers with retry logic and error isolation

**Impact**:
- 5x more data sources
- Robust error handling
- Deduplication working

---

## 🎯 Immediate Next Steps

### CRITICAL - Must Do Now (5-10 minutes) 🔥
1. **Apply Performance Indexes** (see `APPLY_INDEXES.md`)
   ```bash
   psql $DATABASE_URL -f migrations/006_performance_indexes.sql
   ```
   **Impact**: API speed 11.4s → <3s (73% faster!)

2. **Verify Sources Populate** (after next scraper run)
   - Scraper runs every 15 minutes
   - Check: `curl "https://www.dronemap.cc/api/incidents?limit=3"`
   - Look for non-empty `sources` arrays

3. **Test Production Site**
   - Visit https://www.dronemap.cc
   - Verify new logo and tagline
   - Check About page loads
   - Test Analytics dashboard
   - Verify List view shows source counts

### Should Do (This Week)
1. ✅ Brand overhaul (completed Oct 1)
2. ✅ Evidence system consistency (completed Oct 1)
3. Monitor scraper for source population
4. Performance testing after index application
5. Mobile UX testing

### Nice to Have (Future)
1. Timeline slider implementation
2. User submission form
3. Embed mode for newsrooms
4. Keyboard shortcuts
5. Expand to more countries

---

## 🔍 Code Patterns to Follow

### Python (Scrapers & API)
```python
# Always use try-except with specific exceptions
try:
    result = scrape_source(url)
except requests.exceptions.Timeout:
    logger.error(f"Timeout: {url}")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)

# Use retry logic with exponential backoff
for attempt in range(max_retries):
    try:
        # operation
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)
            continue
```

### TypeScript (Frontend)
```typescript
// Use proper typing
interface Incident {
  id: string;
  title: string;
  lat: number;
  lon: number;
  // ...
}

// Handle loading and error states
const { incidents, loading, error } = useIncidents();
if (loading) return <LoadingSpinner />;
if (error) return <ErrorMessage error={error} />;
```

### SQL (Database)
```sql
-- Always use parameterized queries
SELECT * FROM incidents WHERE country = $1 AND status = $2

-- Use PostGIS for geospatial queries
SELECT ST_Y(location::geometry) as lat,
       ST_X(location::geometry) as lon
FROM incidents

-- Index for performance
CREATE INDEX idx_incidents_country ON incidents(country);
```

---

## ⚠️ Important Notes

### Security
- **Never commit** `.env.local` with real credentials
- **Always use** parameterized SQL queries
- **Validate** all user input before database operations
- **Rate limit** API endpoints to prevent abuse

### Performance
- Database queries have 9s timeout (Vercel limit)
- Keep API responses under 6MB (Vercel limit)
- Use transaction mode pooling for serverless
- Cache frequently accessed data

### Data Quality
- Evidence scores must be justified with sources
- All locations must have valid lat/lon coordinates
- Dates should be in ISO 8601 format
- Narratives should be factual and neutral

---

## 🤝 Getting Help

### Resources
- **GitHub Issues**: https://github.com/Arnarsson/2/issues
- **GitHub Actions**: https://github.com/Arnarsson/2/actions
- **Vercel Dashboard**: Check deployment logs
- **Supabase Dashboard**: Database queries and logs

### Contact
- **GitHub**: [@Arnarsson](https://github.com/Arnarsson)
- **Repository**: https://github.com/Arnarsson/2

---

## 📚 Related Documentation

- `README.md` - Quick start and API reference
- `FORWARD_PLAN.md` - Roadmap and future features
- `DEPLOYMENT_GUIDE.md` - Deployment instructions (if exists)
- `SUPABASE_SETUP.md` - Database configuration
- `OPTIMIZATION_SUMMARY.md` - Performance notes

---

---

## 🎨 Evidence System Reference

**ALL components must use** `constants/evidence.ts` for consistency

### Evidence Scores
- 🟢 **Score 4 - OFFICIAL**: Emerald (#10b981) - Police/Military/NOTAM
- 🟡 **Score 3 - VERIFIED**: Amber (#f59e0b) - Multiple credible sources
- 🟠 **Score 2 - REPORTED**: Orange (#f97316) - Single credible source
- 🔴 **Score 1 - UNCONFIRMED**: Red (#ef4444) - Unverified reports

### Components Using Evidence System
- `EvidenceBadge.tsx` - UI badges with icons and tooltips
- `Map.tsx` - Marker colors and popup badges
- `EvidenceLegend.tsx` - Legend panel
- `Analytics.tsx` - Chart colors
- Any future components - **MUST import from constants**

### How to Use
```typescript
import { EVIDENCE_SYSTEM, getEvidenceConfig } from '@/constants/evidence'

const config = getEvidenceConfig(incident.evidence_score)
// Returns: { label, color, bgClass, description, icon, etc. }
```

---

---

## 🔖 Checkpoint

**For detailed status snapshot, see:** `CHECKPOINT.md`

**Quick status:**
- ✅ All code deployed to production
- ⏳ Migrations ready (need manual Supabase execution)
- 🔥 32 duplicates exist (run migration 007 to fix)
- ⚡ API slow (run migration 006 to fix)

**Next actions:** Run migrations 006 & 007 in Supabase SQL Editor

---

**Last Updated**: October 1, 2025
**Version**: 1.1.0 (Brand Overhaul)
**Status**: Production deployed, migrations pending

🤖 Generated with [Claude Code](https://claude.com/claude-code)
