"""
Twitter/X RSS Scraper - Danish Police Accounts
Fetches drone-related incidents from police Twitter accounts via RSS.app feeds
"""
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import List, Dict, Optional
import sys
import os
import time
import logging
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TWITTER_POLICE_SOURCES
from utils import (
    extract_location, extract_datetime, extract_quote,
    is_drone_incident, is_nordic_incident, clean_html, calculate_evidence_score
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TwitterScraper:
    """
    Scraper for Danish police Twitter accounts via RSS.app feeds

    Features:
    - RSS feed parsing from RSS.app
    - Twitter-specific content extraction
    - Keyword filtering (drone, dron, uav)
    - Multi-language support (Danish, English)
    - Source attribution with trust_weight: 4 (police)
    - Rate limiting and error handling
    """

    def __init__(self, max_retries=3, backoff_factor=2):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'da,en-US;q=0.7,en;q=0.3',
            'Connection': 'keep-alive'
        })
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def _retry_request(self, method, url, **kwargs):
        """
        Execute HTTP request with exponential backoff retry logic
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = method(url, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    sleep_time = self.backoff_factor ** attempt
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")

        raise last_exception

    def _clean_tweet_text(self, text: str) -> str:
        """
        Clean Twitter text: Remove HTML, normalize whitespace, preserve hashtags
        """
        # Remove HTML tags but preserve text
        text = clean_html(text)

        # Normalize whitespace
        text = ' '.join(text.split())

        # Remove Twitter widgets script references
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)

        return text.strip()

    def _extract_tweet_content(self, entry: Dict) -> Optional[Dict]:
        """
        Extract structured content from RSS feed entry

        Returns:
            {
                'title': str,
                'content': str,
                'link': str,
                'published_at': datetime,
                'creator': str (Twitter handle)
            }
        """
        try:
            title = entry.get('title', '')
            description = entry.get('description', '')
            link = entry.get('link', '')
            published = entry.get('published', '')
            creator = entry.get('dc:creator', entry.get('author', 'Unknown'))

            # Clean HTML from description to get pure text
            content = self._clean_tweet_text(description)

            # Parse published date
            try:
                pub_date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %Z')
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            except:
                pub_date = datetime.now(timezone.utc)

            return {
                'title': self._clean_tweet_text(title),
                'content': content,
                'link': link,
                'published_at': pub_date,
                'creator': creator
            }
        except Exception as e:
            logger.error(f"Error extracting tweet content: {e}")
            return None

    def fetch_twitter_rss(self, source_key: str) -> List[Dict]:
        """
        Fetch and parse Twitter RSS feed from RSS.app

        Args:
            source_key: Key in TWITTER_POLICE_SOURCES config

        Returns:
            List of incident dictionaries
        """
        source = TWITTER_POLICE_SOURCES.get(source_key)
        if not source or not source.get('enabled', False):
            logger.info(f"Source {source_key} is disabled or not found")
            return []

        if 'rss' not in source or 'PLACEHOLDER' in source['rss']:
            logger.warning(f"No RSS feed URL configured for {source_key}")
            return []

        incidents = []

        try:
            logger.info(f"Fetching Twitter RSS feed from {source['name']}")

            # Fetch and parse RSS feed
            feed = feedparser.parse(source['rss'])

            if not feed.entries:
                logger.info(f"No entries found in RSS feed for {source_key}")
                return []

            logger.info(f"Processing {len(feed.entries)} tweets from {source_key}")

            for entry in feed.entries:
                try:
                    # Extract tweet content
                    tweet = self._extract_tweet_content(entry)
                    if not tweet:
                        continue

                    # Check if drone-related
                    if not is_drone_incident(tweet['title'], tweet['content']):
                        continue

                    # CRITICAL: Filter out police drones (NOT incidents)
                    # Police using drones for surveillance/security is NOT an incident
                    police_drone_keywords = [
                        'politiet har',  # "Police have..."
                        'politiets droner',  # "Police's drones"
                        'vores droner',  # "Our drones"
                        'drone i luften',  # "Drone in the air" (police operational)
                        'ifm. eu-topmøde',  # "regarding EU summit"
                        'som en del af indsatsen',  # "As part of the operation"
                        'efter planen',  # "According to plan"
                        'ingen grund til at være urolig'  # "No reason to be worried"
                    ]

                    content_lower = (tweet['title'] + ' ' + tweet['content']).lower()
                    if any(keyword in content_lower for keyword in police_drone_keywords):
                        logger.info(f"Skipping police drone operation (not incident): {tweet['title'][:80]}...")
                        continue

                    logger.info(f"Found drone INCIDENT tweet: {tweet['title'][:80]}...")

                    # Extract location FIRST (needed for Nordic check)
                    # extract_location returns (lat, lon, asset_type) tuple
                    lat, lon, asset_type = extract_location(tweet['title'] + ' ' + tweet['content'])

                    # Default to Copenhagen for Copenhagen Police tweets if no location found
                    if lat is None and source['region'] == 'Copenhagen':
                        lat, lon, asset_type = 55.6761, 12.5683, 'other'
                        logger.info(f"Using Copenhagen default location for tweet")

                    if lat is None:
                        logger.warning(f"Could not extract location, skipping: {tweet['title'][:80]}")
                        continue

                    # Check if Nordic incident (geographic scope + text validation)
                    if not is_nordic_incident(tweet['title'], tweet['content'], lat, lon):
                        logger.info(f"Skipping non-Nordic incident: {tweet['title'][:80]}...")
                        continue

                    # Build location dict for incident
                    location = {
                        'name': source['region'],  # Use region name from config
                        'lat': lat,
                        'lon': lon,
                        'asset_type': asset_type or 'other'
                    }

                    # Extract occurrence datetime (use tweet publish date as fallback)
                    occurred_at = extract_datetime(tweet['title'] + ' ' + tweet['content'])
                    if not occurred_at:
                        occurred_at = tweet['published_at']

                    # Extract quote (first sentence of tweet)
                    quote = extract_quote(tweet['content'])

                    # Build incident
                    incident = {
                        'title': tweet['title'][:200],  # Limit title length
                        'narrative': tweet['content'][:1000],  # Limit narrative length
                        'occurred_at': occurred_at.isoformat(),
                        'first_seen_at': tweet['published_at'].isoformat(),
                        'location': location,
                        'lat': lat,  # Top-level for ingest.py compatibility
                        'lon': lon,  # Top-level for ingest.py compatibility
                        'asset_type': location.get('asset_type', 'other'),
                        'status': 'active',
                        'verification_status': 'auto_verified',  # Police source
                        'evidence_score': 4,  # Police = automatic score 4
                        'country': 'DK',  # All Twitter sources are Danish
                        'sources': [{
                            'source_url': tweet['link'],
                            'source_type': source['source_type'],
                            'source_name': source['name'],
                            'source_quote': quote,
                            'published_at': tweet['published_at'].isoformat(),
                            'trust_weight': source['trust_weight'],  # 4 for police
                            'metadata': {
                                'twitter_handle': source['handle'],
                                'region': source['region'],
                                'creator': tweet['creator']
                            }
                        }],
                        'metadata': {
                            'scraper': 'twitter_scraper',
                            'scraper_version': '2.2.0',
                            'source_key': source_key,
                            'twitter_handle': source['handle'],
                            'hashtags': source.get('hashtags', [])
                        }
                    }

                    incidents.append(incident)

                except Exception as e:
                    logger.error(f"Error processing tweet: {e}")
                    continue

            logger.info(f"Extracted {len(incidents)} drone incidents from {source['name']}")
            return incidents

        except Exception as e:
            logger.error(f"Error fetching Twitter RSS feed for {source_key}: {e}")
            return []

    def fetch_all(self) -> List[Dict]:
        """
        Fetch from all enabled Twitter sources

        Returns:
            Combined list of incidents from all sources
        """
        all_incidents = []

        enabled_sources = {k: v for k, v in TWITTER_POLICE_SOURCES.items() if v.get('enabled', False)}
        logger.info(f"Fetching from {len(enabled_sources)} enabled Twitter sources")

        for source_key in enabled_sources:
            try:
                incidents = self.fetch_twitter_rss(source_key)
                all_incidents.extend(incidents)

                # Rate limiting: small delay between sources
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error processing source {source_key}: {e}")
                continue

        logger.info(f"Total incidents from Twitter: {len(all_incidents)}")
        return all_incidents


if __name__ == "__main__":
    """
    Test Twitter scraper independently
    """
    print("🐦 Twitter Scraper Test\n")

    scraper = TwitterScraper()

    # Test single source (Copenhagen Police)
    print("Testing Copenhagen Police (@KobenhavnPoliti)...")
    incidents = scraper.fetch_twitter_rss('twitter_kobenhavns_politi')

    print(f"\nFound {len(incidents)} drone incidents\n")

    for i, incident in enumerate(incidents, 1):
        print(f"{i}. {incident['title']}")
        print(f"   Location: {incident['location'].get('name', 'Unknown')}")
        print(f"   Occurred: {incident['occurred_at']}")
        print(f"   Evidence: {incident['evidence_score']} (Police)")
        print(f"   Source: {incident['sources'][0]['source_url']}")
        print()
