"""
Shared database utilities for Vercel serverless functions
"""
import os
import asyncpg
import asyncio
from typing import Optional, Dict, Any, List

async def get_connection():
    """Get database connection with proper SSL configuration"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not configured")

    # For Supabase connections, use SSL
    if 'supabase.co' in DATABASE_URL or 'supabase.com' in DATABASE_URL:
        # Remove query parameters like ?pgbouncer=true
        clean_url = DATABASE_URL.split('?')[0] if '?' in DATABASE_URL else DATABASE_URL
        return await asyncpg.connect(clean_url, ssl='require')
    else:
        return await asyncpg.connect(DATABASE_URL)

async def fetch_incidents(
    min_evidence: int = 1,
    limit: int = 200,
    offset: int = 0,
    status: Optional[str] = None,
    country: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Fetch incidents from database"""
    try:
        conn = await get_connection()

        # Build query
        query = """
        SELECT i.id, i.title, i.narrative, i.occurred_at, i.first_seen_at, i.last_seen_at,
               i.asset_type, i.status, i.evidence_score, i.country,
               ST_Y(i.location::geometry) as lat,
               ST_X(i.location::geometry) as lon
        FROM public.incidents i
        WHERE i.evidence_score >= $1
        """
        params = [min_evidence]
        param_count = 1

        if status:
            param_count += 1
            query += f" AND i.status = ${param_count}"
            params.append(status)

        if country:
            param_count += 1
            query += f" AND i.country = ${param_count}"
            params.append(country)

        query += f" ORDER BY i.occurred_at DESC LIMIT ${param_count+1} OFFSET ${param_count+2}"
        params.extend([limit, offset])

        # Execute query
        rows = await conn.fetch(query, *params)

        # Format results
        incidents = []
        for row in rows:
            incidents.append({
                "id": str(row["id"]),
                "title": row["title"],
                "narrative": row["narrative"],
                "occurred_at": row["occurred_at"].isoformat() if row["occurred_at"] else None,
                "first_seen_at": row["first_seen_at"].isoformat() if row["first_seen_at"] else None,
                "last_seen_at": row["last_seen_at"].isoformat() if row["last_seen_at"] else None,
                "asset_type": row["asset_type"],
                "status": row["status"],
                "evidence_score": row["evidence_score"],
                "country": row["country"],
                "lat": float(row["lat"]) if row["lat"] else None,
                "lon": float(row["lon"]) if row["lon"] else None,
                "sources": []
            })

        await conn.close()
        return incidents

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()