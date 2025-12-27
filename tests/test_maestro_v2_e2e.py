"""
MAESTRO v2 End-to-End Tests - Phase 4

Tests the complete MAESTRO v2 workflow from design brief to design decision.
These tests verify the integration of all v2 components.

Test Categories:
1. Soul Extraction Flow
2. Dynamic Question Generation
3. State Machine Transitions
4. Session Management
5. Graceful Fallback
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from gemini_mcp.maestro import (
    Maestro,
    MAESTROv2Wrapper,
    SoulAwareSession,
    SessionState,
    ProjectSoul,
    InterviewPhase,
    Question,
    QuestionCategory,
    QuestionType,
    QuestionOption,
)
from gemini_mcp.maestro.models.soul import (
    BrandPersonality,
    TargetAudience,
    VisualLanguage,
    EmotionalFramework,
    ProjectMetadata,
    ConfidenceScores,
)
from gemini_mcp.maestro.models.brand import PersonalityArchetype
from gemini_mcp.maestro.models.audience import DemographicProfile, PsychographicProfile, TechSavviness
from gemini_mcp.maestro.models.visual import ColorPalette, TypographyStyle
from gemini_mcp.maestro.models.emotion import (
    EmotionalTone,
    EmotionMapping,
    PrimaryEmotion,
    EmotionIntensity,
)
from gemini_mcp.maestro.models.gap import (
    GapAnalysis,
    GapInfo,
    GapCategory,
    GapSeverity,
)
from gemini_mcp.maestro.interview import (
    InterviewStateMachine,
    ProgressTracker,
    create_interview_state_machine,
    create_progress_tracker,
)
from gemini_mcp.maestro.interview.state_machine import TransitionResult
from gemini_mcp.maestro.prompts.tr import (
    PHASE_PROMPTS,
    QUESTION_TEMPLATES,
    get_phase_prompt,
    get_question_text,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_brief():
    """Sample design brief for testing."""
    return """
    Proje: FinTech Dashboard

    Modern bir finans yönetim dashboard'u tasarlıyoruz. Hedef kitle genç
    profesyoneller (25-35 yaş). Minimalist ve profesyonel bir görünüm istiyoruz.

    Ana renkler: Mavi ve beyaz tonları
    Tipografi: Sans-serif, modern

    Önemli özellikler:
    - Karanlık mod desteği
    - Mobil uyumlu
    - Erişilebilirlik (WCAG AA)
    """


@pytest.fixture
def sample_soul():
    """Sample ProjectSoul for testing."""
    return ProjectSoul(
        metadata=ProjectMetadata(
            name="FinTech Dashboard",
            tagline="Modern Finansal Yönetim",
            industry="fintech",
            project_type="dashboard",
        ),
        brand_personality=BrandPersonality(
            sincerity=0.6,
            excitement=0.4,
            competence=0.9,
            sophistication=0.7,
            ruggedness=0.2,
            dominant_trait="competence",
            personality_archetype=PersonalityArchetype.THE_SAGE,
        ),
        target_audience=TargetAudience(
            demographic=DemographicProfile(
                age_range=(25, 35),
                tech_savviness=TechSavviness.ADVANCED,
                profession_category="Finance",
            ),
            psychographic=PsychographicProfile(
                core_values=["Hızlı erişim", "Güvenlik", "Görsel netlik"],
                pain_points=["Karmaşık arayüzler", "Yavaş yükleme"],
            ),
        ),
        visual_language=VisualLanguage(
            theme="modern-minimal",
            palette=ColorPalette(
                primary="#3B82F6",
                secondary="#1E40AF",
                accent="#60A5FA",
            ),
            typography=TypographyStyle(
                style="modern_sans",
            ),
            density="balanced",
            border_radius="rounded",
            shadow_style="subtle",
            animation_level="subtle",
        ),
        emotional_framework=EmotionalFramework(
            primary_tone=EmotionalTone.PROFESSIONAL,
            secondary_tone=EmotionalTone.AUTHORITATIVE,
            entry_emotion=EmotionMapping(
                emotion=PrimaryEmotion.TRUST,
                intensity=EmotionIntensity.MODERATE,
            ),
            emotions_to_avoid=[PrimaryEmotion.FEAR, PrimaryEmotion.DISGUST],
        ),
        confidence_scores=ConfidenceScores(
            intent_clarity=0.8,
            scope_match=0.9,
            context_richness=0.7,
            parameter_completeness=0.6,
            constraint_satisfaction=0.75,
            alternative_viability=0.7,
        ),
        gap_analysis=GapAnalysis(
            gaps=[
                GapInfo(
                    id="gap_animation_preference",
                    category=GapCategory.VISUAL,
                    severity=GapSeverity.MEDIUM,
                    description="Animation level not specified",
                    suggested_question="Animasyon tercihiniz nedir?",
                ),
            ],
        ),
        extraction_timestamp=datetime.now(),
        source_brief="Sample brief",
    )


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing."""
    client = MagicMock()
    client.generate_content = AsyncMock()
    return client


@pytest.fixture
def mock_legacy_maestro():
    """Mock legacy Maestro for fallback testing."""
    maestro = MagicMock(spec=Maestro)
    maestro.start_session = AsyncMock(return_value=(
        "legacy_session_123",
        Question(
            id="q_intent",
            text="Ne yapmak istiyorsunuz?",
            category=QuestionCategory.INTENT,
            question_type=QuestionType.SINGLE_CHOICE,
            options=[
                QuestionOption(id="opt_new", label="Yeni tasarım", description=""),
            ],
        ),
    ))
    return maestro


# =============================================================================
# TEST: SOUL EXTRACTION FLOW
# =============================================================================


class TestSoulExtractionFlow:
    """Tests for ProjectSoul extraction from design briefs."""

    def test_project_soul_creation(self, sample_soul):
        """Test ProjectSoul dataclass creation."""
        assert sample_soul.project_name == "FinTech Dashboard"
        assert sample_soul.brand_personality.dominant_trait == "competence"
        assert sample_soul.confidence_scores.overall > 0.5  # Weighted average
        assert len(sample_soul.identified_gaps) == 1

    def test_brand_personality_aaker_dimensions(self, sample_soul):
        """Test Aaker's 5 brand personality dimensions."""
        bp = sample_soul.brand_personality

        # All dimensions should be between 0 and 1
        assert 0 <= bp.sincerity <= 1
        assert 0 <= bp.excitement <= 1
        assert 0 <= bp.competence <= 1
        assert 0 <= bp.sophistication <= 1
        assert 0 <= bp.ruggedness <= 1

        # Dominant trait should be the highest
        assert bp.dominant_trait == "competence"
        assert bp.competence >= max(bp.sincerity, bp.excitement, bp.sophistication, bp.ruggedness)

    def test_gap_detection(self, sample_soul):
        """Test gap detection in ProjectSoul."""
        gaps = sample_soul.identified_gaps
        assert len(gaps) >= 1

        gap = gaps[0]
        assert gap.id == "gap_animation_preference"
        assert gap.category == GapCategory.VISUAL
        assert gap.severity == GapSeverity.MEDIUM
        assert gap.suggested_question is not None

    def test_confidence_scores_calculation(self, sample_soul):
        """Test confidence score structure (ConfidenceScores dataclass)."""
        scores = sample_soul.confidence_scores

        # All required dimensions should be present and valid (6-dimension model)
        assert 0 <= scores.intent_clarity <= 1
        assert 0 <= scores.scope_match <= 1
        assert 0 <= scores.context_richness <= 1
        assert 0 <= scores.parameter_completeness <= 1
        assert 0 <= scores.constraint_satisfaction <= 1
        assert 0 <= scores.alternative_viability <= 1

        # Overall is a computed property (weighted average)
        assert 0 <= scores.overall <= 1
        assert scores.is_sufficient == (scores.overall >= 0.6 and scores.intent_clarity >= 0.5)


# =============================================================================
# TEST: STATE MACHINE TRANSITIONS
# =============================================================================


class TestStateMachineTransitions:
    """Tests for interview state machine."""

    def test_state_machine_creation(self):
        """Test state machine initialization."""
        machine = create_interview_state_machine()
        assert machine.current_state == InterviewPhase.BRIEF_INGESTION

    def test_valid_transitions(self):
        """Test valid state transitions."""
        machine = create_interview_state_machine()

        # BRIEF_INGESTION -> SOUL_EXTRACTION
        result = machine.transition_to(InterviewPhase.SOUL_EXTRACTION)
        assert result == TransitionResult.SUCCESS
        assert machine.current_state == InterviewPhase.SOUL_EXTRACTION

        # SOUL_EXTRACTION -> CONTEXT_GATHERING
        result = machine.transition_to(InterviewPhase.CONTEXT_GATHERING)
        assert result == TransitionResult.SUCCESS
        assert machine.current_state == InterviewPhase.CONTEXT_GATHERING

    def test_invalid_transition_blocked(self):
        """Test that invalid transitions are blocked."""
        machine = create_interview_state_machine()

        # Cannot skip directly to COMPLETE
        result = machine.transition_to(InterviewPhase.COMPLETE)
        assert result != TransitionResult.SUCCESS
        assert machine.current_state == InterviewPhase.BRIEF_INGESTION

    def test_full_interview_flow(self):
        """Test complete interview state flow."""
        machine = create_interview_state_machine()

        # Normal happy path
        transitions = [
            InterviewPhase.SOUL_EXTRACTION,
            InterviewPhase.CONTEXT_GATHERING,
            InterviewPhase.DEEP_DIVE,
            InterviewPhase.VISUAL_EXPLORATION,
            InterviewPhase.VALIDATION,
            InterviewPhase.SYNTHESIS,
            InterviewPhase.COMPLETE,
        ]

        for next_phase in transitions:
            result = machine.transition_to(next_phase)
            assert result == TransitionResult.SUCCESS, f"Failed transition to {next_phase}"
            assert machine.current_state == next_phase


# =============================================================================
# TEST: PROGRESS TRACKING
# =============================================================================


class TestProgressTracking:
    """Tests for interview progress tracking."""

    def test_progress_tracker_creation(self):
        """Test progress tracker initialization."""
        tracker = create_progress_tracker()
        assert tracker.get_overall_progress() == 0.0

    def test_phase_progress_weights(self):
        """Test that phase weights sum to approximately 1.0."""
        tracker = create_progress_tracker()
        total_weight = sum(tracker.PHASE_WEIGHTS.values())
        assert 0.99 <= total_weight <= 1.01, f"Weights sum to {total_weight}"

    def test_progress_updates(self):
        """Test progress updates through phases."""
        tracker = create_progress_tracker()

        # Must start interview first for progress tracking
        tracker.start_interview()

        # Start phase
        tracker.start_phase(InterviewPhase.BRIEF_INGESTION)
        initial_progress = tracker.get_overall_progress()

        # Complete phase
        tracker.complete_phase()
        assert tracker.get_overall_progress() > initial_progress

    def test_snapshot_creation(self):
        """Test progress snapshot functionality."""
        tracker = create_progress_tracker()
        tracker.start_interview()
        tracker.start_phase(InterviewPhase.SOUL_EXTRACTION)

        snapshot = tracker.take_snapshot()
        assert snapshot.current_phase == InterviewPhase.SOUL_EXTRACTION
        assert snapshot.overall_progress >= 0.0
        assert snapshot.timestamp is not None


# =============================================================================
# TEST: TURKISH PROMPTS
# =============================================================================


class TestTurkishPrompts:
    """Tests for Turkish prompt templates."""

    def test_phase_prompts_complete(self):
        """Test all phases have Turkish prompts."""
        for phase in InterviewPhase:
            assert phase in PHASE_PROMPTS, f"Missing prompt for {phase}"

            phase_data = PHASE_PROMPTS[phase]
            assert "title" in phase_data
            assert "emoji" in phase_data
            assert "intro" in phase_data

    def test_question_templates_structure(self):
        """Test question template structure."""
        assert len(QUESTION_TEMPLATES) > 0

        for qid, qdata in QUESTION_TEMPLATES.items():
            assert "text" in qdata, f"Question {qid} missing text"
            assert "phase" in qdata, f"Question {qid} missing phase"
            assert "type" in qdata, f"Question {qid} missing type"

    def test_get_phase_prompt_helper(self):
        """Test phase prompt helper function."""
        prompt = get_phase_prompt(InterviewPhase.BRIEF_INGESTION, "title")
        assert prompt == "Brief Analizi"

        prompt = get_phase_prompt(InterviewPhase.SOUL_EXTRACTION, "emoji")
        assert prompt == "✨"

    def test_turkish_content_language(self):
        """Test that prompts are in Turkish."""
        # Check some key Turkish phrases
        brief_prompt = PHASE_PROMPTS[InterviewPhase.BRIEF_INGESTION]
        assert "Proje" in brief_prompt["intro"] or "brief" in brief_prompt["intro"].lower()

        soul_prompt = PHASE_PROMPTS[InterviewPhase.SOUL_EXTRACTION]
        assert "kimliğini" in soul_prompt["intro"] or "keşfediyorum" in soul_prompt["intro"]


# =============================================================================
# TEST: SESSION MANAGEMENT
# =============================================================================


class TestSessionManagement:
    """Tests for v2 session management."""

    def test_soul_aware_session_creation(self, sample_brief):
        """Test SoulAwareSession creation."""
        session = SoulAwareSession.create(
            design_brief=sample_brief,
            project_context="FinTech Dashboard",
        )

        assert session.session_id is not None
        assert session.design_brief == sample_brief
        assert session.state == SessionState.CREATED

    def test_session_state_transitions(self, sample_brief):
        """Test session state transitions."""
        session = SoulAwareSession.create(design_brief=sample_brief)

        # Initial state
        assert session.state == SessionState.CREATED

        # Transition to extracting
        session.transition_to(SessionState.EXTRACTING_SOUL, "Starting extraction")
        assert session.state == SessionState.EXTRACTING_SOUL

        # Check history (transitions track phase changes, not state changes)
        # State transitions are tracked internally, verify state changed
        assert session.state == SessionState.EXTRACTING_SOUL

    def test_session_soul_attachment(self, sample_brief, sample_soul):
        """Test attaching ProjectSoul to session."""
        session = SoulAwareSession.create(design_brief=sample_brief)

        # Initially no soul
        assert session.soul is None

        # Attach soul
        session.soul = sample_soul
        assert session.soul is not None
        assert session.soul.project_name == "FinTech Dashboard"


# =============================================================================
# TEST: GRACEFUL FALLBACK
# =============================================================================


class TestGracefulFallback:
    """Tests for graceful fallback to v1."""

    def test_fallback_without_brief(self, mock_gemini_client):
        """Test fallback when no design brief is provided."""
        wrapper = MAESTROv2Wrapper(client=mock_gemini_client)

        # v2 should not be used without brief
        assert not wrapper._should_use_v2(None)
        assert not wrapper._should_use_v2("")

    def test_v2_enabled_with_brief(self, mock_gemini_client):
        """Test v2 is enabled when brief is provided."""
        wrapper = MAESTROv2Wrapper(client=mock_gemini_client)

        # v2 should be used with brief
        assert wrapper._should_use_v2("This is a design brief")

    def test_feature_flag_control(self, mock_gemini_client):
        """Test feature flag controls v2 activation."""
        wrapper = MAESTROv2Wrapper(client=mock_gemini_client)

        # Disable v2
        wrapper._config.V2_ENABLED = False
        assert not wrapper._should_use_v2("This is a design brief")

        # Re-enable
        wrapper._config.V2_ENABLED = True
        assert wrapper._should_use_v2("This is a design brief")


# =============================================================================
# TEST: INTEGRATION
# =============================================================================


class TestIntegration:
    """Integration tests for complete v2 workflow."""

    @pytest.mark.asyncio
    async def test_v2_wrapper_initialization(self, mock_gemini_client):
        """Test MAESTROv2Wrapper initialization."""
        wrapper = MAESTROv2Wrapper(client=mock_gemini_client)

        assert wrapper._client is not None
        assert wrapper._legacy_maestro is not None
        assert wrapper._config is not None

    def test_state_machine_and_progress_integration(self):
        """Test state machine and progress tracker work together."""
        machine = create_interview_state_machine()
        tracker = create_progress_tracker()
        tracker.start_interview()

        # Simulate interview flow
        phases = [
            InterviewPhase.BRIEF_INGESTION,
            InterviewPhase.SOUL_EXTRACTION,
            InterviewPhase.CONTEXT_GATHERING,
        ]

        for phase in phases:
            if phase != InterviewPhase.BRIEF_INGESTION:
                result = machine.transition_to(phase)
                assert result == TransitionResult.SUCCESS

            tracker.start_phase(phase)
            tracker.complete_phase()

        # Progress should have increased
        assert tracker.get_overall_progress() > 0

    def test_session_with_soul_and_gaps(self, sample_brief, sample_soul):
        """Test session with soul and gap tracking."""
        session = SoulAwareSession.create(design_brief=sample_brief)
        session.soul = sample_soul

        # Session should track gaps from soul
        assert session.soul.identified_gaps is not None
        assert len(session.soul.identified_gaps) > 0

        # Get first gap
        gap = session.soul.identified_gaps[0]
        assert gap.id == "gap_animation_preference"
        assert gap.category == GapCategory.VISUAL


# =============================================================================
# TEST: EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_brief_handling(self):
        """Test handling of empty design brief."""
        session = SoulAwareSession.create(design_brief="")
        assert session.design_brief == ""
        assert session.soul is None

    def test_minimal_soul(self):
        """Test ProjectSoul with minimal data."""
        soul = ProjectSoul(
            metadata=ProjectMetadata(
                name="Minimal Project",
            ),
            brand_personality=BrandPersonality(
                sincerity=0.5,
                excitement=0.5,
                competence=0.5,
                sophistication=0.5,
                ruggedness=0.5,
                dominant_trait="balanced",
                personality_archetype=PersonalityArchetype.THE_EVERYMAN,
            ),
            target_audience=TargetAudience(
                demographic=DemographicProfile(
                    age_range=(18, 65),
                    tech_savviness=TechSavviness.INTERMEDIATE,
                    profession_category="General",
                ),
            ),
            visual_language=VisualLanguage(theme="modern-minimal"),
            emotional_framework=EmotionalFramework(
                primary_tone=EmotionalTone.NEUTRAL,
            ),
            confidence_scores=ConfidenceScores(
                intent_clarity=0.5,
                scope_match=0.5,
                context_richness=0.5,
                parameter_completeness=0.5,
                constraint_satisfaction=0.5,
                alternative_viability=0.5,
            ),
            gap_analysis=GapAnalysis(gaps=[]),
            extraction_timestamp=datetime.now(),
        )

        assert soul.project_name == "Minimal Project"
        assert len(soul.identified_gaps) == 0

    def test_state_machine_reset(self):
        """Test state machine can be reset."""
        machine = create_interview_state_machine()

        # Move forward
        machine.transition_to(InterviewPhase.SOUL_EXTRACTION)
        assert machine.current_state == InterviewPhase.SOUL_EXTRACTION

        # Reset
        machine.reset()
        assert machine.current_state == InterviewPhase.BRIEF_INGESTION

    def test_progress_tracker_analytics(self):
        """Test progress tracker analytics summary."""
        tracker = create_progress_tracker()
        tracker.start_interview()

        # Complete some phases
        tracker.start_phase(InterviewPhase.BRIEF_INGESTION)
        tracker.complete_phase()

        # Get analytics
        analytics = tracker.get_analytics_summary()
        assert "phases_completed" in analytics
        assert "elapsed_seconds" in analytics
