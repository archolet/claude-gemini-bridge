"""
AgentOrchestrator - Multi-Agent Pipeline Coordinator

This is the main coordinator that runs design pipelines by:
1. Loading the appropriate pipeline configuration
2. Executing agents in sequence (or parallel)
3. Managing context passing between agents
4. Handling errors and recovery
5. Validating cross-layer consistency (e.g., HTML IDs vs JS selectors)

Usage:
    orchestrator = AgentOrchestrator(client)
    result = await orchestrator.run_pipeline(
        PipelineType.COMPONENT,
        AgentContext(component_type="hero", theme="cyberpunk")
    )
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Optional

from gemini_mcp.orchestration.context import AgentContext, QualityTarget
from gemini_mcp.orchestration.pipelines import (
    Pipeline,
    PipelineStep,
    PipelineType,
    ParallelGroup,
    get_pipeline,
)
from gemini_mcp.orchestration.telemetry import get_telemetry
from gemini_mcp.few_shot_examples import (
    get_few_shot_examples_for_prompt,
    get_corporate_examples_for_prompt,
)
from gemini_mcp.frontend_presets import MICRO_INTERACTIONS

if TYPE_CHECKING:
    from gemini_mcp.agents.base import AgentResult, BaseAgent
    from gemini_mcp.agents.critic import CriticAgent, CriticScores
    from gemini_mcp.client import GeminiClient

logger = logging.getLogger(__name__)

# === Refiner Loop Constants (Gemini 3 Quality Loop) ===
# Default quality threshold for CSS refinement. Alchemist will be re-run
# until Critic scores reach this level or max iterations is hit.
QUALITY_THRESHOLD = 8.0

# Maximum iterations for the refiner loop to prevent infinite loops.
# Each iteration: Alchemist -> Critic -> (if score < threshold) repeat
MAX_REFINER_ITERATIONS = 3

# === Adaptive Threshold System (Creativity Enhancement) ===
# Component-type specific quality thresholds.
# High-impact components require higher quality; atomic components can be simpler.
COMPONENT_THRESHOLDS: dict[str, float] = {
    # High-impact components (user's first impression)
    "hero": 8.5,
    "navbar": 8.5,
    "landing_page": 8.5,
    "dashboard": 8.5,
    # Standard components
    "card": 8.0,
    "form": 8.0,
    "modal": 8.0,
    "footer": 8.0,
    "sidebar": 8.0,
    "pricing": 8.0,
    "features": 8.0,
    "testimonials": 8.0,
    # Simple/atomic components (lower complexity)
    "button": 7.5,
    "input": 7.5,
    "badge": 7.5,
    "avatar": 7.5,
    "toggle": 7.5,
    "tooltip": 7.5,
    "spinner": 7.5,
    "divider": 7.0,
    # Default for unknown components
    "default": 8.0,
}

# === Convergence Detection (Early Stopping) ===
# Minimum score improvement to continue iterating
CONVERGENCE_THRESHOLD = 0.2
# Number of consecutive low-delta iterations before stopping
CONVERGENCE_COUNT = 2


def get_quality_threshold(component_type: str) -> float:
    """
    Get the quality threshold for a specific component type.

    Higher-impact components (hero, navbar) require higher quality scores,
    while simpler atomic components (button, badge) can have lower thresholds.

    Args:
        component_type: The type of component being designed

    Returns:
        The quality threshold (1.0-10.0 scale)
    """
    return COMPONENT_THRESHOLDS.get(
        component_type.lower(),
        COMPONENT_THRESHOLDS["default"]
    )


@dataclass
class PipelineResult:
    """Result of a complete pipeline execution."""

    success: bool
    html: str
    css: str
    js: str
    combined_output: str

    # Metadata
    pipeline_type: PipelineType
    pipeline_id: str
    total_steps: int
    completed_steps: int
    execution_time_ms: float

    # Token usage
    total_tokens: int = 0
    tokens_per_agent: dict[str, int] = field(default_factory=dict)

    # Issues
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Validation results
    validation_passed: bool = True
    validation_issues: list[str] = field(default_factory=list)

    # Step results for Trifecta agent tracking
    step_results: list = field(default_factory=list)  # list[AgentResult]

    def to_mcp_response(self) -> dict[str, Any]:
        """Convert to MCP tool response format."""
        response = {
            "html": self.combined_output,
            "component_id": self.pipeline_id,
            "pipeline_type": self.pipeline_type.value,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "total_tokens": self.total_tokens,
            "validation_passed": self.validation_passed,
            "warnings": self.warnings,
            "errors": self.errors,
        }
        # Include separate CSS and JS outputs if present
        if self.css:
            response["css_output"] = self.css
        if self.js:
            response["js_output"] = self.js
        return response


@dataclass
class Checkpoint:
    """A saved state of the pipeline for recovery."""

    step_index: int
    agent_name: str
    context_snapshot: str  # Serialized AgentContext
    timestamp: float


class CheckpointManager:
    """Manages pipeline checkpoints for error recovery."""

    def __init__(self):
        self._checkpoints: dict[str, list[Checkpoint]] = {}

    def save(self, pipeline_id: str, step_index: int, agent_name: str, context: AgentContext) -> None:
        """Save a checkpoint for the current step."""
        if pipeline_id not in self._checkpoints:
            self._checkpoints[pipeline_id] = []

        checkpoint = Checkpoint(
            step_index=step_index,
            agent_name=agent_name,
            context_snapshot=context.serialize(),
            timestamp=time.time(),
        )
        self._checkpoints[pipeline_id].append(checkpoint)
        logger.debug(f"Checkpoint saved: pipeline={pipeline_id}, step={step_index}, agent={agent_name}")

    def get_last_valid(self, pipeline_id: str, before_step: int) -> Optional[Checkpoint]:
        """Get the last valid checkpoint before a given step."""
        if pipeline_id not in self._checkpoints:
            return None

        checkpoints = self._checkpoints[pipeline_id]
        for cp in reversed(checkpoints):
            if cp.step_index < before_step:
                return cp
        return None

    def clear(self, pipeline_id: str) -> None:
        """Clear all checkpoints for a pipeline."""
        if pipeline_id in self._checkpoints:
            del self._checkpoints[pipeline_id]


class AgentOrchestrator:
    """
    Main coordinator for multi-agent design pipelines.

    The orchestrator:
    1. Loads the appropriate pipeline based on tool type
    2. Initializes required agents
    3. Executes steps in sequence (or parallel for page pipelines)
    4. Passes compressed context between agents
    5. Validates cross-layer consistency
    6. Handles errors and recovery via checkpoints
    """

    def __init__(
        self,
        client: "GeminiClient",
        enable_checkpoints: bool = True,
        enable_validation: bool = True,
    ):
        """
        Initialize the orchestrator.

        Args:
            client: GeminiClient for API calls
            enable_checkpoints: Whether to save checkpoints for recovery
            enable_validation: Whether to run cross-layer validation
        """
        self.client = client
        self.enable_checkpoints = enable_checkpoints
        self.enable_validation = enable_validation
        self._agents: dict[str, "BaseAgent"] = {}
        self._checkpoint_manager = CheckpointManager()
        self._validators: dict[str, Callable] = {}

        logger.info("AgentOrchestrator initialized")

    def register_agent(self, name: str, agent: "BaseAgent") -> None:
        """Register an agent for use in pipelines."""
        self._agents[name] = agent
        logger.info(f"Registered agent: {name}")

    def register_validator(self, name: str, validator: Callable[[AgentContext], tuple[bool, list[str]]]) -> None:
        """Register a validation function."""
        self._validators[name] = validator
        logger.info(f"Registered validator: {name}")

    def get_agent(self, name: str) -> Optional["BaseAgent"]:
        """Get a registered agent by name."""
        return self._agents.get(name)

    async def run_pipeline(
        self,
        pipeline_type: PipelineType,
        context: AgentContext,
        on_step_complete: Optional[Callable[[str, "AgentResult"], None]] = None,
        **pipeline_kwargs,
    ) -> PipelineResult:
        """
        Execute a complete pipeline.

        Args:
            pipeline_type: Type of pipeline to run
            context: Initial context with user requirements
            on_step_complete: Optional callback after each step
            **pipeline_kwargs: Additional args for pipeline creation (e.g., section_count)

        Returns:
            PipelineResult with combined output and metadata
        """
        start_time = time.time()
        telemetry = get_telemetry()

        # Get pipeline configuration
        pipeline = get_pipeline(pipeline_type, **pipeline_kwargs)
        context.total_steps = pipeline.count_steps()
        context.pipeline_id = context.pipeline_id or f"{pipeline_type.value}_{int(time.time())}"

        # Start telemetry tracking
        telemetry.start_pipeline(
            pipeline_type=pipeline_type.value,
            pipeline_id=context.pipeline_id,
            component_type=context.component_type,
            theme=context.theme,
            quality_target=context.quality_target.value,
        )

        logger.info(
            f"Starting pipeline: type={pipeline_type.value}, "
            f"id={context.pipeline_id}, steps={context.total_steps}"
        )

        # === Phase 1: Select Few-Shot Examples ===
        # Pass high-quality examples to guide agent outputs
        self._prepare_few_shot_examples(context)

        # === Phase 4: Prepare Micro-Interactions ===
        # UX Enhancement: Distribute FULL preset contents to all agents
        if context.micro_interactions_enabled:
            context.interaction_presets = list(MICRO_INTERACTIONS.keys())
            # Also store full preset data for Alchemist/Physicist
            context.micro_interaction_presets = {
                name: {
                    "classes": preset.get("classes", ""),
                    "description": preset.get("description", ""),
                }
                for name, preset in MICRO_INTERACTIONS.items()
            }

        # Track metrics
        tokens_per_agent: dict[str, int] = {}
        total_tokens = 0
        completed_steps = 0
        errors: list[str] = []
        warnings: list[str] = []
        step_results: list = []  # Collect AgentResult for each step

        try:
            for step in pipeline.steps:
                if isinstance(step, ParallelGroup):
                    # Execute parallel steps
                    results = await self._execute_parallel_group(step, context)
                    for agent_name, result in results.items():
                        step_results.append(result)  # Collect for Trifecta tracking
                        if result.success:
                            completed_steps += 1
                            if result.token_usage:
                                tokens = sum(result.token_usage.values())
                                tokens_per_agent[agent_name] = tokens_per_agent.get(agent_name, 0) + tokens
                                total_tokens += tokens
                            warnings.extend(result.warnings)
                        else:
                            errors.extend(result.errors)

                        if on_step_complete:
                            on_step_complete(agent_name, result)

                else:
                    # Execute single step
                    if not step.should_run(context):
                        logger.info(f"Skipping step: {step.agent_name}")
                        continue

                    result = await self._execute_step(step, context, pipeline)
                    step_results.append(result)  # Collect for Trifecta tracking
                    context.step_index += 1

                    # Record telemetry for this agent
                    agent_tokens = sum(result.token_usage.values()) if result.token_usage else 0
                    telemetry.record_agent_execution(
                        pipeline_id=context.pipeline_id,
                        agent_name=step.agent_name,
                        execution_time_ms=result.execution_time_ms,
                        tokens_used=agent_tokens,
                        success=result.success,
                        error_message=result.errors[0] if result.errors else "",
                    )

                    if result.success:
                        completed_steps += 1
                        # Update context with output
                        context.set_output(step.agent_name, result.output)
                        if step.compress_output:
                            context.compress_current_output(result.output, step.output_type)

                        # === PHASE 7: DNA Propagation Fix ===
                        # Propagate DNA from Strategist to context
                        if step.agent_name == "strategist" and result.metadata:
                            dna_data = result.metadata.get("design_dna")
                            if dna_data:
                                from gemini_mcp.orchestration.context import DesignDNA
                                context.design_dna = DesignDNA.from_dict(dna_data)
                                logger.info(
                                    f"[Orchestrator] DNA propagated from Strategist: "
                                    f"mood={context.design_dna.mood}"
                                )

                        # === CREATIVITY ENHANCEMENT: Reference Adherence Check ===
                        # After Alchemist in REFERENCE pipeline, evaluate adherence
                        if (
                            pipeline_type == PipelineType.REFERENCE
                            and step.agent_name == "alchemist"
                            and context.design_tokens  # Tokens from Visionary
                            and context.html_output
                        ):
                            try:
                                from gemini_mcp.agents.critic import CriticAgent

                                critic = CriticAgent(client=self.client)
                                adherence_score, improvements = await critic.evaluate_reference_adherence(
                                    reference_tokens=context.design_tokens,
                                    generated_html=context.html_output,
                                    generated_css=context.css_output or "",
                                    context=context,
                                )

                                # Log adherence score
                                logger.info(
                                    f"[Orchestrator] Reference adherence: {adherence_score:.2f}"
                                )

                                # Add warning if adherence is low
                                REFERENCE_ADHERENCE_THRESHOLD = 7.0
                                if adherence_score < REFERENCE_ADHERENCE_THRESHOLD:
                                    warnings.append(
                                        f"Reference adherence is {adherence_score:.1f}/10 "
                                        f"(threshold: {REFERENCE_ADHERENCE_THRESHOLD}). "
                                        f"Improvements: {'; '.join(improvements[:3])}"
                                    )
                                    # Store improvements for potential retry
                                    context.reference_adherence_improvements = improvements

                            except Exception as e:
                                logger.warning(f"Reference adherence check failed: {e}")

                        # Track tokens
                        if result.token_usage:
                            tokens = sum(result.token_usage.values())
                            tokens_per_agent[step.agent_name] = tokens
                            total_tokens += tokens

                        warnings.extend(result.warnings)
                    else:
                        errors.extend(result.errors)
                        if step.required and not step.recoverable:
                            raise RuntimeError(f"Required step {step.agent_name} failed: {result.errors}")

                    if on_step_complete:
                        on_step_complete(step.agent_name, result)

            # Run cross-layer validation
            validation_passed = True
            validation_issues: list[str] = []

            if self.enable_validation:
                validation_passed, validation_issues = self._run_validation(context)
                if not validation_passed:
                    warnings.extend(validation_issues)

            # Build result
            execution_time = (time.time() - start_time) * 1000
            pipeline_success = len(errors) == 0

            # End telemetry tracking
            telemetry.end_pipeline(context.pipeline_id, pipeline_success)

            return PipelineResult(
                success=pipeline_success,
                html=context.html_output,
                css=context.css_output,
                js=context.js_output,
                combined_output=context.get_combined_output(),
                pipeline_type=pipeline_type,
                pipeline_id=context.pipeline_id,
                total_steps=context.total_steps,
                completed_steps=completed_steps,
                execution_time_ms=execution_time,
                total_tokens=total_tokens,
                tokens_per_agent=tokens_per_agent,
                errors=errors,
                warnings=warnings,
                validation_passed=validation_passed,
                validation_issues=validation_issues,
                step_results=step_results,
            )

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            execution_time = (time.time() - start_time) * 1000

            # End telemetry tracking with failure
            telemetry.end_pipeline(context.pipeline_id, False)

            return PipelineResult(
                success=False,
                html=context.html_output,
                css=context.css_output,
                js=context.js_output,
                combined_output=context.get_combined_output(),
                pipeline_type=pipeline_type,
                pipeline_id=context.pipeline_id,
                total_steps=context.total_steps,
                completed_steps=completed_steps,
                execution_time_ms=execution_time,
                total_tokens=total_tokens,
                tokens_per_agent=tokens_per_agent,
                errors=[str(e)] + errors,
                warnings=warnings,
                validation_passed=False,
                step_results=step_results,
            )

        finally:
            # Cleanup checkpoints
            if self.enable_checkpoints:
                self._checkpoint_manager.clear(context.pipeline_id)

    def _prepare_few_shot_examples(self, context: AgentContext) -> None:
        """
        Select and attach few-shot examples to context (Phase 1 Integration).

        Selects examples based on:
        1. Component type (exact match from COMPONENT_EXAMPLES)
        2. Industry/vibe (corporate examples for enterprise quality)

        Args:
            context: The agent context to populate with examples
        """
        examples = []

        # 1. Get component-specific examples
        component_examples = get_few_shot_examples_for_prompt(context.component_type)
        examples.extend(component_examples)

        # 2. Get corporate examples if industry specified (Phase 5)
        industry = context.style_guide.get("industry", "")
        if industry:
            corporate_examples = get_corporate_examples_for_prompt(industry)
            examples.extend(corporate_examples)

        # 3. Vibe-based examples (Phase 5)
        vibe = context.style_guide.get("vibe", "")
        if vibe:
            vibe_examples = get_few_shot_examples_for_prompt(vibe)
            examples.extend(vibe_examples)

        # Limit to 3 examples max to avoid token bloat
        context.few_shot_examples = examples[:3]

        if context.few_shot_examples:
            logger.debug(
                f"Attached {len(context.few_shot_examples)} few-shot examples "
                f"for component_type={context.component_type}"
            )

    async def _execute_step(
        self,
        step: PipelineStep,
        context: AgentContext,
        pipeline: Pipeline,
    ) -> "AgentResult":
        """Execute a single pipeline step with retry and checkpointing."""
        from gemini_mcp.agents.base import AgentResult, AgentRole

        agent = self.get_agent(step.agent_name)
        if agent is None:
            logger.warning(f"Agent not registered: {step.agent_name}")
            # Return a placeholder result for unregistered agents
            return AgentResult(
                success=True,
                output=context.previous_output or "",
                agent_role=AgentRole.ARCHITECT,  # Default
                execution_time_ms=0,
                warnings=[f"Agent '{step.agent_name}' not registered, skipping"],
            )

        context.current_agent = step.agent_name

        # Save checkpoint before execution
        if self.enable_checkpoints:
            self._checkpoint_manager.save(
                context.pipeline_id,
                context.step_index,
                step.agent_name,
                context,
            )

        # Execute with self-correction
        result = await self._execute_with_correction(
            agent,
            context,
            max_retries=pipeline.max_retries if step.recoverable else 0,
        )

        return result

    async def _execute_with_correction(
        self,
        agent: "BaseAgent",
        context: AgentContext,
        max_retries: int = 2,
    ) -> "AgentResult":
        """
        Execute an agent with self-correction loop.

        If validation fails, the agent is re-run with correction feedback.
        """
        from gemini_mcp.agents.base import AgentResult

        for attempt in range(max_retries + 1):
            context.attempt = attempt

            result = await agent.execute(context)

            if not result.success:
                # Agent execution failed
                if attempt < max_retries:
                    logger.warning(
                        f"Agent {agent.name} failed, retrying ({attempt + 1}/{max_retries})"
                    )
                    continue
                return result

            # Validate output
            is_valid, issues = agent.validate_output(result.output)

            if is_valid:
                return result

            # Validation failed
            if attempt < max_retries:
                logger.warning(
                    f"Agent {agent.name} output invalid, retrying with feedback: {issues}"
                )
                context.correction_feedback = "\n".join(issues)
            else:
                result.warnings.extend(issues)

        return result

    async def _run_refiner_loop(
        self,
        context: AgentContext,
        initial_css: str = "",
    ) -> tuple[str, "CriticScores", int]:
        """
        Run the Alchemist → Critic → Alchemist refinement loop.

        This is a Gemini 3 optimization that iteratively improves CSS quality
        until the Critic scores reach the quality threshold or max iterations.

        The loop:
        1. Alchemist generates/refines CSS
        2. Critic evaluates with 5-dimension scoring
        3. If score < QUALITY_THRESHOLD, feed improvements back to Alchemist
        4. Repeat until score >= threshold or MAX_REFINER_ITERATIONS

        Args:
            context: Pipeline context with HTML output
            initial_css: Optional initial CSS to refine (empty for new generation)

        Returns:
            Tuple of (final_css, final_scores, iterations_used)
        """
        from gemini_mcp.agents.critic import CriticAgent, CriticScores

        # Get agents
        alchemist = self.get_agent("alchemist")
        critic_agent = self.get_agent("critic")

        if alchemist is None:
            logger.warning("[RefinerLoop] Alchemist agent not registered")
            return initial_css, CriticScores(), 0

        if critic_agent is None or not isinstance(critic_agent, CriticAgent):
            logger.warning("[RefinerLoop] Critic agent not registered or wrong type")
            return initial_css, CriticScores(), 0

        critic: CriticAgent = critic_agent

        # Initialize
        current_css = initial_css
        context.refiner_iteration = 0
        best_css = initial_css
        best_scores = CriticScores()

        # === Adaptive Threshold (Enhancement) ===
        # Get component-specific threshold instead of fixed value
        adaptive_threshold = get_quality_threshold(context.component_type or "default")

        # === Score History for Convergence Detection ===
        score_history: list[float] = []
        low_delta_count = 0  # Track consecutive low-improvement iterations

        logger.info(
            f"[RefinerLoop] Starting refinement. "
            f"Component: {context.component_type or 'unknown'}, "
            f"Adaptive threshold: {adaptive_threshold}, "
            f"Max iterations: {MAX_REFINER_ITERATIONS}"
        )

        for iteration in range(MAX_REFINER_ITERATIONS):
            context.refiner_iteration = iteration + 1

            # Step 1: Alchemist generates/refines CSS
            if iteration == 0 and not initial_css:
                # First iteration: generate from scratch
                logger.info(f"[RefinerLoop] Iteration {iteration + 1}: Generating CSS")
            else:
                # Subsequent iterations: refine with feedback
                logger.info(
                    f"[RefinerLoop] Iteration {iteration + 1}: Refining CSS. "
                    f"Feedback: {len(context.critic_feedback)} items"
                )

            alchemist_result = await alchemist.execute(context)

            if not alchemist_result.success:
                logger.warning(
                    f"[RefinerLoop] Alchemist failed at iteration {iteration + 1}"
                )
                break

            current_css = alchemist_result.output

            # Step 2: Critic evaluates quality
            scores, improvements = await critic.evaluate(
                html=context.html_output,
                css=current_css,
                js=context.js_output,
                context=context,
            )

            logger.info(
                f"[RefinerLoop] Iteration {iteration + 1} scores: "
                f"layout={scores.layout:.1f}, typography={scores.typography:.1f}, "
                f"color={scores.color:.1f}, interaction={scores.interaction:.1f}, "
                f"accessibility={scores.accessibility:.1f}, "
                f"overall={scores.overall:.2f}"
            )

            # Track best result
            if scores.overall > best_scores.overall:
                best_css = current_css
                best_scores = scores

            # === Score History Tracking (Enhancement) ===
            score_history.append(scores.overall)

            # Step 3: Check adaptive threshold
            if scores.overall >= adaptive_threshold:
                logger.info(
                    f"[RefinerLoop] Quality threshold reached at iteration {iteration + 1}! "
                    f"Score: {scores.overall:.2f} >= {adaptive_threshold} "
                    f"(component: {context.component_type or 'unknown'})"
                )
                return current_css, scores, iteration + 1

            # === Convergence Detection (Enhancement) ===
            # If improvement is too small, we're likely stuck - stop early to save resources
            if len(score_history) >= 2:
                delta = score_history[-1] - score_history[-2]
                if delta < CONVERGENCE_THRESHOLD:
                    low_delta_count += 1
                    logger.debug(
                        f"[RefinerLoop] Low improvement detected: delta={delta:.3f} "
                        f"(count: {low_delta_count}/{CONVERGENCE_COUNT})"
                    )
                    if low_delta_count >= CONVERGENCE_COUNT:
                        logger.info(
                            f"[RefinerLoop] Converged at iteration {iteration + 1}. "
                            f"Score delta ({delta:.3f}) < threshold ({CONVERGENCE_THRESHOLD}) "
                            f"for {CONVERGENCE_COUNT} consecutive iterations. "
                            f"Final score: {scores.overall:.2f}"
                        )
                        return best_css, best_scores, iteration + 1
                else:
                    # Reset counter if we see meaningful improvement
                    low_delta_count = 0

            # Step 4: Feed improvements back for next iteration
            context.critic_feedback = improvements
            context.css_output = current_css  # Update for next Alchemist run

        # Max iterations reached - return best result
        logger.info(
            f"[RefinerLoop] Max iterations reached. Best score: {best_scores.overall:.2f}"
        )
        return best_css, best_scores, MAX_REFINER_ITERATIONS

    async def run_refiner_for_css(
        self,
        context: AgentContext,
    ) -> tuple[str, float]:
        """
        Convenience method to run refiner loop and update context.

        This is the primary entry point for CSS refinement in pipelines.

        Args:
            context: Pipeline context (should have html_output set)

        Returns:
            Tuple of (refined_css, overall_score)
        """
        css, scores, iterations = await self._run_refiner_loop(
            context=context,
            initial_css=context.css_output,
        )

        # Update context
        context.css_output = css
        context.refiner_iteration = iterations

        logger.info(
            f"[RefinerLoop] Complete. Iterations: {iterations}, "
            f"Final score: {scores.overall:.2f}"
        )

        return css, scores.overall

    async def run_corporate_quality_loop(
        self,
        context: AgentContext,
        industry: str = "consulting",
        formality: str = "semi-formal",
    ) -> tuple[str, str, str, dict]:
        """
        Enhanced quality loop for corporate/enterprise designs.

        This method extends the standard refiner loop with:
        1. Standard Critic evaluation
        2. Professional Validator checks (if PREMIUM/ENTERPRISE)
        3. Corporate-specific evaluation (if ENTERPRISE)
        4. Iterative refinement until all quality gates pass

        Args:
            context: Pipeline context with HTML output
            industry: Industry context (finance, healthcare, legal, tech, etc.)
            formality: Formality level (formal, semi-formal, approachable)

        Returns:
            Tuple of (html, css, js, corporate_metrics)
        """
        from gemini_mcp.orchestration.context import (
            QualityTarget,
            get_quality_config,
            get_threshold_for_target,
            get_max_iterations_for_target,
        )
        from gemini_mcp.agents.critic import CriticAgent
        from gemini_mcp.validation.professional_validator import validate_professional

        logger.info(
            f"[CorporateLoop] Starting. Industry: {industry}, "
            f"Formality: {formality}, Quality: {context.quality_target.value}"
        )

        # Get quality configuration for target level
        quality_config = get_quality_config(context.quality_target)
        threshold = quality_config["threshold"]
        max_iterations = quality_config["max_iterations"]
        enable_pro_validator = quality_config["enable_professional_validator"]
        require_corporate = quality_config["require_corporate_evaluation"]

        # Get critic agent
        critic_agent = self.get_agent("critic")
        critic: CriticAgent | None = (
            critic_agent if isinstance(critic_agent, CriticAgent) else None
        )

        # Initialize tracking
        best_html = context.html_output
        best_css = context.css_output
        best_js = context.js_output
        corporate_metrics: dict = {}

        for iteration in range(max_iterations):
            logger.info(f"[CorporateLoop] Iteration {iteration + 1}/{max_iterations}")

            # Step 1: Run standard refiner loop for CSS
            css, standard_score = await self.run_refiner_for_css(context)

            # Step 2: Professional Validator (if enabled)
            pro_result = None
            if enable_pro_validator:
                pro_result = validate_professional(
                    html=context.html_output,
                    css=css,
                    formality=formality,
                    industry=industry,
                    accessibility_level="AAA" if formality == "formal" else "AA",
                )

                logger.info(
                    f"[CorporateLoop] Professional Validator: "
                    f"{pro_result.overall_score:.1f}/100, "
                    f"Professional: {pro_result.is_professional}"
                )

            # Step 3: Corporate Evaluation (if required and critic available)
            if require_corporate and critic:
                scores, improvements, corp_metrics = await critic.evaluate_corporate_quality(
                    html=context.html_output,
                    css=css,
                    industry=industry,
                    formality=formality,
                    context=context,
                )

                corporate_metrics = corp_metrics
                corporate_score = corp_metrics.get("corporate_score", 5.0)
                is_corporate_grade = corp_metrics.get("is_corporate_grade", False)

                logger.info(
                    f"[CorporateLoop] Corporate Evaluation: "
                    f"Score: {corporate_score:.1f}/10, "
                    f"Corporate Grade: {is_corporate_grade}"
                )

                # Check if we meet all quality gates
                if (
                    standard_score >= threshold and
                    (not enable_pro_validator or pro_result.is_professional) and
                    is_corporate_grade
                ):
                    logger.info(
                        f"[CorporateLoop] All quality gates passed at iteration {iteration + 1}"
                    )
                    best_css = css
                    break

            else:
                # Non-corporate path: just check standard score
                if standard_score >= threshold:
                    if not enable_pro_validator or (pro_result and pro_result.is_professional):
                        logger.info(
                            f"[CorporateLoop] Quality threshold met at iteration {iteration + 1}"
                        )
                        best_css = css
                        break

            # Update best if this iteration improved
            best_css = css

        # Build final corporate metrics
        if pro_result and not corporate_metrics:
            corporate_metrics = {
                "professional_validator_result": pro_result.to_dict(),
                "is_corporate_grade": pro_result.is_professional,
            }

        corporate_metrics["quality_target"] = context.quality_target.value
        corporate_metrics["industry"] = industry
        corporate_metrics["formality"] = formality
        corporate_metrics["iterations_used"] = iteration + 1

        logger.info(
            f"[CorporateLoop] Complete. Iterations: {iteration + 1}, "
            f"Corporate Grade: {corporate_metrics.get('is_corporate_grade', 'N/A')}"
        )

        return best_html, best_css, best_js, corporate_metrics

    async def _execute_parallel_group(
        self,
        group: ParallelGroup,
        context: AgentContext,
    ) -> dict[str, "AgentResult"]:
        """
        Execute a group of steps in parallel.

        For PAGE pipeline section_architects group, each step gets a different
        section from context.sections.
        """
        from gemini_mcp.agents.base import AgentResult, AgentRole

        tasks = []
        step_names = []
        section_indices = []  # Track which section each task handles

        # Check if this is a section_architects parallel group
        is_section_group = group.name == "section_architects"
        sections = context.sections if is_section_group and context.sections else []

        for idx, step in enumerate(group.steps):
            if not step.should_run(context):
                continue

            agent = self.get_agent(step.agent_name)
            if agent is None:
                continue

            # For section architects, set section-specific context
            if is_section_group and idx < len(sections):
                section = sections[idx]
                section_type = section.get("type", f"section_{idx}")
                # Use lightweight fork for parallel execution (Issue 3 fix)
                step_context = context.fork_for_parallel(
                    step_index=idx,
                    section_type=section_type,
                )
                step_context.component_type = section.get("type", "section")
                # Set section-specific content structure if available
                if section.get("content"):
                    step_context.content_structure = section.get("content", "{}")

                step_names.append(f"{step.agent_name}_{idx}")
                section_indices.append(idx)
            else:
                # Non-section parallel execution - use lightweight fork
                step_context = context.fork_for_parallel(step_index=idx)
                step_names.append(step.agent_name)
                section_indices.append(-1)

            tasks.append(agent.execute(step_context))

        if not tasks:
            return {}

        logger.info(f"Executing {len(tasks)} parallel tasks: {step_names}")

        # Run all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results to agent names
        result_map: dict[str, AgentResult] = {}
        section_htmls: list[tuple[int, str]] = []  # (index, html) for ordering

        for name, result, section_idx in zip(step_names, results, section_indices):
            if isinstance(result, Exception):
                result_map[name] = AgentResult(
                    success=False,
                    output="",
                    agent_role=AgentRole.ARCHITECT,
                    execution_time_ms=0,
                    errors=[str(result)],
                )
                logger.error(f"Parallel task {name} failed: {result}")
            else:
                result_map[name] = result
                # Collect section HTML for merging
                if section_idx >= 0 and result.success:
                    section_htmls.append((section_idx, result.output))

        # Merge section HTMLs in order and update context
        if section_htmls:
            section_htmls.sort(key=lambda x: x[0])
            merged_html = "\n\n".join(html for _, html in section_htmls)
            context.html_output = merged_html
            context.previous_output = merged_html
            logger.info(f"Merged {len(section_htmls)} section HTMLs")

        return result_map

    def _run_validation(self, context: AgentContext) -> tuple[bool, list[str]]:
        """
        Run cross-layer validation.

        Validates:
        1. HTML ID consistency with JS selectors
        2. CSS variable usage
        3. Responsive breakpoint coverage
        """
        issues: list[str] = []

        # ID Validation: Check JS doesn't reference non-existent IDs
        if context.html_output and context.js_output:
            html_ids = set(self._extract_ids(context.html_output))
            js_ids = set(self._extract_js_selectors(context.js_output))

            missing_ids = js_ids - html_ids
            if missing_ids:
                issues.append(
                    f"JS references non-existent IDs: {', '.join(missing_ids)}"
                )

        # CSS Variable validation
        if context.css_output:
            undefined_vars = self._check_undefined_css_vars(context.css_output)
            if undefined_vars:
                issues.append(
                    f"Undefined CSS variables used: {', '.join(undefined_vars)}"
                )

        # === Phase 2: Anti-Laziness Density Validation ===
        if context.html_output:
            from gemini_mcp.validation.density_validator import DensityValidator

            density_validator = DensityValidator(strict_mode=False)
            density_result = density_validator.validate(context.html_output)

            if not density_result.meets_minimum:
                issues.append(
                    f"Low class density: {density_result.overall_density:.1f}/element "
                    f"(minimum: 6). {density_result.elements_below_minimum} elements need more classes."
                )
            elif not density_result.meets_target:
                # Warning only, not a hard failure
                logger.warning(
                    f"Class density below target: {density_result.overall_density:.1f}/element "
                    f"(target: 8). Consider adding more styling classes."
                )

            # Log density score for telemetry
            logger.debug(f"Density score: {density_result.score}/100")

        # Run registered validators
        for name, validator in self._validators.items():
            try:
                is_valid, validator_issues = validator(context)
                if not is_valid:
                    issues.extend(validator_issues)
            except Exception as e:
                logger.warning(f"Validator {name} failed: {e}")

        return len(issues) == 0, issues

    def _extract_ids(self, html: str) -> list[str]:
        """Extract element IDs from HTML."""
        import re
        pattern = r'id=["\']([^"\']+)["\']'
        return re.findall(pattern, html)

    def _extract_js_selectors(self, js: str) -> list[str]:
        """Extract getElementById selectors from JS."""
        import re
        pattern = r'getElementById\(["\']([^"\']+)["\']\)'
        return re.findall(pattern, js)

    def _check_undefined_css_vars(self, css: str) -> list[str]:
        """Check for CSS variables that are used but not defined."""
        import re

        # Find all var() usages
        used_pattern = r"var\(--([a-zA-Z0-9-]+)"
        used_vars = set(re.findall(used_pattern, css))

        # Find all definitions
        defined_pattern = r"--([a-zA-Z0-9-]+)\s*:"
        defined_vars = set(re.findall(defined_pattern, css))

        # Find undefined
        undefined = used_vars - defined_vars

        # Filter out common CSS variables that might be defined elsewhere
        common_vars = {"tw-", "primary", "secondary", "accent", "background"}
        undefined = {v for v in undefined if not any(v.startswith(c) for c in common_vars)}

        return list(undefined)


# Global orchestrator instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator(client: Optional["GeminiClient"] = None) -> AgentOrchestrator:
    """
    Get or create the global orchestrator instance.

    Automatically registers all Trifecta agents on first initialization.

    Args:
        client: GeminiClient instance (required on first call)

    Returns:
        AgentOrchestrator instance with all agents registered
    """
    global _orchestrator

    if _orchestrator is None:
        if client is None:
            raise ValueError("Client is required for first orchestrator initialization")
        _orchestrator = AgentOrchestrator(client)

        # === Auto-register all Trifecta agents ===
        from gemini_mcp.agents import (
            ArchitectAgent,
            AlchemistAgent,
            PhysicistAgent,
            StrategistAgent,
            QualityGuardAgent,
            CriticAgent,
            VisionaryAgent,
        )

        # Core Trifecta pipeline agents
        _orchestrator.register_agent("architect", ArchitectAgent(client=client))
        _orchestrator.register_agent("alchemist", AlchemistAgent(client=client))
        _orchestrator.register_agent("physicist", PhysicistAgent(client=client))

        # Extended agents
        _orchestrator.register_agent("strategist", StrategistAgent(client=client))
        _orchestrator.register_agent("quality_guard", QualityGuardAgent(client=client))
        _orchestrator.register_agent("critic", CriticAgent(client=client))
        _orchestrator.register_agent("visionary", VisionaryAgent(client=client))

        logger.info(f"[Orchestrator] Registered {len(_orchestrator._agents)} agents")

    return _orchestrator


def reset_orchestrator() -> None:
    """Reset the global orchestrator instance."""
    global _orchestrator
    _orchestrator = None
