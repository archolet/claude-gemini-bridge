"""
MAESTRO Analytics Module - Phase 6.1

Provides session tracking, cost analysis, and quality metrics
for MAESTRO design wizard sessions.

Components:
- SessionTracker: Tracks session duration, questions, decisions
- CostAnalyzer: Calculates API costs based on Gemini pricing
- QualityMetrics: Aggregates 5-dimension quality scores

Usage:
    from gemini_mcp.maestro.analytics import (
        SessionTracker,
        CostAnalyzer,
        QualityMetrics,
    )

    # Session tracking (singleton)
    tracker = SessionTracker()
    tracker.start_session("maestro_123")
    tracker.record_question("maestro_123", response_time=1.5)

    # Cost analysis
    analyzer = CostAnalyzer()
    analyzer.start_session("maestro_123")
    analyzer.record_api_call("maestro_123", input_tokens=1000)

    # Quality metrics
    metrics = QualityMetrics()
    metrics.record_score("maestro_123", QualityScore(layout=8.5, ...))
"""
from __future__ import annotations

from gemini_mcp.maestro.analytics.session_tracker import (
    SessionTracker,
    SessionMetrics,
)
from gemini_mcp.maestro.analytics.cost_analyzer import (
    CostAnalyzer,
    CostBreakdown,
    PRICING,
)
from gemini_mcp.maestro.analytics.quality_metrics import (
    QualityMetrics,
    QualityScore,
)

__all__ = [
    # Session Tracking
    "SessionTracker",
    "SessionMetrics",
    # Cost Analysis
    "CostAnalyzer",
    "CostBreakdown",
    "PRICING",
    # Quality Metrics
    "QualityMetrics",
    "QualityScore",
]
