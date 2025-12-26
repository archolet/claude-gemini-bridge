"""
Session Tracker - Tracks metrics for MAESTRO sessions.

Captures:
- Session duration (start → complete)
- Question count and response times
- Decision confidence history
- Mode selection frequency
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SessionMetrics:
    """Metrics for a single MAESTRO session."""

    session_id: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None

    # Interview metrics
    questions_asked: int = 0
    questions_answered: int = 0
    question_response_times: list[float] = field(default_factory=list)

    # Decision metrics
    decision_confidence: float = 0.0
    selected_mode: str = ""
    alternative_modes: list[str] = field(default_factory=list)

    # Execution metrics
    execution_time: float = 0.0
    execution_success: bool = False
    used_trifecta: bool = False
    quality_target: str = "production"

    @property
    def total_duration(self) -> float:
        """Total session duration in seconds."""
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def avg_response_time(self) -> float:
        """Average response time per question."""
        if not self.question_response_times:
            return 0.0
        return sum(self.question_response_times) / len(self.question_response_times)

    @property
    def completion_rate(self) -> float:
        """Ratio of answered to asked questions."""
        if self.questions_asked == 0:
            return 0.0
        return self.questions_answered / self.questions_asked

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "duration_seconds": self.total_duration,
            "questions": {
                "asked": self.questions_asked,
                "answered": self.questions_answered,
                "completion_rate": self.completion_rate,
                "avg_response_time": self.avg_response_time,
            },
            "decision": {
                "mode": self.selected_mode,
                "confidence": self.decision_confidence,
                "alternatives": self.alternative_modes,
            },
            "execution": {
                "time_seconds": self.execution_time,
                "success": self.execution_success,
                "trifecta_enabled": self.used_trifecta,
                "quality_target": self.quality_target,
            },
        }


class SessionTracker:
    """
    Tracks session metrics across all MAESTRO sessions.

    Thread-safe singleton pattern for global access.

    Usage:
        tracker = SessionTracker()  # Gets singleton instance
        tracker.start_session("maestro_123")
        tracker.record_question("maestro_123", response_time=1.5)
        tracker.record_decision("maestro_123", mode="design_page", confidence=0.85)
        tracker.complete_session("maestro_123")
        stats = tracker.get_aggregate_stats()
    """

    _instance: "SessionTracker | None" = None

    def __new__(cls) -> "SessionTracker":
        """Singleton pattern - ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._metrics: dict[str, SessionMetrics] = {}
            cls._instance._completed: list[SessionMetrics] = []
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton for testing purposes."""
        cls._instance = None

    def start_session(self, session_id: str) -> SessionMetrics:
        """
        Start tracking a new session.

        Args:
            session_id: Unique session identifier

        Returns:
            New SessionMetrics instance
        """
        metrics = SessionMetrics(session_id=session_id)
        self._metrics[session_id] = metrics
        logger.debug(f"[SessionTracker] Started: {session_id}")
        return metrics

    def get_metrics(self, session_id: str) -> SessionMetrics | None:
        """
        Get metrics for an active session.

        Args:
            session_id: Session to look up

        Returns:
            SessionMetrics or None if not found
        """
        return self._metrics.get(session_id)

    def record_question(self, session_id: str, response_time: float = 0.0) -> None:
        """
        Record that a question was asked.

        Args:
            session_id: Active session
            response_time: Time taken to respond (optional)
        """
        if metrics := self._metrics.get(session_id):
            metrics.questions_asked += 1
            if response_time > 0:
                metrics.question_response_times.append(response_time)

    def record_answer(self, session_id: str, response_time: float = 0.0) -> None:
        """
        Record that an answer was received.

        Args:
            session_id: Active session
            response_time: Time taken for this answer (optional)
        """
        if metrics := self._metrics.get(session_id):
            metrics.questions_answered += 1
            if response_time > 0:
                metrics.question_response_times.append(response_time)

    def record_decision(
        self,
        session_id: str,
        mode: str,
        confidence: float,
        alternatives: list[str] | None = None,
    ) -> None:
        """
        Record that a decision was made.

        Args:
            session_id: Active session
            mode: Selected design mode
            confidence: Decision confidence (0.0-1.0)
            alternatives: Alternative modes considered
        """
        if metrics := self._metrics.get(session_id):
            metrics.selected_mode = mode
            metrics.decision_confidence = confidence
            metrics.alternative_modes = alternatives or []

    def record_execution(
        self,
        session_id: str,
        execution_time: float,
        success: bool,
        used_trifecta: bool = False,
        quality_target: str = "production",
    ) -> None:
        """
        Record execution completed.

        Args:
            session_id: Active session
            execution_time: Time taken for execution
            success: Whether execution succeeded
            used_trifecta: Whether Trifecta pipeline was used
            quality_target: Quality level used
        """
        if metrics := self._metrics.get(session_id):
            metrics.execution_time = execution_time
            metrics.execution_success = success
            metrics.used_trifecta = used_trifecta
            metrics.quality_target = quality_target

    def complete_session(self, session_id: str) -> SessionMetrics | None:
        """
        Mark session as complete and archive metrics.

        Args:
            session_id: Session to complete

        Returns:
            Completed SessionMetrics or None if not found
        """
        if metrics := self._metrics.pop(session_id, None):
            metrics.end_time = time.time()
            self._completed.append(metrics)
            logger.debug(f"[SessionTracker] Completed: {session_id}")
            return metrics
        return None

    def get_aggregate_stats(self) -> dict[str, Any]:
        """
        Get aggregate statistics across all completed sessions.

        Returns:
            Dict with overall statistics
        """
        if not self._completed:
            return {"total_sessions": 0}

        total = len(self._completed)
        success_count = sum(1 for m in self._completed if m.execution_success)
        trifecta_count = sum(1 for m in self._completed if m.used_trifecta)

        # Mode distribution
        mode_counts: dict[str, int] = {}
        for m in self._completed:
            if m.selected_mode:
                mode_counts[m.selected_mode] = mode_counts.get(m.selected_mode, 0) + 1

        # Quality target distribution
        quality_counts: dict[str, int] = {}
        for m in self._completed:
            quality_counts[m.quality_target] = (
                quality_counts.get(m.quality_target, 0) + 1
            )

        return {
            "total_sessions": total,
            "success_rate": success_count / total,
            "avg_duration": sum(m.total_duration for m in self._completed) / total,
            "avg_confidence": sum(m.decision_confidence for m in self._completed) / total,
            "avg_questions": sum(m.questions_answered for m in self._completed) / total,
            "trifecta_usage_rate": trifecta_count / total,
            "mode_distribution": mode_counts,
            "quality_distribution": quality_counts,
        }

    def track_event(
        self,
        session_id: str,
        event_type: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """
        Track a custom event during a session.

        Args:
            session_id: Active session
            event_type: Type of event (e.g., "execution_complete")
            data: Optional event data
        """
        # Currently just logs - could be extended for detailed event tracking
        logger.debug(f"[SessionTracker] Event {event_type} for {session_id}: {data}")

    def end_session(self, session_id: str) -> SessionMetrics | None:
        """
        Alias for complete_session - marks session as complete.

        Args:
            session_id: Session to end

        Returns:
            Completed SessionMetrics or None if not found
        """
        return self.complete_session(session_id)

    def get_session_duration(self, session_id: str) -> float:
        """
        Get duration of a session (active or completed).

        Args:
            session_id: Session to look up

        Returns:
            Duration in seconds, 0.0 if not found
        """
        # Check active sessions
        if metrics := self._metrics.get(session_id):
            return metrics.total_duration

        # Check completed sessions
        for metrics in self._completed:
            if metrics.session_id == session_id:
                return metrics.total_duration

        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """
        Convert tracker state to dictionary.

        Returns:
            Dict with tracker statistics
        """
        return {
            "active_sessions": self.active_count,
            "completed_sessions": self.completed_count,
            "aggregate_stats": self.get_aggregate_stats(),
        }

    @property
    def active_count(self) -> int:
        """Number of currently active sessions."""
        return len(self._metrics)

    @property
    def completed_count(self) -> int:
        """Number of completed sessions."""
        return len(self._completed)
