#!/usr/bin/env python3
"""
Master Ingestion Script for DroneWatch
Orchestrates all scrapers and sends data to API
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

from config import API_BASE_URL, INGEST_TOKEN, IngestTokenError
from db_cache import ScraperCache
from geographic_analyzer import analyze_incident_geography

# Optional AI verification
try:
    from openai_client import OpenAIClient, OpenAIClientError
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logger = logging.getLogger(__name__)
    logger.warning("OpenAI package not available - AI verification disabled")

from scrapers.news_scraper import NewsScraper
from scrapers.police_scraper import PoliceScraper
from scrapers.twitter_scraper import TwitterScraper
from utils import generate_incident_hash, is_recent_incident, format_age, is_drone_incident
from verification import (calculate_confidence_score, get_verification_status,
                          requires_manual_review)
from non_incident_filter import NonIncidentFilter
from satire_domains import is_satire_domain, get_satire_reason

# Scraper version for tracking deployments
SCRAPER_VERSION = "2.3.1"  # Fixed Istanbul Convention bug - added Layer 2A/2B filters

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DroneWatchIngester:
    def __init__(self):
        self.api_url = f"{API_BASE_URL}/ingest"

        # Validate INGEST_TOKEN before attempting any API calls
        try:
            self.token = str(INGEST_TOKEN)
        except IngestTokenError as e:
            logger.error(f"❌ Configuration Error: {e}")
            raise SystemExit(1)

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        })
        self.cache = ScraperCache()
        self.processed_hashes = self.cache.load_sync()
        self.run_id = str(uuid.uuid4())
        self._openai_client = None

        # Filter statistics tracking
        self.stats = {
            'layer_2a_blocked': 0,  # Drone keyword filter
            'layer_2b_blocked': 0,  # Non-incident filter
            'satire_blocked': 0,    # Satire domain
            'geographic_blocked': 0, # Geographic filter
            'ai_blocked': 0,         # AI verification
            'temporal_blocked': 0,   # Temporal validation
            'duplicates_skipped': 0, # Duplicate hash
        }

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
            incident = self._cleanup_incident(incident)

            # Block test incidents
            title_lower = incident['title'].lower()
            if any(test_word in title_lower for test_word in ['dronetest', 'test incident', 'testing drone']):
                logger.warning(f"🚫 Blocking test incident: {incident['title'][:50]}")
                return False

            # === LAYER 2A: Basic Drone Keyword Check ===
            if not is_drone_incident(incident['title'], incident.get('narrative', '')):
                self.stats['layer_2a_blocked'] += 1
                logger.warning(
                    f"🚫 BLOCKED (Not a drone incident): {incident['title'][:60]}",
                    extra={
                        'title': incident['title'],
                        'reason': 'No drone keywords found or excluded category',
                        'layer': 'keyword_filter'
                    }
                )
                return False

            logger.info(f"✓ Drone keyword validation passed: {incident['title'][:50]}")

            # === LAYER 2B: Non-Incident Filter (Policy/Simulation/Discussion) ===
            non_incident_filter = NonIncidentFilter()
            is_non, confidence, reasons = non_incident_filter.is_non_incident(incident)

            if is_non and confidence >= 0.5:
                self.stats['layer_2b_blocked'] += 1
                logger.warning(
                    f"🚫 BLOCKED (Non-Incident Filter): {incident['title'][:60]}",
                    extra={
                        'title': incident['title'],
                        'category': 'policy/simulation/discussion',
                        'confidence': confidence,
                        'reasons': reasons,
                        'layer': 'non_incident_filter'
                    }
                )
                return False

            logger.info(f"✓ Non-incident filter passed: {incident['title'][:50]}")

            # === SATIRE DOMAIN BLOCKING (Layer 1 - Domain Blacklist) ===
            # Check all sources for satire domains
            sources = incident.get('sources', [])
            for source in sources:
                source_url = source.get('source_url', '')
                if is_satire_domain(source_url):
                    self.stats['satire_blocked'] += 1
                    reason_short, reason_detail = get_satire_reason(source_url)
                    logger.warning(f"🚫 BLOCKED (Satire Domain): {incident['title'][:60]}")
                    logger.warning(f"   Reason: {reason_detail}")
                    logger.warning(f"   URL: {source_url}")
                    return False

            # === GEOGRAPHIC VALIDATION (Layer 2 - Python Filter) ===
            # Analyze incident geography with confidence scoring
            geo_analysis = analyze_incident_geography(
                incident['title'],
                incident.get('narrative', ''),
                incident.get('lat'),
                incident.get('lon')
            )

            if not geo_analysis['is_nordic']:
                self.stats['geographic_blocked'] += 1
                logger.warning(f"🚫 BLOCKED (Geographic): {incident['title'][:60]}")
                logger.warning(f"   Reason: {geo_analysis['reason']}")
                logger.warning(f"   Confidence: {geo_analysis['confidence']}")
                logger.warning(f"   Flags: {', '.join(geo_analysis['flags'])}")
                return False

            # Add geographic validation metadata + version tracking
            incident['validation_confidence'] = geo_analysis['confidence']
            incident['validation_flags'] = geo_analysis['flags']
            incident['scraper_version'] = SCRAPER_VERSION
            incident['ingested_at'] = datetime.now(timezone.utc).isoformat()
            logger.info(f"✓ Geographic validation passed: {incident['title'][:50]} (confidence: {geo_analysis['confidence']}, version: {SCRAPER_VERSION})")

            # === AI VERIFICATION (Layer 3 - Intelligent Classification) ===
            # Use AI to verify if this is an actual incident (not policy/defense/discussion)
            if os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"):
                try:
                    ai_verification = self._get_openai_client().verify_incident(
                        incident['title'],
                        incident.get('narrative', ''),
                        incident.get('location_name', '')
                    )

                    if not ai_verification['is_incident']:
                        self.stats['ai_blocked'] += 1
                        logger.warning(f"🚫 BLOCKED (AI Verification): {incident['title'][:60]}")
                        logger.warning(f"   Category: {ai_verification['category']}")
                        logger.warning(f"   Reasoning: {ai_verification['reasoning']}")
                        logger.warning(f"   Confidence: {ai_verification['confidence']}")
                        return False

                    # Add AI verification metadata
                    incident['ai_category'] = ai_verification['category']
                    incident['ai_confidence'] = ai_verification['confidence']
                    incident['ai_reasoning'] = ai_verification['reasoning']
                    logger.info(f"✓ AI verification passed: {ai_verification['category']} (confidence: {ai_verification['confidence']})")

                except Exception as e:  # Catch OpenAIClientError if available, or generic Exception
                    logger.warning(f"AI verification failed, continuing with Python filters: {e}")
                    # Fallback: Continue without AI verification (Python filters already passed)
            else:
                logger.debug("AI verification disabled (no API key configured)")

            # === TEMPORAL VALIDATION (Layer 7 - Age Check) ===
            # Accept incidents from last 60 days (user requirement: "Go 60 days back")
            is_valid, reason = is_recent_incident(
                datetime.fromisoformat(incident['occurred_at']),
                max_age_days=60  # Changed from 365 to 60 days per user request
            )

            if not is_valid:
                self.stats['temporal_blocked'] += 1
                logger.warning(f"🚫 BLOCKED (Temporal): {incident['title'][:60]}")
                logger.warning(f"   Reason: {reason}")
                return False

            # Add age metadata
            incident['incident_age'] = format_age(datetime.fromisoformat(incident['occurred_at']))
            logger.info(f"✓ Temporal validation passed: {incident['incident_age']}")

            # Generate hash for deduplication
            incident_hash = generate_incident_hash(
                incident['title'],
                datetime.fromisoformat(incident['occurred_at']),
                incident['lat'],
                incident['lon']
            )

            # Skip if already processed
            if incident_hash in self.processed_hashes:
                self.stats['duplicates_skipped'] += 1
                logger.info(
                    f"⏭️  Skipping duplicate: {incident['title'][:50]}")
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
                logger.info(
                    f"✓ Auto-verified: {incident['title'][:50]} (confidence: {confidence_score:.2f})")
            else:
                logger.info(
                    f"⚠️  Pending review: {incident['title'][:50]} - {review_reason} (priority: {review_priority})")

            # Send to API
            logger.debug(f"Sending incident to {self.api_url}")
            response = self.session.post(
                self.api_url, json=incident, timeout=15)
            response.raise_for_status()

            # Mark as processed in cache
            self.processed_hashes.add(incident_hash)
            self.cache.add_sync(
                incident_hash,
                incident['title'],
                datetime.fromisoformat(incident['occurred_at']),
                sources[0].get(
                    'source_name', 'unknown') if sources else 'unknown'
            )

            logger.info(f"✅ Ingested: {incident['title'][:50]}")
            logger.debug(
                f"   ID: {response.json().get('id')}, Status: {verification_status}")
            return True

        except requests.exceptions.Timeout:
            logger.error(f"⏱️  API Timeout: {incident['title'][:50]}")
            return False
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"❌ HTTP Error ({e.response.status_code}): {incident['title'][:50]}")
            if hasattr(e.response, 'text'):
                logger.error(f"   Response: {e.response.text[:500]}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API Error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return False

    def _cleanup_incident(self, incident: Dict) -> Dict:
        """Normalize text fields using OpenAI cleanup."""
        try:
            client = self._get_openai_client()
        except ValueError:
            logger.debug("OPENAI_API_KEY not set; skipping OpenAI cleanup")
            return incident

        if not incident.get('narrative'):
            return incident

        try:
            cleaned_narrative = client.cleanup_text(incident['narrative'])
            incident['narrative'] = cleaned_narrative
        except Exception:  # Catch OpenAIClientError if available, or generic Exception
            logger.warning("OpenAI cleanup failed; using original narrative")

        return incident

    def _get_openai_client(self):
        if not HAS_OPENAI:
            return None
        if self._openai_client is None:
            self._openai_client = OpenAIClient()
        return self._openai_client

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

        # 4. Filter out non-incidents (regulatory news, bans, advisories)
        print(f"\n🔍 Filtering non-incidents (regulatory news)...")
        non_incident_filter = NonIncidentFilter()
        actual_incidents, filtered_out = non_incident_filter.filter_incidents(all_incidents)

        if filtered_out:
            print(f"   ❌ Filtered out {len(filtered_out)} non-incidents:")
            for item in filtered_out:
                print(f"      - {item['title'][:60]}... (confidence: {item['_filter_confidence']:.2f})")

        all_incidents = actual_incidents

        # 5. Consolidate incidents (merge multiple sources)
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

        # 6. Sort by evidence score (highest first)
        all_incidents.sort(key=lambda x: x['evidence_score'], reverse=True)

        # 7. Send to API
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
        print(
            f"⏭️  Skipped: {len(all_incidents) - success_count - error_count}")
        print(f"\n🔍 Filter Statistics:")
        print(f"   Layer 2A (Drone Keywords):  {self.stats['layer_2a_blocked']} blocked")
        print(f"   Layer 2B (Non-Incident):    {self.stats['layer_2b_blocked']} blocked")
        print(f"   Satire Domains:             {self.stats['satire_blocked']} blocked")
        print(f"   Geographic Filter:          {self.stats['geographic_blocked']} blocked")
        print(f"   AI Verification:            {self.stats['ai_blocked']} blocked")
        print(f"   Temporal Validation:        {self.stats['temporal_blocked']} blocked")
        print(f"   Duplicate Hashes:           {self.stats['duplicates_skipped']} skipped")
        total_blocked = sum(self.stats.values())
        print(f"   Total Filtered:             {total_blocked} incidents")
        print(f"{'='*60}\n")

        return success_count, error_count


def main():
    import argparse
    parser = argparse.ArgumentParser(description='DroneWatch Ingestion Script')
    parser.add_argument('--test', action='store_true',
                        help='Test mode - show data without sending')
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
