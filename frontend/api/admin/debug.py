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
        import traceback
        return {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
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

        # Get debug info
        result = run_async(debug_incidents())

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2).encode())
