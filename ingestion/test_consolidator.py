#!/usr/bin/env python3
"""
Test Suite for Incident Consolidation Engine

Tests:
1. Single incident → No consolidation
2. Same location + time → MERGE
3. Different locations → NO MERGE
4. Evidence upgrade: media (2) + police (4) → OFFICIAL (4)
5. Source deduplication by URL
6. Authority ranking verification
7. Consolidation statistics
"""
import sys
from datetime import datetime, timedelta, timezone
from consolidator import ConsolidationEngine


def create_test_incident(
    title: str,
    lat: float,
    lon: float,
    occurred_at: datetime,
    source_url: str,
    source_name: str,
    source_type: str,
    trust_weight: int,
    asset_type: str = "airport",
    country: str = "DK",
    narrative: str = "Test narrative"
) -> dict:
    """Helper to create test incident"""
    return {
        'title': title,
        'lat': lat,
        'lon': lon,
        'occurred_at': occurred_at.isoformat(),
        'asset_type': asset_type,
        'country': country,
        'narrative': narrative,
        'evidence_score': 2 if trust_weight >= 2 else 1,  # Initial score
        'sources': [
            {
                'source_url': source_url,
                'source_name': source_name,
                'source_type': source_type,
                'trust_weight': trust_weight
            }
        ]
    }


def test_single_incident():
    """Test 1: Single incident should pass through unchanged"""
    print("\n" + "="*60)
    print("TEST 1: Single Incident (No Consolidation)")
    print("="*60)

    engine = ConsolidationEngine()
    base_time = datetime.now(timezone.utc)

    incident = create_test_incident(
        title="Drone spotted at Copenhagen Airport",
        lat=55.618,
        lon=12.648,
        occurred_at=base_time,
        source_url="https://example.com/1",
        source_name="BT",
        source_type="news",
        trust_weight=2
    )

    result = engine.consolidate_incidents([incident])

    assert len(result) == 1, f"Expected 1 incident, got {len(result)}"
    assert result[0]['title'] == incident['title'], "Title should be unchanged"
    assert len(result[0]['sources']) == 1, "Should have 1 source"
    assert result[0]['evidence_score'] == 2, "Evidence score should be 2 (single credible source)"

    print("✅ PASS: Single incident passed through unchanged")
    print(f"   Title: {result[0]['title']}")
    print(f"   Sources: {len(result[0]['sources'])}")
    print(f"   Evidence Score: {result[0]['evidence_score']}")


def test_same_location_time_merge():
    """Test 2: Same location + time → MERGE"""
    print("\n" + "="*60)
    print("TEST 2: Same Location + Time → MERGE")
    print("="*60)

    engine = ConsolidationEngine(location_precision=0.01, time_window_hours=6)
    # Use fixed time at start of 6-hour window to avoid boundary issues
    base_time = datetime(2025, 10, 14, 12, 0, 0, tzinfo=timezone.utc)

    # Two incidents at nearly same location (~50m apart) and same time window
    incident1 = create_test_incident(
        title="Drone spotted at Kastrup",
        lat=55.6180,
        lon=12.6480,
        occurred_at=base_time,
        source_url="https://bt.dk/article1",
        source_name="BT",
        source_type="news",
        trust_weight=2,
        narrative="BT reports a drone sighting at Copenhagen Airport, causing delays."
    )

    incident2 = create_test_incident(
        title="UAV forces airport closure",
        lat=55.6185,  # 50m away, rounds to same 0.01° bucket
        lon=12.6485,
        occurred_at=base_time + timedelta(hours=2),  # Within same 6-hour window (12:00-18:00)
        source_url="https://dr.dk/article2",
        source_name="DR",
        source_type="news",
        trust_weight=2,
        narrative="DR confirms Copenhagen Airport temporarily closed due to unauthorized drone activity in airspace."
    )

    result = engine.consolidate_incidents([incident1, incident2])

    assert len(result) == 1, f"Expected 1 merged incident, got {len(result)}"
    assert len(result[0]['sources']) == 2, f"Expected 2 sources, got {len(result[0]['sources'])}"
    assert result[0]['evidence_score'] == 3, f"Evidence score should be 3 (multi-source), got {result[0]['evidence_score']}"
    assert result[0]['merged_from'] == 2, "Should indicate merged from 2 incidents"
    assert result[0]['source_count'] == 2, "Should have 2 unique sources"

    print("✅ PASS: Incidents merged successfully")
    print(f"   Title: {result[0]['title']}")
    print(f"   Sources: {len(result[0]['sources'])} (BT, DR)")
    print(f"   Evidence Score: {result[0]['evidence_score']} (upgraded from 2 to 3)")
    print(f"   Merged From: {result[0]['merged_from']} incidents")
    print(f"   Narrative Length: {len(result[0]['narrative'])} chars (longest)")


def test_different_locations_no_merge():
    """Test 3: Different locations → NO MERGE"""
    print("\n" + "="*60)
    print("TEST 3: Different Locations → NO MERGE")
    print("="*60)

    engine = ConsolidationEngine()
    base_time = datetime.now(timezone.utc)

    # Two incidents at different airports
    incident1 = create_test_incident(
        title="Drone at Copenhagen Airport",
        lat=55.618,
        lon=12.648,
        occurred_at=base_time,
        source_url="https://example.com/cph",
        source_name="BT",
        source_type="news",
        trust_weight=2,
        country="DK"
    )

    incident2 = create_test_incident(
        title="Drone at Aalborg Airport",
        lat=57.093,  # Different location (>150km away)
        lon=9.849,
        occurred_at=base_time,
        source_url="https://example.com/aal",
        source_name="Nordjyske",
        source_type="news",
        trust_weight=2,
        country="DK"
    )

    result = engine.consolidate_incidents([incident1, incident2])

    assert len(result) == 2, f"Expected 2 separate incidents, got {len(result)}"
    assert all(len(inc['sources']) == 1 for inc in result), "Each incident should have 1 source"

    print("✅ PASS: Incidents kept separate")
    print(f"   Incident 1: {result[0]['title']} ({result[0]['lat']:.3f}, {result[0]['lon']:.3f})")
    print(f"   Incident 2: {result[1]['title']} ({result[1]['lat']:.3f}, {result[1]['lon']:.3f})")
    print(f"   Distance: >150km apart → No merge")


def test_evidence_score_upgrade():
    """Test 4: Evidence upgrade when merging different source types"""
    print("\n" + "="*60)
    print("TEST 4: Evidence Score Upgrade (Media + Police → OFFICIAL)")
    print("="*60)

    engine = ConsolidationEngine()
    # Use fixed time at start of 6-hour window to avoid boundary issues
    base_time = datetime(2025, 10, 14, 12, 0, 0, tzinfo=timezone.utc)

    # Media source (trust_weight: 2) + Police source (trust_weight: 4)
    incident1 = create_test_incident(
        title="Drone reported near airport",
        lat=55.618,
        lon=12.648,
        occurred_at=base_time,
        source_url="https://bt.dk/drone1",
        source_name="BT",
        source_type="news",
        trust_weight=2
    )

    incident2 = create_test_incident(
        title="Police investigating drone incident at Kastrup",
        lat=55.6185,
        lon=12.6485,
        occurred_at=base_time + timedelta(hours=2),  # Within same 6-hour window (12:00-18:00)
        source_url="https://politi.dk/incident123",
        source_name="Copenhagen Police",
        source_type="police",
        trust_weight=4  # Official source
    )

    result = engine.consolidate_incidents([incident1, incident2])

    assert len(result) == 1, "Should merge into 1 incident"
    assert result[0]['evidence_score'] == 4, f"Evidence score should be 4 (official source present), got {result[0]['evidence_score']}"
    assert result[0]['sources'][0]['trust_weight'] == 4, "Highest trust source should be first"
    assert result[0]['sources'][0]['source_type'] == 'police', "Police source should be ranked first"

    print("✅ PASS: Evidence score upgraded")
    print(f"   Sources: {len(result[0]['sources'])}")
    print(f"   Source 1: {result[0]['sources'][0]['source_name']} (trust_weight: {result[0]['sources'][0]['trust_weight']})")
    print(f"   Source 2: {result[0]['sources'][1]['source_name']} (trust_weight: {result[0]['sources'][1]['trust_weight']})")
    print(f"   Evidence Score: {result[0]['evidence_score']} (upgraded from 2 to 4)")


def test_source_deduplication():
    """Test 5: Source deduplication by URL"""
    print("\n" + "="*60)
    print("TEST 5: Source Deduplication by URL")
    print("="*60)

    engine = ConsolidationEngine()
    base_time = datetime.now(timezone.utc)

    # Two "incidents" with SAME source URL (shouldn't happen, but test deduplication)
    incident1 = create_test_incident(
        title="Drone at airport",
        lat=55.618,
        lon=12.648,
        occurred_at=base_time,
        source_url="https://bt.dk/same-article",
        source_name="BT",
        source_type="news",
        trust_weight=2
    )

    incident2 = create_test_incident(
        title="Airport closure due to drone",
        lat=55.6185,
        lon=12.6485,
        occurred_at=base_time,
        source_url="https://bt.dk/same-article",  # SAME URL
        source_name="BT",
        source_type="news",
        trust_weight=2
    )

    result = engine.consolidate_incidents([incident1, incident2])

    assert len(result) == 1, "Should merge incidents"
    assert len(result[0]['sources']) == 1, f"Should deduplicate to 1 source, got {len(result[0]['sources'])}"
    assert result[0]['source_count'] == 1, "Source count should be 1"

    print("✅ PASS: Source deduplication successful")
    print(f"   Input: 2 incidents with same source URL")
    print(f"   Output: 1 incident with 1 unique source")
    print(f"   Source: {result[0]['sources'][0]['source_url']}")


def test_authority_ranking():
    """Test 6: Authority ranking verification"""
    print("\n" + "="*60)
    print("TEST 6: Authority Ranking (Sources Sorted by Trust Weight)")
    print("="*60)

    engine = ConsolidationEngine()
    base_time = datetime.now(timezone.utc)

    # Create 4 incidents with different trust weights
    incidents = [
        create_test_incident(
            title="Social media post",
            lat=55.618, lon=12.648, occurred_at=base_time,
            source_url="https://twitter.com/user1", source_name="Twitter User",
            source_type="social_media", trust_weight=1
        ),
        create_test_incident(
            title="News report",
            lat=55.6185, lon=12.6485, occurred_at=base_time,
            source_url="https://bt.dk/news1", source_name="BT",
            source_type="news", trust_weight=2
        ),
        create_test_incident(
            title="Police statement",
            lat=55.619, lon=12.649, occurred_at=base_time,
            source_url="https://politi.dk/stmt1", source_name="Copenhagen Police",
            source_type="police", trust_weight=4
        ),
        create_test_incident(
            title="Major news outlet",
            lat=55.6195, lon=12.6495, occurred_at=base_time,
            source_url="https://dr.dk/news1", source_name="DR",
            source_type="news", trust_weight=3
        )
    ]

    result = engine.consolidate_incidents(incidents)

    assert len(result) == 1, "Should merge all incidents"
    assert len(result[0]['sources']) == 4, "Should have 4 sources"

    # Verify ranking: 4 → 3 → 2 → 1
    trust_weights = [s['trust_weight'] for s in result[0]['sources']]
    assert trust_weights == [4, 3, 2, 1], f"Sources should be ranked 4→3→2→1, got {trust_weights}"

    print("✅ PASS: Sources ranked correctly by authority")
    for i, source in enumerate(result[0]['sources'], 1):
        print(f"   {i}. {source['source_name']} (trust_weight: {source['trust_weight']}, type: {source['source_type']})")


def test_consolidation_statistics():
    """Test 7: Consolidation statistics calculation"""
    print("\n" + "="*60)
    print("TEST 7: Consolidation Statistics")
    print("="*60)

    engine = ConsolidationEngine()
    # Use fixed time to ensure all incidents in same 6-hour window
    base_time = datetime(2025, 10, 14, 12, 0, 0, tzinfo=timezone.utc)

    # Create test dataset:
    # - 2 incidents at location A (should merge) → 1 merge operation
    # - 3 incidents at location B (should merge) → 2 merge operations
    # - 1 incident at location C (no merge) → 0 merge operations
    # Total potential_merges = 1 + 2 = 3 (number of "extra" incidents that get merged into groups)
    incidents = [
        # Location A: Copenhagen Airport (2 incidents, 1 merge)
        create_test_incident(
            "Incident A1", 55.618, 12.648, base_time,
            "https://source1.com", "Source 1", "news", 2
        ),
        create_test_incident(
            "Incident A2", 55.6185, 12.6485, base_time,
            "https://source2.com", "Source 2", "news", 2
        ),
        # Location B: Aalborg Airport (3 incidents, 2 merges)
        create_test_incident(
            "Incident B1", 57.093, 9.849, base_time,
            "https://source3.com", "Source 3", "news", 2
        ),
        create_test_incident(
            "Incident B2", 57.0935, 9.8495, base_time,
            "https://source4.com", "Source 4", "police", 4
        ),
        create_test_incident(
            "Incident B3", 57.094, 9.850, base_time,
            "https://source5.com", "Source 5", "news", 3
        ),
        # Location C: Billund Airport (1 incident, no merge)
        create_test_incident(
            "Incident C1", 55.740, 9.152, base_time,
            "https://source6.com", "Source 6", "news", 2
        )
    ]

    stats = engine.get_consolidation_stats(incidents)

    assert stats['total_incidents'] == 6, "Should have 6 total incidents"
    assert stats['unique_hashes'] == 3, f"Should have 3 unique locations, got {stats['unique_hashes']}"
    assert stats['multi_source_groups'] == 2, f"Should have 2 multi-source groups (A, B), got {stats['multi_source_groups']}"
    # potential_merges = (2-1) + (3-1) = 1 + 2 = 3
    assert stats['potential_merges'] == 3, f"Should have 3 potential merges ((2-1)+(3-1)), got {stats['potential_merges']}"
    expected_merge_rate = (2 / 3) * 100  # 2 multi-source groups out of 3 unique locations
    assert abs(stats['merge_rate'] - expected_merge_rate) < 0.1, f"Merge rate should be ~{expected_merge_rate:.1f}%, got {stats['merge_rate']:.1f}%"

    print("✅ PASS: Statistics calculated correctly")
    print(f"   Total Incidents: {stats['total_incidents']}")
    print(f"   Unique Locations: {stats['unique_hashes']}")
    print(f"   Multi-Source Groups: {stats['multi_source_groups']}")
    print(f"   Potential Merges: {stats['potential_merges']}")
    print(f"   Merge Rate: {stats['merge_rate']:.1f}%")

    # Verify actual consolidation
    result = engine.consolidate_incidents(incidents)
    assert len(result) == 3, f"Should consolidate to 3 incidents, got {len(result)}"
    print(f"   After Consolidation: {len(result)} incidents")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("INCIDENT CONSOLIDATION ENGINE - TEST SUITE")
    print("="*60)

    tests = [
        test_single_incident,
        test_same_location_time_merge,
        test_different_locations_no_merge,
        test_evidence_score_upgrade,
        test_source_deduplication,
        test_authority_ranking,
        test_consolidation_statistics
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAIL: {test_func.__name__}")
            print(f"   {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {test_func.__name__}")
            print(f"   {e}")
            failed += 1

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("="*60 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
