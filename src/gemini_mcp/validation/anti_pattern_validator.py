"""
AntiPatternValidator - Enterprise Anti-Pattern Detection

Detects and reports anti-patterns across three categories:
1. Accessibility: Focus removal, tabindex abuse, missing ARIA
2. Performance: Scroll handlers without throttle, layout thrashing
3. Styling: Arbitrary z-index, !important abuse, inline styles

Each pattern includes severity, detection regex, and auto-fix suggestion.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from gemini_mcp.validation.types import (
    ValidationSeverity,
    ValidationIssue,
    ValidationResult,
)


class AntiPatternCategory(Enum):
    """Categories of anti-patterns."""
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    STYLING = "styling"
    ALPINE = "alpine"


@dataclass
class AntiPattern:
    """
    Definition of a single anti-pattern to detect.

    Attributes:
        name: Short identifier (e.g., "no-focus-outline")
        pattern: Regex pattern to detect the anti-pattern
        message: Human-readable description of the issue
        severity: How serious is this issue?
        category: Which category does this belong to?
        suggestion: How to fix this issue
        auto_fixable: Can this be automatically fixed?
        fix_pattern: Regex replacement for auto-fix (if auto_fixable)
        fix_replacement: Replacement string for auto-fix
    """
    name: str
    pattern: str
    message: str
    severity: ValidationSeverity
    category: AntiPatternCategory
    suggestion: str
    auto_fixable: bool = False
    fix_pattern: Optional[str] = None
    fix_replacement: Optional[str] = None


# === ANTI-PATTERN DEFINITIONS ===

ACCESSIBILITY_ANTIPATTERNS = [
    AntiPattern(
        name="no-focus-outline",
        pattern=r"outline:\s*none|outline:\s*0(?!\.\d)",
        message="Focus outline removed without alternative focus indicator",
        severity=ValidationSeverity.ERROR,
        category=AntiPatternCategory.ACCESSIBILITY,
        suggestion="Use focus-visible:ring-2 instead of removing outline",
        auto_fixable=False,
    ),
    AntiPattern(
        name="high-tabindex",
        pattern=r'tabindex\s*=\s*["\']([2-9]|\d{2,})["\']',
        message="tabindex > 1 disrupts natural tab order",
        severity=ValidationSeverity.ERROR,
        category=AntiPatternCategory.ACCESSIBILITY,
        suggestion="Use tabindex='0' or '-1' only. Restructure DOM for natural tab order.",
        auto_fixable=False,
    ),
    AntiPattern(
        name="missing-button-type",
        pattern=r'<button(?![^>]*type\s*=)[^>]*>',
        message="Button without type attribute may submit forms unexpectedly",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.ACCESSIBILITY,
        suggestion="Add type='button' for non-submit buttons",
        auto_fixable=True,
        fix_pattern=r'<button(?![^>]*type\s*=)([^>]*)>',
        fix_replacement=r'<button type="button"\1>',
    ),
    AntiPattern(
        name="div-with-onclick",
        pattern=r'<div[^>]*@click[^>]*>(?![^<]*role\s*=)',
        message="Clickable div without role attribute is not keyboard accessible",
        severity=ValidationSeverity.ERROR,
        category=AntiPatternCategory.ACCESSIBILITY,
        suggestion="Add role='button' and tabindex='0' to clickable divs",
        auto_fixable=False,
    ),
    AntiPattern(
        name="image-without-alt",
        pattern=r'<img(?![^>]*alt\s*=)[^>]*>',
        message="Image missing alt attribute",
        severity=ValidationSeverity.ERROR,
        category=AntiPatternCategory.ACCESSIBILITY,
        suggestion="Add alt attribute with descriptive text or alt='' for decorative images",
        auto_fixable=False,
    ),
    AntiPattern(
        name="aria-hidden-focusable",
        pattern=r'aria-hidden\s*=\s*["\']true["\'][^>]*(tabindex\s*=\s*["\'][0-9]+["\']|button|input|select|textarea|<a\s)',
        message="aria-hidden='true' on focusable element creates navigation trap",
        severity=ValidationSeverity.ERROR,
        category=AntiPatternCategory.ACCESSIBILITY,
        suggestion="Remove aria-hidden or make element non-focusable",
        auto_fixable=False,
    ),
    AntiPattern(
        name="placeholder-as-label",
        pattern=r'<input[^>]*placeholder\s*=[^>]*>(?![^<]*<label)',
        message="Placeholder text used as only label",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.ACCESSIBILITY,
        suggestion="Add a proper <label> element associated via for/id or wrapping",
        auto_fixable=False,
    ),
    # === NEW ENTERPRISE PATTERNS ===
    AntiPattern(
        name="no-skip-link",
        pattern=r'<body[^>]*>(?:(?!<a[^>]*href\s*=\s*["\']#(?:main|content|skip)["\'][^>]*>).)*?<main',
        message="Missing skip link before main content - keyboard users cannot bypass navigation",
        severity=ValidationSeverity.CRITICAL,
        category=AntiPatternCategory.ACCESSIBILITY,
        suggestion="Add <a href='#main' class='sr-only focus:not-sr-only'>Skip to main content</a> after <body>",
        auto_fixable=True,
        fix_pattern=r'(<body[^>]*>)',
        fix_replacement=r'\1\n  <a href="#main" class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:rounded">Skip to main content</a>',
    ),
    AntiPattern(
        name="heading-skip",
        pattern=r'<h([1-6])[^>]*>.*?</h\1>\s*(?:<[^h][^>]*>\s*)*<h([1-6])',
        message="Heading hierarchy skip detected - accessibility screen readers depend on proper heading order",
        severity=ValidationSeverity.ERROR,
        category=AntiPatternCategory.ACCESSIBILITY,
        suggestion="Ensure headings follow sequential order: h1 → h2 → h3. Do not skip levels.",
        auto_fixable=False,
    ),
]

PERFORMANCE_ANTIPATTERNS = [
    AntiPattern(
        name="scroll-without-throttle",
        pattern=r'@scroll\s*=\s*["\'][^"\']*["\'](?![^>]*\.throttle)',
        message="Scroll event handler without throttle modifier",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.PERFORMANCE,
        suggestion="Use @scroll.throttle.100ms for better performance",
        auto_fixable=True,
        fix_pattern=r'@scroll\s*=',
        fix_replacement=r'@scroll.throttle.100ms=',
    ),
    AntiPattern(
        name="resize-without-debounce",
        pattern=r'@resize\s*=\s*["\'][^"\']*["\'](?![^>]*\.(debounce|throttle))',
        message="Resize event handler without debounce/throttle modifier",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.PERFORMANCE,
        suggestion="Use @resize.debounce.200ms for better performance",
        auto_fixable=True,
        fix_pattern=r'@resize\s*=',
        fix_replacement=r'@resize.debounce.200ms=',
    ),
    AntiPattern(
        name="input-without-debounce",
        pattern=r'@input\s*=\s*["\'][^"\']*\$fetch|@input\s*=\s*["\'][^"\']*fetch\(',
        message="Input event with fetch call without debounce",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.PERFORMANCE,
        suggestion="Use @input.debounce.300ms for API calls on input",
        auto_fixable=False,
    ),
    AntiPattern(
        name="excessive-watchers",
        pattern=r'(x-effect\s*=\s*["\'][^"\']*["\'][^}]*){4,}',
        message="Too many x-effect watchers may cause performance issues",
        severity=ValidationSeverity.INFO,
        category=AntiPatternCategory.PERFORMANCE,
        suggestion="Consider consolidating effects or using computed properties",
        auto_fixable=False,
    ),
    # === NEW ENTERPRISE PATTERNS ===
    AntiPattern(
        name="layout-thrash-loop",
        pattern=r'(for\s*\(|\.forEach\s*\(|\.map\s*\()[^)]*\)[^{]*\{[^}]*(?:getBoundingClientRect|offsetWidth|offsetHeight|clientWidth|clientHeight|scrollWidth|scrollHeight)',
        message="getBoundingClientRect or offset*/client*/scroll* inside loop causes layout thrashing",
        severity=ValidationSeverity.ERROR,
        category=AntiPatternCategory.PERFORMANCE,
        suggestion="Cache layout reads before the loop or use requestAnimationFrame batching",
        auto_fixable=False,
    ),
    AntiPattern(
        name="sync-xhr",
        pattern=r'new\s+XMLHttpRequest[^;]*\.open\s*\([^,]+,[^,]+,\s*false',
        message="Synchronous XHR blocks main thread and degrades user experience",
        severity=ValidationSeverity.ERROR,
        category=AntiPatternCategory.PERFORMANCE,
        suggestion="Use async: true or fetch() API instead of synchronous XHR",
        auto_fixable=False,
    ),
]

STYLING_ANTIPATTERNS = [
    AntiPattern(
        name="arbitrary-high-zindex",
        pattern=r'z-\[\d{4,}\]|z-\[9{3,}\]',
        message="Arbitrary z-index value too high (9999+)",
        severity=ValidationSeverity.ERROR,
        category=AntiPatternCategory.STYLING,
        suggestion="Use semantic z-index scale: z-10 (raised), z-20 (dropdown), z-30 (sticky), z-40 (fixed), z-50 (modal backdrop), z-[60] (modal), z-[80] (tooltip), z-[90] (toast)",
        auto_fixable=False,
    ),
    AntiPattern(
        name="important-abuse",
        pattern=r'!important',
        message="!important overuse can lead to specificity wars",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.STYLING,
        suggestion="Refactor selectors instead of using !important",
        auto_fixable=False,
    ),
    AntiPattern(
        name="inline-style",
        pattern=r'style\s*=\s*["\'][^"\']+["\']',
        message="Inline style attribute detected",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.STYLING,
        suggestion="Use Tailwind classes instead of inline styles",
        auto_fixable=False,
    ),
    AntiPattern(
        name="hardcoded-color",
        pattern=r'(bg|text|border)-\[#[0-9a-fA-F]{3,6}\]',
        message="Hardcoded color value instead of theme token",
        severity=ValidationSeverity.INFO,
        category=AntiPatternCategory.STYLING,
        suggestion="Use semantic color classes like bg-primary, text-slate-700",
        auto_fixable=False,
    ),
    AntiPattern(
        name="mixed-spacing",
        pattern=r'(p|m|gap)-\d[^"\']*\s+(p|m|gap)-\[\d+px\]',
        message="Mixed Tailwind spacing with arbitrary pixel values",
        severity=ValidationSeverity.INFO,
        category=AntiPatternCategory.STYLING,
        suggestion="Use consistent Tailwind spacing scale (4, 8, 12, 16, etc.)",
        auto_fixable=False,
    ),
    # === NEW ENTERPRISE PATTERNS ===
    AntiPattern(
        name="fixed-width",
        pattern=r'w-\[\d{3,}px\]|width:\s*\d{3,}px',
        message="Fixed pixel width (300px+) breaks responsive design",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.STYLING,
        suggestion="Use max-w-* classes or percentage-based widths for responsive layouts",
        auto_fixable=False,
    ),
    AntiPattern(
        name="no-dark-mode",
        pattern=r'(?:bg|text|border)-(?:white|black|gray-[1-9]00|slate-[1-9]00|zinc-[1-9]00|neutral-[1-9]00|stone-[1-9]00)(?![^"\']*dark:)',
        message="Color class without dark mode variant may cause poor contrast in dark mode",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.STYLING,
        suggestion="Add corresponding dark: variant (e.g., 'bg-white dark:bg-gray-900')",
        auto_fixable=False,
    ),
]

ALPINE_ANTIPATTERNS = [
    AntiPattern(
        name="xshow-without-cloak",
        pattern=r'x-show\s*=\s*["\'][^"\']+["\'](?![^>]*x-cloak)',
        message="x-show without x-cloak causes flash of unstyled content",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.ALPINE,
        suggestion="Add x-cloak attribute to prevent FOUC",
        auto_fixable=True,
        fix_pattern=r'(x-show\s*=\s*["\'][^"\']+["\'])(?![^>]*x-cloak)',
        fix_replacement=r'\1 x-cloak',
    ),
    AntiPattern(
        name="dynamic-content-no-live",
        pattern=r'x-text\s*=\s*["\'][^"\']+["\'](?![^<]*aria-live)',
        message="Dynamic text content without aria-live region",
        severity=ValidationSeverity.INFO,
        category=AntiPatternCategory.ALPINE,
        suggestion="Add aria-live='polite' for screen reader announcements",
        auto_fixable=False,
    ),
    AntiPattern(
        name="xdata-in-child",
        pattern=r'<[^>]+x-data\s*=\s*["\'][^"\']+["\'][^>]*>[^<]*<[^>]+x-data\s*=',
        message="Nested x-data components can cause scope confusion",
        severity=ValidationSeverity.INFO,
        category=AntiPatternCategory.ALPINE,
        suggestion="Consider using $refs or events for component communication",
        auto_fixable=False,
    ),
    AntiPattern(
        name="direct-dom-manipulation",
        pattern=r'\$el\.(innerHTML|outerHTML|textContent)\s*=',
        message="Direct DOM manipulation bypasses Alpine reactivity",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.ALPINE,
        suggestion="Use x-text, x-html, or reactive data instead of direct DOM manipulation",
        auto_fixable=False,
    ),
    AntiPattern(
        name="error-no-role-alert",
        pattern=r'class\s*=\s*["\'][^"\']*text-red[^"\']*["\'][^>]*>(?![^<]*role\s*=\s*["\']alert["\'])',
        message="Error message without role='alert' for screen readers",
        severity=ValidationSeverity.WARNING,
        category=AntiPatternCategory.ALPINE,
        suggestion="Add role='alert' to error messages for accessibility",
        auto_fixable=False,
    ),
    # === NEW ENTERPRISE PATTERNS ===
    AntiPattern(
        name="sync-init",
        pattern=r'x-init\s*=\s*["\'][^"\']*(?:fetch\(|await\s|\.then\()[^"\']*["\']',
        message="Async operations in x-init without proper wrapper blocks rendering",
        severity=ValidationSeverity.ERROR,
        category=AntiPatternCategory.ALPINE,
        suggestion="Wrap async operations: x-init=\"$nextTick(async () => { await fetch(...) })\" or use x-data with init() method",
        auto_fixable=False,
    ),
]


# Combine all anti-patterns
ALL_ANTIPATTERNS = (
    ACCESSIBILITY_ANTIPATTERNS
    + PERFORMANCE_ANTIPATTERNS
    + STYLING_ANTIPATTERNS
    + ALPINE_ANTIPATTERNS
)


class AntiPatternValidator:
    """
    Validator for detecting enterprise anti-patterns in HTML/CSS/JS.

    Usage:
        validator = AntiPatternValidator()
        result = validator.validate(html_content)

        # Or with auto-fix
        fixed_html, result = validator.validate_and_fix(html_content)
    """

    def __init__(
        self,
        categories: Optional[list[AntiPatternCategory]] = None,
        severity_threshold: ValidationSeverity = ValidationSeverity.INFO,
    ):
        """
        Initialize the anti-pattern validator.

        Args:
            categories: Categories to check (default: all)
            severity_threshold: Minimum severity to report (default: INFO)
        """
        self.categories = categories or list(AntiPatternCategory)
        self.severity_threshold = severity_threshold

        # Build pattern list based on categories
        self.patterns = [
            p for p in ALL_ANTIPATTERNS
            if p.category in self.categories
        ]

    def validate(self, content: str, content_type: str = "html") -> ValidationResult:
        """
        Validate content for anti-patterns.

        Args:
            content: HTML/CSS/JS content to validate
            content_type: Type of content ("html", "css", "js")

        Returns:
            ValidationResult with all detected anti-patterns
        """
        issues: list[ValidationIssue] = []

        for pattern in self.patterns:
            # Skip if below severity threshold
            if ValidationSeverity.get_order(pattern.severity) < ValidationSeverity.get_order(self.severity_threshold):
                continue

            # Find all matches
            try:
                matches = list(re.finditer(pattern.pattern, content, re.IGNORECASE | re.DOTALL))
            except re.error:
                continue

            for match in matches:
                # Calculate line number
                line_num = content[:match.start()].count('\n') + 1

                # Get context snippet
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 20)
                location = content[start:end].replace('\n', ' ')

                issues.append(ValidationIssue(
                    severity=pattern.severity,
                    message=pattern.message,
                    line=line_num,
                    suggestion=pattern.suggestion,
                    location=f"...{location}...",
                    rule=f"{pattern.category.value}/{pattern.name}",
                    auto_fixable=pattern.auto_fixable,
                ))

        # Determine validity (no critical or errors = valid)
        has_blockers = any(
            i.severity in (ValidationSeverity.CRITICAL, ValidationSeverity.ERROR)
            for i in issues
        )

        return ValidationResult(
            valid=not has_blockers,
            issues=issues,
        )

    def validate_and_fix(self, content: str) -> tuple[str, ValidationResult]:
        """
        Validate and auto-fix content where possible.

        Args:
            content: HTML/CSS/JS content to validate and fix

        Returns:
            Tuple of (fixed_content, validation_result)
        """
        fixed_content = content
        fixed_issues: list[ValidationIssue] = []

        for pattern in self.patterns:
            if not pattern.auto_fixable or not pattern.fix_pattern or not pattern.fix_replacement:
                continue

            try:
                # Apply fix
                new_content = re.sub(
                    pattern.fix_pattern,
                    pattern.fix_replacement,
                    fixed_content,
                    flags=re.IGNORECASE | re.DOTALL,
                )

                if new_content != fixed_content:
                    fixed_issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        message=f"Auto-fixed: {pattern.message}",
                        suggestion=f"Applied: {pattern.suggestion}",
                        rule=f"{pattern.category.value}/{pattern.name}",
                        auto_fixable=True,
                    ))
                    fixed_content = new_content
            except re.error:
                continue

        # Now validate the fixed content
        result = self.validate(fixed_content)

        # Add info about auto-fixes
        for fix_issue in fixed_issues:
            result.issues.insert(0, fix_issue)

        return fixed_content, result

    def get_patterns_by_category(
        self, category: AntiPatternCategory
    ) -> list[AntiPattern]:
        """Get all patterns for a specific category."""
        return [p for p in self.patterns if p.category == category]

    def get_auto_fixable_patterns(self) -> list[AntiPattern]:
        """Get all auto-fixable patterns."""
        return [p for p in self.patterns if p.auto_fixable]


# === CONVENIENCE FUNCTIONS ===

def validate_antipatterns(
    content: str,
    categories: Optional[list[str]] = None,
) -> ValidationResult:
    """
    Convenience function for quick anti-pattern validation.

    Args:
        content: HTML/CSS/JS content to validate
        categories: List of category names (default: all)

    Returns:
        ValidationResult with detected anti-patterns
    """
    cat_enum = None
    if categories:
        cat_enum = [AntiPatternCategory(c) for c in categories if c in [e.value for e in AntiPatternCategory]]

    validator = AntiPatternValidator(categories=cat_enum)
    return validator.validate(content)


def fix_antipatterns(content: str) -> tuple[str, ValidationResult]:
    """
    Convenience function to validate and auto-fix anti-patterns.

    Args:
        content: HTML/CSS/JS content to fix

    Returns:
        Tuple of (fixed_content, validation_result)
    """
    validator = AntiPatternValidator()
    return validator.validate_and_fix(content)


def get_antipattern_report(result: ValidationResult) -> str:
    """
    Generate a human-readable report from validation result.

    Args:
        result: ValidationResult from anti-pattern validation

    Returns:
        Formatted string report
    """
    lines = [
        "=== ANTI-PATTERN VALIDATION REPORT ===",
        "",
        f"Status: {'PASS' if result.valid else 'FAIL'}",
        f"Critical: {result.critical_count}",
        f"Errors: {result.error_count}",
        f"Warnings: {result.warning_count}",
        f"Info: {result.info_count}",
        "",
    ]

    if result.issues:
        lines.append("Issues Found:")
        lines.append("-" * 40)

        for issue in result.issues:
            icon = {
                ValidationSeverity.CRITICAL: "[CRIT]",
                ValidationSeverity.ERROR: "[ERROR]",
                ValidationSeverity.WARNING: "[WARN]",
                ValidationSeverity.INFO: "[INFO]",
            }.get(issue.severity, "[?]")

            lines.append(f"{icon} {issue.message}")
            if issue.line:
                lines.append(f"       Line: {issue.line}")
            if issue.rule:
                lines.append(f"       Rule: {issue.rule}")
            if issue.suggestion:
                lines.append(f"       Fix: {issue.suggestion}")
            if issue.auto_fixable:
                lines.append("       [Auto-fixable]")
            lines.append("")
    else:
        lines.append("No anti-patterns detected!")

    return "\n".join(lines)
