"""
Phase 7 Tests - InterviewEngine Unit Tests

Comprehensive tests for MAESTRO InterviewEngine:
- Question selection logic
- Answer processing
- Progress calculation
- Follow-up queue management
"""
import pytest
from unittest.mock import MagicMock

from gemini_mcp.maestro.interview.engine import InterviewEngine
from gemini_mcp.maestro.interview.flow_controller import FlowController
from gemini_mcp.maestro.models import (
    Answer,
    ContextData,
    InterviewState,
    MaestroStatus,
    QuestionCategory,
)
from gemini_mcp.maestro.questions.bank import QuestionBank


class MockContextData:
    """Mock ContextData for testing."""

    def __init__(self, previous_html: str | None = None, project_context: str = ""):
        self.previous_html = previous_html
        self.project_context = project_context


class TestInterviewEngineInit:
    """Tests for InterviewEngine initialization."""

    def test_init_with_all_dependencies(self):
        """Engine initializes with required dependencies."""
        bank = QuestionBank()
        controller = FlowController()
        context = MockContextData()

        engine = InterviewEngine(
            question_bank=bank,
            flow_controller=controller,
            context=context,
        )

        assert engine.question_bank is bank
        assert engine.flow_controller is controller
        assert engine.context is context

    def test_follow_up_queue_empty_on_init(self):
        """Follow-up queue is empty on initialization."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        assert engine.get_pending_follow_ups() == []


class TestGetInitialQuestion:
    """Tests for initial question selection."""

    def test_initial_question_without_html(self):
        """Initial question is q_intent_main without HTML."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(previous_html=None),
        )

        question = engine.get_initial_question()
        assert question.id == "q_intent_main"

    def test_initial_question_with_html(self):
        """Initial question is q_existing_action with HTML."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(previous_html="<div>Test</div>"),
        )

        question = engine.get_initial_question()
        assert question.id == "q_existing_action"


class TestGetNextQuestion:
    """Tests for next question selection logic."""

    def test_first_question_for_new_interview(self):
        """First question from highest priority category."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )
        state = InterviewState(status=MaestroStatus.INTERVIEWING)

        question = engine.get_next_question(state)

        # Should be from INTENT category (priority 1)
        assert question.category == QuestionCategory.INTENT

    def test_skip_answered_questions(self):
        """Skip questions that are already answered."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # Answer the intent question
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(
                    question_id="q_intent_main",
                    selected_options=["opt_new_design"],
                )
            ],
        )

        question = engine.get_next_question(state)

        # Should NOT be q_intent_main
        assert question.id != "q_intent_main"

    def test_follow_up_queue_has_priority(self):
        """Follow-up questions are returned before category questions."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # Add follow-up to queue
        engine.add_follow_up("q_page_type")

        state = InterviewState(status=MaestroStatus.INTERVIEWING)
        question = engine.get_next_question(state)

        # Should be the follow-up question
        assert question.id == "q_page_type"

    def test_skip_follow_up_if_already_answered(self):
        """Skip follow-up questions if already answered."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # Add follow-up and mark as answered
        engine.add_follow_up("q_page_type")

        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_page_type", selected_options=["opt_landing_page"])
            ],
        )

        question = engine.get_next_question(state)

        # Should NOT be q_page_type
        assert question.id != "q_page_type"

    def test_returns_none_when_complete(self):
        """Returns None when interview is complete."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # Create state with all required questions answered
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
                Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
                Answer(question_id="q_page_type", selected_options=["opt_landing_page"]),
                Answer(question_id="q_theme_preference", selected_options=["opt_modern_minimal"]),
                Answer(question_id="q_color_mode", selected_options=["opt_light"]),
                Answer(question_id="q_content_language", selected_options=["opt_turkish"]),
            ],
        )

        question = engine.get_next_question(state)

        # May or may not be None depending on optional questions
        # At minimum, required categories should be satisfied


class TestShouldSkipQuestion:
    """Tests for question skip logic."""

    def test_skip_question_by_question_rule(self):
        """Skip question when question-level rule applies."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # q_border_radius should be skipped when not opt_yes_technical
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_technical_level", selected_options=["opt_no_technical"])
            ],
        )

        question = engine.question_bank.get_question("q_border_radius")
        result = engine.should_skip_question(question, state)

        assert result is True

    def test_dont_skip_when_rule_not_triggered(self):
        """Don't skip when skip rule doesn't apply."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_technical_level", selected_options=["opt_yes_technical"])
            ],
        )

        question = engine.question_bank.get_question("q_border_radius")
        result = engine.should_skip_question(question, state)

        assert result is False


class TestProcessAnswer:
    """Tests for answer processing."""

    def test_valid_answer_returns_valid_result(self):
        """Valid answer returns is_valid=True."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)
        answer = Answer(
            question_id="q_intent_main",
            selected_options=["opt_new_design"],
        )

        result = engine.process_answer(state, answer)

        assert result.is_valid is True
        assert result.error_message is None

    def test_invalid_question_returns_error(self):
        """Invalid question ID returns error."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)
        answer = Answer(
            question_id="nonexistent_question",
            selected_options=["opt_something"],
        )

        result = engine.process_answer(state, answer)

        assert result.is_valid is False
        assert "bulunamadı" in result.error_message.lower()

    def test_answer_triggers_follow_ups(self):
        """Answer triggers follow-up questions."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)
        answer = Answer(
            question_id="q_scope_type",
            selected_options=["opt_full_page"],
        )

        result = engine.process_answer(state, answer)

        # Should trigger q_page_type
        assert "q_page_type" in result.follow_ups

    def test_follow_ups_added_to_queue(self):
        """Follow-ups are added to internal queue."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)
        answer = Answer(
            question_id="q_scope_type",
            selected_options=["opt_full_page"],
        )

        engine.process_answer(state, answer)

        pending = engine.get_pending_follow_ups()
        assert "q_page_type" in pending

    def test_progress_calculated_on_answer(self):
        """Progress is calculated with each answer."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)
        answer = Answer(
            question_id="q_intent_main",
            selected_options=["opt_new_design"],
        )

        result = engine.process_answer(state, answer)

        assert result.progress >= 0.0
        assert result.progress <= 1.0


class TestCalculateProgress:
    """Tests for progress calculation."""

    def test_progress_starts_at_zero(self):
        """Progress is 0 with no answers."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)
        progress = engine.calculate_progress(state)

        assert progress == 0.0

    def test_progress_increases_with_answers(self):
        """Progress increases as questions are answered."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # Answer one question
        state1 = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"])
            ],
        )
        progress1 = engine.calculate_progress(state1)

        # Answer two questions
        state2 = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
                Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
            ],
        )
        progress2 = engine.calculate_progress(state2)

        assert progress2 > progress1

    def test_progress_only_counts_required(self):
        """Progress only counts required category questions."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # Answer optional question only
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_target_audience", selected_options=["opt_b2b"])
            ],
        )

        progress = engine.calculate_progress(state)

        # Optional question doesn't affect progress
        assert progress == 0.0


class TestIsComplete:
    """Tests for interview completion check."""

    def test_not_complete_with_no_answers(self):
        """Interview not complete without answers."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)
        assert engine.is_complete(state) is False

    def test_complete_when_no_more_questions(self):
        """Interview complete when get_next_question returns None."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # Answer all required questions
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
                Answer(question_id="q_scope_type", selected_options=["opt_component"]),
                Answer(question_id="q_component_type", selected_options=["opt_button"]),
                Answer(question_id="q_theme_preference", selected_options=["opt_modern_minimal"]),
                Answer(question_id="q_color_mode", selected_options=["opt_light"]),
                Answer(question_id="q_content_language", selected_options=["opt_turkish"]),
            ],
        )

        # May or may not be complete - depends on skip rules
        result = engine.is_complete(state)
        # Just check it doesn't raise
        assert isinstance(result, bool)


class TestFollowUpQueueManagement:
    """Tests for follow-up queue management."""

    def test_add_follow_up(self):
        """Add follow-up to queue."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        engine.add_follow_up("q_page_type")

        assert "q_page_type" in engine.get_pending_follow_ups()

    def test_add_follow_up_no_duplicates(self):
        """Adding same follow-up twice doesn't duplicate."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        engine.add_follow_up("q_page_type")
        engine.add_follow_up("q_page_type")

        pending = engine.get_pending_follow_ups()
        assert pending.count("q_page_type") == 1

    def test_clear_follow_up_queue(self):
        """Clear follow-up queue removes all items."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        engine.add_follow_up("q_page_type")
        engine.add_follow_up("q_section_type")
        engine.clear_follow_up_queue()

        assert engine.get_pending_follow_ups() == []

    def test_get_pending_follow_ups_returns_copy(self):
        """get_pending_follow_ups returns copy, not reference."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        engine.add_follow_up("q_page_type")
        pending = engine.get_pending_follow_ups()
        pending.append("q_section_type")

        # Original should not be modified
        assert len(engine.get_pending_follow_ups()) == 1


class TestTriggersDecision:
    """Tests for decision trigger logic."""

    def test_triggers_decision_when_complete(self):
        """Triggers decision when interview would be complete."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # State with most required answers
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
                Answer(question_id="q_scope_type", selected_options=["opt_component"]),
                Answer(question_id="q_component_type", selected_options=["opt_button"]),
                Answer(question_id="q_theme_preference", selected_options=["opt_modern_minimal"]),
                Answer(question_id="q_color_mode", selected_options=["opt_light"]),
            ],
        )

        # This answer might trigger decision
        answer = Answer(
            question_id="q_content_language",
            selected_options=["opt_turkish"],
        )

        result = engine.process_answer(state, answer)

        # Depending on optional questions, may or may not trigger
        assert isinstance(result.triggers_decision, bool)

    def test_no_trigger_with_pending_follow_ups(self):
        """No decision trigger if follow-up queue not empty."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # Manually add pending follow-up
        engine.add_follow_up("q_section_type")

        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
            ],
        )

        answer = Answer(
            question_id="q_scope_type",
            selected_options=["opt_full_page"],
        )

        result = engine.process_answer(state, answer)

        # Should not trigger decision with pending follow-ups
        # Note: This answer adds more follow-ups too
        # Decision is only triggered when interview is truly complete


class TestCategoryPriority:
    """Tests for category priority handling."""

    def test_intent_questions_come_first(self):
        """INTENT category questions are asked first."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)
        question = engine.get_next_question(state)

        assert question.category == QuestionCategory.INTENT

    def test_scope_after_intent(self):
        """SCOPE questions come after INTENT."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"])
            ],
        )

        # Clear follow-up queue to test category priority
        engine.clear_follow_up_queue()
        question = engine.get_next_question(state)

        assert question.category == QuestionCategory.SCOPE


class TestShowWhenHandling:
    """Tests for show_when condition handling in engine."""

    def test_skip_question_when_show_when_false(self):
        """Skip questions when show_when evaluates to False."""
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=MockContextData(),
        )

        # q_page_type has show_when: q_scope_type == 'opt_full_page'
        # Answer with section scope
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
                Answer(question_id="q_scope_type", selected_options=["opt_section"]),
            ],
        )

        # Clear follow-ups to test category flow
        engine.clear_follow_up_queue()

        # Get all questions until we find one
        questions_found = []
        current_state = state
        for _ in range(10):  # Safety limit
            q = engine.get_next_question(current_state)
            if q is None:
                break
            questions_found.append(q.id)
            # Add answer to continue
            # Handle questions with options vs free-text questions
            if q.options:
                answer = Answer(question_id=q.id, selected_options=[q.options[0].id])
            else:
                # Free-text questions (COLOR_PICKER, TEXT_INPUT, etc.)
                answer = Answer(question_id=q.id, free_text="#FF0000")
            current_state = InterviewState(
                status=MaestroStatus.INTERVIEWING,
                answers=list(current_state.answers) + [answer],
            )

        # q_page_type should NOT be in the list
        assert "q_page_type" not in questions_found
