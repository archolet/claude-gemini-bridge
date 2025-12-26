"""MAESTRO Decision Module - Phase 3

Contains DecisionTree, ContextAnalyzer, and decision models.

Key Components:
- DecisionTree: AI-powered mode selection with lambda-based rules
- ContextAnalyzer: HTML parsing and Tailwind token extraction
- DecisionScores: 6-dimension weighted confidence scoring
- EnrichedContext: Combined interview answers + HTML analysis
"""

from gemini_mcp.maestro.decision.context_analyzer import ContextAnalyzer
from gemini_mcp.maestro.decision.models import (
    ContextAnalysis,
    DecisionAnalysis,
    DecisionScores,
    EnrichedContext,
)
from gemini_mcp.maestro.decision.tree import DecisionTree

__all__ = [
    # Main classes
    "DecisionTree",
    "ContextAnalyzer",
    # Data models
    "DecisionScores",
    "ContextAnalysis",
    "EnrichedContext",
    "DecisionAnalysis",
]
