"""
Simple test runner for OpenRouter LLM deduplicator (no pytest required).
Verifies core functionality with mocked API responses.
"""

import asyncio
import os
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from openrouter_llm_deduplicator import OpenRouterLLMDeduplicator


def create_incident(title, occurred_at, location_name, lat, lon, narrative,
                     asset_type="airport", country="Denmark", evidence_score=2, source_count=1):
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
        'source_type': 'news',
        'source_name': 'Test News',
        'evidence_score': evidence_score,
        'source_count': source_count
    }


def mock_llm_response(verdict, confidence, reasoning):
    """Create mock LLM response text"""
    return f"""VERDICT: {verdict}
CONFIDENCE: {confidence}
REASONING: {reasoning}"""


async def test_clear_duplicate():
    """Test 1: Clear duplicate - same event, different sources"""
    print("\n=== Test 1: Clear Duplicate ===")

    os.environ['OPENROUTER_API_KEY'] = 'test-key-123'
    deduplicator = OpenRouterLLMDeduplicator(confidence_threshold=0.80)

    new = create_incident(
        "Drone sighting closes Copenhagen Airport",
        "2025-10-02 14:30:00",
        "Copenhagen Airport (Kastrup)",
        55.6181, 12.6508,
        "Copenhagen Airport temporarily closed airspace after drone spotted near runway."
    )

    existing = create_incident(
        "Copenhagen Airport shut down due to drone",
        "2025-10-02 14:25:00",
        "Kastrup Airport",
        55.6181, 12.6508,
        "Operations suspended at Kastrup following drone detection.",
        evidence_score=3,
        source_count=2
    )

    # Mock OpenAI response
    with patch.object(deduplicator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = mock_llm_response(
            "DUPLICATE", 0.95,
            "Both describe drone closure at Kastrup Airport on October 2, same event."
        )
        mock_create.return_value = mock_response

        result = await deduplicator.analyze_potential_duplicate(new, existing, 0.88)

        assert result is not None, "Result should not be None"
        is_duplicate, reasoning, confidence = result
        assert is_duplicate is True, f"Should be duplicate, got: {is_duplicate}"
        assert confidence >= 0.80, f"Confidence too low: {confidence}"
        print(f"✓ PASS - Detected duplicate (confidence: {confidence:.2f})")
        print(f"  Reasoning: {reasoning}")


async def test_clear_unique():
    """Test 2: Clear unique - different locations and dates"""
    print("\n=== Test 2: Clear Unique ===")

    os.environ['OPENROUTER_API_KEY'] = 'test-key-123'
    deduplicator = OpenRouterLLMDeduplicator(confidence_threshold=0.80)

    new = create_incident(
        "Drone spotted at Aalborg Airport",
        "2025-10-01 10:00:00",
        "Aalborg Airport",
        57.0928, 9.8492,
        "Drone sighting reported at Aalborg Airport."
    )

    existing = create_incident(
        "Copenhagen Airport closed by drone",
        "2025-10-03 14:00:00",
        "Copenhagen Airport",
        55.6181, 12.6508,
        "Copenhagen Airport operations halted due to drone intrusion.",
        evidence_score=4,
        source_count=3
    )

    with patch.object(deduplicator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = mock_llm_response(
            "UNIQUE", 0.90,
            "Different locations (Aalborg vs Copenhagen) and dates (Oct 1 vs Oct 3) indicate separate events."
        )
        mock_create.return_value = mock_response

        result = await deduplicator.analyze_potential_duplicate(new, existing, 0.82)

        assert result is not None, "Result should not be None"
        is_duplicate, reasoning, confidence = result
        assert is_duplicate is False, f"Should be unique, got: {is_duplicate}"
        assert confidence >= 0.80, f"Confidence too low: {confidence}"
        print(f"✓ PASS - Detected unique (confidence: {confidence:.2f})")
        print(f"  Reasoning: {reasoning}")


async def test_asset_type_mismatch():
    """Test 3: Asset type mismatch - same event, categorized differently"""
    print("\n=== Test 3: Asset Type Mismatch ===")

    os.environ['OPENROUTER_API_KEY'] = 'test-key-123'
    deduplicator = OpenRouterLLMDeduplicator(confidence_threshold=0.80)

    new = create_incident(
        "Drone disrupts Oslo Airport operations",
        "2025-10-05 16:00:00",
        "Gardermoen",
        60.1939, 11.1004,
        "Drone sighting forces temporary closure of Oslo Airport.",
        asset_type="other"  # Miscategorized
    )

    existing = create_incident(
        "Oslo Airport closed by drone activity",
        "2025-10-05 16:05:00",
        "Oslo Gardermoen Airport",
        60.1939, 11.1004,
        "Airspace closed at Oslo Airport following drone detection.",
        asset_type="airport",  # Correctly categorized
        evidence_score=4
    )

    with patch.object(deduplicator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = mock_llm_response(
            "DUPLICATE", 0.85,
            "Same Gardermoen Airport incident on Oct 5, asset_type differs but timing and details match."
        )
        mock_create.return_value = mock_response

        result = await deduplicator.analyze_potential_duplicate(new, existing, 0.89)

        assert result is not None, "Result should not be None"
        is_duplicate, reasoning, confidence = result
        assert is_duplicate is True, f"Should be duplicate despite asset_type mismatch, got: {is_duplicate}"
        assert confidence >= 0.80, f"Confidence too low: {confidence}"
        print(f"✓ PASS - Detected duplicate despite asset_type mismatch (confidence: {confidence:.2f})")
        print(f"  Reasoning: {reasoning}")


async def test_api_failure_graceful_degradation():
    """Test 4: All models fail - graceful degradation"""
    print("\n=== Test 4: API Failure Graceful Degradation ===")

    os.environ['OPENROUTER_API_KEY'] = 'test-key-123'
    deduplicator = OpenRouterLLMDeduplicator(confidence_threshold=0.80)

    new = create_incident(
        "Test incident",
        "2025-10-05 12:00:00",
        "Test Airport",
        55.0, 12.0,
        "Test narrative"
    )

    existing = create_incident(
        "Existing incident",
        "2025-10-05 12:00:00",
        "Test Airport",
        55.0, 12.0,
        "Existing narrative"
    )

    # Mock API to raise error for all models
    from openai import APIError
    with patch.object(deduplicator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = APIError("API error", request=None, body=None)

        result = await deduplicator.analyze_potential_duplicate(new, existing, 0.85)

        assert result is None, f"Should return None on API failure, got: {result}"
        assert mock_create.call_count == 2, f"Should try both models, got: {mock_create.call_count} attempts"
        print(f"✓ PASS - Graceful degradation (returned None after {mock_create.call_count} model attempts)")


async def test_response_parsing():
    """Test 5: Response parsing edge cases"""
    print("\n=== Test 5: Response Parsing ===")

    os.environ['OPENROUTER_API_KEY'] = 'test-key-123'
    deduplicator = OpenRouterLLMDeduplicator(confidence_threshold=0.80)

    # Test with extra whitespace
    response1 = """
    VERDICT:    DUPLICATE

    CONFIDENCE:   0.95

    REASONING:  Same event at same location.
    """
    is_dup, reasoning, conf = deduplicator._parse_response(response1)
    assert is_dup is True, "Should parse DUPLICATE correctly"
    assert conf == 0.95, f"Should parse confidence correctly, got: {conf}"
    print("✓ PASS - Parsed response with whitespace")

    # Test with lowercase
    response2 = """VERDICT: duplicate
CONFIDENCE: 0.88
REASONING: Same incident."""
    is_dup, reasoning, conf = deduplicator._parse_response(response2)
    assert is_dup is True, "Should handle lowercase verdict"
    assert conf == 0.88, f"Should parse confidence correctly, got: {conf}"
    print("✓ PASS - Parsed lowercase verdict")

    # Test with missing fields
    response3 = """VERDICT: UNIQUE
REASONING: Different events."""
    is_dup, reasoning, conf = deduplicator._parse_response(response3)
    assert is_dup is False, "Should parse UNIQUE correctly"
    assert conf == 0.5, f"Should use default confidence, got: {conf}"
    print("✓ PASS - Parsed response with missing confidence")

    # Test invalid response
    response4 = """This is not a valid response."""
    is_dup, reasoning, conf = deduplicator._parse_response(response4)
    assert is_dup is False, "Should default to UNIQUE on parse failure"
    assert "unable to parse" in reasoning.lower(), f"Should have error reasoning, got: {reasoning}"
    print("✓ PASS - Handled invalid response gracefully")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OpenRouter LLM Deduplicator Test Suite")
    print("="*60)

    try:
        await test_clear_duplicate()
        await test_clear_unique()
        await test_asset_type_mismatch()
        await test_api_failure_graceful_degradation()
        await test_response_parsing()

        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED (5/5)")
        print("="*60)
        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)
