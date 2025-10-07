"""
Shared database utilities for Vercel serverless functions
Optimized for Supabase transaction pooling and serverless environments
"""
import os
import asyncpg
import asyncio
from typing import Optional, Dict, Any, List
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_connection():
    """
    Get database connection optimized for serverless with Supabase pooler.
    Uses transaction mode pooling for better serverless performance.
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not configured")

    # Parse and optimize connection string for serverless
    connection_params = {}

    # For Supabase, ensure we're using the pooler endpoint for serverless
    if 'supabase.co' in DATABASE_URL or 'supabase.com' in DATABASE_URL:
        # Remove query parameters
        clean_url = DATABASE_URL.split('?')[0] if '?' in DATABASE_URL else DATABASE_URL

        # Check if using pooler endpoint (port 6543 for transaction mode)
        if ':6543' in clean_url or 'pooler.supabase.com' in clean_url:
            # Transaction mode pooler - optimal for serverless
            logger.info("Using Supabase transaction mode pooler")
            connection_params['command_timeout'] = 10
            connection_params['server_settings'] = {
                'jit': 'off'  # Disable JIT for faster cold starts
            }
            # Disable prepared statements for transaction mode
            connection_params['statement_cache_size'] = 0

        # Always use SSL with Supabase
        connection_params['ssl'] = 'require'

        return await asyncpg.connect(clean_url, **connection_params)
    else:
        # Non-Supabase connections
        return await asyncpg.connect(DATABASE_URL, **connection_params)

async def fetch_incidents(
    min_evidence: int = 1,
    limit: int = 200,
    offset: int = 0,
    status: Optional[str] = None,
    country: Optional[str] = None,
    asset_type: Optional[str] = None,
    since: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch incidents from database with retry logic for serverless environments.
    Optimized for Vercel Functions with connection pooling.
    """
    max_retries = 2
    retry_delay = 0.5

    for attempt in range(max_retries + 1):
        conn = None
        try:
            conn = await get_connection()

            # Build query with proper parameterization
            # IMPORTANT: Only show verified or auto-verified incidents to public
            # Sources optimized with LEFT JOIN (migration 015 adds indexes for performance)
            query = """
            WITH incident_sources_agg AS (
                SELECT
                    is2.incident_id,
                    json_agg(json_build_object(
                        'source_url', is2.source_url,
                        'source_type', COALESCE(s.source_type, 'unknown'),
                        'source_name', COALESCE(s.name, 'Unknown'),
                        'source_title', is2.source_title,
                        'source_quote', is2.source_quote,
                        'published_at', is2.published_at
                    )) as sources
                FROM public.incident_sources is2
                LEFT JOIN public.sources s ON is2.source_id = s.id
                GROUP BY is2.incident_id
            )
            SELECT i.id, i.title, i.narrative, i.occurred_at, i.first_seen_at, i.last_seen_at,
                   i.asset_type, i.status, i.evidence_score, i.country,
                   ST_Y(i.location::geometry) as lat,
                   ST_X(i.location::geometry) as lon,
                   COALESCE(isa.sources, '[]'::json) as sources
            FROM public.incidents i
            LEFT JOIN incident_sources_agg isa ON i.id = isa.incident_id
            WHERE i.evidence_score >= $1
              AND (i.verification_status IN ('verified', 'auto_verified', 'pending')
                   OR i.verification_status IS NULL)
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

            if asset_type:
                param_count += 1
                query += f" AND i.asset_type = ${param_count}"
                params.append(asset_type)

            if since:
                param_count += 1
                query += f" AND i.occurred_at >= ${param_count}"
                params.append(since)

            query += f" ORDER BY i.occurred_at DESC LIMIT ${param_count+1} OFFSET ${param_count+2}"
            params.extend([limit, offset])

            # Execute query with timeout
            rows = await asyncio.wait_for(
                conn.fetch(query, *params),
                timeout=9.0  # Vercel function timeout buffer
            )

            # Format results
            incidents = []
            for row in rows:
                # Handle sources - could be JSON object, string, or None
                sources = row.get("sources")
                if sources:
                    # If it's a string, parse it as JSON
                    if isinstance(sources, str):
                        import json
                        try:
                            sources = json.loads(sources) if sources != "[]" else []
                        except:
                            sources = []
                    # If it's already a list, use it
                    elif isinstance(sources, list):
                        sources = sources
                    else:
                        sources = []
                else:
                    sources = []

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
                    "sources": sources
                })

            return incidents

        except asyncio.TimeoutError:
            logger.error(f"Query timeout on attempt {attempt + 1}")
            if attempt < max_retries:
                await asyncio.sleep(retry_delay)
                continue
            return {"error": "Query timeout", "type": "TimeoutError"}

        except (OSError, asyncpg.exceptions.PostgresError) as e:
            logger.error(f"Database error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries and "Cannot assign requested address" in str(e):
                # Common serverless cold start issue
                await asyncio.sleep(retry_delay)
                continue
            return {"error": str(e), "type": type(e).__name__}

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"error": str(e), "type": type(e).__name__}

        finally:
            if conn:
                try:
                    await conn.close()
                except:
                    pass  # Ignore close errors

def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()