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
                return {
                    "ok": False,
                    "service": "dronewatch-api",
                    "database": "error",
                    "error": str(e),
                    "type": type(e).__name__,
                    "has_env": bool(DATABASE_URL),
                    "using_pooler": 'pooler.supabase.com' in (DATABASE_URL or '') and ':6543' in (DATABASE_URL or '')
                }

        result = run_async(check_db())
        self.send_response(200 if result.get("ok") else 503)

        self.send_header('Content-Type', 'application/json')

        # Add CORS headers
        origin = self.headers.get('Origin', '')
        if origin and ('.vercel.app' in origin or origin in [
            "https://dronewatch.cc",
            "https://www.dronewatch.cc",
            "https://dronewatchv2.vercel.app",
            "http://localhost:3000"
        ]):
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')

        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

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
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()