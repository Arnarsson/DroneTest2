"""
Incident Consolidation Engine
Merges multiple sources reporting the same incident

Architecture: "1 incident = multiple sources"
- Deduplicates incidents by location + time + asset_type
- Merges sources from different outlets reporting same event
- Recalculates evidence scores based on combined authority
- Tracks source count and merge metadata
"""
import logging
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConsolidationEngine:
    """
    Consolidates incidents from multiple sources

    Rules:
    - Same location (~1km radius = 0.01° precision)
    - Same time window (±6 hours)
    - Same asset type (airport, military, etc.)

    Example:
    Input:
        [
            {title: "Drone spotted at Kastrup", source: "BT", trust_weight: 2},
            {title: "UAV forces airport closure", source: "Police", trust_weight: 4}
        ]
    Output:
        [
            {
                title: "UAV forces airport closure",
                sources: [Police (trust_weight: 4), BT (trust_weight: 2)],
                evidence_score: 4,  # Upgraded from 2 to 4
                merged_from: 2,
                source_count: 2
            }
        ]
    """

    def __init__(self, location_precision: float = 0.01, time_window_hours: int = 6):
        """
        Initialize consolidation engine

        Args:
            location_precision: Geographic precision in degrees (~1.1km per 0.01° at Nordic latitudes)
            time_window_hours: Time window for grouping incidents (6 hours = quarter-day buckets)
        """
        self.location_precision = location_precision
        self.time_window_hours = time_window_hours

    def generate_spacetime_key(self, incident: Dict) -> str:
        """
        Generate hash key based on location + time + asset_type

        Strategy: Round coordinates and time to create buckets that group nearby/concurrent incidents

        Example:
            lat 55.618, lon 12.648, time 2025-10-14T20:30, asset_type airport
            → "55.62_12.65_2025-10-14T18:00_airport"

            lat 55.619, lon 12.647, time 2025-10-14T21:15, asset_type airport
            → "55.62_12.65_2025-10-14T18:00_airport"  # SAME KEY → Will merge

        Args:
            incident: Incident dict with lat, lon, occurred_at, asset_type

        Returns:
            Spacetime hash key string
        """
        # Round coordinates to precision (0.01° ≈ 1.1km)
        lat_rounded = round(incident['lat'] / self.location_precision) * self.location_precision
        lon_rounded = round(incident['lon'] / self.location_precision) * self.location_precision

        # Round time to time window (e.g., 20:30 → 18:00, 21:15 → 18:00)
        occurred_at = datetime.fromisoformat(incident['occurred_at'])
        time_bucket = occurred_at.replace(
            hour=(occurred_at.hour // self.time_window_hours) * self.time_window_hours,
            minute=0,
            second=0,
            microsecond=0
        )

        asset_type = incident.get('asset_type', 'other')
        country = incident.get('country', 'unknown')

        # Include country in key to prevent cross-border merging
        # (e.g., Helsinki airport != Stockholm airport even if same time window)
        key = f"{lat_rounded:.2f}_{lon_rounded:.2f}_{time_bucket.isoformat()}_{asset_type}_{country}"
        return key

    def rank_sources_by_authority(self, sources: List[Dict]) -> List[Dict]:
        """
        Sort sources by trust_weight descending (4 → 3 → 2 → 1)

        Ranking:
        - 4: Official (police, military, aviation authority)
        - 3: Verified media (major news outlets)
        - 2: Credible media (local news, specialized outlets)
        - 1: Social media, unverified sources

        Args:
            sources: List of source dicts with trust_weight field

        Returns:
            Sorted list (highest trust first)
        """
        return sorted(sources, key=lambda s: s.get('trust_weight', 0), reverse=True)

    def recalculate_evidence_score(self, sources: List[Dict]) -> int:
        """
        Recalculate evidence score based on combined sources

        Rules (from constants/evidence.ts):
        - ANY trust_weight 4 source → score 4 (OFFICIAL)
        - 2+ trust_weight ≥2 sources → score 3 (VERIFIED - multi-source)
        - Single trust_weight ≥2 → score 2 (REPORTED)
        - Low trust → score 1 (UNCONFIRMED)

        Example:
            [BT (trust_weight: 2)] → score 2
            [BT (trust_weight: 2), DR (trust_weight: 2)] → score 3 (upgraded!)
            [BT (trust_weight: 2), Police (trust_weight: 4)] → score 4

        Args:
            sources: List of source dicts with trust_weight field

        Returns:
            Evidence score (1-4)
        """
        if not sources:
            return 1

        # Tier 4: ANY official source (police, military, NOTAM, aviation authority)
        max_trust = max([s.get('trust_weight', 1) for s in sources])
        if max_trust >= 4:
            return 4

        # Tier 3: Multiple credible sources (trust_weight ≥ 2)
        credible_sources = [s for s in sources if s.get('trust_weight', 0) >= 2]
        if len(credible_sources) >= 2:
            return 3  # Multi-source verification upgrade

        # Tier 2: Single credible source
        if max_trust >= 2:
            return 2

        # Tier 1: Low trust sources only
        return 1

    def merge_incident_data(self, incidents: List[Dict]) -> Dict:
        """
        Merge data from multiple incidents reporting the same event

        Strategy:
        - Keep longest narrative (most detailed)
        - Keep best title (most descriptive, not generic)
        - Merge all unique sources (deduplicate by URL)
        - Rank sources by authority
        - Recalculate evidence score based on combined sources
        - Track merge metadata (merged_from count, source_count)

        Args:
            incidents: List of incident dicts to merge

        Returns:
            Single merged incident dict
        """
        if not incidents:
            raise ValueError("Cannot merge empty incident list")

        # Use first incident as base template
        merged = incidents[0].copy()

        # Collect all sources (deduplicate by URL)
        all_sources = []
        seen_urls = set()

        for incident in incidents:
            for source in incident.get('sources', []):
                url = source.get('source_url')
                if url and url not in seen_urls:
                    all_sources.append(source)
                    seen_urls.add(url)

        # Rank sources by authority (highest trust first)
        all_sources = self.rank_sources_by_authority(all_sources)

        # Find longest narrative (most detailed reporting)
        narratives = [inc.get('narrative', '') for inc in incidents]
        longest_narrative = max(narratives, key=len) if narratives else ''

        # Find best title (longest with substance, avoid generic headlines)
        titles = [inc.get('title', '') for inc in incidents]
        # Score titles by word count (more words = more descriptive usually)
        best_title = max(titles, key=lambda t: len(t.split())) if titles else merged.get('title', '')

        # Update merged incident
        merged['sources'] = all_sources
        merged['narrative'] = longest_narrative
        merged['title'] = best_title
        merged['evidence_score'] = self.recalculate_evidence_score(all_sources)
        merged['merged_from'] = len(incidents)
        merged['source_count'] = len(all_sources)

        # Use highest trust source metadata as primary
        if all_sources:
            primary_source = all_sources[0]  # Already sorted by authority
            merged['source_type'] = primary_source.get('source_type', 'unknown')
            merged['source_name'] = primary_source.get('source_name', 'Multiple Sources')

        return merged

    def consolidate_incidents(self, incidents: List[Dict]) -> List[Dict]:
        """
        Main consolidation method

        Process:
        1. Group incidents by spacetime key (location + time + asset_type)
        2. For each group with 2+ incidents: merge into single incident
        3. For single-incident groups: keep as-is
        4. Return consolidated list with merge statistics logged

        Args:
            incidents: List of raw incident dicts

        Returns:
            List of consolidated incidents with merged sources
        """
        if not incidents:
            return []

        logger.info(f"Consolidating {len(incidents)} incidents...")

        # Group by spacetime key
        grouped = defaultdict(list)
        for incident in incidents:
            try:
                key = self.generate_spacetime_key(incident)
                grouped[key].append(incident)
            except Exception as e:
                logger.warning(f"Failed to generate key for incident: {incident.get('title', 'unknown')[:50]} - {e}")
                # Add to unique group to preserve incident
                unique_key = f"error_{id(incident)}"
                grouped[unique_key].append(incident)

        # Merge groups
        consolidated = []
        merge_count = 0
        total_merged_incidents = 0

        for key, group in grouped.items():
            if len(group) > 1:
                # Multiple incidents at same location+time → MERGE
                try:
                    merged = self.merge_incident_data(group)
                    consolidated.append(merged)
                    merge_count += 1
                    total_merged_incidents += len(group)

                    logger.info(
                        f"✓ Merged {len(group)} incidents: {merged['title'][:50]}... "
                        f"(evidence: {merged['evidence_score']}, sources: {len(merged['sources'])})"
                    )
                except Exception as e:
                    logger.error(f"Failed to merge group: {e}")
                    # Fallback: keep all incidents separate
                    consolidated.extend(group)
            else:
                # Single incident → Keep as-is
                consolidated.append(group[0])

        logger.info(
            f"Consolidation complete: {len(incidents)} → {len(consolidated)} incidents "
            f"({merge_count} merges, {total_merged_incidents} total incidents merged, "
            f"{len(consolidated) - merge_count} unique)"
        )

        return consolidated

    def get_consolidation_stats(self, incidents: List[Dict]) -> Dict:
        """
        Get consolidation statistics WITHOUT actually merging

        Useful for:
        - Pre-consolidation analysis
        - Testing consolidation logic
        - Monitoring merge rates

        Args:
            incidents: List of raw incident dicts

        Returns:
            Dict with statistics:
            - total_incidents: Total input incidents
            - unique_hashes: Number of unique spacetime groups
            - potential_merges: Number of groups with 2+ incidents
            - merge_rate: Percentage of groups that would merge
        """
        if not incidents:
            return {
                'total_incidents': 0,
                'unique_hashes': 0,
                'multi_source_groups': 0,
                'potential_merges': 0,
                'merge_rate': 0.0
            }

        grouped = defaultdict(list)
        for incident in incidents:
            try:
                key = self.generate_spacetime_key(incident)
                grouped[key].append(incident)
            except Exception as e:
                logger.warning(f"Failed to generate key for stats: {e}")
                continue

        multi_source_groups = {k: v for k, v in grouped.items() if len(v) > 1}

        return {
            'total_incidents': len(incidents),
            'unique_hashes': len(grouped),
            'multi_source_groups': len(multi_source_groups),
            'potential_merges': sum(len(v) - 1 for v in multi_source_groups.values()),
            'merge_rate': (len(multi_source_groups) / len(grouped) * 100) if grouped else 0.0
        }
