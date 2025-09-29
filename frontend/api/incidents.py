from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs, urlparse

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import fetch_incidents, run_async

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

        # Fetch incidents from database
        try:
            result = run_async(fetch_incidents(
                min_evidence=min_evidence,
                limit=limit,
                offset=offset,
                status=status,
                country=country
            ))

            # Check if it's an error response
            if isinstance(result, dict) and 'error' in result:
                incidents = []
                status_code = 500
            else:
                incidents = result
                status_code = 200
        except Exception as e:
            incidents = []
            status_code = 500

        # Handle CORS
        origin = self.headers.get('Origin', '')

        # Send response
        self.send_response(status_code)
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
        self.wfile.write(json.dumps(incidents).encode())