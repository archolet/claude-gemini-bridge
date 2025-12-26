"""
MAESTRO Intelligence Module - Phase 6.3

Smart adaptive systems for improved user experience:
- AdaptiveFlow: Dynamic interview flow based on context
- PreferenceLearner: Learn and apply user patterns
- Recommender: Intelligent suggestions and defaults
"""
from __future__ import annotations

from gemini_mcp.maestro.intelligence.adaptive_flow import (
    AdaptiveFlow,
    FlowContext,
    SkipDecision,
)
from gemini_mcp.maestro.intelligence.preference_learner import (
    PreferenceLearner,
    UserPreference,
    PreferencePattern,
)
from gemini_mcp.maestro.intelligence.recommender import (
    Recommender,
    Recommendation,
    RecommendationType,
)

__all__ = [
    # Adaptive Flow
    "AdaptiveFlow",
    "FlowContext",
    "SkipDecision",
    # Preference Learner
    "PreferenceLearner",
    "UserPreference",
    "PreferencePattern",
    # Recommender
    "Recommender",
    "Recommendation",
    "RecommendationType",
]
