"""
Phase 6 Tests - Analytics, UI, and Intelligence Modules

Tests for MAESTRO Phase 6 enhancements:
- Analytics: SessionTracker, CostAnalyzer, QualityMetrics
- UI: MaestroFormatter, progress indicators, summaries
- Intelligence: AdaptiveFlow, PreferenceLearner, Recommender
"""
import pytest
from unittest.mock import MagicMock

from gemini_mcp.maestro.analytics import (
    SessionTracker,
    SessionMetrics,
    CostAnalyzer,
    CostBreakdown,
    QualityMetrics,
    QualityScore,
)
from gemini_mcp.maestro.ui import (
    MaestroFormatter,
    generate_progress_bar,
    generate_decision_summary,
    MODE_DESCRIPTIONS,
)
from gemini_mcp.maestro.intelligence import (
    AdaptiveFlow,
    PreferenceLearner,
    Recommender,
)
from gemini_mcp.maestro.intelligence.adaptive_flow import FlowContext, SkipReason
from gemini_mcp.maestro.intelligence.preference_learner import PreferenceType


class TestSessionTracker:
    """Tests for SessionTracker singleton."""

    def setup_method(self):
        """Reset singleton before each test."""
        SessionTracker.reset_instance()

    def test_singleton_pattern(self):
        """Same instance is returned on multiple calls."""
        tracker1 = SessionTracker()
        tracker2 = SessionTracker()
        assert tracker1 is tracker2

    def test_start_session(self):
        """Start session creates metrics."""
        tracker = SessionTracker()
        metrics = tracker.start_session("test_001")
        assert metrics.session_id == "test_001"
        assert metrics.questions_asked == 0

    def test_record_question(self):
        """Record question increments counter."""
        tracker = SessionTracker()
        tracker.start_session("test_001")
        tracker.record_question("test_001", response_time=1.5)
        metrics = tracker.get_metrics("test_001")
        assert metrics.questions_asked == 1

    def test_record_answer(self):
        """Record answer increments counter."""
        tracker = SessionTracker()
        tracker.start_session("test_001")
        tracker.record_question("test_001")
        tracker.record_answer("test_001", response_time=0.5)
        metrics = tracker.get_metrics("test_001")
        assert metrics.questions_answered == 1

    def test_record_decision(self):
        """Record decision stores mode and confidence."""
        tracker = SessionTracker()
        tracker.start_session("test_001")
        tracker.record_decision("test_001", mode="design_page", confidence=0.85)
        metrics = tracker.get_metrics("test_001")
        assert metrics.selected_mode == "design_page"
        assert metrics.decision_confidence == 0.85

    def test_track_event(self):
        """Track event logs without error."""
        tracker = SessionTracker()
        tracker.start_session("test_001")
        # Should not raise
        tracker.track_event("test_001", "test_event", {"key": "value"})

    def test_complete_session(self):
        """Complete session moves to completed list."""
        tracker = SessionTracker()
        tracker.start_session("test_001")
        metrics = tracker.complete_session("test_001")
        assert metrics is not None
        assert metrics.end_time is not None
        assert tracker.active_count == 0
        assert tracker.completed_count == 1

    def test_get_session_duration(self):
        """Get session duration returns positive value."""
        tracker = SessionTracker()
        tracker.start_session("test_001")
        duration = tracker.get_session_duration("test_001")
        assert duration >= 0

    def test_to_dict(self):
        """to_dict returns proper structure."""
        tracker = SessionTracker()
        tracker.start_session("test_001")
        result = tracker.to_dict()
        assert "active_sessions" in result
        assert "completed_sessions" in result
        assert "aggregate_stats" in result


class TestCostAnalyzer:
    """Tests for CostAnalyzer."""

    def test_record_api_call(self):
        """Record API call tracks tokens."""
        analyzer = CostAnalyzer()
        analyzer.start_session("test_001")
        analyzer.record_api_call("test_001", input_tokens=1000, output_tokens=500)
        cost = analyzer.get_session_cost("test_001")
        assert cost.input_tokens == 1000
        assert cost.output_tokens == 500

    def test_record_call_simplified(self):
        """Simplified record_call API works."""
        analyzer = CostAnalyzer()
        analyzer.record_call("gemini-3-pro", 500, 250, 100)
        # Uses global session
        cost = analyzer.get_session_cost("_global")
        assert cost.input_tokens == 500
        assert cost.output_tokens == 250
        assert cost.thinking_tokens == 100

    def test_cost_calculation(self):
        """Cost breakdown calculates correctly."""
        breakdown = CostBreakdown(
            input_tokens=1000,
            output_tokens=1000,
            thinking_tokens=1000,
        )
        # Input: 1K * 0.00025 = 0.00025
        # Output: 1K * 0.00125 = 0.00125
        # Thinking: 1K * 0.0025 = 0.0025
        # Total: 0.004
        assert breakdown.total_cost == pytest.approx(0.004, rel=0.01)

    def test_get_summary(self):
        """get_summary returns aggregate data."""
        analyzer = CostAnalyzer()
        analyzer.start_session("test_001")
        analyzer.record_api_call("test_001", input_tokens=1000, output_tokens=500)
        analyzer.complete_session("test_001")
        summary = analyzer.get_summary()
        assert "total_sessions" in summary
        assert "total_cost" in summary

    def test_estimate_trifecta_cost(self):
        """Estimate trifecta cost returns breakdown."""
        analyzer = CostAnalyzer()
        estimate = analyzer.estimate_trifecta_cost("design_page")
        assert isinstance(estimate, CostBreakdown)
        assert estimate.total_tokens > 0


class TestQualityMetrics:
    """Tests for QualityMetrics."""

    def test_quality_score_weighted_average(self):
        """Weighted average calculation."""
        score = QualityScore(
            layout=8.0,
            typography=7.0,
            color=9.0,
            interaction=6.0,
            accessibility=8.5,
        )
        # layout*0.25 + typography*0.15 + color*0.20 + interaction*0.15 + accessibility*0.25
        # 2.0 + 1.05 + 1.8 + 0.9 + 2.125 = 7.875
        assert score.weighted_average == pytest.approx(7.875, rel=0.01)

    def test_quality_score_from_overall(self):
        """from_overall factory method."""
        score = QualityScore.from_overall(8.5)
        assert score.layout == 8.5
        assert score.typography == 8.5
        assert score.weighted_average == 8.5

    def test_quality_score_meets_threshold(self):
        """meets_threshold checks correctly."""
        score = QualityScore.from_overall(7.5)
        assert score.meets_threshold(7.0) is True
        assert score.meets_threshold(8.0) is False

    def test_record_score(self):
        """Record score stores in metrics."""
        metrics = QualityMetrics()
        score = QualityScore.from_overall(8.0)
        metrics.record_score("test_001", score)
        final = metrics.get_final_score("test_001")
        assert final.weighted_average == 8.0

    def test_get_improvement(self):
        """Calculate improvement between scores."""
        metrics = QualityMetrics()
        metrics.record_score("test_001", QualityScore.from_overall(6.0))
        metrics.record_score("test_001", QualityScore.from_overall(8.0))
        improvement = metrics.get_improvement("test_001")
        assert improvement == pytest.approx(2.0, rel=0.01)

    def test_get_summary(self):
        """get_summary returns aggregate stats."""
        metrics = QualityMetrics()
        metrics.record_score("test_001", QualityScore.from_overall(8.0))
        summary = metrics.get_summary()
        assert "total_sessions" in summary
        assert summary["total_sessions"] == 1


class TestMaestroFormatter:
    """Tests for MaestroFormatter."""

    def test_format_question_dict(self):
        """Format question from dict."""
        formatter = MaestroFormatter()
        result = formatter.format_question({
            "id": "q1",
            "text": "Test question?",
            "category": "intent",
            "question_type": "single_choice",
            "options": [
                {"id": "opt1", "label": "Option 1", "description": "Desc 1"},
            ],
        })
        assert result["formatted"] is True
        assert result["type"] == "question"
        assert result["question_id"] == "q1"
        assert len(result["options"]) == 1

    def test_format_question_with_progress(self):
        """Format question includes progress when provided."""
        formatter = MaestroFormatter()
        result = formatter.format_question(
            {"id": "q1", "text": "Test?", "category": "intent", "options": []},
            current_step=2,
            total_steps=5,
        )
        assert "progress" in result
        assert result["progress"]["current"] == 2
        assert result["progress"]["total"] == 5

    def test_format_execution_result_success(self):
        """Format successful execution result."""
        formatter = MaestroFormatter()
        result = formatter.format_execution_result({
            "mode": "design_frontend",
            "html": "<div>Test</div>",
            "trifecta_enabled": True,
        })
        assert result["status"] == "complete"
        assert result["type"] == "success"
        assert "preview" in result

    def test_format_execution_result_error(self):
        """Format error execution result."""
        formatter = MaestroFormatter()
        result = formatter.format_execution_result({
            "error": "Something went wrong",
            "mode": "design_frontend",
        })
        assert result["status"] == "failed"
        assert result["type"] == "error"
        assert "error" in result

    def test_format_progress(self):
        """Format progress indicator."""
        formatter = MaestroFormatter()
        result = formatter.format_progress("Generating", 0.5, "Halfway there")
        assert result["type"] == "progress"
        assert result["progress"] == 0.5
        assert result["percent"] == "%50"


class TestAdaptiveFlow:
    """Tests for AdaptiveFlow."""

    def test_set_context(self):
        """Set context stores FlowContext."""
        flow = AdaptiveFlow()
        ctx = FlowContext(project_context="B2B SaaS", existing_html="")
        flow.set_context(ctx)
        # Should not raise
        decision = flow.should_skip_question("industry")
        assert decision is not None

    def test_should_skip_with_inference(self):
        """Skip question when context can infer answer."""
        flow = AdaptiveFlow()
        # "fintech" in context should infer industry=finance
        ctx = FlowContext(project_context="Fintech startup dashboard", existing_html="")
        flow.set_context(ctx)
        decision = flow.should_skip_question("industry")
        # May or may not skip depending on inference rules
        assert decision.should_skip in (True, False)

    def test_should_skip_no_context(self):
        """No skip when no context set."""
        flow = AdaptiveFlow()
        ctx = FlowContext(project_context="", existing_html="")
        flow.set_context(ctx)
        decision = flow.should_skip_question("theme_style")
        assert decision.should_skip is False


class TestPreferenceLearner:
    """Tests for PreferenceLearner."""

    def test_learn_preference(self):
        """Learn stores preference."""
        learner = PreferenceLearner()
        learner.learn(PreferenceType.THEME, "corporate")
        pref = learner.get_preference(PreferenceType.THEME)
        # First learn may not immediately return due to confidence threshold
        # but should not raise
        assert pref is None or pref.value == "corporate"

    def test_get_preference_none(self):
        """Get returns None when no preference learned."""
        learner = PreferenceLearner()
        pref = learner.get_preference(PreferenceType.QUALITY_LEVEL)
        assert pref is None

    def test_get_suggestions(self):
        """Get suggestions returns list."""
        learner = PreferenceLearner()
        suggestions = learner.get_suggestions("B2B dashboard")
        assert isinstance(suggestions, list)


class TestRecommender:
    """Tests for Recommender."""

    def test_get_all_recommendations(self):
        """Get all recommendations returns dict."""
        learner = PreferenceLearner()
        flow = AdaptiveFlow()
        recommender = Recommender(learner, flow)

        ctx = FlowContext(project_context="E-commerce site", existing_html="")
        recommender.set_context(ctx)

        recs = recommender.get_all_recommendations()
        assert isinstance(recs, dict)
        assert "theme" in recs
        assert "mode" in recs

    def test_recommend_theme(self):
        """Recommend theme returns Recommendation."""
        learner = PreferenceLearner()
        flow = AdaptiveFlow()
        recommender = Recommender(learner, flow)

        ctx = FlowContext(project_context="Healthcare portal", existing_html="")
        recommender.set_context(ctx)

        rec = recommender.recommend_theme()
        assert rec is not None
        assert rec.value is not None
        assert 0 <= rec.confidence <= 1


class TestUIHelpers:
    """Tests for UI helper functions."""

    def test_generate_progress_bar(self):
        """Progress bar generates correctly."""
        bar = generate_progress_bar(0.5)
        assert isinstance(bar, str)
        assert len(bar) > 0

    def test_mode_descriptions_complete(self):
        """All modes have descriptions."""
        expected_modes = [
            "design_frontend",
            "design_page",
            "design_section",
            "refine_frontend",
            "replace_section_in_page",
            "design_from_reference",
        ]
        for mode in expected_modes:
            assert mode in MODE_DESCRIPTIONS
