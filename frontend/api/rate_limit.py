"""
DEPRECATED: This module is deprecated and will be removed in a future version.

Use `distributed_rate_limit` instead, which provides distributed rate limiting
using Upstash Redis for serverless environments. The new module falls back to
in-memory rate limiting when Redis is not configured, so it works seamlessly
for local development.

Example migration:
    # Old (deprecated):
    from rate_limit import check_rate_limit, get_rate_limit_headers, get_client_ip

    # New (recommended):
    from distributed_rate_limit import check_rate_limit, get_rate_limit_headers, get_client_ip

This module is kept for backward compatibility only. All new code should use
distributed_rate_limit instead.
"""
import time
import warnings

# Emit deprecation warning when this module is imported
warnings.warn(
    "The 'rate_limit' module is deprecated. Use 'distributed_rate_limit' instead.",
    DeprecationWarning,
    stacklevel=2
)
from collections import defaultdict
from typing import Dict, Tuple

# In-memory store: {ip: [(timestamp, count), ...]}
_rate_limit_store: Dict[str, list] = defaultdict(list)

# Rate limit configuration
RATE_LIMIT_WINDOW = 60  # 1 minute window
RATE_LIMIT_MAX_REQUESTS = 100  # Max requests per window per IP


def get_client_ip(headers: dict) -> str:
    """Extract client IP from headers, handling proxies."""
    # Check X-Forwarded-For (Vercel sets this)
    forwarded_for = headers.get('X-Forwarded-For', '')
    if forwarded_for:
        # Take the first IP (original client)
        return forwarded_for.split(',')[0].strip()
    
    # Fallback to X-Real-IP or Remote-Addr
    return headers.get('X-Real-IP') or headers.get('Remote-Addr', 'unknown')


def check_rate_limit(ip: str) -> Tuple[bool, int, int]:
    """
    Check if IP is within rate limit.
    
    Returns:
        (allowed, remaining, reset_after)
        - allowed: True if request is allowed
        - remaining: Number of requests remaining in window
        - reset_after: Seconds until window resets
    """
    now = time.time()
    
    # Clean old entries (older than window)
    cutoff = now - RATE_LIMIT_WINDOW
    _rate_limit_store[ip] = [
        (ts, count) for ts, count in _rate_limit_store[ip] if ts > cutoff
    ]
    
    # Count requests in current window
    current_count = sum(count for _, count in _rate_limit_store[ip])
    
    if current_count >= RATE_LIMIT_MAX_REQUESTS:
        # Find oldest entry to calculate reset time
        oldest_ts = min((ts for ts, _ in _rate_limit_store[ip]), default=now)
        reset_after = int(RATE_LIMIT_WINDOW - (now - oldest_ts))
        return False, 0, reset_after
    
    # Add current request
    _rate_limit_store[ip].append((now, 1))
    
    remaining = RATE_LIMIT_MAX_REQUESTS - current_count - 1
    reset_after = RATE_LIMIT_WINDOW
    
    return True, remaining, reset_after


def get_rate_limit_headers(remaining: int, reset_after: int) -> Dict[str, str]:
    """Get rate limit headers for response."""
    return {
        'X-RateLimit-Limit': str(RATE_LIMIT_MAX_REQUESTS),
        'X-RateLimit-Remaining': str(remaining),
        'X-RateLimit-Reset': str(int(time.time()) + reset_after),
        'Retry-After': str(reset_after),
    }

