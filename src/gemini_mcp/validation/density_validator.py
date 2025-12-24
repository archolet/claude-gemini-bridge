"""
Density Validator - Anti-Laziness Enforcement for Tailwind CSS

This validator ensures that generated HTML meets the density requirements:
- Minimum 6-8 Tailwind classes per interactive element
- 4-layer background rule for rich visual depth
- Proper responsive and state classes

The goal is to prevent "lazy" outputs with minimal styling.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ElementDensity:
    """Density analysis for a single element."""

    element_type: str  # button, a, input, etc.
    class_count: int
    classes: list[str]
    has_responsive: bool  # sm:, md:, lg: classes
    has_hover_state: bool  # hover: classes
    has_focus_state: bool  # focus: classes
    has_dark_mode: bool  # dark: classes
    meets_target: bool
    recommendations: list[str] = field(default_factory=list)


@dataclass
class DensityValidationResult:
    """Overall density validation result."""

    is_valid: bool
    overall_density: float  # Average classes per element
    elements_analyzed: int
    elements_below_minimum: int
    elements_below_target: int
    element_details: list[ElementDensity] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    score: float = 0.0  # 0-100 score

    @property
    def meets_minimum(self) -> bool:
        """Check if minimum density (6 classes) is met."""
        return self.elements_below_minimum == 0

    @property
    def meets_target(self) -> bool:
        """Check if target density (8-10 classes) is met."""
        return self.elements_below_target == 0


class DensityValidator:
    """
    Validates Tailwind CSS class density for anti-laziness enforcement.

    Anti-Laziness Protocol:
    - MINIMUM: 6 classes per interactive element (warning if below)
    - TARGET: 8-10 classes per interactive element (ideal)
    - PREMIUM: 12+ classes per interactive element (enterprise quality)

    4-Layer Background Rule:
    1. Base background color
    2. Gradient or pattern overlay
    3. Texture or noise layer
    4. Interactive state layer (hover/focus)
    """

    # Class count thresholds
    MINIMUM_CLASSES = 6  # Below this triggers warning
    TARGET_CLASSES = 8  # Ideal minimum
    PREMIUM_CLASSES = 12  # Enterprise quality

    # Interactive elements that need high density
    INTERACTIVE_ELEMENTS = {
        "button",
        "a",
        "input",
        "select",
        "textarea",
        "label",
    }

    # Container elements that should have styling
    CONTAINER_ELEMENTS = {
        "div",
        "section",
        "article",
        "header",
        "footer",
        "nav",
        "aside",
        "main",
    }

    # Regex patterns
    ELEMENT_PATTERN = re.compile(
        r'<(button|a|input|select|textarea|label|div|section|article|header|footer|nav|aside|main)'
        r'[^>]*class=["\']([^"\']*)["\']',
        re.IGNORECASE,
    )

    CLASS_SPLIT_PATTERN = re.compile(r'\s+')

    def __init__(
        self,
        minimum_classes: int = 6,
        target_classes: int = 8,
        strict_mode: bool = False,
    ):
        """
        Initialize the density validator.

        Args:
            minimum_classes: Minimum class count before warning
            target_classes: Target class count for quality
            strict_mode: If True, is_valid=False when below minimum
        """
        self.minimum_classes = minimum_classes
        self.target_classes = target_classes
        self.strict_mode = strict_mode

    def validate(self, html: str) -> DensityValidationResult:
        """
        Validate HTML class density.

        Args:
            html: HTML content to validate

        Returns:
            DensityValidationResult with analysis and recommendations
        """
        element_details = []
        total_classes = 0
        elements_below_minimum = 0
        elements_below_target = 0

        # Find all elements with class attributes
        for match in self.ELEMENT_PATTERN.finditer(html):
            element_type = match.group(1).lower()
            class_string = match.group(2)
            classes = self._parse_classes(class_string)

            # Only analyze interactive elements strictly
            is_interactive = element_type in self.INTERACTIVE_ELEMENTS
            threshold = self.target_classes if is_interactive else self.minimum_classes

            # Analyze element
            density = self._analyze_element(element_type, classes, threshold)
            element_details.append(density)
            total_classes += density.class_count

            # Count violations
            if is_interactive:
                if density.class_count < self.minimum_classes:
                    elements_below_minimum += 1
                if density.class_count < self.target_classes:
                    elements_below_target += 1

        # Calculate overall density
        elements_analyzed = len(element_details)
        overall_density = (
            total_classes / elements_analyzed if elements_analyzed > 0 else 0.0
        )

        # Build recommendations
        recommendations = self._build_recommendations(element_details)

        # Calculate score (0-100)
        score = self._calculate_score(
            overall_density, elements_below_minimum, elements_below_target, elements_analyzed
        )

        # Determine validity
        is_valid = True
        if self.strict_mode and elements_below_minimum > 0:
            is_valid = False

        return DensityValidationResult(
            is_valid=is_valid,
            overall_density=overall_density,
            elements_analyzed=elements_analyzed,
            elements_below_minimum=elements_below_minimum,
            elements_below_target=elements_below_target,
            element_details=element_details,
            recommendations=recommendations,
            score=score,
        )

    def _parse_classes(self, class_string: str) -> list[str]:
        """Parse class string into list of individual classes."""
        if not class_string:
            return []
        return [c.strip() for c in self.CLASS_SPLIT_PATTERN.split(class_string) if c.strip()]

    def _analyze_element(
        self,
        element_type: str,
        classes: list[str],
        threshold: int,
    ) -> ElementDensity:
        """Analyze density for a single element."""
        class_count = len(classes)

        # Check for responsive classes
        has_responsive = any(
            c.startswith(("sm:", "md:", "lg:", "xl:", "2xl:")) for c in classes
        )

        # Check for state classes
        has_hover = any(c.startswith("hover:") for c in classes)
        has_focus = any(c.startswith(("focus:", "focus-visible:", "focus-within:")) for c in classes)
        has_dark = any(c.startswith("dark:") for c in classes)

        # Check if meets target
        meets_target = class_count >= threshold

        # Build recommendations
        recommendations = []
        if class_count < self.minimum_classes:
            recommendations.append(
                f"Add {self.minimum_classes - class_count} more classes (minimum: {self.minimum_classes})"
            )
        elif class_count < self.target_classes:
            recommendations.append(
                f"Add {self.target_classes - class_count} more classes for optimal density"
            )

        if not has_responsive and element_type in self.INTERACTIVE_ELEMENTS:
            recommendations.append("Add responsive classes (sm:, md:, lg:)")
        if not has_hover and element_type in self.INTERACTIVE_ELEMENTS:
            recommendations.append("Add hover: state classes")
        if not has_focus and element_type in {"button", "input", "a"}:
            recommendations.append("Add focus: state classes for accessibility")
        if not has_dark:
            recommendations.append("Consider adding dark: mode classes")

        return ElementDensity(
            element_type=element_type,
            class_count=class_count,
            classes=classes,
            has_responsive=has_responsive,
            has_hover_state=has_hover,
            has_focus_state=has_focus,
            has_dark_mode=has_dark,
            meets_target=meets_target,
            recommendations=recommendations,
        )

    def _build_recommendations(
        self,
        element_details: list[ElementDensity],
    ) -> list[str]:
        """Build overall recommendations from element analysis."""
        recommendations = []

        # Count elements needing improvement
        low_density = [e for e in element_details if e.class_count < self.minimum_classes]
        missing_hover = [
            e for e in element_details
            if not e.has_hover_state and e.element_type in self.INTERACTIVE_ELEMENTS
        ]
        missing_focus = [
            e for e in element_details
            if not e.has_focus_state and e.element_type in {"button", "input", "a"}
        ]
        missing_responsive = [
            e for e in element_details
            if not e.has_responsive and e.element_type in self.INTERACTIVE_ELEMENTS
        ]

        if low_density:
            recommendations.append(
                f"{len(low_density)} elements have too few classes. "
                f"Add bg, text, padding, border, shadow, transition classes."
            )

        if missing_hover:
            recommendations.append(
                f"{len(missing_hover)} interactive elements missing hover: states. "
                f"Add hover:scale-105, hover:bg-*, hover:shadow-* classes."
            )

        if missing_focus:
            recommendations.append(
                f"{len(missing_focus)} focusable elements missing focus: states. "
                f"Add focus:ring-2, focus:outline-none, focus-visible:ring-* classes."
            )

        if missing_responsive:
            recommendations.append(
                f"{len(missing_responsive)} interactive elements missing responsive classes. "
                f"Add sm:px-6, md:text-lg, lg:py-4 for responsive behavior."
            )

        # 4-Layer Background Rule check
        bg_layers = self._check_background_layers(element_details)
        if bg_layers < 2:
            recommendations.append(
                "Consider 4-layer backgrounds: base color + gradient + texture + hover state"
            )

        return recommendations

    def _check_background_layers(self, element_details: list[ElementDensity]) -> int:
        """Check average background layer count."""
        layer_counts = []

        for element in element_details:
            layers = 0
            classes = element.classes

            # Layer 1: Base background
            if any(c.startswith("bg-") and not c.startswith("bg-gradient") for c in classes):
                layers += 1

            # Layer 2: Gradient
            if any(c.startswith(("bg-gradient", "from-", "to-", "via-")) for c in classes):
                layers += 1

            # Layer 3: Pattern/texture (via backdrop, opacity, etc.)
            if any(c.startswith(("backdrop-", "opacity-", "mix-blend-")) for c in classes):
                layers += 1

            # Layer 4: Hover state
            if any(c.startswith("hover:bg-") for c in classes):
                layers += 1

            layer_counts.append(layers)

        return sum(layer_counts) // len(layer_counts) if layer_counts else 0

    def _calculate_score(
        self,
        overall_density: float,
        below_minimum: int,
        below_target: int,
        total_elements: int,
    ) -> float:
        """Calculate a 0-100 quality score."""
        if total_elements == 0:
            return 100.0

        # Base score from density (max 50 points)
        density_score = min(50.0, (overall_density / self.target_classes) * 50)

        # Penalty for below-minimum elements (up to -30 points)
        minimum_penalty = (below_minimum / total_elements) * 30

        # Penalty for below-target elements (up to -20 points)
        target_penalty = (below_target / total_elements) * 20

        score = max(0.0, 100 - (50 - density_score) - minimum_penalty - target_penalty)
        return round(score, 1)

    def get_correction_feedback(self, result: DensityValidationResult) -> str:
        """
        Generate correction feedback for agents.

        Returns a string that can be passed to context.correction_feedback
        for retry attempts.
        """
        if result.meets_target:
            return ""

        lines = ["## DENSITY IMPROVEMENT REQUIRED\n"]
        lines.append(
            f"Current density: {result.overall_density:.1f} classes/element "
            f"(target: {self.target_classes}+)\n"
        )
        lines.append(f"Score: {result.score}/100\n\n")

        lines.append("### Elements Needing Improvement:\n")
        for element in result.element_details:
            if not element.meets_target:
                lines.append(
                    f"- <{element.element_type}>: {element.class_count} classes "
                    f"(needs {self.target_classes - element.class_count} more)\n"
                )
                for rec in element.recommendations[:2]:  # Limit to top 2
                    lines.append(f"  - {rec}\n")

        lines.append("\n### Add These Class Types:\n")
        lines.append("- Padding: px-4 py-2 px-6 py-3\n")
        lines.append("- Text: text-sm font-medium tracking-wide\n")
        lines.append("- Colors: bg-* text-* border-*\n")
        lines.append("- Effects: shadow-md rounded-lg\n")
        lines.append("- Transitions: transition-all duration-300 ease-out\n")
        lines.append("- States: hover:* focus:* active:*\n")
        lines.append("- Responsive: sm:* md:* lg:*\n")
        lines.append("- Dark mode: dark:*\n")

        return "".join(lines)


# Convenience function
def validate_density(html: str, strict: bool = False) -> DensityValidationResult:
    """
    Validate HTML density with default settings.

    Args:
        html: HTML content to validate
        strict: If True, fail validation when below minimum

    Returns:
        DensityValidationResult
    """
    validator = DensityValidator(strict_mode=strict)
    return validator.validate(html)
