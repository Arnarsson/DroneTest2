#!/usr/bin/env python3
"""
Ingestion Pipeline Monitoring
Real-time metrics and health checks for the DroneWatch ingestion system
"""
import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IngestionMonitor:
    def __init__(self):
        """Initialize database connection"""
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to database"""
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL environment variable not set")

            # Use port 5432 for direct connection
            database_url = database_url.replace(':6543/', ':5432/')

            self.conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            logger.info("Connected to database")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def get_total_incidents(self) -> int:
        """Get total number of incidents in database"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM public.incidents")
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting total incidents: {e}")
            return 0

    def get_incidents_by_version(self) -> List[Dict]:
        """
        Get incident count grouped by scraper version

        Returns:
            List of {version, count} dictionaries
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        COALESCE(scraper_version, 'unknown') as version,
                        COUNT(*) as count
                    FROM public.incidents
                    GROUP BY scraper_version
                    ORDER BY count DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting incidents by version: {e}")
            return []

    def get_incidents_last_hour(self) -> int:
        """Get number of incidents ingested in last hour"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM public.incidents
                    WHERE ingested_at > NOW() - INTERVAL '1 hour'
                """)
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting incidents last hour: {e}")
            return 0

    def get_incidents_last_24h(self) -> int:
        """Get number of incidents ingested in last 24 hours"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM public.incidents
                    WHERE ingested_at > NOW() - INTERVAL '24 hours'
                """)
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting incidents last 24h: {e}")
            return 0

    def get_average_confidence(self) -> float:
        """Get average validation confidence for recent incidents"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT AVG(validation_confidence) as avg_confidence
                    FROM public.incidents
                    WHERE ingested_at > NOW() - INTERVAL '24 hours'
                    AND validation_confidence IS NOT NULL
                """)
                result = cursor.fetchone()
                return float(result['avg_confidence']) if result and result['avg_confidence'] else 0.0
        except Exception as e:
            logger.error(f"Error getting average confidence: {e}")
            return 0.0

    def get_confidence_distribution(self) -> List[Dict]:
        """Get distribution of validation confidence scores"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        CASE
                            WHEN validation_confidence >= 0.9 THEN '0.9-1.0 (High)'
                            WHEN validation_confidence >= 0.7 THEN '0.7-0.9 (Medium-High)'
                            WHEN validation_confidence >= 0.5 THEN '0.5-0.7 (Medium)'
                            ELSE '<0.5 (Low)'
                        END as confidence_range,
                        COUNT(*) as count
                    FROM public.incidents
                    WHERE validation_confidence IS NOT NULL
                    GROUP BY confidence_range
                    ORDER BY MIN(validation_confidence) DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting confidence distribution: {e}")
            return []

    def check_trigger_status(self) -> bool:
        """Check if geographic validation trigger is enabled"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT tgname, tgenabled
                    FROM pg_trigger
                    WHERE tgrelid = 'public.incidents'::regclass
                    AND tgname = 'validate_incident_before_insert'
                """)
                result = cursor.fetchone()
                return result and result['tgenabled'] == 'O'  # 'O' = enabled
        except Exception as e:
            logger.error(f"Error checking trigger status: {e}")
            return False

    def get_recent_incidents(self, limit: int = 10) -> List[Dict]:
        """Get most recently ingested incidents"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        title,
                        scraper_version,
                        validation_confidence,
                        ingested_at,
                        ST_Y(location::geometry) as lat,
                        ST_X(location::geometry) as lon
                    FROM public.incidents
                    ORDER BY ingested_at DESC
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting recent incidents: {e}")
            return []

    def get_health_status(self) -> Dict:
        """
        Get overall system health status

        Returns:
            Dictionary with health metrics and status
        """
        metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_incidents': self.get_total_incidents(),
            'incidents_last_hour': self.get_incidents_last_hour(),
            'incidents_last_24h': self.get_incidents_last_24h(),
            'average_confidence': round(self.get_average_confidence(), 2),
            'trigger_enabled': self.check_trigger_status(),
            'version_distribution': self.get_incidents_by_version(),
            'confidence_distribution': self.get_confidence_distribution()
        }

        # Determine health status
        status = 'healthy'
        warnings = []

        # Check if trigger is disabled
        if not metrics['trigger_enabled']:
            status = 'critical'
            warnings.append('Geographic validation trigger is DISABLED!')

        # Check ingestion rate
        if metrics['incidents_last_hour'] == 0 and metrics['incidents_last_24h'] == 0:
            status = 'warning'
            warnings.append('No incidents ingested in last 24 hours')

        # Check confidence scores
        if metrics['average_confidence'] < 0.7:
            if status != 'critical':
                status = 'warning'
            warnings.append(f'Low average confidence: {metrics["average_confidence"]}')

        metrics['status'] = status
        metrics['warnings'] = warnings

        return metrics

    def print_dashboard(self):
        """Print monitoring dashboard to console"""
        print("=" * 80)
        print("DRONEWATCH INGESTION PIPELINE MONITORING")
        print("=" * 80)

        health = self.get_health_status()

        # Status banner
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '🚨'
        }
        print(f"\nStatus: {status_emoji.get(health['status'], '❓')} {health['status'].upper()}")

        if health['warnings']:
            print("\nWarnings:")
            for warning in health['warnings']:
                print(f"  ⚠️  {warning}")

        # Metrics
        print(f"\nTotal Incidents: {health['total_incidents']}")
        print(f"Last Hour: {health['incidents_last_hour']}")
        print(f"Last 24h: {health['incidents_last_24h']}")
        print(f"Average Confidence: {health['average_confidence']}")
        print(f"Trigger Enabled: {'✓' if health['trigger_enabled'] else '✗ DISABLED'}")

        # Version distribution
        print("\nScraper Versions:")
        for item in health['version_distribution']:
            print(f"  {item['version']}: {item['count']} incidents")

        # Confidence distribution
        print("\nConfidence Distribution:")
        for item in health['confidence_distribution']:
            print(f"  {item['confidence_range']}: {item['count']} incidents")

        # Recent incidents
        print("\nRecent Incidents (last 10):")
        recent = self.get_recent_incidents(10)
        for incident in recent:
            confidence = incident.get('validation_confidence')
            conf_str = f"{confidence:.2f}" if confidence else "N/A"
            version = incident.get('scraper_version', 'unknown')
            print(f"  [{conf_str}] {incident['title'][:60]} (v{version})")

        print("\n" + "=" * 80)
        print(f"Generated: {health['timestamp']}")
        print("=" * 80)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Main entry point"""
    monitor = None
    try:
        monitor = IngestionMonitor()
        monitor.print_dashboard()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Monitoring failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if monitor:
            monitor.close()


if __name__ == "__main__":
    main()
