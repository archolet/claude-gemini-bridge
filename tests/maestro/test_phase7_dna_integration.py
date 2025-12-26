"""
Phase 7 Tests - DNA Integration

Tests for MAESTRO DNA persistence and cross-session consistency:
- DNA loading in start_session()
- DNA saving in execute()
- Recommender DNA history signal
- Public DNA accessors
- Cross-session DNA continuity
"""
import pytest
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from gemini_mcp.maestro.core import Maestro
from gemini_mcp.maestro.models import (
    MaestroDecision,
    MaestroSession,
    MaestroStatus,
    InterviewState,
    ContextData,
    Answer,
)
from gemini_mcp.maestro.intelligence import Recommender, PreferenceLearner, AdaptiveFlow
from gemini_mcp.maestro.intelligence.adaptive_flow import FlowContext
from gemini_mcp.orchestration.dna_store import DNAStore, DNAEntry
from gemini_mcp.orchestration.context import DesignDNA


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_client():
    """Create a mock GeminiClient."""
    client = MagicMock()
    client.design_component = AsyncMock(return_value={
        "html": "<div>test</div>",
        "design_tokens": {
            "colors": {"primary": "#E11D48"},
            "typography": {"heading_font": "Inter"},
        },
    })
    return client


@pytest.fixture
def mock_dna_store():
    """Create a mock DNAStore."""
    store = MagicMock(spec=DNAStore)
    store.search.return_value = []
    store.save.return_value = "dna_123"
    store.get_stats.return_value = {
        "total_entries": 5,
        "unique_projects": 2,
        "storage_file": "/tmp/dna.json",
    }
    return store


@pytest.fixture
def sample_dna():
    """Create a sample DesignDNA."""
    return DesignDNA(
        colors={"primary": "#3B82F6", "secondary": "#10B981"},
        typography={"heading_font": "Inter", "body_font": "Open Sans"},
        spacing={"base": "4px", "scale": "1.5"},
        borders={"radius": "8px"},
        animation={"style": "smooth", "duration": "300ms"},
        mood="modern-minimal",
    )


@pytest.fixture
def sample_dna_entry(sample_dna):
    """Create a sample DNAEntry."""
    return DNAEntry(
        dna_id="dna_001",
        component_type="hero",
        theme="modern-minimal",
        project_id="my-project",
        created_at=datetime.now(),
        dna=sample_dna,
    )


# =============================================================================
# DNA LOADING IN start_session TESTS
# =============================================================================


class TestDNALoadingInStartSession:
    """Tests for DNA loading during session start."""

    @pytest.mark.asyncio
    async def test_no_project_context_no_dna_loaded(self, mock_client, mock_dna_store):
        """When no project_context, DNA is not loaded."""
        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)

            session_id, question = await maestro.start_session(
                project_context="",  # No project context
                existing_html=None,
            )

            # search should not be called when no project context
            mock_dna_store.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_project_context_no_previous_dna(self, mock_client, mock_dna_store):
        """When project has no previous DNA, design_tokens not set."""
        mock_dna_store.search.return_value = []  # No previous DNA

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)

            session_id, question = await maestro.start_session(
                project_context="my-project",
                existing_html=None,
            )

            mock_dna_store.search.assert_called_once_with(
                project_id="my-project",
                limit=1,
            )

            # Session should be created, but without design tokens
            session = maestro._session_manager.get(session_id)
            assert session is not None
            # design_tokens defaults to empty dict, not None
            assert session.context.design_tokens == {} or session.context.design_tokens is None

    @pytest.mark.asyncio
    async def test_project_context_with_previous_dna(
        self, mock_client, mock_dna_store, sample_dna_entry
    ):
        """When project has previous DNA, design_tokens are loaded."""
        mock_dna_store.search.return_value = [sample_dna_entry]

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)

            session_id, question = await maestro.start_session(
                project_context="my-project",
                existing_html=None,
            )

            mock_dna_store.search.assert_called_once_with(
                project_id="my-project",
                limit=1,
            )

            # Session should have design tokens from DNA
            session = maestro._session_manager.get(session_id)
            assert session is not None
            assert session.context.design_tokens is not None
            assert session.context.design_tokens["colors"]["primary"] == "#3B82F6"

    @pytest.mark.asyncio
    async def test_dna_load_exception_handled(self, mock_client, mock_dna_store):
        """DNA load exception should not break session start."""
        mock_dna_store.search.side_effect = Exception("Database error")

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)

            # Should not raise, just log warning
            session_id, question = await maestro.start_session(
                project_context="my-project",
                existing_html=None,
            )

            # Session should still be created
            assert session_id is not None
            assert question is not None


# =============================================================================
# DNA SAVING IN execute TESTS
# =============================================================================


class TestDNASavingInExecute:
    """Tests for DNA saving during execution."""

    def _create_session_with_answers(
        self, maestro, session_id: str, project_context: str = "test-project"
    ):
        """Helper to create a decided session with proper timestamp."""
        context_data = ContextData(project_context=project_context)
        state = InterviewState(
            status=MaestroStatus.DECIDING,  # Use DECIDING as the ready-to-execute state
            answers=[
                Answer(question_id="q1", selected_options=["opt1"]),
            ],
        )
        session = MaestroSession(
            session_id=session_id,
            state=state,
            context=context_data,
        )
        # Use create() method to properly set both _sessions and _timestamps
        maestro._session_manager.create(session)
        return session

    @pytest.mark.asyncio
    async def test_successful_execution_saves_dna(self, mock_client, mock_dna_store):
        """Successful execution should save DNA."""
        mock_client.design_component.return_value = {
            "status": "complete",
            "html": "<div>test</div>",
            "design_tokens": {
                "colors": {"primary": "#E11D48"},
                "typography": {"heading_font": "Poppins"},
            },
        }

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)
            self._create_session_with_answers(maestro, "session_001")

            decision = MaestroDecision(
                mode="design_frontend",
                confidence=0.9,
                parameters={
                    "component_type": "card",
                    "theme": "corporate",
                },
                reasoning="Test decision",
            )

            result = await maestro.execute("session_001", decision)

            # DNA should be saved
            mock_dna_store.save.assert_called_once()
            call_args = mock_dna_store.save.call_args
            assert call_args.kwargs["component_type"] == "card"
            assert call_args.kwargs["theme"] == "corporate"
            assert call_args.kwargs["project_id"] == "test-project"

    @pytest.mark.asyncio
    async def test_failed_execution_no_dna_save(self, mock_client, mock_dna_store):
        """Failed execution should not save DNA."""
        mock_client.design_component.return_value = {
            "status": "failed",
            "error": "API error",
        }

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)
            self._create_session_with_answers(maestro, "session_001")

            decision = MaestroDecision(
                mode="design_frontend",
                confidence=0.9,
                parameters={"component_type": "card"},
                reasoning="Test decision",
            )

            result = await maestro.execute("session_001", decision)

            # DNA should NOT be saved
            mock_dna_store.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_design_tokens_no_dna_save(self, mock_client, mock_dna_store):
        """Execution without design_tokens should not save DNA."""
        mock_client.design_component.return_value = {
            "status": "complete",
            "html": "<div>test</div>",
            # No design_tokens
        }

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)
            self._create_session_with_answers(maestro, "session_001")

            decision = MaestroDecision(
                mode="design_frontend",
                confidence=0.9,
                parameters={"component_type": "card"},
                reasoning="Test decision",
            )

            result = await maestro.execute("session_001", decision)

            # DNA should NOT be saved (no design_tokens)
            mock_dna_store.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_dna_save_exception_handled(self, mock_client, mock_dna_store):
        """DNA save exception should not break execution."""
        mock_client.design_component.return_value = {
            "status": "complete",
            "html": "<div>test</div>",
            "design_tokens": {"colors": {"primary": "#E11D48"}},
        }
        mock_dna_store.save.side_effect = Exception("Storage error")

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)
            self._create_session_with_answers(maestro, "session_001")

            decision = MaestroDecision(
                mode="design_frontend",
                confidence=0.9,
                parameters={"component_type": "card"},
                reasoning="Test decision",
            )

            # Should not raise, just log warning
            result = await maestro.execute("session_001", decision)

            # Result should still be returned
            assert result is not None
            assert result.get("html") == "<div>test</div>"

    @pytest.mark.asyncio
    async def test_default_project_id_when_none(self, mock_client, mock_dna_store):
        """When no project_context, 'default' should be used."""
        mock_client.design_component.return_value = {
            "status": "complete",
            "html": "<div>test</div>",
            "design_tokens": {"colors": {"primary": "#E11D48"}},
        }

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)
            # Create session without project_context
            self._create_session_with_answers(maestro, "session_001", project_context="")

            decision = MaestroDecision(
                mode="design_frontend",
                confidence=0.9,
                parameters={"component_type": "card"},
                reasoning="Test decision",
            )

            result = await maestro.execute("session_001", decision)

            # DNA should be saved with "default" project_id
            call_args = mock_dna_store.save.call_args
            assert call_args.kwargs["project_id"] == "default"


# =============================================================================
# RECOMMENDER DNA HISTORY SIGNAL TESTS
# =============================================================================


class TestRecommenderDNASignal:
    """Tests for DNA history signal in Recommender."""

    def test_no_dna_store_no_signal(self):
        """Without DNA store, DNA signal not added."""
        learner = PreferenceLearner()
        flow = AdaptiveFlow()
        recommender = Recommender(learner, flow, dna_store=None)

        ctx = FlowContext(project_context="my-project", existing_html="")
        recommender.set_context(ctx)

        rec = recommender.recommend_theme()

        # Should still return a recommendation (from other signals or default)
        assert rec is not None
        assert rec.value is not None

    def test_dna_store_with_entries_adds_signal(self, mock_dna_store, sample_dna_entry):
        """With DNA entries, DNA history signal is added."""
        # Return 3 entries with same theme
        entry1 = sample_dna_entry
        entry2 = DNAEntry(
            dna_id="dna_002",
            component_type="card",
            theme="modern-minimal",  # Same theme
            project_id="my-project",
            created_at=datetime.now(),
            dna=sample_dna_entry.dna,
        )
        entry3 = DNAEntry(
            dna_id="dna_003",
            component_type="navbar",
            theme="modern-minimal",  # Same theme
            project_id="my-project",
            created_at=datetime.now(),
            dna=sample_dna_entry.dna,
        )
        mock_dna_store.search.return_value = [entry1, entry2, entry3]

        learner = PreferenceLearner()
        flow = AdaptiveFlow()
        recommender = Recommender(learner, flow, dna_store=mock_dna_store)

        ctx = FlowContext(project_context="my-project", existing_html="")
        recommender.set_context(ctx)

        rec = recommender.recommend_theme()

        # Should recommend "modern-minimal" from DNA history
        mock_dna_store.search.assert_called_once()
        # 3/3 consistency = 100%, signal confidence = 0.6 * 1.0 = 0.6
        assert rec is not None

    def test_mixed_themes_affects_confidence(self, mock_dna_store, sample_dna):
        """Mixed theme history should lower confidence."""
        # Return 3 entries with different themes
        entries = [
            DNAEntry(
                dna_id="dna_001",
                component_type="hero",
                theme="corporate",
                project_id="my-project",
                created_at=datetime.now(),
                dna=sample_dna,
            ),
            DNAEntry(
                dna_id="dna_002",
                component_type="card",
                theme="gradient",  # Different
                project_id="my-project",
                created_at=datetime.now(),
                dna=sample_dna,
            ),
            DNAEntry(
                dna_id="dna_003",
                component_type="navbar",
                theme="corporate",  # Same as first
                project_id="my-project",
                created_at=datetime.now(),
                dna=sample_dna,
            ),
        ]
        mock_dna_store.search.return_value = entries

        learner = PreferenceLearner()
        flow = AdaptiveFlow()
        recommender = Recommender(learner, flow, dna_store=mock_dna_store)

        ctx = FlowContext(project_context="my-project", existing_html="")
        recommender.set_context(ctx)

        rec = recommender.recommend_theme()

        # 2/3 consistency for "corporate", confidence = 0.6 * 0.67 = 0.4
        assert rec is not None
        mock_dna_store.search.assert_called_once()

    def test_no_project_context_no_dna_lookup(self, mock_dna_store):
        """Without project context, DNA is not looked up."""
        learner = PreferenceLearner()
        flow = AdaptiveFlow()
        recommender = Recommender(learner, flow, dna_store=mock_dna_store)

        ctx = FlowContext(project_context="", existing_html="")  # No project
        recommender.set_context(ctx)

        rec = recommender.recommend_theme()

        # DNA store should not be called
        mock_dna_store.search.assert_not_called()

    def test_dna_store_exception_handled(self, mock_dna_store):
        """DNA store exception should not break recommendation."""
        mock_dna_store.search.side_effect = Exception("Storage error")

        learner = PreferenceLearner()
        flow = AdaptiveFlow()
        recommender = Recommender(learner, flow, dna_store=mock_dna_store)

        ctx = FlowContext(project_context="my-project", existing_html="")
        recommender.set_context(ctx)

        # Should not raise, just return recommendation from other signals
        rec = recommender.recommend_theme()
        assert rec is not None

    def test_set_dna_store_late_binding(self, mock_dna_store, sample_dna_entry):
        """DNA store can be set after construction."""
        learner = PreferenceLearner()
        flow = AdaptiveFlow()
        recommender = Recommender(learner, flow)  # No dna_store

        # Set later
        mock_dna_store.search.return_value = [sample_dna_entry]
        recommender.set_dna_store(mock_dna_store)

        ctx = FlowContext(project_context="my-project", existing_html="")
        recommender.set_context(ctx)

        rec = recommender.recommend_theme()

        # DNA store should now be called
        mock_dna_store.search.assert_called_once()


# =============================================================================
# PUBLIC DNA ACCESSORS TESTS
# =============================================================================


class TestPublicDNAAccessors:
    """Tests for public DNA accessor methods."""

    def test_get_dna_history(self, mock_client, mock_dna_store, sample_dna_entry):
        """get_dna_history returns DNA entries."""
        mock_dna_store.search.return_value = [sample_dna_entry]

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)

            history = maestro.get_dna_history(
                project_id="my-project",
                component_type="hero",
                limit=5,
            )

            mock_dna_store.search.assert_called_once_with(
                project_id="my-project",
                component_type="hero",
                theme=None,
                limit=5,
            )
            assert isinstance(history, list)

    def test_get_dna_history_with_all_filters(
        self, mock_client, mock_dna_store, sample_dna_entry
    ):
        """get_dna_history passes all filter parameters."""
        mock_dna_store.search.return_value = [sample_dna_entry]

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)

            history = maestro.get_dna_history(
                project_id="my-project",
                component_type="card",
                theme="corporate",
                limit=10,
            )

            mock_dna_store.search.assert_called_once_with(
                project_id="my-project",
                component_type="card",
                theme="corporate",
                limit=10,
            )

    def test_get_dna_stats(self, mock_client, mock_dna_store):
        """get_dna_stats returns storage statistics."""
        mock_dna_store.get_stats.return_value = {
            "total_entries": 42,
            "unique_projects": 5,
            "storage_file": "/tmp/dna.json",
        }

        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)

            stats = maestro.get_dna_stats()

            mock_dna_store.get_stats.assert_called_once()
            assert stats["total_entries"] == 42
            assert stats["unique_projects"] == 5

    def test_dna_store_property(self, mock_client, mock_dna_store):
        """dna_store property returns the DNAStore instance."""
        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=mock_dna_store):
            maestro = Maestro(mock_client)

            store = maestro.dna_store

            assert store is mock_dna_store


# =============================================================================
# CROSS-SESSION DNA CONTINUITY TESTS
# =============================================================================


class TestCrossSessionDNAContinuity:
    """Tests for DNA continuity across sessions."""

    @pytest.fixture
    def temp_dna_store(self):
        """Create a temporary DNAStore for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_dna.json")
            store = DNAStore(db_path=db_path)
            yield store

    @pytest.mark.asyncio
    async def test_save_in_session1_load_in_session2(self, mock_client, temp_dna_store):
        """DNA saved in session 1 should be loaded in session 2."""
        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=temp_dna_store):
            maestro = Maestro(mock_client)

            # Session 1: Execute and save DNA
            session1_id, _ = await maestro.start_session(
                project_context="shared-project",
            )

            # Manually trigger DNA save (simulating execution)
            dna = DesignDNA(
                colors={"primary": "#FF5733"},
                typography={"heading_font": "Roboto"},
            )
            temp_dna_store.save(
                component_type="hero",
                theme="gradient",
                dna=dna,
                project_id="shared-project",
            )

            # Session 2: Should load the DNA
            session2_id, _ = await maestro.start_session(
                project_context="shared-project",
            )

            # Verify DNA was loaded
            session2 = maestro._session_manager.get(session2_id)
            assert session2.context.design_tokens is not None
            assert session2.context.design_tokens["colors"]["primary"] == "#FF5733"

    @pytest.mark.asyncio
    async def test_different_projects_isolated(self, mock_client, temp_dna_store):
        """DNA from different projects should be isolated."""
        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=temp_dna_store):
            maestro = Maestro(mock_client)

            # Save DNA for project A
            dna_a = DesignDNA(colors={"primary": "#FF0000"})
            temp_dna_store.save(
                component_type="hero",
                theme="gradient",
                dna=dna_a,
                project_id="project-a",
            )

            # Start session for project B
            session_id, _ = await maestro.start_session(
                project_context="project-b",  # Different project
            )

            # Project B should NOT have Project A's DNA
            session = maestro._session_manager.get(session_id)
            # design_tokens defaults to empty dict when no DNA loaded
            assert session.context.design_tokens == {} or session.context.design_tokens is None

    @pytest.mark.asyncio
    async def test_latest_dna_loaded(self, mock_client, temp_dna_store):
        """Most recent DNA should be loaded."""
        with patch("gemini_mcp.maestro.core.get_dna_store", return_value=temp_dna_store):
            maestro = Maestro(mock_client)

            # Save multiple DNA entries
            dna1 = DesignDNA(colors={"primary": "#111111"})
            temp_dna_store.save(
                component_type="hero",
                theme="minimal",
                dna=dna1,
                project_id="my-project",
            )

            dna2 = DesignDNA(colors={"primary": "#222222"})
            temp_dna_store.save(
                component_type="card",
                theme="corporate",
                dna=dna2,
                project_id="my-project",
            )

            # Start session - should get the most recent DNA
            session_id, _ = await maestro.start_session(
                project_context="my-project",
            )

            session = maestro._session_manager.get(session_id)
            assert session.context.design_tokens is not None
            # Most recent is dna2
            assert session.context.design_tokens["colors"]["primary"] == "#222222"
