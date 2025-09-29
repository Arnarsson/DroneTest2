from http.server import BaseHTTPRequestHandler
import json
import os
import asyncpg
from datetime import datetime
from urllib.parse import parse_qs, urlparse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_get()

    def do_OPTIONS(self):
        # Handle CORS preflight
        origin = self.headers.get('Origin', '')
        self.send_response(200)
        if origin and ('.vercel.app' in origin or origin in [
            "https://dronewatch.cc",
            "https://www.dronewatch.cc",
            "https://dronewatchv2.vercel.app",
            "http://localhost:3000"
        ]):
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def handle_get(self):
        # Parse query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Get parameters with defaults
        min_evidence = int(query_params.get('min_evidence', ['1'])[0])
        limit = min(int(query_params.get('limit', ['200'])[0]), 1000)
        offset = int(query_params.get('offset', ['0'])[0])
        status = query_params.get('status', [None])[0]
        country = query_params.get('country', [None])[0]

        # Get database connection
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            self.send_error(500, "Database not configured")
            return

        # Run async query
        import asyncio

        async def get_incidents():
            try:
                # Connect to database
                if 'supabase.co' in DATABASE_URL or 'supabase.com' in DATABASE_URL:
                    clean_url = DATABASE_URL.split('?')[0] if '?' in DATABASE_URL else DATABASE_URL
                    conn = await asyncpg.connect(clean_url, ssl='require')
                else:
                    conn = await asyncpg.connect(DATABASE_URL)

                # Build query
                query = """
                SELECT i.id, i.title, i.narrative, i.occurred_at, i.first_seen_at, i.last_seen_at,
                       i.asset_type, i.status, i.evidence_score, i.country,
                       ST_Y(i.location::geometry) as lat,
                       ST_X(i.location::geometry) as lon
                FROM public.incidents i
                WHERE i.evidence_score >= $1
                """
                params = [min_evidence]
                param_count = 1

                if status:
                    param_count += 1
                    query += f" AND i.status = ${param_count}"
                    params.append(status)

                if country:
                    param_count += 1
                    query += f" AND i.country = ${param_count}"
                    params.append(country)

                query += f" ORDER BY i.occurred_at DESC LIMIT ${param_count+1} OFFSET ${param_count+2}"
                params.extend([limit, offset])

                # Execute query
                rows = await conn.fetch(query, *params)

                # Format results
                incidents = []
                for row in rows:
                    incidents.append({
                        "id": str(row["id"]),
                        "title": row["title"],
                        "narrative": row["narrative"],
                        "occurred_at": row["occurred_at"].isoformat() if row["occurred_at"] else None,
                        "first_seen_at": row["first_seen_at"].isoformat() if row["first_seen_at"] else None,
                        "last_seen_at": row["last_seen_at"].isoformat() if row["last_seen_at"] else None,
                        "asset_type": row["asset_type"],
                        "status": row["status"],
                        "evidence_score": row["evidence_score"],
                        "country": row["country"],
                        "lat": row["lat"],
                        "lon": row["lon"],
                        "sources": []
                    })

                await conn.close()
                return incidents

            except Exception as e:
                return {"error": str(e), "type": type(e).__name__}

        # Run the async function
        result = asyncio.run(get_incidents())

        # Handle CORS
        origin = self.headers.get('Origin', '')

        # Send response
        if isinstance(result, dict) and 'error' in result:
            self.send_response(500)
        else:
            self.send_response(200)

        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'public, max-age=15')

        if origin and ('.vercel.app' in origin or origin in [
            "https://dronewatch.cc",
            "https://www.dronewatch.cc",
            "https://dronewatchv2.vercel.app",
            "http://localhost:3000"
        ]):
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')

        self.end_headers()
        self.wfile.write(json.dumps(result).encode())