"""
Distributed rate limiter using Upstash Redis for serverless environments.
Uses sliding window algorithm to track request counts per IP across all instances.

Falls back to in-memory rate limiting when Upstash Redis is not configured.
"""
import os
import time
import logging
from collections import defaultdict
from typing import Dict, Tuple
import uuid

# Configure logging
logger = logging.getLogger(__name__)

# Rate limit configuration (can be overridden via environment variables)
RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', '60'))  # seconds
RATE_LIMIT_MAX_REQUESTS = int(os.environ.get('RATE_LIMIT_MAX_REQUESTS', '100'))

# Upstash Redis configuration
UPSTASH_REDIS_REST_URL = os.environ.get('UPSTASH_REDIS_REST_URL')
UPSTASH_REDIS_REST_TOKEN = os.environ.get('UPSTASH_REDIS_REST_TOKEN')

# Redis client (lazy initialized)
_redis_client = None
_redis_available = None  # None = not checked, True = available, False = unavailable

# In-memory fallback store
_fallback_store: Dict[str, list] = defaultdict(list)


def _get_redis_client():
    """
    Get or create Redis client. Returns None if Redis is not configured.
    Uses lazy initialization to avoid startup delays.
    """
    global _redis_client, _redis_available

    # If we already know Redis is unavailable, return None immediately
    if _redis_available is False:
        return None

    # If client already exists, return it
    if _redis_client is not None:
        return _redis_client

    # Check if Redis credentials are configured
    if not UPSTASH_REDIS_REST_URL or not UPSTASH_REDIS_REST_TOKEN:
        logger.warning(
            "Upstash Redis not configured (UPSTASH_REDIS_REST_URL or UPSTASH_REDIS_REST_TOKEN missing). "
            "Falling back to in-memory rate limiting."
        )
        _redis_available = False
        return None

    try:
        from upstash_redis import Redis
        _redis_client = Redis(
            url=UPSTASH_REDIS_REST_URL,
            token=UPSTASH_REDIS_REST_TOKEN
        )
        _redis_available = True
        logger.info("Upstash Redis client initialized successfully")
        return _redis_client
    except ImportError:
        logger.warning(
            "upstash-redis package not installed. Falling back to in-memory rate limiting."
        )
        _redis_available = False
        return None
    except Exception as e:
        logger.warning(
            f"Failed to initialize Upstash Redis client: {e}. "
            "Falling back to in-memory rate limiting."
        )
        _redis_available = False
        return None


def get_client_ip(headers: dict) -> str:
    """Extract client IP from headers, handling proxies."""
    # Check X-Forwarded-For (Vercel sets this)
    forwarded_for = headers.get('X-Forwarded-For', '')
    if forwarded_for:
        # Take the first IP (original client)
        return forwarded_for.split(',')[0].strip()

    # Fallback to X-Real-IP or Remote-Addr
    return headers.get('X-Real-IP') or headers.get('Remote-Addr', 'unknown')


def _check_rate_limit_redis(ip: str) -> Tuple[bool, int, int]:
    """
    Check rate limit using Redis sliding window algorithm.

    Uses a sorted set where:
    - Key: rate_limit:{ip}
    - Score: timestamp (milliseconds)
    - Value: unique request ID

    Returns:
        (allowed, remaining, reset_after)
    """
    redis = _get_redis_client()
    if redis is None:
        return _check_rate_limit_memory(ip)

    try:
        now_ms = int(time.time() * 1000)
        window_ms = RATE_LIMIT_WINDOW * 1000
        cutoff_ms = now_ms - window_ms

        key = f"rate_limit:{ip}"

        # Use a pipeline for atomic operations
        # 1. Remove old entries outside the window
        redis.zremrangebyscore(key, 0, cutoff_ms)

        # 2. Count current requests in window
        current_count = redis.zcard(key)

        if current_count >= RATE_LIMIT_MAX_REQUESTS:
            # Rate limit exceeded
            # Get the oldest entry to calculate reset time
            oldest_entries = redis.zrange(key, 0, 0, withscores=True)
            if oldest_entries:
                oldest_ts_ms = oldest_entries[0][1]
                reset_after = max(1, int((oldest_ts_ms + window_ms - now_ms) / 1000))
            else:
                reset_after = RATE_LIMIT_WINDOW
            return False, 0, reset_after

        # 3. Add new request with current timestamp as score
        request_id = f"{now_ms}:{uuid.uuid4().hex[:8]}"
        redis.zadd(key, {request_id: now_ms})

        # 4. Set expiry on the key to auto-cleanup
        redis.expire(key, RATE_LIMIT_WINDOW + 1)

        remaining = RATE_LIMIT_MAX_REQUESTS - current_count - 1
        reset_after = RATE_LIMIT_WINDOW

        return True, remaining, reset_after

    except Exception as e:
        # Fail open: if Redis has an error, allow the request
        logger.error(f"Redis rate limit check failed: {e}. Allowing request (fail-open).")
        return True, RATE_LIMIT_MAX_REQUESTS - 1, RATE_LIMIT_WINDOW


def _check_rate_limit_memory(ip: str) -> Tuple[bool, int, int]:
    """
    Fallback in-memory rate limiting using sliding window.

    Returns:
        (allowed, remaining, reset_after)
    """
    now = time.time()

    # Clean old entries (older than window)
    cutoff = now - RATE_LIMIT_WINDOW
    _fallback_store[ip] = [
        (ts, count) for ts, count in _fallback_store[ip] if ts > cutoff
    ]

    # Count requests in current window
    current_count = sum(count for _, count in _fallback_store[ip])

    if current_count >= RATE_LIMIT_MAX_REQUESTS:
        # Find oldest entry to calculate reset time
        oldest_ts = min((ts for ts, _ in _fallback_store[ip]), default=now)
        reset_after = max(1, int(RATE_LIMIT_WINDOW - (now - oldest_ts)))
        return False, 0, reset_after

    # Add current request
    _fallback_store[ip].append((now, 1))

    remaining = RATE_LIMIT_MAX_REQUESTS - current_count - 1
    reset_after = RATE_LIMIT_WINDOW

    return True, remaining, reset_after


def check_rate_limit(ip: str) -> Tuple[bool, int, int]:
    """
    Check if IP is within rate limit.

    Uses Redis if available, falls back to in-memory otherwise.

    Returns:
        (allowed, remaining, reset_after)
        - allowed: True if request is allowed
        - remaining: Number of requests remaining in window
        - reset_after: Seconds until window resets
    """
    redis = _get_redis_client()
    if redis is not None:
        return _check_rate_limit_redis(ip)
    else:
        return _check_rate_limit_memory(ip)


def get_rate_limit_headers(remaining: int, reset_after: int) -> Dict[str, str]:
    """Get rate limit headers for response."""
    return {
        'X-RateLimit-Limit': str(RATE_LIMIT_MAX_REQUESTS),
        'X-RateLimit-Remaining': str(max(0, remaining)),
        'X-RateLimit-Reset': str(int(time.time()) + reset_after),
        'Retry-After': str(reset_after),
    }


def is_redis_available() -> bool:
    """
    Check if Redis is available and configured.
    Useful for monitoring and health checks.
    """
    redis = _get_redis_client()
    if redis is None:
        return False

    try:
        redis.ping()
        return True
    except Exception:
        return False
