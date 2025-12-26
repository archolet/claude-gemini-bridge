"""
MAESTRO Core - The Intelligent Design Wizard

The Maestro orchestrates the interview process and decision making.
It asks questions to understand user intent and automatically selects
the correct design mode and parameters.

Phase 1: Core skeleton with placeholder logic ✓
Phase 2: QuestionBank, Interview Engine ✓
Phase 3: DecisionTree, Context Analyzer ✓
Phase 4: ToolExecutor, Parameter Adapters ✓
Phase 5: MCP Integration, SessionManager, Trifecta ✓
Phase 6: Analytics, UI Enhancement, Smart Intelligence ✓
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any

from gemini_mcp.maestro.decision.context_analyzer import ContextAnalyzer
from gemini_mcp.maestro.decision.tree import DecisionTree
from gemini_mcp.maestro.execution import ToolExecutor
from gemini_mcp.maestro.interview.engine import InterviewEngine
from gemini_mcp.maestro.interview.flow_controller import FlowController
from gemini_mcp.maestro.session.manager import SessionManager
from gemini_mcp.maestro.models import (
    Answer,
    AnswerResult,
    ContextData,
    InterviewState,
    MaestroDecision,
    MaestroSession,
    MaestroStatus,
    Question,
)
from gemini_mcp.maestro.questions.bank import QuestionBank

# Phase 6: Analytics, UI, Intelligence
from gemini_mcp.maestro.analytics import (
    SessionTracker,
    CostAnalyzer,
    QualityMetrics,
)
from gemini_mcp.maestro.ui import (
    MaestroFormatter,
    generate_decision_summary,
    generate_execution_summary,
    generate_session_complete_summary,
    generate_interview_progress,
)
from gemini_mcp.maestro.intelligence import (
    AdaptiveFlow,
    FlowContext,
    PreferenceLearner,
    Recommender,
)

# Phase 7: DNA Integration
from gemini_mcp.orchestration.dna_store import get_dna_store, DNAStore
from gemini_mcp.orchestration.context import DesignDNA

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient

logger = logging.getLogger(__name__)


class Maestro:
    """
    The Maestro - Intelligent Design Wizard for Gemini MCP.

    Orchestrates the interview process and decision making.
    Asks questions to understand user intent and automatically selects
    the correct design mode and parameters.

    Usage:
        maestro = Maestro(client)
        session_id, first_question = await maestro.start_session()
        result = await maestro.process_answer(session_id, answer)
        if isinstance(result, MaestroDecision):
            output = await maestro.execute(session_id, result)
    """

    def __init__(self, client: "GeminiClient"):
        """
        Initialize the Maestro wizard.

        Args:
            client: GeminiClient for API calls
        """
        self.client = client

        # Phase 2 components
        self._question_bank = QuestionBank()
        self._flow_controller = FlowController()
        self._engines: dict[str, InterviewEngine] = {}  # session_id → engine

        # Phase 3 components
        self._decision_tree = DecisionTree(client=client)
        self._context_analyzer = ContextAnalyzer()

        # Phase 4 component
        self._executor = ToolExecutor(client)

        # Phase 5: Session management with TTL and limits
        self._session_manager = SessionManager()

        # Phase 6: Analytics, UI, Intelligence
        self._session_tracker = SessionTracker()
        self._cost_analyzer = CostAnalyzer()
        self._quality_metrics = QualityMetrics()
        self._formatter = MaestroFormatter()
        self._preference_learner = PreferenceLearner()
        self._adaptive_flow = AdaptiveFlow()
        self._recommender = Recommender(
            preference_learner=self._preference_learner,
            adaptive_flow=self._adaptive_flow,
        )

        # Phase 7: DNA persistence for cross-session consistency
        self._dna_store: DNAStore = get_dna_store()

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    async def start_session(
        self,
        project_context: str = "",
        existing_html: str | None = None,
    ) -> tuple[str, Question]:
        """
        Start a new MAESTRO interview session.

        Args:
            project_context: Optional project description for context
            existing_html: Optional existing HTML to refine or match

        Returns:
            Tuple of (session_id, first_question)
        """
        session_id = self._generate_session_id()
        logger.info(f"[Maestro] Starting new session: {session_id}")

        # Create context data
        context_data = ContextData(
            previous_html=existing_html,
            project_context=project_context,
        )

        # Phase 7: Load previous DNA for project continuity
        if project_context:
            try:
                # Search for most recent DNA in this project (any component type)
                previous_entries = self._dna_store.search(
                    project_id=project_context,
                    limit=1,
                )
                if previous_entries:
                    context_data.design_tokens = previous_entries[0].dna.to_dict()
                    logger.info(
                        f"[Maestro] Loaded previous DNA for project: {project_context} "
                        f"(from {previous_entries[0].component_type})"
                    )
            except Exception as e:
                # DNA load failure should not break session start
                logger.warning(f"[Maestro] Failed to load DNA for project {project_context}: {e}")

        # Create initial state
        initial_state = InterviewState(
            status=MaestroStatus.INTERVIEWING,
        )

        # Create session
        session = MaestroSession(
            session_id=session_id,
            state=initial_state,
            context=context_data,
        )

        # Phase 5: Use SessionManager instead of raw dict
        self._session_manager.create(session)

        # Create engine for this session
        engine = self._create_engine(context_data)
        self._engines[session_id] = engine

        # Phase 6: Initialize adaptive flow with context
        flow_context = FlowContext(
            project_context=project_context,
            existing_html=existing_html or "",
        )
        self._adaptive_flow.set_context(flow_context)
        self._recommender.set_context(flow_context)

        # Phase 6: Start session tracking
        self._session_tracker.start_session(session_id)

        # Get first question based on context
        first_question = engine.get_initial_question()
        session.state.current_question_id = first_question.id
        session.state.question_history.append(first_question.id)

        # Phase 6: Format question with rich UI
        formatted_question = self._formatter.format_question(first_question.to_dict())

        logger.info(f"[Maestro] Session started, first question: {first_question.id}")

        return session_id, first_question

    async def process_answer(
        self,
        session_id: str,
        answer: Answer,
    ) -> Question | MaestroDecision:
        """
        Process user's answer and return next question or final decision.

        Args:
            session_id: Active session ID
            answer: User's answer to the current question

        Returns:
            Next Question or MaestroDecision if ready

        Raises:
            ValueError: If session not found or invalid state
        """
        session = self._get_session(session_id)
        engine = self._get_engine(session_id)

        # Validate state
        if session.state.status not in (
            MaestroStatus.INTERVIEWING,
            MaestroStatus.AWAITING_ANSWER,
        ):
            raise ValueError(f"Session not in interview state: {session.state.status}")

        # Process answer through engine
        result = engine.process_answer(session.state, answer)

        if not result.is_valid:
            # Return validation error - re-ask the same question
            logger.warning(f"[Maestro] Invalid answer: {result.error_message}")
            current_question = self._question_bank.get_question(
                session.state.current_question_id
            )
            if current_question:
                return current_question
            raise ValueError(f"Current question not found: {session.state.current_question_id}")

        # Store answer in session state
        session.state.answers.append(answer)
        logger.info(
            f"[Maestro] Answer received for {answer.question_id}: "
            f"{answer.selected_options}"
        )

        # Check if decision should be triggered
        if result.triggers_decision or self._can_make_decision(session):
            logger.info("[Maestro] Sufficient information gathered, making decision")
            session.state.status = MaestroStatus.DECIDING
            return await self._make_decision(session)

        # Get next question
        next_question = engine.get_next_question(session.state)

        if next_question is None:
            # No more questions - make decision
            logger.info("[Maestro] Interview complete, making decision")
            session.state.status = MaestroStatus.DECIDING
            return await self._make_decision(session)

        session.state.current_question_id = next_question.id
        session.state.question_history.append(next_question.id)

        logger.info(f"[Maestro] Next question: {next_question.id}")

        return next_question

    async def get_final_decision(
        self,
        session_id: str,
    ) -> MaestroDecision:
        """
        Force a decision with current answers (skip remaining questions).

        Args:
            session_id: Active session ID

        Returns:
            MaestroDecision based on answers so far
        """
        session = self._get_session(session_id)
        session.state.status = MaestroStatus.DECIDING

        logger.info("[Maestro] Forcing decision with current answers")

        return await self._make_decision(session)

    async def execute(
        self,
        session_id: str,
        decision: MaestroDecision,
        use_trifecta: bool = False,
        quality_target: str = "production",
    ) -> dict[str, Any]:
        """
        Execute the selected design mode with gathered parameters.

        Args:
            session_id: Active session ID
            decision: The decision to execute
            use_trifecta: Use multi-agent pipeline for higher quality (default: False)
            quality_target: Quality level - draft, production, high, premium, enterprise
                           (default: "production")

        Returns:
            Result from the design tool
        """
        session = self._get_session(session_id)
        session.state.status = MaestroStatus.EXECUTING

        logger.info(
            f"[Maestro] Executing mode: {decision.mode} "
            f"(trifecta={use_trifecta}, quality={quality_target})"
        )

        # Phase 5: Use ToolExecutor with Trifecta support
        result = await self._executor.execute(
            decision,
            session.context,
            use_trifecta=use_trifecta,
            quality_target=quality_target,
        )

        session.state.status = MaestroStatus.COMPLETE

        # Phase 6: Track execution metrics
        self._session_tracker.end_session(session_id)
        self._session_tracker.track_event(session_id, "execution_complete", {
            "mode": decision.mode,
            "use_trifecta": use_trifecta,
            "quality_target": quality_target,
        })

        # Phase 7: Save DNA for cross-session consistency
        if result.get("status") != "failed" and result.get("design_tokens"):
            try:
                dna = DesignDNA.from_dict(result.get("design_tokens", {}))
                project_id = session.context.project_context or "default"
                component_type = decision.parameters.get("component_type", "unknown")
                theme = decision.parameters.get("theme", "modern-minimal")

                self._dna_store.save(
                    component_type=component_type,
                    theme=theme,
                    dna=dna,
                    project_id=project_id,
                )
                logger.info(
                    f"[Maestro] Saved DNA for {component_type} ({theme}) in project {project_id}"
                )
            except Exception as e:
                # Don't fail execution if DNA save fails
                logger.warning(f"[Maestro] Failed to save DNA: {e}")

        # Phase 6: Learn from session for future recommendations
        self._preference_learner.learn_from_session({
            "answers": {a.question_id: a.selected_options for a in session.state.answers},
            "decision": {
                "mode": decision.mode,
                "parameters": decision.parameters,
            },
        })

        # Phase 6: Generate execution summary
        # Add mode to result for summary generation
        result["mode"] = decision.mode
        cost_breakdown = self._cost_analyzer.get_session_cost(session_id)
        execution_summary = generate_execution_summary(
            result=result,
            cost_breakdown=cost_breakdown.to_dict() if cost_breakdown else None,
        )

        # Add summary to result
        result["execution_summary"] = execution_summary
        decision_summary = generate_decision_summary(decision)
        result["session_complete_summary"] = generate_session_complete_summary(
            decision_summary=decision_summary,
            execution_summary=execution_summary,
        )

        logger.info("[Maestro] Execution complete")

        return result

    def abort_session(self, session_id: str) -> bool:
        """
        Abort an active session.

        Args:
            session_id: Session to abort

        Returns:
            True if session was aborted, False if not found
        """
        # Phase 5: Use SessionManager
        session = self._session_manager.get(session_id)
        if session is None:
            return False

        session.state.status = MaestroStatus.ABORTED

        # Cleanup engine
        if session_id in self._engines:
            del self._engines[session_id]

        # Delete from SessionManager
        self._session_manager.delete(session_id)

        logger.info(f"[Maestro] Session aborted: {session_id}")

        return True

    def get_session(self, session_id: str) -> MaestroSession | None:
        """Get a session by ID (public accessor)."""
        return self._session_manager.get(session_id)

    def get_session_info(self, session_id: str) -> dict | None:
        """
        Get session metadata without returning full session object.

        Useful for MCP tools to check session status without exposing internals.
        """
        return self._session_manager.get_session_info(session_id)

    def list_sessions(self) -> list[str]:
        """List all active session IDs."""
        return self._session_manager.list_sessions()

    @property
    def active_session_count(self) -> int:
        """Get count of active sessions."""
        return self._session_manager.active_count

    def get_progress(self, session_id: str) -> float:
        """
        Get the interview progress for a session.

        Args:
            session_id: Active session ID

        Returns:
            Progress as float between 0.0 and 1.0
        """
        session = self._get_session(session_id)
        engine = self._get_engine(session_id)
        return engine.calculate_progress(session.state)

    # =========================================================================
    # PHASE 6: ANALYTICS, RECOMMENDATIONS, RICH UI
    # =========================================================================

    def get_recommendations(self) -> dict[str, Any]:
        """
        Get smart recommendations for design choices.

        Phase 6 feature: Uses PreferenceLearner and Recommender
        to provide intelligent defaults and suggestions.

        Returns:
            Dictionary with theme, mode, quality, and default recommendations
        """
        return self._recommender.get_all_recommendations()

    def get_analytics(self) -> dict[str, Any]:
        """
        Get session analytics and usage metrics.

        Phase 6 feature: Provides cost, quality, and usage insights.

        Returns:
            Dictionary with analytics data
        """
        return {
            "session_tracker": self._session_tracker.to_dict(),
            "cost_summary": self._cost_analyzer.get_summary(),
            "quality_summary": self._quality_metrics.get_summary(),
        }

    def get_formatted_progress(self, session_id: str) -> dict[str, Any]:
        """
        Get rich formatted progress display.

        Phase 6 feature: Returns visual progress bar and status.

        Args:
            session_id: Active session ID

        Returns:
            Formatted progress with visual elements
        """
        session = self._get_session(session_id)
        progress = self.get_progress(session_id)
        current_category = self._get_current_category(session)

        return generate_interview_progress(
            progress=progress,
            current_step=len(session.state.answers) + 1,
            total_steps=self._estimate_total_steps(session),
            current_category=current_category,
        )

    def get_decision_summary(self, decision: MaestroDecision) -> dict[str, Any]:
        """
        Get rich formatted decision summary.

        Phase 6 feature: Returns human-readable decision explanation.

        Args:
            decision: The MaestroDecision to summarize

        Returns:
            Formatted decision summary
        """
        return generate_decision_summary(
            mode=decision.mode,
            confidence=decision.confidence,
            reasoning=decision.reasoning,
            parameters=decision.parameters,
        )

    def record_api_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """
        Record an API call for cost analysis.

        Phase 6 feature: Tracks token usage for cost estimation.

        Args:
            model: Model name (e.g., "gemini-3-pro")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        """
        self._cost_analyzer.record_call(model, input_tokens, output_tokens)

    def record_quality_score(
        self,
        session_id: str,
        score: float,
        dimensions: dict[str, float] | None = None,
    ) -> None:
        """
        Record a quality score for metrics.

        Phase 6 feature: Tracks design quality for analytics.

        Args:
            session_id: Session to record score for
            score: Overall quality score (0-10)
            dimensions: Optional dimension scores
        """
        from gemini_mcp.maestro.analytics import QualityScore
        quality_score = QualityScore.from_overall(score, dimensions)
        self._quality_metrics.record_score(session_id, quality_score)

    # =========================================================================
    # PHASE 7: DNA PERSISTENCE
    # =========================================================================

    def get_dna_history(
        self,
        project_id: str | None = None,
        component_type: str | None = None,
        theme: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get DNA history for recommendations and continuity.

        Phase 7 feature: Enables cross-session design consistency.

        Args:
            project_id: Filter by project
            component_type: Filter by component type
            theme: Filter by theme
            limit: Maximum results

        Returns:
            List of DNA entries with metadata
        """
        entries = self._dna_store.search(
            project_id=project_id,
            component_type=component_type,
            theme=theme,
            limit=limit,
        )
        return [
            {
                "dna_id": e.dna_id,
                "component_type": e.component_type,
                "theme": e.theme,
                "project_id": e.project_id,
                "created_at": e.created_at,
                "tokens": e.dna.to_dict(),
            }
            for e in entries
        ]

    def get_dna_stats(self) -> dict[str, Any]:
        """
        Get DNA storage statistics.

        Phase 7 feature: Monitor DNA storage usage.

        Returns:
            Dictionary with storage stats
        """
        return self._dna_store.get_stats()

    @property
    def dna_store(self) -> DNAStore:
        """Expose DNAStore for direct access (used by Recommender)."""
        return self._dna_store

    def _get_current_category(self, session: MaestroSession) -> str:
        """Get current question category for progress display."""
        if session.state.current_question_id:
            question = self._question_bank.get_question(session.state.current_question_id)
            if question:
                return question.category
        return "intent"

    def _estimate_total_steps(self, session: MaestroSession) -> int:
        """Estimate total interview steps."""
        # Base estimate + adaptive adjustments
        base = 5
        if session.context.previous_html:
            base -= 1  # Refine mode is shorter
        return base

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"maestro_{uuid.uuid4().hex[:12]}"

    def _get_session(self, session_id: str) -> MaestroSession:
        """Get session or raise error if not found/expired."""
        session = self._session_manager.get(session_id)
        if session is None:
            raise ValueError(f"Session not found or expired: {session_id}")
        return session

    def _get_engine(self, session_id: str) -> InterviewEngine:
        """Get engine for session or raise error if not found."""
        if session_id not in self._engines:
            raise ValueError(f"Engine not found for session: {session_id}")
        return self._engines[session_id]

    def _create_engine(self, context: ContextData) -> InterviewEngine:
        """Create a new InterviewEngine for a session."""
        return InterviewEngine(
            question_bank=self._question_bank,
            flow_controller=self._flow_controller,
            context=context,
        )

    def _can_make_decision(self, session: MaestroSession) -> bool:
        """
        Check if we have enough information to make a decision.

        Phase 3: This will use DecisionTree analysis.
        For now, we rely on InterviewEngine.is_complete().
        """
        engine = self._engines.get(session.session_id)
        if engine:
            return engine.is_complete(session.state)
        return len(session.state.answers) >= 3

    async def _make_decision(self, session: MaestroSession) -> MaestroDecision:
        """
        Make the final design mode decision using DecisionTree.

        Uses AI-powered decision making with:
        - Lambda-based MODE_RULES for mode selection
        - 6-dimension weighted confidence scoring
        - Optional Gemini reasoning for low-confidence decisions

        Args:
            session: Active Maestro session

        Returns:
            MaestroDecision with selected mode and parameters
        """
        decision = await self._decision_tree.make_decision(
            state=session.state,
            previous_html=session.context.previous_html,
            project_context=session.context.project_context or "",
        )

        session.state.status = MaestroStatus.CONFIRMING
        logger.info(
            f"[Maestro] Decision: {decision.mode} "
            f"(confidence={decision.confidence:.2f})"
        )

        return decision

