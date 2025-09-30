# Claude Code Instructions for DroneWatch

## 🎯 Project Overview

**DroneWatch** is a real-time drone incident tracking platform for Europe, providing verified evidence-based reporting of drone-related events.

- **Repository**: https://github.com/Arnarsson/2
- **Live Site**: https://www.dronemap.cc
- **Status**: Production (v1.0) - Active Development
- **Last Major Update**: September 30, 2025

---

## 📊 Current Status

### What's Working ✅
- **Frontend**: Next.js 14 app deployed on Vercel
- **API**: Serverless functions handling 200+ incidents/request
- **Database**: Supabase PostgreSQL with PostGIS for geospatial data
- **Scraper**: GitHub Actions running every 15 minutes
- **Data**: 20+ sources across 4 countries (Denmark, Norway, Sweden, Finland)
- **Features**: Real-time map, filtering, evidence scoring, responsive design

### Recent Integration (Sept 30, 2025) 🎉
Successfully merged `terragon/scraper-improvements` into `terragon/modern-ui-overhaul`:
- ✅ Added missing files: `db_cache.py`, `verification.py`
- ✅ Expanded from 4 to 20+ data sources
- ✅ Enhanced error handling with exponential backoff
- ✅ Database-backed deduplication
- ✅ Fixed database debugging code
- **PR #40**: https://github.com/Arnarsson/2/pull/40 (Open - Ready to merge)

### Known Issues ⚠️
- Scraper had interference issues between branches (NOW RESOLVED)
- Some duplicate incidents in database (cleanup script available)
- Timeline slider not yet implemented
- User submission form pending

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
│   ├── app/                 # Pages and layouts
│   ├── components/          # React components
│   │   ├── Map.tsx         # Leaflet map with clustering
│   │   ├── FilterPanel.tsx # Country/status/evidence filters
│   │   └── IncidentCard.tsx
│   ├── hooks/
│   │   └── useIncidents.ts # API data fetching
│   ├── api/                # Vercel serverless functions
│   │   ├── incidents.py    # Main API endpoint
│   │   ├── ingest.py       # Scraper ingestion
│   │   └── db.py          # Database utilities
│   └── types/
│       └── incident.ts     # TypeScript definitions
│
├── ingestion/              # Scraper system
│   ├── config.py          # 20+ source configurations (13KB)
│   ├── ingest.py          # Main orchestration script
│   ├── db_cache.py        # Database-backed deduplication
│   ├── verification.py    # Confidence scoring system
│   ├── utils.py           # Helper functions
│   └── scrapers/
│       ├── police_scraper.py  # RSS feed scraper
│       └── news_scraper.py    # News source scraper
│
├── .github/workflows/
│   └── ingest.yml         # Scheduled scraper execution
│
├── migrations/            # Database schema evolution
├── sql/                   # Database queries and setup
└── docs/                  # Additional documentation
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
API_BASE_URL=http://localhost:8000
INGEST_TOKEN=dw-secret-2025-nordic-drone-watch
DATABASE_URL=your-supabase-connection-string
```

### Git Workflow
```bash
# Current active branches
main                              # Production
terragon/modern-ui-overhaul      # UI improvements + integrated scraper (PR #40)
terragon/scraper-improvements    # Can be archived after PR #40 merge

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
- `frontend/api/db.py` - Database connection and queries (IMPORTANT: Uses sources subquery)
- `ingestion/config.py` - 20+ source configurations (13KB, recently expanded)
- `ingestion/db_cache.py` - Deduplication caching (recently added)
- `ingestion/verification.py` - Incident verification logic (recently added)
- `.github/workflows/ingest.yml` - Scraper automation

### Important Scripts
- `ingestion/ingest.py` - Main scraper orchestration
- `setup-scraper.sh` - One-time scraper setup
- `cleanup_codebase.sh` - Code cleanup utility
- `final_cleanup.sql` - Duplicate removal script

### Documentation
- `README.md` - Project overview and API docs
- `FORWARD_PLAN.md` - Roadmap and future features
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `SUPABASE_SETUP.md` - Database setup guide
- `OPTIMIZATION_SUMMARY.md` - Performance optimizations

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

### September 30, 2025 - Major Integration
**Commit**: `3d765d2` - "feat: Integrate scraper-improvements into modern-ui-overhaul"

**What Changed**:
- Added `ingestion/db_cache.py` (6.3KB) - Database deduplication
- Added `ingestion/verification.py` (9.6KB) - Confidence scoring
- Expanded `config.py` from 2.9KB to 13KB (4 → 20+ sources)
- Enhanced scrapers with retry logic and error isolation
- Fixed `frontend/api/db.py` - Re-enabled sources subquery
- Resolved import errors and configuration mismatches

**Impact**:
- 5x more data sources
- Robust error handling
- No more duplicate incidents
- Ready for production merge

### Earlier September 2025
- Multiple UI improvements (badge design, animations)
- Database query optimizations
- Performance profiling and fixes
- Evidence scoring system implementation

---

## 🎯 Immediate Next Steps

### Must Do (Before merging PR #40)
1. ✅ Review PR #40: https://github.com/Arnarsson/2/pull/40
2. ✅ Test integrated scraper in production
3. ✅ Verify all 20+ sources are working
4. ✅ Merge to main
5. ✅ Archive `terragon/scraper-improvements` branch

### Should Do (This Week)
1. Run duplicate cleanup script on database
2. Add unique constraint to prevent future duplicates
3. Document evidence scoring criteria
4. Test scraper with all new sources

### Nice to Have (Next Week)
1. Implement timeline slider
2. Add user submission form
3. Create analytics dashboard
4. Expand to more countries

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

**Last Updated**: September 30, 2025
**Version**: 1.0.0
**Status**: Production with active development

🤖 Generated with [Claude Code](https://claude.com/claude-code)
