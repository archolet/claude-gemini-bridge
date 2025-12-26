"""MAESTRO Execution Module - Phase 4 & 5

Contains ToolExecutor for executing design tools based on MaestroDecision.

Key Components:
- ToolExecutor: Bridges MaestroDecision to GeminiClient calls
- Adapters: Parameter transformation functions for each mode
- Pipeline configs: MODE_TO_PIPELINE, QUALITY_CONFIGS (Phase 5)

Architecture:
    MaestroDecision → Adapter → GeminiClient method → Result

    With Trifecta (use_trifecta=True):
    MaestroDecision → Pipeline → [Architect → Alchemist → Physicist → QualityGuard] → Result
"""

from gemini_mcp.maestro.execution.executor import (
    ToolExecutor,
    MODE_TO_PIPELINE,
    QUALITY_CONFIGS,
)
from gemini_mcp.maestro.execution.adapters import (
    adapt_for_design_frontend,
    adapt_for_design_page,
    adapt_for_design_section,
    adapt_for_refine_frontend,
    adapt_for_replace_section,
    adapt_for_design_from_reference,
)

__all__ = [
    # Main class
    "ToolExecutor",
    # Phase 5: Pipeline configurations
    "MODE_TO_PIPELINE",
    "QUALITY_CONFIGS",
    # Adapters (for testing/extension)
    "adapt_for_design_frontend",
    "adapt_for_design_page",
    "adapt_for_design_section",
    "adapt_for_refine_frontend",
    "adapt_for_replace_section",
    "adapt_for_design_from_reference",
]
