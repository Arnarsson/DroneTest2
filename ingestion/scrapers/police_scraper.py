"""
Danish Police RSS/Website Scraper
Fetches drone-related incidents from police news feeds
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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SOURCES
from utils import (
    extract_location, extract_datetime, extract_quote,
    is_drone_incident, clean_html, calculate_evidence_score
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PoliceScraper:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DroneWatch/1.0 (https://dronewatch.cc)'
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

    def fetch_police_rss(self, source_key: str) -> List[Dict]:
        """
        Fetch and parse police RSS feed with retry logic
        """
        source = SOURCES.get(source_key)
        if not source or 'rss' not in source:
            logger.warning(f"Invalid source configuration for {source_key}")
            return []

        incidents = []

        try:
            # Parse RSS feed with timeout
            logger.info(f"Fetching RSS feed from {source['name']}")
            feed = feedparser.parse(source['rss'])

            if not feed.entries:
                logger.info(f"No entries found in RSS feed for {source_key}")
                return []

            logger.debug(f"Processing {len(feed.entries)} entries from {source_key}")

            for entry in feed.entries[:20]:  # Check last 20 entries
                try:
                    # Check if drone-related
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    link = entry.get('link', '')

                    if not title or not summary:
                        logger.debug(f"Skipping entry with missing title or summary")
                        continue

                    if not is_drone_incident(title, summary):
                        continue

                    # Extract full article if possible
                    full_content = self.fetch_article_content(link) if link else summary

                    # Extract location
                    lat, lon, asset_type = extract_location(title + " " + full_content)

                    # Extract datetime
                    published = entry.get('published_parsed')
                    if published:
                        occurred_at = datetime(*published[:6], tzinfo=timezone.utc)
                    else:
                        occurred_at = extract_datetime(full_content)

                    # Extract quote
                    quote = extract_quote(full_content)

                    # Build incident
                    incident = {
                        "title": title,
                        "narrative": clean_html(summary[:500]),
                        "occurred_at": occurred_at.isoformat(),
                        "lat": lat,
                        "lon": lon,
                        "asset_type": asset_type,
                        "status": "active",
                        "evidence_score": 4,  # Police = official
                        "country": "DK",
                        "sources": [{
                            "source_url": link,
                            "source_type": "police",
                            "source_name": source['name'],
                            "source_quote": quote,
                            "trust_weight": 4
                        }]
                    }

                    incidents.append(incident)
                    logger.info(f"✓ Found police incident: {title[:60]}")

                except Exception as e:
                    logger.error(f"Error processing entry from {source_key}: {e}", exc_info=True)
                    continue

        except Exception as e:
            logger.error(f"Error fetching RSS feed from {source_key}: {e}", exc_info=True)

        return incidents

    def fetch_article_content(self, url: str) -> str:
        """
        Fetch full article content from police website with retry logic
        """
        try:
            logger.debug(f"Fetching article content from: {url}")
            response = self._retry_request(self.session.get, url, timeout=10)

            soup = BeautifulSoup(response.content, 'html.parser')

            # Police.dk article structure
            article = soup.find('article') or soup.find('div', class_='content')
            if article:
                # Remove script and style elements
                for element in article(['script', 'style']):
                    element.decompose()
                content = article.get_text(separator=' ', strip=True)
                logger.debug(f"Successfully extracted {len(content)} characters from article")
                return content

            logger.debug(f"No article content found at {url}")
            return ""
        except Exception as e:
            logger.warning(f"Error fetching article {url}: {e}")
            return ""

    def fetch_all_police(self) -> List[Dict]:
        """
        Fetch from all configured police sources with error isolation
        """
        all_incidents = []
        successful_sources = 0
        failed_sources = []

        police_sources = [k for k, v in SOURCES.items() if v.get('type') == 'police']

        logger.info(f"Checking {len(police_sources)} police sources...")

        for source_key in police_sources:
            try:
                incidents = self.fetch_police_rss(source_key)
                all_incidents.extend(incidents)
                successful_sources += 1
                if incidents:
                    logger.info(f"✓ {source_key}: Found {len(incidents)} incident(s)")
            except Exception as e:
                failed_sources.append(source_key)
                logger.error(f"✗ {source_key}: Failed to fetch - {e}", exc_info=True)
                # Continue processing other sources
                continue

        logger.info(f"Police scraper summary: {len(all_incidents)} incidents from {successful_sources}/{len(police_sources)} sources")
        if failed_sources:
            logger.warning(f"Failed sources: {', '.join(failed_sources)}")

        return all_incidents

if __name__ == "__main__":
    scraper = PoliceScraper()
    incidents = scraper.fetch_all_police()

    for incident in incidents:
        print(f"\n📍 {incident['title']}")
        print(f"   Location: {incident['lat']}, {incident['lon']} ({incident['asset_type']})")
        print(f"   Time: {incident['occurred_at']}")
        print(f"   Source: {incident['sources'][0]['source_url']}")
        if incident['sources'][0]['source_quote']:
            print(f"   Quote: {incident['sources'][0]['source_quote'][:100]}...")