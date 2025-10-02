# DroneWatch AI Deduplication System - Session Summary
**Date**: October 1, 2025 (Evening)
**Status**: Implementation Phase Started

---

## 🎯 Problem Identified

**Issue**: Map shows "14" marker cluster at Copenhagen → User clicks → Re-clusters to "8+4+5" instead of spreading markers

**Root Cause**: 13-14 separate incidents stored in database that should be 2-4 unique incidents with multiple sources aggregated

**User Request**:
1. AI-powered deduplication to merge duplicate incidents
2. Source verification to assign accurate evidence scores
3. Failsafes against AI hallucinations and simulations

---

## ✅ Phase 1 Complete: AI Similarity Engine

### File Created: `ingestion/ai_similarity.py`

**Purpose**: Intelligent incident comparison using OpenRouter's FREE DeepSeek R1 model

**Key Features**:
- ✅ OpenRouter integration with DeepSeek R1 (FREE tier)
- ✅ Rule-based fallback when AI unavailable
- ✅ **5-Layer Anti-Hallucination Protection**:
  1. Required field validation
  2. Confidence score bounds checking (0.0-1.0, capped at 0.95)
  3. Cross-validation with rule-based logic (facts override AI)
  4. Reasoning quality check (min 20 chars)
  5. Merged content validation (60% word overlap, no speculation phrases)
- ✅ Levenshtein distance for fuzzy text matching
- ✅ Haversine formula for geographic distance
- ✅ Session-based result caching

**Anti-Hallucination Safeguards**:
```python
# If AI says duplicate but locations >500m apart → REJECT AI, trust facts
# If AI says duplicate but times >3hrs apart → REJECT AI, trust facts
# If merged content >3x longer than originals → REJECT, use original
# If merged content contains "I think", "probably", etc → REJECT, use original
# If merged content has <60% word overlap → REJECT, use original
```

**Cost**: $0/month (using free tier with 1000 requests/day limit)

---

## 📦 Configuration Created

### File: `ingestion/.env`

```bash
OPENROUTER_API_KEY=sk-or-v1-*** (user's key)
OPENROUTER_MODEL=deepseek/deepseek-r1:free
ENABLE_AI_DEDUP=true
DEDUP_SIMILARITY_THRESHOLD=0.80
DEDUP_AUTO_MERGE_THRESHOLD=0.85
```

---

## 🛡️ Safety Features Implemented

### 1. No Hallucinations
- Enhanced system prompt explicitly forbidding speculation
- Content validation rejecting non-factual additions
- Word overlap check ensuring merged content comes from originals

### 2. No Simulations
- Conservative thresholds (>0.8 confidence required)
- Rule-based cross-validation (facts override AI interpretation)
- Fallback to original content if AI produces suspicious output

### 3. Graceful Degradation
- Falls back to rule-based matching if AI fails
- Falls back to Levenshtein if python-Levenshtein unavailable
- Falls back to simple word matching as last resort

---

## 📋 Next Steps (Remaining Tasks)

### Task 2: Domain Classifier
Create `ingestion/domain_classifier.py` with:
- Official domains (police, military, aviation authorities)
- Major media outlets (DR, NRK, BBC, Reuters)
- Regional media and social media classification
- Trust level scoring (1-4)

### Task 3: Batch Deduplication Script
Create `scripts/ai_deduplicate_batch.py` with:
- Fetch all 27 incidents from database
- Group by location proximity (±1km)
- Run AI similarity analysis
- Generate merge plan with dry-run mode
- Execute merges with user approval
- **Expected Result**: 27 incidents → 12-15 unique events

### Task 4: Source Verifier
Create `ingestion/source_verifier.py` with:
- AI content analysis for verification signals
- Official source detection
- Evidence score calculation (1-4)
- Verification caching

### Task 5: Database Migration
Create `migrations/009_source_verification_cache.sql` with:
- source_verification_cache table
- Embedding cache (optional)
- Metadata columns for AI verification

### Task 6: Frontend Updates
- Show source count badges ("3 sources")
- Display AI confidence tooltips
- Source quality indicators

---

## 🧪 Testing Plan

### Unit Tests
```bash
# Test AI similarity engine
cd ingestion
python3 -m pytest ai_similarity.py -v

# Test with mock incidents
python3 ai_similarity.py  # Runs example comparison
```

### Integration Tests
```bash
# Dry-run batch deduplication
python3 scripts/ai_deduplicate_batch.py --dry-run

# Review merge plan
cat merge_plan.json

# Execute with approval
python3 scripts/ai_deduplicate_batch.py --execute
```

---

## 💰 Cost Analysis

| Provider | Model | Monthly Cost | Rate Limit |
|----------|-------|--------------|------------|
| OpenRouter | DeepSeek R1 | **$0 FREE** | 1000/day |
| OpenRouter | Gemini 2.5 Flash | ~$9 | Unlimited |
| Anthropic | Claude Haiku | ~$18 | Unlimited |
| OpenAI | GPT-4o-mini | ~$12 | Unlimited |

**Winner**: OpenRouter + DeepSeek R1 = **FREE** with professional quality (71.4% Aider score)

---

## 📊 Expected Impact

### Before:
- 27 incidents in database
- 14 markers clustered at Copenhagen
- Confusing re-clustering behavior
- No source aggregation

### After:
- 12-15 unique incidents (40-50% reduction)
- Each incident shows 2-5 aggregated sources
- Clean map with individual markers
- Professional data presentation
- Accurate evidence scores

---

## 🔐 Security Notes

1. ✅ API key stored in `.env` (not committed to git)
2. ✅ Anti-hallucination validation at 5 layers
3. ✅ Conservative thresholds prevent over-merging
4. ✅ Rule-based fallback ensures reliability
5. ✅ Transaction rollback capability (to be added in batch script)

---

## 📚 Documentation

### Files Created:
1. `ingestion/ai_similarity.py` - AI similarity engine (479 lines)
2. `ingestion/.env` - Configuration with API key
3. `SESSION_SUMMARY_AI_DEDUP.md` - This summary
4. `AI_DEDUPLICATION_PLAN.md` - Original comprehensive plan
5. `SOURCE_VERIFICATION_CHECKLIST.md` - Verification system design

### Files to Create:
1. `ingestion/domain_classifier.py`
2. `scripts/ai_deduplicate_batch.py`
3. `ingestion/source_verifier.py`
4. `migrations/009_source_verification_cache.sql`

---

## 🎬 Quick Start

```bash
# 1. Install dependencies
cd ingestion
pip install openai python-Levenshtein

# 2. Test AI similarity
python3 ai_similarity.py

# 3. Expected output:
# Is Duplicate: True
# Confidence: 0.89
# Method: ai_validated
# Reasoning: AI analysis: Both incidents... | Rule-based check: ...
```

---

## 🚀 Deployment Checklist

- [x] AI similarity engine implemented
- [x] Anti-hallucination safeguards added
- [x] API key configured
- [x] Rule-based fallback working
- [ ] Batch deduplication script
- [ ] Domain classifier
- [ ] Source verifier
- [ ] Database migration
- [ ] Frontend updates
- [ ] Production testing
- [ ] Git commit and deploy

---

**Status**: Core AI engine complete with anti-hallucination protection. Ready to proceed with batch deduplication script.

**Next Action**: Create `scripts/ai_deduplicate_batch.py` to clean up existing database.
