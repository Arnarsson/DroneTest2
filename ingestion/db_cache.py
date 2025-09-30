"""
Database-backed cache for scraper deduplication
Replaces file-based processed_incidents.json
"""
import os
import asyncio
import asyncpg
import logging
from typing import Set, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ScraperCache:
    """Database-backed cache for tracking processed incidents"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            logger.warning("DATABASE_URL not set, cache will not persist")
            self._memory_cache = set()
            self._use_db = False
        else:
            self._memory_cache = None
            self._use_db = True

    async def _get_connection(self):
        """Get database connection"""
        if 'supabase.co' in self.database_url or 'supabase.com' in self.database_url:
            clean_url = self.database_url.split('?')[0] if '?' in self.database_url else self.database_url
            return await asyncpg.connect(clean_url, ssl='require', statement_cache_size=0)
        else:
            return await asyncpg.connect(self.database_url)

    async def load(self) -> Set[str]:
        """Load processed incident hashes from database"""
        if not self._use_db:
            logger.info("Using in-memory cache (DATABASE_URL not configured)")
            return self._memory_cache

        try:
            conn = await self._get_connection()
            try:
                # Load hashes from last 30 days
                query = """
                SELECT incident_hash
                FROM public.scraper_cache
                WHERE processed_at > NOW() - INTERVAL '30 days'
                """
                rows = await conn.fetch(query)
                hashes = {row['incident_hash'] for row in rows}
                logger.info(f"Loaded {len(hashes)} cached incident hashes from database")
                return hashes
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"Failed to load cache from database: {e}")
            logger.warning("Falling back to in-memory cache")
            self._memory_cache = set()
            self._use_db = False
            return self._memory_cache

    async def add(self, incident_hash: str, title: str, occurred_at: datetime, source_name: str):
        """Add incident hash to cache"""
        if not self._use_db:
            self._memory_cache.add(incident_hash)
            return

        try:
            conn = await self._get_connection()
            try:
                query = """
                INSERT INTO public.scraper_cache (incident_hash, title, occurred_at, source_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (incident_hash) DO UPDATE
                SET processed_at = NOW()
                """
                await conn.execute(query, incident_hash, title[:500], occurred_at, source_name[:200])
                logger.debug(f"Added hash {incident_hash} to cache")
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"Failed to add hash to cache: {e}")

    async def cleanup(self):
        """Remove old cache entries"""
        if not self._use_db:
            return

        try:
            conn = await self._get_connection()
            try:
                result = await conn.execute("SELECT public.cleanup_old_scraper_cache()")
                logger.info("Cleaned up old cache entries")
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")

    def load_sync(self) -> Set[str]:
        """Synchronous wrapper for load()"""
        return asyncio.run(self.load())

    def add_sync(self, incident_hash: str, title: str, occurred_at: datetime, source_name: str):
        """Synchronous wrapper for add()"""
        asyncio.run(self.add(incident_hash, title, occurred_at, source_name))


class ScraperMetrics:
    """Track scraper performance metrics"""

    def __init__(self, scraper_type: str, source_key: str, source_name: str):
        self.scraper_type = scraper_type
        self.source_key = source_key
        self.source_name = source_name
        self.incidents_found = 0
        self.incidents_ingested = 0
        self.incidents_skipped = 0
        self.errors = 0
        self.error_message = None
        self.started_at = datetime.now()
        self.completed_at = None
        self.database_url = os.getenv("DATABASE_URL")

    async def _get_connection(self):
        """Get database connection"""
        if 'supabase.co' in self.database_url or 'supabase.com' in self.database_url:
            clean_url = self.database_url.split('?')[0] if '?' in self.database_url else self.database_url
            return await asyncpg.connect(clean_url, ssl='require', statement_cache_size=0)
        else:
            return await asyncpg.connect(self.database_url)

    async def save(self):
        """Save metrics to database"""
        if not self.database_url:
            logger.debug("Skipping metrics save (DATABASE_URL not configured)")
            return

        self.completed_at = datetime.now()
        execution_time_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)

        try:
            conn = await self._get_connection()
            try:
                query = """
                INSERT INTO public.scraper_metrics
                (scraper_type, source_key, source_name, incidents_found, incidents_ingested,
                 incidents_skipped, errors, error_message, execution_time_ms, started_at, completed_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """
                await conn.execute(
                    query,
                    self.scraper_type, self.source_key, self.source_name[:200],
                    self.incidents_found, self.incidents_ingested, self.incidents_skipped,
                    self.errors, self.error_message[:1000] if self.error_message else None,
                    execution_time_ms, self.started_at, self.completed_at
                )
                logger.debug(f"Saved metrics for {self.source_key}")
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def save_sync(self):
        """Synchronous wrapper for save()"""
        asyncio.run(self.save())