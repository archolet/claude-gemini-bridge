"""
MAESTRO Data Models

All dataclasses and enums used by the MAESTRO wizard system.
Each dataclass implements to_dict() and from_dict() for serialization.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Self


# =============================================================================
# ENUMS
# =============================================================================


class QuestionCategory(str, Enum):
    """Categories of questions in the MAESTRO interview flow."""

    INTENT = "intent"  # Ne yapmak istiyorsun?
    SCOPE = "scope"  # Component/Page/Section?
    EXISTING_CONTEXT = "existing_context"  # Mevcut kod var mı?
    INDUSTRY = "industry"  # Hangi sektör?
    THEME_STYLE = "theme_style"  # Görsel stil
    VIBE_MOOD = "vibe_mood"  # Tasarım ruhu
    CONTENT = "content"  # İçerik yapısı
    TECHNICAL = "technical"  # Teknik gereksinimler
    ACCESSIBILITY = "accessibility"  # A11y level
    LANGUAGE = "language"  # Content language


class MaestroStatus(str, Enum):
    """Status of the MAESTRO session state machine."""

    IDLE = "idle"
    ANALYZING = "analyzing"
    INTERVIEWING = "interviewing"
    AWAITING_ANSWER = "awaiting_answer"
    DECIDING = "deciding"
    CONFIRMING = "confirming"
    EXECUTING = "executing"
    COMPLETE = "complete"
    ABORTED = "aborted"


# =============================================================================
# QUESTION DATACLASSES
# =============================================================================


@dataclass
class QuestionOption:
    """A single option for a multiple-choice question."""

    id: str  # Unique identifier, e.g., "opt_new_page"
    label: str  # Display text, e.g., "Yeni Sayfa"
    description: str = ""  # Additional context
    icon: str = ""  # Optional emoji or icon

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "icon": self.icon,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create instance from dictionary."""
        return cls(
            id=data["id"],
            label=data["label"],
            description=data.get("description", ""),
            icon=data.get("icon", ""),
        )


class QuestionType(str, Enum):
    """Types of questions for different input methods."""

    SINGLE_CHOICE = "single_choice"  # One option only
    MULTI_CHOICE = "multi_choice"  # Multiple options allowed
    SLIDER = "slider"  # Numeric slider
    TEXT_INPUT = "text_input"  # Free text input
    COLOR_PICKER = "color_picker"  # Color selection


@dataclass
class Question:
    """An interview question presented to the user."""

    id: str  # Unique identifier, e.g., "q_intent_type"
    category: QuestionCategory  # Question category
    text: str  # The question text (Turkish)
    options: list[QuestionOption] = field(default_factory=list)
    follow_up_map: dict[str, str] = field(default_factory=dict)  # option_id → next_question_id
    required: bool = True
    multi_select: bool = False
    help_text: str = ""  # Optional help text

    # Phase 2 additions
    question_type: QuestionType = QuestionType.SINGLE_CHOICE  # Input type
    show_when: str | None = None  # Conditional display rule (evaluated by FlowController)
    max_selections: int | None = None  # Max selections for multi_choice
    slider_min: int = 0  # Min value for slider
    slider_max: int = 100  # Max value for slider
    slider_step: int = 1  # Step value for slider

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "category": self.category.value,
            "text": self.text,
            "options": [opt.to_dict() for opt in self.options],
            "follow_up_map": self.follow_up_map,
            "required": self.required,
            "multi_select": self.multi_select,
            "help_text": self.help_text,
            "question_type": self.question_type.value,
            "show_when": self.show_when,
            "max_selections": self.max_selections,
            "slider_min": self.slider_min,
            "slider_max": self.slider_max,
            "slider_step": self.slider_step,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create instance from dictionary."""
        return cls(
            id=data["id"],
            category=QuestionCategory(data["category"]),
            text=data["text"],
            options=[QuestionOption.from_dict(opt) for opt in data.get("options", [])],
            follow_up_map=data.get("follow_up_map", {}),
            required=data.get("required", True),
            multi_select=data.get("multi_select", False),
            help_text=data.get("help_text", ""),
            question_type=QuestionType(data.get("question_type", "single_choice")),
            show_when=data.get("show_when"),
            max_selections=data.get("max_selections"),
            slider_min=data.get("slider_min", 0),
            slider_max=data.get("slider_max", 100),
            slider_step=data.get("slider_step", 1),
        )


@dataclass
class Answer:
    """User's answer to a question."""

    question_id: str  # ID of the answered question
    selected_options: list[str] = field(default_factory=list)  # Selected option IDs
    free_text: str | None = None  # Optional free-form text
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "question_id": self.question_id,
            "selected_options": self.selected_options,
            "free_text": self.free_text,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create instance from dictionary."""
        return cls(
            question_id=data["question_id"],
            selected_options=data.get("selected_options", []),
            free_text=data.get("free_text"),
            timestamp=data.get("timestamp", time.time()),
        )


# =============================================================================
# STATE DATACLASSES
# =============================================================================


@dataclass
class InterviewState:
    """Current state of the interview process."""

    status: MaestroStatus = MaestroStatus.IDLE
    current_question_id: str | None = None
    answers: list[Answer] = field(default_factory=list)
    question_history: list[str] = field(default_factory=list)  # Visited question IDs

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "current_question_id": self.current_question_id,
            "answers": [ans.to_dict() for ans in self.answers],
            "question_history": self.question_history,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create instance from dictionary."""
        return cls(
            status=MaestroStatus(data.get("status", "idle")),
            current_question_id=data.get("current_question_id"),
            answers=[Answer.from_dict(ans) for ans in data.get("answers", [])],
            question_history=data.get("question_history", []),
        )

    def get_answer(self, question_id: str) -> Answer | None:
        """Get answer for a specific question."""
        for answer in self.answers:
            if answer.question_id == question_id:
                return answer
        return None

    def get_answer_value(self, question_id: str) -> str | list[str] | None:
        """
        Get the primary value from an answer.

        Returns:
            - Single string if single_choice (first selected option)
            - List of strings if multi_choice
            - free_text if no options selected
            - None if question not answered
        """
        answer = self.get_answer(question_id)
        if answer is None:
            return None

        if answer.selected_options:
            # Return first option for single choice, all for multi
            if len(answer.selected_options) == 1:
                return answer.selected_options[0]
            return answer.selected_options

        return answer.free_text

    def has_answer(self, question_id: str) -> bool:
        """Check if a question has been answered."""
        return self.get_answer(question_id) is not None

    @property
    def has_existing_projects(self) -> bool:
        """Check if session has existing project context."""
        # This will be set based on ContextData.previous_html
        # Used by FlowController skip rules
        return False  # Will be updated by Maestro core


# =============================================================================
# CONTEXT DATACLASSES
# =============================================================================


@dataclass
class ProjectInfo:
    """Detected information about the current project."""

    name: str = ""
    path: str = ""
    existing_files: list[str] = field(default_factory=list)
    detected_theme: str | None = None
    detected_framework: str | None = None  # React, Vue, vanilla, etc.

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "path": self.path,
            "existing_files": self.existing_files,
            "detected_theme": self.detected_theme,
            "detected_framework": self.detected_framework,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create instance from dictionary."""
        return cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            existing_files=data.get("existing_files", []),
            detected_theme=data.get("detected_theme"),
            detected_framework=data.get("detected_framework"),
        )


@dataclass
class ContextData:
    """Gathered context for design decisions."""

    previous_html: str | None = None  # Existing HTML to refine or match
    design_tokens: dict[str, Any] = field(default_factory=dict)  # Extracted style tokens
    project_context: str = ""  # User-provided project description
    content_language: str = "tr"  # Default: Turkish

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "previous_html": self.previous_html,
            "design_tokens": self.design_tokens,
            "project_context": self.project_context,
            "content_language": self.content_language,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create instance from dictionary."""
        return cls(
            previous_html=data.get("previous_html"),
            design_tokens=data.get("design_tokens", {}),
            project_context=data.get("project_context", ""),
            content_language=data.get("content_language", "tr"),
        )


# =============================================================================
# SESSION DATACLASS
# =============================================================================


@dataclass
class MaestroSession:
    """A complete MAESTRO wizard session."""

    session_id: str
    created_at: float = field(default_factory=time.time)
    state: InterviewState = field(default_factory=InterviewState)
    context: ContextData = field(default_factory=ContextData)
    project_info: ProjectInfo | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "state": self.state.to_dict(),
            "context": self.context.to_dict(),
            "project_info": self.project_info.to_dict() if self.project_info else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create instance from dictionary."""
        project_info = None
        if data.get("project_info"):
            project_info = ProjectInfo.from_dict(data["project_info"])

        return cls(
            session_id=data["session_id"],
            created_at=data.get("created_at", time.time()),
            state=InterviewState.from_dict(data.get("state", {})),
            context=ContextData.from_dict(data.get("context", {})),
            project_info=project_info,
        )


# =============================================================================
# DECISION DATACLASS
# =============================================================================


@dataclass
class MaestroDecision:
    """Final decision from the MAESTRO wizard."""

    mode: str  # "design_frontend", "design_page", etc.
    confidence: float = 1.0  # 0.0 - 1.0
    parameters: dict[str, Any] = field(default_factory=dict)  # Tool-specific params
    reasoning: str = ""  # Why this mode was chosen
    alternatives: list[dict[str, Any]] = field(default_factory=list)  # Other options

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "mode": self.mode,
            "confidence": self.confidence,
            "parameters": self.parameters,
            "reasoning": self.reasoning,
            "alternatives": self.alternatives,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create instance from dictionary."""
        return cls(
            mode=data["mode"],
            confidence=data.get("confidence", 1.0),
            parameters=data.get("parameters", {}),
            reasoning=data.get("reasoning", ""),
            alternatives=data.get("alternatives", []),
        )

    def get_tool_kwargs(self) -> dict[str, Any]:
        """Get parameters formatted for MCP tool call."""
        return self.parameters.copy()


# =============================================================================
# VALIDATION DATACLASSES (Phase 2)
# =============================================================================


@dataclass
class ValidationResult:
    """Result of validating an answer."""

    is_valid: bool
    error_message: str | None = None
    normalized_value: Any = None  # Cleaned/normalized answer value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "error_message": self.error_message,
            "normalized_value": self.normalized_value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create instance from dictionary."""
        return cls(
            is_valid=data["is_valid"],
            error_message=data.get("error_message"),
            normalized_value=data.get("normalized_value"),
        )

    @classmethod
    def valid(cls, normalized_value: Any = None) -> Self:
        """Factory method for valid result."""
        return cls(is_valid=True, normalized_value=normalized_value)

    @classmethod
    def invalid(cls, error_message: str) -> Self:
        """Factory method for invalid result."""
        return cls(is_valid=False, error_message=error_message)


@dataclass
class AnswerResult:
    """Result of processing an answer through InterviewEngine."""

    is_valid: bool
    error_message: str | None = None
    follow_ups: list[str] = field(default_factory=list)  # Triggered follow-up question IDs
    triggers_decision: bool = False  # Whether this answer completes the interview
    progress: float = 0.0  # Interview progress (0.0 - 1.0)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "error_message": self.error_message,
            "follow_ups": self.follow_ups,
            "triggers_decision": self.triggers_decision,
            "progress": self.progress,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create instance from dictionary."""
        return cls(
            is_valid=data["is_valid"],
            error_message=data.get("error_message"),
            follow_ups=data.get("follow_ups", []),
            triggers_decision=data.get("triggers_decision", False),
            progress=data.get("progress", 0.0),
        )
