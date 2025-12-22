"""Tests for Phase 3 Performance implementations.

GAP 7: Prompt Optimization - PromptBuilder class
GAP 8: JS Fallback - modular library
GAP 9: Caching - component cache layer
GAP 12: Observability - telemetry module
"""

import pytest
import time


# =============================================================================
# GAP 7: Prompt Optimization Tests
# =============================================================================

class TestGAP7PromptBuilder:
    """Tests for PromptBuilder modular prompt construction."""

    def test_prompt_builder_basic(self):
        """Test basic prompt builder usage."""
        from gemini_mcp.prompt_builder import PromptBuilder

        builder = PromptBuilder()
        prompt = builder.with_role().build()

        assert "World-Class Frontend Architect" in prompt
        assert len(prompt) > 100

    def test_prompt_builder_fluent_interface(self):
        """Test fluent interface chaining."""
        from gemini_mcp.prompt_builder import PromptBuilder

        prompt = (
            PromptBuilder()
            .with_role()
            .with_anti_laziness()
            .with_output_format()
            .build()
        )

        assert "ANTI-LAZINESS PROTOCOL" in prompt
        assert "OUTPUT FORMAT" in prompt

    def test_prompt_builder_with_component(self):
        """Test component-specific instructions."""
        from gemini_mcp.prompt_builder import PromptBuilder

        prompt = (
            PromptBuilder()
            .with_role()
            .with_component("button")
            .build()
        )

        assert "BUTTON SPECIFICS" in prompt
        assert "Gradient border" in prompt

    def test_prompt_builder_with_theme(self):
        """Test theme-specific instructions."""
        from gemini_mcp.prompt_builder import PromptBuilder

        prompt = (
            PromptBuilder()
            .with_role()
            .with_theme("glassmorphism")
            .build()
        )

        assert "GLASSMORPHISM THEME" in prompt
        assert "backdrop-blur" in prompt

    def test_prompt_builder_with_language(self):
        """Test language configuration."""
        from gemini_mcp.prompt_builder import PromptBuilder

        prompt = (
            PromptBuilder()
            .with_language("tr")
            .build()
        )

        assert "Turkish" in prompt

    def test_prompt_builder_with_project_context(self):
        """Test project context injection."""
        from gemini_mcp.prompt_builder import PromptBuilder

        prompt = (
            PromptBuilder()
            .with_project_context("E-commerce checkout flow")
            .build()
        )

        assert "E-commerce checkout flow" in prompt

    def test_prompt_builder_full_design_system(self):
        """Test full design system preset."""
        from gemini_mcp.prompt_builder import PromptBuilder

        prompt = PromptBuilder().with_full_design_system().build()

        # Should have all major sections
        assert "ANTI-LAZINESS" in prompt
        assert "OUTPUT FORMAT" in prompt
        assert "VISUAL DENSITY" in prompt
        assert "MICRO-INTERACTION" in prompt
        assert "ALPINE.JS" in prompt
        assert "ACCESSIBILITY" in prompt
        assert "DARK MODE" in prompt
        assert "RESPONSIVE" in prompt

    def test_prompt_builder_with_few_shot(self):
        """Test few-shot examples injection."""
        from gemini_mcp.prompt_builder import PromptBuilder

        examples = ["Example 1: Button code", "Example 2: Card code"]
        prompt = (
            PromptBuilder()
            .with_few_shot(examples)
            .build()
        )

        assert "EXAMPLES" in prompt
        assert "Example 1" in prompt
        assert "Example 2" in prompt

    def test_prompt_builder_build_with_task(self):
        """Test building prompt with task description."""
        from gemini_mcp.prompt_builder import PromptBuilder

        prompt = (
            PromptBuilder()
            .with_role()
            .build_with_task("Create a login button")
        )

        assert "YOUR TASK" in prompt
        assert "Create a login button" in prompt

    def test_build_component_prompt_helper(self):
        """Test build_component_prompt helper function."""
        from gemini_mcp.prompt_builder import build_component_prompt

        prompt = build_component_prompt(
            component_type="navbar",
            theme="modern-minimal",
            language="en",
            project_context="SaaS dashboard",
        )

        assert "NAVBAR SPECIFICS" in prompt
        assert "MODERN-MINIMAL THEME" in prompt
        assert "English" in prompt
        assert "SaaS dashboard" in prompt

    def test_build_section_prompt_modular(self):
        """Test section prompt with style consistency."""
        from gemini_mcp.prompt_builder import build_section_prompt_modular

        previous_tokens = {
            "colors": {"primary": "blue-600"},
            "typography": {"heading": "font-bold"},
            "spacing": {"section": "py-16"},
        }

        prompt = build_section_prompt_modular(
            section_type="hero",
            theme="gradient",
            previous_tokens=previous_tokens,
        )

        assert "STYLE CONSISTENCY" in prompt
        assert "blue-600" in prompt
        assert "SECTION: HERO" in prompt

    def test_build_refinement_prompt_modular(self):
        """Test refinement prompt generation."""
        from gemini_mcp.prompt_builder import build_refinement_prompt_modular

        prompt = build_refinement_prompt_modular(
            previous_html="<button>Test</button>",
            modifications="Make it blue",
        )

        assert "HYPER-ITERATION" in prompt
        assert "<button>Test</button>" in prompt
        assert "Make it blue" in prompt

    def test_utility_functions(self):
        """Test utility functions."""
        from gemini_mcp.prompt_builder import (
            get_available_sections,
            get_component_types,
            get_supported_themes,
            estimate_prompt_tokens,
        )

        sections = get_available_sections()
        assert "role" in sections
        assert "anti_laziness" in sections

        components = get_component_types()
        assert "button" in components
        assert "navbar" in components

        themes = get_supported_themes()
        assert "modern-minimal" in themes
        assert "glassmorphism" in themes

        # Token estimation
        tokens = estimate_prompt_tokens("Test " * 100)
        assert tokens > 0


# =============================================================================
# GAP 8: JS Fallback Tests
# =============================================================================

class TestGAP8JSFallbacks:
    """Tests for modular JavaScript fallback library."""

    def test_get_js_module(self):
        """Test getting a specific JS module."""
        from gemini_mcp.js_fallbacks import get_js_module

        modal_js = get_js_module("modal")

        assert modal_js is not None
        assert "Modal" in modal_js
        assert "focus" in modal_js.lower()
        assert "utils" in modal_js  # Should include dependency

    def test_get_js_for_component(self):
        """Test getting JS for a component type."""
        from gemini_mcp.js_fallbacks import get_js_for_component

        navbar_js = get_js_for_component("navbar")

        assert "Dropdown" in navbar_js
        assert "utils" in navbar_js

    def test_get_js_for_carousel(self):
        """Test carousel JS module."""
        from gemini_mcp.js_fallbacks import get_js_for_component

        carousel_js = get_js_for_component("carousel")

        assert "Carousel" in carousel_js
        assert "touchstart" in carousel_js
        assert "autoplay" in carousel_js

    def test_detect_needed_modules(self):
        """Test auto-detection of needed modules."""
        from gemini_mcp.js_fallbacks import detect_needed_modules

        html = '''
        <div data-modal="test">
            <button data-modal-open="test">Open</button>
        </div>
        <div data-accordion>
            <div data-accordion-item>Item</div>
        </div>
        '''

        modules = detect_needed_modules(html)

        assert "modal" in modules
        assert "accordion" in modules
        assert "utils" in modules  # Dependency

    def test_inject_js_fallbacks(self):
        """Test JS injection into HTML."""
        from gemini_mcp.js_fallbacks import inject_js_fallbacks

        html = '''
        <html>
        <body>
            <div data-dropdown>Dropdown</div>
        </body>
        </html>
        '''

        result = inject_js_fallbacks(html, detect_needed=True)

        assert "<script>" in result
        assert "Dropdown" in result
        assert "utils" in result

    def test_inject_js_fallbacks_specific_modules(self):
        """Test injecting specific modules."""
        from gemini_mcp.js_fallbacks import inject_js_fallbacks

        html = "<body><div>Test</div></body>"

        result = inject_js_fallbacks(
            html,
            modules=["toast", "tabs"],
            detect_needed=False,
        )

        assert "Toast" in result
        assert "Tabs" in result

    def test_get_all_module_names(self):
        """Test getting all module names."""
        from gemini_mcp.js_fallbacks import get_all_module_names

        names = get_all_module_names()

        assert "utils" in names
        assert "modal" in names
        assert "dropdown" in names
        assert "carousel" in names
        assert "tabs" in names
        assert "accordion" in names
        assert "toast" in names

    def test_get_module_info(self):
        """Test getting module info."""
        from gemini_mcp.js_fallbacks import get_module_info

        info = get_module_info("modal")

        assert info is not None
        assert info["name"] == "modal"
        assert "focus trap" in info["description"].lower()
        assert "utils" in info["dependencies"]

    def test_module_has_no_inner_html(self):
        """Test that modules use safe DOM methods."""
        from gemini_mcp.js_fallbacks import JS_MODULES

        for name, module in JS_MODULES.items():
            # innerHTML should not be used (security)
            assert "innerHTML" not in module.code, f"Module {name} uses innerHTML"


# =============================================================================
# GAP 9: Caching Tests
# =============================================================================

class TestGAP9Caching:
    """Tests for design cache functionality."""

    def test_cache_basic_operations(self):
        """Test basic cache get/set."""
        from gemini_mcp.cache import DesignCache

        cache = DesignCache(ttl_hours=1, max_entries=10)

        # Set value
        key = cache.set(
            {"html": "<div>Test</div>"},
            component_type="button",
            theme="modern-minimal",
        )

        assert key != ""

        # Get value
        result = cache.get(
            component_type="button",
            theme="modern-minimal",
        )

        assert result is not None
        assert result["html"] == "<div>Test</div>"

    def test_cache_miss(self):
        """Test cache miss."""
        from gemini_mcp.cache import DesignCache

        cache = DesignCache(ttl_hours=1, max_entries=10)

        result = cache.get(component_type="nonexistent")
        assert result is None

    def test_cache_invalidate(self):
        """Test cache invalidation."""
        from gemini_mcp.cache import DesignCache

        cache = DesignCache(ttl_hours=1, max_entries=10)

        cache.set(
            {"html": "<div>Test</div>"},
            component_type="card",
        )

        # Invalidate
        removed = cache.invalidate(component_type="card")
        assert removed is True

        # Should be gone
        result = cache.get(component_type="card")
        assert result is None

    def test_cache_stats(self):
        """Test cache statistics."""
        from gemini_mcp.cache import DesignCache

        cache = DesignCache(ttl_hours=1, max_entries=10)

        # Set and get
        cache.set({"html": "test"}, key="test1")
        cache.get(key="test1")  # Hit
        cache.get(key="test2")  # Miss

        stats = cache.get_stats()

        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["entries"] == 1

    def test_cache_clear(self):
        """Test cache clearing."""
        from gemini_mcp.cache import DesignCache

        cache = DesignCache(ttl_hours=1, max_entries=10)

        cache.set({"html": "test1"}, key="k1")
        cache.set({"html": "test2"}, key="k2")

        cleared = cache.clear()
        assert cleared == 2

        stats = cache.get_stats()
        assert stats["entries"] == 0

    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        from gemini_mcp.cache import DesignCache

        cache = DesignCache(ttl_hours=1, max_entries=3)

        # Fill cache
        cache.set({"v": 1}, key="k1")
        cache.set({"v": 2}, key="k2")
        cache.set({"v": 3}, key="k3")

        # Access k1 to make it recently used
        cache.get(key="k1")

        # Add new entry - should evict k2 (least recently used)
        cache.set({"v": 4}, key="k4")

        assert cache.get(key="k1") is not None  # Still there
        assert cache.get(key="k3") is not None  # Still there
        assert cache.get(key="k4") is not None  # New entry

    def test_global_cache_singleton(self):
        """Test global cache singleton."""
        from gemini_mcp.cache import get_design_cache, clear_design_cache

        cache1 = get_design_cache()
        cache2 = get_design_cache()

        assert cache1 is cache2

        # Clear for other tests
        clear_design_cache()


# =============================================================================
# GAP 12: Telemetry Tests
# =============================================================================

class TestGAP12Telemetry:
    """Tests for telemetry and observability."""

    def test_telemetry_track_operation(self):
        """Test tracking an operation."""
        from gemini_mcp.telemetry import Telemetry

        Telemetry.init()
        Telemetry.clear()

        with Telemetry.track("design_frontend") as ctx:
            ctx.set_component("button")
            ctx.set_theme("modern-minimal")
            ctx.set_tokens(input_tokens=100, output_tokens=200, thinking_tokens=50)
            time.sleep(0.01)  # Small delay

        metrics = Telemetry.get_metrics()

        assert metrics["total_operations"] == 1
        assert metrics["completed_operations"] == 1
        assert metrics["tokens"]["input_tokens"] == 100
        assert metrics["tokens"]["output_tokens"] == 200
        assert metrics["latency"]["avg_ms"] > 0

    def test_telemetry_track_failure(self):
        """Test tracking a failed operation."""
        from gemini_mcp.telemetry import Telemetry

        Telemetry.init()
        Telemetry.clear()

        try:
            with Telemetry.track("design_frontend") as ctx:
                ctx.set_component("navbar")
                raise ValueError("Test error")
        except ValueError:
            pass

        metrics = Telemetry.get_metrics()

        assert metrics["total_operations"] == 1
        assert metrics["failed_operations"] == 1
        assert "ValueError" in metrics["errors_by_type"]

    def test_telemetry_request_id(self):
        """Test request ID generation."""
        from gemini_mcp.telemetry import Telemetry

        Telemetry.init()

        request_id = Telemetry.generate_request_id()

        assert len(request_id) == 8
        assert request_id.isalnum()

    def test_telemetry_get_recent_operations(self):
        """Test getting recent operations."""
        from gemini_mcp.telemetry import Telemetry

        Telemetry.init()
        Telemetry.clear()

        with Telemetry.track("op1") as ctx:
            ctx.set_component("button")

        with Telemetry.track("op2") as ctx:
            ctx.set_component("card")

        recent = Telemetry.get_recent_operations(limit=10)

        assert len(recent) == 2
        assert recent[0]["operation_type"] == "op1"
        assert recent[1]["operation_type"] == "op2"

    def test_telemetry_metrics_by_operation(self):
        """Test metrics by operation type."""
        from gemini_mcp.telemetry import Telemetry

        Telemetry.init()
        Telemetry.clear()

        with Telemetry.track("design_frontend"):
            pass
        with Telemetry.track("design_frontend"):
            pass
        with Telemetry.track("design_section"):
            pass

        metrics = Telemetry.get_metrics_by_operation("design_frontend")

        assert metrics["total"] == 2
        assert metrics["completed"] == 2

    def test_telemetry_export(self):
        """Test telemetry export."""
        from gemini_mcp.telemetry import Telemetry

        Telemetry.init()
        Telemetry.clear()

        with Telemetry.track("test_op"):
            pass

        export = Telemetry.export()

        assert "metrics" in export
        assert "recent_operations" in export
        assert "exported_at" in export

    def test_telemetry_disabled(self):
        """Test telemetry when disabled."""
        from gemini_mcp.telemetry import Telemetry

        Telemetry.init()
        Telemetry.clear()
        Telemetry.set_enabled(False)

        with Telemetry.track("test_op") as ctx:
            ctx.set_component("button")

        metrics = Telemetry.get_metrics()
        # Should not record when disabled
        assert metrics["total_operations"] == 0

        # Re-enable for other tests
        Telemetry.set_enabled(True)

    def test_token_usage_class(self):
        """Test TokenUsage dataclass."""
        from gemini_mcp.telemetry import TokenUsage

        usage = TokenUsage(
            input_tokens=100,
            output_tokens=200,
            thinking_tokens=50,
        )

        assert usage.total_tokens == 350

        dict_repr = usage.to_dict()
        assert dict_repr["total_tokens"] == 350

    def test_telemetry_summary(self):
        """Test telemetry summary generation."""
        from gemini_mcp.telemetry import Telemetry, get_telemetry_summary

        Telemetry.init()
        Telemetry.clear()

        with Telemetry.track("test_op") as ctx:
            ctx.set_tokens(input_tokens=100, output_tokens=200)

        summary = get_telemetry_summary()

        assert "Telemetry Summary" in summary
        assert "Total Operations: 1" in summary
        assert "Input: 100" in summary

    def test_operation_context_metadata(self):
        """Test adding custom metadata."""
        from gemini_mcp.telemetry import Telemetry

        Telemetry.init()
        Telemetry.clear()

        with Telemetry.track("test_op") as ctx:
            ctx.add_metadata("custom_key", "custom_value")
            ctx.set_cached(True)
            ctx.set_model("gemini-3-pro")

        recent = Telemetry.get_recent_operations(limit=1)

        assert recent[0]["metadata"]["custom_key"] == "custom_value"
        assert recent[0]["cached"] is True
        assert recent[0]["model"] == "gemini-3-pro"


# =============================================================================
# Integration Tests
# =============================================================================

class TestPhase3Integration:
    """Integration tests for Phase 3 components."""

    def test_prompt_builder_token_estimation(self):
        """Test that prompt builder produces reasonable prompts."""
        from gemini_mcp.prompt_builder import PromptBuilder, estimate_prompt_tokens

        prompt = (
            PromptBuilder()
            .with_full_design_system()
            .with_component("navbar")
            .with_theme("glassmorphism")
            .with_language("tr")
            .build()
        )

        tokens = estimate_prompt_tokens(prompt)

        # Should be substantial but not excessive
        assert tokens > 500  # Has content
        assert tokens < 10000  # Not bloated

    def test_js_fallbacks_component_coverage(self):
        """Test that JS fallbacks cover common components."""
        from gemini_mcp.js_fallbacks import COMPONENT_JS_REQUIREMENTS

        common_components = [
            "dropdown",
            "modal",
            "carousel",
            "tabs",
            "accordion",
            "navbar",
        ]

        for component in common_components:
            assert component in COMPONENT_JS_REQUIREMENTS, f"Missing JS for {component}"

    def test_telemetry_with_cache(self):
        """Test telemetry tracking cache operations."""
        from gemini_mcp.telemetry import Telemetry
        from gemini_mcp.cache import DesignCache

        Telemetry.init()
        Telemetry.clear()

        cache = DesignCache(ttl_hours=1, max_entries=10)

        # Simulate cache hit tracking
        with Telemetry.track("cache_lookup") as ctx:
            result = cache.get(key="test")
            ctx.set_cached(result is not None)

        metrics = Telemetry.get_metrics()
        assert metrics["total_operations"] == 1

    def test_modules_importable(self):
        """Test that all Phase 3 modules are importable."""
        # These imports should all succeed
        from gemini_mcp.prompt_builder import PromptBuilder
        from gemini_mcp.js_fallbacks import inject_js_fallbacks
        from gemini_mcp.cache import DesignCache
        from gemini_mcp.telemetry import Telemetry

        assert PromptBuilder is not None
        assert inject_js_fallbacks is not None
        assert DesignCache is not None
        assert Telemetry is not None
