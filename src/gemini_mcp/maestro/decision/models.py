"""
MAESTRO Decision Models - Phase 3

Data structures for AI-powered decision making.
Includes confidence scoring, context analysis, and decision results.

Pattern Reference: agents/critic.py CriticScores
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class DecisionScores:
    """
    6-dimension weighted scoring for decision confidence.

    Used to evaluate how confident we are in the selected design mode.
    Each dimension represents a different aspect of decision quality.

    Dimension Weights:
    - intent_clarity (25%): How clearly user expressed their intent
    - scope_match (20%): How well scope matches selected mode
    - context_richness (15%): Amount of available context (HTML, project info)
    - parameter_completeness (20%): Whether all required params are available
    - constraint_satisfaction (10%): Whether constraints are met
    - alternative_viability (10%): How viable other options are

    Total weights = 100% (must sum to 1.0)
    """

    # Score dimensions (0.0 to 1.0 scale)
    intent_clarity: float = 0.5
    scope_match: float = 0.5
    context_richness: float = 0.5
    parameter_completeness: float = 0.5
    constraint_satisfaction: float = 0.5
    alternative_viability: float = 0.5

    # Dimension weights (must sum to 1.0)
    WEIGHTS: ClassVar[dict[str, float]] = {
        "intent_clarity": 0.25,
        "scope_match": 0.20,
        "context_richness": 0.15,
        "parameter_completeness": 0.20,
        "constraint_satisfaction": 0.10,
        "alternative_viability": 0.10,
    }

    @property
    def overall(self) -> float:
        """Calculate weighted average confidence score."""
        return (
            self.intent_clarity * self.WEIGHTS["intent_clarity"]
            + self.scope_match * self.WEIGHTS["scope_match"]
            + self.context_richness * self.WEIGHTS["context_richness"]
            + self.parameter_completeness * self.WEIGHTS["parameter_completeness"]
            + self.constraint_satisfaction * self.WEIGHTS["constraint_satisfaction"]
            + self.alternative_viability * self.WEIGHTS["alternative_viability"]
        )

    def weighted_average(self) -> float:
        """Alias for overall property - for compatibility."""
        return self.overall

    def get_dimension_scores(self) -> dict[str, float]:
        """Get all dimension scores as a dictionary."""
        return {
            "intent_clarity": self.intent_clarity,
            "scope_match": self.scope_match,
            "context_richness": self.context_richness,
            "parameter_completeness": self.parameter_completeness,
            "constraint_satisfaction": self.constraint_satisfaction,
            "alternative_viability": self.alternative_viability,
        }

    def get_lowest_dimensions(self, count: int = 2) -> list[tuple[str, float]]:
        """
        Get dimensions with lowest scores for targeted improvement.

        Useful for understanding why confidence is low.

        Args:
            count: Number of lowest dimensions to return

        Returns:
            List of (dimension_name, score) tuples, sorted lowest to highest
        """
        dimension_scores = self.get_dimension_scores()
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])
        return sorted_dims[:count]

    def get_highest_dimensions(self, count: int = 2) -> list[tuple[str, float]]:
        """
        Get dimensions with highest scores.

        Useful for understanding decision strengths.

        Args:
            count: Number of highest dimensions to return

        Returns:
            List of (dimension_name, score) tuples, sorted highest to lowest
        """
        dimension_scores = self.get_dimension_scores()
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_dims[:count]

    def is_high_confidence(self, threshold: float = 0.85) -> bool:
        """Check if overall confidence exceeds threshold."""
        return self.overall >= threshold

    def needs_gemini(self, threshold: float = 0.70) -> bool:
        """Check if confidence is low enough to warrant Gemini reasoning."""
        return self.overall < threshold


@dataclass
class ContextAnalysis:
    """
    Results from analyzing existing HTML context.

    When user provides previous_html for refinement or style matching,
    ContextAnalyzer extracts design tokens from it.
    """

    # Basic state
    has_html: bool = False

    # Detected design elements
    detected_theme: str | None = None
    detected_colors: dict[str, str] = field(default_factory=dict)
    detected_typography: dict[str, list[str]] = field(default_factory=dict)
    detected_spacing: dict[str, list[str]] = field(default_factory=dict)
    detected_components: list[str] = field(default_factory=list)

    # Raw Tailwind data
    tailwind_classes: list[str] = field(default_factory=list)

    # Aggregated design tokens for passing to design tools
    design_tokens: dict[str, Any] = field(default_factory=dict)

    # Section markers detected (for replace_section_in_page)
    section_markers: list[str] = field(default_factory=list)

    @property
    def class_count(self) -> int:
        """Total number of unique Tailwind classes detected."""
        return len(self.tailwind_classes)

    @property
    def component_count(self) -> int:
        """Number of components detected in HTML."""
        return len(self.detected_components)

    def has_section_markers(self) -> bool:
        """Check if HTML has section markers for replacement."""
        return len(self.section_markers) > 0

    def get_primary_color(self) -> str | None:
        """Get the primary color if detected."""
        return self.detected_colors.get("primary")

    def to_design_tokens(self) -> dict[str, Any]:
        """Export as design tokens dict for design tools."""
        if self.design_tokens:
            return self.design_tokens

        return {
            "theme": self.detected_theme,
            "colors": self.detected_colors,
            "typography": self.detected_typography,
            "spacing": self.detected_spacing,
            "components": self.detected_components,
        }


@dataclass
class EnrichedContext:
    """
    Combined interview answers + HTML analysis.

    This is the complete context passed to DecisionTree for mode selection.
    """

    # Interview answers: question_id → first selected option
    answers: dict[str, str] = field(default_factory=dict)

    # HTML analysis results
    html_analysis: ContextAnalysis = field(default_factory=ContextAnalysis)

    # Project context string
    project_context: str = ""

    # Explicit constraints (e.g., "must support dark mode")
    constraints: list[str] = field(default_factory=list)

    def get_answer(self, question_id: str) -> str | None:
        """Get answer for a specific question."""
        return self.answers.get(question_id)

    def has_answer(self, question_id: str) -> bool:
        """Check if a question was answered."""
        return question_id in self.answers

    def has_html_context(self) -> bool:
        """Check if HTML context is available."""
        return self.html_analysis.has_html

    def has_project_context(self) -> bool:
        """Check if project context is provided."""
        return bool(self.project_context)

    @property
    def answer_count(self) -> int:
        """Total number of answers collected."""
        return len(self.answers)


@dataclass
class DecisionAnalysis:
    """
    Full decision analysis with reasoning.

    Returned by DecisionTree.make_decision() with complete analysis.
    """

    # Selected mode
    selected_mode: str

    # Confidence score (0.0 to 1.0)
    confidence: float

    # Detailed scores
    scores: DecisionScores

    # Human-readable reasoning (Turkish)
    reasoning: str

    # Parameters extracted for the mode
    parameters: dict[str, Any] = field(default_factory=dict)

    # Alternative modes considered
    alternatives: list[dict[str, Any]] = field(default_factory=list)

    # Whether Gemini was used for reasoning
    used_gemini: bool = False

    # Low dimensions that affected confidence
    weak_dimensions: list[tuple[str, float]] = field(default_factory=list)

    def is_confident(self, threshold: float = 0.85) -> bool:
        """Check if decision confidence is high enough."""
        return self.confidence >= threshold

    def get_primary_weakness(self) -> str | None:
        """Get the primary weakness in the decision."""
        if self.weak_dimensions:
            return self.weak_dimensions[0][0]
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "selected_mode": self.selected_mode,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "parameters": self.parameters,
            "alternatives": self.alternatives,
            "used_gemini": self.used_gemini,
            "scores": self.scores.get_dimension_scores(),
        }


# Type aliases for clarity
ModeParameters = dict[str, Any]
AnswerMap = dict[str, str]  # question_id → selected_option
