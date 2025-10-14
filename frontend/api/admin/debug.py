from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import run_async, get_connection

async def debug_incidents():
    """Debug incidents in database"""
    try:
        conn = await get_connection()

        # Get total count
        total = await conn.fetchval("SELECT COUNT(*) FROM public.incidents")

        # Get sample incidents
        incidents = await conn.fetch("""
            SELECT id, title, evidence_score, verification_status, country, status, occurred_at
            FROM public.incidents
            ORDER BY occurred_at DESC
            LIMIT 10
        """)

        # Get verification_status distribution
        verification_dist = await conn.fetch("""
            SELECT
                COALESCE(verification_status, 'NULL') as status,
                COUNT(*) as count
            FROM public.incidents
            GROUP BY verification_status
        """)

        # Get evidence_score distribution
        evidence_dist = await conn.fetch("""
            SELECT
                evidence_score,
                COUNT(*) as count
            FROM public.incidents
            GROUP BY evidence_score
            ORDER BY evidence_score
        """)

        await conn.close()

        return {
            "total_incidents": total,
            "verification_distribution": {row['status']: row['count'] for row in verification_dist},
            "evidence_distribution": {row['evidence_score']: row['count'] for row in evidence_dist},
            "sample_incidents": [
                {
                    "id": str(row['id']),
                    "title": row['title'][:60],
                    "evidence_score": row['evidence_score'],
                    "verification_status": row['verification_status'],
                    "country": row['country'],
                    "status": row['status'],
                    "occurred_at": row['occurred_at'].isoformat() if row['occurred_at'] else None
                }
                for row in incidents
            ]
        }

    except Exception as e:
        # SECURITY: Log full error server-side only, never expose to client
        # Even admin endpoints should not expose tracebacks (defense in depth)
        import traceback
        traceback.print_exc()  # Server-side logging for debugging
        print(f"Debug endpoint error: {type(e).__name__}: {str(e)}", file=sys.stderr)

        # Return generic error to client - no internal details
        return {
            "error": "Failed to retrieve debug information",
            "detail": "Check server logs for details."
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
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

        # Get debug info
        result = run_async(debug_incidents())

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2).encode())
