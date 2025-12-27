"""
MAESTRO Progress Tracker - Phase 3

Tracks interview progress with rich metrics and visual feedback.
Provides real-time progress updates, phase completion tracking,
and time-based analytics.

Features:
- Phase-by-phase progress tracking
- Question completion metrics
- Confidence evolution tracking
- Time analytics (duration, estimated remaining)
- Rich progress display formatting

Usage:
    >>> from gemini_mcp.maestro.interview.progress import ProgressTracker
    >>> tracker = ProgressTracker()
    >>> tracker.start_phase(InterviewPhase.BRIEF_INGESTION)
    >>> tracker.record_question_answered("q_intent_main")
    >>> display = tracker.get_progress_display()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional, Set

from gemini_mcp.maestro.models.soul import InterviewPhase

if TYPE_CHECKING:
    from gemini_mcp.maestro.models.soul import ProjectSoul

logger = logging.getLogger(__name__)


class ProgressStatus(str, Enum):
    """Status of the interview progress."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PhaseMetrics:
    """
    Metrics for a single interview phase.

    Tracks timing, questions, and completion status.
    """
    phase: InterviewPhase
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    questions_asked: int = 0
    questions_answered: int = 0
    questions_skipped: int = 0
    confidence_start: float = 0.0
    confidence_end: float = 0.0

    @property
    def is_started(self) -> bool:
        """Check if phase has been started."""
        return self.started_at is not None

    @property
    def is_completed(self) -> bool:
        """Check if phase has been completed."""
        return self.completed_at is not None

    @property
    def duration(self) -> Optional[timedelta]:
        """Get phase duration if completed."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return datetime.now() - self.started_at
        return None

    @property
    def answer_rate(self) -> float:
        """Get question answer rate (0.0 - 1.0)."""
        total = self.questions_asked
        if total == 0:
            return 0.0
        return self.questions_answered / total

    @property
    def confidence_gain(self) -> float:
        """Get confidence improvement during phase."""
        return self.confidence_end - self.confidence_start

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "phase": self.phase.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration.total_seconds() if self.duration else None,
            "questions_asked": self.questions_asked,
            "questions_answered": self.questions_answered,
            "questions_skipped": self.questions_skipped,
            "answer_rate": round(self.answer_rate, 2),
            "confidence_start": round(self.confidence_start, 2),
            "confidence_end": round(self.confidence_end, 2),
            "confidence_gain": round(self.confidence_gain, 2),
        }


@dataclass
class ProgressSnapshot:
    """
    Point-in-time snapshot of interview progress.

    Used for analytics and display updates.
    """
    timestamp: datetime
    current_phase: InterviewPhase
    overall_progress: float  # 0.0 - 1.0
    phase_progress: float  # 0.0 - 1.0
    overall_confidence: float
    questions_total: int
    questions_answered: int
    elapsed_time: timedelta
    estimated_remaining: Optional[timedelta]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "current_phase": self.current_phase.value,
            "overall_progress": round(self.overall_progress, 2),
            "phase_progress": round(self.phase_progress, 2),
            "overall_confidence": round(self.overall_confidence, 2),
            "questions_total": self.questions_total,
            "questions_answered": self.questions_answered,
            "elapsed_time_seconds": self.elapsed_time.total_seconds(),
            "estimated_remaining_seconds": (
                self.estimated_remaining.total_seconds()
                if self.estimated_remaining else None
            ),
        }


@dataclass
class ProgressDisplay:
    """
    Rich progress display data for UI rendering.

    Contains formatted strings ready for display.
    """
    progress_bar: str
    percentage: str
    current_step: int
    total_steps: int
    phase_name: str
    phase_emoji: str
    category_tip: str
    elapsed_formatted: str
    remaining_formatted: str
    confidence_indicator: str


class ProgressTracker:
    """
    Comprehensive progress tracking for MAESTRO interviews.

    Tracks phase-by-phase progress, timing, question metrics,
    confidence evolution, and provides rich display formatting.

    Example:
        >>> tracker = ProgressTracker()
        >>> tracker.start_interview()
        >>> tracker.start_phase(InterviewPhase.BRIEF_INGESTION)
        >>> tracker.record_question_answered("q_intent")
        >>> display = tracker.get_progress_display()
        >>> print(display.progress_bar)
        ████████░░░░░░░░ 50%
    """

    # =========================================================================
    # PHASE CONFIGURATION
    # =========================================================================

    # Weight of each phase in overall progress
    PHASE_WEIGHTS: ClassVar[Dict[InterviewPhase, float]] = {
        InterviewPhase.BRIEF_INGESTION: 0.05,
        InterviewPhase.SOUL_EXTRACTION: 0.10,
        InterviewPhase.CONTEXT_GATHERING: 0.20,
        InterviewPhase.DEEP_DIVE: 0.25,
        InterviewPhase.VISUAL_EXPLORATION: 0.15,
        InterviewPhase.VALIDATION: 0.15,
        InterviewPhase.SYNTHESIS: 0.05,
        InterviewPhase.COMPLETE: 0.05,
    }

    # Expected questions per phase (for estimation)
    EXPECTED_QUESTIONS: ClassVar[Dict[InterviewPhase, int]] = {
        InterviewPhase.BRIEF_INGESTION: 0,
        InterviewPhase.SOUL_EXTRACTION: 2,
        InterviewPhase.CONTEXT_GATHERING: 3,
        InterviewPhase.DEEP_DIVE: 4,
        InterviewPhase.VISUAL_EXPLORATION: 3,
        InterviewPhase.VALIDATION: 2,
        InterviewPhase.SYNTHESIS: 0,
        InterviewPhase.COMPLETE: 0,
    }

    # Phase display info
    PHASE_INFO: ClassVar[Dict[InterviewPhase, tuple[str, str]]] = {
        InterviewPhase.BRIEF_INGESTION: ("Brief Analizi", "📋"),
        InterviewPhase.SOUL_EXTRACTION: ("Proje Ruhu", "✨"),
        InterviewPhase.CONTEXT_GATHERING: ("Bağlam Toplama", "🔍"),
        InterviewPhase.DEEP_DIVE: ("Derinlemesine Analiz", "🎯"),
        InterviewPhase.VISUAL_EXPLORATION: ("Görsel Keşif", "🎨"),
        InterviewPhase.VALIDATION: ("Doğrulama", "✅"),
        InterviewPhase.SYNTHESIS: ("Sentez", "🧩"),
        InterviewPhase.COMPLETE: ("Tamamlandı", "🎉"),
    }

    # Phase-specific tips
    PHASE_TIPS: ClassVar[Dict[InterviewPhase, str]] = {
        InterviewPhase.BRIEF_INGESTION: "Brief'iniz analiz ediliyor...",
        InterviewPhase.SOUL_EXTRACTION: "Projenizin kimliğini keşfediyoruz",
        InterviewPhase.CONTEXT_GATHERING: "Detayları anlamamıza yardımcı olun",
        InterviewPhase.DEEP_DIVE: "Spesifik tercihlerinizi öğreniyoruz",
        InterviewPhase.VISUAL_EXPLORATION: "Görsel stilinizi belirliyoruz",
        InterviewPhase.VALIDATION: "Bilgileri doğruluyoruz",
        InterviewPhase.SYNTHESIS: "Tasarım kararları oluşturuluyor",
        InterviewPhase.COMPLETE: "Interview tamamlandı!",
    }

    # Confidence level indicators
    CONFIDENCE_INDICATORS: ClassVar[Dict[str, str]] = {
        "low": "🔴",      # < 0.4
        "medium": "🟡",   # 0.4 - 0.7
        "high": "🟢",     # > 0.7
    }

    def __init__(self) -> None:
        """Initialize progress tracker."""
        self._status = ProgressStatus.NOT_STARTED
        self._started_at: Optional[datetime] = None
        self._completed_at: Optional[datetime] = None

        # Phase tracking
        self._current_phase: Optional[InterviewPhase] = None
        self._phase_metrics: Dict[InterviewPhase, PhaseMetrics] = {}
        self._phase_order: List[InterviewPhase] = []

        # Question tracking
        self._answered_questions: Set[str] = set()
        self._skipped_questions: Set[str] = set()
        self._total_questions_asked: int = 0

        # Confidence tracking
        self._confidence_history: List[tuple[datetime, float]] = []

        # Snapshots for analytics
        self._snapshots: List[ProgressSnapshot] = []

    # =========================================================================
    # PUBLIC API - Lifecycle
    # =========================================================================

    def start_interview(self) -> None:
        """Start the interview session."""
        if self._status == ProgressStatus.IN_PROGRESS:
            logger.warning("Interview already in progress")
            return

        self._started_at = datetime.now()
        self._status = ProgressStatus.IN_PROGRESS
        logger.info("Interview started")

    def complete_interview(self) -> None:
        """Mark interview as completed."""
        if self._current_phase:
            self.complete_phase()

        self._completed_at = datetime.now()
        self._status = ProgressStatus.COMPLETED
        logger.info(f"Interview completed in {self.elapsed_time}")

    def pause_interview(self) -> None:
        """Pause the interview."""
        self._status = ProgressStatus.PAUSED
        logger.info("Interview paused")

    def resume_interview(self) -> None:
        """Resume paused interview."""
        if self._status == ProgressStatus.PAUSED:
            self._status = ProgressStatus.IN_PROGRESS
            logger.info("Interview resumed")

    @property
    def status(self) -> ProgressStatus:
        """Get current status."""
        return self._status

    @property
    def is_active(self) -> bool:
        """Check if interview is active."""
        return self._status == ProgressStatus.IN_PROGRESS

    @property
    def is_completed(self) -> bool:
        """Check if interview is completed."""
        return self._status == ProgressStatus.COMPLETED

    @property
    def elapsed_time(self) -> timedelta:
        """Get elapsed time since interview started."""
        if not self._started_at:
            return timedelta(0)

        end = self._completed_at or datetime.now()
        return end - self._started_at

    # =========================================================================
    # PUBLIC API - Phase Management
    # =========================================================================

    def start_phase(
        self,
        phase: InterviewPhase,
        initial_confidence: float = 0.0,
    ) -> None:
        """
        Start a new interview phase.

        Args:
            phase: Phase to start
            initial_confidence: Confidence at phase start
        """
        # Complete previous phase if active
        if self._current_phase and not self._phase_metrics.get(
            self._current_phase, PhaseMetrics(phase=self._current_phase)
        ).is_completed:
            self.complete_phase()

        # Initialize phase metrics
        metrics = PhaseMetrics(
            phase=phase,
            started_at=datetime.now(),
            confidence_start=initial_confidence,
        )
        self._phase_metrics[phase] = metrics
        self._current_phase = phase

        # Track phase order
        if phase not in self._phase_order:
            self._phase_order.append(phase)

        logger.info(f"Started phase: {phase.value}")

    def complete_phase(
        self,
        final_confidence: Optional[float] = None,
    ) -> None:
        """
        Complete the current phase.

        Args:
            final_confidence: Confidence at phase end
        """
        if not self._current_phase:
            return

        metrics = self._phase_metrics.get(self._current_phase)
        if metrics:
            metrics.completed_at = datetime.now()
            if final_confidence is not None:
                metrics.confidence_end = final_confidence

            logger.info(
                f"Completed phase: {self._current_phase.value} "
                f"(duration: {metrics.duration})"
            )

    @property
    def current_phase(self) -> Optional[InterviewPhase]:
        """Get current phase."""
        return self._current_phase

    def get_phase_metrics(self, phase: InterviewPhase) -> Optional[PhaseMetrics]:
        """Get metrics for a specific phase."""
        return self._phase_metrics.get(phase)

    # =========================================================================
    # PUBLIC API - Question Tracking
    # =========================================================================

    def record_question_asked(self) -> None:
        """Record that a question was asked."""
        self._total_questions_asked += 1

        if self._current_phase:
            metrics = self._phase_metrics.get(self._current_phase)
            if metrics:
                metrics.questions_asked += 1

    def record_question_answered(
        self,
        question_id: str,
        confidence_after: Optional[float] = None,
    ) -> None:
        """
        Record that a question was answered.

        Args:
            question_id: ID of the answered question
            confidence_after: Confidence after answer
        """
        self._answered_questions.add(question_id)

        if self._current_phase:
            metrics = self._phase_metrics.get(self._current_phase)
            if metrics:
                metrics.questions_answered += 1
                if confidence_after is not None:
                    metrics.confidence_end = confidence_after

        # Track confidence evolution
        if confidence_after is not None:
            self._confidence_history.append((datetime.now(), confidence_after))

    def record_question_skipped(self, question_id: str) -> None:
        """Record that a question was skipped."""
        self._skipped_questions.add(question_id)

        if self._current_phase:
            metrics = self._phase_metrics.get(self._current_phase)
            if metrics:
                metrics.questions_skipped += 1

    @property
    def questions_answered(self) -> int:
        """Get total questions answered."""
        return len(self._answered_questions)

    @property
    def questions_skipped(self) -> int:
        """Get total questions skipped."""
        return len(self._skipped_questions)

    @property
    def questions_total(self) -> int:
        """Get total questions asked."""
        return self._total_questions_asked

    # =========================================================================
    # PUBLIC API - Progress Calculation
    # =========================================================================

    def get_overall_progress(self) -> float:
        """
        Calculate overall interview progress (0.0 - 1.0).

        Based on weighted phase completion.
        """
        if self._status == ProgressStatus.COMPLETED:
            return 1.0

        if self._status == ProgressStatus.NOT_STARTED:
            return 0.0

        total_progress = 0.0

        for phase, weight in self.PHASE_WEIGHTS.items():
            metrics = self._phase_metrics.get(phase)

            if metrics and metrics.is_completed:
                total_progress += weight
            elif phase == self._current_phase and metrics:
                # Partial credit for current phase
                phase_progress = self.get_phase_progress()
                total_progress += weight * phase_progress

        return min(total_progress, 1.0)

    def get_phase_progress(self) -> float:
        """
        Calculate current phase progress (0.0 - 1.0).

        Based on questions answered vs expected.
        """
        if not self._current_phase:
            return 0.0

        expected = self.EXPECTED_QUESTIONS.get(self._current_phase, 1)
        metrics = self._phase_metrics.get(self._current_phase)

        if not metrics or expected == 0:
            return 0.0

        # Progress based on questions answered
        answered = metrics.questions_answered
        return min(answered / expected, 1.0)

    def get_current_confidence(self) -> float:
        """Get the latest confidence value."""
        if not self._confidence_history:
            return 0.0
        return self._confidence_history[-1][1]

    def get_estimated_remaining(self) -> Optional[timedelta]:
        """
        Estimate remaining time based on current pace.

        Returns:
            Estimated remaining time or None if can't estimate
        """
        progress = self.get_overall_progress()
        elapsed = self.elapsed_time

        if progress <= 0.05:  # Not enough data
            return None

        # Estimate total time based on current pace
        estimated_total = elapsed / progress
        remaining = estimated_total - elapsed

        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    # =========================================================================
    # PUBLIC API - Display Formatting
    # =========================================================================

    def get_progress_display(self) -> ProgressDisplay:
        """
        Get rich progress display data.

        Returns:
            ProgressDisplay with formatted strings for UI
        """
        # Calculate values
        overall = self.get_overall_progress()
        phase = self._current_phase or InterviewPhase.BRIEF_INGESTION
        phase_name, phase_emoji = self.PHASE_INFO.get(
            phase, ("Bilinmiyor", "❓")
        )

        # Progress bar (16 chars)
        filled = int(overall * 16)
        bar = "█" * filled + "░" * (16 - filled)

        # Percentage
        percentage = f"{int(overall * 100)}%"

        # Steps
        current_step = self._phase_order.index(phase) + 1 if phase in self._phase_order else 1
        total_steps = 8  # Total phases

        # Time formatting
        elapsed = self.elapsed_time
        elapsed_fmt = self._format_duration(elapsed)

        remaining = self.get_estimated_remaining()
        remaining_fmt = self._format_duration(remaining) if remaining else "Hesaplanıyor..."

        # Confidence indicator
        confidence = self.get_current_confidence()
        if confidence < 0.4:
            conf_indicator = self.CONFIDENCE_INDICATORS["low"]
        elif confidence < 0.7:
            conf_indicator = self.CONFIDENCE_INDICATORS["medium"]
        else:
            conf_indicator = self.CONFIDENCE_INDICATORS["high"]

        return ProgressDisplay(
            progress_bar=bar,
            percentage=percentage,
            current_step=current_step,
            total_steps=total_steps,
            phase_name=phase_name,
            phase_emoji=phase_emoji,
            category_tip=self.PHASE_TIPS.get(phase, ""),
            elapsed_formatted=elapsed_fmt,
            remaining_formatted=remaining_fmt,
            confidence_indicator=conf_indicator,
        )

    def get_progress_bar_string(self) -> str:
        """Get formatted progress bar string."""
        display = self.get_progress_display()
        return f"{display.progress_bar} {display.percentage}"

    def get_status_string(self) -> str:
        """Get formatted status string."""
        display = self.get_progress_display()
        return (
            f"{display.phase_emoji} {display.phase_name} "
            f"({display.current_step}/{display.total_steps}) "
            f"| {display.progress_bar} {display.percentage}"
        )

    # =========================================================================
    # PUBLIC API - Snapshot & Analytics
    # =========================================================================

    def take_snapshot(self) -> ProgressSnapshot:
        """
        Take a point-in-time snapshot.

        Returns:
            ProgressSnapshot for analytics
        """
        snapshot = ProgressSnapshot(
            timestamp=datetime.now(),
            current_phase=self._current_phase or InterviewPhase.BRIEF_INGESTION,
            overall_progress=self.get_overall_progress(),
            phase_progress=self.get_phase_progress(),
            overall_confidence=self.get_current_confidence(),
            questions_total=self._total_questions_asked,
            questions_answered=len(self._answered_questions),
            elapsed_time=self.elapsed_time,
            estimated_remaining=self.get_estimated_remaining(),
        )

        self._snapshots.append(snapshot)
        return snapshot

    def get_analytics_summary(self) -> Dict:
        """
        Get comprehensive analytics summary.

        Returns:
            Dictionary with all tracking data
        """
        return {
            "status": self._status.value,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "completed_at": self._completed_at.isoformat() if self._completed_at else None,
            "elapsed_seconds": self.elapsed_time.total_seconds(),
            "overall_progress": round(self.get_overall_progress(), 2),
            "current_phase": self._current_phase.value if self._current_phase else None,
            "phases_completed": [
                phase.value for phase, metrics in self._phase_metrics.items()
                if metrics.is_completed
            ],
            "questions": {
                "total_asked": self._total_questions_asked,
                "answered": len(self._answered_questions),
                "skipped": len(self._skipped_questions),
            },
            "confidence": {
                "current": round(self.get_current_confidence(), 2),
                "history_length": len(self._confidence_history),
            },
            "phase_metrics": {
                phase.value: metrics.to_dict()
                for phase, metrics in self._phase_metrics.items()
            },
            "snapshots_count": len(self._snapshots),
        }

    def get_confidence_evolution(self) -> List[Dict]:
        """
        Get confidence evolution over time.

        Returns:
            List of {timestamp, confidence} dicts
        """
        return [
            {"timestamp": ts.isoformat(), "confidence": round(conf, 2)}
            for ts, conf in self._confidence_history
        ]

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _format_duration(self, duration: Optional[timedelta]) -> str:
        """Format timedelta as human-readable string."""
        if not duration:
            return "0s"

        total_seconds = int(duration.total_seconds())

        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_progress_tracker() -> ProgressTracker:
    """
    Create a new ProgressTracker instance.

    Returns:
        Configured ProgressTracker
    """
    return ProgressTracker()


def track_interview_progress(
    phases: List[InterviewPhase],
) -> ProgressTracker:
    """
    Create and initialize a tracker for specific phases.

    Args:
        phases: List of phases to track

    Returns:
        Initialized ProgressTracker
    """
    tracker = ProgressTracker()
    tracker.start_interview()

    if phases:
        tracker.start_phase(phases[0])

    return tracker
