"""
MAESTRO Flow Controller - Phase 2

Controls the flow of interview questions through skip rules
and follow-up triggers. Evaluates conditional display rules
and manages question navigation.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Callable, ClassVar

from gemini_mcp.maestro.models import QuestionCategory

if TYPE_CHECKING:
    from gemini_mcp.maestro.models import InterviewState

logger = logging.getLogger(__name__)


class FlowController:
    """
    Controls the flow of interview questions.

    Manages:
    - Skip rules: When to skip certain questions/categories
    - Follow-up triggers: Which questions to ask based on answers
    - show_when evaluation: Conditional question display

    Usage:
        controller = FlowController()
        if controller.should_skip("q_industry_type", QuestionCategory.INDUSTRY, state):
            # Skip this question
        follow_ups = controller.get_follow_ups("q_page_type", ["opt_e-commerce"])
    """

    # =========================================================================
    # SKIP RULES
    # =========================================================================

    # Skip rules by question ID: question_id → lambda(state) → bool
    # If lambda returns True, the question should be SKIPPED
    SKIP_RULES_BY_QUESTION: ClassVar[
        dict[str, Callable[["InterviewState"], bool]]
    ] = {
        # Skip technical details if user chose automatic
        "q_border_radius": lambda s: s.get_answer_value("q_technical_level")
        != "opt_yes_technical",
        "q_animation_level": lambda s: s.get_answer_value("q_technical_level")
        != "opt_yes_technical",
        # Skip brand color input if not using brand colors
        "q_brand_primary_color": lambda s: s.get_answer_value("q_color_preference")
        != "opt_brand_colors",
        # Skip content input if not providing content
        "q_content_input": lambda s: s.get_answer_value("q_content_ready")
        != "opt_content_ready",
        # Skip reference adherence if not doing reference-based design
        "q_reference_adherence": lambda s: s.get_answer_value("q_intent_main")
        != "opt_from_reference",
    }

    # Skip rules by category: category → lambda(state) → bool
    # If lambda returns True, the entire category should be SKIPPED
    SKIP_RULES_BY_CATEGORY: ClassVar[
        dict[QuestionCategory, Callable[["InterviewState"], bool]]
    ] = {
        # Skip EXISTING_CONTEXT if user chose new design
        QuestionCategory.EXISTING_CONTEXT: lambda s: s.get_answer_value("q_intent_main")
        == "opt_new_design",
        # Skip INDUSTRY for B2C consumer apps (less formal requirements)
        QuestionCategory.INDUSTRY: lambda s: s.get_answer_value("q_target_audience")
        == "opt_b2c",
        # Skip VIBE_MOOD for simple components (buttons, inputs)
        QuestionCategory.VIBE_MOOD: lambda s: _is_simple_component(s),
        # Skip ACCESSIBILITY if not B2B or internal (less compliance needs)
        QuestionCategory.ACCESSIBILITY: lambda s: s.get_answer_value("q_target_audience")
        not in ["opt_b2b", "opt_internal"],
    }

    # =========================================================================
    # FOLLOW-UP TRIGGERS
    # =========================================================================

    # Follow-up triggers: "question_id:option_value" → [follow_up_question_ids]
    # When a specific option is selected, these questions are added to the queue
    FOLLOW_UP_TRIGGERS: ClassVar[dict[str, list[str]]] = {
        # Intent triggers
        "q_intent_main:opt_from_reference": [
            "q_reference_upload",
            "q_reference_adherence",
        ],
        "q_intent_main:opt_refine_existing": ["q_existing_action"],
        # Scope triggers
        "q_scope_type:opt_full_page": ["q_page_type"],
        "q_scope_type:opt_section": ["q_section_type"],
        "q_scope_type:opt_component": ["q_component_type"],
        # Color preference trigger
        "q_color_preference:opt_brand_colors": ["q_brand_primary_color"],
        # Technical triggers
        "q_technical_level:opt_yes_technical": [
            "q_border_radius",
            "q_animation_level",
        ],
        # Content triggers
        "q_content_ready:opt_content_ready": ["q_content_input"],
    }

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def should_skip(
        self,
        question_id: str,
        category: QuestionCategory,
        state: "InterviewState",
    ) -> bool:
        """
        Check if a question should be skipped.

        Args:
            question_id: The question ID to check
            category: The question's category
            state: Current interview state

        Returns:
            True if the question should be skipped
        """
        # Check category-level skip rules first
        category_rule = self.SKIP_RULES_BY_CATEGORY.get(category)
        if category_rule is not None:
            try:
                if category_rule(state):
                    logger.debug(f"Skipping {question_id}: category rule triggered")
                    return True
            except Exception as e:
                logger.warning(f"Error evaluating category skip rule: {e}")

        # Check question-level skip rules
        question_rule = self.SKIP_RULES_BY_QUESTION.get(question_id)
        if question_rule is not None:
            try:
                if question_rule(state):
                    logger.debug(f"Skipping {question_id}: question rule triggered")
                    return True
            except Exception as e:
                logger.warning(f"Error evaluating question skip rule: {e}")

        return False

    def get_follow_ups(
        self,
        question_id: str,
        selected_options: list[str],
    ) -> list[str]:
        """
        Get follow-up question IDs triggered by the selected options.

        Args:
            question_id: The answered question ID
            selected_options: List of selected option IDs

        Returns:
            List of follow-up question IDs to add to the queue
        """
        follow_ups = []
        for option_id in selected_options:
            trigger_key = f"{question_id}:{option_id}"
            triggered = self.FOLLOW_UP_TRIGGERS.get(trigger_key, [])
            follow_ups.extend(triggered)

        if follow_ups:
            logger.debug(f"Follow-ups triggered for {question_id}: {follow_ups}")

        return follow_ups

    def evaluate_show_when(
        self,
        condition: str | None,
        state: "InterviewState",
    ) -> bool:
        """
        Evaluate a show_when condition string.

        Supports simple conditions like:
        - "q_scope_type == 'opt_full_page'"
        - "q_target_audience in ['opt_b2b', 'opt_internal']"

        Args:
            condition: The condition string to evaluate
            state: Current interview state

        Returns:
            True if condition passes (question should be shown)
        """
        if condition is None:
            return True

        try:
            return self._eval_condition(condition, state)
        except Exception as e:
            logger.warning(f"Error evaluating show_when '{condition}': {e}")
            return True  # Default to showing the question

    # =========================================================================
    # CONDITION EVALUATION
    # =========================================================================

    def _eval_condition(self, condition: str, state: "InterviewState") -> bool:
        """
        Safely evaluate a condition string.

        Supports:
        - Equality: q_id == 'value'
        - Inequality: q_id != 'value'
        - In list: q_id in ['val1', 'val2']
        - Not in list: q_id not in ['val1', 'val2']
        """
        # Pattern for equality check: q_id == 'value'
        eq_match = re.match(r"(\w+)\s*==\s*['\"](\w+)['\"]", condition)
        if eq_match:
            q_id, expected = eq_match.groups()
            actual = state.get_answer_value(q_id)
            return actual == expected

        # Pattern for inequality: q_id != 'value'
        neq_match = re.match(r"(\w+)\s*!=\s*['\"](\w+)['\"]", condition)
        if neq_match:
            q_id, expected = neq_match.groups()
            actual = state.get_answer_value(q_id)
            return actual != expected

        # Pattern for 'in' check: q_id in ['val1', 'val2']
        in_match = re.match(
            r"(\w+)\s+in\s+\[([^\]]+)\]",
            condition,
        )
        if in_match:
            q_id, values_str = in_match.groups()
            actual = state.get_answer_value(q_id)
            # Parse the list values
            values = [v.strip().strip("'\"") for v in values_str.split(",")]
            return actual in values

        # Pattern for 'not in' check
        not_in_match = re.match(
            r"(\w+)\s+not\s+in\s+\[([^\]]+)\]",
            condition,
        )
        if not_in_match:
            q_id, values_str = not_in_match.groups()
            actual = state.get_answer_value(q_id)
            values = [v.strip().strip("'\"") for v in values_str.split(",")]
            return actual not in values

        # Unknown pattern - default to True
        logger.warning(f"Unknown condition pattern: {condition}")
        return True


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _is_simple_component(state: "InterviewState") -> bool:
    """
    Check if the user is designing a simple component.

    Simple components (buttons, inputs, badges) don't need vibe/mood settings.
    """
    scope = state.get_answer_value("q_scope_type")
    if scope != "opt_component":
        return False

    component_type = state.get_answer_value("q_component_type")
    simple_types = {"opt_button", "opt_input", "opt_badge", "opt_avatar"}
    return component_type in simple_types
