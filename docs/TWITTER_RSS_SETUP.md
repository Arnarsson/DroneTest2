# Twitter/X RSS Feed Setup Guide - RSS.app

## ⚠️ CRITICAL BLOCKER

This document explains how to generate RSS feeds for Danish police Twitter accounts using RSS.app. **This is a manual step that must be completed before the Twitter scraper can work.**

---

## Why RSS.app?

- **Nitter**: Discontinued February 2024 ❌
- **TwitRSS.me**: Currently offline (shows "Coming...soon") ❌
- **RSS.app**: Working as of October 2025 ✅
- **Direct X API**: Requires paid access ($100+/month) 💰

---

## Setup Instructions

### Step 1: Create RSS.app Account

1. Visit: https://rss.app/
2. Click "Sign Up" or "Get Started"
3. Create free account (no credit card required)
4. Verify email address

### Step 2: Generate First Test Feed (@KobenhavnPoliti)

1. Log into RSS.app dashboard
2. Click "Create New Feed" or "+"
3. Select **"Twitter/X"** as source type
4. Enter Twitter handle: `KobenhavnPoliti` (without @)
5. Configure feed settings:
   - **Name**: Copenhagen Police - Denmark
   - **Keywords** (optional): drone, dron, uav, lufthavn
   - **Language**: Danish (da)
6. Click "Create Feed"
7. **SAVE THE RSS FEED URL** - looks like:
   - Format 1: `https://rss.app/feeds/[feed-id]/KobenhavnPoliti.xml`
   - Format 2: `https://api.rss.app/v1/feeds/[feed-id].xml`
   - Format 3: Custom format (document what you see)

### Step 3: Test Feed URL

```bash
# Test that feed works
curl -I "YOUR_RSS_FEED_URL_HERE"

# Should return: HTTP 200 OK
# Content-Type: application/xml or application/rss+xml
```

### Step 4: Document Feed URL Format

**Please provide:**
1. ✅ The exact RSS feed URL for @KobenhavnPoliti
2. ✅ The URL format/pattern RSS.app uses
3. ✅ Any API keys or authentication required
4. ✅ Feed update frequency (how often RSS.app refreshes)
5. ✅ Rate limits (requests per hour/day)

**Example:**
```
Feed URL: https://rss.app/feeds/abc123xyz/KobenhavnPoliti.xml
Pattern: https://rss.app/feeds/{feed_id}/{handle}.xml
Auth: None required (public feed)
Update: Every 15 minutes
Limit: 100 requests/hour on free tier
```

### Step 5: Generate Feeds for Priority Accounts

Generate RSS feeds for these **high-priority** accounts first:

1. **@KobenhavnPoliti** (Copenhagen) - Already done ✅
2. **@Rigspoliti** (National Police)
3. **@NjylPoliti** (North Jutland - Aalborg Airport)
4. **@OjylPoliti** (East Jutland - Aarhus)
5. **@MVJPoliti** (Central/West Jutland - Billund Airport)

Save all 5 RSS feed URLs.

---

## Alternative: RSS.app API Automation

If RSS.app provides an API, we can automate feed generation:

### Check for API Access

1. In RSS.app dashboard, look for:
   - "API" section
   - "Developer" settings
   - "API Keys" or "Access Tokens"

2. If API exists, document:
   - API endpoint: `https://api.rss.app/v1/...`
   - Authentication method: Bearer token, API key, etc.
   - Endpoint to create feed: `POST /feeds`
   - Required parameters: `handle`, `source_type`, etc.

### API Documentation

If API exists, I can write automation script:

```python
# Example automation (IF RSS.app has API)
import requests

def create_twitter_rss_feed(handle, api_key):
    response = requests.post(
        'https://api.rss.app/v1/feeds',
        headers={'Authorization': f'Bearer {api_key}'},
        json={
            'source': 'twitter',
            'handle': handle,
            'keywords': ['drone', 'dron', 'uav']
        }
    )
    return response.json()['feed_url']
```

---

## RSS.app Free Tier Limitations

Check these limits in your account:

- **Max feeds**: ? (usually 5-10 on free tier)
- **Requests/hour**: ? (usually 100-500)
- **Feed items**: ? (usually last 50-100 tweets)
- **Update frequency**: ? (usually 15-30 minutes)

If free tier is too limited:

### Upgrade Options

**RSS.app Pricing** (check current rates):
- Free: 5 feeds, 100 requests/hour
- Basic: $9/mo - 20 feeds, 500 requests/hour
- Pro: $29/mo - 100 feeds, unlimited requests

**Cost-Benefit Analysis**:
- 15 police accounts = need at least 15 feeds
- Estimated: **Basic ($9/mo) or Pro ($29/mo)** tier required

---

## What I Need From You

Please provide:

### Required (Minimum to start)
1. ✅ RSS feed URL for @KobenhavnPoliti
2. ✅ URL pattern/format

### Helpful (For automation)
3. ✅ All 15 feed URLs (if you create them manually)
4. ✅ RSS.app API key (if automation possible)
5. ✅ Rate limits and quotas

### Nice to Have
6. Screenshot of RSS.app dashboard
7. Subscription tier you're using (Free/Basic/Pro)

---

## Once You Provide Feed URLs

I will:
1. ✅ Add all 15 accounts to `config.py` with your RSS URLs
2. ✅ Create `twitter_scraper.py` to parse feeds
3. ✅ Integrate into `ingest.py` pipeline
4. ✅ Test with Copenhagen Police first
5. ✅ Scale to all 15 accounts
6. ✅ Handle rate limiting and errors gracefully

---

## Testing Without RSS.app (Temporary)

If RSS.app setup takes time, I can:

1. **Mock the Twitter scraper** with placeholder data
2. **Test the scraper logic** with fake RSS feeds
3. **Validate parsing** using sample Twitter RSS XML

But **real testing requires real RSS feed URLs**.

---

## Alternative Solutions (If RSS.app Fails)

### Option 1: Direct X API ($100/month)
- Official Twitter/X API access
- Requires X Developer account
- Basic tier: $100/month for 10K tweets
- More reliable but expensive

### Option 2: Web Scraping
- Scrape X profile pages directly
- Higher risk of IP blocking
- Requires rotating proxies
- Against X Terms of Service

### Option 3: Focus on politi.dk
- Already working with police_scraper.py
- Single RSS feed: https://politi.dk/nyhedsliste
- No Twitter integration needed
- Fallback if Twitter RSS too complex

---

## Summary

**STATUS**: ⚠️ BLOCKED - Waiting for RSS.app feed URLs

**ACTION REQUIRED**:
1. Create RSS.app account
2. Generate RSS feed for @KobenhavnPoliti
3. Provide feed URL and format

**ESTIMATED TIME**: 15-30 minutes for setup

**Once provided**: I can implement Twitter scraper in ~2 hours

---

**Last Updated**: October 7, 2025
**Status**: Awaiting RSS.app feed URLs
