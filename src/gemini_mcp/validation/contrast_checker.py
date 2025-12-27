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

from dataclasses import dataclass, field

# Import shared utilities from central location
from gemini_mcp.validation.utils import (
    hex_to_rgb,
    relative_luminance,
    tailwind_to_hex,
    extract_color_pairs,
)

# Re-export for backward compatibility
from gemini_mcp.constants.colors import TAILWIND_COLOR_MAP as TAILWIND_COLORS

# Backward compatibility alias
rgb_to_relative_luminance = relative_luminance


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

def calculate_contrast_ratio(foreground: str, background: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors.

    Formula: (L1 + 0.05) / (L2 + 0.05)
    where L1 is the lighter color's luminance

    Args:
        foreground: Hex color for foreground (text) or Tailwind class
        background: Hex color for background or Tailwind class

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
    fg_lum = relative_luminance(*fg_rgb)
    bg_lum = relative_luminance(*bg_rgb)

    # Ensure L1 is the lighter color
    lighter = max(fg_lum, bg_lum)
    darker = min(fg_lum, bg_lum)

    # Calculate ratio
    ratio = (lighter + 0.05) / (darker + 0.05)

    return round(ratio, 2)


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
            luminance = relative_luminance(r, g, b)

            if luminance > 0.5:
                # Light background - suggest darker text
                return "Use darker text color (e.g., gray-900, slate-800) or darken background"
            else:
                # Dark background - suggest lighter text
                return "Use lighter text color (e.g., white, gray-100) or lighten background"
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


# ═══════════════════════════════════════════════════════════════
# WCAG 2.1 UI COMPONENT & FOCUS VALIDATION
# ═══════════════════════════════════════════════════════════════

def check_ui_component_contrast(
    foreground: str,
    background: str,
) -> tuple[bool, float, str]:
    """
    Check WCAG 2.1 UI component contrast (3:1 minimum).

    WCAG 2.1 Success Criterion 1.4.11 requires that UI components
    (buttons, form controls, icons, focus indicators) have at least
    3:1 contrast ratio against adjacent colors.

    Args:
        foreground: UI component color (button border, icon, etc.)
        background: Adjacent background color

    Returns:
        Tuple of (passes, ratio, message)

    Example:
        >>> check_ui_component_contrast("blue-600", "white")
        (True, 4.68, "✓ UI component contrast 4.68:1 meets WCAG 2.1 (3:1 required)")
    """
    ratio = calculate_contrast_ratio(foreground, background)
    required = 3.0
    passes = ratio >= required

    if passes:
        message = f"✓ UI component contrast {ratio}:1 meets WCAG 2.1 ({required}:1 required)"
    else:
        message = f"✗ UI component contrast {ratio}:1 fails WCAG 2.1 ({required}:1 required)"

    return passes, ratio, message


def check_focus_indicator(
    focus_color: str,
    background: str,
) -> tuple[bool, float, str]:
    """
    Check WCAG 2.1 focus indicator contrast (3:1 minimum).

    WCAG 2.1 Success Criterion 2.4.7 & 1.4.11 require that focus
    indicators have at least 3:1 contrast ratio against the
    background they appear on.

    For enterprise data tables, this is critical for keyboard
    navigation visibility.

    Args:
        focus_color: Focus indicator color (ring, outline)
        background: Background color where focus appears

    Returns:
        Tuple of (passes, ratio, message)

    Example:
        >>> check_focus_indicator("blue-500", "white")
        (True, 4.52, "✓ Focus indicator contrast 4.52:1 meets WCAG 2.1 (3:1 required)")

        >>> check_focus_indicator("blue-300", "slate-100")
        (False, 2.1, "✗ Focus indicator contrast 2.1:1 fails WCAG 2.1 (3:1 required)")
    """
    ratio = calculate_contrast_ratio(focus_color, background)
    required = 3.0
    passes = ratio >= required

    if passes:
        message = f"✓ Focus indicator contrast {ratio}:1 meets WCAG 2.1 ({required}:1 required)"
    else:
        message = f"✗ Focus indicator contrast {ratio}:1 fails WCAG 2.1 ({required}:1 required)"

    return passes, ratio, message


def suggest_focus_color(
    background: str,
) -> list[str]:
    """
    Suggest accessible focus indicator colors for a given background.

    Args:
        background: Background color where focus will appear

    Returns:
        List of Tailwind colors that pass 3:1 focus indicator requirement

    Example:
        >>> suggest_focus_color("white")
        ["blue-600", "blue-700", "slate-700", "slate-800", "black"]
    """
    required_ratio = 3.0
    suggestions = []

    # Common focus colors (enterprise palette)
    focus_candidates = [
        "blue-500", "blue-600", "blue-700",
        "slate-600", "slate-700", "slate-800",
        "black",
    ]

    for color in focus_candidates:
        ratio = calculate_contrast_ratio(color, background)
        if ratio >= required_ratio:
            suggestions.append(color)

    return suggestions


@dataclass
class UIContrastReport:
    """Report for UI component and focus indicator contrast checks."""

    ui_component_checks: list[tuple[str, str, bool, float]] = field(default_factory=list)
    focus_indicator_checks: list[tuple[str, str, bool, float]] = field(default_factory=list)
    all_pass: bool = True
    total_checks: int = 0
    failed_checks: int = 0

    def add_ui_check(
        self,
        component: str,
        foreground: str,
        background: str,
    ) -> None:
        """Add a UI component contrast check."""
        passes, ratio, _ = check_ui_component_contrast(foreground, background)
        self.ui_component_checks.append((component, f"{foreground}/{background}", passes, ratio))
        self.total_checks += 1
        if not passes:
            self.failed_checks += 1
            self.all_pass = False

    def add_focus_check(
        self,
        element: str,
        focus_color: str,
        background: str,
    ) -> None:
        """Add a focus indicator contrast check."""
        passes, ratio, _ = check_focus_indicator(focus_color, background)
        self.focus_indicator_checks.append((element, f"{focus_color}/{background}", passes, ratio))
        self.total_checks += 1
        if not passes:
            self.failed_checks += 1
            self.all_pass = False

    @property
    def score(self) -> float:
        """Calculate pass percentage."""
        if self.total_checks == 0:
            return 100.0
        return round(((self.total_checks - self.failed_checks) / self.total_checks) * 100, 1)
