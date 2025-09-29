"""
News RSS Aggregator
Fetches drone incidents from Danish news sources
"""
import feedparser
import requests
from datetime import datetime, timezone
from typing import List, Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SOURCES
from utils import (
    extract_location, extract_datetime, extract_quote,
    is_drone_incident, clean_html
)

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DroneWatch/1.0 (https://dronewatch.cc)'
        })

    def fetch_news_rss(self, source_key: str) -> List[Dict]:
        """
        Fetch and parse news RSS feed
        """
        source = SOURCES.get(source_key)
        if not source or 'rss' not in source:
            return []

        incidents = []

        try:
            feed = feedparser.parse(source['rss'])

            for entry in feed.entries[:50]:  # Check more entries for news
                title = entry.get('title', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                link = entry.get('link', '')

                # Check if drone-related
                if not any(keyword in (title + summary).lower()
                          for keyword in source.get('keywords', [])):
                    continue

                # Verify it's an incident, not general news
                if not is_drone_incident(title, summary):
                    continue

                # Extract details
                lat, lon, asset_type = extract_location(title + " " + summary)

                # Extract datetime
                published = entry.get('published_parsed')
                if published:
                    occurred_at = datetime(*published[:6], tzinfo=timezone.utc)
                else:
                    occurred_at = extract_datetime(summary)

                # Check for official quotes
                has_official = any(word in summary.lower() for word in [
                    "politi", "police", "myndighed", "authority",
                    "minister", "forsvar", "defense"
                ])

                # Extract quote
                quote = extract_quote(summary)

                # Calculate evidence score
                evidence_score = 3 if has_official else 2

                # Build incident
                incident = {
                    "title": title,
                    "narrative": clean_html(summary[:500]),
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
                print(f"Found news incident: {title}")

        except Exception as e:
            print(f"Error fetching {source_key}: {e}")

        return incidents

    def fetch_all_news(self) -> List[Dict]:
        """
        Fetch from all configured news sources
        """
        all_incidents = []

        news_sources = [k for k, v in SOURCES.items() if v.get('type') == 'media']

        for source_key in news_sources:
            print(f"Checking {source_key}...")
            incidents = self.fetch_news_rss(source_key)
            all_incidents.extend(incidents)

        print(f"Found {len(all_incidents)} total news incidents")
        return all_incidents

if __name__ == "__main__":
    scraper = NewsScraper()
    incidents = scraper.fetch_all_news()

    for incident in incidents:
        print(f"\n📰 {incident['title']}")
        print(f"   Evidence: {incident['evidence_score']}/4")
        print(f"   Source: {incident['sources'][0]['source_name']}")