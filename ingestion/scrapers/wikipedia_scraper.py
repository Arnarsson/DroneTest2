#!/usr/bin/env python3
"""
Wikipedia Historical Incident Scraper
Extracts drone incidents from Wikipedia articles for historical data enrichment.
"""

import requests
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WikipediaIncidentScraper:
    """Scrapes drone incidents from Wikipedia articles"""

    WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"

    # Wikipedia articles with drone incident data
    ARTICLE_TITLES = [
        "2025 Danish drone incidents",
        "List of drone incidents",
        "Unmanned aerial vehicle",
    ]

    # Additional search terms for finding incidents
    SEARCH_TERMS = [
        "drone incident airport 2024",
        "drone incident airport 2025",
        "military base drone sighting",
        "UAV intrusion Europe",
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DroneWatch/1.0 (https://dronemap.cc; research@dronemap.cc) Educational/Research'
        })

    def get_article_content(self, title: str) -> Optional[str]:
        """Fetch Wikipedia article content via API"""
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'revisions',
            'rvprop': 'content',
            'rvslots': 'main',
        }

        try:
            response = self.session.get(self.WIKIPEDIA_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if page_id == '-1':  # Article doesn't exist
                    logger.warning(f"Article '{title}' not found")
                    return None

                revisions = page_data.get('revisions', [])
                if revisions:
                    content = revisions[0].get('slots', {}).get('main', {}).get('*', '')
                    return content

            return None

        except Exception as e:
            logger.error(f"Error fetching article '{title}': {e}")
            return None

    def parse_coordinates(self, text: str) -> Optional[Tuple[float, float]]:
        """Extract coordinates from Wikipedia text"""
        # Match patterns like: {{coord|55|37|N|12|39|E}}
        coord_pattern = r'\{\{coord\|(\d+)\|(\d+)\|([NS])\|(\d+)\|(\d+)\|([EW])'
        match = re.search(coord_pattern, text)

        if match:
            lat_deg, lat_min, lat_dir = float(match.group(1)), float(match.group(2)), match.group(3)
            lon_deg, lon_min, lon_dir = float(match.group(4)), float(match.group(5)), match.group(6)

            lat = lat_deg + (lat_min / 60)
            if lat_dir == 'S':
                lat = -lat

            lon = lon_deg + (lon_min / 60)
            if lon_dir == 'W':
                lon = -lon

            return (lat, lon)

        # Try decimal format: 55.618, 12.647
        decimal_pattern = r'(\d+\.\d+)[°\s]*([NS])?[,\s]+(\d+\.\d+)[°\s]*([EW])?'
        match = re.search(decimal_pattern, text)
        if match:
            lat = float(match.group(1))
            lon = float(match.group(3))

            if match.group(2) == 'S':
                lat = -lat
            if match.group(4) == 'W':
                lon = -lon

            return (lat, lon)

        return None

    def parse_date(self, text: str) -> Optional[datetime]:
        """Extract date from Wikipedia text"""
        # Try ISO format first
        iso_pattern = r'(\d{4})-(\d{2})-(\d{2})'
        match = re.search(iso_pattern, text)
        if match:
            try:
                return datetime.strptime(match.group(0), '%Y-%m-%d')
            except ValueError:
                pass

        # Try written format: "22 September 2025"
        written_pattern = r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})'
        match = re.search(written_pattern, text)
        if match:
            try:
                date_str = f"{match.group(1)} {match.group(2)} {match.group(3)}"
                return datetime.strptime(date_str, '%d %B %Y')
            except ValueError:
                pass

        return None

    def get_article_html(self, title: str) -> Optional[str]:
        """Fetch rendered HTML of Wikipedia article"""
        params = {
            'action': 'parse',
            'format': 'json',
            'page': title,
            'prop': 'text',
        }

        try:
            response = self.session.get(self.WIKIPEDIA_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'error' in data:
                logger.warning(f"Article '{title}' error: {data['error'].get('info')}")
                return None

            html = data.get('parse', {}).get('text', {}).get('*', '')
            return html

        except Exception as e:
            logger.error(f"Error fetching HTML for '{title}': {e}")
            return None

    def extract_incidents_from_article(self, title: str, content: str) -> List[Dict]:
        """Parse incidents from Wikipedia article content"""
        incidents = []

        # Try HTML parsing first (more reliable for structured data)
        html = self.get_article_html(title)
        if html:
            soup = BeautifulSoup(html, 'html.parser')

            # Extract incidents from tables
            tables = soup.find_all('table', class_='wikitable')
            for table in tables:
                incidents.extend(self.parse_incidents_from_table(table, title))

            # Extract incidents from lists
            lists = soup.find_all(['ul', 'ol'])
            for lst in lists:
                items = lst.find_all('li', recursive=False)
                for item in items:
                    incident = self.parse_incident_from_html_item(item, title)
                    if incident:
                        incidents.append(incident)

        # Fallback to wikitext parsing
        if not incidents:
            sections = re.split(r'==\s*(.+?)\s*==', content)

            for i, section in enumerate(sections):
                if any(keyword in section.lower() for keyword in ['incident', 'event', 'timeline', 'chronology']):
                    items = re.findall(r'\*\s*(.+?)(?=\n\*|\n==|\Z)', section, re.DOTALL)

                    for item in items:
                        incident = self.parse_incident_item(item, title)
                        if incident:
                            incidents.append(incident)

        return incidents

    def parse_incidents_from_table(self, table, source_article: str) -> List[Dict]:
        """Extract incidents from Wikipedia table"""
        incidents = []
        rows = table.find_all('tr')

        # Skip header row
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue

            # Extract text from cells
            cell_texts = [cell.get_text(strip=True) for cell in cells]

            # Try to find date, location, description
            incident_data = {
                'date': None,
                'location': None,
                'description': None,
            }

            for text in cell_texts:
                if not incident_data['date']:
                    incident_data['date'] = self.parse_date(text)

                if not incident_data['location'] and len(text) > 3 and len(text) < 100:
                    incident_data['location'] = text

                if len(text) > 50:
                    incident_data['description'] = text

            if incident_data['date'] and incident_data['description']:
                incident = {
                    'title': incident_data['location'] or f"Incident on {incident_data['date'].strftime('%Y-%m-%d')}",
                    'narrative': incident_data['description'][:500],
                    'occurred_at': incident_data['date'],
                    'lat': None,
                    'lon': None,
                    'source_url': f"https://en.wikipedia.org/wiki/{source_article.replace(' ', '_')}",
                    'source_type': 'wikipedia',
                    'source_name': 'Wikipedia',
                    'evidence_score': 2,
                    'asset_type': self.infer_asset_type(incident_data['description']),
                    'country': self.infer_country(incident_data['description'] + ' ' + (incident_data['location'] or ''), None),
                }
                incidents.append(incident)

        return incidents

    def parse_incident_from_html_item(self, item, source_article: str) -> Optional[Dict]:
        """Parse incident from HTML list item"""
        text = item.get_text(strip=True)

        if len(text) < 50:  # Too short to be useful
            return None

        date = self.parse_date(text)
        if not date:
            return None

        # Extract links for location
        links = item.find_all('a')
        location_name = None
        for link in links:
            link_text = link.get_text(strip=True)
            if len(link_text) > 3 and 'airport' in link_text.lower() or 'base' in link_text.lower():
                location_name = link_text
                break

        return {
            'title': location_name or f"Incident on {date.strftime('%Y-%m-%d')}",
            'narrative': text[:500],
            'occurred_at': date,
            'lat': None,
            'lon': None,
            'source_url': f"https://en.wikipedia.org/wiki/{source_article.replace(' ', '_')}",
            'source_type': 'wikipedia',
            'source_name': 'Wikipedia',
            'evidence_score': 2,
            'asset_type': self.infer_asset_type(text),
            'country': self.infer_country(text, None),
        }

    def parse_incident_item(self, text: str, source_article: str) -> Optional[Dict]:
        """Parse a single incident from Wikipedia text"""
        # Extract date
        date = self.parse_date(text)
        if not date:
            return None

        # Extract coordinates
        coords = self.parse_coordinates(text)

        # Extract location name (often in bold or quotes)
        location_pattern = r"'''(.+?)'''|\"(.+?)\""
        location_match = re.search(location_pattern, text)
        location_name = None
        if location_match:
            location_name = location_match.group(1) or location_match.group(2)

        # Clean up text (remove wiki markup)
        clean_text = re.sub(r'\[\[(.+?)\|(.+?)\]\]', r'\2', text)  # [[link|text]] -> text
        clean_text = re.sub(r'\[\[(.+?)\]\]', r'\1', clean_text)  # [[link]] -> link
        clean_text = re.sub(r"'''(.+?)'''", r'\1', clean_text)  # bold
        clean_text = re.sub(r"''(.+?)''", r'\1', clean_text)  # italic
        clean_text = re.sub(r'<ref>.+?</ref>', '', clean_text)  # remove references
        clean_text = re.sub(r'\{\{.+?\}\}', '', clean_text)  # remove templates
        clean_text = clean_text.strip()

        # Only return if we have minimum required data
        if not clean_text or len(clean_text) < 50:
            return None

        return {
            'title': location_name or f"Incident on {date.strftime('%Y-%m-%d')}",
            'narrative': clean_text[:500],  # Limit narrative length
            'occurred_at': date,
            'lat': coords[0] if coords else None,
            'lon': coords[1] if coords else None,
            'source_url': f"https://en.wikipedia.org/wiki/{source_article.replace(' ', '_')}",
            'source_type': 'wikipedia',
            'source_name': 'Wikipedia',
            'evidence_score': 2,  # Wikipedia gets score 2 (single credible source)
            'asset_type': self.infer_asset_type(clean_text),
            'country': self.infer_country(clean_text, coords),
        }

    def infer_asset_type(self, text: str) -> str:
        """Infer asset type from incident text"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['airport', 'airfield', 'runway', 'aviation']):
            return 'airport'
        elif any(word in text_lower for word in ['military', 'base', 'airbase', 'naval', 'army']):
            return 'military'
        elif any(word in text_lower for word in ['harbor', 'harbour', 'port', 'maritime']):
            return 'harbor'
        elif any(word in text_lower for word in ['power', 'nuclear', 'energy', 'grid']):
            return 'powerplant'
        elif any(word in text_lower for word in ['bridge']):
            return 'bridge'
        else:
            return 'other'

    def infer_country(self, text: str, coords: Optional[Tuple[float, float]]) -> Optional[str]:
        """Infer country code from text or coordinates"""
        # Text-based country detection
        country_map = {
            'denmark': 'DK', 'danish': 'DK', 'copenhagen': 'DK',
            'norway': 'NO', 'norwegian': 'NO', 'oslo': 'NO',
            'sweden': 'SE', 'swedish': 'SE', 'stockholm': 'SE',
            'finland': 'FI', 'finnish': 'FI', 'helsinki': 'FI',
            'germany': 'DE', 'german': 'DE', 'berlin': 'DE', 'munich': 'DE',
            'france': 'FR', 'french': 'FR', 'paris': 'FR',
            'uk': 'GB', 'britain': 'GB', 'england': 'GB', 'london': 'GB',
            'netherlands': 'NL', 'dutch': 'NL', 'amsterdam': 'NL',
            'belgium': 'BE', 'belgian': 'BE', 'brussels': 'BE',
            'poland': 'PL', 'polish': 'PL', 'warsaw': 'PL',
            'spain': 'ES', 'spanish': 'ES', 'madrid': 'ES',
            'italy': 'IT', 'italian': 'IT', 'rome': 'IT',
            'latvia': 'LV', 'latvian': 'LV', 'riga': 'LV',
            'estonia': 'EE', 'estonian': 'EE', 'tallinn': 'EE',
        }

        text_lower = text.lower()
        for keyword, code in country_map.items():
            if keyword in text_lower:
                return code

        # TODO: Coordinate-based reverse geocoding for more accuracy

        return None

    def scrape_all_articles(self) -> List[Dict]:
        """Scrape all Wikipedia articles and return incidents"""
        all_incidents = []

        for title in self.ARTICLE_TITLES:
            logger.info(f"Fetching article: {title}")
            content = self.get_article_content(title)

            if content:
                incidents = self.extract_incidents_from_article(title, content)
                logger.info(f"Found {len(incidents)} incidents in '{title}'")
                all_incidents.extend(incidents)
            else:
                logger.warning(f"Could not fetch content for '{title}'")

        logger.info(f"Total incidents found: {len(all_incidents)}")
        return all_incidents


def main():
    """Test Wikipedia scraper"""
    scraper = WikipediaIncidentScraper()

    # Test with single article
    print("\n=== Testing Wikipedia Article Scraping ===\n")

    content = scraper.get_article_content("2025 Danish drone incidents")
    if content:
        print(f"Fetched article content: {len(content)} characters")
        print(f"First 200 chars: {content[:200]}...")

        incidents = scraper.extract_incidents_from_article("2025 Danish drone incidents", content)
        print(f"\nFound {len(incidents)} incidents")

        for i, incident in enumerate(incidents[:3], 1):
            print(f"\n--- Incident {i} ---")
            print(f"Title: {incident['title']}")
            print(f"Date: {incident['occurred_at']}")
            print(f"Location: {incident['lat']}, {incident['lon']}")
            print(f"Country: {incident['country']}")
            print(f"Asset: {incident['asset_type']}")
            print(f"Narrative: {incident['narrative'][:150]}...")
    else:
        print("Could not fetch article content")

    # Scrape all articles
    print("\n\n=== Scraping All Articles ===\n")
    all_incidents = scraper.scrape_all_articles()

    print(f"\nTotal incidents scraped: {len(all_incidents)}")
    print(f"Countries: {set(i['country'] for i in all_incidents if i['country'])}")
    print(f"Asset types: {set(i['asset_type'] for i in all_incidents)}")


if __name__ == '__main__':
    main()
