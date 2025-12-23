"""
IDValidator - Cross-Layer ID Validation

Validates consistency between HTML IDs and JavaScript selectors.
This is a critical validator that ensures The Physicist's JS code
can actually target the elements created by The Architect.

Key Validations:
- All JS selectors have matching HTML IDs/classes
- No orphan IDs (defined in HTML but never used)
- Selector naming convention consistency
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from gemini_mcp.validation.html_validator import ValidationSeverity, ValidationIssue, ValidationResult


@dataclass
class CrossLayerReport:
    """Detailed report of cross-layer validation."""

    html_ids: list[str]
    html_classes: list[str]
    js_id_selectors: list[str]
    js_class_selectors: list[str]
    js_query_selectors: list[str]

    missing_in_html: list[str] = field(default_factory=list)
    unused_in_js: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "html_ids": self.html_ids,
            "html_classes": self.html_classes,
            "js_id_selectors": self.js_id_selectors,
            "js_class_selectors": self.js_class_selectors,
            "js_query_selectors": self.js_query_selectors,
            "missing_in_html": self.missing_in_html,
            "unused_in_js": self.unused_in_js,
        }


class IDValidator:
    """
    Cross-layer validator for HTML IDs and JavaScript selectors.

    This validator ensures that:
    1. All JS getElementById/querySelector calls have matching HTML IDs
    2. All JS class selectors have matching HTML classes
    3. Data attributes used in JS exist in HTML
    4. No critical IDs are missing
    """

    # Data attributes commonly used for JS targeting
    DATA_ATTRIBUTES = [
        "data-parallax",
        "data-reveal",
        "data-tilt",
        "data-magnetic",
        "data-scroll",
        "data-animate",
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, missing IDs are errors; if False, warnings
        """
        self.strict_mode = strict_mode

    def validate(self, html: str, js: str) -> ValidationResult:
        """
        Validate that JS selectors match HTML IDs/classes.

        Args:
            html: HTML content from The Architect
            js: JavaScript content from The Physicist

        Returns:
            ValidationResult with cross-layer issues
        """
        issues: list[ValidationIssue] = []

        # Empty JS is valid - not all components need interactions
        if not js or not js.strip():
            return ValidationResult(valid=True, issues=[])

        # Empty HTML with JS is a problem
        if not html or not html.strip():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="JavaScript references DOM elements but HTML is empty",
                suggestion="Ensure Architect generates HTML before Physicist generates JS",
            ))
            return ValidationResult(valid=False, issues=issues)

        # Extract IDs and classes from HTML
        html_ids = self._extract_html_ids(html)
        html_classes = self._extract_html_classes(html)
        html_data_attrs = self._extract_data_attributes(html)

        # Extract selectors from JS
        js_id_refs = self._extract_js_id_references(js)
        js_class_refs = self._extract_js_class_references(js)
        js_data_refs = self._extract_js_data_references(js)
        js_query_selectors = self._extract_query_selectors(js)

        # Validate ID references
        issues.extend(self._validate_id_references(html_ids, js_id_refs))

        # Validate class references
        issues.extend(self._validate_class_references(html_classes, js_class_refs))

        # Validate data attribute references
        issues.extend(self._validate_data_references(html_data_attrs, js_data_refs))

        # Validate complex query selectors
        issues.extend(self._validate_query_selectors(html_ids, html_classes, js_query_selectors))

        # Check for unused IDs (info only)
        issues.extend(self._check_unused_ids(html_ids, js_id_refs, js_query_selectors))

        # Determine overall validity
        has_errors = any(i.severity == ValidationSeverity.ERROR for i in issues)
        if self.strict_mode:
            has_warnings = any(i.severity == ValidationSeverity.WARNING for i in issues)
            valid = not has_errors and not has_warnings
        else:
            valid = not has_errors

        return ValidationResult(valid=valid, issues=issues)

    def _extract_html_ids(self, html: str) -> set[str]:
        """Extract all IDs from HTML."""
        pattern = r'id=["\']([^"\']+)["\']'
        return set(re.findall(pattern, html, re.IGNORECASE))

    def _extract_html_classes(self, html: str) -> set[str]:
        """Extract all classes from HTML."""
        pattern = r'class=["\']([^"\']+)["\']'
        matches = re.findall(pattern, html, re.IGNORECASE)
        classes = set()
        for match in matches:
            classes.update(match.split())
        return classes

    def _extract_data_attributes(self, html: str) -> set[str]:
        """Extract all data-* attributes from HTML."""
        pattern = r'(data-[a-z0-9-]+)'
        return set(re.findall(pattern, html, re.IGNORECASE))

    def _extract_js_id_references(self, js: str) -> set[str]:
        """Extract IDs referenced via getElementById."""
        pattern = r'getElementById\s*\(\s*["\']([^"\']+)["\']'
        return set(re.findall(pattern, js))

    def _extract_js_class_references(self, js: str) -> set[str]:
        """Extract classes referenced via getElementsByClassName."""
        pattern = r'getElementsByClassName\s*\(\s*["\']([^"\']+)["\']'
        return set(re.findall(pattern, js))

    def _extract_js_data_references(self, js: str) -> set[str]:
        """Extract data attributes referenced in JS."""
        refs = set()

        # querySelector with data attribute
        qs_pattern = r'querySelector(?:All)?\s*\(\s*["\'][^"\']*\[(data-[a-z0-9-]+)'
        refs.update(re.findall(qs_pattern, js, re.IGNORECASE))

        # dataset access
        dataset_pattern = r'\.dataset\.([a-zA-Z0-9]+)'
        for match in re.findall(dataset_pattern, js):
            # Convert camelCase to kebab-case
            kebab = re.sub(r'([A-Z])', r'-\1', match).lower()
            refs.add(f"data-{kebab}")

        return refs

    def _extract_query_selectors(self, js: str) -> list[str]:
        """Extract all querySelector/querySelectorAll arguments."""
        pattern = r'querySelector(?:All)?\s*\(\s*["\']([^"\']+)["\']'
        return re.findall(pattern, js)

    def _validate_id_references(
        self,
        html_ids: set[str],
        js_id_refs: set[str]
    ) -> list[ValidationIssue]:
        """Validate that all JS ID references exist in HTML."""
        issues = []

        missing_ids = js_id_refs - html_ids
        for missing_id in missing_ids:
            severity = ValidationSeverity.ERROR if self.strict_mode else ValidationSeverity.WARNING
            issues.append(ValidationIssue(
                severity=severity,
                message=f"JS references ID '{missing_id}' not found in HTML",
                suggestion=f"Add id=\"{missing_id}\" to the target element in HTML",
            ))

        return issues

    def _validate_class_references(
        self,
        html_classes: set[str],
        js_class_refs: set[str]
    ) -> list[ValidationIssue]:
        """Validate that all JS class references exist in HTML."""
        issues = []

        missing_classes = js_class_refs - html_classes
        for missing_class in missing_classes:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=f"JS references class '{missing_class}' not found in HTML",
                suggestion=f"Add class=\"{missing_class}\" to target elements in HTML",
            ))

        return issues

    def _validate_data_references(
        self,
        html_data: set[str],
        js_data_refs: set[str]
    ) -> list[ValidationIssue]:
        """Validate that all JS data attribute references exist in HTML."""
        issues = []

        # Normalize both sets to lowercase for comparison
        html_data_lower = {d.lower() for d in html_data}

        for data_ref in js_data_refs:
            if data_ref.lower() not in html_data_lower:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"JS references data attribute '{data_ref}' not found in HTML",
                    suggestion=f"Add {data_ref} attribute to target elements",
                ))

        return issues

    def _validate_query_selectors(
        self,
        html_ids: set[str],
        html_classes: set[str],
        query_selectors: list[str]
    ) -> list[ValidationIssue]:
        """Validate complex query selectors."""
        issues = []

        for selector in query_selectors:
            # Extract IDs from selector
            id_pattern = r'#([a-zA-Z0-9_-]+)'
            selector_ids = set(re.findall(id_pattern, selector))

            missing_ids = selector_ids - html_ids
            for missing_id in missing_ids:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR if self.strict_mode else ValidationSeverity.WARNING,
                    message=f"Selector '#{missing_id}' in querySelector not found in HTML",
                    suggestion=f"Add id=\"{missing_id}\" to the target element",
                ))

            # Extract classes from selector
            class_pattern = r'\.([a-zA-Z0-9_-]+)'
            selector_classes = set(re.findall(class_pattern, selector))

            # Filter out Tailwind-like classes (usually not custom)
            custom_classes = {
                c for c in selector_classes
                if not any(c.startswith(p) for p in [
                    "bg-", "text-", "font-", "p-", "m-", "w-", "h-",
                    "flex", "grid", "gap-", "rounded-", "shadow-",
                ])
            }

            missing_classes = custom_classes - html_classes
            for missing_class in missing_classes:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Selector '.{missing_class}' in querySelector not found in HTML",
                    suggestion=f"Add class=\"{missing_class}\" to target elements",
                ))

        return issues

    def _check_unused_ids(
        self,
        html_ids: set[str],
        js_id_refs: set[str],
        query_selectors: list[str]
    ) -> list[ValidationIssue]:
        """Check for IDs defined in HTML but never used in JS."""
        issues = []

        # Extract all IDs mentioned in query selectors
        qs_ids = set()
        for selector in query_selectors:
            id_pattern = r'#([a-zA-Z0-9_-]+)'
            qs_ids.update(re.findall(id_pattern, selector))

        all_js_ids = js_id_refs | qs_ids

        # Find unused IDs
        unused_ids = html_ids - all_js_ids

        # Only report if there are many unused IDs (could indicate a problem)
        if len(unused_ids) > 5 and len(all_js_ids) > 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message=f"{len(unused_ids)} HTML IDs not referenced in JS",
                suggestion="Consider if all IDs are necessary or if JS is missing references",
            ))

        return issues

    def generate_report(self, html: str, js: str) -> CrossLayerReport:
        """
        Generate a detailed cross-layer report.

        Args:
            html: HTML content
            js: JavaScript content

        Returns:
            CrossLayerReport with all extracted data
        """
        html_ids = list(self._extract_html_ids(html))
        html_classes = list(self._extract_html_classes(html))
        js_id_refs = list(self._extract_js_id_references(js))
        js_class_refs = list(self._extract_js_class_references(js))
        query_selectors = self._extract_query_selectors(js)

        # Calculate missing/unused
        missing_in_html = list(set(js_id_refs) - set(html_ids))

        # IDs mentioned in query selectors
        qs_ids = set()
        for selector in query_selectors:
            qs_ids.update(re.findall(r'#([a-zA-Z0-9_-]+)', selector))
        all_js_ids = set(js_id_refs) | qs_ids
        unused_in_js = list(set(html_ids) - all_js_ids)

        return CrossLayerReport(
            html_ids=html_ids,
            html_classes=html_classes,
            js_id_selectors=js_id_refs,
            js_class_selectors=js_class_refs,
            js_query_selectors=query_selectors,
            missing_in_html=missing_in_html,
            unused_in_js=unused_in_js,
        )

    def suggest_fixes(self, html: str, js: str) -> dict[str, list[str]]:
        """
        Suggest fixes for cross-layer issues.

        Returns:
            Dict with 'html_additions' and 'js_changes' lists
        """
        report = self.generate_report(html, js)

        html_additions = []
        for missing_id in report.missing_in_html:
            html_additions.append(f'Add id="{missing_id}" to target element')

        js_changes = []
        # Could suggest removing references to non-existent IDs
        # But usually the fix is in HTML, not JS

        return {
            "html_additions": html_additions,
            "js_changes": js_changes,
        }
