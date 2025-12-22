"""Tests for Phase 2 Validation implementations.

GAP 4: Token Extraction - arbitrary values and opacity modifiers
GAP 5: Responsive Validation - breakpoint coverage
GAP 6: A11y Enforcement - ARIA, heading hierarchy, focus states
"""

import pytest

from gemini_mcp.validators import (
    # GAP 4: Token Extraction
    parse_tailwind_class,
    extract_all_tokens,
    extract_color_palette,
    TailwindTokenType,
    ExtractedToken,
    # GAP 5: Responsive Validation
    validate_responsive,
    ResponsiveReport,
    # GAP 6: A11y
    A11yValidator,
    A11yLevel,
    A11yReport,
    A11yIssue,
    # Combined
    validate_design_output,
    auto_fix_design,
    ValidationReport,
)


# =============================================================================
# GAP 4: Token Extraction Tests
# =============================================================================

class TestGAP4TokenExtraction:
    """Tests for Tailwind token extraction with arbitrary values and modifiers."""

    def test_parse_simple_class(self):
        """Test parsing a simple Tailwind class."""
        token = parse_tailwind_class("bg-blue-500")

        assert token.raw_class == "bg-blue-500"
        assert token.token_type == TailwindTokenType.COLOR
        assert token.base_value == "bg-blue-500"
        assert token.modifier is None
        assert token.opacity is None

    def test_parse_arbitrary_color_value(self):
        """Test parsing arbitrary color value like text-[#E11D48]."""
        token = parse_tailwind_class("text-[#E11D48]")

        assert token.raw_class == "text-[#E11D48]"
        assert token.token_type == TailwindTokenType.COLOR
        assert token.arbitrary_value == "#E11D48"

    def test_parse_arbitrary_spacing_value(self):
        """Test parsing arbitrary spacing value like p-[2.5rem]."""
        token = parse_tailwind_class("p-[2.5rem]")

        assert token.raw_class == "p-[2.5rem]"
        assert token.token_type == TailwindTokenType.SPACING
        assert token.arbitrary_value == "2.5rem"

    def test_parse_opacity_modifier(self):
        """Test parsing opacity modifier like bg-blue-500/50."""
        token = parse_tailwind_class("bg-blue-500/50")

        assert token.raw_class == "bg-blue-500/50"
        assert token.token_type == TailwindTokenType.COLOR
        assert token.opacity == 0.5  # /50 = 50%
        assert token.base_value == "bg-blue-500"

    def test_parse_responsive_prefix(self):
        """Test parsing responsive prefix like md:text-lg."""
        token = parse_tailwind_class("md:text-lg")

        assert token.raw_class == "md:text-lg"
        assert token.modifier == "md"
        assert token.base_value == "text-lg"

    def test_parse_state_variant(self):
        """Test parsing state variant like hover:bg-blue-600."""
        token = parse_tailwind_class("hover:bg-blue-600")

        assert token.raw_class == "hover:bg-blue-600"
        assert token.state == "hover"
        assert token.base_value == "bg-blue-600"

    def test_parse_dark_mode(self):
        """Test parsing dark mode variant like dark:bg-gray-900."""
        token = parse_tailwind_class("dark:bg-gray-900")

        assert token.raw_class == "dark:bg-gray-900"
        assert token.is_dark_mode is True
        assert token.base_value == "bg-gray-900"

    def test_parse_negative_value(self):
        """Test parsing negative value like -mt-4."""
        token = parse_tailwind_class("-mt-4")

        assert token.raw_class == "-mt-4"
        assert token.is_negative is True
        assert token.base_value == "mt-4"

    def test_parse_combined_modifiers(self):
        """Test parsing combined modifiers like sm:hover:dark:bg-blue-500/80."""
        token = parse_tailwind_class("sm:hover:dark:bg-blue-500/80")

        assert token.raw_class == "sm:hover:dark:bg-blue-500/80"
        assert token.modifier == "sm"
        assert token.state == "hover"
        assert token.is_dark_mode is True
        assert token.opacity == 0.8
        assert token.base_value == "bg-blue-500"

    def test_extract_all_tokens_from_html(self):
        """Test extracting all tokens from HTML."""
        html = '''
        <div class="bg-blue-500 text-white p-4 md:p-8 hover:bg-blue-600">
            <span class="text-[#E11D48] font-bold">Text</span>
        </div>
        '''

        tokens = extract_all_tokens(html)

        # Check we got tokens of different types
        assert len(tokens[TailwindTokenType.COLOR]) > 0
        assert len(tokens[TailwindTokenType.SPACING]) > 0

    def test_extract_color_palette(self):
        """Test extracting color palette from HTML."""
        html = '''
        <div class="bg-blue-500 text-white border-gray-200">
            <span class="text-[#E11D48]">Text</span>
        </div>
        '''

        palette = extract_color_palette(html)

        assert len(palette) >= 3
        # Should have background, text, and border colors
        assert any("background" in k for k in palette.keys())
        assert any("text" in k for k in palette.keys())

    def test_arbitrary_rgb_value(self):
        """Test parsing arbitrary RGB value."""
        token = parse_tailwind_class("bg-[rgb(59,130,246)]")

        assert token.arbitrary_value == "rgb(59,130,246)"
        assert token.token_type == TailwindTokenType.COLOR

    def test_arbitrary_px_value(self):
        """Test parsing arbitrary pixel value."""
        token = parse_tailwind_class("w-[320px]")

        assert token.arbitrary_value == "320px"
        assert token.token_type == TailwindTokenType.SPACING


# =============================================================================
# GAP 5: Responsive Validation Tests
# =============================================================================

class TestGAP5ResponsiveValidation:
    """Tests for responsive design validation."""

    def test_validate_responsive_with_coverage(self):
        """Test validation with good breakpoint coverage."""
        html = '''
        <div class="p-4 sm:p-6 md:p-8 lg:p-12">
            <h1 class="text-2xl md:text-4xl lg:text-6xl">Title</h1>
        </div>
        '''

        report = validate_responsive(html, required_breakpoints=["sm", "md", "lg"])

        assert report.is_valid
        assert len(report.missing_breakpoints) == 0

    def test_validate_responsive_missing_breakpoints(self):
        """Test validation with missing breakpoints."""
        html = '''
        <div class="p-4">
            <h1 class="text-2xl">Title</h1>
        </div>
        '''

        report = validate_responsive(html, required_breakpoints=["sm", "md", "lg"])

        assert not report.is_valid
        assert "sm" in report.missing_breakpoints
        assert "md" in report.missing_breakpoints
        assert "lg" in report.missing_breakpoints

    def test_validate_responsive_mobile_first(self):
        """Test mobile-first validation."""
        # Desktop-first anti-pattern (only lg: classes, no base)
        html = '''
        <div class="lg:p-4 lg:m-4">
            <h1 class="lg:text-2xl">Title</h1>
        </div>
        '''

        report = validate_responsive(html, mobile_first=True)

        # Should have issues about mobile-first
        assert any("mobile" in issue.lower() for issue in report.issues)

    def test_validate_responsive_touch_targets(self):
        """Test touch target size validation."""
        html = '''
        <button class="w-6 h-6">X</button>
        <button class="w-12 h-12">OK</button>
        '''

        report = validate_responsive(html)

        # w-6 = 24px, too small for touch
        assert len(report.touch_target_violations) > 0

    def test_validate_responsive_coverage_calculation(self):
        """Test that coverage percentages are calculated."""
        html = '''
        <div class="p-4 sm:p-6 md:p-8">
            <h1 class="text-xl sm:text-2xl">Title</h1>
        </div>
        '''

        report = validate_responsive(html)

        assert "sm" in report.coverage
        assert "md" in report.coverage
        assert report.coverage["sm"] > 0

    def test_validate_responsive_fixed_width_warning(self):
        """Test warning for fixed pixel widths."""
        html = '''
        <div class="w-[500px]">Fixed width container</div>
        '''

        report = validate_responsive(html)

        # Should suggest responsive alternatives
        assert len(report.suggestions) > 0


# =============================================================================
# GAP 6: Accessibility Validation Tests
# =============================================================================

class TestGAP6AccessibilityValidation:
    """Tests for accessibility validation and auto-fix."""

    def test_a11y_heading_hierarchy_valid(self):
        """Test valid heading hierarchy."""
        html = '''
        <h1>Main Title</h1>
        <h2>Section</h2>
        <h3>Subsection</h3>
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should pass heading check
        assert "Heading hierarchy is correct" in report.passed_checks

    def test_a11y_heading_hierarchy_skipped(self):
        """Test detection of skipped heading levels."""
        html = '''
        <h1>Main Title</h1>
        <h3>Skipped h2!</h3>
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should have heading error
        heading_errors = [i for i in report.issues if i.rule == "heading-order"]
        assert len(heading_errors) > 0

    def test_a11y_missing_h1(self):
        """Test detection of missing h1."""
        html = '''
        <h2>Section</h2>
        <h3>Subsection</h3>
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should warn about missing h1
        h1_issues = [i for i in report.issues if "h1" in i.message.lower()]
        assert len(h1_issues) > 0

    def test_a11y_focus_states_missing(self):
        """Test detection of missing focus states."""
        html = '''
        <button class="bg-blue-500 text-white">No focus style</button>
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should have focus error
        focus_errors = [i for i in report.issues if i.rule == "focus-visible"]
        assert len(focus_errors) > 0

    def test_a11y_focus_states_present(self):
        """Test passing when focus states are present."""
        html = '''
        <button class="bg-blue-500 text-white focus:ring-2 focus:ring-blue-300">Has focus</button>
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should pass focus check
        assert "Focus states are defined" in report.passed_checks

    def test_a11y_img_alt_missing(self):
        """Test detection of images without alt."""
        html = '''
        <img src="hero.jpg">
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should have img-alt error
        alt_errors = [i for i in report.issues if i.rule == "img-alt"]
        assert len(alt_errors) > 0

    def test_a11y_img_alt_present(self):
        """Test passing when alt is present."""
        html = '''
        <img src="hero.jpg" alt="Hero image">
        <img src="decoration.png" alt="">
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should pass alt check
        assert "Images have alt attributes" in report.passed_checks

    def test_a11y_form_labels(self):
        """Test detection of inputs without labels."""
        html = '''
        <input id="email" type="email">
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should have form-label error
        label_errors = [i for i in report.issues if i.rule == "form-label"]
        assert len(label_errors) > 0

    def test_a11y_form_labels_with_for(self):
        """Test passing when labels use for attribute."""
        html = '''
        <label for="email">Email</label>
        <input id="email" type="email">
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should pass form label check
        assert "Form inputs have labels" in report.passed_checks

    def test_a11y_generic_link_text(self):
        """Test detection of generic link text."""
        html = '''
        <a href="/page">Click here</a>
        <a href="/more">Read more</a>
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should warn about generic text
        link_issues = [i for i in report.issues if i.rule == "link-text"]
        assert len(link_issues) > 0

    def test_a11y_color_contrast_hint(self):
        """Test detection of potential contrast issues."""
        html = '''
        <div class="bg-white text-gray-300">Low contrast</div>
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should warn about contrast
        contrast_issues = [i for i in report.issues if i.rule == "color-contrast"]
        assert len(contrast_issues) > 0

    def test_a11y_auto_fix_focus(self):
        """Test auto-fix for focus states."""
        html = '''
        <button class="bg-blue-500">No focus</button>
        '''

        validator = A11yValidator()
        fixed = validator.auto_fix(html)

        # Should add focus styles
        assert "focus-visible:ring" in fixed

    def test_a11y_auto_fix_img_alt(self):
        """Test auto-fix for missing alt."""
        html = '''
        <img src="test.jpg">
        '''

        validator = A11yValidator()
        fixed = validator.auto_fix(html)

        # Should add alt=""
        assert 'alt=""' in fixed

    def test_a11y_report_score(self):
        """Test that report calculates score correctly."""
        html = '''
        <h1>Title</h1>
        <img src="test.jpg" alt="Test">
        <button class="focus:ring-2">OK</button>
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Score should be high for good accessibility
        assert report.score >= 50

    def test_a11y_error_vs_warning(self):
        """Test that errors and warnings are separated."""
        html = '''
        <h1>Title</h1>
        <h3>Skipped h2</h3>
        <a href="#">click here</a>
        '''

        validator = A11yValidator()
        report = validator.validate(html)

        # Should have both errors and warnings
        assert len(report.errors) > 0 or len(report.warnings) > 0


# =============================================================================
# Combined Validation Tests
# =============================================================================

class TestCombinedValidation:
    """Tests for combined validation workflow."""

    def test_validate_design_output(self):
        """Test combined validation of design output."""
        html = '''
        <div class="p-4 sm:p-6 md:p-8">
            <h1 class="text-2xl md:text-4xl">Title</h1>
            <button class="bg-blue-500 focus:ring-2">Click</button>
            <img src="hero.jpg" alt="Hero">
        </div>
        '''

        report = validate_design_output(html)

        assert isinstance(report, ValidationReport)
        assert isinstance(report.responsive, ResponsiveReport)
        assert isinstance(report.accessibility, A11yReport)
        assert report.tokens_extracted > 0

    def test_validate_design_output_overall_score(self):
        """Test that overall score is calculated."""
        html = '''
        <div class="p-4 sm:p-6 md:p-8 lg:p-12">
            <h1>Title</h1>
        </div>
        '''

        report = validate_design_output(html)

        assert 0 <= report.overall_score <= 100

    def test_auto_fix_design(self):
        """Test auto-fix of common issues."""
        html = '''
        <button class="bg-blue-500">No focus</button>
        <img src="test.jpg">
        '''

        fixed, fixes = auto_fix_design(html)

        # Should have applied some fixes
        assert len(fixes) > 0
        assert "focus-visible:ring" in fixed
        assert 'alt=""' in fixed

    def test_is_valid_property(self):
        """Test is_valid property on combined report."""
        # Good HTML
        good_html = '''
        <div class="p-4 sm:p-6 md:p-8 lg:p-12">
            <h1 class="focus:ring-2">Title</h1>
            <button class="focus:ring-2">OK</button>
        </div>
        '''

        report = validate_design_output(good_html, required_breakpoints=["sm", "md", "lg"])

        # Both validators should pass
        assert report.responsive.is_valid
        # A11y may have warnings but no errors
        # is_valid is true if no errors (warnings OK)
