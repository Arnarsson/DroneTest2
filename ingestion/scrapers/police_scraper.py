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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SOURCES
from utils import (
    extract_location, extract_datetime, extract_quote,
    is_drone_incident, clean_html, calculate_evidence_score
)

class PoliceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DroneWatch/1.0 (https://dronewatch.cc)'
        })

    def fetch_police_rss(self, source_key: str) -> List[Dict]:
        """
        Fetch and parse police RSS feed
        """
        source = SOURCES.get(source_key)
        if not source or 'rss' not in source:
            return []

        incidents = []

        try:
            # Parse RSS feed
            feed = feedparser.parse(source['rss'])

            for entry in feed.entries[:20]:  # Check last 20 entries
                # Check if drone-related
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                link = entry.get('link', '')

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
                print(f"Found police incident: {title}")

        except Exception as e:
            print(f"Error fetching {source_key}: {e}")

        return incidents

    def fetch_article_content(self, url: str) -> str:
        """
        Fetch full article content from police website
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Police.dk article structure
            article = soup.find('article') or soup.find('div', class_='content')
            if article:
                # Remove script and style elements
                for element in article(['script', 'style']):
                    element.decompose()
                return article.get_text()

            return ""
        except Exception as e:
            print(f"Error fetching article {url}: {e}")
            return ""

    def fetch_all_police(self) -> List[Dict]:
        """
        Fetch from all configured police sources
        """
        all_incidents = []

        police_sources = [k for k, v in SOURCES.items() if v.get('type') == 'police']

        for source_key in police_sources:
            print(f"Checking {source_key}...")
            incidents = self.fetch_police_rss(source_key)
            all_incidents.extend(incidents)

        print(f"Found {len(all_incidents)} total police incidents")
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