"""
Example integration of Tier 3 LLM deduplicator into ingestion pipeline.

This shows how to integrate the OpenRouter LLM deduplicator after Tier 2
embedding similarity check for borderline cases (0.80-0.92 similarity).
"""

import asyncio
import logging
from typing import Dict, Optional, Tuple
import asyncpg

from openrouter_llm_deduplicator import OpenRouterLLMDeduplicator

logger = logging.getLogger(__name__)


class DuplicateDetectionPipeline:
    """
    Complete 3-tier duplicate detection pipeline.

    Tier 1: Hash-based (instant, 70-80% of duplicates)
    Tier 2: Embedding similarity (50-100ms, 15-20% of duplicates)
    Tier 3: LLM reasoning (300-500ms, 5-10% of duplicates)
    """

    def __init__(self, db_pool: asyncpg.Pool):
        self.db = db_pool

        # Initialize Tier 3 LLM deduplicator
        self.llm_dedup = OpenRouterLLMDeduplicator(confidence_threshold=0.80)

        # Thresholds
        self.TIER2_HIGH_CONFIDENCE = 0.92  # Above this: auto-merge
        self.TIER2_LOW_CONFIDENCE = 0.80   # Below this: auto-create new
        # Between 0.80-0.92: Use Tier 3 LLM

    async def check_duplicate(
        self,
        new_incident: Dict
    ) -> Tuple[Optional[str], str, float]:
        """
        Check if incident is duplicate using 3-tier system.

        Args:
            new_incident: Incident data with title, location, narrative, etc.

        Returns:
            (duplicate_id, reason, confidence)
            - duplicate_id: UUID of existing incident if duplicate, else None
            - reason: Human-readable explanation
            - confidence: 0.0-1.0 confidence score
        """
        # TIER 1: Hash-based check (instant)
        duplicate_id = await self._check_hash_duplicate(new_incident)
        if duplicate_id:
            logger.info(f"Tier 1: Hash duplicate detected: {duplicate_id}")
            return (duplicate_id, "Exact duplicate (hash match)", 1.0)

        # TIER 2: Embedding similarity check (50-100ms)
        embedding_match = await self._check_embedding_duplicate(new_incident)

        if not embedding_match:
            # No similar incidents found
            logger.info("Tier 2: No similar incidents found, creating new")
            return (None, "No duplicates found", 0.0)

        duplicate_id, similarity, tier2_reason = embedding_match

        # High confidence match (>0.92) - skip LLM
        if similarity >= self.TIER2_HIGH_CONFIDENCE:
            logger.info(
                f"Tier 2: High confidence duplicate (similarity: {similarity:.2f})",
                extra={'duplicate_id': duplicate_id}
            )
            return (duplicate_id, tier2_reason, similarity)

        # Low confidence match (<0.80) - not duplicate
        if similarity < self.TIER2_LOW_CONFIDENCE:
            logger.info(f"Tier 2: Low confidence match (similarity: {similarity:.2f}), creating new")
            return (None, "Different incident (low similarity)", 1 - similarity)

        # TIER 3: Borderline case (0.80-0.92) - use LLM reasoning
        logger.info(
            f"Tier 2: Borderline match (similarity: {similarity:.2f}), escalating to LLM",
            extra={'duplicate_id': duplicate_id}
        )

        # Fetch full details of candidate
        candidate = await self._fetch_incident_details(duplicate_id)

        # LLM analysis
        llm_result = await self.llm_dedup.analyze_potential_duplicate(
            new_incident=new_incident,
            candidate=candidate,
            similarity_score=similarity
        )

        if llm_result is None:
            # LLM unavailable - use Tier 2 decision (conservative: merge)
            logger.warning(
                "Tier 3: LLM unavailable, accepting Tier 2 decision",
                extra={'duplicate_id': duplicate_id, 'similarity': similarity}
            )
            return (duplicate_id, f"{tier2_reason} (LLM unavailable)", similarity)

        # Parse LLM result
        is_duplicate, llm_reasoning, confidence = llm_result

        if is_duplicate and confidence >= self.llm_dedup.confidence_threshold:
            logger.info(
                f"Tier 3: LLM confirmed duplicate (confidence: {confidence:.2f})",
                extra={
                    'duplicate_id': duplicate_id,
                    'reasoning': llm_reasoning,
                    'embedding_similarity': similarity
                }
            )
            return (duplicate_id, llm_reasoning, confidence)
        else:
            logger.info(
                f"Tier 3: LLM classified as unique (confidence: {confidence:.2f})",
                extra={
                    'reasoning': llm_reasoning,
                    'embedding_similarity': similarity
                }
            )
            return (None, llm_reasoning, confidence)

    async def _check_hash_duplicate(self, incident: Dict) -> Optional[str]:
        """Tier 1: Check for exact hash match."""
        # Implementation would use content_hash from migration 018
        # This is a placeholder
        return None

    async def _check_embedding_duplicate(
        self,
        incident: Dict
    ) -> Optional[Tuple[str, float, str]]:
        """Tier 2: Check for embedding similarity match."""
        # Implementation would use incident_embeddings table
        # This is a placeholder that returns borderline case for demo
        return ("test-uuid-123", 0.88, "High semantic similarity; nearby location")

    async def _fetch_incident_details(self, incident_id: str) -> Dict:
        """Fetch full incident details for LLM analysis."""
        row = await self.db.fetchrow("""
            SELECT
                id,
                title,
                occurred_at,
                location_name,
                ST_Y(location::geometry) as lat,
                ST_X(location::geometry) as lon,
                narrative,
                asset_type,
                country,
                evidence_score,
                (SELECT COUNT(*) FROM incident_sources WHERE incident_id = i.id) as source_count
            FROM incidents i
            WHERE id = $1
        """, incident_id)

        return dict(row)


# Example usage
async def example_ingestion():
    """Example: Ingest new incident with duplicate detection"""

    # Mock database connection
    db_pool = None  # In production: await asyncpg.create_pool(DATABASE_URL)

    pipeline = DuplicateDetectionPipeline(db_pool)

    # New incident being ingested
    new_incident = {
        'title': 'Drone sighting at Copenhagen Airport',
        'occurred_at': '2025-10-02 14:30:00',
        'location_name': 'Copenhagen Airport (Kastrup)',
        'lat': 55.6181,
        'lon': 12.6508,
        'narrative': 'Copenhagen Airport temporarily closed airspace after drone spotted near runway.',
        'asset_type': 'airport',
        'country': 'Denmark',
        'source_type': 'news',
        'source_name': 'DR News'
    }

    # Check for duplicates
    duplicate_id, reason, confidence = await pipeline.check_duplicate(new_incident)

    if duplicate_id:
        print(f"✓ DUPLICATE DETECTED")
        print(f"  Existing Incident ID: {duplicate_id}")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Reason: {reason}")
        print(f"  Action: Merge with existing incident")
    else:
        print(f"✗ UNIQUE INCIDENT")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Reason: {reason}")
        print(f"  Action: Create new incident")


if __name__ == '__main__':
    asyncio.run(example_ingestion())
