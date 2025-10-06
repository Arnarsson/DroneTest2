#!/usr/bin/env python3
"""
Automated Foreign Incident Cleanup Job
Scans database hourly and removes foreign incidents that slipped through

Run via cron:
0 * * * * cd /path/to/ingestion && python3 cleanup_foreign_incidents.py

This is Layer 3 of the multi-layer defense system.
"""
import logging
import os
import sys
from datetime import datetime, timezone
from typing import List, Dict

import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from geographic_analyzer import analyze_incident_geography

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Alert threshold - if more than this many foreign incidents found, send alert
ALERT_THRESHOLD = 5


class ForeignIncidentCleaner:
    def __init__(self):
        """Initialize database connection"""
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to database"""
        try:
            # Read connection string from environment
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL environment variable not set")

            # Parse and modify connection string for direct connection (port 5432)
            database_url = database_url.replace(':6543/', ':5432/')

            self.conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            logger.info("Connected to database")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def find_suspicious_incidents(self) -> List[Dict]:
        """
        Find incidents that match foreign location patterns

        Returns:
            List of suspicious incident records
        """
        suspicious_keywords = [
            'ukraina', 'ukraine', 'russisk', 'russian', 'kiev', 'kyiv',
            'tysk', 'germany', 'berlin', 'münchen', 'munich',
            'polsk', 'poland', 'warsaw', 'warszawa',
            'fransk', 'france', 'paris',
            'britannisk', 'britain', 'london'
        ]

        # Build ILIKE conditions for all keywords
        ilike_conditions = ' OR '.join([f"title ILIKE '%{kw}%'" for kw in suspicious_keywords])

        query = f"""
            SELECT
                id,
                title,
                narrative,
                ST_Y(location::geometry) as lat,
                ST_X(location::geometry) as lon,
                occurred_at,
                scraper_version,
                validation_confidence
            FROM public.incidents
            WHERE
                ({ilike_conditions})
                AND (ST_Y(location::geometry) BETWEEN 54 AND 71)
                AND (ST_X(location::geometry) BETWEEN 4 AND 31)
            ORDER BY occurred_at DESC
        """

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error finding suspicious incidents: {e}")
            return []

    def analyze_and_cleanup(self, incident: Dict) -> bool:
        """
        Re-validate incident with enhanced filter and delete if foreign

        Args:
            incident: Incident record from database

        Returns:
            True if incident was deleted, False otherwise
        """
        try:
            # Re-validate with enhanced analyzer
            analysis = analyze_incident_geography(
                incident['title'],
                incident.get('narrative', ''),
                incident['lat'],
                incident['lon']
            )

            if not analysis['is_nordic']:
                # Delete foreign incident
                logger.warning(f"🗑️  REMOVING FOREIGN INCIDENT:")
                logger.warning(f"   ID: {incident['id']}")
                logger.warning(f"   Title: {incident['title'][:80]}")
                logger.warning(f"   Reason: {analysis['reason']}")
                logger.warning(f"   Confidence: {analysis['confidence']}")
                logger.warning(f"   Flags: {', '.join(analysis['flags'])}")
                logger.warning(f"   Scraper Version: {incident.get('scraper_version', 'unknown')}")

                with self.conn.cursor() as cursor:
                    cursor.execute("DELETE FROM public.incidents WHERE id = %s", (incident['id'],))
                    self.conn.commit()

                return True
            else:
                logger.debug(f"✓ Valid incident: {incident['title'][:60]} (confidence: {analysis['confidence']})")
                return False

        except Exception as e:
            logger.error(f"Error analyzing incident {incident['id']}: {e}")
            self.conn.rollback()
            return False

    def run_cleanup(self) -> Dict[str, int]:
        """
        Run full cleanup scan and removal

        Returns:
            Dictionary with cleanup statistics
        """
        logger.info("=" * 80)
        logger.info("STARTING FOREIGN INCIDENT CLEANUP")
        logger.info(f"Time: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 80)

        # Find suspicious incidents
        suspicious = self.find_suspicious_incidents()
        logger.info(f"Found {len(suspicious)} suspicious incidents to analyze")

        if not suspicious:
            logger.info("✓ No suspicious incidents found - database is clean")
            return {'scanned': 0, 'removed': 0, 'kept': 0}

        # Analyze and cleanup
        removed_count = 0
        kept_count = 0

        for incident in suspicious:
            was_deleted = self.analyze_and_cleanup(incident)
            if was_deleted:
                removed_count += 1
            else:
                kept_count += 1

        # Log results
        logger.info("=" * 80)
        logger.info("CLEANUP COMPLETE")
        logger.info(f"Scanned: {len(suspicious)} incidents")
        logger.info(f"Removed: {removed_count} foreign incidents")
        logger.info(f"Kept: {kept_count} valid incidents")
        logger.info("=" * 80)

        # Alert if too many foreign incidents found
        if removed_count >= ALERT_THRESHOLD:
            logger.error(f"⚠️  ALERT: {removed_count} foreign incidents found!")
            logger.error(f"⚠️  This suggests scraper may be running old code")
            logger.error(f"⚠️  Check deployment and scraper versions")
            self.send_alert(removed_count)

        return {
            'scanned': len(suspicious),
            'removed': removed_count,
            'kept': kept_count,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def send_alert(self, count: int):
        """
        Send alert about high number of foreign incidents

        Args:
            count: Number of foreign incidents removed
        """
        # TODO: Implement alerting (email, Slack, etc.)
        logger.warning(f"⚠️  ALERT: {count} foreign incidents removed - scraper may be broken!")
        logger.warning("   Consider:")
        logger.warning("   1. Check if latest scraper code is deployed")
        logger.warning("   2. Verify database trigger is active")
        logger.warning("   3. Review scraper logs for errors")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


def main():
    """Main entry point"""
    cleaner = None
    try:
        cleaner = ForeignIncidentCleaner()
        stats = cleaner.run_cleanup()

        # Log to cleanup log
        logger.info(f"Cleanup stats: {stats}")

        # Exit code 0 for success, 1 if removed incidents
        exit_code = 0 if stats['removed'] == 0 else 1
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        sys.exit(2)
    finally:
        if cleaner:
            cleaner.close()


if __name__ == "__main__":
    main()
