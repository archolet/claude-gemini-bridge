"""
BaseAgent - Abstract Base Class for Trifecta Agents

Each agent in the Trifecta Engine inherits from BaseAgent and implements
specialized behavior for their domain (HTML, CSS, JS, etc.).

Architecture:
    BaseAgent (abstract)
    ├── ArchitectAgent (HTML)
    ├── AlchemistAgent (CSS)
    ├── PhysicistAgent (JS)
    ├── StrategistAgent (Planning)
    ├── QualityGuardAgent (QA)
    └── CriticAgent (Art Direction)
"""

from __future__ import annotations

import logging
import re
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from gemini_mcp.orchestration.context import AgentContext

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Defines the specialized role of each agent."""

    ARCHITECT = "architect"  # HTML structure
    ALCHEMIST = "alchemist"  # Premium CSS
    PHYSICIST = "physicist"  # Vanilla JS
    STRATEGIST = "strategist"  # Planning & DNA
    QUALITY_GUARD = "quality_guard"  # QA validation
    CRITIC = "critic"  # Art direction
    VISIONARY = "visionary"  # Vision API analysis


@dataclass
class AgentConfig:
    """
    Configuration for an agent's execution behavior.

    Gemini 3 API Notes:
        - thinking_level: Use "high" for complex tasks, "low" for latency-sensitive
        - temperature: MUST be 1.0 for Gemini 3 reasoning engine
        - thinking_budget is DEPRECATED and removed

    References:
        - https://ai.google.dev/gemini-api/docs/gemini-3
        - https://ai.google.dev/gemini-api/docs/thinking
    """

    model: str = "gemini-3-pro-preview"

    # Gemini 3 Thinking Configuration
    # thinking_level: Controls reasoning depth (Gemini 3+)
    # - "high": Complex tasks requiring optimal thinking (default)
    # - "low": Latency-sensitive tasks (extraction, summarization)
    # - "minimal": Flash only - zero-budget thinking (not used in Pro)
    thinking_level: str = "high"

    # Temperature MUST be 1.0 for Gemini 3 reasoning engine
    # Lowering temperature may cause looping behavior
    temperature: float = 1.0

    max_output_tokens: int = 16384
    timeout_seconds: float = 120.0

    # Retry configuration
    max_retries: int = 2
    retry_delay_seconds: float = 1.0

    # Validation strictness
    strict_mode: bool = True
    auto_fix: bool = True


@dataclass
class AgentResult:
    """Result returned by an agent after execution."""

    success: bool
    output: str
    agent_role: AgentRole
    execution_time_ms: float

    # Metadata
    token_usage: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # For debugging
    prompt_used: Optional[str] = None
    raw_response: Optional[str] = None

    # Agent-specific metadata (e.g., design_dna from Strategist)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Extracted data (populated by post-processing)
    extracted_ids: list[str] = field(default_factory=list)
    extracted_css_vars: list[str] = field(default_factory=list)
    extracted_classes: list[str] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
        logger.warning(f"[{self.agent_role.value}] {warning}")

    def add_error(self, error: str) -> None:
        self.errors.append(error)
        logger.error(f"[{self.agent_role.value}] {error}")


class BaseAgent(ABC):
    """
    Abstract base class for all Trifecta agents.

    Each agent specializes in a specific domain:
    - Architect: Semantic HTML5 + Tailwind (NO CSS/JS)
    - Alchemist: Premium CSS effects (NO HTML changes)
    - Physicist: Vanilla JS interactions (NO frameworks)

    Usage:
        class ArchitectAgent(BaseAgent):
            role = AgentRole.ARCHITECT

            async def execute(self, context: AgentContext) -> AgentResult:
                # Generate HTML based on context
                ...
    """

    role: AgentRole
    config: AgentConfig

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the agent with optional custom configuration."""
        self.config = config or self._default_config()
        self._execution_id: Optional[str] = None
        logger.info(f"Initialized {self.role.value} agent")

    @classmethod
    def _default_config(cls) -> AgentConfig:
        """Get default configuration for this agent type."""
        # Subclasses can override for agent-specific defaults
        return AgentConfig()

    @property
    def name(self) -> str:
        """Human-readable name for this agent."""
        return f"The {self.role.value.title()}"

    @property
    def execution_id(self) -> Optional[str]:
        """Current execution ID for tracking."""
        return self._execution_id

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the system prompt that defines this agent's behavior.

        The prompt should:
        1. Clearly define the agent's role and boundaries
        2. List what the agent CAN and CANNOT do
        3. Specify the expected output format
        """
        pass

    @abstractmethod
    async def execute(self, context: "AgentContext") -> AgentResult:
        """
        Execute the agent's main task.

        Args:
            context: The current pipeline context containing:
                - Previous agent outputs
                - Design DNA and tokens
                - User requirements
                - Pipeline state

        Returns:
            AgentResult with the agent's output and metadata
        """
        pass

    @abstractmethod
    def validate_output(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate the agent's output against its constraints.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        pass

    def build_prompt(self, context: "AgentContext") -> str:
        """
        Build the full prompt from system prompt + context.

        Can be overridden by subclasses for custom prompt construction.
        """
        system = self.get_system_prompt()

        # Build context section
        context_parts = []

        if context.design_dna:
            import json

            context_parts.append(
                f"== DESIGN DNA ==\n{json.dumps(context.design_dna, indent=2, ensure_ascii=False)}"
            )

        if context.component_type:
            context_parts.append(f"== COMPONENT TYPE ==\n{context.component_type}")

        if context.theme:
            context_parts.append(f"== THEME ==\n{context.theme}")

        if context.content_structure:
            context_parts.append(
                f"== USER CONTENT ==\n{context.content_structure}"
            )

        if context.previous_output:
            context_parts.append(
                f"== PREVIOUS AGENT OUTPUT ==\n{context.previous_output}"
            )

        if context.correction_feedback:
            context_parts.append(
                f"== CORRECTION REQUIRED ==\n{context.correction_feedback}\n"
                f"Attempt: {context.attempt}"
            )

        context_section = "\n\n".join(context_parts)

        return f"{system}\n\n{context_section}"

    async def execute_with_retry(
        self,
        context: "AgentContext",
        on_retry: Optional[Callable[[int, Exception], None]] = None,
    ) -> AgentResult:
        """
        Execute with automatic retry on failure.

        Args:
            context: Pipeline context
            on_retry: Optional callback called on each retry with (attempt, exception)

        Returns:
            AgentResult from successful execution or last failed attempt
        """
        last_error: Optional[Exception] = None
        self._execution_id = str(uuid.uuid4())[:8]

        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()
                result = await self.execute(context)
                result.execution_time_ms = (time.time() - start_time) * 1000
                return result

            except Exception as e:
                last_error = e
                logger.warning(
                    f"[{self.role.value}] Attempt {attempt + 1} failed: {e}"
                )

                if on_retry and attempt < self.config.max_retries:
                    on_retry(attempt + 1, e)

                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay_seconds)

        # All retries exhausted
        return AgentResult(
            success=False,
            output="",
            agent_role=self.role,
            execution_time_ms=0,
            errors=[f"All {self.config.max_retries + 1} attempts failed: {last_error}"],
        )

    def extract_ids(self, html: str) -> list[str]:
        """Extract all element IDs from HTML."""
        pattern = r'id=["\']([^"\']+)["\']'
        return re.findall(pattern, html)

    def extract_css_variables(self, css: str) -> list[str]:
        """Extract all CSS variable names from CSS."""
        pattern = r"--([a-zA-Z0-9-]+)"
        return list(set(re.findall(pattern, css)))

    def extract_tailwind_classes(self, html: str) -> list[str]:
        """Extract Tailwind classes from class attributes."""
        pattern = r'class=["\']([^"\']+)["\']'
        matches = re.findall(pattern, html)
        classes = []
        for match in matches:
            classes.extend(match.split())
        return list(set(classes))

    def post_process(self, result: AgentResult, output: str) -> AgentResult:
        """
        Post-process the output to extract metadata.

        Called after successful execution to populate extracted_* fields.
        """
        if self.role == AgentRole.ARCHITECT:
            result.extracted_ids = self.extract_ids(output)
            result.extracted_classes = self.extract_tailwind_classes(output)
        elif self.role == AgentRole.ALCHEMIST:
            result.extracted_css_vars = self.extract_css_variables(output)

        return result

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} role={self.role.value}>"
