"""
MAESTRO UI Module - Phase 6.2

Provides rich formatting, progress indicators, and summary generators
for MAESTRO design wizard sessions.

Components:
- MaestroFormatter: Rich text formatting for questions and options
- Progress indicators: Visual progress bars and status displays
- Summary generators: Decision and execution summaries
"""
from __future__ import annotations

from gemini_mcp.maestro.ui.formatter import (
    MaestroFormatter,
    CATEGORY_TIPS,
    PARAMETER_LABELS,
    QUESTION_TYPE_ICONS,
)
from gemini_mcp.maestro.ui.summary import (
    MODE_DESCRIPTIONS,
    CONFIDENCE_LEVELS,
    generate_decision_summary,
    generate_execution_summary,
    generate_session_complete_summary,
)
from gemini_mcp.maestro.ui.progress import (
    generate_progress_bar,
    generate_interview_progress,
    generate_execution_progress,
    generate_quality_progress,
)

__all__ = [
    # Formatter
    "MaestroFormatter",
    "CATEGORY_TIPS",
    "PARAMETER_LABELS",
    "QUESTION_TYPE_ICONS",
    # Summary
    "MODE_DESCRIPTIONS",
    "CONFIDENCE_LEVELS",
    "generate_decision_summary",
    "generate_execution_summary",
    "generate_session_complete_summary",
    # Progress
    "generate_progress_bar",
    "generate_interview_progress",
    "generate_execution_progress",
    "generate_quality_progress",
]
