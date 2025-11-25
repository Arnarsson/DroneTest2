#!/usr/bin/env python3
"""
Master Ingestion Script for DroneWatch
Orchestrates all scrapers and sends data to API

Architecture: Clean 4-Layer Pipeline
- Layer 1: Fast rejection (satire, temporal, keyword)
- Layer 2: Content classification (drone incident, non-incident, foreign)
- Layer 3: AI verification (optional, for uncertain cases)
- Layer 4: Database enforcement (PostgreSQL trigger - authoritative)
"""
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Dict, List

import requests

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import API_BASE_URL, INGEST_TOKEN
from db_cache import ScraperCache

# Import clean pipeline
from pipeline import IncidentProcessor, ProcessResult

from scrapers.news_scraper import NewsScraper
from scrapers.police_scraper import PoliceScraper
from scrapers.twitter_scraper import TwitterScraper
from utils import generate_incident_hash, format_age
from verification import (calculate_confidence_score, get_verification_status,
                          requires_manual_review)

# Scraper version for tracking deployments
SCRAPER_VERSION = "3.0.0"  # Clean 4-layer pipeline architecture


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DroneWatchIngester:
    """
    Clean ingestion orchestrator using 4-layer pipeline.

    Layer 1-3: Python validation (IncidentProcessor)
    Layer 4: Database enforcement (PostgreSQL trigger)
    """

    def __init__(self, ai_threshold: float = 0.7, enable_ai: bool = True):
        self.api_url = f"{API_BASE_URL}/ingest"
        self.token = INGEST_TOKEN
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        })
        self.cache = ScraperCache()
        self.processed_hashes = self.cache.load_sync()
        self.run_id = str(uuid.uuid4())

        # Clean pipeline processor
        self.processor = IncidentProcessor(
            ai_threshold=ai_threshold,
            enable_ai=enable_ai
        )

        # Statistics tracking
        self.stats = {
            'layer1_rejected': 0,
            'layer2_rejected': 0,
            'layer3_rejected': 0,
            'duplicates_skipped': 0,
            'api_success': 0,
            'api_errors': 0,
        }

        logger.info(f"Initialized ingester v{SCRAPER_VERSION} (run_id: {self.run_id})")

    def save_processed_hashes(self):
        """DEPRECATED: Now handled by ScraperCache (auto-saves)"""
        pass

    def send_to_api(self, incident: Dict) -> bool:
        """
        Process incident through clean 4-layer pipeline and send to API.

        Layers 1-3: Handled by IncidentProcessor
        Layer 4: Handled by PostgreSQL trigger on insert
        """
        title = incident.get('title', '')[:50]

        try:
            # Block test incidents first
            if any(test in incident.get('title', '').lower()
                   for test in ['dronetest', 'test incident', 'testing drone']):
                logger.warning(f"🚫 Blocking test incident: {title}")
                return False

            # ===== LAYERS 1-3: Pipeline Validation =====
            result = self.processor.process(incident)

            if result.rejected:
                # Update stats based on rejection layer
                if result.layer == 1:
                    self.stats['layer1_rejected'] += 1
                elif result.layer == 2:
                    self.stats['layer2_rejected'] += 1
                elif result.layer == 3:
                    self.stats['layer3_rejected'] += 1

                logger.info(f"🚫 REJECTED [L{result.layer}] {title} - {result.reason}")
                return False

            # ===== DEDUPLICATION: Check local cache =====
            incident_hash = generate_incident_hash(
                incident['title'],
                datetime.fromisoformat(incident['occurred_at']),
                incident['lat'],
                incident['lon']
            )

            if incident_hash in self.processed_hashes:
                self.stats['duplicates_skipped'] += 1
                logger.info(f"⏭️  Skipping duplicate: {title}")
                return False

            # ===== ENRICHMENT: Add metadata =====
            sources = incident.get('sources', [])

            # Calculate verification metrics
            confidence_score = calculate_confidence_score(incident, sources)
            verification_status = get_verification_status(incident, sources)
            needs_review, review_reason, review_priority = requires_manual_review(
                incident, sources, confidence_score
            )

            # Enrich incident with metadata
            incident.update({
                'confidence_score': confidence_score,
                'verification_status': verification_status,
                'requires_review': needs_review,
                'scraper_version': SCRAPER_VERSION,
                'ingested_at': datetime.now(timezone.utc).isoformat(),
                'incident_age': format_age(datetime.fromisoformat(incident['occurred_at'])),
                'pipeline_confidence': result.confidence,
            })

            # Add AI metadata if available
            if result.layer3_result and result.layer3_result.used_ai:
                incident['ai_category'] = result.layer3_result.category
                incident['ai_confidence'] = result.layer3_result.confidence
                incident['ai_reasoning'] = result.layer3_result.reasoning

            # ===== LAYER 4: Send to API (Database trigger validates) =====
            logger.debug(f"Sending to API: {self.api_url}")
            response = self.session.post(self.api_url, json=incident, timeout=15)
            response.raise_for_status()

            # Mark as processed
            self.processed_hashes.add(incident_hash)
            self.cache.add_sync(
                incident_hash,
                incident['title'],
                datetime.fromisoformat(incident['occurred_at']),
                sources[0].get('source_name', 'unknown') if sources else 'unknown'
            )

            self.stats['api_success'] += 1
            logger.info(f"✅ Ingested: {title} (confidence={result.confidence:.2f})")
            return True

        except requests.exceptions.Timeout:
            self.stats['api_errors'] += 1
            logger.error(f"⏱️  API Timeout: {title}")
            return False
        except requests.exceptions.HTTPError as e:
            self.stats['api_errors'] += 1
            logger.error(f"❌ HTTP Error ({e.response.status_code}): {title}")
            if hasattr(e.response, 'text'):
                logger.error(f"   Response: {e.response.text[:300]}")
            return False
        except requests.exceptions.RequestException as e:
            self.stats['api_errors'] += 1
            logger.error(f"❌ API Error: {e}")
            return False
        except Exception as e:
            self.stats['api_errors'] += 1
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return False

    def run_ingestion(self, test_mode: bool = False):
        """Run all scrapers and ingest data"""
        print(f"\n{'='*60}")
        print(f"🚁 DroneWatch Ingestion - {datetime.now().isoformat()}")
        print(f"{'='*60}\n")

        all_incidents = []
        success_count = 0
        error_count = 0

        # 1. Fetch police incidents
        print("\n📮 Fetching Police Incidents...")
        try:
            police_scraper = PoliceScraper()
            police_incidents = police_scraper.fetch_all_police()
            all_incidents.extend(police_incidents)
        except Exception as e:
            print(f"Error in police scraper: {e}")

        # 2. Fetch news incidents
        print("\n📰 Fetching News Incidents...")
        try:
            news_scraper = NewsScraper()
            news_incidents = news_scraper.fetch_all_news()
            all_incidents.extend(news_incidents)
        except Exception as e:
            print(f"Error in news scraper: {e}")

        # 3. Fetch Twitter incidents (Danish police accounts)
        print("\n🐦 Fetching Twitter Incidents...")
        try:
            twitter_scraper = TwitterScraper()
            twitter_incidents = twitter_scraper.fetch_all()
            print(f"   Found {len(twitter_incidents)} incidents from Twitter")
            all_incidents.extend(twitter_incidents)
        except Exception as e:
            print(f"Error in Twitter scraper: {e}")

        # 4. Consolidate incidents (merge multiple sources)
        # NOTE: Non-incident filtering happens in send_to_api() as Layer 2B
        # Removed redundant pre-filtering that was running twice
        print(f"\n🔄 Consolidating incidents (merging multiple sources)...")
        from consolidator import ConsolidationEngine

        consolidation_engine = ConsolidationEngine(
            location_precision=0.01,  # ~1km (rounds to 0.01° ≈ 1.1km at Nordic latitudes)
            time_window_hours=6       # Groups incidents within 6-hour windows
        )

        # Get statistics before consolidation
        stats = consolidation_engine.get_consolidation_stats(all_incidents)
        print(f"   Before consolidation: {stats['total_incidents']} incidents")
        print(f"   Unique locations: {stats['unique_hashes']}")
        print(f"   Multi-source groups: {stats['multi_source_groups']}")
        if stats['potential_merges'] > 0:
            print(f"   Potential merges: {stats['potential_merges']} incidents → {stats['multi_source_groups']} consolidated")
            print(f"   Merge rate: {stats['merge_rate']:.1f}%")

        # Consolidate
        all_incidents = consolidation_engine.consolidate_incidents(all_incidents)
        print(f"   After consolidation: {len(all_incidents)} incidents")

        # 5. Sort by evidence score (highest first)
        all_incidents.sort(key=lambda x: x['evidence_score'], reverse=True)

        # 6. Send to API
        print(f"\n📤 Sending {len(all_incidents)} incidents to API...")

        if test_mode and all_incidents:
            print("\n🧪 TEST MODE - Showing first incident only:")
            print(json.dumps(all_incidents[0], indent=2, ensure_ascii=False))
            return

        for incident in all_incidents:
            if self.send_to_api(incident):
                success_count += 1
            else:
                error_count += 1

        # 7. Save processed hashes
        self.save_processed_hashes()

        # 8. Summary
        print(f"\n{'='*60}")
        print(f"📊 Ingestion Summary (v{SCRAPER_VERSION})")
        print(f"{'='*60}")
        print(f"✅ Success: {success_count}")
        print(f"❌ Errors: {error_count}")
        print(f"⏭️  Skipped: {len(all_incidents) - success_count - error_count}")

        # Pipeline statistics
        pipeline_stats = self.processor.get_stats()
        print(f"\n🔍 Pipeline Statistics:")
        print(f"   Layer 1 (Fast Reject):   {self.stats['layer1_rejected']} blocked")
        print(f"   Layer 2 (Classification): {self.stats['layer2_rejected']} blocked")
        print(f"   Layer 3 (AI Verify):      {self.stats['layer3_rejected']} blocked")
        print(f"   Duplicates:               {self.stats['duplicates_skipped']} skipped")
        print(f"   API Success:              {self.stats['api_success']}")
        print(f"   API Errors:               {self.stats['api_errors']}")

        total_rejected = (self.stats['layer1_rejected'] +
                         self.stats['layer2_rejected'] +
                         self.stats['layer3_rejected'])
        print(f"\n   Total Rejected:           {total_rejected} incidents")
        print(f"   AI Usage Rate:            {pipeline_stats['ai_usage_rate']:.1%}")
        print(f"{'='*60}\n")

        return success_count, error_count


def should_run_ingestion(api_base_url: str) -> bool:
    """
    Smart Scheduling Logic:
    1. If top of the hour (minute < 5), always run.
    2. If recent incident (< 1 hour ago), run (Active Mode).
    3. Otherwise, skip to save resources.
    """
    try:
        now = datetime.now(timezone.utc)
        
        # Method 1: Top of the hour check (0-5 min)
        # We allow a 5-minute window because cron might delay slightly
        if now.minute < 5:
            print(f"⏰ Hourly schedule check ({now.strftime('%H:%M')}): RUNNING")
            return True

        # Method 2: Active Mode check
        print("🔍 Checking for active incidents...")
        api_url = f"{api_base_url}/incidents?limit=1"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            incidents = response.json()
            if incidents and len(incidents) > 0:
                # Parse occurred_at safely handling Z or offset
                occurred_str = incidents[0]['occurred_at'].replace('Z', '+00:00')
                latest_time = datetime.fromisoformat(occurred_str)
                
                # Ensure aware comparison (if API returns naive, assume UTC)
                if latest_time.tzinfo is None:
                    latest_time = latest_time.replace(tzinfo=timezone.utc)
                
                # Calculate time difference
                diff = now - latest_time
                hours_diff = diff.total_seconds() / 3600
                
                if hours_diff < 1.0:
                    print(f"🚨 Active Incident detected ({hours_diff:.1f}h ago): RUNNING (High Frequency Mode)")
                    return True
                else:
                    print(f"💤 No recent activity ({hours_diff:.1f}h ago). Skipping off-hour run.")
                    return False
            else:
                print("ℹ️ No incidents found in DB. Skipping off-hour run.")
                return False
        else:
            print(f"⚠️ API Error ({response.status_code}) checking status. Defaulting to RUN.")
            return True
            
    except Exception as e:
        print(f"⚠️ Error checking active status: {e}. Defaulting to RUN.")
        return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description='DroneWatch Ingestion Script')
    parser.add_argument('--test', action='store_true',
                        help='Test mode - show data without sending')
    parser.add_argument('--api-url', help='Override API URL', default=None)
    parser.add_argument('--smart-schedule', action='store_true',
                        help='Enable smart scheduling (hourly default, 5min if active)')
    args = parser.parse_args()

    # Override API URL if provided
    if args.api_url:
        import config
        config.API_BASE_URL = args.api_url

    # Check schedule if enabled
    if args.smart_schedule and not args.test:
        if not should_run_ingestion(API_BASE_URL):
            return

    # Run ingestion
    ingester = DroneWatchIngester()
    ingester.run_ingestion(test_mode=args.test)


if __name__ == "__main__":
    main()
