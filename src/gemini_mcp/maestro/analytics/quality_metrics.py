"""
Quality Metrics - Aggregates design quality scores.

Tracks 5-dimension quality scores from Critic agent:
- Layout (25%)
- Typography (15%)
- Color (20%)
- Interaction (15%)
- Accessibility (25%)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """5-dimension quality score from Critic agent."""

    layout: float = 0.0
    typography: float = 0.0
    color: float = 0.0
    interaction: float = 0.0
    accessibility: float = 0.0

    # Weights match Critic agent's scoring priorities
    WEIGHTS: ClassVar[dict[str, float]] = {
        "layout": 0.25,
        "typography": 0.15,
        "color": 0.20,
        "interaction": 0.15,
        "accessibility": 0.25,
    }

    @property
    def weighted_average(self) -> float:
        """Calculate weighted average across all dimensions."""
        total = 0.0
        for dim, weight in self.WEIGHTS.items():
            total += getattr(self, dim) * weight
        return total

    @property
    def lowest_dimension(self) -> tuple[str, float]:
        """Get the dimension with lowest score for targeted improvement."""
        scores = [(dim, getattr(self, dim)) for dim in self.WEIGHTS]
        return min(scores, key=lambda x: x[1])

    @property
    def highest_dimension(self) -> tuple[str, float]:
        """Get the dimension with highest score."""
        scores = [(dim, getattr(self, dim)) for dim in self.WEIGHTS]
        return max(scores, key=lambda x: x[1])

    def get_improvement_priorities(self, count: int = 2) -> list[tuple[str, float]]:
        """Get dimensions that need the most improvement."""
        scores = [(dim, getattr(self, dim)) for dim in self.WEIGHTS]
        scores.sort(key=lambda x: x[1])
        return scores[:count]

    def meets_threshold(self, threshold: float = 7.0) -> bool:
        """Check if weighted average meets quality threshold."""
        return self.weighted_average >= threshold

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "dimensions": {
                "layout": round(self.layout, 2),
                "typography": round(self.typography, 2),
                "color": round(self.color, 2),
                "interaction": round(self.interaction, 2),
                "accessibility": round(self.accessibility, 2),
            },
            "weighted_average": round(self.weighted_average, 2),
            "lowest": self.lowest_dimension[0],
            "highest": self.highest_dimension[0],
            "meets_production": self.meets_threshold(7.0),
        }

    @classmethod
    def from_critic_response(cls, response: dict[str, Any]) -> "QualityScore":
        """
        Create QualityScore from Critic agent response.

        Args:
            response: Critic agent response dict with dimension scores

        Returns:
            QualityScore instance
        """
        scores = response.get("scores", {})
        return cls(
            layout=scores.get("layout", 0.0),
            typography=scores.get("typography", 0.0),
            color=scores.get("color", 0.0),
            interaction=scores.get("interaction", 0.0),
            accessibility=scores.get("accessibility", 0.0),
        )

    @classmethod
    def from_overall(
        cls,
        overall: float,
        dimensions: dict[str, float] | None = None,
    ) -> "QualityScore":
        """
        Create QualityScore from overall score and optional dimensions.

        If dimensions not provided, distributes overall score evenly.

        Args:
            overall: Overall quality score (0-10)
            dimensions: Optional dimension-specific scores

        Returns:
            QualityScore instance
        """
        if dimensions:
            return cls(
                layout=dimensions.get("layout", overall),
                typography=dimensions.get("typography", overall),
                color=dimensions.get("color", overall),
                interaction=dimensions.get("interaction", overall),
                accessibility=dimensions.get("accessibility", overall),
            )
        # Distribute evenly if no dimensions provided
        return cls(
            layout=overall,
            typography=overall,
            color=overall,
            interaction=overall,
            accessibility=overall,
        )


class QualityMetrics:
    """
    Aggregates quality metrics across MAESTRO sessions.

    Tracks score history per session to measure:
    - Quality improvement over iterations
    - Average quality across all sessions
    - Dimension-specific performance patterns

    Usage:
        metrics = QualityMetrics()
        metrics.record_score("session_123", QualityScore(layout=8.0, ...))
        final = metrics.get_final_score("session_123")
        avg = metrics.get_average_score()
    """

    def __init__(self):
        """Initialize QualityMetrics."""
        self._scores: dict[str, list[QualityScore]] = {}

    def record_score(self, session_id: str, score: QualityScore) -> None:
        """
        Record a quality score for a session.

        Multiple scores per session are allowed for tracking
        iteration improvements (e.g., Critic refinement loop).

        Args:
            session_id: Session identifier
            score: QualityScore to record
        """
        if session_id not in self._scores:
            self._scores[session_id] = []
        self._scores[session_id].append(score)

        logger.debug(
            f"[QualityMetrics] Recorded score for {session_id}: "
            f"{score.weighted_average:.2f}"
        )

    def get_session_scores(self, session_id: str) -> list[QualityScore]:
        """
        Get all scores for a session.

        Args:
            session_id: Session to look up

        Returns:
            List of QualityScore objects (may be empty)
        """
        return self._scores.get(session_id, [])

    def get_final_score(self, session_id: str) -> QualityScore | None:
        """
        Get the final (most recent) score for a session.

        Args:
            session_id: Session to look up

        Returns:
            Final QualityScore or None if no scores
        """
        scores = self._scores.get(session_id, [])
        return scores[-1] if scores else None

    def get_initial_score(self, session_id: str) -> QualityScore | None:
        """
        Get the initial score for a session.

        Args:
            session_id: Session to look up

        Returns:
            Initial QualityScore or None if no scores
        """
        scores = self._scores.get(session_id, [])
        return scores[0] if scores else None

    def get_improvement(self, session_id: str) -> float:
        """
        Calculate quality improvement for a session.

        Returns the difference between final and initial scores.

        Args:
            session_id: Session to look up

        Returns:
            Improvement in weighted average (can be negative)
        """
        scores = self._scores.get(session_id, [])
        if len(scores) < 2:
            return 0.0

        initial = scores[0].weighted_average
        final = scores[-1].weighted_average
        return final - initial

    def get_average_score(self) -> QualityScore:
        """
        Get average score across all sessions.

        Uses final score from each session for calculation.

        Returns:
            Average QualityScore (all zeros if no data)
        """
        final_scores = [
            scores[-1]
            for scores in self._scores.values()
            if scores
        ]

        if not final_scores:
            return QualityScore()

        n = len(final_scores)
        return QualityScore(
            layout=sum(s.layout for s in final_scores) / n,
            typography=sum(s.typography for s in final_scores) / n,
            color=sum(s.color for s in final_scores) / n,
            interaction=sum(s.interaction for s in final_scores) / n,
            accessibility=sum(s.accessibility for s in final_scores) / n,
        )

    def get_dimension_stats(self) -> dict[str, dict[str, float]]:
        """
        Get statistics for each quality dimension.

        Returns:
            Dict with min, max, avg for each dimension
        """
        final_scores = [
            scores[-1]
            for scores in self._scores.values()
            if scores
        ]

        if not final_scores:
            return {}

        stats = {}
        for dim in QualityScore.WEIGHTS:
            values = [getattr(s, dim) for s in final_scores]
            stats[dim] = {
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "avg": round(sum(values) / len(values), 2),
            }

        return stats

    def get_aggregate_stats(self) -> dict[str, Any]:
        """
        Get aggregate statistics across all sessions.

        Returns:
            Dict with overall metrics summary
        """
        if not self._scores:
            return {"total_sessions": 0}

        final_scores = [
            scores[-1]
            for scores in self._scores.values()
            if scores
        ]

        if not final_scores:
            return {"total_sessions": 0}

        # Calculate metrics
        averages = [s.weighted_average for s in final_scores]
        passed_production = sum(1 for s in final_scores if s.meets_threshold(7.0))

        # Calculate total improvement across sessions
        total_improvement = sum(
            self.get_improvement(sid)
            for sid in self._scores
        )

        return {
            "total_sessions": len(self._scores),
            "total_scores": sum(len(s) for s in self._scores.values()),
            "avg_quality": round(sum(averages) / len(averages), 2),
            "min_quality": round(min(averages), 2),
            "max_quality": round(max(averages), 2),
            "production_pass_rate": round(passed_production / len(final_scores), 2),
            "total_improvement": round(total_improvement, 2),
            "dimension_stats": self.get_dimension_stats(),
        }

    def clear_session(self, session_id: str) -> bool:
        """
        Clear scores for a session.

        Args:
            session_id: Session to clear

        Returns:
            True if session existed and was cleared
        """
        if session_id in self._scores:
            del self._scores[session_id]
            return True
        return False

    def get_summary(self) -> dict[str, Any]:
        """
        Get quality summary (alias for get_aggregate_stats).

        Returns:
            Dict with quality metrics summary
        """
        return self.get_aggregate_stats()

    @property
    def session_count(self) -> int:
        """Number of sessions with recorded scores."""
        return len(self._scores)

    @property
    def total_score_count(self) -> int:
        """Total number of scores across all sessions."""
        return sum(len(scores) for scores in self._scores.values())
