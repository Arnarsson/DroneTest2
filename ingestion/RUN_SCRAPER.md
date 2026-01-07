# Quick Start: Run DroneWatch Scraper

**Purpose**: Populate database with European incidents from 77 configured sources

**Expected Result**: 40-90 new incidents from 15 European countries in 5-10 minutes

---

## Prerequisites

1. **Environment Variables** (required):
   ```bash
   export DATABASE_URL="postgresql://postgres:PASSWORD@HOST:6543/postgres"
   export INGEST_TOKEN="your-secure-token-here"
   export OPENROUTER_API_KEY="sk-or-v1-..."
   ```

   **Get from**:
   - DATABASE_URL: Vercel dashboard → Environment Variables
   - INGEST_TOKEN: Generate a secure token (min 16 characters) or get from Vercel environment
   - OPENROUTER_API_KEY: OpenRouter account

   **Generate a secure INGEST_TOKEN**:
   ```bash
   # Option 1: Using openssl (recommended)
   openssl rand -base64 32

   # Option 2: Using Python
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"

   # Option 3: Using /dev/urandom
   head -c 32 /dev/urandom | base64
   ```

   > **Security Note**: The INGEST_TOKEN must be at least 16 characters and match the token
   > configured in your Vercel environment. Never share or commit your token to version control.

2. **Python 3.11+** with virtual environment:
   ```bash
   cd /home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Option 1: Test Run (Recommended First)

**Dry run** - No database writes, validates configuration:

```bash
cd /home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion
source venv/bin/activate

# Set environment variables (see Prerequisites)
export DATABASE_URL="..."
export INGEST_TOKEN="..."
export OPENROUTER_API_KEY="..."

# Test run (no API calls, just validates)
python3 ingest.py --test
```

**Expected Output**:
```
✓ Configuration loaded: 77 sources
✓ Environment variables set
✓ Database connection successful
✓ API endpoint accessible
✓ OpenRouter API key valid
✓ Test mode: No database writes

TEST PASSED - Ready for production run
```

---

## Option 2: Full Scraper Run (Production)

**WARNING**: This will write incidents to production database

```bash
cd /home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion
source venv/bin/activate

# Set environment variables
export DATABASE_URL="..."
export INGEST_TOKEN="..."
export OPENROUTER_API_KEY="..."

# Full ingestion (writes to database)
python3 ingest.py
```

**Expected Output**:
```
Processing 77 sources...
[1/77] Danish Police: 3 articles, 1 incident extracted
[2/77] Norwegian Police Oslo: 5 articles, 2 incidents extracted
[3/77] Swedish Police Stockholm: 8 articles, 3 incidents extracted
...
[77/77] The Local Switzerland: 2 articles, 0 incidents extracted

Summary:
- Sources processed: 77
- Articles scanned: 450-600
- Incidents extracted: 60-110
- Duplicates filtered: 15-25
- Fake news blocked: 5-10
- Non-incidents blocked: 20-30
- Database writes: 40-90 NEW incidents

Total time: 5m 23s
Success rate: 81.2% (56/69 RSS feeds working)

✓ INGESTION COMPLETE
```

---

## Validation After Run

### 1. Check API Response

```bash
curl -s "https://www.dronemap.cc/api/incidents?limit=500" | \
  python3 -c "import sys, json; \
  d=json.load(sys.stdin); \
  print(f'Total incidents: {len(d)}'); \
  countries = {}; \
  for inc in d: countries[inc['country']] = countries.get(inc['country'], 0) + 1; \
  print('By country:', dict(sorted(countries.items())))"
```

**Expected Before**:
```
Total incidents: 8
By country: {'DK': 8}
```

**Expected After**:
```
Total incidents: 55
By country: {'DE': 3, 'DK': 8, 'FI': 7, 'FR': 4, 'GB': 3, 'NL': 2, 'NO': 15, 'SE': 18, ...}
```

### 2. Check Map Display

Visit: https://www.dronemap.cc

**Expected**:
- Markers appear across Europe (not just Denmark)
- Norway: Oslo, Bergen, Stavanger areas
- Sweden: Stockholm, Gothenburg, Malmö areas
- Finland: Helsinki area
- UK: London, Manchester areas
- Germany: Munich, Frankfurt, Berlin areas
- France: Paris area

### 3. Run Database Investigation (Optional)

```bash
cd /home/svenni/Downloads/claudecode-template-plugin/DroneWatch2.0/ingestion
export DATABASE_URL="..."
python3 investigate_incidents.py
```

**Output**:
- Incidents per country
- Source distribution
- Evidence score breakdown
- Date range validation
- Geographic bounds check

---

## Troubleshooting

### Error: DATABASE_URL not set

```bash
ValueError: DATABASE_URL environment variable not configured
```

**Solution**: Export DATABASE_URL before running:
```bash
export DATABASE_URL="postgresql://..."
```

### Error: INGEST_TOKEN invalid

```bash
HTTP 401 Unauthorized: Invalid Bearer token
```

**Solution**: Check INGEST_TOKEN matches the token configured in your Vercel environment:
```bash
export INGEST_TOKEN="your-secure-token-here"  # Must match Vercel env var
```

If you haven't set up INGEST_TOKEN yet, generate a secure one:
```bash
openssl rand -base64 32
```
Then add it to both your local environment and Vercel dashboard.

### Error: OpenRouter API key invalid

```bash
OpenRouter API error: Invalid API key
```

**Solution**: Get new API key from https://openrouter.ai/
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### Error: Norwegian police rate limiting

```bash
HTTP 429 Too Many Requests: politiet.no API
```

**Solution**: This is EXPECTED for Norwegian police sources
- 9/12 Norwegian police feeds return 429 (rate limited)
- This is normal behavior, not an error
- Other 60 sources will still work

### Low incident count (< 20 new incidents)

**Possible Causes**:
1. Sources already scraped recently (check logs for "duplicate" messages)
2. 7-day temporal filter excludes older incidents
3. AI verification blocking false positives

**Solution**: Check scraper logs for details
```bash
grep "BLOCKED" logs/ingestion_*.log
grep "DUPLICATE" logs/ingestion_*.log
```

---

## Expected Results by Source Type

### Police Sources (Trust Weight 4)

**Norwegian Police (12 feeds)**:
- Expected: 10-20 incidents total
- Rate limiting: 9/12 feeds return HTTP 429 (expected)
- Working: Oslo, Øst, Innlandet (3/12)

**Swedish Police (17 feeds)**:
- Expected: 10-20 incidents total
- Working: 17/17 feeds operational (100%)
- Coverage: Stockholm, Skåne, Västra Götaland, etc.

**Finnish Police (3 feeds)**:
- Expected: 5-10 incidents total
- Working: 3/3 feeds operational (100%)
- Coverage: National, Helsinki, Southwestern Finland

**Danish Police (13 feeds)**:
- Expected: 8 incidents (already in database)
- Working: RSS feeds + Twitter feeds

**Dutch Police (2 feeds)**:
- Expected: 1-3 incidents total
- Working: 2/2 feeds operational (100%)
- Coverage: National + urgent messages

### Verified Media Sources (Trust Weight 3)

**UK Media (2 feeds)**:
- BBC UK News + BBC General
- Expected: 2-5 incidents total

**German Media (2 feeds)**:
- Deutsche Welle + The Local Germany
- Expected: 2-5 incidents total

**French Media (3 feeds)**:
- France24 (main + France + Europe)
- Expected: 2-5 incidents total

**European Media (7 feeds)**:
- Belgium, Spain, Italy (2), Poland, Austria, Switzerland
- Expected: 0-7 incidents total (1 per country max)

---

## Automated Scraping (Future - Wave 12)

**Not yet implemented** - Manual execution required for now

**Planned Features**:
- Cron job: Every 6 hours (4x per day)
- Source verification: Monitor 77 feeds for uptime
- Alerting: Email/Slack on critical failures
- Historical tracking: 30-day health trends

**Timeline**: Wave 12 implementation (1-2 weeks)

---

## Cost Estimate

**OpenRouter API (GPT-3.5-turbo)**:
- Cost per incident: $0.75-1.50 per 1000 incidents
- Expected usage: 60-110 incidents per run
- Cost per run: ~$0.05-0.15
- Cost per month (4x daily): ~$6-18

**Database (Supabase)**:
- Included in free tier (up to 500MB)
- Current usage: <1MB for 8 incidents
- Expected usage: ~10MB for 100 incidents

**Total Monthly Cost**: ~$6-20 (OpenRouter API only)

---

## Quick Reference

**Test run**:
```bash
cd ingestion && source venv/bin/activate && python3 ingest.py --test
```

**Production run**:
```bash
cd ingestion && source venv/bin/activate && python3 ingest.py
```

**Validate**:
```bash
curl -s "https://www.dronemap.cc/api/incidents?limit=500" | \
  python3 -c "import sys, json; print(f'Total: {len(json.load(sys.stdin))}')"
```

**Investigate**:
```bash
cd ingestion && python3 investigate_incidents.py
```

---

**Last Updated**: October 14, 2025
**Version**: 2.6.0 (Wave 12 Source Verification Complete)
**Repository**: https://github.com/Arnarsson/DroneWatch2.0
