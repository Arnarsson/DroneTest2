#!/usr/bin/env python3
"""Test Supabase database connection"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

async def test_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env")
        return False

    print(f"📡 Connecting to Supabase...")
    print(f"   Project: uhwsuaebakkdmdogzrrz")

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.connect() as conn:
            # Test basic connection
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL: {version[:30]}...")

            # Check PostGIS
            result = await conn.execute(text("SELECT PostGIS_version()"))
            postgis = result.scalar()
            print(f"✅ PostGIS enabled: {postgis}")

            # Check tables
            result = await conn.execute(text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename IN ('incidents', 'sources', 'assets')
                ORDER BY tablename
            """))
            tables = [row[0] for row in result]

            if tables:
                print(f"✅ Tables found: {', '.join(tables)}")
            else:
                print("⚠️  Tables not created yet - run sql/supabase_schema.sql")

            # Check RLS
            result = await conn.execute(text("""
                SELECT tablename, rowsecurity
                FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename = 'incidents'
            """))
            rls_check = result.first()
            if rls_check and rls_check[1]:
                print("✅ RLS enabled on incidents table")
            else:
                print("⚠️  RLS not enabled - security risk!")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())