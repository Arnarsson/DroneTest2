# Source Expansion Plan - European Coverage

**Current Status**: 7 sources (Danish police Twitter only)
**Goal**: 100+ sources across Nordic countries + Europe
**Priority**: HIGH - User reported missing sources

---

## Problem Analysis

### Current State
**Database**:
- 28 configured sources in `sources` table
- Only 7 actually being scraped
- All 7 are Danish police Twitter accounts

**Scrapers Running**:
1. ✅ `PoliceScraper` - Working (Twitter/RSS.app)
2. ⚠️ `NewsScraper` - Configured but not finding incidents
3. ⚠️ `TwitterScraper` - Working but limited to Denmark

**Why So Few Sources**:
1. **Recent incidents only**: News scrapers only find incidents from last 7-14 days
2. **Keyword matching**: Strict keywords may be missing incidents
3. **Geographic limitation**: Only Danish police have Twitter accounts configured
4. **No active scraping**: RSS news feeds not producing results

---

## Immediate Actions (Next 30 Minutes)

### 1. Expand Police Twitter Sources
**Target**: Norway, Sweden, Finland police departments

**Norwegian Police** (add to config):
```python
# Oslo Police
"oslo_politi": {
    "name": "Oslo politidistrikt",
    "twitter": "@oslopolitiet",
    "rss_app": "https://rss.app/feeds/...",  # Need to create
    "source_type": "police",
    "trust_weight": 4,
    "country": "NO"
}

# Østlandet Police
"ostlandet_politi": {
    "name": "Østlandet politidistrikt",
    "twitter": "@politietost",
    "source_type": "police",
    "trust_weight": 4,
    "country": "NO"
}

# Trøndelag Police
"trondelag_politi": {
    "name": "Trøndelag politidistrikt",
    "twitter": "@tronderlagpoliti",
    "source_type": "police",
    "trust_weight": 4,
    "country": "NO"
}
```

**Swedish Police** (add to config):
```python
# National Police
"polisen_sverige": {
    "name": "Polisen Sverige",
    "twitter": "@polisen",
    "source_type": "police",
    "trust_weight": 4,
    "country": "SE"
}

# Stockholm Police
"polisen_stockholm": {
    "name": "Polisen Stockholm",
    "twitter": "@polisenstockholm",
    "source_type": "police",
    "trust_weight": 4,
    "country": "SE"
}
```

**Finnish Police** (add to config):
```python
# National Police
"poliisi_finland": {
    "name": "Poliisi",
    "twitter": "@PoliisiHelsinki",
    "source_type": "police",
    "trust_weight": 4,
    "country": "FI"
}
```

**Estimated**: +15 Nordic police sources

### 2. Fix News Scraper Keywords
**Problem**: Too strict keywords missing incidents

**Current keywords** (Danish):
- drone, dron, lufthavn, forsvar, uav

**Expand to Nordic languages**:
```python
NORDIC_KEYWORDS = {
    'DK': ['drone', 'dron', 'lufthavn', 'forsvar', 'uav', 'droner'],
    'NO': ['drone', 'lufthavn', 'forsvar', 'gardermoen', 'oslo lufthavn'],
    'SE': ['drönare', 'flygplats', 'försvar', 'arlanda', 'bromma'],
    'FI': ['drone', 'lentokenttä', 'puolustus', 'vantaa', 'helsinki'],
    'EU': ['drone', 'uav', 'airport', 'airspace', 'unmanned']
}
```

**Estimated**: 3x more incident matches

### 3. Add European Aviation Authorities
**Official NOTAM sources** (Evidence Score 4):

```python
# Eurocontrol
"eurocontrol_notam": {
    "name": "Eurocontrol NOTAM",
    "api": "https://www.public.nm.eurocontrol.int/PUBPORTAL/gateway/spec/",
    "source_type": "notam",
    "trust_weight": 4,
    "country": "EU"
}

# UK CAA
"uk_caa": {
    "name": "UK Civil Aviation Authority",
    "rss": "https://www.caa.co.uk/news/feed/",
    "source_type": "aviation_authority",
    "trust_weight": 4,
    "country": "GB"
}

# German DFS
"dfs_germany": {
    "name": "DFS Deutsche Flugsicherung",
    "rss": "https://www.dfs.de/dfs_homepage/en/press/feed.xml",
    "source_type": "aviation_authority",
    "trust_weight": 4,
    "country": "DE"
}
```

**Estimated**: +10 aviation authority sources

---

## Medium-Term Actions (Next Session)

### 4. Add Major European News Sources
**Target**: Reuters, AFP, AP, The Guardian, BBC

```python
# International wire services
"reuters_europe": {
    "name": "Reuters Europe",
    "rss": "https://www.reuters.com/europe/feed/",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "uav", "airport", "airspace"],
    "country": "INT"
}

"ap_europe": {
    "name": "Associated Press Europe",
    "rss": "https://www.ap.org/en-us/topics/europe.rss",
    "source_type": "media",
    "trust_weight": 3,
    "country": "INT"
}

# UK news
"guardian_security": {
    "name": "The Guardian - Security",
    "rss": "https://www.theguardian.com/uk/defence-and-security/rss",
    "source_type": "media",
    "trust_weight": 3,
    "country": "GB"
}

"bbc_europe": {
    "name": "BBC Europe",
    "rss": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "source_type": "media",
    "trust_weight": 3,
    "country": "GB"
}
```

**Estimated**: +20 major news sources

### 5. Add Defense News Sources
**Military and security news**:

```python
"janes_defence": {
    "name": "Jane's Defence Weekly",
    "rss": "https://www.janes.com/feeds/defence-news.xml",
    "source_type": "media",
    "trust_weight": 3,
    "keywords": ["drone", "uav", "unmanned"],
    "country": "INT"
}

"defense_news": {
    "name": "Defense News Europe",
    "rss": "https://www.defensenews.com/arc/outboundfeeds/rss/category/europe/",
    "source_type": "media",
    "trust_weight": 3,
    "country": "INT"
}

"the_drive_warzone": {
    "name": "The Drive - The War Zone",
    "rss": "https://www.thedrive.com/the-war-zone/rss",
    "source_type": "media",
    "trust_weight": 2,
    "keywords": ["drone", "europe", "nato"],
    "country": "US"
}
```

**Estimated**: +10 defense news sources

---

## Long-Term Actions (Future)

### 6. GDELT Integration
**Global event database**:

```python
# GDELT GKG API
gdelt_query = """
    SELECT * FROM gdelt.gkg
    WHERE themes LIKE '%DRONE%'
    AND geo IN ('Denmark', 'Norway', 'Sweden', 'Finland', ...)
    AND date > NOW() - INTERVAL '7 days'
"""
```

**Benefits**:
- 100K+ news sources worldwide
- Real-time event detection
- Automatic translation
- Geographic filtering

**Estimated**: +1000 potential sources

### 7. Social Media Expansion
**Twitter/X premium APIs**:

```python
# Search for drone + airport mentions
twitter_api.search(
    query="(drone OR dron OR drönare) (airport OR lufthavn OR flygplats)",
    geocode="59.91,10.75,500km",  # Oslo + 500km radius
    lang="da,no,sv,fi,en"
)
```

**Estimated**: +50 real-time sources

---

## Implementation Priority

### Phase 1: Immediate (This Session) 🔴
1. Add Nordic police Twitter accounts (+15 sources)
2. Expand keyword lists for all languages
3. Fix news scraper to find more incidents
4. Test with real data

**Estimated Time**: 1-2 hours
**Impact**: 3-5x more incidents

### Phase 2: This Week 🟡
1. Add European aviation authorities (+10 sources)
2. Add major news sources (+20 sources)
3. Add defense news (+10 sources)
4. Set up hourly scraping cron

**Estimated Time**: 3-4 hours
**Impact**: 10x more incidents

### Phase 3: Next Week 🟢
1. GDELT integration
2. Twitter premium API
3. Automated source discovery
4. Quality monitoring

**Estimated Time**: 8-10 hours
**Impact**: 100x more incidents

---

## Technical Requirements

### Database Schema
Already have:
- ✅ `sources` table (28 configured)
- ✅ `incident_sources` table (multi-source support)
- ✅ Consolidation engine

Need to add:
- [ ] Source performance tracking (success rate, latency)
- [ ] Source blacklist (broken feeds)
- [ ] Auto-disable failing sources

### API Rate Limits
**Current**: No limits
**Need**:
- RSS.app: 1000 requests/day (free tier)
- Twitter: 500 requests/month (free tier)
- GDELT: 250 requests/15min (free)

### Performance
**Current**: 7 sources in <60s
**Target**: 100 sources in <5 minutes
**Strategy**: Parallel scraping with asyncio

---

## Success Metrics

### Coverage
- **Current**: Denmark only (7 sources)
- **Phase 1**: All Nordic countries (25+ sources)
- **Phase 2**: Europe (50+ sources)
- **Phase 3**: Global (100+ sources)

### Incident Volume
- **Current**: ~6 incidents in production
- **Phase 1**: 20-30 incidents expected
- **Phase 2**: 50-100 incidents expected
- **Phase 3**: 200-500 incidents expected

### Evidence Quality
- **Current**: 85% OFFICIAL (5/6)
- **Target**: 60% OFFICIAL, 30% VERIFIED, 10% REPORTED
- **Strategy**: Multi-source consolidation upgrades scores

---

## Next Steps

### Immediate (USER ACTION)
1. **Decide priority**: Nordic first OR Europe first?
2. **Approve Twitter accounts**: Create RSS.app feeds for police
3. **Keyword review**: Verify Nordic language keywords

### Developer Actions (ME)
1. Add Nordic police sources to config
2. Expand keyword lists
3. Create RSS.app feeds for new Twitter accounts
4. Test scraping with new sources
5. Deploy to production

**Estimated Total Time**: 1-2 hours for Phase 1

---

**Status**: 🔴 HIGH PRIORITY - USER WAITING

**Next Action**: Add Nordic police Twitter sources + expand keywords

