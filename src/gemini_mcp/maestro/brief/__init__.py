"""
MAESTRO v2 Brief Parser Module

Handles parsing and validation of design briefs.
Extracts structured information from natural language input.

Components:
- BriefParser: Main parser orchestrator
- BriefValidator: Validates brief structure and content
- NLPExtractor: Extracts entities using regex + Gemini

Usage:
    >>> from gemini_mcp.maestro.brief import BriefParser
    >>> parser = BriefParser()
    >>> result = await parser.parse("Design a modern fintech dashboard...")
    >>> result.project_name
    'Fintech Dashboard'
"""

from gemini_mcp.maestro.brief.parser import BriefParser, ParsedBrief
from gemini_mcp.maestro.brief.validator import BriefValidator, ValidationResult
from gemini_mcp.maestro.brief.extractor import NLPExtractor, ExtractedEntities

__all__ = [
    "BriefParser",
    "ParsedBrief",
    "BriefValidator",
    "ValidationResult",
    "NLPExtractor",
    "ExtractedEntities",
]
