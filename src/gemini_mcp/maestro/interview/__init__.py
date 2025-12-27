"""MAESTRO Interview Module - Phase 2 & 3

Contains:
- InterviewEngine: Main interview orchestrator
- FlowController: Interview flow management

Phase 3 Additions:
- InterviewStateMachine: Pure Python state machine for phases
- StateTransitionManager: Intelligent transition management
- ProgressTracker: Rich progress tracking and analytics
"""

# Phase 2: Core Interview Components
from gemini_mcp.maestro.interview.engine import InterviewEngine
from gemini_mcp.maestro.interview.flow_controller import FlowController

# Phase 3: State Machine
from gemini_mcp.maestro.interview.state_machine import (
    InterviewStateMachine,
    StateEvent,
    TransitionAttempt,
    TransitionResult,
    create_interview_state_machine,
)

# Phase 3: Transition Management
from gemini_mcp.maestro.interview.transitions import (
    StateTransitionManager,
    TransitionCondition,
    TransitionDecision,
    TransitionEvaluationContext,
    TransitionTrigger,
    create_transition_manager,
)

# Phase 3: Progress Tracking
from gemini_mcp.maestro.interview.progress import (
    PhaseMetrics,
    ProgressDisplay,
    ProgressSnapshot,
    ProgressStatus,
    ProgressTracker,
    create_progress_tracker,
    track_interview_progress,
)

__all__ = [
    # Phase 2: Core
    "InterviewEngine",
    "FlowController",
    # Phase 3: State Machine
    "InterviewStateMachine",
    "TransitionResult",
    "StateEvent",
    "TransitionAttempt",
    "create_interview_state_machine",
    # Phase 3: Transitions
    "StateTransitionManager",
    "TransitionTrigger",
    "TransitionCondition",
    "TransitionEvaluationContext",
    "TransitionDecision",
    "create_transition_manager",
    # Phase 3: Progress
    "ProgressTracker",
    "ProgressStatus",
    "PhaseMetrics",
    "ProgressSnapshot",
    "ProgressDisplay",
    "create_progress_tracker",
    "track_interview_progress",
]
