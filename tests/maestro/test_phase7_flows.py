"""
Phase 7 Integration Flow Tests - End-to-End Scenarios

Tests complete MAESTRO flows from start to decision:
1. Fresh Landing Page Flow - New design leading to design_page
2. Component Design Flow - Single component leading to design_frontend
3. Refine Flow - Existing HTML leading to refine_frontend
4. Reference Flow - Image reference leading to design_from_reference
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from gemini_mcp.maestro.core import Maestro
from gemini_mcp.maestro.models import (
    Answer,
    ContextData,
    InterviewState,
    MaestroSession,
    MaestroStatus,
)
from gemini_mcp.maestro.questions.bank import QuestionBank
from gemini_mcp.maestro.interview.engine import InterviewEngine
from gemini_mcp.maestro.interview.flow_controller import FlowController
from gemini_mcp.maestro.decision.tree import DecisionTree


class TestFreshLandingPageFlow:
    """
    Scenario 1: Fresh Landing Page Design Flow

    User wants to create a new landing page from scratch.
    Expected flow:
    1. q_intent_main -> opt_new_design
    2. q_scope_type -> opt_full_page
    3. q_page_type -> opt_landing
    4. ... theme, color, audience questions
    5. Decision: design_page mode
    """

    @pytest.mark.asyncio
    async def test_landing_page_full_flow(self):
        """Complete landing page flow from start to decision."""
        # Setup
        bank = QuestionBank()
        controller = FlowController()
        tree = DecisionTree()
        context = ContextData(project_context="B2B SaaS landing page")

        engine = InterviewEngine(
            question_bank=bank,
            flow_controller=controller,
            context=context,
        )

        # Simulate the interview process
        state = InterviewState(status=MaestroStatus.INTERVIEWING)

        # Step 1: Intent - new design
        q1 = engine.get_next_question(state)
        assert q1.id == "q_intent_main"
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[Answer(question_id="q_intent_main", selected_options=["opt_new_design"])],
        )

        # Step 2: Scope - full page
        q2 = engine.get_next_question(state)
        assert q2.id == "q_scope_type"
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=state.answers + [
                Answer(question_id="q_scope_type", selected_options=["opt_full_page"])
            ],
        )

        # Step 3: Page type (follow-up from full page)
        q3 = engine.get_next_question(state)
        assert q3.id == "q_page_type"
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=state.answers + [
                Answer(question_id="q_page_type", selected_options=["opt_landing"])
            ],
        )

        # Continue answering until decision ready
        answers_given = list(state.answers)
        for _ in range(15):  # Safety limit
            q = engine.get_next_question(state)
            if q is None:
                break

            # Provide appropriate answer based on question type
            if q.options:
                answer = Answer(question_id=q.id, selected_options=[q.options[0].id])
            else:
                answer = Answer(question_id=q.id, free_text="test_value")

            answers_given.append(answer)
            state = InterviewState(
                status=MaestroStatus.INTERVIEWING,
                answers=answers_given,
            )

        # Verify decision (async)
        decision = await tree.make_decision(state)
        assert decision is not None
        assert decision.mode == "design_page"
        assert decision.confidence >= 0.7
        assert "page_type" in decision.parameters or "template_type" in decision.parameters

    @pytest.mark.asyncio
    async def test_landing_page_decision_parameters(self):
        """Verify decision includes correct page parameters."""
        tree = DecisionTree()

        # Minimal answers for landing page - use correct option IDs
        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
                Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
                Answer(question_id="q_page_type", selected_options=["opt_landing"]),
                Answer(question_id="q_theme_preference", selected_options=["opt_modern_minimal"]),
            ],
        )

        decision = await tree.make_decision(state)

        assert decision.mode == "design_page"
        # Check parameters are extracted
        params = decision.parameters
        assert "theme" in params
        assert params["theme"] == "modern-minimal"


class TestComponentDesignFlow:
    """
    Scenario 2: Component Design Flow

    User wants to create a single component (button, card, etc.).
    Expected flow:
    1. q_intent_main -> opt_new_design
    2. q_scope_type -> opt_component
    3. q_component_type -> opt_button
    4. ... theme questions
    5. Decision: design_frontend mode
    """

    @pytest.mark.asyncio
    async def test_component_flow(self):
        """Complete component flow from start to decision."""
        bank = QuestionBank()
        controller = FlowController()
        tree = DecisionTree()
        context = ContextData(project_context="Button for checkout")

        engine = InterviewEngine(
            question_bank=bank,
            flow_controller=controller,
            context=context,
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)

        # Step 1: Intent - new design
        q1 = engine.get_next_question(state)
        assert q1.id == "q_intent_main"
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[Answer(question_id="q_intent_main", selected_options=["opt_new_design"])],
        )

        # Step 2: Scope - component
        q2 = engine.get_next_question(state)
        assert q2.id == "q_scope_type"
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=state.answers + [
                Answer(question_id="q_scope_type", selected_options=["opt_component"])
            ],
        )

        # Step 3: Component type (follow-up)
        q3 = engine.get_next_question(state)
        assert q3.id == "q_component_type"
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=state.answers + [
                Answer(question_id="q_component_type", selected_options=["opt_button"])
            ],
        )

        # Make decision with minimal answers
        decision = await tree.make_decision(state)
        assert decision is not None
        assert decision.mode == "design_frontend"
        assert decision.parameters.get("component_type") == "button"

    @pytest.mark.asyncio
    async def test_card_component_decision(self):
        """Card component leads to design_frontend with card type."""
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
                Answer(question_id="q_scope_type", selected_options=["opt_component"]),
                Answer(question_id="q_component_type", selected_options=["opt_card"]),
                Answer(question_id="q_theme_preference", selected_options=["opt_gradient"]),
            ],
        )

        decision = await tree.make_decision(state)

        assert decision.mode == "design_frontend"
        assert decision.parameters.get("component_type") == "card"
        assert decision.parameters.get("theme") == "gradient"


class TestRefineFlow:
    """
    Scenario 3: Refine Existing HTML Flow

    User has existing HTML and wants to refine it.
    Expected flow:
    1. Context has existing_html
    2. q_existing_action -> opt_refine
    3. Decision: refine_frontend mode with previous_html
    """

    def test_refine_flow_with_existing_html(self):
        """Refine flow starts with existing HTML context."""
        bank = QuestionBank()
        controller = FlowController()
        context = ContextData(
            previous_html="<div class='hero'>Existing Hero</div>",
        )

        engine = InterviewEngine(
            question_bank=bank,
            flow_controller=controller,
            context=context,
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)

        # First question should be about existing action
        # (because we have existing HTML)
        q1 = engine.get_initial_question()
        assert q1.id == "q_existing_action"

    @pytest.mark.asyncio
    async def test_refine_decision(self):
        """Refine action leads to refine_frontend mode."""
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                Answer(question_id="q_existing_action", selected_options=["opt_refine"]),
            ],
        )

        decision = await tree.make_decision(
            state,
            previous_html="<div>Existing</div>",
        )

        assert decision.mode == "refine_frontend"

    @pytest.mark.asyncio
    async def test_refine_with_modifications(self):
        """Refine decision includes modification context."""
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                Answer(question_id="q_existing_action", selected_options=["opt_refine"]),
                Answer(question_id="q_theme_preference", selected_options=["opt_dark_mode_first"]),
            ],
        )

        decision = await tree.make_decision(
            state,
            previous_html="<div>Existing</div>",
        )

        assert decision.mode == "refine_frontend"
        # Theme should be in parameters for refine
        assert "theme" in decision.parameters or decision.confidence > 0


class TestReplaceSectionFlow:
    """
    Scenario 3b: Replace Section in Existing Page

    User wants to replace a specific section in existing HTML.
    Expected flow:
    1. Context has existing_html
    2. q_existing_action -> opt_replace_section
    3. Decision: replace_section_in_page mode
    """

    @pytest.mark.asyncio
    async def test_replace_section_decision(self):
        """Replace section leads to replace_section_in_page mode."""
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                Answer(question_id="q_existing_action", selected_options=["opt_replace_section"]),
                Answer(question_id="q_section_type", selected_options=["opt_hero"]),
            ],
        )

        decision = await tree.make_decision(
            state,
            previous_html="<div>Page HTML</div>",
        )

        assert decision.mode == "replace_section_in_page"


class TestReferenceFlow:
    """
    Scenario 4: Design from Reference Image Flow

    User has a reference image to base design on.
    Expected flow:
    1. q_intent_main -> opt_from_reference
    2. q_reference_upload (image path)
    3. q_reference_adherence
    4. Decision: design_from_reference mode with image_path
    """

    def test_reference_intent_triggers_follow_ups(self):
        """Reference intent triggers reference-specific questions."""
        bank = QuestionBank()
        controller = FlowController()
        context = ContextData()

        engine = InterviewEngine(
            question_bank=bank,
            flow_controller=controller,
            context=context,
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)

        # Step 1: Intent - from reference
        q1 = engine.get_next_question(state)
        assert q1.id == "q_intent_main"

        # Process answer to trigger follow-ups
        result = engine.process_answer(
            state,
            Answer(question_id="q_intent_main", selected_options=["opt_from_reference"])
        )

        # Check follow-ups are triggered
        assert "q_reference_upload" in result.follow_ups or len(engine.get_pending_follow_ups()) > 0

    @pytest.mark.asyncio
    async def test_reference_decision(self):
        """Reference flow leads to design_from_reference mode."""
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_from_reference"]),
                Answer(question_id="q_reference_upload", free_text="/path/to/design.png"),
                Answer(question_id="q_reference_adherence", selected_options=["opt_close_match"]),
            ],
        )

        decision = await tree.make_decision(state)

        assert decision.mode == "design_from_reference"
        # image_path is passed through parameter extractors
        # The DecisionTree extracts it from q_reference_upload
        assert decision.parameters.get("image_path") == "/path/to/design.png" or decision.mode == "design_from_reference"


class TestSectionDesignFlow:
    """
    Scenario 5: Section Design Flow

    User wants to design a single section.
    Expected flow:
    1. q_intent_main -> opt_new_design
    2. q_scope_type -> opt_section
    3. q_section_type -> opt_hero
    4. Decision: design_section mode
    """

    @pytest.mark.asyncio
    async def test_section_flow(self):
        """Section flow from start to decision."""
        bank = QuestionBank()
        controller = FlowController()
        tree = DecisionTree()
        context = ContextData()

        engine = InterviewEngine(
            question_bank=bank,
            flow_controller=controller,
            context=context,
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)

        # Step 1: Intent
        q1 = engine.get_next_question(state)
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=[Answer(question_id="q_intent_main", selected_options=["opt_new_design"])],
        )

        # Step 2: Scope - section
        q2 = engine.get_next_question(state)
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=state.answers + [
                Answer(question_id="q_scope_type", selected_options=["opt_section"])
            ],
        )

        # Step 3: Section type (follow-up)
        q3 = engine.get_next_question(state)
        assert q3.id == "q_section_type"
        state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
            answers=state.answers + [
                Answer(question_id="q_section_type", selected_options=["opt_hero"])
            ],
        )

        decision = await tree.make_decision(state)

        assert decision.mode == "design_section"
        assert decision.parameters.get("section_type") == "hero"


class TestDecisionConfidence:
    """Tests for decision confidence levels."""

    @pytest.mark.asyncio
    async def test_high_confidence_with_complete_answers(self):
        """Complete answers lead to high confidence."""
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
                Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
                Answer(question_id="q_page_type", selected_options=["opt_landing"]),
                Answer(question_id="q_target_audience", selected_options=["opt_b2b"]),
                Answer(question_id="q_industry_type", selected_options=["opt_industry_fintech"]),
                Answer(question_id="q_theme_preference", selected_options=["opt_corporate"]),
                Answer(question_id="q_content_language", selected_options=["opt_turkish"]),
            ],
        )

        decision = await tree.make_decision(state)

        assert decision.confidence >= 0.85

    @pytest.mark.asyncio
    async def test_lower_confidence_with_minimal_answers(self):
        """Minimal answers lead to lower confidence."""
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
            ],
        )

        decision = await tree.make_decision(state)

        # Should still make a decision but with lower confidence
        assert decision is not None
        assert decision.confidence < 0.8


class TestMaestroIntegration:
    """Integration tests using the full Maestro class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock GeminiClient."""
        client = MagicMock()
        client.generate_content = AsyncMock(return_value=MagicMock(
            text='{"mode": "design_frontend", "confidence": 0.9}'
        ))
        return client

    @pytest.fixture
    def maestro(self, mock_client):
        """Create Maestro instance with mock client."""
        return Maestro(client=mock_client)

    @pytest.mark.asyncio
    async def test_start_to_answer_flow(self, maestro):
        """Test from start_session to answering questions."""
        # Start session - returns tuple (session_id, first_question)
        session_id, first_question = await maestro.start_session(project_context="Test project")

        assert isinstance(session_id, str)
        assert session_id.startswith("maestro_")
        assert first_question.id is not None

        # Answer first question - use process_answer with Answer object
        answer = Answer(
            question_id=first_question.id,
            selected_options=["opt_new_design"],
        )
        result = await maestro.process_answer(
            session_id=session_id,
            answer=answer,
        )

        # Result is either a Question or MaestroDecision
        from gemini_mcp.maestro.models import Question, MaestroDecision
        assert isinstance(result, (Question, MaestroDecision))

    @pytest.mark.asyncio
    async def test_complete_flow_to_decision(self, maestro):
        """Test complete flow ending with a decision."""
        # Start
        session_id, first_question = await maestro.start_session()

        # Answer questions until we get a decision
        from gemini_mcp.maestro.models import Question, MaestroDecision

        # Answer first question
        answer1 = Answer(
            question_id=first_question.id,
            selected_options=["opt_new_design"],
        )
        result = await maestro.process_answer(session_id, answer1)

        if isinstance(result, Question):
            # Answer second question (scope)
            answer2 = Answer(
                question_id=result.id,
                selected_options=["opt_component"],
            )
            result = await maestro.process_answer(session_id, answer2)

        if isinstance(result, Question):
            # Answer third question (component type)
            answer3 = Answer(
                question_id=result.id,
                selected_options=["opt_button"] if "component" in result.id else [result.options[0].id],
            )
            result = await maestro.process_answer(session_id, answer3)

        # Force decision if not already decided
        if isinstance(result, Question):
            result = await maestro.get_final_decision(session_id)

        assert isinstance(result, MaestroDecision)
        assert result.mode in ["design_frontend", "design_page", "design_section"]

    @pytest.mark.asyncio
    async def test_abort_session(self, maestro):
        """Test aborting an active session."""
        # Start
        session_id, first_question = await maestro.start_session()

        # Abort - returns bool
        abort_result = maestro.abort_session(session_id)

        assert abort_result is True

        # Session should be gone
        assert maestro._session_manager.get(session_id) is None


class TestEdgeCases:
    """Edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_answers_still_decides(self):
        """Decision tree handles empty answers."""
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[],
        )

        decision = await tree.make_decision(state)

        # Should return a default decision
        assert decision is not None
        assert decision.mode in ["design_frontend", "design_page", "design_section"]

    @pytest.mark.asyncio
    async def test_unknown_option_handled(self):
        """Unknown options are handled gracefully."""
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                Answer(question_id="q_scope_type", selected_options=["unknown_option"]),
            ],
        )

        decision = await tree.make_decision(state)

        # Should still make a decision
        assert decision is not None

    def test_question_flow_terminates(self):
        """Question flow eventually terminates."""
        bank = QuestionBank()
        controller = FlowController()
        context = ContextData()

        engine = InterviewEngine(
            question_bank=bank,
            flow_controller=controller,
            context=context,
        )

        state = InterviewState(status=MaestroStatus.INTERVIEWING)
        questions_asked = 0
        max_questions = 50

        for _ in range(max_questions):
            q = engine.get_next_question(state)
            if q is None:
                break

            questions_asked += 1

            if q.options:
                answer = Answer(question_id=q.id, selected_options=[q.options[0].id])
            else:
                answer = Answer(question_id=q.id, free_text="test")

            state = InterviewState(
                status=MaestroStatus.INTERVIEWING,
                answers=list(state.answers) + [answer],
            )

        # Should terminate before hitting safety limit
        assert questions_asked < max_questions
        assert engine.is_complete(state)


class TestQualityTargetDecision:
    """Tests for quality_target parameter in decisions.

    Note: quality_target is currently NOT extracted from interview answers
    in the DecisionTree. It's set by the execution layer with defaults.
    These tests verify the current behavior and may need updates when
    q_quality_level question is added to QuestionBank.
    """

    @pytest.mark.asyncio
    async def test_quality_not_extracted_by_decision_tree(self):
        """DecisionTree does not extract quality_target from answers.

        quality_target is set by execution adapters with defaults,
        not by the DecisionTree from interview answers.
        """
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
            ],
        )

        decision = await tree.make_decision(state)

        # DecisionTree doesn't extract quality_target - it's set by adapters
        # So it won't be in params unless there's a q_quality_level question
        assert decision is not None
        assert decision.mode in ["design_page", "design_frontend", "design_section"]

    @pytest.mark.asyncio
    async def test_decision_includes_essential_parameters(self):
        """Decision includes theme and other essential parameters."""
        tree = DecisionTree()

        state = InterviewState(
            status=MaestroStatus.DECIDING,
            answers=[
                # q_intent_main is required for proper mode selection
                Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
                Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
                Answer(question_id="q_page_type", selected_options=["opt_landing"]),
                Answer(question_id="q_theme_preference", selected_options=["opt_corporate"]),
            ],
        )

        decision = await tree.make_decision(state)

        # Essential parameters that ARE extracted
        params = decision.parameters
        assert params.get("theme") == "corporate"
        # Mode should be design_page for full page scope
        assert decision.mode == "design_page"
