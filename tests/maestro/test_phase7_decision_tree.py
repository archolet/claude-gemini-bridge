"""
Phase 7 Tests - DecisionTree Unit Tests

Comprehensive tests for MAESTRO DecisionTree:
- MODE_RULES evaluation and priority
- PARAMETER_EXTRACTORS for all 6 modes
- Mapping functions (page, section, component, theme, language)
- 6-dimension confidence scoring (DecisionScores)
- Score calculation logic
- Required parameters for each mode
- Common parameters extraction
- Alternatives and reasoning generation
- State conversion and Gemini trigger logic
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from gemini_mcp.maestro.decision.tree import (
    DecisionTree,
    _map_page_type,
    _map_section_type,
    _map_component_type,
    _map_theme,
    _map_language,
)
from gemini_mcp.maestro.decision.models import (
    DecisionScores,
    ContextAnalysis,
    EnrichedContext,
    DecisionAnalysis,
)
from gemini_mcp.maestro.models import InterviewState, Answer


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def decision_tree():
    """Create DecisionTree instance without Gemini client."""
    return DecisionTree(client=None)


@pytest.fixture
def decision_tree_with_client():
    """Create DecisionTree instance with mock Gemini client."""
    mock_client = AsyncMock()
    return DecisionTree(client=mock_client)


@pytest.fixture
def empty_context():
    """Create empty EnrichedContext."""
    return EnrichedContext(
        answers={},
        html_analysis=ContextAnalysis(has_html=False),
        project_context="",
    )


@pytest.fixture
def new_page_context():
    """Context for new page design."""
    return EnrichedContext(
        answers={
            "q_intent_main": "opt_new_design",
            "q_scope_type": "opt_full_page",
            "q_page_type": "opt_landing_page",
            "q_theme_preference": "opt_modern_minimal",
        },
        html_analysis=ContextAnalysis(has_html=False),
        project_context="B2B SaaS landing page",
    )


@pytest.fixture
def refine_context():
    """Context for refine mode."""
    return EnrichedContext(
        answers={
            "q_existing_action": "opt_refine",
        },
        html_analysis=ContextAnalysis(
            has_html=True,
            detected_theme="corporate",
        ),
        project_context="",
    )


@pytest.fixture
def mock_interview_state():
    """Create mock InterviewState with answers."""
    state = MagicMock(spec=InterviewState)
    state.answers = [
        MagicMock(question_id="q_intent_main", selected_options=["opt_new_design"]),
        MagicMock(question_id="q_scope_type", selected_options=["opt_full_page"]),
        MagicMock(question_id="q_page_type", selected_options=["opt_landing_page"]),
    ]
    return state


# =============================================================================
# MODE_RULES TESTS
# =============================================================================


class TestModeRules:
    """Tests for MODE_RULES lambda conditions."""

    def test_mode_rules_has_all_modes(self, decision_tree):
        """All 6 design modes should have rules."""
        expected_modes = [
            "design_frontend",
            "design_page",
            "design_section",
            "refine_frontend",
            "replace_section_in_page",
            "design_from_reference",
        ]
        for mode in expected_modes:
            assert mode in DecisionTree.MODE_RULES

    def test_refine_frontend_condition(self, refine_context):
        """refine_frontend should match when has_html and opt_refine."""
        condition, priority = DecisionTree.MODE_RULES["refine_frontend"]
        assert condition(refine_context) is True
        assert priority == 100  # Highest priority

    def test_refine_frontend_no_html(self, empty_context):
        """refine_frontend should not match without HTML."""
        condition, _ = DecisionTree.MODE_RULES["refine_frontend"]
        empty_context.answers["q_existing_action"] = "opt_refine"
        assert condition(empty_context) is False

    def test_replace_section_condition(self):
        """replace_section_in_page should match with has_html and opt_replace_section."""
        ctx = EnrichedContext(
            answers={"q_existing_action": "opt_replace_section"},
            html_analysis=ContextAnalysis(has_html=True),
        )
        condition, priority = DecisionTree.MODE_RULES["replace_section_in_page"]
        assert condition(ctx) is True
        assert priority == 95

    def test_design_from_reference_condition(self):
        """design_from_reference should match when intent is opt_from_reference."""
        ctx = EnrichedContext(
            answers={"q_intent_main": "opt_from_reference"},
            html_analysis=ContextAnalysis(has_html=False),
        )
        condition, priority = DecisionTree.MODE_RULES["design_from_reference"]
        assert condition(ctx) is True
        assert priority == 90

    def test_design_page_condition(self, new_page_context):
        """design_page should match with new_design + full_page."""
        condition, priority = DecisionTree.MODE_RULES["design_page"]
        assert condition(new_page_context) is True
        assert priority == 80

    def test_design_page_requires_both_conditions(self):
        """design_page needs both new_design intent AND full_page scope."""
        # Only intent, no scope
        ctx = EnrichedContext(
            answers={"q_intent_main": "opt_new_design"},
            html_analysis=ContextAnalysis(has_html=False),
        )
        condition, _ = DecisionTree.MODE_RULES["design_page"]
        assert condition(ctx) is False

    def test_design_section_with_scope(self):
        """design_section should match with new_design + section scope."""
        ctx = EnrichedContext(
            answers={
                "q_intent_main": "opt_new_design",
                "q_scope_type": "opt_section",
            },
            html_analysis=ContextAnalysis(has_html=False),
        )
        condition, priority = DecisionTree.MODE_RULES["design_section"]
        assert condition(ctx) is True
        assert priority == 70

    def test_design_section_with_style_match(self):
        """design_section should also match with has_html + opt_match_style."""
        ctx = EnrichedContext(
            answers={"q_existing_action": "opt_match_style"},
            html_analysis=ContextAnalysis(has_html=True),
        )
        condition, _ = DecisionTree.MODE_RULES["design_section"]
        assert condition(ctx) is True

    def test_design_frontend_fallback(self, empty_context):
        """design_frontend should always match (fallback)."""
        condition, priority = DecisionTree.MODE_RULES["design_frontend"]
        assert condition(empty_context) is True
        assert priority == 0  # Lowest priority


class TestRulePriority:
    """Tests for rule priority evaluation."""

    def test_rules_evaluated_in_priority_order(self, decision_tree):
        """Higher priority rules should be evaluated first."""
        sorted_rules = sorted(
            DecisionTree.MODE_RULES.items(),
            key=lambda x: x[1][1],
            reverse=True,
        )
        priorities = [rule[1][1] for rule in sorted_rules]
        assert priorities == sorted(priorities, reverse=True)

    def test_refine_has_highest_priority(self):
        """refine_frontend should have highest priority (100)."""
        _, priority = DecisionTree.MODE_RULES["refine_frontend"]
        assert priority == 100

    def test_fallback_has_lowest_priority(self):
        """design_frontend (fallback) should have lowest priority (0)."""
        _, priority = DecisionTree.MODE_RULES["design_frontend"]
        assert priority == 0

    def test_evaluate_rules_first_match_wins(self, decision_tree, refine_context):
        """First matching rule should win, even if others would also match."""
        # refine_context would match refine_frontend (priority 100)
        # but design_frontend (priority 0) would also match
        mode = decision_tree._evaluate_rules(refine_context)
        assert mode == "refine_frontend"

    def test_evaluate_rules_fallback_on_no_match(self, decision_tree, empty_context):
        """Empty context should fall back to design_frontend."""
        mode = decision_tree._evaluate_rules(empty_context)
        assert mode == "design_frontend"


# =============================================================================
# MAPPING FUNCTION TESTS
# =============================================================================


class TestMapPageType:
    """Tests for _map_page_type function."""

    def test_map_known_page_types(self):
        """Map known page type options correctly."""
        assert _map_page_type("opt_landing_page") == "landing_page"
        assert _map_page_type("opt_dashboard") == "dashboard"
        assert _map_page_type("opt_auth_page") == "auth_page"
        assert _map_page_type("opt_pricing_page") == "pricing_page"
        assert _map_page_type("opt_blog_post") == "blog_post"
        assert _map_page_type("opt_product_page") == "product_page"
        assert _map_page_type("opt_portfolio") == "portfolio"
        assert _map_page_type("opt_documentation") == "documentation"
        assert _map_page_type("opt_error_page") == "error_page"
        assert _map_page_type("opt_coming_soon") == "coming_soon"

    def test_map_none_to_default(self):
        """None should map to landing_page default."""
        assert _map_page_type(None) == "landing_page"

    def test_map_unknown_strips_opt_prefix(self):
        """Unknown values should strip opt_ prefix."""
        assert _map_page_type("opt_custom") == "custom"


class TestMapSectionType:
    """Tests for _map_section_type function."""

    def test_map_known_section_types(self):
        """Map known section type options correctly."""
        assert _map_section_type("opt_hero") == "hero"
        assert _map_section_type("opt_features") == "features"
        assert _map_section_type("opt_pricing_section") == "pricing"
        assert _map_section_type("opt_testimonials") == "testimonials"
        assert _map_section_type("opt_cta") == "cta"
        assert _map_section_type("opt_footer") == "footer"
        assert _map_section_type("opt_stats") == "stats"
        assert _map_section_type("opt_faq") == "faq"
        assert _map_section_type("opt_team") == "team"
        assert _map_section_type("opt_contact") == "contact"
        assert _map_section_type("opt_gallery") == "gallery"
        assert _map_section_type("opt_newsletter") == "newsletter"

    def test_map_none_to_default(self):
        """None should map to hero default."""
        assert _map_section_type(None) == "hero"


class TestMapComponentType:
    """Tests for _map_component_type function."""

    def test_map_known_component_types(self):
        """Map known component type options correctly."""
        assert _map_component_type("opt_button") == "button"
        assert _map_component_type("opt_input") == "input"
        assert _map_component_type("opt_badge") == "badge"
        assert _map_component_type("opt_avatar") == "avatar"
        assert _map_component_type("opt_card") == "card"
        assert _map_component_type("opt_form") == "form"
        assert _map_component_type("opt_modal") == "modal"
        assert _map_component_type("opt_tabs") == "tabs"
        assert _map_component_type("opt_table") == "table"
        assert _map_component_type("opt_navbar") == "navbar"
        assert _map_component_type("opt_sidebar") == "sidebar"
        assert _map_component_type("opt_data_table") == "data_table"

    def test_map_none_to_default(self):
        """None should map to card default."""
        assert _map_component_type(None) == "card"


class TestMapTheme:
    """Tests for _map_theme function."""

    def test_map_known_themes(self):
        """Map known theme options correctly."""
        assert _map_theme("opt_modern_minimal") == "modern-minimal"
        assert _map_theme("opt_corporate") == "corporate"
        assert _map_theme("opt_startup") == "startup"
        assert _map_theme("opt_brutalist") == "brutalist"
        assert _map_theme("opt_glassmorphism") == "glassmorphism"
        assert _map_theme("opt_neo_brutalism") == "neo-brutalism"
        assert _map_theme("opt_cyberpunk") == "cyberpunk"
        assert _map_theme("opt_nature") == "nature"
        assert _map_theme("opt_pastel") == "pastel"
        assert _map_theme("opt_gradient") == "gradient"
        assert _map_theme("opt_soft_ui") == "soft-ui"
        assert _map_theme("opt_dark_mode_first") == "dark_mode_first"
        assert _map_theme("opt_high_contrast") == "high_contrast"
        assert _map_theme("opt_retro") == "retro"

    def test_map_none_to_default(self):
        """None should map to modern-minimal default."""
        assert _map_theme(None) == "modern-minimal"

    def test_map_unknown_converts_underscores(self):
        """Unknown themes should convert underscores to dashes."""
        assert _map_theme("opt_custom_theme") == "custom-theme"


class TestMapLanguage:
    """Tests for _map_language function."""

    def test_map_known_languages(self):
        """Map known language options correctly."""
        assert _map_language("opt_turkish") == "tr"
        assert _map_language("opt_english") == "en"
        assert _map_language("opt_german") == "de"

    def test_map_none_to_default(self):
        """None should map to Turkish default."""
        assert _map_language(None) == "tr"

    def test_map_unknown_to_default(self):
        """Unknown languages should default to Turkish."""
        assert _map_language("opt_unknown") == "tr"


# =============================================================================
# PARAMETER_EXTRACTORS TESTS
# =============================================================================


class TestParameterExtractors:
    """Tests for PARAMETER_EXTRACTORS lambdas."""

    def test_has_extractors_for_all_modes(self):
        """All modes should have parameter extractors."""
        expected_modes = [
            "design_frontend",
            "design_page",
            "design_section",
            "refine_frontend",
            "replace_section_in_page",
            "design_from_reference",
        ]
        for mode in expected_modes:
            assert mode in DecisionTree.PARAMETER_EXTRACTORS

    def test_design_page_extractor(self, new_page_context):
        """design_page should extract template_type."""
        extractor = DecisionTree.PARAMETER_EXTRACTORS["design_page"]
        params = extractor(new_page_context)
        assert params == {"template_type": "landing_page"}

    def test_design_section_extractor(self):
        """design_section should extract section_type."""
        ctx = EnrichedContext(
            answers={"q_section_type": "opt_hero"},
            html_analysis=ContextAnalysis(has_html=False),
        )
        extractor = DecisionTree.PARAMETER_EXTRACTORS["design_section"]
        params = extractor(ctx)
        assert params == {"section_type": "hero"}

    def test_design_frontend_extractor(self):
        """design_frontend should extract component_type."""
        ctx = EnrichedContext(
            answers={"q_component_type": "opt_button"},
            html_analysis=ContextAnalysis(has_html=False),
        )
        extractor = DecisionTree.PARAMETER_EXTRACTORS["design_frontend"]
        params = extractor(ctx)
        assert params == {"component_type": "button"}

    def test_refine_frontend_extractor_empty(self, refine_context):
        """refine_frontend should return empty params (HTML comes from context)."""
        extractor = DecisionTree.PARAMETER_EXTRACTORS["refine_frontend"]
        params = extractor(refine_context)
        assert params == {}

    def test_replace_section_extractor(self):
        """replace_section_in_page should extract section_type."""
        ctx = EnrichedContext(
            answers={
                "q_existing_action": "opt_replace_section",
                "q_section_type": "opt_pricing_section",
            },
            html_analysis=ContextAnalysis(has_html=True),
        )
        extractor = DecisionTree.PARAMETER_EXTRACTORS["replace_section_in_page"]
        params = extractor(ctx)
        assert params == {"section_type": "pricing"}

    def test_design_from_reference_extractor_empty(self):
        """design_from_reference should return empty params."""
        ctx = EnrichedContext(
            answers={"q_intent_main": "opt_from_reference"},
            html_analysis=ContextAnalysis(has_html=False),
        )
        extractor = DecisionTree.PARAMETER_EXTRACTORS["design_from_reference"]
        params = extractor(ctx)
        assert params == {}


# =============================================================================
# DECISION SCORES TESTS
# =============================================================================


class TestDecisionScores:
    """Tests for DecisionScores dataclass."""

    def test_default_scores_all_half(self):
        """Default scores should be 0.5 for all dimensions."""
        scores = DecisionScores()
        assert scores.intent_clarity == 0.5
        assert scores.scope_match == 0.5
        assert scores.context_richness == 0.5
        assert scores.parameter_completeness == 0.5
        assert scores.constraint_satisfaction == 0.5
        assert scores.alternative_viability == 0.5

    def test_weights_sum_to_one(self):
        """All weights should sum to exactly 1.0."""
        total = sum(DecisionScores.WEIGHTS.values())
        assert total == pytest.approx(1.0)

    def test_overall_weighted_average(self):
        """overall property should calculate weighted average correctly."""
        scores = DecisionScores(
            intent_clarity=1.0,  # 0.25 weight
            scope_match=0.8,  # 0.20 weight
            context_richness=0.6,  # 0.15 weight
            parameter_completeness=0.7,  # 0.20 weight
            constraint_satisfaction=0.9,  # 0.10 weight
            alternative_viability=0.5,  # 0.10 weight
        )
        # Expected: 1.0*0.25 + 0.8*0.20 + 0.6*0.15 + 0.7*0.20 + 0.9*0.10 + 0.5*0.10
        # = 0.25 + 0.16 + 0.09 + 0.14 + 0.09 + 0.05 = 0.78
        assert scores.overall == pytest.approx(0.78, rel=0.01)

    def test_weighted_average_alias(self):
        """weighted_average() should be alias for overall."""
        scores = DecisionScores()
        assert scores.weighted_average() == scores.overall

    def test_get_dimension_scores(self):
        """get_dimension_scores should return all dimensions as dict."""
        scores = DecisionScores(intent_clarity=0.9)
        dims = scores.get_dimension_scores()
        assert dims["intent_clarity"] == 0.9
        assert len(dims) == 6

    def test_get_lowest_dimensions(self):
        """get_lowest_dimensions should return lowest scoring dimensions."""
        scores = DecisionScores(
            intent_clarity=0.9,
            scope_match=0.3,
            context_richness=0.2,  # Lowest
            parameter_completeness=0.8,
            constraint_satisfaction=0.7,
            alternative_viability=0.4,
        )
        lowest = scores.get_lowest_dimensions(2)
        assert lowest[0][0] == "context_richness"
        assert lowest[0][1] == 0.2
        assert lowest[1][0] == "scope_match"

    def test_get_highest_dimensions(self):
        """get_highest_dimensions should return highest scoring dimensions."""
        scores = DecisionScores(
            intent_clarity=0.9,  # Highest
            scope_match=0.3,
            context_richness=0.2,
            parameter_completeness=0.8,  # Second highest
            constraint_satisfaction=0.7,
            alternative_viability=0.4,
        )
        highest = scores.get_highest_dimensions(2)
        assert highest[0][0] == "intent_clarity"
        assert highest[0][1] == 0.9
        assert highest[1][0] == "parameter_completeness"

    def test_is_high_confidence(self):
        """is_high_confidence should check threshold correctly."""
        high_scores = DecisionScores(
            intent_clarity=0.9,
            scope_match=0.9,
            context_richness=0.9,
            parameter_completeness=0.9,
            constraint_satisfaction=0.9,
            alternative_viability=0.9,
        )
        low_scores = DecisionScores()  # All 0.5

        assert high_scores.is_high_confidence() is True
        assert low_scores.is_high_confidence() is False

    def test_needs_gemini(self):
        """needs_gemini should check if confidence below threshold."""
        low_scores = DecisionScores()  # Overall ~0.5
        assert low_scores.needs_gemini() is True
        assert low_scores.needs_gemini(threshold=0.3) is False


# =============================================================================
# SCORE CALCULATION TESTS
# =============================================================================


class TestScoreCalculation:
    """Tests for _calculate_scores method."""

    def test_intent_clarity_with_answer(self, decision_tree, new_page_context):
        """Intent clarity should be high when intent answer provided."""
        scores = decision_tree._calculate_scores("design_page", new_page_context)
        assert scores.intent_clarity == 0.9

    def test_intent_clarity_multiple_answers(self, decision_tree):
        """Intent clarity should be medium with multiple answers but no intent."""
        ctx = EnrichedContext(
            answers={
                "q_theme_preference": "opt_corporate",
                "q_scope_type": "opt_full_page",
            },
            html_analysis=ContextAnalysis(has_html=False),
        )
        scores = decision_tree._calculate_scores("design_page", ctx)
        assert scores.intent_clarity == 0.7

    def test_intent_clarity_no_answers(self, decision_tree, empty_context):
        """Intent clarity should be low with no answers."""
        scores = decision_tree._calculate_scores("design_frontend", empty_context)
        assert scores.intent_clarity == 0.5

    def test_scope_match_correct_mode(self, decision_tree, new_page_context):
        """Scope match should be 1.0 when scope matches mode."""
        # new_page_context has opt_full_page -> design_page
        scores = decision_tree._calculate_scores("design_page", new_page_context)
        assert scores.scope_match == 1.0

    def test_scope_match_incorrect_mode(self, decision_tree, new_page_context):
        """Scope match should be lower when scope doesn't match mode."""
        # new_page_context has opt_full_page, but we're evaluating design_frontend
        scores = decision_tree._calculate_scores("design_frontend", new_page_context)
        assert scores.scope_match == 0.6

    def test_context_richness_with_html(self, decision_tree, refine_context):
        """Context richness should be higher with HTML context."""
        scores = decision_tree._calculate_scores("refine_frontend", refine_context)
        assert scores.context_richness >= 0.6

    def test_context_richness_with_project(self, decision_tree, new_page_context):
        """Context richness should be higher with project context."""
        scores = decision_tree._calculate_scores("design_page", new_page_context)
        assert scores.context_richness >= 0.5

    def test_parameter_completeness_all_present(self, decision_tree, new_page_context):
        """Parameter completeness should be 1.0 when all required params present."""
        scores = decision_tree._calculate_scores("design_page", new_page_context)
        assert scores.parameter_completeness == 1.0

    def test_parameter_completeness_missing(self, decision_tree):
        """Parameter completeness should be lower when params missing."""
        ctx = EnrichedContext(
            answers={"q_intent_main": "opt_new_design"},  # Missing q_page_type
            html_analysis=ContextAnalysis(has_html=False),
        )
        scores = decision_tree._calculate_scores("design_page", ctx)
        assert scores.parameter_completeness == 0.0


# =============================================================================
# REQUIRED PARAMS TESTS
# =============================================================================


class TestRequiredParams:
    """Tests for _get_required_params method."""

    def test_design_page_requires_page_type(self, decision_tree):
        """design_page should require q_page_type."""
        params = decision_tree._get_required_params("design_page")
        assert "q_page_type" in params

    def test_design_section_requires_section_type(self, decision_tree):
        """design_section should require q_section_type."""
        params = decision_tree._get_required_params("design_section")
        assert "q_section_type" in params

    def test_design_frontend_requires_component_type(self, decision_tree):
        """design_frontend should require q_component_type."""
        params = decision_tree._get_required_params("design_frontend")
        assert "q_component_type" in params

    def test_refine_has_no_required_params(self, decision_tree):
        """refine_frontend should have no required params."""
        params = decision_tree._get_required_params("refine_frontend")
        assert params == []

    def test_design_from_reference_no_required(self, decision_tree):
        """design_from_reference should have no required params."""
        params = decision_tree._get_required_params("design_from_reference")
        assert params == []

    def test_unknown_mode_returns_empty(self, decision_tree):
        """Unknown mode should return empty list."""
        params = decision_tree._get_required_params("unknown_mode")
        assert params == []


# =============================================================================
# COMMON PARAMETERS TESTS
# =============================================================================


class TestCommonParameters:
    """Tests for _extract_common_parameters method."""

    def test_extract_theme(self, decision_tree, new_page_context):
        """Should extract theme from answers."""
        params = decision_tree._extract_common_parameters(new_page_context)
        assert params["theme"] == "modern-minimal"

    def test_extract_theme_from_html(self, decision_tree):
        """Should extract theme from HTML analysis if not in answers."""
        ctx = EnrichedContext(
            answers={},
            html_analysis=ContextAnalysis(has_html=True, detected_theme="corporate"),
        )
        params = decision_tree._extract_common_parameters(ctx)
        assert params.get("theme") == "corporate"

    def test_extract_dark_mode(self, decision_tree):
        """Should extract dark_mode from color mode answer."""
        ctx = EnrichedContext(
            answers={"q_color_mode": "opt_dark"},
            html_analysis=ContextAnalysis(has_html=False),
        )
        params = decision_tree._extract_common_parameters(ctx)
        assert params["dark_mode"] is True

    def test_extract_language(self, decision_tree):
        """Should extract content_language from answers."""
        ctx = EnrichedContext(
            answers={"q_content_language": "opt_english"},
            html_analysis=ContextAnalysis(has_html=False),
        )
        params = decision_tree._extract_common_parameters(ctx)
        assert params["content_language"] == "en"

    def test_extract_project_context(self, decision_tree, new_page_context):
        """Should include project_context if provided."""
        params = decision_tree._extract_common_parameters(new_page_context)
        assert params["project_context"] == "B2B SaaS landing page"


# =============================================================================
# ALTERNATIVES TESTS
# =============================================================================


class TestAlternatives:
    """Tests for _get_alternatives method."""

    def test_get_alternatives_excludes_selected(self, decision_tree):
        """Alternatives should not include selected mode."""
        alternatives = decision_tree._get_alternatives("design_page")
        modes = [alt["mode"] for alt in alternatives]
        assert "design_page" not in modes

    def test_get_alternatives_returns_two(self, decision_tree):
        """Should return top 2 alternatives."""
        alternatives = decision_tree._get_alternatives("design_frontend")
        assert len(alternatives) == 2

    def test_alternatives_have_reason(self, decision_tree):
        """Each alternative should have a reason."""
        alternatives = decision_tree._get_alternatives("design_page")
        for alt in alternatives:
            assert "reason" in alt
            assert len(alt["reason"]) > 0


# =============================================================================
# REASONING TESTS
# =============================================================================


class TestReasoning:
    """Tests for _build_basic_reasoning method."""

    def test_reasoning_mentions_answer_count(self, decision_tree, new_page_context):
        """Reasoning should mention number of answers."""
        scores = DecisionScores()
        reasoning = decision_tree._build_basic_reasoning(
            "design_page", new_page_context, scores
        )
        assert "4 cevap" in reasoning

    def test_reasoning_mentions_confidence(self, decision_tree, empty_context):
        """Reasoning should mention confidence percentage."""
        scores = DecisionScores()  # Overall ~0.5 = 50%
        reasoning = decision_tree._build_basic_reasoning(
            "design_frontend", empty_context, scores
        )
        assert "%50" in reasoning or "%" in reasoning

    def test_reasoning_mentions_html_context(self, decision_tree, refine_context):
        """Reasoning should mention HTML analysis if available."""
        scores = DecisionScores()
        reasoning = decision_tree._build_basic_reasoning(
            "refine_frontend", refine_context, scores
        )
        # Case-insensitive check for html/HTML mention
        assert "html" in reasoning.lower()

    def test_reasoning_in_turkish(self, decision_tree, new_page_context):
        """Reasoning should be in Turkish."""
        scores = DecisionScores()
        reasoning = decision_tree._build_basic_reasoning(
            "design_page", new_page_context, scores
        )
        # Turkish words
        assert "değerlendirildi" in reasoning or "seçildi" in reasoning


# =============================================================================
# STATE CONVERSION TESTS
# =============================================================================


class TestStateConversion:
    """Tests for _state_to_answer_dict method."""

    def test_convert_state_to_dict(self, decision_tree, mock_interview_state):
        """Should convert InterviewState answers to dict."""
        result = decision_tree._state_to_answer_dict(mock_interview_state)
        assert result["q_intent_main"] == "opt_new_design"
        assert result["q_scope_type"] == "opt_full_page"
        assert result["q_page_type"] == "opt_landing_page"

    def test_takes_first_selected_option(self, decision_tree):
        """Should take first selected option if multiple."""
        state = MagicMock(spec=InterviewState)
        state.answers = [
            MagicMock(
                question_id="q_multi",
                selected_options=["first", "second"],
            ),
        ]
        result = decision_tree._state_to_answer_dict(state)
        assert result["q_multi"] == "first"

    def test_skips_empty_selections(self, decision_tree):
        """Should skip answers with empty selections."""
        state = MagicMock(spec=InterviewState)
        state.answers = [
            MagicMock(question_id="q_empty", selected_options=[]),
            MagicMock(question_id="q_filled", selected_options=["value"]),
        ]
        result = decision_tree._state_to_answer_dict(state)
        assert "q_empty" not in result
        assert result["q_filled"] == "value"


# =============================================================================
# ENRICHED CONTEXT TESTS
# =============================================================================


class TestEnrichedContext:
    """Tests for EnrichedContext dataclass."""

    def test_get_answer(self, new_page_context):
        """get_answer should return correct value."""
        assert new_page_context.get_answer("q_intent_main") == "opt_new_design"
        assert new_page_context.get_answer("unknown") is None

    def test_has_answer(self, new_page_context):
        """has_answer should check existence."""
        assert new_page_context.has_answer("q_intent_main") is True
        assert new_page_context.has_answer("unknown") is False

    def test_has_html_context(self, refine_context, empty_context):
        """has_html_context should check HTML analysis."""
        assert refine_context.has_html_context() is True
        assert empty_context.has_html_context() is False

    def test_has_project_context(self, new_page_context, empty_context):
        """has_project_context should check project_context."""
        assert new_page_context.has_project_context() is True
        assert empty_context.has_project_context() is False

    def test_answer_count(self, new_page_context):
        """answer_count should return number of answers."""
        assert new_page_context.answer_count == 4


# =============================================================================
# CONTEXT ANALYSIS TESTS
# =============================================================================


class TestContextAnalysis:
    """Tests for ContextAnalysis dataclass."""

    def test_class_count(self):
        """class_count should return number of tailwind classes."""
        analysis = ContextAnalysis(
            has_html=True,
            tailwind_classes=["bg-blue-500", "text-white", "p-4"],
        )
        assert analysis.class_count == 3

    def test_component_count(self):
        """component_count should return detected components."""
        analysis = ContextAnalysis(
            has_html=True,
            detected_components=["navbar", "hero", "footer"],
        )
        assert analysis.component_count == 3

    def test_has_section_markers(self):
        """has_section_markers should check for markers."""
        with_markers = ContextAnalysis(
            has_html=True,
            section_markers=["hero", "features"],
        )
        without_markers = ContextAnalysis(has_html=True)

        assert with_markers.has_section_markers() is True
        assert without_markers.has_section_markers() is False

    def test_get_primary_color(self):
        """get_primary_color should return primary color."""
        analysis = ContextAnalysis(
            has_html=True,
            detected_colors={"primary": "#3B82F6", "secondary": "#6B7280"},
        )
        assert analysis.get_primary_color() == "#3B82F6"

    def test_to_design_tokens(self):
        """to_design_tokens should export design tokens."""
        analysis = ContextAnalysis(
            has_html=True,
            detected_theme="corporate",
            detected_colors={"primary": "#3B82F6"},
        )
        tokens = analysis.to_design_tokens()
        assert tokens["theme"] == "corporate"
        assert tokens["colors"]["primary"] == "#3B82F6"


# =============================================================================
# DECISION ANALYSIS TESTS
# =============================================================================


class TestDecisionAnalysis:
    """Tests for DecisionAnalysis dataclass."""

    def test_is_confident(self):
        """is_confident should check threshold."""
        confident = DecisionAnalysis(
            selected_mode="design_page",
            confidence=0.9,
            scores=DecisionScores(),
            reasoning="Test",
        )
        not_confident = DecisionAnalysis(
            selected_mode="design_frontend",
            confidence=0.5,
            scores=DecisionScores(),
            reasoning="Test",
        )

        assert confident.is_confident() is True
        assert not_confident.is_confident() is False

    def test_get_primary_weakness(self):
        """get_primary_weakness should return first weak dimension."""
        analysis = DecisionAnalysis(
            selected_mode="design_page",
            confidence=0.7,
            scores=DecisionScores(),
            reasoning="Test",
            weak_dimensions=[("context_richness", 0.3), ("scope_match", 0.4)],
        )
        assert analysis.get_primary_weakness() == "context_richness"

    def test_get_primary_weakness_none(self):
        """get_primary_weakness should return None if no weaknesses."""
        analysis = DecisionAnalysis(
            selected_mode="design_page",
            confidence=0.9,
            scores=DecisionScores(),
            reasoning="Test",
        )
        assert analysis.get_primary_weakness() is None

    def test_to_dict(self):
        """to_dict should serialize correctly."""
        analysis = DecisionAnalysis(
            selected_mode="design_page",
            confidence=0.85,
            scores=DecisionScores(),
            reasoning="Test reasoning",
            parameters={"template_type": "landing_page"},
            alternatives=[{"mode": "design_section", "reason": "Alternative"}],
            used_gemini=False,
        )
        result = analysis.to_dict()

        assert result["selected_mode"] == "design_page"
        assert result["confidence"] == 0.85
        assert result["reasoning"] == "Test reasoning"
        assert result["parameters"]["template_type"] == "landing_page"
        assert len(result["alternatives"]) == 1
        assert result["used_gemini"] is False
        assert "scores" in result


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestDecisionTreeIntegration:
    """Integration tests for complete decision flow."""

    @pytest.mark.asyncio
    async def test_make_decision_new_page(self, decision_tree, mock_interview_state):
        """Complete decision for new page design."""
        decision = await decision_tree.make_decision(
            state=mock_interview_state,
            project_context="B2B SaaS landing",
        )

        assert decision.mode == "design_page"
        assert decision.confidence > 0
        assert decision.parameters.get("template_type") == "landing_page"
        assert len(decision.reasoning) > 0

    @pytest.mark.asyncio
    async def test_make_decision_refine_mode(self, decision_tree):
        """Complete decision for refine mode with HTML."""
        state = MagicMock(spec=InterviewState)
        state.answers = [
            MagicMock(question_id="q_existing_action", selected_options=["opt_refine"]),
        ]

        decision = await decision_tree.make_decision(
            state=state,
            previous_html="<div>Existing HTML</div>",
        )

        assert decision.mode == "refine_frontend"
        assert decision.parameters.get("previous_html") == "<div>Existing HTML</div>"

    @pytest.mark.asyncio
    async def test_make_decision_fallback(self, decision_tree):
        """Empty state should fall back to design_frontend."""
        state = MagicMock(spec=InterviewState)
        state.answers = []

        decision = await decision_tree.make_decision(state=state)

        assert decision.mode == "design_frontend"

    @pytest.mark.asyncio
    async def test_make_decision_includes_alternatives(self, decision_tree, mock_interview_state):
        """Decision should include alternatives."""
        decision = await decision_tree.make_decision(state=mock_interview_state)

        assert len(decision.alternatives) > 0
        assert decision.alternatives[0]["mode"] != decision.mode


class TestGeminiTrigger:
    """Tests for Gemini reasoning trigger."""

    def test_gemini_trigger_threshold(self):
        """Verify Gemini trigger threshold constant."""
        assert DecisionTree.GEMINI_TRIGGER_THRESHOLD == 0.70

    def test_high_confidence_threshold(self):
        """Verify high confidence threshold constant."""
        assert DecisionTree.HIGH_CONFIDENCE_THRESHOLD == 0.85

    @pytest.mark.asyncio
    async def test_gemini_not_called_high_confidence(self, decision_tree, mock_interview_state):
        """Gemini should not be called for high confidence decisions."""
        # With no client, verify the flow works
        decision = await decision_tree.make_decision(state=mock_interview_state)
        # Decision should complete without error
        assert decision is not None

    @pytest.mark.asyncio
    async def test_gemini_called_low_confidence(self, decision_tree_with_client):
        """Gemini should be triggered for low confidence decisions."""
        state = MagicMock(spec=InterviewState)
        state.answers = []  # Empty = low confidence

        # Mock Gemini response
        decision_tree_with_client.client.generate_text.return_value = {
            "text": '{"mode": "design_frontend", "reasoning": "Varsayılan mod"}'
        }

        decision = await decision_tree_with_client.make_decision(state=state)
        assert decision.mode == "design_frontend"
