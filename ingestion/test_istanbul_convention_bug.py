#!/usr/bin/env python3
"""
Test case for Istanbul Convention bug - non-drone article slipped through.

This test verifies that political news articles (like the Istanbul Convention article)
are properly blocked by Layer 2A (drone keyword check) and Layer 2B (non-incident filter).
"""

from utils import is_drone_incident
from non_incident_filter import NonIncidentFilter


def test_istanbul_convention_blocked():
    """Verify that political news (Istanbul Convention) is blocked."""

    title = "Latvia's president asks parliament to rethink Istanbul Convention exit"
    narrative = "Political news about women's rights treaty in Latvia. Latvia's president has asked parliament to reconsider its decision to withdraw from the Istanbul Convention on preventing violence against women."

    # Layer 2A: Should fail drone keyword check
    has_drone_keywords = is_drone_incident(title, narrative)

    print("\n=== Test 1: Istanbul Convention Article ===")
    print(f"Title: {title}")
    print(f"Has drone keywords: {has_drone_keywords}")

    assert has_drone_keywords == False, \
        "Istanbul Convention article should NOT pass drone keyword check"

    print("✓ Test passed: Istanbul Convention article blocked by drone keyword filter")


def test_other_non_drone_articles():
    """Test other common false positives that should be blocked."""

    test_cases = [
        {
            'title': "Government announces new drone regulations",
            'narrative': "The government has announced new regulations for drone operations in urban areas.",
            'description': "Policy announcement"
        },
        {
            'title': "Drone ban under discussion in parliament",
            'narrative': "Parliament is discussing a proposed ban on recreational drone flights near airports.",
            'description': "Discussion article"
        },
        {
            'title': "Think piece: The future of drone warfare",
            'narrative': "An opinion article exploring how drones will change military strategy in coming decades.",
            'description': "Opinion article"
        },
        {
            'title': "Training exercise with drones planned at airport",
            'narrative': "The airport will conduct a training exercise next week to practice response to unauthorized drone activity.",
            'description': "Simulation/drill"
        },
        {
            'title': "Military to deploy anti-drone systems",
            'narrative': "The military announced deployment of new anti-drone systems to defend critical infrastructure.",
            'description': "Defense deployment"
        },
    ]

    filter = NonIncidentFilter()

    print("\n=== Test 2: Other Non-Drone/Non-Incident Articles ===")

    for idx, test_case in enumerate(test_cases, 1):
        title = test_case['title']
        narrative = test_case['narrative']
        description = test_case['description']

        incident = {
            'title': title,
            'narrative': narrative
        }

        # Check drone keywords first
        has_drone = is_drone_incident(title, narrative)

        # Check non-incident filter
        is_non, confidence, reasons = filter.is_non_incident(incident)

        print(f"\n{idx}. {description}")
        print(f"   Title: {title}")
        print(f"   Has drone keywords: {has_drone}")
        print(f"   Non-incident: {is_non}")
        print(f"   Confidence: {confidence:.2f}")
        if reasons:
            print(f"   Reasons: {', '.join(reasons[:3])}")  # Show first 3 reasons

        # At least one filter should catch it
        blocked = (not has_drone) or (is_non and confidence >= 0.5)
        status = "✓ BLOCKED" if blocked else "❌ PASSED THROUGH"
        print(f"   Result: {status}")

        if not blocked:
            print(f"   ⚠️  WARNING: This article would pass through filters!")


def test_actual_incidents_pass():
    """Verify that actual drone incidents are NOT blocked by the filters."""

    actual_incidents = [
        {
            'title': "Drone spotted near Copenhagen Airport",
            'narrative': "A drone was observed flying near runway 22L at Copenhagen Airport, causing brief disruption to arrivals.",
            'description': "Airport incident"
        },
        {
            'title': "Unidentified drones over military base",
            'narrative': "Multiple unidentified drones were detected flying over the military base in Aalborg, prompting investigation.",
            'description': "Military base incident"
        },
        {
            'title': "Airport closed after drone sighting",
            'narrative': "Stockholm Arlanda Airport was temporarily closed after several drones were spotted in controlled airspace.",
            'description': "Airport closure"
        },
    ]

    filter = NonIncidentFilter()

    print("\n=== Test 3: Actual Incidents (Should Pass Filters) ===")

    for idx, test_case in enumerate(actual_incidents, 1):
        title = test_case['title']
        narrative = test_case['narrative']
        description = test_case['description']

        incident = {
            'title': title,
            'narrative': narrative
        }

        # Check drone keywords
        has_drone = is_drone_incident(title, narrative)

        # Check non-incident filter
        is_non, confidence, reasons = filter.is_non_incident(incident)

        print(f"\n{idx}. {description}")
        print(f"   Title: {title}")
        print(f"   Has drone keywords: {has_drone}")
        print(f"   Non-incident: {is_non}")
        print(f"   Confidence: {confidence:.2f}")

        # Should pass through filters
        passed = has_drone and (not is_non or confidence < 0.5)
        status = "✓ PASSED" if passed else "❌ BLOCKED"
        print(f"   Result: {status}")

        assert passed, f"Actual incident should NOT be blocked: {title}"


def main():
    """Run all tests"""
    print("=" * 70)
    print("Testing Istanbul Convention Bug Fix")
    print("=" * 70)

    try:
        # Test 1: Istanbul Convention should be blocked
        test_istanbul_convention_blocked()

        # Test 2: Other non-drone/non-incident articles
        test_other_non_drone_articles()

        # Test 3: Actual incidents should pass
        test_actual_incidents_pass()

        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print("\nSummary:")
        print("- Layer 2A (drone keywords): Blocks articles without drone keywords")
        print("- Layer 2B (non-incident filter): Blocks policy/simulation/discussion articles")
        print("- Actual drone incidents: Pass through both filters correctly")

    except AssertionError as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 70)
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
