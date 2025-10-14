# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository

**Main Repository**: https://github.com/Arnarsson/DroneWatch2.0
**Live Site**: https://dronewatch.cc (redirects to www.dronemap.cc)
**Production**: https://www.dronemap.cc
**Platform**: Vercel (auto-deploys from `main` branch)

Real-time drone incident tracking across **ALL OF EUROPE** with evidence-based reporting and multi-source verification.

**Geographic Coverage**: 🌍 35-71°N, -10-31°E (Nordic + UK + Ireland + Germany + France + Spain + Italy + Poland + Benelux + Baltics)
**Live Sources**: 45+ verified RSS feeds from 15+ countries | 100-200 incidents/month expected

---

## Development Commands

### Local Development Options

**Option 1: Vercel Dev (Recommended for Full Testing)**
```bash
cd /Users/sven/Desktop/MCP/DroneTest2  # Run from PROJECT ROOT, not frontend/
npx vercel dev
```

This will:
- Run Next.js dev server on port 3000 (or auto-assigned)
- Run Python serverless functions locally (`/api/*` endpoints)
- Properly route API requests to Python functions
- Simulate production environment

**Option 2: Next.js Dev Only (UI Development)**
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Dev server → http://localhost:3000
npm run build        # Production build
npm run lint         # TypeScript + ESLint
```

**⚠️ LIMITATION**: Python API endpoints (`/api/incidents`, `/api/ingest`) will return 404 errors with `npm run dev`. The Python serverless functions require Vercel's environment to run. For full local testing with API support, use `vercel dev` instead.

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
python3 test_ai_verification.py       # Test AI incident classification (NEW v2.2.0)

# Production
python3 ingest.py                     # Full ingestion pipeline (v2.2.0)
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

### 3. Multi-Source Consolidation Pipeline ✅ IMPLEMENTED (v2.3.0)

**Files**: `ingestion/consolidator.py` (345 lines), `ingestion/ingest.py` (integrated)

**Architecture**: "1 incident → multiple sources" with intelligent deduplication

```python
# Hash-based deduplication (location + time, NOT title)
from consolidator import ConsolidationEngine

engine = ConsolidationEngine(
    location_precision=0.01,  # ~1km (rounds coordinates)
    time_window_hours=6        # Groups incidents within 6h window
)

# Deduplication strategy:
# - Location: Rounded to 0.01° (~1.1km at Nordic latitudes)
# - Time: Grouped into 6-hour windows
# - Title: NOT included (allows different headlines for same incident)
# - Country + asset_type: Used to prevent cross-border/type merging

# Get statistics before consolidation
stats = engine.get_consolidation_stats(raw_incidents)
# Returns: {total_incidents, unique_hashes, potential_merges, merge_rate}

# Consolidate incidents
consolidated = engine.consolidate_incidents(raw_incidents)
# Returns: List of merged incidents with combined sources
```

**Source Merging Logic**:
- Deduplicates sources by URL (prevents double-counting same article)
- Keeps ALL unique sources (no filtering by type)
- Uses longest narrative (most detailed)
- Uses best title (most descriptive - longest with substance)
- Tracks `merged_from` count and `source_count`

**Evidence Score Recalculation** (from `verification.py`):
- **Score 4**: ANY official source (police/military/NOTAM/aviation, trust_weight=4)
- **Score 3**: 2+ media sources (trust_weight≥2) WITH official quote detection
- **Score 2**: Single credible source (trust_weight ≥ 2)
- **Score 1**: Low trust sources (trust_weight < 2)

**Testing**: 5 scenarios, 100% pass rate
- Single incident (no consolidation)
- Same location + time → MERGE
- Different locations → NO MERGE
- Evidence upgrade: media (2) + police (4) → OFFICIAL (4)
- Consolidation statistics calculation

**Integration** (in `ingest.py`):
```python
# Step 5 in ingestion pipeline (after non-incident filtering)
all_incidents = consolidation_engine.consolidate_incidents(all_incidents)
# Runs automatically on every ingestion
```

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

**Coverage**: 150+ verified European locations across 15+ countries
- 🇩🇰 Denmark: 25+ locations
- 🇳🇴 Norway: 25 locations
- 🇸🇪 Sweden: 29 locations
- 🇫🇮 Finland: 19 locations
- 🇵🇱 Poland: 8 locations
- 🇳🇱 Netherlands: 5 locations
- 🇩🇪 Germany: 10+ major cities/airports
- 🇫🇷 France: 5+ major locations
- 🇬🇧 UK: 10+ major locations
- 🇪🇸 Spain, 🇮🇹 Italy, 🇧🇪 Belgium, 🇪🇪 Estonia, 🇱🇻 Latvia, 🇱🇹 Lithuania

**Geographic Bounds**: 35-71°N, -10-31°E (all of Europe)

**Asset Types**: airport, military, harbor, powerplant, bridge, other

### 8. Duplicate Prevention System (October 2025)

**4-Layer Protection** - Prevents duplicate incidents from appearing in the database and on the map.

#### Layer 1: Database Constraints (PostgreSQL)
**File**: `migrations/016_prevent_duplicate_incidents.sql`
- Prevents duplicate incident storage at database level
- Unique constraint on `content_hash` column (combination of date, location, title, narrative)
- Works even if scraper logic fails
- **Status**: ✅ Active (executed October 9, 2025)
- **Result**: Removed 2 duplicate incidents from database (9 → 7 incidents)

```sql
-- Unique constraint prevents duplicates
ALTER TABLE incidents ADD CONSTRAINT unique_content_hash UNIQUE (content_hash);

-- Automatic hash generation on insert
UPDATE incidents SET content_hash = MD5(
    CONCAT(
        COALESCE(incident_date::text, ''),
        COALESCE(ST_X(location::geometry)::text, ''),
        COALESCE(ST_Y(location::geometry)::text, ''),
        COALESCE(LOWER(title), ''),
        COALESCE(LOWER(narrative), '')
    )
) WHERE content_hash IS NULL;
```

#### Layer 2: API Source Checking
**File**: `frontend/api/ingest.py`
- Checks if source URL already exists before processing incident
- Prevents race conditions from parallel scraper runs
- Returns early if duplicate source detected
- **Status**: ✅ Active (implemented October 9, 2025)

```python
# Check if this source URL already exists
cursor.execute("SELECT COUNT(*) FROM incident_sources WHERE source_url = %s", (source_url,))
if cursor.fetchone()[0] > 0:
    return {"status": "duplicate", "message": "Source already exists"}
```

#### Layer 3: Geographic Consolidation
**File**: `ingestion/consolidator.py`
- Consolidates incidents with same location + time window
- Merges multiple sources for same incident
- Prevents map clutter from duplicate reports
- **Status**: ✅ Active (v2.3.0)

```python
# Deduplication strategy:
# - Location: Rounded to 0.01° (~1.1km)
# - Time: Grouped into 6-hour windows
# - Merges sources, upgrades evidence scores
```

#### Layer 4: Scraper Hash Deduplication
**File**: `ingestion/db_cache.py`
- Hash-based caching of processed incidents
- Prevents re-processing of same content
- Session-level duplicate detection
- **Status**: ✅ Active

**Testing**:
```bash
cd ingestion

# Test consolidation (Layer 3)
python3 test_consolidator.py

# Test geographic filtering
python3 test_geographic_filter.py

# Integration test
python3 ingest.py --test
```

**Current Database State** (October 9, 2025):
- **7 incidents** total (down from 9)
- 2 duplicates removed by migration 016
- All incidents have unique content hashes
- No duplicate source URLs in incident_sources table

### 9. Multi-Layer Defense System (v2.2.0)

**5-Layer Architecture** - Prevents foreign incidents, policy announcements, and defense deployments from appearing on the map.

#### Layer 1: Database Trigger (PostgreSQL)
**Files**: `migrations/014_geographic_validation_trigger.sql` (deprecated), `migrations/015_expand_to_european_coverage.sql` (active)
- Validates EVERY incident BEFORE insertion at database level
- Checks coordinates (35-71°N, -10-31°E for European region)
- Validates title AND narrative for NON-European keywords (Ukraine, Russia, Middle East, Asia, Americas, Africa)
- Works even if scrapers use old code
- **Status**: ✅ Active (European coverage enabled)

#### Layer 2: Python Filters
**File**: `ingestion/utils.py`
- `is_nordic_incident()` - **European** scope validation (function name legacy, but validates European bounds 35-71°N, -10-31°E)
- `is_drone_incident()` - Incident type validation
- Keyword-based filtering for policy, defense, and NON-European incidents
- Enhanced with policy/defense exclusion patterns
- **Status**: ✅ Active (European coverage enabled)

#### Layer 3: AI Verification (NEW v2.2.0)
**Files**: `ingestion/openai_client.py`, `ingestion/ingest.py`
- **OpenRouter/OpenAI integration** for intelligent classification
- Detects: actual incidents vs policy announcements vs defense deployments
- Uses GPT-3.5-turbo (default) or configurable models
- Result caching to minimize API costs (~$0.75-1.50 per 1000 incidents)
- Graceful fallback to Python filters if API fails
- **Test accuracy**: 100% on Copenhagen incidents (4/4 passed)
- **Status**: ✅ Active and tested

```python
# AI verification in ingest.py
ai_verification = openai_client.verify_incident(title, narrative, location)
# Returns: {is_incident: bool, category: str, confidence: float, reasoning: str}

# Blocks:
# - Policy announcements ("drone ban announced")
# - Defense deployments ("troops rushed to defend")
# - Discussion articles ("think piece about drone threats")
```

#### Layer 4: Automated Cleanup Job
**File**: `ingestion/cleanup_foreign_incidents.py`
- Hourly background scan for foreign incidents
- Re-validates with enhanced analyzer
- Auto-removes foreign incidents
- Alerts if >5 incidents found (scraper broken)
- **Status**: ✅ Tested, ready for cron

#### Layer 5: Monitoring Dashboard
**File**: `ingestion/monitoring.py`
- Real-time system health metrics
- Scraper version tracking
- Validation confidence scoring
- Database trigger status
- **Status**: ✅ Working

**Testing All Layers**:
```bash
cd ingestion
export OPENROUTER_API_KEY="sk-or-v1-..."

# Test Layer 3 (AI verification)
python3 test_ai_verification.py

# Run monitoring dashboard (Layer 5)
python3 monitoring.py

# Run cleanup job (Layer 4)
python3 cleanup_foreign_incidents.py
```

---

## Recent Changes & Build Fixes (October 2025)

### Duplicate Prevention System - October 9, 2025
**Migration**: `016_prevent_duplicate_incidents.sql`

**What's New**:
- Database-level duplicate prevention with unique content hash constraint
- API-level source URL checking to prevent race conditions
- 4-layer protection architecture (database, API, consolidation, scraper)
- Automatic cleanup of existing duplicates

**Implementation**:
- Added `content_hash` column with unique constraint to `incidents` table
- Enhanced `frontend/api/ingest.py` with source URL duplicate checking
- Leveraged existing consolidation and scraper deduplication layers
- Migration automatically removed 2 duplicate incidents

**Test Results**:
```
✅ Migration executed successfully
✅ 2 duplicate incidents removed (9 → 7 incidents)
✅ Unique constraint active on content_hash
✅ All 7 remaining incidents have unique hashes
✅ API source checking prevents new duplicates
```

**Database State**:
- Total incidents: 7 (verified unique)
- Duplicates removed: 2 (Kastrup duplicates from October 2-3)
- Source URLs: All unique in incident_sources table

### AI Verification Layer (v2.2.0) - October 6, 2025
**Commit**: `6f863c0`

**What's New**:
- AI-powered incident classification using OpenRouter/OpenAI
- Context-aware detection of policy announcements and defense deployments
- 100% test accuracy on Copenhagen incidents
- OpenRouter integration for flexible model selection (GPT-3.5-turbo default)
- Result caching to minimize costs

**Implementation**:
- Enhanced `openai_client.py` with `verify_incident()` method
- Integrated into `ingest.py` as Layer 3 (after Python filters, before DB trigger)
- Added test suite: `test_ai_verification.py`
- Complete documentation: `AI_VERIFICATION.md`
- Updated scraper version to 2.2.0

**Test Results**:
```
✅ Copenhagen Airport incident → "incident" (0.95 confidence)
✅ Kastrup Airbase incident → "incident" (0.95 confidence)
❌ Policy announcement → BLOCKED as "policy" (1.0 confidence)
❌ Defense deployment → BLOCKED as "defense" (1.0 confidence)
```

**Cost**: ~$0.75-1.50 per 1000 incidents with GPT-3.5-turbo

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

## Troubleshooting Local Development

### Issue: API 404 Errors on Localhost

**Symptoms**:
```
GET /api/incidents?... 404 Not Found
```

**Cause**: Python serverless functions (`frontend/api/*.py`) don't run with `npm run dev`. They require Vercel's runtime environment.

**Solutions**:
1. **Use `vercel dev`** (recommended) - Run from project root: `npx vercel dev`
2. **Test on production** - Live site: https://www.dronemap.cc
3. **Mock API responses** - For pure UI development without backend

### Issue: Chrome DevTools MCP Not Working

**Symptoms**: MCP server fails to start or can't find Chrome canary

**Solution**: The global MCP configuration has been updated to use stable Chrome. If issues persist:
1. Restart VSCode/reload window
2. Check that Chrome (stable) is installed
3. Verify `.claude/.mcp.json` has correct configuration

### Issue: Build Failures (Barrel Loader Errors)

**Symptoms**: 
```
Error: barrel loader failed
Error: TypeScriptTransformer crashed
```

**Solution**:
1. Check all date-fns imports - use specific paths: `'date-fns/format'` not `'date-fns'`
2. Clean rebuild: `rm -rf .next node_modules/.cache && npm run dev`
3. Ensure Next.js 14.2.33+ is installed

### Localhost Testing Summary (October 8, 2025)

**Tested**: localhost:3001 with `npm run dev`
**Results**:
- ✅ Frontend loads correctly (Next.js working)
- ✅ Map renders (Leaflet integration working)
- ✅ UI components functional
- ❌ API endpoints return 404 (Python functions need Vercel)
- ✅ Chrome DevTools MCP configuration fixed

**Recommendations**:
- For full local testing: Use `vercel dev` from project root
- For UI-only development: `npm run dev` is sufficient
- For quick testing: Use production site (www.dronemap.cc)

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

### 7. Geographic Scope Filtering
❌ OLD: Check coords first → return True if Nordic (ignores foreign text)
✅ NEW: Check text for foreign keywords FIRST → then check coords

**Why?** Foreign incidents (e.g., "Russian drone attack over Ukraine") can have Nordic coordinates from context mentions (e.g., "Danish officials in Copenhagen comment"). The filter must check BOTH text AND coordinates.

**Fixed in:** October 2025 - `is_nordic_incident()` now checks text before coordinates + added adjective forms ("russisk", "ukrainsk", "tysk")

### 8. Duplicate Prevention (NEW October 2025)
❌ Same incident submitted multiple times → Database allows duplicates
✅ Content hash + source URL checking → Automatic duplicate prevention

**Why?** Multiple scraper runs or race conditions can create duplicate incidents. The 4-layer system prevents this:
1. Database constraint on content_hash (location + date + title + narrative)
2. API checks source_url before processing
3. Geographic consolidation merges similar incidents
4. Scraper hash cache prevents re-processing

**Result**: Database cleaned from 9 → 7 incidents, all verified unique

---

## Data Quality Principles

1. **Evidence-Based**: Only verified incidents with credible sources
2. **No Speculation**: Factual, neutral reporting only
3. **Single Source of Truth**: Evidence system in `constants/evidence.ts`
4. **Quality > Quantity**: Fewer verified incidents better than many unverified
5. **Multi-Source Verification**: Consolidate sources, upgrade evidence scores
6. **Fake News Filtering**: 6-layer detection with confidence scoring
7. **Geographic Scope**: European coverage (35-71°N, -10-31°E) - filters out non-European events (Ukraine/Russia war zones, Middle East, Asia, Americas, Africa)
8. **Duplicate Prevention**: 4-layer protection prevents duplicate incidents (database constraints, API checking, consolidation, scraper hashing)

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
python3 test_geographic_filter.py     # 9 test cases (Nordic vs foreign, including context mentions)

# Test geographic database
python3 test_geographic_database_simple.py  # 5 validation tests

# Test AI verification (NEW v2.2.0)
export OPENROUTER_API_KEY="sk-or-v1-..."
python3 test_ai_verification.py       # 4 test cases (100% accuracy)

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
- `migrations/017_migration_tracking.sql` - Migration tracking system (NEW October 14, 2025)
- `migrations/016_prevent_duplicate_incidents.sql` - Duplicate prevention (EXECUTED October 9, 2025)
- `migrations/015_expand_to_european_coverage.sql` - European coverage expansion (EXECUTED October 9, 2025)
- `migrations/011_source_verification.sql` - Multi-source schema (PENDING execution)
- `migrations/012_flight_correlation.sql` - OpenSky integration (MISSING - gap in numbering)
- `frontend/api/db.py` - PostGIS query builders
- `frontend/api/ingest.py` - API ingestion with source URL duplicate checking

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
- `OPENROUTER_API_KEY` - OpenRouter API key for AI verification (NEW v2.2.0)
- `OPENROUTER_MODEL` - Model to use (default: `openai/gpt-3.5-turbo`)

**Production Values** (from `.env.production`):
```bash
# ⚠️ SECURITY: Do not expose actual values in documentation
# Configure these in Vercel dashboard: Settings → Environment Variables
DATABASE_URL="<CONFIGURED_IN_VERCEL>"
INGEST_TOKEN="<CONFIGURED_IN_VERCEL>"
OPENROUTER_API_KEY="<CONFIGURED_IN_VERCEL>"
OPENROUTER_MODEL="openai/gpt-3.5-turbo"
```

**Updated**: October 8, 2025 - New OpenRouter API key deployed to production

**Local Development** (`.env.local`):
```bash
# Copy from .env.example and fill in your values
DATABASE_URL="<YOUR_SUPABASE_CONNECTION_STRING>"
INGEST_TOKEN="<YOUR_INGEST_TOKEN>"
OPENROUTER_API_KEY="<YOUR_OPENROUTER_API_KEY>"
OPENROUTER_MODEL="openai/gpt-3.5-turbo"
```

---

## Deployment Workflow

1. **Development**: Make changes, test locally (`npm run dev`)
2. **Testing**: Run test suite (`python3 ingest.py --test`, `npm run build`)
3. **Commit**: Create meaningful commit with context
4. **Push**: `git push origin main`
5. **Vercel**: Auto-deploys to production
6. **Validation**: Check deployment logs, test live site

**Migration Deployment** (with tracking):

**IMPORTANT**: Always check migration tracking before running new migrations (since October 14, 2025)

```bash
# Step 1: Check if migration already executed
psql "postgresql://...@...pooler.supabase.com:5432/postgres" \
  -c "SELECT * FROM public.check_migration_executed('017');"

# Step 2: If NOT executed, run migration
# Test locally first (optional):
psql "..." -f migrations/017_migration_tracking.sql --dry-run

# Step 3: Backup database
# Use Supabase dashboard: Database → Backups

# Step 4: Execute migration
psql "postgresql://...@...pooler.supabase.com:5432/postgres" \
  -f migrations/017_migration_tracking.sql

# Step 5: Verify execution
psql "postgresql://...@...pooler.supabase.com:5432/postgres" \
  -c "SELECT version, description, executed_at FROM public.schema_migrations ORDER BY version;"

# Step 6: Validate application
# - Check schema changes applied correctly
# - Test queries that use new schema
# - Verify frontend still works
```

**Migration Tracking System** (Migration 017):
- Table `public.schema_migrations` tracks all executed migrations
- Prevents duplicate executions
- Documents migration history with git commit SHAs
- Helper functions:
  - `check_migration_executed(version)` - Check before running
  - `record_migration(version, description, ...)` - Record after running

**View Migration History**:
```sql
-- All executed migrations
SELECT version, description, executed_at, executed_by
FROM public.schema_migrations
ORDER BY version;

-- Check for gaps in numbering
-- (useful for identifying missing/duplicate migrations)
WITH numbered AS (
  SELECT version::INTEGER AS num
  FROM public.schema_migrations
  WHERE version ~ '^\d+$'
),
expected AS (
  SELECT generate_series(1, (SELECT MAX(num) FROM numbered)) AS num
)
SELECT e.num AS missing_migration_number
FROM expected e
LEFT JOIN numbered n ON e.num = n.num
WHERE n.num IS NULL
ORDER BY e.num;
```

**Current Migration Status** (October 14, 2025):
- Total migrations: 17 (001-017, with 012 missing)
- Backfilled migrations: 001-016 with git timestamps
- Duplicate files identified: 014 (2 files), 015 (3 files)
- Migration tracking: ✅ Active (since migration 017)

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
- Dashboard: https://vercel.com/arnarssons-projects/dronewatch2.0
- Logs: Available in Vercel dashboard
- Live Site: https://www.dronemap.cc

---

## Comprehensive Code Review - October 14, 2025

### Review Summary

**Status**: Comprehensive full-stack code review completed
**Document**: See `CODE_REVIEW_2025_10_14.md` for complete findings
**Overall Score**: 6.7/10 - Production-ready with critical fixes needed

### Key Findings

**✅ Database Already Consolidated in Supabase**
- All database operations use Supabase (port 6543 transaction pooler)
- No local PostgreSQL dependencies
- Migration tracking needed, but architecture is sound

**🚨 Critical Issues Identified (12 total)**

1. **Schema Constraint Mismatch** - `ingest.py:166` conflicts with database (CRITICAL)
2. **<5% Test Coverage** - No frontend tests, minimal backend tests (CRITICAL)
3. **645-line Map Component** - Performance bottleneck, needs refactoring (HIGH)
4. **Traceback Exposure** - Security risk exposing internal paths (CRITICAL)
5. **Missing Migration Tracking** - No way to know which migrations executed (MEDIUM)
6. **Duplicate Connection Logic** - DRY violation across 3 files (HIGH)
7. **Missing source_url Index** - O(n) lookups on every ingest (HIGH)
8. **N+1 Query Pattern** - Sources aggregation inefficient (MEDIUM)
9. **Debug Logs in Production** - 30+ console.log statements (MEDIUM)
10. **No Error Handling** - Scraper main loop can crash (HIGH)
11. **Config File Too Large** - 930 lines, needs splitting (MEDIUM)
12. **CORS Allows All Origins** - Security risk (MEDIUM)

### Codebase Metrics

- **Total Lines**: ~10,000 (3,500 frontend TypeScript, 6,000 backend Python, 500 SQL)
- **Components**: 14 React components
- **API Endpoints**: 2 (incidents, ingest)
- **Migrations**: 17 files (with duplicates/conflicts)
- **Test Coverage**: <5% (CRITICAL GAP)
- **RSS Sources**: 45+ verified feeds across 15 European countries

### Action Plan & Timeline

**Week 1: Critical Fixes (1 day)**
1. Fix schema constraint mismatch (`ingest.py:166`) - 30 min
2. Add migration tracking system (migration 017) - 1 hour
3. Extract shared connection logic (`db_utils.py`) - 2 hours
4. Remove traceback exposure in errors - 1 hour
5. Add `source_url` index - 15 min

**Week 2-3: High Priority (5 days)**
6. Refactor Map.tsx into modules - 1 day
7. Optimize sources query (filtered CTE) - 2 hours
8. Remove debug logs (add logger utility) - 2 hours
9. Fix CORS policy (whitelist origins) - 30 min
10. Add basic test coverage (API + components) - 3 days

**Month 2: Enhancements (2 weeks)**
11. API documentation (OpenAPI spec) - 1 day
12. Marker diffing for performance - 1 day
13. Component documentation (Storybook) - 2 days
14. Full test coverage (80%+) - 1 week
15. Monitoring dashboard - 2 days

### Estimated Total Effort

- **Critical fixes**: 1 week
- **Testing + performance**: 2-3 weeks
- **Polish + documentation**: 1-2 weeks
- **Total to production-grade**: 4-6 weeks

### Current System Status (October 14, 2025)

**Working Well:**
- ✅ Database architecture (Supabase + PostGIS)
- ✅ Multi-layer defense system (5 validation layers)
- ✅ Evidence scoring system
- ✅ Geographic filtering (European coverage)
- ✅ AI verification (OpenRouter integration)
- ✅ Duplicate prevention (4 layers)
- ✅ Sentry monitoring integration
- ✅ Documentation (CLAUDE.md)

**Needs Attention:**
- ⚠️ Test coverage (<5% - biggest gap)
- ⚠️ Frontend performance (Map component)
- ⚠️ Security hardening (error exposure, CORS)
- ⚠️ Code quality (DRY violations)
- ⚠️ Migration tracking
- ⚠️ API documentation

### Recommendations

**Top 3 Priorities:**
1. **Testing Infrastructure** - Biggest gap, highest risk
2. **Performance Optimization** - Map component + query optimization
3. **Security Hardening** - Remove traceback exposure, fix CORS

**Long-Term Vision:**
Make DroneWatch 2.0 a reference implementation for geospatial incident tracking with:
- Full test coverage (80%+)
- Sub-200ms API response times
- Comprehensive API documentation
- Production-grade error handling
- Monitoring and alerting

### Next Review

**Scheduled**: After Week 1 fixes (estimated October 21, 2025)
**Focus**: Verify critical issues resolved, plan testing infrastructure

---

**Last Updated**: October 14, 2025
**Version**: 2.3.0 (DroneWatch 2.0 - European Coverage Expansion)
**Repository**: https://github.com/Arnarsson/DroneWatch2.0

---

## Recent Changes - European Coverage (v2.3.0) - October 9, 2025

**What's New**:
- 🌍 **European Coverage**: Expanded from Nordic-only (54-71°N, 4-31°E) to ALL of Europe (35-71°N, -10-31°E)
- 🗺️ **Geographic Bounds**: Now includes UK, Ireland, Germany, France, Spain, Italy, Poland, Benelux, Baltics, Mediterranean
- 🚫 **Smart Filtering**: Blocks non-European incidents (Ukraine/Russia war zones, Middle East, Asia, Americas, Africa)
- 📊 **Source Coverage**: 45+ RSS feeds now actively processing incidents from 15+ European countries

**Implementation**:
- Updated `ingestion/utils.py` `is_nordic_incident()` to validate European bounds (35-71°N, -10-31°E)
- Created `migrations/015_expand_to_european_coverage.sql` - database trigger with European bounds
- Updated foreign keyword list to exclude ONLY non-European locations (war zones, other continents)
- Documentation updated to reflect European coverage

**Impact**:
- Expected incidents: 100-200/month (up from 30-100/month Nordic-only)
- Coverage: Norwegian, Swedish, Finnish, German, French, UK, Spanish, Italian, Polish, Baltic, Benelux sources all active
- Previous Nordic sources (Danish police, Twitter, local news) continue working unchanged

---

## Sentry Error Tracking Integration - October 13, 2025

### Setup Complete ✅

**SDK Installed**: `@sentry/nextjs` v10.19.0

**Configuration Files**:
- `instrumentation-client.ts` - Browser-side error capture (CRITICAL: filename must use dash, not dot)
- `sentry.server.config.ts` - Server-side monitoring
- `sentry.edge.config.ts` - Edge runtime monitoring
- `instrumentation.ts` - Runtime hooks loader
- `next.config.js` - withSentryConfig wrapper

**Key Features Enabled**:
- ✅ Browser error capture and exception tracking
- ✅ Performance monitoring with browser tracing
- ✅ Console log capture (log, warn, error levels)
- ✅ Navigation instrumentation via `onRouterTransitionStart`
- ✅ Release tracking using git commit SHA or package version
- ✅ Environment-based configuration (development vs production)

**Instrumented Code**:
- `frontend/hooks/useIncidents.ts` - Wrapped API calls with Sentry.startSpan() for performance tracing
- Tracks: API URL, filters, response status, incident count, errors

**Dashboard Access**:
- URL: https://sentry.io/organizations/svc-cc/projects/dronewatch/
- Org: `svc-cc`
- Project: `dronewatch`

### Build Fixes Applied

**Problem**: Sentry configuration causing TypeScript build failures for 30+ minutes

**Root Causes**:
1. ❌ Wrong filename: `instrumentation.client.ts` (dot) → TypeScript couldn't find it
2. ❌ Invalid options: `autoSessionTracking` and `sessionSampleRate` not valid in browser client config
3. ❌ TypeScript error: `tracePropagationTargets` not in BrowserTracingOptions type

**Solutions Applied** (commits: 0ef4d47, 312e955, 6940d22, 12d1517):
1. ✅ Renamed to `instrumentation-client.ts` (dash) - correct Next.js 13+ App Router convention
2. ✅ Removed invalid session tracking options (only valid in server config)
3. ✅ Simplified browserTracingIntegration() without tracePropagationTargets
4. ✅ Added `onRouterTransitionStart` export for navigation instrumentation
5. ✅ Build now passes successfully (verified with `npm run build`)

**Deployment Status**:
- All failed Vercel deployments resolved
- Latest deployment should complete successfully
- Sentry is capturing events in production

### Using Sentry for Debugging

**Current Issue**: Frontend shows "0 incidents" despite API returning 7 incidents

**Sentry Instrumentation** (already in place):
```typescript
// In frontend/hooks/useIncidents.ts
Sentry.startSpan({
  op: "http.client",
  name: "GET /api/incidents",
}, async (span) => {
  span.setAttribute("api_url", API_URL)
  span.setAttribute("filters", JSON.stringify(filters))
  span.setAttribute("http.status_code", response.status)
  span.setAttribute("incident_count", data.length)

  if (data.length === 0) {
    Sentry.captureMessage('API returned empty array', {
      level: 'warning',
      extra: { url, filters }
    })
  }
})
```

**What to Check in Sentry Dashboard**:
1. **Performance Tab** → Look for `GET /api/incidents` traces
   - Check span attributes: api_url, incident_count, http.status_code
   - Verify if fetch is completing or timing out
2. **Issues Tab** → Filter by `level:warning`
   - Look for "API returned empty array" messages
   - Check error context and extra data
3. **Console Logs** → Search for `[useIncidents]` output
   - See exact API URL being constructed
   - Check if NEXT_PUBLIC_API_URL is set correctly

### Critical Filename Convention

**IMPORTANT**: The client instrumentation file MUST be named with a **dash**, not a dot:
- ✅ Correct: `instrumentation-client.ts`
- ❌ Wrong: `instrumentation.client.ts`

This is the Next.js 13+ App Router convention. Using a dot will cause the SDK to fail silently and build errors in production.

### Configuration Notes

**Release Tracking Strategy**:
```javascript
const RELEASE = process.env.SENTRY_RELEASE ||
  process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA ||
  `dronewatch@${process.env.npm_package_version || '0.1.0'}`;
```

**Environment Variables** (optional, not required for basic functionality):
- `SENTRY_AUTH_TOKEN` - For source map uploads (not set, not required for error capture)
- `SENTRY_RELEASE` - Override default release name
- `NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA` - Auto-set by Vercel for release tracking

### Issue Resolution - October 13, 2025 ✅

**Original Issue**: Frontend showed "0 incidents" and stuck in loading state

**Root Cause**: Build deployment delay - old broken build was cached in browser and CDN. Once the latest build with working Sentry integration deployed, everything resolved automatically.

**Resolution Timeline**:
1. Sentry integration completed with proper instrumentation (commits: 0ef4d47, 312e955, 6940d22, 12d1517)
2. Build fixes applied (renamed `instrumentation-client.ts`, removed invalid options)
3. Vercel deployment completed successfully
4. Browser cache cleared / CDN propagated
5. **Frontend now working** - 7 incidents loading correctly

**Verification**:
- ✅ API endpoint functional - returns 7 incidents
- ✅ Sentry capturing console logs and performance traces
- ✅ Frontend React Query receiving and displaying data
- ✅ Map showing incidents correctly
- ✅ All 7 unique incidents verified in database

**Sentry Traces Confirmed Working**:
- Console breadcrumbs showing API URL construction: `https://www.dronemap.cc/api/incidents?min_evidence=1&country=all&status=all&limit=500`
- Performance spans tracking `GET /api/incidents` with correct attributes
- LCP: 140ms, FCP: 140ms, page load: 290ms (23% faster than average)

**Cleanup Applied**:
- Removed debug console.log statements from `frontend/app/page.tsx`
- Cleaned up verbose logging in `frontend/hooks/useIncidents.ts`
- Kept Sentry instrumentation for ongoing monitoring

**Lessons Learned**:
1. Build deployment can take 5-10 minutes to fully propagate
2. Browser/CDN caching can mask successful fixes
3. Sentry instrumentation invaluable for production debugging
4. Always verify deployment completion before troubleshooting frontend
