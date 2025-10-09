# AI Verification Layer (Layer 3)

**Version**: 2.2.0
**Status**: ✅ Tested and working
**Last Updated**: October 6, 2025

## Overview

AI-powered intelligent verification layer that uses OpenRouter/OpenAI to classify incidents BEFORE they reach the database. Specifically designed to catch policy announcements and defense deployments that keyword-based filters miss.

## Architecture

```
Scraper → Python Filters (Layer 2) → AI Verification (Layer 3) → Database Trigger (Layer 1) → Database
```

### Layer Integration:
- **Layer 1**: PostgreSQL trigger - Geographic validation at database level
- **Layer 2**: Python filters - `is_drone_incident()`, `is_nordic_incident()` keyword matching
- **Layer 3**: AI verification - Context-aware classification (NEW)
- **Layer 4**: Automated cleanup - Hourly scan and removal
- **Layer 5**: Monitoring dashboard - Real-time metrics

## Features

### Intelligent Classification
- **Actual Incidents**: Drone observations, airspace closures, police investigations
- **Policy Announcements**: Drone bans, regulations, government measures
- **Defense Deployments**: Military assets deployed, security increased
- **Discussion Articles**: Analysis pieces, opinion articles, think pieces

### Technical Features
- **OpenRouter Integration**: Supports switching between free/paid models
- **Result Caching**: Avoids duplicate API calls for similar incidents
- **Graceful Fallback**: Continues with Python filters if API fails
- **Detailed Logging**: AI reasoning logged for debugging

## Setup

### 1. Install Dependencies
```bash
cd ingestion
pip install openai==1.44.0  # Already in requirements.txt
```

### 2. Configure API Key

**Option A: OpenRouter (Recommended)**
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

**Option B: OpenAI**
```bash
export OPENAI_API_KEY="sk-..."
```

### 3. Configure Model (Optional)
```bash
# Default: openai/gpt-3.5-turbo (cheap and reliable)
export OPENROUTER_MODEL="openai/gpt-3.5-turbo"

# Or use other models:
# export OPENROUTER_MODEL="anthropic/claude-3-haiku"
# export OPENROUTER_MODEL="google/gemini-pro"
```

### 4. Test Verification
```bash
cd ingestion
export OPENROUTER_API_KEY="your-key"
python3 test_ai_verification.py
```

Expected output:
```
✅ PASS: Correctly classified as incident (2 tests)
✅ PASS: Correctly classified as policy (1 test)
✅ PASS: Correctly classified as defense (1 test)
Success rate: 100.0%
```

## Production Deployment

### Vercel Environment Variables
Add to your Vercel project:
```
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openai/gpt-3.5-turbo
```

### Local Development
```bash
# Add to .env file
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openai/gpt-3.5-turbo
```

### Cron Job
```bash
# ingestion/run_scraper.sh
#!/bin/bash
export OPENROUTER_API_KEY="sk-or-v1-..."
cd /path/to/ingestion
python3 ingest.py
```

## Cost Analysis

**Using GPT-3.5-turbo via OpenRouter:**
- Cost: ~$0.0015 per verification (~200 tokens)
- With caching: ~50% reduction for duplicate headlines
- Estimated: **$0.75-1.50 per 1000 incidents**
- Very affordable for production use

**Free Models:**
- Free models (google/gemini-flash-1.5:free, meta-llama/llama-3.1-8b-instruct:free) often unavailable
- Recommend using affordable paid models for reliability

## Performance

**Latency:**
- API call: 1-3 seconds per verification
- Cached results: <100ms
- With fallback: Continues immediately if API fails

**Accuracy (Based on Tests):**
- ✅ 100% accuracy on Copenhagen test cases
- ✅ Correctly classified 2 actual incidents
- ✅ Correctly blocked 2 non-incidents (policy + defense)

## Files Modified

### New Files:
- `ingestion/test_ai_verification.py` - Test suite for AI verification
- `ingestion/AI_VERIFICATION.md` - This documentation

### Modified Files:
- `ingestion/openai_client.py` - Added `verify_incident()` method, OpenRouter support
- `ingestion/ingest.py` - Integrated AI verification layer, updated to v2.2.0
- `ingestion/utils.py` - Enhanced policy/defense exclusions

## Verification Workflow

```python
# In ingest.py send_to_api() method:

# 1. Geographic validation (Layer 2)
geo_analysis = analyze_incident_geography(title, narrative, lat, lon)
if not geo_analysis['is_nordic']:
    return False  # Blocked by Layer 2

# 2. AI verification (Layer 3 - NEW)
if OPENROUTER_API_KEY:
    ai_result = openai_client.verify_incident(title, narrative, location)
    if not ai_result['is_incident']:
        logger.warning(f"🚫 BLOCKED (AI): {ai_result['category']}")
        return False  # Blocked by Layer 3

    # Add AI metadata
    incident['ai_category'] = ai_result['category']
    incident['ai_confidence'] = ai_result['confidence']

# 3. Database trigger (Layer 1)
# Send to API → PostgreSQL trigger validates
```

## Monitoring

### Check AI Verification Status
```bash
# View recent incidents with AI metadata
psql "postgresql://..." -c "
SELECT
    title,
    ai_category,
    ai_confidence,
    scraper_version
FROM incidents
WHERE scraper_version = '2.2.0'
ORDER BY ingested_at DESC
LIMIT 10;
"
```

### Dashboard
```bash
cd ingestion
python3 monitoring.py
```

Output includes:
- Total incidents ingested
- Scraper version distribution
- AI verification effectiveness

## Troubleshooting

### AI Verification Not Working
```bash
# Check API key
echo $OPENROUTER_API_KEY

# Test manually
cd ingestion
python3 test_ai_verification.py
```

### High API Costs
```bash
# Switch to cheaper model
export OPENROUTER_MODEL="openai/gpt-3.5-turbo"  # $0.0015/verification

# Or disable AI verification temporarily
unset OPENROUTER_API_KEY
# System will use Python filters only
```

### API Rate Limits
```bash
# Check ingestion logs
tail -f ingestion/logs/*.log | grep "AI verification"

# If rate limited, system falls back to Python filters automatically
```

## Testing Examples

### Test 1: Actual Incident (PASS ✅)
```
Title: Copenhagen Airport - Major Drone Disruption
Result: {
  "is_incident": true,
  "category": "incident",
  "confidence": 0.95,
  "reasoning": "Describes drones causing disruptions at airport"
}
```

### Test 2: Policy Announcement (BLOCKED ❌)
```
Title: Mange ministre kommer til byen - giver nyt droneforbud
Result: {
  "is_incident": false,
  "category": "policy",
  "confidence": 1.0,
  "reasoning": "New drone ban being implemented for EU presidency meeting"
}
```

### Test 3: Defense Deployment (BLOCKED ❌)
```
Title: Frigate, Radars, Troops Rushed To Copenhagen...
Result: {
  "is_incident": false,
  "category": "defense",
  "confidence": 1.0,
  "reasoning": "Military assets being deployed for defense"
}
```

## Benefits

### Before AI Layer:
- ❌ Policy announcements incorrectly appearing on map
- ❌ Defense deployments showing as incidents
- ❌ Keyword filters miss contextual articles

### After AI Layer:
- ✅ Context-aware classification
- ✅ Policy announcements blocked
- ✅ Defense deployments blocked
- ✅ Only actual incidents appear on map
- ✅ Detailed reasoning logged for debugging

## Future Improvements

1. **Add AI metadata to frontend**: Display AI category and confidence in incident popups
2. **Fine-tune prompts**: Improve classification accuracy based on production data
3. **Multi-language support**: Enhanced Danish/Norwegian/Swedish classification
4. **Confidence thresholds**: Auto-flag low-confidence results for manual review
5. **Model comparison**: A/B test different models for best accuracy/cost ratio

---

**Questions?** Check logs in `ingestion/*.log` or run `python3 monitoring.py`

**Version**: 2.2.0
**Last Updated**: October 6, 2025
**Status**: ✅ Production Ready
