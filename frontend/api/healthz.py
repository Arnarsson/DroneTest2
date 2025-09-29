from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        DATABASE_URL = os.getenv("DATABASE_URL")

        result = {
            "ok": bool(DATABASE_URL),
            "service": "dronewatch-api",
            "database": "configured" if DATABASE_URL else "not configured"
        }

        self.send_response(200 if result["ok"] else 503)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())