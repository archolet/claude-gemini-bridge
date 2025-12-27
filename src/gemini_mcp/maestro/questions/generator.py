"""
MAESTRO Dynamic Question Generator - Phase 3

The orchestrator that combines static questions, gap-based dynamic questions,
and intelligent prioritization to create the optimal interview experience.

Key Features:
1. Merges QuestionBank (static) + GapBasedQuestionFactory (dynamic)
2. Uses QuestionPrioritizer for smart ordering
3. Tracks answered questions and interview progress
4. Adapts question flow based on answers and detected gaps
5. Supports multiple generation modes (gap_first, balanced, static_first)

Usage:
    >>> from gemini_mcp.maestro.questions.generator import DynamicQuestionGenerator
    >>> generator = DynamicQuestionGenerator()
    >>> questions = generator.generate(soul, gaps)
    >>> next_q = generator.get_next_question(answered_ids)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional, Set, Tuple

from gemini_mcp.maestro.models import (
    Question,
    QuestionCategory,
    QuestionOption,
    QuestionType,
)
from gemini_mcp.maestro.models.gap import (
    GapAnalysis,
    GapCategory,
    GapInfo,
    GapSeverity,
)
from gemini_mcp.maestro.questions.bank import QuestionBank
from gemini_mcp.maestro.questions.gap_factory import GapBasedQuestionFactory
from gemini_mcp.maestro.questions.prioritizer import (
    PriorityStrategy,
    QuestionPrioritizer,
)

if TYPE_CHECKING:
    from gemini_mcp.maestro.models.soul import ProjectSoul

logger = logging.getLogger(__name__)


class GenerationMode(str, Enum):
    """
    Question generation modes.

    GAP_FIRST: Prioritize gap-based questions (address critical gaps first)
    BALANCED: Mix gap-based and static questions by priority
    STATIC_FIRST: Use static questions, gap-based as supplement
    ADAPTIVE: Dynamically switch based on confidence score
    """
    GAP_FIRST = "gap_first"
    BALANCED = "balanced"
    STATIC_FIRST = "static_first"
    ADAPTIVE = "adaptive"


@dataclass
class GenerationContext:
    """
    Context for question generation.

    Tracks the current state of the interview including which questions
    have been asked, answered, and skipped.
    """
    answered_question_ids: Set[str] = field(default_factory=set)
    skipped_question_ids: Set[str] = field(default_factory=set)
    current_category: Optional[QuestionCategory] = None
    current_phase: Optional[str] = None
    confidence_score: float = 0.0
    questions_asked: int = 0
    max_questions: int = 15

    def mark_answered(self, question_id: str) -> None:
        """Mark a question as answered."""
        self.answered_question_ids.add(question_id)
        self.questions_asked += 1

    def mark_skipped(self, question_id: str) -> None:
        """Mark a question as skipped."""
        self.skipped_question_ids.add(question_id)

    def is_asked(self, question_id: str) -> bool:
        """Check if a question has been asked (answered or skipped)."""
        return question_id in self.answered_question_ids or question_id in self.skipped_question_ids

    def can_ask_more(self) -> bool:
        """Check if we can ask more questions."""
        return self.questions_asked < self.max_questions

    def reset(self) -> None:
        """Reset the context for a new interview."""
        self.answered_question_ids.clear()
        self.skipped_question_ids.clear()
        self.current_category = None
        self.current_phase = None
        self.questions_asked = 0


@dataclass
class GenerationResult:
    """
    Result of question generation.

    Contains generated questions and metadata about the generation process.
    """
    questions: List[Question]
    gap_based_count: int
    static_count: int
    total_gaps: int
    resolved_gaps: int
    generation_mode: GenerationMode

    @property
    def total_questions(self) -> int:
        """Total number of questions generated."""
        return len(self.questions)

    @property
    def gap_coverage(self) -> float:
        """Percentage of gaps covered by questions."""
        if self.total_gaps == 0:
            return 1.0
        return self.gap_based_count / self.total_gaps

    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/debugging."""
        return {
            "total_questions": self.total_questions,
            "gap_based_count": self.gap_based_count,
            "static_count": self.static_count,
            "total_gaps": self.total_gaps,
            "resolved_gaps": self.resolved_gaps,
            "generation_mode": self.generation_mode.value,
            "gap_coverage": round(self.gap_coverage, 2),
        }


class DynamicQuestionGenerator:
    """
    Orchestrates dynamic question generation for MAESTRO interviews.

    Combines three sources:
    1. Static questions from QuestionBank
    2. Dynamic questions from GapBasedQuestionFactory
    3. Intelligent prioritization from QuestionPrioritizer

    Features:
    - Multiple generation modes (gap_first, balanced, static_first, adaptive)
    - Question deduplication across sources
    - Category-based filtering
    - Phase-aware question selection
    - Progress tracking and completion detection

    Example:
        >>> generator = DynamicQuestionGenerator(mode=GenerationMode.BALANCED)
        >>> result = generator.generate(soul, gaps)
        >>> print(f"Generated {result.total_questions} questions")
        >>>
        >>> # Get questions one by one
        >>> while (q := generator.get_next_question(context)):
        ...     print(f"Ask: {q.text}")
        ...     # ... process answer ...
        ...     context.mark_answered(q.id)
    """

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    # Minimum confidence to reduce questions
    CONFIDENCE_THRESHOLD_HIGH: ClassVar[float] = 0.8
    CONFIDENCE_THRESHOLD_MEDIUM: ClassVar[float] = 0.6

    # Question limits by confidence level
    MAX_QUESTIONS_LOW_CONFIDENCE: ClassVar[int] = 15
    MAX_QUESTIONS_MEDIUM_CONFIDENCE: ClassVar[int] = 10
    MAX_QUESTIONS_HIGH_CONFIDENCE: ClassVar[int] = 5

    # Category question limits (to avoid over-asking in one area)
    MAX_QUESTIONS_PER_CATEGORY: ClassVar[int] = 3

    # Categories that always need at least one question
    REQUIRED_CATEGORIES: ClassVar[List[QuestionCategory]] = [
        QuestionCategory.INTENT,
        QuestionCategory.SCOPE,
        QuestionCategory.THEME_STYLE,
    ]

    def __init__(
        self,
        mode: GenerationMode = GenerationMode.BALANCED,
        priority_strategy: PriorityStrategy = PriorityStrategy.BALANCED,
        language: str = "tr",
    ) -> None:
        """
        Initialize the generator.

        Args:
            mode: Question generation mode
            priority_strategy: Strategy for question prioritization
            language: Language for generated questions
        """
        self.mode = mode
        self.language = language

        # Initialize sub-components
        self.question_bank = QuestionBank()
        self.gap_factory = GapBasedQuestionFactory(language=language)
        self.prioritizer = QuestionPrioritizer(strategy=priority_strategy)

        # State
        self._generated_questions: List[Question] = []
        self._question_id_set: Set[str] = set()
        self._context: Optional[GenerationContext] = None

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def generate(
        self,
        soul: Optional["ProjectSoul"] = None,
        gaps: Optional[GapAnalysis] = None,
        categories: Optional[List[QuestionCategory]] = None,
        max_questions: Optional[int] = None,
    ) -> GenerationResult:
        """
        Generate questions based on soul and gaps.

        Args:
            soul: ProjectSoul for context-aware generation
            gaps: GapAnalysis with identified information gaps
            categories: Filter to specific categories (optional)
            max_questions: Override max question limit (optional)

        Returns:
            GenerationResult with questions and metadata
        """
        # Determine effective mode
        effective_mode = self._determine_effective_mode(soul, gaps)

        # Calculate max questions based on confidence
        if max_questions is None:
            max_questions = self._calculate_max_questions(soul)

        # Generate questions from both sources
        gap_questions = self._generate_gap_questions(gaps, soul)
        static_questions = self._generate_static_questions(soul, gaps)

        # Merge and deduplicate
        all_questions = self._merge_questions(
            gap_questions,
            static_questions,
            effective_mode,
        )

        # Filter by categories if specified
        if categories:
            all_questions = [q for q in all_questions if q.category in categories]

        # Apply category limits
        all_questions = self._apply_category_limits(all_questions)

        # Prioritize
        prioritized = self.prioritizer.prioritize(
            all_questions,
            soul=soul,
            gaps=gaps,
        )

        # Apply max limit
        final_questions = prioritized[:max_questions]

        # Store for get_next_question
        self._generated_questions = final_questions
        self._question_id_set = {q.id for q in final_questions}

        return GenerationResult(
            questions=final_questions,
            gap_based_count=len(gap_questions),
            static_count=len(static_questions),
            total_gaps=gaps.total_gaps if gaps else 0,
            resolved_gaps=gaps.total_gaps - gaps.open_gaps if gaps else 0,
            generation_mode=effective_mode,
        )

    def get_next_question(
        self,
        context: Optional[GenerationContext] = None,
    ) -> Optional[Question]:
        """
        Get the next unanswered question.

        Args:
            context: Generation context with answered question IDs

        Returns:
            Next Question or None if all answered
        """
        if context is None:
            context = self._context or GenerationContext()

        if not context.can_ask_more():
            return None

        for question in self._generated_questions:
            if not context.is_asked(question.id):
                return question

        return None

    def get_questions_by_category(
        self,
        category: QuestionCategory,
        context: Optional[GenerationContext] = None,
    ) -> List[Question]:
        """
        Get unanswered questions in a specific category.

        Args:
            category: Category to filter by
            context: Generation context

        Returns:
            List of unanswered questions in the category
        """
        context = context or GenerationContext()

        return [
            q for q in self._generated_questions
            if q.category == category and not context.is_asked(q.id)
        ]

    def get_remaining_count(
        self,
        context: Optional[GenerationContext] = None,
    ) -> int:
        """
        Get count of remaining questions.

        Args:
            context: Generation context

        Returns:
            Number of unanswered questions
        """
        context = context or GenerationContext()

        return sum(
            1 for q in self._generated_questions
            if not context.is_asked(q.id)
        )

    def is_complete(
        self,
        context: Optional[GenerationContext] = None,
    ) -> bool:
        """
        Check if the interview is complete.

        Args:
            context: Generation context

        Returns:
            True if all questions answered or max reached
        """
        context = context or GenerationContext()

        return self.get_remaining_count(context) == 0 or not context.can_ask_more()

    def regenerate_for_phase(
        self,
        phase: str,
        soul: Optional["ProjectSoul"] = None,
        gaps: Optional[GapAnalysis] = None,
        context: Optional[GenerationContext] = None,
    ) -> List[Question]:
        """
        Regenerate questions relevant to a specific interview phase.

        Args:
            phase: Interview phase (e.g., "DEEP_DIVE", "VALIDATION")
            soul: ProjectSoul for context
            gaps: GapAnalysis for gap-based questions
            context: Generation context

        Returns:
            Phase-relevant questions
        """
        context = context or GenerationContext()
        context.current_phase = phase

        # Generate fresh questions
        result = self.generate(soul, gaps)

        # Filter by phase relevance using prioritizer's phase scoring
        phase_categories = self.prioritizer.PHASE_CATEGORY_MAP.get(phase, [])

        if phase_categories:
            # Prioritize phase-relevant categories
            phase_questions = [
                q for q in result.questions
                if q.category in phase_categories and not context.is_asked(q.id)
            ]
            other_questions = [
                q for q in result.questions
                if q.category not in phase_categories and not context.is_asked(q.id)
            ]
            return phase_questions + other_questions

        return [q for q in result.questions if not context.is_asked(q.id)]

    def create_context(self, max_questions: int = 15) -> GenerationContext:
        """
        Create a new generation context.

        Args:
            max_questions: Maximum questions to ask

        Returns:
            New GenerationContext instance
        """
        self._context = GenerationContext(max_questions=max_questions)
        return self._context

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _determine_effective_mode(
        self,
        soul: Optional["ProjectSoul"],
        gaps: Optional[GapAnalysis],
    ) -> GenerationMode:
        """Determine effective generation mode based on context."""
        if self.mode != GenerationMode.ADAPTIVE:
            return self.mode

        # Adaptive mode logic
        if gaps and gaps.blocking_gaps > 0:
            return GenerationMode.GAP_FIRST

        if soul:
            confidence = getattr(soul, 'overall_confidence', 0.5)
            if confidence >= self.CONFIDENCE_THRESHOLD_HIGH:
                return GenerationMode.STATIC_FIRST
            elif confidence >= self.CONFIDENCE_THRESHOLD_MEDIUM:
                return GenerationMode.BALANCED
            else:
                return GenerationMode.GAP_FIRST

        return GenerationMode.BALANCED

    def _calculate_max_questions(
        self,
        soul: Optional["ProjectSoul"],
    ) -> int:
        """Calculate max questions based on confidence."""
        if not soul:
            return self.MAX_QUESTIONS_LOW_CONFIDENCE

        confidence = getattr(soul, 'overall_confidence', 0.5)

        if confidence >= self.CONFIDENCE_THRESHOLD_HIGH:
            return self.MAX_QUESTIONS_HIGH_CONFIDENCE
        elif confidence >= self.CONFIDENCE_THRESHOLD_MEDIUM:
            return self.MAX_QUESTIONS_MEDIUM_CONFIDENCE
        else:
            return self.MAX_QUESTIONS_LOW_CONFIDENCE

    def _generate_gap_questions(
        self,
        gaps: Optional[GapAnalysis],
        soul: Optional["ProjectSoul"],
    ) -> List[Question]:
        """Generate questions from gap analysis."""
        if not gaps or not gaps.gaps:
            return []

        # Only generate for open gaps
        open_gaps = [g for g in gaps.gaps if not g.is_resolved()]

        return self.gap_factory.create_questions_from_gaps(open_gaps, soul)

    def _generate_static_questions(
        self,
        soul: Optional["ProjectSoul"],
        gaps: Optional[GapAnalysis],
    ) -> List[Question]:
        """Generate questions from static bank."""
        questions = []

        # Determine which categories need questions
        covered_categories = set()
        if gaps:
            for gap in gaps.gaps:
                covered_categories.add(
                    self.gap_factory._map_category(gap.category)
                )

        # Get static questions for uncovered required categories
        for category in self.REQUIRED_CATEGORIES:
            if category not in covered_categories:
                category_questions = self.question_bank.get_by_category(
                    category.value
                )
                if category_questions:
                    questions.extend(category_questions[:2])  # Max 2 per category

        # Add some variety from other categories
        for category in QuestionCategory:
            if category not in self.REQUIRED_CATEGORIES:
                category_questions = self.question_bank.get_by_category(
                    category.value
                )
                if category_questions:
                    questions.append(category_questions[0])  # 1 per category

        return questions

    def _merge_questions(
        self,
        gap_questions: List[Question],
        static_questions: List[Question],
        mode: GenerationMode,
    ) -> List[Question]:
        """Merge questions from both sources with deduplication."""
        seen_ids: Set[str] = set()
        merged: List[Question] = []

        def add_question(q: Question) -> None:
            if q.id not in seen_ids:
                seen_ids.add(q.id)
                merged.append(q)

        if mode == GenerationMode.GAP_FIRST:
            # Gap questions first
            for q in gap_questions:
                add_question(q)
            for q in static_questions:
                add_question(q)

        elif mode == GenerationMode.STATIC_FIRST:
            # Static questions first
            for q in static_questions:
                add_question(q)
            for q in gap_questions:
                add_question(q)

        else:  # BALANCED or ADAPTIVE (resolved to balanced)
            # Interleave: gap, static, gap, static...
            max_len = max(len(gap_questions), len(static_questions))
            for i in range(max_len):
                if i < len(gap_questions):
                    add_question(gap_questions[i])
                if i < len(static_questions):
                    add_question(static_questions[i])

        return merged

    def _apply_category_limits(
        self,
        questions: List[Question],
    ) -> List[Question]:
        """Apply per-category question limits."""
        category_counts: Dict[QuestionCategory, int] = {}
        limited: List[Question] = []

        for question in questions:
            count = category_counts.get(question.category, 0)
            if count < self.MAX_QUESTIONS_PER_CATEGORY:
                limited.append(question)
                category_counts[question.category] = count + 1

        return limited


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def generate_interview_questions(
    soul: Optional["ProjectSoul"] = None,
    gaps: Optional[GapAnalysis] = None,
    mode: GenerationMode = GenerationMode.BALANCED,
    max_questions: int = 15,
    language: str = "tr",
) -> List[Question]:
    """
    Convenience function to generate interview questions.

    Args:
        soul: ProjectSoul for context
        gaps: GapAnalysis for gap-based questions
        mode: Generation mode
        max_questions: Maximum questions
        language: Question language

    Returns:
        List of prioritized questions
    """
    generator = DynamicQuestionGenerator(mode=mode, language=language)
    result = generator.generate(soul, gaps, max_questions=max_questions)
    return result.questions


def get_critical_questions(
    gaps: GapAnalysis,
    language: str = "tr",
) -> List[Question]:
    """
    Get questions for critical gaps only.

    Args:
        gaps: GapAnalysis with identified gaps
        language: Question language

    Returns:
        Questions for critical gaps
    """
    factory = GapBasedQuestionFactory(language=language)
    critical_gaps = gaps.critical_gaps
    return factory.create_questions_from_gaps(critical_gaps)
