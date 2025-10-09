# Revised Source Strategy - Practical Approach

**Discovery**: Nordic police are leaving Twitter/moving to official websites
**New Strategy**: Focus on NEWS SOURCES + Aviation Authorities

---

## Reality Check

### What's NOT Working
- ❌ Oslo police left Twitter (2025)
- ❌ Finnish police moved to poliisi.fi (Feb 2024)
- ❌ Many police departments abandoning social media
- ❌ Twitter API restrictions + costs

### What IS Working
- ✅ Danish police still on Twitter (Rigspolitiet, Nordjyllands, etc.)
- ✅ Swedish police active (@polisen_sthlm, @Polisen_Sverige)
- ✅ RSS news feeds (unlimited, free)
- ✅ Aviation authority NOTAMs (official, free)

---

## NEW Strategy: News-First Approach

### Phase 1: Expand Nordic NEWS Sources (Immediate)

**Norwegian News** (add 5-10 sources):
```python
"nrk_norge": {
    "name": "NRK Norge",
    "rss": "https://www.nrk.no/nyheter/siste.rss",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "lufthavn", "gardermoen", "forsvaret"],
    "country": "NO"
},

"vg_norge": {
    "name": "VG (Verdens Gang)",
    "rss": "https://www.vg.no/rss/create.php?categories=10,25",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "lufthavn"],
    "country": "NO"
},

"aftenposten_no": {
    "name": "Aftenposten",
    "rss": "https://www.aftenposten.no/rss",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "fly", "lufthavn"],
    "country": "NO"
},

"dagbladet_no": {
    "name": "Dagbladet",
    "rss": "https://www.dagbladet.no/rss",
    "source_type": "media",
    "trust_weight": 2,
    "keywords": ["drone"],
    "country": "NO"
}
```

**Swedish News** (add 5-10 sources):
```python
"svt_nyheter": {
    "name": "SVT Nyheter",
    "rss": "https://www.svt.se/nyheter/rss.xml",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drönare", "flygplats", "arlanda", "försvar"],
    "country": "SE"
},

"dn_se": {
    "name": "Dagens Nyheter",
    "rss": "https://www.dn.se/nyheter/rss/",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drönare", "flygplats"],
    "country": "SE"
},

"svenska_dagbladet": {
    "name": "Svenska Dagbladet",
    "rss": "https://www.svd.se/feeds/nyheter.rss",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drönare", "flygplats"],
    "country": "SE"
},

"expressen_se": {
    "name": "Expressen",
    "rss": "https://feeds.expressen.se/nyheter/",
    "source_type": "media",
    "trust_weight": 2,
    "keywords": ["drönare"],
    "country": "SE"
}
```

**Finnish News** (add 3-5 sources):
```python
"yle_uutiset": {
    "name": "YLE Uutiset",
    "rss": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "lentokenttä", "vantaa", "puolustus"],
    "country": "FI"
},

"helsingin_sanomat": {
    "name": "Helsingin Sanomat",
    "rss": "https://www.hs.fi/rss/tuoreimmat.xml",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "lentokenttä"],
    "country": "FI"
},

"iltalehti_fi": {
    "name": "Iltalehti",
    "rss": "https://www.iltalehti.fi/rss.xml",
    "source_type": "media",
    "trust_weight": 2,
    "keywords": ["drone"],
    "country": "FI"
}
```

**Estimated**: +20 Nordic news sources

### Phase 2: Add European News (Next)

**International Wire Services**:
```python
"reuters_europe": {
    "name": "Reuters Europe",
    "rss": "https://www.reuters.com/world/europe/rss",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "airport", "airspace"],
    "country": "INT"
},

"ap_news_europe": {
    "name": "AP News Europe",
    "rss": "https://rsshub.app/apnews/topics/europe",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "airport"],
    "country": "INT"
}
```

**UK News**:
```python
"bbc_europe": {
    "name": "BBC Europe",
    "rss": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "airport"],
    "country": "GB"
},

"guardian_europe": {
    "name": "The Guardian Europe",
    "rss": "https://www.theguardian.com/world/europe-news/rss",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "airport"],
    "country": "GB"
}
```

**Estimated**: +10 European news sources

---

## Implementation Plan

### Step 1: Update config.py (15 minutes)
Add 20+ Nordic news RSS feeds with correct keywords

### Step 2: Test RSS feeds (10 minutes)
Verify all RSS URLs are valid and parseable

### Step 3: Run scraper test (5 minutes)
```bash
cd ingestion
python3 ingest.py --test
```

### Step 4: Deploy to production (5 minutes)
Push to main, Vercel auto-deploys

**Total Time**: 35 minutes

---

## Expected Results

### Current State
- 7 sources (Danish police Twitter only)
- 6 incidents in production

### After Phase 1
- 25+ sources (DK/NO/SE/FI news + DK police)
- 20-30 incidents expected
- Better geographic coverage

### After Phase 2
- 35+ sources (+ European news)
- 40-60 incidents expected
- European coverage

---

## Next Action

Shall I proceed with adding Nordic news sources to `config.py`?

**Yes** → I'll add 20+ news RSS feeds immediately
**Wait** → I'll wait for your approval first

