from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response = {
            "name": "DroneWatch API",
            "version": "0.1.0",
            "docs": "/api/docs",
            "status": "operational"
        }
        self.wfile.write(json.dumps(response).encode())