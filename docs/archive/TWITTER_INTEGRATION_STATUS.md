# Twitter/X Integration Status - Danish Police Accounts

## Summary

Prepared configuration for 15 Danish police Twitter/X accounts using RSS.app for RSS feed generation. Implementation is **blocked** pending RSS.app account setup and feed URL generation.

---

## ✅ Completed

### 1. Research Phase
- ✅ Identified all 15 Danish police district Twitter accounts
- ✅ Verified account handles via politi.dk/en/social-media
- ✅ Researched RSS feed solutions (Nitter ❌, TwitRSS.me ❌, RSS.app ✅)
- ✅ Documented RSS.app as working solution (October 2025)

### 2. Configuration Phase
- ✅ Added `TWITTER_POLICE_SOURCES` to `ingestion/config.py`
- ✅ Configured all 15 police accounts with metadata:
  - Twitter handle
  - Trust weight: 4 (police = official source)
  - Keywords: drone, dron, uav, lufthavn, forsvar
  - Hashtags: #politidk, #kriseinfodk
  - Regional coverage mapping
  - Airport correlation (Copenhagen, Aalborg, Aarhus, Billund, Odense)
- ✅ Set `enabled: False` for all accounts (awaiting RSS URLs)
- ✅ Deprecated old Nitter sources in config

### 3. Documentation Phase
- ✅ Created `docs/TWITTER_RSS_SETUP.md` - Step-by-step RSS.app setup guide
- ✅ Created `TWITTER_INTEGRATION_STATUS.md` - This file

---

## 🚨 BLOCKED - Awaiting User Action

### Critical Blocker: RSS.app Feed URLs Required

**Status**: ⚠️ BLOCKED
**Action**: User must create RSS.app account and provide RSS feed URLs
**Estimated Time**: 15-30 minutes for setup
**Documentation**: See `docs/TWITTER_RSS_SETUP.md`

### What's Needed

1. **RSS.app Account**: Sign up at https://rss.app/
2. **Generate Test Feed**: Create RSS feed for @KobenhavnPoliti first
3. **Provide Feed URL**: Format example: `https://rss.app/feeds/{feed_id}/KobenhavnPoliti.xml`
4. **Document Pattern**: What URL format does RSS.app use?
5. **Check Limits**: How many feeds on free tier? Rate limits?

### Priority Accounts (Test These First)

1. **@KobenhavnPoliti** (Copenhagen) - Highest priority, test first ✨
2. **@Rigspoliti** (National Police) - National coordination
3. **@NjylPoliti** (North Jutland) - Aalborg Airport
4. **@OjylPoliti** (East Jutland) - Aarhus Airport
5. **@MVJPoliti** (Central/West Jutland) - Billund Airport

---

## 📋 All 15 Danish Police Accounts

### National Level (2)
| # | Handle | Name | Coverage |
|---|--------|------|----------|
| 1 | @rigspoliti | Rigspolitiet | National coordination |
| 2 | @NSK_politi | National Special Crime | Serious crimes/terrorism |

### Regional Police Districts (12)
| # | Handle | Name | Region | Airport |
|---|--------|------|--------|---------|
| 3 | @KobenhavnPoliti | Københavns Politi | Copenhagen | **Copenhagen Airport** ✈️ |
| 4 | @VestegnsPoliti | Vestegns Politi | West Copenhagen | - |
| 5 | @NjylPoliti | Nordjyllands Politi | North Jutland | **Aalborg Airport** ✈️ |
| 6 | @OjylPoliti | Østjyllands Politi | East Jutland | **Aarhus Airport** ✈️ |
| 7 | @SydOjylPoliti | Sydøstjyllands Politi | Southeast Jutland | - |
| 8 | @SjylPoliti | Syd- og Sønderjyllands | South Jutland | - |
| 9 | @MVJPoliti | Midt/Vestjyllands | Central/West Jutland | **Billund Airport** ✈️ |
| 10 | @NSJPoliti | Nordsjællands Politi | North Zealand | - |
| 11 | @MVSJPoliti | Midt/Vestsjællands | Central/West Zealand | - |
| 12 | @SSJ_LFPoliti | Sydsjællands/Lolland | South Zealand | - |
| 13 | @FynsPoliti | Fyns Politi | Funen | Odense Airport |
| 14 | @BornholmsPoliti | Bornholms Politi | Bornholm | Bornholm Airport |

### Other (1)
| # | Handle | Name | Purpose |
|---|--------|------|---------|
| 15 | @Politimuseet | Politimuseet | Educational (low priority) |

---

## 📊 Expected Impact

### Source Expansion
- **Current**: 1 police source (politi.dk RSS)
- **After Integration**: 16 police sources (1 RSS + 15 Twitter)
- **Growth**: 15x expansion in police incident coverage

### Regional Coverage
- **5 major airports**: Copenhagen, Aalborg, Aarhus, Billund, Odense
- **All 12 police districts**: Complete Denmark coverage
- **Real-time alerts**: Twitter faster than politi.dk website

### Evidence Quality
- **Trust Weight**: 4 (police = official source)
- **Multi-source Verification**: Same incident from district + national police
- **Automatic Evidence Score**: 4 for all police tweets

---

## 🔧 Pending Implementation Tasks

### Once RSS URLs Provided

#### Task 1: Create `twitter_scraper.py`
**Status**: Not started (blocked)
**Estimated Time**: 2 hours
**Dependencies**: RSS.app feed URLs

Features:
- RSS feed parsing (reuse `police_scraper.py` logic)
- Twitter-specific formatting (@mentions, hashtags)
- Keyword filtering (drone, dron, uav)
- Multi-language support (Danish, English)
- Source attribution with trust_weight: 4
- Error handling and rate limiting

#### Task 2: Update `ingest.py`
**Status**: Not started (blocked)
**Estimated Time**: 30 minutes
**Dependencies**: `twitter_scraper.py` completed

Changes:
```python
from scrapers.twitter_scraper import TwitterScraper

# Add to main pipeline
twitter_scraper = TwitterScraper()
twitter_incidents = twitter_scraper.fetch_all()
all_incidents.extend(twitter_incidents)
```

#### Task 3: Create `test_twitter_scraper.py`
**Status**: Not started (blocked)
**Estimated Time**: 1 hour
**Dependencies**: `twitter_scraper.py` completed

Test cases:
- RSS feed parsing
- Keyword filtering
- Source attribution
- Error handling
- Rate limit respect

#### Task 4: Test Single Account
**Status**: Not started (blocked)
**Estimated Time**: 30 minutes
**Dependencies**: All above completed

Steps:
1. Enable `twitter_kobenhavns_politi` only
2. Run `python3 ingest.py --test`
3. Verify incidents extracted correctly
4. Check source attribution (trust_weight: 4)
5. Validate database insertion

#### Task 5: Scale to All 15 Accounts
**Status**: Not started (blocked)
**Estimated Time**: 1 hour
**Dependencies**: Single account test passing

Steps:
1. Enable all 15 accounts in config.py
2. Run full ingestion pipeline
3. Monitor for rate limit issues
4. Validate multi-source consolidation
5. Check evidence score upgrades (1 source → 2+ sources)

---

## 💰 Cost Considerations

### RSS.app Pricing (October 2025)
- **Free Tier**: ~5-10 feeds, limited requests
- **Basic ($9/mo)**: ~20 feeds, 500 requests/hour
- **Pro ($29/mo)**: ~100 feeds, unlimited requests

### Recommendation
**15 police accounts** → Need at least **Basic tier ($9/mo)**
- Free tier insufficient (max ~5-10 feeds)
- Basic tier covers all 15 accounts
- Pro tier if scaling to other countries (Norway, Sweden)

### Alternative: Direct X API
- **Cost**: $100/month for 10K tweets
- **Pro**: More reliable, official API
- **Con**: 10x more expensive than RSS.app

---

## 🎯 Success Criteria

### Phase 1: Single Account Test (Copenhagen)
- ✅ RSS feed parsed successfully
- ✅ Drone-related tweets extracted
- ✅ Source attribution correct (trust_weight: 4)
- ✅ Geographic location extracted (Copenhagen)
- ✅ Database insertion successful

### Phase 2: All 15 Accounts
- ✅ All feeds parsed without errors
- ✅ Rate limits respected (no API blocks)
- ✅ Multi-source consolidation working
- ✅ Evidence scores upgraded for duplicate incidents
- ✅ Regional coverage complete (all 12 districts)

### Phase 3: Production Monitoring
- ✅ Hourly ingestion cron job running
- ✅ Error rate <1%
- ✅ Average latency <5 seconds per feed
- ✅ New incidents detected within 30 minutes
- ✅ Zero false positives (no non-drone tweets)

---

## 📁 Files Modified/Created

### Modified
- `ingestion/config.py` - Added TWITTER_POLICE_SOURCES (15 accounts)

### Created
- `docs/TWITTER_RSS_SETUP.md` - RSS.app setup guide
- `TWITTER_INTEGRATION_STATUS.md` - This status document

### Pending Creation
- `ingestion/scrapers/twitter_scraper.py` - Twitter scraper module
- `ingestion/test_twitter_scraper.py` - Test suite
- `docs/TWITTER_INTEGRATION.md` - Final integration documentation

---

## 🚀 Next Steps

### Immediate (User Action Required)
1. **Create RSS.app account**: https://rss.app/
2. **Generate test feed**: @KobenhavnPoliti
3. **Provide feed URL**: Post in chat or update config.py
4. **Document URL format**: What pattern does RSS.app use?

### After RSS URLs Provided (My Action)
1. **Implement twitter_scraper.py**: Parse RSS feeds, extract incidents
2. **Update ingest.py**: Add Twitter scraper to pipeline
3. **Create test suite**: Validate scraper functionality
4. **Test single account**: @KobenhavnPoliti first
5. **Scale to all 15**: Enable all police accounts
6. **Deploy to production**: Update Vercel environment

---

## 📚 Documentation References

- **Setup Guide**: `docs/TWITTER_RSS_SETUP.md`
- **Status Document**: `TWITTER_INTEGRATION_STATUS.md` (this file)
- **Config File**: `ingestion/config.py` (lines 271-538)
- **Police Website**: https://politi.dk/en/social-media
- **RSS.app**: https://rss.app/

---

**Last Updated**: October 7, 2025
**Status**: ⚠️ BLOCKED - Awaiting RSS.app feed URLs
**Next Action**: User must create RSS.app account
**Estimated Implementation**: 4 hours after RSS URLs provided
