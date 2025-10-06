#!/usr/bin/env python3
import asyncio
import asyncpg

HOST = '135.181.101.70'
PORT = 5432
DATABASE = 'postgres'

# Try different user/password combinations
CONFIGS = [
    {'user': 'postgres', 'password': 'El54d9tlwzgmn7EH18K1vLfVXjKg5CCA'},
    {'user': 'postgres', 'password': 'postgres'},
    {'user': 'supabase', 'password': 'El54d9tlwzgmn7EH18K1vLfVXjKg5CCA'},
    {'user': 'supabase_admin', 'password': 'El54d9tlwzgmn7EH18K1vLfVXjKg5CCA'},
    {'user': 'authenticator', 'password': 'El54d9tlwzgmn7EH18K1vLfVXjKg5CCA'},
]

async def test_config(config):
    try:
        conn = await asyncpg.connect(
            host=HOST,
            port=PORT,
            user=config['user'],
            password=config['password'],
            database=DATABASE,
            timeout=5
        )
        version = await conn.fetchval('SELECT version()')
        await conn.close()
        print(f"✅ SUCCESS: user={config['user']}")
        print(f"   Connection string: postgresql://{config['user']}:***@{HOST}:{PORT}/{DATABASE}")
        return config
    except asyncpg.exceptions.InvalidPasswordError:
        print(f"❌ AUTH FAILED: user={config['user']}")
    except asyncpg.exceptions.InvalidCatalogNameError:
        print(f"❌ DATABASE NOT FOUND: user={config['user']}")
    except Exception as e:
        print(f"❌ ERROR: user={config['user']} - {e}")
    return None

async def main():
    print("Testing PostgreSQL connection variations...")
    print("=" * 60)
    
    for config in CONFIGS:
        result = await test_config(config)
        if result:
            print("\n🎯 WORKING CONFIGURATION FOUND!")
            print(f"Update Vercel DATABASE_URL to:")
            print(f"postgresql://{result['user']}:{result['password']}@{HOST}:{PORT}/{DATABASE}")
            return
        print()
    
    print("❌ No working configuration found.")
    print("\nYou need to:")
    print("1. Check PostgreSQL logs on your server")
    print("2. Verify pg_hba.conf allows external MD5 auth")
    print("3. Check Docker Compose for actual POSTGRES_PASSWORD")

asyncio.run(main())
