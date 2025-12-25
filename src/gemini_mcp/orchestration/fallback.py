"""
Fallback Chain - Graceful Degradation for Agent Failures

This module implements a 4-level fallback strategy for handling agent failures
in the Trifecta Engine. When an agent fails, the system progressively tries
more conservative approaches before returning a placeholder.

Fallback Levels:
    Level 1: Retry with same configuration (transient errors)
    Level 2: Retry with lower thinking level (high → low)
    Level 3: Use cached template from few-shot examples
    Level 4: Return static placeholder HTML

Gemini 3 API Notes:
    - thinking_level can be lowered (high → low) but NOT disabled
    - Temperature MUST remain 1.0 for Gemini 3 reasoning engine
    - Gemini 3 Pro only supports "low" | "high" (not "minimal")

References:
    - https://ai.google.dev/gemini-api/docs/gemini-3
    - https://ai.google.dev/gemini-api/docs/thinking
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from gemini_mcp.agents.base import AgentResult, BaseAgent
    from gemini_mcp.orchestration.context import AgentContext

logger = logging.getLogger(__name__)


class FallbackLevel(Enum):
    """Fallback levels in order of preference."""

    RETRY_SAME = 1        # Retry with same config
    LOWER_THINKING = 2    # Lower thinking level
    CACHED_TEMPLATE = 3   # Use cached/few-shot template
    STATIC_PLACEHOLDER = 4  # Return static placeholder


@dataclass
class FallbackStrategy:
    """
    Configuration for fallback behavior.

    This dataclass defines how the fallback chain should behave at each level.
    Each level can be enabled/disabled independently.

    Attributes:
        retry_same: Enable Level 1 (retry same config)
        max_retries: Maximum retries for Level 1
        retry_lower_thinking: Enable Level 2 (lower thinking level)
        lower_thinking_level: Target thinking level for Level 2
        use_cached_template: Enable Level 3 (cached templates)
        template_source: Where to get templates ("few_shot_examples" | "component_cache")
        static_placeholder: Enable Level 4 (static placeholder)
        placeholder_html: HTML to return as last resort
    """

    # Level 1: Retry same config
    retry_same: bool = True
    max_retries: int = 2
    retry_delay_seconds: float = 1.0

    # Level 2: Lower thinking level (high → low)
    # NOTE: Gemini 3 Pro doesn't support disabling thinking entirely
    retry_lower_thinking: bool = True
    lower_thinking_level: str = "low"

    # Level 3: Use cached template
    use_cached_template: bool = True
    template_source: str = "few_shot_examples"

    # Level 4: Static placeholder
    static_placeholder: bool = True
    placeholder_html: str = """
<div class="fallback-placeholder p-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
    <div class="text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">Component Generation Failed</h3>
        <p class="mt-2 text-sm text-gray-500">
            We couldn't generate this component. Please try again or simplify your request.
        </p>
    </div>
</div>
"""


@dataclass
class FallbackResult:
    """Result of a fallback chain execution."""

    success: bool
    output: str
    level_used: FallbackLevel
    attempts_per_level: dict[FallbackLevel, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def used_fallback(self) -> bool:
        """Check if any fallback level was used."""
        return self.level_used != FallbackLevel.RETRY_SAME or self.attempts_per_level.get(FallbackLevel.RETRY_SAME, 0) > 1

    @property
    def degraded(self) -> bool:
        """Check if output quality is degraded (level 2+)."""
        return self.level_used.value >= FallbackLevel.LOWER_THINKING.value


# === Default Strategies by Component Type ===

COMPONENT_STRATEGIES: dict[str, FallbackStrategy] = {
    # High-impact components: More aggressive retries
    "hero": FallbackStrategy(
        max_retries=3,
        retry_lower_thinking=True,
        use_cached_template=True,
    ),
    "navbar": FallbackStrategy(
        max_retries=3,
        retry_lower_thinking=True,
        use_cached_template=True,
    ),
    "dashboard": FallbackStrategy(
        max_retries=3,
        retry_lower_thinking=True,
        use_cached_template=True,
    ),
    # Simple components: Fewer retries, faster fallback
    "button": FallbackStrategy(
        max_retries=1,
        retry_lower_thinking=False,  # Skip level 2 for simple components
        use_cached_template=True,
    ),
    "badge": FallbackStrategy(
        max_retries=1,
        retry_lower_thinking=False,
        use_cached_template=True,
    ),
    "divider": FallbackStrategy(
        max_retries=1,
        retry_lower_thinking=False,
        use_cached_template=False,  # Just use placeholder
    ),
}


def get_strategy_for_component(component_type: str) -> FallbackStrategy:
    """
    Get the fallback strategy for a component type.

    Args:
        component_type: The component type (e.g., "hero", "button")

    Returns:
        FallbackStrategy configured for the component
    """
    normalized = component_type.lower().strip()
    return COMPONENT_STRATEGIES.get(normalized, FallbackStrategy())


class FallbackChain:
    """
    Executes the 4-level fallback chain for agent failures.

    Usage:
        chain = FallbackChain(strategy=FallbackStrategy())
        result = await chain.execute(
            agent=architect_agent,
            context=pipeline_context,
            executor=agent_executor_func,
        )
    """

    def __init__(
        self,
        strategy: Optional[FallbackStrategy] = None,
        template_provider: Optional[Callable[[str], Optional[str]]] = None,
    ):
        """
        Initialize the fallback chain.

        Args:
            strategy: Fallback strategy configuration
            template_provider: Function to get cached templates (component_type → html)
        """
        self.strategy = strategy or FallbackStrategy()
        self.template_provider = template_provider or self._default_template_provider

    def _default_template_provider(self, component_type: str) -> Optional[str]:
        """
        Default template provider using few-shot examples.

        Args:
            component_type: Component type to get template for

        Returns:
            HTML template or None if not found
        """
        try:
            from gemini_mcp.few_shot_examples import get_few_shot_examples_for_prompt

            examples = get_few_shot_examples_for_prompt(component_type)
            if examples:
                # Return the first example's HTML
                first_example = examples[0]
                if "html" in first_example:
                    return first_example["html"]
                elif "output" in first_example:
                    return first_example["output"]
        except Exception as e:
            logger.warning(f"Failed to get template for {component_type}: {e}")

        return None

    async def execute(
        self,
        agent: "BaseAgent",
        context: "AgentContext",
        executor: Callable[["BaseAgent", "AgentContext"], "AgentResult"],
        component_type: str = "",
    ) -> FallbackResult:
        """
        Execute the fallback chain.

        Tries each level in order until success or all levels exhausted.

        Args:
            agent: The agent to execute
            context: Pipeline context
            executor: Async function to execute agent (agent, context) → result
            component_type: Component type for template lookup

        Returns:
            FallbackResult with output and metadata
        """
        import asyncio
        import time

        errors: list[str] = []
        warnings: list[str] = []
        attempts: dict[FallbackLevel, int] = {}

        # === Level 1: Retry Same Config ===
        if self.strategy.retry_same:
            attempts[FallbackLevel.RETRY_SAME] = 0

            for attempt in range(self.strategy.max_retries + 1):
                attempts[FallbackLevel.RETRY_SAME] = attempt + 1

                try:
                    result = await executor(agent, context)

                    if result.success:
                        logger.info(
                            f"[FallbackChain] Level 1 success at attempt {attempt + 1}"
                        )
                        return FallbackResult(
                            success=True,
                            output=result.output,
                            level_used=FallbackLevel.RETRY_SAME,
                            attempts_per_level=attempts,
                        )

                    errors.append(f"L1 attempt {attempt + 1}: {result.errors}")

                except Exception as e:
                    errors.append(f"L1 attempt {attempt + 1} exception: {str(e)}")
                    logger.warning(f"[FallbackChain] L1 attempt {attempt + 1} failed: {e}")

                # Delay before retry
                if attempt < self.strategy.max_retries:
                    await asyncio.sleep(self.strategy.retry_delay_seconds)

            logger.info("[FallbackChain] Level 1 exhausted, trying Level 2")

        # === Level 2: Lower Thinking Level ===
        if self.strategy.retry_lower_thinking:
            attempts[FallbackLevel.LOWER_THINKING] = 0

            # Modify agent config to use lower thinking level
            original_thinking = agent.config.thinking_level
            agent.config.thinking_level = self.strategy.lower_thinking_level

            try:
                attempts[FallbackLevel.LOWER_THINKING] = 1
                result = await executor(agent, context)

                if result.success:
                    logger.info("[FallbackChain] Level 2 success with lower thinking")
                    warnings.append(
                        f"Used lower thinking level ({self.strategy.lower_thinking_level})"
                    )
                    return FallbackResult(
                        success=True,
                        output=result.output,
                        level_used=FallbackLevel.LOWER_THINKING,
                        attempts_per_level=attempts,
                        warnings=warnings,
                    )

                errors.append(f"L2: {result.errors}")

            except Exception as e:
                errors.append(f"L2 exception: {str(e)}")
                logger.warning(f"[FallbackChain] L2 failed: {e}")

            finally:
                # Restore original thinking level
                agent.config.thinking_level = original_thinking

            logger.info("[FallbackChain] Level 2 failed, trying Level 3")

        # === Level 3: Cached Template ===
        if self.strategy.use_cached_template:
            attempts[FallbackLevel.CACHED_TEMPLATE] = 1

            template = self.template_provider(component_type)

            if template:
                logger.info(
                    f"[FallbackChain] Level 3 success with cached template for {component_type}"
                )
                warnings.append(f"Used cached template for {component_type}")
                return FallbackResult(
                    success=True,
                    output=template,
                    level_used=FallbackLevel.CACHED_TEMPLATE,
                    attempts_per_level=attempts,
                    warnings=warnings,
                )

            errors.append(f"L3: No cached template for {component_type}")
            logger.info("[FallbackChain] Level 3 failed (no template), trying Level 4")

        # === Level 4: Static Placeholder ===
        if self.strategy.static_placeholder:
            attempts[FallbackLevel.STATIC_PLACEHOLDER] = 1

            logger.warning(
                f"[FallbackChain] Level 4: Returning static placeholder for {component_type}"
            )
            warnings.append("Returned static placeholder due to generation failure")

            return FallbackResult(
                success=True,  # Placeholder is a valid output
                output=self.strategy.placeholder_html,
                level_used=FallbackLevel.STATIC_PLACEHOLDER,
                attempts_per_level=attempts,
                errors=errors,
                warnings=warnings,
            )

        # All levels failed
        logger.error(
            f"[FallbackChain] All levels failed for {component_type}. "
            f"Errors: {errors}"
        )

        return FallbackResult(
            success=False,
            output="",
            level_used=FallbackLevel.STATIC_PLACEHOLDER,
            attempts_per_level=attempts,
            errors=errors,
            warnings=warnings,
        )


# === Component-Specific Placeholders ===

COMPONENT_PLACEHOLDERS: dict[str, str] = {
    "button": """
<button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700
               transition-colors duration-200 font-medium">
    Click Me
</button>
""",
    "card": """
<div class="bg-white rounded-lg shadow-md p-6 max-w-sm">
    <h3 class="text-lg font-semibold text-gray-900 mb-2">Card Title</h3>
    <p class="text-gray-600">Card content goes here.</p>
</div>
""",
    "badge": """
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
              bg-blue-100 text-blue-800">
    Badge
</span>
""",
    "input": """
<input type="text"
       class="block w-full px-4 py-2 border border-gray-300 rounded-lg
              focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
       placeholder="Enter text...">
""",
    "spinner": """
<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
""",
}


def get_placeholder_for_component(component_type: str) -> str:
    """
    Get a component-specific placeholder or the default.

    Args:
        component_type: Component type

    Returns:
        Placeholder HTML for the component
    """
    normalized = component_type.lower().strip()
    return COMPONENT_PLACEHOLDERS.get(
        normalized,
        FallbackStrategy().placeholder_html
    )


# === Convenience Functions ===

async def execute_with_fallback(
    agent: "BaseAgent",
    context: "AgentContext",
    executor: Callable[["BaseAgent", "AgentContext"], "AgentResult"],
    component_type: str = "",
    strategy: Optional[FallbackStrategy] = None,
) -> FallbackResult:
    """
    Convenience function to execute an agent with fallback chain.

    Args:
        agent: Agent to execute
        context: Pipeline context
        executor: Execution function
        component_type: Component type for template lookup
        strategy: Optional custom strategy

    Returns:
        FallbackResult
    """
    effective_strategy = strategy or get_strategy_for_component(component_type)
    chain = FallbackChain(strategy=effective_strategy)

    return await chain.execute(
        agent=agent,
        context=context,
        executor=executor,
        component_type=component_type,
    )
