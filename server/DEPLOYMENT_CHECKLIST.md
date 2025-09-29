# DroneWatch API - Production Deployment Checklist

## 🚨 Must-Checks (Critical)

### 1. ✅ API Docs Live
```bash
uvicorn app.main:app --reload --port 8000
# Open http://localhost:8000/docs
```

### 2. ✅ Database Connection
- [ ] `DATABASE_URL` uses Supabase **service role** (server only)
- [ ] Public clients must NOT have this key
- [ ] Test connection: `curl http://localhost:8000/healthz`

### 3. ✅ PostGIS Enabled
```sql
-- Run in Supabase SQL editor
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 4. ✅ RLS (Row Level Security)
- [ ] RLS enabled on all tables
- [ ] SELECT policies for anon (read-only)
- [ ] NO write policies for anon
- [ ] Verify: `curl http://localhost:8000/incidents`

### 5. ✅ CORS Configuration
- [ ] Edit `.env`:
```
ALLOWED_ORIGINS=https://dronewatch.cc,https://*.jp.dk,http://localhost:3000
```

### 6. ✅ Ingest Security
- [ ] `INGEST_TOKEN` is set in `.env`
- [ ] Test rejection without token:
```bash
curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{}'
# Should return 401
```

### 7. ✅ Indexes Verified
```sql
-- Check indexes exist
SELECT indexname FROM pg_indexes WHERE tablename = 'incidents';
-- Should see: idx_incidents_gix, idx_incidents_time, idx_incidents_evidence, idx_incidents_status
```

### 8. ✅ Seed Data Works
```bash
curl -s "http://localhost:8000/incidents?min_evidence=2&country=DK&limit=5"
# Should return incidents with expected shape
```

---

## 🎯 Smoke Tests

### Health Check
```bash
curl -s http://localhost:8000/healthz
# Expected: {"ok": true, "service": "dronewatch-api"}
```

### List Incidents (with filters)
```bash
# Recent incidents in Denmark with evidence ≥2
curl -s "http://localhost:8000/incidents?min_evidence=2&country=DK&limit=50"

# With pagination
curl -s "http://localhost:8000/incidents?min_evidence=2&offset=50&limit=50"
```

### BBox Query (Denmark)
```bash
# Denmark bounding box
curl -s "http://localhost:8000/incidents?bbox=7.7,54.4,15.5,57.8&min_evidence=2"
```

### Ingest Test
```bash
export INGEST_TOKEN="your-secret-token-here"

curl -s -X POST http://localhost:8000/ingest \
 -H "Authorization: Bearer $INGEST_TOKEN" \
 -H "Content-Type: application/json" \
 -d '{
   "title": "Test: Drone over Aalborg Airport",
   "narrative": "Police report drones observed near runway.",
   "occurred_at": "2025-09-29T21:44:00Z",
   "lat": 57.0928,
   "lon": 9.8492,
   "asset_type": "airport",
   "status": "active",
   "evidence_score": 4,
   "country": "DK",
   "sources": [{
     "source_url": "https://politi.dk/test",
     "source_type": "police",
     "source_quote": "Der er lørdag aften kl. 21:44..."
   }]
 }'
```

### Embed Snippet
```bash
curl -s "http://localhost:8000/embed/snippet?min_evidence=3&country=DK"
# Should return iframe HTML
```

---

## 🔧 Nice-to-Add (Quality)

### ✅ Pagination
- [x] Added `offset` parameter to `/incidents`
- [x] SQL includes `LIMIT :limit OFFSET :offset`

### ✅ Cache Headers
- [x] Added `Cache-Control: public, max-age=15` to `/incidents`

### ✅ BBox Validation
- [x] Validates numeric ranges (-180/180, -90/90)
- [x] Returns 400 on invalid bbox
- [x] Checks min < max values

### ⬜ Rate Limiting
```nginx
# Add to nginx config
limit_req_zone $binary_remote_addr zone=ingest:10m rate=10r/m;
location /ingest {
    limit_req zone=ingest burst=5;
}
```

### ⬜ Database View for Lat/Lon
```sql
CREATE OR REPLACE VIEW v_incidents AS
SELECT
    id, title, narrative, occurred_at,
    ST_Y(location::geometry) as lat,
    ST_X(location::geometry) as lon,
    asset_type, status, evidence_score, country
FROM incidents;
```

### ⬜ Evidence Constants Table
```sql
CREATE TABLE evidence_levels (
    score INT PRIMARY KEY,
    name TEXT,
    description TEXT
);

INSERT INTO evidence_levels VALUES
(4, 'Official', 'Police press release or NOTAM'),
(3, 'Verified Media', 'Trusted outlet citing officials'),
(2, 'OSINT', 'News without official quote'),
(1, 'Unverified', 'Rumor, no supporting sources');
```

---

## 🚀 Frontend Integration

### Replace Static JSON
```javascript
// Before: fetch('/incidents.json')
// After:
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const params = new URLSearchParams({
  min_evidence: 2,
  country: 'DK',
  limit: 200,
  offset: 0
});

const response = await fetch(`${API_BASE}/incidents?${params}`);
const incidents = await response.json();

// Render on Leaflet
incidents.forEach(incident => {
  L.marker([incident.lat, incident.lon])
    .bindPopup(`
      <h3>${incident.title}</h3>
      <p>Evidence: ${incident.evidence_score}/4</p>
      <p>${incident.narrative || ''}</p>
      ${incident.sources.map(s =>
        `<a href="${s.source_url}" target="_blank">Source</a>`
      ).join(' | ')}
    `)
    .addTo(map);
});
```

---

## 📡 n8n Ingestion Setup

### HTTP Request Node Configuration

**Settings:**
- Method: `POST`
- URL: `https://api.dronewatch.cc/ingest`
- Authentication: `None` (use headers instead)

**Headers:**
```
Authorization: Bearer {{$env.INGEST_TOKEN}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "title": "{{$json.title}}",
  "narrative": "{{$json.description}}",
  "occurred_at": "{{$json.timestamp}}",
  "lat": {{$json.location.lat}},
  "lon": {{$json.location.lon}},
  "asset_type": "{{$json.asset_type}}",
  "status": "active",
  "evidence_score": {{$json.evidence_score}},
  "country": "{{$json.country}}",
  "sources": [
    {
      "source_url": "{{$json.source_url}}",
      "source_type": "{{$json.source_type}}",
      "source_quote": "{{$json.quote}}"
    }
  ]
}
```

---

## 🔒 Security Notes

1. **Never expose** `DATABASE_URL` service role to frontend
2. **Always require** Bearer token for `/ingest`
3. **Validate all inputs** (coordinates, bbox, dates)
4. **Use HTTPS** in production
5. **Set CORS** to specific domains only
6. **Monitor** failed auth attempts on `/ingest`

---

## 🎉 Launch Readiness

- [ ] All must-checks pass
- [ ] Smoke tests successful
- [ ] Frontend connected to API
- [ ] n8n pipeline tested
- [ ] HTTPS certificate ready
- [ ] Monitoring configured
- [ ] Backup strategy defined

**Ready to go live? 🚀**