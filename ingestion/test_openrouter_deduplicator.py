"""
Test suite for openrouter_deduplicator.py - Tier 2 duplicate detection.

Tests embedding generation, similarity search, and duplicate detection
using mocked API calls (no actual OpenRouter/Gemini calls).
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from datetime import datetime, timedelta
import numpy as np
from openrouter_deduplicator import OpenRouterEmbeddingDeduplicator


class TestOpenRouterEmbeddingDeduplicator(unittest.TestCase):
    """Test cases for OpenRouterEmbeddingDeduplicator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock database pool
        self.mock_db = AsyncMock()

        # Mock OpenRouter API key
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'sk-or-test-key'}):
            with patch('openrouter_deduplicator.AsyncOpenAI'):
                self.dedup = OpenRouterEmbeddingDeduplicator(
                    db_pool=self.mock_db,
                    similarity_threshold=0.85
                )

    def test_construct_embedding_text_complete(self):
        """Test embedding text construction with all fields."""
        incident = {
            'title': 'Drone closes Copenhagen Airport',
            'location_name': 'Kastrup Airport',
            'asset_type': 'airport',
            'occurred_at': datetime(2025, 11, 13, 12, 0),
            'narrative': 'A drone was spotted near the runway causing temporary closure.'
        }

        text = self.dedup._construct_embedding_text(incident)

        # Check all components present
        self.assertIn('Event: Drone closes Copenhagen Airport', text)
        self.assertIn('Location: Kastrup Airport', text)
        self.assertIn('Type: airport aerodrome airfield', text)
        self.assertIn('Date: 2025-11-13', text)
        self.assertIn('Details: A drone was spotted', text)

    def test_construct_embedding_text_minimal(self):
        """Test embedding text construction with minimal fields."""
        incident = {
            'title': 'Drone sighting',
            'asset_type': 'other'
        }

        text = self.dedup._construct_embedding_text(incident)

        # Check basic components
        self.assertIn('Event: Drone sighting', text)
        self.assertIn('Type: area location', text)

    def test_construct_embedding_text_city_fallback(self):
        """Test that city is used if location_name not provided."""
        incident = {
            'title': 'Drone incident',
            'city': 'Copenhagen',
            'asset_type': 'other'
        }

        text = self.dedup._construct_embedding_text(incident)

        # Should use city instead of location_name
        self.assertIn('City: Copenhagen', text)
        self.assertNotIn('Location:', text)

    def test_construct_embedding_text_narrative_truncation(self):
        """Test that long narratives are truncated."""
        long_narrative = 'A' * 300  # 300 characters

        incident = {
            'title': 'Test incident',
            'narrative': long_narrative
        }

        text = self.dedup._construct_embedding_text(incident)

        # Should be truncated to 200 chars + "..."
        self.assertIn('Details: ' + 'A' * 200 + '...', text)
        self.assertLess(len(text), 500)

    @patch('openrouter_deduplicator.AsyncOpenAI')
    async def test_generate_embedding_success(self, mock_openai):
        """Test successful embedding generation."""
        # Mock API response
        mock_embedding = [0.1] * 768  # 768-dimensional vector
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding)]

        mock_client = AsyncMock()
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        self.dedup.client = mock_client

        incident = {
            'title': 'Test incident',
            'location_name': 'Test location',
            'asset_type': 'airport'
        }

        embedding = await self.dedup.generate_embedding(incident)

        # Check result
        self.assertEqual(len(embedding), 768)
        self.assertEqual(embedding, mock_embedding)

        # Verify API was called
        mock_client.embeddings.create.assert_called_once()

    @patch('openrouter_deduplicator.AsyncOpenAI')
    async def test_generate_embedding_api_failure(self, mock_openai):
        """Test embedding generation handles API failures."""
        mock_client = AsyncMock()
        mock_client.embeddings.create = AsyncMock(side_effect=Exception("API error"))

        self.dedup.client = mock_client

        incident = {'title': 'Test incident'}

        # Should raise exception
        with self.assertRaises(Exception):
            await self.dedup.generate_embedding(incident)

    async def test_find_duplicate_no_match(self):
        """Test duplicate search with no matches."""
        # Mock no similar incidents found
        self.mock_db.fetch = AsyncMock(return_value=[])

        # Mock embedding generation
        with patch.object(self.dedup, 'generate_embedding', return_value=[0.1] * 768):
            incident = {
                'title': 'Unique incident',
                'lat': 55.6181,
                'lon': 12.6561,
                'occurred_at': datetime.now()
            }

            result = await self.dedup.find_duplicate(incident)

            # Should return None (no duplicate)
            self.assertIsNone(result)

    async def test_find_duplicate_match_found(self):
        """Test duplicate search finds match."""
        # Mock similar incident found
        mock_similar = [{
            'incident_id': '123e4567-e89b-12d3-a456-426614174000',
            'similarity_score': 0.92,
            'distance_km': 0.5,
            'title': 'Existing incident',
            'occurred_at': datetime.now() - timedelta(hours=2)
        }]
        self.mock_db.fetch = AsyncMock(return_value=mock_similar)

        # Mock embedding generation
        with patch.object(self.dedup, 'generate_embedding', return_value=[0.1] * 768):
            incident = {
                'title': 'Similar incident',
                'lat': 55.6181,
                'lon': 12.6561,
                'occurred_at': datetime.now()
            }

            result = await self.dedup.find_duplicate(incident)

            # Should return match
            self.assertIsNotNone(result)
            incident_id, similarity, explanation = result

            self.assertEqual(incident_id, '123e4567-e89b-12d3-a456-426614174000')
            self.assertEqual(similarity, 0.92)
            self.assertIsInstance(explanation, str)

    async def test_find_duplicate_handles_embedding_failure(self):
        """Test duplicate search handles embedding generation failure gracefully."""
        # Mock embedding generation failure
        with patch.object(self.dedup, 'generate_embedding', side_effect=Exception("API error")):
            incident = {
                'title': 'Test incident',
                'lat': 55.6181,
                'lon': 12.6561
            }

            result = await self.dedup.find_duplicate(incident)

            # Should return None (graceful failure)
            self.assertIsNone(result)

    def test_explain_match_high_similarity(self):
        """Test explanation for high similarity match."""
        new_incident = {
            'title': 'Drone at Kastrup',
            'occurred_at': datetime(2025, 11, 13, 12, 0)
        }

        existing_record = {
            'similarity_score': 0.96,
            'distance_km': 0.3,
            'occurred_at': datetime(2025, 11, 13, 12, 30)
        }

        explanation = self.dedup._explain_match(new_incident, existing_record)

        # Check explanation components
        self.assertIn('very high similarity', explanation)
        self.assertIn('same location', explanation)
        self.assertIn('within same hour', explanation)

    def test_explain_match_moderate_similarity(self):
        """Test explanation for moderate similarity match."""
        new_incident = {
            'title': 'Drone incident',
            'occurred_at': datetime(2025, 11, 13, 12, 0)
        }

        existing_record = {
            'similarity_score': 0.87,
            'distance_km': 15.0,
            'occurred_at': datetime(2025, 11, 12, 18, 0)
        }

        explanation = self.dedup._explain_match(new_incident, existing_record)

        # Check explanation components
        self.assertIn('moderate similarity', explanation)
        self.assertIn('15km', explanation)  # Format is "15km" not "15.0km"
        self.assertIn('18.0h apart', explanation)

    async def test_store_embedding_success(self):
        """Test successful embedding storage."""
        incident_id = '123e4567-e89b-12d3-a456-426614174000'
        embedding = [0.1] * 768

        self.mock_db.execute = AsyncMock()

        await self.dedup.store_embedding(incident_id, embedding)

        # Verify database was called
        self.mock_db.execute.assert_called_once()

        # Check SQL contains INSERT and ON CONFLICT
        call_args = self.mock_db.execute.call_args
        sql = call_args[0][0]
        self.assertIn('INSERT INTO incident_embeddings', sql)
        self.assertIn('ON CONFLICT', sql)

    async def test_store_embedding_failure(self):
        """Test embedding storage handles database errors."""
        incident_id = '123e4567-e89b-12d3-a456-426614174000'
        embedding = [0.1] * 768

        self.mock_db.execute = AsyncMock(side_effect=Exception("Database error"))

        # Should raise exception
        with self.assertRaises(Exception):
            await self.dedup.store_embedding(incident_id, embedding)

    async def test_batch_generate_embeddings_success(self):
        """Test batch embedding generation."""
        incidents = [
            {'title': 'Incident 1', 'asset_type': 'airport'},
            {'title': 'Incident 2', 'asset_type': 'military'},
            {'title': 'Incident 3', 'asset_type': 'harbor'}
        ]

        # Mock embedding generation
        mock_embedding = [0.1] * 768
        with patch.object(self.dedup, 'generate_embedding', return_value=mock_embedding):
            embeddings = await self.dedup.batch_generate_embeddings(incidents)

            # Should return embeddings for all incidents
            self.assertEqual(len(embeddings), 3)
            for embedding in embeddings:
                self.assertEqual(len(embedding), 768)

    async def test_batch_generate_embeddings_partial_failure(self):
        """Test batch embedding generation with some failures."""
        incidents = [
            {'title': 'Incident 1'},
            {'title': 'Incident 2'},
            {'title': 'Incident 3'}
        ]

        # Mock embedding generation with one failure
        mock_embedding = [0.1] * 768
        side_effects = [mock_embedding, Exception("API error"), mock_embedding]

        with patch.object(self.dedup, 'generate_embedding', side_effect=side_effects):
            embeddings = await self.dedup.batch_generate_embeddings(incidents)

            # Should return embeddings with None for failed ones
            self.assertEqual(len(embeddings), 3)
            self.assertIsNotNone(embeddings[0])
            self.assertIsNone(embeddings[1])  # Failed
            self.assertIsNotNone(embeddings[2])

    def test_cosine_similarity_identical(self):
        """Test cosine similarity for identical vectors."""
        vec1 = [0.1, 0.2, 0.3, 0.4]
        vec2 = [0.1, 0.2, 0.3, 0.4]

        similarity = self.dedup.cosine_similarity(vec1, vec2)

        # Should be 1.0 (identical)
        self.assertAlmostEqual(similarity, 1.0, places=5)

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity for orthogonal vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]

        similarity = self.dedup.cosine_similarity(vec1, vec2)

        # Should be 0.0 (orthogonal)
        self.assertAlmostEqual(similarity, 0.0, places=5)

    def test_cosine_similarity_opposite(self):
        """Test cosine similarity for opposite vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]

        similarity = self.dedup.cosine_similarity(vec1, vec2)

        # Should be -1.0 (opposite)
        self.assertAlmostEqual(similarity, -1.0, places=5)

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]

        similarity = self.dedup.cosine_similarity(vec1, vec2)

        # Should be 0.0 (undefined, but we return 0)
        self.assertEqual(similarity, 0.0)


def run_async_test(coro):
    """Helper to run async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == '__main__':
    # Patch async test methods to run with asyncio
    for attr_name in dir(TestOpenRouterEmbeddingDeduplicator):
        if attr_name.startswith('test_') and asyncio.iscoroutinefunction(
            getattr(TestOpenRouterEmbeddingDeduplicator, attr_name)
        ):
            attr = getattr(TestOpenRouterEmbeddingDeduplicator, attr_name)
            setattr(
                TestOpenRouterEmbeddingDeduplicator,
                attr_name,
                lambda self, f=attr: run_async_test(f(self))
            )

    # Run tests
    unittest.main(verbosity=2)
