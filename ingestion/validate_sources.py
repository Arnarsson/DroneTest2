#!/usr/bin/env python3
"""
URL Validation for DroneWatch Sources
NO FAKE URLS - ALL SOURCES VERIFIED BEFORE USE

Context Engineering Principles:
- Just-in-time verification (test before use)
- Structured output (clear pass/fail)
- Progressive disclosure (validate → fix → re-validate)

Anti-Hallucination Measures:
- Tests every URL with HTTP request
- Validates RSS feeds parse correctly
- Documents working vs broken sources
- Zero tolerance for 404s
"""

import requests
import feedparser
from config import SOURCES
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple

class SourceValidator:
    """Validate all source URLs before scraper deployment"""

    def __init__(self):
        self.results = {
            'working': [],
            'broken': [],
            'needs_manual_check': []
        }
        self.timeout = 15

    def validate_url(self, url: str, source_type: str = 'html') -> Tuple[bool, str, Dict]:
        """
        Test if URL exists and returns valid content

        Args:
            url: URL to test
            source_type: 'html' or 'rss'

        Returns:
            (success: bool, message: str, details: dict)
        """
        try:
            if source_type == 'rss':
                # Test RSS feed parsing
                print(f"      Testing RSS: {url}")
                feed = feedparser.parse(url)

                if feed.bozo:  # Parse error
                    return False, f"Invalid RSS: {str(feed.bozo_exception)[:100]}", {
                        'error': str(feed.bozo_exception)
                    }

                entry_count = len(feed.entries)
                if entry_count == 0:
                    return False, "RSS feed empty (0 entries)", {'entries': 0}

                return True, f"RSS OK: {entry_count} entries", {
                    'entries': entry_count,
                    'title': feed.feed.get('title', 'N/A')[:100]
                }

            else:
                # Test HTML page accessibility
                print(f"      Testing HTML: {url}")
                r = requests.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    headers={'User-Agent': 'DroneWatch/2.0 Validator'}
                )

                if r.status_code == 404:
                    return False, "404 Not Found", {'status': 404}

                if r.status_code == 403:
                    return False, "403 Forbidden (may need auth/headers)", {'status': 403}

                if r.status_code >= 500:
                    return False, f"Server error {r.status_code}", {'status': r.status_code}

                if r.status_code >= 400:
                    return False, f"HTTP {r.status_code}", {'status': r.status_code}

                # Check if redirected
                if r.url != url:
                    return True, f"Redirects to {r.url[:60]}", {
                        'redirected': True,
                        'final_url': r.url,
                        'status': r.status_code
                    }

                return True, f"HTML OK ({r.status_code})", {
                    'status': r.status_code,
                    'content_length': len(r.content)
                }

        except requests.exceptions.Timeout:
            return False, f"Timeout (>{self.timeout}s)", {}

        except requests.exceptions.SSLError as e:
            return False, f"SSL error: {str(e)[:80]}", {}

        except requests.exceptions.ConnectionError as e:
            return False, f"Connection error: {str(e)[:80]}", {}

        except Exception as e:
            return False, f"Error: {str(e)[:100]}", {}

    def validate_all(self):
        """Validate all sources in config.py"""
        print("🔍 DroneWatch Source URL Validation")
        print("=" * 80)
        print(f"Testing {len(SOURCES)} sources...")
        print(f"Timeout: {self.timeout}s per request")
        print("=" * 80)

        for idx, (source_key, source) in enumerate(SOURCES.items(), 1):
            print(f"\n[{idx}/{len(SOURCES)}] {source['name']}:")
            print(f"    Source Key: {source_key}")

            # Test main URL
            if 'url' in source and source['url']:
                ok, msg, details = self.validate_url(source['url'], 'html')
                status = "✅" if ok else "❌"
                print(f"    {status} URL: {msg}")

                if ok:
                    self.results['working'].append({
                        'key': source_key,
                        'name': source['name'],
                        'type': 'url',
                        'url': source['url'],
                        'message': msg,
                        'details': details
                    })
                else:
                    self.results['broken'].append({
                        'key': source_key,
                        'name': source['name'],
                        'type': 'url',
                        'url': source['url'],
                        'error': msg,
                        'details': details
                    })

            # Test RSS feed
            if 'rss' in source and source['rss']:
                ok, msg, details = self.validate_url(source['rss'], 'rss')
                status = "✅" if ok else "❌"
                print(f"    {status} RSS: {msg}")

                if ok:
                    self.results['working'].append({
                        'key': source_key,
                        'name': source['name'],
                        'type': 'rss',
                        'url': source['rss'],
                        'message': msg,
                        'details': details
                    })
                else:
                    self.results['broken'].append({
                        'key': source_key,
                        'name': source['name'],
                        'type': 'rss',
                        'url': source['rss'],
                        'error': msg,
                        'details': details
                    })

    def generate_report(self) -> bool:
        """
        Generate structured validation report

        Returns:
            bool: True if all URLs valid, False if any broken
        """
        print("\n" + "=" * 80)
        print("\n📊 VALIDATION RESULTS:")
        print("=" * 80)
        print(f"✅ Working URLs: {len(self.results['working'])}")
        print(f"❌ Broken URLs: {len(self.results['broken'])}")
        print(f"⚠️  Needs Manual Check: {len(self.results['needs_manual_check'])}")

        if self.results['broken']:
            print(f"\n🚨 BROKEN URLS (MUST FIX BEFORE DEPLOYMENT):")
            print("=" * 80)

            for item in self.results['broken']:
                print(f"\n  Source: {item['name']}")
                print(f"  Key: {item['key']}")
                print(f"  Type: {item['type']}")
                print(f"  URL: {item['url']}")
                print(f"  ❌ Error: {item['error']}")

                # Suggest fixes
                if '404' in item['error']:
                    print(f"  💡 Fix: Remove this URL or find correct endpoint")
                elif 'Timeout' in item['error']:
                    print(f"  💡 Fix: Check if site is accessible, may need longer timeout")
                elif 'RSS' in item['error']:
                    print(f"  💡 Fix: Use HTML scraping instead, or find correct RSS URL")

        # Save detailed JSON report
        report_path = '/root/repo/ingestion/source_validation_report.json'
        with open(report_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_sources': len(SOURCES),
                'working_count': len(self.results['working']),
                'broken_count': len(self.results['broken']),
                'results': self.results
            }, f, indent=2)

        print(f"\n💾 Detailed report saved: {report_path}")

        # Summary
        print("\n" + "=" * 80)
        if len(self.results['broken']) == 0:
            print("✅ SUCCESS: All URLs validated!")
            print("Ready for deployment.")
        else:
            print("❌ FAILURE: Broken URLs found!")
            print("Fix ALL broken URLs before proceeding with implementation.")
        print("=" * 80)

        return len(self.results['broken']) == 0

def main():
    """Run validation and exit with appropriate code"""
    print("\n" + "=" * 80)
    print("DroneWatch Source URL Validation")
    print("Anti-Hallucination Check: Verify ALL sources before deployment")
    print("=" * 80 + "\n")

    validator = SourceValidator()
    validator.validate_all()
    all_valid = validator.generate_report()

    # Exit with code 0 if all valid, 1 if any broken
    sys.exit(0 if all_valid else 1)

if __name__ == "__main__":
    main()
