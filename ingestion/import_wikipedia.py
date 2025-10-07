#!/usr/bin/env python3
"""
Import Wikipedia Historical Incidents
Integrates Wikipedia scraper with main ingestion pipeline.
"""

import sys
import os
import asyncio
import asyncpg
from datetime import datetime
import logging
from typing import List, Dict
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scrapers.wikipedia_scraper import WikipediaIncidentScraper
from config import DANISH_AIRPORTS, DANISH_HARBORS

# Trust weights for sources
TRUST_WEIGHTS = {
    'wikipedia': 0.6,
    'police': 1.0,
    'aviation': 0.9,
    'media': 0.7
}

# European locations for matching (combining Danish data + known Nordic/EU locations)
MONITORED_LOCATIONS = []

# Add Danish airports
for name, data in DANISH_AIRPORTS.items():
    MONITORED_LOCATIONS.append({
        'name': name,
        'lat': data['lat'],
        'lon': data['lon'],
        'country': 'DK',
        'type': 'airport',
        'aliases': [name]
    })

# Add Danish harbors
for name, data in DANISH_HARBORS.items():
    MONITORED_LOCATIONS.append({
        'name': name,
        'lat': data['lat'],
        'lon': data['lon'],
        'country': 'DK',
        'type': 'harbor',
        'aliases': [name]
    })

# Add known Nordic/European locations from existing incidents
MONITORED_LOCATIONS.extend([
    # Norway
    {'name': 'Oslo Airport', 'lat': 60.1939, 'lon': 11.1004, 'country': 'NO', 'type': 'airport', 'aliases': ['gardermoen', 'oslo']},
    # Sweden
    {'name': 'Stockholm Arlanda', 'lat': 59.6519, 'lon': 17.9186, 'country': 'SE', 'type': 'airport', 'aliases': ['arlanda', 'stockholm']},
    # Netherlands
    {'name': 'Amsterdam Schiphol', 'lat': 52.3105, 'lon': 4.7683, 'country': 'NL', 'type': 'airport', 'aliases': ['schiphol', 'amsterdam']},
    # Poland
    {'name': 'Lublin Airport', 'lat': 51.2403, 'lon': 22.7136, 'country': 'PL', 'type': 'airport', 'aliases': ['lublin']},
    # Denmark military
    {'name': 'Karup Air Base', 'lat': 56.2975, 'lon': 9.1247, 'country': 'DK', 'type': 'military', 'aliases': ['karup']},
    {'name': 'Skrydstrup Air Base', 'lat': 55.2214, 'lon': 9.2631, 'country': 'DK', 'type': 'military', 'aliases': ['skrydstrup']},
    {'name': 'Kastrup Airbase', 'lat': 55.63, 'lon': 12.65, 'country': 'DK', 'type': 'military', 'aliases': ['kastrup base']},
])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WikipediaImporter:
    """Import historical incidents from Wikipedia into database"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.scraper = WikipediaIncidentScraper()

    def match_location(self, incident: Dict) -> Dict:
        """Match incident to known location from database"""
        narrative = incident.get('narrative', '').lower()
        title = incident.get('title', '').lower()
        country = incident.get('country')

        # Search for location match
        for location in MONITORED_LOCATIONS:
            loc_name = location['name'].lower()

            # Skip if country mismatch
            if country and location.get('country') != country:
                continue

            # Check if location name appears in text
            if loc_name in narrative or loc_name in title:
                logger.info(f"Matched '{incident['title']}' to {location['name']}")
                return {
                    **incident,
                    'lat': location['lat'],
                    'lon': location['lon'],
                    'country': location.get('country', incident['country']),
                    'asset_type': location.get('type', incident['asset_type']),
                }

            # Check aliases
            for alias in location.get('aliases', []):
                if alias.lower() in narrative or alias.lower() in title:
                    logger.info(f"Matched '{incident['title']}' to {location['name']} (alias: {alias})")
                    return {
                        **incident,
                        'lat': location['lat'],
                        'lon': location['lon'],
                        'country': location.get('country', incident['country']),
                        'asset_type': location.get('type', incident['asset_type']),
                    }

        return incident

    async def import_incident(self, conn, incident: Dict) -> bool:
        """Import single incident into database"""
        # Skip if missing required data
        if not incident.get('occurred_at'):
            logger.warning(f"Skipping incident without date: {incident.get('title')}")
            return False

        if not incident.get('country'):
            logger.warning(f"Skipping incident without country: {incident.get('title')}")
            return False

        # Generate UUIDs
        incident_id = str(uuid.uuid4())
        source_id = str(uuid.uuid4())

        try:
            # Insert incident
            await conn.execute("""
                INSERT INTO incidents (
                    id, title, narrative, occurred_at, first_seen_at, last_seen_at,
                    asset_type, status, evidence_score, country, location, verification_status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                          ST_SetSRID(ST_MakePoint($11, $12), 4326)::geography, $13)
                ON CONFLICT (id) DO NOTHING
            """,
                incident_id,
                incident['title'],
                incident.get('narrative', ''),
                incident['occurred_at'],
                datetime.now(),  # first_seen_at
                datetime.now(),  # last_seen_at
                incident.get('asset_type', 'other'),
                'resolved',  # Historical incidents are resolved
                incident.get('evidence_score', 2),  # Wikipedia = score 2
                incident['country'],
                incident.get('lon'),  # PostGIS: lon first
                incident.get('lat'),  # PostGIS: lat second
                'auto_verified'  # Wikipedia incidents auto-verified
            )

            # Insert source reference
            await conn.execute("""
                INSERT INTO incident_sources (
                    id, incident_id, source_url, source_type, source_name,
                    source_title, source_quote, published_at, trust_weight
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO NOTHING
            """,
                source_id,
                incident_id,
                incident.get('source_url', ''),
                'wikipedia',
                'Wikipedia',
                incident['title'],
                incident.get('narrative', '')[:500],  # First 500 chars as quote
                incident['occurred_at'],
                TRUST_WEIGHTS.get('wikipedia', 0.6)
            )

            logger.info(f"✅ Imported: {incident['title']} ({incident['country']})")
            return True

        except Exception as e:
            logger.error(f"Error importing incident '{incident['title']}': {e}")
            return False

    async def import_all(self, dry_run: bool = False):
        """Import all Wikipedia incidents"""
        # Scrape Wikipedia
        logger.info("Scraping Wikipedia articles...")
        raw_incidents = self.scraper.scrape_all_articles()
        logger.info(f"Found {len(raw_incidents)} raw incidents")

        # Match locations
        logger.info("Matching incidents to known locations...")
        matched_incidents = []
        for incident in raw_incidents:
            matched = self.match_location(incident)
            if matched.get('lat') and matched.get('lon'):  # Only keep geocoded
                matched_incidents.append(matched)

        logger.info(f"Matched {len(matched_incidents)} incidents with coordinates")

        # Filter to unique countries/dates
        logger.info(f"\nCountries: {set(i['country'] for i in matched_incidents if i.get('country'))}")
        logger.info(f"Date range: {min(i['occurred_at'] for i in matched_incidents if i.get('occurred_at'))} to {max(i['occurred_at'] for i in matched_incidents if i.get('occurred_at'))}")

        if dry_run:
            logger.info("\n🔍 DRY RUN - No database changes")
            for i, incident in enumerate(matched_incidents[:10], 1):
                logger.info(f"\n{i}. {incident['title']}")
                logger.info(f"   Date: {incident['occurred_at']}")
                logger.info(f"   Location: {incident.get('lat')}, {incident.get('lon')}")
                logger.info(f"   Country: {incident.get('country')}")
                logger.info(f"   Narrative: {incident.get('narrative', '')[:100]}...")
            return

        # Import to database
        logger.info(f"\nImporting {len(matched_incidents)} incidents to database...")
        conn = await asyncpg.connect(self.database_url)

        try:
            imported = 0
            for incident in matched_incidents:
                success = await self.import_incident(conn, incident)
                if success:
                    imported += 1

            logger.info(f"\n✅ Successfully imported {imported}/{len(matched_incidents)} incidents")

        finally:
            await conn.close()


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Import Wikipedia historical drone incidents')
    parser.add_argument('--dry-run', action='store_true', help='Preview without importing')
    parser.add_argument('--database-url', help='PostgreSQL connection string')
    args = parser.parse_args()

    # Get database URL (not required for dry run)
    database_url = args.database_url or os.getenv('DATABASE_URL')
    if not database_url and not args.dry_run:
        logger.error("DATABASE_URL not set (required for actual import)")
        sys.exit(1)
    elif not database_url:
        database_url = "postgresql://dummy:dummy@localhost/dummy"  # Placeholder for dry run

    # Convert pooler URL to direct connection (port 6543 → 5432)
    if ':6543' in database_url:
        database_url = database_url.replace(':6543', ':5432')
        logger.info("Using direct connection (port 5432) for imports")

    importer = WikipediaImporter(database_url)
    await importer.import_all(dry_run=args.dry_run)


if __name__ == '__main__':
    asyncio.run(main())
