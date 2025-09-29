from http.server import BaseHTTPRequestHandler
import json
import os
import asyncpg
import asyncio

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
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def handle_get(self):
        DATABASE_URL = os.getenv("DATABASE_URL")

        async def check_health():
            try:
                if not DATABASE_URL:
                    return {"ok": False, "service": "dronewatch-api", "error": "Database not configured"}

                # Connect and test database
                if 'supabase.co' in DATABASE_URL or 'supabase.com' in DATABASE_URL:
                    clean_url = DATABASE_URL.split('?')[0] if '?' in DATABASE_URL else DATABASE_URL
                    conn = await asyncpg.connect(clean_url, ssl='require')
                else:
                    conn = await asyncpg.connect(DATABASE_URL)

                await conn.fetchval("SELECT 1")
                await conn.close()
                return {"ok": True, "service": "dronewatch-api", "database": "connected"}
            except Exception as e:
                return {
                    "ok": False,
                    "service": "dronewatch-api",
                    "error": str(e),
                    "type": type(e).__name__
                }

        result = asyncio.run(check_health())

        # Handle CORS
        origin = self.headers.get('Origin', '')

        # Send response
        status_code = 200 if result.get("ok") else 503
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')

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