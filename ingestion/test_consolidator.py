#!/usr/bin/env python3
"""
Test Suite for Multi-Source Consolidation Engine
Tests deduplication, source merging, and evidence score recalculation
"""
import sys
from datetime import datetime, timedelta, timezone
from consolidator import ConsolidationEngine

def create_test_incident(
    title: str,
    lat: float,
    lon: float,
    occurred_at: datetime,
    sources: list,
    narrative: str = "Test narrative",
    country: str = "DK",
    asset_type: str = "airport"
) -> dict:
    """Helper to create test incident"""
    return {
        'title': title,
        'lat': lat,
        'lon': lon,
        'occurred_at': occurred_at.isoformat(),
        'narrative': narrative,
        'country': country,
        'asset_type': asset_type,
        'sources': sources
    }

def test_scenario_1_single_incident():
    """
    Scenario 1: Single Incident (No Consolidation)
    Expected: Returns unchanged
    """
    print("\n" + "="*60)
    print("TEST SCENARIO 1: Single Incident (No Consolidation)")
    print("="*60)

    engine = ConsolidationEngine()

    incident = create_test_incident(
        title="Copenhagen Airport - Drone Sighting",
        lat=55.618,
        lon=12.6476,
        occurred_at=datetime.now(timezone.utc),
        sources=[{
            'source_url': 'https://dr.dk/test1',
            'source_type': 'media',
            'source_name': 'DR Nyheder',
            'trust_weight': 3
        }]
    )

    result = engine.consolidate_incidents([incident])

    print(f"Input:  1 incident")
    print(f"Output: {len(result)} incident")
    print(f"Sources: {len(result[0]['sources'])}")
    print(f"Evidence Score: {result[0].get('evidence_score', 'Not calculated')}")

    assert len(result) == 1, "Should return 1 incident"
    assert len(result[0]['sources']) == 1, "Should have 1 source"
    print("✅ PASSED")

def test_scenario_2_identical_location_time():
    """
    Scenario 2: Same Location + Same Time Window → MERGE
    Different headlines but same incident
    """
    print("\n" + "="*60)
    print("TEST SCENARIO 2: Same Location + Time → MERGE")
    print("="*60)

    engine = ConsolidationEngine()

    base_time = datetime.now(timezone.utc)
    copenhagen_lat, copenhagen_lon = 55.618, 12.6476

    incidents = [
        create_test_incident(
            title="Drone spotted near Copenhagen Airport",
            lat=copenhagen_lat,
            lon=copenhagen_lon,
            occurred_at=base_time,
            sources=[{
                'source_url': 'https://dr.dk/test',
                'source_type': 'media',
                'source_name': 'DR Nyheder',
                'trust_weight': 3
            }],
            narrative="Police investigating drone sighting at airport"
        ),
        create_test_incident(
            title="Kastrup Airport closed due to UAV activity",
            lat=copenhagen_lat + 0.005,  # Within 1km
            lon=copenhagen_lon + 0.005,
            occurred_at=base_time + timedelta(hours=2),  # Within 6h window
            sources=[{
                'source_url': 'https://tv2.dk/test',
                'source_type': 'media',
                'source_name': 'TV2',
                'trust_weight': 3
            }],
            narrative="Aviation authorities confirm drone incident leading to temporary closure"
        )
    ]

    result = engine.consolidate_incidents(incidents)

    print(f"Input:  {len(incidents)} incidents (different headlines)")
    print(f"  - '{incidents[0]['title'][:40]}...'")
    print(f"  - '{incidents[1]['title'][:40]}...'")
    print(f"Output: {len(result)} incident (merged)")
    print(f"Sources: {len(result[0]['sources'])}")
    print(f"Evidence Score: {result[0].get('evidence_score', 'Not calculated')}")
    print(f"Best Narrative Length: {len(result[0].get('narrative', ''))}")

    assert len(result) == 1, "Should merge into 1 incident"
    assert len(result[0]['sources']) == 2, "Should have 2 sources"
    assert result[0].get('merged_from') == 2, "Should track merge count"
    print("✅ PASSED")

def test_scenario_3_different_locations():
    """
    Scenario 3: Different Locations → NO MERGE
    Even if same time, different airports = different incidents
    """
    print("\n" + "="*60)
    print("TEST SCENARIO 3: Different Locations → NO MERGE")
    print("="*60)

    engine = ConsolidationEngine()

    base_time = datetime.now(timezone.utc)

    incidents = [
        create_test_incident(
            title="Drone at Copenhagen Airport",
            lat=55.618,
            lon=12.6476,
            occurred_at=base_time,
            sources=[{
                'source_url': 'https://dr.dk/test1',
                'source_type': 'media',
                'source_name': 'DR Nyheder',
                'trust_weight': 3
            }]
        ),
        create_test_incident(
            title="Drone at Aalborg Airport",
            lat=57.0928,  # Different location (>1km)
            lon=9.8492,
            occurred_at=base_time,
            sources=[{
                'source_url': 'https://dr.dk/test2',
                'source_type': 'media',
                'source_name': 'DR Nyheder',
                'trust_weight': 3
            }]
        )
    ]

    result = engine.consolidate_incidents(incidents)

    print(f"Input:  {len(incidents)} incidents (different airports)")
    print(f"  - Copenhagen (55.618, 12.6476)")
    print(f"  - Aalborg (57.0928, 9.8492)")
    print(f"Output: {len(result)} incidents (no merge)")

    assert len(result) == 2, "Should NOT merge different locations"
    print("✅ PASSED")

def test_scenario_4_evidence_score_upgrade():
    """
    Scenario 4: Evidence Score Upgrade with Multiple Sources
    Media source (score 2) + Police source (score 4) → Final score 4
    """
    print("\n" + "="*60)
    print("TEST SCENARIO 4: Evidence Score Upgrade")
    print("="*60)

    engine = ConsolidationEngine()

    base_time = datetime.now(timezone.utc)
    copenhagen_lat, copenhagen_lon = 55.618, 12.6476

    incidents = [
        create_test_incident(
            title="Media reports drone at airport",
            lat=copenhagen_lat,
            lon=copenhagen_lon,
            occurred_at=base_time,
            sources=[{
                'source_url': 'https://dr.dk/test',
                'source_type': 'media',
                'source_name': 'DR Nyheder',
                'trust_weight': 3,
                'source_quote': 'Witness reports seeing drone'
            }],
            narrative="Local news reports drone sighting"
        ),
        create_test_incident(
            title="Police confirm drone incident",
            lat=copenhagen_lat,
            lon=copenhagen_lon,
            occurred_at=base_time + timedelta(hours=1),
            sources=[{
                'source_url': 'https://politi.dk/test',
                'source_type': 'police',
                'source_name': 'Rigspolitiet',
                'trust_weight': 4,
                'source_quote': 'Politiet bekræfter droneaktivitet ved lufthavn'
            }],
            narrative="Police investigating drone incident at Copenhagen Airport"
        )
    ]

    # Calculate expected evidence scores before consolidation
    print("\nBefore Consolidation:")
    print(f"  Incident 1 (media): trust_weight=3")
    print(f"  Incident 2 (police): trust_weight=4")

    result = engine.consolidate_incidents(incidents)

    print(f"\nAfter Consolidation:")
    print(f"Input:  {len(incidents)} incidents")
    print(f"Output: {len(result)} incident")
    print(f"Sources: {len(result[0]['sources'])}")
    print(f"Evidence Score: {result[0].get('evidence_score', 'Not calculated')}")
    print(f"\nSource Breakdown:")
    for i, source in enumerate(result[0]['sources'], 1):
        print(f"  {i}. {source['source_name']} (type={source['source_type']}, trust={source['trust_weight']})")

    assert len(result) == 1, "Should merge into 1 incident"
    assert len(result[0]['sources']) == 2, "Should have 2 sources"
    assert result[0].get('evidence_score') == 4, "Should upgrade to evidence score 4 (official source)"
    print("✅ PASSED - Evidence upgraded from 2 → 4")

def test_consolidation_stats():
    """
    Test: Consolidation Statistics
    Verify stats calculation is accurate
    """
    print("\n" + "="*60)
    print("TEST: Consolidation Statistics")
    print("="*60)

    engine = ConsolidationEngine()

    base_time = datetime.now(timezone.utc)
    copenhagen_lat, copenhagen_lon = 55.618, 12.6476

    incidents = [
        create_test_incident("Incident 1", copenhagen_lat, copenhagen_lon, base_time, []),
        create_test_incident("Incident 2", copenhagen_lat, copenhagen_lon, base_time, []),
        create_test_incident("Incident 3", 57.0928, 9.8492, base_time, []),  # Aalborg
    ]

    stats = engine.get_consolidation_stats(incidents)

    print(f"Total Incidents: {stats['total_incidents']}")
    print(f"Unique Hashes: {stats['unique_hashes']}")
    print(f"Potential Merges: {stats['potential_merges']}")
    print(f"Merge Rate: {stats['merge_rate']:.1%}")

    assert stats['total_incidents'] == 3, "Should count 3 incidents"
    assert stats['unique_hashes'] == 2, "Should have 2 unique locations"
    assert stats['potential_merges'] == 1, "Should identify 1 potential merge"
    print("✅ PASSED")

def main():
    """Run all test scenarios"""
    print("\n" + "="*60)
    print("CONSOLIDATION ENGINE TEST SUITE")
    print("="*60)

    try:
        test_scenario_1_single_incident()
        test_scenario_2_identical_location_time()
        test_scenario_3_different_locations()
        test_scenario_4_evidence_score_upgrade()
        test_consolidation_stats()

        print("\n" + "="*60)
        print("ALL TESTS PASSED ✅")
        print("="*60)
        print("\nConsolidation engine is ready for production use.")
        print("Next steps:")
        print("  1. Integrate into ingest.py")
        print("  2. Run with real data")
        print("  3. Monitor merge rates and evidence scores")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
