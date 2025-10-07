"""
Multi-Source Consolidation Engine for DroneWatch
Merges incidents from multiple sources and recalculates evidence scores

Architecture: "1 incident → multiple sources"
Strategy: Hash-based deduplication on location + time (NOT title)
"""
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from verification import has_official_quote

logger = logging.getLogger(__name__)


class ConsolidationEngine:
    """
    Consolidates incidents from multiple sources using intelligent deduplication

    Deduplication Strategy:
    - Location: Rounded to ~1km precision (0.01°)
    - Time: Rounded to 6-hour windows
    - Title: NOT included in hash (different headlines = same incident)

    Evidence Score Recalculation:
    - Score 4: ANY official source (police/military/NOTAM/aviation)
    - Score 3: 2+ media sources WITH official quote detection
    - Score 2: 1 credible source (trust_weight ≥ 2)
    - Score 1: Low trust sources
    """

    def __init__(self, location_precision: float = 0.01, time_window_hours: int = 6):
        """
        Initialize consolidation engine

        Args:
            location_precision: Degree precision for location rounding (default 0.01° ≈ 1km)
            time_window_hours: Time window for incident grouping (default 6 hours)
        """
        self.location_precision = location_precision
        self.time_window_hours = time_window_hours
        logger.info(f"Consolidation engine initialized: location_precision={location_precision}°, "
                   f"time_window={time_window_hours}h")

    def consolidate_incidents(self, incidents: List[Dict]) -> List[Dict]:
        """
        Consolidate list of incidents by merging duplicates

        Args:
            incidents: List of raw incident dictionaries

        Returns:
            List of consolidated incidents with merged sources
        """
        if not incidents:
            return []

        logger.info(f"Starting consolidation of {len(incidents)} incidents")

        # Group incidents by hash
        incident_groups = {}
        for incident in incidents:
            hash_key = self._generate_incident_hash(incident)

            if hash_key not in incident_groups:
                incident_groups[hash_key] = []

            incident_groups[hash_key].append(incident)

        # Merge grouped incidents
        consolidated = []
        for hash_key, group in incident_groups.items():
            if len(group) == 1:
                # Single incident - no consolidation needed
                consolidated.append(group[0])
            else:
                # Multiple incidents - merge sources
                merged = self._merge_incidents(group)
                consolidated.append(merged)
                logger.info(f"Merged {len(group)} incidents into 1 (hash={hash_key[:8]}...)")

        logger.info(f"Consolidation complete: {len(incidents)} → {len(consolidated)} incidents")
        return consolidated

    def _generate_incident_hash(self, incident: Dict) -> str:
        """
        Generate deduplication hash based on location + time

        Args:
            incident: Incident dictionary

        Returns:
            Hash string
        """
        # Round location to precision
        lat = incident.get('lat')
        lon = incident.get('lon')

        if lat is None or lon is None:
            # No location - use country + asset_type as fallback
            lat_rounded = "unknown"
            lon_rounded = "unknown"
        else:
            lat_rounded = round(lat / self.location_precision) * self.location_precision
            lon_rounded = round(lon / self.location_precision) * self.location_precision

        # Round time to window
        occurred_at = incident.get('occurred_at')
        if isinstance(occurred_at, str):
            occurred_at = datetime.fromisoformat(occurred_at.replace('Z', '+00:00'))

        if occurred_at:
            # Round to nearest time window
            from datetime import timezone as tz
            epoch = datetime(1970, 1, 1, tzinfo=tz.utc)
            # Make sure occurred_at is timezone-aware
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=tz.utc)
            hours_since_epoch = (occurred_at - epoch).total_seconds() / 3600
            window_number = int(hours_since_epoch / self.time_window_hours)
            time_key = f"{window_number}"
        else:
            time_key = "unknown"

        # Create hash from location + time + country + asset_type
        # NOTE: Title is deliberately excluded to allow different headlines for same incident
        hash_input = f"{lat_rounded}_{lon_rounded}_{time_key}_{incident.get('country', 'unknown')}_{incident.get('asset_type', 'other')}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def _merge_incidents(self, incidents: List[Dict]) -> Dict:
        """
        Merge multiple incidents into one consolidated incident

        Strategy:
        - Use earliest occurred_at
        - Combine all sources
        - Use most detailed narrative
        - Recalculate evidence score
        - Keep highest trust_weight per source type

        Args:
            incidents: List of incidents to merge

        Returns:
            Merged incident dictionary
        """
        if len(incidents) == 1:
            return incidents[0]

        # Sort by occurred_at (earliest first)
        sorted_incidents = sorted(
            incidents,
            key=lambda x: datetime.fromisoformat(x['occurred_at'].replace('Z', '+00:00'))
                if x.get('occurred_at') else datetime.now()
        )

        # Use first incident as base
        base = sorted_incidents[0].copy()

        # Collect all sources (deduplicate by URL only)
        all_sources = []
        seen_source_urls = set()

        for incident in sorted_incidents:
            for source in incident.get('sources', []):
                source_url = source.get('source_url')
                if source_url and source_url not in seen_source_urls:
                    all_sources.append(source)
                    seen_source_urls.add(source_url)

        merged_sources = all_sources

        # Use longest narrative (most detailed)
        narratives = [inc.get('narrative', '') for inc in sorted_incidents if inc.get('narrative')]
        best_narrative = max(narratives, key=len) if narratives else base.get('narrative', '')

        # Use most descriptive title (longest with substance)
        titles = [inc.get('title', '') for inc in sorted_incidents if inc.get('title')]
        best_title = max(titles, key=lambda t: len(t.split())) if titles else base.get('title', '')

        # Recalculate evidence score based on all sources
        new_evidence_score = self._calculate_evidence_score(base, merged_sources)

        # Update merged incident
        base['sources'] = merged_sources
        base['narrative'] = best_narrative
        base['title'] = best_title
        base['evidence_score'] = new_evidence_score
        base['source_count'] = len(merged_sources)
        base['merged_from'] = len(sorted_incidents)

        # Update timestamps
        base['first_seen_at'] = sorted_incidents[0].get('occurred_at')
        base['last_seen_at'] = sorted_incidents[-1].get('occurred_at')

        logger.debug(f"Merged incident: {len(sorted_incidents)} sources → evidence={new_evidence_score}")

        return base

    def _calculate_evidence_score(self, incident: Dict, sources: List[Dict]) -> int:
        """
        Calculate evidence score based on source trust weights and quotes

        Implementation of 4-tier evidence system:
        - 4 (OFFICIAL): ANY official source (police/military/NOTAM/aviation)
        - 3 (VERIFIED): 2+ media sources WITH official quote
        - 2 (REPORTED): Single credible source (trust_weight ≥ 2)
        - 1 (UNCONFIRMED): Low trust sources

        Args:
            incident: Incident dictionary (for quote detection)
            sources: List of source dictionaries

        Returns:
            Evidence score (1-4)
        """
        if not sources:
            return 1

        # Check for official sources (trust_weight = 4 or specific types)
        official_sources = [
            s for s in sources
            if s.get('trust_weight', 0) == 4 or
               s.get('source_type', '').lower() in ['police', 'military', 'notam', 'aviation', 'aviation_authority']
        ]

        if official_sources:
            logger.debug(f"Evidence=4: Found {len(official_sources)} official sources")
            return 4

        # Check for multiple media sources with official quote
        media_sources = [
            s for s in sources
            if s.get('source_type', '').lower() in ['media', 'verified_media'] and
               s.get('trust_weight', 0) >= 2
        ]

        if len(media_sources) >= 2 and has_official_quote(incident):
            logger.debug(f"Evidence=3: {len(media_sources)} media sources with official quote")
            return 3

        # Check for single credible source
        max_trust = max([s.get('trust_weight', 0) for s in sources])
        if max_trust >= 2:
            logger.debug(f"Evidence=2: Single credible source (trust={max_trust})")
            return 2

        # Low trust sources
        logger.debug(f"Evidence=1: Low trust sources (max_trust={max_trust})")
        return 1

    def get_consolidation_stats(self, incidents: List[Dict]) -> Dict:
        """
        Get statistics about potential consolidation

        Args:
            incidents: List of incidents

        Returns:
            Statistics dictionary
        """
        if not incidents:
            return {
                'total_incidents': 0,
                'unique_hashes': 0,
                'potential_merges': 0,
                'merge_rate': 0.0
            }

        # Count unique hashes
        hashes = set()
        for incident in incidents:
            hash_key = self._generate_incident_hash(incident)
            hashes.add(hash_key)

        unique = len(hashes)
        total = len(incidents)
        potential_merges = total - unique
        merge_rate = potential_merges / total if total > 0 else 0.0

        return {
            'total_incidents': total,
            'unique_hashes': unique,
            'potential_merges': potential_merges,
            'merge_rate': merge_rate
        }
