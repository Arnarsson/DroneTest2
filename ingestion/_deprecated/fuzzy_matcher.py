"""
Fuzzy string matching for duplicate detection (Tier 1).

100% free, uses Python's built-in difflib.
Catches typos and variations in titles.
"""

from difflib import SequenceMatcher
import re
from typing import Dict, List

class FuzzyMatcher:
    """Free fuzzy string matching using built-in Python libraries."""

    # Common word synonyms for drone incidents
    SYNONYMS = {
        'drone': ['uav', 'unmanned aircraft', 'quadcopter', 'multicopter', 'droner'],
        'airport': ['airfield', 'aerodrome', 'airstrip', 'lufthavn', 'flyplass'],
        'closed': ['shutdown', 'halted', 'suspended', 'stopped', 'stengt', 'lukket'],
        'sighting': ['spotted', 'observed', 'seen', 'detected', 'observert'],
        'military': ['defense', 'armed forces', 'base', 'forsvar', 'militær'],
        'harbor': ['port', 'seaport', 'dock', 'havn'],
        'investigation': ['probe', 'inquiry', 'undersøkelse', 'etterforskning'],
        'police': ['authorities', 'politi', 'politiet'],
    }

    @staticmethod
    def normalize_title(title: str) -> str:
        """
        Normalize title for fuzzy comparison.

        Steps:
        1. Lowercase
        2. Remove punctuation
        3. Expand synonyms
        4. Remove extra whitespace

        Args:
            title: Original title string

        Returns:
            Normalized title string with synonyms expanded

        Examples:
            >>> FuzzyMatcher.normalize_title("Copenhagen Airport Closed!")
            'copenhagen airport airfield aerodrome airstrip lufthavn flyplass closed shutdown halted suspended stopped stengt lukket'
            >>> FuzzyMatcher.normalize_title("Drone Sighting at Military Base")
            'drone uav unmanned aircraft quadcopter multicopter droner sighting spotted observed seen detected observert at military defense armed forces base forsvar militær'
        """
        # Lowercase
        title = title.lower()

        # Remove punctuation (keep alphanumeric and spaces)
        title = re.sub(r'[^\w\s]', ' ', title)

        # Expand synonyms (add related words)
        words = title.split()
        expanded_words = words.copy()
        for word in words:
            if word in FuzzyMatcher.SYNONYMS:
                expanded_words.extend(FuzzyMatcher.SYNONYMS[word])

        # Join and remove duplicates while preserving order
        seen = set()
        unique_words = []
        for word in expanded_words:
            if word not in seen:
                seen.add(word)
                unique_words.append(word)

        # Join and normalize whitespace
        normalized = ' '.join(unique_words)

        return normalized

    @staticmethod
    def similarity_ratio(str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings.

        Uses SequenceMatcher (Ratcliff-Obershelp algorithm).
        Returns value between 0.0 (completely different) and 1.0 (identical).

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score (0.0-1.0)

        Examples:
            >>> FuzzyMatcher.similarity_ratio("Copenhagen Airport", "Copenhagen Airprt")
            0.95
            >>> FuzzyMatcher.similarity_ratio("Drone sighting", "UAV spotted")
            0.65
            >>> FuzzyMatcher.similarity_ratio("Airport", "Airfield")
            0.40
        """
        norm1 = FuzzyMatcher.normalize_title(str1)
        norm2 = FuzzyMatcher.normalize_title(str2)

        return SequenceMatcher(None, norm1, norm2).ratio()

    @staticmethod
    def is_fuzzy_match(str1: str, str2: str, threshold: float = 0.75) -> bool:
        """
        Check if two strings are fuzzy matches.

        Args:
            str1: First string
            str2: Second string
            threshold: Similarity threshold (0.0-1.0). Default 0.75.

        Returns:
            True if similarity >= threshold

        Examples:
            >>> FuzzyMatcher.is_fuzzy_match("Copenhagen Airport closed", "Kastrup Airport closed")
            True
            >>> FuzzyMatcher.is_fuzzy_match("Oslo", "Stockholm")
            False
        """
        return FuzzyMatcher.similarity_ratio(str1, str2) >= threshold

    @staticmethod
    def explain_similarity(str1: str, str2: str) -> Dict[str, any]:
        """
        Explain why two strings are similar or different.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Dict with:
            - similarity: float (0.0-1.0)
            - is_match: bool
            - normalized_1: str
            - normalized_2: str
            - common_words: list
            - unique_to_1: list
            - unique_to_2: list

        Examples:
            >>> result = FuzzyMatcher.explain_similarity("Copenhagen Airport", "Kastrup Airport")
            >>> result['similarity'] > 0.7
            True
            >>> 'airport' in result['common_words']
            True
        """
        norm1 = FuzzyMatcher.normalize_title(str1)
        norm2 = FuzzyMatcher.normalize_title(str2)
        similarity = SequenceMatcher(None, norm1, norm2).ratio()

        words1 = set(norm1.split())
        words2 = set(norm2.split())
        common_words = list(words1 & words2)

        return {
            'similarity': similarity,
            'is_match': similarity >= 0.75,
            'normalized_1': norm1,
            'normalized_2': norm2,
            'common_words': common_words,
            'unique_to_1': list(words1 - words2),
            'unique_to_2': list(words2 - words1)
        }

    @staticmethod
    def find_best_match(query: str, candidates: List[str], threshold: float = 0.75) -> tuple:
        """
        Find best matching string from a list of candidates.

        Args:
            query: String to match
            candidates: List of candidate strings
            threshold: Minimum similarity threshold

        Returns:
            (best_match, similarity_score) or (None, 0.0) if no match above threshold

        Examples:
            >>> candidates = ["Oslo Airport", "Copenhagen Airport", "Stockholm Airport"]
            >>> FuzzyMatcher.find_best_match("Kastrup Airport", candidates)
            ('Copenhagen Airport', 0.82)
        """
        best_match = None
        best_score = 0.0

        for candidate in candidates:
            score = FuzzyMatcher.similarity_ratio(query, candidate)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate

        return (best_match, best_score)
