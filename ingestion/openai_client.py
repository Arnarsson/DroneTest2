"""OpenAI/OpenRouter client utilities for text cleanup and incident verification."""

import hashlib
import json
import logging
import os
from typing import Dict, Optional

from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)


class OpenAIClientError(Exception):
    """Raised when the OpenAI API returns an error."""


class OpenAIClient:
    """Lightweight OpenAI/OpenRouter client for text cleanup and incident verification"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        # Support both OpenAI and OpenRouter
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY or OPENAI_API_KEY is not set")

        self.model_name = model

        # Detect if using OpenRouter
        self.use_openrouter = self.api_key.startswith("sk-or-") or os.getenv("OPENROUTER_API_KEY")

        if self.use_openrouter:
            # OpenRouter configuration
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            # Use model for OpenRouter (GPT-3.5-turbo is cheap and reliable)
            # Note: Free models often unavailable, using affordable paid model
            self.model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
            logger.info(f"Using OpenRouter with model: {self.model_name}")
        else:
            # Standard OpenAI
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"Using OpenAI with model: {self.model_name}")

        # Cache for verification results
        self._verification_cache = {}

    def cleanup_text(self, text: str, *, max_tokens: int = 512) -> str:
        """Call OpenAI to clean up noisy article text."""

        system_prompt = (
            "You clean up scraped news article content. Remove leftover text from "
            "news website UI elements like 'play-circle', 'Læs op', navigation menus, "
            "advertisements, social media buttons, and other non-article content. "
            " Preserve only the factual news content in Danish or English. "
            "Do NOT rewrite or rephrase anything - keep the original content exactly as written after cleaning. "
            "Return clean, readable text only."
        )

        try:
            completion_params = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
            }

            response = self.client.chat.completions.create(**completion_params)
        except OpenAIError as exc:
            logger.error("OpenAI cleanup failed: %s", exc, exc_info=True)
            raise OpenAIClientError("OpenAI cleanup failed") from exc

        if not response or not response.choices:
            logger.warning(
                "OpenAI cleanup returned no choices; fallback to original text")
            return text

        choice = response.choices[0]
        if not choice.message or not choice.message.content:
            logger.warning(
                "OpenAI cleanup returned empty content; fallback to original text")
            return text

        cleaned = choice.message.content.strip()

        if not cleaned:
            logger.warning(
                "OpenAI cleanup returned blank text; fallback to original")
            return text

        return cleaned

    def verify_incident(self, title: str, narrative: str, location: str = "") -> Dict:
        """
        Use AI to intelligently verify if article is an actual drone incident

        Args:
            title: Article title
            narrative: Article content/narrative
            location: Location name (optional)

        Returns:
            {
                'is_incident': bool,
                'confidence': float (0.0-1.0),
                'reasoning': str,
                'category': 'incident' | 'policy' | 'defense' | 'discussion' | 'unknown'
            }
        """
        # Check cache first
        cache_key = hashlib.md5(f"{title}:{narrative[:100]}".encode()).hexdigest()
        if cache_key in self._verification_cache:
            logger.debug(f"Cache hit for verification: {title[:50]}")
            return self._verification_cache[cache_key]

        system_prompt = """You are a drone incident classifier for European DroneWatch coverage (35-71°N, -10-31°E).

Analyze if this article is about an ACTUAL drone incident or a non-incident.

**CRITICAL: Only classify as "incident" if it's a REAL drone sighting or disruption that occurred in Europe.**

ACTUAL INCIDENTS (return is_incident=true):
- Drone observed/spotted/sighted at a location
- Airspace closed/suspended due to drone activity
- Airport operations disrupted by drones
- Investigation launched after drone detection
- Police/military responding to drone sighting
- Actual security breach or airspace violation

NON-INCIDENTS (return is_incident=false):
- SIMULATION: Military exercises, airport drills, training scenarios, test flights, demonstrations, rehearsals
  Examples: "NATO conducts counter-drone exercise", "Airport holds drone detection drill", "Military tests new drone defense system"

- POLICY: Drone bans, regulations, proposed measures, government announcements, advisories
  Examples: "New drone ban announced", "Government introduces restrictions", "No-fly zone established"

- DEFENSE: Military assets deployed, equipment sent to defend, security increased (without actual incident)
  Examples: "Troops rushed to defend", "Anti-drone systems deployed", "Security measures enhanced"

- DISCUSSION: Analysis pieces, opinion articles, think pieces about drone threats
  Examples: "The growing threat of drones", "Expert discusses drone security", "Report analyzes drone risks"

- FAKE: Satire, unverified rumors, absurd claims, conspiracy theories
  Examples: "Aliens use drones to spy", articles from satire sites, obviously false claims

Return ONLY valid JSON (no markdown, no extra text):
{
  "is_incident": true or false,
  "confidence": 0.0 to 1.0,
  "reasoning": "Brief 1-2 sentence explanation",
  "category": "incident" or "simulation" or "policy" or "defense" or "discussion" or "fake"
}"""

        user_prompt = f"""Title: {title}

Narrative: {narrative[:500]}

Location: {location if location else 'Not specified'}

Classify this article:"""

        try:
            completion_params = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.1,  # Low temperature for consistent classification
            }

            # Add OpenRouter-specific headers if needed
            if self.use_openrouter:
                completion_params["extra_headers"] = {
                    "HTTP-Referer": "https://dronemap.cc",
                    "X-Title": "DroneWatch Incident Verification"
                }

            response = self.client.chat.completions.create(**completion_params)

            if not response or not response.choices:
                logger.warning("AI verification returned no choices; assuming incident")
                return self._fallback_result(title, narrative)

            choice = response.choices[0]
            if not choice.message or not choice.message.content:
                logger.warning("AI verification returned empty content; assuming incident")
                return self._fallback_result(title, narrative)

            # Parse JSON response
            content = choice.message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response: {content[:200]}")
                return self._fallback_result(title, narrative)

            # Validate result structure
            if not all(key in result for key in ['is_incident', 'confidence', 'reasoning', 'category']):
                logger.warning(f"Invalid result structure: {result}")
                return self._fallback_result(title, narrative)

            # Cache successful result
            self._verification_cache[cache_key] = result
            logger.info(f"AI verification: {result['category']} (confidence: {result['confidence']}, is_incident: {result['is_incident']})")

            return result

        except OpenAIError as exc:
            logger.error(f"AI verification failed: {exc}", exc_info=True)
            raise OpenAIClientError("AI verification failed") from exc
        except Exception as exc:
            logger.error(f"Unexpected error in AI verification: {exc}", exc_info=True)
            return self._fallback_result(title, narrative)

    def _fallback_result(self, title: str, narrative: str) -> Dict:
        """Return fallback result when AI verification fails"""
        logger.warning("Using fallback verification (assumes incident)")
        return {
            'is_incident': True,  # Conservative: assume incident if AI fails
            'confidence': 0.5,
            'reasoning': 'AI verification unavailable - using fallback',
            'category': 'unknown'
        }
