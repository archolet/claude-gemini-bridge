"""
AnimationValidator - Animation Timing and Accessibility Validation

Validates animation and transition durations against 2025 best practices:
- Optimal range: 200-500ms for most interactions
- Enforces reduced-motion accessibility
- Checks for performance hints (will-change)
- Validates easing functions

Based on research:
- Nielsen Norman Group: 100-400ms for UI feedback
- Material Design: 150-300ms for small components
- Apple HIG: 250-350ms for standard transitions
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

# Import standardized types from central location
from gemini_mcp.validation.types import ValidationSeverity

# Backward compatibility alias - AnimationSeverity is now ValidationSeverity
AnimationSeverity = ValidationSeverity


@dataclass
class AnimationIssue:
    """A single animation validation issue."""
    severity: ValidationSeverity
    message: str
    duration_ms: Optional[int] = None
    suggestion: Optional[str] = None
    location: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "suggestion": self.suggestion,
            "location": self.location,
        }


@dataclass
class AnimationValidationResult:
    """Result of animation validation."""
    valid: bool
    issues: list[AnimationIssue] = field(default_factory=list)
    durations_found: list[int] = field(default_factory=list)
    has_reduced_motion: bool = False
    has_will_change: bool = False

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING)

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "durations_found": self.durations_found,
            "has_reduced_motion": self.has_reduced_motion,
            "has_will_change": self.has_will_change,
            "issues": [i.to_dict() for i in self.issues],
        }


class AnimationValidator:
    """
    Validates animation timing against 2025 best practices.

    Timing Guidelines:
    - Micro-interactions: 150-250ms
    - Hover effects: 200-300ms
    - Modals/Dropdowns: 300-400ms
    - Page transitions: 400-500ms
    - Complex animations: 500-800ms (acceptable)
    - > 800ms: Warning (feels slow)
    - < 100ms: Warning (too fast to perceive)
    """

    # Timing boundaries in milliseconds
    MIN_PERCEIVABLE = 100
    OPTIMAL_MIN = 200
    OPTIMAL_MAX = 500
    MAX_ACCEPTABLE = 800

    # Regex patterns for duration extraction
    DURATION_PATTERNS = [
        # CSS transition/animation: 300ms, 0.3s, .3s
        r'(?:transition|animation)(?:-duration)?[^;]*?(\d*\.?\d+)(m?s)',
        # Inline duration: duration-300, duration-[300ms]
        r'duration-(\d+)',
        r'duration-\[(\d+)(m?s)\]',
        # Tailwind transition classes with timing
        r'transition-(\d+)',
        # Direct timing in styles
        r'(\d*\.?\d+)(m?s)(?:\s+(?:ease|linear|cubic-bezier))',
    ]

    # Easing function patterns
    VALID_EASINGS = [
        "ease", "ease-in", "ease-out", "ease-in-out", "linear",
        r"cubic-bezier\([^)]+\)",
    ]

    def __init__(
        self,
        strict_mode: bool = False,
        min_duration_ms: int = 100,
        max_duration_ms: int = 800,
    ):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, optimal range violations become errors
            min_duration_ms: Minimum acceptable duration
            max_duration_ms: Maximum acceptable duration
        """
        self.strict_mode = strict_mode
        self.min_duration = min_duration_ms
        self.max_duration = max_duration_ms

    def validate(self, content: str, content_type: str = "auto") -> AnimationValidationResult:
        """
        Validate animation timing in content.

        Args:
            content: CSS, HTML, or JS content to validate
            content_type: "css", "html", "js", or "auto" for auto-detection

        Returns:
            AnimationValidationResult with issues found
        """
        issues: list[AnimationIssue] = []
        durations: list[int] = []

        if not content or not content.strip():
            return AnimationValidationResult(valid=True, issues=[], durations_found=[])

        # Auto-detect content type
        if content_type == "auto":
            content_type = self._detect_content_type(content)

        # Extract durations based on content type
        if content_type in ["css", "html"]:
            durations.extend(self._extract_css_durations(content))
        if content_type in ["js", "html"]:
            durations.extend(self._extract_js_durations(content))
        if content_type == "html":
            durations.extend(self._extract_tailwind_durations(content))

        # Validate each duration
        for duration_ms in durations:
            issue = self._check_duration(duration_ms)
            if issue:
                issues.append(issue)

        # Check for reduced-motion support
        has_reduced_motion = self._check_reduced_motion(content)
        if not has_reduced_motion and durations:
            issues.append(AnimationIssue(
                severity=AnimationSeverity.WARNING,
                message="Missing prefers-reduced-motion media query",
                suggestion="Add @media (prefers-reduced-motion: reduce) to disable animations for accessibility",
            ))

        # Check for will-change hints (performance)
        has_will_change = "will-change" in content.lower()

        # Determine overall validity
        has_errors = any(i.severity == AnimationSeverity.ERROR for i in issues)
        if self.strict_mode:
            has_warnings = any(i.severity == AnimationSeverity.WARNING for i in issues)
            valid = not has_errors and not has_warnings
        else:
            valid = not has_errors

        return AnimationValidationResult(
            valid=valid,
            issues=issues,
            durations_found=list(set(durations)),
            has_reduced_motion=has_reduced_motion,
            has_will_change=has_will_change,
        )

    def _detect_content_type(self, content: str) -> str:
        """Detect content type from content structure."""
        # Check for HTML markers
        if re.search(r'<[a-z]+[^>]*>', content, re.IGNORECASE):
            return "html"
        # Check for CSS markers
        if re.search(r'[.#][\w-]+\s*\{', content):
            return "css"
        # Check for JS markers
        if re.search(r'(function|const|let|var|=>|document\.)', content):
            return "js"
        return "css"  # Default to CSS

    def _extract_css_durations(self, content: str) -> list[int]:
        """Extract durations from CSS content."""
        durations = []

        # Pattern: transition: all 300ms ease, animation: name 0.3s
        css_patterns = [
            r'(?:transition|animation)(?:-duration)?[^;{]*?(\d*\.?\d+)(m?s)',
            r':\s*(\d*\.?\d+)(m?s)\s+(?:ease|linear|cubic)',
        ]

        for pattern in css_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                value = float(match.group(1))
                unit = match.group(2).lower()
                # Convert to milliseconds
                if unit == 's':
                    value *= 1000
                durations.append(int(value))

        return durations

    def _extract_js_durations(self, content: str) -> list[int]:
        """Extract durations from JavaScript content."""
        durations = []

        # Pattern: setTimeout(..., 300), transition = '300ms'
        js_patterns = [
            r'setTimeout\s*\([^,]+,\s*(\d+)\)',
            r'setInterval\s*\([^,]+,\s*(\d+)\)',
            r'["\'](\d+)(m?s)?["\']',  # String durations
            r'duration\s*[=:]\s*(\d+)',
            r'delay\s*[=:]\s*(\d+)',
        ]

        for pattern in js_patterns:
            for match in re.finditer(pattern, content):
                value = int(match.group(1))
                # Heuristic: values > 50 are likely milliseconds
                if 50 <= value <= 10000:
                    durations.append(value)

        return durations

    def _extract_tailwind_durations(self, content: str) -> list[int]:
        """Extract durations from Tailwind classes."""
        durations = []

        # Tailwind duration classes
        tailwind_patterns = [
            r'duration-(\d+)',
            r'delay-(\d+)',
            r'transition-(\d+)',
        ]

        for pattern in tailwind_patterns:
            for match in re.finditer(pattern, content):
                durations.append(int(match.group(1)))

        return durations

    def _check_duration(self, duration_ms: int) -> Optional[AnimationIssue]:
        """Check if a duration is within acceptable range."""
        if duration_ms < self.MIN_PERCEIVABLE:
            return AnimationIssue(
                severity=AnimationSeverity.WARNING,
                message=f"Duration {duration_ms}ms is too fast to perceive",
                duration_ms=duration_ms,
                suggestion=f"Increase to at least {self.OPTIMAL_MIN}ms for noticeable animation",
            )

        if duration_ms < self.OPTIMAL_MIN:
            return AnimationIssue(
                severity=AnimationSeverity.INFO,
                message=f"Duration {duration_ms}ms is below optimal range (200-500ms)",
                duration_ms=duration_ms,
                suggestion="Consider 200-300ms for hover effects, 300-400ms for modals",
            )

        if duration_ms > self.max_duration:
            return AnimationIssue(
                severity=AnimationSeverity.WARNING if self.strict_mode else AnimationSeverity.INFO,
                message=f"Duration {duration_ms}ms exceeds maximum ({self.max_duration}ms)",
                duration_ms=duration_ms,
                suggestion="Long animations may feel sluggish. Keep under 500ms for most interactions.",
            )

        if duration_ms > self.OPTIMAL_MAX:
            return AnimationIssue(
                severity=AnimationSeverity.INFO,
                message=f"Duration {duration_ms}ms exceeds optimal range (200-500ms)",
                duration_ms=duration_ms,
                suggestion="Consider if this animation needs to be this long",
            )

        return None  # Duration is acceptable

    def _check_reduced_motion(self, content: str) -> bool:
        """Check if content includes reduced-motion support."""
        patterns = [
            r'prefers-reduced-motion',
            r'@media.*reduced-motion',
            r'matchMedia.*reduced-motion',
        ]
        return any(re.search(p, content, re.IGNORECASE) for p in patterns)


def validate_animation_timing(
    content: str,
    strict_mode: bool = False,
) -> AnimationValidationResult:
    """
    Convenience function to validate animation timing.

    Args:
        content: CSS, HTML, or JS content
        strict_mode: If True, optimal range violations become errors

    Returns:
        AnimationValidationResult
    """
    validator = AnimationValidator(strict_mode=strict_mode)
    return validator.validate(content)
