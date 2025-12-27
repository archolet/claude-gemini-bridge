"""
MAESTRO Turkish Prompt Templates - Phase 4

Turkish language prompts for the MAESTRO interview system.
All user-facing text is in Turkish for native UX.

Modules:
- interview: Interview phase prompts and transitions
- questions: Dynamic question templates
- feedback: User feedback and validation messages
- extraction: Soul extraction prompts for Gemini
"""

from gemini_mcp.maestro.prompts.tr.interview import (
    PHASE_PROMPTS,
    TRANSITION_MESSAGES,
    PROGRESS_MESSAGES,
    get_phase_prompt,
    get_transition_message,
)

from gemini_mcp.maestro.prompts.tr.questions import (
    QUESTION_TEMPLATES,
    CATEGORY_HEADERS,
    OPTION_LABELS,
    get_question_text,
    get_category_header,
)

from gemini_mcp.maestro.prompts.tr.feedback import (
    VALIDATION_MESSAGES,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
    get_validation_message,
    get_error_message,
)

from gemini_mcp.maestro.prompts.tr.extraction import (
    SOUL_EXTRACTION_PROMPT,
    GAP_DETECTION_PROMPT,
    BRIEF_ANALYSIS_PROMPT,
    get_extraction_prompt,
)

__all__ = [
    # Interview
    "PHASE_PROMPTS",
    "TRANSITION_MESSAGES",
    "PROGRESS_MESSAGES",
    "get_phase_prompt",
    "get_transition_message",
    # Questions
    "QUESTION_TEMPLATES",
    "CATEGORY_HEADERS",
    "OPTION_LABELS",
    "get_question_text",
    "get_category_header",
    # Feedback
    "VALIDATION_MESSAGES",
    "ERROR_MESSAGES",
    "SUCCESS_MESSAGES",
    "get_validation_message",
    "get_error_message",
    # Extraction
    "SOUL_EXTRACTION_PROMPT",
    "GAP_DETECTION_PROMPT",
    "BRIEF_ANALYSIS_PROMPT",
    "get_extraction_prompt",
]
