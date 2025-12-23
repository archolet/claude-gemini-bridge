"""
CSSValidator - CSS Syntax and Best Practices Validation

Validates CSS output from The Alchemist agent for:
- Valid CSS syntax
- No JavaScript code
- No HTML elements
- Proper selector usage (class/ID preferred)
- CSS variable consistency
- Performance considerations (will-change, etc.)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from gemini_mcp.validation.html_validator import ValidationSeverity, ValidationIssue, ValidationResult


class CSSValidator:
    """
    Validates CSS output from The Alchemist.

    Checks:
    1. No HTML elements in output
    2. No JavaScript code
    3. Valid CSS syntax (balanced braces)
    4. Proper selector usage
    5. CSS variable definitions
    6. Animation/keyframe validation
    7. Performance patterns
    """

    # CSS properties that affect performance
    PERFORMANCE_PROPERTIES = {
        "will-change",
        "transform",
        "opacity",
        "filter",
        "backdrop-filter",
    }

    # Properties that should use CSS variables for theming
    THEMEABLE_PROPERTIES = {
        "color",
        "background-color",
        "border-color",
        "fill",
        "stroke",
    }

    def __init__(self, strict_mode: bool = True):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, warnings become errors
        """
        self.strict_mode = strict_mode

    def validate(self, css: str) -> ValidationResult:
        """
        Validate CSS content.

        Args:
            css: CSS string to validate

        Returns:
            ValidationResult with issues found
        """
        issues: list[ValidationIssue] = []

        if not css or not css.strip():
            # Empty CSS is valid - not all components need custom CSS
            return ValidationResult(valid=True, issues=[])

        # Run all validation checks
        issues.extend(self._check_no_html(css))
        issues.extend(self._check_no_javascript(css))
        issues.extend(self._check_syntax(css))
        issues.extend(self._check_selectors(css))
        issues.extend(self._check_important_usage(css))
        issues.extend(self._check_vendor_prefixes(css))
        issues.extend(self._check_animations(css))
        issues.extend(self._check_css_variables(css))

        # Determine overall validity
        has_errors = any(i.severity == ValidationSeverity.ERROR for i in issues)
        if self.strict_mode:
            has_warnings = any(i.severity == ValidationSeverity.WARNING for i in issues)
            valid = not has_errors and not has_warnings
        else:
            valid = not has_errors

        return ValidationResult(valid=valid, issues=issues)

    def _check_no_html(self, css: str) -> list[ValidationIssue]:
        """Check that output contains no HTML."""
        issues = []

        # Check for HTML tags
        html_pattern = r"<[a-z]+[^>]*>"
        if re.search(html_pattern, css, re.IGNORECASE):
            # Make sure it's not inside a string (content property)
            if not re.search(r"content\s*:\s*['\"][^'\"]*<", css):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message="Contains HTML elements - Alchemist only outputs CSS",
                    suggestion="Remove all HTML tags from output",
                ))

        return issues

    def _check_no_javascript(self, css: str) -> list[ValidationIssue]:
        """Check that output contains no JavaScript."""
        issues = []

        js_patterns = [
            (r"\bfunction\s*\(", "function declaration"),
            (r"\bconst\s+\w+\s*=", "const declaration"),
            (r"\blet\s+\w+\s*=", "let declaration"),
            (r"\bvar\s+\w+\s*=", "var declaration"),
            (r"=>\s*\{", "arrow function"),
            (r"addEventListener", "event listener"),
            (r"document\.", "document API"),
            (r"window\.", "window API"),
        ]

        for pattern, description in js_patterns:
            if re.search(pattern, css):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Contains JavaScript code ({description})",
                    suggestion="Remove JavaScript - Alchemist only outputs CSS",
                ))
                break  # One error is enough

        return issues

    def _check_syntax(self, css: str) -> list[ValidationIssue]:
        """Check for basic CSS syntax issues."""
        issues = []

        # Check balanced braces
        open_braces = css.count("{")
        close_braces = css.count("}")
        if open_braces != close_braces:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Unbalanced braces: {open_braces} open, {close_braces} close",
                suggestion="Ensure all CSS blocks are properly closed",
            ))

        # Check for unclosed strings
        single_quotes = css.count("'") - css.count("\\'")
        double_quotes = css.count('"') - css.count('\\"')
        if single_quotes % 2 != 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Unclosed single quote in CSS",
            ))
        if double_quotes % 2 != 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Unclosed double quote in CSS",
            ))

        # Check for missing semicolons (heuristic)
        # Look for property: value followed by another property without semicolon
        missing_semi_pattern = r":\s*[^;{}]+\n\s*[a-z-]+\s*:"
        if re.search(missing_semi_pattern, css, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Possible missing semicolon detected",
                suggestion="Ensure all CSS declarations end with semicolons",
            ))

        return issues

    def _check_selectors(self, css: str) -> list[ValidationIssue]:
        """Check for proper selector usage."""
        issues = []

        # Extract all selectors (before {)
        selector_pattern = r"([^{}@]+)\s*\{"
        selectors = re.findall(selector_pattern, css)

        # Valid at-rules and pseudo selectors
        valid_starts = [
            "@keyframes", "@media", "@supports", "@font-face",
            ":root", "from", "to", "@layer", "@property",
        ]

        for selector in selectors:
            selector = selector.strip()
            if not selector:
                continue

            # Skip at-rules and keyframe internals
            if any(selector.lower().startswith(v.lower()) for v in valid_starts):
                continue

            # Skip percentage selectors (keyframes)
            if re.match(r"^\d+%$", selector):
                continue

            # Check for bare element selectors
            # Allow combinators like "section > div" but flag bare "div" or "p"
            bare_element_pattern = r"^[a-z]+$"
            if re.match(bare_element_pattern, selector, re.IGNORECASE):
                if selector.lower() not in ["from", "to"]:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Bare element selector '{selector}' - prefer class/ID",
                        suggestion=f"Use .{selector}-class or #{selector}-id instead",
                    ))

        return issues

    def _check_important_usage(self, css: str) -> list[ValidationIssue]:
        """Check for excessive !important usage."""
        issues = []

        important_count = len(re.findall(r"!important", css, re.IGNORECASE))
        if important_count > 5:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=f"Excessive !important usage ({important_count} occurrences)",
                suggestion="Reduce !important usage - increase selector specificity instead",
            ))
        elif important_count > 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message=f"Found {important_count} !important declaration(s)",
                suggestion="Consider if !important is necessary",
            ))

        return issues

    def _check_vendor_prefixes(self, css: str) -> list[ValidationIssue]:
        """Check for missing vendor prefixes on critical properties."""
        issues = []

        # Properties that need vendor prefixes
        prefix_needed = {
            "backdrop-filter": ["-webkit-backdrop-filter"],
            "clip-path": ["-webkit-clip-path"],
            "mask": ["-webkit-mask"],
            "mask-image": ["-webkit-mask-image"],
        }

        for prop, prefixes in prefix_needed.items():
            # Check if property is used
            if re.search(rf"\b{prop}\s*:", css):
                # Check if prefixed version exists
                for prefix in prefixes:
                    if prefix not in css:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message=f"Missing vendor prefix: {prefix} for {prop}",
                            suggestion=f"Add {prefix} before {prop} for Safari support",
                        ))

        return issues

    def _check_animations(self, css: str) -> list[ValidationIssue]:
        """Validate @keyframes and animation properties."""
        issues = []

        # Extract keyframe names
        keyframe_pattern = r"@keyframes\s+([a-zA-Z0-9_-]+)"
        defined_keyframes = set(re.findall(keyframe_pattern, css))

        # Extract animation-name references
        animation_pattern = r"animation(?:-name)?\s*:\s*([a-zA-Z0-9_-]+)"
        used_animations = set(re.findall(animation_pattern, css))

        # Check for undefined animations
        for anim in used_animations:
            # Skip CSS keywords
            if anim.lower() in ["none", "initial", "inherit", "unset"]:
                continue
            if anim not in defined_keyframes:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Animation '{anim}' used but not defined",
                    suggestion=f"Add @keyframes {anim} {{ ... }}",
                ))

        # Check for unused keyframes
        for keyframe in defined_keyframes:
            if keyframe not in used_animations:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message=f"@keyframes '{keyframe}' defined but not used",
                    suggestion="Remove unused keyframes or add animation property",
                ))

        return issues

    def _check_css_variables(self, css: str) -> list[ValidationIssue]:
        """Check CSS variable definitions and usage."""
        issues = []

        # Extract variable definitions
        var_def_pattern = r"--([a-zA-Z0-9_-]+)\s*:"
        defined_vars = set(re.findall(var_def_pattern, css))

        # Extract variable usages
        var_use_pattern = r"var\(--([a-zA-Z0-9_-]+)"
        used_vars = set(re.findall(var_use_pattern, css))

        # Check for undefined variables (INFO only - might be defined elsewhere)
        for var in used_vars:
            if var not in defined_vars:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message=f"CSS variable '--{var}' used but not defined in this file",
                    suggestion="Ensure variable is defined in :root or parent scope",
                ))

        # Check for unused defined variables
        for var in defined_vars:
            if var not in used_vars:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message=f"CSS variable '--{var}' defined but not used",
                    suggestion="Remove unused variable or use it in styles",
                ))

        return issues

    def extract_keyframes(self, css: str) -> list[str]:
        """Extract all @keyframes names from CSS."""
        pattern = r"@keyframes\s+([a-zA-Z0-9_-]+)"
        return re.findall(pattern, css)

    def extract_css_variables(self, css: str) -> list[str]:
        """Extract all CSS variable names from CSS."""
        pattern = r"--([a-zA-Z0-9_-]+)"
        return list(set(re.findall(pattern, css)))

    def extract_selectors(self, css: str) -> list[str]:
        """Extract all CSS selectors."""
        pattern = r"([.#][a-zA-Z0-9_-]+)"
        return list(set(re.findall(pattern, css)))
