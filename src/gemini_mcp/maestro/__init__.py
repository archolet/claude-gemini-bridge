"""
MAESTRO - Multi-Agent Expert System for Tool Route Optimization

An intelligent design wizard for Gemini MCP that interviews users
to understand their intent and automatically selects the correct
design mode and parameters.

Supported Design Modes:
- design_frontend: Component design (button, card, form, etc.)
- design_page: Full page layouts (landing, dashboard, auth)
- design_section: Single section with style consistency
- refine_frontend: Iterate on existing designs
- replace_section_in_page: Surgical section replacement
- design_from_reference: Design based on reference images

Example Usage:
    from gemini_mcp.maestro import Maestro, Answer

    maestro = Maestro(client)
    session_id, question = await maestro.start_session()

    # Process user answers
    answer = Answer(question_id=question.id, selected_options=["opt_new_page"])
    result = await maestro.process_answer(session_id, answer)

    # When result is a MaestroDecision, execute it
    if isinstance(result, MaestroDecision):
        output = await maestro.execute(session_id, result)
"""

from gemini_mcp.maestro.models import (
    # Enums
    MaestroStatus,
    QuestionCategory,
    QuestionType,
    # Question-related dataclasses
    Answer,
    Question,
    QuestionOption,
    # State dataclasses
    ContextData,
    InterviewState,
    ProjectInfo,
    # Session and Decision
    MaestroDecision,
    MaestroSession,
    # Validation (Phase 2)
    AnswerResult,
    ValidationResult,
)
from gemini_mcp.maestro.core import Maestro

# Phase 2: Interview System Components
from gemini_mcp.maestro.questions.bank import QuestionBank
from gemini_mcp.maestro.questions.validators import (
    AnswerValidator,
    get_validator,
    validate_answer,
    VALIDATORS,
)
from gemini_mcp.maestro.interview.engine import InterviewEngine
from gemini_mcp.maestro.interview.flow_controller import FlowController

# Phase 3: Decision System Components
from gemini_mcp.maestro.decision import (
    ContextAnalyzer,
    ContextAnalysis,
    DecisionAnalysis,
    DecisionScores,
    DecisionTree,
    EnrichedContext,
)

# Phase 4: Execution System Components
from gemini_mcp.maestro.execution import ToolExecutor

# Phase 5: Session Management
from gemini_mcp.maestro.session import SessionManager

# MAESTRO v2: Soul-Aware Interview System
from gemini_mcp.maestro.v2.wrapper import MAESTROv2Wrapper
from gemini_mcp.maestro.v2.session import SoulAwareSession, SessionState
from gemini_mcp.maestro.models.soul import ProjectSoul, InterviewPhase

__all__ = [
    # Main class
    "Maestro",
    # Enums
    "MaestroStatus",
    "QuestionCategory",
    "QuestionType",
    # Question-related
    "QuestionOption",
    "Question",
    "Answer",
    # State
    "InterviewState",
    "ProjectInfo",
    "ContextData",
    # Session and Decision
    "MaestroSession",
    "MaestroDecision",
    # Validation (Phase 2)
    "ValidationResult",
    "AnswerResult",
    # Phase 2: Interview System
    "QuestionBank",
    "InterviewEngine",
    "FlowController",
    "AnswerValidator",
    "get_validator",
    "validate_answer",
    "VALIDATORS",
    # Phase 3: Decision System
    "DecisionTree",
    "ContextAnalyzer",
    "DecisionScores",
    "ContextAnalysis",
    "EnrichedContext",
    "DecisionAnalysis",
    # Phase 4: Execution System
    "ToolExecutor",
    # Phase 5: Session Management
    "SessionManager",
    # MAESTRO v2: Soul-Aware Interview System
    "MAESTROv2Wrapper",
    "SoulAwareSession",
    "SessionState",
    "ProjectSoul",
    "InterviewPhase",
]

__version__ = "0.1.0"
