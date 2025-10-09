# DroneWatch Data Ingestion

Automated scrapers for collecting drone incident data from Danish sources.

## 📦 Components

### Scrapers
- **Police Scraper** (`scrapers/police_scraper.py`) - RSS feeds from Danish police districts
- **News Scraper** (`scrapers/news_scraper.py`) - DR, TV2, and other Danish media
- **NOTAM Scraper** (coming soon) - Aviation notices

### Main Script
- **Ingester** (`ingest.py`) - Orchestrates all scrapers and sends to API

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd ingestion
cp .env.example .env
# Edit .env with your API credentials

pip install -r requirements.txt
```

### 2. Test Run

```bash
# Test mode - shows data without sending
python ingest.py --test

# Full run
python ingest.py
```

### 3. Schedule with Cron

```bash
# Add to crontab (runs every 15 minutes)
*/15 * * * * cd /path/to/dronewatch/ingestion && python ingest.py
```

## 🤖 GitHub Actions

Automatic ingestion runs every 15 minutes via GitHub Actions.

**Required Secrets:**
- `API_BASE_URL` - Your API endpoint (e.g., https://api.dronewatch.cc)
- `INGEST_TOKEN` - Bearer token for authentication

Set these in: Settings → Secrets → Actions

## 📊 Data Sources

### Police (Evidence Score: 4)
- Nordjyllands Politi
- Københavns Politi
- More districts can be added in `config.py`

### Media (Evidence Score: 2-3)
- DR Nyheder
- TV2 News
- Score increases to 3 if official quotes detected

## 🔍 Deduplication

The ingester maintains a cache (`processed_incidents.json`) to avoid duplicate submissions. Incidents are deduplicated by:
- Title (first 50 chars)
- Time (rounded to hour)
- Location (rounded to 2 decimals)

## 🛠️ Configuration

Edit `config.py` to:
- Add new RSS sources
- Update location databases (airports, harbors)
- Modify keywords for detection
- Adjust evidence scoring rules

## 📝 Manual Ingestion

You can also manually send incidents:

```python
import requests

incident = {
    "title": "Drone sighting at Copenhagen Airport",
    "narrative": "Multiple drones reported near runway",
    "occurred_at": "2025-09-29T14:30:00Z",
    "lat": 55.6180,
    "lon": 12.6476,
    "asset_type": "airport",
    "status": "active",
    "evidence_score": 4,
    "country": "DK",
    "sources": [{
        "source_url": "https://politi.dk/example",
        "source_type": "police",
        "source_quote": "Vi har modtaget anmeldelse om droner..."
    }]
}

response = requests.post(
    "http://localhost:8000/ingest",
    json=incident,
    headers={"Authorization": "Bearer your-token"}
)
```

## 🐛 Troubleshooting

### No incidents found
- Check RSS feeds are accessible
- Verify keywords in `config.py`
- Try with `--test` mode to see raw data

### API errors
- Verify `INGEST_TOKEN` is correct
- Check API is running and accessible
- Look for error details in response

### Duplicate detection too aggressive
- Clear `processed_incidents.json`
- Adjust hash generation in `utils.py`

## 📈 Monitoring

View ingestion status:
- GitHub Actions: Check workflow runs
- API logs: Monitor `/healthz` endpoint
- Database: Query incidents table for recent entries

## 🔒 Security Notes

- Never commit `.env` files
- Use strong, unique tokens
- Rotate tokens periodically
- Monitor for unusual ingestion patterns# Trigger redeploy
