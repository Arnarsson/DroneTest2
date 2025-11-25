"""
DroneWatch Ingestion Pipeline - Clean 4-Layer Architecture

LAYER 1: Fast Rejection (Python, <50ms)
    - Satire domain blocking
    - Temporal validation
    - Basic drone keyword check
    Result: ~60% rejected early with no DB/API calls

LAYER 2: Content Classification (Python, ~100ms)
    - Full is_drone_incident() check
    - Geographic text filtering
    - Non-incident detection (policy, defense, simulation)
    Result: ~20% additional rejected

LAYER 3: AI Verification (Optional, ~300ms)
    - OpenRouter GPT classification
    - Only triggers when Layer 2 confidence < 0.7
    - Categories: incident / policy / defense / discussion
    Result: Catches ~5-10% edge cases

LAYER 4: Database Enforcement (PostgreSQL, <10ms)
    - Geographic bounds (35-71°N, -10-31°E)
    - Foreign keyword rejection
    - Content hash uniqueness
    - Spatial deduplication (ST_DWithin)
    Result: AUTHORITATIVE - cannot be bypassed
"""

from .layer1_rejection import fast_reject
from .layer2_classification import classify_incident
from .layer3_ai_verification import verify_with_ai, AIVerificationResult
from .processor import IncidentProcessor, ProcessResult

__all__ = [
    'fast_reject',
    'classify_incident',
    'verify_with_ai',
    'AIVerificationResult',
    'IncidentProcessor',
    'ProcessResult',
]
