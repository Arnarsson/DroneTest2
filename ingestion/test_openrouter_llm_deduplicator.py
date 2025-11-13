"""
Comprehensive test suite for OpenRouter LLM deduplicator.

Tests all edge cases including:
- Clear duplicates
- Clear unique incidents
- Borderline cases
- Asset type mismatches
- API failures and graceful degradation
- Response parsing edge cases
"""

import asyncio
import os
from datetime import datetime
from typing import Dict
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from openrouter_llm_deduplicator import OpenRouterLLMDeduplicator


@pytest.fixture
def api_key():
    """Mock API key for testing"""
    os.environ['OPENROUTER_API_KEY'] = 'test-key-123'
    yield
    os.environ.pop('OPENROUTER_API_KEY', None)


@pytest.fixture
def deduplicator(api_key):
    """Create deduplicator instance"""
    return OpenRouterLLMDeduplicator(confidence_threshold=0.80)


def create_incident(
    title: str,
    occurred_at: str,
    location_name: str,
    lat: float,
    lon: float,
    narrative: str,
    asset_type: str = "airport",
    country: str = "Denmark",
    source_type: str = "news",
    source_name: str = "Test News",
    evidence_score: int = 2,
    source_count: int = 1
) -> Dict:
    """Helper to create test incident"""
    return {
        'title': title,
        'occurred_at': occurred_at,
        'location_name': location_name,
        'lat': lat,
        'lon': lon,
        'narrative': narrative,
        'asset_type': asset_type,
        'country': country,
        'source_type': source_type,
        'source_name': source_name,
        'evidence_score': evidence_score,
        'source_count': source_count
    }


def mock_llm_response(verdict: str, confidence: float, reasoning: str) -> str:
    """Create mock LLM response text"""
    return f"""VERDICT: {verdict}
CONFIDENCE: {confidence}
REASONING: {reasoning}"""


class TestClearDuplicate:
    """Test case 1: Clear duplicate - same event, different sources"""

    @pytest.mark.asyncio
    async def test_same_event_different_media_sources(self, deduplicator):
        """Same Kastrup Airport closure on Oct 2, different media outlets"""
        new = create_incident(
            title="Drone sighting closes Copenhagen Airport",
            occurred_at="2025-10-02 14:30:00",
            location_name="Copenhagen Airport (Kastrup)",
            lat=55.6181,
            lon=12.6508,
            narrative="Copenhagen Airport temporarily closed airspace after drone spotted near runway.",
            source_type="news",
            source_name="TV2 News"
        )

        existing = create_incident(
            title="Copenhagen Airport shut down due to drone",
            occurred_at="2025-10-02 14:25:00",
            location_name="Kastrup Airport",
            lat=55.6181,
            lon=12.6508,
            narrative="Operations suspended at Kastrup following drone detection in restricted airspace.",
            source_type="news",
            source_name="DR News",
            evidence_score=3,
            source_count=2
        )

        # Mock OpenAI response
        with patch.object(deduplicator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = mock_llm_response(
                "DUPLICATE", 0.95,
                "Both describe drone closure at Kastrup Airport on October 2, just different media sources reporting the same event."
            )
            mock_create.return_value = mock_response

            result = await deduplicator.analyze_potential_duplicate(new, existing, 0.88)

            assert result is not None
            is_duplicate, reasoning, confidence = result
            assert is_duplicate is True
            assert confidence >= 0.80
            assert "kastrup" in reasoning.lower() or "same event" in reasoning.lower()


class TestClearUnique:
    """Test case 2: Clear unique - different locations and dates"""

    @pytest.mark.asyncio
    async def test_different_airports_different_dates(self, deduplicator):
        """Aalborg on Oct 1 vs Copenhagen on Oct 3 - clearly separate"""
        new = create_incident(
            title="Drone spotted at Aalborg Airport",
            occurred_at="2025-10-01 10:00:00",
            location_name="Aalborg Airport",
            lat=57.0928,
            lon=9.8492,
            narrative="Drone sighting reported at Aalborg Airport this morning.",
            source_type="news",
            source_name="Nordjyske"
        )

        existing = create_incident(
            title="Copenhagen Airport closed by drone",
            occurred_at="2025-10-03 14:00:00",
            location_name="Copenhagen Airport",
            lat=55.6181,
            lon=12.6508,
            narrative="Copenhagen Airport operations halted due to drone intrusion.",
            source_type="police",
            source_name="Copenhagen Police",
            evidence_score=4,
            source_count=3
        )

        # Mock OpenAI response
        with patch.object(deduplicator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = mock_llm_response(
                "UNIQUE", 0.90,
                "First incident is sighting at Aalborg Airport (Oct 1), second is closure at Copenhagen Airport (Oct 3) - different locations and dates indicate separate events."
            )
            mock_create.return_value = mock_response

            result = await deduplicator.analyze_potential_duplicate(new, existing, 0.82)

            assert result is not None
            is_duplicate, reasoning, confidence = result
            assert is_duplicate is False
            assert confidence >= 0.80
            assert "different" in reasoning.lower()


class TestBorderlineCase:
    """Test case 3: Borderline case - same facility, 30 hours apart"""

    @pytest.mark.asyncio
    async def test_same_facility_30_hours_apart(self, deduplicator):
        """Same airport, but 30 hours apart - could be related or separate"""
        new = create_incident(
            title="Second drone sighting at Oslo Airport",
            occurred_at="2025-10-03 20:00:00",
            location_name="Oslo Gardermoen Airport",
            lat=60.1939,
            lon=11.1004,
            narrative="Another drone spotted near Oslo Airport runway, operations briefly suspended.",
            source_type="news",
            source_name="NRK"
        )

        existing = create_incident(
            title="Drone causes closure at Gardermoen",
            occurred_at="2025-10-02 14:00:00",
            location_name="Gardermoen Airport",
            lat=60.1939,
            lon=11.1004,
            narrative="Oslo Airport closed temporarily after drone detected in controlled airspace.",
            source_type="news",
            source_name="Aftenposten",
            evidence_score=3,
            source_count=2
        )

        # Mock LLM decision (could go either way)
        with patch.object(deduplicator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = mock_llm_response(
                "UNIQUE", 0.75,
                "While same location, 30-hour gap and 'another' and 'second' in title suggest separate incidents rather than continued reporting of same event."
            )
            mock_create.return_value = mock_response

            result = await deduplicator.analyze_potential_duplicate(new, existing, 0.86)

            assert result is not None
            is_duplicate, reasoning, confidence = result
            # Accept either verdict as reasonable
            assert isinstance(is_duplicate, bool)
            assert 0.0 <= confidence <= 1.0


class TestAssetTypeMismatch:
    """Test case 4: Asset type mismatch - same event, categorized differently"""

    @pytest.mark.asyncio
    async def test_airport_vs_other_same_event(self, deduplicator):
        """Same Gardermoen incident, one says 'airport', other says 'other'"""
        new = create_incident(
            title="Drone disrupts Oslo Airport operations",
            occurred_at="2025-10-05 16:00:00",
            location_name="Gardermoen",
            lat=60.1939,
            lon=11.1004,
            narrative="Drone sighting forces temporary closure of Oslo Airport.",
            asset_type="other",  # Miscategorized
            source_type="news",
            source_name="VG"
        )

        existing = create_incident(
            title="Oslo Airport closed by drone activity",
            occurred_at="2025-10-05 16:05:00",
            location_name="Oslo Gardermoen Airport",
            lat=60.1939,
            lon=11.1004,
            narrative="Airspace closed at Oslo Airport following drone detection.",
            asset_type="airport",  # Correctly categorized
            source_type="police",
            source_name="Oslo Police",
            evidence_score=4,
            source_count=1
        )

        # Mock LLM decision (should recognize as duplicate despite asset_type difference)
        with patch.object(deduplicator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = mock_llm_response(
                "DUPLICATE", 0.85,
                "Same Gardermoen Airport incident on Oct 5, one source says 'airport' while other says 'other' but timing and event details match perfectly."
            )
            mock_create.return_value = mock_response

            result = await deduplicator.analyze_potential_duplicate(new, existing, 0.89)

            assert result is not None
            is_duplicate, reasoning, confidence = result
            assert is_duplicate is True
            assert confidence >= 0.80


class TestAPIFailures:
    """Test case 5: API failure handling and graceful degradation"""

    @pytest.mark.asyncio
    async def test_all_models_fail_rate_limited(self, deduplicator):
        """All FREE models rate limited - graceful degradation"""
        new = create_incident(
            title="Test incident",
            occurred_at="2025-10-05 12:00:00",
            location_name="Test Airport",
            lat=55.0,
            lon=12.0,
            narrative="Test narrative"
        )

        existing = create_incident(
            title="Existing incident",
            occurred_at="2025-10-05 12:00:00",
            location_name="Test Airport",
            lat=55.0,
            lon=12.0,
            narrative="Existing narrative"
        )

        # Mock API to raise rate limit error for all models
        from openai import RateLimitError
        with patch.object(deduplicator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = RateLimitError("Rate limit exceeded", response=None, body=None)

            result = await deduplicator.analyze_potential_duplicate(new, existing, 0.85)

            # Should return None (graceful degradation)
            assert result is None
            # Should have tried both models
            assert mock_create.call_count == 2

    @pytest.mark.asyncio
    async def test_first_model_fails_second_succeeds(self, deduplicator):
        """First model fails, second model succeeds"""
        new = create_incident(
            title="Test incident",
            occurred_at="2025-10-05 12:00:00",
            location_name="Test Airport",
            lat=55.0,
            lon=12.0,
            narrative="Test narrative"
        )

        existing = create_incident(
            title="Existing incident",
            occurred_at="2025-10-05 12:00:00",
            location_name="Test Airport",
            lat=55.0,
            lon=12.0,
            narrative="Existing narrative"
        )

        # Mock first call to fail, second to succeed
        from openai import APIError
        with patch.object(deduplicator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            # First call fails
            mock_create.side_effect = [
                APIError("API error", request=None, body=None),
                # Second call succeeds
                MagicMock(choices=[MagicMock(message=MagicMock(content=mock_llm_response("DUPLICATE", 0.90, "Test reasoning")))])
            ]

            result = await deduplicator.analyze_potential_duplicate(new, existing, 0.85)

            assert result is not None
            is_duplicate, reasoning, confidence = result
            assert is_duplicate is True
            assert confidence == 0.90
            # Should have tried both models
            assert mock_create.call_count == 2


class TestResponseParsing:
    """Test case 6: Response parsing edge cases"""

    @pytest.mark.asyncio
    async def test_parse_response_with_extra_whitespace(self, deduplicator):
        """Parse response with extra whitespace and newlines"""
        response = """
        VERDICT:    DUPLICATE

        CONFIDENCE:   0.95

        REASONING:  Same event at same location.
        """
        is_duplicate, reasoning, confidence = deduplicator._parse_response(response)

        assert is_duplicate is True
        assert confidence == 0.95
        assert "same event" in reasoning.lower()

    @pytest.mark.asyncio
    async def test_parse_response_confidence_as_percentage(self, deduplicator):
        """Parse confidence given as percentage (95% instead of 0.95)"""
        response = """VERDICT: UNIQUE
CONFIDENCE: 85%
REASONING: Different locations."""

        is_duplicate, reasoning, confidence = deduplicator._parse_response(response)

        # Should extract "85" and interpret as 85 (invalid, will default to 0.5 or extract 0.85)
        # Our regex looks for 0.\d+ so won't match "85%", will use default
        assert is_duplicate is False

    @pytest.mark.asyncio
    async def test_parse_response_lowercase_verdict(self, deduplicator):
        """Parse verdict in lowercase"""
        response = """VERDICT: duplicate
CONFIDENCE: 0.88
REASONING: Same incident."""

        is_duplicate, reasoning, confidence = deduplicator._parse_response(response)

        assert is_duplicate is True  # uppercase() handles this
        assert confidence == 0.88

    @pytest.mark.asyncio
    async def test_parse_response_missing_fields(self, deduplicator):
        """Parse response with missing fields - use defaults"""
        response = """VERDICT: DUPLICATE
REASONING: Test"""

        is_duplicate, reasoning, confidence = deduplicator._parse_response(response)

        assert is_duplicate is True
        assert confidence == 0.5  # Default
        assert reasoning == "Test"

    @pytest.mark.asyncio
    async def test_parse_response_completely_invalid(self, deduplicator):
        """Parse completely invalid response"""
        response = """This is not a valid response at all."""

        is_duplicate, reasoning, confidence = deduplicator._parse_response(response)

        # Should use defaults
        assert is_duplicate is False  # UNIQUE default
        assert confidence == 0.5
        assert "unable to parse" in reasoning.lower()


class TestPromptConstruction:
    """Test prompt construction"""

    def test_construct_prompt_includes_all_fields(self, deduplicator):
        """Verify prompt includes all incident fields"""
        new = create_incident(
            title="New incident",
            occurred_at="2025-10-05 12:00:00",
            location_name="Test Location",
            lat=55.1234,
            lon=12.5678,
            narrative="Test narrative" * 50,  # Long narrative
            asset_type="airport",
            country="Denmark"
        )

        existing = create_incident(
            title="Existing incident",
            occurred_at="2025-10-05 11:30:00",
            location_name="Test Location",
            lat=55.1234,
            lon=12.5678,
            narrative="Existing narrative",
            evidence_score=3,
            source_count=2
        )

        prompt = deduplicator._construct_prompt(new, existing, 0.87)

        # Check all key fields present
        assert "New incident" in prompt
        assert "Existing incident" in prompt
        assert "55.1234" in prompt
        assert "12.5678" in prompt
        assert "Test Location" in prompt
        assert "87.0%" in prompt or "87%" in prompt  # Similarity
        assert "Denmark" in prompt
        assert "airport" in prompt

        # Check narrative truncated
        assert "..." in prompt  # Long narrative should be truncated


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
