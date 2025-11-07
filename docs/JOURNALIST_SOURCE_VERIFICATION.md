# Source Verification Guide for Journalists

## Overview

DroneWatch ensures **all sources are real, verifiable, and accessible** for journalist verification. Every incident includes clickable source URLs that link directly to the original reporting.

## Source Validation System

### Multi-Layer Validation

1. **API-Level Validation** (`frontend/api/source_validation.py`)
   - All source URLs must be valid HTTP/HTTPS URLs
   - Blocks test/placeholder URLs (test.com, example.com, localhost, etc.)
   - Blocks internal/private IP addresses
   - Validates URL format before database insertion

2. **Database Constraints** (`migrations/020_validate_source_urls.sql`)
   - PostgreSQL CHECK constraints ensure URL format
   - Prevents invalid URLs from being stored
   - Validates both `incident_sources.source_url` and `sources.homepage_url`

3. **Ingestion Filtering** (`ingestion/ingest.py`)
   - Blocks test incidents (keywords: "dronetest", "test incident", "testing drone")
   - Blocks satire domains (40+ blacklisted domains)
   - Validates geographic scope (European coverage only)

4. **Source Verification** (`ingestion/validate_sources.py`)
   - All RSS feeds tested before deployment
   - HTTP status validation (200/304 only)
   - RSS parsing verification
   - Zero tolerance for 404s

## Source Types & Trust Levels

### Level 4 - Official Sources (Highest Trust)
- **Police departments**: Official police RSS feeds and statements
- **Military**: Defense ministry announcements
- **Aviation authorities**: NOTAM systems, civil aviation authorities
- **Trust Weight**: 4.0
- **Auto-Verified**: Yes

### Level 3 - Verified Media
- **Major news outlets**: DR, TV2, NRK, SVT, BBC, etc.
- **Requirements**: Multiple sources with official quotes
- **Trust Weight**: 3.0
- **Auto-Verified**: Yes (if contains official quote)

### Level 2 - Reported
- **Credible news sources**: Single verified news outlet
- **Trust Weight**: 2.0
- **Auto-Verified**: No (requires manual review)

### Level 1 - Unconfirmed
- **Social media**: Low-trust sources
- **Trust Weight**: 1.0
- **Auto-Verified**: No

## How to Verify Sources

### 1. Click Source Badges
- Every incident displays source badges
- Hover to see full URL in tooltip
- Click to open source in new tab
- Full URL displayed in monospace font for easy copying

### 2. Check Source URLs
- All URLs are clickable and open in new tab
- URLs are displayed in full (not shortened)
- Source type indicated by badge color/emoji
- Trust weight visible in source metadata

### 3. Verify Multi-Source Incidents
- Incidents with 2+ sources show "Multi-source verified" badge
- Each source can be clicked independently
- Sources sorted by trust weight (highest first)

## Source Display Features

### Source Badge Component
- **Clickable**: Opens source URL in new tab
- **Tooltip**: Shows full URL on hover
- **Visual Indicators**: 
  - 🚔 Police sources (green)
  - 🛫 NOTAM/Aviation (blue)
  - 📰 Media sources (yellow)
  - 💬 Social media (orange)

### Map Popups
- Full source URLs displayed
- Source titles and quotes shown
- Published dates included
- Trust weight indicators

### List View
- Source badges visible for each incident
- Click to verify each source
- Multi-source incidents clearly marked

## Blocked URL Patterns

The following patterns are **automatically blocked**:

- Test URLs: `test.com`, `example.com`, `localhost`
- Placeholder URLs: Contains "placeholder", "dummy", "fake", "mock"
- Internal IPs: `127.0.0.1`, `192.168.x.x`, `10.x.x.x`
- Invalid schemes: Must be `http://` or `https://`
- Empty URLs: Source URL is required

## Source Verification Checklist

When verifying an incident for reporting:

- [ ] Click all source URLs to verify they're accessible
- [ ] Check source type matches trust level (police = Level 4, etc.)
- [ ] Verify source URLs are from legitimate domains
- [ ] Check published dates match incident timeline
- [ ] For multi-source incidents, verify at least 2 sources independently
- [ ] Note evidence score (1-4) indicates verification level

## Current Source Coverage

### Official Sources (64 total)
- **Police**: 45 official RSS feeds (Nordic + Netherlands)
- **Media**: 21 verified news outlets
- **Aviation**: NOTAM systems and aviation authorities

### Geographic Coverage
- **Nordic**: Denmark, Norway, Sweden, Finland
- **Western Europe**: UK, Ireland, Germany, France, Netherlands
- **Southern Europe**: Spain, Italy
- **Eastern Europe**: Poland, Baltic States
- **Total**: 15+ countries covered

## Reporting Issues

If you find:
- Broken source URLs (404 errors)
- Invalid or inaccessible sources
- Test/placeholder URLs in production
- Sources that don't match incident details

Please report via:
- GitHub Issues: https://github.com/Arnarsson/DroneWatch2.0/issues
- Include: Incident ID, source URL, screenshot

## Technical Details

### Source Storage
- **Table**: `public.incident_sources`
- **URL Field**: `source_url` (required, validated)
- **Constraints**: CHECK constraint validates URL format
- **Uniqueness**: `(incident_id, source_url)` unique constraint

### Source Validation Function
```sql
is_valid_source_url(url text) RETURNS boolean
```
- Validates HTTP/HTTPS scheme
- Checks for test/placeholder patterns
- Ensures domain format is valid
- Blocks internal IPs

### API Validation
```python
validate_all_sources(sources: List[dict]) -> (bool, List[str])
```
- Validates all sources before database insertion
- Returns detailed error messages
- Blocks invalid URLs with clear feedback

## Best Practices for Journalists

1. **Always verify sources independently**
   - Click through to original articles
   - Check publication dates
   - Verify quotes match incident details

2. **Use multi-source incidents when possible**
   - Higher evidence scores (3-4) indicate multiple sources
   - Cross-reference information across sources
   - Look for official quotes from authorities

3. **Check evidence scores**
   - Score 4: Official sources (police/military) - highest reliability
   - Score 3: Verified media with official quotes
   - Score 2: Single credible source - verify independently
   - Score 1: Unconfirmed - use with caution

4. **Verify geographic accuracy**
   - Check coordinates match reported location
   - Verify country code matches source
   - Cross-reference with official maps

## Contact

For questions about source verification:
- **Documentation**: See `docs/MONITORING.md` for technical details
- **Issues**: GitHub Issues for bug reports
- **Source List**: See `ingestion/config.py` for complete source list

---

**Last Updated**: 2025-01-XX  
**Version**: 2.5.0  
**Status**: All sources verified and accessible

