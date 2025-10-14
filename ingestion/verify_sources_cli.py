#!/usr/bin/env python3
"""
DroneWatch Source Verification CLI Script
Wave 12 Implementation

Command-line interface for verifying all RSS feed sources.

Usage:
    python3 verify_sources_cli.py              # Standard verification
    python3 verify_sources_cli.py --verbose    # Verbose output
    python3 verify_sources_cli.py --json       # JSON output

Author: DroneWatch Team
Date: 2025-10-14
Version: 1.0.0
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime
from source_verifier import SourceVerifier
from alerting import AlertingSystem
from config import SOURCES


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="DroneWatch Source Verification System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 verify_sources_cli.py                  # Standard verification
  python3 verify_sources_cli.py --verbose        # Verbose output
  python3 verify_sources_cli.py --json           # JSON output
  python3 verify_sources_cli.py --workers 20     # Use 20 parallel workers
  python3 verify_sources_cli.py --timeout 15     # 15 second timeout
        """
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output with per-source details"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )

    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=10,
        help="Number of concurrent workers (default: 10)"
    )

    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=10,
        help="HTTP request timeout in seconds (default: 10)"
    )

    parser.add_argument(
        "--no-alerts",
        action="store_true",
        help="Disable alerting system (console output only)"
    )

    parser.add_argument(
        "--github-actions",
        action="store_true",
        help="GitHub Actions mode - exit with error code on failures"
    )

    return parser.parse_args()


async def verify_sources(args):
    """
    Run source verification

    Args:
        args: Parsed command-line arguments

    Returns:
        Tuple of (results, summary)
    """
    # Initialize verifier
    verifier = SourceVerifier(
        concurrent_workers=args.workers,
        timeout=args.timeout
    )

    # Print header
    if not args.json:
        print("DroneWatch Source Verification System v1.0")
        print("=" * 60)
        print(f"Workers: {args.workers} | Timeout: {args.timeout}s")
        print()

    # Count sources
    rss_sources = {
        name: config for name, config in SOURCES.items()
        if config.get("rss") and config.get("scrape_type") != "html"
    }

    if not args.json:
        print(f"Verifying {len(rss_sources)} RSS feed sources...")
        print()

    # Run verification
    import time
    start_time = time.time()

    results = await verifier.verify_all_sources()

    elapsed_time = time.time() - start_time

    # Get summary
    summary = verifier.get_summary_stats(results)
    summary['elapsed_time'] = elapsed_time

    return results, summary


def output_json(results, summary):
    """
    Output results in JSON format

    Args:
        results: List of VerificationResult objects
        summary: Summary statistics dict
    """
    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "results": [
            {
                "source_name": r.source_name,
                "url": r.url,
                "success": r.success,
                "http_status": r.http_status,
                "content_type": r.content_type,
                "parse_success": r.parse_success,
                "entry_count": r.entry_count,
                "last_updated": r.last_updated.isoformat() if r.last_updated else None,
                "error_message": r.error_message,
                "response_time": r.response_time,
                "verification_time": r.verification_time
            }
            for r in results
        ]
    }

    print(json.dumps(output, indent=2))


def output_verbose(results, summary):
    """
    Output verbose details for each source

    Args:
        results: List of VerificationResult objects
        summary: Summary statistics dict
    """
    print()
    print("=" * 60)
    print("DETAILED RESULTS")
    print("=" * 60)
    print()

    for i, result in enumerate(results, 1):
        status_icon = "✅" if result.success else "❌"
        print(f"{i}. {status_icon} {result.source_name}")
        print(f"   URL: {result.url}")
        print(f"   HTTP Status: {result.http_status}")
        print(f"   Content-Type: {result.content_type}")
        print(f"   Parse Success: {result.parse_success}")
        print(f"   Entry Count: {result.entry_count}")
        print(f"   Response Time: {result.response_time:.2f}s")

        if result.last_updated:
            print(f"   Last Updated: {result.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

        if result.error_message:
            print(f"   Error: {result.error_message}")

        print()


def main():
    """Main entry point"""
    args = parse_args()

    # Run verification
    try:
        results, summary = asyncio.run(verify_sources(args))
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: Verification failed: {e}")
        sys.exit(1)

    # Output results
    if args.json:
        output_json(results, summary)
    else:
        # Send alerts (unless disabled)
        if not args.no_alerts:
            alerting = AlertingSystem()
            alerting.send_alerts(results, summary)
        else:
            # Just print basic summary
            print(f"\nVerification completed in {summary['elapsed_time']:.2f} seconds")
            print(f"Total: {summary['total_sources']} | Working: {summary['working']} | Failed: {summary['failed']}")

        # Verbose output
        if args.verbose:
            output_verbose(results, summary)

    # GitHub Actions mode - exit with error code if failures
    if args.github_actions and summary['failed'] > 0:
        print(f"\n❌ GitHub Actions: {summary['failed']} sources failed")
        sys.exit(1)

    # Exit with success
    sys.exit(0)


if __name__ == "__main__":
    main()
