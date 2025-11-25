"""
LAYER 3: AI Verification (Optional)

Purpose: High-confidence classification for edge cases
Speed: ~300ms per call
Trigger: Only when Layer 2 confidence < 0.7
Cost: ~$0.50/1000 incidents (only ~30% need AI verification)

Uses OpenRouter GPT-3.5-turbo for intelligent classification.
Falls back to Layer 2 result if API unavailable.
"""

import logging
import os
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AIVerificationResult:
    """Result of Layer 3 AI verification"""
    is_incident: bool
    confidence: float
    category: str  # 'incident', 'policy', 'defense', 'simulation', 'discussion'
    reasoning: str
    used_ai: bool  # True if AI was actually called, False if fallback


def verify_with_ai(
    incident: dict,
    layer2_confidence: float,
    confidence_threshold: float = 0.7
) -> AIVerificationResult:
    """
    Layer 3: AI-powered verification for uncertain cases.

    Only calls AI if layer2_confidence < confidence_threshold.
    Falls back gracefully if AI unavailable.

    Args:
        incident: Incident dict with title, narrative, location_name
        layer2_confidence: Confidence from Layer 2 classification
        confidence_threshold: Minimum confidence to skip AI (default 0.7)

    Returns:
        AIVerificationResult with classification and reasoning
    """
    title = incident.get('title', '')
    narrative = incident.get('narrative', '')
    location = incident.get('location_name', '')

    # Skip AI if Layer 2 is confident enough
    if layer2_confidence >= confidence_threshold:
        logger.debug(f"Layer 3 SKIP (confidence {layer2_confidence:.2f} >= {confidence_threshold}): {title[:50]}")
        return AIVerificationResult(
            is_incident=True,  # Layer 2 already approved
            confidence=layer2_confidence,
            category='incident',
            reasoning='Layer 2 confidence sufficient, AI verification skipped',
            used_ai=False
        )

    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.debug(f"Layer 3 SKIP (no API key): {title[:50]}")
        return AIVerificationResult(
            is_incident=True,  # Fallback: trust Layer 2
            confidence=layer2_confidence,
            category='incident',
            reasoning='AI verification unavailable (no API key), using Layer 2 result',
            used_ai=False
        )

    # Try to use AI verification
    try:
        # Import here to avoid circular dependency and allow graceful failure
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from openai_client import OpenAIClient

        client = OpenAIClient()
        ai_result = client.verify_incident(title, narrative, location)

        logger.info(
            f"Layer 3 {'PASS' if ai_result['is_incident'] else 'REJECT'} "
            f"({ai_result['category']}, confidence={ai_result['confidence']:.2f}): {title[:50]}"
        )

        return AIVerificationResult(
            is_incident=ai_result['is_incident'],
            confidence=ai_result['confidence'],
            category=ai_result['category'],
            reasoning=ai_result.get('reasoning', 'AI classification complete'),
            used_ai=True
        )

    except ImportError:
        logger.warning(f"Layer 3 FALLBACK (OpenAI client not available): {title[:50]}")
        return AIVerificationResult(
            is_incident=True,
            confidence=layer2_confidence,
            category='incident',
            reasoning='AI client not available, using Layer 2 result',
            used_ai=False
        )

    except Exception as e:
        logger.warning(f"Layer 3 FALLBACK (API error: {e}): {title[:50]}")
        return AIVerificationResult(
            is_incident=True,  # Fail-safe: trust Layer 2
            confidence=layer2_confidence,
            category='incident',
            reasoning=f'AI verification failed ({str(e)}), using Layer 2 result',
            used_ai=False
        )
