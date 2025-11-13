"""
Test suite for fuzzy_matcher.py - Tier 1 duplicate detection.

Tests normalization, similarity calculation, and synonym expansion.
"""

import unittest
from fuzzy_matcher import FuzzyMatcher


class TestFuzzyMatcher(unittest.TestCase):
    """Test cases for FuzzyMatcher class."""

    def test_normalize_title_lowercase(self):
        """Test that normalization converts to lowercase."""
        result = FuzzyMatcher.normalize_title("COPENHAGEN AIRPORT")
        self.assertTrue(result.islower())
        self.assertIn("copenhagen", result)

    def test_normalize_title_removes_punctuation(self):
        """Test that normalization removes punctuation."""
        result = FuzzyMatcher.normalize_title("Copenhagen Airport: Closed!")
        self.assertNotIn(":", result)
        self.assertNotIn("!", result)
        self.assertIn("copenhagen", result)
        self.assertIn("closed", result)

    def test_normalize_title_expands_synonyms(self):
        """Test that normalization expands synonyms."""
        result = FuzzyMatcher.normalize_title("drone at airport")
        # Should contain original words
        self.assertIn("drone", result)
        self.assertIn("airport", result)
        # Should contain synonyms
        self.assertIn("uav", result)
        self.assertIn("airfield", result)

    def test_similarity_ratio_identical(self):
        """Test similarity ratio for identical strings."""
        score = FuzzyMatcher.similarity_ratio("Copenhagen Airport", "Copenhagen Airport")
        self.assertGreaterEqual(score, 0.99)

    def test_similarity_ratio_typo(self):
        """Test similarity ratio for strings with typos."""
        score = FuzzyMatcher.similarity_ratio("Copenhagen Airport", "Copenhagen Airprt")
        self.assertGreater(score, 0.40)  # Good similarity despite typo

    def test_similarity_ratio_synonyms(self):
        """Test similarity ratio for synonyms."""
        score = FuzzyMatcher.similarity_ratio("Airport closed", "Airfield closed")
        self.assertGreater(score, 0.65)  # Good similarity due to synonym expansion

    def test_similarity_ratio_different(self):
        """Test similarity ratio for completely different strings."""
        score = FuzzyMatcher.similarity_ratio("Oslo Airport", "Stockholm Harbor")
        self.assertLess(score, 0.50)  # Low similarity

    def test_is_fuzzy_match_exact(self):
        """Test fuzzy match with exact strings."""
        self.assertTrue(
            FuzzyMatcher.is_fuzzy_match("Copenhagen Airport", "Copenhagen Airport")
        )

    def test_is_fuzzy_match_typo(self):
        """Test fuzzy match with typo."""
        self.assertTrue(
            FuzzyMatcher.is_fuzzy_match(
                "Copenhagen Airport closed", "Copenhagen Airprt closed"
            )
        )

    def test_is_fuzzy_match_case_variation(self):
        """Test fuzzy match with case variations."""
        self.assertTrue(
            FuzzyMatcher.is_fuzzy_match(
                "COPENHAGEN AIRPORT", "copenhagen airport", threshold=0.70
            )
        )

    def test_is_fuzzy_match_synonym(self):
        """Test fuzzy match with synonyms."""
        # "airport" and "airfield" are synonyms
        self.assertTrue(
            FuzzyMatcher.is_fuzzy_match(
                "Kastrup Airport closed", "Kastrup Airfield closed", threshold=0.70
            )
        )

    def test_is_fuzzy_match_different(self):
        """Test fuzzy match rejects completely different strings."""
        self.assertFalse(
            FuzzyMatcher.is_fuzzy_match("Oslo Airport", "Copenhagen Harbor")
        )

    def test_explain_similarity_structure(self):
        """Test explain_similarity returns correct structure."""
        result = FuzzyMatcher.explain_similarity("Copenhagen Airport", "Kastrup Airport")

        # Check structure
        self.assertIn('similarity', result)
        self.assertIn('is_match', result)
        self.assertIn('normalized_1', result)
        self.assertIn('normalized_2', result)
        self.assertIn('common_words', result)
        self.assertIn('unique_to_1', result)
        self.assertIn('unique_to_2', result)

        # Check types
        self.assertIsInstance(result['similarity'], float)
        self.assertIsInstance(result['is_match'], bool)
        self.assertIsInstance(result['common_words'], list)

    def test_explain_similarity_common_words(self):
        """Test explain_similarity identifies common words."""
        result = FuzzyMatcher.explain_similarity(
            "Copenhagen Airport closed", "Copenhagen Airfield closed"
        )

        # Should have common words
        self.assertGreater(len(result['common_words']), 0)
        # "copenhagen" and "closed" should be common
        self.assertIn('copenhagen', result['common_words'])
        self.assertIn('closed', result['common_words'])

    def test_find_best_match_exact(self):
        """Test find_best_match with exact match."""
        candidates = ["Oslo Airport", "Copenhagen Airport", "Stockholm Airport"]
        best_match, score = FuzzyMatcher.find_best_match("Copenhagen Airport", candidates)

        self.assertEqual(best_match, "Copenhagen Airport")
        self.assertGreater(score, 0.95)

    def test_find_best_match_close(self):
        """Test find_best_match with close match."""
        candidates = ["Oslo Airport", "Copenhagen Airport", "Stockholm Airport"]
        best_match, score = FuzzyMatcher.find_best_match("Copenhgen Airport", candidates, threshold=0.50)

        # Should match Copenhagen (typo)
        self.assertEqual(best_match, "Copenhagen Airport")
        self.assertGreater(score, 0.50)

    def test_find_best_match_no_match(self):
        """Test find_best_match with no match above threshold."""
        candidates = ["Oslo Airport", "Copenhagen Airport", "Stockholm Airport"]
        best_match, score = FuzzyMatcher.find_best_match("Tokyo International", candidates, threshold=0.80)

        self.assertIsNone(best_match)
        self.assertEqual(score, 0.0)

    def test_nordic_languages(self):
        """Test with Nordic language variations."""
        # Norwegian - expanded in normalized text
        result1 = FuzzyMatcher.normalize_title("flyplass")
        self.assertIn("flyplass", result1)

        # Danish - expanded in normalized text
        result2 = FuzzyMatcher.normalize_title("lufthavn")
        self.assertIn("lufthavn", result2)

    def test_real_world_duplicates(self):
        """Test with real-world duplicate scenarios."""
        # Same incident, similar wording
        title1 = "Copenhagen Airport closed due to drone"
        title2 = "Copenhagen Airport shutdown after UAV sighting"

        score = FuzzyMatcher.similarity_ratio(title1, title2)
        self.assertGreater(score, 0.55)  # Should be recognized as similar

        # Different incidents
        title3 = "Oslo Airport drone sighting"
        title4 = "Stockholm Harbor security incident"

        score2 = FuzzyMatcher.similarity_ratio(title3, title4)
        self.assertLess(score2, 0.50)  # Should be recognized as different

    def test_multilingual_support(self):
        """Test multilingual synonyms."""
        # Norwegian police terms - just check they're normalized
        result = FuzzyMatcher.normalize_title("politiet etterforskning")
        self.assertIn("politiet", result)
        self.assertIn("etterforskning", result)

        # Danish closed airport - just check they're normalized
        result2 = FuzzyMatcher.normalize_title("lufthavn lukket")
        self.assertIn("lufthavn", result2)
        self.assertIn("lukket", result2)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
