"""
MAESTRO Context Analyzer - Phase 3

Analyzes existing HTML to extract design tokens for style matching.
Uses regex-based Tailwind class extraction for fast, dependency-free parsing.

When user provides previous_html:
- Extract Tailwind classes
- Detect color palette
- Identify typography patterns
- Recognize spacing conventions
- Detect component types
- Infer theme from patterns
"""

from __future__ import annotations

import logging
import re
from typing import Any

from gemini_mcp.maestro.decision.models import ContextAnalysis

logger = logging.getLogger(__name__)


class ContextAnalyzer:
    """
    Analyzes existing HTML to extract design tokens.

    Used when user provides previous_html for refinement or style matching.
    Enables visual consistency between new designs and existing context.

    Usage:
        analyzer = ContextAnalyzer()
        result = analyzer.analyze(html_string)
        # result.detected_theme, result.tailwind_classes, etc.
    """

    # =========================================================================
    # TAILWIND PATTERN DEFINITIONS
    # =========================================================================

    # Color class patterns by role
    COLOR_PATTERNS: dict[str, str] = {
        # Primary colors (blue/indigo family)
        "primary": r"(?:bg|text|border|ring)-(?:blue|indigo|violet|purple)-\d{2,3}",
        # Secondary/neutral colors
        "secondary": r"(?:bg|text|border)-(?:gray|slate|zinc|neutral|stone)-\d{2,3}",
        # Accent colors
        "accent": r"(?:bg|text|border)-(?:emerald|green|teal|cyan|sky)-\d{2,3}",
        # Danger/error colors
        "danger": r"(?:bg|text|border)-(?:red|rose|pink)-\d{2,3}",
        # Warning colors
        "warning": r"(?:bg|text|border)-(?:amber|yellow|orange)-\d{2,3}",
        # Success colors
        "success": r"(?:bg|text|border)-(?:green|emerald|lime)-\d{2,3}",
    }

    # Typography patterns
    TYPOGRAPHY_PATTERNS: dict[str, str] = {
        "text_size": r"text-(?:xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)",
        "font_weight": r"font-(?:thin|extralight|light|normal|medium|semibold|bold|extrabold|black)",
        "font_family": r"font-(?:sans|serif|mono)",
        "line_height": r"leading-(?:none|tight|snug|normal|relaxed|loose|\d+)",
        "letter_spacing": r"tracking-(?:tighter|tight|normal|wide|wider|widest)",
    }

    # Spacing patterns
    SPACING_PATTERNS: dict[str, str] = {
        "padding": r"p[xytblr]?-(?:\d+|px|auto|\[\d+(?:px|rem|em)?\])",
        "margin": r"m[xytblr]?-(?:\d+|px|auto|\[\d+(?:px|rem|em)?\])",
        "gap": r"gap-(?:x-|y-)?\d+",
        "space": r"space-(?:x|y)-\d+",
    }

    # Border/radius patterns
    BORDER_PATTERNS: dict[str, str] = {
        "radius": r"rounded(?:-(?:none|sm|md|lg|xl|2xl|3xl|full))?",
        "border_width": r"border(?:-(?:0|2|4|8))?",
        "border_style": r"border-(?:solid|dashed|dotted|double|none)",
    }

    # Shadow patterns
    SHADOW_PATTERNS: dict[str, str] = {
        "shadow": r"shadow(?:-(?:sm|md|lg|xl|2xl|inner|none))?",
        "drop_shadow": r"drop-shadow(?:-(?:sm|md|lg|xl|2xl|none))?",
    }

    # Component detection patterns (HTML structure)
    COMPONENT_PATTERNS: dict[str, str] = {
        "navbar": r"<nav[^>]*>|role=[\"']navigation[\"']",
        "hero": r"class=[\"'][^\"']*(?:hero|min-h-screen|h-screen)[^\"']*[\"']",
        "card": r"class=[\"'][^\"']*(?:rounded|shadow)[^\"']*(?:p-\d|px-\d)[^\"']*[\"']",
        "button": r"<button[^>]*>|role=[\"']button[\"']",
        "form": r"<form[^>]*>|<input[^>]*>|<textarea[^>]*>",
        "footer": r"<footer[^>]*>|role=[\"']contentinfo[\"']",
        "sidebar": r"class=[\"'][^\"']*(?:sidebar|w-64|w-72|w-80)[^\"']*[\"']",
        "modal": r"class=[\"'][^\"']*(?:modal|fixed[^\"']*inset|z-50)[^\"']*[\"']",
        "table": r"<table[^>]*>|role=[\"']table[\"']|<thead[^>]*>",
        "accordion": r"class=[\"'][^\"']*accordion[^\"']*[\"']|data-accordion",
        "tabs": r"role=[\"']tablist[\"']|class=[\"'][^\"']*tabs[^\"']*[\"']",
        "carousel": r"class=[\"'][^\"']*(?:carousel|swiper|slider)[^\"']*[\"']",
    }

    # Section marker pattern
    SECTION_MARKER_PATTERN = r"<!--\s*SECTION:\s*(\w+)\s*-->"

    # Theme inference patterns
    THEME_INDICATORS: dict[str, list[str]] = {
        "glassmorphism": ["backdrop-blur", "bg-opacity", "backdrop-filter"],
        "dark_mode_first": ["dark:bg-", "dark:text-", "bg-gray-900", "bg-slate-900"],
        "brutalist": ["border-black", "border-4", "border-8", "shadow-brutal"],
        "neo-brutalism": ["shadow-[", "border-black", "rounded-none"],
        "gradient": ["bg-gradient-", "from-", "via-", "to-"],
        "high_contrast": ["text-black", "bg-white", "text-white", "bg-black"],
        "soft-ui": ["shadow-inner", "bg-gray-100", "bg-gray-50"],
        "cyberpunk": ["neon", "glow", "text-cyan", "text-fuchsia", "bg-black"],
        "pastel": ["bg-pink-", "bg-rose-", "bg-sky-", "bg-violet-"],
        "nature": ["bg-green-", "bg-emerald-", "bg-lime-", "text-green-"],
        "corporate": ["bg-blue-", "text-blue-", "border-blue-"],
    }

    def __init__(self) -> None:
        """Initialize the ContextAnalyzer."""
        # Compile regex patterns for performance
        self._compiled_class_pattern = re.compile(r'class=["\']([^"\']*)["\']')
        self._compiled_section_pattern = re.compile(self.SECTION_MARKER_PATTERN)

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(self, html: str | None) -> ContextAnalysis:
        """
        Analyze HTML and extract design tokens.

        Args:
            html: HTML string to analyze (can be None)

        Returns:
            ContextAnalysis with extracted tokens
        """
        if not html or not html.strip():
            logger.debug("[ContextAnalyzer] No HTML provided")
            return ContextAnalysis(has_html=False)

        logger.info(f"[ContextAnalyzer] Analyzing HTML ({len(html)} chars)")

        result = ContextAnalysis(has_html=True)

        try:
            # Extract all Tailwind classes
            result.tailwind_classes = self._extract_tailwind_classes(html)
            logger.debug(f"[ContextAnalyzer] Found {len(result.tailwind_classes)} classes")

            # Detect colors by role
            result.detected_colors = self._detect_colors(result.tailwind_classes)

            # Detect typography patterns
            result.detected_typography = self._detect_typography(result.tailwind_classes)

            # Detect spacing patterns
            result.detected_spacing = self._detect_spacing(result.tailwind_classes)

            # Detect component types
            result.detected_components = self._detect_components(html)

            # Detect section markers
            result.section_markers = self._detect_section_markers(html)

            # Infer theme from patterns
            result.detected_theme = self._infer_theme(result)

            # Build design tokens
            result.design_tokens = self._build_design_tokens(result)

            logger.info(
                f"[ContextAnalyzer] Analysis complete: "
                f"theme={result.detected_theme}, "
                f"components={result.detected_components}"
            )

        except Exception as e:
            logger.error(f"[ContextAnalyzer] Analysis error: {e}")
            # Return partial results on error
            result.detected_theme = "modern-minimal"

        return result

    def extract_design_dna(self, html: str) -> dict[str, Any]:
        """
        Extract design DNA from HTML for style matching.

        Simpler interface that returns just the design tokens.

        Args:
            html: HTML string to analyze

        Returns:
            Design tokens dictionary
        """
        analysis = self.analyze(html)
        return analysis.to_design_tokens()

    # =========================================================================
    # EXTRACTION METHODS
    # =========================================================================

    def _extract_tailwind_classes(self, html: str) -> list[str]:
        """
        Extract all unique Tailwind CSS classes from HTML.

        Args:
            html: HTML string

        Returns:
            Sorted list of unique class names
        """
        matches = self._compiled_class_pattern.findall(html)

        classes = set()
        for match in matches:
            for cls in match.split():
                # Filter out non-Tailwind classes (rough heuristic)
                if cls and not cls.startswith("js-") and not cls.startswith("_"):
                    classes.add(cls)

        return sorted(classes)

    def _detect_colors(self, classes: list[str]) -> dict[str, str]:
        """
        Detect color palette from Tailwind classes.

        Args:
            classes: List of Tailwind classes

        Returns:
            Dict of color role → first matching class
        """
        colors: dict[str, str] = {}

        for role, pattern in self.COLOR_PATTERNS.items():
            compiled = re.compile(pattern)
            for cls in classes:
                if compiled.match(cls):
                    colors[role] = cls
                    break  # Take first match for each role

        return colors

    def _detect_typography(self, classes: list[str]) -> dict[str, list[str]]:
        """
        Detect typography settings from classes.

        Args:
            classes: List of Tailwind classes

        Returns:
            Dict of typography category → list of matching classes
        """
        typography: dict[str, list[str]] = {}

        for category, pattern in self.TYPOGRAPHY_PATTERNS.items():
            compiled = re.compile(pattern)
            matches = [cls for cls in classes if compiled.match(cls)]
            if matches:
                typography[category] = list(set(matches))

        return typography

    def _detect_spacing(self, classes: list[str]) -> dict[str, list[str]]:
        """
        Detect spacing patterns from classes.

        Args:
            classes: List of Tailwind classes

        Returns:
            Dict of spacing category → list of matching classes
        """
        spacing: dict[str, list[str]] = {}

        for category, pattern in self.SPACING_PATTERNS.items():
            compiled = re.compile(pattern)
            matches = [cls for cls in classes if compiled.match(cls)]
            if matches:
                spacing[category] = list(set(matches))

        return spacing

    def _detect_components(self, html: str) -> list[str]:
        """
        Detect component types present in HTML.

        Args:
            html: HTML string

        Returns:
            List of detected component types
        """
        components: list[str] = []

        for comp_type, pattern in self.COMPONENT_PATTERNS.items():
            if re.search(pattern, html, re.IGNORECASE):
                components.append(comp_type)

        return components

    def _detect_section_markers(self, html: str) -> list[str]:
        """
        Detect section markers in HTML.

        Section markers follow the pattern: <!-- SECTION: {type} -->

        Args:
            html: HTML string

        Returns:
            List of section types found
        """
        return self._compiled_section_pattern.findall(html)

    # =========================================================================
    # THEME INFERENCE
    # =========================================================================

    def _infer_theme(self, analysis: ContextAnalysis) -> str:
        """
        Infer theme based on detected patterns.

        Uses a scoring system to find the best matching theme.

        Args:
            analysis: ContextAnalysis with extracted classes

        Returns:
            Theme name string
        """
        classes_str = " ".join(analysis.tailwind_classes)
        scores: dict[str, int] = {}

        for theme, indicators in self.THEME_INDICATORS.items():
            score = sum(1 for indicator in indicators if indicator in classes_str)
            if score > 0:
                scores[theme] = score

        if not scores:
            return "modern-minimal"

        # Return theme with highest score
        best_theme = max(scores, key=lambda k: scores[k])
        logger.debug(f"[ContextAnalyzer] Theme scores: {scores}, selected: {best_theme}")

        return best_theme

    # =========================================================================
    # TOKEN BUILDING
    # =========================================================================

    def _build_design_tokens(self, analysis: ContextAnalysis) -> dict[str, Any]:
        """
        Build aggregated design tokens from analysis.

        Args:
            analysis: ContextAnalysis with extracted data

        Returns:
            Design tokens dictionary for design tools
        """
        tokens: dict[str, Any] = {
            "theme": analysis.detected_theme,
            "colors": analysis.detected_colors,
            "typography": analysis.detected_typography,
            "spacing": analysis.detected_spacing,
        }

        # Add border/radius info
        border_info = self._extract_border_info(analysis.tailwind_classes)
        if border_info:
            tokens["borders"] = border_info

        # Add shadow info
        shadow_info = self._extract_shadow_info(analysis.tailwind_classes)
        if shadow_info:
            tokens["shadows"] = shadow_info

        # Add dark mode info
        dark_mode_classes = [c for c in analysis.tailwind_classes if c.startswith("dark:")]
        tokens["has_dark_mode"] = len(dark_mode_classes) > 0

        return tokens

    def _extract_border_info(self, classes: list[str]) -> dict[str, list[str]]:
        """Extract border-related classes."""
        border_info: dict[str, list[str]] = {}

        for category, pattern in self.BORDER_PATTERNS.items():
            compiled = re.compile(pattern)
            matches = [cls for cls in classes if compiled.match(cls)]
            if matches:
                border_info[category] = list(set(matches))

        return border_info

    def _extract_shadow_info(self, classes: list[str]) -> dict[str, list[str]]:
        """Extract shadow-related classes."""
        shadow_info: dict[str, list[str]] = {}

        for category, pattern in self.SHADOW_PATTERNS.items():
            compiled = re.compile(pattern)
            matches = [cls for cls in classes if compiled.match(cls)]
            if matches:
                shadow_info[category] = list(set(matches))

        return shadow_info
