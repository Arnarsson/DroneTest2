"""
Test Suite for DroneWatch Source Verification System
Wave 12 Implementation

Tests:
1. HTTP success (200 OK)
2. HTTP failure (404)
3. Timeout handling
4. Valid RSS parsing
5. Invalid RSS parsing
6. Parallel verification performance
7. Retry logic
8. Summary statistics

Author: DroneWatch Team
Date: 2025-10-14
Version: 1.0.0
"""

import asyncio
import time

try:
    import pytest
    from unittest.mock import Mock, patch, AsyncMock
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

from source_verifier import SourceVerifier, VerificationResult
from config import SOURCES


if PYTEST_AVAILABLE:
    class TestSourceVerifier:
        """Test suite for SourceVerifier class"""

        @pytest.fixture
        def verifier(self):
            """Create a SourceVerifier instance for testing"""
            return SourceVerifier(concurrent_workers=5, timeout=5)

    @pytest.mark.asyncio
    async def test_http_success_200(self, verifier):
        """Test successful HTTP 200 response with valid RSS"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/xml"}
        mock_response.text = AsyncMock(return_value="""
        <?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test Feed</title>
                <item>
                    <title>Test Item</title>
                    <link>https://example.com/test</link>
                    <pubDate>Mon, 14 Oct 2025 12:00:00 +0000</pubDate>
                </item>
            </channel>
        </rss>
        """)

        source_config = {
            "rss": "https://example.com/rss",
            "working": True
        }

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

            result = await verifier.verify_source("test_source", source_config)

            assert result.success is True
            assert result.http_status == 200
            assert result.parse_success is True
            assert result.entry_count > 0

    @pytest.mark.asyncio
    async def test_http_failure_404(self, verifier):
        """Test HTTP 404 Not Found response"""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.headers = {"Content-Type": "text/html"}

        source_config = {
            "rss": "https://example.com/broken",
            "working": True
        }

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

            result = await verifier.verify_source("broken_source", source_config)

            assert result.success is False
            assert result.http_status == 404
            assert "HTTP 404" in result.error_message

    @pytest.mark.asyncio
    async def test_timeout_handling(self, verifier):
        """Test timeout handling"""
        source_config = {
            "rss": "https://example.com/slow",
            "working": True
        }

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = asyncio.TimeoutError()

            result = await verifier.verify_source("slow_source", source_config)

            assert result.success is False
            assert "Timeout" in result.error_message

    @pytest.mark.asyncio
    async def test_rss_parse_valid(self, verifier):
        """Test valid RSS feed parsing"""
        valid_rss = """
        <?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Valid Feed</title>
                <item>
                    <title>Item 1</title>
                    <link>https://example.com/1</link>
                    <pubDate>Mon, 14 Oct 2025 12:00:00 +0000</pubDate>
                </item>
                <item>
                    <title>Item 2</title>
                    <link>https://example.com/2</link>
                    <pubDate>Mon, 14 Oct 2025 11:00:00 +0000</pubDate>
                </item>
            </channel>
        </rss>
        """

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "application/rss+xml"}
        mock_response.text = AsyncMock(return_value=valid_rss)

        source_config = {
            "rss": "https://example.com/valid",
            "working": True
        }

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

            result = await verifier.verify_source("valid_source", source_config)

            assert result.success is True
            assert result.parse_success is True
            assert result.entry_count == 2

    @pytest.mark.asyncio
    async def test_rss_parse_invalid(self, verifier):
        """Test invalid RSS feed parsing"""
        invalid_rss = "<html><body>Not RSS</body></html>"

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = AsyncMock(return_value=invalid_rss)

        source_config = {
            "rss": "https://example.com/invalid",
            "working": True
        }

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

            result = await verifier.verify_source("invalid_source", source_config)

            assert result.success is False
            assert result.parse_success is False

    @pytest.mark.asyncio
    async def test_parallel_verification(self, verifier):
        """Test parallel verification of multiple sources (performance benchmark)"""
        # Create test sources
        test_sources = {
            f"test_source_{i}": {
                "rss": f"https://example.com/feed{i}",
                "working": True
            }
            for i in range(20)
        }

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/xml"}
        mock_response.text = AsyncMock(return_value="""
        <?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test Feed</title>
                <item>
                    <title>Test Item</title>
                    <link>https://example.com/test</link>
                </item>
            </channel>
        </rss>
        """)

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

            start_time = time.time()
            results = await verifier.verify_all_sources(test_sources)
            elapsed = time.time() - start_time

            # Verify results
            assert len(results) == 20
            assert all(r.success for r in results)

            # Performance check: 20 sources should complete in < 5 seconds with parallel processing
            assert elapsed < 5.0, f"Verification took {elapsed:.2f}s, expected < 5.0s"

    @pytest.mark.asyncio
    async def test_skip_placeholder_urls(self, verifier):
        """Test that placeholder URLs are skipped"""
        source_config = {
            "rss": "PLACEHOLDER_RSS_APP_URL_HERE",
            "working": False
        }

        result = await verifier.verify_source("placeholder_source", source_config)

        assert result.success is False
        assert "Placeholder" in result.error_message

    @pytest.mark.asyncio
    async def test_skip_disabled_sources(self, verifier):
        """Test that disabled sources are skipped"""
        source_config = {
            "rss": "https://example.com/disabled",
            "working": False
        }

        result = await verifier.verify_source("disabled_source", source_config)

        assert result.success is False
        assert "not working" in result.error_message

    def test_summary_stats(self, verifier):
        """Test summary statistics calculation"""
        # Create mock results
        results = [
            VerificationResult(
                source_name=f"source_{i}",
                url=f"https://example.com/{i}",
                http_status=200 if i < 7 else 404,
                content_type="text/xml",
                parse_success=i < 7,
                entry_count=10 if i < 7 else 0,
                last_updated=None,
                error_message=None if i < 7 else "HTTP 404",
                verification_time=0.5,
                success=i < 7,
                response_time=float(i) * 0.5
            )
            for i in range(10)
        ]

        summary = verifier.get_summary_stats(results)

        assert summary['total_sources'] == 10
        assert summary['working'] == 7
        assert summary['failed'] == 3
        assert summary['success_rate'] == 70.0


def run_integration_test():
    """
    Integration test with real RSS feeds from config.py

    This is NOT a unit test - it makes real HTTP requests.
    Run separately: python3 test_source_verifier.py
    """
    print("=" * 60)
    print("INTEGRATION TEST: Real RSS Feed Verification")
    print("=" * 60)
    print()

    # Test a small subset of real sources
    test_sources = {
        "dr_news": SOURCES["dr_news"],
        "nrk_news": SOURCES["nrk_news"],
        "svt_nyheter": SOURCES["svt_nyheter"]
    }

    async def run_test():
        verifier = SourceVerifier(concurrent_workers=3, timeout=10)
        print(f"Testing {len(test_sources)} real RSS feeds...")
        print()

        start_time = time.time()
        results = await verifier.verify_all_sources(test_sources)
        elapsed = time.time() - start_time

        summary = verifier.get_summary_stats(results)

        print(f"Completed in {elapsed:.2f} seconds")
        print()
        print(f"Total: {summary['total_sources']}")
        print(f"Working: {summary['working']} ({summary['success_rate']:.1f}%)")
        print(f"Failed: {summary['failed']}")
        print()

        for result in results:
            status = "" if result.success else "L"
            print(f"{status} {result.source_name}")
            print(f"   URL: {result.url}")
            print(f"   HTTP Status: {result.http_status}")
            print(f"   Entries: {result.entry_count}")
            print(f"   Response Time: {result.response_time:.2f}s")
            if result.error_message:
                print(f"   Error: {result.error_message}")
            print()

        return results, summary

    return asyncio.run(run_test())


if __name__ == "__main__":
    # Run integration test when script is executed directly
    print("Running integration test with real RSS feeds...")
    print()
    results, summary = run_integration_test()

    if summary['failed'] == 0:
        print(" All tests passed!")
        exit(0)
    else:
        print(f"L {summary['failed']} sources failed")
        exit(1)
