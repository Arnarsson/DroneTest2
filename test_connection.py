#!/usr/bin/env python3
"""
Quick test script to verify PostgreSQL connection to self-hosted Supabase
"""
import asyncio
import asyncpg
import sys

async def test_connection():
    """Test database connection"""
    try:
        print("🔄 Connecting to PostgreSQL at 135.181.101.70:5432...")

        conn = await asyncpg.connect(
            host='135.181.101.70',
            port=5432,
            user='postgres',
            password='El54d9tlwzgmn7EH18K1vLfVXjKg5CCA',
            database='postgres',
            timeout=10
        )

        print("✅ Connection successful!\n")

        # Test query
        version = await conn.fetchval('SELECT version()')
        print(f"📊 PostgreSQL Version:\n{version}\n")

        # Check for DroneWatch tables
        tables = await conn.fetch("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename IN ('incidents', 'sources', 'incident_sources')
            ORDER BY tablename
        """)

        if tables:
            print("📋 DroneWatch Tables Found:")
            for row in tables:
                print(f"   ✓ {row['tablename']}")
        else:
            print("⚠️  No DroneWatch tables found. Schema needs to be applied.")

        # Check PostGIS
        try:
            postgis_version = await conn.fetchval('SELECT PostGIS_version()')
            print(f"\n🗺️  PostGIS Version: {postgis_version}")
        except Exception as e:
            print(f"\n⚠️  PostGIS not found: {e}")

        await conn.close()
        print("\n✅ All tests passed!")
        return True

    except asyncio.TimeoutError:
        print("❌ Connection timeout! Possible issues:")
        print("   1. Port 5432 is not exposed externally")
        print("   2. Firewall is blocking the connection")
        print("   3. PostgreSQL is not listening on 0.0.0.0")
        print("\n💡 Try port 6543 (transaction pooler) instead:")
        print("   DATABASE_URL=postgresql://postgres:...@135.181.101.70:6543/postgres")
        return False

    except asyncpg.exceptions.InvalidPasswordError:
        print("❌ Authentication failed! Check password.")
        return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
