# Database Migrations 020-022: AI-Powered Duplicate Detection
## Summary Report

**Date**: 2025-11-13
**Author**: Claude Code
**Status**: Ready for Review & Testing
**Total Lines**: 793 lines across 3 migrations

---

## Overview

Created three database migration files implementing the AI-powered duplicate detection system as specified in `DUPLICATE_DETECTION_2.0_PLAN.md`. These migrations establish the foundation for a 3-tier duplicate prevention system with expected 99.9% accuracy.

---

## Migration Files Created

### 1. Migration 020: Enhanced Content Hash (197 lines)
**File**: `/home/user/DroneWatch2.0/migrations/020_enhanced_content_hash.sql`

**Purpose**: Implement Tier 1 (Hash-Based) duplicate detection at database level

**Key Features**:
- `content_hash` column with MD5 hash of (date + location + normalized_title + asset_type)
- `normalized_title` column (lowercase, alphanumeric only for semantic matching)
- `location_hash` column (rounded coords to 3 decimals ~110m precision + asset_type)
- **UNIQUE constraint on `content_hash`** - prevents exact duplicates from being inserted
- Automatic hash generation via `update_incident_hashes()` trigger
- Backfills hashes for all existing incidents
- GIN full-text search index on `normalized_title`

**Expected Impact**:
- Catches 70-80% of duplicates at database level
- 0ms latency (O(1) hash lookup)
- $0 cost
- Prevents duplicate insertion with unique constraint violation

**Tables Modified**:
- `incidents` - Added 3 columns (content_hash, normalized_title, location_hash)

**Functions Created**:
- `update_incident_hashes()` - Auto-generates hashes on INSERT/UPDATE

**Indexes Created**:
- `idx_incidents_location_hash` - Fast spatial lookup
- `idx_incidents_normalized_title` - Full-text search for semantic matching
- `idx_incidents_content_hash` - Explicit hash lookup (redundant with unique constraint)

**Idempotency**: ✓ All operations use `IF NOT EXISTS` / `IF EXISTS` checks

---

### 2. Migration 021: Vector Embeddings (260 lines)
**File**: `/home/user/DroneWatch2.0/migrations/021_vector_embeddings.sql`

**Purpose**: Implement Tier 2 (Embedding-Based) semantic duplicate detection using Google Gemini embeddings via OpenRouter

**Key Features**:
- Enables `pgvector` extension for vector operations
- `incident_embeddings` table with 768-dimensional vectors (Google Gemini)
- IVFFlat index for fast cosine similarity search (<50ms for 1000+ incidents)
- `find_similar_incidents()` function with spatial + temporal filtering
- `embedding_stats` view for monitoring and capacity planning
- Automatic `updated_at` timestamp via trigger

**Expected Impact**:
- Catches 15-20% of duplicates that Tier 1 missed (semantic variations)
- 50-100ms latency (includes vector similarity search)
- $5-10/month cost (mostly OpenRouter API overhead)
- Handles semantic equivalents: "Copenhagen Airport" ≈ "Kastrup Airport" ≈ "CPH"

**Tables Created**:
- `incident_embeddings` (incident_id, embedding[768], model, version, timestamps)

**Functions Created**:
- `find_similar_incidents(embedding, threshold, max_results, time_window, distance_km, lat, lon)` - Returns similar incidents with similarity scores
- `update_embedding_timestamp()` - Auto-updates timestamp on embedding changes

**Views Created**:
- `embedding_stats` - Storage size, count, model distribution

**Indexes Created**:
- `idx_incident_embeddings_cosine` - IVFFlat index (lists=100) for approximate nearest neighbor search
- `idx_incident_embeddings_created_at` - Temporal queries

**Model Configuration**:
- **Model**: `google/gemini-embedding-004` (via OpenRouter)
- **Dimensions**: 768
- **Similarity Metric**: Cosine distance (1 - cosine_distance = similarity score)
- **Threshold**: 0.85+ = potential duplicate, 0.92+ = high confidence duplicate

**Idempotency**: ✓ All operations use `IF NOT EXISTS` checks

---

### 3. Migration 022: User Feedback System (336 lines)
**File**: `/home/user/DroneWatch2.0/migrations/022_duplicate_feedback.sql`

**Purpose**: Enable continuous learning through user feedback on AI duplicate detection decisions

**Key Features**:
- `duplicate_feedback` table for user feedback on AI decisions
- Tracks AI decision context (tier, similarity score, verdict, reasoning)
- `duplicate_feedback_analysis` view with precision/recall metrics
- `get_recommended_thresholds()` function for threshold optimization
- Supports 3 feedback types: 'merge', 'separate', 'unsure'

**Expected Impact**:
- Self-improving duplicate detection system
- Identifies when AI is wrong (false positives/negatives)
- Enables threshold optimization based on real-world feedback
- Achieves 99%+ accuracy over time

**Tables Created**:
- `duplicate_feedback` (incident pairs, user feedback, AI decision context)

**Functions Created**:
- `get_recommended_thresholds()` - Analyzes feedback and returns precision/recall/F1 scores for each tier

**Views Created**:
- `duplicate_feedback_analysis` - Aggregates feedback by tier and type, calculates metrics

**Indexes Created**:
- `idx_duplicate_feedback_type` - Filter by feedback type
- `idx_duplicate_feedback_similarity` - Analyze similarity distributions
- `idx_duplicate_feedback_tier` - Tier-specific analysis
- `idx_duplicate_feedback_created` - Temporal analysis
- `idx_duplicate_feedback_verdict_type` - Precision/recall calculations

**Metrics Calculated**:
- **Precision**: TP / (TP + FP) - How many AI duplicates are correct?
- **Recall**: TP / (TP + FN) - How many real duplicates does AI catch?
- **F1 Score**: Harmonic mean of precision and recall

**Idempotency**: ✓ All operations use `IF NOT EXISTS` checks

---

## Validation Results

**Transaction Blocks**: ✓ All migrations have proper BEGIN/COMMIT blocks
**Idempotency**: ✓ All operations are safe to run multiple times
**Comments**: ✓ Comprehensive documentation in each migration
**Indexes**: ✓ All indexes properly named with `IF NOT EXISTS`
**Constraints**: ✓ Named constraints with check conditions
**Error Handling**: ✓ Proper error handling with DO blocks

**SQL Syntax**: Not validated (no database connection available)
**Recommendation**: Test migrations in staging environment before production

---

## Execution Order

**IMPORTANT**: These migrations must be executed in order:

1. **Migration 020** (Enhanced Content Hash)
   - Creates base columns and hash logic
   - Establishes Tier 1 duplicate prevention

2. **Migration 021** (Vector Embeddings)
   - Depends on pgvector extension
   - Establishes Tier 2 duplicate detection

3. **Migration 022** (User Feedback)
   - Depends on incidents table (created in earlier migrations)
   - Establishes continuous learning system

**Execution Command**:
```bash
# Test in staging first
psql "postgresql://...@...pooler.supabase.com:5432/postgres" -f migrations/020_enhanced_content_hash.sql
psql "postgresql://...@...pooler.supabase.com:5432/postgres" -f migrations/021_vector_embeddings.sql
psql "postgresql://...@...pooler.supabase.com:5432/postgres" -f migrations/022_duplicate_feedback.sql
```

**Port Note**: Use port **5432** (direct connection) for migrations, NOT port 6543 (transaction pooler)

---

## Integration Requirements

### Environment Variables (Required)
```bash
# Add to Vercel environment variables
OPENROUTER_API_KEY="sk-or-v1-..."
OPENROUTER_EMBEDDING_MODEL="google/gemini-embedding-004"  # Default if not set
```

### Python Dependencies (Add to requirements.txt)
```
# Vector embeddings
openai>=1.0.0           # OpenRouter is OpenAI-compatible
numpy>=1.24.0           # Vector operations
```

### Code Changes Required

**File**: `frontend/api/ingest.py`
- Add Tier 1 hash duplicate check (before database insert)
- Add Tier 2 embedding generation and similarity search
- Add Tier 3 LLM reasoning for borderline cases (0.85-0.92 similarity)

**File**: `ingestion/embedding_deduplicator.py` (NEW)
- Create embedding generation service
- Implement similarity search logic
- Handle OpenRouter API calls

**File**: `ingestion/llm_deduplicator.py` (NEW)
- Create LLM reasoning service for edge cases
- Implement prompt engineering for duplicate analysis

**File**: `frontend/api/duplicate-feedback.py` (NEW)
- Create POST endpoint for user feedback
- Validate feedback and store in database

**Frontend**: `components/DuplicateFeedbackButton.tsx` (NEW)
- Add feedback UI component for incident pairs
- Integrate with `/api/duplicate-feedback` endpoint

---

## Testing Checklist

### Migration 020 (Content Hash)
- [ ] Run migration in staging
- [ ] Verify `content_hash` populated for existing incidents
- [ ] Try inserting duplicate incident → should fail with unique constraint violation
- [ ] Verify trigger auto-generates hashes on new inserts
- [ ] Check indexes created: `\d incidents` in psql

### Migration 021 (Vector Embeddings)
- [ ] Run migration in staging
- [ ] Verify `pgvector` extension enabled: `SELECT * FROM pg_extension WHERE extname = 'vector';`
- [ ] Test embedding insertion: `INSERT INTO incident_embeddings (...)`
- [ ] Test similarity search: `SELECT * FROM find_similar_incidents(...)`
- [ ] Verify IVFFlat index created: `\d incident_embeddings`
- [ ] Check embedding_stats view: `SELECT * FROM embedding_stats;`

### Migration 022 (User Feedback)
- [ ] Run migration in staging
- [ ] Insert test feedback: `INSERT INTO duplicate_feedback (...)`
- [ ] Query analysis view: `SELECT * FROM duplicate_feedback_analysis;`
- [ ] Get threshold recommendations: `SELECT * FROM get_recommended_thresholds();`
- [ ] Verify unique constraint on incident pairs

### Integration Testing
- [ ] Generate embedding for test incident via OpenRouter
- [ ] Store embedding in `incident_embeddings` table
- [ ] Search for similar incidents using `find_similar_incidents()`
- [ ] Submit user feedback via API endpoint
- [ ] Verify feedback appears in `duplicate_feedback_analysis`

---

## Rollback Plan

If issues occur in production, roll back in reverse order:

```sql
-- Rollback Migration 022
BEGIN;
DROP VIEW IF EXISTS duplicate_feedback_analysis;
DROP FUNCTION IF EXISTS get_recommended_thresholds();
DROP TABLE IF EXISTS duplicate_feedback;
COMMIT;

-- Rollback Migration 021
BEGIN;
DROP VIEW IF EXISTS embedding_stats;
DROP FUNCTION IF EXISTS find_similar_incidents(VECTOR, FLOAT, INTEGER, INTEGER, FLOAT, FLOAT, FLOAT);
DROP FUNCTION IF EXISTS update_embedding_timestamp();
DROP TABLE IF EXISTS incident_embeddings;
DROP EXTENSION IF EXISTS vector;
COMMIT;

-- Rollback Migration 020
BEGIN;
DROP TRIGGER IF EXISTS incident_hashes_trigger ON incidents;
DROP FUNCTION IF EXISTS update_incident_hashes();
DROP INDEX IF EXISTS idx_incidents_content_hash;
DROP INDEX IF EXISTS idx_incidents_normalized_title;
DROP INDEX IF EXISTS idx_incidents_location_hash;
ALTER TABLE incidents DROP CONSTRAINT IF EXISTS incidents_content_hash_unique;
ALTER TABLE incidents DROP COLUMN IF EXISTS location_hash;
ALTER TABLE incidents DROP COLUMN IF EXISTS normalized_title;
ALTER TABLE incidents DROP COLUMN IF EXISTS content_hash;
COMMIT;
```

**Important**: Rollback scripts should be tested in staging first!

---

## Cost Estimates

### Operational Costs (Monthly)
| Component | Cost | Notes |
|-----------|------|-------|
| Tier 1: Hash-Based | $0 | Free (local computation) |
| Tier 2: Embeddings | $5-10 | OpenRouter free tier + overhead |
| Tier 3: LLM Reasoning | $7-10 | Claude Haiku (~20 cases/month) |
| Storage: Embeddings | <$1 | 3KB per incident × 200/month = 0.6MB |
| **Total** | **$12-20/month** | Scales sub-linearly with volume |

### Storage Impact
- **Content Hash**: 32 bytes per incident (VARCHAR(32))
- **Normalized Title**: ~50-200 bytes per incident (TEXT)
- **Location Hash**: 16 bytes per incident (VARCHAR(16))
- **Embedding Vector**: 3,072 bytes per incident (768 floats × 4 bytes)
- **Total**: ~3.4 KB per incident

For 1,000 incidents: ~3.4 MB total storage (negligible)

---

## Expected Performance

### Duplicate Detection Latency
- **Tier 1** (Hash): <1ms (O(1) hash lookup)
- **Tier 2** (Embeddings): 50-100ms (IVFFlat ANN search + OpenRouter API)
- **Tier 3** (LLM): 300-500ms (Claude Haiku API call)

### Catch Rates (Estimated)
- **Tier 1**: 70-80% of duplicates (exact matches)
- **Tier 2**: 15-20% of duplicates (semantic variations)
- **Tier 3**: 5-10% of duplicates (edge cases)
- **Total**: 99.9% duplicate prevention rate

### False Positive Rate (Target)
- **Tier 1**: <0.1% (hash collisions extremely rare)
- **Tier 2**: <5% (with threshold 0.92, conservative)
- **Tier 3**: <1% (LLM reasoning with confidence 0.80+)

---

## Next Steps

### Phase 1: Database Deployment (Day 1, 2 hours)
1. Test migrations in staging environment
2. Review EXPLAIN ANALYZE for performance
3. Deploy to production (use port 5432)
4. Verify all indexes created
5. Backfill content_hash for existing incidents
6. Update migration tracking table

### Phase 2: Python Implementation (Day 2, 6 hours)
1. Create `ingestion/embedding_deduplicator.py`
2. Create `ingestion/llm_deduplicator.py`
3. Update `frontend/api/ingest.py` with 3-tier logic
4. Add OpenRouter API integration
5. Add comprehensive logging and monitoring

### Phase 3: Frontend Integration (Day 3, 4 hours)
1. Create `/api/duplicate-feedback` endpoint
2. Create `DuplicateFeedbackButton` component
3. Add feedback UI to incident popups
4. Implement feedback submission logic

### Phase 4: Testing & Monitoring (Day 4, 4 hours)
1. End-to-end testing with real incidents
2. Performance benchmarking
3. Cost monitoring setup
4. Deploy to production with feature flag
5. Monitor for 48 hours

---

## Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Duplicate Rate | ~5% | <0.1% | Duplicates / Total Incidents |
| Precision | ~95% | >99% | TP / (TP + FP) |
| Recall | ~90% | >95% | TP / (TP + FN) |
| Avg Latency | ~200ms | <400ms | API response time |
| Cost per Incident | $0 | <$0.10 | Monthly cost / Incident count |

---

## Notes and Considerations

### pgvector Extension
- **Requirement**: Supabase has pgvector pre-installed (verify with `SELECT * FROM pg_extension;`)
- **Version**: Uses pgvector 0.5.0+ for IVFFlat index support
- **Index Tuning**: `lists = 100` is optimal for <10,000 incidents. Increase to 500 for 10,000-100,000 incidents.

### OpenRouter vs OpenAI
- **OpenRouter**: Chosen for free tier and model flexibility
- **Model**: `google/gemini-embedding-004` (768 dimensions, free tier)
- **Alternative**: `text-embedding-3-small` (1536 dimensions, $0.02/1M tokens) if free tier exhausted
- **Compatibility**: OpenRouter is OpenAI-compatible (same Python SDK)

### Threshold Tuning
- **Initial Thresholds**: Conservative (prefer false negatives over false positives)
  - Tier 1: 1.0 (exact hash match)
  - Tier 2: 0.85 (high similarity)
  - Tier 3: 0.80 (LLM confidence)
- **Optimization**: Thresholds will be adjusted based on user feedback
- **Goal**: Maximize F1 score (balance precision and recall)

### Data Privacy
- **User Feedback**: No personally identifiable information stored
- **User ID**: Optional field for future user accounts
- **AI Reasoning**: Stored for transparency and debugging (no sensitive data)

---

## Files Created

1. `/home/user/DroneWatch2.0/migrations/020_enhanced_content_hash.sql` (197 lines)
2. `/home/user/DroneWatch2.0/migrations/021_vector_embeddings.sql` (260 lines)
3. `/home/user/DroneWatch2.0/migrations/022_duplicate_feedback.sql` (336 lines)
4. `/home/user/DroneWatch2.0/MIGRATION_SUMMARY_020-022.md` (this file)

**Total**: 793 lines of SQL + comprehensive documentation

---

## Approval Status

**Status**: ✅ Ready for Review
**Next Action**: User approval to proceed with Phase 1 (Database Deployment)
**Estimated Timeline**: 3-4 days from approval to production-ready
**Risk Level**: LOW (graceful degradation, easy rollback)

**Recommendation**: APPROVE & PROCEED with phased rollout in staging first.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-13
**Author**: Claude Code (AI Assistant)
**Related**: `DUPLICATE_DETECTION_2.0_PLAN.md`
