# AI-Powered Incident Deduplication Plan

## Problem Statement

**Current Issue**: Multiple incidents at the same location are stored as separate database rows, creating clusters of markers instead of a single incident with multiple sources.

**Example**: 14 separate incidents near Copenhagen → Should be 1 incident with 14 sources in the incident card

**Root Cause**: Current deduplication logic in `ingestion/db_cache.py` is not aggressive enough and doesn't properly merge incidents from different sources reporting the same event.

---

## Solution Architecture

### Phase 1: AI-Powered Deduplication Service (CRITICAL)

#### 1.1 OpenAI/Anthropic Integration for Semantic Matching

**Purpose**: Use LLM to determine if two incidents are reporting the same event

**Location**: `ingestion/ai_deduplicator.py` (NEW FILE)

**Key Features**:
- Semantic similarity analysis of titles and narratives
- Location proximity matching (within 1km radius)
- Temporal clustering (within 6-hour window)
- Evidence score reconciliation (take highest)
- Source aggregation (merge all sources)

**API Choice**:
- **OpenAI GPT-4o-mini** (recommended): Fast, cheap, good for structured output
- **Anthropic Claude Sonnet**: More accurate but slower/expensive
- **Local LLM** (Ollama): Free but requires hosting

**Implementation**:
```python
import openai
from datetime import datetime, timedelta
import json

class AIDeduplicator:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    async def are_incidents_duplicate(
        self,
        incident1: dict,
        incident2: dict
    ) -> dict:
        """
        Returns:
        {
            "is_duplicate": bool,
            "confidence": float (0-1),
            "reasoning": str,
            "merged_title": str,
            "merged_narrative": str
        }
        """

        # Early rejection: location too far apart
        if self._distance_km(incident1, incident2) > 1.0:
            return {"is_duplicate": False, "confidence": 1.0, "reasoning": "Locations >1km apart"}

        # Early rejection: time too far apart
        if self._time_diff_hours(incident1, incident2) > 6:
            return {"is_duplicate": False, "confidence": 1.0, "reasoning": "Times >6hrs apart"}

        # AI analysis
        prompt = self._build_comparison_prompt(incident1, incident2)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": DEDUPLICATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1  # Low temperature for consistency
        )

        result = json.loads(response.choices[0].message.content)
        return result

    def _build_comparison_prompt(self, inc1: dict, inc2: dict) -> str:
        return f"""
Compare these two drone incidents and determine if they're reporting the SAME event:

INCIDENT 1:
- Title: {inc1['title']}
- Narrative: {inc1.get('narrative', 'N/A')}
- Location: ({inc1['lat']}, {inc1['lon']})
- Time: {inc1['occurred_at']}
- Asset Type: {inc1.get('asset_type', 'N/A')}
- Evidence Score: {inc1['evidence_score']}

INCIDENT 2:
- Title: {inc2['title']}
- Narrative: {inc2.get('narrative', 'N/A')}
- Location: ({inc2['lat']}, {inc2['lon']})
- Time: {inc2['occurred_at']}
- Asset Type: {inc2.get('asset_type', 'N/A')}
- Evidence Score: {inc2['evidence_score']}

ANALYSIS REQUIREMENTS:
1. Are these describing the SAME physical event? (not just similar events)
2. Consider: location proximity, time correlation, asset type, narrative details
3. Provide confidence score (0.0-1.0)
4. If duplicate, suggest merged title and narrative

Return JSON:
{{
    "is_duplicate": boolean,
    "confidence": float,
    "reasoning": "your detailed analysis",
    "merged_title": "best title for merged incident",
    "merged_narrative": "comprehensive narrative combining both"
}}
"""

DEDUPLICATION_SYSTEM_PROMPT = """You are an expert analyst specializing in drone incident verification and deduplication.

Your task is to determine if two incident reports are describing the SAME real-world event.

GUIDELINES:
- Same event = same location (within 1km), same timeframe (within 6hrs), same basic facts
- Different perspectives of same event = DUPLICATE
- Multiple drone incidents at same location on different days = NOT DUPLICATE
- Similar incidents at different locations = NOT DUPLICATE

Be conservative: only mark as duplicate if >80% confident they're the same event."""
```

#### 1.2 Batch Deduplication Process

**Location**: `ingestion/run_deduplication.py` (NEW FILE)

**Purpose**: One-time script to clean up existing database

**Process**:
1. Fetch all incidents from database
2. Group by location proximity (1km radius)
3. For each group, run pairwise AI comparison
4. Merge duplicates: keep one incident, aggregate sources
5. Update database with merged incidents
6. Generate deduplication report

**Expected Impact**:
- **27 incidents → ~8-12 unique incidents** (estimated)
- Copenhagen cluster "14" → 1-3 actual incidents with multiple sources each

#### 1.3 Real-Time Deduplication in Scraper

**Location**: Modify `ingestion/ingest.py` and `ingestion/db_cache.py`

**Process**:
1. When new incident scraped, before DB insert:
2. Query existing incidents within 1km + 6hrs
3. Run AI comparison against candidates
4. If duplicate found (confidence >0.8):
   - Add source to existing incident
   - Update evidence score if higher
   - Update narrative if more detailed
5. If not duplicate:
   - Insert as new incident

**Caching Strategy**:
- Cache AI responses for 24hrs to avoid redundant API calls
- Use incident title hash as cache key

---

### Phase 2: Enhanced Database Schema (OPTIONAL but RECOMMENDED)

#### 2.1 Add Deduplication Metadata

**Migration**: `migrations/009_add_deduplication_metadata.sql`

```sql
ALTER TABLE public.incidents ADD COLUMN IF NOT EXISTS dedupe_cluster_id UUID;
ALTER TABLE public.incidents ADD COLUMN IF NOT EXISTS dedupe_confidence FLOAT;
ALTER TABLE public.incidents ADD COLUMN IF NOT EXISTS ai_reviewed BOOLEAN DEFAULT FALSE;
ALTER TABLE public.incidents ADD COLUMN IF NOT EXISTS ai_review_timestamp TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_incidents_dedupe_cluster
ON public.incidents(dedupe_cluster_id);

COMMENT ON COLUMN public.incidents.dedupe_cluster_id IS
'UUID linking incidents that were AI-analyzed and confirmed as separate events at same location';

COMMENT ON COLUMN public.incidents.dedupe_confidence IS
'AI confidence score (0-1) that this incident is unique (not a duplicate)';
```

**Benefits**:
- Track which incidents have been AI-reviewed
- Group related-but-separate incidents (e.g., multiple drone flights on different days at same base)
- Audit trail for deduplication decisions

#### 2.2 Sources Array Already Exists ✅

**Current Schema**: `sources JSONB[]` already in incidents table

**No changes needed** - just ensure scraper populates this correctly

---

### Phase 3: API & Frontend Updates

#### 3.1 API Endpoint Enhancement

**File**: `frontend/api/incidents.py`

**Current**: Returns incidents with sources array
**Enhancement**: No changes needed! Sources are already returned

#### 3.2 Frontend Incident Card Update

**File**: `frontend/components/Map.tsx` (popup content)

**Current**: Shows incident details with sources list at bottom
**Enhancement**: More prominent source display

**Suggested Improvements**:
1. **Source count badge**: "3 sources" next to evidence badge
2. **Source quality indicator**: Show mix of official/news/social
3. **Source timeline**: "First reported 5 days ago, last update 2 days ago"
4. **Click to expand sources**: Collapsible source list for incidents with many sources

---

## Implementation Plan

### Week 1: AI Deduplication Core
- [ ] Day 1: Create `ai_deduplicator.py` with OpenAI integration
- [ ] Day 2: Create `run_deduplication.py` batch script
- [ ] Day 3: Test on sample data (5-10 known duplicates)
- [ ] Day 4: Run on production database (DRY RUN - report only)
- [ ] Day 5: Review results, adjust confidence thresholds

### Week 2: Integration & Cleanup
- [ ] Day 1: Integrate AI deduplication into scraper pipeline
- [ ] Day 2: Run production deduplication (backup first!)
- [ ] Day 3: Migration 009 - add metadata columns
- [ ] Day 4: Update frontend to show source count
- [ ] Day 5: Testing and verification

### Week 3: Monitoring & Refinement
- [ ] Day 1: Monitor scraper for false positives/negatives
- [ ] Day 2: Tune confidence thresholds based on results
- [ ] Day 3: Add deduplication metrics dashboard
- [ ] Day 4: Documentation updates
- [ ] Day 5: Performance optimization

---

## Cost Estimation

### OpenAI API Costs (GPT-4o-mini)

**Assumptions**:
- 27 existing incidents → ~350 pairwise comparisons (one-time)
- 5-10 new incidents per day → ~50 comparisons per day
- ~500 tokens per comparison (input + output)

**One-Time Batch Deduplication**:
- 350 comparisons × 500 tokens = 175,000 tokens
- Cost: ~$0.03 (GPT-4o-mini: $0.15/1M input, $0.60/1M output)

**Ongoing Daily Costs**:
- 50 comparisons/day × 500 tokens = 25,000 tokens/day
- Cost: ~$0.004/day = **$0.12/month**

**Total First Month**: $0.03 (one-time) + $0.12 (ongoing) = **$0.15**

**Extremely affordable!**

---

## Alternative: Rule-Based Approach (Faster but Less Accurate)

If you want to avoid AI API costs entirely, we can use a rule-based system:

### Rule-Based Deduplication Logic

```python
def are_duplicates_rule_based(inc1, inc2) -> bool:
    # Must be within 500m
    if distance_km(inc1, inc2) > 0.5:
        return False

    # Must be within 3 hours
    if time_diff_hours(inc1, inc2) > 3:
        return False

    # Title similarity (using fuzzy matching)
    title_similarity = fuzz.ratio(inc1['title'], inc2['title'])
    if title_similarity > 80:
        return True

    # Narrative similarity
    if inc1.get('narrative') and inc2.get('narrative'):
        narrative_similarity = fuzz.ratio(inc1['narrative'], inc2['narrative'])
        if narrative_similarity > 70:
            return True

    # Asset type must match
    if inc1.get('asset_type') != inc2.get('asset_type'):
        return False

    return False
```

**Pros**: Free, fast, no external dependencies
**Cons**: Less accurate, can't handle semantic variations, rigid rules

**Recommendation**: Start with AI approach for accuracy, fall back to rule-based if costs become an issue

---

## Success Metrics

### Before AI Deduplication
- ❌ 27 incidents total
- ❌ 14 markers clustered at Copenhagen
- ❌ Multiple identical incidents from different news sources
- ❌ User confusion about "multiple incidents"

### After AI Deduplication
- ✅ ~8-12 unique incidents (estimated)
- ✅ 1-3 markers at Copenhagen (each representing a distinct event)
- ✅ Each incident has multiple sources aggregated
- ✅ Clear incident cards showing source provenance
- ✅ User confidence in data quality

---

## Monitoring & Alerting

### Deduplication Dashboard

**Metrics to Track**:
1. Total incidents in database
2. Incidents with multiple sources (good!)
3. Incidents within 1km of each other (potential duplicates)
4. AI confidence scores distribution
5. Manual review queue (low confidence cases)

### Alerts
- Alert if >5 incidents within 1km added in same day (likely duplicates missed)
- Alert if incident has >20 sources (likely over-merging)
- Alert if AI confidence <0.6 (needs manual review)

---

## Next Steps - Your Decision

**Option A: AI-Powered (Recommended)**
- More accurate, handles semantic variations
- Costs ~$0.15/month (negligible)
- Better user experience
- **Timeline**: 2-3 weeks

**Option B: Enhanced Rule-Based**
- Free, faster to implement
- Less accurate, more false positives/negatives
- **Timeline**: 1 week

**Option C: Hybrid**
- Rule-based for obvious duplicates (exact location + time)
- AI for edge cases (semantic analysis needed)
- Balance of cost and accuracy
- **Timeline**: 2 weeks

---

## Questions for You

1. **Budget**: Are you comfortable with ~$0.15/month for AI API calls?
2. **Timeline**: Do you need this fixed ASAP (rule-based) or can we do it right (AI)?
3. **Accuracy**: How important is it to get this 100% right vs. 90% right?
4. **Manual Review**: Are you willing to manually review low-confidence cases?

---

**Recommendation**: Go with **Option C (Hybrid)** - it's the best balance of cost, accuracy, and timeline. Start with rule-based for obvious duplicates, use AI for edge cases, and monitor results to tune the system.

Let me know which option you prefer and I'll start implementing immediately!
