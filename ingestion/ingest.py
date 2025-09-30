#!/usr/bin/env python3
"""
Master Ingestion Script for DroneWatch
Orchestrates all scrapers and sends data to API
"""
import os
import sys
import json
import requests
import logging
from datetime import datetime
from typing import List, Dict
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import API_BASE_URL, INGEST_TOKEN
from scrapers.police_scraper import PoliceScraper
from scrapers.news_scraper import NewsScraper
from utils import generate_incident_hash
from db_cache import ScraperCache
from verification import (
    calculate_confidence_score,
    get_verification_status,
    requires_manual_review
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DroneWatchIngester:
    def __init__(self):
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
        logger.info(f"Initialized ingester (run_id: {self.run_id})")

    def load_processed_hashes(self) -> set:
        """DEPRECATED: Now handled by ScraperCache"""
        return self.processed_hashes

    def save_processed_hashes(self):
        """DEPRECATED: Now handled by ScraperCache (auto-saves)"""
        pass

    def send_to_api(self, incident: Dict) -> bool:
        """Send incident to API with verification and improved error handling"""
        try:
            # Generate hash for deduplication
            incident_hash = generate_incident_hash(
                incident['title'],
                datetime.fromisoformat(incident['occurred_at']),
                incident['lat'],
                incident['lon']
            )

            # Skip if already processed
            if incident_hash in self.processed_hashes:
                logger.info(f"⏭️  Skipping duplicate: {incident['title'][:50]}")
                return False

            # === VERIFICATION LOGIC ===
            sources = incident.get('sources', [])
            source_dict = {'trust_weight': sources[0].get('trust_weight', 1),
                          'type': sources[0].get('source_type', 'unknown'),
                          'name': sources[0].get('source_name', 'unknown')} if sources else {}

            # Calculate confidence score
            confidence_score = calculate_confidence_score(incident, sources)
            incident['confidence_score'] = confidence_score

            # Determine verification status
            verification_status = get_verification_status(incident, sources)
            incident['verification_status'] = verification_status

            # Check if requires manual review
            needs_review, review_reason, review_priority = requires_manual_review(
                incident, sources, confidence_score
            )
            incident['requires_review'] = needs_review

            # Log verification decision
            if verification_status == 'auto_verified':
                logger.info(f"✓ Auto-verified: {incident['title'][:50]} (confidence: {confidence_score:.2f})")
            else:
                logger.info(f"⚠️  Pending review: {incident['title'][:50]} - {review_reason} (priority: {review_priority})")

            # Send to API
            logger.debug(f"Sending incident to {self.api_url}")
            response = self.session.post(self.api_url, json=incident, timeout=15)
            response.raise_for_status()

            # Mark as processed in cache
            self.processed_hashes.add(incident_hash)
            self.cache.add_sync(
                incident_hash,
                incident['title'],
                datetime.fromisoformat(incident['occurred_at']),
                sources[0].get('source_name', 'unknown') if sources else 'unknown'
            )

            logger.info(f"✅ Ingested: {incident['title'][:50]}")
            logger.debug(f"   ID: {response.json().get('id')}, Status: {verification_status}")
            return True

        except requests.exceptions.Timeout:
            logger.error(f"⏱️  API Timeout: {incident['title'][:50]}")
            return False
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error ({e.response.status_code}): {incident['title'][:50]}")
            if hasattr(e.response, 'text'):
                logger.debug(f"   Response: {e.response.text[:200]}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API Error: {e}")
            return False
        except Exception as e:
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

        # 3. Sort by evidence score (highest first)
        all_incidents.sort(key=lambda x: x['evidence_score'], reverse=True)

        # 4. Send to API
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

        # 5. Save processed hashes
        self.save_processed_hashes()

        # 6. Summary
        print(f"\n{'='*60}")
        print(f"📊 Ingestion Summary")
        print(f"{'='*60}")
        print(f"✅ Success: {success_count}")
        print(f"❌ Errors: {error_count}")
        print(f"⏭️  Skipped: {len(all_incidents) - success_count - error_count}")
        print(f"{'='*60}\n")

        return success_count, error_count

def main():
    import argparse
    parser = argparse.ArgumentParser(description='DroneWatch Ingestion Script')
    parser.add_argument('--test', action='store_true', help='Test mode - show data without sending')
    parser.add_argument('--api-url', help='Override API URL', default=None)
    args = parser.parse_args()

    # Override API URL if provided
    if args.api_url:
        import config
        config.API_BASE_URL = args.api_url

    # Run ingestion
    ingester = DroneWatchIngester()
    ingester.run_ingestion(test_mode=args.test)

if __name__ == "__main__":
    main()