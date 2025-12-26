"""
Phase 7 Tests - FlowController Unit Tests

Comprehensive tests for MAESTRO FlowController:
- Skip rules (question and category level)
- Follow-up triggers
- show_when condition evaluation
"""
import pytest
from unittest.mock import MagicMock

from gemini_mcp.maestro.interview.flow_controller import FlowController, _is_simple_component
from gemini_mcp.maestro.models import QuestionCategory


class MockInterviewState:
    """Mock InterviewState for testing."""

    def __init__(self, answers: dict[str, str] | None = None):
        self._answers = answers or {}

    def get_answer_value(self, question_id: str) -> str | None:
        return self._answers.get(question_id)


class TestFlowControllerInit:
    """Tests for FlowController initialization."""

    def test_skip_rules_by_question_defined(self):
        """SKIP_RULES_BY_QUESTION has expected entries."""
        expected_keys = [
            "q_border_radius",
            "q_animation_level",
            "q_brand_primary_color",
            "q_content_input",
            "q_reference_adherence",
        ]
        for key in expected_keys:
            assert key in FlowController.SKIP_RULES_BY_QUESTION

    def test_skip_rules_by_category_defined(self):
        """SKIP_RULES_BY_CATEGORY has expected entries."""
        expected_cats = [
            QuestionCategory.EXISTING_CONTEXT,
            QuestionCategory.INDUSTRY,
            QuestionCategory.VIBE_MOOD,
            QuestionCategory.ACCESSIBILITY,
        ]
        for cat in expected_cats:
            assert cat in FlowController.SKIP_RULES_BY_CATEGORY

    def test_follow_up_triggers_defined(self):
        """FOLLOW_UP_TRIGGERS has expected entries."""
        expected_keys = [
            "q_intent_main:opt_from_reference",
            "q_intent_main:opt_refine_existing",
            "q_scope_type:opt_full_page",
            "q_scope_type:opt_section",
            "q_scope_type:opt_component",
        ]
        for key in expected_keys:
            assert key in FlowController.FOLLOW_UP_TRIGGERS


class TestSkipRulesByQuestion:
    """Tests for question-level skip rules."""

    def test_skip_border_radius_when_automatic(self):
        """Skip q_border_radius when user chose automatic."""
        controller = FlowController()
        state = MockInterviewState({"q_technical_level": "opt_no_technical"})

        result = controller.should_skip(
            "q_border_radius",
            QuestionCategory.TECHNICAL,
            state,
        )
        assert result is True

    def test_dont_skip_border_radius_when_yes_technical(self):
        """Don't skip q_border_radius when user wants technical options."""
        controller = FlowController()
        state = MockInterviewState({"q_technical_level": "opt_yes_technical"})

        result = controller.should_skip(
            "q_border_radius",
            QuestionCategory.TECHNICAL,
            state,
        )
        assert result is False

    def test_skip_animation_level_when_automatic(self):
        """Skip q_animation_level when user chose automatic."""
        controller = FlowController()
        state = MockInterviewState({"q_technical_level": "opt_no_technical"})

        result = controller.should_skip(
            "q_animation_level",
            QuestionCategory.TECHNICAL,
            state,
        )
        assert result is True

    def test_skip_brand_color_when_not_brand_colors(self):
        """Skip brand color question when not using brand colors."""
        controller = FlowController()
        state = MockInterviewState({"q_color_preference": "opt_blue_corporate"})

        result = controller.should_skip(
            "q_brand_primary_color",
            QuestionCategory.THEME_STYLE,
            state,
        )
        assert result is True

    def test_dont_skip_brand_color_when_brand_colors(self):
        """Don't skip brand color when using brand colors."""
        controller = FlowController()
        state = MockInterviewState({"q_color_preference": "opt_brand_colors"})

        result = controller.should_skip(
            "q_brand_primary_color",
            QuestionCategory.THEME_STYLE,
            state,
        )
        assert result is False

    def test_skip_content_input_when_not_ready(self):
        """Skip content input when content not ready."""
        controller = FlowController()
        state = MockInterviewState({"q_content_ready": "opt_placeholder"})

        result = controller.should_skip(
            "q_content_input",
            QuestionCategory.CONTENT,
            state,
        )
        assert result is True

    def test_skip_reference_adherence_when_not_reference(self):
        """Skip reference adherence when not doing reference design."""
        controller = FlowController()
        state = MockInterviewState({"q_intent_main": "opt_new_design"})

        result = controller.should_skip(
            "q_reference_adherence",
            QuestionCategory.EXISTING_CONTEXT,
            state,
        )
        assert result is True


class TestSkipRulesByCategory:
    """Tests for category-level skip rules."""

    def test_skip_existing_context_for_new_design(self):
        """Skip EXISTING_CONTEXT category for new designs."""
        controller = FlowController()
        state = MockInterviewState({"q_intent_main": "opt_new_design"})

        result = controller.should_skip(
            "q_existing_action",
            QuestionCategory.EXISTING_CONTEXT,
            state,
        )
        assert result is True

    def test_dont_skip_existing_context_for_refine(self):
        """Don't skip EXISTING_CONTEXT for refine intent."""
        controller = FlowController()
        state = MockInterviewState({"q_intent_main": "opt_refine_existing"})

        result = controller.should_skip(
            "q_existing_action",
            QuestionCategory.EXISTING_CONTEXT,
            state,
        )
        assert result is False

    def test_skip_industry_for_b2c(self):
        """Skip INDUSTRY category for B2C audience."""
        controller = FlowController()
        state = MockInterviewState({"q_target_audience": "opt_b2c"})

        result = controller.should_skip(
            "q_industry_type",
            QuestionCategory.INDUSTRY,
            state,
        )
        assert result is True

    def test_dont_skip_industry_for_b2b(self):
        """Don't skip INDUSTRY for B2B audience."""
        controller = FlowController()
        state = MockInterviewState({"q_target_audience": "opt_b2b"})

        result = controller.should_skip(
            "q_industry_type",
            QuestionCategory.INDUSTRY,
            state,
        )
        assert result is False

    def test_skip_accessibility_for_non_b2b(self):
        """Skip ACCESSIBILITY when not B2B or internal."""
        controller = FlowController()
        state = MockInterviewState({"q_target_audience": "opt_b2c"})

        result = controller.should_skip(
            "q_accessibility_level",
            QuestionCategory.ACCESSIBILITY,
            state,
        )
        assert result is True

    def test_dont_skip_accessibility_for_internal(self):
        """Don't skip ACCESSIBILITY for internal apps."""
        controller = FlowController()
        state = MockInterviewState({"q_target_audience": "opt_internal"})

        result = controller.should_skip(
            "q_accessibility_level",
            QuestionCategory.ACCESSIBILITY,
            state,
        )
        assert result is False


class TestSkipVibeMoodForSimpleComponents:
    """Tests for VIBE_MOOD skip logic with simple components."""

    def test_skip_vibe_for_button(self):
        """Skip VIBE_MOOD for button component."""
        controller = FlowController()
        state = MockInterviewState({
            "q_scope_type": "opt_component",
            "q_component_type": "opt_button",
        })

        result = controller.should_skip(
            "q_design_vibe",
            QuestionCategory.VIBE_MOOD,
            state,
        )
        assert result is True

    def test_skip_vibe_for_input(self):
        """Skip VIBE_MOOD for input component."""
        controller = FlowController()
        state = MockInterviewState({
            "q_scope_type": "opt_component",
            "q_component_type": "opt_input",
        })

        result = controller.should_skip(
            "q_design_vibe",
            QuestionCategory.VIBE_MOOD,
            state,
        )
        assert result is True

    def test_dont_skip_vibe_for_navbar(self):
        """Don't skip VIBE_MOOD for navbar (complex component)."""
        controller = FlowController()
        state = MockInterviewState({
            "q_scope_type": "opt_component",
            "q_component_type": "opt_navbar",
        })

        result = controller.should_skip(
            "q_design_vibe",
            QuestionCategory.VIBE_MOOD,
            state,
        )
        assert result is False

    def test_dont_skip_vibe_for_page(self):
        """Don't skip VIBE_MOOD for full page designs."""
        controller = FlowController()
        state = MockInterviewState({
            "q_scope_type": "opt_full_page",
        })

        result = controller.should_skip(
            "q_design_vibe",
            QuestionCategory.VIBE_MOOD,
            state,
        )
        assert result is False


class TestIsSimpleComponent:
    """Tests for _is_simple_component helper function."""

    def test_button_is_simple(self):
        """Button is a simple component."""
        state = MockInterviewState({
            "q_scope_type": "opt_component",
            "q_component_type": "opt_button",
        })
        assert _is_simple_component(state) is True

    def test_input_is_simple(self):
        """Input is a simple component."""
        state = MockInterviewState({
            "q_scope_type": "opt_component",
            "q_component_type": "opt_input",
        })
        assert _is_simple_component(state) is True

    def test_badge_is_simple(self):
        """Badge is a simple component."""
        state = MockInterviewState({
            "q_scope_type": "opt_component",
            "q_component_type": "opt_badge",
        })
        assert _is_simple_component(state) is True

    def test_avatar_is_simple(self):
        """Avatar is a simple component."""
        state = MockInterviewState({
            "q_scope_type": "opt_component",
            "q_component_type": "opt_avatar",
        })
        assert _is_simple_component(state) is True

    def test_card_is_not_simple(self):
        """Card is not a simple component."""
        state = MockInterviewState({
            "q_scope_type": "opt_component",
            "q_component_type": "opt_card",
        })
        assert _is_simple_component(state) is False

    def test_navbar_is_not_simple(self):
        """Navbar is not a simple component."""
        state = MockInterviewState({
            "q_scope_type": "opt_component",
            "q_component_type": "opt_navbar",
        })
        assert _is_simple_component(state) is False

    def test_page_is_not_simple(self):
        """Full page is not a simple component."""
        state = MockInterviewState({
            "q_scope_type": "opt_full_page",
        })
        assert _is_simple_component(state) is False


class TestFollowUpTriggers:
    """Tests for get_follow_ups method."""

    def test_follow_ups_for_reference_intent(self):
        """Reference intent triggers reference questions."""
        controller = FlowController()
        follow_ups = controller.get_follow_ups(
            "q_intent_main",
            ["opt_from_reference"],
        )

        assert "q_reference_upload" in follow_ups
        assert "q_reference_adherence" in follow_ups

    def test_follow_ups_for_refine_intent(self):
        """Refine intent triggers existing action question."""
        controller = FlowController()
        follow_ups = controller.get_follow_ups(
            "q_intent_main",
            ["opt_refine_existing"],
        )

        assert "q_existing_action" in follow_ups

    def test_follow_ups_for_full_page(self):
        """Full page scope triggers page type question."""
        controller = FlowController()
        follow_ups = controller.get_follow_ups(
            "q_scope_type",
            ["opt_full_page"],
        )

        assert "q_page_type" in follow_ups

    def test_follow_ups_for_section(self):
        """Section scope triggers section type question."""
        controller = FlowController()
        follow_ups = controller.get_follow_ups(
            "q_scope_type",
            ["opt_section"],
        )

        assert "q_section_type" in follow_ups

    def test_follow_ups_for_component(self):
        """Component scope triggers component type question."""
        controller = FlowController()
        follow_ups = controller.get_follow_ups(
            "q_scope_type",
            ["opt_component"],
        )

        assert "q_component_type" in follow_ups

    def test_follow_ups_for_brand_colors(self):
        """Brand colors triggers color picker."""
        controller = FlowController()
        follow_ups = controller.get_follow_ups(
            "q_color_preference",
            ["opt_brand_colors"],
        )

        assert "q_brand_primary_color" in follow_ups

    def test_follow_ups_for_technical_yes(self):
        """Technical yes triggers border and animation questions."""
        controller = FlowController()
        follow_ups = controller.get_follow_ups(
            "q_technical_level",
            ["opt_yes_technical"],
        )

        assert "q_border_radius" in follow_ups
        assert "q_animation_level" in follow_ups

    def test_no_follow_ups_for_unknown_option(self):
        """Unknown options return empty list."""
        controller = FlowController()
        follow_ups = controller.get_follow_ups(
            "q_intent_main",
            ["nonexistent_option"],
        )

        assert follow_ups == []

    def test_multiple_options_combine_follow_ups(self):
        """Multiple options combine their follow-ups."""
        controller = FlowController()
        # This is edge case - normally single select, but test the logic
        follow_ups = controller.get_follow_ups(
            "q_scope_type",
            ["opt_full_page", "opt_section"],
        )

        assert "q_page_type" in follow_ups
        assert "q_section_type" in follow_ups


class TestShowWhenEvaluation:
    """Tests for evaluate_show_when condition evaluation."""

    def test_none_condition_returns_true(self):
        """None condition always returns True."""
        controller = FlowController()
        state = MockInterviewState()

        result = controller.evaluate_show_when(None, state)
        assert result is True

    def test_equality_condition_true(self):
        """Equality condition evaluates correctly (match)."""
        controller = FlowController()
        state = MockInterviewState({"q_scope_type": "opt_full_page"})

        result = controller.evaluate_show_when(
            "q_scope_type == 'opt_full_page'",
            state,
        )
        assert result is True

    def test_equality_condition_false(self):
        """Equality condition evaluates correctly (no match)."""
        controller = FlowController()
        state = MockInterviewState({"q_scope_type": "opt_section"})

        result = controller.evaluate_show_when(
            "q_scope_type == 'opt_full_page'",
            state,
        )
        assert result is False

    def test_inequality_condition_true(self):
        """Inequality condition evaluates correctly (match)."""
        controller = FlowController()
        state = MockInterviewState({"q_scope_type": "opt_section"})

        result = controller.evaluate_show_when(
            "q_scope_type != 'opt_full_page'",
            state,
        )
        assert result is True

    def test_inequality_condition_false(self):
        """Inequality condition evaluates correctly (no match)."""
        controller = FlowController()
        state = MockInterviewState({"q_scope_type": "opt_full_page"})

        result = controller.evaluate_show_when(
            "q_scope_type != 'opt_full_page'",
            state,
        )
        assert result is False

    def test_in_condition_true(self):
        """'in' condition evaluates correctly (match)."""
        controller = FlowController()
        state = MockInterviewState({"q_target_audience": "opt_b2b"})

        result = controller.evaluate_show_when(
            "q_target_audience in ['opt_b2b', 'opt_internal']",
            state,
        )
        assert result is True

    def test_in_condition_false(self):
        """'in' condition evaluates correctly (no match)."""
        controller = FlowController()
        state = MockInterviewState({"q_target_audience": "opt_b2c"})

        result = controller.evaluate_show_when(
            "q_target_audience in ['opt_b2b', 'opt_internal']",
            state,
        )
        assert result is False

    def test_not_in_condition_true(self):
        """'not in' condition evaluates correctly (match)."""
        controller = FlowController()
        state = MockInterviewState({"q_target_audience": "opt_b2c"})

        result = controller.evaluate_show_when(
            "q_target_audience not in ['opt_b2b', 'opt_internal']",
            state,
        )
        assert result is True

    def test_not_in_condition_false(self):
        """'not in' condition evaluates correctly (no match)."""
        controller = FlowController()
        state = MockInterviewState({"q_target_audience": "opt_b2b"})

        result = controller.evaluate_show_when(
            "q_target_audience not in ['opt_b2b', 'opt_internal']",
            state,
        )
        assert result is False

    def test_double_quote_in_condition(self):
        """Condition with double quotes works."""
        controller = FlowController()
        state = MockInterviewState({"q_scope_type": "opt_full_page"})

        result = controller.evaluate_show_when(
            'q_scope_type == "opt_full_page"',
            state,
        )
        assert result is True

    def test_unknown_condition_defaults_true(self):
        """Unknown condition pattern defaults to True."""
        controller = FlowController()
        state = MockInterviewState()

        result = controller.evaluate_show_when(
            "some_unknown_pattern",
            state,
        )
        assert result is True


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_state(self):
        """Empty state handles gracefully."""
        controller = FlowController()
        state = MockInterviewState()

        # Should not raise
        result = controller.should_skip(
            "q_border_radius",
            QuestionCategory.TECHNICAL,
            state,
        )
        # Without q_technical_level answer, rule should trigger skip
        assert result is True

    def test_question_without_skip_rule(self):
        """Questions without skip rules return False."""
        controller = FlowController()
        state = MockInterviewState()

        result = controller.should_skip(
            "q_intent_main",  # No skip rule for this
            QuestionCategory.INTENT,
            state,
        )
        assert result is False

    def test_category_without_skip_rule(self):
        """Categories without skip rules don't skip."""
        controller = FlowController()
        state = MockInterviewState()

        result = controller.should_skip(
            "q_content_language",
            QuestionCategory.LANGUAGE,  # No category skip rule
            state,
        )
        assert result is False

    def test_none_answer_handling(self):
        """None answers handled gracefully."""
        controller = FlowController()
        state = MockInterviewState({"q_scope_type": None})

        # Should not raise
        result = controller.evaluate_show_when(
            "q_scope_type == 'opt_full_page'",
            state,
        )
        assert result is False  # None != 'opt_full_page'


class TestConditionParsing:
    """Tests for regex-based condition parsing."""

    def test_parse_equality_with_spaces(self):
        """Equality with various spacing works."""
        controller = FlowController()
        state = MockInterviewState({"q_test": "value"})

        # Various spacing
        assert controller.evaluate_show_when("q_test == 'value'", state) is True
        assert controller.evaluate_show_when("q_test=='value'", state) is True
        assert controller.evaluate_show_when("q_test  ==  'value'", state) is True

    def test_parse_in_with_various_lists(self):
        """'in' condition parses various list formats."""
        controller = FlowController()
        state = MockInterviewState({"q_test": "val2"})

        # Various formats
        assert controller.evaluate_show_when(
            "q_test in ['val1', 'val2']",
            state,
        ) is True
        assert controller.evaluate_show_when(
            "q_test in ['val1','val2','val3']",
            state,
        ) is True
