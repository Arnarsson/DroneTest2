# Historical Incidents & Source Verification Plan
**DroneWatch - Data Quality & Historical Coverage Enhancement**

Created: 2025-09-30
Updated: 2025-09-30 (Revised scope: Jan 1, 2025+)
Status: Planning Phase → Implementation Ready

---

## Executive Summary

This plan outlines a comprehensive approach to:
1. **Find and ingest historical drone incidents from January 1, 2025 onwards** from Danish archives and databases
2. **Verify source credibility** before publishing incidents on the website
3. **Implement quality controls** to ensure data accuracy and trustworthiness

**Revised Scope:** Focused on **Jan 1, 2025 - Present** (~10 months, ~150-250 incidents) for faster implementation and easier verification.

---

## 1. Current State Analysis

### 1.1 Existing Data Coverage

**Current Sources (20 total):**
- 12 Danish police district RSS feeds (only recent incidents)
- 8 news media RSS feeds (only recent articles)
- **Limitation:** RSS feeds typically only include last 30-90 days

**Database Schema Status:**
- ✅ `verification_status` field exists (pending/verified/rejected/auto_verified)
- ✅ `evidence_score` field (1-4 scale)
- ✅ `admin_notes` and `verified_by` fields for manual review
- ✅ Deduplication via `content_hash` and spatial/temporal constraints

**Current Verification:**
- ❌ No manual verification workflow
- ❌ No source credibility checking
- ❌ Auto-publishes all scraped incidents immediately
- ❌ No admin interface for review/approval

### 1.2 Data Quality Concerns

**High Risk Areas:**
1. **False Positives:** News about drone deliveries, regulations, or commercial use mistaken for incidents
2. **Unverified Reports:** Social media or unconfirmed sightings
3. **Duplicate Events:** Same incident reported by multiple sources with different details
4. **Location Inaccuracy:** Falls back to Copenhagen center (55.6761, 12.5683) when location unknown
5. **Date Ambiguity:** Published date vs actual incident date confusion

---

## 2. Historical Data Sources Strategy

### 2.1 Danish Archives & Databases

#### Priority 1: Official Government Sources

**Danish Aviation Authority (Trafikstyrelsen)**
- **URL:** https://www.trafikstyrelsen.dk
- **Coverage:** Regulatory violations, airport incidents, NOTAM archives
- **Method:** Web scraping + FOIA requests for incident reports
- **Trust Level:** 4/4 (official)
- **Historical Coverage:** Jan 1, 2025 - present (current year focus)

**Danish Defense (Forsvaret)**
- **URL:** https://www.forsvaret.dk
- **Coverage:** Military base incidents, airspace violations
- **Method:** Press releases archive, FOIA requests
- **Trust Level:** 4/4 (official)
- **Historical Coverage:** Jan 1, 2025 - present

**NOTAM Archive**
- **URL:** https://aim.naviair.dk (Danish AIS)
- **Coverage:** Flight restrictions, airspace closures due to drones
- **Method:** API access if available, otherwise manual extraction
- **Trust Level:** 4/4 (official aviation)
- **Historical Coverage:** Jan 1, 2025 - present

#### Priority 2: Police Archives

**Danish Police Archive Search**
- **Method:** Deep scraping of police district news archives (beyond RSS)
- **Coverage:** Historical press releases going back 5+ years
- **Implementation:**
  ```python
  # Scrape archive pages with pagination
  # Example: https://politi.dk/koebenhavns-politi/nyhedsliste?page=1
  # Parse older articles not in RSS feed
  ```
- **Trust Level:** 4/4 (official)
- **Historical Coverage:** Jan 1, 2025 - present

#### Priority 3: News Media Archives

**Major Danish Newspapers**
- **DR Nyheder Archive:** https://www.dr.dk/nyheder/soeg
- **TV2 Archive:** Search function for historical articles
- **Berlingske Archive:** Premium access may be required
- **Jyllands-Posten Archive:** Historical article search
- **Politiken Archive:** Digital archive search

**Implementation:**
- Use newspaper search APIs where available
- Implement targeted keyword searches: "drone + lufthavn", "drone + politi", etc.
- Filter by date range: 2015-present
- **Trust Level:** 3/4 (reputable media)

#### Priority 4: Academic & Research Sources

**Danish Aviation Research**
- Universities with aviation security programs
- Research papers on drone incidents in Nordic countries
- Civil aviation authority reports and statistics

**International Databases**
- **EASA (European Aviation Safety Agency):** Incident reports involving Denmark
- **FAA ASRS (if applicable):** Any reports involving Danish airspace
- **Aviation Safety Network:** Historical drone-related incidents

### 2.2 Search Keywords & Filters

**Danish Keywords:**
```
"drone + lufthavn"
"drone + politi"
"dron + kastrup"
"ubemannede luftfartøj"
"UAV + hændelse"
"drone + flyveplads"
"drone + sikkerhed"
"drone + militær"
```

**English Keywords:**
```
"drone incident Denmark"
"UAV Denmark airport"
"unmanned aircraft Copenhagen"
```

**Date Range:** 2025-01-01 to present (10 months of data)

---

## 3. Source Verification Framework

### 3.1 Credibility Scoring System

**Trust Levels (1-4):**

**Level 4 - Official/Authoritative**
- Government agencies (police, aviation authority, military)
- NOTAM/aviation notices
- Court records
- **Auto-verification:** Yes (incidents from these sources auto-approve)

**Level 3 - Reputable Media**
- Major newspapers (DR, TV2, Berlingske, Jyllands-Posten, Politiken)
- International news agencies (Reuters, AFP)
- **Verification:** Auto-approve if has official quote, otherwise manual review

**Level 2 - Regional/Secondary Media**
- Regional TV2 stations
- Local newspapers
- Online news portals
- **Verification:** Manual review required

**Level 1 - Unverified Sources**
- Social media
- Blogs
- Unconfirmed reports
- **Verification:** Manual review required + require corroboration from Level 3+ source

### 3.2 Verification Checklist

**Before Publishing an Incident:**

1. ✅ **Source Verification**
   - Is source in trusted sources list?
   - Can we verify source URL is legitimate?
   - Does article contain official quotes/statements?

2. ✅ **Content Verification**
   - Is this actually an incident (not news about regulations/deliveries)?
   - Is location clearly specified?
   - Is date/time of incident clear (not just publication date)?

3. ✅ **Corroboration Check**
   - Are there multiple sources reporting this incident?
   - Do police/official sources confirm it?
   - Does location/timing match NOTAM records?

4. ✅ **Duplicate Detection**
   - Check against existing incidents by location + time
   - Check content_hash
   - Manual review for similar titles/narratives

5. ✅ **Data Quality**
   - Location accuracy (not defaulting to Copenhagen center)
   - Complete narrative available
   - Evidence score appropriate for source

### 3.3 Verification Workflow States

**Database Schema (Already Exists):**
```sql
verification_status: 'pending' | 'verified' | 'rejected' | 'auto_verified'
```

**Workflow:**
```
1. Ingestion → verification_status = 'pending'
   ├─ Trust Level 4 → 'auto_verified' → Publish immediately
   ├─ Trust Level 3 + official quote → 'auto_verified' → Publish immediately
   └─ All others → 'pending' → Manual review queue

2. Manual Review
   ├─ Approve → verification_status = 'verified' → Publish
   ├─ Reject → verification_status = 'rejected' → Hide from public
   └─ Request more info → Add admin_notes, keep 'pending'

3. Published Incidents
   - Can be flagged for re-review
   - Can be marked as 'false_positive' status
```

---

## 4. Implementation Plan

### Phase 1: Verification Infrastructure (Week 1-2)

**4.1 Database Enhancements**

```sql
-- Migration: 003_verification_workflow.sql

-- Add verification fields if not exist
ALTER TABLE public.incidents
  ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(3,2) DEFAULT 0.5,
  ADD COLUMN IF NOT EXISTS requires_review BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS review_notes JSONB DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS last_reviewed_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0;

-- Create review queue table
CREATE TABLE IF NOT EXISTS public.incident_review_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id UUID NOT NULL REFERENCES public.incidents(id) ON DELETE CASCADE,
  priority INTEGER DEFAULT 3, -- 1=high, 2=medium, 3=low
  reason TEXT, -- Why flagged for review
  assigned_to TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at TIMESTAMPTZ,
  UNIQUE(incident_id)
);

-- Create verification audit log
CREATE TABLE IF NOT EXISTS public.verification_audit (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id UUID NOT NULL REFERENCES public.incidents(id),
  action TEXT NOT NULL, -- 'verified', 'rejected', 'flagged', 'edited'
  performed_by TEXT NOT NULL,
  previous_status TEXT,
  new_status TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- View for review queue with incident details
CREATE OR REPLACE VIEW public.v_review_queue AS
SELECT
  rq.*,
  i.title,
  i.occurred_at,
  i.evidence_score,
  i.verification_status,
  i.country,
  ST_Y(i.location::geometry) AS lat,
  ST_X(i.location::geometry) AS lon,
  (SELECT COUNT(*) FROM public.incident_sources WHERE incident_id = i.id) as source_count
FROM public.incident_review_queue rq
JOIN public.incidents i ON rq.incident_id = i.id
WHERE rq.reviewed_at IS NULL
ORDER BY rq.priority ASC, rq.created_at ASC;
```

**4.2 Auto-Verification Logic**

```python
# ingestion/verification.py

def should_auto_verify(incident: Dict, source: Dict) -> bool:
    """
    Determine if incident should be auto-verified
    """
    trust_weight = source.get('trust_weight', 1)

    # Level 4 sources always auto-verify
    if trust_weight == 4:
        return True

    # Level 3 with official quotes auto-verify
    if trust_weight == 3:
        narrative = incident.get('narrative', '').lower()
        has_official_quote = any(word in narrative for word in [
            'politi', 'police', 'luftfart', 'forsvar',
            'myndighed', 'authority', 'bekræfter', 'confirms'
        ])
        if has_official_quote:
            return True

    return False

def calculate_confidence_score(incident: Dict, sources: List[Dict]) -> float:
    """
    Calculate confidence score 0.0-1.0 based on multiple factors
    """
    score = 0.0

    # Source trust (40%)
    max_trust = max([s.get('trust_weight', 1) for s in sources])
    score += (max_trust / 4.0) * 0.4

    # Multiple sources (20%)
    source_bonus = min(len(sources) / 3.0, 1.0) * 0.2
    score += source_bonus

    # Location specificity (20%)
    if incident.get('asset_type') != 'other':
        score += 0.2
    elif incident.get('location_name'):
        score += 0.1

    # Has quotes (10%)
    if incident.get('sources', [{}])[0].get('source_quote'):
        score += 0.1

    # Complete narrative (10%)
    if len(incident.get('narrative', '')) > 100:
        score += 0.1

    return min(score, 1.0)
```

### Phase 2: Historical Data Scrapers (Week 2-3)

**4.3 Police Archive Scraper**

```python
# ingestion/scrapers/police_archive_scraper.py

class PoliceArchiveScraper:
    """
    Scrape historical police news beyond RSS feed
    """

    def fetch_archive_pages(self, source_key: str, start_year: int = 2018):
        """
        Paginate through archive pages
        Example: https://politi.dk/koebenhavns-politi/nyhedsliste?page=1
        """
        for year in range(start_year, datetime.now().year + 1):
            for page in range(1, 100):  # Adjust max pages as needed
                # Fetch page
                # Parse articles
                # Check for drone keywords
                # Extract incidents
                pass

    def is_historical_article(self, article_date: datetime) -> bool:
        """Check if article is older than current RSS feed coverage"""
        cutoff = datetime.now() - timedelta(days=90)
        return article_date < cutoff
```

**4.4 News Archive Searcher**

```python
# ingestion/scrapers/news_archive_scraper.py

class NewsArchiveScraper:
    """
    Search news archives for historical incidents
    """

    SEARCH_KEYWORDS = [
        "drone lufthavn",
        "drone politi",
        "dron kastrup",
        # ... more keywords
    ]

    def search_dr_archive(self, keyword: str, start_date: str, end_date: str):
        """
        Search DR Nyheder archive
        URL: https://www.dr.dk/nyheder/soeg?query={keyword}&from={date}
        """
        pass

    def search_tv2_archive(self, keyword: str, start_date: str, end_date: str):
        """
        Search TV2 archive
        """
        pass
```

### Phase 3: Admin Interface (Week 3-4)

**4.5 API Endpoints for Verification**

```python
# frontend/api/admin/review_queue.py

@require_admin_auth
def get_review_queue(request):
    """
    GET /api/admin/review-queue
    Returns incidents pending review
    """
    query = """
    SELECT * FROM public.v_review_queue
    LIMIT 50
    """
    # Return incidents for review

@require_admin_auth
def verify_incident(request):
    """
    POST /api/admin/verify-incident
    Body: {
      "incident_id": "uuid",
      "action": "verify" | "reject",
      "notes": "string",
      "verified_by": "string"
    }
    """
    # Update incident verification_status
    # Log to verification_audit
    # Remove from review queue

@require_admin_auth
def edit_incident(request):
    """
    PUT /api/admin/incidents/{id}
    Update incident details after review
    """
    # Update incident
    # Log changes to verification_audit
```

**4.6 Simple Admin Dashboard**

Create a basic admin interface at `/admin/review`:
- List of incidents in review queue
- Show incident details, sources, location on map
- Approve/Reject buttons
- Edit form for corrections
- Batch operations

### Phase 4: Historical Data Import (Week 4-6)

**4.7 Import Pipeline**

```python
# scripts/import_historical.py

class HistoricalDataImporter:
    """
    Import historical incidents with verification
    """

    def import_from_archive(self, source_type: str, start_date: str):
        """
        Main import function
        """
        incidents = []

        if source_type == 'police_archive':
            scraper = PoliceArchiveScraper()
            incidents = scraper.fetch_all_historical()

        elif source_type == 'news_archive':
            scraper = NewsArchiveScraper()
            incidents = scraper.search_all_keywords(start_date)

        # Process each incident
        for incident in incidents:
            # Calculate confidence score
            confidence = calculate_confidence_score(incident, incident['sources'])
            incident['confidence_score'] = confidence

            # Determine if auto-verify
            auto_verify = should_auto_verify(incident, incident['sources'][0])

            if auto_verify:
                incident['verification_status'] = 'auto_verified'
            else:
                incident['verification_status'] = 'pending'
                # Add to review queue

            # Send to ingest API
            self.ingest_incident(incident)
```

**4.8 Batch Processing with Rate Limiting**

```python
# Prevent overwhelming the system
BATCH_SIZE = 50
DELAY_BETWEEN_BATCHES = 60  # seconds

for batch in chunks(historical_incidents, BATCH_SIZE):
    process_batch(batch)
    time.sleep(DELAY_BETWEEN_BATCHES)
```

---

## 5. Data Quality Controls

### 5.1 Pre-Publication Filters

**API Modification:**
```python
# frontend/api/incidents.py

def fetch_incidents(filters):
    """
    Only return verified or auto-verified incidents to public
    """
    query = """
    SELECT * FROM public.incidents
    WHERE verification_status IN ('verified', 'auto_verified')
    AND status = 'active'
    -- ... other filters
    """
```

### 5.2 Monitoring & Alerts

**Metrics to Track:**
- Incidents in review queue (alert if > 100)
- Average time to review (target < 48 hours)
- Auto-verification rate
- Rejection rate by source
- False positive reports from users

### 5.3 User Reporting

**Add "Report Issue" button:**
- Users can flag incorrect incidents
- Creates entry in review queue with priority=1
- Email notification to admin

---

## 6. Timeline & Resources

### Week 1-2: Infrastructure
- ✅ Database migration 003_verification_workflow.sql
- ✅ Verification logic in Python
- ✅ Update ingester to use verification

### Week 2-3: Historical Scrapers
- ✅ Police archive scraper
- ✅ News archive searcher
- ✅ Test on small date range

### Week 3-4: Admin Interface
- ✅ Review queue API endpoints
- ✅ Basic admin dashboard
- ✅ Authentication for admin routes

### Week 4-6: Historical Import
- ✅ Run historical scrapers
- ✅ Import incidents to review queue
- ✅ Manual review and verification
- ✅ Publish verified incidents

### Week 6+: Ongoing
- Monitor data quality
- Refine auto-verification rules
- Expand to additional sources
- Community moderation features

---

## 7. Success Metrics

**Data Coverage:**
- Target: 150-250 historical incidents from Jan 1, 2025-present
- Geographic coverage: All major Danish airports represented
- Temporal coverage: No gaps > 2 months

**Data Quality:**
- Verification rate: >95% of published incidents verified
- False positive rate: <2%
- Location accuracy: <5% defaulting to Copenhagen center
- Duplicate rate: <1%

**Operational:**
- Review queue processing time: <48 hours average
- User reports handled: <24 hours response time
- System uptime: >99%

---

## 8. Security & Privacy Considerations

**Authentication:**
- Admin routes require authentication
- Use environment variable for admin tokens
- Log all admin actions to audit trail

**Data Privacy:**
- No personal information stored
- Public incidents only
- Comply with GDPR for any user data

**Rate Limiting:**
- Prevent abuse of admin APIs
- Throttle historical scraping to avoid overloading sources

---

## 9. Future Enhancements

**Phase 2 Features:**
- **Community Verification:** Allow trusted users to help verify incidents
- **ML Classification:** Train model to auto-classify incident types
- **Severity Scoring:** Automatic risk/severity assessment
- **Cross-referencing:** Auto-match incidents with NOTAM, weather data
- **Geocoding API:** Use Nominatim for better location extraction
- **Multi-language:** Translate and normalize data from international sources

---

## 10. Next Steps

**Immediate Actions:**
1. Review and approve this plan
2. Run database migration 003_verification_workflow.sql
3. Implement auto-verification logic in ingester
4. Create admin authentication system
5. Build basic review queue API
6. Test with small historical dataset (1 month of police archives)
7. Scale up to full historical import

**Questions to Resolve:**
- Who will perform manual review? (You? Trusted users?)
- What authentication method for admin? (Password? GitHub OAuth?)
- Should we build full admin dashboard or use database tool initially?
- Priority order for historical sources? (Police first? News first?)

---

**Document Version:** 1.0
**Last Updated:** 2025-09-30
**Author:** Terry (Terragon Labs AI Agent)