"""
API endpoint for Vercel serverless function
"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "message": "DroneWatch API",
            "status": "operational",
            "path": self.path,
            "test": "This is a working serverless function"
        }

        self.wfile.write(json.dumps(response).encode())
        return