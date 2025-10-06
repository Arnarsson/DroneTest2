# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository

**Main Repository**: https://github.com/Arnarsson/DroneTest2
**Live Site**: https://www.dronemap.cc (production), https://dronetest-h3w7bsly4-arnarssons-projects.vercel.app (staging)
**Platform**: Vercel (auto-deploys from `main` branch)

Real-time drone incident tracking for Europe with evidence-based reporting and multi-source verification.

---

## Development Commands

### Frontend (Next.js 14.2.33)
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Dev server → http://localhost:3000
npm run build        # Production build
npm run lint         # TypeScript + ESLint
```

**CRITICAL**: If build fails with "barrel loader" or "TypeScriptTransformer" errors:
1. Check date-fns imports - use SPECIFIC paths only: `'date-fns/format'` NOT `'date-fns'`
2. Clean rebuild: `rm -rf .next node_modules/.cache && npm run dev`
3. Next.js 14.2.33+ required (14.1.0 has barrel loader bug)

### Scraper (Python 3.11)
```bash
cd ingestion
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Testing
python3 ingest.py --test              # Dry run (no API calls)
python3 test_consolidator.py          # Test multi-source consolidation
python3 test_fake_detection.py        # Test fake news filtering
python3 test_evidence_scoring.py      # Test evidence logic
python3 test_geographic_database_simple.py  # Test location database

# Production
python3 ingest.py                     # Full ingestion pipeline
```

### Database
```bash
# CRITICAL: Use port 5432 for migrations, NOT 6543
psql "postgresql://...@...pooler.supabase.com:5432/postgres" -f migrations/XXX.sql

# Port 6543 (transaction pooler) for serverless functions only
```

---

## Critical Architecture

### 1. Evidence System - Single Source of Truth

**File**: `frontend/constants/evidence.ts`

**RULE**: ALL components MUST import from this file. Never duplicate evidence colors/labels.

```typescript
import { getEvidenceConfig } from '@/constants/evidence'
const config = getEvidenceConfig(score as 1 | 2 | 3 | 4)
// Use: config.color, config.label, config.emoji, config.gradient
```

**4-Tier Scoring System**:
- **4 (OFFICIAL/Green)**: Police, military, NOTAM, aviation authority sources
- **3 (VERIFIED/Amber)**: 2+ media sources WITH official quotes in content
- **2 (REPORTED/Orange)**: Single credible source (trust_weight ≥ 2)
- **1 (UNCONFIRMED/Red)**: Social media, low trust sources

**Multi-Source Architecture**: Backend consolidates multiple sources for same incident, recalculates evidence score based on combined sources (see `ingestion/consolidator.py`)

### 2. Map Clustering - Manual Pre-Processing

**File**: `frontend/components/Map.tsx`

The map does NOT use Leaflet's auto-clustering. Instead:

```typescript
// Pre-process incidents by: coordinates (rounded to ~110m) + asset_type
const facilityKey = `${lat.toFixed(3)},${lon.toFixed(3)}-${asset_type}`
// 2+ incidents at same facility → ONE marker showing ✈️ 3
// Individual incidents → Evidence score marker (1-4)
```

**Why?** Prevents confusing numbered clusters (7, 8, 9) that look like evidence scores.

### 3. Multi-Source Consolidation Pipeline

**Files**: `ingestion/consolidator.py`, `ingestion/ingest.py`

**Architecture**: "1 incident → multiple sources"

```python
# Hash-based deduplication (location + time, NOT title)
from consolidator import ConsolidationEngine
engine = ConsolidationEngine()

# Deduplication strategy:
# - Location rounded to ~1km (0.01°)
# - Time rounded to 6-hour window
# - Title NOT in hash (different headlines = same incident)

consolidated = engine.consolidate_incidents(raw_incidents)
# Merges sources, recalculates evidence scores, enhances narratives
```

**Evidence Score Recalculation**:
- Score 4: ANY official source (police/military/NOTAM/aviation)
- Score 3: 2+ media sources WITH official quote detection (`has_official_quote()`)
- Score 2: 1 credible source (trust_weight ≥ 2)
- Score 1: Low trust sources

### 4. Fake News Detection System

**File**: `ingestion/fake_detection.py`

**6-Layer Detection**:
1. Domain blacklist (satire sites like Rokokoposten.dk)
2. Satire keyword detection (satire, parodi, spøg)
3. Clickbait pattern matching ("du vil ikke tro", "shocking")
4. Conspiracy theory detection (false flag, coverup)
5. Temporal consistency (future dates, >30 days old)
6. Source credibility (avg trust_weight < 0.3)

```python
from fake_detection import FakeNewsDetector
detector = FakeNewsDetector()

# Returns (is_fake: bool, confidence: float, reasons: list)
is_fake, confidence, reasons = detector.is_fake_news(incident)

# Default threshold: 0.5 (configurable in ingest.py)
```

### 5. PostGIS Database Schema

**CRITICAL**: Coordinates stored as PostGIS `geography` points, NOT `lat`/`lon` columns.

```sql
-- ✅ Correct
SELECT ST_Y(location::geometry) as lat, ST_X(location::geometry) as lon
FROM incidents;

-- ❌ Wrong - columns don't exist
SELECT lat, lon FROM incidents;
```

**Connection Modes**:
- Port **6543** (transaction pooler): Serverless functions (frontend API)
- Port **5432** (direct connection): Migrations, long queries, manual operations

**Multi-Source Schema** (Migration 011):
```sql
-- incident_sources table stores multiple sources per incident
CREATE TABLE incident_sources (
    id UUID PRIMARY KEY,
    incident_id UUID REFERENCES incidents(id),
    source_url TEXT,
    source_type VARCHAR(50),  -- police, news, aviation_authority
    source_name TEXT,
    source_quote TEXT,        -- For official quote detection
    trust_weight DECIMAL(3,2) -- 0.0-1.0 trust score
);

-- Auto-recalculates evidence score when sources change
CREATE TRIGGER update_evidence_score_trigger ...
```

### 6. API Architecture - Python Serverless

**Location**: `frontend/api/` (NOT Next.js API routes - these are Python)

- `incidents.py` - GET endpoint (filtered incidents, PostGIS queries)
- `ingest.py` - POST endpoint (scraper ingestion, requires Bearer token)
- `db.py` - Database utilities (connection pooling, PostGIS helpers)

**Why Python?**
- Better PostGIS/PostgreSQL integration than Node.js
- Matches scraper language for consistency
- Vercel supports Python serverless functions

### 7. Geographic Database

**File**: `ingestion/config.py`

**Coverage**: 111 verified Nordic locations
- 🇩🇰 Denmark: 7 locations
- 🇳🇴 Norway: 25 locations
- 🇸🇪 Sweden: 29 locations
- 🇫🇮 Finland: 19 locations
- 🇵🇱 Poland: 8 locations
- 🇳🇱 Netherlands: 5 locations

**Note**: 16 legacy Danish airports missing country/type metadata (still work for matching)

**Asset Types**: airport, military, harbor, powerplant, bridge, other

---

## Recent Changes & Build Fixes (October 2025)

### Next.js Build Error Fix (Latest)
**Problem**: Next.js 14.1.0 barrel loader incompatible with date-fns 3.0.0
**Solution** (commit `c574ae3`):
1. Converted ALL date-fns barrel imports to specific paths:
   - `'date-fns'` → `'date-fns/format'`, `'date-fns/formatDistance'`, etc.
   - Fixed in: page.tsx, Map.tsx, Timeline.tsx, Analytics.tsx, IncidentList.tsx
2. Upgraded Next.js 14.1.0 → 14.2.33
3. Fresh dependency install resolved Sucrase/TypeScript transformer bugs

### Brand & UX Overhaul (October 1, 2025)
**Commits**: 694dabb (merge), f59373d, dc5f1e2

**What Changed**:
- **Brand Identity**: New logo + "Safety Through Transparency" tagline
- **Evidence Constants**: `constants/evidence.ts` - single source of truth
- **New Components**: DroneWatchLogo, EvidenceBadge, SourceBadge
- **Page Redesigns**: About, Analytics, List views completely rebuilt
- **API Fixes**: Re-enabled sources subquery, fixed ingest schema mismatch
- **Consistency**: All evidence colors/labels now match across Map/List/Popups/Legend

---

## Git Workflow

```bash
git push origin main    # Main repository → triggers Vercel deploy
```

---

## Common Gotchas

### 1. date-fns Imports (CRITICAL for builds)
❌ `import { format } from 'date-fns'` → Build error
✅ `import { format } from 'date-fns/format'` → Works

**Why?** Next.js 14 barrel loader optimization incompatible with date-fns structure

### 2. Evidence Colors
❌ Hardcoding: `<div className="bg-green-500">Official</div>`
✅ Importing: `const config = getEvidenceConfig(score); <div className={config.bgClass}>`

### 3. PostGIS Columns
❌ `SELECT lat, lon FROM incidents` → ERROR
✅ `SELECT ST_Y(location::geometry) as lat, ST_X(location::geometry) as lon`

### 4. Database Connection
❌ Port 6543 for migrations → Timeout
✅ Port 5432 for migrations (change in DATABASE_URL)

### 5. Map Clustering
❌ Adding markers directly → Leaflet creates numbered clusters
✅ Pre-process by facility first → Add grouped markers

### 6. Multi-Source Deduplication
❌ Using title in hash → Same incident with different headlines treated as duplicates
✅ Using location + time only → Properly merges sources for same incident

---

## Data Quality Principles

1. **Evidence-Based**: Only verified incidents with credible sources
2. **No Speculation**: Factual, neutral reporting only
3. **Single Source of Truth**: Evidence system in `constants/evidence.ts`
4. **Quality > Quantity**: Fewer verified incidents better than many unverified
5. **Multi-Source Verification**: Consolidate sources, upgrade evidence scores
6. **Fake News Filtering**: 6-layer detection with confidence scoring
7. **Geographic Scope**: Only Nordic region incidents (54-71°N, 4-31°E) - filters out foreign events covered by Nordic news

---

## Testing Strategy

### Backend Testing
```bash
cd ingestion

# Test multi-source consolidation
python3 test_consolidator.py          # 4 test scenarios

# Test fake news detection
python3 test_fake_detection.py        # 6 detection layers

# Test evidence scoring
python3 test_evidence_scoring.py      # Single & multi-source

# Test geographic scope filtering
python3 test_geographic_filter.py     # 8 test cases (Nordic vs foreign)

# Test geographic database
python3 test_geographic_database_simple.py  # 5 validation tests

# Test SQL migrations
bash test_migrations.sh               # Syntax validation

# Integration test
python3 ingest.py --test              # End-to-end dry run
```

### Frontend Testing
```bash
cd frontend

# Build validation
npm run build                         # Production build test
npm run lint                          # TypeScript + ESLint

# Local development
npm run dev                           # http://localhost:3000

# Chrome DevTools testing
# Use mcp__chrome-devtools tools for E2E validation
```

---

## Key Files

**Evidence System**:
- `frontend/constants/evidence.ts` - Single source of truth for colors, labels, scoring logic

**Multi-Source Engine**:
- `ingestion/consolidator.py` - Deduplication, source merging, score recalculation
- `ingestion/fake_detection.py` - 6-layer fake news filtering
- `ingestion/utils.py` - Geographic scope filter (`is_nordic_incident()`), location extraction
- `ingestion/opensky_api.py` - Flight correlation (OpenSky Network API)

**Scrapers**:
- `ingestion/config.py` - 111 Nordic locations, trust weights
- `ingestion/db_cache.py` - Hash-based deduplication cache
- `ingestion/ingest.py` - Main orchestration pipeline + test blocking
- `ingestion/scrapers/police_scraper.py` - Danish police RSS (score 4)
- `ingestion/scrapers/news_scraper.py` - News aggregator (score 2-3)
- `ingestion/scrapers/aviation_scraper.py` - Nordic aviation authorities (framework complete)

**Frontend Components**:
- `frontend/components/Map.tsx` - Custom facility clustering logic
- `frontend/components/EvidenceBadge.tsx` - Evidence UI with tooltips
- `frontend/components/FilterPanel.tsx` - Filtering controls
- `frontend/app/page.tsx` - Main page with filter/timeline integration
- `frontend/components/DroneWatchLogo.tsx` - Brand logo component

**Database**:
- `migrations/011_source_verification.sql` - Multi-source schema (PENDING execution)
- `migrations/012_flight_correlation.sql` - OpenSky integration (PENDING execution)
- `frontend/api/db.py` - PostGIS query builders

**Testing**:
- `ingestion/test_consolidator.py` - Multi-source consolidation tests
- `ingestion/test_fake_detection.py` - Fake news detection tests
- `ingestion/test_evidence_scoring.py` - Evidence scoring validation
- `ingestion/test_geographic_filter.py` - Geographic scope filtering tests
- `ingestion/test_geographic_database_simple.py` - Location database tests
- `ingestion/test_migrations.sh` - SQL syntax validation

---

## Environment Variables

**Required in Vercel**:
- `DATABASE_URL` - Supabase connection string (port 6543 transaction pooler)
- `INGEST_TOKEN` - Secret Bearer token for scraper authentication

**Local Development** (`.env.local`):
```bash
DATABASE_URL="postgresql://...@...pooler.supabase.com:6543/postgres"
INGEST_TOKEN="your-secret-token"
```

---

## Deployment Workflow

1. **Development**: Make changes, test locally (`npm run dev`)
2. **Testing**: Run test suite (`python3 ingest.py --test`, `npm run build`)
3. **Commit**: Create meaningful commit with context
4. **Push**: `git push origin main`
5. **Vercel**: Auto-deploys to production
6. **Validation**: Check deployment logs, test live site

**Migration Deployment**:
1. Test locally: `psql "..." -f migrations/XXX.sql --dry-run`
2. Backup database: Use Supabase dashboard
3. Execute: `psql "...@...supabase.com:5432/postgres" -f migrations/XXX.sql`
4. Validate: Check schema, test queries, verify frontend

---

## Vercel Deployment

**Deploy to Production**:
```bash
cd frontend
vercel --prod
```

This will:
- Build Next.js application
- Deploy Python serverless functions
- Update production environment
- Return deployment URL

**Check Deployment Status**:
- Dashboard: https://vercel.com/arnarssons-projects/dronetest
- Logs: Available in Vercel dashboard
- Live Site: Check deployment URL

---

**Last Updated**: October 5, 2025
**Version**: 1.4.0 (DroneTest2 - Build Fixes + Multi-Source + Clean Architecture)
**Repository**: https://github.com/Arnarsson/DroneTest2
