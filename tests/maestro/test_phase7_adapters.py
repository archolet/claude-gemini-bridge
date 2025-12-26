"""
Phase 7 Tests - Parameter Adapter Tests

Comprehensive tests for MAESTRO parameter adapters:
- adapt_for_design_frontend - Component design parameters
- adapt_for_design_page - Page layout parameters
- adapt_for_design_section - Section design parameters
- adapt_for_refine_frontend - Refinement parameters (requires HTML)
- adapt_for_replace_section - Section replacement parameters (requires HTML)
- adapt_for_design_from_reference - Reference-based design (requires image)
- _ensure_dict - JSON string to dict conversion
"""
import json
import pytest
from dataclasses import dataclass, field
from typing import Any

from gemini_mcp.maestro.execution.adapters import (
    adapt_for_design_frontend,
    adapt_for_design_page,
    adapt_for_design_section,
    adapt_for_refine_frontend,
    adapt_for_replace_section,
    adapt_for_design_from_reference,
    _ensure_dict,
)
from gemini_mcp.maestro.models import ContextData


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def empty_context():
    """Empty context with no previous HTML or project context."""
    return ContextData(
        previous_html=None,
        design_tokens={},
        project_context="",
        content_language="tr",
    )


@pytest.fixture
def context_with_html():
    """Context with previous HTML for refinement/replacement."""
    return ContextData(
        previous_html="<div class='hero'>Existing content</div>",
        design_tokens={"theme": "corporate"},
        project_context="B2B SaaS dashboard",
        content_language="tr",
    )


@pytest.fixture
def context_with_project():
    """Context with project context but no HTML."""
    return ContextData(
        previous_html=None,
        design_tokens={},
        project_context="E-commerce product page",
        content_language="en",
    )


# =============================================================================
# adapt_for_design_frontend TESTS
# =============================================================================


class TestAdaptForDesignFrontend:
    """Tests for adapt_for_design_frontend adapter."""

    def test_basic_component_params(self, empty_context):
        """Should extract basic component parameters."""
        params = {
            "component_type": "button",
            "context": "Primary CTA button",
        }
        result = adapt_for_design_frontend(params, empty_context)

        assert result["component_type"] == "button"
        assert result["design_spec"]["context"] == "Primary CTA button"

    def test_default_component_type(self, empty_context):
        """Should default to 'card' if component_type not provided."""
        result = adapt_for_design_frontend({}, empty_context)
        assert result["component_type"] == "card"

    def test_content_structure_dict(self, empty_context):
        """Should preserve dict content_structure."""
        params = {
            "component_type": "card",
            "content_structure": {"title": "Hello", "description": "World"},
        }
        result = adapt_for_design_frontend(params, empty_context)

        assert result["design_spec"]["content_structure"]["title"] == "Hello"

    def test_content_structure_json_string(self, empty_context):
        """Should parse JSON string content_structure."""
        params = {
            "component_type": "card",
            "content_structure": '{"title": "Hello"}',
        }
        result = adapt_for_design_frontend(params, empty_context)

        assert result["design_spec"]["content_structure"]["title"] == "Hello"

    def test_project_context_from_params(self, empty_context):
        """Should use project_context from params if provided."""
        params = {
            "component_type": "button",
            "project_context": "Fintech app",
        }
        result = adapt_for_design_frontend(params, empty_context)

        assert result["project_context"] == "Fintech app"

    def test_project_context_fallback_to_session(self, context_with_project):
        """Should fall back to session context for project_context."""
        params = {"component_type": "button"}
        result = adapt_for_design_frontend(params, context_with_project)

        assert result["project_context"] == "E-commerce product page"

    def test_content_language(self, empty_context):
        """Should extract content_language parameter."""
        params = {
            "component_type": "button",
            "content_language": "en",
        }
        result = adapt_for_design_frontend(params, empty_context)

        assert result["content_language"] == "en"

    def test_default_content_language(self, empty_context):
        """Should default to Turkish for content_language."""
        result = adapt_for_design_frontend({}, empty_context)
        assert result["content_language"] == "tr"

    def test_style_guide_is_none(self, empty_context):
        """Should set style_guide to None (caller builds from theme)."""
        result = adapt_for_design_frontend({}, empty_context)
        assert result["style_guide"] is None


# =============================================================================
# adapt_for_design_page TESTS
# =============================================================================


class TestAdaptForDesignPage:
    """Tests for adapt_for_design_page adapter."""

    def test_page_component_type_format(self, empty_context):
        """Should format component_type as 'page:{template}'."""
        params = {"template_type": "dashboard"}
        result = adapt_for_design_page(params, empty_context)

        assert result["component_type"] == "page:dashboard"

    def test_default_template_type(self, empty_context):
        """Should default to 'landing_page' template."""
        result = adapt_for_design_page({}, empty_context)
        assert result["component_type"] == "page:landing_page"

    def test_all_template_types(self, empty_context):
        """Should handle all valid template types."""
        templates = [
            "landing_page",
            "dashboard",
            "auth_page",
            "pricing_page",
            "blog_post",
            "product_page",
            "portfolio",
            "documentation",
            "error_page",
            "coming_soon",
        ]
        for template in templates:
            params = {"template_type": template}
            result = adapt_for_design_page(params, empty_context)
            assert result["component_type"] == f"page:{template}"

    def test_design_spec_structure(self, empty_context):
        """Should include design_spec with context and content_structure."""
        params = {
            "template_type": "landing_page",
            "context": "B2B SaaS landing",
            "content_structure": {"hero_title": "Welcome"},
        }
        result = adapt_for_design_page(params, empty_context)

        assert result["design_spec"]["context"] == "B2B SaaS landing"
        assert result["design_spec"]["content_structure"]["hero_title"] == "Welcome"

    def test_project_context_inheritance(self, context_with_project):
        """Should inherit project_context from session if not in params."""
        params = {"template_type": "dashboard"}
        result = adapt_for_design_page(params, context_with_project)

        assert result["project_context"] == "E-commerce product page"


# =============================================================================
# adapt_for_design_section TESTS
# =============================================================================


class TestAdaptForDesignSection:
    """Tests for adapt_for_design_section adapter."""

    def test_basic_section_params(self, empty_context):
        """Should extract basic section parameters."""
        params = {
            "section_type": "hero",
            "context": "Landing page hero",
        }
        result = adapt_for_design_section(params, empty_context)

        assert result["section_type"] == "hero"
        assert result["context"] == "Landing page hero"

    def test_default_section_type(self, empty_context):
        """Should default to 'hero' section type."""
        result = adapt_for_design_section({}, empty_context)
        assert result["section_type"] == "hero"

    def test_all_section_types(self, empty_context):
        """Should handle all valid section types."""
        sections = [
            "hero",
            "features",
            "pricing",
            "testimonials",
            "cta",
            "footer",
            "stats",
            "faq",
            "team",
            "contact",
            "gallery",
            "newsletter",
        ]
        for section in sections:
            params = {"section_type": section}
            result = adapt_for_design_section(params, empty_context)
            assert result["section_type"] == section

    def test_previous_html_from_context(self, context_with_html):
        """Should use previous_html from context for style matching."""
        params = {"section_type": "features"}
        result = adapt_for_design_section(params, context_with_html)

        assert result["previous_html"] == "<div class='hero'>Existing content</div>"

    def test_previous_html_from_params(self, empty_context):
        """Should use previous_html from params if context is empty."""
        params = {
            "section_type": "features",
            "previous_html": "<div>From params</div>",
        }
        result = adapt_for_design_section(params, empty_context)

        assert result["previous_html"] == "<div>From params</div>"

    def test_context_takes_precedence(self, context_with_html):
        """Context previous_html should take precedence over params."""
        params = {
            "section_type": "features",
            "previous_html": "<div>From params</div>",
        }
        result = adapt_for_design_section(params, context_with_html)

        # Context should win
        assert result["previous_html"] == "<div class='hero'>Existing content</div>"

    def test_design_tokens_dict(self, empty_context):
        """Should preserve design_tokens dict."""
        params = {
            "section_type": "hero",
            "design_tokens": {"primary_color": "#3B82F6"},
        }
        result = adapt_for_design_section(params, empty_context)

        assert result["design_tokens"]["primary_color"] == "#3B82F6"

    def test_design_tokens_json_string(self, empty_context):
        """Should parse design_tokens JSON string."""
        params = {
            "section_type": "hero",
            "design_tokens": '{"primary_color": "#3B82F6"}',
        }
        result = adapt_for_design_section(params, empty_context)

        assert result["design_tokens"]["primary_color"] == "#3B82F6"

    def test_theme_parameter(self, empty_context):
        """Should extract theme parameter."""
        params = {
            "section_type": "hero",
            "theme": "cyberpunk",
        }
        result = adapt_for_design_section(params, empty_context)

        assert result["theme"] == "cyberpunk"

    def test_default_theme(self, empty_context):
        """Should default to 'modern-minimal' theme."""
        result = adapt_for_design_section({}, empty_context)
        assert result["theme"] == "modern-minimal"


# =============================================================================
# adapt_for_refine_frontend TESTS
# =============================================================================


class TestAdaptForRefineFrontend:
    """Tests for adapt_for_refine_frontend adapter."""

    def test_requires_previous_html(self, empty_context):
        """Should raise ValueError if no previous_html in context."""
        params = {"modifications": "Make it blue"}

        with pytest.raises(ValueError) as exc_info:
            adapt_for_refine_frontend(params, empty_context)

        assert "previous_html" in str(exc_info.value)
        assert "session context" in str(exc_info.value)

    def test_with_previous_html(self, context_with_html):
        """Should work when previous_html is in context."""
        params = {"modifications": "Make the hero larger"}
        result = adapt_for_refine_frontend(params, context_with_html)

        assert result["previous_html"] == "<div class='hero'>Existing content</div>"
        assert result["modifications"] == "Make the hero larger"

    def test_project_context_from_params(self, context_with_html):
        """Should use project_context from params if provided."""
        params = {
            "modifications": "Improve colors",
            "project_context": "Override context",
        }
        result = adapt_for_refine_frontend(params, context_with_html)

        assert result["project_context"] == "Override context"

    def test_project_context_fallback(self, context_with_html):
        """Should fall back to session project_context."""
        params = {"modifications": "Improve colors"}
        result = adapt_for_refine_frontend(params, context_with_html)

        assert result["project_context"] == "B2B SaaS dashboard"

    def test_empty_modifications(self, context_with_html):
        """Should handle empty modifications string."""
        result = adapt_for_refine_frontend({}, context_with_html)
        assert result["modifications"] == ""


# =============================================================================
# adapt_for_replace_section TESTS
# =============================================================================


class TestAdaptForReplaceSection:
    """Tests for adapt_for_replace_section adapter."""

    def test_requires_page_html(self, empty_context):
        """Should raise ValueError if no page_html in context."""
        params = {
            "section_type": "hero",
            "modifications": "Update hero",
        }

        with pytest.raises(ValueError) as exc_info:
            adapt_for_replace_section(params, empty_context)

        assert "page_html" in str(exc_info.value)
        assert "full page" in str(exc_info.value)

    def test_with_page_html(self, context_with_html):
        """Should work when page HTML is in context."""
        params = {
            "section_type": "features",
            "modifications": "Add more features",
        }
        result = adapt_for_replace_section(params, context_with_html)

        assert result["page_html"] == "<div class='hero'>Existing content</div>"
        assert result["section_type"] == "features"
        assert result["modifications"] == "Add more features"

    def test_preserve_design_tokens_default(self, context_with_html):
        """Should default preserve_design_tokens to True."""
        params = {"section_type": "hero"}
        result = adapt_for_replace_section(params, context_with_html)

        assert result["preserve_design_tokens"] is True

    def test_preserve_design_tokens_false(self, context_with_html):
        """Should allow preserve_design_tokens to be False."""
        params = {
            "section_type": "hero",
            "preserve_design_tokens": False,
        }
        result = adapt_for_replace_section(params, context_with_html)

        assert result["preserve_design_tokens"] is False

    def test_theme_parameter(self, context_with_html):
        """Should extract theme parameter."""
        params = {
            "section_type": "hero",
            "theme": "glassmorphism",
        }
        result = adapt_for_replace_section(params, context_with_html)

        assert result["theme"] == "glassmorphism"

    def test_content_language(self, context_with_html):
        """Should extract content_language parameter."""
        params = {
            "section_type": "hero",
            "content_language": "de",
        }
        result = adapt_for_replace_section(params, context_with_html)

        assert result["content_language"] == "de"

    def test_default_section_type(self, context_with_html):
        """Should default to 'hero' section type."""
        result = adapt_for_replace_section({}, context_with_html)
        assert result["section_type"] == "hero"


# =============================================================================
# adapt_for_design_from_reference TESTS
# =============================================================================


class TestAdaptForDesignFromReference:
    """Tests for adapt_for_design_from_reference adapter."""

    def test_requires_image_path(self, empty_context):
        """Should raise ValueError if no image_path provided."""
        params = {"component_type": "hero"}

        with pytest.raises(ValueError) as exc_info:
            adapt_for_design_from_reference(params, empty_context)

        assert "image_path" in str(exc_info.value)
        assert "reference image" in str(exc_info.value)

    def test_with_image_path(self, empty_context):
        """Should work when image_path is provided."""
        params = {
            "image_path": "/path/to/reference.png",
            "component_type": "hero",
        }
        result = adapt_for_design_from_reference(params, empty_context)

        assert result["image_path"] == "/path/to/reference.png"
        assert result["component_type"] == "hero"

    def test_empty_image_path_raises(self, empty_context):
        """Empty string image_path should raise ValueError."""
        params = {"image_path": ""}

        with pytest.raises(ValueError):
            adapt_for_design_from_reference(params, empty_context)

    def test_instructions_parameter(self, empty_context):
        """Should extract instructions parameter."""
        params = {
            "image_path": "/path/to/ref.png",
            "instructions": "Match the color scheme",
        }
        result = adapt_for_design_from_reference(params, empty_context)

        assert result["instructions"] == "Match the color scheme"

    def test_context_parameter(self, empty_context):
        """Should extract context parameter."""
        params = {
            "image_path": "/path/to/ref.png",
            "context": "E-commerce hero section",
        }
        result = adapt_for_design_from_reference(params, empty_context)

        assert result["context"] == "E-commerce hero section"

    def test_project_context(self, context_with_project):
        """Should extract project_context."""
        params = {"image_path": "/path/to/ref.png"}
        result = adapt_for_design_from_reference(params, context_with_project)

        assert result["project_context"] == "E-commerce product page"

    def test_content_language(self, empty_context):
        """Should extract content_language."""
        params = {
            "image_path": "/path/to/ref.png",
            "content_language": "en",
        }
        result = adapt_for_design_from_reference(params, empty_context)

        assert result["content_language"] == "en"

    def test_empty_component_type_default(self, empty_context):
        """Should allow empty component_type (auto-detect mode)."""
        params = {"image_path": "/path/to/ref.png"}
        result = adapt_for_design_from_reference(params, empty_context)

        assert result["component_type"] == ""


# =============================================================================
# _ensure_dict HELPER TESTS
# =============================================================================


class TestEnsureDict:
    """Tests for _ensure_dict helper function."""

    def test_dict_passthrough(self):
        """Dict input should pass through unchanged."""
        input_dict = {"key": "value", "nested": {"a": 1}}
        result = _ensure_dict(input_dict)

        assert result == input_dict
        assert result is input_dict  # Same object

    def test_json_string_parsing(self):
        """Valid JSON string should be parsed to dict."""
        json_str = '{"key": "value", "number": 42}'
        result = _ensure_dict(json_str)

        assert result == {"key": "value", "number": 42}

    def test_nested_json_string(self):
        """Nested JSON string should be parsed correctly."""
        json_str = '{"outer": {"inner": "value"}}'
        result = _ensure_dict(json_str)

        assert result["outer"]["inner"] == "value"

    def test_invalid_json_returns_empty(self):
        """Invalid JSON string should return empty dict."""
        result = _ensure_dict("not valid json")
        assert result == {}

    def test_json_array_returns_empty(self):
        """JSON array should return empty dict (not a dict)."""
        result = _ensure_dict('[1, 2, 3]')
        assert result == {}

    def test_none_returns_empty(self):
        """None should return empty dict."""
        result = _ensure_dict(None)
        assert result == {}

    def test_number_returns_empty(self):
        """Number should return empty dict."""
        result = _ensure_dict(42)
        assert result == {}

    def test_list_returns_empty(self):
        """List should return empty dict."""
        result = _ensure_dict([1, 2, 3])
        assert result == {}

    def test_empty_string_returns_empty(self):
        """Empty string should return empty dict."""
        result = _ensure_dict("")
        assert result == {}

    def test_empty_json_object(self):
        """Empty JSON object string should return empty dict."""
        result = _ensure_dict("{}")
        assert result == {}

    def test_json_with_unicode(self):
        """JSON with Unicode characters should parse correctly."""
        json_str = '{"title": "Türkçe içerik", "emoji": "🚀"}'
        result = _ensure_dict(json_str)

        assert result["title"] == "Türkçe içerik"
        assert result["emoji"] == "🚀"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestAdapterIntegration:
    """Integration tests for adapter functions."""

    def test_all_adapters_return_dict(self, context_with_html):
        """All adapters should return dict type."""
        adapters = [
            (adapt_for_design_frontend, {}),
            (adapt_for_design_page, {}),
            (adapt_for_design_section, {}),
            (adapt_for_refine_frontend, {}),
            (adapt_for_replace_section, {}),
            (adapt_for_design_from_reference, {"image_path": "/test.png"}),
        ]

        for adapter, extra_params in adapters:
            result = adapter(extra_params, context_with_html)
            assert isinstance(result, dict)

    def test_adapters_preserve_extra_params(self, empty_context):
        """Adapters should not lose known parameters."""
        params = {
            "component_type": "button",
            "content_language": "en",
            "project_context": "Test project",
        }
        result = adapt_for_design_frontend(params, empty_context)

        assert result["component_type"] == "button"
        assert result["content_language"] == "en"
        assert result["project_context"] == "Test project"

    def test_context_data_to_dict_round_trip(self):
        """ContextData should serialize and deserialize correctly."""
        original = ContextData(
            previous_html="<div>Test</div>",
            design_tokens={"theme": "corporate"},
            project_context="Test project",
            content_language="en",
        )

        serialized = original.to_dict()
        restored = ContextData.from_dict(serialized)

        assert restored.previous_html == original.previous_html
        assert restored.design_tokens == original.design_tokens
        assert restored.project_context == original.project_context
        assert restored.content_language == original.content_language


class TestEdgeCases:
    """Edge case tests for adapters."""

    def test_very_long_html(self, empty_context):
        """Should handle very long HTML content."""
        long_html = "<div>" + "x" * 100000 + "</div>"
        context = ContextData(previous_html=long_html)

        result = adapt_for_refine_frontend({}, context)
        assert len(result["previous_html"]) == len(long_html)

    def test_special_characters_in_content(self, empty_context):
        """Should handle special characters in content."""
        params = {
            "component_type": "card",
            "content_structure": {
                "title": "Test <script>alert('xss')</script>",
                "emoji": "🎉🚀✨",
            },
        }
        result = adapt_for_design_frontend(params, empty_context)

        assert "<script>" in result["design_spec"]["content_structure"]["title"]
        assert "🎉" in result["design_spec"]["content_structure"]["emoji"]

    def test_deeply_nested_content_structure(self, empty_context):
        """Should handle deeply nested content structures."""
        params = {
            "component_type": "card",
            "content_structure": {
                "level1": {
                    "level2": {
                        "level3": {
                            "value": "deep"
                        }
                    }
                }
            },
        }
        result = adapt_for_design_frontend(params, empty_context)

        assert (
            result["design_spec"]["content_structure"]["level1"]["level2"]["level3"]["value"]
            == "deep"
        )

    def test_whitespace_only_project_context(self, empty_context):
        """Should handle whitespace-only project context."""
        params = {
            "component_type": "button",
            "project_context": "   ",
        }
        result = adapt_for_design_frontend(params, empty_context)

        assert result["project_context"] == "   "  # Preserved as-is
