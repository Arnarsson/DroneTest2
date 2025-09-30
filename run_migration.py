#!/usr/bin/env python3
"""
Run database migration to set verification_status for existing incidents
"""
import asyncio
import asyncpg
import os
import sys

async def run_migration():
    """Run the migration"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Please set it in GitHub secrets or provide it")
        sys.exit(1)

    print(f"Connecting to database...")

    # Connect to database
    if 'supabase.co' in DATABASE_URL or 'supabase.com' in DATABASE_URL:
        clean_url = DATABASE_URL.split('?')[0] if '?' in DATABASE_URL else DATABASE_URL
        conn = await asyncpg.connect(clean_url, ssl='require', statement_cache_size=0)
    else:
        conn = await asyncpg.connect(DATABASE_URL)

    print("Connected successfully!")

    # Check current state
    print("\n📊 Current verification_status distribution:")
    rows = await conn.fetch("""
        SELECT
            COALESCE(verification_status, 'NULL') as status,
            COUNT(*) as count
        FROM public.incidents
        GROUP BY verification_status
        ORDER BY count DESC
    """)

    for row in rows:
        print(f"  {row['status']}: {row['count']}")

    # Run migration
    print("\n🔄 Updating incidents with NULL verification_status to 'pending'...")
    result = await conn.execute("""
        UPDATE public.incidents
        SET verification_status = 'pending'
        WHERE verification_status IS NULL
    """)

    print(f"✅ Updated {result.split()[-1]} incidents")

    # Check new state
    print("\n📊 New verification_status distribution:")
    rows = await conn.fetch("""
        SELECT
            COALESCE(verification_status, 'NULL') as status,
            COUNT(*) as count
        FROM public.incidents
        GROUP BY verification_status
        ORDER BY count DESC
    """)

    for row in rows:
        print(f"  {row['status']}: {row['count']}")

    await conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_migration())
