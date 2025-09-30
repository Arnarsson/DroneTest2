from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import run_async, get_connection

async def test_connection():
    """Simple connection test"""
    try:
        conn = await get_connection()

        # Simple count query
        count = await conn.fetchval("SELECT COUNT(*) FROM public.incidents")

        # Close immediately
        await conn.close()

        return {
            "success": True,
            "incident_count": count
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # No auth required for simple test
        result = run_async(test_connection())

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2).encode())
