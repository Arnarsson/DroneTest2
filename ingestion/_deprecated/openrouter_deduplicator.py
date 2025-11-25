"""
Tier 2: Semantic duplicate detection using OpenRouter embeddings.

Uses Google Gemini Embedding (FREE tier):
- Model: google/gemini-embedding-004
- Dimensions: 768
- Cost: FREE (within 1M tokens/day limit)
- Quality: Excellent semantic understanding
"""

import os
import asyncio
import asyncpg
from openai import AsyncOpenAI
from typing import List, Dict, Optional, Tuple
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenRouterEmbeddingDeduplicator:
    """
    FREE semantic duplicate detection using OpenRouter + Gemini.

    No recurring costs within Gemini free tier (1M tokens/day).
    Catches semantic duplicates that hash-based can't:
    - "Copenhagen Airport" ≈ "Kastrup Airport" ≈ "CPH"
    - "drone sighting" ≈ "UAV spotted" ≈ "unmanned aircraft"
    """

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        similarity_threshold: float = 0.85,
        model: str = "google/gemini-embedding-004"
    ):
        """
        Initialize with OpenRouter client.

        Args:
            db_pool: AsyncPG connection pool
            similarity_threshold: Cosine similarity threshold (0.85 = 85% similar)
            model: OpenRouter model ID (default: free Gemini)
        """
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.db = db_pool
        self.threshold = similarity_threshold
        self.model = model
        logger.info(f"Initialized OpenRouter embedding deduplicator with {model}")

    async def generate_embedding(self, incident: Dict) -> List[float]:
        """
        Generate 768-dimensional embedding using Gemini (FREE).

        Args:
            incident: Dict with keys: title, location_name, city, asset_type, occurred_at, narrative

        Returns:
            List of floats for PostgreSQL vector storage (768 dimensions)

        Example:
            >>> incident = {
            ...     'title': 'Drone closes Copenhagen Airport',
            ...     'location_name': 'Kastrup Airport',
            ...     'asset_type': 'airport',
            ...     'occurred_at': datetime.now(),
            ...     'narrative': 'A drone was spotted...'
            ... }
            >>> embedding = await dedup.generate_embedding(incident)
            >>> len(embedding)
            768
        """
        text = self._construct_embedding_text(incident)

        try:
            # Call OpenRouter API (Gemini free tier)
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                extra_headers={
                    "HTTP-Referer": "https://dronemap.cc",
                    "X-Title": "DroneWatch Duplicate Detection"
                }
            )

            embedding = response.data[0].embedding

            logger.debug(f"Generated embedding for incident: {incident.get('title', 'Unknown')[:50]}")

            return embedding  # List[float], length 768

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def _construct_embedding_text(self, incident: Dict) -> str:
        """
        Construct rich text representation for embedding.

        Include all semantic information:
        - Title (event description)
        - Location (facility name)
        - Asset type (category)
        - Date (temporal context)
        - Narrative excerpt (details)

        Args:
            incident: Incident dictionary

        Returns:
            Concatenated text string for embedding

        Examples:
            >>> incident = {'title': 'Drone closes airport', 'location_name': 'Kastrup', 'asset_type': 'airport'}
            >>> text = dedup._construct_embedding_text(incident)
            >>> 'Event: Drone closes airport' in text
            True
        """
        parts = []

        if incident.get('title'):
            parts.append(f"Event: {incident['title']}")

        if incident.get('location_name'):
            parts.append(f"Location: {incident['location_name']}")
        elif incident.get('city'):
            parts.append(f"City: {incident['city']}")

        # Asset type with synonyms
        asset_type = incident.get('asset_type', 'other')
        asset_labels = {
            'airport': 'airport aerodrome airfield',
            'military': 'military base defense facility',
            'harbor': 'harbor port seaport',
            'powerplant': 'power plant energy facility',
            'bridge': 'bridge overpass',
            'other': 'area location'
        }
        parts.append(f"Type: {asset_labels.get(asset_type, asset_type)}")

        if incident.get('occurred_at'):
            # Handle both datetime and string
            if isinstance(incident['occurred_at'], datetime):
                parts.append(f"Date: {incident['occurred_at'].strftime('%Y-%m-%d')}")
            else:
                parts.append(f"Date: {incident['occurred_at']}")

        if incident.get('narrative'):
            excerpt = incident['narrative'][:200].strip()
            if len(incident['narrative']) > 200:
                excerpt += "..."
            parts.append(f"Details: {excerpt}")

        return " | ".join(parts)

    async def find_duplicate(
        self,
        incident: Dict,
        time_window_hours: int = 48,
        distance_km: float = 50
    ) -> Optional[Tuple[str, float, str]]:
        """
        Find if incident is duplicate using embedding similarity.

        Args:
            incident: New incident dict with title, lat, lon, occurred_at, etc.
            time_window_hours: Look back this many hours (default 48)
            distance_km: Search within this radius (default 50km)

        Returns:
            (incident_id, similarity_score, explanation) if duplicate found
            None if unique

        Example:
            >>> incident = {'title': 'Drone at Kastrup', 'lat': 55.6181, 'lon': 12.6561}
            >>> result = await dedup.find_duplicate(incident)
            >>> if result:
            ...     incident_id, similarity, explanation = result
            ...     print(f"Duplicate found: {similarity:.2%} similar")
        """
        # Generate embedding for new incident (FREE API call)
        try:
            query_embedding = await self.generate_embedding(incident)
        except Exception as e:
            logger.error(f"Failed to generate embedding for duplicate check: {e}")
            return None

        # Find similar incidents using pgvector
        try:
            similar = await self.db.fetch("""
                SELECT * FROM find_similar_incidents(
                    $1::vector,
                    $2,  -- similarity_threshold
                    5,   -- max_results
                    $3,  -- time_window_hours
                    $4,  -- distance_km
                    $5,  -- query_lat
                    $6   -- query_lon
                )
            """,
                query_embedding,
                self.threshold,
                time_window_hours,
                distance_km,
                incident.get('lat'),
                incident.get('lon')
            )
        except Exception as e:
            logger.error(f"Failed to query similar incidents: {e}")
            return None

        if not similar:
            logger.debug(f"No similar incidents found for: {incident.get('title', 'Unknown')[:50]}")
            return None

        # Return best match with explanation
        best = similar[0]
        explanation = self._explain_match(incident, best)

        logger.info(f"Duplicate found: {best['title'][:50]} (similarity: {best['similarity_score']:.2%})")

        return (
            str(best['incident_id']),
            float(best['similarity_score']),
            explanation
        )

    def _explain_match(self, new: Dict, existing: Dict) -> str:
        """
        Generate human-readable explanation of duplicate match.

        Args:
            new: New incident dict
            existing: Existing incident record from database

        Returns:
            Human-readable explanation string

        Examples:
            >>> explanation = dedup._explain_match(new_incident, existing_record)
            >>> print(explanation)
            'very high similarity (95.3%); same location (120m); within same hour'
        """
        reasons = []

        similarity = float(existing['similarity_score'])
        distance_km = float(existing['distance_km'])

        # Similarity level
        if similarity >= 0.95:
            reasons.append(f"very high similarity ({similarity:.1%})")
        elif similarity >= 0.90:
            reasons.append(f"high similarity ({similarity:.1%})")
        else:
            reasons.append(f"moderate similarity ({similarity:.1%})")

        # Distance
        if distance_km < 1:
            reasons.append(f"same location ({distance_km*1000:.0f}m)")
        elif distance_km < 5:
            reasons.append(f"nearby ({distance_km:.1f}km)")
        else:
            reasons.append(f"within region ({distance_km:.0f}km)")

        # Time difference
        if 'occurred_at' in new and 'occurred_at' in existing:
            new_time = new['occurred_at']
            existing_time = existing['occurred_at']

            # Handle both datetime and string
            if not isinstance(new_time, datetime):
                new_time = datetime.fromisoformat(str(new_time))
            if not isinstance(existing_time, datetime):
                existing_time = datetime.fromisoformat(str(existing_time))

            time_diff_hours = abs(
                (new_time - existing_time).total_seconds() / 3600
            )

            if time_diff_hours < 1:
                reasons.append("within same hour")
            elif time_diff_hours < 24:
                reasons.append(f"{time_diff_hours:.1f}h apart")
            else:
                reasons.append(f"{time_diff_hours/24:.1f}d apart")

        return "; ".join(reasons)

    async def store_embedding(self, incident_id: str, embedding: List[float]):
        """
        Store embedding in database for future similarity searches.

        Args:
            incident_id: UUID of incident
            embedding: 768-dimensional vector from Gemini

        Example:
            >>> incident_id = "123e4567-e89b-12d3-a456-426614174000"
            >>> embedding = await dedup.generate_embedding(incident)
            >>> await dedup.store_embedding(incident_id, embedding)
        """
        try:
            await self.db.execute("""
                INSERT INTO incident_embeddings (incident_id, embedding, embedding_model)
                VALUES ($1, $2::vector, $3)
                ON CONFLICT (incident_id)
                DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    embedding_model = EXCLUDED.embedding_model,
                    updated_at = NOW()
            """, incident_id, embedding, self.model)

            logger.debug(f"Stored embedding for incident: {incident_id}")

        except Exception as e:
            logger.error(f"Failed to store embedding for {incident_id}: {e}")
            raise

    async def batch_generate_embeddings(self, incidents: List[Dict]) -> List[List[float]]:
        """
        Generate embeddings for multiple incidents (batch processing).

        More efficient than calling generate_embedding() one by one.

        Args:
            incidents: List of incident dicts

        Returns:
            List of embeddings (same order as input)

        Example:
            >>> incidents = [incident1, incident2, incident3]
            >>> embeddings = await dedup.batch_generate_embeddings(incidents)
            >>> len(embeddings) == len(incidents)
            True
        """
        tasks = [self.generate_embedding(incident) for incident in incidents]
        embeddings = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        results = []
        for i, embedding in enumerate(embeddings):
            if isinstance(embedding, Exception):
                logger.error(f"Failed to generate embedding for incident {i}: {embedding}")
                results.append(None)
            else:
                results.append(embedding)

        return results

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Similarity score (0.0-1.0)

        Example:
            >>> vec1 = [0.1, 0.2, 0.3]
            >>> vec2 = [0.1, 0.2, 0.3]
            >>> dedup.cosine_similarity(vec1, vec2)
            1.0
        """
        a = np.array(vec1)
        b = np.array(vec2)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))
