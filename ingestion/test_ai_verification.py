#!/usr/bin/env python3
"""
Test AI Verification Layer
Tests the AI-powered incident verification with real Copenhagen incidents
"""
import os
import sys
from openai_client import OpenAIClient, OpenAIClientError

# Test cases from Copenhagen incidents
TEST_CASES = [
    {
        'title': 'Copenhagen Airport - Major Drone Disruption',
        'narrative': 'Copenhagen Airport experienced significant disruptions on December 23-24, 2024, when 2-3 drones were observed flying over the airport area. The incident led to a 4-hour suspension of flight operations, affecting dozens of flights. Airport authorities and police investigated the incident, which occurred during the busy Christmas travel period.',
        'location': 'Copenhagen Airport',
        'expected': 'incident',
        'should_pass': True
    },
    {
        'title': 'Kastrup Airbase - Brief Airspace Closure',
        'narrative': 'Kastrup military airbase reported drone activity in the vicinity, leading to a brief airspace closure. Military authorities detected unidentified aerial objects near the base perimeter. The incident was investigated by defense officials.',
        'location': 'Kastrup Airbase, Copenhagen',
        'expected': 'incident',
        'should_pass': True
    },
    {
        'title': 'Mange ministre kommer til byen - giver nyt droneforbud',
        'narrative': 'EU-formandskabet i København giver anledning til nyt droneforbud. Flere ministre kommer til byen i forbindelse med mødet, og myndighederne indføre nye restriktioner for droner i området.',
        'location': 'Copenhagen',
        'expected': 'policy',
        'should_pass': False
    },
    {
        'title': 'Frigate, Radars, Troops Rushed To Copenhagen To Defend Against Mystery Drones',
        'narrative': 'In response to increased drone activity, military assets including a frigate, radar systems, and additional troops have been deployed to Copenhagen to bolster air defense. The deployment comes as part of increased security measures.',
        'location': 'Copenhagen',
        'expected': 'defense',
        'should_pass': False
    }
]


def test_ai_verification():
    """Test AI verification with Copenhagen incidents"""
    print("=" * 80)
    print("TESTING AI VERIFICATION LAYER")
    print("=" * 80)
    print()

    # Check if API key is configured
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: No API key configured")
        print("   Set OPENROUTER_API_KEY or OPENAI_API_KEY environment variable")
        return False

    print(f"✓ API key configured: {api_key[:10]}...")
    print()

    # Initialize client
    try:
        client = OpenAIClient()
        print(f"✓ OpenAI client initialized")
        print(f"  Using: {'OpenRouter' if client.use_openrouter else 'OpenAI'}")
        print(f"  Model: {client.model_name}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False

    # Test each case
    passed = 0
    failed = 0

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"Test {i}/{len(TEST_CASES)}: {test_case['title'][:60]}")
        print("-" * 80)

        try:
            result = client.verify_incident(
                test_case['title'],
                test_case['narrative'],
                test_case['location']
            )

            # Display result
            print(f"  is_incident: {result['is_incident']}")
            print(f"  category: {result['category']}")
            print(f"  confidence: {result['confidence']}")
            print(f"  reasoning: {result['reasoning']}")

            # Check if result matches expectation
            category_match = result['category'] == test_case['expected']
            pass_match = result['is_incident'] == test_case['should_pass']

            if category_match and pass_match:
                print(f"  ✅ PASS: Correctly classified as {result['category']}")
                passed += 1
            else:
                print(f"  ❌ FAIL: Expected {test_case['expected']}, got {result['category']}")
                print(f"         Expected is_incident={test_case['should_pass']}, got {result['is_incident']}")
                failed += 1

        except OpenAIClientError as e:
            print(f"  ❌ FAIL: API error - {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ FAIL: Unexpected error - {e}")
            failed += 1

        print()

    # Summary
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Total tests: {len(TEST_CASES)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success rate: {(passed / len(TEST_CASES)) * 100:.1f}%")
    print()

    if failed == 0:
        print("🎉 All tests passed! AI verification is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Review the results above.")
        return False


if __name__ == "__main__":
    success = test_ai_verification()
    sys.exit(0 if success else 1)
