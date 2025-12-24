"""
HTMLValidator - HTML Structure and Accessibility Validation

Validates HTML output from The Architect agent for:
- Proper tag closure
- Unique IDs
- Accessibility (ARIA attributes)
- Semantic structure
- Responsive class usage
- No forbidden elements (style, script)
- WCAG color contrast compliance (optional)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from gemini_mcp.validation.contrast_checker import check_wcag_compliance


class ValidationSeverity(Enum):
    """Severity level for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue."""

    severity: ValidationSeverity
    message: str
    line: Optional[int] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "message": self.message,
            "line": self.line,
            "suggestion": self.suggestion,
        }


@dataclass
class ValidationResult:
    """Result of validation."""

    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

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
            "issues": [i.to_dict() for i in self.issues],
        }


class HTMLValidator:
    """
    Validates HTML output from The Architect.

    Checks:
    1. Structural integrity (tag closure, nesting)
    2. ID uniqueness
    3. Accessibility compliance
    4. Semantic HTML usage
    5. Responsive design patterns
    6. Forbidden elements (no style/script)
    """

    # Void elements that don't need closing tags
    VOID_ELEMENTS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    # Semantic HTML5 elements
    SEMANTIC_ELEMENTS = {
        "header", "nav", "main", "section", "article", "aside",
        "footer", "figure", "figcaption", "details", "summary",
    }

    # Interactive elements that should have IDs
    INTERACTIVE_ELEMENTS = {
        "button", "input", "select", "textarea", "a", "form",
    }

    def __init__(
        self,
        strict_mode: bool = True,
        check_contrast: bool = False,
        wcag_level: str = "AA",
    ):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, warnings become errors
            check_contrast: If True, validate WCAG color contrast
            wcag_level: WCAG level for contrast checking - "AA" or "AAA"
        """
        self.strict_mode = strict_mode
        self.check_contrast = check_contrast
        self.wcag_level = wcag_level

    def validate(self, html: str) -> ValidationResult:
        """
        Validate HTML content.

        Args:
            html: HTML string to validate

        Returns:
            ValidationResult with issues found
        """
        issues: list[ValidationIssue] = []

        if not html or not html.strip():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="HTML content is empty",
            ))
            return ValidationResult(valid=False, issues=issues)

        # Run all validation checks
        issues.extend(self._check_forbidden_elements(html))
        issues.extend(self._check_tag_closure(html))
        issues.extend(self._check_id_uniqueness(html))
        issues.extend(self._check_accessibility(html))
        issues.extend(self._check_semantic_structure(html))
        issues.extend(self._check_responsive_classes(html))
        issues.extend(self._check_inline_styles(html))

        # WCAG Contrast check (Phase 6)
        if self.check_contrast:
            issues.extend(self._check_color_contrast(html))

        # Determine overall validity
        has_errors = any(i.severity == ValidationSeverity.ERROR for i in issues)
        if self.strict_mode:
            has_warnings = any(i.severity == ValidationSeverity.WARNING for i in issues)
            valid = not has_errors and not has_warnings
        else:
            valid = not has_errors

        return ValidationResult(valid=valid, issues=issues)

    def _check_forbidden_elements(self, html: str) -> list[ValidationIssue]:
        """Check for forbidden elements like style and script."""
        issues = []

        if re.search(r"<style", html, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Contains <style> tag - HTML should not include CSS",
                suggestion="Remove style tags - CSS is handled by The Alchemist",
            ))

        if re.search(r"<script", html, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Contains <script> tag - HTML should not include JS",
                suggestion="Remove script tags - JS is handled by The Physicist",
            ))

        return issues

    def _check_tag_closure(self, html: str) -> list[ValidationIssue]:
        """Check for unclosed or improperly nested tags."""
        issues = []

        # Extract all tags
        tag_pattern = r"<(/?)(\w+)[^>]*(/?)>"
        matches = re.findall(tag_pattern, html)

        stack = []
        for is_closing, tag_name, is_self_closing in matches:
            tag_name = tag_name.lower()

            # Skip void elements and self-closing tags
            if tag_name in self.VOID_ELEMENTS or is_self_closing:
                continue

            if not is_closing:
                # Opening tag
                stack.append(tag_name)
            else:
                # Closing tag
                if not stack:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Unexpected closing tag </{tag_name}>",
                    ))
                elif stack[-1] != tag_name:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Mismatched tags: expected </{stack[-1]}>, found </{tag_name}>",
                    ))
                    # Try to recover by popping
                    if tag_name in stack:
                        while stack and stack[-1] != tag_name:
                            stack.pop()
                        if stack:
                            stack.pop()
                else:
                    stack.pop()

        # Check for unclosed tags
        for unclosed in stack:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Unclosed tag: <{unclosed}>",
            ))

        return issues

    def _check_id_uniqueness(self, html: str) -> list[ValidationIssue]:
        """Check that all IDs are unique."""
        issues = []

        id_pattern = r'id=["\']([^"\']+)["\']'
        ids = re.findall(id_pattern, html, re.IGNORECASE)

        seen = {}
        for id_value in ids:
            if id_value in seen:
                seen[id_value] += 1
            else:
                seen[id_value] = 1

        duplicates = [id_val for id_val, count in seen.items() if count > 1]
        for dup in duplicates:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Duplicate ID: '{dup}' appears {seen[dup]} times",
                suggestion=f"Make IDs unique: {dup}-1, {dup}-2, etc.",
            ))

        return issues

    def _check_accessibility(self, html: str) -> list[ValidationIssue]:
        """Check for accessibility issues."""
        issues = []

        # Check images for alt attributes
        img_pattern = r"<img[^>]*>"
        for img in re.findall(img_pattern, html, re.IGNORECASE):
            if 'alt=' not in img.lower():
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Image missing alt attribute",
                    suggestion="Add alt attribute for accessibility",
                ))

        # Check buttons for accessible names
        button_pattern = r"<button[^>]*>([^<]*)</button>"
        for match in re.finditer(button_pattern, html, re.IGNORECASE):
            button_tag = match.group(0)
            button_content = match.group(1).strip()

            has_aria_label = 'aria-label' in button_tag.lower()
            has_content = bool(button_content)

            if not has_aria_label and not has_content:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Button without accessible name",
                    suggestion="Add aria-label or visible text content",
                ))

        # Check form inputs for labels
        input_pattern = r"<input[^>]*>"
        for input_tag in re.findall(input_pattern, html, re.IGNORECASE):
            input_type = re.search(r'type=["\']([^"\']+)["\']', input_tag)
            if input_type and input_type.group(1).lower() not in ['submit', 'button', 'hidden']:
                has_id = 'id=' in input_tag.lower()
                has_aria_label = 'aria-label' in input_tag.lower()

                if not has_id and not has_aria_label:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message="Input without ID or aria-label",
                        suggestion="Add id attribute for label association or aria-label",
                    ))

        return issues

    def _check_semantic_structure(self, html: str) -> list[ValidationIssue]:
        """Check for proper semantic HTML usage."""
        issues = []

        # Check for non-semantic div soup
        div_count = len(re.findall(r"<div", html, re.IGNORECASE))
        semantic_count = sum(
            len(re.findall(f"<{elem}", html, re.IGNORECASE))
            for elem in self.SEMANTIC_ELEMENTS
        )

        if div_count > 10 and semantic_count == 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message=f"Heavy div usage ({div_count} divs) without semantic elements",
                suggestion="Consider using semantic HTML5 elements: section, article, nav, etc.",
            ))

        # Check for heading hierarchy
        headings = re.findall(r"<(h[1-6])", html, re.IGNORECASE)
        heading_levels = [int(h[1]) for h in headings]

        if heading_levels and heading_levels[0] != 1:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message=f"First heading is h{heading_levels[0]}, not h1",
                suggestion="Consider starting with h1 for proper document outline",
            ))

        # Check for skipped heading levels
        for i in range(1, len(heading_levels)):
            if heading_levels[i] > heading_levels[i - 1] + 1:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message=f"Skipped heading level: h{heading_levels[i - 1]} to h{heading_levels[i]}",
                    suggestion="Use consecutive heading levels for proper hierarchy",
                ))

        return issues

    def _check_responsive_classes(self, html: str) -> list[ValidationIssue]:
        """Check for responsive design patterns."""
        issues = []

        # Check for Tailwind responsive prefixes
        responsive_prefixes = ["sm:", "md:", "lg:", "xl:", "2xl:"]
        has_responsive = any(prefix in html for prefix in responsive_prefixes)

        if not has_responsive:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message="No responsive Tailwind classes detected",
                suggestion="Consider adding responsive breakpoints (sm:, md:, lg:)",
            ))

        return issues

    def _check_inline_styles(self, html: str) -> list[ValidationIssue]:
        """Check for inline styles."""
        issues = []

        inline_style_pattern = r'style=["\'][^"\']+["\']'
        inline_styles = re.findall(inline_style_pattern, html, re.IGNORECASE)

        if inline_styles:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Found {len(inline_styles)} inline style attribute(s)",
                suggestion="Use Tailwind classes instead of inline styles",
            ))

        return issues

    def _check_color_contrast(self, html: str) -> list[ValidationIssue]:
        """Check WCAG color contrast compliance."""
        issues = []

        # Use contrast_checker to validate
        contrast_report = check_wcag_compliance(html, level=self.wcag_level)

        for contrast_issue in contrast_report.issues:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=(
                    f"Contrast ratio {contrast_issue.ratio}:1 fails WCAG {contrast_issue.wcag_level} "
                    f"({contrast_issue.required_ratio}:1 required) - {contrast_issue.element}"
                ),
                suggestion=contrast_issue.suggestion,
            ))

        return issues

    def extract_ids(self, html: str) -> list[str]:
        """Extract all IDs from HTML."""
        pattern = r'id=["\']([^"\']+)["\']'
        return re.findall(pattern, html, re.IGNORECASE)

    def extract_classes(self, html: str) -> list[str]:
        """Extract all classes from HTML."""
        pattern = r'class=["\']([^"\']+)["\']'
        matches = re.findall(pattern, html, re.IGNORECASE)
        classes = []
        for match in matches:
            classes.extend(match.split())
        return list(set(classes))
