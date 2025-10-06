from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Return environment variable status
        env_status = {
            "SUPABASE_URL": "set" if os.getenv("SUPABASE_URL") else "not set",
            "SUPABASE_ANON_KEY": "set" if os.getenv("SUPABASE_ANON_KEY") else "not set",
            "SUPABASE_SERVICE_KEY": "set" if os.getenv("SUPABASE_SERVICE_KEY") else "not set",
            "DATABASE_URL": "set" if os.getenv("DATABASE_URL") else "not set",
            "SUPABASE_URL_value": os.getenv("SUPABASE_URL", "")[:50] + "..." if os.getenv("SUPABASE_URL") else ""
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(env_status, indent=2).encode())
