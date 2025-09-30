#!/usr/bin/env python3
"""
Remove duplicate incidents from the database.
Keeps the incident with the longest narrative for each location/date.
"""

import os
import asyncio
import asyncpg
from collections import defaultdict

DATABASE_URL = os.getenv("DATABASE_URL")

# Duplicates to remove (keep first ID, delete others)
DUPLICATES = {
    # Copenhagen Airport - keep most detailed
    "keep": "0e7a4198-4e93-4cf7-ad2e-9b464b0f7813",
    "delete": ["1f6ce124-f791-49d0-aca5-ffc44deaa4b3", "778ed6dd-562b-424d-a933-f7efd8119e18", "942427f5-5cf3-48d1-b6dc-575de24609ae"],

    # Amsterdam Schiphol - keep detailed version
    "keep": "5028062c-78c7-4c6c-a131-67e58fe9f23f",
    "delete": ["9af27eab-ac7a-4049-859b-ed6c11fbac5f"],

    # Billund - keep detailed
    "keep": "6bd476b0-2ca9-4f8d-a4bf-f6d84dc03989",
    "delete": ["a2e23251-80e3-4ab8-b957-4e457d66fb3d"],

    # Skrydstrup - keep detailed
    "keep": "4d16637c-ee52-42a1-986e-03ead51fd37f",
    "delete": ["558b7fd3-dc39-487d-8b18-394adb036896"],

    # Sønderborg - keep detailed
    "keep": "beb3df14-af7d-4184-b96f-1c792a2322f8",
    "delete": ["e0dd6b30-1c5c-4c55-b1b0-1d7fc348c6d2"],

    # Esbjerg - keep detailed
    "keep": "73e367aa-8c31-4de3-950e-1a4077bebb6a",
    "delete": ["5d21e17a-9cf5-4b79-ac0d-2b867da7ab2c"],

    # Aalborg - keep detailed
    "keep": "df02e3be-851e-412c-9969-fda497ffaa70",
    "delete": ["914083f9-78db-44e0-915e-225035c0a5b7"],

    # Oslo - keep detailed
    "keep": "e47623c6-5d90-4190-bce2-af1b99786cc5",
    "delete": ["24d0fc9c-2436-4260-ae02-07d519822256"],

    # Warsaw - keep most detailed
    "keep": "44c7bdbe-2baf-4654-9a15-371d0732739a",
    "delete": ["b340b296-1bdb-4954-866f-19525fd8b2c9"],
}

# Karup has 2 different dates so keep both
# Manual Test entries can be deleted
DELETE_TEST_ENTRIES = [
    "40a1bfad-791a-4d15-9fec-3760a82401b8",  # Manual Test 2
    "e7dfa442-3810-4537-8a36-4183e215fef0",  # Test Copenhagen Airport Drone Sighting
]

async def cleanup_duplicates():
    """Remove duplicate incidents from database"""

    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not set")
        return

    # Use pooler for serverless
    clean_url = DATABASE_URL.split('?')[0] if '?' in DATABASE_URL else DATABASE_URL

    conn = await asyncpg.connect(
        clean_url,
        ssl='require',
        statement_cache_size=0
    )

    try:
        all_deletes = DUPLICATES["delete"] + DELETE_TEST_ENTRIES

        print(f"Removing {len(all_deletes)} duplicate/test incidents...")
        print(f"Keeping: {DUPLICATES['keep']}\n")

        for incident_id in all_deletes:
            # Get title first
            title = await conn.fetchval(
                "SELECT title FROM public.incidents WHERE id = $1",
                incident_id
            )

            if title:
                print(f"Deleting: {title[:50]} (ID: {incident_id[:8]})")
                await conn.execute(
                    "DELETE FROM public.incidents WHERE id = $1",
                    incident_id
                )
            else:
                print(f"Not found: {incident_id[:8]}")

        # Count remaining
        count = await conn.fetchval("SELECT COUNT(*) FROM public.incidents")
        print(f"\n✅ Cleanup complete! Remaining incidents: {count}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())