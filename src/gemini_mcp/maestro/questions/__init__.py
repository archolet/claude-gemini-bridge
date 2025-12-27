"""MAESTRO Questions Module - Phase 2 & 3

Contains:
- QuestionBank: Static question repository
- Answer Validators: Input validation
- GapBasedQuestionFactory: Dynamic question generation from gaps
- QuestionPrioritizer: Multi-factor question prioritization
- DynamicQuestionGenerator: Orchestrates all question sources
"""

from gemini_mcp.maestro.questions.bank import QuestionBank
from gemini_mcp.maestro.questions.validators import (
    VALIDATORS,
    AnswerValidator,
    ColorPickerValidator,
    MultiChoiceValidator,
    SingleChoiceValidator,
    SliderValidator,
    TextInputValidator,
    get_validator,
    validate_answer,
)

# Phase 3: Dynamic Question Generation
from gemini_mcp.maestro.questions.gap_factory import (
    GapBasedQuestionFactory,
    create_questions_from_analysis,
)
from gemini_mcp.maestro.questions.prioritizer import (
    PriorityScore,
    PriorityStrategy,
    QuestionPrioritizer,
    prioritize_questions,
)
from gemini_mcp.maestro.questions.generator import (
    DynamicQuestionGenerator,
    GenerationContext,
    GenerationMode,
    GenerationResult,
    generate_interview_questions,
    get_critical_questions,
)

__all__ = [
    # Static Questions
    "QuestionBank",
    # Validators
    "AnswerValidator",
    "SingleChoiceValidator",
    "MultiChoiceValidator",
    "SliderValidator",
    "TextInputValidator",
    "ColorPickerValidator",
    # Validator Registry
    "VALIDATORS",
    "get_validator",
    "validate_answer",
    # Phase 3: Gap Factory
    "GapBasedQuestionFactory",
    "create_questions_from_analysis",
    # Phase 3: Prioritizer
    "QuestionPrioritizer",
    "PriorityStrategy",
    "PriorityScore",
    "prioritize_questions",
    # Phase 3: Generator
    "DynamicQuestionGenerator",
    "GenerationMode",
    "GenerationContext",
    "GenerationResult",
    "generate_interview_questions",
    "get_critical_questions",
]
