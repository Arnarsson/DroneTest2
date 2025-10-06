#!/usr/bin/env python3
"""
Test script for geographic scope filtering
Verifies that is_nordic_incident() correctly filters out non-Nordic incidents
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import is_nordic_incident

# Test cases
test_cases = [
    {
        "name": "Copenhagen Airport (Danish incident)",
        "title": "Drone observation at Copenhagen Airport",
        "content": "Danish police reported drone activity at Kastrup airport",
        "lat": 55.618,
        "lon": 12.6476,
        "expected": True
    },
    {
        "name": "Oslo incident (Norwegian)",
        "title": "Drone spotted near Oslo",
        "content": "Norwegian authorities investigating drone near Gardermoen",
        "lat": 60.1939,
        "lon": 11.1004,
        "expected": True
    },
    {
        "name": "Stockholm incident (Swedish)",
        "title": "Drone incident in Stockholm",
        "content": "Swedish police investigating drone sighting",
        "lat": 59.3293,
        "lon": 18.0686,
        "expected": True
    },
    {
        "name": "Ukrainian incident (foreign)",
        "title": "Massivt droneangrep over hele Ukraina",
        "content": "Multiple drone attacks across Ukraine reported by Ukrainian authorities",
        "lat": 50.4501,
        "lon": 30.5234,
        "expected": False
    },
    {
        "name": "Munich incident (German)",
        "title": "Droner i München tvang Esbjerg-stjerner til at sove på gulvet",
        "content": "Danish article about drone incident in Munich, Germany",
        "lat": 48.1351,
        "lon": 11.5820,
        "expected": False
    },
    {
        "name": "Nordic news about Ukraine (no coords)",
        "title": "Massivt droneangrep over hele Ukraina",
        "content": "Norway reports on Ukrainian drone situation. Multiple attacks in Kiev and Odesa",
        "lat": None,
        "lon": None,
        "expected": False  # Should detect Ukraine mentions
    },
    {
        "name": "Copenhagen discussion (no coords)",
        "title": "Ministers meet in Copenhagen about security",
        "content": "European leaders gathering in Copenhagen to discuss defense, no mention of foreign locations",
        "lat": None,
        "lon": None,
        "expected": True  # Nordic location, no foreign mentions
    },
    {
        "name": "Nordic article mentioning Germany",
        "title": "Denmark responds to German drone policy",
        "content": "Danish government reacts to new regulations in Berlin and Munich",
        "lat": None,
        "lon": None,
        "expected": False  # Mentions Berlin/Munich
    },
    {
        "name": "Ukrainian incident with Nordic coords (context mention)",
        "title": "Massivt russisk droneangrep over hele Ukraina: – Det er farlig å gå ute i gatene",
        "content": "Multiple drone attacks across Ukraine. Danish officials comment on the situation from Copenhagen",
        "lat": 55.618,
        "lon": 12.6476,
        "expected": False  # Foreign incident despite Nordic coords from context
    }
]

def run_tests():
    """Run all test cases and report results"""
    print("="*80)
    print("GEOGRAPHIC SCOPE FILTER TESTS")
    print("="*80)

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        result = is_nordic_incident(test["title"], test["content"], test["lat"], test["lon"])
        status = "✅ PASS" if result == test["expected"] else "❌ FAIL"

        if result == test["expected"]:
            passed += 1
        else:
            failed += 1

        print(f"\n#{i}: {test['name']}")
        print(f"   Title: {test['title'][:60]}")
        print(f"   Coords: {test['lat']}, {test['lon']}")
        print(f"   Expected: {test['expected']}, Got: {result}")
        print(f"   {status}")

    print("\n" + "="*80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80)

    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
