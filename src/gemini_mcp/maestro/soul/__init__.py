"""
MAESTRO v2 Soul Extraction Module

Extracts ProjectSoul from parsed design briefs.
This is the heart of the intelligent interview system.

Components:
- SoulExtractor: Main extraction orchestrator
- AakerAnalyzer: Brand personality analysis (Aaker Framework)
- ConfidenceCalculator: Multi-dimensional confidence scoring
- GapDetector: Identifies missing information

Pipeline:
    ParsedBrief → SoulExtractor → ProjectSoul
                      ↓
    ┌─────────────────┼─────────────────┐
    ↓                 ↓                 ↓
  AakerAnalyzer  ConfidenceCalc  GapDetector

Usage:
    >>> from gemini_mcp.maestro.soul import SoulExtractor
    >>> extractor = SoulExtractor()
    >>> soul = await extractor.extract(parsed_brief)
    >>> soul.brand_personality.dominant_trait
    'competence'
"""

from gemini_mcp.maestro.soul.extractor import SoulExtractor, ExtractionResult
from gemini_mcp.maestro.soul.aaker import AakerAnalyzer, AakerScores
from gemini_mcp.maestro.soul.confidence import ConfidenceCalculator
from gemini_mcp.maestro.soul.gaps import GapDetector

__all__ = [
    "SoulExtractor",
    "ExtractionResult",
    "AakerAnalyzer",
    "AakerScores",
    "ConfidenceCalculator",
    "GapDetector",
]
