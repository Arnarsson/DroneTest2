#!/usr/bin/env python3
"""
Test Evidence Scoring System
Validates the 4-tier evidence scoring logic across scrapers and verification module
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from verification import calculate_evidence_score_from_sources, has_official_quote
from utils import calculate_evidence_score

def test_evidence_scoring():
    """Test evidence scoring with various scenarios"""

    print("🧪 Testing Evidence Scoring System\n")
    print("=" * 60)

    # Test cases
    test_cases = [
        {
            "name": "Tier 4: Official Police Source",
            "sources": [{"trust_weight": 4, "source_type": "police", "name": "Copenhagen Police"}],
            "has_quote": False,
            "expected": 4
        },
        {
            "name": "Tier 3: Multiple Credible Sources",
            "sources": [
                {"trust_weight": 3, "source_type": "media", "name": "DR Nyheder"},
                {"trust_weight": 3, "source_type": "media", "name": "TV2 News"}
            ],
            "has_quote": False,
            "expected": 3
        },
        {
            "name": "Tier 3: Single Credible + Official Quote",
            "sources": [{"trust_weight": 3, "source_type": "media", "name": "DR Nyheder"}],
            "has_quote": True,
            "expected": 3
        },
        {
            "name": "Tier 2: Single Credible Source (No Quote)",
            "sources": [{"trust_weight": 2, "source_type": "media", "name": "TV2 Lorry"}],
            "has_quote": False,
            "expected": 2
        },
        {
            "name": "Tier 1: Low Trust Source",
            "sources": [{"trust_weight": 1, "source_type": "social", "name": "Twitter User"}],
            "has_quote": False,
            "expected": 1
        },
        {
            "name": "Tier 1: No Sources",
            "sources": [],
            "has_quote": False,
            "expected": 1
        },
        {
            "name": "Edge Case: trust_weight=3 without quote (only 1 source)",
            "sources": [{"trust_weight": 3, "source_type": "media", "name": "Single Source"}],
            "has_quote": False,
            "expected": 2  # Should be tier 2, not tier 3
        }
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   Sources: {len(test['sources'])}")
        if test['sources']:
            for src in test['sources']:
                print(f"   - {src['name']} (trust={src['trust_weight']})")
        print(f"   Has official quote: {test['has_quote']}")

        # Calculate score
        score = calculate_evidence_score_from_sources(test['sources'], test['has_quote'])

        # Check result
        if score == test['expected']:
            print(f"   ✅ PASS: Score = {score}")
            passed += 1
        else:
            print(f"   ❌ FAIL: Score = {score}, Expected = {test['expected']}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"\n📊 Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    if failed == 0:
        print("✅ All evidence scoring tests PASSED!")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1


def test_official_quote_detection():
    """Test official quote detection"""

    print("\n\n🧪 Testing Official Quote Detection\n")
    print("=" * 60)

    test_cases = [
        {
            "narrative": "Politiet bekræfter at en drone blev observeret",
            "expected": True,
            "reason": "Danish 'politiet bekræfter'"
        },
        {
            "narrative": "According to police, a drone was spotted near the airport",
            "expected": True,
            "reason": "English 'according to police'"
        },
        {
            "narrative": "The minister confirms increased drone activity",
            "expected": True,
            "reason": "Authority 'minister confirms'"
        },
        {
            "narrative": "A drone was seen flying over the area",
            "expected": False,
            "reason": "No official quote"
        },
        {
            "narrative": "Someone posted about a drone on social media",
            "expected": False,
            "reason": "Social media mention only"
        }
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        incident = {"narrative": test['narrative']}
        result = has_official_quote(incident)

        print(f"\n{i}. {test['reason']}")
        print(f"   Text: \"{test['narrative'][:60]}...\"")

        if result == test['expected']:
            print(f"   ✅ PASS: {result}")
            passed += 1
        else:
            print(f"   ❌ FAIL: Got {result}, Expected {test['expected']}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"\n📊 Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    return 0 if failed == 0 else 1


def test_utils_calculate_evidence():
    """Test the utils.py calculate_evidence_score function"""

    print("\n\n🧪 Testing utils.calculate_evidence_score\n")
    print("=" * 60)

    test_cases = [
        {"trust": 4, "has_official": False, "expected": 4, "desc": "Trust 4 (official)"},
        {"trust": 3, "has_official": True, "expected": 3, "desc": "Trust 3 + quote"},
        {"trust": 3, "has_official": False, "expected": 2, "desc": "Trust 3 no quote"},
        {"trust": 2, "has_official": True, "expected": 2, "desc": "Trust 2 + quote"},
        {"trust": 2, "has_official": False, "expected": 2, "desc": "Trust 2 no quote"},
        {"trust": 1, "has_official": False, "expected": 1, "desc": "Trust 1"},
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        score = calculate_evidence_score(test['trust'], test['has_official'])

        print(f"\n{i}. {test['desc']}")
        print(f"   trust_weight={test['trust']}, has_official={test['has_official']}")

        if score == test['expected']:
            print(f"   ✅ PASS: Score = {score}")
            passed += 1
        else:
            print(f"   ❌ FAIL: Score = {score}, Expected = {test['expected']}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"\n📊 Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    print("\n" + "🎯" * 30)
    print("DRONEWATCH EVIDENCE SCORING TEST SUITE")
    print("🎯" * 30 + "\n")

    # Run all test suites
    exit_code = 0
    exit_code |= test_evidence_scoring()
    exit_code |= test_official_quote_detection()
    exit_code |= test_utils_calculate_evidence()

    print("\n" + "=" * 60)
    if exit_code == 0:
        print("\n✅ ALL TESTS PASSED - Evidence Scoring System is VERIFIED!\n")
    else:
        print("\n❌ SOME TESTS FAILED - Please review the implementation\n")

    sys.exit(exit_code)
