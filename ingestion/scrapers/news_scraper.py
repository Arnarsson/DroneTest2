"""
News RSS Aggregator
Fetches drone incidents from Danish news sources
"""
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import List, Dict
import sys
import os
import time
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SOURCES
from utils import (
    extract_location, extract_datetime, extract_quote,
    is_drone_incident, is_nordic_incident, clean_html
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsScraper:
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

    def fetch_article_content(self, url: str) -> str:
        """
        Fetch full article content from news website with retry logic
        """
        try:
            logger.debug(f"Fetching article content from: {url}")
            response = self._retry_request(self.session.get, url, timeout=10)

            soup = BeautifulSoup(response.content, 'html.parser')

            # Try common article structures
            article = (soup.find('article') or
                      soup.find('div', class_='article-body') or
                      soup.find('div', class_='content') or
                      soup.find('div', class_='article-content'))

            if article:
                # Remove script, style, and navigation elements
                for element in article(['script', 'style', 'nav', 'aside']):
                    element.decompose()
                content = article.get_text(separator=' ', strip=True)
                logger.debug(f"Successfully extracted {len(content)} characters from article")
                return content

            logger.debug(f"No article content found at {url}")
            return ""
        except Exception as e:
            logger.warning(f"Error fetching article {url}: {e}")
            return ""

    def fetch_news_rss(self, source_key: str) -> List[Dict]:
        """
        Fetch and parse news RSS feed with improved content extraction
        """
        source = SOURCES.get(source_key)
        if not source or 'rss' not in source:
            logger.warning(f"Invalid source configuration for {source_key}")
            return []

        incidents = []

        try:
            logger.info(f"Fetching RSS feed from {source['name']}")
            feed = feedparser.parse(source['rss'])

            if not feed.entries:
                logger.info(f"No entries found in RSS feed for {source_key}")
                return []

            logger.debug(f"Processing {len(feed.entries)} entries from {source_key}")

            for entry in feed.entries[:50]:  # Check more entries for news
                try:
                    title = entry.get('title', '')
                    summary = entry.get('summary', '') or entry.get('description', '')
                    link = entry.get('link', '')

                    if not title or not summary:
                        logger.debug(f"Skipping entry with missing title or summary")
                        continue

                    # Check if drone-related
                    if not any(keyword in (title + summary).lower()
                              for keyword in source.get('keywords', [])):
                        continue

                    # Verify it's an incident, not general news
                    if not is_drone_incident(title, summary):
                        continue

                    # Fetch full article content
                    full_content = self.fetch_article_content(link) if link else summary
                    content_to_analyze = full_content if full_content else summary

                    # Extract details
                    lat, lon, asset_type = extract_location(title + " " + content_to_analyze)

                    # Skip incidents without valid location
                    if lat is None or lon is None:
                        logger.info(f"⏭️  Skipping (no location): {title[:60]}...")
                        continue

                    # Geographic scope filter: Only ingest Nordic incidents
                    if not is_nordic_incident(title, content_to_analyze, lat, lon):
                        logger.info(f"⏭️  Skipping (non-Nordic): {title[:60]}...")
                        continue

                    # Extract datetime
                    published = entry.get('published_parsed')
                    if published:
                        occurred_at = datetime(*published[:6], tzinfo=timezone.utc)
                    else:
                        occurred_at = extract_datetime(content_to_analyze)

                    # Check for official quotes
                    has_official = any(word in content_to_analyze.lower() for word in [
                        "politi", "police", "myndighed", "authority",
                        "minister", "forsvar", "defense"
                    ])

                    # Extract quote
                    quote = extract_quote(content_to_analyze)

                    # Calculate evidence score based on source trust_weight
                    trust_weight = source.get('trust_weight', 2)

                    # Evidence scoring rules:
                    # 4: Official sources (trust_weight=4)
                    # 3: Credible source (trust_weight=3) with official quote
                    # 2: Credible source (trust_weight>=2) without quote
                    # 1: Low trust source (trust_weight=1)
                    if trust_weight == 4:
                        evidence_score = 4
                    elif trust_weight == 3 and has_official:
                        evidence_score = 3
                    elif trust_weight >= 2:
                        evidence_score = 2
                    else:
                        evidence_score = 1

                    # Build incident
                    incident = {
                        "title": title,
                        "narrative": clean_html(content_to_analyze[:500]),
                        "occurred_at": occurred_at.isoformat(),
                        "lat": lat,
                        "lon": lon,
                        "asset_type": asset_type,
                        "status": "active",
                        "evidence_score": evidence_score,
                        "country": "DK",
                        "sources": [{
                            "source_url": link,
                            "source_type": "media",
                            "source_name": source['name'],
                            "source_quote": quote,
                            "trust_weight": source.get('trust_weight', 2)
                        }]
                    }

                    incidents.append(incident)
                    logger.info(f"✓ Found news incident: {title[:60]}")

                except Exception as e:
                    logger.error(f"Error processing entry from {source_key}: {e}", exc_info=True)
                    continue

        except Exception as e:
            logger.error(f"Error fetching RSS feed from {source_key}: {e}", exc_info=True)

        return incidents

    def fetch_all_news(self) -> List[Dict]:
        """
        Fetch from all configured news sources with error isolation
        """
        all_incidents = []
        successful_sources = 0
        failed_sources = []

        news_sources = [k for k, v in SOURCES.items() if v.get('type') == 'media']

        logger.info(f"Checking {len(news_sources)} news sources...")

        for source_key in news_sources:
            try:
                incidents = self.fetch_news_rss(source_key)
                all_incidents.extend(incidents)
                successful_sources += 1
                if incidents:
                    logger.info(f"✓ {source_key}: Found {len(incidents)} incident(s)")
            except Exception as e:
                failed_sources.append(source_key)
                logger.error(f"✗ {source_key}: Failed to fetch - {e}", exc_info=True)
                # Continue processing other sources
                continue

        logger.info(f"News scraper summary: {len(all_incidents)} incidents from {successful_sources}/{len(news_sources)} sources")
        if failed_sources:
            logger.warning(f"Failed sources: {', '.join(failed_sources)}")

        return all_incidents

if __name__ == "__main__":
    scraper = NewsScraper()
    incidents = scraper.fetch_all_news()

    for incident in incidents:
        print(f"\n📰 {incident['title']}")
        print(f"   Evidence: {incident['evidence_score']}/4")
        print(f"   Source: {incident['sources'][0]['source_name']}")