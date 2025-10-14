from http.server import BaseHTTPRequestHandler
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import run_async, get_connection

async def simple_query():
    """Simple query without sources subquery"""
    try:
        conn = await get_connection()

        # Simple query without complex subquery
        rows = await conn.fetch("""
            SELECT i.id, i.title, i.narrative, i.occurred_at, i.evidence_score,
                   i.country, i.status, i.verification_status,
                   ST_Y(i.location::geometry) as lat,
                   ST_X(i.location::geometry) as lon
            FROM public.incidents i
            WHERE i.evidence_score >= 1
              AND (i.verification_status IN ('verified', 'auto_verified', 'pending')
                   OR i.verification_status IS NULL)
            ORDER BY i.occurred_at DESC
            LIMIT 5
        """)

        incidents = [
            {
                "id": str(row['id']),
                "title": row['title'],
                "narrative": row['narrative'][:100] if row['narrative'] else None,
                "occurred_at": row['occurred_at'].isoformat() if row['occurred_at'] else None,
                "evidence_score": row['evidence_score'],
                "country": row['country'],
                "status": row['status'],
                "verification_status": row['verification_status'],
                "lat": float(row['lat']) if row['lat'] else None,
                "lon": float(row['lon']) if row['lon'] else None
            }
            for row in rows
        ]

        await conn.close()

        return {
            "success": True,
            "count": len(incidents),
            "incidents": incidents
        }

    except Exception as e:
        # SECURITY: Log full error server-side only, never expose to client
        # Exposing tracebacks reveals internal file paths, database schema,
        # and implementation details that can aid attackers
        import traceback
        traceback.print_exc()  # Server-side logging for debugging
        print(f"Simple test error: {type(e).__name__}: {str(e)}", file=sys.stderr)

        # Return generic error to client - no internal details
        return {
            "success": False,
            "error": "Internal server error",
            "detail": "Failed to fetch incidents. Check server logs for details."
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        result = run_async(simple_query())

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2).encode())
