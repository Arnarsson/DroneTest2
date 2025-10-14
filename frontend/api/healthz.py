from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_connection, run_async

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        DATABASE_URL = os.getenv("DATABASE_URL")

        # Check database connectivity
        async def check_db():
            try:
                if not DATABASE_URL:
                    return {
                        "ok": False,
                        "service": "dronewatch-api",
                        "database": "not configured",
                        "error": "DATABASE_URL environment variable not set"
                    }

                # Debug: Check if URL is correct format
                is_pooler = 'pooler.supabase.com' in DATABASE_URL and ':6543' in DATABASE_URL
                url_masked = DATABASE_URL[:30] + '...' if DATABASE_URL else 'None'

                # Test actual connection
                conn = await get_connection()
                await conn.fetchval("SELECT 1")

                # Get incident count
                count = await conn.fetchval("SELECT COUNT(*) FROM public.incidents")

                await conn.close()

                return {
                    "ok": True,
                    "service": "dronewatch-api",
                    "database": "connected",
                    "incident_count": count,
                    "using_pooler": is_pooler,
                    "debug_url": url_masked
                }
            except Exception as e:
                # SECURITY: Log full error server-side, don't expose to client
                import traceback
                print(f"Health check error: {type(e).__name__}: {str(e)}", file=sys.stderr)
                traceback.print_exc()  # Server-side logging for debugging

                # Return generic error - no internal details
                return {
                    "ok": False,
                    "service": "dronewatch-api",
                    "database": "error",
                    "error": "Database connection failed",
                    "detail": "Check server logs for details"
                }

        result = run_async(check_db())
        self.send_response(200 if result.get("ok") else 503)

        self.send_header('Content-Type', 'application/json')

        # Handle CORS - whitelist specific origins only
        ALLOWED_ORIGINS = [
            'https://www.dronemap.cc',
            'https://dronewatch.cc',
            'http://localhost:3000',
            'http://localhost:3001'
        ]

        origin = self.headers.get('Origin', '')
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')

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

        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        self.end_headers()