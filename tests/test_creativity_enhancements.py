"""
Tests for Creativity Enhancement features.

This module tests all 7 creativity enhancements implemented across 4 batches:
- Batch 1: Adaptive Critic Threshold + Convergence Detection
- Batch 2: Missing Vibe Examples + Theme-Vibe Compatibility
- Batch 3: Reference Adherence Evaluation
- Batch 4: Theme Parity (brutalist + soft-ui expansion)
"""

import pytest
from typing import Any

# =============================================================================
# BATCH 1 TESTS: Adaptive Threshold + Convergence Detection
# =============================================================================


class TestAdaptiveThreshold:
    """Tests for component-type specific quality thresholds."""

    def test_component_thresholds_exist(self):
        """COMPONENT_THRESHOLDS dict should exist in orchestrator."""
        from gemini_mcp.orchestration.orchestrator import COMPONENT_THRESHOLDS

        assert COMPONENT_THRESHOLDS is not None
        assert isinstance(COMPONENT_THRESHOLDS, dict)

    def test_component_threshold_hero_higher_than_button(self):
        """Hero (high-impact) should have higher threshold than button (atomic)."""
        from gemini_mcp.orchestration.orchestrator import get_quality_threshold

        hero_threshold = get_quality_threshold("hero")
        button_threshold = get_quality_threshold("button")

        assert hero_threshold > button_threshold
        assert hero_threshold == 8.5
        assert button_threshold == 7.5

    def test_component_threshold_default(self):
        """Unknown components should use default threshold (8.0)."""
        from gemini_mcp.orchestration.orchestrator import get_quality_threshold

        unknown_threshold = get_quality_threshold("unknown_component_xyz")
        assert unknown_threshold == 8.0

    @pytest.mark.parametrize(
        "component,expected",
        [
            ("hero", 8.5),
            ("navbar", 8.5),
            ("landing_page", 8.5),
            ("card", 8.0),
            ("form", 8.0),
            ("modal", 8.0),
            ("footer", 8.0),
            ("button", 7.5),
            ("input", 7.5),
            ("badge", 7.5),
            ("avatar", 7.5),
        ],
    )
    def test_component_threshold_values(self, component: str, expected: float):
        """Each component type should have its designated threshold."""
        from gemini_mcp.orchestration.orchestrator import get_quality_threshold

        assert get_quality_threshold(component) == expected

    def test_component_threshold_case_insensitive(self):
        """Threshold lookup should be case-insensitive."""
        from gemini_mcp.orchestration.orchestrator import get_quality_threshold

        assert get_quality_threshold("HERO") == get_quality_threshold("hero")
        assert get_quality_threshold("Button") == get_quality_threshold("button")


class TestConvergenceDetection:
    """Tests for convergence-based early stopping."""

    def test_convergence_constants_exist(self):
        """Convergence constants should be defined."""
        from gemini_mcp.orchestration.orchestrator import (
            CONVERGENCE_THRESHOLD,
            CONVERGENCE_COUNT,
        )

        assert CONVERGENCE_THRESHOLD == 0.2
        assert CONVERGENCE_COUNT == 2

    def test_convergence_threshold_reasonable(self):
        """Convergence threshold should be between 0.1 and 0.5."""
        from gemini_mcp.orchestration.orchestrator import CONVERGENCE_THRESHOLD

        assert 0.1 <= CONVERGENCE_THRESHOLD <= 0.5


# =============================================================================
# BATCH 2 TESTS: Vibe Examples + Theme-Vibe Compatibility
# =============================================================================


class TestVibeExamples:
    """Tests for few-shot vibe examples."""

    def test_cyberpunk_edge_example_exists(self):
        """CYBERPUNK_EDGE_EXAMPLE should exist in few_shot_examples."""
        from gemini_mcp.few_shot_examples import CYBERPUNK_EDGE_EXAMPLE

        assert CYBERPUNK_EDGE_EXAMPLE is not None
        assert "component_type" in CYBERPUNK_EDGE_EXAMPLE
        assert "vibe" in CYBERPUNK_EDGE_EXAMPLE
        assert "html" in CYBERPUNK_EDGE_EXAMPLE
        assert CYBERPUNK_EDGE_EXAMPLE["vibe"] == "cyberpunk_edge"

    def test_luxury_editorial_example_exists(self):
        """LUXURY_EDITORIAL_EXAMPLE should exist in few_shot_examples."""
        from gemini_mcp.few_shot_examples import LUXURY_EDITORIAL_EXAMPLE

        assert LUXURY_EDITORIAL_EXAMPLE is not None
        assert "component_type" in LUXURY_EDITORIAL_EXAMPLE
        assert "vibe" in LUXURY_EDITORIAL_EXAMPLE
        assert "html" in LUXURY_EDITORIAL_EXAMPLE
        assert LUXURY_EDITORIAL_EXAMPLE["vibe"] == "luxury_editorial"

    def test_cyberpunk_edge_has_neon_classes(self):
        """Cyberpunk edge example should contain neon styling."""
        from gemini_mcp.few_shot_examples import CYBERPUNK_EDGE_EXAMPLE

        html = CYBERPUNK_EDGE_EXAMPLE["html"]
        assert "cyan" in html.lower() or "neon" in html.lower()

    def test_luxury_editorial_has_serif_typography(self):
        """Luxury editorial example should use serif typography."""
        from gemini_mcp.few_shot_examples import LUXURY_EDITORIAL_EXAMPLE

        html = LUXURY_EDITORIAL_EXAMPLE["html"]
        assert "serif" in html.lower() or "tracking" in html.lower()


class TestThemeVibeCompatibility:
    """Tests for theme-vibe compatibility matrix."""

    def test_compatibility_matrix_exists(self):
        """THEME_VIBE_COMPATIBILITY matrix should exist."""
        from gemini_mcp.theme_factories import THEME_VIBE_COMPATIBILITY

        assert THEME_VIBE_COMPATIBILITY is not None
        assert isinstance(THEME_VIBE_COMPATIBILITY, dict)

    def test_compatibility_matrix_has_all_themes(self):
        """Compatibility matrix should cover all 14 themes."""
        from gemini_mcp.theme_factories import THEME_VIBE_COMPATIBILITY

        expected_themes = {
            "modern-minimal",
            "brutalist",
            "glassmorphism",
            "neo-brutalism",
            "soft-ui",
            "corporate",
            "gradient",
            "cyberpunk",
            "retro",
            "pastel",
            "dark_mode_first",
            "high_contrast",
            "nature",
            "startup",
        }

        assert set(THEME_VIBE_COMPATIBILITY.keys()) == expected_themes

    def test_compatibility_matrix_has_all_vibes(self):
        """Each theme should have scores for all 7 vibes (4 core + 3 enterprise)."""
        from gemini_mcp.theme_factories import THEME_VIBE_COMPATIBILITY

        # Core vibes + Enterprise vibes (added for ERP dashboard transformation)
        expected_vibes = {
            "elite_corporate",
            "playful_funny",
            "cyberpunk_edge",
            "luxury_editorial",
            # Enterprise vibes
            "swiss_precision",
            "sap_fiori",
            "ibm_carbon",
        }

        for theme, vibes in THEME_VIBE_COMPATIBILITY.items():
            assert (
                set(vibes.keys()) == expected_vibes
            ), f"Theme '{theme}' missing vibes"

    def test_compatibility_scores_valid_range(self):
        """All compatibility scores should be between 1 and 5."""
        from gemini_mcp.theme_factories import THEME_VIBE_COMPATIBILITY

        for theme, vibes in THEME_VIBE_COMPATIBILITY.items():
            for vibe, score in vibes.items():
                assert 1 <= score <= 5, f"Invalid score for {theme}/{vibe}: {score}"

    def test_cyberpunk_theme_matches_cyberpunk_vibe(self):
        """Cyberpunk theme should have highest score with cyberpunk_edge vibe."""
        from gemini_mcp.theme_factories import THEME_VIBE_COMPATIBILITY

        cyberpunk_scores = THEME_VIBE_COMPATIBILITY["cyberpunk"]
        assert cyberpunk_scores["cyberpunk_edge"] == 5


class TestVibeRecommendations:
    """Tests for vibe recommendation functions."""

    def test_get_recommended_vibes_exists(self):
        """get_recommended_vibes function should exist."""
        from gemini_mcp.theme_factories import get_recommended_vibes

        assert callable(get_recommended_vibes)

    def test_get_vibe_compatibility_exists(self):
        """get_vibe_compatibility function should exist."""
        from gemini_mcp.theme_factories import get_vibe_compatibility

        assert callable(get_vibe_compatibility)

    def test_recommended_vibes_sorted_by_score(self):
        """Recommended vibes should be sorted by score (best first)."""
        from gemini_mcp.theme_factories import (
            get_recommended_vibes,
            THEME_VIBE_COMPATIBILITY,
        )

        for theme in THEME_VIBE_COMPATIBILITY.keys():
            vibes = get_recommended_vibes(theme)
            scores = [
                THEME_VIBE_COMPATIBILITY[theme].get(v, 0) for v in vibes
            ]
            # Should be descending
            assert scores == sorted(scores, reverse=True)

    def test_vibe_compatibility_returns_tuple(self):
        """get_vibe_compatibility should return (score, message) tuple."""
        from gemini_mcp.theme_factories import get_vibe_compatibility

        result = get_vibe_compatibility("cyberpunk", "cyberpunk_edge")

        assert isinstance(result, tuple)
        assert len(result) == 2
        score, message = result
        assert isinstance(score, int)
        assert isinstance(message, str)

    def test_vibe_compatibility_messages(self):
        """Each score level should have a descriptive message."""
        from gemini_mcp.theme_factories import get_vibe_compatibility

        # Score 5 (perfect match)
        score, msg = get_vibe_compatibility("cyberpunk", "cyberpunk_edge")
        assert score == 5
        assert "perfect" in msg.lower() or "amplifies" in msg.lower()

        # Score 1 (conflict)
        score, msg = get_vibe_compatibility("cyberpunk", "elite_corporate")
        assert score == 1
        assert "conflict" in msg.lower()


# =============================================================================
# BATCH 3 TESTS: Reference Adherence
# =============================================================================


class TestReferenceAdherence:
    """Tests for reference adherence evaluation."""

    def test_reference_adherence_scores_dataclass_exists(self):
        """ReferenceAdherenceScores dataclass should exist."""
        from gemini_mcp.agents.critic import ReferenceAdherenceScores

        assert ReferenceAdherenceScores is not None

    def test_reference_adherence_scores_properties(self):
        """ReferenceAdherenceScores should have required properties."""
        from gemini_mcp.agents.critic import ReferenceAdherenceScores

        scores = ReferenceAdherenceScores(
            color_match=8.0,
            typography_match=7.5,
            spacing_match=8.0,
            aesthetic_match=7.0,
        )

        assert scores.color_match == 8.0
        assert scores.typography_match == 7.5
        assert scores.spacing_match == 8.0
        assert scores.aesthetic_match == 7.0

    def test_reference_adherence_scores_overall(self):
        """ReferenceAdherenceScores.overall should calculate average."""
        from gemini_mcp.agents.critic import ReferenceAdherenceScores

        scores = ReferenceAdherenceScores(
            color_match=8.0,
            typography_match=8.0,
            spacing_match=8.0,
            aesthetic_match=8.0,
        )

        assert scores.overall == 8.0

    def test_reference_adherence_scores_default_values(self):
        """ReferenceAdherenceScores should have sensible defaults."""
        from gemini_mcp.agents.critic import ReferenceAdherenceScores

        scores = ReferenceAdherenceScores()
        assert scores.color_match == 5.0
        assert scores.overall == 5.0

    def test_agent_context_has_design_tokens(self):
        """AgentContext should have design_tokens attribute."""
        from gemini_mcp.orchestration.context import AgentContext

        context = AgentContext(
            component_type="card",
            theme="modern-minimal",
        )

        assert hasattr(context, "design_tokens")
        assert isinstance(context.design_tokens, dict)

    def test_agent_context_has_reference_improvements(self):
        """AgentContext should have reference_adherence_improvements attribute."""
        from gemini_mcp.orchestration.context import AgentContext

        context = AgentContext(
            component_type="card",
            theme="modern-minimal",
        )

        assert hasattr(context, "reference_adherence_improvements")
        assert isinstance(context.reference_adherence_improvements, list)


# =============================================================================
# BATCH 4 TESTS: Theme Parity
# =============================================================================


class TestBrutalistThemeExpansion:
    """Tests for expanded brutalist theme parameters."""

    def test_brutalist_accepts_accent_color(self):
        """Brutalist theme should accept accent_color parameter."""
        from gemini_mcp.theme_factories import create_brutalist_theme

        theme = create_brutalist_theme(accent_color="cyan")
        assert "_accent_color" in theme or "accent" in theme

    def test_brutalist_accent_colors_valid(self):
        """Brutalist should accept all defined accent colors."""
        from gemini_mcp.theme_factories import create_brutalist_theme

        valid_colors = ["yellow", "red", "cyan", "pink", "lime"]
        for color in valid_colors:
            theme = create_brutalist_theme(accent_color=color)
            assert theme is not None

    def test_brutalist_accepts_enable_animations(self):
        """Brutalist theme should accept enable_animations parameter."""
        from gemini_mcp.theme_factories import create_brutalist_theme

        theme_animated = create_brutalist_theme(enable_animations=True)
        theme_static = create_brutalist_theme(enable_animations=False)

        assert theme_animated["_enable_animations"] is True
        assert theme_static["_enable_animations"] is False

    def test_brutalist_accepts_border_width(self):
        """Brutalist theme should accept border_width parameter."""
        from gemini_mcp.theme_factories import create_brutalist_theme

        for width in ["2", "4", "8"]:
            theme = create_brutalist_theme(border_width=width)
            assert theme["_border_width"] == width

    def test_brutalist_accepts_shadow_offset(self):
        """Brutalist theme should accept shadow_offset parameter."""
        from gemini_mcp.theme_factories import create_brutalist_theme

        for offset in ["sm", "md", "lg"]:
            theme = create_brutalist_theme(shadow_offset=offset)
            assert theme["_shadow_offset"] == offset


class TestSoftUIThemeExpansion:
    """Tests for expanded soft-ui theme parameters."""

    def test_soft_ui_accepts_color_temperature(self):
        """Soft-UI theme should accept color_temperature parameter."""
        from gemini_mcp.theme_factories import create_soft_ui_theme

        for temp in ["cool", "neutral", "warm"]:
            theme = create_soft_ui_theme(color_temperature=temp)
            assert theme["_color_temperature"] == temp

    def test_soft_ui_temperature_affects_text(self):
        """Color temperature should affect text color tints."""
        from gemini_mcp.theme_factories import create_soft_ui_theme

        cool_theme = create_soft_ui_theme(color_temperature="cool")
        warm_theme = create_soft_ui_theme(color_temperature="warm")

        assert "blue" in cool_theme["text"]
        assert "amber" in warm_theme["text"]

    def test_soft_ui_accepts_surface_variant(self):
        """Soft-UI theme should accept surface_variant parameter."""
        from gemini_mcp.theme_factories import create_soft_ui_theme

        for variant in ["flat", "raised", "inset"]:
            theme = create_soft_ui_theme(surface_variant=variant)
            assert theme["_surface_variant"] == variant

    def test_soft_ui_accepts_glow_color(self):
        """Soft-UI theme should accept glow_color parameter."""
        from gemini_mcp.theme_factories import create_soft_ui_theme

        theme_with_glow = create_soft_ui_theme(glow_color="blue-400")
        theme_no_glow = create_soft_ui_theme(glow_color=None)

        assert theme_with_glow["_glow_color"] == "blue-400"
        assert theme_no_glow["_glow_color"] is None

    def test_soft_ui_accepts_enable_inner_shadow(self):
        """Soft-UI theme should accept enable_inner_shadow parameter."""
        from gemini_mcp.theme_factories import create_soft_ui_theme

        theme_with_inner = create_soft_ui_theme(enable_inner_shadow=True)
        theme_no_inner = create_soft_ui_theme(enable_inner_shadow=False)

        assert theme_with_inner["_enable_inner_shadow"] is True
        assert theme_no_inner["_enable_inner_shadow"] is False

    def test_soft_ui_has_card_variants(self):
        """Soft-UI should have all 3 card variants."""
        from gemini_mcp.theme_factories import create_soft_ui_theme

        theme = create_soft_ui_theme()

        assert "card_raised" in theme
        assert "card_flat" in theme
        assert "card_inset" in theme

    def test_soft_ui_name_includes_temperature(self):
        """Theme name should include temperature setting."""
        from gemini_mcp.theme_factories import create_soft_ui_theme

        theme = create_soft_ui_theme(color_temperature="warm", intensity="medium")
        assert "warm" in theme["name"]
        assert "medium" in theme["name"]


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestCreativityEnhancementsIntegration:
    """Integration tests ensuring all enhancements work together."""

    def test_all_imports_work(self):
        """All enhancement imports should work without errors."""
        # Batch 1
        from gemini_mcp.orchestration.orchestrator import (
            COMPONENT_THRESHOLDS,
            CONVERGENCE_THRESHOLD,
            CONVERGENCE_COUNT,
            get_quality_threshold,
        )

        # Batch 2
        from gemini_mcp.few_shot_examples import (
            CYBERPUNK_EDGE_EXAMPLE,
            LUXURY_EDITORIAL_EXAMPLE,
        )
        from gemini_mcp.theme_factories import (
            THEME_VIBE_COMPATIBILITY,
            get_recommended_vibes,
            get_vibe_compatibility,
        )

        # Batch 3
        from gemini_mcp.agents.critic import ReferenceAdherenceScores

        # Batch 4
        from gemini_mcp.theme_factories import (
            create_brutalist_theme,
            create_soft_ui_theme,
        )

        # All imports successful
        assert True

    def test_theme_vibe_integration(self):
        """Theme and vibe systems should work together."""
        from gemini_mcp.theme_factories import (
            create_brutalist_theme,
            get_recommended_vibes,
            get_vibe_compatibility,
        )

        # Get recommended vibes for brutalist
        vibes = get_recommended_vibes("brutalist")
        assert len(vibes) == 4

        # Check compatibility with top recommendation
        top_vibe = vibes[0]
        score, msg = get_vibe_compatibility("brutalist", top_vibe)
        assert score >= 3  # Should be at least neutral

        # Create theme
        theme = create_brutalist_theme()
        assert theme is not None
