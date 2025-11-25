"""
AI-Powered Incident Similarity Detection using OpenRouter

Uses DeepSeek R1 (FREE) via OpenRouter API for semantic incident matching.
Fallback to rule-based matching if AI unavailable.
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass

try:
    import openai  # OpenRouter uses OpenAI SDK format
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("openai package not installed. AI similarity disabled, using rule-based fallback.")

try:
    from Levenshtein import distance as levenshtein_distance
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False
    logging.warning("python-Levenshtein not installed. Using basic string matching.")

logger = logging.getLogger(__name__)


@dataclass
class SimilarityResult:
    """Result of incident similarity analysis"""
    is_duplicate: bool
    confidence: float  # 0.0-1.0
    reasoning: str
    method: str  # 'ai', 'fuzzy', 'rule_based'
    merged_title: Optional[str] = None
    merged_narrative: Optional[str] = None


class OpenRouterClient:
    """
    Client for OpenRouter API with automatic model rotation to avoid rate limits
    """

    # Free models to rotate through when rate limits hit
    FREE_MODELS = [
        "deepseek/deepseek-r1:free",           # Primary: Best quality, slower
        "x-ai/grok-4-fast:free",               # Backup 1: Fast, good quality
        "google/gemini-2.5-flash-lite-preview-09-2025:free",  # Backup 2: Very fast
        "zhipu-ai/glm-4-flash:free",           # Backup 3: Alternative provider
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek/deepseek-r1:free",
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        """
        Initialize OpenRouter client with model rotation

        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            model: Primary model to use (falls back to others if rate limited)
            base_url: OpenRouter API endpoint
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.primary_model = model
        self.current_model = model
        self.base_url = base_url
        self.model_index = 0  # Track which model we're using

        if not self.api_key:
            logger.warning("No OPENROUTER_API_KEY found. AI similarity disabled.")
            self.enabled = False
        elif not OPENAI_AVAILABLE:
            logger.warning("openai package not available. AI similarity disabled.")
            self.enabled = False
        else:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.enabled = True
            logger.info(f"OpenRouter client initialized with primary model: {self.primary_model}")
            logger.info(f"Backup models available: {len(self.FREE_MODELS) - 1}")

        # In-memory cache for session
        self.cache = {}

    def _get_next_model(self) -> Optional[str]:
        """
        Get next available model for rotation
        Returns None if all models exhausted
        """
        self.model_index += 1
        if self.model_index < len(self.FREE_MODELS):
            next_model = self.FREE_MODELS[self.model_index]
            logger.info(f"🔄 Rotating to backup model: {next_model}")
            return next_model
        logger.warning("⚠️ All free models exhausted. Falling back to rule-based.")
        return None

    async def compare_incidents(
        self,
        incident1: Dict,
        incident2: Dict
    ) -> SimilarityResult:
        """
        Compare two incidents using AI to determine if they're duplicates

        Args:
            incident1: First incident dict with title, narrative, lat, lon, occurred_at
            incident2: Second incident dict

        Returns:
            SimilarityResult with is_duplicate, confidence, reasoning
        """
        if not self.enabled:
            # Fallback to rule-based
            logger.debug("AI disabled, using rule-based fallback")
            return await self._rule_based_comparison(incident1, incident2)

        # Check cache
        cache_key = self._get_cache_key(incident1, incident2)
        if cache_key in self.cache:
            logger.debug("Using cached similarity result")
            return self.cache[cache_key]

        # Build prompt
        prompt = self._build_comparison_prompt(incident1, incident2)

        # Try models in rotation until one works
        while True:
            try:
                # Call OpenRouter API with current model
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.current_model,
                    messages=[
                        {
                            "role": "system",
                            "content": DEDUPLICATION_SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,  # Low temperature for consistency
                    max_tokens=500
                )
                break  # Success! Exit retry loop

            except Exception as e:
                error_msg = str(e)

                # Check if it's a rate limit error (429)
                if '429' in error_msg or 'rate' in error_msg.lower():
                    logger.warning(f"⚠️ Rate limit hit on {self.current_model}")

                    # Try next model
                    next_model = self._get_next_model()
                    if next_model:
                        self.current_model = next_model
                        await asyncio.sleep(1)  # Brief delay before retry
                        continue  # Retry with new model
                    else:
                        # All models exhausted, fall back to rule-based
                        logger.error("All free models rate limited. Using rule-based fallback.")
                        return await self._rule_based_comparison(incident1, incident2)
                else:
                    # Different error, re-raise
                    raise

        try:

            # Parse response
            content = response.choices[0].message.content
            result_dict = json.loads(content)

            # 🛡️ ANTI-HALLUCINATION VALIDATION #1: Check required fields
            if not all(key in result_dict for key in ['is_duplicate', 'confidence', 'reasoning']):
                logger.warning("AI response missing required fields. Using rule-based fallback.")
                return await self._rule_based_comparison(incident1, incident2)

            # 🛡️ ANTI-HALLUCINATION VALIDATION #2: Validate confidence score
            confidence = result_dict.get('confidence', 0.0)
            if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
                logger.warning(f"Invalid confidence score from AI: {confidence}. Using rule-based fallback.")
                return await self._rule_based_comparison(incident1, incident2)

            # 🛡️ ANTI-HALLUCINATION VALIDATION #3: Cross-check with rule-based
            rule_result = await self._rule_based_comparison(incident1, incident2)

            # If AI says duplicate but rule-based says NOT duplicate:
            # - For LOCATION mismatches: ALWAYS reject (different places = different events)
            # - For TIME mismatches: Only reject if AI confidence is LOW (<0.75)
            #   (News articles about same event can be published days apart)
            if result_dict.get('is_duplicate') and not rule_result.is_duplicate:
                if 'Locations' in rule_result.reasoning:
                    # Location mismatch = definitely not same event
                    logger.warning(
                        f"AI hallucination detected: {rule_result.reasoning}. REJECTING AI, using facts."
                    )
                    return rule_result
                elif 'Times' in rule_result.reasoning and confidence < 0.75:
                    # Time mismatch + low confidence = probably different events
                    logger.warning(
                        f"AI low confidence on time mismatch: {rule_result.reasoning}. REJECTING AI, using facts."
                    )
                    return rule_result
                # If time mismatch but HIGH confidence (>=0.75), trust AI
                # (likely news coverage of same event published over multiple days)

            # 🛡️ ANTI-HALLUCINATION VALIDATION #3.5: Detect geocoding conflicts
            # If AI mentions different location than coordinates, reject merge
            reasoning = result_dict.get('reasoning', '')
            reasoning_lower = reasoning.lower()
            lat1, lon1 = incident1.get('lat'), incident1.get('lon')
            lat2, lon2 = incident2.get('lat'), incident2.get('lon')

            # Check if AI mentions specific locations that don't match coordinates
            location_keywords = ['portugal', 'troia', 'sesimbra', 'spain', 'france', 'germany',
                               'italy', 'uk', 'england', 'scotland', 'ireland', 'belgium',
                               'netherlands', 'poland', 'estonia', 'latvia', 'lithuania']

            # If both incidents have same coordinates AND AI mentions specific non-Nordic location
            if (abs(lat1 - lat2) < 0.001 and abs(lon1 - lon2) < 0.001 and
                result_dict.get('is_duplicate')):
                for keyword in location_keywords:
                    if keyword in reasoning_lower:
                        logger.warning(
                            f"🚨 GEOCODING CONFLICT: AI mentions '{keyword}' but coordinates show "
                            f"({lat1:.4f}, {lon1:.4f}). Likely default coordinates. REJECTING merge."
                        )
                        return SimilarityResult(
                            is_duplicate=False,
                            confidence=0.0,
                            reasoning=f"Geocoding conflict detected: AI mentions {keyword} but coordinates "
                                    f"suggest default location. Cannot trust merge.",
                            method='geocoding_conflict_detected'
                        )

            # 🛡️ ANTI-HALLUCINATION VALIDATION #4: Check reasoning quality
            if len(reasoning) < 20:
                logger.warning("AI reasoning too short, may be hallucinating. Using rule-based.")
                return await self._rule_based_comparison(incident1, incident2)

            # 🛡️ ANTI-HALLUCINATION VALIDATION #5: Verify merged content doesn't introduce new facts
            merged_title = result_dict.get('merged_title', '')
            merged_narrative = result_dict.get('merged_narrative', '')

            if merged_title and not self._validate_merged_content(
                merged_title, incident1.get('title', ''), incident2.get('title', '')
            ):
                logger.warning("AI merged title contains hallucinated content. Using original.")
                merged_title = incident1.get('title')  # Use original

            if merged_narrative and not self._validate_merged_content(
                merged_narrative, incident1.get('narrative', ''), incident2.get('narrative', '')
            ):
                logger.warning("AI merged narrative contains hallucinated content. Using original.")
                merged_narrative = incident1.get('narrative')  # Use original

            result = SimilarityResult(
                is_duplicate=result_dict.get('is_duplicate', False),
                confidence=min(confidence, 0.95),  # Cap at 0.95 to never be 100% certain
                reasoning=f"AI analysis: {reasoning} | Rule-based check: {rule_result.reasoning}",
                method='ai_validated',
                merged_title=merged_title or incident1.get('title'),
                merged_narrative=merged_narrative or incident1.get('narrative')
            )

            # Cache result
            self.cache[cache_key] = result

            logger.info(
                f"AI comparison (VALIDATED): duplicate={result.is_duplicate}, "
                f"confidence={result.confidence:.2f}, method={result.method}"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"AI returned invalid JSON: {e}. Falling back to rule-based.")
            return await self._rule_based_comparison(incident1, incident2)
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}. Falling back to rule-based.")
            return await self._rule_based_comparison(incident1, incident2)

    def _build_comparison_prompt(self, inc1: Dict, inc2: Dict) -> str:
        """Build comparison prompt for AI"""
        return f"""Compare these two drone incidents and determine if they're reporting the SAME event:

INCIDENT 1:
- Title: {inc1.get('title', 'N/A')}
- Narrative: {inc1.get('narrative', 'N/A')[:500]}
- Location: ({inc1.get('lat')}, {inc1.get('lon')})
- Time: {inc1.get('occurred_at')}
- Asset Type: {inc1.get('asset_type', 'N/A')}

INCIDENT 2:
- Title: {inc2.get('title', 'N/A')}
- Narrative: {inc2.get('narrative', 'N/A')[:500]}
- Location: ({inc2.get('lat')}, {inc2.get('lon')})
- Time: {inc2.get('occurred_at')}
- Asset Type: {inc2.get('asset_type', 'N/A')}

ANALYSIS REQUIREMENTS:
1. Are these describing the SAME physical event? (not just similar events)
2. Consider: location proximity, time correlation, asset type, narrative details
3. Provide confidence score (0.0-1.0)
4. If duplicate, suggest merged title and narrative

Return JSON:
{{
    "is_duplicate": boolean,
    "confidence": float,
    "reasoning": "your detailed analysis",
    "merged_title": "best title for merged incident",
    "merged_narrative": "comprehensive narrative combining both"
}}"""

    async def _rule_based_comparison(
        self,
        inc1: Dict,
        inc2: Dict
    ) -> SimilarityResult:
        """
        Fallback rule-based comparison when AI unavailable

        Rules:
        - Must be within 500m
        - Must be within 3 hours
        - Title similarity >80% OR narrative similarity >70%
        """
        from datetime import datetime
        from math import radians, cos, sin, asin, sqrt

        # Calculate geographic distance
        lat1, lon1 = inc1.get('lat'), inc1.get('lon')
        lat2, lon2 = inc2.get('lat'), inc2.get('lon')

        # Haversine formula
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        distance_km = 6371 * c  # Earth radius in km

        # Must be within 500m
        if distance_km > 0.5:
            return SimilarityResult(
                is_duplicate=False,
                confidence=1.0,
                reasoning=f"Locations {distance_km:.2f}km apart (>500m threshold)",
                method='rule_based'
            )

        # Calculate time difference
        try:
            time1 = datetime.fromisoformat(inc1.get('occurred_at').replace('Z', '+00:00'))
            time2 = datetime.fromisoformat(inc2.get('occurred_at').replace('Z', '+00:00'))
            time_diff_hours = abs((time1 - time2).total_seconds() / 3600)
        except:
            time_diff_hours = 24  # Assume different if can't parse

        # Must be within 3 hours
        if time_diff_hours > 3:
            return SimilarityResult(
                is_duplicate=False,
                confidence=0.9,
                reasoning=f"Times {time_diff_hours:.1f}hrs apart (>3hr threshold)",
                method='rule_based'
            )

        # Calculate title similarity
        title_sim = self._calculate_title_similarity(
            inc1.get('title', ''),
            inc2.get('title', '')
        )

        # Calculate narrative similarity if both exist
        narrative_sim = 0.0
        if inc1.get('narrative') and inc2.get('narrative'):
            narrative_sim = self._calculate_title_similarity(
                inc1.get('narrative', ''),
                inc2.get('narrative', '')
            )

        # Decision logic
        if title_sim > 0.8 or (narrative_sim > 0.7 and narrative_sim > 0):
            confidence = max(title_sim, narrative_sim)
            return SimilarityResult(
                is_duplicate=True,
                confidence=confidence,
                reasoning=f"Rule-based match: title_sim={title_sim:.2f}, narrative_sim={narrative_sim:.2f}, distance={distance_km:.2f}km, time_diff={time_diff_hours:.1f}hrs",
                method='rule_based',
                merged_title=inc1.get('title') if len(inc1.get('title', '')) > len(inc2.get('title', '')) else inc2.get('title'),
                merged_narrative=inc1.get('narrative') if len(inc1.get('narrative', '')) > len(inc2.get('narrative', '')) else inc2.get('narrative')
            )

        return SimilarityResult(
            is_duplicate=False,
            confidence=0.7,
            reasoning=f"No match: title_sim={title_sim:.2f}, narrative_sim={narrative_sim:.2f}",
            method='rule_based'
        )

    def _calculate_title_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using Levenshtein or fallback"""
        if not text1 or not text2:
            return 0.0

        text1 = text1.lower().strip()
        text2 = text2.lower().strip()

        if text1 == text2:
            return 1.0

        if LEVENSHTEIN_AVAILABLE:
            # Levenshtein distance normalized
            max_len = max(len(text1), len(text2))
            if max_len == 0:
                return 0.0
            dist = levenshtein_distance(text1, text2)
            return 1 - (dist / max_len)
        else:
            # Simple fallback: count common words
            words1 = set(text1.split())
            words2 = set(text2.split())
            if not words1 or not words2:
                return 0.0
            common = words1 & words2
            return len(common) / max(len(words1), len(words2))

    def _validate_merged_content(
        self,
        merged: str,
        original1: str,
        original2: str
    ) -> bool:
        """
        Validate that merged content doesn't hallucinate new facts

        Checks:
        1. Merged text should be similar length to originals (not 10x longer)
        2. Key words from merged should exist in at least one original
        3. No suspicious phrases like "I think", "probably", "maybe"

        Returns:
            True if merged content is valid, False if likely hallucinated
        """
        if not merged or not (original1 or original2):
            return True  # Nothing to validate

        merged_lower = merged.lower()

        # Check 1: Length sanity
        max_orig_len = max(len(original1 or ''), len(original2 or ''))
        if len(merged) > max_orig_len * 3:
            logger.warning(
                f"Merged content {len(merged)} chars is >3x longer than "
                f"originals ({max_orig_len} chars). Likely hallucinated."
            )
            return False

        # Check 2: Hallucination phrases
        hallucination_phrases = [
            'i think', 'i believe', 'probably', 'maybe', 'perhaps',
            'it seems', 'it appears', 'could be', 'might be',
            'according to my analysis', 'based on the information',
            'as an ai', 'i cannot', 'i apologize'
        ]
        for phrase in hallucination_phrases:
            if phrase in merged_lower:
                logger.warning(f"Merged content contains hallucination phrase: '{phrase}'")
                return False

        # Check 3: Key words should come from originals
        # Extract words >4 chars from merged
        merged_words = set(w.lower() for w in merged.split() if len(w) > 4)
        orig1_words = set(w.lower() for w in (original1 or '').split() if len(w) > 4)
        orig2_words = set(w.lower() for w in (original2 or '').split() if len(w) > 4)
        orig_words = orig1_words | orig2_words

        if not orig_words:
            return True  # Nothing to compare

        # At least 60% of merged words should come from originals
        common_words = merged_words & orig_words
        if len(merged_words) > 0:
            overlap_ratio = len(common_words) / len(merged_words)
            if overlap_ratio < 0.6:
                logger.warning(
                    f"Merged content has low word overlap ({overlap_ratio:.1%}) "
                    f"with originals. May be hallucinated."
                )
                return False

        return True

    def _get_cache_key(self, inc1: Dict, inc2: Dict) -> str:
        """Generate cache key for incident pair"""
        # Sort by ID to ensure consistent cache key
        id1 = inc1.get('id', inc1.get('title', ''))
        id2 = inc2.get('id', inc2.get('title', ''))
        if id1 > id2:
            id1, id2 = id2, id1

        content = f"{id1}||{id2}"
        return hashlib.md5(content.encode()).hexdigest()


# System prompt for AI deduplication
DEDUPLICATION_SYSTEM_PROMPT = """You are an expert analyst specializing in drone incident verification and deduplication.

Your task is to determine if two incident reports are describing the SAME real-world event.

GUIDELINES:
- Same event = same location (within 1km), same timeframe (within 6hrs), same basic facts
- Different perspectives of same event = DUPLICATE
- Multiple drone incidents at same location on different days = NOT DUPLICATE
- Similar incidents at different locations = NOT DUPLICATE

⚠️ CRITICAL RULES - NO HALLUCINATIONS:
1. DO NOT invent or imagine details not present in the original incidents
2. DO NOT add speculative information (no "probably", "might be", "could be")
3. DO NOT include AI commentary ("I think", "based on my analysis", "it seems")
4. ONLY combine facts explicitly stated in the two incidents
5. If information conflicts, use the more specific/detailed version
6. If unsure, mark as NOT DUPLICATE (be conservative)

MERGED CONTENT RULES:
- merged_title: Combine only actual words from both titles (no new content)
- merged_narrative: Combine only actual facts from both narratives (no interpretation)
- Keep merged content under 2x the length of originals

Be conservative: only mark as duplicate if >80% confident they're the same event.

Return JSON with:
- is_duplicate: boolean
- confidence: float (0.0-1.0, max 0.95)
- reasoning: string (2-3 sentences explaining your decision based on facts)
- merged_title: string (combined title using ONLY words from originals)
- merged_narrative: string (combined narrative using ONLY facts from originals)"""


# Example usage
if __name__ == "__main__":
    # Test the similarity engine
    import asyncio

    async def test():
        client = OpenRouterClient()

        incident1 = {
            "id": "test1",
            "title": "Copenhagen Airport Closed Due to Drone",
            "narrative": "Drone spotted near runway at 14:00, flights delayed",
            "lat": 55.6180,
            "lon": 12.6476,
            "occurred_at": "2025-10-01T14:00:00Z",
            "asset_type": "airport"
        }

        incident2 = {
            "id": "test2",
            "title": "CPH Airport Shutdown - UAV Incident",
            "narrative": "UAV observed close to landing strip around 2pm, operations suspended",
            "lat": 55.6185,  # Slightly different
            "lon": 12.6480,
            "occurred_at": "2025-10-01T14:30:00Z",  # 30 minutes later
            "asset_type": "airport"
        }

        result = await client.compare_incidents(incident1, incident2)

        print(f"Is Duplicate: {result.is_duplicate}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Method: {result.method}")
        print(f"Reasoning: {result.reasoning}")
        if result.merged_title:
            print(f"Merged Title: {result.merged_title}")

    asyncio.run(test())
