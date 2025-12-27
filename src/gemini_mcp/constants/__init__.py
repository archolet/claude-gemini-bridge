"""Constants module for Gemini MCP.

This module provides centralized constant definitions used across the Gemini MCP server.

Available exports:
    - TAILWIND_COLOR_MAP: Full Tailwind color palette with HEX values
    - HEX_TO_TAILWIND_MAP: Reverse mapping from HEX to Tailwind class
    - COLOR_PREFIXES: Tuple of color utility prefixes (bg-, border-, etc.)
    - TEXT_COLOR_PREFIXES: Tuple of text color prefixes
    - TYPOGRAPHY_PREFIXES: Tuple of typography class prefixes
    - SPACING_PREFIXES: Tuple of spacing class prefixes
    - EFFECTS_PREFIXES: Tuple of effects class prefixes
    - COLOR_FAMILIES: Tuple of Tailwind color family names
    - COLOR_SHADES: Tuple of Tailwind shade levels (50-950)
"""

from .colors import (
    TAILWIND_COLOR_MAP,
    HEX_TO_TAILWIND_MAP,
    COLOR_PREFIXES,
    TEXT_COLOR_PREFIXES,
    TYPOGRAPHY_PREFIXES,
    SPACING_PREFIXES,
    EFFECTS_PREFIXES,
    COLOR_FAMILIES,
    COLOR_SHADES,
)
from .tier_mapping import (
    ComponentTier,
    TIER_MAPPING,
    TIER_FEATURES,
    TIER_QUALITY_THRESHOLDS,
    get_component_tier,
    get_tier_features,
    get_tier_quality_threshold,
    get_tier_name,
)

__all__ = [
    # Colors
    "TAILWIND_COLOR_MAP",
    "HEX_TO_TAILWIND_MAP",
    "COLOR_PREFIXES",
    "TEXT_COLOR_PREFIXES",
    "TYPOGRAPHY_PREFIXES",
    "SPACING_PREFIXES",
    "EFFECTS_PREFIXES",
    "COLOR_FAMILIES",
    "COLOR_SHADES",
    # Tier System
    "ComponentTier",
    "TIER_MAPPING",
    "TIER_FEATURES",
    "TIER_QUALITY_THRESHOLDS",
    "get_component_tier",
    "get_tier_features",
    "get_tier_quality_threshold",
    "get_tier_name",
]
