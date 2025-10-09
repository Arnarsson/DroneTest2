# Product Requirements Document (PRD) — DroneWatch.cc

## 1. Executive Summary

DroneWatch.cc is a **public-facing, map-first tool** for tracking and visualizing verified drone incidents across Denmark and the Nordics, with expansion to Europe.
Its mission: **make drone incidents legible, explorable, and defensible for journalists and the public.**

Core value:
- **Real-time incident mapping** (airports, harbors, critical sites)
- **Evidence-based classification** (police, NOTAMs, media, OSINT)
- **Source transparency** (direct links, supporting quotes)
- **Embeddability** (iframe/JS widget for news sites)

---

## 2. Goals

- Deliver **fast, transparent drone incident intelligence**
- Provide **evidence trails** and confidence levels
- Ensure **sub-2s perceived load time** on mobile
- Make newsroom embedding as simple as `<iframe>` or `<script>`
- Use **open-source software** to maximize trust and adoption

### KPIs

- Map time-to-first-interactive: ≤ 2.0s (4G mid-tier Android)
- % of incidents with direct source links ≥ 95%
- Avg. time from source → DroneWatch incident ≤ 10 minutes
- At least 3 newsroom embeds (pilot partners like JP.dk)

### Non-Goals

- Crowdsource unverified hobbyist drone sightings
- Act as a law enforcement alert system
- Provide predictive analytics (future versions may)

---

## 3. Users & Use Cases

**Primary users:**
- Journalists (embed map in live articles)
- Newsroom editors (use map as context for coverage)
- Public (view incidents, verify with sources)

**Use cases:**
1. A journalist embeds DroneWatch to illustrate a breaking story on a drone sighting at Copenhagen Airport
2. An editor filters incidents by "harbor" to see trends in Nordics
3. A reader taps a map marker → sees source police press release

---

## 4. System Overview

### Architecture

```
[Sources: police, NOTAM, media, Twitter]
   ↓ ingestion (n8n or scripts)
[FastAPI Backend + Postgres/PostGIS (Supabase)]
   ↓ API (/incidents, /embed, /verify)
[Frontend (Next.js + Leaflet.js + Tailwind)]
   ↓
[Embed mode: iframe / JS widget for partners]
```

### Key Modules

- **Data ingestion:** Scraping police sites, fetching NOTAMs, filtering news APIs
- **Verification layer:** Evidence scoring (1–4), rule + AI cross-check, quote extraction
- **Database:** Incident storage with geospatial indexing
- **API (FastAPI):** Interactive docs, query filters, SSE/WebSockets for live updates
- **Frontend:** Leaflet map, filters, evidence overlays, embed mode
- **Admin tools:** Review queue for low-confidence articles

---

## 5. Features & Requirements

### 5.1 Incident Ingestion

- Fetch sources every 5–10 min
- Parse: timestamp, location, source URL, narrative
- Deduplicate incidents by time/location hash
- Verify using rule-based checks + optional AI
- Assign evidence score (1–4)
- Store in DB

### 5.2 Verification

- **Rules:** Whitelist sources, regex for time/location, NOTAM cross-check
- **AI assistance:** Extract entities, quotes. Must return JSON + evidence quotes
- **Human review:** Flag low-confidence (score=1)
- **Output schema (Supabase):**
  ```
  id | title | lat | lon | timestamp | source_url | source_quote | evidence_score | asset_type | status
  ```

### 5.3 API (FastAPI)

- **Endpoints:**
  - `GET /incidents` → list, filter by date, type, evidence
  - `GET /incidents/{id}` → detail view
  - `POST /ingest` (protected) → add new incidents from pipeline
  - `GET /embed` → preconfigured iframe snippet
  - SSE `/updates` → stream live incidents
- **Docs:** Interactive Swagger/Redoc (`/docs`)
- **CORS:** Allow newsroom domains

### 5.4 Frontend

- Built in **Next.js + React + Tailwind**
- Map: Leaflet.js (MapLibre or Esri basemap)
- Features:
  - Cluster markers
  - Filters: time range, evidence strength, type
  - Popup: source links, supporting quote, evidence badge
  - Info modal: "How we verify"
- Embed mode: hide branding, responsive iframe view

### 5.5 Admin / Review

- `/verify` dashboard (restricted)
- Queue of flagged incidents
- Accept, reject, or update evidence score
- Audit log (who verified what, when)

---

## 6. Data Sources

| Source | Access | Update freq | Evidence | Integration |
|--------|--------|-------------|----------|-------------|
| Danish police (politi.dk) | HTML/RSS | real-time | 4 (official) | Scraper → ingest |
| NOTAMs (FAA/Eurocontrol) | API/scrape | minutes | 4 (official) | Parser → ingest |
| Police Twitter (NjylPoliti) | API/bridge | live | 3–4 | RSSBridge → ingest |
| Media (DR, Ritzau, Reuters) | RSS/News API | hourly | 2–3 | n8n → ingest |
| Industry (UnmannedAirspace) | RSS | weekly | 2 | optional |

---

## 7. Evidence Scoring

| Score | Level | Criteria |
|-------|-------|----------|
| 4 | Official | Police press release, NOTAM |
| 3 | Verified media | Trusted outlet citing officials |
| 2 | OSINT | News w/out official quote, or social media by trusted account |
| 1 | Unverified | Rumor, no supporting sources |

---

## 8. Milestones

### Phase 1 (MVP: 4–6 weeks)
- Scaffold FastAPI backend + Supabase schema
- Port ingestion (police + NOTAM)
- Leaflet frontend with mock data
- Embed iframe mode

### Phase 2 (Data Expansion: 6–10 weeks)
- Add Twitter + media ingestion
- Verification with rule-based + AI quotes
- SSE/WebSocket live updates

### Phase 3 (Pilot Launch: 10–12 weeks)
- Polish UX (filters, mobile load)
- Partner embed with newsroom (JP.dk)
- Admin panel for verification

### Phase 4 (EU Expansion: 3–6 months)
- Add SE, NO, FI police feeds + NOTAMs
- Historical import (Airprox, Gatwick, etc.)
- Multi-language support (DA/EN/SV/NO)

---

## 9. Risks & Mitigations

- **Data scarcity** → Mitigate with multi-source OSINT + official cross-checks
- **Misinformation** → Evidence scoring + quote requirement
- **Performance** → Optimize frontend bundle, CDN map tiles
- **Legal reuse** → Use public data, cite sources, avoid copying copyrighted text

---

## 10. Success Criteria

- DroneWatch map loads <2s on mobile
- ≥80% of incidents have evidence score ≥3
- At least one major newsroom partner embeds DroneWatch
- Public GitHub repo with reproducible open-source code