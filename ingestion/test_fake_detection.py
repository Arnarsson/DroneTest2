#!/usr/bin/env python3
"""
Comprehensive Fake Detection Test Suite
Tests all quality control layers with 30 known fake incidents

Coverage:
- Layer 1: Satire domain blacklist (10 tests)
- Layer 2: Simulation/drill keyword detection (10 tests)
- Layer 3: Policy announcement detection (5 tests)
- Layer 4: Historical/temporal validation (5 tests)

Target: 100% blocking rate for known fakes
"""
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple

from non_incident_filter import NonIncidentFilter
from satire_domains import is_satire_domain, get_satire_reason

# Import is_recent_incident manually to avoid dateutil dependency
def is_recent_incident(occurred_at: datetime, max_age_days: int = 7) -> Tuple[bool, str]:
    """Check if incident occurred within acceptable timeframe"""
    if not occurred_at.tzinfo:
        occurred_at = occurred_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    age = now - occurred_at
    age_days = age.days

    # Check: Future date
    if occurred_at > now + timedelta(days=1):
        return (False, f"Future date: {occurred_at.isoformat()}")

    # Check: Ancient history (>1 year)
    if age_days > 365:
        return (False, f"Historical article: {age_days} days ago ({age_days // 365} years)")

    # Check: Too old
    if age_days > max_age_days:
        return (False, f"Too old: {age_days} days ago (max {max_age_days})")

    return (True, "Recent incident")


# Test dataset: 30 known fakes across 4 categories
FAKE_INCIDENTS = [
    # ========================================
    # SATIRE DOMAIN TESTS (10 tests)
    # ========================================
    {
        "title": "Aliens Use Drones to Monitor Earth Leaders",
        "narrative": "Extraterrestrial beings spotted using advanced drones over government buildings...",
        "sources": [{"source_url": "https://der-postillon.com/2025/10/aliens-drones"}],
        "expected_block": "satire_domain",
        "expected_reason": "der-postillon.com",
        "description": "German satire site - absurd claim"
    },
    {
        "title": "Government Announces Mandatory Drone Helmets for All Citizens",
        "narrative": "New law requires all drones to wear safety helmets starting next month...",
        "sources": [{"source_url": "https://speld.nl/2025/drone-helmets-mandatory"}],
        "expected_block": "satire_domain",
        "expected_reason": "speld.nl",
        "description": "Dutch satire site - absurd regulation"
    },
    {
        "title": "Pope's Blessing Drone Malfunctions During Vatican Ceremony",
        "narrative": "The Vatican's new blessing drone crashed into St. Peter's Basilica...",
        "sources": [{"source_url": "https://lercio.it/drone-blessing-vatican"}],
        "expected_block": "satire_domain",
        "expected_reason": "lercio.it",
        "description": "Italian satire site - absurd incident"
    },
    {
        "title": "Danish Minister Proposes Drone Tax Based on Wing Size",
        "narrative": "New proposal would tax drones €10 per centimeter of wingspan...",
        "sources": [{"source_url": "https://rokokoposten.dk/drone-wing-tax"}],
        "expected_block": "satire_domain",
        "expected_reason": "rokokoposten.dk",
        "description": "Danish satire site - absurd policy"
    },
    {
        "title": "Irish Leprechauns Using Drones to Protect Gold",
        "narrative": "Mythical creatures adopting modern technology for security...",
        "sources": [{"source_url": "https://waterfordwhispersnews.com/leprechaun-drones"}],
        "expected_block": "satire_domain",
        "expected_reason": "waterfordwhispersnews.com",
        "description": "Irish satire site - folklore parody"
    },
    {
        "title": "Austrian Government Bans Drones from Making Eye Contact",
        "narrative": "New regulation prohibits drones from staring at pedestrians...",
        "sources": [{"source_url": "https://tagespresse.com/drone-eye-contact-ban"}],
        "expected_block": "satire_domain",
        "expected_reason": "tagespresse.com",
        "description": "Austrian satire site - absurd law"
    },
    {
        "title": "Polish Scientists Teach Drones to Speak",
        "narrative": "Breakthrough technology enables drones to communicate verbally...",
        "sources": [{"source_url": "https://aszdziennik.pl/talking-drones"}],
        "expected_block": "satire_domain",
        "expected_reason": "aszdziennik.pl",
        "description": "Polish satire site - fake technology"
    },
    {
        "title": "UK Pub Owner Uses Drone to Deliver Pints to Customers",
        "narrative": "Revolutionary beer delivery system causes hilarious mishaps...",
        "sources": [{"source_url": "https://newsthump.com/beer-delivery-drone"}],
        "expected_block": "satire_domain",
        "expected_reason": "newsthump.com",
        "description": "British satire site - absurd business"
    },
    {
        "title": "Spanish Bull Fighting Drones Introduced in Barcelona",
        "narrative": "Animal rights activists celebrate humane alternative to bullfighting...",
        "sources": [{"source_url": "https://elmundotoday.com/bull-fighting-drones"}],
        "expected_block": "satire_domain",
        "expected_reason": "elmundotoday.com",
        "description": "Spanish satire site - cultural parody"
    },
    {
        "title": "French Government Requires Drones to Carry Baguettes",
        "narrative": "New law mandates all drones display French cultural symbols...",
        "sources": [{"source_url": "https://legorafi.fr/drones-baguettes"}],
        "expected_block": "satire_domain",
        "expected_reason": "legorafi.fr",
        "description": "French satire site - cultural stereotype"
    },

    # ========================================
    # SIMULATION/DRILL TESTS (10 tests)
    # ========================================
    {
        "title": "NATO Conducts Counter-Drone Exercise at Oslo Airport",
        "narrative": "Military forces practice drone interception during planned exercise. Training scenario simulates coordinated attack...",
        "sources": [{"source_url": "https://forsvaret.no/exercise-2025"}],
        "expected_block": "simulation",
        "expected_keywords": ["exercise", "planned", "training", "scenario"],
        "description": "Military exercise with multiple simulation keywords"
    },
    {
        "title": "Frankfurt Airport Holds Anti-Drone Training Drill",
        "narrative": "Airport security tests new counter-drone systems in simulated attack scenario. The drill lasted 3 hours...",
        "sources": [{"source_url": "https://fraport.de/training-2025"}],
        "expected_block": "simulation",
        "expected_keywords": ["training", "drill", "simulated"],
        "description": "Airport drill with simulation language"
    },
    {
        "title": "Swedish Military Tests New Drone Defense System",
        "narrative": "Försvarsmakten conducts test of anti-drone technology at Arlanda. Demonstration shows capabilities...",
        "sources": [{"source_url": "https://forsvarsmakten.se/test-2025"}],
        "expected_block": "simulation",
        "expected_keywords": ["test", "demonstration"],
        "description": "Defense system test with demonstration"
    },
    {
        "title": "Copenhagen Airport Lufthavnsøvelse - Counter-Drone Practice",
        "narrative": "Kastrup gennemfører træningsøvelse for at teste beredskapsprocedurer mod droner...",
        "sources": [{"source_url": "https://cph.dk/ovelse-2025"}],
        "expected_block": "simulation",
        "expected_keywords": ["øvelse", "træning"],
        "description": "Danish drill with native keywords"
    },
    {
        "title": "Helsinki Airport Drone Detection Harjoitus",
        "narrative": "Helsinki-Vantaa airport conducts harjoitus to test drone detection systems. Simulaatio lasted all day...",
        "sources": [{"source_url": "https://finavia.fi/harjoitus-2025"}],
        "expected_block": "simulation",
        "expected_keywords": ["harjoitus", "simulaatio"],
        "description": "Finnish exercise with native keywords"
    },
    {
        "title": "Polish Air Force Ćwiczenia Wojskowe - Drone Defense",
        "narrative": "Siły Powietrzne conduct ćwiczenia to practice counter-drone tactics. Szkolenie includes multiple scenarios...",
        "sources": [{"source_url": "https://wojsko-polskie.pl/cwiczenia"}],
        "expected_block": "simulation",
        "expected_keywords": ["ćwiczenia", "szkolenie"],
        "description": "Polish military exercise with native keywords"
    },
    {
        "title": "Dutch Airport Oefening - Emergency Response Practice",
        "narrative": "Schiphol holds oefening to test emergency procedures. Training includes simulatie of drone threat...",
        "sources": [{"source_url": "https://schiphol.nl/oefening-2025"}],
        "expected_block": "simulation",
        "expected_keywords": ["oefening", "training", "simulatie"],
        "description": "Dutch drill with native keywords"
    },
    {
        "title": "Military Manöver Tests Drone Interception Übung",
        "narrative": "Bundeswehr conducts übung at Berlin airport. The demonstration shows new capabilities...",
        "sources": [{"source_url": "https://bundeswehr.de/uebung-2025"}],
        "expected_block": "simulation",
        "expected_keywords": ["manöver", "übung", "demonstration"],
        "description": "German exercise with native keywords"
    },
    {
        "title": "Paris Airport Exercice Militaire - Drone Defense",
        "narrative": "Charles de Gaulle hosts exercice to test counter-drone measures. Entraînement includes simulation...",
        "sources": [{"source_url": "https://aeroports-paris.fr/exercice"}],
        "expected_block": "simulation",
        "expected_keywords": ["exercice", "entraînement", "simulation"],
        "description": "French exercise with native keywords"
    },
    {
        "title": "Mock Drone Attack Planned for London Heathrow Rehearsal",
        "narrative": "Airport authorities will rehearse emergency procedures. The practice scenario simulates coordinated threat...",
        "sources": [{"source_url": "https://heathrow.com/rehearsal-2025"}],
        "expected_block": "simulation",
        "expected_keywords": ["mock", "rehearsal", "practice", "simulates"],
        "description": "British rehearsal with multiple simulation terms"
    },

    # ========================================
    # POLICY ANNOUNCEMENT TESTS (5 tests)
    # ========================================
    {
        "title": "Copenhagen Municipality Announces New Drone Ban for City Center",
        "narrative": "Starting next month, drones will be prohibited in central Copenhagen. The new restriction aims to protect privacy...",
        "sources": [{"source_url": "https://kk.dk/drone-ban-2025"}],
        "expected_block": "policy",
        "expected_keywords": ["ban", "prohibited", "restriction"],
        "description": "Municipal drone ban announcement"
    },
    {
        "title": "Norway Introduces Stricter Drone Regulations",
        "narrative": "Government proposes new legislation to regulate drone flights. The law will require registration...",
        "sources": [{"source_url": "https://regjeringen.no/drone-regulations"}],
        "expected_block": "policy",
        "expected_keywords": ["regulations", "legislation", "law"],
        "description": "National regulatory announcement"
    },
    {
        "title": "Germany Plans Temporary Flight Restriction for Upcoming Summit",
        "narrative": "Luftraumbeschränkung will be implemented during G7 meeting. No-fly zone covers 50km radius...",
        "sources": [{"source_url": "https://bmvi.de/tfr-g7"}],
        "expected_block": "policy",
        "expected_keywords": ["restriction", "no-fly zone", "temporary"],
        "description": "Temporary restriction announcement"
    },
    {
        "title": "EU Drone Rules to be Harmonized Across Member States",
        "narrative": "European Commission announces new regulatory framework. The rules will standardize drone operations...",
        "sources": [{"source_url": "https://ec.europa.eu/drone-rules"}],
        "expected_block": "policy",
        "expected_keywords": ["rules", "regulatory", "framework"],
        "description": "International policy coordination"
    },
    {
        "title": "Swedish Aviation Authority Issues Drone Advisory for Winter",
        "narrative": "Transportstyrelsen releases new guidelines for cold weather operations. The advisory recommends safety measures...",
        "sources": [{"source_url": "https://transportstyrelsen.se/drone-advisory"}],
        "expected_block": "policy",
        "expected_keywords": ["advisory", "guidelines", "recommends"],
        "description": "Safety advisory announcement"
    },

    # ========================================
    # HISTORICAL/TEMPORAL TESTS (5 tests)
    # ========================================
    {
        "title": "Gatwick Airport Drone Incident - December 2018",
        "narrative": "Major disruption caused by drone sightings shut down airport for three days. Thousands of passengers affected...",
        "sources": [{"source_url": "https://bbc.com/news/gatwick-2018"}],
        "occurred_at": "2018-12-20T10:00:00Z",
        "expected_block": "temporal",
        "expected_reason": "Historical article (>30 days old)",
        "description": "Famous 2018 Gatwick incident - too old"
    },
    {
        "title": "2017 Swedish Nuclear Power Plant Drone Incident",
        "narrative": "Drones spotted over Ringhals nuclear facility in 2017. Investigation never found perpetrators...",
        "sources": [{"source_url": "https://svt.se/ringhals-2017"}],
        "occurred_at": "2017-08-15T14:30:00Z",
        "expected_block": "temporal",
        "expected_reason": "Historical article (>30 days old)",
        "description": "2017 nuclear plant incident - too old"
    },
    {
        "title": "Future Drone Conference Scheduled for Next Year",
        "narrative": "Major drone security summit planned for March 2026. Experts will discuss threats...",
        "sources": [{"source_url": "https://drone-conference.eu/2026"}],
        "occurred_at": "2026-03-15T09:00:00Z",
        "expected_block": "temporal",
        "expected_reason": "Future-dated article",
        "description": "Future event - invalid date"
    },
    {
        "title": "Last Year's Oslo Airport Closure - Anniversary Report",
        "narrative": "Looking back at last year's drone incident that closed Oslo Airport. One year later, lessons learned...",
        "sources": [{"source_url": "https://nrk.no/anniversary-report"}],
        "occurred_at": (datetime.now(timezone.utc) - timedelta(days=400)).isoformat(),
        "expected_block": "temporal",
        "expected_reason": "Historical article (>30 days old)",
        "description": "Anniversary report - too old"
    },
    {
        "title": "2019 Frankfurt Airport Drone Sighting",
        "narrative": "Drone sighting caused brief delay in 2019. Airport resumed operations after 30 minutes...",
        "sources": [{"source_url": "https://fraport.de/incident-2019"}],
        "occurred_at": "2019-07-10T16:45:00Z",
        "expected_block": "temporal",
        "expected_reason": "Historical article (>30 days old)",
        "description": "2019 incident - too old"
    },
]


def test_satire_detection() -> Tuple[int, int, List[str]]:
    """Test satire domain blacklist (10 tests)"""
    print("\n" + "="*70)
    print("LAYER 1: SATIRE DOMAIN DETECTION (10 TESTS)")
    print("="*70 + "\n")

    passed = 0
    failed = 0
    failures = []

    tests = [t for t in FAKE_INCIDENTS if t['expected_block'] == 'satire_domain']

    for idx, test in enumerate(tests, 1):
        url = test['sources'][0]['source_url']
        is_satire = is_satire_domain(url)

        if is_satire:
            reason_short, reason_detail = get_satire_reason(url)
            print(f"✅ Test {idx}: BLOCKED satire domain")
            print(f"   Title: {test['title'][:60]}")
            print(f"   Reason: {reason_detail}")
            print(f"   Description: {test['description']}\n")
            passed += 1
        else:
            print(f"❌ Test {idx}: FAILED to block")
            print(f"   Title: {test['title'][:60]}")
            print(f"   URL: {url}")
            print(f"   Expected: {test['expected_reason']}\n")
            failed += 1
            failures.append(f"Satire Test {idx}: {test['title'][:50]}")

    print(f"Satire Detection: {passed}/{passed+failed} passed ({(passed/(passed+failed)*100):.0f}%)\n")
    return passed, failed, failures


def test_simulation_detection() -> Tuple[int, int, List[str]]:
    """Test simulation/drill keyword detection (10 tests)"""
    print("\n" + "="*70)
    print("LAYER 2: SIMULATION/DRILL DETECTION (10 TESTS)")
    print("="*70 + "\n")

    filter = NonIncidentFilter()
    passed = 0
    failed = 0
    failures = []

    tests = [t for t in FAKE_INCIDENTS if t['expected_block'] == 'simulation']

    for idx, test in enumerate(tests, 1):
        is_non, confidence, reasons = filter.is_non_incident(test)

        # Check if any expected keyword was detected
        detected_keywords = [kw for kw in test['expected_keywords']
                            if any(kw.lower() in reason.lower() for reason in reasons)]

        if is_non and confidence >= 0.5:
            print(f"✅ Test {idx}: BLOCKED simulation/drill")
            print(f"   Title: {test['title'][:60]}")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   Keywords detected: {', '.join(detected_keywords)}")
            print(f"   Description: {test['description']}\n")
            passed += 1
        else:
            print(f"❌ Test {idx}: FAILED to block (confidence: {confidence:.2f})")
            print(f"   Title: {test['title'][:60]}")
            print(f"   Expected keywords: {', '.join(test['expected_keywords'])}")
            print(f"   Reasons: {reasons}\n")
            failed += 1
            failures.append(f"Simulation Test {idx}: {test['title'][:50]}")

    print(f"Simulation Detection: {passed}/{passed+failed} passed ({(passed/(passed+failed)*100):.0f}%)\n")
    return passed, failed, failures


def test_policy_detection() -> Tuple[int, int, List[str]]:
    """Test policy announcement detection (5 tests)"""
    print("\n" + "="*70)
    print("LAYER 3: POLICY ANNOUNCEMENT DETECTION (5 TESTS)")
    print("="*70 + "\n")

    filter = NonIncidentFilter()
    passed = 0
    failed = 0
    failures = []

    tests = [t for t in FAKE_INCIDENTS if t['expected_block'] == 'policy']

    for idx, test in enumerate(tests, 1):
        is_non, confidence, reasons = filter.is_non_incident(test)

        # Check if any expected keyword was detected
        text = test['title'].lower() + ' ' + test['narrative'].lower()
        detected_keywords = [kw for kw in test['expected_keywords']
                            if kw.lower() in text]

        if is_non and confidence >= 0.5:
            print(f"✅ Test {idx}: BLOCKED policy announcement")
            print(f"   Title: {test['title'][:60]}")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   Keywords detected: {', '.join(detected_keywords)}")
            print(f"   Description: {test['description']}\n")
            passed += 1
        else:
            print(f"❌ Test {idx}: FAILED to block (confidence: {confidence:.2f})")
            print(f"   Title: {test['title'][:60]}")
            print(f"   Reasons: {reasons}\n")
            failed += 1
            failures.append(f"Policy Test {idx}: {test['title'][:50]}")

    print(f"Policy Detection: {passed}/{passed+failed} passed ({(passed/(passed+failed)*100):.0f}%)\n")
    return passed, failed, failures


def test_temporal_validation() -> Tuple[int, int, List[str]]:
    """Test historical/temporal validation (5 tests)"""
    print("\n" + "="*70)
    print("LAYER 4: TEMPORAL VALIDATION (5 TESTS)")
    print("="*70 + "\n")

    passed = 0
    failed = 0
    failures = []

    tests = [t for t in FAKE_INCIDENTS if t['expected_block'] == 'temporal']

    for idx, test in enumerate(tests, 1):
        occurred_at = datetime.fromisoformat(test['occurred_at'].replace('Z', '+00:00'))
        is_valid, reason = is_recent_incident(occurred_at, max_age_days=30)

        if not is_valid:
            print(f"✅ Test {idx}: BLOCKED temporal issue")
            print(f"   Title: {test['title'][:60]}")
            print(f"   Date: {occurred_at.strftime('%Y-%m-%d')}")
            print(f"   Reason: {reason}")
            print(f"   Description: {test['description']}\n")
            passed += 1
        else:
            print(f"❌ Test {idx}: FAILED to block")
            print(f"   Title: {test['title'][:60]}")
            print(f"   Date: {occurred_at.strftime('%Y-%m-%d')}")
            print(f"   Expected: {test['expected_reason']}\n")
            failed += 1
            failures.append(f"Temporal Test {idx}: {test['title'][:50]}")

    print(f"Temporal Validation: {passed}/{passed+failed} passed ({(passed/(passed+failed)*100):.0f}%)\n")
    return passed, failed, failures


def main():
    """Run comprehensive fake detection test suite"""
    print("\n" + "="*70)
    print("DRONEWATCH FAKE DETECTION TEST SUITE")
    print("Testing 30 known fake incidents across 4 quality control layers")
    print("="*70)

    # Run all test layers
    satire_passed, satire_failed, satire_failures = test_satire_detection()
    sim_passed, sim_failed, sim_failures = test_simulation_detection()
    policy_passed, policy_failed, policy_failures = test_policy_detection()
    temporal_passed, temporal_failed, temporal_failures = test_temporal_validation()

    # Calculate totals
    total_passed = satire_passed + sim_passed + policy_passed + temporal_passed
    total_failed = satire_failed + sim_failed + policy_failed + temporal_failed
    total_tests = total_passed + total_failed

    # Print final summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%")

    print("\nBreakdown by Layer:")
    print(f"  Layer 1 (Satire Domains):    {satire_passed}/{satire_passed+satire_failed} ({(satire_passed/(satire_passed+satire_failed)*100):.0f}%)")
    print(f"  Layer 2 (Simulations):       {sim_passed}/{sim_passed+sim_failed} ({(sim_passed/(sim_passed+sim_failed)*100):.0f}%)")
    print(f"  Layer 3 (Policy):            {policy_passed}/{policy_passed+policy_failed} ({(policy_passed/(policy_passed+policy_failed)*100):.0f}%)")
    print(f"  Layer 4 (Temporal):          {temporal_passed}/{temporal_passed+temporal_failed} ({(temporal_passed/(temporal_passed+temporal_failed)*100):.0f}%)")

    print("\n" + "="*70)

    if total_failed == 0:
        print("\n✅ ALL TESTS PASSED - ZERO FAKES WOULD BE INGESTED!")
        print("\nQuality Control Status: 100% EFFECTIVE")
        print("All fake news, simulations, policy announcements, and historical")
        print("articles would be successfully blocked from DroneWatch database.\n")
        return 0
    else:
        print(f"\n⚠️  {total_failed} TESTS FAILED - QUALITY CONTROL NEEDS IMPROVEMENT\n")
        print("Failed Tests:")
        all_failures = satire_failures + sim_failures + policy_failures + temporal_failures
        for failure in all_failures:
            print(f"  - {failure}")
        print("\nAction Required: Review and enhance detection logic\n")
        return 1


if __name__ == "__main__":
    exit(main())
