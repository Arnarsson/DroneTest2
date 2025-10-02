#!/usr/bin/env python3
"""Test AI similarity engine with sample incidents"""
import asyncio
import sys
import os
from pathlib import Path

# Add ingestion to path
sys.path.insert(0, str(Path(__file__).parent / 'ingestion'))

# Load .env from ingestion directory
from dotenv import load_dotenv
load_dotenv('ingestion/.env')

from ingestion.ai_similarity import OpenRouterClient

async def test_similarity():
    client = OpenRouterClient()
    
    if not client.enabled:
        print("❌ OpenRouter client not enabled")
        print("   Check OPENROUTER_API_KEY in ingestion/.env")
        return
    
    print("✅ OpenRouter client enabled")
    print(f"   Model: {client.model}")
    
    # Test with two incidents from the API analysis
    incident1 = {
        'id': '62b3a8a5',
        'title': 'Eksplosiv vækst: Droneangreb har fået mange til at melde sig',
        'narrative': 'Hjemmeværnets styrke af soldater vokser - især efter sidste uges hybridangreb med droner.',
        'lat': 55.618,
        'lon': 12.6476,
        'occurred_at': '2025-10-01T04:00:00+00:00',
        'evidence_score': 3,
        'asset_type': 'airport'
    }
    
    incident2 = {
        'id': '4d918254',
        'title': 'Skib med mulig forbindelse til dronesagen efterforskes i Frankrig',
        'narrative': 'USA har drone-værn i København under topmøde. USA støtter Danmark med anti-drone kapabiliteter.',
        'lat': 55.618,
        'lon': 12.6496,
        'occurred_at': '2025-09-30T13:37:00+00:00',
        'evidence_score': 3,
        'asset_type': 'airport'
    }
    
    print("\n🔍 Testing AI similarity analysis...")
    print(f"\n📍 Incident 1: {incident1['title'][:60]}...")
    print(f"📍 Incident 2: {incident2['title'][:60]}...")
    
    result = await client.are_incidents_duplicate(incident1, incident2)
    
    print(f"\n🤖 AI Analysis Result:")
    print(f"   Is Duplicate: {result.is_duplicate}")
    print(f"   Confidence: {result.confidence:.2%}")
    print(f"   Method: {result.method}")
    print(f"   Reasoning: {result.reasoning}")
    
    if result.merged_title:
        print(f"\n   Merged Title: {result.merged_title}")
    if result.merged_narrative:
        print(f"   Merged Narrative: {result.merged_narrative[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_similarity())
