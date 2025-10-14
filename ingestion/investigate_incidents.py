#!/usr/bin/env python3
"""
Database investigation script to analyze incident distribution.
Connects to production database to diagnose why only Danish incidents are showing.
"""
import os
import sys
import asyncio
import asyncpg
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def get_db_connection() -> asyncpg.Connection:
    """Get database connection using direct connection (port 5432) for queries."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")

    # Use port 5432 for direct queries (not 6543 pooler)
    # Replace port if needed
    if ':6543' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace(':6543', ':5432')
        print(f"Using port 5432 for direct queries")

    # Remove query parameters for clean connection
    clean_url = DATABASE_URL.split('?')[0] if '?' in DATABASE_URL else DATABASE_URL

    return await asyncpg.connect(clean_url, ssl='require')


async def investigate_incidents():
    """Run diagnostic queries to understand incident distribution."""

    print("=" * 80)
    print("DRONEWATCH DATABASE INVESTIGATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    print()

    conn = await get_db_connection()

    try:
        # Query 1: Incidents per country
        print("1. INCIDENTS PER COUNTRY")
        print("-" * 80)
        rows = await conn.fetch("""
            SELECT country, COUNT(*) as count
            FROM incidents
            GROUP BY country
            ORDER BY count DESC
        """)

        total_incidents = sum(row['count'] for row in rows)
        for row in rows:
            percentage = (row['count'] / total_incidents * 100) if total_incidents > 0 else 0
            print(f"  {row['country']}: {row['count']:3d} incidents ({percentage:5.1f}%)")
        print(f"\n  TOTAL: {total_incidents} incidents")
        print()

        # Query 2: Source distribution
        print("2. TOP 30 SOURCES (by incident count)")
        print("-" * 80)
        rows = await conn.fetch("""
            SELECT source_name, COUNT(*) as count
            FROM incident_sources
            GROUP BY source_name
            ORDER BY count DESC
            LIMIT 30
        """)

        for i, row in enumerate(rows, 1):
            print(f"  {i:2d}. {row['source_name']:<40s}: {row['count']:3d} incidents")
        print()

        # Query 3: European incidents check
        print("3. EUROPEAN INCIDENTS (NO, SE, FI, PL)")
        print("-" * 80)
        rows = await conn.fetch("""
            SELECT
                title,
                country,
                incident_date,
                ST_Y(location::geometry) as lat,
                ST_X(location::geometry) as lon
            FROM incidents
            WHERE country IN ('NO', 'SE', 'FI', 'PL')
            ORDER BY incident_date DESC
            LIMIT 20
        """)

        if rows:
            for row in rows:
                print(f"  [{row['country']}] {row['incident_date'].date()} - {row['title'][:60]}")
                print(f"      Location: {row['lat']:.4f}, {row['lon']:.4f}")
        else:
            print("  NO INCIDENTS FOUND for Norway, Sweden, Finland, Poland")
        print()

        # Query 4: Date range by country
        print("4. DATE RANGE BY COUNTRY")
        print("-" * 80)
        rows = await conn.fetch("""
            SELECT
                country,
                MIN(incident_date) as earliest,
                MAX(incident_date) as latest,
                COUNT(*) as count,
                EXTRACT(EPOCH FROM (MAX(incident_date) - MIN(incident_date)))/86400 as days_span
            FROM incidents
            GROUP BY country
            ORDER BY count DESC
        """)

        for row in rows:
            print(f"  {row['country']}:")
            print(f"    Earliest: {row['earliest'].date() if row['earliest'] else 'N/A'}")
            print(f"    Latest:   {row['latest'].date() if row['latest'] else 'N/A'}")
            print(f"    Count:    {row['count']}")
            print(f"    Span:     {row['days_span']:.1f} days" if row['days_span'] else "    Span: N/A")
        print()

        # Query 5: Recent incidents (last 7 days) by country
        print("5. RECENT INCIDENTS (Last 7 Days)")
        print("-" * 80)
        rows = await conn.fetch("""
            SELECT
                country,
                COUNT(*) as count
            FROM incidents
            WHERE incident_date >= NOW() - INTERVAL '7 days'
            GROUP BY country
            ORDER BY count DESC
        """)

        if rows:
            for row in rows:
                print(f"  {row['country']}: {row['count']} incidents")
        else:
            print("  NO INCIDENTS in last 7 days")
        print()

        # Query 6: Source verification (which sources have data)
        print("6. ACTIVE SOURCES (with incidents)")
        print("-" * 80)
        rows = await conn.fetch("""
            SELECT
                source_name,
                source_type,
                COUNT(*) as incident_count,
                MIN(i.incident_date) as earliest,
                MAX(i.incident_date) as latest
            FROM incident_sources s
            JOIN incidents i ON s.incident_id = i.id
            GROUP BY source_name, source_type
            ORDER BY incident_count DESC
            LIMIT 20
        """)

        for row in rows:
            print(f"  {row['source_name']:<40s} [{row['source_type']}]")
            print(f"    Incidents: {row['incident_count']}, Range: {row['earliest'].date()} to {row['latest'].date()}")
        print()

        # Query 7: Geographic bounds check
        print("7. GEOGRAPHIC BOUNDS")
        print("-" * 80)
        rows = await conn.fetch("""
            SELECT
                MIN(ST_Y(location::geometry)) as min_lat,
                MAX(ST_Y(location::geometry)) as max_lat,
                MIN(ST_X(location::geometry)) as min_lon,
                MAX(ST_X(location::geometry)) as max_lon,
                COUNT(*) as total_incidents
            FROM incidents
        """)

        row = rows[0]
        print(f"  Latitude:  {row['min_lat']:.4f} to {row['max_lat']:.4f}")
        print(f"  Longitude: {row['min_lon']:.4f} to {row['max_lon']:.4f}")
        print(f"  Total incidents: {row['total_incidents']}")
        print()

        # Expected European bounds: 35-71°N, -10-31°E
        print("  Expected European bounds: 35-71°N, -10-31°E")
        if row['min_lat'] < 35 or row['max_lat'] > 71:
            print("  ⚠️  WARNING: Latitude out of expected European range")
        if row['min_lon'] < -10 or row['max_lon'] > 31:
            print("  ⚠️  WARNING: Longitude out of expected European range")
        print()

        # Query 8: Evidence score distribution
        print("8. EVIDENCE SCORE DISTRIBUTION")
        print("-" * 80)
        rows = await conn.fetch("""
            SELECT
                evidence_score,
                COUNT(*) as count
            FROM incidents
            GROUP BY evidence_score
            ORDER BY evidence_score DESC
        """)

        for row in rows:
            score_label = {4: "OFFICIAL", 3: "VERIFIED", 2: "REPORTED", 1: "UNCONFIRMED"}.get(row['evidence_score'], "UNKNOWN")
            print(f"  Score {row['evidence_score']} ({score_label}): {row['count']} incidents")
        print()

    finally:
        await conn.close()

    print("=" * 80)
    print("INVESTIGATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(investigate_incidents())
