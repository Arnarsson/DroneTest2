from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import run_async, get_connection

async def run_migration():
    """Run migration to set verification_status for existing incidents"""
    try:
        conn = await get_connection()

        # Check current state
        current_state = await conn.fetch("""
            SELECT
                COALESCE(verification_status, 'NULL') as status,
                COUNT(*) as count
            FROM public.incidents
            GROUP BY verification_status
            ORDER BY count DESC
        """)

        current_dist = {row['status']: row['count'] for row in current_state}

        # Run migration
        result = await conn.execute("""
            UPDATE public.incidents
            SET verification_status = 'pending'
            WHERE verification_status IS NULL
        """)

        updated_count = int(result.split()[-1])

        # Check new state
        new_state = await conn.fetch("""
            SELECT
                COALESCE(verification_status, 'NULL') as status,
                COUNT(*) as count
            FROM public.incidents
            GROUP BY verification_status
            ORDER BY count DESC
        """)

        new_dist = {row['status']: row['count'] for row in new_state}

        await conn.close()

        return {
            "success": True,
            "updated_count": updated_count,
            "before": current_dist,
            "after": new_dist
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
    def do_POST(self):
        # Check authorization
        auth_header = self.headers.get('Authorization', '')
        expected_token = os.getenv('INGEST_TOKEN', 'test-token-please-change')

        if not auth_header.startswith('Bearer '):
            self.send_error(401, "Missing Bearer token")
            return

        token = auth_header.replace('Bearer ', '')
        if token != expected_token:
            self.send_error(403, "Invalid token")
            return

        # Run migration
        result = run_async(run_migration())

        # Send response
        if result.get('success'):
            self.send_response(200)
        else:
            self.send_response(500)

        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2).encode())
