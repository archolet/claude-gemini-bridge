"""
ProfessionalValidator - Corporate/Professional Design Standards Validation

Validates design outputs against professional/enterprise standards:
- Color palette restrictions based on formality level
- Animation appropriateness for corporate contexts
- WCAG contrast requirements (AA/AAA)
- Industry-specific patterns and anti-patterns
- Typography and spacing consistency
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal

# Import from centralized locations
from gemini_mcp.validation.types import ValidationSeverity, ValidationIssue
from gemini_mcp.validation.utils import (
    extract_tailwind_colors,
    extract_color_pairs,
    TAILWIND_COLOR_CLASS_PATTERN,
)
from gemini_mcp.validation.contrast_checker import (
    check_contrast,
    check_wcag_compliance,
)


# =============================================================================
# FORMALITY RULES
# =============================================================================

FORMALITY_RULES: Dict[str, Dict[str, Any]] = {
    "formal": {
        "max_colors": 4,
        "allowed_animations": ["fade", "slide"],
        "min_contrast_ratio": 7.0,  # WCAG AAA
        "prohibited_patterns": [
            "emoji",
            "rounded-full",  # On large containers (not avatars/icons)
            "neon",
            "animate-bounce",
            "animate-spin",
            "animate-ping",
            "bg-gradient.*neon",
        ],
        "required_patterns": [
            "font-serif|font-sans",  # Needs proper font
        ],
        "max_animation_duration": "500ms",
        "button_style": "uppercase|tracking-wider|font-semibold",
        "heading_style": "font-semibold",
        "description": "Enterprise-grade formal design for banks, law firms, hospitals",
    },
    "semi-formal": {
        "max_colors": 5,
        "allowed_animations": ["fade", "slide", "scale"],
        "min_contrast_ratio": 4.5,  # WCAG AA
        "prohibited_patterns": [
            "emoji",
            "neon",
            "animate-bounce",
            "animate-ping",
        ],
        "required_patterns": [],
        "max_animation_duration": "700ms",
        "button_style": "font-medium|font-semibold",
        "heading_style": "font-bold",
        "description": "Professional design for SaaS, consulting, tech companies",
    },
    "approachable": {
        "max_colors": 6,
        "allowed_animations": ["fade", "slide", "scale", "bounce"],
        "min_contrast_ratio": 4.5,  # WCAG AA
        "prohibited_patterns": [],
        "required_patterns": [],
        "max_animation_duration": "1000ms",
        "button_style": "",
        "heading_style": "font-bold|font-extrabold",
        "description": "Friendly professional design for startups and creative agencies",
    },
}


INDUSTRY_PATTERNS: Dict[str, Dict[str, Any]] = {
    "finance": {
        "recommended_colors": ["blue", "slate", "emerald", "gray"],
        "avoid_colors": ["pink", "purple", "orange"],
        "recommended_patterns": ["trust-badge", "security-indicator", "chart"],
        "avoid_patterns": ["playful", "casual", "emoji"],
    },
    "healthcare": {
        "recommended_colors": ["teal", "blue", "green", "white"],
        "avoid_colors": ["red", "orange", "neon"],  # Red can trigger anxiety
        "recommended_patterns": ["accessibility-focus", "calm-design", "clear-typography"],
        "avoid_patterns": ["aggressive", "high-contrast-neon"],
    },
    "legal": {
        "recommended_colors": ["slate", "gray", "blue", "gold"],
        "avoid_colors": ["bright", "neon", "playful"],
        "recommended_patterns": ["serif-headings", "editorial-layout", "formal-spacing"],
        "avoid_patterns": ["casual", "rounded-corners-excessive"],
    },
    "tech": {
        "recommended_colors": ["indigo", "violet", "blue", "slate"],
        "avoid_colors": [],  # Tech is flexible
        "recommended_patterns": ["modern-layout", "gradient-subtle", "dark-mode-support"],
        "avoid_patterns": [],
    },
    "manufacturing": {
        "recommended_colors": ["orange", "gray", "slate", "blue"],
        "avoid_colors": ["pastel", "neon"],
        "recommended_patterns": ["industrial-bold", "clear-hierarchy", "data-display"],
        "avoid_patterns": ["playful", "delicate"],
    },
    "consulting": {
        "recommended_colors": ["blue", "slate", "indigo", "gray"],
        "avoid_colors": ["neon", "bright-pink"],
        "recommended_patterns": ["editorial-layout", "professional-typography", "whitespace"],
        "avoid_patterns": ["crowded", "flashy"],
    },
}


# =============================================================================
# RESULT DATACLASSES
# =============================================================================

@dataclass
class ProfessionalDimensionScore:
    """Score for a single dimension of professional validation."""

    name: str
    score: float  # 0-100
    weight: float  # 0-1
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "weight": self.weight,
            "weighted_score": self.weighted_score,
            "issues": self.issues,
            "recommendations": self.recommendations,
        }


@dataclass
class ProfessionalValidationResult:
    """Complete result of professional validation."""

    is_professional: bool
    overall_score: float  # 0-100
    formality: str
    industry: str
    dimension_scores: Dict[str, ProfessionalDimensionScore] = field(default_factory=dict)
    issues: List[ValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_professional": self.is_professional,
            "overall_score": self.overall_score,
            "formality": self.formality,
            "industry": self.industry,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "dimension_scores": {k: v.to_dict() for k, v in self.dimension_scores.items()},
            "issues": [i.to_dict() for i in self.issues],
            "recommendations": self.recommendations,
        }


# =============================================================================
# PROFESSIONAL VALIDATOR
# =============================================================================

class ProfessionalValidator:
    """
    Validates design outputs against professional/corporate standards.

    This validator ensures that generated designs meet industry-specific
    requirements for professionalism, accessibility, and brand consistency.

    Usage:
        validator = ProfessionalValidator(formality="formal", industry="finance")
        result = validator.validate(html_content, css_content)

        if not result.is_professional:
            print(f"Score: {result.overall_score}/100")
            for issue in result.issues:
                print(f"- {issue.message}")
    """

    # Dimension weights for overall score calculation
    DIMENSION_WEIGHTS = {
        "color_palette": 0.20,       # Appropriate color usage
        "typography": 0.15,          # Professional typography
        "animation": 0.15,           # Animation appropriateness
        "accessibility": 0.25,       # WCAG compliance
        "layout": 0.15,              # Visual hierarchy and spacing
        "industry_fit": 0.10,        # Industry-specific patterns
    }

    def __init__(
        self,
        formality: Literal["formal", "semi-formal", "approachable"] = "semi-formal",
        industry: Literal["finance", "healthcare", "legal", "tech", "manufacturing", "consulting"] = "consulting",
    ):
        """
        Initialize ProfessionalValidator.

        Args:
            formality: Formality level determining strictness of validation
            industry: Industry context for industry-specific patterns
        """
        self.formality = formality
        self.industry = industry
        self.rules = FORMALITY_RULES.get(formality, FORMALITY_RULES["semi-formal"])
        self.industry_patterns = INDUSTRY_PATTERNS.get(industry, INDUSTRY_PATTERNS["consulting"])

    def validate(
        self,
        html: str,
        css: str = "",
        accessibility_level: str = "AA",
    ) -> ProfessionalValidationResult:
        """
        Run full professional validation suite.

        Args:
            html: HTML content to validate
            css: Optional CSS content
            accessibility_level: Target WCAG level (AA or AAA)

        Returns:
            ProfessionalValidationResult with scores, issues, and recommendations
        """
        dimension_scores: Dict[str, ProfessionalDimensionScore] = {}
        all_issues: List[ValidationIssue] = []
        all_recommendations: List[str] = []

        # Run each dimension validation
        dimension_scores["color_palette"] = self._validate_color_palette(html, css)
        dimension_scores["typography"] = self._validate_typography(html, css)
        dimension_scores["animation"] = self._validate_animation(html, css)
        dimension_scores["accessibility"] = self._validate_accessibility(html, css, accessibility_level)
        dimension_scores["layout"] = self._validate_layout(html, css)
        dimension_scores["industry_fit"] = self._validate_industry_fit(html, css)

        # Collect all issues and recommendations
        for dim in dimension_scores.values():
            all_issues.extend([
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=issue,
                )
                for issue in dim.issues
            ])
            all_recommendations.extend(dim.recommendations)

        # Calculate overall score
        overall_score = sum(dim.weighted_score for dim in dimension_scores.values())

        # Determine if design is professional
        # Must score at least 70% overall and no dimension below 50%
        min_dimension_score = min(dim.score for dim in dimension_scores.values())
        is_professional = overall_score >= 70.0 and min_dimension_score >= 50.0

        return ProfessionalValidationResult(
            is_professional=is_professional,
            overall_score=overall_score,
            formality=self.formality,
            industry=self.industry,
            dimension_scores=dimension_scores,
            issues=all_issues,
            recommendations=all_recommendations,
        )

    def _validate_color_palette(self, html: str, css: str) -> ProfessionalDimensionScore:
        """Validate color usage against formality rules."""
        issues = []
        recommendations = []
        score = 100.0

        combined = html + " " + css

        # Check for prohibited patterns
        for pattern in self.rules.get("prohibited_patterns", []):
            if re.search(pattern, combined, re.IGNORECASE):
                issues.append(f"Prohibited pattern found: '{pattern}'")
                score -= 15

        # Count unique colors using shared utility
        colors = extract_tailwind_colors(combined)

        max_colors = self.rules.get("max_colors", 5)
        if len(colors) > max_colors:
            issues.append(f"Too many colors ({len(colors)}) - max {max_colors} for {self.formality} formality")
            score -= 10

        # Check for industry-appropriate colors
        avoid_colors = self.industry_patterns.get("avoid_colors", [])
        for color in avoid_colors:
            if re.search(rf'\b{color}\b', combined, re.IGNORECASE):
                issues.append(f"Color '{color}' not recommended for {self.industry} industry")
                score -= 5

        # Ensure minimum score
        score = max(0, min(100, score))

        return ProfessionalDimensionScore(
            name="Color Palette",
            score=score,
            weight=self.DIMENSION_WEIGHTS["color_palette"],
            issues=issues,
            recommendations=recommendations,
        )

    def _validate_typography(self, html: str, css: str) -> ProfessionalDimensionScore:
        """Validate typography appropriateness."""
        issues = []
        recommendations = []
        score = 100.0

        combined = html + " " + css

        # Check for required heading style
        heading_style = self.rules.get("heading_style", "")
        if heading_style:
            patterns = heading_style.split("|")
            if not any(p in combined for p in patterns):
                issues.append(f"Missing appropriate heading weight for {self.formality}")
                score -= 10

        # Check for font-serif in formal contexts
        if self.formality == "formal":
            if "font-serif" not in combined and "font-sans" not in combined:
                recommendations.append("Consider using font-serif for formal heading typography")

        # Check for excessive text sizes
        huge_text = len(re.findall(r'text-(?:8|9)xl', combined))
        if huge_text > 2:
            issues.append(f"Excessive large text sizes ({huge_text} instances of 8xl/9xl)")
            score -= 10

        # Ensure minimum score
        score = max(0, min(100, score))

        return ProfessionalDimensionScore(
            name="Typography",
            score=score,
            weight=self.DIMENSION_WEIGHTS["typography"],
            issues=issues,
            recommendations=recommendations,
        )

    def _validate_animation(self, html: str, css: str) -> ProfessionalDimensionScore:
        """Validate animation usage for corporate appropriateness."""
        issues = []
        recommendations = []
        score = 100.0

        combined = html + " " + css

        allowed = self.rules.get("allowed_animations", ["fade", "slide", "scale"])

        # Tailwind animation classes
        animation_patterns = {
            "fade": r'animate-(?:fade|pulse)',
            "slide": r'animate-(?:slide|translateX|translateY)',
            "scale": r'animate-(?:scale|grow|shrink)',
            "bounce": r'animate-bounce',
            "spin": r'animate-spin',
            "ping": r'animate-ping',
        }

        for anim_type, pattern in animation_patterns.items():
            if re.search(pattern, combined):
                if anim_type not in allowed:
                    issues.append(f"Animation type '{anim_type}' not appropriate for {self.formality} design")
                    score -= 15

        # Check for transition duration
        max_duration = self.rules.get("max_animation_duration", "700ms")
        max_ms = int(max_duration.replace("ms", ""))

        duration_pattern = r'duration-\[?(\d+)(?:ms)?\]?'
        durations = re.findall(duration_pattern, combined)
        for d in durations:
            if int(d) > max_ms:
                issues.append(f"Animation duration {d}ms exceeds {max_ms}ms limit for {self.formality}")
                score -= 5

        # Ensure minimum score
        score = max(0, min(100, score))

        return ProfessionalDimensionScore(
            name="Animation",
            score=score,
            weight=self.DIMENSION_WEIGHTS["animation"],
            issues=issues,
            recommendations=recommendations,
        )

    def _validate_accessibility(
        self,
        html: str,
        css: str,
        level: str = "AA",
    ) -> ProfessionalDimensionScore:
        """Validate accessibility compliance including WCAG contrast ratios."""
        issues = []
        recommendations = []
        score = 100.0

        combined = html + " " + css

        # ============================================================
        # WCAG COLOR CONTRAST VALIDATION (The actual check!)
        # ============================================================
        min_contrast = self.rules.get("min_contrast_ratio", 4.5)
        wcag_level = "AAA" if min_contrast >= 7.0 else "AA"

        # Use contrast_checker for actual WCAG validation
        contrast_report = check_wcag_compliance(html, level=wcag_level)

        if not contrast_report.passes:
            for issue in contrast_report.issues:
                issues.append(
                    f"WCAG {wcag_level} contrast fail: {issue.foreground} on {issue.background} "
                    f"(ratio: {issue.ratio}:1, required: {issue.required_ratio}:1)"
                )
                score -= 10  # 10 points per contrast failure

            if contrast_report.issues:
                recommendations.append(
                    f"Fix {len(contrast_report.issues)} contrast issues for WCAG {wcag_level} compliance"
                )

        # ============================================================
        # ARIA ATTRIBUTES
        # ============================================================
        if "aria-" not in html:
            issues.append("Missing ARIA attributes for accessibility")
            score -= 10
            recommendations.append("Add aria-label, aria-describedby, or role attributes")

        # ============================================================
        # FOCUS STATES
        # ============================================================
        focus_patterns = ["focus:", "focus-visible:", "focus-within:"]
        has_focus = any(p in combined for p in focus_patterns)
        if not has_focus:
            issues.append("Missing focus state indicators")
            score -= 15
            recommendations.append("Add focus:ring or focus:outline classes for keyboard navigation")

        # ============================================================
        # SCREEN READER SUPPORT
        # ============================================================
        sr_patterns = ["sr-only", "not-sr-only", "aria-hidden"]
        has_sr = any(p in html for p in sr_patterns)
        if not has_sr:
            recommendations.append("Consider adding sr-only content for screen readers")

        # ============================================================
        # FORMAL/AAA LEVEL REQUIREMENTS
        # ============================================================
        if level == "AAA" or self.formality == "formal":
            # Formal mode: stricter contrast requirements
            if contrast_report.score < 100:
                issues.append(
                    f"Formal design requires 100% WCAG {wcag_level} compliance (current: {contrast_report.score}%)"
                )
                score -= 5

            # Check for prefers-reduced-motion support
            if "prefers-reduced-motion" not in combined:
                recommendations.append("Add prefers-reduced-motion support for motion sensitivity")

            # Check for high contrast mode support
            if "contrast-" not in combined:
                recommendations.append("Consider adding high contrast mode support for AAA compliance")

        # Ensure minimum score
        score = max(0, min(100, score))

        return ProfessionalDimensionScore(
            name="Accessibility",
            score=score,
            weight=self.DIMENSION_WEIGHTS["accessibility"],
            issues=issues,
            recommendations=recommendations,
        )

    def _validate_layout(self, html: str, css: str) -> ProfessionalDimensionScore:
        """Validate layout structure and visual hierarchy."""
        issues = []
        recommendations = []
        score = 100.0

        combined = html + " " + css

        # Check for proper container usage
        if "container" not in combined and "max-w-" not in combined:
            issues.append("Missing container or max-width for proper layout")
            score -= 10

        # Check for consistent spacing
        spacing_classes = re.findall(r'(?:p|m|gap)-\d+', combined)
        if len(set(spacing_classes)) > 10:
            issues.append("Inconsistent spacing - too many different spacing values")
            score -= 5

        # Check for responsive design
        responsive_patterns = ["sm:", "md:", "lg:", "xl:"]
        responsive_count = sum(1 for p in responsive_patterns if p in combined)
        if responsive_count < 2:
            issues.append("Limited responsive design implementation")
            score -= 10
            recommendations.append("Add sm:, md:, lg: breakpoint modifiers")

        # Check for grid/flex usage
        if "grid" not in combined and "flex" not in combined:
            recommendations.append("Consider using grid or flex for modern layouts")

        # Ensure minimum score
        score = max(0, min(100, score))

        return ProfessionalDimensionScore(
            name="Layout",
            score=score,
            weight=self.DIMENSION_WEIGHTS["layout"],
            issues=issues,
            recommendations=recommendations,
        )

    def _validate_industry_fit(self, html: str, css: str) -> ProfessionalDimensionScore:
        """Validate industry-specific patterns."""
        issues = []
        recommendations = []
        score = 100.0

        combined = html + " " + css

        # Check for avoided patterns
        avoid_patterns = self.industry_patterns.get("avoid_patterns", [])
        for pattern in avoid_patterns:
            if pattern.lower() in combined.lower():
                issues.append(f"Pattern '{pattern}' not recommended for {self.industry}")
                score -= 10

        # Check for recommended patterns (as recommendations, not penalties)
        recommended = self.industry_patterns.get("recommended_patterns", [])
        for pattern in recommended:
            if pattern.lower() not in combined.lower():
                recommendations.append(f"Consider adding '{pattern}' pattern for {self.industry}")

        # Industry-specific checks
        if self.industry == "finance":
            # Finance should have trust indicators
            if "trust" not in combined.lower() and "secure" not in combined.lower():
                recommendations.append("Consider adding trust/security indicators for finance")

        elif self.industry == "healthcare":
            # Healthcare needs calm, accessible design
            if "calm" not in combined.lower() and "peaceful" not in combined.lower():
                recommendations.append("Healthcare design should convey calm and trust")

        elif self.industry == "legal":
            # Legal should feel authoritative
            if "font-serif" not in combined:
                recommendations.append("Legal industry often benefits from serif typography")

        # Ensure minimum score
        score = max(0, min(100, score))

        return ProfessionalDimensionScore(
            name="Industry Fit",
            score=score,
            weight=self.DIMENSION_WEIGHTS["industry_fit"],
            issues=issues,
            recommendations=recommendations,
        )

    def get_formality_description(self) -> str:
        """Get description of current formality level."""
        return self.rules.get("description", "Professional design standards")

    @staticmethod
    def list_formality_levels() -> List[str]:
        """List all available formality levels."""
        return list(FORMALITY_RULES.keys())

    @staticmethod
    def list_industries() -> List[str]:
        """List all available industries."""
        return list(INDUSTRY_PATTERNS.keys())


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def validate_professional(
    html: str,
    css: str = "",
    formality: str = "semi-formal",
    industry: str = "consulting",
    accessibility_level: str = "AA",
) -> ProfessionalValidationResult:
    """
    Convenience function for professional validation.

    Args:
        html: HTML content
        css: CSS content
        formality: Formality level (formal, semi-formal, approachable)
        industry: Industry context
        accessibility_level: WCAG level (AA or AAA)

    Returns:
        ProfessionalValidationResult
    """
    validator = ProfessionalValidator(
        formality=formality,
        industry=industry,
    )
    return validator.validate(html, css, accessibility_level)


def get_formality_rules(formality: str) -> Dict[str, Any]:
    """Get the rules for a specific formality level."""
    return FORMALITY_RULES.get(formality, FORMALITY_RULES["semi-formal"])


def get_industry_patterns(industry: str) -> Dict[str, Any]:
    """Get the patterns for a specific industry."""
    return INDUSTRY_PATTERNS.get(industry, INDUSTRY_PATTERNS["consulting"])
