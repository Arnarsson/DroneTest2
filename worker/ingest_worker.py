#!/usr/bin/env python3
"""
DroneWatch Ingestion Worker
Schedules and runs data collection from various sources
"""
import os
import asyncio
import httpx
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.log import get_logger
from utils.verify import (
    ExtractedIncident, extract_domain, score_from_source,
    safe_accept, is_drone_related, extract_police_quote
)
from utils.dedupe import incident_hash, DedupCache
from utils.geocode import extract_location, get_country_from_location
from sources.rss_generic import parse_rss_feed
from sources.dk_police import fetch_police_news, fetch_police_article

# Load environment
load_dotenv()
log = get_logger("ingest_worker")

# Configuration
INGEST_URL = os.getenv("INGEST_URL", "http://localhost:8000/ingest")
INGEST_TOKEN = os.getenv("INGEST_TOKEN", "")
TRUSTED = set(os.getenv("TRUSTED", "").split(","))
RSS_FEEDS = [u.strip() for u in os.getenv("RSS_FEEDS", "").split(",") if u.strip()]
POLICE_URLS = [u.strip() for u in os.getenv("POLICE_HTML", "").split(",") if u.strip()]
COUNTRIES = [c.strip() for c in os.getenv("COUNTRIES", "DK").split(",") if c.strip()]

# Deduplication cache
dedupe = DedupCache(max_size=10000)
dedupe.load_from_file("dedupe_cache.json")

async def post_incident(payload: Dict) -> Optional[Dict]:
    """Post incident to API"""
    if not INGEST_TOKEN:
        log.error("INGEST_TOKEN not configured")
        return None

    headers = {
        "Authorization": f"Bearer {INGEST_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(INGEST_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        log.error(f"API error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        log.error(f"Failed to post incident: {e}")
        return None

def build_payload(
    incident: ExtractedIncident,
    source_url: str,
    source_type: str,
    lat: float,
    lon: float,
    location_name: Optional[str],
    asset_type: str,
    country: str,
    evidence_score: int,
    content_hash: str
) -> Dict:
    """Build API payload from extracted incident"""
    return {
        "title": incident.title or "Drone incident",
        "narrative": incident.narrative or "",
        "occurred_at": incident.occurred_at_iso or datetime.now(timezone.utc).isoformat(),
        "lat": lat,
        "lon": lon,
        "location_name": location_name,
        "asset_type": asset_type,
        "status": "active",
        "evidence_score": evidence_score,
        "country": country,
        "content_hash": content_hash,
        "sources": [{
            "source_url": source_url,
            "source_type": source_type,
            "source_quote": (
                incident.quotes.get("title") or
                incident.quotes.get("narrative") or
                incident.quotes.get("location_name") or
                ""
            )[:500]
        }]
    }

def extract_from_text(title: str, text: str, url: str = "") -> ExtractedIncident:
    """Extract incident data from text"""
    full_text = f"{title} {text}"

    # Check if drone-related
    if not is_drone_related(full_text):
        return ExtractedIncident(is_incident=False)

    # Extract location
    lat, lon, location_name, asset_type = extract_location(full_text)

    # Extract quotes (prefer police quotes)
    quote = extract_police_quote(text) if "politi" in url.lower() else None

    # Build confirmations list
    confirmations = []
    text_lower = text.lower()
    if "politi" in text_lower or "police" in text_lower:
        confirmations.append("police")
    if "lufthavn" in text_lower or "airport" in text_lower:
        confirmations.append("airport")
    if "notam" in text_lower:
        confirmations.append("notam")

    return ExtractedIncident(
        is_incident=True,
        title=title[:200],
        location_name=location_name,
        narrative=text[:500] if text else None,
        confirmations=confirmations,
        quotes={"narrative": quote} if quote else {}
    )

async def process_rss_feeds():
    """Process RSS feeds"""
    log.info("Processing RSS feeds...")
    count = 0

    for feed_url in RSS_FEEDS:
        try:
            for item in parse_rss_feed(feed_url):
                # Extract incident
                incident = extract_from_text(
                    item.get("title", ""),
                    item.get("summary", ""),
                    item.get("url", "")
                )

                if not incident.is_incident:
                    continue

                # Get location
                lat, lon, location_name, asset_type = extract_location(
                    f"{incident.title} {incident.narrative}"
                )

                # Calculate evidence score
                domain = extract_domain(item.get("url", ""))
                evidence = score_from_source(domain, "media", TRUSTED)

                # Generate hash for deduplication
                hash_key = incident_hash(
                    incident.title,
                    location_name,
                    incident.occurred_at_iso,
                    get_country_from_location(lat, lon)
                )

                # Skip if already processed
                if dedupe.has_seen(hash_key):
                    continue

                # Verify quality
                if not safe_accept(incident, evidence):
                    log.debug(f"Rejected low-quality: {incident.title}")
                    continue

                # Build and post
                payload = build_payload(
                    incident, item.get("url", ""), "media",
                    lat, lon, location_name, asset_type,
                    get_country_from_location(lat, lon),
                    evidence, hash_key
                )

                result = await post_incident(payload)
                if result:
                    dedupe.mark_seen(hash_key)
                    count += 1
                    log.info(f"RSS ingested: {incident.title[:50]}")

        except Exception as e:
            log.error(f"Error processing RSS {feed_url}: {e}")

    log.info(f"RSS: Ingested {count} incidents")

async def process_police_sites():
    """Process police websites"""
    log.info("Processing police sites...")
    count = 0

    for police_url in POLICE_URLS:
        try:
            news_items = fetch_police_news(police_url)

            for item in news_items:
                # Fetch full article
                article = fetch_police_article(item["url"])

                # Extract incident
                incident = extract_from_text(
                    item.get("title", ""),
                    article.get("text", ""),
                    item.get("url", "")
                )

                if not incident.is_incident:
                    continue

                # Override with article data if available
                if article.get("occurred_iso"):
                    incident.occurred_at_iso = article["occurred_iso"]
                if article.get("quote"):
                    incident.quotes["narrative"] = article["quote"]

                # Get location
                lat, lon, location_name, asset_type = extract_location(
                    f"{incident.title} {incident.narrative}"
                )

                # Police = evidence score 4
                evidence = 4

                # Generate hash
                hash_key = incident_hash(
                    incident.title,
                    location_name,
                    incident.occurred_at_iso,
                    get_country_from_location(lat, lon)
                )

                # Skip if seen
                if dedupe.has_seen(hash_key):
                    continue

                # Build and post
                payload = build_payload(
                    incident, item["url"], "police",
                    lat, lon, location_name, asset_type,
                    get_country_from_location(lat, lon),
                    evidence, hash_key
                )

                result = await post_incident(payload)
                if result:
                    dedupe.mark_seen(hash_key)
                    count += 1
                    log.info(f"Police ingested: {incident.title[:50]}")

        except Exception as e:
            log.error(f"Error processing police site {police_url}: {e}")

    log.info(f"Police: Ingested {count} incidents")

async def process_notams():
    """Process NOTAMs (placeholder for future implementation)"""
    log.debug("NOTAM processing not yet implemented")
    # TODO: Implement NOTAM fetching from FAA/Eurocontrol APIs

async def main():
    """Main worker loop"""
    log.info("=" * 60)
    log.info("DroneWatch Ingestion Worker Starting")
    log.info(f"API: {INGEST_URL}")
    log.info(f"Countries: {', '.join(COUNTRIES)}")
    log.info(f"RSS Feeds: {len(RSS_FEEDS)}")
    log.info(f"Police Sites: {len(POLICE_URLS)}")
    log.info("=" * 60)

    # Create scheduler
    scheduler = AsyncIOScheduler()

    # Schedule jobs
    scheduler.add_job(
        process_rss_feeds,
        'interval',
        minutes=int(os.getenv("SCHED_RSS", "10")),
        id='rss_feeds',
        max_instances=1
    )

    scheduler.add_job(
        process_police_sites,
        'interval',
        minutes=int(os.getenv("SCHED_POLICE_HTML", "5")),
        id='police_sites',
        max_instances=1
    )

    scheduler.add_job(
        process_notams,
        'interval',
        minutes=int(os.getenv("SCHED_NOTAM", "15")),
        id='notams',
        max_instances=1
    )

    # Start scheduler
    scheduler.start()

    # Run initial fetch
    log.info("Running initial fetch...")
    await process_police_sites()
    await process_rss_feeds()

    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
            # Save dedupe cache periodically
            dedupe.save_to_file("dedupe_cache.json")
    except KeyboardInterrupt:
        log.info("Shutting down...")
        scheduler.shutdown()
        dedupe.save_to_file("dedupe_cache.json")

if __name__ == "__main__":
    asyncio.run(main())