"""
MAESTRO Adaptive Flow - Phase 6.3

Dynamically adapts interview flow based on:
- Previous answers (skip redundant questions)
- User expertise level (adjust complexity)
- Project context (pre-fill known values)
- Time pressure (fast-track mode)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SkipReason(Enum):
    """Reasons for skipping a question."""
    ALREADY_ANSWERED = "already_answered"
    INFERRED_FROM_CONTEXT = "inferred_from_context"
    NOT_APPLICABLE = "not_applicable"
    EXPERT_MODE = "expert_mode"
    FAST_TRACK = "fast_track"


@dataclass
class SkipDecision:
    """Decision to skip a question with reasoning."""
    should_skip: bool
    reason: SkipReason | None = None
    inferred_value: Any = None
    confidence: float = 0.0
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "should_skip": self.should_skip,
            "reason": self.reason.value if self.reason else None,
            "inferred_value": self.inferred_value,
            "confidence": self.confidence,
            "explanation": self.explanation,
        }


@dataclass
class FlowContext:
    """Context for flow adaptation decisions."""
    answers: dict[str, Any] = field(default_factory=dict)
    project_context: str = ""
    existing_html: str = ""
    expertise_level: str = "intermediate"  # beginner, intermediate, expert
    fast_track: bool = False
    time_budget_seconds: int | None = None

    def has_answer(self, question_id: str) -> bool:
        """Check if question was already answered."""
        return question_id in self.answers

    def get_answer(self, question_id: str) -> Any:
        """Get answer for a question."""
        return self.answers.get(question_id)


# Question inference rules
INFERENCE_RULES: dict[str, dict[str, Any]] = {
    # If project_context mentions "dashboard", likely design_page with dashboard template
    "q_intent_main": {
        "keywords": {
            "dashboard": {"value": "opt_full_page", "confidence": 0.8},
            "landing": {"value": "opt_full_page", "confidence": 0.85},
            "component": {"value": "opt_new_design", "confidence": 0.7},
            "button": {"value": "opt_new_design", "confidence": 0.9},
            "card": {"value": "opt_new_design", "confidence": 0.9},
        }
    },
    "q_scope_page_type": {
        "keywords": {
            "dashboard": {"value": "opt_dashboard", "confidence": 0.9},
            "landing": {"value": "opt_landing", "confidence": 0.9},
            "auth": {"value": "opt_auth", "confidence": 0.85},
            "login": {"value": "opt_auth", "confidence": 0.9},
            "pricing": {"value": "opt_pricing", "confidence": 0.9},
        }
    },
    "q_theme_style": {
        "keywords": {
            "corporate": {"value": "opt_corporate", "confidence": 0.85},
            "modern": {"value": "opt_modern_minimal", "confidence": 0.8},
            "dark": {"value": "opt_dark_mode_first", "confidence": 0.75},
            "neon": {"value": "opt_cyberpunk", "confidence": 0.85},
            "glass": {"value": "opt_glassmorphism", "confidence": 0.9},
        }
    },
}

# Questions that can be skipped for experts
EXPERT_SKIP_QUESTIONS = {
    "q_quality_level",  # Experts know what they want
    "q_accessibility_level",  # Experts specify explicitly
}

# Questions that can be skipped in fast-track mode
FAST_TRACK_SKIP_QUESTIONS = {
    "q_theme_customization",
    "q_advanced_options",
    "q_quality_level",
}


class AdaptiveFlow:
    """
    Adaptive interview flow controller.

    Makes intelligent decisions about:
    - Which questions to skip
    - What values to infer from context
    - How to adjust complexity for user level
    """

    def __init__(self) -> None:
        self._context: FlowContext | None = None

    def set_context(self, context: FlowContext) -> None:
        """Set the flow context for adaptation decisions."""
        self._context = context

    def should_skip_question(self, question_id: str) -> SkipDecision:
        """
        Determine if a question should be skipped.

        Args:
            question_id: The question identifier

        Returns:
            SkipDecision with reasoning
        """
        if not self._context:
            return SkipDecision(should_skip=False)

        # Check if already answered
        if self._context.has_answer(question_id):
            return SkipDecision(
                should_skip=True,
                reason=SkipReason.ALREADY_ANSWERED,
                inferred_value=self._context.get_answer(question_id),
                confidence=1.0,
                explanation="Bu soru zaten yanıtlandı",
            )

        # Check expert mode
        if (self._context.expertise_level == "expert" and
            question_id in EXPERT_SKIP_QUESTIONS):
            return SkipDecision(
                should_skip=True,
                reason=SkipReason.EXPERT_MODE,
                confidence=0.7,
                explanation="Uzman modunda bu soru atlandı",
            )

        # Check fast-track mode
        if (self._context.fast_track and
            question_id in FAST_TRACK_SKIP_QUESTIONS):
            return SkipDecision(
                should_skip=True,
                reason=SkipReason.FAST_TRACK,
                confidence=0.6,
                explanation="Hızlı modda bu soru atlandı",
            )

        # Try to infer from project context
        inference = self._infer_from_context(question_id)
        if inference.should_skip:
            return inference

        return SkipDecision(should_skip=False)

    def _infer_from_context(self, question_id: str) -> SkipDecision:
        """Try to infer answer from project context."""
        if not self._context or not self._context.project_context:
            return SkipDecision(should_skip=False)

        rules = INFERENCE_RULES.get(question_id, {})
        keywords = rules.get("keywords", {})

        context_lower = self._context.project_context.lower()

        best_match: tuple[str, float] | None = None

        for keyword, config in keywords.items():
            if keyword in context_lower:
                confidence = config["confidence"]
                if best_match is None or confidence > best_match[1]:
                    best_match = (config["value"], confidence)

        if best_match and best_match[1] >= 0.75:  # High confidence threshold
            return SkipDecision(
                should_skip=True,
                reason=SkipReason.INFERRED_FROM_CONTEXT,
                inferred_value=best_match[0],
                confidence=best_match[1],
                explanation=f"Proje bağlamından çıkarıldı (güven: {best_match[1]:.0%})",
            )

        return SkipDecision(should_skip=False)

    def get_suggested_answers(self, question_id: str) -> list[dict[str, Any]]:
        """
        Get suggested answers for a question based on context.

        Returns list of suggestions with confidence scores.
        """
        if not self._context:
            return []

        suggestions: list[dict[str, Any]] = []

        # Get from inference rules
        rules = INFERENCE_RULES.get(question_id, {})
        keywords = rules.get("keywords", {})

        if self._context.project_context:
            context_lower = self._context.project_context.lower()

            for keyword, config in keywords.items():
                if keyword in context_lower:
                    suggestions.append({
                        "value": config["value"],
                        "confidence": config["confidence"],
                        "reason": f"'{keyword}' bağlamda bulundu",
                    })

        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)

        return suggestions[:3]  # Top 3 suggestions

    def adjust_question_complexity(
        self,
        question: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Adjust question complexity based on user expertise.

        - Beginners: More explanation, simpler options
        - Experts: Concise, technical options
        """
        if not self._context:
            return question

        adjusted = question.copy()

        if self._context.expertise_level == "beginner":
            # Add more explanation
            if "hint" not in adjusted:
                adjusted["hint"] = "Bu seçenek tasarımınızı şekillendirir"

        elif self._context.expertise_level == "expert":
            # Remove explanations, keep it concise
            if "hint" in adjusted:
                del adjusted["hint"]

        return adjusted

    def estimate_remaining_questions(
        self,
        current_question_idx: int,
        total_questions: int
    ) -> int:
        """Estimate remaining questions considering skips."""
        if not self._context:
            return total_questions - current_question_idx

        remaining = total_questions - current_question_idx

        # Estimate skips
        if self._context.expertise_level == "expert":
            remaining -= len(EXPERT_SKIP_QUESTIONS)

        if self._context.fast_track:
            remaining -= len(FAST_TRACK_SKIP_QUESTIONS)

        return max(1, remaining)

    def to_dict(self) -> dict[str, Any]:
        """Convert flow state to dictionary."""
        return {
            "context": {
                "answers_count": len(self._context.answers) if self._context else 0,
                "expertise_level": self._context.expertise_level if self._context else "intermediate",
                "fast_track": self._context.fast_track if self._context else False,
                "has_project_context": bool(self._context and self._context.project_context),
            } if self._context else None
        }
