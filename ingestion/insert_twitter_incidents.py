#!/usr/bin/env python3
"""
Direct database insertion of Twitter incidents
Bypasses the API to avoid timeout issues
"""
import psycopg2
from datetime import datetime, timezone
from scrapers.twitter_scraper import TwitterScraper
import hashlib
import json

# Database connection
DATABASE_URL = "postgresql://postgres.uhwsuaebakkdmdogzrrz:stUPw5co47Yq8uSI@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

def generate_hash(title, occurred_at, lat, lon):
    """Generate content hash for deduplication"""
    # Round to 6-hour window
    rounded_hour = occurred_at.replace(minute=0, second=0, microsecond=0)
    rounded_hour = rounded_hour.replace(hour=(rounded_hour.hour // 6) * 6)

    # Round coordinates to ~1km
    lat_rounded = round(lat, 2)
    lon_rounded = round(lon, 2)

    hash_input = f"{lat_rounded:.2f},{lon_rounded:.2f},{rounded_hour.isoformat()}"
    return hashlib.md5(hash_input.encode()).hexdigest()

def insert_incident(conn, incident):
    """Insert incident and its sources into database"""
    cursor = conn.cursor()

    try:
        # Extract data
        title = incident['title']
        narrative = incident['narrative']
        occurred_at = incident['occurred_at']
        location = incident['location']
        lat = location['lat']
        lon = location['lon']
        asset_type = incident['asset_type']
        country = incident['country']
        evidence_score = incident['evidence_score']

        # Generate hash
        occurred_dt = datetime.fromisoformat(occurred_at.replace('Z', '+00:00'))
        content_hash = generate_hash(title, occurred_dt, lat, lon)

        # Check if incident already exists
        cursor.execute("SELECT id FROM incidents WHERE content_hash = %s", (content_hash,))
        existing = cursor.fetchone()

        if existing:
            print(f"⏭️  Skipping duplicate: {title[:60]}...")
            return None

        # Insert incident
        cursor.execute("""
            INSERT INTO incidents (
                title, narrative, occurred_at, location, asset_type,
                status, evidence_score, verification_status, country,
                content_hash, first_seen_at, last_seen_at,
                lat_rounded, lon_rounded, occurred_hour,
                scraper_version, ingested_at
            ) VALUES (
                %s, %s, %s, ST_GeogFromText(%s), %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s
            ) RETURNING id
        """, (
            title, narrative, occurred_at, f'POINT({lon} {lat})', asset_type,
            'active', evidence_score, 'auto_verified', country,
            content_hash, occurred_at, occurred_at,
            round(lat, 4), round(lon, 4), occurred_dt.replace(minute=0, second=0, microsecond=0),
            '2.2.0', datetime.now(timezone.utc)
        ))

        incident_id = cursor.fetchone()[0]
        print(f"✅ Inserted: {title[:60]}... (ID: {incident_id})")

        # Insert sources
        for source in incident['sources']:
            # Check if source exists by name and type
            cursor.execute("""
                SELECT id FROM sources
                WHERE name = %s AND source_type = %s
                LIMIT 1
            """, (source['source_name'], source['source_type']))

            existing_source = cursor.fetchone()

            if existing_source:
                source_id = existing_source[0]
            else:
                # Insert new source
                cursor.execute("""
                    INSERT INTO sources (name, source_type, trust_weight)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (source['source_name'], source['source_type'], source['trust_weight']))
                source_id = cursor.fetchone()[0]

            # Insert incident_source link
            cursor.execute("""
                INSERT INTO incident_sources (
                    incident_id, source_id, source_url, source_quote,
                    source_title, published_at, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                incident_id, source_id, source['source_url'], source.get('source_quote', ''),
                source['source_name'], source.get('published_at'), json.dumps(source.get('metadata', {}))
            ))

            print(f"   📎 Source: {source['source_name']}")

        conn.commit()
        return incident_id

    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting incident: {e}")
        return None

def main():
    print("🐦 Fetching Twitter incidents...")
    scraper = TwitterScraper()
    incidents = scraper.fetch_all()
    print(f"Found {len(incidents)} incidents\n")

    # Connect to database
    print("📊 Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)

    inserted_count = 0
    for incident in incidents:
        result = insert_incident(conn, incident)
        if result:
            inserted_count += 1

    conn.close()

    print(f"\n✨ Done! Inserted {inserted_count}/{len(incidents)} incidents")

if __name__ == "__main__":
    main()
