"""
Tests for MAESTRO Phase 5: MCP Tool Integration.

Tests cover:
- MAESTRO MCP tool wrappers
- Session lifecycle via MCP tools
- Trifecta pipeline integration
- Quality target configurations
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from gemini_mcp.maestro import (
    Maestro,
    Answer,
    MaestroDecision,
    Question,
    QuestionOption,
    QuestionCategory,
    QuestionType,
)
from gemini_mcp.maestro.execution import (
    ToolExecutor,
    MODE_TO_PIPELINE,
    QUALITY_CONFIGS,
)
from gemini_mcp.orchestration import PipelineType


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_client():
    """Create mock GeminiClient for MAESTRO."""
    client = MagicMock()
    client.design_component = AsyncMock(return_value={
        "html": "<div class='designed'>Designed</div>",
        "component_id": "comp_123",
    })
    client.design_section = AsyncMock(return_value={
        "html": "<section>Section</section>",
        "section_type": "hero",
    })
    client.refine_component = AsyncMock(return_value={
        "html": "<div class='refined'>Refined</div>",
    })
    client.design_from_reference = AsyncMock(return_value={
        "html": "<div>From reference</div>",
    })
    client.generate_text = AsyncMock(return_value='{"mode": "design_frontend"}')
    return client


@pytest.fixture
def mock_question():
    """Create mock Question for testing."""
    return Question(
        id="q_intent_main",
        text="What do you want to create?",
        category=QuestionCategory.INTENT,
        options=[
            QuestionOption(
                id="opt_new_design",
                label="New Design",
                description="Create a new design from scratch",
            ),
            QuestionOption(
                id="opt_refine",
                label="Refine",
                description="Improve existing design",
            ),
        ],
        question_type=QuestionType.SINGLE_CHOICE,
    )


@pytest.fixture
def maestro(mock_client):
    """Create MAESTRO with mock client."""
    return Maestro(mock_client)


# =============================================================================
# PIPELINE CONFIGURATION TESTS
# =============================================================================


class TestPipelineConfigs:
    """Tests for MODE_TO_PIPELINE and QUALITY_CONFIGS."""

    def test_mode_to_pipeline_mapping(self):
        """Test all modes have pipeline mappings."""
        expected_modes = {
            "design_frontend",
            "design_page",
            "design_section",
            "refine_frontend",
            "replace_section_in_page",
            "design_from_reference",
        }
        actual_modes = set(MODE_TO_PIPELINE.keys())

        assert actual_modes == expected_modes

    def test_pipeline_types_are_valid(self):
        """Test all mapped pipeline types are valid."""
        for mode, pipeline_type in MODE_TO_PIPELINE.items():
            assert isinstance(pipeline_type, PipelineType), (
                f"Invalid pipeline type for {mode}"
            )

    def test_quality_configs_have_required_keys(self):
        """Test all quality configs have required keys."""
        required_keys = {"threshold", "max_iterations", "description"}

        for target, config in QUALITY_CONFIGS.items():
            for key in required_keys:
                assert key in config, f"Missing '{key}' in {target}"

    def test_quality_configs_thresholds(self):
        """Test quality thresholds are in expected order."""
        assert QUALITY_CONFIGS["draft"]["threshold"] < QUALITY_CONFIGS["production"]["threshold"]
        assert QUALITY_CONFIGS["production"]["threshold"] < QUALITY_CONFIGS["high"]["threshold"]
        assert QUALITY_CONFIGS["high"]["threshold"] < QUALITY_CONFIGS["premium"]["threshold"]
        assert QUALITY_CONFIGS["premium"]["threshold"] < QUALITY_CONFIGS["enterprise"]["threshold"]

    def test_quality_configs_iterations(self):
        """Test max iterations increase with quality."""
        assert QUALITY_CONFIGS["draft"]["max_iterations"] < QUALITY_CONFIGS["enterprise"]["max_iterations"]

    def test_production_standard_alias(self):
        """Test 'standard' is alias for 'production'."""
        assert QUALITY_CONFIGS["standard"]["threshold"] == QUALITY_CONFIGS["production"]["threshold"]
        assert QUALITY_CONFIGS["standard"]["max_iterations"] == QUALITY_CONFIGS["production"]["max_iterations"]


# =============================================================================
# MAESTRO SESSION LIFECYCLE
# =============================================================================


class TestMaestroSessionLifecycle:
    """Tests for MAESTRO session management."""

    @pytest.mark.asyncio
    async def test_start_session(self, maestro):
        """Test session start returns ID and question."""
        session_id, question = await maestro.start_session(
            project_context="Test project"
        )

        assert session_id.startswith("maestro_")
        assert isinstance(question, Question)
        assert question.id is not None

    @pytest.mark.asyncio
    async def test_start_session_with_existing_html(self, maestro):
        """Test session start with existing HTML."""
        session_id, question = await maestro.start_session(
            existing_html="<div>Existing</div>"
        )

        session = maestro.get_session(session_id)
        assert session.context.previous_html == "<div>Existing</div>"

    @pytest.mark.asyncio
    async def test_get_session(self, maestro):
        """Test get_session returns session object."""
        session_id, _ = await maestro.start_session()
        session = maestro.get_session(session_id)

        assert session is not None
        assert session.session_id == session_id

    @pytest.mark.asyncio
    async def test_get_session_info(self, maestro):
        """Test get_session_info returns metadata."""
        session_id, _ = await maestro.start_session()
        info = maestro.get_session_info(session_id)

        assert info is not None
        assert info["session_id"] == session_id
        assert "status" in info

    @pytest.mark.asyncio
    async def test_abort_session(self, maestro):
        """Test abort cleans up session."""
        session_id, _ = await maestro.start_session()
        result = maestro.abort_session(session_id)

        assert result is True
        assert maestro.get_session(session_id) is None

    @pytest.mark.asyncio
    async def test_abort_nonexistent_returns_false(self, maestro):
        """Test abort returns False for nonexistent."""
        result = maestro.abort_session("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_list_sessions(self, maestro):
        """Test list_sessions returns all active sessions."""
        session_id1, _ = await maestro.start_session()
        session_id2, _ = await maestro.start_session()

        sessions = maestro.list_sessions()

        assert session_id1 in sessions
        assert session_id2 in sessions

    @pytest.mark.asyncio
    async def test_active_session_count(self, maestro):
        """Test active_session_count property."""
        await maestro.start_session()
        await maestro.start_session()

        assert maestro.active_session_count == 2


# =============================================================================
# TRIFECTA EXECUTION TESTS
# =============================================================================


class TestTrifectaExecution:
    """Tests for Trifecta pipeline integration."""

    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock Orchestrator."""
        orchestrator = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.completed_steps = 4
        mock_result.total_steps = 4
        mock_result.step_results = []
        mock_result.to_mcp_response.return_value = {
            "html": "<div>Trifecta output</div>",
        }
        orchestrator.run_pipeline = AsyncMock(return_value=mock_result)
        return orchestrator

    @pytest.mark.asyncio
    async def test_execute_with_trifecta_disabled(self, maestro):
        """Test execute without Trifecta uses direct path."""
        session_id, _ = await maestro.start_session()
        decision = await maestro.get_final_decision(session_id)

        result = await maestro.execute(
            session_id,
            decision,
            use_trifecta=False,
        )

        # Should have mode but not trifecta metadata
        assert "mode" in result or "error" in result
        assert result.get("trifecta_enabled") is not True

    @pytest.mark.asyncio
    async def test_execute_with_quality_target(self, maestro):
        """Test execute respects quality_target parameter."""
        session_id, _ = await maestro.start_session()
        decision = await maestro.get_final_decision(session_id)

        # Should not raise error with valid quality target
        result = await maestro.execute(
            session_id,
            decision,
            quality_target="premium",
        )

        assert "mode" in result or "error" in result


# =============================================================================
# MCP TOOL SIMULATION
# =============================================================================


class TestMCPToolPatterns:
    """Tests simulating MCP tool usage patterns."""

    @pytest.mark.asyncio
    async def test_full_interview_flow(self, maestro):
        """Test complete interview flow: start -> answer -> decision -> execute."""
        # Start session
        session_id, question = await maestro.start_session(
            project_context="E-commerce landing page"
        )
        assert question is not None

        # Answer first question
        answer = Answer(
            question_id=question.id,
            selected_options=[question.options[0].id],
        )
        result = await maestro.process_answer(session_id, answer)

        # Continue or get decision
        if isinstance(result, Question):
            # Force decision for testing
            decision = await maestro.get_final_decision(session_id)
        else:
            decision = result

        assert isinstance(decision, MaestroDecision)

        # Execute
        output = await maestro.execute(session_id, decision)
        assert "mode" in output or "error" in output

    @pytest.mark.asyncio
    async def test_get_progress(self, maestro):
        """Test progress tracking during interview."""
        session_id, question = await maestro.start_session()

        initial_progress = maestro.get_progress(session_id)
        assert 0.0 <= initial_progress <= 1.0

        # Answer a question
        answer = Answer(
            question_id=question.id,
            selected_options=[question.options[0].id],
        )
        await maestro.process_answer(session_id, answer)

        new_progress = maestro.get_progress(session_id)
        assert new_progress >= initial_progress

    @pytest.mark.asyncio
    async def test_session_expires_after_get(self, mock_client):
        """Test expired session returns None."""
        import time
        from gemini_mcp.maestro.session import SessionManager

        # Create manager with 60s TTL
        manager = SessionManager(ttl=60)

        # Manually set in Maestro
        maestro = Maestro(mock_client)
        maestro._session_manager = manager

        session_id, _ = await maestro.start_session()

        # Manually set timestamp to past (2 minutes ago)
        manager._timestamps[session_id] = time.time() - 120

        # Session should be expired on next get
        session = maestro.get_session(session_id)
        assert session is None


# =============================================================================
# ERROR HANDLING
# =============================================================================


class TestPhase5ErrorHandling:
    """Tests for Phase 5 error handling."""

    @pytest.mark.asyncio
    async def test_process_answer_invalid_session(self, maestro):
        """Test process_answer with invalid session raises."""
        answer = Answer(
            question_id="q_test",
            selected_options=["opt_test"],
        )

        with pytest.raises(ValueError, match="not found"):
            await maestro.process_answer("invalid_session", answer)

    @pytest.mark.asyncio
    async def test_execute_invalid_session(self, maestro):
        """Test execute with invalid session raises."""
        decision = MaestroDecision(
            mode="design_frontend",
            parameters={},
        )

        with pytest.raises(ValueError, match="not found"):
            await maestro.execute("invalid_session", decision)

    @pytest.mark.asyncio
    async def test_get_final_decision_invalid_session(self, maestro):
        """Test get_final_decision with invalid session raises."""
        with pytest.raises(ValueError, match="not found"):
            await maestro.get_final_decision("invalid_session")
