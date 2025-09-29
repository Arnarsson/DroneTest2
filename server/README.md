# DroneWatch Backend API

FastAPI-based backend for the DroneWatch.cc drone incident tracking system.

## Features

- **RESTful API** with interactive docs (Swagger/ReDoc)
- **PostGIS** geospatial database (Supabase)
- **Evidence scoring** (1-4 scale) with source verification
- **Ingest endpoint** for automated data pipelines
- **Embed support** for newsroom integration
- **CORS-enabled** for frontend consumption

## Setup

### 1. Database (Supabase)

1. Create a new Supabase project
2. Run the schema in SQL editor:
   ```sql
   -- Run /sql/supabase_schema.sql
   ```
3. Optional: Seed demo data with `/sql/seed_demo.sql`

### 2. Environment

```bash
cp .env.example .env
```

Edit `.env`:
- `DATABASE_URL`: Your Supabase connection string (use service role for writes)
- `INGEST_TOKEN`: Secret token for data ingestion
- `ALLOWED_ORIGINS`: CORS-allowed domains

### 3. Install & Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Access docs at http://localhost:8000/docs

## API Endpoints

### Public

- `GET /incidents` - List incidents with filters
- `GET /incidents/{id}` - Get incident details
- `GET /embed/snippet` - Get iframe embed code
- `GET /healthz` - Health check

### Protected

- `POST /ingest` - Add new incident (requires Bearer token)

## Ingestion

Send POST to `/ingest` with Authorization header:

```json
{
  "title": "Drone sighting near Copenhagen Airport",
  "narrative": "Multiple drones reported...",
  "occurred_at": "2025-09-29T21:44:00Z",
  "lat": 55.6180,
  "lon": 12.6476,
  "asset_type": "airport",
  "status": "active",
  "evidence_score": 4,
  "country": "DK",
  "sources": [
    {
      "source_url": "https://politi.dk/...",
      "source_type": "police",
      "source_quote": "Politiet har modtaget anmeldelse..."
    }
  ]
}
```

## Frontend Integration

Replace static `incidents.json` with API call:

```javascript
const response = await fetch('https://api.dronewatch.cc/incidents?min_evidence=2');
const incidents = await response.json();
```

## Deployment

For production:
1. Use proper HTTPS domain
2. Set `ENV=production` in .env
3. Use connection pooling for Postgres
4. Consider adding rate limiting
5. Add monitoring (Sentry, DataDog)