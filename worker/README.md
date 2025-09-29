# DroneWatch Ingestion Worker

Production-ready Python worker for automated drone incident collection.

## 🚀 Features

- **APScheduler** for reliable task scheduling
- **Strict verification** to prevent hallucinations
- **Quote extraction** for evidence
- **Deduplication** with content hashing
- **Multi-source support** (RSS, Police, NOTAMs)
- **Geographic detection** for Nordic locations

## 📦 Quick Start

### Local Development

```bash
cd worker
cp .env.example .env
# Edit .env with your credentials

pip install -r requirements.txt
python ingest_worker.py
```

### Docker

```bash
docker build -f Dockerfile.worker -t dronewatch-worker .
docker run --env-file worker/.env dronewatch-worker
```

### Production (Systemd)

```bash
sudo ./ops/install_worker.sh
sudo nano /opt/dronewatch/worker/.env  # Add credentials
sudo systemctl start dronewatch-worker
sudo systemctl enable dronewatch-worker
```

## 🔧 Configuration

Edit `.env`:

```env
# API endpoint
INGEST_URL=https://api.dronewatch.cc/ingest
INGEST_TOKEN=your-secret-token

# Schedule (minutes)
SCHED_RSS=10          # Check RSS every 10 min
SCHED_POLICE_HTML=5   # Check police every 5 min
SCHED_NOTAM=15        # Check NOTAMs every 15 min

# Sources
RSS_FEEDS=https://www.dr.dk/nyheder/service/feeds/allenyheder
POLICE_HTML=https://politi.dk/nordjyllands-politi/nyhedsliste
TRUSTED=politi.dk,reuters.com,dr.dk
```

## 📊 How It Works

1. **Fetches** from configured sources on schedule
2. **Extracts** incidents with strict verification
3. **Requires quotes** to prevent hallucinations
4. **Geolocates** using Nordic location database
5. **Deduplicates** using content hashing
6. **Posts** to API with evidence scoring

## 🔍 Evidence Scoring

- **4 (Official)**: Police, NOTAMs
- **3 (Verified)**: Trusted media domains
- **2 (OSINT)**: Other media with quotes
- **1 (Unverified)**: No quotes (rejected)

## 🗺️ Supported Locations

### Airports
- Denmark: Copenhagen, Aalborg, Billund
- Norway: Oslo, Bergen
- Sweden: Stockholm Arlanda, Gothenburg
- Finland: Helsinki-Vantaa

### Harbors
- Major ports in Copenhagen, Aarhus, Oslo, Stockholm, etc.

## 📝 Logs

### Local
```bash
# Runs with stdout logging
python ingest_worker.py
```

### Systemd
```bash
sudo journalctl -u dronewatch-worker -f
```

### Docker
```bash
docker logs -f <container-id>
```

## 🧪 Testing

```bash
# Test extraction without posting
python -c "
from worker.sources.dk_police import fetch_police_news
items = fetch_police_news('https://politi.dk/nordjyllands-politi/nyhedsliste')
print(items)
"
```

## 🔒 Security

- Never commit `.env` files
- Rotate `INGEST_TOKEN` regularly
- Use HTTPS for `INGEST_URL`
- Run as non-root user (`dronewatch`)
- Validate all extracted data

## 🐛 Troubleshooting

### No incidents found
- Check RSS feeds are accessible
- Verify keywords match content
- Review logs for extraction errors

### API errors
- Verify `INGEST_TOKEN` is correct
- Check API is running
- Review response in logs

### Duplicate detection
- Clear `dedupe_cache.json` if needed
- Adjust hashing in `utils/dedupe.py`

## 📈 Monitoring

Check ingestion stats:
```sql
-- In Supabase
SELECT
  DATE(created_at) as day,
  COUNT(*) as incidents,
  AVG(evidence_score) as avg_evidence
FROM incidents
GROUP BY DATE(created_at)
ORDER BY day DESC;
```

## 🚁 Adding Sources

1. Create scraper in `sources/`
2. Add to `ingest_worker.py`
3. Schedule with APScheduler
4. Test extraction quality

Example:
```python
# sources/no_police.py
def fetch_norwegian_police():
    # Scrape Norwegian police feeds
    pass
```