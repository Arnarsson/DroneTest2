#!/usr/bin/env python3
"""
Analyze duplicate incidents using production API data
Shows which incidents would be merged by the AI deduplication system
"""
import json
import requests
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two lat/lon points"""
    R = 6371  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c

def time_diff_hours(dt1: str, dt2: str) -> float:
    """Calculate time difference in hours"""
    try:
        t1 = datetime.fromisoformat(dt1.replace('Z', '+00:00'))
        t2 = datetime.fromisoformat(dt2.replace('Z', '+00:00'))
        return abs((t1 - t2).total_seconds() / 3600)
    except:
        return 999  # If parsing fails, assume very different

def fetch_incidents() -> List[Dict]:
    """Fetch all incidents from production API"""
    print("📡 Fetching incidents from production API...")
    response = requests.get("https://www.dronemap.cc/api/incidents?limit=50")
    response.raise_for_status()
    incidents = response.json()
    print(f"✅ Fetched {len(incidents)} incidents\n")
    return incidents

def group_by_proximity(incidents: List[Dict], radius_km: float = 5.0, time_window_hrs: int = 24) -> Dict[int, List[Dict]]:
    """Group incidents by geographic proximity and time window"""
    groups = defaultdict(list)
    assigned = set()
    group_id = 0

    for i, inc1 in enumerate(incidents):
        if i in assigned:
            continue

        # Start new group
        groups[group_id].append(inc1)
        assigned.add(i)

        # Find nearby incidents within time window
        for j, inc2 in enumerate(incidents):
            if j in assigned or i == j:
                continue

            dist_km = haversine_distance(inc1['lat'], inc1['lon'], inc2['lat'], inc2['lon'])
            time_diff = time_diff_hours(inc1['occurred_at'], inc2['occurred_at'])

            if dist_km <= radius_km and time_diff <= time_window_hrs:
                groups[group_id].append(inc2)
                assigned.add(j)

        group_id += 1

    return dict(groups)

def analyze_potential_duplicates(groups: Dict[int, List[Dict]]) -> Tuple[int, List[Dict]]:
    """Analyze groups to find potential duplicates"""
    potential_clusters = []
    total_duplicates = 0

    for group_id, incidents_in_group in groups.items():
        if len(incidents_in_group) > 1:
            # This is a potential duplicate cluster
            primary = incidents_in_group[0]
            duplicates = incidents_in_group[1:]

            cluster = {
                'primary': primary,
                'duplicates': duplicates,
                'count': len(incidents_in_group),
                'location': f"{primary['lat']:.4f}, {primary['lon']:.4f}",
                'country': primary['country']
            }
            potential_clusters.append(cluster)
            total_duplicates += len(duplicates)

    return total_duplicates, potential_clusters

def print_analysis(clusters: List[Dict], total_duplicates: int, total_incidents: int):
    """Print detailed analysis"""
    print("=" * 80)
    print("🔍 AI DEDUPLICATION ANALYSIS - DRY RUN")
    print("=" * 80)
    print(f"\n📊 SUMMARY:")
    print(f"   Total incidents in database: {total_incidents}")
    print(f"   Potential duplicate clusters: {len(clusters)}")
    print(f"   Incidents that would be merged: {total_duplicates}")
    print(f"   Unique incidents after merge: {total_incidents - total_duplicates}")
    print(f"   Reduction: {(total_duplicates / total_incidents * 100):.1f}%")

    if not clusters:
        print("\n✅ No duplicates found! Database is clean.")
        return

    print(f"\n📍 DUPLICATE CLUSTERS FOUND:")
    print("-" * 80)

    for i, cluster in enumerate(clusters, 1):
        print(f"\n🎯 Cluster #{i} - {cluster['country']} ({cluster['location']})")
        print(f"   {cluster['count']} incidents at this location")

        print(f"\n   PRIMARY (will be kept):")
        print(f"   📌 ID: {cluster['primary']['id'][:8]}...")
        print(f"   📝 Title: {cluster['primary']['title'][:80]}...")
        print(f"   🗓️  Date: {cluster['primary']['occurred_at']}")
        print(f"   🏆 Evidence: {cluster['primary']['evidence_score']}")

        print(f"\n   DUPLICATES (will be merged as sources):")
        for j, dup in enumerate(cluster['duplicates'], 1):
            print(f"   {j}. ID: {dup['id'][:8]}... | {dup['occurred_at']} | Evidence: {dup['evidence_score']}")
            print(f"      Title: {dup['title'][:70]}...")

    print("\n" + "=" * 80)
    print("💡 NEXT STEPS:")
    print("=" * 80)
    print("1. This is a DRY RUN - no changes have been made")
    print("2. Review clusters above to verify they are true duplicates")
    print("3. To execute merge with AI validation:")
    print("   python3 scripts/ai_deduplicate_batch.py --execute")
    print("4. Each cluster will be analyzed by AI for semantic similarity")
    print("5. Duplicates will become sources in the primary incident")
    print("=" * 80)

def main():
    try:
        # Fetch incidents
        incidents = fetch_incidents()

        # Group by proximity (5km, 24hrs)
        print("🔎 Grouping incidents by proximity...")
        groups = group_by_proximity(incidents, radius_km=5.0, time_window_hrs=24)
        print(f"✅ Found {len(groups)} geographic groups\n")

        # Analyze for duplicates
        print("🤖 Analyzing for potential duplicates...")
        total_duplicates, clusters = analyze_potential_duplicates(groups)

        # Print results
        print_analysis(clusters, total_duplicates, len(incidents))

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
