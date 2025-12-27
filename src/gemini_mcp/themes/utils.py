"""
Utility functions for theme operations.

Includes color conversion, contrast calculation, and WCAG validation utilities.
Most color utilities are imported from gemini_mcp.validation.utils to avoid duplication.
"""

from __future__ import annotations

from typing import Tuple

# Import core color utilities from validation module (single source of truth)
from gemini_mcp.validation.utils import (
    hex_to_rgb,
    rgb_to_hex,
    hex_to_hsl,
    hsl_to_hex,
    relative_luminance,
    contrast_ratio,
    validate_contrast,
)

# Re-export for backward compatibility
__all__ = [
    # Color conversions
    "hex_to_rgb",
    "rgb_to_hex",
    "hex_to_hsl",
    "hsl_to_hex",
    # WCAG utilities
    "relative_luminance",
    "contrast_ratio",
    "validate_contrast",
    # Theme-specific utilities
    "to_css_color",
    "next_shadow",
    "next_intensity",
]


# ═══════════════════════════════════════════════════════════════
# THEME-SPECIFIC UTILITIES
# ═══════════════════════════════════════════════════════════════

def to_css_color(tailwind_color: str) -> str:
    """Convert Tailwind color to CSS RGB values."""
    color_map = {
        "blue-600": "59 130 246",
        "blue-700": "29 78 216",
        "blue-800": "30 64 175",
        "indigo-600": "79 70 229",
        "indigo-500": "99 102 241",
        "pink-500": "236 72 153",
    }
    return color_map.get(tailwind_color, "59 130 246")


def next_shadow(intensity: str) -> str:
    """Get the next shadow intensity level for hover states."""
    shadow_levels = ["none", "sm", "md", "lg", "xl", "2xl"]
    try:
        idx = shadow_levels.index(intensity)
        return shadow_levels[min(idx + 1, len(shadow_levels) - 1)]
    except ValueError:
        return "md"


def next_intensity(current: str, intensities: list[str] | None = None) -> str:
    """Get the next intensity level from a list."""
    if intensities is None:
        intensities = ["subtle", "medium", "strong", "intense", "extreme"]
    try:
        idx = intensities.index(current)
        return intensities[min(idx + 1, len(intensities) - 1)]
    except ValueError:
        return intensities[1] if len(intensities) > 1 else current
