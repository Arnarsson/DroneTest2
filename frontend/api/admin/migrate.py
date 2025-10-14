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
        # SECURITY: Log full error server-side only, never expose to client
        # Even admin endpoints should not expose tracebacks (defense in depth)
        import traceback
        traceback.print_exc()  # Server-side logging for debugging
        print(f"Migration error: {type(e).__name__}: {str(e)}", file=sys.stderr)

        # Return generic error to client - no internal details
        return {
            "success": False,
            "error": "Migration failed",
            "detail": "Check server logs for details."
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Check authorization with security best practices
        import secrets
        expected_token = os.getenv('INGEST_TOKEN')
        if not expected_token:
            self.send_error(500, "Server configuration error: INGEST_TOKEN not set")
            return

        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self.send_error(401, "Missing Bearer token")
            return

        token = auth_header.replace('Bearer ', '')
        # Use constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(token, expected_token):
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
