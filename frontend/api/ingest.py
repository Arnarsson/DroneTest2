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

        # Check for existing incident at same location
        # Location: ±0.01° (≈1.1km)
        # Strategy: One incident per location regardless of time
        existing_incident = await conn.fetchrow("""
            SELECT id, evidence_score, title
            FROM public.incidents
            WHERE ST_DWithin(
                location::geography,
                ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                1100  -- 1.1km radius
            )
            ORDER BY occurred_at ASC
            LIMIT 1
        """, lon, lat)

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
        if incident_data.get('sources'):
            for source in incident_data['sources']:
                try:
                    # Extract domain from source_url
                    from urllib.parse import urlparse
                    domain = urlparse(source.get('source_url', '')).netloc or 'unknown'

                    # First, get or create source in sources table
                    # Schema: UNIQUE (domain, source_type, homepage_url)
                    source_id = await conn.fetchval("""
                        INSERT INTO public.sources (name, domain, source_type, homepage_url, trust_weight)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (domain, source_type, homepage_url)
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
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(f"Database error: {error_details}", file=sys.stderr)
        return error_details

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Check authorization
        auth_header = self.headers.get('Authorization', '')
        expected_token = os.getenv('INGEST_TOKEN', 'test-token-please-change')

        if not auth_header.startswith('Bearer '):
            self.send_error(401, "Missing Bearer token")
            return

        token = auth_header.replace('Bearer ', '')
        if token != expected_token:
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

        # Handle CORS
        origin = self.headers.get('Origin', '')

        if 'error' in result:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
        else:
            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Location', f'/api/incidents/{result["id"]}')

        if origin and ('.vercel.app' in origin or origin in [
            "https://dronewatch.cc",
            "https://www.dronewatch.cc",
            "https://dronewatchv2.vercel.app",
            "http://localhost:3000"
        ]):
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')

        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight
        origin = self.headers.get('Origin', '')
        self.send_response(200)
        if origin:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()