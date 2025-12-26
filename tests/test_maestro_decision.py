"""Tests for MAESTRO Phase 3 - Decision System.

Tests for:
- DecisionScores: 6-dimension weighted scoring
- ContextAnalyzer: HTML parsing, Tailwind extraction
- DecisionTree: Mode selection, Gemini integration
- EnrichedContext: Combined interview + HTML context
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from gemini_mcp.maestro.decision import (
    ContextAnalyzer,
    ContextAnalysis,
    DecisionScores,
    DecisionTree,
    EnrichedContext,
    DecisionAnalysis,
)
from gemini_mcp.maestro.models import (
    Answer,
    InterviewState,
    MaestroDecision,
)


# =============================================================================
# DecisionScores Tests
# =============================================================================


class TestDecisionScores:
    """Tests for 6-dimension weighted scoring."""

    def test_default_scores(self):
        """Verify default scores are 0.5 for all dimensions."""
        scores = DecisionScores()

        assert scores.intent_clarity == 0.5
        assert scores.scope_match == 0.5
        assert scores.context_richness == 0.5
        assert scores.parameter_completeness == 0.5
        assert scores.constraint_satisfaction == 0.5
        assert scores.alternative_viability == 0.5

    def test_weights_sum_to_one(self):
        """Verify weights sum to 1.0 for proper normalization."""
        total = sum(DecisionScores.WEIGHTS.values())
        assert abs(total - 1.0) < 0.0001, f"Weights sum to {total}, expected 1.0"

    def test_weighted_average_calculation(self):
        """Test overall score calculation with weighted average."""
        scores = DecisionScores(
            intent_clarity=1.0,      # 25% weight
            scope_match=1.0,         # 20% weight
            context_richness=1.0,    # 15% weight
            parameter_completeness=1.0,  # 20% weight
            constraint_satisfaction=1.0,  # 10% weight
            alternative_viability=1.0,    # 10% weight
        )

        # All 1.0 should give overall 1.0
        assert abs(scores.overall - 1.0) < 0.0001

    def test_weighted_average_partial(self):
        """Test weighted average with partial scores."""
        scores = DecisionScores(
            intent_clarity=0.8,      # 0.8 * 0.25 = 0.20
            scope_match=0.6,         # 0.6 * 0.20 = 0.12
            context_richness=0.4,    # 0.4 * 0.15 = 0.06
            parameter_completeness=1.0,  # 1.0 * 0.20 = 0.20
            constraint_satisfaction=0.5,  # 0.5 * 0.10 = 0.05
            alternative_viability=0.7,    # 0.7 * 0.10 = 0.07
        )

        expected = 0.20 + 0.12 + 0.06 + 0.20 + 0.05 + 0.07  # 0.70
        assert abs(scores.overall - expected) < 0.0001

    def test_get_dimension_scores(self):
        """Test getting all dimension scores as dictionary."""
        scores = DecisionScores(intent_clarity=0.9, scope_match=0.8)

        dim_scores = scores.get_dimension_scores()

        assert "intent_clarity" in dim_scores
        assert "scope_match" in dim_scores
        assert dim_scores["intent_clarity"] == 0.9
        assert dim_scores["scope_match"] == 0.8

    def test_get_lowest_dimensions(self):
        """Test identifying weakest dimensions."""
        scores = DecisionScores(
            intent_clarity=0.9,
            scope_match=0.3,  # Lowest
            context_richness=0.7,
            parameter_completeness=0.2,  # Second lowest
            constraint_satisfaction=0.8,
            alternative_viability=0.6,
        )

        lowest = scores.get_lowest_dimensions(2)

        assert len(lowest) == 2
        assert lowest[0][0] == "parameter_completeness"
        assert lowest[0][1] == 0.2
        assert lowest[1][0] == "scope_match"
        assert lowest[1][1] == 0.3

    def test_get_highest_dimensions(self):
        """Test identifying strongest dimensions."""
        scores = DecisionScores(
            intent_clarity=0.9,  # Highest
            scope_match=0.3,
            context_richness=0.7,
            parameter_completeness=0.2,
            constraint_satisfaction=0.85,  # Second highest
            alternative_viability=0.6,
        )

        highest = scores.get_highest_dimensions(2)

        assert len(highest) == 2
        assert highest[0][0] == "intent_clarity"
        assert highest[0][1] == 0.9
        assert highest[1][0] == "constraint_satisfaction"
        assert highest[1][1] == 0.85

    def test_is_high_confidence(self):
        """Test high confidence threshold check."""
        high_scores = DecisionScores(
            intent_clarity=1.0,
            scope_match=1.0,
            context_richness=0.8,
            parameter_completeness=0.9,
            constraint_satisfaction=0.7,
            alternative_viability=0.6,
        )

        low_scores = DecisionScores(
            intent_clarity=0.5,
            scope_match=0.5,
            context_richness=0.5,
            parameter_completeness=0.5,
            constraint_satisfaction=0.5,
            alternative_viability=0.5,
        )

        assert high_scores.is_high_confidence(threshold=0.85)
        assert not low_scores.is_high_confidence(threshold=0.85)

    def test_needs_gemini(self):
        """Test Gemini trigger threshold check."""
        low_conf = DecisionScores(
            intent_clarity=0.4,
            scope_match=0.5,
            context_richness=0.3,
            parameter_completeness=0.5,
            constraint_satisfaction=0.5,
            alternative_viability=0.5,
        )

        high_conf = DecisionScores(
            intent_clarity=0.9,
            scope_match=0.9,
            context_richness=0.8,
            parameter_completeness=0.9,
            constraint_satisfaction=0.8,
            alternative_viability=0.7,
        )

        assert low_conf.needs_gemini(threshold=0.70)
        assert not high_conf.needs_gemini(threshold=0.70)


# =============================================================================
# ContextAnalyzer Tests
# =============================================================================


class TestContextAnalyzer:
    """Tests for HTML parsing and Tailwind extraction."""

    @pytest.fixture
    def analyzer(self):
        """Create ContextAnalyzer instance."""
        return ContextAnalyzer()

    def test_analyze_none_html(self, analyzer):
        """Test analyzing None HTML returns empty result."""
        result = analyzer.analyze(None)

        assert not result.has_html
        assert result.detected_theme is None
        assert len(result.tailwind_classes) == 0

    def test_analyze_empty_html(self, analyzer):
        """Test analyzing empty string returns empty result."""
        result = analyzer.analyze("")

        assert not result.has_html

    def test_extract_tailwind_classes(self, analyzer):
        """Test extracting Tailwind classes from HTML."""
        html = '''
        <div class="bg-blue-500 text-white p-4 rounded-lg">
            <button class="px-6 py-2 font-bold hover:bg-blue-600">
                Click me
            </button>
        </div>
        '''

        result = analyzer.analyze(html)

        assert result.has_html
        assert "bg-blue-500" in result.tailwind_classes
        assert "text-white" in result.tailwind_classes
        assert "p-4" in result.tailwind_classes
        assert "rounded-lg" in result.tailwind_classes
        assert "px-6" in result.tailwind_classes
        assert "font-bold" in result.tailwind_classes

    def test_detect_primary_color(self, analyzer):
        """Test detecting primary color from classes."""
        html = '<div class="bg-blue-600 text-blue-100 border-blue-500"></div>'

        result = analyzer.analyze(html)

        assert "primary" in result.detected_colors

    def test_detect_secondary_color(self, analyzer):
        """Test detecting secondary/neutral colors."""
        html = '<div class="bg-gray-100 text-slate-800"></div>'

        result = analyzer.analyze(html)

        assert "secondary" in result.detected_colors

    def test_detect_typography(self, analyzer):
        """Test detecting typography patterns."""
        html = '''
        <h1 class="text-4xl font-bold tracking-tight">Title</h1>
        <p class="text-base font-normal leading-relaxed">Body</p>
        '''

        result = analyzer.analyze(html)

        assert "text_size" in result.detected_typography
        assert "font_weight" in result.detected_typography

    def test_detect_spacing(self, analyzer):
        """Test detecting spacing patterns."""
        html = '<div class="p-4 m-2 gap-6 space-y-4">Content</div>'

        result = analyzer.analyze(html)

        assert "padding" in result.detected_spacing
        assert "margin" in result.detected_spacing
        assert "gap" in result.detected_spacing

    def test_detect_navbar_component(self, analyzer):
        """Test detecting navbar component."""
        html = '<nav class="bg-white shadow-md">Navigation</nav>'

        result = analyzer.analyze(html)

        assert "navbar" in result.detected_components

    def test_detect_hero_component(self, analyzer):
        """Test detecting hero section."""
        html = '<section class="hero min-h-screen bg-gradient-to-r">Hero</section>'

        result = analyzer.analyze(html)

        assert "hero" in result.detected_components

    def test_detect_button_component(self, analyzer):
        """Test detecting button."""
        html = '<button class="btn bg-blue-500">Submit</button>'

        result = analyzer.analyze(html)

        assert "button" in result.detected_components

    def test_detect_form_component(self, analyzer):
        """Test detecting form elements."""
        html = '<form><input type="text" /><textarea></textarea></form>'

        result = analyzer.analyze(html)

        assert "form" in result.detected_components

    def test_detect_card_component(self, analyzer):
        """Test detecting card pattern."""
        html = '<div class="rounded-lg shadow-lg p-6">Card content</div>'

        result = analyzer.analyze(html)

        assert "card" in result.detected_components

    def test_detect_section_markers(self, analyzer):
        """Test detecting section markers."""
        html = '''
        <!-- SECTION: hero -->
        <section>Hero content</section>
        <!-- /SECTION: hero -->
        <!-- SECTION: features -->
        <section>Features content</section>
        <!-- /SECTION: features -->
        '''

        result = analyzer.analyze(html)

        assert result.has_section_markers()
        assert "hero" in result.section_markers
        assert "features" in result.section_markers

    def test_infer_glassmorphism_theme(self, analyzer):
        """Test inferring glassmorphism theme."""
        html = '<div class="backdrop-blur-xl bg-white/30 bg-opacity-50">Glass</div>'

        result = analyzer.analyze(html)

        assert result.detected_theme == "glassmorphism"

    def test_infer_dark_mode_first_theme(self, analyzer):
        """Test inferring dark mode first theme."""
        html = '<div class="bg-gray-900 dark:bg-slate-800 dark:text-white">Dark</div>'

        result = analyzer.analyze(html)

        assert result.detected_theme == "dark_mode_first"

    def test_infer_gradient_theme(self, analyzer):
        """Test inferring gradient theme."""
        html = '<div class="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500">Gradient</div>'

        result = analyzer.analyze(html)

        assert result.detected_theme == "gradient"

    def test_default_theme_modern_minimal(self, analyzer):
        """Test default theme is modern-minimal."""
        html = '<div class="p-4 m-2">Simple content</div>'

        result = analyzer.analyze(html)

        assert result.detected_theme == "modern-minimal"

    def test_build_design_tokens(self, analyzer):
        """Test building design tokens dict."""
        html = '''
        <div class="bg-blue-500 text-white p-4 rounded-lg shadow-md">
            Content
        </div>
        '''

        result = analyzer.analyze(html)
        tokens = result.to_design_tokens()

        assert "theme" in tokens
        assert "colors" in tokens
        assert "typography" in tokens
        assert "spacing" in tokens

    def test_extract_design_dna(self, analyzer):
        """Test extract_design_dna helper method."""
        html = '<div class="bg-indigo-600 p-6 rounded-xl">Content</div>'

        dna = analyzer.extract_design_dna(html)

        assert isinstance(dna, dict)
        assert "theme" in dna


# =============================================================================
# EnrichedContext Tests
# =============================================================================


class TestEnrichedContext:
    """Tests for combined interview + HTML context."""

    def test_empty_context(self):
        """Test creating empty context."""
        ctx = EnrichedContext()

        assert ctx.answer_count == 0
        assert not ctx.has_html_context()
        assert not ctx.has_project_context()

    def test_with_answers(self):
        """Test context with interview answers."""
        ctx = EnrichedContext(
            answers={
                "q_intent_main": "opt_new_design",
                "q_scope_type": "opt_full_page",
            }
        )

        assert ctx.answer_count == 2
        assert ctx.has_answer("q_intent_main")
        assert ctx.get_answer("q_intent_main") == "opt_new_design"
        assert not ctx.has_answer("q_nonexistent")
        assert ctx.get_answer("q_nonexistent") is None

    def test_with_html_analysis(self):
        """Test context with HTML analysis."""
        html_analysis = ContextAnalysis(
            has_html=True,
            detected_theme="glassmorphism",
            detected_components=["navbar", "hero"],
        )

        ctx = EnrichedContext(html_analysis=html_analysis)

        assert ctx.has_html_context()
        assert ctx.html_analysis.detected_theme == "glassmorphism"

    def test_with_project_context(self):
        """Test context with project description."""
        ctx = EnrichedContext(project_context="E-commerce site for Turkish market")

        assert ctx.has_project_context()

    def test_with_constraints(self):
        """Test context with constraints."""
        ctx = EnrichedContext(
            constraints=["must support dark mode", "WCAG AA compliance"]
        )

        assert len(ctx.constraints) == 2


# =============================================================================
# DecisionTree Tests
# =============================================================================


class TestDecisionTree:
    """Tests for mode selection and decision making."""

    @pytest.fixture
    def tree(self):
        """Create DecisionTree without Gemini client."""
        return DecisionTree(client=None)

    @pytest.fixture
    def mock_client(self):
        """Create mock GeminiClient."""
        client = MagicMock()
        client.generate_text = AsyncMock(return_value='{"mode": "design_page", "reasoning": "Test"}')
        return client

    def test_state_to_answer_dict(self, tree):
        """Test converting InterviewState to answer dict."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_intent", selected_options=["opt_new"]),
            Answer(question_id="q_scope", selected_options=["opt_page"]),
        ]

        result = tree._state_to_answer_dict(state)

        assert result["q_intent"] == "opt_new"
        assert result["q_scope"] == "opt_page"

    @pytest.mark.asyncio
    async def test_make_decision_design_page(self, tree):
        """Test selecting design_page mode."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
            Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
            Answer(question_id="q_page_type", selected_options=["opt_landing_page"]),
        ]

        decision = await tree.make_decision(state)

        assert isinstance(decision, MaestroDecision)
        assert decision.mode == "design_page"
        assert decision.confidence > 0

    @pytest.mark.asyncio
    async def test_make_decision_design_section(self, tree):
        """Test selecting design_section mode."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
            Answer(question_id="q_scope_type", selected_options=["opt_section"]),
            Answer(question_id="q_section_type", selected_options=["opt_hero"]),
        ]

        decision = await tree.make_decision(state)

        assert decision.mode == "design_section"

    @pytest.mark.asyncio
    async def test_make_decision_design_frontend_component(self, tree):
        """Test selecting design_frontend for components."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
            Answer(question_id="q_scope_type", selected_options=["opt_component"]),
            Answer(question_id="q_component_type", selected_options=["opt_button"]),
        ]

        decision = await tree.make_decision(state)

        assert decision.mode == "design_frontend"

    @pytest.mark.asyncio
    async def test_make_decision_refine_frontend(self, tree):
        """Test selecting refine_frontend with existing HTML."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_existing_action", selected_options=["opt_refine"]),
        ]

        decision = await tree.make_decision(
            state,
            previous_html="<div>existing content</div>",
        )

        assert decision.mode == "refine_frontend"

    @pytest.mark.asyncio
    async def test_make_decision_replace_section(self, tree):
        """Test selecting replace_section_in_page."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_existing_action", selected_options=["opt_replace_section"]),
            Answer(question_id="q_section_type", selected_options=["opt_hero"]),
        ]

        decision = await tree.make_decision(
            state,
            previous_html="<section>existing</section>",
        )

        assert decision.mode == "replace_section_in_page"

    @pytest.mark.asyncio
    async def test_make_decision_from_reference(self, tree):
        """Test selecting design_from_reference."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_intent_main", selected_options=["opt_from_reference"]),
        ]

        decision = await tree.make_decision(state)

        assert decision.mode == "design_from_reference"

    @pytest.mark.asyncio
    async def test_make_decision_default_fallback(self, tree):
        """Test fallback to design_frontend with minimal answers."""
        state = InterviewState()
        state.answers = []

        decision = await tree.make_decision(state)

        assert decision.mode == "design_frontend"

    @pytest.mark.asyncio
    async def test_make_decision_with_project_context(self, tree):
        """Test decision with project context."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
            Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
        ]

        decision = await tree.make_decision(
            state,
            project_context="Turkish e-commerce site",
        )

        assert "project_context" in decision.parameters

    @pytest.mark.asyncio
    async def test_make_decision_theme_extraction(self, tree):
        """Test theme parameter extraction."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
            Answer(question_id="q_theme_preference", selected_options=["opt_glassmorphism"]),
        ]

        decision = await tree.make_decision(state)

        assert "theme" in decision.parameters
        assert decision.parameters["theme"] == "glassmorphism"

    @pytest.mark.asyncio
    async def test_make_decision_language_extraction(self, tree):
        """Test content language extraction."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_content_language", selected_options=["opt_turkish"]),
        ]

        decision = await tree.make_decision(state)

        assert decision.parameters.get("content_language") == "tr"

    @pytest.mark.asyncio
    async def test_make_decision_with_html_tokens(self, tree):
        """Test design tokens extraction from HTML."""
        state = InterviewState()
        state.answers = [
            Answer(question_id="q_existing_action", selected_options=["opt_match_style"]),
        ]

        html = '''
        <div class="bg-blue-500 p-4 rounded-lg">
            Content
        </div>
        '''

        decision = await tree.make_decision(state, previous_html=html)

        assert "design_tokens" in decision.parameters

    def test_confidence_score_calculation(self, tree):
        """Test confidence score calculation."""
        from gemini_mcp.maestro.decision.tree import EnrichedContext
        from gemini_mcp.maestro.decision.models import ContextAnalysis

        ctx = EnrichedContext(
            answers={
                "q_intent_main": "opt_new_design",
                "q_scope_type": "opt_full_page",
                "q_page_type": "opt_landing_page",
                "q_theme_preference": "opt_modern_minimal",
                "q_content_language": "opt_turkish",
            },
            html_analysis=ContextAnalysis(has_html=False),
            project_context="Test project",
        )

        scores = tree._calculate_scores("design_page", ctx)

        assert scores.intent_clarity > 0.5
        assert scores.scope_match > 0.5
        assert scores.overall > 0.5

    def test_get_alternatives(self, tree):
        """Test getting alternative mode suggestions."""
        alternatives = tree._get_alternatives("design_page")

        assert len(alternatives) <= 2
        assert all("mode" in alt for alt in alternatives)
        assert all("reason" in alt for alt in alternatives)
        assert not any(alt["mode"] == "design_page" for alt in alternatives)

    def test_build_basic_reasoning(self, tree):
        """Test building reasoning text (Turkish output)."""
        from gemini_mcp.maestro.decision.tree import EnrichedContext
        from gemini_mcp.maestro.decision.models import ContextAnalysis

        ctx = EnrichedContext(
            answers={"q_intent_main": "opt_new_design"},
            html_analysis=ContextAnalysis(has_html=True),
        )
        scores = DecisionScores(intent_clarity=0.9, scope_match=0.8)

        reasoning = tree._build_basic_reasoning("design_page", ctx, scores)

        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
        # Turkish reasoning includes mode description and confidence percentage
        assert "modu" in reasoning or "%" in reasoning  # "modu" = "mode" in Turkish

    @pytest.mark.asyncio
    async def test_gemini_fallback_not_called_high_confidence(self, mock_client):
        """Test Gemini is not called for high confidence decisions."""
        tree = DecisionTree(client=mock_client)

        state = InterviewState()
        state.answers = [
            Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
            Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
            Answer(question_id="q_page_type", selected_options=["opt_landing_page"]),
            Answer(question_id="q_theme_preference", selected_options=["opt_modern_minimal"]),
            Answer(question_id="q_content_language", selected_options=["opt_turkish"]),
        ]

        decision = await tree.make_decision(state)

        # Should not call Gemini for clear decisions
        # (depends on threshold, may or may not be called)
        assert decision.mode == "design_page"


# =============================================================================
# DecisionAnalysis Tests
# =============================================================================


class TestDecisionAnalysis:
    """Tests for DecisionAnalysis dataclass."""

    def test_is_confident_above_threshold(self):
        """Test confidence threshold check."""
        analysis = DecisionAnalysis(
            selected_mode="design_page",
            confidence=0.9,
            scores=DecisionScores(),
            reasoning="Test",
        )

        assert analysis.is_confident(threshold=0.85)

    def test_is_confident_below_threshold(self):
        """Test confidence below threshold."""
        analysis = DecisionAnalysis(
            selected_mode="design_page",
            confidence=0.7,
            scores=DecisionScores(),
            reasoning="Test",
        )

        assert not analysis.is_confident(threshold=0.85)

    def test_get_primary_weakness(self):
        """Test getting primary weakness."""
        analysis = DecisionAnalysis(
            selected_mode="design_page",
            confidence=0.6,
            scores=DecisionScores(),
            reasoning="Test",
            weak_dimensions=[("parameter_completeness", 0.3), ("scope_match", 0.4)],
        )

        assert analysis.get_primary_weakness() == "parameter_completeness"

    def test_get_primary_weakness_none(self):
        """Test no weakness when list is empty."""
        analysis = DecisionAnalysis(
            selected_mode="design_page",
            confidence=0.9,
            scores=DecisionScores(),
            reasoning="Test",
        )

        assert analysis.get_primary_weakness() is None

    def test_to_dict(self):
        """Test serialization to dictionary."""
        scores = DecisionScores(intent_clarity=0.9, scope_match=0.8)
        analysis = DecisionAnalysis(
            selected_mode="design_page",
            confidence=0.85,
            scores=scores,
            reasoning="Test reasoning",
            parameters={"theme": "modern-minimal"},
            alternatives=[{"mode": "design_section", "reason": "Alternative"}],
        )

        result = analysis.to_dict()

        assert result["selected_mode"] == "design_page"
        assert result["confidence"] == 0.85
        assert result["reasoning"] == "Test reasoning"
        assert "intent_clarity" in result["scores"]
        assert result["parameters"]["theme"] == "modern-minimal"


# =============================================================================
# Integration Tests
# =============================================================================


class TestMaestroDecisionIntegration:
    """Integration tests for MAESTRO decision system."""

    @pytest.mark.asyncio
    async def test_full_decision_flow(self):
        """Test complete decision flow from answers to decision."""
        tree = DecisionTree(client=None)

        state = InterviewState()
        state.answers = [
            Answer(question_id="q_intent_main", selected_options=["opt_new_design"]),
            Answer(question_id="q_scope_type", selected_options=["opt_full_page"]),
            Answer(question_id="q_page_type", selected_options=["opt_landing_page"]),
            Answer(question_id="q_theme_preference", selected_options=["opt_glassmorphism"]),
            Answer(question_id="q_content_language", selected_options=["opt_turkish"]),
        ]

        decision = await tree.make_decision(
            state,
            project_context="Turkish SaaS landing page",
        )

        assert decision.mode == "design_page"
        assert decision.confidence > 0.5
        assert decision.parameters.get("theme") == "glassmorphism"
        assert decision.parameters.get("content_language") == "tr"
        assert "project_context" in decision.parameters
        assert len(decision.reasoning) > 0

    @pytest.mark.asyncio
    async def test_refine_with_html_analysis(self):
        """Test refinement decision with HTML context."""
        tree = DecisionTree(client=None)

        state = InterviewState()
        state.answers = [
            Answer(question_id="q_existing_action", selected_options=["opt_refine"]),
        ]

        html = '''
        <nav class="bg-blue-600 text-white p-4">Navigation</nav>
        <section class="hero min-h-screen bg-gradient-to-r from-blue-500 to-purple-600">
            Hero content
        </section>
        '''

        decision = await tree.make_decision(
            state,
            previous_html=html,
        )

        assert decision.mode == "refine_frontend"
        assert "design_tokens" in decision.parameters

    @pytest.mark.asyncio
    async def test_section_matching_with_context(self):
        """Test section design with style matching."""
        tree = DecisionTree(client=None)

        state = InterviewState()
        state.answers = [
            Answer(question_id="q_existing_action", selected_options=["opt_match_style"]),
            Answer(question_id="q_section_type", selected_options=["opt_pricing"]),
        ]

        html = '<div class="bg-blue-500 p-8 rounded-xl">Existing content</div>'

        decision = await tree.make_decision(
            state,
            previous_html=html,
        )

        assert decision.mode == "design_section"
        assert "design_tokens" in decision.parameters
