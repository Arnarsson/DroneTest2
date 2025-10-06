"""
Shared database utilities using Supabase REST API (PostgREST)
Works with self-hosted Supabase without requiring direct PostgreSQL access
"""
import os
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_incidents(
    min_evidence: int = 1,
    limit: int = 200,
    offset: int = 0,
    status: Optional[str] = None,
    country: Optional[str] = None,
    asset_type: Optional[str] = None,
    since: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch incidents from Supabase using REST API (PostgREST).
    Falls back to PostgreSQL if DATABASE_URL is set.
    """
    # Get environment variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Try REST API first if configured
    if SUPABASE_URL and (SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY):
        try:
            return await fetch_incidents_rest(
                supabase_url=SUPABASE_URL,
                api_key=SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY,
                min_evidence=min_evidence,
                limit=limit,
                offset=offset,
                status=status,
                country=country,
                asset_type=asset_type,
                since=since
            )
        except Exception as e:
            logger.error(f"REST API failed: {e}")
            # If REST fails and we have DATABASE_URL, try PostgreSQL
            if DATABASE_URL:
                logger.info("Falling back to PostgreSQL...")
                from db import fetch_incidents as fetch_pg
                return await fetch_pg(min_evidence, limit, offset, status, country, asset_type, since)
            raise

    # Fall back to PostgreSQL if configured
    elif DATABASE_URL:
        from db import fetch_incidents as fetch_pg
        return await fetch_pg(min_evidence, limit, offset, status, country, asset_type, since)

    else:
        raise ValueError("No database configuration found. Set either SUPABASE_URL+keys or DATABASE_URL")


async def fetch_incidents_rest(
    supabase_url: str,
    api_key: str,
    min_evidence: int = 1,
    limit: int = 200,
    offset: int = 0,
    status: Optional[str] = None,
    country: Optional[str] = None,
    asset_type: Optional[str] = None,
    since: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch incidents using Supabase REST API (PostgREST).
    """
    # Build REST API URL
    base_url = supabase_url.rstrip('/')
    rest_url = f"{base_url}/rest/v1/incidents"

    # Build query parameters for PostgREST
    # Use v_incidents view which has lat/lon already extracted
    rest_url = f"{base_url}/rest/v1/v_incidents"

    params = {
        'select': '''id,title,narrative,occurred_at,first_seen_at,last_seen_at,
                     asset_type,status,evidence_score,country,lat,lon''',
        'evidence_score': f'gte.{min_evidence}',
        'or': '(verification_status.in.(verified,auto_verified,pending),verification_status.is.null)',
        'order': 'occurred_at.desc',
        'limit': str(limit),
        'offset': str(offset)
    }

    # Add optional filters
    if status:
        params['status'] = f'eq.{status}'
    if country:
        params['country'] = f'eq.{country}'
    if asset_type:
        params['asset_type'] = f'eq.{asset_type}'
    if since:
        params['occurred_at'] = f'gte.{since}'

    headers = {
        'apikey': api_key,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rest_url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=9)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"REST API error {response.status}: {error_text}")
                    raise Exception(f"REST API returned {response.status}: {error_text}")

                incidents_data = await response.json()

                # Process incidents - v_incidents view already has lat/lon extracted
                incidents = []
                for row in incidents_data:
                    incident = {
                        "id": str(row["id"]),
                        "title": row.get("title"),
                        "narrative": row.get("narrative"),
                        "occurred_at": row.get("occurred_at"),
                        "first_seen_at": row.get("first_seen_at"),
                        "last_seen_at": row.get("last_seen_at"),
                        "asset_type": row.get("asset_type"),
                        "status": row.get("status"),
                        "evidence_score": row.get("evidence_score"),
                        "country": row.get("country"),
                        "lat": row.get("lat"),
                        "lon": row.get("lon"),
                        "sources": []  # We'll fetch sources separately if needed
                    }
                    incidents.append(incident)

                # Fetch sources for each incident
                if incidents:
                    incidents = await enrich_with_sources(base_url, api_key, incidents)

                return incidents

    except asyncio.TimeoutError:
        logger.error("REST API timeout")
        return {"error": "Query timeout", "type": "TimeoutError"}
    except Exception as e:
        logger.error(f"REST API error: {e}")
        return {"error": str(e), "type": type(e).__name__}


def extract_coordinates_from_geometry(geometry_hex: Optional[str]) -> tuple:
    """
    Extract lat/lon from PostGIS geometry hex string.
    For now, return None if not in expected format.
    PostgREST can also return GeoJSON if we use the right function.
    """
    # This is complex - PostGIS binary format
    # Better approach: use PostgREST's geometry conversion
    # For now, return None and we'll fix this with a better query
    return (None, None)


async def enrich_with_sources(base_url: str, api_key: str, incidents: List[Dict]) -> List[Dict]:
    """
    Fetch sources for each incident using a separate REST API call.
    """
    if not incidents:
        return incidents

    # Get all incident IDs
    incident_ids = [inc['id'] for inc in incidents]

    # Fetch all incident_sources in one query
    sources_url = f"{base_url}/rest/v1/incident_sources"
    params = {
        'select': 'incident_id,source_url,source_title,source_quote,published_at,sources(name,source_type)',
        'incident_id': f'in.({",".join(incident_ids)})'
    }
    headers = {
        'apikey': api_key,
        'Authorization': f'Bearer {api_key}'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(sources_url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    sources_data = await response.json()

                    # Group sources by incident_id
                    sources_by_incident = {}
                    for source in sources_data:
                        incident_id = str(source['incident_id'])
                        if incident_id not in sources_by_incident:
                            sources_by_incident[incident_id] = []

                        source_info = source.get('sources', {}) or {}
                        sources_by_incident[incident_id].append({
                            'source_url': source.get('source_url'),
                            'source_type': source_info.get('source_type', 'unknown'),
                            'source_name': source_info.get('name', 'Unknown'),
                            'source_title': source.get('source_title'),
                            'source_quote': source.get('source_quote'),
                            'published_at': source.get('published_at')
                        })

                    # Attach sources to incidents
                    for incident in incidents:
                        incident['sources'] = sources_by_incident.get(incident['id'], [])

    except Exception as e:
        logger.warning(f"Failed to fetch sources: {e}")

    return incidents


def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
