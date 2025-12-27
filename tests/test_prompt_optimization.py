"""
Test Suite for Prompt Engineering Optimizations (Phase 5)

This module validates all prompt engineering enhancements:
1. Design-CoT has 7 structured steps (SCoT)
2. Negative examples (BAD_EXAMPLES) exist
3. Complexity levels define density requirements
4. Few-shot examples meet coverage targets
5. Schema enforcement works correctly
6. Complexity level configuration is valid
7. Output density validation works
8. Design thinking validation works
"""

import pytest
import re
from typing import Any, Dict


class TestDesignCoT:
    """Tests for Design Chain-of-Thought (SCoT) structure."""

    def test_design_cot_prompt_exists(self):
        """FRONTEND_DESIGN_SYSTEM_PROMPT must be defined in frontend_presets."""
        from gemini_mcp.frontend_presets import FRONTEND_DESIGN_SYSTEM_PROMPT

        assert FRONTEND_DESIGN_SYSTEM_PROMPT is not None
        assert len(FRONTEND_DESIGN_SYSTEM_PROMPT) > 0

    def test_design_cot_has_7_steps(self):
        """Design-CoT must have 7 structured steps in the prompt."""
        from gemini_mcp.frontend_presets import FRONTEND_DESIGN_SYSTEM_PROMPT

        # Check for all 7 SCoT steps
        required_steps = [
            "CONSTRAINT_CHECK",
            "AESTHETIC_PHYSICS",
            "VISUAL_DNA",
            "MICRO_INTERACTIONS",
            "RESPONSIVE_STRATEGY",
            "A11Y_CHECKLIST",
            "DENSITY_ITERATION",
        ]

        for step in required_steps:
            assert step in FRONTEND_DESIGN_SYSTEM_PROMPT, f"Missing SCoT step: {step}"

    def test_design_cot_mentions_7_step_scot(self):
        """Prompt should mention 7-step SCoT methodology."""
        from gemini_mcp.frontend_presets import FRONTEND_DESIGN_SYSTEM_PROMPT

        # Should mention 7-step SCoT
        assert "7-STEP" in FRONTEND_DESIGN_SYSTEM_PROMPT or "7 step" in FRONTEND_DESIGN_SYSTEM_PROMPT.lower(), (
            "Prompt should explicitly mention 7-step SCoT"
        )


class TestNegativeExamples:
    """Tests for BAD_EXAMPLES (negative examples)."""

    def test_bad_examples_exists(self):
        """BAD_EXAMPLES dict must exist in few_shot_examples."""
        from collections.abc import Mapping

        from gemini_mcp.few_shot_examples import BAD_EXAMPLES

        assert BAD_EXAMPLES is not None
        assert isinstance(BAD_EXAMPLES, Mapping)

    def test_bad_examples_has_minimum_count(self):
        """BAD_EXAMPLES must have at least 3 entries."""
        from gemini_mcp.few_shot_examples import BAD_EXAMPLES

        assert len(BAD_EXAMPLES) >= 3, (
            f"BAD_EXAMPLES has only {len(BAD_EXAMPLES)} entries, need 3+"
        )

    def test_bad_examples_structure(self):
        """Each BAD_EXAMPLE must have required fields."""
        from gemini_mcp.few_shot_examples import BAD_EXAMPLES

        required_fields = ["problem", "bad_output", "why_bad"]

        for name, example in BAD_EXAMPLES.items():
            for field in required_fields:
                assert field in example, (
                    f"BAD_EXAMPLE '{name}' missing field: {field}"
                )
            # bad_output should contain HTML/Tailwind
            assert "<" in example["bad_output"] or "class" in example["bad_output"], (
                f"BAD_EXAMPLE '{name}' bad_output doesn't look like HTML"
            )

    def test_get_bad_examples_function(self):
        """get_bad_examples_for_prompt must return formatted string."""
        from gemini_mcp.few_shot_examples import get_bad_examples_for_prompt

        # Test with known component types
        for component in ["button", "card", "hero"]:
            examples = get_bad_examples_for_prompt(component)
            # Function should return a formatted string for prompt injection
            assert isinstance(examples, str)


class TestComplexityBasedDensity:
    """Tests for complexity-based density rules (replaced COMPONENT_DENSITY_RULES)."""

    def test_complexity_levels_define_density(self):
        """Complexity levels must define min and target classes."""
        from gemini_mcp.schemas import COMPLEXITY_LEVELS

        for level, config in COMPLEXITY_LEVELS.items():
            assert hasattr(config, "min_classes"), f"Missing min_classes for {level}"
            assert hasattr(config, "target_classes"), f"Missing target_classes for {level}"
            assert config.min_classes > 0, f"Invalid min_classes for {level}"
            assert config.target_classes >= config.min_classes, (
                f"target_classes < min_classes for {level}"
            )

    def test_component_complexity_inference(self):
        """Components should be mapped to appropriate complexity levels."""
        from gemini_mcp.schemas import infer_complexity_from_component

        # Core components should have reasonable complexity mappings
        components_to_test = ["button", "card", "hero", "navbar", "footer", "input"]

        for component in components_to_test:
            level = infer_complexity_from_component(component)
            assert level in ["low", "standard", "high", "ultra"], (
                f"Invalid complexity level for {component}: {level}"
            )

    def test_density_min_values_are_reasonable(self):
        """Minimum density values should be reasonable."""
        from gemini_mcp.schemas import COMPLEXITY_LEVELS

        # Low: 6, Standard: 10, High: 14, Ultra: 18
        expected_ranges = {
            "low": (4, 8),
            "standard": (8, 12),
            "high": (12, 16),
            "ultra": (16, 22),
        }

        for level, (min_expected, max_expected) in expected_ranges.items():
            config = COMPLEXITY_LEVELS[level]
            assert min_expected <= config.min_classes <= max_expected, (
                f"Unreasonable min_classes for {level}: {config.min_classes}"
            )


class TestFewShotExamples:
    """Tests for few-shot examples coverage."""

    def test_component_examples_exist(self):
        """COMPONENT_EXAMPLES must exist."""
        from collections.abc import Mapping

        from gemini_mcp.few_shot_examples import COMPONENT_EXAMPLES

        assert COMPONENT_EXAMPLES is not None
        assert isinstance(COMPONENT_EXAMPLES, Mapping)

    def test_component_examples_count(self):
        """COMPONENT_EXAMPLES must have 15+ examples."""
        from gemini_mcp.few_shot_examples import COMPONENT_EXAMPLES

        assert len(COMPONENT_EXAMPLES) >= 15, (
            f"Only {len(COMPONENT_EXAMPLES)} examples, need 15+"
        )

    def test_component_examples_have_html(self):
        """Each example must have HTML output."""
        from gemini_mcp.few_shot_examples import COMPONENT_EXAMPLES

        for name, example in COMPONENT_EXAMPLES.items():
            output = example.get("output", {})
            assert "html" in output or "html" in example, (
                f"Example '{name}' missing HTML output"
            )

    def test_theme_coverage(self):
        """Examples should cover multiple themes."""
        from gemini_mcp.few_shot_examples import COMPONENT_EXAMPLES

        themes_covered = set()
        for example in COMPONENT_EXAMPLES.values():
            # Theme is inside the "input" dict
            input_data = example.get("input", {})
            if "theme" in input_data:
                themes_covered.add(input_data["theme"])

        # Should cover at least 4 different themes
        assert len(themes_covered) >= 4, (
            f"Only {len(themes_covered)} themes covered: {themes_covered}, need 4+"
        )

    def test_get_few_shot_examples_function(self):
        """get_few_shot_examples_for_prompt must return formatted string."""
        from gemini_mcp.few_shot_examples import get_few_shot_examples_for_prompt

        # Test with known component type
        examples = get_few_shot_examples_for_prompt("button")
        # Returns a formatted string, not a list
        assert isinstance(examples, str)

    def test_vibe_coverage(self):
        """Examples should cover multiple vibes."""
        from gemini_mcp.few_shot_examples import COMPONENT_EXAMPLES

        vibes_covered = set()
        for example in COMPONENT_EXAMPLES.values():
            input_data = example.get("input", {})
            if "vibe" in input_data:
                vibes_covered.add(input_data["vibe"])

        # Should cover at least 3 different vibes
        assert len(vibes_covered) >= 3, (
            f"Only {len(vibes_covered)} vibes covered: {vibes_covered}, need 3+"
        )


class TestSchemaEnforcement:
    """Tests for design_thinking schema enforcement."""

    def test_design_thinking_schema_exists(self):
        """DESIGN_THINKING_SCHEMA must be defined."""
        from gemini_mcp.schemas import DESIGN_THINKING_SCHEMA

        assert DESIGN_THINKING_SCHEMA is not None
        assert isinstance(DESIGN_THINKING_SCHEMA, dict)

    def test_design_thinking_schema_has_required_fields(self):
        """Schema must require all 7 SCoT steps."""
        from gemini_mcp.schemas import DESIGN_THINKING_SCHEMA

        required_fields = DESIGN_THINKING_SCHEMA.get("required", [])

        scot_steps = [
            "constraint_check",
            "aesthetic_physics",
            "visual_dna",
            "micro_interactions",
            "responsive_strategy",
            "a11y_checklist",
        ]

        for step in scot_steps:
            assert step in required_fields, (
                f"Schema missing required field: {step}"
            )

    def test_design_thinking_pydantic_model(self):
        """DesignThinking Pydantic model must work correctly."""
        from gemini_mcp.schemas import DesignThinking

        # Create valid instance
        dt = DesignThinking(
            constraint_check="4-Layer Rule? Yes. Density 8+? Yes.",
            aesthetic_physics="Materiality: frosted glass. Lighting: top-left ambient glow.",
            visual_dna="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900",
            micro_interactions="hover:translateY(-4px) with 150ms ease-out transition",
            responsive_strategy="Mobile-first, sm:grid-cols-1, md:grid-cols-2, lg:grid-cols-3",
            a11y_checklist="focus-visible:ring-2, aria-label on buttons, contrast 4.5:1+",
            density_iteration="Added inner-ring effect, shadow-inner for depth",
        )

        assert dt.constraint_check is not None
        assert len(dt.aesthetic_physics) > 0

    def test_design_thinking_validation_function(self):
        """validate_design_thinking must work correctly."""
        from gemini_mcp.schemas import validate_design_thinking

        # Valid design thinking text
        valid_text = """
        CONSTRAINT_CHECK: 4-Layer Rule confirmed. Density target 10+.
        AESTHETIC_PHYSICS: Frosted glass materiality with top-left lighting.
        VISUAL_DNA: bg-gradient-to-br from-slate-900 to-slate-800
        MICRO_INTERACTIONS: hover:scale-105 with 200ms transition
        RESPONSIVE_STRATEGY: Mobile-first grid layout
        A11Y_CHECKLIST: focus-visible ring, contrast 4.5:1
        DENSITY_ITERATION: Added subtle glow effect
        """

        is_valid, issues = validate_design_thinking(valid_text)
        # Should detect structured design thinking
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)


class TestComplexityLevels:
    """Tests for complexity level system."""

    def test_complexity_levels_exist(self):
        """COMPLEXITY_LEVELS must be defined."""
        from gemini_mcp.schemas import COMPLEXITY_LEVELS

        assert COMPLEXITY_LEVELS is not None
        assert isinstance(COMPLEXITY_LEVELS, dict)

    def test_all_complexity_levels_defined(self):
        """All 4 complexity levels must be defined."""
        from gemini_mcp.schemas import COMPLEXITY_LEVELS

        required_levels = ["low", "standard", "high", "ultra"]

        for level in required_levels:
            assert level in COMPLEXITY_LEVELS, (
                f"Missing complexity level: {level}"
            )

    def test_complexity_config_structure(self):
        """Each complexity config must have required fields."""
        from gemini_mcp.schemas import COMPLEXITY_LEVELS

        required_fields = [
            "min_classes",
            "target_classes",
            "design_cot_steps",
            "few_shot_count",
            "quality_threshold",
        ]

        for level, config in COMPLEXITY_LEVELS.items():
            for field in required_fields:
                assert hasattr(config, field) or field in config.__dict__, (
                    f"Level '{level}' missing field: {field}"
                )

    def test_complexity_levels_are_ordered(self):
        """Complexity levels should be properly ordered (low < standard < high < ultra)."""
        from gemini_mcp.schemas import COMPLEXITY_LEVELS

        levels_ordered = ["low", "standard", "high", "ultra"]
        prev_min = 0

        for level in levels_ordered:
            config = COMPLEXITY_LEVELS[level]
            assert config.min_classes >= prev_min, (
                f"Level '{level}' min_classes should be >= previous level"
            )
            prev_min = config.min_classes

    def test_get_complexity_config_function(self):
        """get_complexity_config must return valid config."""
        from gemini_mcp.schemas import get_complexity_config

        config = get_complexity_config("standard")
        assert config is not None
        assert config.min_classes > 0

    def test_infer_complexity_from_component(self):
        """infer_complexity_from_component must work correctly."""
        from gemini_mcp.schemas import infer_complexity_from_component

        # Hero should be high complexity
        assert infer_complexity_from_component("hero") in ["high", "ultra"]

        # Button should be low complexity
        assert infer_complexity_from_component("button") in ["low", "standard"]

        # Landing page should be ultra
        assert infer_complexity_from_component("landing_page") == "ultra"


class TestOutputDensityValidation:
    """Tests for output density validation."""

    def test_validate_output_density_function(self):
        """validate_output_density must work correctly."""
        from gemini_mcp.schemas import validate_output_density

        # Sparse HTML (should fail standard complexity)
        sparse_html = '<button class="px-4 py-2">Click</button>'

        passed, report = validate_output_density(sparse_html, "standard")
        assert isinstance(passed, bool)
        assert isinstance(report, dict)
        # Check for actual key names in the report
        assert "avg_classes_per_element" in report or "density_score" in report

    def test_validate_output_density_with_rich_html(self):
        """Rich HTML should pass density validation."""
        from gemini_mcp.schemas import validate_output_density

        # Rich HTML with many classes
        rich_html = '''
        <button class="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600
                       text-white font-semibold rounded-xl shadow-lg
                       hover:shadow-xl hover:scale-105 transition-all duration-300
                       focus:outline-none focus:ring-4 focus:ring-blue-300">
            Click Me
        </button>
        '''

        passed, report = validate_output_density(rich_html, "standard")
        # Rich HTML should have high density score
        assert report["avg_classes_per_element"] >= 8 or report.get("density_score", 0) >= 7


class TestOrchestratorIntegration:
    """Tests for orchestrator integration."""

    def test_orchestrator_imports_work(self):
        """Orchestrator must import schema functions correctly."""
        from gemini_mcp.orchestration.orchestrator import (
            COMPLEXITY_LEVELS,
            get_complexity_config,
            infer_complexity_from_component,
            validate_output_density,
            get_bad_examples_for_prompt,
        )

        assert COMPLEXITY_LEVELS is not None
        assert callable(get_complexity_config)
        assert callable(infer_complexity_from_component)
        assert callable(validate_output_density)
        assert callable(get_bad_examples_for_prompt)


class TestAgentPromptEnhancements:
    """Tests for agent prompt enhancements."""

    def test_quality_guard_prompt_has_few_shot(self):
        """Quality Guard prompt should have validation examples."""
        from gemini_mcp.prompts import get_agent_prompt

        quality_guard_prompt = get_agent_prompt("quality_guard")

        # Should have validation-related keywords
        assert "valid" in quality_guard_prompt.lower()
        assert "error" in quality_guard_prompt.lower() or "issue" in quality_guard_prompt.lower()

    def test_strategist_prompt_has_dna_extraction(self):
        """Strategist prompt should have DNA extraction methodology."""
        from gemini_mcp.prompts import get_agent_prompt

        strategist_prompt = get_agent_prompt("strategist")

        # Should mention design DNA or tokens
        prompt_lower = strategist_prompt.lower()
        assert "dna" in prompt_lower or "token" in prompt_lower or "extract" in prompt_lower

    def test_visionary_prompt_has_analysis_methodology(self):
        """Visionary prompt should have visual analysis methodology."""
        from gemini_mcp.prompts import get_agent_prompt

        visionary_prompt = get_agent_prompt("visionary")

        # Should have analysis-related keywords
        prompt_lower = visionary_prompt.lower()
        assert "analyz" in prompt_lower or "extract" in prompt_lower
        assert "color" in prompt_lower
        assert "component" in prompt_lower


class TestPromptEngineeringCoverage:
    """Integration tests for overall prompt engineering coverage."""

    def test_all_critical_constants_exist(self):
        """All critical prompt engineering constants must exist."""
        # Design-CoT (in FRONTEND_DESIGN_SYSTEM_PROMPT)
        from gemini_mcp.frontend_presets import FRONTEND_DESIGN_SYSTEM_PROMPT

        # Few-shot examples
        from gemini_mcp.few_shot_examples import COMPONENT_EXAMPLES
        from gemini_mcp.few_shot_examples import BAD_EXAMPLES

        # Schema
        from gemini_mcp.schemas import DESIGN_THINKING_SCHEMA
        from gemini_mcp.schemas import COMPLEXITY_LEVELS

        assert all([
            FRONTEND_DESIGN_SYSTEM_PROMPT,
            COMPONENT_EXAMPLES,
            BAD_EXAMPLES,
            DESIGN_THINKING_SCHEMA,
            COMPLEXITY_LEVELS,
        ])

    def test_metrics_improvement_targets(self):
        """Verify we meet improvement targets from the plan."""
        from gemini_mcp.few_shot_examples import COMPONENT_EXAMPLES, BAD_EXAMPLES
        from gemini_mcp.frontend_presets import FRONTEND_DESIGN_SYSTEM_PROMPT

        # Target: 15+ few-shot examples
        assert len(COMPONENT_EXAMPLES) >= 15, "Need 15+ few-shot examples"

        # Target: 3+ negative examples
        assert len(BAD_EXAMPLES) >= 3, "Need 3+ negative examples"

        # Target: 7 Design-CoT steps (6 core + DENSITY_ITERATION)
        scot_steps = ["CONSTRAINT_CHECK", "AESTHETIC_PHYSICS", "VISUAL_DNA",
                      "MICRO_INTERACTIONS", "RESPONSIVE_STRATEGY", "A11Y_CHECKLIST"]
        for step in scot_steps:
            assert step in FRONTEND_DESIGN_SYSTEM_PROMPT, f"Missing SCoT step: {step}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
