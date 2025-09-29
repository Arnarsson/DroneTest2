#!/usr/bin/env python3
"""
Master Ingestion Script for DroneWatch
Orchestrates all scrapers and sends data to API
"""
import os
import sys
import json
import requests
from datetime import datetime
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import API_BASE_URL, INGEST_TOKEN
from scrapers.police_scraper import PoliceScraper
from scrapers.news_scraper import NewsScraper
from utils import generate_incident_hash

class DroneWatchIngester:
    def __init__(self):
        self.api_url = f"{API_BASE_URL}/ingest"
        self.token = INGEST_TOKEN
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        })
        self.processed_hashes = self.load_processed_hashes()

    def load_processed_hashes(self) -> set:
        """Load previously processed incident hashes to avoid duplicates"""
        cache_file = 'processed_incidents.json'
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def save_processed_hashes(self):
        """Save processed incident hashes"""
        cache_file = 'processed_incidents.json'
        # Keep only last 1000 hashes
        recent_hashes = list(self.processed_hashes)[-1000:]
        with open(cache_file, 'w') as f:
            json.dump(recent_hashes, f)

    def send_to_api(self, incident: Dict) -> bool:
        """Send incident to API"""
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
                print(f"⏭️  Skipping duplicate: {incident['title'][:50]}")
                return False

            # Send to API
            response = self.session.post(self.api_url, json=incident, timeout=10)
            response.raise_for_status()

            # Mark as processed
            self.processed_hashes.add(incident_hash)

            print(f"✅ Ingested: {incident['title'][:50]}")
            print(f"   ID: {response.json().get('id')}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
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