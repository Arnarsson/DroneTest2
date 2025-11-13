"""
Example usage of Tier 1 & Tier 2 duplicate detection.

This demonstrates how to integrate fuzzy matching and embedding-based
duplicate detection into the ingestion pipeline.
"""

import asyncio
import asyncpg
from datetime import datetime
from fuzzy_matcher import FuzzyMatcher
from openrouter_deduplicator import OpenRouterEmbeddingDeduplicator


async def example_duplicate_detection():
    """Demonstrate Tier 1 and Tier 2 duplicate detection."""

    print("=" * 70)
    print("TIER 1: FUZZY MATCHER (FREE, <1ms)")
    print("=" * 70)

    # Example incidents
    title1 = "Copenhagen Airport closed due to drone"
    title2 = "Copenhagen Airport shutdown after UAV sighting"
    title3 = "Oslo Gardermoen drone incident"

    print(f"\nTitle 1: {title1}")
    print(f"Title 2: {title2}")
    print(f"Title 3: {title3}")

    # Fuzzy matching
    similarity_1_2 = FuzzyMatcher.similarity_ratio(title1, title2)
    similarity_1_3 = FuzzyMatcher.similarity_ratio(title1, title3)

    print(f"\nSimilarity (1 vs 2): {similarity_1_2:.2%}")
    print(f"Similarity (1 vs 3): {similarity_1_3:.2%}")

    # Check for matches
    if FuzzyMatcher.is_fuzzy_match(title1, title2, threshold=0.55):
        print("\n✓ Titles 1 and 2 are DUPLICATES (Tier 1 detection)")
        explanation = FuzzyMatcher.explain_similarity(title1, title2)
        print(f"  Common words: {len(explanation['common_words'])}")
        print(f"  Unique to 1: {explanation['unique_to_1'][:3]}...")
        print(f"  Unique to 2: {explanation['unique_to_2'][:3]}...")
    else:
        print("\n✗ Titles 1 and 2 are UNIQUE")

    if FuzzyMatcher.is_fuzzy_match(title1, title3, threshold=0.55):
        print("\n✓ Titles 1 and 3 are DUPLICATES")
    else:
        print("\n✗ Titles 1 and 3 are UNIQUE")

    print("\n" + "=" * 70)
    print("TIER 2: OPENROUTER EMBEDDINGS (FREE, 50-100ms)")
    print("=" * 70)

    print("\n⚠ Note: Tier 2 requires:")
    print("  1. OPENROUTER_API_KEY environment variable")
    print("  2. PostgreSQL with pgvector extension")
    print("  3. incident_embeddings table (migration 019)")
    print("\nThis example shows API structure only (no real calls).\n")

    # Example incident data
    incident1 = {
        'title': 'Drone closes Copenhagen Airport',
        'location_name': 'Kastrup Airport',
        'city': 'Copenhagen',
        'asset_type': 'airport',
        'occurred_at': datetime(2025, 11, 13, 12, 0),
        'narrative': 'A drone was spotted near the runway causing temporary closure of the airport.',
        'lat': 55.6181,
        'lon': 12.6561
    }

    incident2 = {
        'title': 'UAV sighting at Kastrup',
        'location_name': 'Copenhagen Airport',
        'city': 'Copenhagen',
        'asset_type': 'airport',
        'occurred_at': datetime(2025, 11, 13, 12, 30),
        'narrative': 'Airport operations suspended after unmanned aircraft spotted.',
        'lat': 55.6180,
        'lon': 12.6560
    }

    print("Incident 1:")
    print(f"  Title: {incident1['title']}")
    print(f"  Location: {incident1['location_name']}")
    print(f"  Time: {incident1['occurred_at']}")
    print(f"  Coords: ({incident1['lat']}, {incident1['lon']})")

    print("\nIncident 2:")
    print(f"  Title: {incident2['title']}")
    print(f"  Location: {incident2['location_name']}")
    print(f"  Time: {incident2['occurred_at']}")
    print(f"  Coords: ({incident2['lat']}, {incident2['lon']})")

    print("\nExpected behavior:")
    print("  1. Generate 768-dimensional embeddings for both incidents")
    print("  2. Calculate cosine similarity")
    print("  3. Check if similarity >= 0.85 (threshold)")
    print("  4. Consider: location distance (<1km), time difference (30min)")
    print("\nExpected result:")
    print("  ✓ DUPLICATE detected (similarity ~95%, same location, same time)")
    print("  Explanation: 'very high similarity (95.3%); same location (120m); within same hour'")

    print("\n" + "=" * 70)
    print("INTEGRATION PATTERN")
    print("=" * 70)

    print("""
# Full duplicate detection pipeline:

def check_duplicate(incident):
    # Step 1: Hash-based check (existing system)
    hash_dup = check_content_hash(incident)
    if hash_dup:
        return merge_with_existing(hash_dup)

    # Step 2: Fuzzy matching (Tier 1)
    recent_titles = get_recent_titles(hours=48)
    best_match, score = FuzzyMatcher.find_best_match(
        incident['title'],
        recent_titles,
        threshold=0.75
    )
    if best_match:
        return merge_with_existing(best_match)

    # Step 3: Embedding similarity (Tier 2)
    duplicate = await embedding_dedup.find_duplicate(
        incident,
        time_window_hours=48,
        distance_km=50
    )
    if duplicate:
        dup_id, similarity, explanation = duplicate
        if similarity >= 0.92:
            # High confidence - merge
            return merge_with_existing(dup_id)
        elif similarity >= 0.85:
            # Borderline - escalate to Tier 3 (LLM)
            return await llm_dedup.analyze(incident, dup_id)

    # No duplicate - create new incident
    incident_id = create_new_incident(incident)
    embedding = await embedding_dedup.generate_embedding(incident)
    await embedding_dedup.store_embedding(incident_id, embedding)
    return incident_id
""")

    print("=" * 70)
    print("EXAMPLE COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    # Run example
    asyncio.run(example_duplicate_detection())
