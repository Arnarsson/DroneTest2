"""
Incident Processor - Clean Pipeline Orchestration

Orchestrates the 4-layer validation pipeline:
1. Fast Rejection (satire, temporal, basic keywords)
2. Content Classification (drone incident, non-incident filter, foreign)
3. AI Verification (optional, for uncertain cases)
4. Database Enforcement (handled by PostgreSQL trigger)

This module provides a clean interface for processing incidents
through the validation pipeline.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from enum import Enum

from .layer1_rejection import fast_reject, RejectionResult
from .layer2_classification import classify_incident, ClassificationResult
from .layer3_ai_verification import verify_with_ai, AIVerificationResult

logger = logging.getLogger(__name__)


class ProcessStatus(Enum):
    """Status of incident processing"""
    APPROVED = 'approved'
    REJECTED = 'rejected'
    NEEDS_REVIEW = 'needs_review'


@dataclass
class ProcessResult:
    """Complete result of pipeline processing"""
    status: ProcessStatus
    layer: int  # Which layer made the decision (1, 2, 3, or 4)
    reason: str
    confidence: float
    category: Optional[str] = None  # For rejections: satire, temporal, policy, defense, foreign, etc.

    # Layer results for debugging/logging
    layer1_result: Optional[RejectionResult] = None
    layer2_result: Optional[ClassificationResult] = None
    layer3_result: Optional[AIVerificationResult] = None

    @property
    def approved(self) -> bool:
        return self.status == ProcessStatus.APPROVED

    @property
    def rejected(self) -> bool:
        return self.status == ProcessStatus.REJECTED


class IncidentProcessor:
    """
    Clean 4-layer incident processing pipeline.

    Usage:
        processor = IncidentProcessor(ai_threshold=0.7)
        result = processor.process(incident)

        if result.approved:
            # Send to API (Layer 4 DB validation happens there)
            send_to_api(incident)
        else:
            logger.info(f"Rejected at Layer {result.layer}: {result.reason}")
    """

    def __init__(self, ai_threshold: float = 0.7, enable_ai: bool = True):
        """
        Initialize processor.

        Args:
            ai_threshold: Layer 2 confidence below this triggers AI verification
            enable_ai: Whether to use AI verification at all
        """
        self.ai_threshold = ai_threshold
        self.enable_ai = enable_ai

        # Statistics
        self.stats = {
            'processed': 0,
            'approved': 0,
            'rejected_layer1': 0,
            'rejected_layer2': 0,
            'rejected_layer3': 0,
            'ai_calls': 0,
        }

    def process(self, incident: dict) -> ProcessResult:
        """
        Process incident through the validation pipeline.

        Layers 1-3 are handled here (Python validation).
        Layer 4 (database enforcement) happens when API inserts the incident.

        Args:
            incident: Dict with title, narrative, sources, occurred_at, lat, lon, etc.

        Returns:
            ProcessResult with status, layer, reason, and confidence
        """
        self.stats['processed'] += 1
        title = incident.get('title', '')[:50]

        # ===== LAYER 1: Fast Rejection =====
        layer1 = fast_reject(incident)
        if layer1.rejected:
            self.stats['rejected_layer1'] += 1
            logger.info(f"[L1 REJECT] {title} - {layer1.reason}")
            return ProcessResult(
                status=ProcessStatus.REJECTED,
                layer=1,
                reason=layer1.details or layer1.reason,
                confidence=1.0,  # Layer 1 is definitive
                category=layer1.reason,
                layer1_result=layer1,
            )

        # ===== LAYER 2: Content Classification =====
        layer2 = classify_incident(incident)
        if not layer2.is_incident:
            self.stats['rejected_layer2'] += 1
            logger.info(f"[L2 REJECT] {title} - {layer2.category}")
            return ProcessResult(
                status=ProcessStatus.REJECTED,
                layer=2,
                reason=layer2.reason or f'Classified as {layer2.category}',
                confidence=layer2.confidence,
                category=layer2.category,
                layer1_result=layer1,
                layer2_result=layer2,
            )

        # ===== LAYER 3: AI Verification (if enabled and uncertain) =====
        layer3 = None
        if self.enable_ai and layer2.confidence < self.ai_threshold:
            layer3 = verify_with_ai(
                incident,
                layer2_confidence=layer2.confidence,
                confidence_threshold=self.ai_threshold
            )
            if layer3.used_ai:
                self.stats['ai_calls'] += 1

            if not layer3.is_incident:
                self.stats['rejected_layer3'] += 1
                logger.info(f"[L3 REJECT] {title} - {layer3.category}")
                return ProcessResult(
                    status=ProcessStatus.REJECTED,
                    layer=3,
                    reason=layer3.reasoning,
                    confidence=layer3.confidence,
                    category=layer3.category,
                    layer1_result=layer1,
                    layer2_result=layer2,
                    layer3_result=layer3,
                )

        # ===== APPROVED: Ready for Layer 4 (Database) =====
        self.stats['approved'] += 1
        final_confidence = layer3.confidence if layer3 else layer2.confidence

        logger.info(f"[APPROVED] {title} (confidence={final_confidence:.2f})")
        return ProcessResult(
            status=ProcessStatus.APPROVED,
            layer=3 if layer3 and layer3.used_ai else 2,
            reason='Passed all validation layers',
            confidence=final_confidence,
            category='incident',
            layer1_result=layer1,
            layer2_result=layer2,
            layer3_result=layer3,
        )

    def get_stats(self) -> dict:
        """Get processing statistics"""
        return {
            **self.stats,
            'approval_rate': (
                self.stats['approved'] / self.stats['processed']
                if self.stats['processed'] > 0 else 0
            ),
            'ai_usage_rate': (
                self.stats['ai_calls'] / self.stats['processed']
                if self.stats['processed'] > 0 else 0
            ),
        }

    def reset_stats(self):
        """Reset statistics counters"""
        for key in self.stats:
            self.stats[key] = 0
