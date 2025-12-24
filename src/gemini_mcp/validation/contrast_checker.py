"""
Contrast Checker - WCAG Color Contrast Validation

This module provides utilities for validating color contrast ratios
according to WCAG 2.1 guidelines.

WCAG Contrast Requirements:
- Level AA (Normal text): 4.5:1
- Level AA (Large text 18pt+ or 14pt bold): 3:1
- Level AAA (Normal text): 7:1
- Level AAA (Large text): 4.5:1
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# TAILWIND COLOR MAP - Common Tailwind colors to hex values
# ═══════════════════════════════════════════════════════════════

TAILWIND_COLORS: dict[str, str] = {
    # Grays
    "slate-50": "#f8fafc", "slate-100": "#f1f5f9", "slate-200": "#e2e8f0",
    "slate-300": "#cbd5e1", "slate-400": "#94a3b8", "slate-500": "#64748b",
    "slate-600": "#475569", "slate-700": "#334155", "slate-800": "#1e293b",
    "slate-900": "#0f172a", "slate-950": "#020617",

    "gray-50": "#f9fafb", "gray-100": "#f3f4f6", "gray-200": "#e5e7eb",
    "gray-300": "#d1d5db", "gray-400": "#9ca3af", "gray-500": "#6b7280",
    "gray-600": "#4b5563", "gray-700": "#374151", "gray-800": "#1f2937",
    "gray-900": "#111827", "gray-950": "#030712",

    "zinc-50": "#fafafa", "zinc-100": "#f4f4f5", "zinc-200": "#e4e4e7",
    "zinc-300": "#d4d4d8", "zinc-400": "#a1a1aa", "zinc-500": "#71717a",
    "zinc-600": "#52525b", "zinc-700": "#3f3f46", "zinc-800": "#27272a",
    "zinc-900": "#18181b", "zinc-950": "#09090b",

    "neutral-50": "#fafafa", "neutral-100": "#f5f5f5", "neutral-200": "#e5e5e5",
    "neutral-300": "#d4d4d4", "neutral-400": "#a3a3a3", "neutral-500": "#737373",
    "neutral-600": "#525252", "neutral-700": "#404040", "neutral-800": "#262626",
    "neutral-900": "#171717", "neutral-950": "#0a0a0a",

    "stone-50": "#fafaf9", "stone-100": "#f5f5f4", "stone-200": "#e7e5e4",
    "stone-300": "#d6d3d1", "stone-400": "#a8a29e", "stone-500": "#78716c",
    "stone-600": "#57534e", "stone-700": "#44403c", "stone-800": "#292524",
    "stone-900": "#1c1917", "stone-950": "#0c0a09",

    # Colors
    "red-50": "#fef2f2", "red-100": "#fee2e2", "red-200": "#fecaca",
    "red-300": "#fca5a5", "red-400": "#f87171", "red-500": "#ef4444",
    "red-600": "#dc2626", "red-700": "#b91c1c", "red-800": "#991b1b",
    "red-900": "#7f1d1d", "red-950": "#450a0a",

    "orange-50": "#fff7ed", "orange-100": "#ffedd5", "orange-200": "#fed7aa",
    "orange-300": "#fdba74", "orange-400": "#fb923c", "orange-500": "#f97316",
    "orange-600": "#ea580c", "orange-700": "#c2410c", "orange-800": "#9a3412",
    "orange-900": "#7c2d12", "orange-950": "#431407",

    "amber-50": "#fffbeb", "amber-100": "#fef3c7", "amber-200": "#fde68a",
    "amber-300": "#fcd34d", "amber-400": "#fbbf24", "amber-500": "#f59e0b",
    "amber-600": "#d97706", "amber-700": "#b45309", "amber-800": "#92400e",
    "amber-900": "#78350f", "amber-950": "#451a03",

    "yellow-50": "#fefce8", "yellow-100": "#fef9c3", "yellow-200": "#fef08a",
    "yellow-300": "#fde047", "yellow-400": "#facc15", "yellow-500": "#eab308",
    "yellow-600": "#ca8a04", "yellow-700": "#a16207", "yellow-800": "#854d0e",
    "yellow-900": "#713f12", "yellow-950": "#422006",

    "lime-50": "#f7fee7", "lime-100": "#ecfccb", "lime-200": "#d9f99d",
    "lime-300": "#bef264", "lime-400": "#a3e635", "lime-500": "#84cc16",
    "lime-600": "#65a30d", "lime-700": "#4d7c0f", "lime-800": "#3f6212",
    "lime-900": "#365314", "lime-950": "#1a2e05",

    "green-50": "#f0fdf4", "green-100": "#dcfce7", "green-200": "#bbf7d0",
    "green-300": "#86efac", "green-400": "#4ade80", "green-500": "#22c55e",
    "green-600": "#16a34a", "green-700": "#15803d", "green-800": "#166534",
    "green-900": "#14532d", "green-950": "#052e16",

    "emerald-50": "#ecfdf5", "emerald-100": "#d1fae5", "emerald-200": "#a7f3d0",
    "emerald-300": "#6ee7b7", "emerald-400": "#34d399", "emerald-500": "#10b981",
    "emerald-600": "#059669", "emerald-700": "#047857", "emerald-800": "#065f46",
    "emerald-900": "#064e3b", "emerald-950": "#022c22",

    "teal-50": "#f0fdfa", "teal-100": "#ccfbf1", "teal-200": "#99f6e4",
    "teal-300": "#5eead4", "teal-400": "#2dd4bf", "teal-500": "#14b8a6",
    "teal-600": "#0d9488", "teal-700": "#0f766e", "teal-800": "#115e59",
    "teal-900": "#134e4a", "teal-950": "#042f2e",

    "cyan-50": "#ecfeff", "cyan-100": "#cffafe", "cyan-200": "#a5f3fc",
    "cyan-300": "#67e8f9", "cyan-400": "#22d3ee", "cyan-500": "#06b6d4",
    "cyan-600": "#0891b2", "cyan-700": "#0e7490", "cyan-800": "#155e75",
    "cyan-900": "#164e63", "cyan-950": "#083344",

    "sky-50": "#f0f9ff", "sky-100": "#e0f2fe", "sky-200": "#bae6fd",
    "sky-300": "#7dd3fc", "sky-400": "#38bdf8", "sky-500": "#0ea5e9",
    "sky-600": "#0284c7", "sky-700": "#0369a1", "sky-800": "#075985",
    "sky-900": "#0c4a6e", "sky-950": "#082f49",

    "blue-50": "#eff6ff", "blue-100": "#dbeafe", "blue-200": "#bfdbfe",
    "blue-300": "#93c5fd", "blue-400": "#60a5fa", "blue-500": "#3b82f6",
    "blue-600": "#2563eb", "blue-700": "#1d4ed8", "blue-800": "#1e40af",
    "blue-900": "#1e3a8a", "blue-950": "#172554",

    "indigo-50": "#eef2ff", "indigo-100": "#e0e7ff", "indigo-200": "#c7d2fe",
    "indigo-300": "#a5b4fc", "indigo-400": "#818cf8", "indigo-500": "#6366f1",
    "indigo-600": "#4f46e5", "indigo-700": "#4338ca", "indigo-800": "#3730a3",
    "indigo-900": "#312e81", "indigo-950": "#1e1b4b",

    "violet-50": "#f5f3ff", "violet-100": "#ede9fe", "violet-200": "#ddd6fe",
    "violet-300": "#c4b5fd", "violet-400": "#a78bfa", "violet-500": "#8b5cf6",
    "violet-600": "#7c3aed", "violet-700": "#6d28d9", "violet-800": "#5b21b6",
    "violet-900": "#4c1d95", "violet-950": "#2e1065",

    "purple-50": "#faf5ff", "purple-100": "#f3e8ff", "purple-200": "#e9d5ff",
    "purple-300": "#d8b4fe", "purple-400": "#c084fc", "purple-500": "#a855f7",
    "purple-600": "#9333ea", "purple-700": "#7e22ce", "purple-800": "#6b21a8",
    "purple-900": "#581c87", "purple-950": "#3b0764",

    "fuchsia-50": "#fdf4ff", "fuchsia-100": "#fae8ff", "fuchsia-200": "#f5d0fe",
    "fuchsia-300": "#f0abfc", "fuchsia-400": "#e879f9", "fuchsia-500": "#d946ef",
    "fuchsia-600": "#c026d3", "fuchsia-700": "#a21caf", "fuchsia-800": "#86198f",
    "fuchsia-900": "#701a75", "fuchsia-950": "#4a044e",

    "pink-50": "#fdf2f8", "pink-100": "#fce7f3", "pink-200": "#fbcfe8",
    "pink-300": "#f9a8d4", "pink-400": "#f472b6", "pink-500": "#ec4899",
    "pink-600": "#db2777", "pink-700": "#be185d", "pink-800": "#9d174d",
    "pink-900": "#831843", "pink-950": "#500724",

    "rose-50": "#fff1f2", "rose-100": "#ffe4e6", "rose-200": "#fecdd3",
    "rose-300": "#fda4af", "rose-400": "#fb7185", "rose-500": "#f43f5e",
    "rose-600": "#e11d48", "rose-700": "#be123c", "rose-800": "#9f1239",
    "rose-900": "#881337", "rose-950": "#4c0519",

    # Special colors
    "white": "#ffffff",
    "black": "#000000",
    "transparent": "transparent",
}


# ═══════════════════════════════════════════════════════════════
# CONTRAST DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════

@dataclass
class ContrastResult:
    """Result of a single contrast check."""

    foreground: str  # Color (hex or Tailwind class)
    background: str  # Color (hex or Tailwind class)
    ratio: float  # Calculated contrast ratio
    passes_aa_normal: bool  # Passes WCAG AA for normal text (4.5:1)
    passes_aa_large: bool  # Passes WCAG AA for large text (3:1)
    passes_aaa_normal: bool  # Passes WCAG AAA for normal text (7:1)
    passes_aaa_large: bool  # Passes WCAG AAA for large text (4.5:1)

    @property
    def passes_aa(self) -> bool:
        """Check if passes AA for normal text."""
        return self.passes_aa_normal

    @property
    def passes_aaa(self) -> bool:
        """Check if passes AAA for normal text."""
        return self.passes_aaa_normal


@dataclass
class ContrastIssue:
    """A contrast issue found in HTML."""

    element: str  # HTML element description
    foreground: str  # Text color
    background: str  # Background color
    ratio: float  # Calculated ratio
    required_ratio: float  # Required ratio
    wcag_level: str  # "AA" or "AAA"
    suggestion: str  # Fix suggestion


@dataclass
class ContrastReport:
    """Overall contrast validation report."""

    passes: bool  # Overall pass/fail
    wcag_level: str  # "AA" or "AAA"
    color_pairs_checked: int
    issues: list[ContrastIssue] = field(default_factory=list)
    score: float = 100.0  # 0-100 score

    @property
    def issue_count(self) -> int:
        return len(self.issues)


# ═══════════════════════════════════════════════════════════════
# CONTRAST CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#ff0000" or "ff0000")

    Returns:
        Tuple of (R, G, B) values (0-255)
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


def rgb_to_relative_luminance(r: int, g: int, b: int) -> float:
    """
    Calculate relative luminance from RGB values.

    Formula: L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    where R, G, B are linearized (gamma corrected)

    See: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
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


def calculate_contrast_ratio(foreground: str, background: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors.

    Formula: (L1 + 0.05) / (L2 + 0.05)
    where L1 is the lighter color's luminance

    Args:
        foreground: Hex color for foreground (text)
        background: Hex color for background

    Returns:
        Contrast ratio (1:1 to 21:1)
    """
    # Convert colors to hex if they're Tailwind classes
    fg_hex = tailwind_to_hex(foreground)
    bg_hex = tailwind_to_hex(background)

    # Handle transparent
    if fg_hex == "transparent" or bg_hex == "transparent":
        return 1.0  # Can't calculate for transparent

    # Get RGB values
    fg_rgb = hex_to_rgb(fg_hex)
    bg_rgb = hex_to_rgb(bg_hex)

    # Calculate luminance
    fg_lum = rgb_to_relative_luminance(*fg_rgb)
    bg_lum = rgb_to_relative_luminance(*bg_rgb)

    # Ensure L1 is the lighter color
    lighter = max(fg_lum, bg_lum)
    darker = min(fg_lum, bg_lum)

    # Calculate ratio
    ratio = (lighter + 0.05) / (darker + 0.05)

    return round(ratio, 2)


def tailwind_to_hex(color: str) -> str:
    """
    Convert Tailwind color class to hex.

    Args:
        color: Tailwind color (e.g., "blue-500") or hex color

    Returns:
        Hex color string
    """
    # Already a hex color
    if color.startswith("#"):
        return color

    # Handle special values
    if color in ("transparent", "currentColor", "inherit"):
        return color

    # Try direct lookup
    if color in TAILWIND_COLORS:
        return TAILWIND_COLORS[color]

    # Try without prefix (text-, bg-, border-, etc.)
    for prefix in ["text-", "bg-", "border-", "ring-", "from-", "to-", "via-"]:
        if color.startswith(prefix):
            color_name = color[len(prefix):]
            if color_name in TAILWIND_COLORS:
                return TAILWIND_COLORS[color_name]

    # Not found
    return color


def check_contrast(
    foreground: str,
    background: str,
) -> ContrastResult:
    """
    Check contrast ratio and WCAG compliance.

    Args:
        foreground: Foreground (text) color
        background: Background color

    Returns:
        ContrastResult with all compliance levels
    """
    ratio = calculate_contrast_ratio(foreground, background)

    return ContrastResult(
        foreground=foreground,
        background=background,
        ratio=ratio,
        passes_aa_normal=ratio >= 4.5,
        passes_aa_large=ratio >= 3.0,
        passes_aaa_normal=ratio >= 7.0,
        passes_aaa_large=ratio >= 4.5,
    )


# ═══════════════════════════════════════════════════════════════
# HTML CONTRAST ANALYSIS
# ═══════════════════════════════════════════════════════════════

def extract_color_pairs(html: str) -> list[tuple[str, str, str]]:
    """
    Extract text/background color pairs from HTML with Tailwind classes.

    Returns list of (element_description, text_color, bg_color) tuples.
    """
    pairs = []

    # Pattern to find elements with both text and bg colors
    element_pattern = re.compile(
        r'<(\w+)[^>]*class=["\']([^"\']*)["\'][^>]*>',
        re.IGNORECASE
    )

    for match in element_pattern.finditer(html):
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


def check_wcag_compliance(
    html: str,
    level: str = "AA",
) -> ContrastReport:
    """
    Check WCAG contrast compliance for an HTML string.

    Args:
        html: HTML string with Tailwind classes
        level: WCAG level - "AA" or "AAA"

    Returns:
        ContrastReport with all issues found
    """
    issues: list[ContrastIssue] = []
    color_pairs = extract_color_pairs(html)

    required_ratio = 4.5 if level == "AA" else 7.0

    for element_desc, text_color, bg_color in color_pairs:
        result = check_contrast(text_color, bg_color)

        passes = result.passes_aa_normal if level == "AA" else result.passes_aaa_normal

        if not passes:
            # Generate suggestion
            suggestion = _generate_contrast_suggestion(
                text_color, bg_color, required_ratio
            )

            issues.append(ContrastIssue(
                element=element_desc,
                foreground=text_color,
                background=bg_color,
                ratio=result.ratio,
                required_ratio=required_ratio,
                wcag_level=level,
                suggestion=suggestion,
            ))

    # Calculate score
    if color_pairs:
        passing_count = len(color_pairs) - len(issues)
        score = (passing_count / len(color_pairs)) * 100
    else:
        score = 100.0  # No color pairs to check

    return ContrastReport(
        passes=len(issues) == 0,
        wcag_level=level,
        color_pairs_checked=len(color_pairs),
        issues=issues,
        score=round(score, 1),
    )


def _generate_contrast_suggestion(
    text_color: str,
    bg_color: str,
    required_ratio: float,
) -> str:
    """Generate a suggestion for fixing contrast issues."""
    # Check if background is light or dark
    bg_hex = tailwind_to_hex(bg_color)
    if bg_hex not in ("transparent", "currentColor", "inherit"):
        try:
            r, g, b = hex_to_rgb(bg_hex)
            luminance = rgb_to_relative_luminance(r, g, b)

            if luminance > 0.5:
                # Light background - suggest darker text
                return f"Use darker text color (e.g., gray-900, slate-800) or darken background"
            else:
                # Dark background - suggest lighter text
                return f"Use lighter text color (e.g., white, gray-100) or lighten background"
        except ValueError:
            pass

    return f"Adjust colors to achieve {required_ratio}:1 contrast ratio"


def suggest_accessible_pair(
    base_color: str,
    is_background: bool = True,
    level: str = "AA",
) -> list[str]:
    """
    Suggest accessible color pairs for a given color.

    Args:
        base_color: The starting color (Tailwind name or hex)
        is_background: True if base_color is background, False if text
        level: WCAG level - "AA" or "AAA"

    Returns:
        List of Tailwind colors that pass contrast requirements
    """
    required_ratio = 4.5 if level == "AA" else 7.0
    suggestions = []

    base_hex = tailwind_to_hex(base_color)
    if base_hex in ("transparent", "currentColor", "inherit"):
        return []

    # Test against common text/background colors
    test_colors = [
        "white", "black",
        "gray-50", "gray-100", "gray-200", "gray-800", "gray-900",
        "slate-50", "slate-100", "slate-800", "slate-900",
    ]

    for color in test_colors:
        if is_background:
            ratio = calculate_contrast_ratio(color, base_color)
        else:
            ratio = calculate_contrast_ratio(base_color, color)

        if ratio >= required_ratio:
            suggestions.append(color)

    return suggestions


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def validate_contrast(
    foreground: str,
    background: str,
    level: str = "AA",
    text_size: str = "normal",
) -> tuple[bool, float, float, str]:
    """
    Validate contrast and return detailed results.

    Args:
        foreground: Foreground (text) color
        background: Background color
        level: WCAG level - "AA" or "AAA"
        text_size: "normal" or "large"

    Returns:
        Tuple of (passes, ratio, required_ratio, message)
    """
    result = check_contrast(foreground, background)

    # Determine required ratio based on level and size
    if level == "AAA":
        required = 4.5 if text_size == "large" else 7.0
    else:  # AA
        required = 3.0 if text_size == "large" else 4.5

    passes = result.ratio >= required

    if passes:
        message = f"✓ Contrast ratio {result.ratio}:1 meets WCAG {level} ({required}:1 required)"
    else:
        message = f"✗ Contrast ratio {result.ratio}:1 fails WCAG {level} ({required}:1 required)"

    return passes, result.ratio, required, message
