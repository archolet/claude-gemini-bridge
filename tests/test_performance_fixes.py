"""Correctness tests for performance anti-pattern fixes.

These tests verify that the performance optimizations maintain
correct behavior (not benchmarking, just correctness).
"""

import pytest
from collections import OrderedDict

# =============================================================================
# Issue 6: Regex Recompilation → @lru_cache patterns
# =============================================================================


class TestIssue6RegexCaching:
    """Test that cached regex patterns return same results."""

    def test_section_pattern_consistency(self):
        """Pattern caching returns identical results for same section name."""
        from gemini_mcp.section_utils import _get_section_pattern

        pattern1 = _get_section_pattern("hero")
        pattern2 = _get_section_pattern("hero")

        # Should be the exact same object due to caching
        assert pattern1 is pattern2

        # Different section names should have different patterns
        pattern3 = _get_section_pattern("navbar")
        assert pattern1 is not pattern3

    def test_section_with_groups_pattern_consistency(self):
        """Pattern with groups caching works correctly."""
        from gemini_mcp.section_utils import _get_section_with_groups_pattern

        pattern1 = _get_section_with_groups_pattern("features")
        pattern2 = _get_section_with_groups_pattern("features")

        assert pattern1 is pattern2

    def test_section_boundaries_pattern_consistency(self):
        """Section boundaries pattern caching works correctly."""
        from gemini_mcp.section_utils import _get_section_boundaries_pattern

        pattern1 = _get_section_boundaries_pattern("cta")
        pattern2 = _get_section_boundaries_pattern("cta")

        assert pattern1 is pattern2


# =============================================================================
# Issue 1: N+1 Section Extraction → Batch extraction
# =============================================================================


class TestIssue1BatchExtraction:
    """Test that batch extraction matches per-section extraction."""

    def test_batch_extraction_matches_individual(self):
        """Batch extraction produces same results as individual extraction."""
        from gemini_mcp.section_utils import (
            extract_design_tokens_from_section,
            extract_design_tokens_batch,
        )

        html = """
        <!-- SECTION: hero -->
        <div class="bg-blue-600 text-white p-8">Hero</div>
        <!-- /SECTION: hero -->
        <!-- SECTION: features -->
        <div class="bg-gray-100 text-gray-800 p-4">Features</div>
        <!-- /SECTION: features -->
        """

        # Individual extraction
        hero_tokens = extract_design_tokens_from_section(html, "hero")
        features_tokens = extract_design_tokens_from_section(html, "features")

        # Batch extraction
        batch_tokens = extract_design_tokens_batch(html)

        # Verify consistency
        assert set(hero_tokens.get("colors", [])) == set(
            batch_tokens.get("hero", {}).get("colors", [])
        )
        assert set(features_tokens.get("colors", [])) == set(
            batch_tokens.get("features", {}).get("colors", [])
        )

    def test_batch_extraction_with_exclusion(self):
        """Batch extraction correctly excludes specified section."""
        from gemini_mcp.section_utils import extract_design_tokens_batch

        html = """
        <!-- SECTION: hero -->
        <div class="bg-blue-600">Hero</div>
        <!-- /SECTION: hero -->
        <!-- SECTION: features -->
        <div class="bg-gray-100">Features</div>
        <!-- /SECTION: features -->
        """

        batch_tokens = extract_design_tokens_batch(html, exclude_section="hero")

        assert "hero" not in batch_tokens
        assert "features" in batch_tokens


# =============================================================================
# Issue 2: O(n^2) String Classification → Sets + tuple prefixes
# =============================================================================


class TestIssue2SetClassification:
    """Test that set-based classification produces correct output."""

    def test_color_classification(self):
        """Color classes are correctly classified."""
        from gemini_mcp.section_utils import extract_design_tokens_from_section

        html = """
        <!-- SECTION: test -->
        <div class="bg-blue-600 text-white border-gray-300 ring-blue-500">
            Test content
        </div>
        <!-- /SECTION: test -->
        """

        tokens = extract_design_tokens_from_section(html, "test")

        colors = set(tokens.get("colors", []))
        assert "bg-blue-600" in colors
        assert "text-white" in colors
        assert "border-gray-300" in colors
        assert "ring-blue-500" in colors

    def test_typography_classification(self):
        """Typography classes are correctly classified."""
        from gemini_mcp.section_utils import extract_design_tokens_from_section

        html = """
        <!-- SECTION: test -->
        <div class="font-bold text-xl tracking-wide leading-relaxed">
            Test content
        </div>
        <!-- /SECTION: test -->
        """

        tokens = extract_design_tokens_from_section(html, "test")

        typography = set(tokens.get("typography", []))
        assert "font-bold" in typography
        assert "text-xl" in typography
        assert "tracking-wide" in typography
        assert "leading-relaxed" in typography

    def test_no_duplicates(self):
        """Classification produces no duplicates (set behavior)."""
        from gemini_mcp.section_utils import extract_design_tokens_from_section

        html = """
        <!-- SECTION: test -->
        <div class="bg-blue-600 bg-blue-600 bg-blue-600">
            <span class="bg-blue-600">Duplicate classes</span>
        </div>
        <!-- /SECTION: test -->
        """

        tokens = extract_design_tokens_from_section(html, "test")

        colors = tokens.get("colors", [])
        # Should only appear once despite multiple occurrences
        assert colors.count("bg-blue-600") == 1


# =============================================================================
# Issue 7: String Concatenation in Loop → Collect-then-apply
# =============================================================================


class TestIssue7MigrateToMarkers:
    """Test that migrate_to_markers produces identical output."""

    def test_migrate_single_section(self):
        """Single section migration works correctly."""
        from gemini_mcp.section_utils import migrate_to_markers, has_section_markers

        html = "<header>Navigation content</header>"
        mapping = {"<header": "navbar"}

        result = migrate_to_markers(html, mapping)

        assert has_section_markers(result)
        assert "<!-- SECTION: navbar -->" in result
        assert "<!-- /SECTION: navbar -->" in result

    def test_migrate_multiple_sections(self):
        """Multiple section migration works correctly."""
        from gemini_mcp.section_utils import migrate_to_markers

        html = """
        <header>Nav</header>
        <main>Content</main>
        <footer>Footer</footer>
        """
        mapping = {
            "<header": "navbar",
            "<main": "content",
            "<footer": "footer",
        }

        result = migrate_to_markers(html, mapping)

        assert "<!-- SECTION: navbar -->" in result
        assert "<!-- SECTION: content -->" in result
        assert "<!-- SECTION: footer -->" in result


# =============================================================================
# Issue 8: Redundant Body Tag Scan → Module-level pattern
# =============================================================================


class TestIssue8BodyPattern:
    """Test that body content extraction works correctly."""

    def test_body_pattern_exists(self):
        """Module-level body pattern is defined."""
        from gemini_mcp.server import _BODY_CONTENT_PATTERN

        assert _BODY_CONTENT_PATTERN is not None
        assert hasattr(_BODY_CONTENT_PATTERN, "search")

    def test_body_pattern_extraction(self):
        """Body pattern correctly extracts content."""
        from gemini_mcp.server import _BODY_CONTENT_PATTERN

        html = "<html><body class='dark'><div>Content</div></body></html>"
        match = _BODY_CONTENT_PATTERN.search(html)

        assert match is not None
        assert match.group(1) == "<div>Content</div>"


# =============================================================================
# Issue 4: Multiple Regex Per Element → Precompiled patterns
# =============================================================================


class TestIssue4PrecompiledPatterns:
    """Test that precompiled patterns are defined and work correctly."""

    def test_element_pattern_exists(self):
        """Element pattern is defined at module level."""
        from gemini_mcp.orchestration.context import _ELEMENT_PATTERN

        assert _ELEMENT_PATTERN is not None
        assert hasattr(_ELEMENT_PATTERN, "finditer")

    def test_id_pattern_exists(self):
        """ID pattern is defined at module level."""
        from gemini_mcp.orchestration.context import _ID_PATTERN

        assert _ID_PATTERN is not None
        assert hasattr(_ID_PATTERN, "search")

    def test_data_attr_pattern_exists(self):
        """Data attribute pattern is defined at module level."""
        from gemini_mcp.orchestration.context import _DATA_ATTR_PATTERN

        assert _DATA_ATTR_PATTERN is not None
        assert hasattr(_DATA_ATTR_PATTERN, "finditer")

    def test_element_pattern_matching(self):
        """Element pattern correctly matches HTML elements."""
        from gemini_mcp.orchestration.context import _ELEMENT_PATTERN

        html = '<button id="btn" data-interaction="click">Click</button>'
        matches = list(_ELEMENT_PATTERN.finditer(html))

        assert len(matches) == 1
        assert matches[0].group(1) == "button"


# =============================================================================
# Issue 5: Inefficient LRU Cache Eviction → OrderedDict
# =============================================================================


class TestIssue5LRUEviction:
    """Test that OrderedDict-based LRU eviction works correctly."""

    def test_cache_uses_ordered_dict(self):
        """Cache uses OrderedDict internally."""
        from gemini_mcp.cache import DesignCache

        cache = DesignCache(max_entries=5)

        assert isinstance(cache._cache, OrderedDict)

    def test_lru_eviction_order(self):
        """LRU eviction removes oldest accessed items first."""
        from gemini_mcp.cache import DesignCache

        cache = DesignCache(max_entries=3, ttl_hours=1)

        # Add 3 items
        cache.set({"data": 1}, key="a")
        cache.set({"data": 2}, key="b")
        cache.set({"data": 3}, key="c")

        # Access 'a' to make it recently used
        cache.get(key="a")

        # Add 4th item, should evict 'b' (least recently used)
        cache.set({"data": 4}, key="d")

        assert cache.get(key="a") is not None  # Still exists
        assert cache.get(key="b") is None  # Evicted
        assert cache.get(key="c") is not None  # Still exists
        assert cache.get(key="d") is not None  # Still exists

    def test_move_to_end_on_access(self):
        """Accessing an item moves it to the end of OrderedDict."""
        from gemini_mcp.cache import DesignCache

        cache = DesignCache(max_entries=5, ttl_hours=1)

        cache.set({"data": 1}, key="a")
        cache.set({"data": 2}, key="b")
        cache.set({"data": 3}, key="c")

        # Access 'a' - should move to end
        cache.get(key="a")

        # Check order: b, c, a (a moved to end)
        keys = list(cache._cache.keys())
        assert keys[-1].endswith("a") or cache._cache[keys[-1]].value == {"data": 1}


# =============================================================================
# Issue 3: Deep Copy in Parallel Loop → fork_for_parallel
# =============================================================================


class TestIssue3ForkForParallel:
    """Test that fork_for_parallel creates isolated contexts."""

    def test_fork_exists(self):
        """fork_for_parallel method exists on AgentContext."""
        from gemini_mcp.orchestration.context import AgentContext

        ctx = AgentContext()
        assert hasattr(ctx, "fork_for_parallel")

    def test_fork_creates_independent_errors(self):
        """Forked context has independent error list."""
        from gemini_mcp.orchestration.context import AgentContext

        ctx = AgentContext()
        ctx.add_error("original error")

        forked = ctx.fork_for_parallel(step_index=0)
        forked.add_error("forked error")

        # Original should only have its error
        assert len(ctx.errors) == 1
        assert "original error" in ctx.errors

        # Forked should have both (copied + new)
        assert len(forked.errors) == 2

    def test_fork_sets_step_index(self):
        """Forked context has correct step index."""
        from gemini_mcp.orchestration.context import AgentContext

        ctx = AgentContext()
        forked = ctx.fork_for_parallel(step_index=5)

        assert forked.step_index == 5
        assert forked.current_section_index == 5

    def test_fork_sets_section_type(self):
        """Forked context has correct section type."""
        from gemini_mcp.orchestration.context import AgentContext

        ctx = AgentContext()
        forked = ctx.fork_for_parallel(step_index=0, section_type="hero")

        assert forked.current_section_type == "hero"

    def test_fork_has_unique_pipeline_id(self):
        """Forked context has modified pipeline ID."""
        from gemini_mcp.orchestration.context import AgentContext

        ctx = AgentContext()
        original_id = ctx.pipeline_id

        forked = ctx.fork_for_parallel(step_index=3)

        assert forked.pipeline_id != original_id
        assert forked.pipeline_id.startswith(original_id)
        assert "-3" in forked.pipeline_id
