-- Migration 021: Vector Embeddings for Semantic Duplicate Detection
-- Date: 2025-11-13
-- Purpose: Implement Tier 2 (embedding-based) duplicate detection using Google Gemini
-- Addresses: Semantic duplicates that differ in wording but describe same event
-- Related: DUPLICATE_DETECTION_2.0_PLAN.md - Tier 2 Embedding-Based Similarity
--
-- This migration implements:
-- 1. pgvector extension for vector similarity search
-- 2. incident_embeddings table (768-dim Google Gemini embeddings via OpenRouter)
-- 3. IVFFlat index for fast cosine similarity search
-- 4. find_similar_incidents() function for duplicate detection
--
-- Examples of semantic duplicates this catches:
--   "Copenhagen Airport" ≈ "Kastrup Airport" ≈ "CPH"
--   "drone sighting" ≈ "UAV spotted" ≈ "unmanned aircraft"
--   "closed temporarily" ≈ "operations suspended" ≈ "halted briefly"
--
-- Cost: ~$5-10/month (mostly OpenRouter API overhead)
-- Expected Impact: Catches 15-20% of duplicates that Tier 1 missed

BEGIN;

-- =====================================================
-- 1. Enable pgvector extension for vector operations
-- =====================================================

-- Install pgvector extension (if not already installed)
-- Provides VECTOR data type and similarity operators (<=> for cosine distance)
CREATE EXTENSION IF NOT EXISTS vector;

COMMENT ON EXTENSION vector IS
  'pgvector extension for vector similarity search - used for semantic duplicate detection';

-- =====================================================
-- 2. Create incident_embeddings table
-- =====================================================

CREATE TABLE IF NOT EXISTS incident_embeddings (
  -- Primary key: references incident
  incident_id UUID PRIMARY KEY REFERENCES incidents(id) ON DELETE CASCADE,

  -- Embedding vector (Google Gemini: 768 dimensions)
  -- Using OpenRouter API: google/gemini-embedding-004
  embedding VECTOR(768),

  -- Metadata for tracking and versioning
  embedding_model VARCHAR(50) DEFAULT 'google/gemini-embedding-004',
  embedding_version INTEGER DEFAULT 1,

  -- Timestamps for cache invalidation
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE incident_embeddings IS
  'Stores vector embeddings for semantic duplicate detection (Tier 2)';

COMMENT ON COLUMN incident_embeddings.embedding IS
  'Google Gemini 768-dimensional embedding vector - generated via OpenRouter API';

COMMENT ON COLUMN incident_embeddings.embedding_model IS
  'Model used to generate embedding (google/gemini-embedding-004)';

COMMENT ON COLUMN incident_embeddings.embedding_version IS
  'Version of embedding (allows re-generation if model changes)';

-- =====================================================
-- 3. Create indexes for fast similarity search
-- =====================================================

-- IVFFlat index for approximate nearest neighbor (ANN) search
-- Lists=100 is a good default for datasets <10,000 embeddings
-- This enables fast cosine similarity queries (<50ms for 1000+ incidents)
CREATE INDEX IF NOT EXISTS idx_incident_embeddings_cosine
  ON incident_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

COMMENT ON INDEX idx_incident_embeddings_cosine IS
  'IVFFlat index for fast cosine similarity search - enables <50ms queries for duplicate detection';

-- Index for timestamp-based queries (e.g., find stale embeddings)
CREATE INDEX IF NOT EXISTS idx_incident_embeddings_created_at
  ON incident_embeddings(created_at);

-- =====================================================
-- 4. Function to find similar incidents
-- =====================================================

CREATE OR REPLACE FUNCTION find_similar_incidents(
  query_embedding VECTOR(768),
  similarity_threshold FLOAT DEFAULT 0.85,
  max_results INTEGER DEFAULT 5,
  time_window_hours INTEGER DEFAULT 48,
  distance_km FLOAT DEFAULT 50,
  query_lat FLOAT DEFAULT NULL,
  query_lon FLOAT DEFAULT NULL
) RETURNS TABLE (
  incident_id UUID,
  similarity_score FLOAT,
  title TEXT,
  occurred_at TIMESTAMP,
  distance_km FLOAT,
  lat FLOAT,
  lon FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    i.id,
    -- Convert cosine distance to similarity score (1 - distance)
    -- Score of 1.0 = identical, 0.85+ = very similar, <0.80 = different
    1 - (e.embedding <=> query_embedding) as similarity,
    i.title,
    i.occurred_at,
    -- Calculate geographic distance if query coordinates provided
    CASE
      WHEN query_lat IS NOT NULL AND query_lon IS NOT NULL THEN
        ST_Distance(
          i.location::geography,
          ST_SetSRID(ST_MakePoint(query_lon, query_lat), 4326)::geography
        ) / 1000  -- Convert meters to kilometers
      ELSE 0
    END as distance_km,
    ST_Y(i.location::geometry) as lat,
    ST_X(i.location::geometry) as lon
  FROM incident_embeddings e
  JOIN incidents i ON e.incident_id = i.id
  WHERE
    -- Similarity threshold (cosine similarity >= threshold)
    1 - (e.embedding <=> query_embedding) >= similarity_threshold
    -- Temporal filter (within time window)
    AND i.occurred_at >= NOW() - INTERVAL '1 hour' * time_window_hours
    -- Spatial filter (within distance, if coordinates provided)
    AND (
      query_lat IS NULL OR query_lon IS NULL OR
      ST_DWithin(
        i.location::geography,
        ST_SetSRID(ST_MakePoint(query_lon, query_lat), 4326)::geography,
        distance_km * 1000  -- Convert km to meters
      )
    )
  ORDER BY similarity DESC
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION find_similar_incidents IS
  'Find semantically similar incidents using vector embeddings - used for Tier 2 duplicate detection';

-- =====================================================
-- 5. Function to update embedding timestamp
-- =====================================================

CREATE OR REPLACE FUNCTION update_embedding_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update timestamp
DROP TRIGGER IF EXISTS incident_embeddings_updated_at_trigger ON incident_embeddings;

CREATE TRIGGER incident_embeddings_updated_at_trigger
  BEFORE UPDATE ON incident_embeddings
  FOR EACH ROW
  EXECUTE FUNCTION update_embedding_timestamp();

-- =====================================================
-- 6. View for embedding statistics
-- =====================================================

CREATE OR REPLACE VIEW embedding_stats AS
SELECT
  COUNT(*) as total_embeddings,
  COUNT(DISTINCT embedding_model) as unique_models,
  MAX(created_at) as latest_embedding,
  MIN(created_at) as oldest_embedding,
  -- Storage size (768 floats * 4 bytes = 3.072 KB per embedding)
  pg_size_pretty(pg_total_relation_size('incident_embeddings')) as storage_size
FROM incident_embeddings;

COMMENT ON VIEW embedding_stats IS
  'Statistics about stored embeddings - useful for monitoring and capacity planning';

-- =====================================================
-- 7. Validation and statistics
-- =====================================================

DO $$
DECLARE
  incident_count INTEGER;
  embedding_count INTEGER;
  coverage_pct NUMERIC;
BEGIN
  SELECT COUNT(*) INTO incident_count FROM incidents;
  SELECT COUNT(*) INTO embedding_count FROM incident_embeddings;

  IF incident_count > 0 THEN
    coverage_pct := ROUND((embedding_count::NUMERIC / incident_count) * 100, 2);
  ELSE
    coverage_pct := 0;
  END IF;

  RAISE NOTICE 'Migration 021 Complete:';
  RAISE NOTICE '  Total incidents: %', incident_count;
  RAISE NOTICE '  Incidents with embeddings: %', embedding_count;
  RAISE NOTICE '  Coverage: %%%', coverage_pct;
  RAISE NOTICE '';
  RAISE NOTICE 'Tier 2 duplicate detection is now enabled!';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '  1. Backfill embeddings for existing incidents (background job)';
  RAISE NOTICE '  2. Configure OPENROUTER_API_KEY environment variable';
  RAISE NOTICE '  3. Monitor usage at https://openrouter.ai/activity';
END $$;

COMMIT;

-- =====================================================
-- Post-Migration Notes
-- =====================================================

-- This migration implements Tier 2 of the 3-tier duplicate detection system:
--
-- TIER 2 (Embeddings) - $5-10/month, 50-100ms latency
--   - Catches: 15-20% of duplicates (semantic variations)
--   - Method: Vector similarity search (cosine distance)
--   - Model: Google Gemini Embedding (768 dims) via OpenRouter
--   - Threshold: 0.85+ similarity = potential duplicate
--
-- How it works:
--   1. Convert incident to text: "Event: X | Location: Y | Type: Z | Description: ..."
--   2. Generate embedding via OpenRouter API (google/gemini-embedding-004)
--   3. Store in incident_embeddings table
--   4. For new incidents, search for similar embeddings (cosine similarity)
--   5. If similarity >= 0.92: Auto-merge as duplicate
--   6. If similarity 0.85-0.92: Send to Tier 3 (LLM reasoning)
--   7. If similarity < 0.85: Treat as unique incident
--
-- Usage example:
--   -- Find incidents similar to incident ID 'abc-123'
--   SELECT * FROM find_similar_incidents(
--     (SELECT embedding FROM incident_embeddings WHERE incident_id = 'abc-123'),
--     0.85,  -- similarity threshold
--     5,     -- max results
--     48,    -- time window (hours)
--     50     -- distance (km)
--   );
--
-- Cost breakdown:
--   - Embedding generation: ~$0 (OpenRouter free tier)
--   - Storage: ~3 KB per incident (768 floats * 4 bytes)
--   - Query cost: <1ms for index search
--
-- Testing:
--   1. Insert test embedding: INSERT INTO incident_embeddings (incident_id, embedding) VALUES (...);
--   2. Test similarity search: SELECT * FROM embedding_stats;
--   3. Verify index is used: EXPLAIN ANALYZE SELECT * FROM find_similar_incidents(...);
