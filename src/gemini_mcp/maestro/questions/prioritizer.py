"""
MAESTRO Question Prioritizer - Phase 3

Prioritizes questions using multi-factor scoring to determine optimal
interview order. Considers gap severity, confidence impact, dependencies,
and interview phase.

Scoring Formula:
    score = (severity_weight * 0.4) + (confidence_impact * 0.3) +
            (category_priority * 0.2) + (dependency_bonus * 0.1)

Usage:
    >>> from gemini_mcp.maestro.questions.prioritizer import QuestionPrioritizer
    >>> prioritizer = QuestionPrioritizer()
    >>> ordered = prioritizer.prioritize(questions, soul, gaps)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional, Set

from gemini_mcp.maestro.models import (
    Question,
    QuestionCategory,
)
from gemini_mcp.maestro.models.gap import (
    GapCategory,
    GapInfo,
    GapSeverity,
    GapAnalysis,
)

if TYPE_CHECKING:
    from gemini_mcp.maestro.models.soul import ProjectSoul, InterviewPhase

logger = logging.getLogger(__name__)


class PriorityStrategy(str, Enum):
    """
    Different prioritization strategies.

    CRITICAL_FIRST: Always ask critical gaps first (default)
    CONFIDENCE_BOOST: Prioritize questions that boost confidence most
    CATEGORY_FLOW: Follow natural category order
    DEPENDENCY_AWARE: Resolve dependencies first
    BALANCED: Weighted combination of all factors
    """
    CRITICAL_FIRST = "critical_first"
    CONFIDENCE_BOOST = "confidence_boost"
    CATEGORY_FLOW = "category_flow"
    DEPENDENCY_AWARE = "dependency_aware"
    BALANCED = "balanced"


@dataclass
class PriorityScore:
    """
    Detailed priority score for a question.

    Tracks individual factor contributions for transparency.
    """
    question_id: str
    total_score: float
    severity_score: float = 0.0
    confidence_score: float = 0.0
    category_score: float = 0.0
    dependency_score: float = 0.0
    phase_bonus: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for debugging."""
        return {
            "question_id": self.question_id,
            "total": round(self.total_score, 2),
            "severity": round(self.severity_score, 2),
            "confidence": round(self.confidence_score, 2),
            "category": round(self.category_score, 2),
            "dependency": round(self.dependency_score, 2),
            "phase_bonus": round(self.phase_bonus, 2),
        }


class QuestionPrioritizer:
    """
    Multi-factor question prioritizer.

    Uses a weighted scoring system to determine optimal question order,
    considering gap severity, confidence impact, category flow, and
    dependency resolution.

    Example:
        >>> prioritizer = QuestionPrioritizer(strategy=PriorityStrategy.BALANCED)
        >>> questions = [q1, q2, q3]
        >>> gaps = GapAnalysis(gaps=[g1, g2, g3])
        >>> ordered = prioritizer.prioritize(questions, gaps=gaps)
        >>> # Questions now in optimal order
    """

    # =========================================================================
    # WEIGHT CONFIGURATION
    # =========================================================================

    # Default weights for balanced strategy
    DEFAULT_WEIGHTS: ClassVar[Dict[str, float]] = {
        "severity": 0.40,
        "confidence": 0.30,
        "category": 0.20,
        "dependency": 0.10,
    }

    # Severity scores (normalized 0-100)
    SEVERITY_SCORES: ClassVar[Dict[GapSeverity, float]] = {
        GapSeverity.CRITICAL: 100.0,
        GapSeverity.HIGH: 75.0,
        GapSeverity.MEDIUM: 50.0,
        GapSeverity.LOW: 25.0,
    }

    # Category priority (lower = higher priority)
    CATEGORY_PRIORITY: ClassVar[Dict[QuestionCategory, int]] = {
        QuestionCategory.INTENT: 1,
        QuestionCategory.SCOPE: 2,
        QuestionCategory.EXISTING_CONTEXT: 3,
        QuestionCategory.INDUSTRY: 4,
        QuestionCategory.THEME_STYLE: 5,
        QuestionCategory.VIBE_MOOD: 6,
        QuestionCategory.CONTENT: 7,
        QuestionCategory.TECHNICAL: 8,
        QuestionCategory.ACCESSIBILITY: 9,
        QuestionCategory.LANGUAGE: 10,
    }

    # Phase bonuses (questions relevant to current phase get bonus)
    PHASE_CATEGORY_MAP: ClassVar[Dict[str, List[QuestionCategory]]] = {
        "BRIEF_INGESTION": [QuestionCategory.INTENT, QuestionCategory.SCOPE],
        "SOUL_EXTRACTION": [QuestionCategory.INDUSTRY, QuestionCategory.VIBE_MOOD],
        "CONTEXT_GATHERING": [QuestionCategory.EXISTING_CONTEXT],
        "DEEP_DIVE": [QuestionCategory.THEME_STYLE, QuestionCategory.CONTENT],
        "VISUAL_EXPLORATION": [QuestionCategory.THEME_STYLE, QuestionCategory.VIBE_MOOD],
        "VALIDATION": [QuestionCategory.TECHNICAL, QuestionCategory.ACCESSIBILITY],
    }

    def __init__(
        self,
        strategy: PriorityStrategy = PriorityStrategy.BALANCED,
        weights: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Initialize prioritizer.

        Args:
            strategy: Prioritization strategy to use
            weights: Custom weights (overrides defaults for balanced strategy)
        """
        self.strategy = strategy
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._gap_map: Dict[str, GapInfo] = {}

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def prioritize(
        self,
        questions: List[Question],
        soul: Optional["ProjectSoul"] = None,
        gaps: Optional[GapAnalysis] = None,
        current_phase: Optional[str] = None,
        answered_ids: Optional[Set[str]] = None,
    ) -> List[Question]:
        """
        Prioritize questions by calculated score.

        Args:
            questions: Questions to prioritize
            soul: Optional ProjectSoul for context
            gaps: Gap analysis for severity/confidence info
            current_phase: Current interview phase for bonuses
            answered_ids: Set of already answered question IDs

        Returns:
            Questions sorted by priority (highest first)
        """
        if not questions:
            return []

        answered_ids = answered_ids or set()

        # Build gap map for lookups
        if gaps:
            self._gap_map = {f"q_{g.id}": g for g in gaps.gaps}
            self._gap_map.update({g.id: g for g in gaps.gaps})

        # Filter out answered questions
        unanswered = [q for q in questions if q.id not in answered_ids]

        # Calculate scores
        scores = [
            self._calculate_score(q, soul, current_phase)
            for q in unanswered
        ]

        # Sort by score descending
        sorted_pairs = sorted(
            zip(unanswered, scores),
            key=lambda pair: pair[1].total_score,
            reverse=True,
        )

        return [q for q, _ in sorted_pairs]

    def get_top_priority(
        self,
        questions: List[Question],
        soul: Optional["ProjectSoul"] = None,
        gaps: Optional[GapAnalysis] = None,
        current_phase: Optional[str] = None,
    ) -> Optional[Question]:
        """
        Get the single highest priority question.

        Args:
            questions: Questions to evaluate
            soul: Optional ProjectSoul
            gaps: Gap analysis
            current_phase: Current phase

        Returns:
            Highest priority Question or None
        """
        prioritized = self.prioritize(questions, soul, gaps, current_phase)
        return prioritized[0] if prioritized else None

    def get_score_breakdown(
        self,
        question: Question,
        soul: Optional["ProjectSoul"] = None,
        current_phase: Optional[str] = None,
    ) -> PriorityScore:
        """
        Get detailed score breakdown for a question.

        Args:
            question: Question to score
            soul: Optional ProjectSoul
            current_phase: Current phase

        Returns:
            PriorityScore with factor breakdown
        """
        return self._calculate_score(question, soul, current_phase)

    def reorder_by_dependencies(
        self,
        questions: List[Question],
        gaps: Optional[GapAnalysis] = None,
    ) -> List[Question]:
        """
        Reorder questions to respect dependencies.

        Ensures that questions with dependencies come after their
        dependency questions.

        Args:
            questions: Questions to reorder
            gaps: Gap analysis with dependency info

        Returns:
            Questions in dependency-valid order
        """
        if not gaps:
            return questions

        # Build dependency graph
        dependency_map: Dict[str, Set[str]] = {}
        for gap in gaps.gaps:
            q_id = f"q_{gap.id}"
            dependency_map[q_id] = set(f"q_{d}" for d in gap.depends_on)

        # Topological sort
        result = []
        visited = set()
        temp_visited = set()

        def visit(q: Question) -> None:
            if q.id in temp_visited:
                # Circular dependency - skip
                logger.warning(f"Circular dependency detected for {q.id}")
                return
            if q.id in visited:
                return

            temp_visited.add(q.id)

            # Visit dependencies first
            for dep_id in dependency_map.get(q.id, set()):
                dep_q = next((qq for qq in questions if qq.id == dep_id), None)
                if dep_q:
                    visit(dep_q)

            temp_visited.remove(q.id)
            visited.add(q.id)
            result.append(q)

        for q in questions:
            visit(q)

        return result

    # =========================================================================
    # SCORING METHODS
    # =========================================================================

    def _calculate_score(
        self,
        question: Question,
        soul: Optional["ProjectSoul"],
        current_phase: Optional[str],
    ) -> PriorityScore:
        """Calculate comprehensive priority score."""

        # Initialize score
        score = PriorityScore(question_id=question.id, total_score=0.0)

        # Get associated gap if exists
        gap = self._gap_map.get(question.id)

        # Calculate each factor
        if self.strategy in [PriorityStrategy.CRITICAL_FIRST, PriorityStrategy.BALANCED]:
            score.severity_score = self._score_severity(gap)

        if self.strategy in [PriorityStrategy.CONFIDENCE_BOOST, PriorityStrategy.BALANCED]:
            score.confidence_score = self._score_confidence_impact(gap)

        if self.strategy in [PriorityStrategy.CATEGORY_FLOW, PriorityStrategy.BALANCED]:
            score.category_score = self._score_category(question.category)

        if self.strategy in [PriorityStrategy.DEPENDENCY_AWARE, PriorityStrategy.BALANCED]:
            score.dependency_score = self._score_dependency(gap)

        # Phase bonus
        if current_phase:
            score.phase_bonus = self._score_phase_relevance(
                question.category, current_phase
            )

        # Calculate total based on strategy
        if self.strategy == PriorityStrategy.CRITICAL_FIRST:
            score.total_score = score.severity_score
        elif self.strategy == PriorityStrategy.CONFIDENCE_BOOST:
            score.total_score = score.confidence_score
        elif self.strategy == PriorityStrategy.CATEGORY_FLOW:
            score.total_score = score.category_score
        elif self.strategy == PriorityStrategy.DEPENDENCY_AWARE:
            score.total_score = score.dependency_score + score.severity_score * 0.5
        else:  # BALANCED
            score.total_score = (
                score.severity_score * self.weights["severity"] +
                score.confidence_score * self.weights["confidence"] +
                score.category_score * self.weights["category"] +
                score.dependency_score * self.weights["dependency"] +
                score.phase_bonus * 0.1  # Extra bonus
            )

        return score

    def _score_severity(self, gap: Optional[GapInfo]) -> float:
        """Score based on gap severity."""
        if not gap:
            return 50.0  # Default medium score
        return self.SEVERITY_SCORES.get(gap.severity, 50.0)

    def _score_confidence_impact(self, gap: Optional[GapInfo]) -> float:
        """Score based on confidence impact."""
        if not gap:
            return 50.0
        # Normalize confidence_impact (0-0.5) to 0-100
        return min(gap.confidence_impact * 200, 100.0)

    def _score_category(self, category: QuestionCategory) -> float:
        """Score based on category priority."""
        priority = self.CATEGORY_PRIORITY.get(category, 5)
        # Invert so priority 1 → score 100, priority 10 → score 10
        return max(0, 110 - priority * 10)

    def _score_dependency(self, gap: Optional[GapInfo]) -> float:
        """Score based on how many other gaps depend on this one."""
        if not gap:
            return 50.0
        # More blockers = higher priority (need to resolve first)
        blocker_count = len(gap.blocks) if hasattr(gap, 'blocks') else 0
        return min(50 + blocker_count * 10, 100.0)

    def _score_phase_relevance(
        self,
        category: QuestionCategory,
        current_phase: str,
    ) -> float:
        """Score based on phase relevance."""
        relevant_categories = self.PHASE_CATEGORY_MAP.get(current_phase, [])
        if category in relevant_categories:
            return 20.0  # Bonus for phase-relevant questions
        return 0.0


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def prioritize_questions(
    questions: List[Question],
    gaps: Optional[GapAnalysis] = None,
    strategy: PriorityStrategy = PriorityStrategy.BALANCED,
) -> List[Question]:
    """
    Convenience function to prioritize questions.

    Args:
        questions: Questions to prioritize
        gaps: Gap analysis for scoring
        strategy: Prioritization strategy

    Returns:
        Questions in priority order
    """
    prioritizer = QuestionPrioritizer(strategy=strategy)
    return prioritizer.prioritize(questions, gaps=gaps)
