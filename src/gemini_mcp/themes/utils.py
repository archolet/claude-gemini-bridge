"""
Utility functions for theme operations.

Includes color conversion, contrast calculation, and WCAG validation utilities.
"""

from __future__ import annotations

import colorsys
from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color to HSL values (h: 0-360, s: 0-100, l: 0-100)."""
    r, g, b = hex_to_rgb(hex_color)
    r, g, b = r / 255, g / 255, b / 255
    hue, lum, sat = colorsys.rgb_to_hls(r, g, b)
    return hue * 360, sat * 100, lum * 100


def hsl_to_hex(h: float, s: float, lightness: float) -> str:
    """Convert HSL (h: 0-360, s: 0-100, l: 0-100) to hex color."""
    h, s, lum = h / 360, s / 100, lightness / 100
    r, g, b = colorsys.hls_to_rgb(h, lum, s)
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


def relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance per WCAG 2.1."""
    def adjust(c: int) -> float:
        c_normalized = c / 255
        return c_normalized / 12.92 if c_normalized <= 0.03928 else ((c_normalized + 0.055) / 1.055) ** 2.4
    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)


def contrast_ratio(color1: str, color2: str) -> float:
    """Calculate contrast ratio between two hex colors."""
    l1 = relative_luminance(*hex_to_rgb(color1))
    l2 = relative_luminance(*hex_to_rgb(color2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def validate_contrast(
    foreground: str,
    background: str,
    level: str = "AA",
    text_size: str = "normal"
) -> Tuple[bool, float, str]:
    """
    Validate WCAG contrast requirements.

    Args:
        foreground: Foreground (text) color in hex format.
        background: Background color in hex format.
        level: WCAG level - "AA" or "AAA".
        text_size: Text size - "normal" or "large".

    Returns:
        Tuple of (passes, ratio, message).
    """
    ratio = contrast_ratio(foreground, background)

    requirements = {
        ("AA", "normal"): 4.5,
        ("AA", "large"): 3.0,
        ("AAA", "normal"): 7.0,
        ("AAA", "large"): 4.5,
    }

    required = requirements.get((level, text_size), 4.5)
    passes = ratio >= required

    message = f"Contrast ratio: {ratio:.2f}:1 ({'PASS' if passes else 'FAIL'} {level} {text_size})"

    return passes, ratio, message


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
