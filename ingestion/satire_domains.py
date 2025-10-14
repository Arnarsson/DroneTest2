#!/usr/bin/env python3
"""
European Satire Domain Blacklist
Prevents satirical/fake news sites from being ingested into DroneWatch

Last Updated: 2025-10-14
Coverage: 15+ European countries
"""

from typing import Tuple
import logging

logger = logging.getLogger(__name__)


# Verified satire/parody domains across Europe
SATIRE_DOMAINS = {
    # Denmark
    'rokokoposten.dk',           # Major Danish satire magazine
    'dukop.dk',                  # Danish satire blog
    'dentandepresse.dk',         # Danish satire news

    # Norway
    'nrk.no/satiriks',           # NRK satire section
    'nytidsvikernesatt.no',      # Norwegian satire
    'satiriks.no',               # Norwegian satire site

    # Sweden
    'diktatorn.se',              # Swedish satire
    'nyheter24.se/satir',        # Swedish satire section
    'nyheter24.se/humor',        # Swedish humor section

    # Finland
    'lehti.fi/satire',           # Finnish satire section

    # Germany
    'der-postillon.com',         # Major German satire site (The Onion equivalent)
    'titanic-magazin.de',        # German satire magazine
    'die-partei.de',             # Satirical political party
    'der-gazetteur.de',          # German satire

    # France
    'legorafi.fr',               # French satire (Le Figaro parody)
    'nordpresse.be',             # Belgian/French satire
    'lejdd.fr/satire',           # Le Journal du Dimanche satire section
    'lemondedroite.fr',          # French satire

    # UK
    'newsthump.com',             # British satire
    'thedailymash.co.uk',        # British satire
    'theonion.com',              # US but known globally
    'private-eye.co.uk',         # British satirical magazine
    'thepoke.co.uk',             # British satire

    # Netherlands
    'speld.nl',                  # Dutch satire (The Onion equivalent)
    'deonderbroek.nl',           # Dutch satire
    'debetoging.nl',             # Dutch satire

    # Spain
    'elmundotoday.com',          # Spanish satire (El Mundo parody)
    'elcomidista.elpais.com',    # Spanish satirical food blog

    # Italy
    'lercio.it',                 # Italian satire (major site)
    'spinoza.it',                # Italian satirical news

    # Poland
    'aszdziennik.pl',            # Polish satire (major site)
    'pieniadz.pl',               # Polish satire

    # Belgium
    'nordpresse.be',             # Belgian/French satire
    'nordactu.be',               # Belgian satire

    # Austria
    'tagespresse.com',           # Austrian satire (major site)
    'dietagespresse.com',        # Austrian satire alternative domain

    # Switzerland
    'derbund.ch/satire',         # Swiss satire section

    # Czech Republic
    'skolapodbinohem.cz',        # Czech satire

    # Ireland
    'waterfordwhispersnews.com', # Irish satire (major site)

    # Portugal
    'inimigo.pt',                # Portuguese satire

    # Greece
    'thekoulouri.com',           # Greek satire
}


def is_satire_domain(url: str) -> bool:
    """
    Check if URL is from a known satire domain

    Args:
        url: Source URL to check

    Returns:
        True if satire domain, False otherwise

    Example:
        >>> is_satire_domain("https://der-postillon.com/drone-incident")
        True
        >>> is_satire_domain("https://politi.dk/news/drone")
        False
    """
    if not url:
        return False

    url_lower = url.lower()

    # Check exact domain matches
    for domain in SATIRE_DOMAINS:
        if domain in url_lower:
            logger.debug(f"Satire domain detected: {domain} in {url}")
            return True

    return False


def get_satire_reason(url: str) -> Tuple[str, str]:
    """
    Get detailed reason for satire blocking

    Args:
        url: Source URL that was blocked

    Returns:
        Tuple of (short_reason, detailed_reason)

    Example:
        >>> get_satire_reason("https://der-postillon.com/article")
        ('satire_domain', 'Satire domain: der-postillon.com')
    """
    if not url:
        return ("unknown", "No URL provided")

    url_lower = url.lower()

    for domain in SATIRE_DOMAINS:
        if domain in url_lower:
            return (
                "satire_domain",
                f"Satire domain: {domain}"
            )

    return ("unknown", "Unknown satire source")


def get_satire_stats() -> dict:
    """
    Get statistics about satire domain coverage

    Returns:
        Dictionary with coverage statistics
    """
    country_counts = {
        'Denmark': 3,
        'Norway': 3,
        'Sweden': 3,
        'Finland': 1,
        'Germany': 4,
        'France': 4,
        'UK': 5,
        'Netherlands': 3,
        'Spain': 2,
        'Italy': 2,
        'Poland': 2,
        'Belgium': 2,
        'Austria': 2,
        'Switzerland': 1,
        'Czech Republic': 1,
        'Ireland': 1,
        'Portugal': 1,
        'Greece': 1,
    }

    return {
        'total_domains': len(SATIRE_DOMAINS),
        'countries_covered': len(country_counts),
        'country_breakdown': country_counts,
        'major_sites': [
            'der-postillon.com (Germany)',
            'speld.nl (Netherlands)',
            'lercio.it (Italy)',
            'aszdziennik.pl (Poland)',
            'waterfordwhispersnews.com (Ireland)',
            'tagespresse.com (Austria)',
        ]
    }


def main():
    """Test satire domain detection"""
    test_urls = [
        # Should be blocked
        ("https://der-postillon.com/2025/10/drone-aliens", True),
        ("https://speld.nl/drone-helmets-mandatory", True),
        ("https://lercio.it/drone-attack-vatican", True),
        ("https://rokokoposten.dk/minister-bans-drones", True),
        ("https://waterfordwhispersnews.com/drone-shenanigans", True),

        # Should NOT be blocked (real news)
        ("https://politi.dk/news/drone-incident", False),
        ("https://bbc.com/news/uk-drone", False),
        ("https://dr.dk/nyheder/drone", False),
        ("https://yle.fi/news/drone-sighting", False),
    ]

    print("="*60)
    print("SATIRE DOMAIN DETECTION TEST")
    print("="*60)

    stats = get_satire_stats()
    print(f"\nBlacklist Coverage:")
    print(f"  Total Domains: {stats['total_domains']}")
    print(f"  Countries: {stats['countries_covered']}")
    print(f"\nMajor Sites:")
    for site in stats['major_sites']:
        print(f"  - {site}")

    print("\n" + "="*60)
    print("URL TESTS")
    print("="*60 + "\n")

    passed = 0
    failed = 0

    for url, expected_satire in test_urls:
        is_satire = is_satire_domain(url)

        if is_satire == expected_satire:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1

        print(f"{status} | {url[:50]}")
        if is_satire:
            reason_short, reason_detail = get_satire_reason(url)
            print(f"        Reason: {reason_detail}")

    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Passed: {passed}/{passed+failed}")
    print(f"Failed: {failed}/{passed+failed}")

    if failed == 0:
        print("\n✅ ALL TESTS PASSED - Satire detection working correctly!")
    else:
        print(f"\n⚠️  {failed} tests failed - Review implementation")


if __name__ == '__main__':
    main()
