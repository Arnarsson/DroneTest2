#!/usr/bin/env python3
"""
DroneWatch Batch Deduplication Script

Uses AI-powered similarity detection to clean up duplicate incidents in the database.
Aggregates sources from duplicates into single incidents.

Usage:
    python3 scripts/ai_deduplicate_batch.py --dry-run          # Show merge plan
    python3 scripts/ai_deduplicate_batch.py --execute          # Execute merges
    python3 scripts/ai_deduplicate_batch.py --auto-approve 0.95  # Auto-merge high confidence
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncpg

# Add ingestion directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ingestion'))

from ai_similarity import OpenRouterClient, SimilarityResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DuplicateCluster:
    """Group of duplicate incidents"""
    primary_incident: Dict
    duplicate_incidents: List[Dict]
    similarity_scores: List[float]
    merge_reasoning: List[str]
    avg_confidence: float


@dataclass
class MergeResult:
    """Result of merge operation"""
    primary_id: str
    merged_count: int
    sources_created: int
    evidence_score_before: int
    evidence_score_after: int
    dry_run: bool


class BatchDeduplicator:
    """
    Batch deduplication of incidents using AI similarity detection
    """

    def __init__(
        self,
        database_url: str,
        ai_client: OpenRouterClient,
        dry_run: bool = True,
        auto_approve_threshold: float = 0.95
    ):
        self.database_url = database_url
        self.ai_client = ai_client
        self.dry_run = dry_run
        self.auto_approve_threshold = auto_approve_threshold
        self.conn: Optional[asyncpg.Connection] = None

    async def connect(self):
        """Connect to database"""
        try:
            # Disable statement caching for pgbouncer transaction mode
            self.conn = await asyncpg.connect(
                self.database_url,
                statement_cache_size=0
            )
            logger.info("✅ Connected to database")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    async def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            await self.conn.close()
            logger.info("✅ Disconnected from database")

    async def fetch_all_incidents(self) -> List[Dict]:
        """Fetch all incidents from database"""
        logger.info("📥 Fetching incidents from database...")

        query = """
        SELECT
            i.id,
            i.title,
            i.narrative,
            i.occurred_at,
            ST_Y(i.location::geometry) as lat,
            ST_X(i.location::geometry) as lon,
            i.evidence_score,
            i.asset_type,
            i.country,
            i.last_seen_at,
            i.first_seen_at,
            COALESCE(
                json_agg(
                    json_build_object(
                        'source_url', isc.source_url,
                        'source_title', isc.source_title,
                        'source_name', src.name,
                        'source_domain', src.domain
                    )
                ) FILTER (WHERE isc.id IS NOT NULL),
                '[]'::json
            ) as sources
        FROM public.incidents i
        LEFT JOIN public.incident_sources isc ON isc.incident_id = i.id
        LEFT JOIN public.sources src ON src.id = isc.source_id
        GROUP BY i.id
        ORDER BY i.occurred_at DESC
        """

        rows = await self.conn.fetch(query)
        incidents = [dict(row) for row in rows]

        logger.info(f"✅ Fetched {len(incidents)} incidents")
        return incidents

    async def group_by_proximity(
        self,
        incidents: List[Dict],
        radius_km: float = 5.0,
        time_window_hours: int = 24
    ) -> List[List[Dict]]:
        """
        Group incidents by geographic proximity and time window

        Args:
            incidents: List of incident dicts
            radius_km: Max distance to consider for grouping
            time_window_hours: Max time difference to consider

        Returns:
            List of incident groups (clusters)
        """
        logger.info(f"🔍 Grouping incidents (radius={radius_km}km, time_window={time_window_hours}hrs)")

        groups = []
        processed = set()

        for i, incident1 in enumerate(incidents):
            if incident1['id'] in processed:
                continue

            # Start new group
            group = [incident1]
            processed.add(incident1['id'])

            # Find nearby incidents
            for j, incident2 in enumerate(incidents[i+1:], start=i+1):
                if incident2['id'] in processed:
                    continue

                # Calculate distance
                distance_km = self._calculate_distance(
                    incident1['lat'], incident1['lon'],
                    incident2['lat'], incident2['lon']
                )

                # Calculate time difference
                time_diff_hours = self._calculate_time_diff(
                    incident1['occurred_at'],
                    incident2['occurred_at']
                )

                # Add to group if close enough
                if distance_km <= radius_km and time_diff_hours <= time_window_hours:
                    group.append(incident2)
                    processed.add(incident2['id'])

            # Only keep groups with 2+ incidents
            if len(group) > 1:
                groups.append(group)

        logger.info(f"✅ Found {len(groups)} groups with potential duplicates")
        for idx, group in enumerate(groups, 1):
            logger.info(f"   Group {idx}: {len(group)} incidents")

        return groups

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in km using Haversine formula"""
        from math import radians, cos, sin, asin, sqrt

        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return 6371 * c  # Earth radius in km

    def _calculate_time_diff(self, time1, time2) -> float:
        """Calculate time difference in hours"""
        if isinstance(time1, str):
            time1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
        if isinstance(time2, str):
            time2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))

        return abs((time1 - time2).total_seconds() / 3600)

    async def identify_duplicate_clusters(
        self,
        groups: List[List[Dict]],
        similarity_threshold: float = 0.80
    ) -> List[DuplicateCluster]:
        """
        Use AI to identify duplicate incidents within each group

        Args:
            groups: List of incident groups
            similarity_threshold: Min similarity to consider duplicate

        Returns:
            List of DuplicateCluster objects ready for merging
        """
        logger.info(f"🤖 Running AI similarity analysis (threshold={similarity_threshold})")

        clusters = []

        for group_idx, group in enumerate(groups, 1):
            logger.info(f"\n📊 Analyzing Group {group_idx}/{len(groups)} ({len(group)} incidents)")

            # Build similarity matrix
            n = len(group)
            similarity_matrix = [[0.0] * n for _ in range(n)]
            reasoning_matrix = [[None] * n for _ in range(n)]

            # Compare each pair
            for i in range(n):
                for j in range(i+1, n):
                    result: SimilarityResult = await self.ai_client.compare_incidents(
                        group[i], group[j]
                    )

                    similarity_matrix[i][j] = result.confidence if result.is_duplicate else 0.0
                    similarity_matrix[j][i] = similarity_matrix[i][j]
                    reasoning_matrix[i][j] = result.reasoning

                    if result.is_duplicate:
                        logger.info(
                            f"   ✓ Match found: "
                            f"'{group[i]['title'][:40]}...' ≈ '{group[j]['title'][:40]}...' "
                            f"(confidence={result.confidence:.2f}, method={result.method})"
                        )

            # Find connected components (transitive duplicates)
            # A-B duplicate + B-C duplicate => A-B-C cluster
            visited = set()

            for i in range(n):
                if i in visited:
                    continue

                # Start new cluster
                cluster_indices = [i]
                visited.add(i)

                # Find all connected incidents
                queue = [i]
                while queue:
                    current = queue.pop(0)
                    for j in range(n):
                        if j not in visited and similarity_matrix[current][j] >= similarity_threshold:
                            cluster_indices.append(j)
                            visited.add(j)
                            queue.append(j)

                # Create cluster if >1 incident
                if len(cluster_indices) > 1:
                    # Primary = most recent or highest evidence score
                    cluster_incidents = [group[idx] for idx in cluster_indices]
                    primary = max(
                        cluster_incidents,
                        key=lambda x: (x['evidence_score'], x['occurred_at'])
                    )
                    duplicates = [inc for inc in cluster_incidents if inc['id'] != primary['id']]

                    # Collect similarity scores and reasoning
                    scores = []
                    reasoning = []
                    primary_idx = cluster_indices[0]

                    for idx in cluster_indices[1:]:
                        scores.append(similarity_matrix[primary_idx][idx])
                        if reasoning_matrix[primary_idx][idx]:
                            reasoning.append(reasoning_matrix[primary_idx][idx])

                    cluster = DuplicateCluster(
                        primary_incident=primary,
                        duplicate_incidents=duplicates,
                        similarity_scores=scores,
                        merge_reasoning=reasoning,
                        avg_confidence=sum(scores) / len(scores) if scores else 0.0
                    )

                    clusters.append(cluster)

                    logger.info(
                        f"   🎯 Cluster identified: 1 primary + {len(duplicates)} duplicates "
                        f"(avg_confidence={cluster.avg_confidence:.2f})"
                    )

        logger.info(f"\n✅ Found {len(clusters)} clusters ready for merging")
        return clusters

    async def merge_cluster(
        self,
        cluster: DuplicateCluster,
        user_approved: bool = False
    ) -> MergeResult:
        """
        Merge duplicate incidents into primary incident

        Args:
            cluster: DuplicateCluster to merge
            user_approved: Whether user has approved this merge

        Returns:
            MergeResult with statistics
        """
        primary = cluster.primary_incident
        duplicates = cluster.duplicate_incidents

        logger.info(
            f"\n{'[DRY RUN] ' if self.dry_run else ''}Merging cluster: "
            f"primary={str(primary['id'])[:8]}, duplicates={len(duplicates)}"
        )

        if self.dry_run:
            # Simulate merge
            return MergeResult(
                primary_id=primary['id'],
                merged_count=len(duplicates),
                sources_created=len(duplicates),
                evidence_score_before=primary['evidence_score'],
                evidence_score_after=min(primary['evidence_score'] + 1, 4),
                dry_run=True
            )

        # Real merge
        try:
            async with self.conn.transaction():
                sources_created = 0

                # For each duplicate, create source entry in primary
                for dup in duplicates:
                    # Step 1: Create or get source entry in sources table
                    # Schema: UNIQUE (domain, source_type) - see sql/supabase_schema_v2.sql line 45
                    source_id = await self.conn.fetchval("""
                        INSERT INTO public.sources (
                            name,
                            domain,
                            source_type,
                            homepage_url,
                            trust_weight
                        ) VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (domain, source_type)
                        DO UPDATE SET name = EXCLUDED.name
                        RETURNING id
                    """,
                        f"Merged: {dup['title'][:50]}",
                        'dronewatch-internal',
                        'other',
                        f"internal://merged/{dup['id']}",
                        3  # Merged duplicates get trust_weight 3
                    )

                    # Step 2: Link source to incident
                    await self.conn.execute("""
                        INSERT INTO public.incident_sources (
                            incident_id,
                            source_id,
                            source_url,
                            source_title,
                            source_quote
                        ) VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (incident_id, source_url) DO NOTHING
                    """,
                        primary['id'],
                        source_id,
                        f"internal://merged/{dup['id']}",
                        dup['title'],
                        (dup.get('narrative') or '')[:500]
                    )
                    sources_created += 1

                    # Also migrate any existing sources from duplicate
                    await self.conn.execute("""
                        INSERT INTO public.incident_sources (
                            incident_id,
                            source_id,
                            source_url,
                            source_title,
                            source_quote,
                            published_at,
                            lang,
                            metadata
                        )
                        SELECT
                            $1,
                            source_id,
                            source_url,
                            source_title,
                            source_quote,
                            published_at,
                            lang,
                            metadata
                        FROM public.incident_sources
                        WHERE incident_id = $2
                        ON CONFLICT (incident_id, source_url) DO NOTHING
                    """,
                        primary['id'],
                        dup['id']
                    )

                # Recalculate evidence score based on all sources
                new_evidence_score = await self._recalculate_evidence_score(primary['id'])

                # Update primary incident
                await self.conn.execute("""
                    UPDATE public.incidents
                    SET
                        evidence_score = $2,
                        last_seen_at = NOW()
                    WHERE id = $1
                """, primary['id'], new_evidence_score)

                # Delete duplicates
                dup_ids = [dup['id'] for dup in duplicates]
                await self.conn.execute("""
                    DELETE FROM public.incidents
                    WHERE id = ANY($1)
                """, dup_ids)

                logger.info(
                    f"   ✅ Merged {len(duplicates)} duplicates into {str(primary['id'])[:8]}, "
                    f"created {sources_created} sources, evidence_score: "
                    f"{primary['evidence_score']} → {new_evidence_score}"
                )

                return MergeResult(
                    primary_id=primary['id'],
                    merged_count=len(duplicates),
                    sources_created=sources_created,
                    evidence_score_before=primary['evidence_score'],
                    evidence_score_after=new_evidence_score,
                    dry_run=False
                )

        except Exception as e:
            logger.error(f"   ❌ Merge failed: {e}")
            raise

    async def _recalculate_evidence_score(self, incident_id: str) -> int:
        """
        Recalculate evidence score based on sources

        Rules:
        - 1+ official source → score 4
        - 2+ verified sources → score 3
        - 1 verified source → score 2
        - Otherwise → score 1
        """
        sources = await self.conn.fetch("""
            SELECT s.source_type
            FROM public.incident_sources isc
            JOIN public.sources s ON isc.source_id = s.id
            WHERE isc.incident_id = $1
        """, incident_id)

        if not sources:
            return 1

        source_types = [s['source_type'] for s in sources]
        source_count = len(sources)

        # Check for official sources
        official_types = ['police', 'military', 'notam', 'official', 'government']
        if any(st in official_types for st in source_types):
            return 4

        # Check for multiple verified sources
        verified_types = ['news', 'media', 'verified']
        verified_count = sum(1 for st in source_types if st in verified_types)

        if verified_count >= 2:
            return 3
        elif verified_count >= 1:
            return 2

        # If no official/verified sources, use source count
        # This handles merged duplicates (type='other') and other edge cases
        if source_count >= 3:
            return 2  # Multiple sources
        elif source_count >= 1:
            return 1  # At least one source
        else:
            return 1  # Default

    async def run(self):
        """Main execution flow"""
        try:
            await self.connect()

            # Step 1: Fetch all incidents
            incidents = await self.fetch_all_incidents()

            if len(incidents) == 0:
                logger.info("ℹ️  No incidents found in database")
                return

            logger.info(f"\n📊 BEFORE: {len(incidents)} total incidents")

            # Step 2: Group by proximity
            groups = await self.group_by_proximity(incidents)

            if len(groups) == 0:
                logger.info("ℹ️  No potential duplicate groups found")
                return

            # Step 3: Identify duplicate clusters using AI
            clusters = await self.identify_duplicate_clusters(groups)

            if len(clusters) == 0:
                logger.info("ℹ️  No duplicate clusters found")
                return

            # Step 4: Present merge plan
            self._print_merge_plan(clusters)

            # Step 5: Execute merges (if not dry-run and approved)
            if not self.dry_run:
                logger.info("\n⚠️  EXECUTE MODE - Merges will be PERMANENT")

                # Request user approval
                for cluster in clusters:
                    should_merge = False

                    if cluster.avg_confidence >= self.auto_approve_threshold:
                        logger.info(f"✅ Auto-approving merge (confidence={cluster.avg_confidence:.2f})")
                        should_merge = True
                    else:
                        response = input(f"\nApprove merge? (y/n): ")
                        should_merge = response.lower() == 'y'

                    if should_merge:
                        result = await self.merge_cluster(cluster, user_approved=True)
                        logger.info(f"✅ Merge complete: {result.merged_count} duplicates merged")
                    else:
                        logger.info("⏭️  Skipped")

                # Final count
                final_incidents = await self.fetch_all_incidents()
                logger.info(f"\n📊 AFTER: {len(final_incidents)} total incidents")
                logger.info(f"🎉 Reduction: {len(incidents)} → {len(final_incidents)} ({len(incidents) - len(final_incidents)} removed)")

        finally:
            await self.disconnect()

    def _print_merge_plan(self, clusters: List[DuplicateCluster]):
        """Print merge plan for user review"""
        logger.info("\n" + "="*80)
        logger.info("📋 MERGE PLAN")
        logger.info("="*80)

        for idx, cluster in enumerate(clusters, 1):
            primary = cluster.primary_incident
            duplicates = cluster.duplicate_incidents

            logger.info(f"\nCluster {idx}/{len(clusters)}:")
            logger.info(f"  Confidence: {cluster.avg_confidence:.2f}")
            logger.info(f"  PRIMARY: {primary['title']}")
            logger.info(f"           ID: {primary['id']}")
            logger.info(f"           Date: {primary['occurred_at']}")
            logger.info(f"           Location: ({primary['lat']:.4f}, {primary['lon']:.4f})")
            logger.info(f"           Evidence: {primary['evidence_score']}")

            for dup_idx, dup in enumerate(duplicates, 1):
                logger.info(f"  DUP {dup_idx}:    {dup['title']}")
                logger.info(f"           ID: {dup['id']}")
                logger.info(f"           Date: {dup['occurred_at']}")

            if cluster.merge_reasoning:
                logger.info(f"  Reasoning: {cluster.merge_reasoning[0][:120]}...")

        logger.info("\n" + "="*80)
        logger.info(f"SUMMARY: {len(clusters)} clusters, {sum(len(c.duplicate_incidents) for c in clusters)} duplicates to merge")
        logger.info("="*80)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="DroneWatch AI-Powered Batch Deduplication")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show merge plan without executing (default)"
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help="Execute merges (CAUTION: permanent changes)"
    )
    parser.add_argument(
        '--auto-approve',
        type=float,
        default=0.95,
        help="Auto-approve merges above this confidence (default: 0.95)"
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.80,
        help="Similarity threshold for duplicates (default: 0.80)"
    )

    args = parser.parse_args()

    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        sys.exit(1)

    # Initialize AI client
    ai_client = OpenRouterClient()
    if not ai_client.enabled:
        logger.warning("⚠️  AI client not enabled, using rule-based fallback only")

    # Run deduplication
    deduplicator = BatchDeduplicator(
        database_url=database_url,
        ai_client=ai_client,
        dry_run=not args.execute,
        auto_approve_threshold=args.auto_approve
    )

    logger.info("🚀 DroneWatch Batch Deduplication")
    logger.info(f"   Mode: {'DRY RUN' if not args.execute else 'EXECUTE'}")
    logger.info(f"   Auto-approve threshold: {args.auto_approve}")
    logger.info(f"   Similarity threshold: {args.threshold}\n")

    await deduplicator.run()


if __name__ == "__main__":
    asyncio.run(main())
