from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs, urlparse

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import run_async
import asyncpg

async def insert_incident(incident_data):
    """Insert incident into database"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            return {"error": "DATABASE_URL not configured"}

        # Connect to database
        if 'supabase.co' in DATABASE_URL or 'supabase.com' in DATABASE_URL:
            clean_url = DATABASE_URL.split('?')[0] if '?' in DATABASE_URL else DATABASE_URL
            conn = await asyncpg.connect(clean_url, ssl='require', statement_cache_size=0)
        else:
            conn = await asyncpg.connect(DATABASE_URL)

        # Insert incident
        query = """
        INSERT INTO public.incidents
        (title, narrative, occurred_at, first_seen_at, last_seen_at,
         asset_type, status, evidence_score, country, location)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9,
                ST_SetSRID(ST_MakePoint($10, $11), 4326))
        RETURNING id
        """

        incident_id = await conn.fetchval(
            query,
            incident_data['title'],
            incident_data.get('narrative', ''),
            incident_data.get('occurred_at'),
            incident_data.get('first_seen_at', incident_data.get('occurred_at')),
            incident_data.get('last_seen_at', incident_data.get('occurred_at')),
            incident_data.get('asset_type', 'unknown'),
            incident_data.get('status', 'active'),
            incident_data.get('evidence_score', 1),
            incident_data.get('country', 'DK'),
            incident_data.get('lon'),
            incident_data.get('lat')
        )

        # Insert sources if provided
        if incident_data.get('sources'):
            for source in incident_data['sources']:
                source_query = """
                INSERT INTO public.incident_sources
                (incident_id, source_url, source_type, source_quote)
                VALUES ($1, $2, $3, $4)
                """
                await conn.execute(
                    source_query,
                    incident_id,
                    source.get('source_url', ''),
                    source.get('source_type', 'unknown'),
                    source.get('source_quote', '')
                )

        await conn.close()

        return {"id": str(incident_id), "status": "created"}

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

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