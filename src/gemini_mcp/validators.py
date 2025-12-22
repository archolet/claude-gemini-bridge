"""Validation utilities for design output quality assurance.

Phase 2 Implementation:
- GAP 4: Token Extraction - arbitrary values and opacity modifiers
- GAP 5: Responsive Validation - breakpoint coverage
- GAP 6: A11y Enforcement - ARIA, heading hierarchy, focus states
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


# =============================================================================
# GAP 4: Token Extraction - Arbitrary Values & Opacity Modifiers
# =============================================================================

class TailwindTokenType(Enum):
    """Types of Tailwind tokens."""
    COLOR = "color"
    SPACING = "spacing"
    TYPOGRAPHY = "typography"
    EFFECT = "effect"
    LAYOUT = "layout"
    ARBITRARY = "arbitrary"


@dataclass
class ExtractedToken:
    """A single extracted Tailwind token with full parsing."""
    raw_class: str
    token_type: TailwindTokenType
    base_value: str
    modifier: Optional[str] = None  # responsive prefix (sm:, md:, etc.)
    state: Optional[str] = None  # hover:, focus:, etc.
    opacity: Optional[float] = None  # /50 -> 0.5
    arbitrary_value: Optional[str] = None  # [#E11D48], [2.5rem]
    is_dark_mode: bool = False
    is_negative: bool = False


# Patterns for parsing Tailwind classes
ARBITRARY_VALUE_PATTERN = re.compile(r'\[([^\]]+)\]')
OPACITY_PATTERN = re.compile(r'/(\d+)$')
RESPONSIVE_PREFIXES = {'sm', 'md', 'lg', 'xl', '2xl'}
STATE_PREFIXES = {'hover', 'focus', 'active', 'disabled', 'visited',
                  'focus-within', 'focus-visible', 'group-hover'}

# Color prefixes
COLOR_PREFIXES = {'bg-', 'text-', 'border-', 'ring-', 'fill-', 'stroke-',
                  'outline-', 'divide-', 'accent-', 'caret-', 'decoration-',
                  'placeholder-', 'from-', 'via-', 'to-'}

# Spacing prefixes
SPACING_PREFIXES = {'p-', 'px-', 'py-', 'pt-', 'pr-', 'pb-', 'pl-',
                    'm-', 'mx-', 'my-', 'mt-', 'mr-', 'mb-', 'ml-',
                    'gap-', 'gap-x-', 'gap-y-', 'space-x-', 'space-y-',
                    'w-', 'h-', 'min-w-', 'min-h-', 'max-w-', 'max-h-',
                    'inset-', 'top-', 'right-', 'bottom-', 'left-',
                    'basis-', 'grow-', 'shrink-'}

# Typography prefixes
TYPOGRAPHY_PREFIXES = {'font-', 'text-', 'tracking-', 'leading-',
                       'indent-', 'align-', 'whitespace-', 'break-',
                       'hyphens-', 'content-'}


def parse_tailwind_class(cls: str) -> ExtractedToken:
    """Parse a single Tailwind class into its components.

    Handles:
    - Arbitrary values: text-[#E11D48], p-[2.5rem], bg-[url(...)]
    - Opacity modifiers: bg-blue-500/50, text-white/80
    - Responsive prefixes: sm:, md:, lg:, xl:, 2xl:
    - State variants: hover:, focus:, active:, etc.
    - Dark mode: dark:
    - Negative values: -mt-4, -translate-x-1

    Args:
        cls: A single Tailwind class string

    Returns:
        ExtractedToken with all parsed components
    """
    original = cls
    modifier = None
    state = None
    is_dark = False
    is_negative = False
    opacity = None
    arbitrary = None

    # Split by colons to get prefixes
    parts = cls.split(':')
    base = parts[-1]  # Last part is the actual class
    prefixes = parts[:-1] if len(parts) > 1 else []

    # Parse prefixes
    for prefix in prefixes:
        if prefix == 'dark':
            is_dark = True
        elif prefix in RESPONSIVE_PREFIXES:
            modifier = prefix
        elif prefix in STATE_PREFIXES or prefix.startswith('group-'):
            state = prefix

    # Check for negative value
    if base.startswith('-'):
        is_negative = True
        base = base[1:]

    # Extract opacity modifier (e.g., /50)
    opacity_match = OPACITY_PATTERN.search(base)
    if opacity_match:
        opacity = int(opacity_match.group(1)) / 100
        base = OPACITY_PATTERN.sub('', base)

    # Extract arbitrary value (e.g., [#E11D48])
    arbitrary_match = ARBITRARY_VALUE_PATTERN.search(base)
    if arbitrary_match:
        arbitrary = arbitrary_match.group(1)
        # Keep the bracket syntax in base for identification

    # Determine token type
    token_type = _classify_token_type(base, arbitrary)

    return ExtractedToken(
        raw_class=original,
        token_type=token_type,
        base_value=base,
        modifier=modifier,
        state=state,
        opacity=opacity,
        arbitrary_value=arbitrary,
        is_dark_mode=is_dark,
        is_negative=is_negative,
    )


def _classify_token_type(base: str, arbitrary: Optional[str]) -> TailwindTokenType:
    """Classify a Tailwind class into a token type."""
    # Arbitrary values need special handling
    if arbitrary:
        # Check if it's a color (hex, rgb, hsl)
        if arbitrary.startswith('#') or arbitrary.startswith('rgb') or arbitrary.startswith('hsl'):
            return TailwindTokenType.COLOR
        # Check if it's a spacing value (rem, px, em, %)
        if re.match(r'^[\d.]+(?:rem|px|em|%|vh|vw)$', arbitrary):
            return TailwindTokenType.SPACING
        # Default to arbitrary
        return TailwindTokenType.ARBITRARY

    # Check by prefix
    for prefix in COLOR_PREFIXES:
        if base.startswith(prefix):
            return TailwindTokenType.COLOR

    for prefix in SPACING_PREFIXES:
        if base.startswith(prefix):
            return TailwindTokenType.SPACING

    for prefix in TYPOGRAPHY_PREFIXES:
        if base.startswith(prefix):
            return TailwindTokenType.TYPOGRAPHY

    # Effects
    if any(base.startswith(p) for p in ['shadow-', 'opacity-', 'blur-', 'brightness-',
                                         'contrast-', 'grayscale-', 'invert-', 'saturate-',
                                         'sepia-', 'backdrop-', 'transition-', 'duration-',
                                         'ease-', 'delay-', 'animate-']):
        return TailwindTokenType.EFFECT

    # Layout
    if any(base.startswith(p) for p in ['flex', 'grid', 'block', 'inline', 'hidden',
                                         'columns-', 'float-', 'clear-', 'isolate',
                                         'object-', 'overflow-', 'position', 'z-',
                                         'justify-', 'items-', 'content-', 'place-',
                                         'self-', 'order-']):
        return TailwindTokenType.LAYOUT

    return TailwindTokenType.ARBITRARY


def extract_all_tokens(html: str) -> Dict[TailwindTokenType, List[ExtractedToken]]:
    """Extract and categorize all Tailwind tokens from HTML.

    Args:
        html: HTML string containing Tailwind classes

    Returns:
        Dictionary mapping token types to lists of extracted tokens
    """
    # Extract all class attributes
    class_pattern = r'class="([^"]*)"'
    all_classes_raw = re.findall(class_pattern, html)
    all_classes = ' '.join(all_classes_raw)

    # Parse each class
    tokens: Dict[TailwindTokenType, List[ExtractedToken]] = {
        t: [] for t in TailwindTokenType
    }

    seen = set()
    for cls in all_classes.split():
        cls = cls.strip()
        if not cls or cls in seen:
            continue
        seen.add(cls)

        token = parse_tailwind_class(cls)
        tokens[token.token_type].append(token)

    return tokens


def extract_color_palette(html: str) -> Dict[str, str]:
    """Extract color palette from HTML including arbitrary values.

    Returns dict mapping role (inferred) to color value.
    Handles: bg-blue-500, text-[#E11D48], border-gray-200/50
    """
    tokens = extract_all_tokens(html)
    colors = {}

    for token in tokens[TailwindTokenType.COLOR]:
        # Determine role from prefix
        role = "unknown"
        base = token.base_value

        if base.startswith('bg-'):
            role = "background"
            color_part = base[3:]
        elif base.startswith('text-'):
            role = "text"
            color_part = base[5:]
        elif base.startswith('border-'):
            role = "border"
            color_part = base[7:]
        elif base.startswith('ring-'):
            role = "ring"
            color_part = base[5:]
        else:
            color_part = base

        # Get the actual color value
        if token.arbitrary_value:
            color_value = token.arbitrary_value
        else:
            color_value = color_part

        # Add opacity if present
        if token.opacity is not None:
            color_value = f"{color_value}/{int(token.opacity * 100)}"

        # Create unique key
        key = f"{role}:{color_value}"
        colors[key] = token.raw_class

    return colors


# =============================================================================
# GAP 5: Responsive Validation
# =============================================================================

@dataclass
class ResponsiveReport:
    """Report on responsive design coverage."""
    is_valid: bool
    coverage: Dict[str, float]  # breakpoint -> coverage percentage
    missing_breakpoints: List[str]
    issues: List[str]
    touch_target_violations: List[str]
    suggestions: List[str]


# Standard breakpoints
BREAKPOINTS = {
    'sm': 640,
    'md': 768,
    'lg': 1024,
    'xl': 1280,
    '2xl': 1536,
}

# Minimum touch target size (WCAG 2.5.5)
MIN_TOUCH_TARGET = 44  # px


def validate_responsive(
    html: str,
    required_breakpoints: Optional[List[str]] = None,
    mobile_first: bool = True,
) -> ResponsiveReport:
    """Validate responsive design coverage in HTML.

    Checks:
    - Breakpoint coverage (are responsive variants used?)
    - Mobile-first approach (base classes before responsive variants)
    - Touch target sizes (44x44px minimum)
    - Common responsive issues

    Args:
        html: HTML string to validate
        required_breakpoints: List of breakpoints that must have coverage
        mobile_first: Whether to enforce mobile-first approach

    Returns:
        ResponsiveReport with validation results
    """
    if required_breakpoints is None:
        required_breakpoints = ['sm', 'md', 'lg']

    tokens = extract_all_tokens(html)
    issues = []
    suggestions = []
    touch_violations = []

    # Count classes per breakpoint
    breakpoint_counts: Dict[str, int] = {bp: 0 for bp in BREAKPOINTS}
    base_count = 0

    for token_list in tokens.values():
        for token in token_list:
            if token.modifier and token.modifier in BREAKPOINTS:
                breakpoint_counts[token.modifier] += 1
            else:
                base_count += 1

    # Calculate coverage
    total = base_count + sum(breakpoint_counts.values())
    coverage = {}
    for bp, count in breakpoint_counts.items():
        coverage[bp] = (count / total * 100) if total > 0 else 0

    # Check required breakpoints
    missing = []
    for bp in required_breakpoints:
        if breakpoint_counts.get(bp, 0) == 0:
            missing.append(bp)
            issues.append(f"No responsive variants for breakpoint '{bp}'")

    # Mobile-first check
    if mobile_first and base_count == 0:
        issues.append("No base (mobile) classes found - not mobile-first")
        suggestions.append("Add base classes without breakpoint prefixes for mobile view")

    # Check for desktop-first anti-patterns
    if breakpoint_counts.get('lg', 0) > base_count and mobile_first:
        suggestions.append("Consider mobile-first: more lg: variants than base classes")

    # Touch target check - look for small interactive elements
    touch_violations = _check_touch_targets(html)
    if touch_violations:
        issues.extend([f"Touch target too small: {v}" for v in touch_violations[:3]])

    # Common responsive issues
    _check_common_responsive_issues(html, issues, suggestions)

    is_valid = len(missing) == 0 and len(issues) <= 1  # Allow minor issues

    return ResponsiveReport(
        is_valid=is_valid,
        coverage=coverage,
        missing_breakpoints=missing,
        issues=issues,
        touch_target_violations=touch_violations,
        suggestions=suggestions,
    )


def _check_touch_targets(html: str) -> List[str]:
    """Check for interactive elements that may be too small for touch."""
    violations = []

    # Pattern to find buttons, links, inputs with small sizes
    small_size_patterns = [
        (r'<button[^>]*class="[^"]*\bw-(\d+)\b[^"]*"', 'button'),
        (r'<a[^>]*class="[^"]*\bw-(\d+)\b[^"]*"', 'link'),
        (r'<input[^>]*class="[^"]*\bh-(\d+)\b[^"]*"', 'input'),
    ]

    for pattern, element_type in small_size_patterns:
        for match in re.finditer(pattern, html, re.IGNORECASE):
            size = int(match.group(1))
            # Tailwind size 10 = 2.5rem = 40px, 11 = 44px
            if size < 11:
                violations.append(f"{element_type} with w/h-{size} (< 44px)")

    # Also check for explicit small pixel sizes
    explicit_small = re.findall(r'(?:w|h)-\[(\d+)px\]', html)
    for size in explicit_small:
        if int(size) < MIN_TOUCH_TARGET:
            violations.append(f"Element with {size}px dimension (< 44px)")

    return violations


def _check_common_responsive_issues(html: str, issues: List[str], suggestions: List[str]):
    """Check for common responsive design anti-patterns."""
    # Fixed widths without responsive variants
    fixed_widths = re.findall(r'\bw-\[\d+px\](?!.*(?:sm:|md:|lg:))', html)
    if fixed_widths:
        suggestions.append(f"Fixed pixel widths found ({len(fixed_widths)}): consider responsive alternatives")

    # Text sizes without responsive scaling
    text_sizes = re.findall(r'\btext-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl)\b', html)
    responsive_text = re.findall(r'(?:sm:|md:|lg:|xl:)text-', html)
    if len(text_sizes) > 5 and len(responsive_text) == 0:
        suggestions.append("Consider responsive text sizes (text-base md:text-lg lg:text-xl)")

    # Hidden elements without responsive show
    hidden = len(re.findall(r'\bhidden\b', html))
    responsive_block = len(re.findall(r'(?:sm:|md:|lg:)(?:block|flex|grid)', html))
    if hidden > 0 and responsive_block == 0:
        suggestions.append("'hidden' used but no responsive show variants (md:block)")


# =============================================================================
# GAP 6: Accessibility (A11y) Enforcement
# =============================================================================

class A11yLevel(Enum):
    """WCAG conformance levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


@dataclass
class A11yIssue:
    """A single accessibility issue."""
    severity: str  # "error", "warning", "info"
    rule: str  # WCAG rule reference
    message: str
    element: Optional[str] = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class A11yReport:
    """Accessibility validation report."""
    is_valid: bool
    level: A11yLevel
    issues: List[A11yIssue]
    passed_checks: List[str]
    score: int  # 0-100

    @property
    def errors(self) -> List[A11yIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[A11yIssue]:
        return [i for i in self.issues if i.severity == "warning"]


class A11yValidator:
    """Accessibility validator with auto-fix capabilities.

    Validates:
    - ARIA attributes
    - Heading hierarchy
    - Focus states
    - Color contrast (basic)
    - Form labels
    - Image alt text
    - Link text
    """

    def __init__(self, level: A11yLevel = A11yLevel.AA):
        self.level = level

    def validate(self, html: str) -> A11yReport:
        """Validate HTML for accessibility issues.

        Args:
            html: HTML string to validate

        Returns:
            A11yReport with all findings
        """
        issues: List[A11yIssue] = []
        passed: List[str] = []

        # Run all checks
        self._check_heading_hierarchy(html, issues, passed)
        self._check_aria_attributes(html, issues, passed)
        self._check_focus_states(html, issues, passed)
        self._check_form_labels(html, issues, passed)
        self._check_image_alt(html, issues, passed)
        self._check_link_text(html, issues, passed)
        self._check_color_contrast_hints(html, issues, passed)
        self._check_interactive_roles(html, issues, passed)

        # Calculate score
        total_checks = len(issues) + len(passed)
        score = int((len(passed) / total_checks * 100)) if total_checks > 0 else 100

        # AA level requires no errors
        is_valid = len([i for i in issues if i.severity == "error"]) == 0

        return A11yReport(
            is_valid=is_valid,
            level=self.level,
            issues=issues,
            passed_checks=passed,
            score=score,
        )

    def auto_fix(self, html: str, issues: Optional[List[A11yIssue]] = None) -> str:
        """Attempt to automatically fix accessibility issues.

        Args:
            html: HTML string to fix
            issues: Optional list of specific issues to fix

        Returns:
            HTML with fixes applied
        """
        if issues is None:
            report = self.validate(html)
            issues = [i for i in report.issues if i.auto_fixable]

        result = html

        for issue in issues:
            if not issue.auto_fixable:
                continue

            if issue.rule == "focus-visible":
                result = self._fix_focus_visible(result)
            elif issue.rule == "button-type":
                result = self._fix_button_type(result)
            elif issue.rule == "img-alt":
                result = self._fix_img_alt(result)
            elif issue.rule == "link-role":
                result = self._fix_link_role(result)

        return result

    def _check_heading_hierarchy(self, html: str, issues: List[A11yIssue], passed: List[str]):
        """Check for proper heading hierarchy (h1 -> h2 -> h3, no skipping)."""
        headings = re.findall(r'<h(\d)[^>]*>', html, re.IGNORECASE)

        if not headings:
            passed.append("No headings to validate")
            return

        levels = [int(h) for h in headings]

        # Check for h1
        if 1 not in levels:
            issues.append(A11yIssue(
                severity="warning",
                rule="heading-order",
                message="No h1 heading found",
                suggestion="Add an h1 as the main page heading",
            ))

        # Check for skipped levels
        prev_level = 0
        for level in levels:
            if level > prev_level + 1 and prev_level > 0:
                issues.append(A11yIssue(
                    severity="error",
                    rule="heading-order",
                    message=f"Heading level skipped: h{prev_level} to h{level}",
                    suggestion=f"Use h{prev_level + 1} instead of h{level}",
                ))
            prev_level = level

        if not any(i.rule == "heading-order" for i in issues):
            passed.append("Heading hierarchy is correct")

    def _check_aria_attributes(self, html: str, issues: List[A11yIssue], passed: List[str]):
        """Check for proper ARIA attribute usage."""
        # Check for aria-label on interactive elements without visible text
        buttons_no_text = re.findall(r'<button[^>]*>(\s*<[^>]+>\s*)</button>', html, re.IGNORECASE)
        for match in buttons_no_text:
            # Icon-only buttons need aria-label
            if 'aria-label' not in match and 'aria-labelledby' not in match:
                issues.append(A11yIssue(
                    severity="error",
                    rule="aria-label",
                    message="Icon button without aria-label",
                    element=match[:50],
                    suggestion="Add aria-label describing the button action",
                    auto_fixable=False,
                ))

        # Check for invalid ARIA roles
        roles = re.findall(r'role="([^"]+)"', html)
        valid_roles = {'button', 'link', 'checkbox', 'radio', 'textbox', 'listbox',
                       'menu', 'menuitem', 'tab', 'tabpanel', 'tablist', 'dialog',
                       'alert', 'alertdialog', 'navigation', 'main', 'banner',
                       'contentinfo', 'complementary', 'form', 'search', 'region',
                       'img', 'list', 'listitem', 'presentation', 'none'}

        for role in roles:
            if role not in valid_roles:
                issues.append(A11yIssue(
                    severity="warning",
                    rule="aria-role",
                    message=f"Unknown ARIA role: {role}",
                    suggestion="Use a valid ARIA role",
                ))

        if not any(i.rule.startswith("aria") for i in issues):
            passed.append("ARIA attributes are valid")

    def _check_focus_states(self, html: str, issues: List[A11yIssue], passed: List[str]):
        """Check for focus visibility on interactive elements."""
        # Look for interactive elements
        interactive_pattern = r'<(button|a|input|select|textarea)[^>]*class="([^"]*)"[^>]*>'
        matches = re.findall(interactive_pattern, html, re.IGNORECASE)

        missing_focus = []
        for element, classes in matches:
            # Check if focus styles are present
            has_focus = any(f in classes for f in [
                'focus:', 'focus-visible:', 'focus-within:',
                'ring-', 'outline-'
            ])
            if not has_focus:
                missing_focus.append(element)

        if missing_focus:
            issues.append(A11yIssue(
                severity="error",
                rule="focus-visible",
                message=f"Interactive elements without focus styles: {', '.join(set(missing_focus))}",
                suggestion="Add focus:ring-2 or focus-visible:outline-2 classes",
                auto_fixable=True,
            ))
        else:
            passed.append("Focus states are defined")

    def _check_form_labels(self, html: str, issues: List[A11yIssue], passed: List[str]):
        """Check that form inputs have associated labels."""
        # Find inputs without labels
        inputs = re.findall(r'<input[^>]*id="([^"]*)"[^>]*>', html, re.IGNORECASE)
        labels = re.findall(r'<label[^>]*for="([^"]*)"[^>]*>', html, re.IGNORECASE)

        # Also check for aria-label
        aria_labeled = re.findall(r'<input[^>]*aria-label="[^"]*"[^>]*>', html, re.IGNORECASE)

        unlabeled = set(inputs) - set(labels)
        if unlabeled and len(aria_labeled) < len(unlabeled):
            issues.append(A11yIssue(
                severity="error",
                rule="form-label",
                message=f"Form inputs without labels: {len(unlabeled)} found",
                suggestion="Add <label for='id'> or aria-label attribute",
            ))
        else:
            passed.append("Form inputs have labels")

    def _check_image_alt(self, html: str, issues: List[A11yIssue], passed: List[str]):
        """Check that images have alt attributes."""
        # Images without alt
        imgs_no_alt = re.findall(r'<img(?![^>]*alt=)[^>]*>', html, re.IGNORECASE)

        if imgs_no_alt:
            issues.append(A11yIssue(
                severity="error",
                rule="img-alt",
                message=f"Images without alt attribute: {len(imgs_no_alt)}",
                suggestion="Add alt='description' or alt='' for decorative images",
                auto_fixable=True,
            ))
        else:
            passed.append("Images have alt attributes")

    def _check_link_text(self, html: str, issues: List[A11yIssue], passed: List[str]):
        """Check that links have meaningful text."""
        # Find links with generic text
        generic_texts = ['click here', 'here', 'read more', 'learn more', 'more', 'link']
        links = re.findall(r'<a[^>]*>([^<]*)</a>', html, re.IGNORECASE)

        generic_found = []
        for text in links:
            if text.strip().lower() in generic_texts:
                generic_found.append(text.strip())

        if generic_found:
            issues.append(A11yIssue(
                severity="warning",
                rule="link-text",
                message=f"Generic link text found: {', '.join(generic_found[:3])}",
                suggestion="Use descriptive link text that makes sense out of context",
            ))
        else:
            passed.append("Link text is descriptive")

    def _check_color_contrast_hints(self, html: str, issues: List[A11yIssue], passed: List[str]):
        """Basic check for potential color contrast issues."""
        # This is a hint-based check since we can't calculate actual contrast
        # without rendering

        # Light text on light backgrounds
        light_on_light = re.findall(
            r'class="[^"]*\bbg-(?:white|gray-50|gray-100|slate-50|slate-100)[^"]*\btext-(?:gray-300|gray-400|slate-300|slate-400)',
            html
        )

        if light_on_light:
            issues.append(A11yIssue(
                severity="warning",
                rule="color-contrast",
                message="Potential low contrast: light text on light background",
                suggestion="Use darker text colors (text-gray-700 or darker)",
            ))

        # Dark text on dark backgrounds
        dark_on_dark = re.findall(
            r'class="[^"]*\bbg-(?:gray-800|gray-900|slate-800|slate-900|black)[^"]*\btext-(?:gray-600|gray-700|slate-600|slate-700)',
            html
        )

        if dark_on_dark:
            issues.append(A11yIssue(
                severity="warning",
                rule="color-contrast",
                message="Potential low contrast: dark text on dark background",
                suggestion="Use lighter text colors (text-gray-300 or lighter)",
            ))

        if not light_on_light and not dark_on_dark:
            passed.append("No obvious contrast issues detected")

    def _check_interactive_roles(self, html: str, issues: List[A11yIssue], passed: List[str]):
        """Check that interactive elements have proper roles."""
        # Divs with onClick should have button role
        clickable_divs = re.findall(r'<div[^>]*(?:@click|onclick|x-on:click)[^>]*>', html, re.IGNORECASE)

        for div in clickable_divs:
            if 'role="button"' not in div and 'role="link"' not in div:
                issues.append(A11yIssue(
                    severity="error",
                    rule="interactive-role",
                    message="Clickable div without button/link role",
                    element=div[:80],
                    suggestion="Add role='button' and tabindex='0'",
                    auto_fixable=True,
                ))

        if not clickable_divs:
            passed.append("Interactive roles are properly assigned")

    # Auto-fix methods
    def _fix_focus_visible(self, html: str) -> str:
        """Add focus-visible styles to interactive elements."""
        # Add focus ring to buttons without focus styles
        pattern = r'(<button[^>]*class=")([^"]*)(")([^>]*>)'

        def add_focus(match):
            classes = match.group(2)
            if 'focus:' not in classes and 'focus-visible:' not in classes:
                classes += ' focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500'
            return f'{match.group(1)}{classes}{match.group(3)}{match.group(4)}'

        return re.sub(pattern, add_focus, html)

    def _fix_button_type(self, html: str) -> str:
        """Add type='button' to buttons without type."""
        pattern = r'<button(?![^>]*type=)([^>]*)>'
        return re.sub(pattern, r'<button type="button"\1>', html)

    def _fix_img_alt(self, html: str) -> str:
        """Add empty alt to images without alt attribute."""
        pattern = r'<img(?![^>]*alt=)([^>]*)>'
        return re.sub(pattern, r'<img alt=""\1>', html)

    def _fix_link_role(self, html: str) -> str:
        """Add proper attributes to div-based links."""
        pattern = r'<div([^>]*)(onclick|@click|x-on:click)([^>]*)>'

        def add_role(match):
            attrs = match.group(1) + match.group(3)
            if 'role=' not in attrs:
                attrs = f' role="button" tabindex="0"' + attrs
            return f'<div{attrs}{match.group(2)}{match.group(3)}>'

        return re.sub(pattern, add_role, html, flags=re.IGNORECASE)


# =============================================================================
# Combined Validator
# =============================================================================

@dataclass
class ValidationReport:
    """Combined validation report."""
    responsive: ResponsiveReport
    accessibility: A11yReport
    tokens_extracted: int

    @property
    def is_valid(self) -> bool:
        return self.responsive.is_valid and self.accessibility.is_valid

    @property
    def overall_score(self) -> int:
        return (self.accessibility.score +
                (100 if self.responsive.is_valid else 50)) // 2


def validate_design_output(
    html: str,
    required_breakpoints: Optional[List[str]] = None,
    a11y_level: A11yLevel = A11yLevel.AA,
) -> ValidationReport:
    """Run all validators on design output.

    Args:
        html: HTML string to validate
        required_breakpoints: List of required responsive breakpoints
        a11y_level: WCAG conformance level to check against

    Returns:
        ValidationReport with all validation results
    """
    tokens = extract_all_tokens(html)
    total_tokens = sum(len(t) for t in tokens.values())

    responsive = validate_responsive(html, required_breakpoints)

    a11y_validator = A11yValidator(level=a11y_level)
    accessibility = a11y_validator.validate(html)

    return ValidationReport(
        responsive=responsive,
        accessibility=accessibility,
        tokens_extracted=total_tokens,
    )


def auto_fix_design(html: str) -> Tuple[str, List[str]]:
    """Attempt to automatically fix common issues.

    Args:
        html: HTML string to fix

    Returns:
        Tuple of (fixed HTML, list of fixes applied)
    """
    fixes_applied = []
    result = html

    # A11y fixes
    a11y = A11yValidator()
    report = a11y.validate(result)

    fixable = [i for i in report.issues if i.auto_fixable]
    if fixable:
        result = a11y.auto_fix(result, fixable)
        fixes_applied.extend([f"A11y: {i.rule}" for i in fixable])

    return result, fixes_applied
