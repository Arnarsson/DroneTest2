from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        DATABASE_URL = os.getenv("DATABASE_URL")

        # Basic check - just verify DATABASE_URL is set
        if not DATABASE_URL:
            result = {
                "ok": False,
                "service": "dronewatch-api",
                "database": "not configured",
                "error": "DATABASE_URL environment variable not set"
            }
            self.send_response(503)
        else:
            # For now, just confirm it's configured
            # We'll add actual connection test once basic setup works
            result = {
                "ok": True,
                "service": "dronewatch-api",
                "database": "configured"
            }
            self.send_response(200)

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