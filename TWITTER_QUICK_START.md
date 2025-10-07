# Twitter Integration - Quick Start Guide

## TL;DR - What You Need To Do

**STATUS**: ⚠️ BLOCKED - Need RSS.app feed URLs

I've configured all 15 Danish police Twitter accounts in the scraper, but I can't implement the code until you provide RSS feed URLs from RSS.app.

---

## 5-Minute Setup

### Step 1: Create Account (2 minutes)
1. Go to https://rss.app/
2. Click "Sign Up"
3. Create free account (no credit card)

### Step 2: Generate Test Feed (3 minutes)
1. Click "Create New Feed"
2. Select "Twitter/X" as source
3. Enter handle: `KobenhavnPoliti`
4. Click "Create Feed"
5. **COPY THE RSS FEED URL**

### Step 3: Give Me The URL
Paste the RSS feed URL here or in config.py:

```
Feed URL: https://rss.app/feeds/[YOUR_FEED_ID_HERE]/KobenhavnPoliti.xml
```

That's it! Once I have that URL, I can implement the Twitter scraper in ~2 hours.

---

## What I've Already Done

### ✅ Configured All 15 Police Accounts

File: `ingestion/config.py` (lines 289-511)

```python
TWITTER_POLICE_SOURCES = {
    "twitter_kobenhavns_politi": {
        "name": "Københavns Politi (Copenhagen Police)",
        "handle": "@KobenhavnPoliti",
        "rss": "PLACEHOLDER_RSS_APP_URL_HERE",  # ← Need real URL here
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "kastrup", "lufthavn"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "enabled": False  # ← Will enable after RSS.app setup
    },
    # ... 14 more accounts
}
```

### ✅ Complete Account List

**National**: @rigspoliti, @NSK_politi
**Copenhagen**: @KobenhavnPoliti (TEST THIS FIRST), @VestegnsPoliti
**Jutland**: @NjylPoliti, @OjylPoliti, @SydOjylPoliti, @SjylPoliti, @MVJPoliti
**Zealand**: @NSJPoliti, @MVSJPoliti, @SSJ_LFPoliti
**Islands**: @FynsPoliti, @BornholmsPoliti
**Other**: @Politimuseet

---

## What Happens Next

### Once You Give Me 1 RSS Feed URL

I will:
1. ✅ Create `twitter_scraper.py` - Parse RSS feeds from Twitter
2. ✅ Test with Copenhagen Police (@KobenhavnPoliti)
3. ✅ Validate drone incident extraction
4. ✅ Update `ingest.py` pipeline
5. ✅ Create test suite

**Estimated Time**: 2-3 hours

### Then You Generate 14 More URLs

For the remaining accounts:
- @rigspoliti (National)
- @NjylPoliti (Aalborg Airport)
- @OjylPoliti (Aarhus Airport)
- @MVJPoliti (Billund Airport)
- ... 11 more

Or, if RSS.app has an API, I can automate this step.

---

## Quick FAQ

### Q: Why not use Nitter?
**A**: Nitter was discontinued February 2024. No longer works.

### Q: Why not use TwitRSS.me?
**A**: Currently offline. Shows "Coming...soon" placeholder.

### Q: Why not use X/Twitter API directly?
**A**: Costs $100/month. RSS.app is $0-9/month for 15 feeds.

### Q: How many feeds do I need?
**A**: 15 total (one per police district). Free tier = ~5-10 feeds, so you'll likely need **Basic tier ($9/mo)**.

### Q: Can I test with just Copenhagen first?
**A**: Yes! That's exactly what I recommend. Test @KobenhavnPoliti first, then scale to all 15.

---

## Example RSS.app Feed URL

I expect the URL to look something like:

```
https://rss.app/feeds/abc123xyz/KobenhavnPoliti.xml
```

Or:

```
https://api.rss.app/v1/feeds/abc123xyz.xml
```

Once you create the feed, just paste the exact URL here and I'll handle the rest.

---

## Full Documentation

For detailed instructions and troubleshooting:
- **Setup**: `docs/TWITTER_RSS_SETUP.md`
- **Status**: `TWITTER_INTEGRATION_STATUS.md`
- **Config**: `ingestion/config.py` (lines 271-538)

---

## Summary

**What I need**: 1 RSS feed URL for @KobenhavnPoliti
**Where to get it**: https://rss.app/ (free account)
**Time to set up**: 5 minutes
**Time to implement**: 2 hours after I get the URL

Let me know when you have the feed URL! 🚀
