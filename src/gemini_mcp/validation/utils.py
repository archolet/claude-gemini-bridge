"""
Shared Validation Utilities for Gemini MCP Server.

This module provides shared utility functions used across validators:
- Color conversion (hex_to_rgb, rgb_to_hex, tailwind_to_hex)
- WCAG luminance and contrast calculations
- HTML class extraction patterns

All validators should import from this module to avoid duplication.
"""

from __future__ import annotations

import colorsys
import re
from typing import Tuple, List, Set, Optional


# ═══════════════════════════════════════════════════════════════
# REGEX PATTERNS (Shared across validators)
# ═══════════════════════════════════════════════════════════════

# Pattern to extract class attribute from HTML elements
HTML_CLASS_PATTERN = re.compile(
    r'class=["\']([^"\']*)["\']',
    re.IGNORECASE
)

# Pattern to find HTML elements with class attribute
HTML_ELEMENT_WITH_CLASS_PATTERN = re.compile(
    r'<(\w+)[^>]*class=["\']([^"\']*)["\'][^>]*>',
    re.IGNORECASE
)

# Pattern to extract Tailwind color classes (text-*, bg-*, border-*)
TAILWIND_COLOR_CLASS_PATTERN = re.compile(
    r'\b(text|bg|border|ring|from|to|via)-(\w+-\d+|white|black|transparent)\b'
)

# Pattern to split class string into individual classes
CLASS_SPLIT_PATTERN = re.compile(r'\s+')

# Pattern to extract IDs from HTML
HTML_ID_PATTERN = re.compile(
    r'id=["\']([^"\']+)["\']',
    re.IGNORECASE
)


# ═══════════════════════════════════════════════════════════════
# COLOR CONVERSION UTILITIES
# ═══════════════════════════════════════════════════════════════

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#ff0000", "ff0000", or "#fff")

    Returns:
        Tuple of (R, G, B) values (0-255)

    Raises:
        ValueError: If hex color is invalid
    """
    hex_color = hex_color.lstrip("#")

    # Handle shorthand (e.g., "fff" -> "ffffff")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)

    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")

    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hex color.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        Hex color string with # prefix
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
    """
    Convert hex color to HSL values.

    Args:
        hex_color: Hex color string

    Returns:
        Tuple of (H: 0-360, S: 0-100, L: 0-100)
    """
    r, g, b = hex_to_rgb(hex_color)
    r, g, b = r / 255, g / 255, b / 255
    hue, lum, sat = colorsys.rgb_to_hls(r, g, b)
    return hue * 360, sat * 100, lum * 100


def hsl_to_hex(h: float, s: float, lightness: float) -> str:
    """
    Convert HSL values to hex color.

    Args:
        h: Hue (0-360)
        s: Saturation (0-100)
        lightness: Lightness (0-100)

    Returns:
        Hex color string with # prefix
    """
    h, s, lum = h / 360, s / 100, lightness / 100
    r, g, b = colorsys.hls_to_rgb(h, lum, s)
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


# ═══════════════════════════════════════════════════════════════
# WCAG LUMINANCE & CONTRAST
# ═══════════════════════════════════════════════════════════════

def relative_luminance(r: int, g: int, b: int) -> float:
    """
    Calculate relative luminance from RGB values per WCAG 2.1.

    Formula: L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    where R, G, B are linearized (gamma corrected)

    See: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        Relative luminance (0.0 to 1.0)
    """
    def linearize(value: int) -> float:
        """Linearize an 8-bit color value."""
        v = value / 255
        if v <= 0.03928:
            return v / 12.92
        return ((v + 0.055) / 1.055) ** 2.4

    r_lin = linearize(r)
    g_lin = linearize(g)
    b_lin = linearize(b)

    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate WCAG contrast ratio between two hex colors.

    Formula: (L1 + 0.05) / (L2 + 0.05)
    where L1 is the lighter color's luminance

    Args:
        color1: First hex color
        color2: Second hex color

    Returns:
        Contrast ratio (1.0 to 21.0)
    """
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
        foreground: Foreground (text) color in hex format
        background: Background color in hex format
        level: WCAG level - "AA" or "AAA"
        text_size: Text size - "normal" or "large"

    Returns:
        Tuple of (passes, ratio, message)
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


# ═══════════════════════════════════════════════════════════════
# TAILWIND COLOR UTILITIES
# ═══════════════════════════════════════════════════════════════

def tailwind_to_hex(color: str, color_map: Optional[dict] = None) -> str:
    """
    Convert Tailwind color class to hex.

    Args:
        color: Tailwind color (e.g., "blue-500") or hex color
        color_map: Optional custom color map (uses TAILWIND_COLORS if None)

    Returns:
        Hex color string or original value if not found
    """
    # Import here to avoid circular import
    from gemini_mcp.constants.colors import TAILWIND_COLOR_MAP

    if color_map is None:
        color_map = TAILWIND_COLOR_MAP

    # Already a hex color
    if color.startswith("#"):
        return color

    # Handle special values
    if color in ("transparent", "currentColor", "inherit"):
        return color

    # Try direct lookup
    if color in color_map:
        return color_map[color]

    # Try without prefix (text-, bg-, border-, etc.)
    for prefix in ["text-", "bg-", "border-", "ring-", "from-", "to-", "via-"]:
        if color.startswith(prefix):
            color_name = color[len(prefix):]
            if color_name in color_map:
                return color_map[color_name]

    # Not found
    return color


# ═══════════════════════════════════════════════════════════════
# HTML CLASS EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_classes_from_html(html: str) -> List[str]:
    """
    Extract all CSS classes from HTML content.

    Args:
        html: HTML string

    Returns:
        List of all class names found
    """
    classes = []
    for match in HTML_CLASS_PATTERN.finditer(html):
        class_string = match.group(1)
        classes.extend(CLASS_SPLIT_PATTERN.split(class_string))
    return [c.strip() for c in classes if c.strip()]


def extract_tailwind_colors(html: str) -> Set[str]:
    """
    Extract Tailwind color classes from HTML content.

    Args:
        html: HTML string

    Returns:
        Set of color classes (e.g., {"text-blue-500", "bg-white"})
    """
    colors = set()
    for match in TAILWIND_COLOR_CLASS_PATTERN.finditer(html):
        prefix = match.group(1)
        color = match.group(2)
        colors.add(f"{prefix}-{color}")
    return colors


def extract_color_pairs(html: str) -> List[Tuple[str, str, str]]:
    """
    Extract text/background color pairs from HTML with Tailwind classes.

    Args:
        html: HTML string

    Returns:
        List of (element_description, text_color, bg_color) tuples
    """
    pairs = []

    for match in HTML_ELEMENT_WITH_CLASS_PATTERN.finditer(html):
        tag = match.group(1)
        classes = match.group(2)

        # Extract text color
        text_match = re.search(r'text-(\w+-\d+|white|black)', classes)
        # Extract background color
        bg_match = re.search(r'bg-(\w+-\d+|white|black)', classes)

        if text_match and bg_match:
            text_color = text_match.group(1)
            bg_color = bg_match.group(1)
            element_desc = f"<{tag}> with text-{text_color} on bg-{bg_color}"
            pairs.append((element_desc, text_color, bg_color))

    return pairs


def extract_ids_from_html(html: str) -> List[str]:
    """
    Extract all ID attributes from HTML content.

    Args:
        html: HTML string

    Returns:
        List of ID values found
    """
    return [match.group(1) for match in HTML_ID_PATTERN.finditer(html)]
