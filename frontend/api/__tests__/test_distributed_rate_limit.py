"""
Comprehensive test suite for distributed_rate_limit.py module.
Tests rate limiting with mocked Redis responses, fallback behavior, and header generation.
"""
import pytest
import time
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MockRedisClient:
    """Mock Upstash Redis client for testing"""

    def __init__(self, should_fail=False, initial_count=0, oldest_timestamp=None):
        self.should_fail = should_fail
        self.data = {}  # key -> sorted set of (member, score)
        self.initial_count = initial_count
        self.oldest_timestamp = oldest_timestamp
        self.expiry_called = False
        self.expiry_ttl = None

    def zremrangebyscore(self, key, min_score, max_score):
        """Remove members with scores between min and max"""
        if self.should_fail:
            raise Exception("Redis connection failed")
        if key in self.data:
            self.data[key] = [
                (m, s) for m, s in self.data[key]
                if s > max_score
            ]
        return 0

    def zcard(self, key):
        """Return count of members in sorted set"""
        if self.should_fail:
            raise Exception("Redis connection failed")
        if key in self.data:
            return len(self.data[key])
        return self.initial_count

    def zrange(self, key, start, end, withscores=False):
        """Return range of members from sorted set"""
        if self.should_fail:
            raise Exception("Redis connection failed")
        if key in self.data and len(self.data[key]) > 0:
            sorted_members = sorted(self.data[key], key=lambda x: x[1])
            result = sorted_members[start:end + 1] if end >= 0 else sorted_members[start:]
            return result
        if self.oldest_timestamp:
            return [("member", self.oldest_timestamp)]
        return []

    def zadd(self, key, mapping):
        """Add member(s) to sorted set"""
        if self.should_fail:
            raise Exception("Redis connection failed")
        if key not in self.data:
            self.data[key] = []
        for member, score in mapping.items():
            self.data[key].append((member, score))
        return 1

    def expire(self, key, seconds):
        """Set key expiration"""
        if self.should_fail:
            raise Exception("Redis connection failed")
        self.expiry_called = True
        self.expiry_ttl = seconds
        return True

    def ping(self):
        """Health check"""
        if self.should_fail:
            raise Exception("Redis connection failed")
        return "PONG"


class TestGetClientIP:
    """Test IP extraction from request headers"""

    def test_ip_from_x_forwarded_for_single(self):
        """Test extracting IP from single X-Forwarded-For value"""
        # Import fresh to avoid module state issues
        import distributed_rate_limit

        headers = {'X-Forwarded-For': '203.0.113.50'}
        result = distributed_rate_limit.get_client_ip(headers)
        assert result == '203.0.113.50'

    def test_ip_from_x_forwarded_for_multiple(self):
        """Test extracting first IP from multiple X-Forwarded-For values"""
        import distributed_rate_limit

        headers = {'X-Forwarded-For': '203.0.113.50, 70.41.3.18, 150.172.238.178'}
        result = distributed_rate_limit.get_client_ip(headers)
        assert result == '203.0.113.50'

    def test_ip_from_x_forwarded_for_with_spaces(self):
        """Test extracting IP with extra whitespace"""
        import distributed_rate_limit

        headers = {'X-Forwarded-For': '  203.0.113.50  ,  70.41.3.18  '}
        result = distributed_rate_limit.get_client_ip(headers)
        assert result == '203.0.113.50'

    def test_ip_from_x_real_ip(self):
        """Test fallback to X-Real-IP header"""
        import distributed_rate_limit

        headers = {'X-Real-IP': '198.51.100.42'}
        result = distributed_rate_limit.get_client_ip(headers)
        assert result == '198.51.100.42'

    def test_ip_from_remote_addr(self):
        """Test fallback to Remote-Addr header"""
        import distributed_rate_limit

        headers = {'Remote-Addr': '192.0.2.100'}
        result = distributed_rate_limit.get_client_ip(headers)
        assert result == '192.0.2.100'

    def test_ip_priority_order(self):
        """Test X-Forwarded-For takes priority over other headers"""
        import distributed_rate_limit

        headers = {
            'X-Forwarded-For': '203.0.113.50',
            'X-Real-IP': '198.51.100.42',
            'Remote-Addr': '192.0.2.100'
        }
        result = distributed_rate_limit.get_client_ip(headers)
        assert result == '203.0.113.50'

    def test_ip_unknown_when_no_headers(self):
        """Test returns 'unknown' when no IP headers present"""
        import distributed_rate_limit

        headers = {}
        result = distributed_rate_limit.get_client_ip(headers)
        assert result == 'unknown'

    def test_ip_empty_x_forwarded_for_falls_back(self):
        """Test empty X-Forwarded-For falls back to other headers"""
        import distributed_rate_limit

        headers = {
            'X-Forwarded-For': '',
            'X-Real-IP': '198.51.100.42'
        }
        result = distributed_rate_limit.get_client_ip(headers)
        assert result == '198.51.100.42'


class TestRateLimitHeaders:
    """Test rate limit header generation"""

    def test_get_rate_limit_headers_structure(self):
        """Test headers contain all required fields"""
        import distributed_rate_limit

        headers = distributed_rate_limit.get_rate_limit_headers(remaining=50, reset_after=45)

        assert 'X-RateLimit-Limit' in headers
        assert 'X-RateLimit-Remaining' in headers
        assert 'X-RateLimit-Reset' in headers
        assert 'Retry-After' in headers

    def test_get_rate_limit_headers_values(self):
        """Test headers have correct values"""
        import distributed_rate_limit

        # Temporarily set rate limit for consistent testing
        original_limit = distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS
        distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = 100

        try:
            headers = distributed_rate_limit.get_rate_limit_headers(remaining=50, reset_after=30)

            assert headers['X-RateLimit-Limit'] == '100'
            assert headers['X-RateLimit-Remaining'] == '50'
            assert headers['Retry-After'] == '30'

            # X-RateLimit-Reset should be a Unix timestamp in the future
            reset_time = int(headers['X-RateLimit-Reset'])
            assert reset_time > int(time.time())
        finally:
            distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = original_limit

    def test_get_rate_limit_headers_zero_remaining(self):
        """Test headers when no requests remaining"""
        import distributed_rate_limit

        headers = distributed_rate_limit.get_rate_limit_headers(remaining=0, reset_after=60)
        assert headers['X-RateLimit-Remaining'] == '0'

    def test_get_rate_limit_headers_negative_remaining_clamped(self):
        """Test negative remaining is clamped to 0"""
        import distributed_rate_limit

        headers = distributed_rate_limit.get_rate_limit_headers(remaining=-5, reset_after=60)
        assert headers['X-RateLimit-Remaining'] == '0'


class TestCheckRateLimitMemoryFallback:
    """Test in-memory fallback rate limiting"""

    def setup_method(self):
        """Reset module state before each test"""
        import distributed_rate_limit

        # Reset the fallback store and Redis state
        distributed_rate_limit._fallback_store.clear()
        distributed_rate_limit._redis_client = None
        distributed_rate_limit._redis_available = None

    def test_fallback_allows_requests_under_limit(self):
        """Test requests under limit are allowed in fallback mode"""
        import distributed_rate_limit

        # Force fallback by not configuring Redis
        with patch.dict(os.environ, {'UPSTASH_REDIS_REST_URL': '', 'UPSTASH_REDIS_REST_TOKEN': ''}, clear=False):
            distributed_rate_limit._redis_available = False

            allowed, remaining, reset_after = distributed_rate_limit.check_rate_limit('192.0.2.1')

            assert allowed is True
            assert remaining == distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS - 1
            assert reset_after == distributed_rate_limit.RATE_LIMIT_WINDOW

    def test_fallback_blocks_requests_over_limit(self):
        """Test requests over limit are blocked in fallback mode"""
        import distributed_rate_limit

        # Force fallback mode
        distributed_rate_limit._redis_available = False

        original_limit = distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS
        distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = 5  # Small limit for testing

        try:
            ip = '192.0.2.100'

            # Make requests up to the limit
            for i in range(5):
                allowed, remaining, reset_after = distributed_rate_limit.check_rate_limit(ip)
                assert allowed is True
                assert remaining == 4 - i

            # Next request should be blocked
            allowed, remaining, reset_after = distributed_rate_limit.check_rate_limit(ip)
            assert allowed is False
            assert remaining == 0
            assert reset_after >= 1
        finally:
            distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = original_limit

    def test_fallback_different_ips_tracked_separately(self):
        """Test different IPs have separate rate limit counters"""
        import distributed_rate_limit

        distributed_rate_limit._redis_available = False

        original_limit = distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS
        distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = 3

        try:
            # Exhaust limit for IP 1
            for _ in range(3):
                distributed_rate_limit.check_rate_limit('192.0.2.1')

            # IP 1 should be blocked
            allowed1, _, _ = distributed_rate_limit.check_rate_limit('192.0.2.1')
            assert allowed1 is False

            # IP 2 should still be allowed
            allowed2, remaining2, _ = distributed_rate_limit.check_rate_limit('192.0.2.2')
            assert allowed2 is True
            assert remaining2 == 2  # First request for this IP
        finally:
            distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = original_limit


class TestCheckRateLimitRedis:
    """Test Redis-based rate limiting"""

    def setup_method(self):
        """Reset module state before each test"""
        import distributed_rate_limit

        distributed_rate_limit._fallback_store.clear()
        distributed_rate_limit._redis_client = None
        distributed_rate_limit._redis_available = None

    def test_redis_allows_requests_under_limit(self):
        """Test requests under limit are allowed with Redis"""
        import distributed_rate_limit

        mock_redis = MockRedisClient(initial_count=0)

        with patch.object(distributed_rate_limit, '_get_redis_client', return_value=mock_redis):
            allowed, remaining, reset_after = distributed_rate_limit._check_rate_limit_redis('192.0.2.1')

            assert allowed is True
            assert remaining == distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS - 1
            assert reset_after == distributed_rate_limit.RATE_LIMIT_WINDOW

    def test_redis_blocks_requests_at_limit(self):
        """Test requests at limit are blocked with Redis"""
        import distributed_rate_limit

        original_limit = distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS
        distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = 5

        try:
            # Mock Redis returning count at the limit
            mock_redis = MockRedisClient(initial_count=5)

            with patch.object(distributed_rate_limit, '_get_redis_client', return_value=mock_redis):
                allowed, remaining, reset_after = distributed_rate_limit._check_rate_limit_redis('192.0.2.1')

                assert allowed is False
                assert remaining == 0
                assert reset_after >= 1
        finally:
            distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = original_limit

    def test_redis_blocks_requests_over_limit(self):
        """Test requests over limit are blocked with Redis"""
        import distributed_rate_limit

        original_limit = distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS
        distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = 5

        try:
            # Mock Redis returning count over the limit
            mock_redis = MockRedisClient(initial_count=10)

            with patch.object(distributed_rate_limit, '_get_redis_client', return_value=mock_redis):
                allowed, remaining, reset_after = distributed_rate_limit._check_rate_limit_redis('192.0.2.1')

                assert allowed is False
                assert remaining == 0
        finally:
            distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = original_limit

    def test_redis_sets_key_expiry(self):
        """Test Redis key expiry is set for auto-cleanup"""
        import distributed_rate_limit

        mock_redis = MockRedisClient(initial_count=0)

        with patch.object(distributed_rate_limit, '_get_redis_client', return_value=mock_redis):
            distributed_rate_limit._check_rate_limit_redis('192.0.2.1')

            assert mock_redis.expiry_called is True
            assert mock_redis.expiry_ttl == distributed_rate_limit.RATE_LIMIT_WINDOW + 1

    def test_redis_error_fails_open(self):
        """Test Redis errors result in fail-open behavior"""
        import distributed_rate_limit

        mock_redis = MockRedisClient(should_fail=True)

        with patch.object(distributed_rate_limit, '_get_redis_client', return_value=mock_redis):
            allowed, remaining, reset_after = distributed_rate_limit._check_rate_limit_redis('192.0.2.1')

            # Should allow request (fail-open)
            assert allowed is True
            assert remaining == distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS - 1
            assert reset_after == distributed_rate_limit.RATE_LIMIT_WINDOW

    def test_redis_calculates_reset_from_oldest_entry(self):
        """Test reset time is calculated from oldest entry in window"""
        import distributed_rate_limit

        original_limit = distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS
        distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = 5

        try:
            # Oldest entry was 30 seconds ago (in ms)
            now_ms = int(time.time() * 1000)
            oldest_ts = now_ms - 30000  # 30 seconds ago

            mock_redis = MockRedisClient(initial_count=5, oldest_timestamp=oldest_ts)

            with patch.object(distributed_rate_limit, '_get_redis_client', return_value=mock_redis):
                allowed, remaining, reset_after = distributed_rate_limit._check_rate_limit_redis('192.0.2.1')

                assert allowed is False
                # Reset should be approximately window - 30 seconds = 30 seconds
                # Allow some tolerance for timing
                assert 25 <= reset_after <= 35
        finally:
            distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = original_limit


class TestGetRedisClient:
    """Test Redis client initialization and fallback logic"""

    def setup_method(self):
        """Reset module state before each test"""
        import distributed_rate_limit

        distributed_rate_limit._redis_client = None
        distributed_rate_limit._redis_available = None

    def test_returns_none_without_credentials(self):
        """Test returns None when Redis credentials not configured"""
        import distributed_rate_limit

        # Reset state
        distributed_rate_limit._redis_client = None
        distributed_rate_limit._redis_available = None

        # Clear credentials
        with patch.object(distributed_rate_limit, 'UPSTASH_REDIS_REST_URL', ''):
            with patch.object(distributed_rate_limit, 'UPSTASH_REDIS_REST_TOKEN', ''):
                result = distributed_rate_limit._get_redis_client()
                assert result is None
                assert distributed_rate_limit._redis_available is False

    def test_returns_cached_none_when_unavailable(self):
        """Test returns cached None when Redis already marked unavailable"""
        import distributed_rate_limit

        distributed_rate_limit._redis_available = False

        # Should return None immediately without checking credentials
        result = distributed_rate_limit._get_redis_client()
        assert result is None

    def test_returns_cached_client(self):
        """Test returns cached client when already initialized"""
        import distributed_rate_limit

        mock_client = MockRedisClient()
        distributed_rate_limit._redis_client = mock_client
        distributed_rate_limit._redis_available = True

        result = distributed_rate_limit._get_redis_client()
        assert result is mock_client

    def test_handles_import_error(self):
        """Test gracefully handles missing upstash-redis package"""
        import distributed_rate_limit

        distributed_rate_limit._redis_client = None
        distributed_rate_limit._redis_available = None

        with patch.object(distributed_rate_limit, 'UPSTASH_REDIS_REST_URL', 'https://redis.example.com'):
            with patch.object(distributed_rate_limit, 'UPSTASH_REDIS_REST_TOKEN', 'test-token'):
                with patch.dict('sys.modules', {'upstash_redis': None}):
                    # Mock the import to raise ImportError
                    def mock_import(name, *args, **kwargs):
                        if name == 'upstash_redis':
                            raise ImportError("No module named 'upstash_redis'")
                        return original_import(name, *args, **kwargs)

                    import builtins
                    original_import = builtins.__import__

                    with patch.object(builtins, '__import__', side_effect=mock_import):
                        result = distributed_rate_limit._get_redis_client()
                        assert result is None
                        assert distributed_rate_limit._redis_available is False


class TestIsRedisAvailable:
    """Test Redis availability check"""

    def setup_method(self):
        """Reset module state before each test"""
        import distributed_rate_limit

        distributed_rate_limit._redis_client = None
        distributed_rate_limit._redis_available = None

    def test_returns_true_when_redis_responds(self):
        """Test returns True when Redis ping succeeds"""
        import distributed_rate_limit

        mock_redis = MockRedisClient()

        with patch.object(distributed_rate_limit, '_get_redis_client', return_value=mock_redis):
            result = distributed_rate_limit.is_redis_available()
            assert result is True

    def test_returns_false_when_redis_not_configured(self):
        """Test returns False when Redis client is None"""
        import distributed_rate_limit

        with patch.object(distributed_rate_limit, '_get_redis_client', return_value=None):
            result = distributed_rate_limit.is_redis_available()
            assert result is False

    def test_returns_false_when_ping_fails(self):
        """Test returns False when Redis ping fails"""
        import distributed_rate_limit

        mock_redis = MockRedisClient(should_fail=True)

        with patch.object(distributed_rate_limit, '_get_redis_client', return_value=mock_redis):
            result = distributed_rate_limit.is_redis_available()
            assert result is False


class TestCheckRateLimitIntegration:
    """Integration tests for the main check_rate_limit function"""

    def setup_method(self):
        """Reset module state before each test"""
        import distributed_rate_limit

        distributed_rate_limit._fallback_store.clear()
        distributed_rate_limit._redis_client = None
        distributed_rate_limit._redis_available = None

    def test_uses_redis_when_available(self):
        """Test check_rate_limit uses Redis when available"""
        import distributed_rate_limit

        mock_redis = MockRedisClient(initial_count=0)
        distributed_rate_limit._redis_client = mock_redis
        distributed_rate_limit._redis_available = True

        with patch.object(distributed_rate_limit, '_get_redis_client', return_value=mock_redis):
            allowed, remaining, reset = distributed_rate_limit.check_rate_limit('192.0.2.1')

            assert allowed is True
            # Verify Redis was used (zadd was called)
            assert len(mock_redis.data) > 0 or mock_redis.expiry_called

    def test_falls_back_to_memory_when_redis_unavailable(self):
        """Test check_rate_limit falls back to memory when Redis unavailable"""
        import distributed_rate_limit

        distributed_rate_limit._redis_available = False

        with patch.object(distributed_rate_limit, '_get_redis_client', return_value=None):
            allowed, remaining, reset = distributed_rate_limit.check_rate_limit('192.0.2.1')

            assert allowed is True
            # Verify fallback store was used
            assert '192.0.2.1' in distributed_rate_limit._fallback_store


class TestSlidingWindowBehavior:
    """Test sliding window algorithm behavior"""

    def setup_method(self):
        """Reset module state before each test"""
        import distributed_rate_limit

        distributed_rate_limit._fallback_store.clear()
        distributed_rate_limit._redis_client = None
        distributed_rate_limit._redis_available = None

    def test_sliding_window_expiry_in_memory(self):
        """Test old entries expire in sliding window (in-memory)"""
        import distributed_rate_limit

        distributed_rate_limit._redis_available = False

        original_window = distributed_rate_limit.RATE_LIMIT_WINDOW
        original_limit = distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS

        # Use very short window for testing
        distributed_rate_limit.RATE_LIMIT_WINDOW = 1  # 1 second
        distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = 2

        try:
            ip = '192.0.2.99'

            # Make 2 requests (hit limit)
            distributed_rate_limit.check_rate_limit(ip)
            distributed_rate_limit.check_rate_limit(ip)

            # Third request should be blocked
            allowed, _, _ = distributed_rate_limit.check_rate_limit(ip)
            assert allowed is False

            # Wait for window to expire
            time.sleep(1.1)

            # Now requests should be allowed again
            allowed, remaining, _ = distributed_rate_limit.check_rate_limit(ip)
            assert allowed is True
            assert remaining == 1  # Should have full limit minus 1
        finally:
            distributed_rate_limit.RATE_LIMIT_WINDOW = original_window
            distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS = original_limit

    def test_redis_removes_old_entries(self):
        """Test Redis sliding window removes entries outside window"""
        import distributed_rate_limit

        mock_redis = MockRedisClient(initial_count=0)

        # Pre-populate with old entry (outside window)
        now_ms = int(time.time() * 1000)
        window_ms = distributed_rate_limit.RATE_LIMIT_WINDOW * 1000
        old_ts = now_ms - window_ms - 1000  # 1 second outside window

        mock_redis.data['rate_limit:192.0.2.1'] = [('old_request', old_ts)]

        with patch.object(distributed_rate_limit, '_get_redis_client', return_value=mock_redis):
            allowed, _, _ = distributed_rate_limit._check_rate_limit_redis('192.0.2.1')

            assert allowed is True
            # Old entry should have been removed by zremrangebyscore
            remaining_old = [
                (m, s) for m, s in mock_redis.data.get('rate_limit:192.0.2.1', [])
                if s <= old_ts
            ]
            assert len(remaining_old) == 0


class TestEnvironmentVariableConfiguration:
    """Test configuration via environment variables"""

    def test_rate_limit_window_from_env(self):
        """Test RATE_LIMIT_WINDOW can be configured via env"""
        # This tests that the module reads from environment
        # The actual behavior is set at import time, so we test the values
        import distributed_rate_limit

        # Default should be 60 seconds if not set
        assert distributed_rate_limit.RATE_LIMIT_WINDOW >= 1

    def test_rate_limit_max_requests_from_env(self):
        """Test RATE_LIMIT_MAX_REQUESTS can be configured via env"""
        import distributed_rate_limit

        # Default should be 100 if not set
        assert distributed_rate_limit.RATE_LIMIT_MAX_REQUESTS >= 1
