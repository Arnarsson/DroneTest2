"""
LAYER 1: Fast Rejection

Purpose: Eliminate obvious non-incidents before any processing
Speed: <50ms (no DB calls, no API calls)
Expected rejection rate: ~60%

Checks:
1. Satire domain blocking (40+ known fake news sites)
2. Temporal validation (not too old, not future)
3. Basic drone keyword presence
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional
from dataclasses import dataclass

# Import satire domain checker
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from satire_domains import is_satire_domain, get_satire_reason

logger = logging.getLogger(__name__)


@dataclass
class RejectionResult:
    """Result of Layer 1 fast rejection check"""
    rejected: bool
    reason: Optional[str] = None
    details: Optional[str] = None


# Basic drone keywords for fast check
DRONE_KEYWORDS = {
    # English
    'drone', 'drones', 'uav', 'uavs', 'unmanned',
    # Danish
    'dron', 'droner', 'dronen',
    # Norwegian
    'drone', 'droner',
    # Swedish
    'drönare', 'dronare',
    # Finnish
    'drooni', 'droonit', 'lennokki',
    # German
    'drohne', 'drohnen',
    # French
    'drone', 'drones',
}


def has_drone_keyword(title: str, narrative: str = '') -> bool:
    """
    Fast check for drone-related keywords.
    This is a PERMISSIVE check - Layer 2 does the detailed filtering.
    """
    text = (title + ' ' + narrative).lower()
    return any(keyword in text for keyword in DRONE_KEYWORDS)


def is_recent(occurred_at: datetime, max_age_days: int = 60) -> Tuple[bool, str]:
    """
    Check if incident is within acceptable time range.

    Rules:
    - Not in future (>1 day ahead)
    - Not too old (>max_age_days)
    """
    now = datetime.now(timezone.utc)

    # Ensure timezone-aware
    if occurred_at.tzinfo is None:
        occurred_at = occurred_at.replace(tzinfo=timezone.utc)

    # Check for future dates
    if occurred_at > now + timedelta(days=1):
        return False, f"Future date: {occurred_at.isoformat()}"

    # Check for too old
    age = now - occurred_at
    if age.days > max_age_days:
        return False, f"Too old: {age.days} days (max: {max_age_days})"

    return True, "OK"


def fast_reject(incident: dict) -> RejectionResult:
    """
    Layer 1: Fast rejection checks.

    Returns RejectionResult with rejected=True if incident should be blocked.

    This is designed to be FAST - eliminates obvious non-incidents
    before any expensive processing.
    """
    title = incident.get('title', '')
    narrative = incident.get('narrative', '')

    # Check 1: Satire domain
    sources = incident.get('sources', [])
    for source in sources:
        source_url = source.get('source_url', '')
        if source_url and is_satire_domain(source_url):
            reason_short, reason_detail = get_satire_reason(source_url)
            logger.info(f"Layer 1 REJECT (satire): {title[:50]}")
            return RejectionResult(
                rejected=True,
                reason='satire_domain',
                details=reason_detail
            )

    # Check 2: Temporal validation
    occurred_at = incident.get('occurred_at')
    if occurred_at:
        if isinstance(occurred_at, str):
            try:
                # Handle ISO format with Z or timezone offset
                if occurred_at.endswith('Z'):
                    occurred_at = occurred_at[:-1] + '+00:00'
                occurred_at = datetime.fromisoformat(occurred_at)
            except ValueError:
                logger.warning(f"Invalid date format: {occurred_at}")
                return RejectionResult(
                    rejected=True,
                    reason='invalid_date',
                    details=f"Cannot parse date: {occurred_at}"
                )

        is_valid, reason = is_recent(occurred_at, max_age_days=60)
        if not is_valid:
            logger.info(f"Layer 1 REJECT (temporal): {title[:50]} - {reason}")
            return RejectionResult(
                rejected=True,
                reason='temporal',
                details=reason
            )

    # Check 3: Basic drone keyword presence
    if not has_drone_keyword(title, narrative):
        logger.info(f"Layer 1 REJECT (no drone keyword): {title[:50]}")
        return RejectionResult(
            rejected=True,
            reason='no_drone_keyword',
            details='No drone-related keywords found in title or narrative'
        )

    # Passed all fast checks
    return RejectionResult(rejected=False)
