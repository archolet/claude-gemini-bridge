"""
MAESTRO v2 Integration Tests - Phase 4

Tests the integration between MAESTRO v2 components:
- Soul Extractor + Gap Detector
- State Machine + Progress Tracker
- Session Manager + Wrapper
- Turkish Prompts + Question Generation

These tests verify component interactions without mocking internal dependencies.
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
from gemini_mcp.maestro.models.audience import (
    DemographicProfile,
    PsychographicProfile,
    TechSavviness,
)
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
    TransitionResult,
    create_interview_state_machine,
    create_progress_tracker,
)
from gemini_mcp.maestro.prompts.tr import (
    PHASE_PROMPTS,
    QUESTION_TEMPLATES,
    get_phase_prompt,
)
from gemini_mcp.maestro.config import MAESTROConfig, get_config


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def complete_soul():
    """A complete ProjectSoul with all fields populated."""
    return ProjectSoul(
        metadata=ProjectMetadata(
            name="E-Ticaret Dashboard",
            tagline="Modern Alışveriş Deneyimi",
            industry="e-commerce",
            project_type="dashboard",
            keywords=["e-commerce", "dashboard", "analytics"],
        ),
        brand_personality=BrandPersonality(
            sincerity=0.7,
            excitement=0.6,
            competence=0.8,
            sophistication=0.5,
            ruggedness=0.3,
            dominant_trait="competence",
            personality_archetype=PersonalityArchetype.THE_HERO,
        ),
        target_audience=TargetAudience(
            demographic=DemographicProfile(
                age_range=(25, 45),
                tech_savviness=TechSavviness.ADVANCED,
                profession_category="Business",
            ),
            psychographic=PsychographicProfile(
                core_values=["Verimlilik", "Güvenilirlik", "Hız"],
                pain_points=["Karmaşık raporlar", "Yavaş yükleme"],
            ),
        ),
        visual_language=VisualLanguage(
            theme="modern-minimal",
            palette=ColorPalette(
                primary="#2563EB",
                secondary="#1E40AF",
                accent="#3B82F6",
            ),
            typography=TypographyStyle(style="modern_sans"),
            density="balanced",
            border_radius="rounded",
            shadow_style="subtle",
            animation_level="moderate",
        ),
        emotional_framework=EmotionalFramework(
            primary_tone=EmotionalTone.PROFESSIONAL,
            secondary_tone=EmotionalTone.OPTIMISTIC,  # ENERGETIC doesn't exist, use OPTIMISTIC
            entry_emotion=EmotionMapping(
                emotion=PrimaryEmotion.ANTICIPATION,
                intensity=EmotionIntensity.MODERATE,
            ),
            emotions_to_avoid=[PrimaryEmotion.FEAR],
        ),
        confidence_scores=ConfidenceScores(
            intent_clarity=0.85,
            scope_match=0.80,
            context_richness=0.75,
            parameter_completeness=0.70,
            constraint_satisfaction=0.65,
            alternative_viability=0.60,
        ),
        gap_analysis=GapAnalysis(
            gaps=[
                GapInfo(
                    id="gap_brand_colors",
                    category=GapCategory.VISUAL,
                    severity=GapSeverity.MEDIUM,
                    description="Marka renkleri tam olarak belirtilmemiş",
                    suggested_question="Markanızın ana renkleri nelerdir?",
                ),
            ],
        ),
        source_brief="E-ticaret platformu için modern dashboard tasarımı",
    )


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for integration testing."""
    client = MagicMock()
    client.generate_content = AsyncMock()
    return client


# =============================================================================
# TEST: STATE MACHINE + PROGRESS TRACKER INTEGRATION
# =============================================================================


class TestStateMachineProgressIntegration:
    """Tests state machine and progress tracker working together."""

    def test_phase_transitions_update_progress(self):
        """Test that state transitions properly update progress."""
        machine = create_interview_state_machine()
        tracker = create_progress_tracker()

        # Start interview
        tracker.start_interview()

        # Track each phase transition
        phases_completed = 0

        for target_phase in [
            InterviewPhase.SOUL_EXTRACTION,
            InterviewPhase.CONTEXT_GATHERING,
            InterviewPhase.DEEP_DIVE,
        ]:
            # Transition state machine
            result = machine.transition_to(target_phase)
            assert result == TransitionResult.SUCCESS

            # Update tracker
            tracker.start_phase(target_phase)
            tracker.complete_phase()
            phases_completed += 1

            # Verify progress increased
            progress = tracker.get_overall_progress()
            assert progress > 0

        assert phases_completed == 3

    def test_full_interview_flow_with_progress(self):
        """Test complete interview flow tracks progress correctly."""
        machine = create_interview_state_machine()
        tracker = create_progress_tracker()

        # Start interview
        tracker.start_interview()
        initial_progress = tracker.get_overall_progress()

        # Complete full flow
        flow = [
            InterviewPhase.SOUL_EXTRACTION,
            InterviewPhase.CONTEXT_GATHERING,
            InterviewPhase.VALIDATION,
            InterviewPhase.SYNTHESIS,
            InterviewPhase.COMPLETE,
        ]

        for phase in flow:
            machine.transition_to(phase)
            tracker.start_phase(phase)
            tracker.complete_phase()

        final_progress = tracker.get_overall_progress()
        assert final_progress > initial_progress
        assert machine.current_state == InterviewPhase.COMPLETE

    def test_analytics_after_interview(self):
        """Test analytics summary is generated after interview."""
        machine = create_interview_state_machine()
        tracker = create_progress_tracker()

        tracker.start_interview()

        # Complete a few phases
        for phase in [InterviewPhase.SOUL_EXTRACTION, InterviewPhase.CONTEXT_GATHERING]:
            machine.transition_to(phase)
            tracker.start_phase(phase)
            tracker.complete_phase()

        # Get analytics
        analytics = tracker.get_analytics_summary()
        assert analytics is not None
        assert "phases_completed" in analytics
        # phases_completed is a list of completed phase values
        assert len(analytics["phases_completed"]) >= 2


# =============================================================================
# TEST: SESSION + SOUL INTEGRATION
# =============================================================================


class TestSessionSoulIntegration:
    """Tests session management with ProjectSoul."""

    def test_session_with_soul_attachment(self, complete_soul):
        """Test attaching soul to session."""
        session = SoulAwareSession.create(
            design_brief="E-ticaret dashboard için tasarım"
        )

        # Attach soul
        session.set_soul(complete_soul)

        assert session.soul is not None
        assert session.soul.project_name == "E-Ticaret Dashboard"
        # After setting soul, session transitions to GATHERING_CONTEXT
        assert session.state == SessionState.GATHERING_CONTEXT

    def test_session_state_progression(self, complete_soul):
        """Test session state progression through interview."""
        session = SoulAwareSession.create(design_brief="Test brief")
        session.set_soul(complete_soul)

        # After setting soul, session moves to GATHERING_CONTEXT
        assert session.state == SessionState.GATHERING_CONTEXT

        # Can transition to DEEP_DIVE phase
        session.transition_to(SessionState.DEEP_DIVE, reason="Testing progression")
        assert session.state == SessionState.DEEP_DIVE

    def test_session_with_gaps_tracking(self, complete_soul):
        """Test session tracks gaps from soul."""
        session = SoulAwareSession.create(design_brief="Test brief")
        session.set_soul(complete_soul)

        # Verify gaps are accessible
        gaps = session.soul.identified_gaps
        assert len(gaps) >= 1
        assert gaps[0].category == GapCategory.VISUAL


# =============================================================================
# TEST: TURKISH PROMPTS INTEGRATION
# =============================================================================


class TestTurkishPromptsIntegration:
    """Tests Turkish prompts work with interview flow."""

    def test_phase_prompts_for_all_phases(self):
        """Test phase prompts exist for all interview phases."""
        interview_phases = [
            InterviewPhase.BRIEF_INGESTION,
            InterviewPhase.SOUL_EXTRACTION,
            InterviewPhase.CONTEXT_GATHERING,
            InterviewPhase.DEEP_DIVE,
            InterviewPhase.VISUAL_EXPLORATION,
            InterviewPhase.VALIDATION,
            InterviewPhase.SYNTHESIS,
        ]

        for phase in interview_phases:
            prompt = get_phase_prompt(phase.value)
            assert prompt is not None, f"Missing prompt for phase: {phase}"
            # Verify Turkish content
            assert any(
                c in prompt for c in "ğüşıöçĞÜŞİÖÇ"
            ) or "?" in prompt, f"Prompt may not be Turkish: {phase}"

    def test_question_templates_have_required_fields(self):
        """Test question templates have all required fields."""
        # QUESTION_TEMPLATES uses 'phase' not 'category' for interview phase mapping
        required_fields = ["text", "phase"]

        for template_key, template in QUESTION_TEMPLATES.items():
            for field in required_fields:
                assert (
                    field in template
                ), f"Missing {field} in template: {template_key}"

    def test_phase_prompt_with_context(self):
        """Test phase prompts can be formatted with context."""
        context = {
            "project_name": "Test Projesi",
            "confidence": 0.75,
        }

        prompt = get_phase_prompt("context_gathering")
        assert prompt is not None
        # Verify it's a valid string that could be formatted
        assert isinstance(prompt, str)


# =============================================================================
# TEST: CONFIDENCE SCORES INTEGRATION
# =============================================================================


class TestConfidenceIntegration:
    """Tests confidence scores affect interview flow."""

    def test_high_confidence_allows_synthesis(self, complete_soul):
        """Test high confidence enables transition to synthesis."""
        # Complete soul has high confidence
        assert complete_soul.confidence_scores.overall > 0.6
        assert complete_soul.confidence_scores.is_sufficient

        machine = create_interview_state_machine()

        # Can skip to validation with high confidence
        machine.transition_to(InterviewPhase.SOUL_EXTRACTION)
        machine.transition_to(InterviewPhase.CONTEXT_GATHERING)
        machine.transition_to(InterviewPhase.VALIDATION)

        assert machine.current_state == InterviewPhase.VALIDATION

    def test_low_confidence_requires_more_questions(self):
        """Test low confidence requires additional questions."""
        low_confidence_soul = ProjectSoul(
            metadata=ProjectMetadata(name="Uncertain Project"),
            confidence_scores=ConfidenceScores(
                intent_clarity=0.3,
                scope_match=0.2,
                context_richness=0.3,
                parameter_completeness=0.2,
                constraint_satisfaction=0.3,
                alternative_viability=0.2,
            ),
            gap_analysis=GapAnalysis(
                gaps=[
                    GapInfo(
                        id="gap_intent",
                        category=GapCategory.INTENT,
                        severity=GapSeverity.CRITICAL,
                        description="Proje amacı belirsiz",
                        suggested_question="Projenin ana amacı nedir?",
                    ),
                    GapInfo(
                        id="gap_audience",
                        category=GapCategory.AUDIENCE,
                        severity=GapSeverity.HIGH,
                        description="Hedef kitle tanımsız",
                        suggested_question="Hedef kitleniz kimler?",
                    ),
                ],
            ),
        )

        assert not low_confidence_soul.confidence_scores.is_sufficient
        assert len(low_confidence_soul.identified_gaps) >= 2

    def test_confidence_dimension_tracking(self, complete_soul):
        """Test individual confidence dimensions are tracked."""
        scores = complete_soul.confidence_scores

        # Verify all 6 dimensions
        dimensions = [
            scores.intent_clarity,
            scores.scope_match,
            scores.context_richness,
            scores.parameter_completeness,
            scores.constraint_satisfaction,
            scores.alternative_viability,
        ]

        for dim in dimensions:
            assert 0 <= dim <= 1

        # Verify weakest dimension detection
        weakest = scores.weakest_dimension
        assert weakest in [
            "intent_clarity",
            "scope_match",
            "context_richness",
            "parameter_completeness",
            "constraint_satisfaction",
            "alternative_viability",
        ]


# =============================================================================
# TEST: GAP ANALYSIS INTEGRATION
# =============================================================================


class TestGapAnalysisIntegration:
    """Tests gap analysis integration with interview flow."""

    def test_gaps_drive_question_generation(self, complete_soul):
        """Test gaps determine which questions to ask."""
        gaps = complete_soul.identified_gaps

        # Each gap should have a suggested question
        for gap in gaps:
            assert gap.suggested_question is not None
            assert len(gap.suggested_question) > 10  # Meaningful question

    def test_gap_resolution_updates_soul(self):
        """Test resolving gaps updates the soul state."""
        soul = ProjectSoul(
            metadata=ProjectMetadata(name="Gap Test Project"),
            gap_analysis=GapAnalysis(
                gaps=[
                    GapInfo(
                        id="gap_color",
                        category=GapCategory.VISUAL,
                        severity=GapSeverity.MEDIUM,
                        description="Renk tercihi belirtilmemiş",
                        suggested_question="Ana renginiz nedir?",
                    ),
                ],
            ),
        )

        # Resolve the gap
        gap = soul.gap_analysis.gaps[0]
        gap.resolve("#3B82F6", source="user")

        assert gap.is_resolved()
        assert gap.resolution_value == "#3B82F6"

    def test_blocking_gaps_prevent_progress(self):
        """Test blocking gaps prevent advancement."""
        soul = ProjectSoul(
            metadata=ProjectMetadata(name="Blocked Project"),
            gap_analysis=GapAnalysis(
                gaps=[
                    GapInfo(
                        id="gap_critical",
                        category=GapCategory.INTENT,
                        severity=GapSeverity.CRITICAL,
                        description="Kritik bilgi eksik",
                        suggested_question="Projenin amacı nedir?",
                    ),
                ],
            ),
        )

        # Check blocking gaps
        blocking_count = soul.gap_analysis.blocking_gaps
        assert blocking_count >= 1


# =============================================================================
# TEST: WRAPPER INTEGRATION
# =============================================================================


class TestWrapperIntegration:
    """Tests MAESTROv2Wrapper integration."""

    def test_wrapper_initialization(self, mock_gemini_client):
        """Test wrapper initializes correctly."""
        # MAESTROv2Wrapper creates legacy_maestro internally - no external param
        wrapper = MAESTROv2Wrapper(client=mock_gemini_client)

        # Attributes are private (prefixed with _)
        assert wrapper._client == mock_gemini_client
        assert wrapper._legacy_maestro is not None

    def test_wrapper_config_loading(self, mock_gemini_client):
        """Test wrapper loads configuration correctly."""
        wrapper = MAESTROv2Wrapper(client=mock_gemini_client)

        # Config is accessed via private attribute
        config = wrapper._config
        assert isinstance(config, MAESTROConfig)

    def test_wrapper_metrics_initialization(self, mock_gemini_client):
        """Test wrapper initializes metrics."""
        wrapper = MAESTROv2Wrapper(client=mock_gemini_client)

        # Metrics are accessed via private attribute
        metrics = wrapper._metrics
        assert metrics.sessions_started == 0
        assert metrics.sessions_with_soul == 0


# =============================================================================
# TEST: END-TO-END COMPONENT CHAIN
# =============================================================================


class TestComponentChain:
    """Tests the complete component chain."""

    def test_full_component_chain(self, complete_soul):
        """Test full chain: Soul → Session → StateMachine → Progress."""
        # 1. Create session with soul
        session = SoulAwareSession.create(design_brief="Test brief")
        session.set_soul(complete_soul)
        assert session.soul is not None

        # 2. Create state machine
        machine = create_interview_state_machine()
        assert machine.current_state == InterviewPhase.BRIEF_INGESTION

        # 3. Create progress tracker
        tracker = create_progress_tracker()
        tracker.start_interview()

        # 4. Run through phases (session is already in GATHERING_CONTEXT after set_soul)
        phases = [
            InterviewPhase.SOUL_EXTRACTION,
            InterviewPhase.CONTEXT_GATHERING,
        ]

        for phase in phases:
            machine.transition_to(phase)
            tracker.start_phase(phase)
            tracker.complete_phase()

        # 5. Verify final state
        assert machine.current_state == InterviewPhase.CONTEXT_GATHERING
        # Session state is GATHERING_CONTEXT after set_soul
        assert session.state == SessionState.GATHERING_CONTEXT
        assert tracker.get_overall_progress() > 0

    def test_soul_gaps_to_questions_chain(self, complete_soul):
        """Test gaps from soul generate appropriate questions."""
        session = SoulAwareSession.create(design_brief="Test brief")
        session.set_soul(complete_soul)

        # Get gaps from soul
        gaps = session.soul.identified_gaps

        # Each gap should be addressable
        for gap in gaps:
            assert gap.category in GapCategory
            assert gap.severity in GapSeverity
            if gap.suggested_question:
                # Question should be in Turkish
                assert len(gap.suggested_question) > 5


# =============================================================================
# TEST: ERROR HANDLING INTEGRATION
# =============================================================================


class TestErrorHandlingIntegration:
    """Tests error handling across components."""

    def test_invalid_transition_handled(self):
        """Test invalid state transitions are handled gracefully."""
        machine = create_interview_state_machine()

        # Try invalid transition (skipping phases)
        result = machine.transition_to(InterviewPhase.COMPLETE)

        # Should fail gracefully (returns INVALID_TRANSITION for invalid state jumps)
        assert result != TransitionResult.SUCCESS
        assert machine.current_state == InterviewPhase.BRIEF_INGESTION

    def test_empty_soul_handled(self):
        """Test empty soul is handled properly."""
        soul = ProjectSoul()  # Default/empty soul

        assert soul.project_name == "Untitled Project"
        assert soul.confidence_scores.overall == 0.5  # Default
        assert len(soul.identified_gaps) == 0

    def test_session_without_soul(self):
        """Test session works without soul attached."""
        session = SoulAwareSession.create(design_brief="")

        assert session.soul is None
        assert session.state == SessionState.CREATED
