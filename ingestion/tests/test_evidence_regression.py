"""
Evidence Regression Test Suite

Ensures the rebuild maintains or improves evidence accuracy.
Run before and after any pipeline changes to verify no regressions.

Usage:
    cd /root/repo/ingestion
    python -m pytest tests/test_evidence_regression.py -v
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime, timezone

from verification import (
    calculate_evidence_score_from_sources,
    has_official_quote,
    calculate_confidence_score,
    should_auto_verify,
)
from pipeline import IncidentProcessor, ProcessResult
from pipeline.layer1_rejection import fast_reject, has_drone_keyword
from pipeline.layer2_classification import classify_incident, has_foreign_keywords


# =============================================================================
# EVIDENCE SCORE TEST CASES
# =============================================================================

EVIDENCE_SCORE_CASES = [
    # Score 4: Official sources
    {
        "name": "Police source gets score 4",
        "sources": [{"trust_weight": 4, "source_type": "police"}],
        "expected_score": 4,
    },
    {
        "name": "Military source gets score 4",
        "sources": [{"trust_weight": 4, "source_type": "military"}],
        "expected_score": 4,
    },
    {
        "name": "Aviation authority gets score 4",
        "sources": [{"trust_weight": 4, "source_type": "notam"}],
        "expected_score": 4,
    },

    # Score 3: Multiple verified sources
    {
        "name": "Two verified media sources get score 3",
        "sources": [
            {"trust_weight": 3, "source_type": "media"},
            {"trust_weight": 3, "source_type": "media"},
        ],
        "expected_score": 3,
    },
    {
        "name": "Single verified source with official quote gets score 3",
        "sources": [{"trust_weight": 3, "source_type": "media", "source_quote": "Police confirm..."}],
        "has_official_quote": True,
        "expected_score": 3,
    },

    # Score 2: Single credible source
    {
        "name": "Single media source gets score 2",
        "sources": [{"trust_weight": 2, "source_type": "media"}],
        "expected_score": 2,
    },
    {
        "name": "Single verified source without quote gets score 2",
        "sources": [{"trust_weight": 3, "source_type": "media"}],
        "expected_score": 2,
    },

    # Score 1: Low trust or no sources
    {
        "name": "Social media source gets score 1",
        "sources": [{"trust_weight": 1, "source_type": "social"}],
        "expected_score": 1,
    },
    {
        "name": "No sources gets score 1",
        "sources": [],
        "expected_score": 1,
    },
]


class TestEvidenceScoring:
    """Test evidence score calculation remains accurate"""

    @pytest.mark.parametrize("case", EVIDENCE_SCORE_CASES, ids=lambda c: c["name"])
    def test_evidence_score(self, case):
        """Verify evidence scores match expected values"""
        has_quote = case.get("has_official_quote", False)
        score = calculate_evidence_score_from_sources(case["sources"], has_quote)
        assert score == case["expected_score"], f"Expected {case['expected_score']}, got {score}"


# =============================================================================
# PIPELINE ACCEPTANCE TEST CASES
# =============================================================================

ACCEPTANCE_CASES = [
    # SHOULD ACCEPT: Real drone incidents
    {
        "name": "Copenhagen Airport drone sighting",
        "incident": {
            "title": "Drone spotted near Copenhagen Airport",
            "narrative": "Danish police investigate drone sighting near runway",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "lat": 55.618,
            "lon": 12.647,
            "sources": [{"source_url": "https://politi.dk/123", "trust_weight": 4}],
        },
        "expected": "accept",
    },
    {
        "name": "Heathrow drone disruption",
        "incident": {
            "title": "Drones disrupt Heathrow Airport operations",
            "narrative": "Multiple flights delayed after drone sighting",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "lat": 51.47,
            "lon": -0.454,
            "sources": [{"source_url": "https://bbc.com/news/123", "trust_weight": 3}],
        },
        "expected": "accept",
    },
    {
        "name": "Swedish police drone report",
        "incident": {
            "title": "Drönare observerad vid kärnkraftverket",
            "narrative": "Polisen utreder drönarincident vid Forsmark",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "lat": 60.403,
            "lon": 18.188,
            "sources": [{"source_url": "https://polisen.se/123", "trust_weight": 4}],
        },
        "expected": "accept",
    },
]

REJECTION_CASES = [
    # SHOULD REJECT: Policy announcements
    {
        "name": "Drone ban announcement",
        "incident": {
            "title": "New drone regulations announced by EU",
            "narrative": "European commission proposes new drone flight restrictions",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "lat": 50.85,
            "lon": 4.35,
            "sources": [{"source_url": "https://eu.int/123", "trust_weight": 3}],
        },
        "expected": "reject",
        "reason_contains": "policy",
    },

    # SHOULD REJECT: Foreign incidents
    # Note: This gets rejected in Layer 2 for failing is_drone_incident() check
    # because the foreign keywords (Ukraine, Russia, Kharkiv) are detected there
    {
        "name": "Ukraine drone attack",
        "incident": {
            "title": "Russian drone strikes Ukraine power plant",
            "narrative": "Multiple casualties reported in Kharkiv",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "lat": 55.6,  # Danish coords but Ukraine content
            "lon": 12.6,
            "sources": [{"source_url": "https://reuters.com/123", "trust_weight": 3}],
        },
        "expected": "reject",
        # Rejected correctly - reason varies based on which filter catches it first
    },

    # SHOULD REJECT: Satire
    {
        "name": "Satire article",
        "incident": {
            "title": "Drones take over Copenhagen",
            "narrative": "Hilarious fake news about drone invasion",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "lat": 55.6,
            "lon": 12.6,
            "sources": [{"source_url": "https://rokokoposten.dk/drones", "trust_weight": 1}],
        },
        "expected": "reject",
        "reason_contains": "satire",
    },

    # SHOULD REJECT: Too old
    {
        "name": "Old incident (90 days)",
        "incident": {
            "title": "Drone spotted at airport",
            "narrative": "Police investigating",
            "occurred_at": "2024-01-01T00:00:00+00:00",  # Very old
            "lat": 55.6,
            "lon": 12.6,
            "sources": [{"source_url": "https://news.com/123", "trust_weight": 2}],
        },
        "expected": "reject",
        "reason_contains": "old",
    },

    # SHOULD REJECT: No drone keywords
    {
        "name": "Non-drone article",
        "incident": {
            "title": "New airport terminal opens",
            "narrative": "Copenhagen welcomes new facilities",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "lat": 55.6,
            "lon": 12.6,
            "sources": [{"source_url": "https://news.com/123", "trust_weight": 2}],
        },
        "expected": "reject",
        "reason_contains": "drone",
    },
]


class TestPipelineAcceptance:
    """Test pipeline correctly accepts real incidents"""

    @pytest.fixture
    def processor(self):
        return IncidentProcessor(ai_threshold=0.7, enable_ai=False)

    @pytest.mark.parametrize("case", ACCEPTANCE_CASES, ids=lambda c: c["name"])
    def test_accepts_real_incidents(self, processor, case):
        """Verify pipeline accepts legitimate drone incidents"""
        result = processor.process(case["incident"])
        assert result.approved, f"Should accept '{case['name']}' but got: {result.reason}"


class TestPipelineRejection:
    """Test pipeline correctly rejects non-incidents"""

    @pytest.fixture
    def processor(self):
        return IncidentProcessor(ai_threshold=0.7, enable_ai=False)

    @pytest.mark.parametrize("case", REJECTION_CASES, ids=lambda c: c["name"])
    def test_rejects_non_incidents(self, processor, case):
        """Verify pipeline rejects non-incidents"""
        result = processor.process(case["incident"])
        assert result.rejected, f"Should reject '{case['name']}' but was approved"

        if "reason_contains" in case:
            assert case["reason_contains"].lower() in result.reason.lower(), \
                f"Rejection reason should contain '{case['reason_contains']}' but was '{result.reason}'"


# =============================================================================
# LAYER 1 UNIT TESTS
# =============================================================================

class TestLayer1FastRejection:
    """Test Layer 1 fast rejection checks"""

    def test_drone_keywords_detected(self):
        """Verify drone keywords are detected"""
        assert has_drone_keyword("Drone spotted at airport", "") is True
        assert has_drone_keyword("UAV sighting reported", "") is True
        assert has_drone_keyword("Drönare över kärnkraftverk", "") is True
        assert has_drone_keyword("Drohne über Flughafen", "") is True

    def test_non_drone_rejected(self):
        """Verify non-drone content is rejected"""
        assert has_drone_keyword("Airport opens new terminal", "") is False
        assert has_drone_keyword("Weather delays flights", "") is False


# =============================================================================
# LAYER 2 UNIT TESTS
# =============================================================================

class TestLayer2Classification:
    """Test Layer 2 content classification"""

    def test_foreign_keywords_detected(self):
        """Verify foreign location keywords are detected"""
        assert has_foreign_keywords("Drone attack in Ukraine", "")[0] is True
        assert has_foreign_keywords("Russian military drone", "")[0] is True
        assert has_foreign_keywords("Drone over Washington DC", "")[0] is True

    def test_european_locations_pass(self):
        """Verify European locations pass"""
        assert has_foreign_keywords("Drone at Copenhagen Airport", "")[0] is False
        assert has_foreign_keywords("Drönare över Stockholm", "")[0] is False
        assert has_foreign_keywords("Drone near Heathrow", "")[0] is False


# =============================================================================
# OFFICIAL QUOTE DETECTION
# =============================================================================

class TestOfficialQuoteDetection:
    """Test official quote detection for evidence scoring"""

    def test_detects_police_quotes(self):
        """Verify police quotes are detected"""
        incident = {"narrative": "Police confirm they are investigating the sighting"}
        assert has_official_quote(incident) is True

    def test_detects_danish_quotes(self):
        """Verify Danish official quotes are detected"""
        incident = {"narrative": "Politiet oplyser, at de undersøger hændelsen"}
        assert has_official_quote(incident) is True

    def test_detects_source_quotes(self):
        """Verify quotes from sources are detected"""
        incident = {
            "narrative": "An incident occurred",
            "sources": [{"source_quote": "Police said they are aware of the situation"}]
        }
        assert has_official_quote(incident) is True

    def test_rejects_non_official(self):
        """Verify non-official content doesn't trigger quote detection"""
        incident = {"narrative": "Someone reported seeing something in the sky"}
        assert has_official_quote(incident) is False


# =============================================================================
# CONFIDENCE SCORE TESTS
# =============================================================================

class TestConfidenceScoring:
    """Test confidence score calculation"""

    def test_high_trust_source_high_confidence(self):
        """High trust sources should yield high confidence"""
        incident = {"asset_type": "airport", "narrative": "A detailed narrative about the incident at the airport."}
        sources = [{"trust_weight": 4, "source_quote": "Police confirmed..."}]
        score = calculate_confidence_score(incident, sources)
        assert score >= 0.7, f"Expected confidence >= 0.7 for high trust source, got {score}"

    def test_low_trust_source_lower_confidence(self):
        """Low trust sources should yield lower confidence"""
        incident = {"asset_type": "other", "narrative": ""}
        sources = [{"trust_weight": 1}]
        score = calculate_confidence_score(incident, sources)
        assert score < 0.5, f"Expected confidence < 0.5 for low trust source, got {score}"

    def test_multiple_sources_boost_confidence(self):
        """Multiple sources should boost confidence"""
        incident = {"asset_type": "airport", "narrative": "Detailed narrative here"}
        single_source = [{"trust_weight": 3}]
        multiple_sources = [{"trust_weight": 3}, {"trust_weight": 3}]

        single_score = calculate_confidence_score(incident, single_source)
        multiple_score = calculate_confidence_score(incident, multiple_sources)

        assert multiple_score > single_score, \
            f"Multiple sources ({multiple_score}) should yield higher confidence than single ({single_score})"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
