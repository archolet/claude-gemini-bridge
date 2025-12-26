"""
MAESTRO Interview Engine - Phase 2

The central engine that orchestrates the interview process.
Manages question flow, answer processing, and progress tracking.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from gemini_mcp.maestro.interview.flow_controller import FlowController
from gemini_mcp.maestro.models import (
    Answer,
    AnswerResult,
    InterviewState,
    Question,
    QuestionCategory,
)
from gemini_mcp.maestro.questions.bank import QuestionBank
from gemini_mcp.maestro.questions.validators import validate_answer

if TYPE_CHECKING:
    from gemini_mcp.maestro.models import ContextData

logger = logging.getLogger(__name__)


class InterviewEngine:
    """
    The Interview Engine - Orchestrates the question flow.

    Manages:
    - Question selection based on priority and skip rules
    - Answer validation and processing
    - Follow-up question queue
    - Progress calculation

    Usage:
        engine = InterviewEngine(
            question_bank=QuestionBank(),
            flow_controller=FlowController(),
            context=context_data,
        )
        next_q = engine.get_next_question(state)
        result = engine.process_answer(state, answer)
    """

    def __init__(
        self,
        question_bank: QuestionBank,
        flow_controller: FlowController,
        context: "ContextData",
    ) -> None:
        """
        Initialize the InterviewEngine.

        Args:
            question_bank: Repository of all questions
            flow_controller: Skip rules and follow-up triggers
            context: Design context (previous HTML, project info)
        """
        self.question_bank = question_bank
        self.flow_controller = flow_controller
        self.context = context

        # Follow-up question queue (prioritized over normal flow)
        self._follow_up_queue: list[str] = []

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def get_next_question(self, state: InterviewState) -> Question | None:
        """
        Get the next question to ask.

        Algorithm:
        1. Check follow-up queue first
        2. Iterate through categories by priority
        3. For each category, find unanswered questions
        4. Apply skip rules and show_when conditions
        5. Return first valid question or None if complete

        Args:
            state: Current interview state

        Returns:
            Next Question or None if interview is complete
        """
        # 1. Check follow-up queue first
        while self._follow_up_queue:
            follow_up_id = self._follow_up_queue.pop(0)
            question = self.question_bank.get_question(follow_up_id)

            if question is None:
                logger.warning(f"Follow-up question not found: {follow_up_id}")
                continue

            # Check if already answered
            if state.has_answer(follow_up_id):
                continue

            # Check skip rules
            if self.should_skip_question(question, state):
                continue

            logger.debug(f"Returning follow-up question: {follow_up_id}")
            return question

        # 2. Iterate through categories by priority
        for category in self.question_bank.get_categories_by_priority():
            # Get questions in this category
            questions = self.question_bank.get_questions_by_category(category)

            for question in questions:
                # Skip if already answered
                if state.has_answer(question.id):
                    continue

                # Check skip rules
                if self.should_skip_question(question, state):
                    continue

                # Check show_when condition
                if not self.flow_controller.evaluate_show_when(
                    question.show_when, state
                ):
                    continue

                logger.debug(f"Returning question: {question.id}")
                return question

        # No more questions - interview complete
        logger.debug("Interview complete - no more questions")
        return None

    def process_answer(
        self,
        state: InterviewState,
        answer: Answer,
    ) -> AnswerResult:
        """
        Process a user's answer.

        Steps:
        1. Get the question being answered
        2. Validate the answer
        3. If valid, check for follow-up triggers
        4. Calculate progress
        5. Check if interview is complete

        Args:
            state: Current interview state
            answer: The user's answer

        Returns:
            AnswerResult with validation status and follow-ups
        """
        # Get the question
        question = self.question_bank.get_question(answer.question_id)
        if question is None:
            return AnswerResult(
                is_valid=False,
                error_message=f"Soru bulunamadı: {answer.question_id}",
            )

        # Validate the answer
        validation = validate_answer(answer, question)
        if not validation.is_valid:
            return AnswerResult(
                is_valid=False,
                error_message=validation.error_message,
                progress=self.calculate_progress(state),
            )

        # Check for follow-up triggers
        follow_ups = self.flow_controller.get_follow_ups(
            answer.question_id,
            answer.selected_options,
        )

        # Add follow-ups to queue
        for follow_up_id in follow_ups:
            if follow_up_id not in self._follow_up_queue:
                self._follow_up_queue.append(follow_up_id)

        # Calculate progress
        progress = self.calculate_progress(state)

        # Check if interview is complete
        # Note: We check AFTER adding the answer to state
        triggers_decision = self._check_triggers_decision(state, answer)

        return AnswerResult(
            is_valid=True,
            follow_ups=follow_ups,
            triggers_decision=triggers_decision,
            progress=progress,
        )

    def should_skip_question(
        self,
        question: Question,
        state: InterviewState,
    ) -> bool:
        """
        Check if a question should be skipped.

        Args:
            question: The question to check
            state: Current interview state

        Returns:
            True if question should be skipped
        """
        return self.flow_controller.should_skip(
            question.id,
            question.category,
            state,
        )

    def calculate_progress(self, state: InterviewState) -> float:
        """
        Calculate interview progress percentage.

        Formula: answered_required / total_required

        Args:
            state: Current interview state

        Returns:
            Progress as float between 0.0 and 1.0
        """
        required_questions = self.question_bank.get_required_questions()

        if not required_questions:
            return 1.0

        answered = 0
        total = 0

        for question in required_questions:
            # Skip questions that would be skipped by rules
            if self.should_skip_question(question, state):
                continue

            # Check show_when
            if not self.flow_controller.evaluate_show_when(
                question.show_when, state
            ):
                continue

            total += 1
            if state.has_answer(question.id):
                answered += 1

        if total == 0:
            return 1.0

        return answered / total

    def is_complete(self, state: InterviewState) -> bool:
        """
        Check if the interview is complete.

        The interview is complete when get_next_question returns None.

        Args:
            state: Current interview state

        Returns:
            True if all required questions are answered
        """
        return self.get_next_question(state) is None

    def get_initial_question(self) -> Question:
        """
        Get the first question based on context.

        Returns:
            The appropriate starting question
        """
        has_existing = self.context.previous_html is not None
        return self.question_bank.get_initial_question(has_existing)

    def add_follow_up(self, question_id: str) -> None:
        """
        Manually add a question to the follow-up queue.

        Args:
            question_id: Question ID to add
        """
        if question_id not in self._follow_up_queue:
            self._follow_up_queue.append(question_id)

    def clear_follow_up_queue(self) -> None:
        """Clear the follow-up queue."""
        self._follow_up_queue.clear()

    def get_pending_follow_ups(self) -> list[str]:
        """Get the current follow-up queue."""
        return list(self._follow_up_queue)

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _check_triggers_decision(
        self,
        state: InterviewState,
        answer: Answer,
    ) -> bool:
        """
        Check if this answer triggers the decision phase.

        We trigger decision when:
        - All required questions are answered
        - The follow-up queue is empty
        - Progress >= 1.0

        Args:
            state: Current interview state (before adding this answer)
            answer: The answer just given

        Returns:
            True if decision should be triggered
        """
        # Check if follow-up queue is empty FIRST
        # (is_complete calls get_next_question which pops from queue!)
        if self._follow_up_queue:
            return False

        # Check if we have enough answers
        # We need to simulate adding this answer to check
        temp_state = InterviewState(
            status=state.status,
            current_question_id=state.current_question_id,
            answers=state.answers + [answer],
            question_history=state.question_history,
        )

        # Check if complete with this answer
        return self.is_complete(temp_state)

    def _get_category_priority(self, category: QuestionCategory) -> int:
        """Get the priority of a category (lower = higher priority)."""
        config = QuestionBank.CATEGORY_CONFIG.get(category, {})
        return config.get("priority", 99)
