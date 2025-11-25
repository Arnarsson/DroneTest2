"""
LAYER 2: Content Classification

Purpose: Distinguish real incidents from policy/deployment/discussion articles
Speed: ~100ms
Expected rejection rate: ~20% additional

Checks:
1. Full drone incident validation (keywords + context)
2. Non-incident detection (policy, simulation, defense)
3. Geographic text filtering (foreign incident mentions)
"""

import logging
from typing import Optional
from dataclasses import dataclass

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import is_drone_incident
from non_incident_filter import NonIncidentFilter

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of Layer 2 content classification"""
    is_incident: bool
    confidence: float  # 0.0 to 1.0
    category: str  # 'incident', 'policy', 'defense', 'simulation', 'foreign', 'not_drone'
    reason: Optional[str] = None


# Foreign location keywords - incidents ABOUT these places should be rejected
FOREIGN_KEYWORDS = [
    # War zones
    'ukraina', 'ukraine', 'ukrainian', 'kiev', 'kyiv', 'kharkiv',
    'russia', 'rusland', 'russian', 'moscow', 'putin',
    'belarus', 'belarusian', 'minsk',
    # Middle East
    'israel', 'gaza', 'tel aviv', 'iran', 'tehran', 'syria', 'iraq',
    'yemen', 'lebanon', 'saudi',
    # Asia
    'china', 'beijing', 'japan', 'tokyo', 'korea', 'seoul', 'taiwan',
    'india', 'delhi', 'pakistan', 'afghanistan',
    # Americas
    'united states', 'usa', 'washington', 'new york', 'canada', 'mexico',
    # Africa
    'egypt', 'cairo', 'nigeria', 'kenya', 'south africa',
]


def has_foreign_keywords(title: str, narrative: str = '') -> tuple:
    """
    Check if text mentions non-European locations.

    Returns: (has_foreign: bool, matched_keyword: str or None)
    """
    text = (title + ' ' + narrative).lower()

    for keyword in FOREIGN_KEYWORDS:
        if keyword in text:
            return True, keyword

    return False, None


def classify_incident(incident: dict) -> ClassificationResult:
    """
    Layer 2: Content classification.

    Performs detailed analysis to determine if this is a real incident
    vs policy announcement, defense deployment, simulation, etc.

    Returns ClassificationResult with confidence score.
    """
    title = incident.get('title', '')
    narrative = incident.get('narrative', '')

    # Check 1: Full drone incident validation (uses is_drone_incident from utils.py)
    if not is_drone_incident(title, narrative):
        logger.info(f"Layer 2 REJECT (not drone incident): {title[:50]}")
        return ClassificationResult(
            is_incident=False,
            confidence=0.9,
            category='not_drone',
            reason='Failed is_drone_incident() check - may be commercial, policy, or non-drone'
        )

    # Check 2: Non-incident filter (policy, simulation, discussion)
    non_incident_filter = NonIncidentFilter()
    is_non, filter_confidence, reasons = non_incident_filter.is_non_incident(incident)

    if is_non and filter_confidence >= 0.5:
        # Determine category from reasons
        category = 'policy'  # default
        if any('simulation' in r.lower() or 'drill' in r.lower() for r in reasons):
            category = 'simulation'
        elif any('defense' in r.lower() or 'deployment' in r.lower() for r in reasons):
            category = 'defense'
        elif any('discussion' in r.lower() or 'opinion' in r.lower() for r in reasons):
            category = 'discussion'

        logger.info(f"Layer 2 REJECT ({category}): {title[:50]}")
        return ClassificationResult(
            is_incident=False,
            confidence=filter_confidence,
            category=category,
            reason='; '.join(reasons) if reasons else 'Non-incident detected'
        )

    # Check 3: Foreign keyword check
    has_foreign, foreign_keyword = has_foreign_keywords(title, narrative)
    if has_foreign:
        logger.info(f"Layer 2 REJECT (foreign): {title[:50]} - keyword: {foreign_keyword}")
        return ClassificationResult(
            is_incident=False,
            confidence=0.95,
            category='foreign',
            reason=f'Foreign location keyword detected: "{foreign_keyword}"'
        )

    # Passed all checks - this appears to be a valid incident
    # Calculate confidence based on how strongly it passed
    confidence = 0.8  # Base confidence for passing all checks

    # Boost confidence if we have strong indicators
    text = (title + ' ' + narrative).lower()
    if any(word in text for word in ['police', 'politi', 'polisen', 'poliisi']):
        confidence += 0.1  # Police involvement is strong indicator
    if any(word in text for word in ['airport', 'lufthavn', 'flygplats', 'flughafen']):
        confidence += 0.05  # Airport location is strong indicator

    confidence = min(confidence, 1.0)

    logger.info(f"Layer 2 PASS (incident, confidence={confidence:.2f}): {title[:50]}")
    return ClassificationResult(
        is_incident=True,
        confidence=confidence,
        category='incident',
        reason=None
    )
