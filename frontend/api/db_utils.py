"""
Shared database connection utilities for serverless and ingestion services.
Optimized for Supabase transaction pooling and serverless environments.

This module provides centralized database connection logic to avoid duplication
across the codebase. Used by both API endpoints and ingestion scrapers.
"""
import os
import asyncpg
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)


async def get_connection() -> asyncpg.Connection:
    """
    Get database connection optimized for serverless with Supabase pooler.
    Uses transaction mode pooling for better serverless performance.

    Connection parameters:
    - For Supabase pooler (port 6543): Optimized for transaction mode
      - command_timeout: 10 seconds
      - jit: off (faster cold starts)
      - statement_cache_size: 0 (required for transaction pooling)
    - SSL required for Supabase connections

    Returns:
        asyncpg.Connection: Database connection ready for queries

    Raises:
        ValueError: If DATABASE_URL environment variable is not set
        asyncpg.exceptions.PostgresError: If connection fails

    Example:
        >>> conn = await get_connection()
        >>> try:
        >>>     rows = await conn.fetch("SELECT * FROM incidents")
        >>> finally:
        >>>     await conn.close()
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        error_msg = (
            "DATABASE_URL environment variable not configured. "
            "Set it in Vercel: Settings → Environment Variables"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Validate DATABASE_URL format
    if not DATABASE_URL.startswith(('postgresql://', 'postgres://')):
        error_msg = (
            f"Invalid DATABASE_URL format. Expected postgresql:// or postgres://, "
            f"got: {DATABASE_URL[:20]}..."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Parse and optimize connection string for serverless
    connection_params: Dict[str, Any] = {}

    # For Supabase, ensure we're using the pooler endpoint for serverless
    if 'supabase.co' in DATABASE_URL or 'supabase.com' in DATABASE_URL:
        # Remove query parameters for clean connection
        clean_url = DATABASE_URL.split('?')[0] if '?' in DATABASE_URL else DATABASE_URL

        # Log connection (without password) for debugging
        safe_url = clean_url.split('@')[1] if '@' in clean_url else clean_url
        logger.debug(f"Connecting to Supabase: {safe_url}")

        # Check if using pooler endpoint (port 6543 for transaction mode)
        if ':6543' in clean_url or 'pooler.supabase.com' in clean_url:
            # Transaction mode pooler - optimal for serverless
            logger.info("Using Supabase transaction mode pooler")
            connection_params['command_timeout'] = 10
            connection_params['server_settings'] = {
                'jit': 'off'  # Disable JIT compilation for faster cold starts
            }
            # Disable prepared statements for transaction mode
            # (required by Supabase transaction pooler)
            connection_params['statement_cache_size'] = 0

        # Always use SSL with Supabase
        connection_params['ssl'] = 'require'

        return await asyncpg.connect(clean_url, **connection_params)
    else:
        # Non-Supabase connections - use default settings
        logger.debug("Using non-Supabase database connection")
        return await asyncpg.connect(DATABASE_URL, **connection_params)
