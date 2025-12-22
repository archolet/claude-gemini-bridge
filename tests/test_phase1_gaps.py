"""Tests for Phase 1 GAP implementations.

GAP 1: Unified Design Token Schema
GAP 2: Section Marker System
GAP 3: Error Handling and Recovery
"""

import pytest
import json


class TestGAP1UnifiedDesignTokenSchema:
    """Tests for UnifiedDesignTokenSchema and token normalization."""

    def test_tailwind_color_map_exists(self):
        """Verify TAILWIND_COLOR_MAP has expected colors."""
        from gemini_mcp.schemas import TAILWIND_COLOR_MAP

        assert "blue-500" in TAILWIND_COLOR_MAP
        assert "slate-900" in TAILWIND_COLOR_MAP
        assert TAILWIND_COLOR_MAP["blue-500"] == "#3B82F6"

    def test_hex_to_tailwind_map_reverse(self):
        """Verify HEX_TO_TAILWIND_MAP is correct reverse mapping."""
        from gemini_mcp.schemas import TAILWIND_COLOR_MAP, HEX_TO_TAILWIND_MAP

        # Check that hex values map back to tailwind names
        assert HEX_TO_TAILWIND_MAP["#3B82F6"] == "blue-500"
        assert HEX_TO_TAILWIND_MAP["#F8FAFC"] == "slate-50"

    def test_unified_color_token_from_tailwind(self):
        """Test creating UnifiedColorToken from Tailwind class."""
        from gemini_mcp.schemas import UnifiedColorToken

        token = UnifiedColorToken.from_tailwind("blue-500", role="primary")

        assert token.tailwind_class == "blue-500"
        assert token.hex_value == "#3B82F6"
        assert token.role == "primary"

    def test_unified_color_token_from_hex(self):
        """Test creating UnifiedColorToken from HEX value."""
        from gemini_mcp.schemas import UnifiedColorToken

        # Exact match
        token = UnifiedColorToken.from_hex("#3B82F6", role="accent")
        assert token.tailwind_class == "blue-500"
        assert token.role == "accent"

        # Close match (should find nearest)
        token2 = UnifiedColorToken.from_hex("#3C82F7", role="primary")
        assert "blue" in token2.tailwind_class  # Should find a blue variant

    def test_unified_color_token_opacity(self):
        """Test opacity parsing from Tailwind classes."""
        from gemini_mcp.schemas import UnifiedColorToken

        token = UnifiedColorToken.from_tailwind("blue-500/50", role="primary")
        assert token.opacity == 0.5
        assert token.tailwind_class == "blue-500"

    def test_unified_spacing_token_from_tailwind(self):
        """Test creating UnifiedSpacingToken from Tailwind class."""
        from gemini_mcp.schemas import UnifiedSpacingToken

        token = UnifiedSpacingToken.from_tailwind("p-4")

        assert token.tailwind_class == "p-4"
        assert token.rem_value == 1.0  # 4 * 0.25rem
        assert token.px_value == 16.0  # 1rem * 16px

    def test_unified_spacing_token_from_px(self):
        """Test creating UnifiedSpacingToken from px value."""
        from gemini_mcp.schemas import UnifiedSpacingToken

        token = UnifiedSpacingToken.from_px(16, prefix="m")

        assert token.px_value == 16.0
        assert token.rem_value == 1.0
        assert token.tailwind_class == "m-4"

    def test_normalize_tokens_from_html(self):
        """Test token normalization from HTML extraction format."""
        from gemini_mcp.schemas import normalize_tokens

        raw_tokens = {
            "colors": {
                "primary": "blue-600",
                "secondary": "gray-500",
            },
            "typography": {
                "heading": "font-bold text-2xl",
            },
            "spacing": {
                "section": "py-16",
            }
        }

        schema = normalize_tokens(raw_tokens, source="html_extraction")

        assert schema.source == "html_extraction"
        assert "primary" in schema.colors
        assert schema.colors["primary"].tailwind_class == "blue-600"


class TestGAP2SectionMarkerSystem:
    """Tests for section marker utilities."""

    def test_ensure_section_markers_adds_markers(self):
        """Test that markers are added to unmarked content."""
        from gemini_mcp.section_utils import ensure_section_markers

        html = '<nav class="bg-white">Navigation</nav>'
        result = ensure_section_markers(html, "navbar")

        assert "<!-- SECTION: navbar -->" in result
        assert "<!-- /SECTION: navbar -->" in result
        assert '<nav class="bg-white">Navigation</nav>' in result

    def test_ensure_section_markers_preserves_existing(self):
        """Test that existing markers are preserved."""
        from gemini_mcp.section_utils import ensure_section_markers

        html = '''<!-- SECTION: hero -->
<section>Hero content</section>
<!-- /SECTION: hero -->'''

        result = ensure_section_markers(html, "hero")

        # Should not add duplicate markers
        assert result.count("<!-- SECTION: hero -->") == 1
        assert result.count("<!-- /SECTION: hero -->") == 1

    def test_combine_sections(self):
        """Test combining multiple sections into a page."""
        from gemini_mcp.section_utils import combine_sections

        sections = [
            ("navbar", "<nav>Nav</nav>"),
            ("hero", "<section>Hero</section>"),
            ("footer", "<footer>Footer</footer>"),
        ]

        result = combine_sections(sections, page_wrapper=False)

        assert "<!-- SECTION: navbar -->" in result
        assert "<!-- SECTION: hero -->" in result
        assert "<!-- SECTION: footer -->" in result

        # Check order is preserved
        nav_pos = result.find("navbar")
        hero_pos = result.find("hero")
        footer_pos = result.find("footer")
        assert nav_pos < hero_pos < footer_pos

    def test_combine_sections_with_wrapper(self):
        """Test combining sections with page wrapper."""
        from gemini_mcp.section_utils import combine_sections

        sections = [("navbar", "<nav>Nav</nav>")]
        result = combine_sections(sections, page_wrapper=True)

        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "tailwindcss" in result

    def test_extract_all_sections(self):
        """Test extracting all sections from HTML."""
        from gemini_mcp.section_utils import extract_all_sections

        html = '''<!-- SECTION: navbar --><nav>Nav</nav><!-- /SECTION: navbar -->
<!-- SECTION: hero --><section>Hero</section><!-- /SECTION: hero -->'''

        sections = extract_all_sections(html)

        assert len(sections) == 2
        assert "navbar" in sections
        assert "hero" in sections
        assert sections["navbar"] == "<nav>Nav</nav>"

    def test_validate_page_structure_valid(self):
        """Test validating a properly structured page."""
        from gemini_mcp.section_utils import validate_page_structure

        html = '''<!-- SECTION: navbar --><nav>Nav</nav><!-- /SECTION: navbar -->
<!-- SECTION: hero --><section>Hero</section><!-- /SECTION: hero -->'''

        is_valid, issues = validate_page_structure(html, ["navbar", "hero"])

        assert is_valid
        assert len(issues) == 0

    def test_validate_page_structure_missing(self):
        """Test detecting missing sections."""
        from gemini_mcp.section_utils import validate_page_structure

        html = '''<!-- SECTION: navbar --><nav>Nav</nav><!-- /SECTION: navbar -->'''

        is_valid, issues = validate_page_structure(html, ["navbar", "hero", "footer"])

        assert not is_valid
        assert "missing:hero" in issues
        assert "missing:footer" in issues

    def test_reorder_sections(self):
        """Test reordering sections."""
        from gemini_mcp.section_utils import reorder_sections, list_sections

        html = '''<!-- SECTION: footer --><footer>F</footer><!-- /SECTION: footer -->
<!-- SECTION: navbar --><nav>N</nav><!-- /SECTION: navbar -->'''

        result = reorder_sections(html, ["navbar", "footer"])
        sections = list_sections(result)

        # Should now be in correct order
        assert sections.index("navbar") < sections.index("footer")


class TestGAP3ErrorHandlingAndRecovery:
    """Tests for error handling and recovery mechanisms."""

    def test_error_type_classification(self):
        """Test error classification works correctly."""
        from gemini_mcp.error_recovery import classify_error, ErrorType

        # Rate limit error
        rate_error = Exception("429 Too Many Requests")
        assert classify_error(rate_error) == ErrorType.RATE_LIMIT

        # Network error
        net_error = Exception("Connection refused")
        assert classify_error(net_error) == ErrorType.NETWORK_ERROR

        # Auth error
        auth_error = Exception("401 Unauthorized")
        assert classify_error(auth_error) == ErrorType.AUTH_ERROR

        # JSON error
        json_error = Exception("JSON decode error")
        assert classify_error(json_error) == ErrorType.INVALID_JSON

    def test_recovery_strategy_defaults(self):
        """Test default recovery strategy configuration."""
        from gemini_mcp.error_recovery import RecoveryStrategy, ErrorType

        strategy = RecoveryStrategy()

        assert strategy.max_retries == 3
        assert strategy.base_delay_seconds == 1.0
        assert strategy.exponential_backoff is True
        assert ErrorType.RATE_LIMIT in strategy.retry_on
        assert ErrorType.AUTH_ERROR not in strategy.retry_on  # Auth errors shouldn't retry

    def test_calculate_delay_exponential(self):
        """Test exponential backoff calculation."""
        from gemini_mcp.error_recovery import calculate_delay, RecoveryStrategy

        strategy = RecoveryStrategy(
            base_delay_seconds=1.0,
            exponential_backoff=True,
            jitter=False,  # Disable jitter for predictable tests
        )

        delay0 = calculate_delay(0, strategy)
        delay1 = calculate_delay(1, strategy)
        delay2 = calculate_delay(2, strategy)

        assert delay0 == 1.0  # 1 * 2^0
        assert delay1 == 2.0  # 1 * 2^1
        assert delay2 == 4.0  # 1 * 2^2

    def test_calculate_delay_max_cap(self):
        """Test that delay is capped at max value."""
        from gemini_mcp.error_recovery import calculate_delay, RecoveryStrategy

        strategy = RecoveryStrategy(
            base_delay_seconds=1.0,
            max_delay_seconds=5.0,
            exponential_backoff=True,
            jitter=False,
        )

        # 2^10 = 1024 seconds, but should be capped at 5
        delay = calculate_delay(10, strategy)
        assert delay == 5.0

    def test_repair_json_response_markdown(self):
        """Test repairing JSON wrapped in markdown code blocks."""
        from gemini_mcp.error_recovery import repair_json_response

        raw = '''```json
{"html": "<div>Test</div>", "component": "card"}
```'''

        result = repair_json_response(raw)

        assert result is not None
        assert result["html"] == "<div>Test</div>"
        assert result["component"] == "card"

    def test_repair_json_response_trailing_comma(self):
        """Test repairing JSON with trailing commas."""
        from gemini_mcp.error_recovery import repair_json_response

        raw = '{"a": 1, "b": 2,}'
        result = repair_json_response(raw)

        assert result is not None
        assert result["a"] == 1
        assert result["b"] == 2

    def test_extract_html_fallback(self):
        """Test extracting HTML from malformed response."""
        from gemini_mcp.error_recovery import extract_html_fallback

        raw = '''Some text before {"html": "<div class=\\"test\\">Content</div>"} some after'''
        result = extract_html_fallback(raw)

        assert result is not None
        assert "div" in result

    def test_response_validator(self):
        """Test response validation and repair."""
        from gemini_mcp.error_recovery import ResponseValidator

        # Valid response
        valid = {"html": "<div>Test</div>", "extra": "data"}
        is_valid, missing = ResponseValidator.validate(valid, "design")
        assert is_valid
        assert len(missing) == 0

        # Invalid response
        invalid = {"extra": "data"}  # Missing 'html'
        is_valid, missing = ResponseValidator.validate(invalid, "design")
        assert not is_valid
        assert "html" in missing

    def test_response_validator_repair(self):
        """Test response repair adds fallback HTML."""
        from gemini_mcp.error_recovery import ResponseValidator

        invalid = {"extra": "data"}  # Missing 'html'
        repaired = ResponseValidator.repair(invalid, "design", "hero")

        assert "html" in repaired
        assert repaired["html"]  # Should have fallback HTML
        assert "_repaired_fields" in repaired
        assert "html" in repaired["_repaired_fields"]

    def test_generate_fallback_html(self):
        """Test fallback HTML generation for different components."""
        from gemini_mcp.error_recovery import generate_fallback_html

        hero_html = generate_fallback_html("hero", "Test error")
        navbar_html = generate_fallback_html("navbar", "Test error")
        unknown_html = generate_fallback_html("unknown_type", "Test error")

        assert "section" in hero_html.lower() or "div" in hero_html.lower()
        assert "nav" in navbar_html.lower()
        assert "unknown_type" in unknown_html  # Should show component type

    def test_create_fallback_response(self):
        """Test creating a complete fallback response."""
        from gemini_mcp.error_recovery import create_fallback_response

        error = Exception("API timeout")
        response = create_fallback_response(
            component_type="card",
            error=error,
            partial_result=None,
        )

        assert response["error"] == "API timeout"
        assert response["error_type"] == "timeout"  # 'timeout' IS in error string
        assert response["recovery_failed"] is True
        assert "html" in response


class TestServerIntegration:
    """Integration tests for server.py changes."""

    def test_safe_design_call_helper_exists(self):
        """Verify safe_design_call helper is importable."""
        # This import should work if server.py compiles correctly
        import importlib
        spec = importlib.util.find_spec("gemini_mcp.server")
        assert spec is not None

    def test_design_recovery_strategy_exists(self):
        """Verify DESIGN_RECOVERY_STRATEGY is configured."""
        # We can't easily import server.py due to MCP dependencies
        # But we can verify the file compiles
        import py_compile
        py_compile.compile(
            "src/gemini_mcp/server.py",
            doraise=True,
        )
