"""
Find and report duplicate incidents in the database.
Helps identify why duplicates are appearing.
"""
import asyncio
import asyncpg
import os
import sys
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_connection, run_async


async def find_duplicates():
    """
    Find duplicate incidents using multiple strategies:
    1. Same location + same day
    2. Same source URL (should never happen)
    3. Same title + location
    """
    conn = await get_connection()
    
    results = {
        'by_location_date': [],
        'by_source_url': [],
        'by_title_location': [],
        'summary': {}
    }
    
    try:
        # Strategy 1: Same location (within 1km) + same day
        location_duplicates = await conn.fetch("""
            SELECT 
                DATE(occurred_at) as event_date,
                ROUND(ST_Y(location::geometry)::numeric, 3) as lat,
                ROUND(ST_X(location::geometry)::numeric, 3) as lon,
                COUNT(*) as duplicate_count,
                array_agg(id::text) as incident_ids,
                array_agg(title) as titles
            FROM public.incidents
            WHERE location IS NOT NULL
            GROUP BY 
                DATE(occurred_at),
                ROUND(ST_Y(location::geometry)::numeric, 3),
                ROUND(ST_X(location::geometry)::numeric, 3)
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC
        """)
        
        results['by_location_date'] = [
            {
                'date': str(row['event_date']),
                'location': f"{row['lat']}, {row['lon']}",
                'count': row['duplicate_count'],
                'incident_ids': row['incident_ids'],
                'titles': row['titles']
            }
            for row in location_duplicates
        ]
        
        # Strategy 2: Same source URL (should never happen due to unique constraint)
        source_duplicates = await conn.fetch("""
            SELECT 
                source_url,
                COUNT(DISTINCT incident_id) as incident_count,
                array_agg(DISTINCT incident_id::text) as incident_ids
            FROM public.incident_sources
            GROUP BY source_url
            HAVING COUNT(DISTINCT incident_id) > 1
            ORDER BY incident_count DESC
        """)
        
        results['by_source_url'] = [
            {
                'source_url': row['source_url'],
                'incident_count': row['incident_count'],
                'incident_ids': row['incident_ids']
            }
            for row in source_duplicates
        ]
        
        # Strategy 3: Same title + same location (within 500m)
        title_location_duplicates = await conn.fetch("""
            SELECT 
                i1.id as id1,
                i2.id as id2,
                i1.title,
                ST_Distance(
                    i1.location::geography,
                    i2.location::geography
                ) as distance_meters
            FROM public.incidents i1
            JOIN public.incidents i2 ON (
                i1.title = i2.title
                AND i1.id < i2.id
                AND ST_DWithin(
                    i1.location::geography,
                    i2.location::geography,
                    500  -- 500 meters
                )
            )
            ORDER BY distance_meters ASC
        """)
        
        results['by_title_location'] = [
            {
                'id1': str(row['id1']),
                'id2': str(row['id2']),
                'title': row['title'],
                'distance_meters': float(row['distance_meters'])
            }
            for row in title_location_duplicates
        ]
        
        # Summary
        results['summary'] = {
            'total_incidents': await conn.fetchval("SELECT COUNT(*) FROM public.incidents"),
            'location_date_duplicates': len(results['by_location_date']),
            'source_url_duplicates': len(results['by_source_url']),
            'title_location_duplicates': len(results['by_title_location']),
            'total_duplicate_groups': len(results['by_location_date']) + len(results['by_source_url']) + len(results['by_title_location'])
        }
        
    finally:
        await conn.close()
    
    return results


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Check authorization
        import secrets
        expected_token = os.getenv('INGEST_TOKEN')
        if not expected_token:
            self.send_error(500, "INGEST_TOKEN not set")
            return
        
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self.send_error(401, "Missing Bearer token")
            return
        
        token = auth_header.replace('Bearer ', '')
        if not secrets.compare_digest(token, expected_token):
            self.send_error(403, "Invalid token")
            return
        
        # Find duplicates
        result = run_async(find_duplicates())
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2, default=str).encode())

