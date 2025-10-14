"""
DroneWatch Source Verifier - Parallel RSS Feed Verification
Wave 12 Implementation

Verifies all 77 RSS feeds using async parallel processing:
- HTTP status check (200 OK)
- RSS parsing validation
- Content freshness check
- Performance monitoring

Author: DroneWatch Team
Date: 2025-10-14
Version: 1.0.0
"""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
import feedparser
from config import SOURCES


@dataclass
class VerificationResult:
    """Result of a single source verification"""
    source_name: str
    url: str
    http_status: int
    content_type: str
    parse_success: bool
    entry_count: int
    last_updated: Optional[datetime]
    error_message: Optional[str]
    verification_time: float  # seconds
    success: bool  # Overall success flag
    response_time: float  # HTTP response time in seconds


class SourceVerifier:
    """Parallel RSS feed verification engine"""

    def __init__(self, concurrent_workers: int = 10, timeout: int = 10):
        """
        Initialize verifier

        Args:
            concurrent_workers: Number of parallel verification tasks (default: 10)
            timeout: HTTP request timeout in seconds (default: 10)
        """
        self.concurrent_workers = concurrent_workers
        self.timeout = timeout
        self.user_agent = "DroneWatch Source Verifier/1.0 (https://dronewatch.cc)"

    async def verify_source(self, source_name: str, source_config: Dict) -> VerificationResult:
        """
        Verify a single RSS feed source

        Args:
            source_name: Source identifier
            source_config: Source configuration dict

        Returns:
            VerificationResult with verification details
        """
        start_time = time.time()

        # Get RSS URL
        rss_url = source_config.get("rss")
        if not rss_url:
            return VerificationResult(
                source_name=source_name,
                url="",
                http_status=0,
                content_type="",
                parse_success=False,
                entry_count=0,
                last_updated=None,
                error_message="No RSS URL configured",
                verification_time=time.time() - start_time,
                success=False,
                response_time=0.0
            )

        # Skip placeholder URLs
        if "PLACEHOLDER" in rss_url or rss_url == "":
            return VerificationResult(
                source_name=source_name,
                url=rss_url,
                http_status=0,
                content_type="",
                parse_success=False,
                entry_count=0,
                last_updated=None,
                error_message="Placeholder URL - not configured",
                verification_time=time.time() - start_time,
                success=False,
                response_time=0.0
            )

        # Skip disabled sources
        if not source_config.get("working", True):
            return VerificationResult(
                source_name=source_name,
                url=rss_url,
                http_status=0,
                content_type="",
                parse_success=False,
                entry_count=0,
                last_updated=None,
                error_message="Source marked as not working",
                verification_time=time.time() - start_time,
                success=False,
                response_time=0.0
            )

        # Perform HTTP request with retries
        http_status = 0
        content_type = ""
        content = None
        error_message = None
        response_time = 0.0

        for attempt in range(3):  # 3 retry attempts
            try:
                request_start = time.time()
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                headers = {"User-Agent": self.user_agent}

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(rss_url, headers=headers) as response:
                        response_time = time.time() - request_start
                        http_status = response.status
                        content_type = response.headers.get("Content-Type", "")

                        if response.status == 200:
                            content = await response.text()
                            break  # Success, no retry needed
                        else:
                            error_message = f"HTTP {response.status}"

                            # Don't retry permanent failures
                            if response.status in [404, 410, 403]:
                                break

            except asyncio.TimeoutError:
                error_message = f"Timeout (>{self.timeout}s)"
                if attempt < 2:  # Retry with exponential backoff
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                error_message = f"Request error: {str(e)}"
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)

        # Parse RSS feed if content retrieved
        parse_success = False
        entry_count = 0
        last_updated = None

        if content and http_status == 200:
            try:
                feed = feedparser.parse(content)

                # Check for parse errors
                if hasattr(feed, 'bozo') and feed.bozo:
                    error_message = f"RSS parse error: {getattr(feed, 'bozo_exception', 'Unknown')}"
                    parse_success = False
                else:
                    parse_success = True
                    entry_count = len(feed.entries)

                    # Extract last updated timestamp
                    if entry_count > 0 and hasattr(feed.entries[0], 'published_parsed'):
                        try:
                            last_updated = datetime(*feed.entries[0].published_parsed[:6])
                        except:
                            pass

                    # Check if feed has entries
                    if entry_count == 0:
                        error_message = "Feed has no entries"
                        parse_success = False

            except Exception as e:
                error_message = f"Parse exception: {str(e)}"
                parse_success = False

        # Determine overall success
        success = (http_status == 200 and parse_success and entry_count > 0)

        verification_time = time.time() - start_time

        return VerificationResult(
            source_name=source_name,
            url=rss_url,
            http_status=http_status,
            content_type=content_type,
            parse_success=parse_success,
            entry_count=entry_count,
            last_updated=last_updated,
            error_message=error_message,
            verification_time=verification_time,
            success=success,
            response_time=response_time
        )

    async def verify_all_sources(self, sources: Dict = None) -> List[VerificationResult]:
        """
        Verify all sources in parallel

        Args:
            sources: Source dict (default: SOURCES from config.py)

        Returns:
            List of VerificationResult objects
        """
        if sources is None:
            sources = SOURCES

        # Filter to only RSS sources (skip HTML scraping sources)
        rss_sources = {
            name: config for name, config in sources.items()
            if config.get("rss") and config.get("scrape_type") != "html"
        }

        # Create verification tasks
        tasks = []
        for source_name, source_config in rss_sources.items():
            task = self.verify_source(source_name, source_config)
            tasks.append(task)

        # Run tasks with concurrency limit
        results = []
        for i in range(0, len(tasks), self.concurrent_workers):
            batch = tasks[i:i + self.concurrent_workers]
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)

        return results

    def get_summary_stats(self, results: List[VerificationResult]) -> Dict:
        """
        Generate summary statistics from verification results

        Args:
            results: List of VerificationResult objects

        Returns:
            Dictionary with summary statistics
        """
        total = len(results)
        working = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)

        # Response time stats
        response_times = [r.response_time for r in results if r.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Find slowest sources
        sorted_by_time = sorted(results, key=lambda r: r.response_time, reverse=True)
        slowest = sorted_by_time[:5]

        # Find fastest sources
        fastest = [r for r in sorted_by_time if r.success][-5:]
        fastest.reverse()

        # Degraded sources (slow but working)
        degraded = [r for r in results if r.success and r.response_time > 5.0]

        return {
            "total_sources": total,
            "working": working,
            "failed": failed,
            "success_rate": (working / total * 100) if total > 0 else 0,
            "average_response_time": avg_response_time,
            "slowest_sources": [
                {"name": r.source_name, "time": r.response_time, "url": r.url}
                for r in slowest[:3]
            ],
            "fastest_sources": [
                {"name": r.source_name, "time": r.response_time, "url": r.url}
                for r in fastest[:3]
            ],
            "degraded_sources": [
                {"name": r.source_name, "time": r.response_time, "url": r.url}
                for r in degraded
            ],
        }


async def main():
    """Main verification function for testing"""
    print("DroneWatch Source Verification System v1.0")
    print("=" * 60)
    print()

    verifier = SourceVerifier(concurrent_workers=10, timeout=10)

    start_time = time.time()
    print("Starting verification of all sources...")

    results = await verifier.verify_all_sources()

    elapsed_time = time.time() - start_time

    # Get summary
    summary = verifier.get_summary_stats(results)

    # Print results
    print(f"\nVerification completed in {elapsed_time:.2f} seconds")
    print()
    print(f"Total Sources: {summary['total_sources']}")
    print(f"✅ Working: {summary['working']} ({summary['success_rate']:.1f}%)")
    print(f"❌ Failed: {summary['failed']} ({100 - summary['success_rate']:.1f}%)")
    print(f"Average Response Time: {summary['average_response_time']:.2f}s")
    print()

    # Print failed sources
    failed_results = [r for r in results if not r.success]
    if failed_results:
        print("Failed Sources:")
        print("-" * 60)
        for i, result in enumerate(failed_results, 1):
            print(f"{i}. {result.source_name}")
            print(f"   URL: {result.url}")
            print(f"   Error: {result.error_message}")
            print(f"   HTTP Status: {result.http_status}")
            print()

    # Print degraded sources
    if summary['degraded_sources']:
        print("Degraded Sources (>5s response time):")
        print("-" * 60)
        for source in summary['degraded_sources']:
            print(f"• {source['name']} ({source['time']:.2f}s)")
        print()

    return results, summary


if __name__ == "__main__":
    asyncio.run(main())
