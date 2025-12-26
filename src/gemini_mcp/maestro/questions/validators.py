"""
MAESTRO Answer Validators - Phase 2

Protocol-based validators for different question types.
Each validator implements the AnswerValidator protocol and
returns a ValidationResult.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Protocol

from gemini_mcp.maestro.models import QuestionType, ValidationResult

if TYPE_CHECKING:
    from gemini_mcp.maestro.models import Answer, Question


class AnswerValidator(Protocol):
    """Protocol for answer validators."""

    def validate(self, answer: "Answer", question: "Question") -> ValidationResult:
        """
        Validate an answer against a question.

        Args:
            answer: The user's answer
            question: The question being answered

        Returns:
            ValidationResult with is_valid, error_message, and normalized_value
        """
        ...


class SingleChoiceValidator:
    """Validator for single-choice questions."""

    def validate(self, answer: "Answer", question: "Question") -> ValidationResult:
        """Validate that exactly one option is selected."""
        # Check if exactly one option is selected
        if len(answer.selected_options) == 0:
            if question.required:
                return ValidationResult.invalid("Bir seçenek seçmelisiniz")
            return ValidationResult.valid(None)

        if len(answer.selected_options) > 1:
            return ValidationResult.invalid("Sadece bir seçenek seçebilirsiniz")

        # Validate the selected option exists
        selected = answer.selected_options[0]
        valid_ids = {opt.id for opt in question.options}
        if selected not in valid_ids:
            return ValidationResult.invalid(f"Geçersiz seçenek: {selected}")

        return ValidationResult.valid(selected)


class MultiChoiceValidator:
    """Validator for multi-choice questions."""

    def __init__(self, default_max: int = 10) -> None:
        """
        Initialize with default max selections.

        Args:
            default_max: Maximum selections if question doesn't specify
        """
        self.default_max = default_max

    def validate(self, answer: "Answer", question: "Question") -> ValidationResult:
        """Validate that selection count is within limits."""
        selected = answer.selected_options
        max_selections = question.max_selections or self.default_max

        # Check minimum (if required)
        if len(selected) == 0:
            if question.required:
                return ValidationResult.invalid("En az bir seçenek seçmelisiniz")
            return ValidationResult.valid([])

        # Check maximum
        if len(selected) > max_selections:
            return ValidationResult.invalid(
                f"En fazla {max_selections} seçenek seçebilirsiniz"
            )

        # Validate all selected options exist
        valid_ids = {opt.id for opt in question.options}
        invalid = [s for s in selected if s not in valid_ids]
        if invalid:
            return ValidationResult.invalid(f"Geçersiz seçenekler: {', '.join(invalid)}")

        return ValidationResult.valid(selected)


class SliderValidator:
    """Validator for slider/range questions."""

    def validate(self, answer: "Answer", question: "Question") -> ValidationResult:
        """Validate that the value is within the slider range."""
        # Get value from free_text (sliders use numeric value)
        raw_value = answer.free_text

        if raw_value is None or raw_value == "":
            if question.required:
                return ValidationResult.invalid("Bir değer seçmelisiniz")
            return ValidationResult.valid(None)

        # Try to parse as number
        try:
            value = int(raw_value)
        except ValueError:
            try:
                value = float(raw_value)
            except ValueError:
                return ValidationResult.invalid("Geçersiz sayısal değer")

        # Check range
        min_val = question.slider_min
        max_val = question.slider_max

        if value < min_val:
            return ValidationResult.invalid(f"Değer en az {min_val} olmalıdır")
        if value > max_val:
            return ValidationResult.invalid(f"Değer en fazla {max_val} olabilir")

        return ValidationResult.valid(value)


class TextInputValidator:
    """Validator for free-text input questions."""

    def __init__(
        self,
        min_length: int = 0,
        max_length: int = 10000,
    ) -> None:
        """
        Initialize with length constraints.

        Args:
            min_length: Minimum text length
            max_length: Maximum text length
        """
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, answer: "Answer", question: "Question") -> ValidationResult:
        """Validate text input."""
        text = answer.free_text

        # Handle empty text
        if text is None or text.strip() == "":
            if question.required:
                return ValidationResult.invalid("Bu alan boş bırakılamaz")
            return ValidationResult.valid("")

        # Normalize
        text = text.strip()

        # Check length
        if len(text) < self.min_length:
            return ValidationResult.invalid(
                f"En az {self.min_length} karakter girilmelidir"
            )
        if len(text) > self.max_length:
            return ValidationResult.invalid(
                f"En fazla {self.max_length} karakter girilebilir"
            )

        return ValidationResult.valid(text)


class ColorPickerValidator:
    """Validator for color picker questions."""

    # Regex for hex color codes
    HEX_PATTERN = re.compile(r"^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")

    def validate(self, answer: "Answer", question: "Question") -> ValidationResult:
        """Validate hex color code."""
        color = answer.free_text

        if color is None or color.strip() == "":
            if question.required:
                return ValidationResult.invalid("Bir renk kodu girilmelidir")
            return ValidationResult.valid(None)

        color = color.strip()

        # Validate hex format
        if not self.HEX_PATTERN.match(color):
            return ValidationResult.invalid(
                "Geçersiz renk kodu. Örnek: #E11D48 veya #3B82F6"
            )

        # Normalize to full hex with #
        if not color.startswith("#"):
            color = f"#{color}"

        # Expand 3-char hex to 6-char
        if len(color) == 4:  # #RGB
            color = f"#{color[1]*2}{color[2]*2}{color[3]*2}"

        return ValidationResult.valid(color.upper())


# =============================================================================
# VALIDATOR REGISTRY
# =============================================================================

# Registry mapping question types to validators
VALIDATORS: dict[QuestionType, AnswerValidator] = {
    QuestionType.SINGLE_CHOICE: SingleChoiceValidator(),
    QuestionType.MULTI_CHOICE: MultiChoiceValidator(),
    QuestionType.SLIDER: SliderValidator(),
    QuestionType.TEXT_INPUT: TextInputValidator(),
    QuestionType.COLOR_PICKER: ColorPickerValidator(),
}


def get_validator(question_type: QuestionType) -> AnswerValidator:
    """
    Get the appropriate validator for a question type.

    Args:
        question_type: The type of question

    Returns:
        The validator for that question type
    """
    return VALIDATORS.get(question_type, SingleChoiceValidator())


def validate_answer(answer: "Answer", question: "Question") -> ValidationResult:
    """
    Validate an answer using the appropriate validator.

    Convenience function that selects the correct validator
    based on the question type.

    Args:
        answer: The user's answer
        question: The question being answered

    Returns:
        ValidationResult
    """
    validator = get_validator(question.question_type)
    return validator.validate(answer, question)
