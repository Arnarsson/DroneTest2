from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import logging
import asyncio
from urllib.parse import parse_qs, urlparse
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import run_async, get_connection
import asyncpg

logger = logging.getLogger(__name__)

def parse_datetime(dt_string):
    """Parse ISO datetime string to datetime object"""
    from datetime import timezone
    if not dt_string:
        return None
    if isinstance(dt_string, datetime):
        # Ensure timezone-aware
        if dt_string.tzinfo is None:
            return dt_string.replace(tzinfo=timezone.utc)
        return dt_string
    # Handle ISO format with 'Z' or timezone
    if dt_string.endswith('Z'):
        dt_string = dt_string[:-1] + '+00:00'
    dt = datetime.fromisoformat(dt_string)
    # Ensure timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

async def insert_incident(incident_data):
    """
    Insert incident or add as source to existing incident.

    Deduplication strategy:
    - Check for existing incident at same location (±1km)
    - If exists: Add as source, update evidence score, extend time range
    - If new: Create new incident
    - Result: One incident per location regardless of when events occurred
    """
    try:
        # Use shared database connection utility
        conn = await get_connection()

        # Parse datetime strings
        occurred_at = parse_datetime(incident_data.get('occurred_at'))
        first_seen_at = parse_datetime(incident_data.get('first_seen_at', incident_data.get('occurred_at')))
        last_seen_at = parse_datetime(incident_data.get('last_seen_at', incident_data.get('occurred_at')))

        lat = incident_data.get('lat')
        lon = incident_data.get('lon')

        # RACE CONDITION FIX: Check if source URL already exists globally
        # This prevents duplicates during batch ingestion when multiple requests
        # for the same incident arrive simultaneously
        existing_incident = None
        if incident_data.get('sources'):
            for source in incident_data['sources']:
                source_url = source.get('source_url', '')
                if source_url:
                    existing_incident = await conn.fetchrow("""
                        SELECT i.id, i.evidence_score, i.title, i.asset_type
                        FROM public.incidents i
                        JOIN public.incident_sources s ON i.id = s.incident_id
                        WHERE s.source_url = $1
                        LIMIT 1
                    """, source_url)
                    if existing_incident:
                        logger.info(f"Found incident via global source check: {existing_incident['title'][:50]}")
                        break

        # If no existing incident found via source URL, check for existing incident at same facility
        # Strategy: One incident per facility (smart radius based on asset type)
        # Airports/Military: 3km (large facilities)
        # Harbors: 1.5km (medium facilities)
        # Other: 500m (specific locations)

        if not existing_incident:
            asset_type = incident_data.get('asset_type', 'other')
            search_radius = {
                'airport': 3000,    # 3km - airports are large
                'military': 3000,   # 3km - military bases are large
                'harbor': 1500,     # 1.5km - harbors are medium
                'powerplant': 1000, # 1km - power plants
                'bridge': 500,      # 500m - bridges are specific
                'other': 500        # 500m - default for unknown
            }.get(asset_type, 500)

            existing_incident = await conn.fetchrow("""
                SELECT id, evidence_score, title, asset_type
                FROM public.incidents
                WHERE ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                    $3  -- Dynamic radius based on asset type
                )
                AND asset_type = $4  -- Must be same asset type
                ORDER BY occurred_at ASC
                LIMIT 1
            """, lon, lat, search_radius, asset_type)

        if existing_incident:
            # Incident already exists - add this as a source instead
            incident_id = existing_incident['id']
            logger.info(f"Found existing incident: {existing_incident['title'][:50]}")
            logger.info(f"Adding new article as source: {incident_data['title'][:50]}")

            # Update time range to encompass all events at this location
            await conn.execute("""
                UPDATE public.incidents
                SET
                    first_seen_at = LEAST(first_seen_at, $1),
                    last_seen_at = GREATEST(last_seen_at, $2),
                    occurred_at = LEAST(occurred_at, $3)
                WHERE id = $4
            """, first_seen_at, last_seen_at, occurred_at, incident_id)

        else:
            # New incident - create it
            query = """
            INSERT INTO public.incidents
            (title, narrative, occurred_at, first_seen_at, last_seen_at,
             asset_type, status, evidence_score, country, location, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9,
                    ST_SetSRID(ST_MakePoint($10, $11), 4326), $12)
            RETURNING id
            """

            incident_id = await conn.fetchval(
                query,
                incident_data['title'],
                incident_data.get('narrative', ''),
                occurred_at,
                first_seen_at,
                last_seen_at,
                incident_data.get('asset_type', 'other'),
                incident_data.get('status', 'active'),
                incident_data.get('evidence_score', 1),
                incident_data.get('country', 'DK'),
                incident_data.get('lon'),
                incident_data.get('lat'),
                incident_data.get('verification_status', 'pending')
            )

        # Insert sources if provided
        # NOTE: After sources are inserted, the database trigger 'trigger_update_evidence_score'
        # will automatically recalculate the incident's evidence_score based on source trust_weights
        if incident_data.get('sources'):
            for source in incident_data['sources']:
                try:
                    # Extract domain from source_url
                    from urllib.parse import urlparse
                    domain = urlparse(source.get('source_url', '')).netloc or 'unknown'

                    # First, get or create source in sources table
                    # Schema: UNIQUE (domain, source_type) - see sql/supabase_schema_v2.sql line 45
                    source_id = await conn.fetchval("""
                        INSERT INTO public.sources (name, domain, source_type, homepage_url, trust_weight)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (domain, source_type)
                        DO UPDATE SET
                            name = EXCLUDED.name,
                            trust_weight = GREATEST(sources.trust_weight, EXCLUDED.trust_weight)
                        RETURNING id
                    """,
                        source.get('source_name', 'Unknown'),  # name field
                        domain,  # domain field
                        source.get('source_type', 'other'),  # source_type (required)
                        source.get('source_url', ''),  # homepage_url (use source_url)
                        source.get('trust_weight', 1)  # trust_weight
                    )

                    # Then insert into incident_sources junction table
                    # This INSERT triggers automatic evidence_score recalculation
                    await conn.execute("""
                        INSERT INTO public.incident_sources
                        (incident_id, source_id, source_url, source_title, source_quote)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (incident_id, source_url) DO NOTHING
                    """,
                        incident_id,
                        source_id,
                        source.get('source_url', ''),
                        source.get('source_name', ''),  # source_title
                        source.get('source_quote', '')
                    )
                except Exception as source_error:
                    # Log source insertion errors but continue with incident
                    logger.error(f"Failed to insert source: {source_error}")
                    continue

        # Close connection gracefully (with timeout for serverless)
        try:
            await asyncio.wait_for(conn.close(), timeout=2.0)
        except asyncio.TimeoutError:
            logger.warning("Connection close timed out (normal for serverless)")
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")

        return {"id": str(incident_id), "status": "created"}

    except Exception as e:
        import traceback
        # SECURITY: Log full traceback server-side only, never expose to client
        # Exposing tracebacks reveals internal file paths, database schema,
        # and implementation details that can aid attackers
        traceback.print_exc()  # Server-side logging for debugging
        logger.error(f"Database error: {type(e).__name__}: {str(e)}")

        # Return generic error to client - no internal details
        return {
            "error": "Internal server error",
            "detail": "Failed to process incident. Check server logs for details."
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Check authorization with security best practices
        import secrets
        expected_token = os.getenv('INGEST_TOKEN')
        if not expected_token:
            self.send_error(500, "Server configuration error: INGEST_TOKEN not set")
            return

        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self.send_error(401, "Missing Bearer token")
            return

        token = auth_header.replace('Bearer ', '')
        # Use constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(token, expected_token):
            self.send_error(403, "Invalid token")
            return

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error(400, "Empty request body")
            return

        body = self.rfile.read(content_length)

        try:
            incident_data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        # Validate required fields
        required_fields = ['title', 'occurred_at', 'lat', 'lon']
        missing = [f for f in required_fields if f not in incident_data]
        if missing:
            self.send_error(400, f"Missing required fields: {', '.join(missing)}")
            return

        # Insert into database
        result = run_async(insert_incident(incident_data))

        # Handle CORS - whitelist specific origins only
        ALLOWED_ORIGINS = [
            'https://www.dronemap.cc',
            'https://dronewatch.cc',
            'http://localhost:3000',
            'http://localhost:3001'
        ]

        origin = self.headers.get('Origin', '')

        if 'error' in result:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
        else:
            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Location', f'/api/incidents/{result["id"]}')

        # Only allow whitelisted origins
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        elif origin:
            # Origin provided but not allowed - reject
            logger.warning(f"Blocked CORS request from unauthorized origin: {origin}")

        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight - whitelist specific origins only
        ALLOWED_ORIGINS = [
            'https://www.dronemap.cc',
            'https://dronewatch.cc',
            'http://localhost:3000',
            'http://localhost:3001'
        ]

        origin = self.headers.get('Origin', '')
        self.send_response(200)

        # Only allow whitelisted origins
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        elif origin:
            # Origin provided but not allowed - reject with 403
            logger.warning(f"Blocked CORS preflight from unauthorized origin: {origin}")
            self.send_response(403)

        self.end_headers()