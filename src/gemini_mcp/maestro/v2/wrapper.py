"""
MAESTRO v2 Wrapper

Main integration point for MAESTRO v2.0 - wraps existing Maestro
with soul-based intelligence while maintaining backward compatibility.

Key Features:
- Soul extraction from design briefs
- Dynamic question generation from gaps
- Graceful fallback to v1 on errors
- Feature flag controlled activation

Usage:
    >>> from gemini_mcp.maestro.v2 import MAESTROv2Wrapper
    >>> from gemini_mcp.client import GeminiClient
    >>>
    >>> client = GeminiClient()
    >>> wrapper = MAESTROv2Wrapper(client)
    >>>
    >>> # With design brief (v2 mode)
    >>> session, question = await wrapper.start_session(
    ...     design_brief="Modern fintech dashboard for Turkish market"
    ... )
    >>> print(session.soul.project_name)
    'Fintech Dashboard'
    >>>
    >>> # Without brief (falls back to v1)
    >>> session, question = await wrapper.start_session()

Environment Variables:
    MAESTRO_V2_ENABLED: Enable v2 features (default: True)
    MAESTRO_GRACEFUL_FALLBACK: Enable graceful fallback (default: True)
    MAESTRO_EXTRACTION_TIMEOUT: Timeout for soul extraction (default: 30s)
    MAESTRO_MIN_CONFIDENCE: Minimum confidence to proceed (default: 0.3)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from gemini_mcp.maestro.config import get_config, MAESTROConfig
from gemini_mcp.maestro.core import Maestro
from gemini_mcp.maestro.models import Answer, MaestroDecision, Question
from gemini_mcp.maestro.v2.session import (
    SoulAwareSession,
    SessionState,
    InterviewPhase,
)
from gemini_mcp.maestro.v2.fallback import FallbackHandler, FallbackReason
from gemini_mcp.maestro.soul import SoulExtractor, ExtractionResult
from gemini_mcp.maestro.soul.gaps import GapDetector
from gemini_mcp.maestro.models.soul import ProjectSoul

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient

logger = logging.getLogger(__name__)


@dataclass
class V2Metrics:
    """Metrics for v2 wrapper operations."""

    sessions_started: int = 0
    sessions_with_soul: int = 0
    sessions_fallback: int = 0
    total_extractions: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    avg_extraction_time_ms: float = 0.0
    avg_confidence: float = 0.0

    # Running totals for averages
    _extraction_times: List[float] = field(default_factory=list)
    _confidences: List[float] = field(default_factory=list)

    def record_extraction(
        self,
        success: bool,
        time_ms: float,
        confidence: float = 0.0,
    ) -> None:
        """Record an extraction attempt."""
        self.total_extractions += 1
        if success:
            self.successful_extractions += 1
            self._extraction_times.append(time_ms)
            self._confidences.append(confidence)
            # Update running averages
            self.avg_extraction_time_ms = sum(self._extraction_times) / len(self._extraction_times)
            self.avg_confidence = sum(self._confidences) / len(self._confidences)
        else:
            self.failed_extractions += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sessions": {
                "started": self.sessions_started,
                "with_soul": self.sessions_with_soul,
                "fallback": self.sessions_fallback,
            },
            "extractions": {
                "total": self.total_extractions,
                "successful": self.successful_extractions,
                "failed": self.failed_extractions,
                "success_rate": (
                    self.successful_extractions / self.total_extractions
                    if self.total_extractions > 0 else 0.0
                ),
            },
            "averages": {
                "extraction_time_ms": self.avg_extraction_time_ms,
                "confidence": self.avg_confidence,
            },
        }


class MAESTROv2Wrapper:
    """
    MAESTRO v2.0 Wrapper - Intelligent Design Interview System.

    Wraps the existing Maestro class to add:
    - Soul extraction from design briefs
    - Dynamic gap-based questioning
    - Intelligent interview flow
    - Graceful fallback to static Q&A

    The wrapper pattern ensures backward compatibility while
    enabling incremental adoption of v2 features.

    Example:
        >>> wrapper = MAESTROv2Wrapper(client)
        >>>
        >>> # Start with design brief
        >>> session, question = await wrapper.start_session(
        ...     design_brief="E-commerce landing page for organic food store"
        ... )
        >>>
        >>> # Check if v2 is active
        >>> if session.is_v2_active:
        ...     print(f"Project: {session.soul.project_name}")
        ...     print(f"Confidence: {session.confidence:.0%}")
        ...
        >>> # Process answers
        >>> result = await wrapper.process_answer(session.session_id, answer)
    """

    def __init__(
        self,
        client: "GeminiClient",
        config: Optional[MAESTROConfig] = None,
    ):
        """
        Initialize the v2 wrapper.

        Args:
            client: GeminiClient for API calls
            config: Optional config (uses global if not provided)
        """
        self._client = client
        self._config = config or get_config()

        # Core components
        self._legacy_maestro = Maestro(client)
        self._soul_extractor = SoulExtractor()
        self._fallback_handler = FallbackHandler()
        self._gap_detector = GapDetector()

        # Session storage (parallel to legacy)
        self._sessions: Dict[str, SoulAwareSession] = {}

        # Metrics
        self._metrics = V2Metrics()

        logger.info(
            f"[MAESTROv2] Initialized "
            f"(v2_enabled={self._config.V2_ENABLED}, "
            f"fallback={self._config.GRACEFUL_FALLBACK})"
        )

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    async def start_session(
        self,
        design_brief: Optional[str] = None,
        project_context: str = "",
        existing_html: Optional[str] = None,
    ) -> Tuple[SoulAwareSession, Question]:
        """
        Start a new MAESTRO v2 session.

        If a design brief is provided and v2 is enabled, extracts ProjectSoul
        and generates dynamic questions. Otherwise falls back to v1 static Q&A.

        Args:
            design_brief: Optional design brief for soul extraction
            project_context: Optional project description
            existing_html: Optional existing HTML for context

        Returns:
            Tuple of (SoulAwareSession, first Question)

        Example:
            >>> session, question = await wrapper.start_session(
            ...     design_brief="Modern SaaS dashboard with dark mode"
            ... )
            >>> print(session.soul.project_name)
            'SaaS Dashboard'
        """
        self._metrics.sessions_started += 1

        # Create soul-aware session
        session = SoulAwareSession.create(
            design_brief=design_brief,
            existing_html=existing_html,
            project_context=project_context,
        )
        self._sessions[session.session_id] = session

        # Check if v2 should be used
        if self._should_use_v2(design_brief):
            try:
                # Extract soul from brief
                session.transition_to(
                    SessionState.EXTRACTING_SOUL,
                    reason="Starting soul extraction",
                )
                session.advance_phase(
                    InterviewPhase.SOUL_EXTRACTION,
                    "Brief received",
                )

                soul = await self._extract_soul_with_timeout(
                    session,
                    design_brief,
                    existing_html,
                )

                if soul:
                    session.set_soul(soul, self._metrics.avg_extraction_time_ms)
                    self._metrics.sessions_with_soul += 1

                    # Generate first question from gaps
                    first_question = self._get_first_soul_question(session)
                    if first_question:
                        session.record_question_asked()
                        return session, first_question

            except Exception as e:
                logger.error(f"[MAESTROv2] Soul extraction failed: {e}")
                if self._fallback_handler.should_fallback(exception=e):
                    session.enter_fallback(str(e))
                    self._metrics.sessions_fallback += 1
                else:
                    raise

        # Fall back to v1 if no soul or fallback triggered
        return await self._start_legacy_session(session, project_context, existing_html)

    async def process_answer(
        self,
        session_id: str,
        answer: Answer,
    ) -> Union[Question, MaestroDecision]:
        """
        Process user's answer and return next question or decision.

        For v2 sessions, updates the soul with gap resolutions.
        For fallback sessions, delegates to legacy Maestro.

        Args:
            session_id: Active session ID
            answer: User's answer

        Returns:
            Next Question or MaestroDecision if ready
        """
        session = self._get_session(session_id)

        if session.is_v2_active:
            return await self._process_v2_answer(session, answer)
        else:
            return await self._legacy_maestro.process_answer(session_id, answer)

    async def get_decision(
        self,
        session_id: str,
    ) -> MaestroDecision:
        """
        Force a decision with current answers.

        Args:
            session_id: Active session ID

        Returns:
            MaestroDecision based on current state
        """
        session = self._get_session(session_id)

        if session.is_v2_active:
            return await self._make_soul_decision(session)
        else:
            return await self._legacy_maestro.get_final_decision(session_id)

    async def execute(
        self,
        session_id: str,
        decision: MaestroDecision,
        use_trifecta: bool = False,
        quality_target: str = "production",
    ) -> Dict[str, Any]:
        """
        Execute the design decision.

        For v2 sessions, enriches parameters with soul context.

        Args:
            session_id: Active session ID
            decision: The decision to execute
            use_trifecta: Use multi-agent pipeline
            quality_target: Quality level

        Returns:
            Design result
        """
        session = self._get_session(session_id)

        # Enrich decision with soul context
        if session.is_v2_active and session.soul:
            decision = self._enrich_decision_with_soul(decision, session.soul)

        # Execute via legacy (handles all modes)
        result = await self._legacy_maestro.execute(
            session_id=session.legacy_session.session_id,
            decision=decision,
            use_trifecta=use_trifecta,
            quality_target=quality_target,
        )

        # Update session state
        session.transition_to(
            SessionState.COMPLETE,
            reason="Execution complete",
        )
        session.advance_phase(InterviewPhase.COMPLETE, "Design generated")

        return result

    def abort_session(self, session_id: str) -> bool:
        """
        Abort an active session.

        Args:
            session_id: Session to abort

        Returns:
            True if aborted, False if not found
        """
        if session_id not in self._sessions:
            return False

        session = self._sessions[session_id]
        session.transition_to(SessionState.ABORTED, reason="User requested abort")

        # Also abort legacy session
        self._legacy_maestro.abort_session(session_id)

        del self._sessions[session_id]
        return True

    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================

    def get_session(self, session_id: str) -> Optional[SoulAwareSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[str]:
        """List all active session IDs."""
        return list(self._sessions.keys())

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session summary."""
        session = self._sessions.get(session_id)
        if session:
            return session.to_summary()
        return None

    # =========================================================================
    # METRICS & ANALYTICS
    # =========================================================================

    def get_metrics(self) -> Dict[str, Any]:
        """Get v2 wrapper metrics."""
        return {
            "v2_metrics": self._metrics.to_dict(),
            "legacy_metrics": self._legacy_maestro.get_analytics(),
            "config": {
                "v2_enabled": self._config.V2_ENABLED,
                "graceful_fallback": self._config.GRACEFUL_FALLBACK,
                "min_confidence": self._config.MIN_CONFIDENCE,
                "extraction_timeout": self._config.EXTRACTION_TIMEOUT,
            },
        }

    def get_recommendations(self) -> Dict[str, Any]:
        """Get smart recommendations."""
        return self._legacy_maestro.get_recommendations()

    # =========================================================================
    # PRIVATE: SOUL EXTRACTION
    # =========================================================================

    def _should_use_v2(self, design_brief: Optional[str]) -> bool:
        """Check if v2 should be used for this session."""
        if not self._config.V2_ENABLED:
            logger.debug("[MAESTROv2] v2 disabled via config")
            return False

        if not design_brief:
            logger.debug("[MAESTROv2] No design brief provided")
            return False

        if len(design_brief.strip()) < 10:
            logger.debug("[MAESTROv2] Brief too short for extraction")
            return False

        return True

    async def _extract_soul_with_timeout(
        self,
        session: SoulAwareSession,
        design_brief: str,
        existing_html: Optional[str] = None,
    ) -> Optional[ProjectSoul]:
        """
        Extract soul with timeout protection.

        Args:
            session: Active session
            design_brief: User's design brief
            existing_html: Optional existing HTML

        Returns:
            ProjectSoul or None on failure
        """
        start_time = time.time()
        timeout = self._config.EXTRACTION_TIMEOUT

        try:
            # Run extraction with timeout
            extraction_task = self._soul_extractor.extract(
                design_brief,
                existing_html=existing_html,
            )

            result: ExtractionResult = await asyncio.wait_for(
                extraction_task,
                timeout=timeout,
            )

            elapsed_ms = (time.time() - start_time) * 1000

            # Check confidence
            if result.soul.confidence_scores:
                confidence = result.soul.confidence_scores.overall
                if confidence < self._config.MIN_CONFIDENCE:
                    logger.warning(
                        f"[MAESTROv2] Low confidence: {confidence:.2f} "
                        f"(min: {self._config.MIN_CONFIDENCE})"
                    )
                    if self._fallback_handler.should_fallback(confidence=confidence):
                        self._metrics.record_extraction(False, elapsed_ms)
                        return None

            self._metrics.record_extraction(True, elapsed_ms, confidence)
            logger.info(
                f"[MAESTROv2] Soul extracted: {result.soul.project_name} "
                f"(confidence: {confidence:.2f}, time: {elapsed_ms:.0f}ms)"
            )

            return result.soul

        except asyncio.TimeoutError:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.warning(f"[MAESTROv2] Extraction timeout after {elapsed_ms:.0f}ms")
            self._metrics.record_extraction(False, elapsed_ms)

            if self._fallback_handler.should_fallback(exception=TimeoutError()):
                return None
            raise

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"[MAESTROv2] Extraction error: {e}")
            self._metrics.record_extraction(False, elapsed_ms)
            raise

    # =========================================================================
    # PRIVATE: QUESTION FLOW
    # =========================================================================

    def _get_first_soul_question(self, session: SoulAwareSession) -> Optional[Question]:
        """Get the first question based on soul gaps."""
        if not session.soul:
            return None

        # Get priority questions from gaps
        questions = self._gap_detector.get_priority_questions(
            session.soul.source_brief_parsed,
            max_questions=5,
        ) if hasattr(session.soul, 'source_brief_parsed') and session.soul.source_brief_parsed else []

        # Convert to Question objects
        for i, question_text in enumerate(questions):
            question = Question(
                id=f"soul_gap_{i}",
                category="intent",  # Will be categorized properly
                text=question_text,
                options=[],  # Free text for now
                required=True,
            )
            session.add_soul_questions([question])

        # Return first unresolved gap question
        question_text = session.get_next_question()
        if question_text:
            from gemini_mcp.maestro.models import QuestionCategory, QuestionType
            return Question(
                id="soul_q_0",
                category=QuestionCategory.INTENT,
                text=question_text,
                question_type=QuestionType.TEXT_INPUT,
                required=True,
            )

        return None

    async def _process_v2_answer(
        self,
        session: SoulAwareSession,
        answer: Answer,
    ) -> Union[Question, MaestroDecision]:
        """Process answer in v2 mode."""
        # Update soul with answer
        if answer.free_text:
            # Find matching gap
            for gap in session.unresolved_gaps:
                session.update_soul(gap.id, answer.free_text)
                break

        # Check if we have enough info to decide
        if not session.critical_gaps and session.confidence >= self._config.MIN_CONFIDENCE:
            session.transition_to(SessionState.DECIDING, reason="Sufficient confidence")
            return await self._make_soul_decision(session)

        # Get next question
        question_text = session.get_next_question()
        if question_text:
            session.record_question_asked()
            from gemini_mcp.maestro.models import QuestionCategory, QuestionType
            return Question(
                id=f"soul_q_{session.total_questions_asked}",
                category=QuestionCategory.INTENT,
                text=question_text,
                question_type=QuestionType.TEXT_INPUT,
                required=True,
            )

        # No more questions, make decision
        return await self._make_soul_decision(session)

    async def _make_soul_decision(
        self,
        session: SoulAwareSession,
    ) -> MaestroDecision:
        """Make decision based on soul context."""
        session.transition_to(SessionState.SYNTHESIZING, reason="Making decision")
        session.advance_phase(InterviewPhase.SYNTHESIS, "Decision time")

        # Use legacy decision tree but enrich with soul
        decision = await self._legacy_maestro.get_final_decision(
            session.legacy_session.session_id
        )

        if session.soul:
            decision = self._enrich_decision_with_soul(decision, session.soul)

        session.transition_to(SessionState.DECIDING, reason="Decision ready")

        return decision

    def _enrich_decision_with_soul(
        self,
        decision: MaestroDecision,
        soul: ProjectSoul,
    ) -> MaestroDecision:
        """Enrich decision parameters with soul context."""
        params = decision.parameters.copy()

        # Add soul-derived parameters
        if soul.brand_personality:
            params["brand_personality"] = soul.brand_personality.dominant_trait
            params["personality_archetype"] = soul.brand_personality.personality_archetype

        if soul.target_audience:
            params["target_audience"] = {
                "age_range": f"{soul.target_audience.age_min}-{soul.target_audience.age_max}",
                "tech_savviness": soul.target_audience.tech_savviness,
            }

        if soul.visual_language:
            params["visual_style"] = {
                "density": soul.visual_language.density.value if soul.visual_language.density else "comfortable",
                "motion_preference": soul.visual_language.motion_preference.value if soul.visual_language.motion_preference else "subtle",
                "contrast_preference": soul.visual_language.contrast_preference.value if soul.visual_language.contrast_preference else "medium",
            }

        if soul.emotional_framework:
            params["emotional_goals"] = {
                "primary_emotion": soul.emotional_framework.primary_emotion.value if soul.emotional_framework.primary_emotion else "trust",
                "emotional_journey": soul.emotional_framework.journey_arc,
            }

        # Create enriched decision
        return MaestroDecision(
            mode=decision.mode,
            confidence=max(decision.confidence, soul.confidence_scores.overall if soul.confidence_scores else 0),
            reasoning=f"{decision.reasoning}\n\nSoul Context: {soul.project_name} ({soul.tagline or 'No tagline'})",
            parameters=params,
            alternatives=decision.alternatives,
        )

    # =========================================================================
    # PRIVATE: LEGACY FALLBACK
    # =========================================================================

    async def _start_legacy_session(
        self,
        session: SoulAwareSession,
        project_context: str,
        existing_html: Optional[str],
    ) -> Tuple[SoulAwareSession, Question]:
        """Start a legacy v1 session."""
        # Start legacy session
        legacy_id, first_question = await self._legacy_maestro.start_session(
            project_context=project_context,
            existing_html=existing_html,
        )

        # Update session with legacy ID mapping
        session.legacy_session.session_id = legacy_id

        # Update our mapping
        if session.session_id != legacy_id:
            self._sessions[legacy_id] = session
            if session.session_id in self._sessions:
                del self._sessions[session.session_id]
            session.session_id = legacy_id

        logger.info(f"[MAESTROv2] Started legacy session: {legacy_id}")

        return session, first_question

    # =========================================================================
    # PRIVATE: UTILITIES
    # =========================================================================

    def _get_session(self, session_id: str) -> SoulAwareSession:
        """Get session or raise error if not found."""
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")
        return session
