"""
Verification logic for incident quality control
Determines auto-verification eligibility and calculates confidence scores
"""
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

# =====================================================
# Trust Level Definitions
# =====================================================

TRUST_LEVEL_4_SOURCES = [
    # Official government/police sources
    'politi.dk',
    'police',
    'trafikstyrelsen.dk',
    'forsvaret.dk',
    'naviair.dk',
    'notam',
]

TRUST_LEVEL_3_SOURCES = [
    # Major reputable media
    'dr.dk',
    'tv2.dk',
    'berlingske.dk',
    'jyllands-posten.dk',
    'politiken.dk',
    'reuters.com',
    'afp.com',
]

OFFICIAL_KEYWORDS = [
    # Danish
    'politi', 'politiet', 'luftfart', 'trafikstyrelsen',
    'forsvar', 'forsvaret', 'myndighed', 'bekræfter',
    'oplyser', 'ifølge politi',
    # English
    'police', 'authority', 'confirms', 'according to police',
    'defense', 'military', 'aviation authority'
]

# =====================================================
# Auto-Verification Logic
# =====================================================

def should_auto_verify(incident: Dict, source: Dict) -> bool:
    """
    Determine if incident should be auto-verified based on source trust

    Args:
        incident: Incident dictionary
        source: Source dictionary with trust_weight

    Returns:
        True if incident can be auto-verified, False otherwise
    """
    trust_weight = source.get('trust_weight', 1)
    source_type = source.get('type', '').lower()
    source_domain = source.get('domain', '').lower()

    # Level 4 sources (official) always auto-verify
    if trust_weight == 4 or source_type in ['police', 'notam']:
        logger.info(f"Auto-verify: Level 4 source ({source.get('name')})")
        return True

    # Check if source domain is in trust level 4 list
    if any(trusted in source_domain for trusted in TRUST_LEVEL_4_SOURCES):
        logger.info(f"Auto-verify: Trusted domain ({source_domain})")
        return True

    # Level 3 sources with official quotes auto-verify
    if trust_weight == 3 or source_type == 'media':
        if has_official_quote(incident):
            logger.info(f"Auto-verify: Level 3 source with official quote ({source.get('name')})")
            return True

    logger.info(f"Manual review required: trust_weight={trust_weight}, has_quote={has_official_quote(incident)}")
    return False


def has_official_quote(incident: Dict) -> bool:
    """
    Check if incident narrative contains official quotes or statements

    Args:
        incident: Incident dictionary

    Returns:
        True if official quote detected
    """
    text = ''

    # Check narrative
    if incident.get('narrative'):
        text += incident['narrative'].lower()

    # Check source quotes
    for source in incident.get('sources', []):
        if source.get('source_quote'):
            text += ' ' + source['source_quote'].lower()

    # Look for official keywords
    return any(keyword in text for keyword in OFFICIAL_KEYWORDS)


# =====================================================
# Confidence Score Calculation
# =====================================================

def calculate_confidence_score(incident: Dict, sources: List[Dict]) -> float:
    """
    Calculate confidence score 0.0-1.0 based on multiple factors

    Scoring breakdown:
    - Source trust level (40%)
    - Multiple source corroboration (20%)
    - Location specificity (20%)
    - Has quotes/evidence (10%)
    - Narrative completeness (10%)

    Args:
        incident: Incident dictionary
        sources: List of source dictionaries

    Returns:
        Confidence score between 0.0 and 1.0
    """
    score = 0.0

    # 1. Source trust (40%)
    if sources:
        max_trust = max([s.get('trust_weight', 1) for s in sources])
        score += (max_trust / 4.0) * 0.4
        logger.debug(f"Trust score component: {(max_trust / 4.0) * 0.4:.2f} (max_trust={max_trust})")

    # 2. Multiple sources (20%)
    source_count = len(sources)
    if source_count > 1:
        # Diminishing returns: 2 sources = 0.1, 3+ sources = 0.2
        source_bonus = min(source_count / 3.0, 1.0) * 0.2
        score += source_bonus
        logger.debug(f"Source count component: {source_bonus:.2f} ({source_count} sources)")

    # 3. Location specificity (20%)
    asset_type = incident.get('asset_type', 'other')
    if asset_type != 'other':
        # Specific asset type = full points
        score += 0.2
        logger.debug(f"Location component: 0.20 (asset_type={asset_type})")
    elif incident.get('location_name'):
        # Has location name but not specific asset = half points
        score += 0.1
        logger.debug(f"Location component: 0.10 (has location_name)")
    else:
        logger.debug(f"Location component: 0.00 (default location)")

    # 4. Has quotes/evidence (10%)
    has_quotes = False
    for source in sources:
        if source.get('source_quote'):
            has_quotes = True
            break
    if has_quotes:
        score += 0.1
        logger.debug(f"Quote component: 0.10 (has quotes)")

    # 5. Complete narrative (10%)
    narrative = incident.get('narrative', '')
    if len(narrative) > 100:
        score += 0.1
        logger.debug(f"Narrative component: 0.10 (length={len(narrative)})")
    elif len(narrative) > 50:
        score += 0.05
        logger.debug(f"Narrative component: 0.05 (length={len(narrative)})")

    final_score = min(score, 1.0)
    logger.info(f"Confidence score: {final_score:.2f}")
    return final_score


# =====================================================
# Review Queue Decision
# =====================================================

def requires_manual_review(incident: Dict, sources: List[Dict], confidence_score: float) -> tuple:
    """
    Determine if incident requires manual review

    Args:
        incident: Incident dictionary
        sources: List of source dictionaries
        confidence_score: Calculated confidence score

    Returns:
        (requires_review: bool, reason: str, priority: int)
    """
    # Check if auto-verified
    if sources and should_auto_verify(incident, sources[0]):
        return (False, None, None)

    # Determine reason and priority for review
    reasons = []
    priority = 3  # default: medium

    # Low trust source
    max_trust = max([s.get('trust_weight', 1) for s in sources]) if sources else 1
    if max_trust < 3:
        reasons.append(f"Low trust source (level {max_trust})")
        priority = min(priority, 2)  # high priority

    # Low confidence score
    if confidence_score < 0.5:
        reasons.append(f"Low confidence score ({confidence_score:.2f})")
        priority = min(priority, 2)

    # Missing location
    if incident.get('asset_type') == 'other' and not incident.get('location_name'):
        reasons.append("Generic/missing location")
        priority = min(priority, 3)

    # Short narrative
    if len(incident.get('narrative', '')) < 50:
        reasons.append("Insufficient narrative")

    # No sources
    if not sources:
        reasons.append("No sources attached")
        priority = 1  # critical

    reason = "; ".join(reasons) if reasons else "Standard review"
    return (True, reason, priority)


# =====================================================
# Verification Status Helper
# =====================================================

def get_verification_status(incident: Dict, sources: List[Dict]) -> str:
    """
    Determine appropriate verification status for incident

    Args:
        incident: Incident dictionary
        sources: List of source dictionaries

    Returns:
        'auto_verified', 'pending', or existing status
    """
    # Check if already has verification status
    if incident.get('verification_status'):
        return incident['verification_status']

    # Determine if can auto-verify
    if sources and should_auto_verify(incident, sources[0]):
        return 'auto_verified'

    return 'pending'


# =====================================================
# Batch Verification
# =====================================================

def verify_batch(incidents: List[Dict]) -> Dict:
    """
    Verify a batch of incidents and return statistics

    Args:
        incidents: List of incident dictionaries

    Returns:
        Statistics dictionary
    """
    stats = {
        'total': len(incidents),
        'auto_verified': 0,
        'requires_review': 0,
        'avg_confidence': 0.0,
        'by_trust_level': {1: 0, 2: 0, 3: 0, 4: 0}
    }

    confidence_scores = []

    for incident in incidents:
        sources = incident.get('sources', [])

        # Calculate confidence
        confidence = calculate_confidence_score(incident, sources)
        confidence_scores.append(confidence)
        incident['confidence_score'] = confidence

        # Determine verification status
        verification_status = get_verification_status(incident, sources)
        incident['verification_status'] = verification_status

        if verification_status == 'auto_verified':
            stats['auto_verified'] += 1
        else:
            stats['requires_review'] += 1

        # Track by trust level
        if sources:
            max_trust = max([s.get('trust_weight', 1) for s in sources])
            stats['by_trust_level'][max_trust] = stats['by_trust_level'].get(max_trust, 0) + 1

    # Calculate average confidence
    if confidence_scores:
        stats['avg_confidence'] = sum(confidence_scores) / len(confidence_scores)

    logger.info(f"Batch verification complete: {stats['auto_verified']} auto-verified, "
                f"{stats['requires_review']} require review, "
                f"avg confidence: {stats['avg_confidence']:.2f}")

    return stats