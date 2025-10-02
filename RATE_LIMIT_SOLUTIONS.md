# Rate Limit Solutions - OpenRouter Free Tier

## Problem

DeepSeek R1 free tier is hitting rate limits (429 errors) during batch deduplication.

---

## Solution 1: Add Delays Between API Calls ⚡ EASIEST

**Modify**: `ingestion/ai_similarity.py`

```python
import asyncio

async def are_incidents_duplicate(self, incident1: Dict, incident2: Dict) -> SimilarityResult:
    """Compare two incidents with AI, includes rate limit delay"""
    
    # Add delay between API calls to avoid rate limits
    await asyncio.sleep(2)  # 2 second delay between calls
    
    # Rest of function...
```

**Pros**:
- Simple 1-line fix
- Free tier stays free
- Prevents rate limits

**Cons**:
- Slower execution (2s × 4 groups = 8s extra)
- Still limited to 1000 req/day

**Implementation**: Add `await asyncio.sleep(2)` before OpenRouter API call

---

## Solution 2: Use Different Free Models (Rotate) 🔄 RECOMMENDED

**Models Available on OpenRouter FREE Tier**:
1. `deepseek/deepseek-r1:free` - Current (rate limited)
2. `x-ai/grok-2-1212:free` - Grok 2 (faster, less thinking)
3. `google/gemini-2.0-flash-exp:free` - Gemini Flash (fast)
4. `anthropic/claude-3.5-haiku:free` - Claude Haiku (balanced)

**Strategy**: Try each model in order until one works

```python
MODELS_TO_TRY = [
    "deepseek/deepseek-r1:free",
    "x-ai/grok-2-1212:free",
    "google/gemini-2.0-flash-exp:free",
    "anthropic/claude-3.5-haiku:free"
]

for model in MODELS_TO_TRY:
    try:
        response = await client.chat.completions.create(model=model, ...)
        break  # Success!
    except RateLimitError:
        continue  # Try next model
```

**Pros**:
- Still free
- Faster execution
- 4x the daily quota (1000 req/day per model)

**Cons**:
- Need to test each model's quality
- Different response formats possible

---

## Solution 3: Paid OpenRouter Credits 💰 BEST QUALITY

**Cost**: ~$5-10/month for occasional use

**Benefits**:
- No rate limits
- Access to best models (GPT-4, Claude Opus, etc.)
- Faster responses
- Higher daily quotas

**How to Add**:
1. Go to https://openrouter.ai/settings/billing
2. Add $10 credit
3. Models now use your credits instead of free tier

**Estimated Cost**:
- DeepSeek R1: $0.14 per 1M input tokens
- Batch of 27 incidents: ~4 API calls × 1000 tokens = ~$0.001
- Monthly usage (daily runs): ~$0.03/month

**Recommendation**: Add $5 credit, lasts months for this use case

---

## Solution 4: Run During Off-Peak Hours ⏰

**Peak Hours** (more rate limits):
- US business hours: 9am-5pm PST (6pm-2am CET)
- Most rate limited

**Off-Peak Hours** (fewer rate limits):
- Late night US: 2am-8am PST (11am-5pm CET)
- Early morning US: 6am-9am PST (3pm-6pm CET)

**Strategy**: Schedule deduplication for European mornings (US night)

**Pros**:
- Free
- No code changes

**Cons**:
- Timing dependent
- Not guaranteed

---

## Solution 5: Caching + Smarter Grouping 🧠

**Current**: AI analyzes every pair in each group

**Improved**: Cache results and skip obvious non-duplicates

```python
# Before AI call, check cache
cache_key = f"{incident1['id']}_{incident2['id']}"
if cache_key in self.cache:
    return self.cache[cache_key]

# Skip AI if rule-based is confident
rule_result = await self._rule_based_comparison(incident1, incident2)
if rule_result.confidence > 0.9:  # Very confident it's NOT duplicate
    return rule_result  # Skip AI call
    
# Only call AI for uncertain cases
```

**Pros**:
- Reduces API calls by 50-70%
- Free
- Faster execution

**Cons**:
- Requires logic changes
- May miss edge cases

---

## Solution 6: Use Claude Code's Free OpenRouter Key

If you used my suggestion to try Grok (`x-ai/grok-4-fast:free`), but it's still using DeepSeek, you might need to:

```bash
# Set model explicitly in environment
export OPENROUTER_MODEL="x-ai/grok-2-1212:free"

# Or pass to script directly
python3 scripts/ai_deduplicate_batch.py --model "x-ai/grok-2-1212:free"
```

---

## Recommendation: Combined Approach ✅

**Best Solution**:
1. Add 2-second delays (Solution 1) ← DO THIS NOW
2. Try Grok model (Solution 2) ← ALREADY TRIED
3. Run during EU morning hours (Solution 4) ← NEXT TIME
4. Add $5 OpenRouter credit if needed (Solution 3) ← IF STILL ISSUES

**Immediate Fix**:
```python
# ingestion/ai_similarity.py line ~110
async def are_incidents_duplicate(self, incident1: Dict, incident2: Dict):
    # Add this line before API call
    await asyncio.sleep(2)  # Rate limit protection
    
    try:
        response = await self.client.chat.completions.create(...)
```

---

## Quick Command

```bash
# Test with delays + Grok model
export OPENROUTER_MODEL="x-ai/grok-2-1212:free"
# (Add sleep(2) to code first)
python3 scripts/ai_deduplicate_batch.py --dry-run
```

---

**Status**: Rate limits hit on DeepSeek free tier
**Recommended Action**: Add 2-second delay + try Grok model
**Cost**: $0 (free solutions) or $5 (paid, lasts months)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
