from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        DATABASE_URL = os.getenv("DATABASE_URL")

        # Parse the URL to show what we have
        info = {
            "has_database_url": bool(DATABASE_URL),
            "url_length": len(DATABASE_URL) if DATABASE_URL else 0,
        }

        if DATABASE_URL:
            # Show safe parts of the URL
            if '@' in DATABASE_URL:
                parts = DATABASE_URL.split('@')
                protocol_user = parts[0].split('://')[0] if '://' in parts[0] else 'unknown'
                host_part = parts[1] if len(parts) > 1 else 'unknown'

                info['protocol'] = protocol_user
                info['host'] = host_part[:50] + '...' if len(host_part) > 50 else host_part
                info['has_pooler'] = 'pooler.supabase.com' in DATABASE_URL
                info['port'] = '6543' if ':6543' in DATABASE_URL else ('5432' if ':5432' in DATABASE_URL else 'unknown')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(info, indent=2).encode())