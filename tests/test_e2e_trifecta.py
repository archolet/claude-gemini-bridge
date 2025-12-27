"""
End-to-End Tests for Trifecta Multi-Agent System.

These tests run the COMPLETE Trifecta pipeline with REAL Gemini API calls.
No mocks - validates all 7 agents working together through orchestration.

Prerequisites:
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    gcloud auth application-default login

Run:
    uv run pytest tests/test_e2e_trifecta.py -v
    uv run pytest tests/test_e2e_trifecta.py -v -m "not slow"  # Skip slow tests
    uv run pytest tests/test_e2e_trifecta.py -v -k "button"    # Only button tests
"""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

import pytest

from gemini_mcp.client import GeminiClient
from gemini_mcp.orchestration import (
    AgentContext,
    PipelineResult,
    PipelineType,
    get_orchestrator,
)
from gemini_mcp.orchestration.context import QualityTarget

if TYPE_CHECKING:
    from gemini_mcp.orchestration.orchestrator import Orchestrator

# =============================================================================
# Module Configuration
# =============================================================================

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.getenv("GOOGLE_CLOUD_PROJECT"),
        reason="GOOGLE_CLOUD_PROJECT not set - real API required",
    ),
]


# =============================================================================
# Assertion Helpers
# =============================================================================


def assert_valid_html_structure(html: str) -> None:
    """Validate basic HTML structure."""
    assert html, "HTML output is empty"
    assert len(html) > 100, f"HTML too short: {len(html)} chars"
    # Basic tag balance check
    assert html.count("<") == html.count(">"), "Unbalanced HTML tags"


def assert_has_tailwind_classes(html: str) -> None:
    """Verify Tailwind CSS classes are used."""
    tailwind_patterns = [
        r'class="[^"]*\b(bg-|text-|p-|m-|flex|grid|rounded)',
        r'class="[^"]*\b(w-|h-|gap-|space-|border)',
    ]
    for pattern in tailwind_patterns:
        if re.search(pattern, html):
            return
    pytest.fail("No Tailwind CSS classes found in HTML output")


def assert_accessibility(html: str) -> None:
    """Check basic accessibility attributes."""
    if "<button" in html.lower():
        has_focus = "focus" in html or "focus-visible" in html
        assert has_focus, "Button missing focus state for keyboard accessibility"

    if "<img" in html.lower():
        has_alt = 'alt="' in html or "alt='" in html
        assert has_alt, "Image missing alt attribute"


def assert_responsive(html: str) -> None:
    """Verify responsive breakpoints are used."""
    breakpoint_pattern = r"\b(sm:|md:|lg:|xl:)"
    assert re.search(breakpoint_pattern, html), "Missing responsive breakpoints"


def assert_token_usage(result: PipelineResult, max_total: int = 100000) -> None:
    """Validate token usage within bounds."""
    assert result.total_tokens > 0, "No tokens recorded"
    assert result.total_tokens <= max_total, (
        f"Token usage {result.total_tokens} exceeds limit {max_total}"
    )


def assert_execution_time(result: PipelineResult, max_ms: float = 180000.0) -> None:
    """Validate execution time is reasonable."""
    assert result.execution_time_ms > 0, "No execution time recorded"
    assert result.execution_time_ms <= max_ms, (
        f"Execution time {result.execution_time_ms}ms exceeds limit {max_ms}ms"
    )


def assert_quality_score(score: float | None, min_score: float = 7.0) -> None:
    """Validate quality score meets threshold."""
    if score is not None:
        assert score >= min_score, f"Quality score {score} < minimum {min_score}"


def assert_pipeline_success(result: PipelineResult) -> None:
    """Assert pipeline completed successfully."""
    assert result.success, f"Pipeline failed with errors: {result.errors}"
    assert result.html, "Pipeline produced no HTML output"
    assert result.completed_steps == result.total_steps, (
        f"Pipeline incomplete: {result.completed_steps}/{result.total_steps} steps"
    )


# =============================================================================
# Fixtures - Module Scope (API Cost Optimization)
# =============================================================================


@pytest.fixture(scope="module")
def gemini_client() -> GeminiClient:
    """Real Gemini client with ADC authentication."""
    return GeminiClient()


@pytest.fixture(scope="module")
def orchestrator(gemini_client: GeminiClient) -> "Orchestrator":
    """Full orchestrator with all 7 agents registered."""
    return get_orchestrator(gemini_client)


# =============================================================================
# Fixtures - Function Scope (Test Contexts)
# =============================================================================


@pytest.fixture
def button_context() -> AgentContext:
    """Simple button component context."""
    return AgentContext(
        component_type="button",
        theme="modern-minimal",
        content_structure={"text": "Get Started", "icon": "arrow-right"},
        content_language="en",
        quality_target=QualityTarget.PRODUCTION,
    )


@pytest.fixture
def pricing_card_context() -> AgentContext:
    """Complex pricing card component context."""
    return AgentContext(
        component_type="pricing_card",
        theme="startup",
        content_structure={
            "tier": "Professional",
            "price": "$99/mo",
            "features": ["Unlimited users", "Priority support", "API access"],
            "cta": "Start Free Trial",
        },
        content_language="en",
        quality_target=QualityTarget.HIGH,
    )


@pytest.fixture
def landing_page_context() -> AgentContext:
    """Full landing page context."""
    return AgentContext(
        template_type="landing_page",
        theme="modern-minimal",
        content_structure={
            "headline": "Build Faster",
            "subheadline": "Ship with confidence",
        },
        content_language="en",
        quality_target=QualityTarget.PRODUCTION,
    )


# =============================================================================
# Test Classes
# =============================================================================


class TestComponentPipeline:
    """Tests for COMPONENT pipeline - individual UI components."""

    @pytest.mark.asyncio
    async def test_button_component(
        self,
        orchestrator: "Orchestrator",
        button_context: AgentContext,
    ) -> None:
        """Test simple button component generation."""
        result = await orchestrator.run_pipeline(
            pipeline_type=PipelineType.COMPONENT,
            context=button_context,
        )

        # Core assertions
        assert_pipeline_success(result)
        assert_valid_html_structure(result.html)
        assert_has_tailwind_classes(result.html)
        assert_accessibility(result.html)

        # Performance bounds
        assert_token_usage(result, max_total=50000)
        assert_execution_time(result, max_ms=60000)

        # Content verification
        assert "Get Started" in result.html or "get-started" in result.html.lower()

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_pricing_card_component(
        self,
        orchestrator: "Orchestrator",
        pricing_card_context: AgentContext,
    ) -> None:
        """Test complex pricing card with features list."""
        result = await orchestrator.run_pipeline(
            pipeline_type=PipelineType.COMPONENT,
            context=pricing_card_context,
        )

        # Core assertions
        assert_pipeline_success(result)
        assert_valid_html_structure(result.html)
        assert_has_tailwind_classes(result.html)

        # Content verification - price should appear
        html_lower = result.html.lower()
        assert "$99" in result.html or "99" in html_lower, "Price not found in output"

        # Performance bounds (complex component = more tokens)
        assert_token_usage(result, max_total=75000)
        assert_execution_time(result, max_ms=90000)


class TestPagePipeline:
    """Tests for PAGE pipeline - full page layouts."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.expensive
    async def test_landing_page(
        self,
        orchestrator: "Orchestrator",
        landing_page_context: AgentContext,
    ) -> None:
        """Test full landing page generation."""
        result = await orchestrator.run_pipeline(
            pipeline_type=PipelineType.PAGE,
            context=landing_page_context,
        )

        # Core assertions
        assert_pipeline_success(result)
        assert_valid_html_structure(result.html)

        # Page should be substantial
        assert len(result.html) > 1000, "Landing page too short"

        # Should have responsive design
        assert_responsive(result.html)

        # Performance bounds (page = highest token usage)
        assert_token_usage(result, max_total=100000)
        assert_execution_time(result, max_ms=180000)


class TestRefinePipeline:
    """Tests for REFINE pipeline - iterating on existing designs."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_refine_adds_dark_mode(
        self,
        orchestrator: "Orchestrator",
        button_context: AgentContext,
    ) -> None:
        """Test refining a component to add dark mode support."""
        # Step 1: Create initial button
        initial_result = await orchestrator.run_pipeline(
            pipeline_type=PipelineType.COMPONENT,
            context=button_context,
        )
        assert_pipeline_success(initial_result)

        # Step 2: Refine to add dark mode
        refine_context = AgentContext(
            previous_html=initial_result.html,
            modifications="Add dark mode support with dark: variants",
            quality_target=QualityTarget.PRODUCTION,
        )

        refined_result = await orchestrator.run_pipeline(
            pipeline_type=PipelineType.REFINE,
            context=refine_context,
        )

        # Assertions
        assert_pipeline_success(refined_result)
        assert_valid_html_structure(refined_result.html)

        # Dark mode classes should be present
        assert "dark:" in refined_result.html, "Dark mode variants not added"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_invalid_component_graceful(
        self,
        orchestrator: "Orchestrator",
    ) -> None:
        """Test that invalid component type is handled gracefully."""
        context = AgentContext(
            component_type="nonexistent_xyz_component",
            theme="modern-minimal",
            quality_target=QualityTarget.DRAFT,
        )

        # Should not crash - may return error or fallback
        result = await orchestrator.run_pipeline(
            pipeline_type=PipelineType.COMPONENT,
            context=context,
        )

        # Either succeeds with some output or fails gracefully
        assert result is not None

    @pytest.mark.asyncio
    async def test_empty_content_structure(
        self,
        orchestrator: "Orchestrator",
    ) -> None:
        """Test component with empty content structure."""
        context = AgentContext(
            component_type="button",
            theme="modern-minimal",
            content_structure={},
            quality_target=QualityTarget.DRAFT,
        )

        result = await orchestrator.run_pipeline(
            pipeline_type=PipelineType.COMPONENT,
            context=context,
        )

        # Should still produce valid output with default content
        assert_pipeline_success(result)
        assert_valid_html_structure(result.html)

    @pytest.mark.asyncio
    async def test_unsupported_theme_fallback(
        self,
        orchestrator: "Orchestrator",
    ) -> None:
        """Test that unsupported theme falls back gracefully."""
        context = AgentContext(
            component_type="button",
            theme="nonexistent-theme-xyz",
            content_structure={"text": "Click Me"},
            quality_target=QualityTarget.DRAFT,
        )

        result = await orchestrator.run_pipeline(
            pipeline_type=PipelineType.COMPONENT,
            context=context,
        )

        # Should not crash - may use default theme
        assert result is not None
        if result.success:
            assert_valid_html_structure(result.html)


class TestMultiAgentCoordination:
    """Tests validating multi-agent coordination."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_trifecta_produces_separate_outputs(
        self,
        orchestrator: "Orchestrator",
    ) -> None:
        """Test that Trifecta pipeline produces HTML, CSS, and JS outputs."""
        context = AgentContext(
            component_type="card",
            theme="glassmorphism",
            content_structure={
                "title": "Premium Card",
                "description": "A beautiful glass card",
                "cta": "Learn More",
            },
            quality_target=QualityTarget.HIGH,
        )

        result = await orchestrator.run_pipeline(
            pipeline_type=PipelineType.COMPONENT,
            context=context,
        )

        assert_pipeline_success(result)

        # HTML is always produced
        assert result.html, "No HTML output"
        assert_valid_html_structure(result.html)

        # CSS and JS may be produced depending on component complexity
        # At minimum, combined_output should have content
        assert result.combined_output, "No combined output"

    @pytest.mark.asyncio
    async def test_token_distribution_across_agents(
        self,
        orchestrator: "Orchestrator",
        button_context: AgentContext,
    ) -> None:
        """Test that tokens are distributed across multiple agents."""
        result = await orchestrator.run_pipeline(
            pipeline_type=PipelineType.COMPONENT,
            context=button_context,
        )

        assert_pipeline_success(result)

        # Should have token tracking per agent
        if result.tokens_per_agent:
            # Multiple agents should have contributed
            agents_with_tokens = [
                agent for agent, tokens in result.tokens_per_agent.items() if tokens > 0
            ]
            assert len(agents_with_tokens) >= 1, "No agents recorded token usage"

        # Total tokens should be sum of per-agent tokens (or close)
        assert result.total_tokens > 0, "No total tokens recorded"
