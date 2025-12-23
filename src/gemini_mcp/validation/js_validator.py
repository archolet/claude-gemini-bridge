"""
JSValidator - JavaScript Safety and Performance Validation

Validates JavaScript output from The Physicist agent for:
- No framework/library usage
- No global namespace pollution
- No unsafe code patterns
- Performance best practices
- Proper error handling
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from gemini_mcp.validation.html_validator import ValidationSeverity, ValidationIssue, ValidationResult


class JSValidator:
    """
    Validates JavaScript output from The Physicist.

    Checks:
    1. No framework/library imports
    2. No global namespace pollution
    3. No unsafe code patterns
    4. Performance patterns (rAF, throttle)
    5. Error isolation (try-catch)
    6. Proper event listener cleanup
    """

    # Forbidden frameworks and libraries
    FORBIDDEN_PATTERNS = [
        (r"\bimport\s+.*from\s+['\"]react", "React import"),
        (r"\bimport\s+.*from\s+['\"]vue", "Vue import"),
        (r"\bimport\s+.*from\s+['\"]angular", "Angular import"),
        (r"\bimport\s+.*from\s+['\"]jquery", "jQuery import"),
        (r"\bimport\s+.*from\s+['\"]gsap", "GSAP import"),
        (r"\bimport\s+.*from\s+['\"]lodash", "Lodash import"),
        (r"\bimport\s+.*from\s+['\"]axios", "Axios import"),
        (r"\brequire\s*\(\s*['\"]react", "React require"),
        (r"\brequire\s*\(\s*['\"]vue", "Vue require"),
        (r"\$\s*\(", "jQuery $ usage"),
        (r"\bjQuery\s*\(", "jQuery usage"),
        (r"\bgsap\.", "GSAP usage"),
        (r"\bTweenMax\.", "TweenMax usage"),
        (r"\bTweenLite\.", "TweenLite usage"),
        (r"\bReact\.", "React usage"),
        (r"\bReactDOM\.", "ReactDOM usage"),
        (r"\bVue\.", "Vue usage"),
        (r"\bAngular\.", "Angular usage"),
        (r"\b_\.(map|filter|reduce|forEach)", "Lodash usage"),
    ]

    # Patterns for dynamic code execution (security risk)
    DYNAMIC_CODE_PATTERNS = [
        (r"\beval\b\s*\(", "dynamic string execution"),
        (r"\bnew\s+Function\s*\(", "dynamic function construction"),
        (r"\bsetTimeout\s*\(\s*['\"]", "timer with string argument"),
        (r"\bsetInterval\s*\(\s*['\"]", "interval with string argument"),
    ]

    # Patterns for unsafe DOM manipulation
    UNSAFE_DOM_PATTERNS = [
        (r"\.innerHTML\s*=", "direct HTML injection"),
        (r"\.outerHTML\s*=", "outer HTML replacement"),
    ]

    # Performance patterns to check for
    PERFORMANCE_PATTERNS = {
        "requestAnimationFrame": "Uses requestAnimationFrame for smooth animations",
        "IntersectionObserver": "Uses IntersectionObserver for scroll detection",
        "throttle": "Uses throttling for performance",
        "debounce": "Uses debouncing for performance",
    }

    def __init__(self, strict_mode: bool = True):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, warnings become errors
        """
        self.strict_mode = strict_mode

    def validate(self, js: str) -> ValidationResult:
        """
        Validate JavaScript content.

        Args:
            js: JavaScript string to validate

        Returns:
            ValidationResult with issues found
        """
        issues: list[ValidationIssue] = []

        if not js or not js.strip():
            # Empty JS is valid - not all components need interactions
            return ValidationResult(valid=True, issues=[])

        # Run all validation checks
        issues.extend(self._check_forbidden_libraries(js))
        issues.extend(self._check_dynamic_code_execution(js))
        issues.extend(self._check_unsafe_dom_patterns(js))
        issues.extend(self._check_global_pollution(js))
        issues.extend(self._check_syntax(js))
        issues.extend(self._check_html_css_content(js))
        issues.extend(self._check_performance_patterns(js))
        issues.extend(self._check_error_handling(js))
        issues.extend(self._check_event_listeners(js))

        # Determine overall validity
        has_errors = any(i.severity == ValidationSeverity.ERROR for i in issues)
        if self.strict_mode:
            has_warnings = any(i.severity == ValidationSeverity.WARNING for i in issues)
            valid = not has_errors and not has_warnings
        else:
            valid = not has_errors

        return ValidationResult(valid=valid, issues=issues)

    def _check_forbidden_libraries(self, js: str) -> list[ValidationIssue]:
        """Check for forbidden framework/library usage."""
        issues = []

        for pattern, description in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, js, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Framework/library detected: {description}",
                    suggestion="Use vanilla JavaScript only - no frameworks or libraries",
                ))

        return issues

    def _check_dynamic_code_execution(self, js: str) -> list[ValidationIssue]:
        """Check for dynamic code execution patterns (security risk)."""
        issues = []

        for pattern, description in self.DYNAMIC_CODE_PATTERNS:
            if re.search(pattern, js):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Unsafe pattern detected: {description}",
                    suggestion="Avoid dynamic code execution - use safe alternatives",
                ))

        return issues

    def _check_unsafe_dom_patterns(self, js: str) -> list[ValidationIssue]:
        """Check for unsafe DOM manipulation patterns."""
        issues = []

        for pattern, description in self.UNSAFE_DOM_PATTERNS:
            if re.search(pattern, js):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Potentially unsafe DOM pattern: {description}",
                    suggestion="Use textContent or DOM methods for safer manipulation",
                ))

        return issues

    def _check_global_pollution(self, js: str) -> list[ValidationIssue]:
        """Check for global namespace pollution."""
        issues = []

        # Check for global variable declarations outside IIFE
        # First, check if wrapped in IIFE
        is_iife_wrapped = bool(re.search(
            r"^\s*\(function\s*\(|^\s*\(\s*\(\s*\)\s*=>",
            js,
            re.MULTILINE
        ))

        if not is_iife_wrapped:
            # Check for var declarations at top level
            if re.search(r"^var\s+\w+", js, re.MULTILINE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Global var declaration without IIFE wrapper",
                    suggestion="Wrap code in IIFE: (function() { ... })();",
                ))

            # Check for function declarations at top level
            if re.search(r"^function\s+\w+", js, re.MULTILINE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Global function declaration without IIFE wrapper",
                    suggestion="Wrap code in IIFE or use const fn = () => {}",
                ))

        # Check for explicit window assignments
        window_assignments = re.findall(r"window\.(\w+)\s*=", js)
        if window_assignments:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=f"Global window assignments: {', '.join(window_assignments[:5])}",
                suggestion="Avoid polluting global namespace with window properties",
            ))

        return issues

    def _check_syntax(self, js: str) -> list[ValidationIssue]:
        """Check for basic JavaScript syntax issues."""
        issues = []

        # Check balanced braces
        open_braces = js.count("{")
        close_braces = js.count("}")
        if open_braces != close_braces:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Unbalanced braces: {open_braces} open, {close_braces} close",
            ))

        # Check balanced brackets
        open_brackets = js.count("[")
        close_brackets = js.count("]")
        if open_brackets != close_brackets:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Unbalanced brackets: {open_brackets} open, {close_brackets} close",
            ))

        # Check balanced parentheses
        open_parens = js.count("(")
        close_parens = js.count(")")
        if open_parens != close_parens:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Unbalanced parentheses: {open_parens} open, {close_parens} close",
            ))

        # Check for trailing commas in objects/arrays (potential issue in older browsers)
        trailing_comma = re.search(r",\s*[}\]]", js)
        if trailing_comma:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message="Trailing comma detected (may cause issues in IE)",
                suggestion="Remove trailing commas for maximum compatibility",
            ))

        return issues

    def _check_html_css_content(self, js: str) -> list[ValidationIssue]:
        """Check for HTML/CSS content that doesn't belong."""
        issues = []

        # Check for HTML elements (not in strings)
        html_pattern = r"<[a-z]+[^>]*>"
        html_matches = re.findall(html_pattern, js, re.IGNORECASE)

        # Filter out matches inside strings
        in_string_pattern = r"['\"`][^'\"`]*<[^'\"`]*>[^'\"`]*['\"`]"
        string_html = re.findall(in_string_pattern, js)

        # If there's HTML outside strings, flag it
        for match in html_matches:
            in_string = any(match in s for s in string_html)
            if not in_string:
                # Could be a template literal or legitimate use
                # Only flag if it looks like actual HTML structure
                if re.match(r"<(div|span|section|article|header|footer|nav|main)", match, re.IGNORECASE):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message="Contains HTML-like content outside strings",
                        suggestion="HTML structure belongs in Architect output, not Physicist",
                    ))
                    break

        # Check for CSS-like content (style blocks)
        if re.search(r"<style[^>]*>", js, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Contains <style> tag - CSS belongs in Alchemist output",
            ))

        return issues

    def _check_performance_patterns(self, js: str) -> list[ValidationIssue]:
        """Check for performance best practices."""
        issues = []

        # Check if using scroll event without optimization
        has_scroll_listener = re.search(r"addEventListener\s*\(\s*['\"]scroll['\"]", js)
        has_raf = "requestAnimationFrame" in js
        has_throttle = "throttle" in js.lower()

        if has_scroll_listener and not (has_raf or has_throttle):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Scroll event listener without throttling",
                suggestion="Use requestAnimationFrame or throttle for scroll handlers",
            ))

        # Check if using mousemove without optimization
        has_mousemove = re.search(r"addEventListener\s*\(\s*['\"]mousemove['\"]", js)
        if has_mousemove and not (has_raf or has_throttle):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Mousemove event listener without optimization",
                suggestion="Use requestAnimationFrame or throttle for mousemove handlers",
            ))

        # Positive feedback for good patterns
        good_patterns = []
        if has_raf:
            good_patterns.append("requestAnimationFrame")
        if "IntersectionObserver" in js:
            good_patterns.append("IntersectionObserver")
        if has_throttle:
            good_patterns.append("throttle")

        if good_patterns:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message=f"Good performance patterns used: {', '.join(good_patterns)}",
            ))

        return issues

    def _check_error_handling(self, js: str) -> list[ValidationIssue]:
        """Check for proper error handling."""
        issues = []

        # Check if there are try-catch blocks
        has_try_catch = "try {" in js or "try{" in js

        # Check if there are async operations that should be wrapped
        has_fetch = "fetch(" in js
        has_async = "async " in js

        if (has_fetch or has_async) and not has_try_catch:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Async operations without error handling",
                suggestion="Wrap async/fetch operations in try-catch blocks",
            ))

        return issues

    def _check_event_listeners(self, js: str) -> list[ValidationIssue]:
        """Check for event listener patterns."""
        issues = []

        # Count addEventListener calls
        add_listeners = len(re.findall(r"addEventListener\s*\(", js))
        remove_listeners = len(re.findall(r"removeEventListener\s*\(", js))

        # If adding multiple listeners, suggest cleanup pattern
        if add_listeners > 3 and remove_listeners == 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message=f"Multiple event listeners ({add_listeners}) without cleanup",
                suggestion="Consider implementing removeEventListener for cleanup",
            ))

        # Check for DOMContentLoaded wrapper
        has_dom_ready = re.search(
            r"addEventListener\s*\(\s*['\"]DOMContentLoaded['\"]|"
            r"document\.readyState\s*===?\s*['\"]complete['\"]",
            js
        )

        # Check for direct DOM access
        has_direct_dom = re.search(
            r"document\.getElementById|document\.querySelector",
            js
        )

        if has_direct_dom and not has_dom_ready:
            # Check if wrapped in IIFE that's at end of body (can't detect, so just info)
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message="DOM access without DOMContentLoaded check",
                suggestion="Wrap in DOMContentLoaded listener or place script at end of body",
            ))

        return issues

    def extract_selectors(self, js: str) -> list[str]:
        """Extract all DOM selectors used in JavaScript."""
        selectors = set()

        # getElementById
        id_pattern = r"getElementById\s*\(\s*['\"]([^'\"]+)['\"]"
        selectors.update(f"#{m}" for m in re.findall(id_pattern, js))

        # querySelector/querySelectorAll
        qs_pattern = r"querySelector(?:All)?\s*\(\s*['\"]([^'\"]+)['\"]"
        selectors.update(re.findall(qs_pattern, js))

        # getElementsByClassName
        class_pattern = r"getElementsByClassName\s*\(\s*['\"]([^'\"]+)['\"]"
        selectors.update(f".{m}" for m in re.findall(class_pattern, js))

        return list(selectors)

    def extract_event_types(self, js: str) -> list[str]:
        """Extract all event types listened for."""
        pattern = r"addEventListener\s*\(\s*['\"]([^'\"]+)['\"]"
        return list(set(re.findall(pattern, js)))

    def extract_ids_referenced(self, js: str) -> list[str]:
        """Extract all element IDs referenced in JavaScript."""
        ids = set()

        # getElementById
        id_pattern = r"getElementById\s*\(\s*['\"]([^'\"]+)['\"]"
        ids.update(re.findall(id_pattern, js))

        # querySelector with ID
        qs_id_pattern = r"querySelector(?:All)?\s*\(\s*['\"]#([^'\"#\s]+)['\"]"
        ids.update(re.findall(qs_id_pattern, js))

        return list(ids)
