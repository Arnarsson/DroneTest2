"""
Duplicate Detection Performance Dashboard

Queries production database to show tier performance and statistics.

Usage:
    python3 duplicate_detection_stats.py

Features:
- Real-time duplicate detection metrics
- Tier performance breakdown
- Embedding coverage stats
- Merge rate analysis
- Historical trends (when implemented)
"""

import asyncio
import asyncpg
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional


class DuplicateDetectionStats:
    """Real-time statistics for duplicate detection system"""

    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize with database connection.

        Args:
            db_url: PostgreSQL connection string (or use DATABASE_URL env var)
        """
        self.db_url = db_url or os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")

    async def get_overall_stats(self) -> Dict:
        """
        Get overall duplicate detection statistics.

        Returns:
            {
                'total_incidents': int,
                'incidents_with_multiple_sources': int,
                'average_sources_per_incident': float,
                'embedding_coverage': str (percentage),
                'estimated_duplicate_rate': str (percentage)
            }
        """
        conn = await asyncpg.connect(self.db_url)

        try:
            # Total incidents
            total = await conn.fetchval("SELECT COUNT(*) FROM incidents")

            # Incidents with multiple sources (duplicates merged)
            multi_source_query = """
                SELECT COUNT(DISTINCT incident_id)
                FROM incident_sources
                GROUP BY incident_id
                HAVING COUNT(*) > 1
            """
            multi_source_result = await conn.fetch(multi_source_query)
            multi_source_count = len(multi_source_result)

            # Average sources per incident
            avg_sources = await conn.fetchval("""
                SELECT AVG(source_count)::NUMERIC(10,2)
                FROM (
                    SELECT incident_id, COUNT(*) as source_count
                    FROM incident_sources
                    GROUP BY incident_id
                ) AS counts
            """)

            # Embedding coverage (Tier 2 enabled)
            try:
                with_embeddings = await conn.fetchval(
                    "SELECT COUNT(*) FROM incident_embeddings"
                )
            except Exception:
                # Table might not exist yet
                with_embeddings = 0

            # Calculate percentages
            embedding_coverage = (with_embeddings / total * 100) if total > 0 else 0
            duplicate_rate = (multi_source_count / total * 100) if total > 0 else 0

            return {
                'total_incidents': total or 0,
                'incidents_with_multiple_sources': multi_source_count or 0,
                'average_sources_per_incident': float(avg_sources or 0),
                'embedding_coverage': f"{embedding_coverage:.1f}%",
                'estimated_duplicate_rate': f"{duplicate_rate:.1f}%"
            }

        finally:
            await conn.close()

    async def get_source_distribution(self) -> Dict:
        """
        Get distribution of sources per incident.

        Returns:
            {
                '1_source': int,
                '2_sources': int,
                '3_sources': int,
                '4+_sources': int
            }
        """
        conn = await asyncpg.connect(self.db_url)

        try:
            query = """
                SELECT
                    CASE
                        WHEN source_count = 1 THEN '1_source'
                        WHEN source_count = 2 THEN '2_sources'
                        WHEN source_count = 3 THEN '3_sources'
                        ELSE '4+_sources'
                    END AS category,
                    COUNT(*) as count
                FROM (
                    SELECT incident_id, COUNT(*) as source_count
                    FROM incident_sources
                    GROUP BY incident_id
                ) AS counts
                GROUP BY category
                ORDER BY category
            """

            results = await conn.fetch(query)

            distribution = {
                '1_source': 0,
                '2_sources': 0,
                '3_sources': 0,
                '4+_sources': 0
            }

            for row in results:
                distribution[row['category']] = row['count']

            return distribution

        finally:
            await conn.close()

    async def get_recent_merges(self, hours: int = 24) -> list:
        """
        Get recent duplicate merges (incidents with sources added recently).

        Args:
            hours: Look back this many hours

        Returns:
            List of recent merge events
        """
        conn = await asyncpg.connect(self.db_url)

        try:
            query = """
                SELECT
                    i.id,
                    i.title,
                    i.evidence_score,
                    COUNT(s.id) as source_count,
                    i.created_at
                FROM incidents i
                JOIN incident_sources s ON i.id = s.incident_id
                WHERE i.created_at >= NOW() - INTERVAL '%s hours'
                GROUP BY i.id, i.title, i.evidence_score, i.created_at
                HAVING COUNT(s.id) > 1
                ORDER BY i.created_at DESC
                LIMIT 10
            """ % hours

            results = await conn.fetch(query)

            merges = []
            for row in results:
                merges.append({
                    'incident_id': str(row['id']),
                    'title': row['title'][:60] + '...' if len(row['title']) > 60 else row['title'],
                    'evidence_score': row['evidence_score'],
                    'source_count': row['source_count'],
                    'created_at': row['created_at'].isoformat()
                })

            return merges

        finally:
            await conn.close()

    async def get_tier_effectiveness(self) -> Dict:
        """
        Estimate tier effectiveness based on merge patterns.

        Returns:
            {
                'tier1_catches': int (exact hash/fuzzy matches),
                'tier2_catches': int (semantic with embeddings),
                'tier3_catches': int (LLM reasoning edge cases),
                'unique_incidents': int (no duplicates found)
            }
        """
        # This is estimated based on source patterns
        # Real tracking would require logging which tier caught each duplicate

        conn = await asyncpg.connect(self.db_url)

        try:
            # Total incidents
            total = await conn.fetchval("SELECT COUNT(*) FROM incidents")

            # Incidents with 2+ sources (some caught by deduplication)
            merged = await conn.fetchval("""
                SELECT COUNT(DISTINCT incident_id)
                FROM incident_sources
                GROUP BY incident_id
                HAVING COUNT(*) >= 2
            """)

            # Estimate breakdown (this is approximate without tier logging)
            # Tier 1 typically catches ~60% (exact/fuzzy matches)
            # Tier 2 catches ~30% (semantic)
            # Tier 3 catches ~10% (edge cases)

            tier1_estimate = int((merged or 0) * 0.60)
            tier2_estimate = int((merged or 0) * 0.30)
            tier3_estimate = int((merged or 0) * 0.10)
            unique = (total or 0) - (merged or 0)

            return {
                'tier1_catches': tier1_estimate,
                'tier2_catches': tier2_estimate,
                'tier3_catches': tier3_estimate,
                'unique_incidents': unique,
                'note': 'Estimates based on merge patterns (actual tracking requires tier logging)'
            }

        finally:
            await conn.close()

    def print_dashboard(self, stats: Dict, distribution: Dict, merges: list, tier_stats: Dict):
        """
        Print beautiful dashboard to console.

        Args:
            stats: Overall statistics
            distribution: Source distribution
            merges: Recent merge events
            tier_stats: Tier effectiveness estimates
        """
        print("\n" + "="*80)
        print(" "*20 + "DUPLICATE DETECTION SYSTEM DASHBOARD")
        print("="*80)

        # Overall Stats
        print("\n📊 OVERALL STATISTICS")
        print("-" * 80)
        print(f"Total Incidents:              {stats['total_incidents']:>6}")
        print(f"Merged Duplicates:            {stats['incidents_with_multiple_sources']:>6}")
        print(f"Average Sources per Incident: {stats['average_sources_per_incident']:>6.2f}")
        print(f"Embedding Coverage (Tier 2):  {stats['embedding_coverage']:>6}")
        print(f"Duplicate Detection Rate:     {stats['estimated_duplicate_rate']:>6}")

        # Source Distribution
        print("\n📈 SOURCE DISTRIBUTION")
        print("-" * 80)
        total_incidents = sum(distribution.values())
        for category, count in distribution.items():
            percentage = (count / total_incidents * 100) if total_incidents > 0 else 0
            bar = '█' * int(percentage / 2)
            print(f"{category:15} {count:>4} ({percentage:>5.1f}%) {bar}")

        # Tier Effectiveness (Estimated)
        print("\n🎯 TIER EFFECTIVENESS (Estimated)")
        print("-" * 80)
        print(f"Tier 1 (Hash/Fuzzy):   {tier_stats['tier1_catches']:>4} catches (~60% of duplicates)")
        print(f"Tier 2 (Embeddings):   {tier_stats['tier2_catches']:>4} catches (~30% of duplicates)")
        print(f"Tier 3 (LLM):          {tier_stats['tier3_catches']:>4} catches (~10% of duplicates)")
        print(f"Unique Incidents:      {tier_stats['unique_incidents']:>4} (no duplicates found)")
        print(f"\n💡 {tier_stats['note']}")

        # Recent Merges
        print("\n🔄 RECENT MERGES (Last 24 Hours)")
        print("-" * 80)
        if merges:
            for i, merge in enumerate(merges, 1):
                print(f"{i:2}. {merge['title']}")
                print(f"    Evidence: {merge['evidence_score']}/4 | Sources: {merge['source_count']} | "
                      f"Created: {merge['created_at']}")
        else:
            print("No recent merges detected.")

        print("\n" + "="*80)
        print(f"Dashboard generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")


async def main():
    """Main entry point for dashboard"""
    try:
        dashboard = DuplicateDetectionStats()

        print("Fetching duplicate detection statistics...")

        # Get all stats
        stats = await dashboard.get_overall_stats()
        distribution = await dashboard.get_source_distribution()
        merges = await dashboard.get_recent_merges(hours=24)
        tier_stats = await dashboard.get_tier_effectiveness()

        # Print dashboard
        dashboard.print_dashboard(stats, distribution, merges, tier_stats)

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        print("\nMake sure DATABASE_URL is set and database is accessible.")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
