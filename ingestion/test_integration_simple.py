#!/usr/bin/env python3
"""
Simple integration test for consolidation engine
Tests consolidation without full ingestion pipeline dependencies
"""
import sys
from datetime import datetime, timezone
from consolidator import ConsolidationEngine


def create_mock_incident(title, lat, lon, occurred_at, source_name, trust_weight, country="DK"):
    """Create a mock incident for testing"""
    return {
        'title': title,
        'lat': lat,
        'lon': lon,
        'occurred_at': occurred_at.isoformat(),
        'asset_type': 'airport',
        'country': country,
        'narrative': f"Mock narrative for {title}",
        'evidence_score': 2 if trust_weight >= 2 else 1,
        'sources': [{
            'source_url': f'https://example.com/{source_name.lower()}',
            'source_name': source_name,
            'source_type': 'news' if trust_weight < 4 else 'police',
            'trust_weight': trust_weight
        }]
    }


def main():
    print("\n" + "="*60)
    print("CONSOLIDATION ENGINE - INTEGRATION TEST")
    print("="*60)

    engine = ConsolidationEngine(location_precision=0.01, time_window_hours=6)

    # Simulate typical ingestion scenario
    base_time = datetime(2025, 10, 14, 14, 30, 0, tzinfo=timezone.utc)

    incidents = [
        # Copenhagen Airport - 3 sources reporting same incident
        create_mock_incident(
            "Drone spotted near Copenhagen Airport",
            55.618, 12.648, base_time,
            "BT", trust_weight=2
        ),
        create_mock_incident(
            "UAV causes delays at Kastrup",
            55.6185, 12.6485, base_time,
            "DR", trust_weight=2
        ),
        create_mock_incident(
            "Police investigating drone incident at Copenhagen Airport",
            55.619, 12.649, base_time,
            "Copenhagen Police", trust_weight=4
        ),

        # Aalborg Airport - 2 sources
        create_mock_incident(
            "Drone sighting at Aalborg Airport",
            57.093, 9.849, base_time,
            "Nordjyske", trust_weight=2
        ),
        create_mock_incident(
            "Air traffic disrupted by drone in Aalborg",
            57.0935, 9.8495, base_time,
            "TV2 Nord", trust_weight=3
        ),

        # Billund Airport - 1 source (no consolidation)
        create_mock_incident(
            "Unauthorized drone near Billund",
            55.740, 9.152, base_time,
            "Ekstra Bladet", trust_weight=2
        )
    ]

    print(f"\n📥 Input: {len(incidents)} incidents from scrapers")
    print(f"   - Copenhagen Airport: 3 incidents")
    print(f"   - Aalborg Airport: 2 incidents")
    print(f"   - Billund Airport: 1 incident")

    # Get consolidation statistics
    print(f"\n📊 Consolidation Statistics:")
    stats = engine.get_consolidation_stats(incidents)
    print(f"   Total incidents: {stats['total_incidents']}")
    print(f"   Unique locations: {stats['unique_hashes']}")
    print(f"   Multi-source groups: {stats['multi_source_groups']}")
    print(f"   Potential merges: {stats['potential_merges']}")
    print(f"   Merge rate: {stats['merge_rate']:.1f}%")

    # Consolidate
    print(f"\n🔄 Running consolidation...")
    consolidated = engine.consolidate_incidents(incidents)

    print(f"\n📤 Output: {len(consolidated)} consolidated incidents")

    # Display results
    for i, incident in enumerate(consolidated, 1):
        print(f"\n{i}. {incident['title'][:60]}")
        print(f"   Location: ({incident['lat']:.4f}, {incident['lon']:.4f})")
        print(f"   Sources: {len(incident['sources'])}")
        print(f"   Evidence Score: {incident['evidence_score']}")

        if incident.get('merged_from', 1) > 1:
            print(f"   ✓ MERGED from {incident['merged_from']} incidents")

        # Show sources ranked by authority
        for j, source in enumerate(incident['sources'], 1):
            print(f"      {j}. {source['source_name']} (trust_weight: {source['trust_weight']})")

    # Verify expected behavior
    print(f"\n{'='*60}")
    print("VERIFICATION")
    print(f"{'='*60}")

    success = True

    # Check: 6 incidents → 3 consolidated
    if len(consolidated) != 3:
        print(f"❌ Expected 3 consolidated incidents, got {len(consolidated)}")
        success = False
    else:
        print(f"✅ Correct number of incidents: 3")

    # Check: Copenhagen incident should have 3 sources and evidence score 4
    copenhagen = next((inc for inc in consolidated if 55.6 < inc['lat'] < 55.7 and 12.6 < inc['lon'] < 12.7), None)
    if copenhagen:
        if len(copenhagen['sources']) != 3:
            print(f"❌ Copenhagen should have 3 sources, got {len(copenhagen['sources'])}")
            success = False
        elif copenhagen['evidence_score'] != 4:
            print(f"❌ Copenhagen should have evidence score 4, got {copenhagen['evidence_score']}")
            success = False
        else:
            print(f"✅ Copenhagen: 3 sources, evidence score 4 (upgraded from 2)")
    else:
        print(f"❌ Copenhagen incident not found")
        success = False

    # Check: Aalborg incident should have 2 sources and evidence score 3
    aalborg = next((inc for inc in consolidated if 57.0 < inc['lat'] < 57.1), None)
    if aalborg:
        if len(aalborg['sources']) != 2:
            print(f"❌ Aalborg should have 2 sources, got {len(aalborg['sources'])}")
            success = False
        elif aalborg['evidence_score'] != 3:
            print(f"❌ Aalborg should have evidence score 3, got {aalborg['evidence_score']}")
            success = False
        else:
            print(f"✅ Aalborg: 2 sources, evidence score 3 (upgraded from 2)")
    else:
        print(f"❌ Aalborg incident not found")
        success = False

    # Check: Billund incident should have 1 source and evidence score 2
    billund = next((inc for inc in consolidated if 55.7 < inc['lat'] < 55.8), None)
    if billund:
        if len(billund['sources']) != 1:
            print(f"❌ Billund should have 1 source, got {len(billund['sources'])}")
            success = False
        elif billund['evidence_score'] != 2:
            print(f"❌ Billund should have evidence score 2, got {billund['evidence_score']}")
            success = False
        else:
            print(f"✅ Billund: 1 source, evidence score 2 (no consolidation)")
    else:
        print(f"❌ Billund incident not found")
        success = False

    print(f"{'='*60}\n")

    if success:
        print("🎉 INTEGRATION TEST PASSED")
        return 0
    else:
        print("❌ INTEGRATION TEST FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
