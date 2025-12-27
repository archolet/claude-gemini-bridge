"""
MAESTRO State Transition Manager - Phase 3

Manages interview state transitions with intelligent decision-making.
Acts as a bridge between the state machine and business logic.

Key Responsibilities:
1. Determines when to trigger state transitions
2. Evaluates transition conditions based on answers and gaps
3. Coordinates with DynamicQuestionGenerator for question availability
4. Manages retry logic and fallback transitions

Usage:
    >>> from gemini_mcp.maestro.interview.transitions import StateTransitionManager
    >>> manager = StateTransitionManager(state_machine, question_generator)
    >>> manager.evaluate_and_transition(soul, gaps)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Callable, ClassVar, Dict, List, Optional, Set

from gemini_mcp.maestro.models.soul import InterviewPhase
from gemini_mcp.maestro.models.gap import GapAnalysis, GapSeverity
from gemini_mcp.maestro.interview.state_machine import (
    InterviewStateMachine,
    TransitionResult,
)

if TYPE_CHECKING:
    from gemini_mcp.maestro.models.soul import ProjectSoul
    from gemini_mcp.maestro.questions.generator import (
        DynamicQuestionGenerator,
        GenerationContext,
    )

logger = logging.getLogger(__name__)


class TransitionTrigger(str, Enum):
    """
    What triggered the transition evaluation.

    Used for logging and analytics.
    """
    ANSWER_RECEIVED = "answer_received"
    TIMEOUT = "timeout"
    USER_SKIP = "user_skip"
    AUTO_ADVANCE = "auto_advance"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    GAP_RESOLVED = "gap_resolved"
    MANUAL = "manual"


@dataclass
class TransitionCondition:
    """
    A condition that must be met for a transition.

    Combines multiple factors into a single evaluable condition.
    """
    name: str
    description: str
    evaluator: Callable[["TransitionEvaluationContext"], bool]
    required: bool = True  # If False, condition is advisory only
    weight: float = 1.0  # For weighted evaluation

    def evaluate(self, context: "TransitionEvaluationContext") -> bool:
        """Evaluate the condition."""
        try:
            return self.evaluator(context)
        except Exception as e:
            logger.error(f"Condition evaluation error ({self.name}): {e}")
            return False


@dataclass
class TransitionEvaluationContext:
    """
    Context for evaluating transition conditions.

    Aggregates all information needed to decide on transitions.
    """
    soul: Optional["ProjectSoul"] = None
    gaps: Optional[GapAnalysis] = None
    questions_answered: int = 0
    questions_remaining: int = 0
    current_phase: Optional[InterviewPhase] = None
    confidence_score: float = 0.0
    critical_gaps_open: int = 0
    high_gaps_open: int = 0
    time_in_phase: float = 0.0  # seconds
    user_requested_skip: bool = False

    @classmethod
    def from_soul_and_gaps(
        cls,
        soul: Optional["ProjectSoul"],
        gaps: Optional[GapAnalysis],
        questions_answered: int = 0,
        questions_remaining: int = 0,
    ) -> "TransitionEvaluationContext":
        """Create context from soul and gaps."""
        return cls(
            soul=soul,
            gaps=gaps,
            questions_answered=questions_answered,
            questions_remaining=questions_remaining,
            current_phase=soul.current_phase if soul else None,
            confidence_score=soul.overall_confidence if soul else 0.0,
            critical_gaps_open=gaps.blocking_gaps if gaps else 0,
            high_gaps_open=len(gaps.high_gaps) if gaps else 0,
        )


@dataclass
class TransitionDecision:
    """
    Result of transition evaluation.

    Contains the decision and reasoning.
    """
    should_transition: bool
    target_phase: Optional[InterviewPhase]
    reason: str
    trigger: TransitionTrigger
    confidence: float = 1.0  # How confident we are in this decision
    fallback_phase: Optional[InterviewPhase] = None


class StateTransitionManager:
    """
    Manages intelligent state transitions.

    Evaluates complex conditions to determine when and where to
    transition the interview state machine.

    Features:
    - Multi-factor transition evaluation
    - Phase-specific transition rules
    - Confidence-based skip logic
    - Gap-aware advancement
    - Fallback handling

    Example:
        >>> manager = StateTransitionManager(machine, generator)
        >>> decision = manager.evaluate_transition(soul, gaps)
        >>> if decision.should_transition:
        ...     result = manager.execute_transition(decision)
    """

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    # Confidence thresholds for phase skipping
    SKIP_DEEP_DIVE_CONFIDENCE: ClassVar[float] = 0.85
    SKIP_VISUAL_CONFIDENCE: ClassVar[float] = 0.80
    VALIDATION_MIN_CONFIDENCE: ClassVar[float] = 0.70

    # Question thresholds
    MIN_QUESTIONS_PER_PHASE: ClassVar[Dict[InterviewPhase, int]] = {
        InterviewPhase.BRIEF_INGESTION: 0,  # Auto-advance
        InterviewPhase.SOUL_EXTRACTION: 0,  # Auto-advance
        InterviewPhase.CONTEXT_GATHERING: 2,
        InterviewPhase.DEEP_DIVE: 3,
        InterviewPhase.VISUAL_EXPLORATION: 2,
        InterviewPhase.VALIDATION: 1,
        InterviewPhase.SYNTHESIS: 0,  # Auto-advance
    }

    # Max time in phase before auto-advancing (seconds)
    MAX_TIME_PER_PHASE: ClassVar[Dict[InterviewPhase, float]] = {
        InterviewPhase.CONTEXT_GATHERING: 300.0,  # 5 minutes
        InterviewPhase.DEEP_DIVE: 600.0,  # 10 minutes
        InterviewPhase.VISUAL_EXPLORATION: 300.0,  # 5 minutes
        InterviewPhase.VALIDATION: 180.0,  # 3 minutes
    }

    def __init__(
        self,
        state_machine: InterviewStateMachine,
        question_generator: Optional["DynamicQuestionGenerator"] = None,
    ) -> None:
        """
        Initialize the transition manager.

        Args:
            state_machine: The interview state machine
            question_generator: Optional question generator for question awareness
        """
        self.machine = state_machine
        self.generator = question_generator

        # Phase entry timestamps for timeout tracking
        self._phase_entry_times: Dict[InterviewPhase, datetime] = {}

        # Transition conditions by source phase
        self._conditions = self._build_default_conditions()

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def evaluate_transition(
        self,
        soul: Optional["ProjectSoul"] = None,
        gaps: Optional[GapAnalysis] = None,
        trigger: TransitionTrigger = TransitionTrigger.AUTO_ADVANCE,
        generation_context: Optional["GenerationContext"] = None,
    ) -> TransitionDecision:
        """
        Evaluate whether a transition should occur.

        Args:
            soul: ProjectSoul for confidence info
            gaps: GapAnalysis for gap info
            trigger: What triggered this evaluation
            generation_context: Question generation context

        Returns:
            TransitionDecision with recommendation
        """
        current_phase = self.machine.current_state

        # Build evaluation context
        questions_answered = 0
        questions_remaining = 0
        if generation_context:
            questions_answered = generation_context.questions_asked
            questions_remaining = self.generator.get_remaining_count(
                generation_context
            ) if self.generator else 0

        context = TransitionEvaluationContext.from_soul_and_gaps(
            soul,
            gaps,
            questions_answered=questions_answered,
            questions_remaining=questions_remaining,
        )
        context.current_phase = current_phase
        context.user_requested_skip = trigger == TransitionTrigger.USER_SKIP

        # Calculate time in phase
        if current_phase in self._phase_entry_times:
            entry_time = self._phase_entry_times[current_phase]
            context.time_in_phase = (datetime.now() - entry_time).total_seconds()

        # Evaluate based on phase
        return self._evaluate_for_phase(current_phase, context, trigger)

    def execute_transition(
        self,
        decision: TransitionDecision,
    ) -> TransitionResult:
        """
        Execute a transition based on a decision.

        Args:
            decision: TransitionDecision to execute

        Returns:
            TransitionResult from the state machine
        """
        if not decision.should_transition or not decision.target_phase:
            return TransitionResult.INVALID_TRANSITION

        # Try primary target
        result = self.machine.transition_to(
            decision.target_phase,
            trigger=decision.trigger.value,
            metadata={"reason": decision.reason},
        )

        # If failed and we have a fallback, try that
        if result != TransitionResult.SUCCESS and decision.fallback_phase:
            logger.info(f"Primary transition failed, trying fallback")
            result = self.machine.transition_to(
                decision.fallback_phase,
                trigger=f"{decision.trigger.value}_fallback",
            )

        # Record phase entry time for new phase
        if result == TransitionResult.SUCCESS:
            self._phase_entry_times[self.machine.current_state] = datetime.now()

        return result

    def evaluate_and_transition(
        self,
        soul: Optional["ProjectSoul"] = None,
        gaps: Optional[GapAnalysis] = None,
        trigger: TransitionTrigger = TransitionTrigger.AUTO_ADVANCE,
        generation_context: Optional["GenerationContext"] = None,
    ) -> TransitionResult:
        """
        Convenience method to evaluate and execute in one call.

        Args:
            soul: ProjectSoul
            gaps: GapAnalysis
            trigger: Transition trigger
            generation_context: Question generation context

        Returns:
            TransitionResult
        """
        decision = self.evaluate_transition(
            soul, gaps, trigger, generation_context
        )
        if decision.should_transition:
            return self.execute_transition(decision)
        return TransitionResult.INVALID_TRANSITION

    def should_advance_phase(
        self,
        soul: Optional["ProjectSoul"] = None,
        gaps: Optional[GapAnalysis] = None,
    ) -> bool:
        """
        Quick check if we should advance phase.

        Args:
            soul: ProjectSoul
            gaps: GapAnalysis

        Returns:
            True if we should advance
        """
        decision = self.evaluate_transition(soul, gaps)
        return decision.should_transition

    def get_recommended_phase(
        self,
        soul: Optional["ProjectSoul"] = None,
        gaps: Optional[GapAnalysis] = None,
    ) -> Optional[InterviewPhase]:
        """
        Get recommended next phase without transitioning.

        Args:
            soul: ProjectSoul
            gaps: GapAnalysis

        Returns:
            Recommended phase or None
        """
        decision = self.evaluate_transition(soul, gaps)
        return decision.target_phase if decision.should_transition else None

    def force_advance(self) -> TransitionResult:
        """
        Force advancement to the next phase.

        Returns:
            TransitionResult
        """
        return self.machine.advance()

    def go_back(self) -> TransitionResult:
        """
        Go back to DEEP_DIVE from VALIDATION.

        Returns:
            TransitionResult
        """
        return self.machine.go_back_to_deep_dive()

    def skip_to_validation(self) -> TransitionResult:
        """
        Skip to VALIDATION phase.

        Returns:
            TransitionResult
        """
        return self.machine.skip_to_validation()

    # =========================================================================
    # PHASE-SPECIFIC EVALUATION
    # =========================================================================

    def _evaluate_for_phase(
        self,
        phase: InterviewPhase,
        context: TransitionEvaluationContext,
        trigger: TransitionTrigger,
    ) -> TransitionDecision:
        """Evaluate transition for a specific phase."""
        evaluators = {
            InterviewPhase.BRIEF_INGESTION: self._eval_brief_ingestion,
            InterviewPhase.SOUL_EXTRACTION: self._eval_soul_extraction,
            InterviewPhase.CONTEXT_GATHERING: self._eval_context_gathering,
            InterviewPhase.DEEP_DIVE: self._eval_deep_dive,
            InterviewPhase.VISUAL_EXPLORATION: self._eval_visual_exploration,
            InterviewPhase.VALIDATION: self._eval_validation,
            InterviewPhase.SYNTHESIS: self._eval_synthesis,
            InterviewPhase.COMPLETE: self._eval_complete,
        }

        evaluator = evaluators.get(phase, self._eval_default)
        return evaluator(context, trigger)

    def _eval_brief_ingestion(
        self,
        context: TransitionEvaluationContext,
        trigger: TransitionTrigger,
    ) -> TransitionDecision:
        """Brief ingestion is auto-advanced."""
        return TransitionDecision(
            should_transition=True,
            target_phase=InterviewPhase.SOUL_EXTRACTION,
            reason="Brief ingestion complete",
            trigger=TransitionTrigger.AUTO_ADVANCE,
            confidence=1.0,
        )

    def _eval_soul_extraction(
        self,
        context: TransitionEvaluationContext,
        trigger: TransitionTrigger,
    ) -> TransitionDecision:
        """Soul extraction is auto-advanced when soul is ready."""
        has_soul = context.soul is not None
        return TransitionDecision(
            should_transition=has_soul,
            target_phase=InterviewPhase.CONTEXT_GATHERING if has_soul else None,
            reason="Soul extracted" if has_soul else "Waiting for soul extraction",
            trigger=TransitionTrigger.AUTO_ADVANCE,
            confidence=1.0 if has_soul else 0.0,
        )

    def _eval_context_gathering(
        self,
        context: TransitionEvaluationContext,
        trigger: TransitionTrigger,
    ) -> TransitionDecision:
        """Context gathering can skip to validation or go to deep dive."""
        min_questions = self.MIN_QUESTIONS_PER_PHASE.get(
            InterviewPhase.CONTEXT_GATHERING, 2
        )

        # Check if user requested skip
        if context.user_requested_skip:
            return TransitionDecision(
                should_transition=True,
                target_phase=InterviewPhase.VALIDATION,
                reason="User requested skip",
                trigger=TransitionTrigger.USER_SKIP,
                confidence=0.8,
                fallback_phase=InterviewPhase.DEEP_DIVE,
            )

        # High confidence can skip deep dive
        if context.confidence_score >= self.SKIP_DEEP_DIVE_CONFIDENCE:
            return TransitionDecision(
                should_transition=True,
                target_phase=InterviewPhase.VALIDATION,
                reason=f"High confidence ({context.confidence_score:.2f}) - skipping deep dive",
                trigger=TransitionTrigger.CONFIDENCE_THRESHOLD,
                confidence=0.9,
            )

        # Normal: go to deep dive if enough questions answered
        if context.questions_answered >= min_questions:
            return TransitionDecision(
                should_transition=True,
                target_phase=InterviewPhase.DEEP_DIVE,
                reason=f"Minimum questions answered ({context.questions_answered})",
                trigger=trigger,
                confidence=0.9,
            )

        # No questions remaining
        if context.questions_remaining == 0 and context.questions_answered > 0:
            return TransitionDecision(
                should_transition=True,
                target_phase=InterviewPhase.DEEP_DIVE,
                reason="No more questions in phase",
                trigger=TransitionTrigger.AUTO_ADVANCE,
                confidence=0.8,
            )

        return TransitionDecision(
            should_transition=False,
            target_phase=None,
            reason="Still gathering context",
            trigger=trigger,
            confidence=1.0,
        )

    def _eval_deep_dive(
        self,
        context: TransitionEvaluationContext,
        trigger: TransitionTrigger,
    ) -> TransitionDecision:
        """Deep dive can skip to validation or go to visual."""
        min_questions = self.MIN_QUESTIONS_PER_PHASE.get(
            InterviewPhase.DEEP_DIVE, 3
        )

        # Check for critical gaps
        if context.critical_gaps_open > 0:
            return TransitionDecision(
                should_transition=False,
                target_phase=None,
                reason=f"Critical gaps still open ({context.critical_gaps_open})",
                trigger=trigger,
                confidence=1.0,
            )

        # User skip
        if context.user_requested_skip:
            return TransitionDecision(
                should_transition=True,
                target_phase=InterviewPhase.VALIDATION,
                reason="User requested skip",
                trigger=TransitionTrigger.USER_SKIP,
                confidence=0.8,
            )

        # High confidence can skip visual
        if context.confidence_score >= self.SKIP_VISUAL_CONFIDENCE:
            return TransitionDecision(
                should_transition=True,
                target_phase=InterviewPhase.VALIDATION,
                reason=f"High confidence ({context.confidence_score:.2f}) - skipping visual",
                trigger=TransitionTrigger.CONFIDENCE_THRESHOLD,
                confidence=0.85,
            )

        # Normal: go to visual if enough questions
        if context.questions_answered >= min_questions:
            return TransitionDecision(
                should_transition=True,
                target_phase=InterviewPhase.VISUAL_EXPLORATION,
                reason=f"Minimum questions answered ({context.questions_answered})",
                trigger=trigger,
                confidence=0.9,
            )

        return TransitionDecision(
            should_transition=False,
            target_phase=None,
            reason="Still in deep dive",
            trigger=trigger,
            confidence=1.0,
        )

    def _eval_visual_exploration(
        self,
        context: TransitionEvaluationContext,
        trigger: TransitionTrigger,
    ) -> TransitionDecision:
        """Visual exploration goes to validation."""
        min_questions = self.MIN_QUESTIONS_PER_PHASE.get(
            InterviewPhase.VISUAL_EXPLORATION, 2
        )

        if context.user_requested_skip or context.questions_answered >= min_questions:
            return TransitionDecision(
                should_transition=True,
                target_phase=InterviewPhase.VALIDATION,
                reason="Visual exploration complete",
                trigger=trigger,
                confidence=0.9,
            )

        if context.questions_remaining == 0 and context.questions_answered > 0:
            return TransitionDecision(
                should_transition=True,
                target_phase=InterviewPhase.VALIDATION,
                reason="No more visual questions",
                trigger=TransitionTrigger.AUTO_ADVANCE,
                confidence=0.8,
            )

        return TransitionDecision(
            should_transition=False,
            target_phase=None,
            reason="Still exploring visual preferences",
            trigger=trigger,
            confidence=1.0,
        )

    def _eval_validation(
        self,
        context: TransitionEvaluationContext,
        trigger: TransitionTrigger,
    ) -> TransitionDecision:
        """Validation can go back to deep dive or proceed to synthesis."""
        # Check if we have enough info
        if context.confidence_score >= self.VALIDATION_MIN_CONFIDENCE:
            if context.critical_gaps_open == 0:
                return TransitionDecision(
                    should_transition=True,
                    target_phase=InterviewPhase.SYNTHESIS,
                    reason="Validation passed - proceeding to synthesis",
                    trigger=trigger,
                    confidence=0.95,
                )

        # Need to go back
        if context.critical_gaps_open > 0:
            return TransitionDecision(
                should_transition=True,
                target_phase=InterviewPhase.DEEP_DIVE,
                reason=f"Validation failed - {context.critical_gaps_open} critical gaps",
                trigger=trigger,
                confidence=0.8,
                fallback_phase=InterviewPhase.SYNTHESIS,  # If can't go back
            )

        return TransitionDecision(
            should_transition=False,
            target_phase=None,
            reason="Waiting for validation input",
            trigger=trigger,
            confidence=1.0,
        )

    def _eval_synthesis(
        self,
        context: TransitionEvaluationContext,
        trigger: TransitionTrigger,
    ) -> TransitionDecision:
        """Synthesis auto-advances to complete."""
        return TransitionDecision(
            should_transition=True,
            target_phase=InterviewPhase.COMPLETE,
            reason="Synthesis complete",
            trigger=TransitionTrigger.AUTO_ADVANCE,
            confidence=1.0,
        )

    def _eval_complete(
        self,
        context: TransitionEvaluationContext,
        trigger: TransitionTrigger,
    ) -> TransitionDecision:
        """Complete is terminal."""
        return TransitionDecision(
            should_transition=False,
            target_phase=None,
            reason="Interview complete - terminal state",
            trigger=trigger,
            confidence=1.0,
        )

    def _eval_default(
        self,
        context: TransitionEvaluationContext,
        trigger: TransitionTrigger,
    ) -> TransitionDecision:
        """Default evaluation - try to advance."""
        return TransitionDecision(
            should_transition=True,
            target_phase=self.machine.PRIMARY_NEXT.get(
                self.machine.current_state
            ),
            reason="Default advancement",
            trigger=trigger,
            confidence=0.5,
        )

    # =========================================================================
    # CONDITION BUILDING
    # =========================================================================

    def _build_default_conditions(
        self,
    ) -> Dict[InterviewPhase, List[TransitionCondition]]:
        """Build default transition conditions."""
        return {
            InterviewPhase.CONTEXT_GATHERING: [
                TransitionCondition(
                    name="min_questions",
                    description="Minimum questions answered",
                    evaluator=lambda ctx: ctx.questions_answered >= 2,
                    required=True,
                ),
                TransitionCondition(
                    name="high_confidence",
                    description="High confidence can skip",
                    evaluator=lambda ctx: ctx.confidence_score >= 0.85,
                    required=False,
                    weight=2.0,
                ),
            ],
            InterviewPhase.DEEP_DIVE: [
                TransitionCondition(
                    name="no_critical_gaps",
                    description="No critical gaps open",
                    evaluator=lambda ctx: ctx.critical_gaps_open == 0,
                    required=True,
                ),
                TransitionCondition(
                    name="min_questions",
                    description="Minimum questions answered",
                    evaluator=lambda ctx: ctx.questions_answered >= 3,
                    required=True,
                ),
            ],
        }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_transition_manager(
    machine: Optional[InterviewStateMachine] = None,
    question_generator: Optional["DynamicQuestionGenerator"] = None,
) -> StateTransitionManager:
    """
    Create a configured StateTransitionManager.

    Args:
        machine: Optional state machine (creates new if None)
        question_generator: Optional question generator

    Returns:
        Configured StateTransitionManager
    """
    if machine is None:
        from gemini_mcp.maestro.interview.state_machine import (
            create_interview_state_machine,
        )
        machine = create_interview_state_machine()

    return StateTransitionManager(
        state_machine=machine,
        question_generator=question_generator,
    )
