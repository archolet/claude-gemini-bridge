"""
MAESTRO v2 Soul-Aware Session

Enhanced session management with ProjectSoul context.
Wraps MaestroSession to add intelligent interview capabilities.

Session Lifecycle:
1. CREATE: SoulAwareSession created with optional design_brief
2. EXTRACT: Soul extracted from brief (if provided)
3. INTERVIEW: Dynamic questions based on soul gaps
4. DECIDE: Decision made with soul context
5. EXECUTE: Design generated with soul parameters
6. COMPLETE: Session archived

Usage:
    >>> from gemini_mcp.maestro.v2 import SoulAwareSession, SessionState
    >>> session = SoulAwareSession.create(
    ...     session_id="maestro_abc123",
    ...     design_brief="Modern fintech dashboard for Turkish market"
    ... )
    >>> if session.has_soul:
    ...     print(session.soul.project_name)
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from gemini_mcp.maestro.models import (
    Answer,
    ContextData,
    InterviewState,
    MaestroSession,
    MaestroStatus,
    Question,
)
from gemini_mcp.maestro.models.soul import ProjectSoul
from gemini_mcp.maestro.models.gap import GapInfo

if TYPE_CHECKING:
    from gemini_mcp.maestro.soul import SoulExtractor, ExtractionResult

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """
    State machine for SoulAwareSession.

    Extends MaestroStatus with soul-specific states.
    Uses different name to avoid collision with existing InterviewState dataclass.
    """

    # Initial states
    CREATED = "created"  # Session just created
    EXTRACTING_SOUL = "extracting_soul"  # Extracting ProjectSoul from brief

    # Interview states (parallel to MaestroStatus)
    GATHERING_CONTEXT = "gathering_context"  # Asking gap-based questions
    DEEP_DIVE = "deep_dive"  # Detailed exploration
    VALIDATING = "validating"  # Confirming gathered info

    # Decision states
    SYNTHESIZING = "synthesizing"  # Building final decision
    DECIDING = "deciding"  # Making mode/params decision

    # Execution states
    EXECUTING = "executing"  # Running design tool
    COMPLETE = "complete"  # Session finished successfully

    # Error states
    FALLBACK = "fallback"  # Fell back to v1
    ABORTED = "aborted"  # User or system aborted
    ERROR = "error"  # Unrecoverable error


class InterviewPhase(Enum):
    """
    Phases of the intelligent interview process.

    Maps to state machine transitions for flow control.
    """

    BRIEF_INGESTION = "brief_ingestion"
    SOUL_EXTRACTION = "soul_extraction"
    CONTEXT_GATHERING = "context_gathering"
    DEEP_DIVE = "deep_dive"
    VISUAL_EXPLORATION = "visual_exploration"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"
    COMPLETE = "complete"


@dataclass
class PhaseTransition:
    """Records a state/phase transition."""

    from_state: SessionState
    to_state: SessionState
    timestamp: float = field(default_factory=time.time)
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "metadata": self.metadata,
        }


@dataclass
class SoulAwareSession:
    """
    Enhanced MAESTRO session with ProjectSoul context.

    Wraps MaestroSession to add:
    - ProjectSoul for intelligent design understanding
    - Dynamic gap-based questioning
    - Phase-based interview flow
    - Soul evolution tracking

    Attributes:
        session_id: Unique session identifier
        legacy_session: Wrapped MaestroSession for compatibility
        soul: Extracted ProjectSoul (if available)
        state: Current session state
        phase: Current interview phase
        design_brief: Original user brief
        transitions: History of state transitions
        gap_resolutions: Track resolved gaps
        questions_from_soul: Dynamic questions generated from soul gaps
    """

    session_id: str
    legacy_session: MaestroSession
    soul: Optional[ProjectSoul] = None
    state: SessionState = SessionState.CREATED
    phase: InterviewPhase = InterviewPhase.BRIEF_INGESTION
    design_brief: Optional[str] = None
    existing_html: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    # Tracking
    transitions: List[PhaseTransition] = field(default_factory=list)
    gap_resolutions: Dict[str, str] = field(default_factory=dict)  # gap_id → answer
    questions_from_soul: List[Question] = field(default_factory=list)
    soul_evolution: List[Dict[str, Any]] = field(default_factory=list)  # Soul snapshots

    # Metrics
    extraction_time_ms: float = 0.0
    total_questions_asked: int = 0
    gaps_resolved: int = 0

    @classmethod
    def create(
        cls,
        session_id: Optional[str] = None,
        design_brief: Optional[str] = None,
        existing_html: Optional[str] = None,
        project_context: str = "",
    ) -> "SoulAwareSession":
        """
        Create a new SoulAwareSession.

        Args:
            session_id: Optional session ID (auto-generated if not provided)
            design_brief: Optional design brief for soul extraction
            existing_html: Optional existing HTML for context
            project_context: Optional project description

        Returns:
            New SoulAwareSession instance
        """
        if session_id is None:
            session_id = f"maestro_v2_{uuid.uuid4().hex[:12]}"

        # Create legacy session for compatibility
        context_data = ContextData(
            previous_html=existing_html,
            project_context=project_context,
        )

        legacy_session = MaestroSession(
            session_id=session_id,
            state=InterviewState(status=MaestroStatus.INTERVIEWING),
            context=context_data,
        )

        session = cls(
            session_id=session_id,
            legacy_session=legacy_session,
            design_brief=design_brief,
            existing_html=existing_html,
        )

        logger.info(f"[SoulAwareSession] Created: {session_id}")

        return session

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def has_soul(self) -> bool:
        """Check if session has an extracted soul."""
        return self.soul is not None

    @property
    def has_brief(self) -> bool:
        """Check if session has a design brief."""
        return bool(self.design_brief)

    @property
    def is_v2_active(self) -> bool:
        """Check if v2 features are active (has soul, not in fallback)."""
        return self.has_soul and self.state != SessionState.FALLBACK

    @property
    def confidence(self) -> float:
        """Get overall confidence from soul."""
        if self.soul and self.soul.confidence_scores:
            return self.soul.confidence_scores.overall
        return 0.0

    @property
    def unresolved_gaps(self) -> List[GapInfo]:
        """Get list of unresolved gaps."""
        if not self.soul or not self.soul.identified_gaps:
            return []
        return [
            gap for gap in self.soul.identified_gaps
            if not gap.is_resolved
        ]

    @property
    def critical_gaps(self) -> List[GapInfo]:
        """Get list of critical unresolved gaps."""
        from gemini_mcp.maestro.models.gap import GapSeverity
        return [
            gap for gap in self.unresolved_gaps
            if gap.severity == GapSeverity.CRITICAL
        ]

    @property
    def duration_seconds(self) -> float:
        """Get session duration in seconds."""
        return time.time() - self.created_at

    @property
    def progress(self) -> float:
        """
        Calculate interview progress (0.0 to 1.0).

        Based on:
        - Phase progression (40%)
        - Gap resolution (40%)
        - Question completion (20%)
        """
        phase_weights = {
            InterviewPhase.BRIEF_INGESTION: 0.0,
            InterviewPhase.SOUL_EXTRACTION: 0.1,
            InterviewPhase.CONTEXT_GATHERING: 0.3,
            InterviewPhase.DEEP_DIVE: 0.5,
            InterviewPhase.VISUAL_EXPLORATION: 0.6,
            InterviewPhase.VALIDATION: 0.8,
            InterviewPhase.SYNTHESIS: 0.9,
            InterviewPhase.COMPLETE: 1.0,
        }

        phase_progress = phase_weights.get(self.phase, 0.0) * 0.4

        # Gap resolution progress
        gap_progress = 0.0
        if self.soul and self.soul.identified_gaps:
            total_gaps = len(self.soul.identified_gaps)
            if total_gaps > 0:
                gap_progress = (self.gaps_resolved / total_gaps) * 0.4

        # Question completion progress
        question_progress = 0.0
        if self.questions_from_soul:
            asked = self.total_questions_asked
            total = len(self.questions_from_soul)
            if total > 0:
                question_progress = min(1.0, asked / total) * 0.2

        return min(1.0, phase_progress + gap_progress + question_progress)

    # =========================================================================
    # STATE TRANSITIONS
    # =========================================================================

    def transition_to(
        self,
        new_state: SessionState,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Transition to a new session state.

        Args:
            new_state: Target state
            reason: Reason for transition
            metadata: Optional transition metadata
        """
        old_state = self.state

        # Record transition
        transition = PhaseTransition(
            from_state=old_state,
            to_state=new_state,
            reason=reason,
            metadata=metadata or {},
        )
        self.transitions.append(transition)

        # Update state
        self.state = new_state

        # Sync with legacy session status
        self._sync_legacy_status(new_state)

        logger.info(
            f"[SoulAwareSession] {self.session_id}: "
            f"{old_state.value} → {new_state.value} ({reason})"
        )

    def advance_phase(
        self,
        new_phase: InterviewPhase,
        reason: str = "",
    ) -> None:
        """
        Advance to a new interview phase.

        Args:
            new_phase: Target phase
            reason: Reason for advancement
        """
        old_phase = self.phase
        self.phase = new_phase

        logger.info(
            f"[SoulAwareSession] Phase: {old_phase.value} → {new_phase.value} ({reason})"
        )

    def _sync_legacy_status(self, new_state: SessionState) -> None:
        """Sync v2 state with legacy MaestroStatus."""
        state_mapping = {
            SessionState.CREATED: MaestroStatus.IDLE,
            SessionState.EXTRACTING_SOUL: MaestroStatus.ANALYZING,
            SessionState.GATHERING_CONTEXT: MaestroStatus.INTERVIEWING,
            SessionState.DEEP_DIVE: MaestroStatus.INTERVIEWING,
            SessionState.VALIDATING: MaestroStatus.AWAITING_ANSWER,
            SessionState.SYNTHESIZING: MaestroStatus.DECIDING,
            SessionState.DECIDING: MaestroStatus.CONFIRMING,
            SessionState.EXECUTING: MaestroStatus.EXECUTING,
            SessionState.COMPLETE: MaestroStatus.COMPLETE,
            SessionState.FALLBACK: MaestroStatus.INTERVIEWING,  # Fallback to static Q&A
            SessionState.ABORTED: MaestroStatus.ABORTED,
            SessionState.ERROR: MaestroStatus.ABORTED,
        }

        legacy_status = state_mapping.get(new_state, MaestroStatus.IDLE)
        self.legacy_session.state.status = legacy_status

    # =========================================================================
    # SOUL MANAGEMENT
    # =========================================================================

    def set_soul(self, soul: ProjectSoul, extraction_time_ms: float = 0.0) -> None:
        """
        Set the extracted ProjectSoul.

        Args:
            soul: Extracted ProjectSoul
            extraction_time_ms: Time taken for extraction
        """
        self.soul = soul
        self.extraction_time_ms = extraction_time_ms

        # Record initial soul state
        self._snapshot_soul("initial_extraction")

        # Update state
        self.transition_to(
            SessionState.GATHERING_CONTEXT,
            reason="Soul extracted successfully",
            metadata={"confidence": soul.confidence_scores.overall if soul.confidence_scores else 0.0},
        )
        self.advance_phase(InterviewPhase.CONTEXT_GATHERING, "Soul ready")

        logger.info(
            f"[SoulAwareSession] Soul set: {soul.project_name} "
            f"(confidence: {soul.confidence_scores.overall if soul.confidence_scores else 0:.2f})"
        )

    def update_soul(self, gap_id: str, answer: str) -> None:
        """
        Update soul with a gap resolution.

        Args:
            gap_id: ID of the resolved gap
            answer: User's answer
        """
        if not self.soul:
            return

        # Record resolution
        self.gap_resolutions[gap_id] = answer
        self.gaps_resolved += 1

        # Find and resolve the gap
        for gap in self.soul.identified_gaps:
            if gap.id == gap_id:
                gap.resolve(answer, source="user_input")
                break

        # Snapshot updated soul
        self._snapshot_soul(f"gap_resolved:{gap_id}")

        logger.debug(f"[SoulAwareSession] Gap resolved: {gap_id}")

    def _snapshot_soul(self, event: str) -> None:
        """Take a snapshot of current soul state."""
        if not self.soul:
            return

        snapshot = {
            "event": event,
            "timestamp": time.time(),
            "confidence": self.soul.confidence_scores.overall if self.soul.confidence_scores else 0,
            "gaps_remaining": len(self.unresolved_gaps),
        }
        self.soul_evolution.append(snapshot)

    # =========================================================================
    # QUESTION MANAGEMENT
    # =========================================================================

    def add_soul_questions(self, questions: List[Question]) -> None:
        """
        Add dynamic questions generated from soul gaps.

        Args:
            questions: List of gap-based questions
        """
        self.questions_from_soul.extend(questions)
        logger.debug(
            f"[SoulAwareSession] Added {len(questions)} soul-based questions"
        )

    def get_next_question(self) -> Optional[str]:
        """
        Get the next question to ask based on gaps.

        Returns:
            Question text or None if no more questions
        """
        if not self.soul:
            return None

        # Get priority gaps
        for gap in self.unresolved_gaps:
            if gap.suggested_question:
                return gap.suggested_question

        return None

    def record_question_asked(self) -> None:
        """Record that a question was asked."""
        self.total_questions_asked += 1

    # =========================================================================
    # FALLBACK
    # =========================================================================

    def enter_fallback(self, reason: str = "unknown") -> None:
        """
        Enter fallback mode (use v1 static questions).

        Args:
            reason: Reason for fallback
        """
        self.transition_to(
            SessionState.FALLBACK,
            reason=f"Fallback triggered: {reason}",
        )
        logger.warning(f"[SoulAwareSession] Entering fallback: {reason}")

    def is_fallback(self) -> bool:
        """Check if session is in fallback mode."""
        return self.state == SessionState.FALLBACK

    # =========================================================================
    # SERIALIZATION
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "phase": self.phase.value,
            "created_at": self.created_at,
            "design_brief": self.design_brief,
            "existing_html": self.existing_html is not None,
            "has_soul": self.has_soul,
            "soul": self.soul.model_dump() if self.soul else None,
            "confidence": self.confidence,
            "progress": self.progress,
            "metrics": {
                "extraction_time_ms": self.extraction_time_ms,
                "duration_seconds": self.duration_seconds,
                "total_questions_asked": self.total_questions_asked,
                "gaps_resolved": self.gaps_resolved,
                "unresolved_gaps": len(self.unresolved_gaps),
            },
            "transitions": [t.to_dict() for t in self.transitions],
            "legacy_session": self.legacy_session.to_dict(),
        }

    def to_summary(self) -> Dict[str, Any]:
        """Get a summary for display."""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "phase": self.phase.value,
            "project_name": self.soul.project_name if self.soul else "Unknown",
            "confidence": f"{self.confidence:.0%}",
            "progress": f"{self.progress:.0%}",
            "duration": f"{self.duration_seconds:.1f}s",
            "gaps_remaining": len(self.unresolved_gaps),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SoulAwareSession("
            f"id={self.session_id}, "
            f"state={self.state.value}, "
            f"phase={self.phase.value}, "
            f"has_soul={self.has_soul}, "
            f"progress={self.progress:.0%})"
        )
