# 🚁 DroneWatch 2.0 - Real-time Drone Incident Tracking

Live map of verified drone incidents across **ALL OF EUROPE** with evidence-based reporting and multi-source verification.

**Live Site**: https://dronewatch.cc → https://www.dronemap.cc
**Repository**: https://github.com/Arnarsson/DroneWatch2.0
**📚 Full Documentation**: [docs/README.md](docs/README.md)

📍 **Geographic Coverage**: 35-71°N, -10-31°E (Nordic + UK + Ireland + Germany + France + Spain + Italy + Poland + Benelux + Baltics)
🔗 **Version**: 2.5.0 (Production Optimized)
📊 **Sources**: 45+ verified RSS feeds from 15+ countries
🔒 **Production Ready**: Security headers, rate limiting, error boundaries, monitoring

---

## Architecture

### Current Stack (Optimized - Sept 2025)
- **Frontend**: Next.js 14 + React + TypeScript + Tailwind CSS
- **Map**: Leaflet.js with marker clustering
- **API**: Vercel Serverless Functions (Python)
- **Database**: Supabase (PostgreSQL + PostGIS)
- **Scraper**: GitHub Actions (runs every 15 minutes)
- **Deployment**: Vercel (auto-deploy from main branch)

### Project Structure
```
/root/repo/
├── frontend/              # Next.js application
│   ├── app/              # Pages and layouts
│   ├── components/       # React components (Map, Filters, etc.)
│   ├── hooks/            # React hooks (useIncidents)
│   ├── api/              # Vercel serverless API routes
│   │   ├── incidents.py  # Main API endpoint
│   │   ├── ingest.py     # Scraper data ingestion
│   │   └── db.py         # Database utilities
│   └── types/            # TypeScript types
├── ingestion/            # Scraper code
│   ├── scrapers/         # Police RSS, news sources
│   └── ingest.py         # Main scraper orchestration
├── .github/workflows/    # GitHub Actions CI/CD
└── migrations/           # Database schema changes
```

---

## Quick Start

### Local Development
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
Required in Vercel:
- `DATABASE_URL` - Supabase connection string (transaction pooler)
- `INGEST_TOKEN` - Secret token for scraper authentication

### Deploy
Push to `main` branch → Vercel auto-deploys

---

## Features

### Current (v1.0)
✅ Real-time incident map with clustering
✅ Filter by country, status, evidence level, date range
✅ Automatic scraping of Danish police + Google News
✅ Evidence-based scoring (1-4 scale)
✅ 16 verified historical incidents (Sept 2025)
✅ Responsive design (mobile + desktop)

### Planned (See FORWARD_PLAN.md)
- Timeline slider to replay incidents
- Analytics dashboard with trends
- User submission form with moderation
- More data sources (Norway, Sweden, NOTAM)
- Public API for researchers

---

## API Endpoints

### GET /api/incidents
Fetch incidents with filtering
```bash
curl "https://www.dronemap.cc/api/incidents?country=all&status=all&min_evidence=1"
```

**Parameters:**
- `country` - Country code (DK, NO, SE, PL, NL) or "all"
- `status` - active, resolved, unconfirmed, or "all"
- `min_evidence` - Minimum evidence score 1-4
- `limit` - Max results (default 200, max 1000)
- `offset` - Pagination offset

### POST /api/ingest
Ingest new incidents (requires Bearer token)
```bash
curl -X POST "https://www.dronemap.cc/api/ingest" \
  -H "Authorization: Bearer $INGEST_TOKEN" \
  -d '{"title":"...", "lat":55.6, "lon":12.6, ...}'
```

---

## Database Schema

### incidents table
- `id` - UUID primary key
- `title` - Incident title
- `narrative` - Detailed description
- `occurred_at` - Timestamp of incident
- `location` - PostGIS geography point
- `country` - ISO country code
- `asset_type` - airport, military, harbor, other
- `status` - active, resolved, unconfirmed
- `evidence_score` - 1 (rumor) to 4 (official report)

### Preventing Duplicates
Run this after cleaning up existing duplicates:
```sql
-- See migrations/001_prevent_duplicates.sql
CREATE UNIQUE INDEX incidents_unique_location_time ON ...
```

---

## Scraper

### How it Works
1. GitHub Actions triggers every 15 minutes
2. Scrapes Danish police RSS + Google News
3. Extracts incident details (location, date, type)
4. Posts to /api/ingest endpoint
5. API validates and inserts to database

### Adding New Sources
Edit `ingestion/scrapers/` and add to `ingestion/ingest.py`

---

## Evidence Scoring

**1 - Social Media / Rumor**: Unverified reports
**2 - OSINT / News**: Verified by multiple news sources
**3 - Official Statement**: Police/military confirmation
**4 - Official Report**: Published incident reports with details

---

## Contributing

### Report an Incident
Use the frontend form (coming soon) or open a GitHub issue with:
- Date, time, location
- Source links
- Description of what happened

### Code Contributions
1. Fork the repo
2. Create feature branch
3. Make changes + test
4. Submit PR to main

---

## Monitoring

### Health Check
```bash
curl https://www.dronemap.cc/api/healthz
```

### Scraper Status
Check GitHub Actions: https://github.com/Arnarsson/DroneWatch2.0/actions

### Production Monitoring
- **Sentry Dashboard**: https://sentry.io/organizations/svc-cc/projects/dronewatch/
- **Monitoring Guide**: [docs/MONITORING.md](docs/MONITORING.md)
- **Production Readiness**: [PRODUCTION_READINESS_REPORT.md](PRODUCTION_READINESS_REPORT.md)

### Production Features
- ✅ Security headers (CSP, HSTS, X-Frame-Options)
- ✅ API rate limiting (100 req/min per IP)
- ✅ Error boundaries with Sentry integration
- ✅ Environment variable validation
- ✅ Optimized Sentry monitoring (10% sample rate)
- ✅ **Source verification system** - All sources are real, verifiable URLs for journalists ([docs/JOURNALIST_SOURCE_VERIFICATION.md](docs/JOURNALIST_SOURCE_VERIFICATION.md))

---

## License
MIT

## Contact
GitHub: [@Arnarsson](https://github.com/Arnarsson)

---

**Last Updated**: 2025-10-07
**Version**: 2.2.0 (DroneWatch 2.0 - AI Verification + Multi-Layer Defense)