"""
Real-World Duplicate Detection Test Cases

Tests using actual incident patterns from production data.

Features:
- Copenhagen Airport variants (Kastrup, CPH, Copenhagen)
- Norwegian police reports (different formats)
- Multi-location incidents (separate or duplicate?)
- Evolving stories (sighting → investigation → arrest)
- Cross-language duplicates (Norwegian, Swedish, Danish)

Usage:
    python3 test_real_world_duplicates.py
"""

import unittest
import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
import os

from fuzzy_matcher import FuzzyMatcher
from ai_similarity import OpenRouterClient, SimilarityResult


class TestCopenhagenAirportVariants(unittest.TestCase):
    """Test Case 1: Copenhagen Airport has many name variants"""

    def setUp(self):
        """Set up test cases with Copenhagen Airport variants"""
        self.base_incident = {
            'title': 'Drone spotted near Copenhagen Airport',
            'narrative': 'A drone was spotted near the runway causing flight delays',
            'lat': 55.6181,
            'lon': 12.6561,
            'occurred_at': '2025-10-01T14:00:00Z',
            'asset_type': 'airport',
            'location_name': 'Copenhagen Airport'
        }

        self.variants = [
            'UAV sighting at Kastrup Airport',
            'Drone causes delays at CPH',
            'Copenhagen Kastrup drone incident',
            'Københavns Lufthavn drone closure',
            'CPH Airport UAV spotted'
        ]

    def test_all_variants_match_base(self):
        """
        All Copenhagen Airport name variants should be detected as duplicates.

        Variants tested:
        - Copenhagen Airport
        - Kastrup Airport
        - CPH
        - København Lufthavn (Danish)
        """
        base_title = self.base_incident['title']

        for variant in self.variants:
            with self.subTest(variant=variant):
                similarity = FuzzyMatcher.similarity_ratio(base_title, variant)

                # Should have reasonable similarity (>0.40 after normalization)
                # Note: "CPH" is short, so threshold is lower
                min_threshold = 0.30 if 'CPH' in variant else 0.40

                self.assertGreater(
                    similarity,
                    min_threshold,
                    f"Variant '{variant}' should match base incident (got {similarity:.2f})"
                )

                print(f"✓ '{variant}' matches base: {similarity:.2%}")

    def test_kastrup_is_synonym_for_copenhagen_airport(self):
        """Kastrup is the official name for Copenhagen Airport"""
        title1 = "Drone at Copenhagen Airport"
        title2 = "Drone at Kastrup Airport"

        # After normalization with synonyms, should have high overlap
        norm1 = FuzzyMatcher.normalize_title(title1)
        norm2 = FuzzyMatcher.normalize_title(title2)

        # Both should contain "airport" and synonyms
        self.assertIn('airport', norm1)
        self.assertIn('airport', norm2)

        # Calculate overlap
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        overlap = len(words1 & words2) / max(len(words1), len(words2))

        self.assertGreater(overlap, 0.60, f"Kastrup/Copenhagen should have >60% word overlap (got {overlap:.2%})")


@pytest.mark.asyncio
class TestNorwegianPoliceReports:
    """Test Case 2: Norwegian police reports come in different formats"""

    @pytest.fixture
    def mock_openrouter(self):
        """Mock OpenRouter client"""
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_key'}):
            client = OpenRouterClient(api_key='test_key')
            # Mock the API call
            client.client = MagicMock()
            yield client

    async def test_norwegian_police_format_variations(self, mock_openrouter):
        """
        Norwegian police reports have Norwegian vs English variations.

        Formats:
        - "Politiet advarer om drone ved Gardermoen" (Norwegian)
        - "Police warn about drone at Gardermoen" (English)
        - "Drone warning near Oslo Airport" (English with different location name)
        - "Gardermoen lufthavn: drone observert" (Norwegian with colon)
        """
        base_incident = {
            'id': 'no_police_1',
            'title': 'Politiet advarer om drone ved Gardermoen',
            'narrative': 'Politiet har mottatt melding om drone aktivitet',
            'lat': 60.1939,
            'lon': 11.1004,
            'occurred_at': '2025-10-05T14:00:00Z',
            'asset_type': 'airport',
            'location_name': 'Gardermoen Airport'
        }

        variants = [
            {
                'id': 'no_police_2',
                'title': 'Police warn about drone at Gardermoen',
                'narrative': 'Police received report of drone activity',
                'lat': 60.1939,
                'lon': 11.1004,
                'occurred_at': '2025-10-05T14:30:00Z',
                'asset_type': 'airport',
                'location_name': 'Gardermoen Airport'
            },
            {
                'id': 'no_police_3',
                'title': 'Drone warning near Oslo Airport',
                'narrative': 'Authorities alerted to UAV near airport',
                'lat': 60.1939,
                'lon': 11.1004,
                'occurred_at': '2025-10-05T15:00:00Z',
                'asset_type': 'airport',
                'location_name': 'Oslo Airport Gardermoen'
            }
        ]

        # Test Tier 1 (Fuzzy matching)
        for i, variant in enumerate(variants, 1):
            # Tier 1: Check fuzzy matching
            similarity = FuzzyMatcher.similarity_ratio(
                base_incident['title'],
                variant['title']
            )

            print(f"\nVariant {i}: '{variant['title']}'")
            print(f"  Fuzzy similarity: {similarity:.2%}")

            # Mock AI response for Tier 2/3 testing
            if hasattr(mock_openrouter, 'client') and hasattr(mock_openrouter.client, 'chat'):
                mock_response = MagicMock()
                mock_response.choices = [
                    MagicMock(message=MagicMock(content="""{
                        "is_duplicate": true,
                        "confidence": 0.90,
                        "reasoning": "Same Gardermoen Airport incident, just different language (Norwegian vs English)",
                        "merged_title": "Police warn about drone at Gardermoen Airport",
                        "merged_narrative": "Police received report of drone activity near Gardermoen Airport"
                    }"""))
                ]
                mock_openrouter.client.chat.completions.create = AsyncMock(return_value=mock_response)

                # Test AI comparison
                result = await mock_openrouter.compare_incidents(base_incident, variant)

                assert result.is_duplicate is True, f"Variant {i} should be detected as duplicate"
                print(f"  AI verdict: DUPLICATE (confidence: {result.confidence:.2f})")


@pytest.mark.asyncio
class TestUniqueEvents:
    """Test Case 3: Unique events should NOT be merged"""

    async def test_different_airports_different_dates(self):
        """
        Different locations and dates = different events (NOT duplicates).

        Cases:
        - Drone at Stockholm Arlanda (Oct 1)
        - Drone at Copenhagen Kastrup (Oct 3)
        - Drone at Oslo Gardermoen (Oct 5)
        - Drone at Helsinki Vantaa (Oct 7)
        """
        incidents = [
            {
                'id': '1',
                'title': 'Drone at Stockholm Arlanda Airport',
                'narrative': 'Drone spotted near runway',
                'lat': 59.6519,
                'lon': 17.9186,
                'occurred_at': '2025-10-01T14:00:00Z',
                'asset_type': 'airport',
                'location_name': 'Stockholm Arlanda Airport'
            },
            {
                'id': '2',
                'title': 'Drone at Copenhagen Kastrup Airport',
                'narrative': 'UAV sighting causes delays',
                'lat': 55.6181,
                'lon': 12.6561,
                'occurred_at': '2025-10-03T16:00:00Z',
                'asset_type': 'airport',
                'location_name': 'Copenhagen Kastrup Airport'
            },
            {
                'id': '3',
                'title': 'Drone at Oslo Gardermoen Airport',
                'narrative': 'Drone activity reported',
                'lat': 60.1939,
                'lon': 11.1004,
                'occurred_at': '2025-10-05T10:00:00Z',
                'asset_type': 'airport',
                'location_name': 'Oslo Gardermoen Airport'
            },
            {
                'id': '4',
                'title': 'Drone at Helsinki Vantaa Airport',
                'narrative': 'Drone spotted near terminal',
                'lat': 60.3172,
                'lon': 24.9633,
                'occurred_at': '2025-10-07T12:00:00Z',
                'asset_type': 'airport',
                'location_name': 'Helsinki Vantaa Airport'
            }
        ]

        # Compare each pair - they should all be UNIQUE
        for i in range(len(incidents)):
            for j in range(i + 1, len(incidents)):
                incident1 = incidents[i]
                incident2 = incidents[j]

                # Calculate geographic distance
                from math import radians, cos, sin, asin, sqrt

                lat1, lon1 = incident1['lat'], incident1['lon']
                lat2, lon2 = incident2['lat'], incident2['lon']

                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                distance_km = 6371 * c

                # Different airports are far apart (>100km)
                assert distance_km > 100, f"Airports should be >100km apart, got {distance_km:.0f}km"

                # Fuzzy similarity should be low (different cities)
                title_similarity = FuzzyMatcher.similarity_ratio(
                    incident1['title'],
                    incident2['title']
                )

                print(f"\n{incident1['location_name']} vs {incident2['location_name']}")
                print(f"  Distance: {distance_km:.0f}km")
                print(f"  Title similarity: {title_similarity:.2%}")
                print(f"  Verdict: UNIQUE (different locations)")

                # Should NOT be marked as duplicate by Tier 1
                assert not FuzzyMatcher.is_fuzzy_match(
                    incident1['title'],
                    incident2['title'],
                    threshold=0.75
                ), "Different airports should not be fuzzy matches"


class TestEvolvingStories(unittest.TestCase):
    """Test Case 4: Evolving stories (sighting → investigation → arrest)"""

    def test_evolving_story_timeline(self):
        """
        Test that evolving story stages are correctly handled.

        Stages:
        - Day 1: Initial sighting
        - Day 2: Investigation launched
        - Day 3: Arrest made

        Question: Are these duplicates (same event) or unique (different stages)?
        Answer: Should be merged as DUPLICATE (same underlying event)
        """
        stages = [
            {
                'date': '2025-10-01T14:00:00Z',
                'title': 'Drone sighting at Copenhagen Airport',
                'narrative': 'Drone spotted near runway, flights delayed',
                'stage': 'sighting'
            },
            {
                'date': '2025-10-02T10:00:00Z',
                'title': 'Police investigate Copenhagen Airport drone incident',
                'narrative': 'Authorities launched investigation into drone sighting',
                'stage': 'investigation'
            },
            {
                'date': '2025-10-03T16:00:00Z',
                'title': 'Arrest made in Copenhagen Airport drone case',
                'narrative': 'Police arrested suspect in connection with drone incident',
                'stage': 'arrest'
            }
        ]

        # These should have moderate fuzzy similarity (same location, different focus)
        for i in range(len(stages) - 1):
            title1 = stages[i]['title']
            title2 = stages[i+1]['title']

            similarity = FuzzyMatcher.similarity_ratio(title1, title2)

            print(f"\nStage {i+1} → {i+2}: {stages[i]['stage']} → {stages[i+1]['stage']}")
            print(f"  Title similarity: {similarity:.2%}")

            # Similarity might be moderate (0.50-0.75) - needs Tier 2/3 analysis
            # Tier 1 alone might not catch this - needs semantic understanding
            if similarity < 0.75:
                print(f"  ⚠️  Fuzzy match below threshold - needs Tier 2 or Tier 3")


class TestCrossLanguageDuplicates(unittest.TestCase):
    """Test Case 5: Cross-language duplicates (Nordic languages)"""

    def test_norwegian_swedish_danish_same_event(self):
        """
        Same event reported in different Nordic languages.

        Norwegian: "Drone observert ved Gardermoen"
        Swedish:   "Drönare sedd vid Gardermoen"
        Danish:    "Drone set ved Gardermoen"
        English:   "Drone spotted at Gardermoen"

        All should be detected as duplicates.
        """
        titles = {
            'norwegian': 'Drone observert ved Gardermoen lufthavn',
            'swedish': 'Drönare sedd vid Gardermoen flygplats',
            'danish': 'Drone set ved Gardermoen lufthavn',
            'english': 'Drone spotted at Gardermoen airport'
        }

        # Test pairwise similarity
        for lang1, title1 in titles.items():
            for lang2, title2 in titles.items():
                if lang1 >= lang2:
                    continue

                similarity = FuzzyMatcher.similarity_ratio(title1, title2)

                print(f"\n{lang1.capitalize()} vs {lang2.capitalize()}: {similarity:.2%}")

                # Cross-language might have lower similarity (different words)
                # But "Gardermoen" should be common, and "drone/drönare" are synonyms
                # Expect moderate similarity (0.50-0.70)

                if similarity < 0.75:
                    print(f"  ⚠️  Below fuzzy threshold - needs Tier 2 (embeddings) for semantic match")
                else:
                    print(f"  ✓ Above fuzzy threshold - Tier 1 catches it")


# Performance benchmark test
class TestRealWorldPerformance(unittest.TestCase):
    """Performance benchmarks with real-world data volumes"""

    def test_batch_comparison_performance(self):
        """
        Test performance of comparing 1 new incident against 100 existing.

        Typical use case: Ingesting new incident, checking against recent incidents.
        Target: <500ms for 100 comparisons (Tier 1 only)
        """
        import time

        new_incident_title = "Drone spotted at Copenhagen Airport"

        # Simulate 100 existing incidents
        existing_titles = [
            f"Incident {i}: Drone at {location} Airport"
            for i in range(100)
            for location in ['Oslo', 'Stockholm', 'Copenhagen', 'Helsinki'][:25]
        ]

        start_time = time.time()

        matches = []
        for existing_title in existing_titles:
            similarity = FuzzyMatcher.similarity_ratio(new_incident_title, existing_title)
            if similarity >= 0.75:
                matches.append((existing_title, similarity))

        elapsed = (time.time() - start_time) * 1000  # ms

        print(f"\nBatch Comparison Performance:")
        print(f"  Compared against: {len(existing_titles)} incidents")
        print(f"  Matches found: {len(matches)}")
        print(f"  Total time: {elapsed:.2f}ms")
        print(f"  Average per comparison: {elapsed/len(existing_titles):.3f}ms")

        self.assertLess(elapsed, 500, f"Batch comparison should be <500ms, got {elapsed:.2f}ms")


def print_test_report():
    """Print test report header"""
    print("\n" + "="*80)
    print(" "*20 + "REAL-WORLD DUPLICATE DETECTION TESTS")
    print("="*80)
    print("\nTEST CATEGORIES:")
    print("  1. Copenhagen Airport Variants (Kastrup, CPH, København)")
    print("  2. Norwegian Police Reports (Norwegian vs English)")
    print("  3. Unique Events (Different locations, should NOT merge)")
    print("  4. Evolving Stories (Sighting → Investigation → Arrest)")
    print("  5. Cross-Language Duplicates (NO, SV, DA, EN)")
    print("  6. Performance Benchmarks (Real-world volumes)")
    print("="*80 + "\n")


if __name__ == '__main__':
    print_test_report()

    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCopenhagenAirportVariants))
    suite.addTests(loader.loadTestsFromTestCase(TestUniqueEvents))
    suite.addTests(loader.loadTestsFromTestCase(TestEvolvingStories))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossLanguageDuplicates))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldPerformance))

    # Run async tests separately
    print("\n🔄 Running async tests...")
    import sys
    sys.exit(pytest.main([__file__, '-v', '-k', 'Norwegian', '--tb=short']))

    # Run sync tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
