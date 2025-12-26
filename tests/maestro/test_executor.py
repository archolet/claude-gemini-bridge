"""
Tests for MAESTRO Phase 4: ToolExecutor and Adapters.

Tests cover:
- ToolExecutor mode dispatch
- Parameter adapters for all 6 modes
- Error handling for missing parameters
- Context injection
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from gemini_mcp.maestro.execution import (
    ToolExecutor,
    adapt_for_design_frontend,
    adapt_for_design_page,
    adapt_for_design_section,
    adapt_for_refine_frontend,
    adapt_for_replace_section,
    adapt_for_design_from_reference,
)
from gemini_mcp.maestro.models import ContextData, MaestroDecision


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_client():
    """Create mock GeminiClient with all design methods."""
    client = MagicMock()
    client.design_component = AsyncMock(return_value={
        "html": "<div class='test-component'>Test</div>",
        "component_id": "comp_123",
    })
    client.design_section = AsyncMock(return_value={
        "html": "<section class='test-section'>Test</section>",
        "section_type": "hero",
    })
    client.refine_component = AsyncMock(return_value={
        "html": "<div class='refined'>Refined</div>",
        "changes_made": ["Updated color"],
    })
    client.design_from_reference = AsyncMock(return_value={
        "html": "<div class='from-ref'>Reference</div>",
        "design_tokens": {},
    })
    return client


@pytest.fixture
def executor(mock_client):
    """Create ToolExecutor with mock client."""
    return ToolExecutor(mock_client)


@pytest.fixture
def context():
    """Create context with previous HTML."""
    return ContextData(
        previous_html="<div class='existing'>Existing HTML</div>",
        project_context="Test project context",
    )


@pytest.fixture
def empty_context():
    """Create context without previous HTML."""
    return ContextData()


# =============================================================================
# ADAPTER TESTS
# =============================================================================


class TestAdaptForDesignFrontend:
    """Tests for adapt_for_design_frontend adapter."""

    def test_basic_params(self, context):
        """Test basic parameter transformation."""
        params = {"component_type": "button", "context": "CTA button"}
        result = adapt_for_design_frontend(params, context)

        assert result["component_type"] == "button"
        assert result["design_spec"]["context"] == "CTA button"
        assert result["project_context"] == "Test project context"
        assert result["content_language"] == "tr"

    def test_defaults(self, empty_context):
        """Test default values when params empty."""
        result = adapt_for_design_frontend({}, empty_context)

        assert result["component_type"] == "card"
        assert result["content_language"] == "tr"
        assert result["project_context"] == ""

    def test_content_structure_dict(self, context):
        """Test content_structure as dict."""
        params = {
            "component_type": "card",
            "content_structure": {"title": "Test", "body": "Content"},
        }
        result = adapt_for_design_frontend(params, context)

        assert result["design_spec"]["content_structure"]["title"] == "Test"

    def test_content_structure_json(self, context):
        """Test content_structure as JSON string."""
        params = {
            "component_type": "card",
            "content_structure": '{"title": "Test"}',
        }
        result = adapt_for_design_frontend(params, context)

        assert result["design_spec"]["content_structure"]["title"] == "Test"


class TestAdaptForDesignPage:
    """Tests for adapt_for_design_page adapter."""

    def test_template_type_prefix(self, context):
        """Test template type gets page: prefix."""
        params = {"template_type": "dashboard"}
        result = adapt_for_design_page(params, context)

        assert result["component_type"] == "page:dashboard"

    def test_default_template(self, context):
        """Test default template is landing_page."""
        result = adapt_for_design_page({}, context)

        assert result["component_type"] == "page:landing_page"


class TestAdaptForDesignSection:
    """Tests for adapt_for_design_section adapter."""

    def test_uses_context_html(self, context):
        """Test previous_html comes from context."""
        params = {"section_type": "hero"}
        result = adapt_for_design_section(params, context)

        assert result["previous_html"] == "<div class='existing'>Existing HTML</div>"
        assert result["section_type"] == "hero"

    def test_param_html_fallback(self, empty_context):
        """Test falls back to param HTML when context empty."""
        params = {
            "section_type": "features",
            "previous_html": "<div>Param HTML</div>",
        }
        result = adapt_for_design_section(params, empty_context)

        assert result["previous_html"] == "<div>Param HTML</div>"


class TestAdaptForRefineFrontend:
    """Tests for adapt_for_refine_frontend adapter."""

    def test_requires_previous_html(self, empty_context):
        """Test raises error without previous_html."""
        with pytest.raises(ValueError, match="requires previous_html"):
            adapt_for_refine_frontend({}, empty_context)

    def test_uses_context_html(self, context):
        """Test uses previous_html from context."""
        params = {"modifications": "Make it blue"}
        result = adapt_for_refine_frontend(params, context)

        assert result["previous_html"] == "<div class='existing'>Existing HTML</div>"
        assert result["modifications"] == "Make it blue"


class TestAdaptForReplaceSection:
    """Tests for adapt_for_replace_section adapter."""

    def test_requires_page_html(self, empty_context):
        """Test raises error without page_html in context."""
        with pytest.raises(ValueError, match="requires page_html"):
            adapt_for_replace_section({}, empty_context)

    def test_uses_context_as_page_html(self, context):
        """Test context.previous_html used as page_html."""
        params = {"section_type": "navbar", "modifications": "Add dropdown"}
        result = adapt_for_replace_section(params, context)

        assert result["page_html"] == "<div class='existing'>Existing HTML</div>"
        assert result["section_type"] == "navbar"


class TestAdaptForDesignFromReference:
    """Tests for adapt_for_design_from_reference adapter."""

    def test_requires_image_path(self, context):
        """Test raises error without image_path."""
        with pytest.raises(ValueError, match="requires image_path"):
            adapt_for_design_from_reference({}, context)

    def test_with_image_path(self, context):
        """Test with valid image_path."""
        params = {
            "image_path": "/path/to/reference.png",
            "component_type": "hero",
            "instructions": "Similar style",
        }
        result = adapt_for_design_from_reference(params, context)

        assert result["image_path"] == "/path/to/reference.png"
        assert result["component_type"] == "hero"
        assert result["instructions"] == "Similar style"


# =============================================================================
# TOOL EXECUTOR TESTS
# =============================================================================


class TestToolExecutorModes:
    """Tests for ToolExecutor mode dispatch."""

    @pytest.mark.asyncio
    async def test_design_frontend_mode(self, executor, context):
        """Test design_frontend mode execution."""
        decision = MaestroDecision(
            mode="design_frontend",
            parameters={"component_type": "button", "theme": "modern-minimal"},
        )
        result = await executor.execute(decision, context)

        assert result["mode"] == "design_frontend"
        assert "html" in result

    @pytest.mark.asyncio
    async def test_design_page_mode(self, executor, context):
        """Test design_page mode execution."""
        decision = MaestroDecision(
            mode="design_page",
            parameters={"template_type": "landing_page"},
        )
        result = await executor.execute(decision, context)

        assert result["mode"] == "design_page"

    @pytest.mark.asyncio
    async def test_design_section_mode(self, executor, context):
        """Test design_section mode execution."""
        decision = MaestroDecision(
            mode="design_section",
            parameters={"section_type": "hero"},
        )
        result = await executor.execute(decision, context)

        assert result["mode"] == "design_section"

    @pytest.mark.asyncio
    async def test_refine_frontend_mode(self, executor, context):
        """Test refine_frontend mode execution."""
        decision = MaestroDecision(
            mode="refine_frontend",
            parameters={"modifications": "Make it blue"},
        )
        result = await executor.execute(decision, context)

        assert result["mode"] == "refine_frontend"

    @pytest.mark.asyncio
    async def test_design_from_reference_mode(self, executor, context):
        """Test design_from_reference mode execution."""
        decision = MaestroDecision(
            mode="design_from_reference",
            parameters={"image_path": "/path/to/ref.png"},
        )
        result = await executor.execute(decision, context)

        assert result["mode"] == "design_from_reference"


class TestToolExecutorErrors:
    """Tests for ToolExecutor error handling."""

    @pytest.mark.asyncio
    async def test_unknown_mode(self, executor, context):
        """Test unknown mode returns error dict."""
        decision = MaestroDecision(
            mode="unknown_mode",
            parameters={},
        )
        result = await executor.execute(decision, context)

        assert result["status"] == "failed"
        assert "Unknown mode" in result["error"]
        assert result["mode"] == "unknown_mode"

    @pytest.mark.asyncio
    async def test_refine_without_html(self, executor, empty_context):
        """Test refine mode fails without previous_html."""
        decision = MaestroDecision(
            mode="refine_frontend",
            parameters={"modifications": "Update"},
        )
        result = await executor.execute(decision, empty_context)

        assert result["status"] == "failed"
        assert "previous_html" in result["error"]

    @pytest.mark.asyncio
    async def test_reference_without_image(self, executor, context):
        """Test reference mode fails without image_path."""
        decision = MaestroDecision(
            mode="design_from_reference",
            parameters={},
        )
        result = await executor.execute(decision, context)

        assert result["status"] == "failed"
        assert "image_path" in result["error"]


class TestToolExecutorHelpers:
    """Tests for ToolExecutor helper methods."""

    def test_extract_section(self, executor):
        """Test section extraction from HTML."""
        html = """
        <!-- SECTION: navbar -->
        <nav>Navigation</nav>
        <!-- /SECTION: navbar -->
        <!-- SECTION: hero -->
        <section>Hero content</section>
        <!-- /SECTION: hero -->
        """
        result = executor._extract_section(html, "hero")

        assert "<section>Hero content</section>" in result

    def test_extract_section_not_found(self, executor):
        """Test section extraction returns empty when not found."""
        html = "<div>No sections</div>"
        result = executor._extract_section(html, "hero")

        assert result == ""

    def test_replace_section_html(self, executor):
        """Test section replacement in HTML."""
        html = """<!-- SECTION: hero --><old>Old</old><!-- /SECTION: hero -->"""
        new_section = "<new>New</new>"
        result = executor._replace_section_html(html, "hero", new_section)

        assert "<new>New</new>" in result
        assert "<old>Old</old>" not in result

    def test_list_sections(self, executor):
        """Test listing all sections in HTML."""
        html = """
        <!-- SECTION: navbar -->nav<!-- /SECTION: navbar -->
        <!-- SECTION: hero -->hero<!-- /SECTION: hero -->
        <!-- SECTION: footer -->footer<!-- /SECTION: footer -->
        """
        result = executor._list_sections(html)

        assert "navbar" in result
        assert "hero" in result
        assert "footer" in result


class TestToolExecutorModeHandlers:
    """Tests for all MODE_HANDLERS are present."""

    def test_all_modes_have_handlers(self):
        """Test all modes have corresponding handler methods."""
        for mode, handler_name in ToolExecutor.MODE_HANDLERS.items():
            assert hasattr(ToolExecutor, handler_name), (
                f"Missing handler {handler_name} for mode {mode}"
            )

    def test_mode_count(self):
        """Test exactly 6 modes are defined."""
        assert len(ToolExecutor.MODE_HANDLERS) == 6

    def test_expected_modes(self):
        """Test all expected modes are present."""
        expected_modes = {
            "design_frontend",
            "design_page",
            "design_section",
            "refine_frontend",
            "replace_section_in_page",
            "design_from_reference",
        }
        actual_modes = set(ToolExecutor.MODE_HANDLERS.keys())
        assert actual_modes == expected_modes
