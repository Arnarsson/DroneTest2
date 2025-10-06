#!/usr/bin/env python3
"""
Test multiple PostgreSQL connection configurations
"""
import asyncio
import asyncpg
import sys

# From your .env file
PASSWORD = 'El54d9tlwzgmn7EH18K1vLfVXjKg5CCA'
HOST = '135.181.101.70'

# Test configurations
CONFIGS = [
    {
        'name': 'Port 5432 - postgres user',
        'host': HOST,
        'port': 5432,
        'user': 'postgres',
        'password': PASSWORD,
        'database': 'postgres'
    },
    {
        'name': 'Port 6543 (pooler) - postgres user',
        'host': HOST,
        'port': 6543,
        'user': 'postgres',
        'password': PASSWORD,
        'database': 'postgres'
    },
    {
        'name': 'Port 5432 - supabase user',
        'host': HOST,
        'port': 5432,
        'user': 'supabase',
        'password': PASSWORD,
        'database': 'postgres'
    },
    {
        'name': 'Port 54322 (alternative) - postgres user',
        'host': HOST,
        'port': 54322,
        'user': 'postgres',
        'password': PASSWORD,
        'database': 'postgres'
    }
]

async def test_config(config):
    """Test a single configuration"""
    try:
        print(f"🔄 Testing: {config['name']}...")

        conn = await asyncpg.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            timeout=5
        )

        version = await conn.fetchval('SELECT version()')
        await conn.close()

        print(f"✅ SUCCESS! {config['name']}")
        print(f"   Connection string: postgresql://{config['user']}:***@{config['host']}:{config['port']}/{config['database']}")
        print(f"   Version: {version[:50]}...\n")
        return config

    except asyncio.TimeoutError:
        print(f"⏱️  TIMEOUT: {config['name']} (port probably not exposed)\n")
        return None
    except asyncpg.exceptions.InvalidPasswordError:
        print(f"🔑 AUTH FAILED: {config['name']} (wrong user/password)\n")
        return None
    except Exception as e:
        print(f"❌ FAILED: {config['name']} - {e}\n")
        return None

async def main():
    print("=" * 60)
    print("Testing PostgreSQL Connection Configurations")
    print("=" * 60)
    print(f"Host: {HOST}")
    print(f"Password: {PASSWORD[:10]}...")
    print("=" * 60)
    print()

    results = []
    for config in CONFIGS:
        result = await test_config(config)
        if result:
            results.append(result)

    print("=" * 60)
    if results:
        print(f"✅ Found {len(results)} working configuration(s)!")
        print("\n🎯 Recommended DATABASE_URL:")
        best = results[0]
        print(f"postgresql://{best['user']}:{best['password']}@{best['host']}:{best['port']}/{best['database']}")
    else:
        print("❌ No working configurations found!")
        print("\n💡 Possible issues:")
        print("1. PostgreSQL ports (5432, 6543, 54322) not exposed externally")
        print("2. Firewall blocking connections")
        print("3. PostgreSQL not configured to accept remote connections")
        print("4. Wrong password or username")
        print("\n🔍 Check your Supabase Docker Compose configuration:")
        print("   - Look for port mappings in docker-compose.yml")
        print("   - Verify POSTGRES_PASSWORD matches")
        print("   - Check if PostgreSQL is bound to 0.0.0.0")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
