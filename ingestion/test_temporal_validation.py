#!/usr/bin/env python3
"""Test temporal validation"""
from datetime import datetime, timedelta, timezone
from utils import is_recent_incident, format_age

def test_recent_incident():
    """Test recent incident (2 days ago) → ACCEPTED"""
    now = datetime.now(timezone.utc)
    recent = now - timedelta(days=2)

    is_valid, reason = is_recent_incident(recent)
    assert is_valid == True
    assert reason == "Recent incident"
    print("✓ Test 1 passed: Recent incident (2 days) accepted")

def test_future_date():
    """Test future date (2 days ahead) → BLOCKED"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=2)

    is_valid, reason = is_recent_incident(future)
    assert is_valid == False
    assert "Future date" in reason
    print("✓ Test 2 passed: Future date blocked")

def test_too_old():
    """Test old incident (10 days ago) → BLOCKED"""
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=10)

    is_valid, reason = is_recent_incident(old)
    assert is_valid == False
    assert "Too old: 10 days ago" in reason
    print("✓ Test 3 passed: Old incident (10 days) blocked")

def test_ancient_history():
    """Test historical incident (2 years ago) → BLOCKED"""
    now = datetime.now(timezone.utc)
    ancient = now - timedelta(days=730)

    is_valid, reason = is_recent_incident(ancient)
    assert is_valid == False
    assert "Historical article" in reason
    print("✓ Test 4 passed: Ancient incident (2 years) blocked")

def test_edge_case_7_days():
    """Test exactly 7 days old → ACCEPTED"""
    now = datetime.now(timezone.utc)
    edge = now - timedelta(days=7)

    is_valid, reason = is_recent_incident(edge, max_age_days=7)
    assert is_valid == True
    print("✓ Test 5 passed: Edge case (exactly 7 days) accepted")

def test_format_age():
    """Test age formatting"""
    now = datetime.now(timezone.utc)

    # 2 days ago
    two_days = now - timedelta(days=2)
    assert format_age(two_days) == "2 days ago"

    # 5 hours ago
    five_hours = now - timedelta(hours=5)
    assert "5 hours ago" in format_age(five_hours)

    # 30 minutes ago
    thirty_min = now - timedelta(minutes=30)
    assert "30 minutes ago" in format_age(thirty_min)

    print("✓ Test 6 passed: Age formatting works")

if __name__ == "__main__":
    print("=== Temporal Validation Test Suite ===\n")
    test_recent_incident()
    test_future_date()
    test_too_old()
    test_ancient_history()
    test_edge_case_7_days()
    test_format_age()
    print("\n✅ All temporal validation tests passed!")
