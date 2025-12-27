"""
MAESTRO Interview State Machine - Phase 3

Pure Python state machine for interview phase management.
No external dependencies (transitions library not used).

States (InterviewPhase):
- BRIEF_INGESTION: Initial brief parsing
- SOUL_EXTRACTION: Extracting project soul
- CONTEXT_GATHERING: Collecting additional context
- DEEP_DIVE: Detailed questions about specifics
- VISUAL_EXPLORATION: Visual preferences deep-dive
- VALIDATION: Confirming gathered information
- SYNTHESIS: Creating final design decision
- COMPLETE: Interview finished

State Transition Diagram:
    BRIEF_INGESTION → SOUL_EXTRACTION → CONTEXT_GATHERING
                                              ↓
              ┌──────────────────────────────DEEP_DIVE
              │                                ↓
              │                     VISUAL_EXPLORATION
              │                                ↓
              └─────────────────────→ VALIDATION
                                          ↓
                                      SYNTHESIS
                                          ↓
                                      COMPLETE

Usage:
    >>> from gemini_mcp.maestro.interview.state_machine import InterviewStateMachine
    >>> machine = InterviewStateMachine()
    >>> machine.start()
    >>> machine.advance()  # BRIEF_INGESTION → SOUL_EXTRACTION
    >>> machine.can_transition_to(InterviewPhase.DEEP_DIVE)
    False  # Not allowed yet
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Callable, ClassVar, Dict, List, Optional, Set

from gemini_mcp.maestro.models.soul import InterviewPhase

if TYPE_CHECKING:
    from gemini_mcp.maestro.models.soul import ProjectSoul

logger = logging.getLogger(__name__)


class TransitionResult(str, Enum):
    """Result of a state transition attempt."""
    SUCCESS = "success"
    INVALID_TRANSITION = "invalid_transition"
    GUARD_FAILED = "guard_failed"
    ALREADY_IN_STATE = "already_in_state"


@dataclass
class StateEvent:
    """
    Event emitted when state changes.

    Contains information about the transition for logging and analytics.
    """
    from_state: InterviewPhase
    to_state: InterviewPhase
    timestamp: datetime = field(default_factory=datetime.now)
    trigger: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for logging."""
        return {
            "from": self.from_state.value,
            "to": self.to_state.value,
            "timestamp": self.timestamp.isoformat(),
            "trigger": self.trigger,
            "metadata": self.metadata,
        }


@dataclass
class TransitionAttempt:
    """
    Record of a transition attempt.

    Used for debugging and analytics.
    """
    from_state: InterviewPhase
    to_state: InterviewPhase
    result: TransitionResult
    timestamp: datetime = field(default_factory=datetime.now)
    reason: Optional[str] = None


# Type alias for guard functions
GuardFunc = Callable[["InterviewStateMachine"], bool]


class InterviewStateMachine:
    """
    Pure Python state machine for interview phases.

    Features:
    - Declarative transition definitions
    - Guard conditions for conditional transitions
    - Transition history tracking
    - Event callbacks for state changes
    - Shortcut transitions for common patterns

    Example:
        >>> machine = InterviewStateMachine()
        >>> machine.start()
        >>> print(machine.current_state)
        InterviewPhase.BRIEF_INGESTION
        >>>
        >>> # Advance through phases
        >>> machine.advance()
        >>> print(machine.current_state)
        InterviewPhase.SOUL_EXTRACTION
        >>>
        >>> # Skip to specific phase
        >>> machine.transition_to(InterviewPhase.VALIDATION)
        TransitionResult.SUCCESS
    """

    # =========================================================================
    # STATE TRANSITION DEFINITIONS
    # =========================================================================

    # Valid transitions: from_state → [allowed_to_states]
    TRANSITIONS: ClassVar[Dict[InterviewPhase, List[InterviewPhase]]] = {
        InterviewPhase.BRIEF_INGESTION: [InterviewPhase.SOUL_EXTRACTION],
        InterviewPhase.SOUL_EXTRACTION: [InterviewPhase.CONTEXT_GATHERING],
        InterviewPhase.CONTEXT_GATHERING: [
            InterviewPhase.DEEP_DIVE,
            InterviewPhase.VALIDATION,  # Skip DEEP_DIVE if enough info
        ],
        InterviewPhase.DEEP_DIVE: [
            InterviewPhase.VISUAL_EXPLORATION,
            InterviewPhase.VALIDATION,  # Skip VISUAL if not needed
        ],
        InterviewPhase.VISUAL_EXPLORATION: [InterviewPhase.VALIDATION],
        InterviewPhase.VALIDATION: [
            InterviewPhase.SYNTHESIS,
            InterviewPhase.DEEP_DIVE,  # Go back if validation fails
        ],
        InterviewPhase.SYNTHESIS: [InterviewPhase.COMPLETE],
        InterviewPhase.COMPLETE: [],  # Terminal state
    }

    # Primary (default) next state for each phase
    PRIMARY_NEXT: ClassVar[Dict[InterviewPhase, Optional[InterviewPhase]]] = {
        InterviewPhase.BRIEF_INGESTION: InterviewPhase.SOUL_EXTRACTION,
        InterviewPhase.SOUL_EXTRACTION: InterviewPhase.CONTEXT_GATHERING,
        InterviewPhase.CONTEXT_GATHERING: InterviewPhase.DEEP_DIVE,
        InterviewPhase.DEEP_DIVE: InterviewPhase.VISUAL_EXPLORATION,
        InterviewPhase.VISUAL_EXPLORATION: InterviewPhase.VALIDATION,
        InterviewPhase.VALIDATION: InterviewPhase.SYNTHESIS,
        InterviewPhase.SYNTHESIS: InterviewPhase.COMPLETE,
        InterviewPhase.COMPLETE: None,
    }

    # Phase progress values (0.0 - 1.0)
    PHASE_PROGRESS: ClassVar[Dict[InterviewPhase, float]] = {
        InterviewPhase.BRIEF_INGESTION: 0.0,
        InterviewPhase.SOUL_EXTRACTION: 0.1,
        InterviewPhase.CONTEXT_GATHERING: 0.3,
        InterviewPhase.DEEP_DIVE: 0.5,
        InterviewPhase.VISUAL_EXPLORATION: 0.6,
        InterviewPhase.VALIDATION: 0.8,
        InterviewPhase.SYNTHESIS: 0.9,
        InterviewPhase.COMPLETE: 1.0,
    }

    def __init__(
        self,
        initial_state: Optional[InterviewPhase] = None,
        soul: Optional["ProjectSoul"] = None,
    ) -> None:
        """
        Initialize the state machine.

        Args:
            initial_state: Starting state (default: BRIEF_INGESTION)
            soul: ProjectSoul for context-aware transitions
        """
        self._state = initial_state or InterviewPhase.BRIEF_INGESTION
        self._soul = soul
        self._started = False

        # History
        self._history: List[StateEvent] = []
        self._attempts: List[TransitionAttempt] = []

        # Callbacks
        self._on_enter_callbacks: Dict[InterviewPhase, List[Callable]] = {}
        self._on_exit_callbacks: Dict[InterviewPhase, List[Callable]] = {}
        self._on_any_transition: List[Callable[[StateEvent], None]] = []

        # Guards
        self._guards: Dict[tuple[InterviewPhase, InterviewPhase], List[GuardFunc]] = {}

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    @property
    def current_state(self) -> InterviewPhase:
        """Get the current state."""
        return self._state

    @property
    def is_started(self) -> bool:
        """Check if the state machine has been started."""
        return self._started

    @property
    def is_complete(self) -> bool:
        """Check if the interview is complete."""
        return self._state == InterviewPhase.COMPLETE

    @property
    def progress(self) -> float:
        """Get the current progress (0.0 - 1.0)."""
        return self.PHASE_PROGRESS.get(self._state, 0.0)

    @property
    def history(self) -> List[StateEvent]:
        """Get the transition history."""
        return list(self._history)

    def start(self) -> None:
        """Start the state machine."""
        if self._started:
            logger.warning("State machine already started")
            return

        self._started = True
        logger.info(f"State machine started in {self._state.value}")

    def advance(self) -> TransitionResult:
        """
        Advance to the primary next state.

        Returns:
            TransitionResult indicating success or failure
        """
        next_state = self.PRIMARY_NEXT.get(self._state)

        if next_state is None:
            return TransitionResult.INVALID_TRANSITION

        return self.transition_to(next_state)

    def transition_to(
        self,
        target: InterviewPhase,
        trigger: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> TransitionResult:
        """
        Attempt to transition to a target state.

        Args:
            target: Target state to transition to
            trigger: Optional trigger name for logging
            metadata: Optional metadata for the transition

        Returns:
            TransitionResult indicating success or failure
        """
        # Check if already in target state
        if self._state == target:
            self._record_attempt(target, TransitionResult.ALREADY_IN_STATE)
            return TransitionResult.ALREADY_IN_STATE

        # Check if transition is valid
        if not self.can_transition_to(target):
            self._record_attempt(target, TransitionResult.INVALID_TRANSITION)
            logger.warning(
                f"Invalid transition: {self._state.value} → {target.value}"
            )
            return TransitionResult.INVALID_TRANSITION

        # Check guards
        guard_result, guard_reason = self._check_guards(target)
        if not guard_result:
            self._record_attempt(
                target, TransitionResult.GUARD_FAILED, guard_reason
            )
            logger.warning(
                f"Guard failed for {self._state.value} → {target.value}: {guard_reason}"
            )
            return TransitionResult.GUARD_FAILED

        # Perform transition
        old_state = self._state
        self._execute_transition(old_state, target, trigger, metadata or {})

        return TransitionResult.SUCCESS

    def can_transition_to(self, target: InterviewPhase) -> bool:
        """
        Check if transition to target is allowed.

        Args:
            target: Target state to check

        Returns:
            True if transition is allowed
        """
        allowed = self.TRANSITIONS.get(self._state, [])
        return target in allowed

    def get_available_transitions(self) -> List[InterviewPhase]:
        """
        Get list of states that can be transitioned to from current state.

        Returns:
            List of available target states
        """
        return list(self.TRANSITIONS.get(self._state, []))

    def reset(self, to_state: Optional[InterviewPhase] = None) -> None:
        """
        Reset the state machine.

        Args:
            to_state: State to reset to (default: BRIEF_INGESTION)
        """
        self._state = to_state or InterviewPhase.BRIEF_INGESTION
        self._started = False
        self._history.clear()
        self._attempts.clear()
        logger.info(f"State machine reset to {self._state.value}")

    def skip_to_validation(self) -> TransitionResult:
        """
        Shortcut to skip directly to VALIDATION phase.

        Useful when enough information is gathered early.

        Returns:
            TransitionResult
        """
        # Build path to VALIDATION
        if self._state == InterviewPhase.VALIDATION:
            return TransitionResult.ALREADY_IN_STATE

        # Check if we can skip
        if self._state in [
            InterviewPhase.CONTEXT_GATHERING,
            InterviewPhase.DEEP_DIVE,
            InterviewPhase.VISUAL_EXPLORATION,
        ]:
            if self.can_transition_to(InterviewPhase.VALIDATION):
                return self.transition_to(
                    InterviewPhase.VALIDATION,
                    trigger="skip_to_validation",
                )

        return TransitionResult.INVALID_TRANSITION

    def go_back_to_deep_dive(self) -> TransitionResult:
        """
        Go back to DEEP_DIVE from VALIDATION.

        Useful when validation reveals missing information.

        Returns:
            TransitionResult
        """
        if self._state != InterviewPhase.VALIDATION:
            return TransitionResult.INVALID_TRANSITION

        return self.transition_to(
            InterviewPhase.DEEP_DIVE,
            trigger="go_back",
            metadata={"reason": "validation_failed"},
        )

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def on_enter(self, state: InterviewPhase, callback: Callable) -> None:
        """
        Register a callback for entering a state.

        Args:
            state: State to register callback for
            callback: Function to call when entering state
        """
        if state not in self._on_enter_callbacks:
            self._on_enter_callbacks[state] = []
        self._on_enter_callbacks[state].append(callback)

    def on_exit(self, state: InterviewPhase, callback: Callable) -> None:
        """
        Register a callback for exiting a state.

        Args:
            state: State to register callback for
            callback: Function to call when exiting state
        """
        if state not in self._on_exit_callbacks:
            self._on_exit_callbacks[state] = []
        self._on_exit_callbacks[state].append(callback)

    def on_transition(self, callback: Callable[[StateEvent], None]) -> None:
        """
        Register a callback for any state transition.

        Args:
            callback: Function to call on any transition
        """
        self._on_any_transition.append(callback)

    # =========================================================================
    # GUARDS
    # =========================================================================

    def add_guard(
        self,
        from_state: InterviewPhase,
        to_state: InterviewPhase,
        guard: GuardFunc,
    ) -> None:
        """
        Add a guard condition for a transition.

        Guards are functions that receive the state machine and return
        True if the transition should be allowed.

        Args:
            from_state: Source state
            to_state: Target state
            guard: Guard function
        """
        key = (from_state, to_state)
        if key not in self._guards:
            self._guards[key] = []
        self._guards[key].append(guard)

    def add_confidence_guard(
        self,
        from_state: InterviewPhase,
        to_state: InterviewPhase,
        min_confidence: float,
    ) -> None:
        """
        Add a guard that requires minimum confidence score.

        Args:
            from_state: Source state
            to_state: Target state
            min_confidence: Minimum confidence required (0.0 - 1.0)
        """
        def guard(machine: InterviewStateMachine) -> bool:
            if machine._soul is None:
                return True  # No soul = no confidence check
            return getattr(machine._soul, 'overall_confidence', 0.0) >= min_confidence

        self.add_guard(from_state, to_state, guard)

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _execute_transition(
        self,
        from_state: InterviewPhase,
        to_state: InterviewPhase,
        trigger: Optional[str],
        metadata: Dict,
    ) -> None:
        """Execute the state transition."""
        # Exit callbacks
        for callback in self._on_exit_callbacks.get(from_state, []):
            try:
                callback()
            except Exception as e:
                logger.error(f"Exit callback error: {e}")

        # Update state
        self._state = to_state

        # Create event
        event = StateEvent(
            from_state=from_state,
            to_state=to_state,
            trigger=trigger,
            metadata=metadata,
        )
        self._history.append(event)

        # Log transition
        logger.info(
            f"Transition: {from_state.value} → {to_state.value}"
            + (f" (trigger: {trigger})" if trigger else "")
        )

        # Enter callbacks
        for callback in self._on_enter_callbacks.get(to_state, []):
            try:
                callback()
            except Exception as e:
                logger.error(f"Enter callback error: {e}")

        # Global callbacks
        for callback in self._on_any_transition:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Transition callback error: {e}")

    def _check_guards(
        self,
        target: InterviewPhase,
    ) -> tuple[bool, Optional[str]]:
        """Check all guards for a transition."""
        key = (self._state, target)
        guards = self._guards.get(key, [])

        for guard in guards:
            try:
                if not guard(self):
                    return False, f"Guard {guard.__name__} failed"
            except Exception as e:
                logger.error(f"Guard error: {e}")
                return False, f"Guard error: {e}"

        return True, None

    def _record_attempt(
        self,
        target: InterviewPhase,
        result: TransitionResult,
        reason: Optional[str] = None,
    ) -> None:
        """Record a transition attempt."""
        attempt = TransitionAttempt(
            from_state=self._state,
            to_state=target,
            result=result,
            reason=reason,
        )
        self._attempts.append(attempt)

    def set_soul(self, soul: "ProjectSoul") -> None:
        """
        Set the ProjectSoul for context-aware transitions.

        Args:
            soul: ProjectSoul instance
        """
        self._soul = soul


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_interview_state_machine(
    soul: Optional["ProjectSoul"] = None,
    with_confidence_guards: bool = True,
) -> InterviewStateMachine:
    """
    Create a configured InterviewStateMachine.

    Args:
        soul: ProjectSoul for context
        with_confidence_guards: Add default confidence guards

    Returns:
        Configured InterviewStateMachine
    """
    machine = InterviewStateMachine(soul=soul)

    if with_confidence_guards and soul:
        # Add confidence guards
        machine.add_confidence_guard(
            InterviewPhase.CONTEXT_GATHERING,
            InterviewPhase.VALIDATION,
            min_confidence=0.8,  # Need high confidence to skip DEEP_DIVE
        )
        machine.add_confidence_guard(
            InterviewPhase.DEEP_DIVE,
            InterviewPhase.VALIDATION,
            min_confidence=0.7,  # Need medium confidence to skip VISUAL
        )

    return machine
