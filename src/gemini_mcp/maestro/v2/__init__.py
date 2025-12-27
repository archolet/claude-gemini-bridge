"""
MAESTRO v2 Integration Layer

Provides backward-compatible integration of the new soul-based
interview system with the existing MAESTRO core.

Components:
- MAESTROv2Wrapper: Main wrapper for MAESTRO v2 integration
- SoulAwareSession: Session with ProjectSoul context
- SessionState: State machine for soul-aware sessions
- InterviewPhase: Interview phase enumeration
- FallbackHandler: Graceful degradation to v1
- FallbackReason: Enum of fallback reasons
- V2Metrics: Metrics for v2 operations

Usage:
    >>> from gemini_mcp.maestro.v2 import MAESTROv2Wrapper
    >>> from gemini_mcp.client import GeminiClient
    >>>
    >>> client = GeminiClient()
    >>> wrapper = MAESTROv2Wrapper(client)
    >>>
    >>> # Start with design brief
    >>> session, question = await wrapper.start_session(
    ...     design_brief="Design a modern fintech dashboard"
    ... )
    >>>
    >>> # Access soul if extracted
    >>> if session.has_soul:
    ...     print(session.soul.project_name)
    'Fintech Dashboard'
"""

from gemini_mcp.maestro.v2.session import (
    SoulAwareSession,
    SessionState,
    InterviewPhase,
    PhaseTransition,
)
from gemini_mcp.maestro.v2.fallback import (
    FallbackHandler,
    FallbackReason,
    FallbackEvent,
)
from gemini_mcp.maestro.v2.wrapper import MAESTROv2Wrapper, V2Metrics

__all__ = [
    # Main wrapper
    "MAESTROv2Wrapper",
    "V2Metrics",
    # Session
    "SoulAwareSession",
    "SessionState",
    "InterviewPhase",
    "PhaseTransition",
    # Fallback
    "FallbackHandler",
    "FallbackReason",
    "FallbackEvent",
]
