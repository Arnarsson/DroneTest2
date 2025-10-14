"""
Nordic Source Verification Script
Tests all RSS feeds and reports status
"""
import requests
import feedparser
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import time

def verify_rss_feed(url: str, timeout: int = 10) -> Tuple[bool, str, Dict]:
    """
    Verify an RSS feed is working and parseable.

    Returns:
        (is_working, status_message, metadata)
    """
    metadata = {
        "http_status": None,
        "entry_count": 0,
        "recent_entries": 0,
        "latest_date": None,
        "parse_error": False
    }

    try:
        # HTTP health check
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        metadata["http_status"] = response.status_code

        if response.status_code not in [200, 301, 302, 304]:
            return False, f"HTTP {response.status_code}", metadata

        # Parse RSS feed
        feed = feedparser.parse(url)

        if feed.bozo:
            metadata["parse_error"] = True
            return False, f"Feed parsing error: {feed.bozo_exception}", metadata

        if not feed.entries:
            return False, "No entries found", metadata

        metadata["entry_count"] = len(feed.entries)

        # Check for recent entries (within 30 days)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_count = 0
        latest_date = None

        for entry in feed.entries:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                entry_date = datetime(*entry.published_parsed[:6])
                if entry_date > recent_cutoff:
                    recent_count += 1
                if not latest_date or entry_date > latest_date:
                    latest_date = entry_date
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                entry_date = datetime(*entry.updated_parsed[:6])
                if entry_date > recent_cutoff:
                    recent_count += 1
                if not latest_date or entry_date > latest_date:
                    latest_date = entry_date

        metadata["recent_entries"] = recent_count
        metadata["latest_date"] = latest_date.isoformat() if latest_date else None

        if recent_count == 0:
            return False, f"No recent entries (last: {latest_date.strftime('%Y-%m-%d') if latest_date else 'unknown'})", metadata

        return True, "Working", metadata

    except requests.exceptions.Timeout:
        return False, "Timeout", metadata
    except requests.exceptions.ConnectionError:
        return False, "Connection error", metadata
    except Exception as e:
        return False, f"Error: {str(e)[:50]}", metadata


def test_swedish_police_regions():
    """Test all Swedish police regions"""
    regions = [
        "vastra-gotaland",
        "uppsala",
        "sodermanland",
        "ostergotland",
        "jonkoping",
        "kronoberg",
        "kalmar",
        "gotland",
        "blekinge",
        "halland",
        "varmland",
        "orebro",
        "vastmanland",
        "dalarna",
        "gavleborg",
        "vasternorrland",
        "jamtland",
        "vasterbotten"
    ]

    results = []
    print("\n" + "="*80)
    print("WAVE 2: SWEDISH POLICE REGIONS")
    print("="*80)

    for region in regions:
        url = f"https://polisen.se/aktuellt/rss/{region}/handelser-rss---{region}/"
        print(f"\nTesting: Polisen {region.title()}")
        print(f"URL: {url}")

        is_working, status, metadata = verify_rss_feed(url)

        result = {
            "region": region,
            "url": url,
            "working": is_working,
            "status": status,
            "metadata": metadata
        }
        results.append(result)

        print(f"Status: {status}")
        if is_working:
            print(f"✅ Entries: {metadata['entry_count']}, Recent: {metadata['recent_entries']}")
        else:
            print(f"❌ Failed: {status}")

        time.sleep(0.5)  # Rate limiting

    return results


def test_finnish_police_departments():
    """Test Finnish police departments"""
    departments = [
        ("eastern-finland", "Eastern Finland"),
        ("lapland", "Lapland"),
        ("oulu", "Oulu"),
        ("central-finland", "Central Finland"),
        ("western-finland", "Western Finland")
    ]

    results = []
    print("\n" + "="*80)
    print("WAVE 3: FINNISH POLICE DEPARTMENTS")
    print("="*80)

    # Test direct RSS URLs
    base_urls = [
        "https://poliisi.fi/en/{dept}/-/asset_publisher/ZtAEeHB39Lxr/rss",
        "https://poliisi.fi/{dept}/-/asset_publisher/ZtAEeHB39Lxr/rss"
    ]

    for dept_slug, dept_name in departments:
        print(f"\nTesting: Poliisi {dept_name}")

        working_url = None
        for base_url in base_urls:
            url = base_url.format(dept=dept_slug)
            print(f"Trying: {url}")

            is_working, status, metadata = verify_rss_feed(url)

            if is_working:
                working_url = url
                print(f"✅ Working: {status}")
                print(f"   Entries: {metadata['entry_count']}, Recent: {metadata['recent_entries']}")
                break
            else:
                print(f"❌ Failed: {status}")

        result = {
            "department": dept_name,
            "slug": dept_slug,
            "working_url": working_url,
            "working": working_url is not None
        }
        results.append(result)

        time.sleep(0.5)

    return results


def test_norwegian_media():
    """Test Norwegian media sources"""
    sources = [
        ("https://www.dagbladet.no/rss", "Dagbladet"),
        ("https://www.tv2.no/rss", "TV2 Norway"),
        ("https://www.nettavisen.no/rss", "Nettavisen")
    ]

    results = []
    print("\n" + "="*80)
    print("WAVE 4: NORWEGIAN MEDIA")
    print("="*80)

    for url, name in sources:
        print(f"\nTesting: {name}")
        print(f"URL: {url}")

        is_working, status, metadata = verify_rss_feed(url)

        result = {
            "name": name,
            "url": url,
            "working": is_working,
            "status": status,
            "metadata": metadata
        }
        results.append(result)

        print(f"Status: {status}")
        if is_working:
            print(f"✅ Entries: {metadata['entry_count']}, Recent: {metadata['recent_entries']}")
        else:
            print(f"❌ Failed: {status}")

        time.sleep(0.5)

    return results


def test_danish_twitter_feeds():
    """Test disabled Danish Twitter RSS.app feeds"""
    # Sources from config.py that are disabled
    disabled_sources = [
        ("twitter_syd_sonderjyllands_politi", "PLACEHOLDER_RSS_APP_URL_HERE", "Syd- og Sønderjyllands Politi"),
        ("twitter_midt_vestsjaellands_politi", "PLACEHOLDER_RSS_APP_URL_HERE", "Midt- og Vestsjællands Politi"),
        ("twitter_sydsjaellands_lolland_falster_politi", "PLACEHOLDER_RSS_APP_URL_HERE", "Sydsjællands og Lolland-Falsters Politi")
    ]

    results = []
    print("\n" + "="*80)
    print("WAVE 1: DANISH TWITTER SOURCES (RSS.app)")
    print("="*80)
    print("\n⚠️  These sources have placeholder URLs and need RSS.app feed generation")
    print("Action required: Create feeds at https://rss.app for these Twitter handles:")

    for key, placeholder_url, name in disabled_sources:
        print(f"\n{name} (key: {key})")
        print(f"  Current URL: {placeholder_url}")
        print(f"  Status: DISABLED - Needs RSS.app feed URL")

        result = {
            "key": key,
            "name": name,
            "status": "PLACEHOLDER",
            "action_required": "Generate RSS.app feed"
        }
        results.append(result)

    return results


def generate_report(swedish_results, finnish_results, norwegian_results, danish_results):
    """Generate summary report"""
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)

    # Swedish Police
    swedish_working = sum(1 for r in swedish_results if r["working"])
    print(f"\n1. Swedish Police Regions: {swedish_working}/{len(swedish_results)} working")
    print("   Working feeds:")
    for r in swedish_results:
        if r["working"]:
            print(f"   ✅ {r['region'].title()}: {r['metadata']['recent_entries']} recent entries")
    print("   Failed feeds:")
    for r in swedish_results:
        if not r["working"]:
            print(f"   ❌ {r['region'].title()}: {r['status']}")

    # Finnish Police
    finnish_working = sum(1 for r in finnish_results if r["working"])
    print(f"\n2. Finnish Police Departments: {finnish_working}/{len(finnish_results)} working")
    if finnish_working > 0:
        print("   Working feeds:")
        for r in finnish_results:
            if r["working"]:
                print(f"   ✅ {r['department']}: {r['working_url']}")
    else:
        print("   ❌ No working feeds found - may need alternative URL patterns")

    # Norwegian Media
    norwegian_working = sum(1 for r in norwegian_results if r["working"])
    print(f"\n3. Norwegian Media: {norwegian_working}/{len(norwegian_results)} working")
    print("   Working feeds:")
    for r in norwegian_results:
        if r["working"]:
            print(f"   ✅ {r['name']}: {r['metadata']['recent_entries']} recent entries")
    print("   Failed feeds:")
    for r in norwegian_results:
        if not r["working"]:
            print(f"   ❌ {r['name']}: {r['status']}")

    # Danish Twitter
    print(f"\n4. Danish Twitter Sources: {len(danish_results)} requiring action")
    print("   All sources need RSS.app feed generation (see WAVE 1 output above)")

    # Total Summary
    total_new = swedish_working + finnish_working + norwegian_working
    print(f"\n" + "="*80)
    print(f"TOTAL NEW SOURCES READY TO ADD: {total_new}")
    print(f"  - Swedish Police: {swedish_working}")
    print(f"  - Finnish Police: {finnish_working}")
    print(f"  - Norwegian Media: {norwegian_working}")
    print(f"  - Danish Twitter: 0 (requires manual RSS.app setup)")
    print("="*80)


if __name__ == "__main__":
    print("="*80)
    print("NORDIC SOURCE VERIFICATION - Complete Coverage")
    print("Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)

    # Run all tests
    danish_results = test_danish_twitter_feeds()
    swedish_results = test_swedish_police_regions()
    finnish_results = test_finnish_police_departments()
    norwegian_results = test_norwegian_media()

    # Generate report
    generate_report(swedish_results, finnish_results, norwegian_results, danish_results)

    print("\n✅ Verification complete. Review results above.")
