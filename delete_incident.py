#!/usr/bin/env python3
"""Delete specific non-incident from database"""

import os
import asyncio
import asyncpg

async def delete_incident():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not set")
        return

    # Convert pooler to direct connection
    if ':6543' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace(':6543', ':5432')

    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Delete the regulatory news incident
        incident_id = '61536178-b3db-47e6-9b58-69e5d48cfca9'

        # First delete related sources
        await conn.execute("""
            DELETE FROM incident_sources WHERE incident_id = $1
        """, incident_id)

        # Then delete the incident
        result = await conn.execute("""
            DELETE FROM incidents WHERE id = $1
        """, incident_id)

        print(f"✅ Deleted incident {incident_id}")
        print(f"   Title: 'Mange ministre kommer til byen - giver nyt droneforbud'")
        print(f"   Reason: Regulatory news, not an actual incident")

    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(delete_incident())
