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
    get_bad_examples_for_prompt,
    COMPONENT_EXAMPLES,
)
from gemini_mcp.frontend_presets import MICRO_INTERACTIONS
from gemini_mcp.schemas import (
    COMPLEXITY_LEVELS,
    ComplexityLevel,
    get_complexity_config,
    infer_complexity_from_component,
    validate_output_density,
    validate_design_thinking,
)

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

        # DEBUG: Log context.sections at pipeline start
        logger.info(f"[DEBUG] Pipeline start - context.sections={context.sections}, len={len(context.sections)}")

        # === Phase 1: Select Few-Shot Examples ===
        # Pass high-quality examples to guide agent outputs
        self._prepare_few_shot_examples(context)

        # === Phase 5: Prepare Complexity Configuration ===
        # Auto-infer complexity level and set density requirements
        self._prepare_complexity_config(context)

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
                    # DEBUG: Log context.html_output immediately after parallel group returns
                    logger.info(f"[DEBUG] After parallel group '{step.name}': html_output_len={len(context.html_output) if context.html_output else 0}")
                    for agent_name, result in results.items():
                        step_results.append(result)  # Collect for Trifecta tracking

                        # Record telemetry for parallel agents
                        agent_tokens = sum(result.token_usage.values()) if result.token_usage else 0
                        telemetry.record_agent_execution(
                            pipeline_id=context.pipeline_id,
                            agent_name=agent_name,
                            execution_time_ms=result.execution_time_ms,
                            tokens_used=agent_tokens,
                            success=result.success,
                            error_message=result.errors[0] if result.errors else "",
                        )

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

                    # DEBUG: Log html_output state before each step
                    logger.info(f"[DEBUG] Before step '{step.agent_name}': html_output_len={len(context.html_output) if context.html_output else 0}")
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
                        # DEBUG: Log html_output after set_output
                        logger.info(f"[DEBUG] After set_output('{step.agent_name}'): html_output_len={len(context.html_output) if context.html_output else 0}")
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

            # === Phase 5: Post-Pipeline Density Validation ===
            # Validate output density against complexity requirements
            density_passed, density_issues = self._validate_output_density_post_pipeline(context)
            if not density_passed:
                warnings.extend(density_issues)
                logger.warning(
                    f"[Orchestrator] Density validation failed: {density_issues}"
                )

            # Build result
            execution_time = (time.time() - start_time) * 1000
            pipeline_success = len(errors) == 0

            # End telemetry tracking
            telemetry.end_pipeline(context.pipeline_id, pipeline_success)

            # DEBUG: Final output check
            logger.info(f"[DEBUG] Final output - html_output_len={len(context.html_output) if context.html_output else 0}, css_len={len(context.css_output) if context.css_output else 0}, js_len={len(context.js_output) if context.js_output else 0}")

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
        3. Negative examples (BAD_EXAMPLES) to prevent anti-patterns

        Args:
            context: The agent context to populate with examples
        """
        examples: list[dict] = []

        # 1. Get component-specific examples from COMPONENT_EXAMPLES dict
        # NOTE: get_few_shot_examples_for_prompt returns string (for prompt text),
        # but agents expect list[dict]. Use COMPONENT_EXAMPLES directly.
        component_type = context.component_type
        if component_type and component_type in COMPONENT_EXAMPLES:
            example_data = COMPONENT_EXAMPLES[component_type]
            output = example_data.get("output", {})
            examples.append({
                "component_type": component_type,
                "html": output.get("html", ""),
                "css": output.get("css", ""),
                "js": output.get("js", ""),
            })

        # 2. Get similar component examples
        similar_map = {
            "button": ["cta"],
            "hero": ["banner", "ultra_dense_card"],
            "card": ["pricing_card", "stat_card"],
            "pricing_card": ["card"],
            "navbar": ["header"],
        }
        similar_types = similar_map.get(component_type, [])
        for similar in similar_types[:1]:  # Limit to 1 similar
            if similar in COMPONENT_EXAMPLES:
                example_data = COMPONENT_EXAMPLES[similar]
                output = example_data.get("output", {})
                examples.append({
                    "component_type": similar,
                    "html": output.get("html", ""),
                    "css": output.get("css", ""),
                    "js": output.get("js", ""),
                })

        # 3. Vibe-based examples (Phase 5)
        vibe = context.style_guide.get("vibe", "")
        if vibe and vibe in COMPONENT_EXAMPLES:
            example_data = COMPONENT_EXAMPLES[vibe]
            output = example_data.get("output", {})
            examples.append({
                "component_type": vibe,
                "html": output.get("html", ""),
                "css": output.get("css", ""),
                "js": output.get("js", ""),
            })

        # Limit to 3 positive examples max to avoid token bloat
        context.few_shot_examples = examples[:3]

        # 4. PHASE 5 - Negative example injection (Anti-Laziness)
        # Inject BAD_EXAMPLES to teach model what NOT to do
        negative_examples = get_bad_examples_for_prompt(context.component_type)
        if negative_examples:
            # Store negative examples separately for prompt injection
            context.metadata["negative_examples"] = negative_examples
            logger.debug(
                f"Attached {len(negative_examples)} negative examples "
                f"for component_type={context.component_type}"
            )

        if context.few_shot_examples:
            logger.debug(
                f"Attached {len(context.few_shot_examples)} few-shot examples "
                f"for component_type={context.component_type}"
            )

    def _prepare_complexity_config(self, context: AgentContext) -> None:
        """
        Prepare complexity level configuration based on component type (Phase 5).

        Auto-infers complexity level from component type and attaches
        configuration to context for agents to use.

        The complexity level affects:
        - Minimum/target Tailwind class counts
        - Design-CoT step depth
        - Few-shot example count
        - Quality thresholds

        Args:
            context: The agent context to configure
        """
        # Infer complexity from component type
        complexity_level = infer_complexity_from_component(
            context.component_type or "card"
        )

        # Get configuration for this level
        complexity_config = get_complexity_config(complexity_level)

        # Store in context metadata for agents
        context.metadata["complexity_level"] = complexity_level
        context.metadata["complexity_config"] = {
            "min_classes": complexity_config.min_classes,
            "target_classes": complexity_config.target_classes,
            "design_cot_steps": complexity_config.design_cot_steps,
            "few_shot_count": complexity_config.few_shot_count,
            "quality_threshold": complexity_config.quality_threshold,
        }

        # Adjust few-shot examples count based on complexity
        if context.few_shot_examples:
            target_count = complexity_config.few_shot_count
            if len(context.few_shot_examples) > target_count:
                context.few_shot_examples = context.few_shot_examples[:target_count]

        logger.info(
            f"[Orchestrator] Complexity configured: level={complexity_level}, "
            f"min_classes={complexity_config.min_classes}, "
            f"target_classes={complexity_config.target_classes}"
        )

    def _validate_output_density_post_pipeline(
        self,
        context: AgentContext,
    ) -> tuple[bool, list[str]]:
        """
        Validate output density after pipeline completion (Phase 5).

        Uses the complexity level to determine expected class density.

        Args:
            context: Pipeline context with HTML output

        Returns:
            Tuple of (passed, issues)
        """
        if not context.html_output:
            return True, []

        complexity_level = context.metadata.get("complexity_level", "standard")

        # Validate density against complexity requirements
        passed, density_report = validate_output_density(
            html=context.html_output,
            complexity=complexity_level,
            strict=False,  # Warnings only in standard mode
        )

        issues = []
        if not passed:
            issues.append(
                f"Output density below {complexity_level} minimum: "
                f"{density_report.get('overall_density', 0):.1f} classes/element "
                f"(required: {density_report.get('min_required', 6)})"
            )

            # Add details about low-density elements
            if density_report.get("elements_below_minimum"):
                issues.append(
                    f"Elements below minimum: "
                    f"{density_report['elements_below_minimum']}"
                )

        return passed, issues

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

    async def _run_targeted_refiner(
        self,
        context: AgentContext,
        scores: "CriticScores",
        max_dimensions: int = 3,
    ) -> tuple[str, str, str, "CriticScores"]:
        """
        Run targeted refinement based on lowest-scoring dimensions.

        This is a Phase 3 enhancement that maps low-scoring dimensions
        to their responsible agents and runs targeted refinement:
        - layout, code_quality, accessibility → Architect
        - color, animation_quality, visual_density, typography → Alchemist
        - interaction → Physicist

        Args:
            context: Pipeline context with HTML/CSS/JS outputs
            scores: CriticScores from evaluation
            max_dimensions: Number of lowest dimensions to target (default: 3)

        Returns:
            Tuple of (html, css, js, updated_scores)
        """
        from gemini_mcp.agents.critic import CriticAgent, CriticScores

        logger.info(
            f"[TargetedRefiner] Starting. Initial overall: {scores.overall:.2f}, "
            f"Targeting {max_dimensions} lowest dimensions"
        )

        # Get lowest-scoring dimensions
        lowest_dims = scores.get_lowest_dimensions(max_dimensions)
        logger.info(
            f"[TargetedRefiner] Lowest dimensions: "
            f"{[(name, f'{score:.1f}') for name, score in lowest_dims]}"
        )

        # Group dimensions by responsible agent
        agent_improvements: dict[str, list[str]] = {
            "architect": [],
            "alchemist": [],
            "physicist": [],
        }

        for dim_name, dim_score in lowest_dims:
            responsible_agent = scores.get_agent_for_dimension(dim_name)
            agent_improvements[responsible_agent].append(
                f"Improve {dim_name} (current: {dim_score:.1f}/10)"
            )

        # Track updated outputs
        current_html = context.html_output
        current_css = context.css_output
        current_js = context.js_output

        # Run targeted refinement for each agent with improvements
        for agent_name, improvements in agent_improvements.items():
            if not improvements:
                continue

            agent = self.get_agent(agent_name)
            if agent is None:
                logger.warning(f"[TargetedRefiner] Agent '{agent_name}' not registered")
                continue

            # Set refinement feedback for this agent
            feedback = (
                f"TARGETED REFINEMENT - Focus on these specific improvements:\n"
                + "\n".join(f"- {imp}" for imp in improvements)
            )
            context.correction_feedback = feedback

            logger.info(
                f"[TargetedRefiner] Running {agent_name} with "
                f"{len(improvements)} targeted improvements"
            )

            # Execute agent with correction feedback
            result = await agent.execute(context)

            if result.success and result.output:
                # Update appropriate output based on agent
                if agent_name == "architect":
                    current_html = result.output
                    context.html_output = result.output
                    context.set_output("architect", result.output)
                elif agent_name == "alchemist":
                    current_css = result.output
                    context.css_output = result.output
                    context.set_output("alchemist", result.output)
                elif agent_name == "physicist":
                    current_js = result.output
                    context.js_output = result.output
                    context.set_output("physicist", result.output)

                logger.info(
                    f"[TargetedRefiner] {agent_name} completed. "
                    f"Output: {len(result.output)} chars"
                )
            else:
                logger.warning(
                    f"[TargetedRefiner] {agent_name} failed: {result.errors}"
                )

        # Clear correction feedback
        context.correction_feedback = ""

        # Re-evaluate with Critic to get updated scores
        critic_agent = self.get_agent("critic")
        updated_scores = scores  # Default to original if re-evaluation fails

        if critic_agent and isinstance(critic_agent, CriticAgent):
            new_scores, _ = await critic_agent.evaluate(
                html=current_html,
                css=current_css,
                js=current_js,
                context=context,
            )
            updated_scores = new_scores

            logger.info(
                f"[TargetedRefiner] Complete. "
                f"Score improvement: {scores.overall:.2f} → {updated_scores.overall:.2f} "
                f"(+{updated_scores.overall - scores.overall:.2f})"
            )
        else:
            logger.warning("[TargetedRefiner] Critic not available for re-evaluation")

        return current_html, current_css, current_js, updated_scores

    async def run_targeted_refinement(
        self,
        context: AgentContext,
        quality_threshold: float = 8.0,
        max_refinement_rounds: int = 2,
    ) -> tuple[str, str, str, float]:
        """
        Public API for targeted refinement with quality loop.

        Runs Critic evaluation, then targeted refinement until quality
        threshold is met or max rounds exhausted.

        Args:
            context: Pipeline context with HTML/CSS/JS outputs
            quality_threshold: Target quality score (1-10)
            max_refinement_rounds: Maximum refinement iterations

        Returns:
            Tuple of (html, css, js, final_score)
        """
        from gemini_mcp.agents.critic import CriticAgent

        critic_agent = self.get_agent("critic")
        if not critic_agent or not isinstance(critic_agent, CriticAgent):
            logger.warning("[TargetedRefinement] Critic not available")
            return (
                context.html_output,
                context.css_output,
                context.js_output,
                0.0,
            )

        logger.info(
            f"[TargetedRefinement] Starting. Threshold: {quality_threshold}, "
            f"Max rounds: {max_refinement_rounds}"
        )

        # Initial evaluation
        scores, improvements = await critic_agent.evaluate(
            html=context.html_output,
            css=context.css_output,
            js=context.js_output,
            context=context,
        )

        logger.info(
            f"[TargetedRefinement] Initial score: {scores.overall:.2f}"
        )

        # Check if already meets threshold
        if scores.overall >= quality_threshold:
            logger.info(
                f"[TargetedRefinement] Already meets threshold. Done."
            )
            return (
                context.html_output,
                context.css_output,
                context.js_output,
                scores.overall,
            )

        # Run refinement rounds
        current_html = context.html_output
        current_css = context.css_output
        current_js = context.js_output
        current_scores = scores

        for round_num in range(max_refinement_rounds):
            logger.info(
                f"[TargetedRefinement] Round {round_num + 1}/{max_refinement_rounds}"
            )

            # Run targeted refiner
            current_html, current_css, current_js, current_scores = (
                await self._run_targeted_refiner(
                    context=context,
                    scores=current_scores,
                    max_dimensions=3,
                )
            )

            # Check if threshold met
            if current_scores.overall >= quality_threshold:
                logger.info(
                    f"[TargetedRefinement] Threshold met at round {round_num + 1}! "
                    f"Score: {current_scores.overall:.2f}"
                )
                break

        logger.info(
            f"[TargetedRefinement] Complete. Final score: {current_scores.overall:.2f}"
        )

        return current_html, current_css, current_js, current_scores.overall

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

        Handles different parallel group types:
        - section_architects: PAGE pipeline section generation (merges HTML)
        - styling_interaction: COMPONENT pipeline Alchemist + Physicist (merges CSS + JS)

        Performance Impact:
            - Sequential: ~5.5s (Alchemist ~1.8s + Physicist ~1.2s + overhead)
            - Parallel:   ~4.4s (~20% faster for COMPONENT pipeline)
        """
        from gemini_mcp.agents.base import AgentResult, AgentRole

        tasks = []
        step_names = []
        step_output_types = []  # Track output type for merge strategy
        section_indices = []  # Track which section each task handles

        # Check parallel group type
        is_section_group = group.name == "section_architects"
        is_styling_group = group.name == "styling_interaction"
        sections = context.sections if is_section_group and context.sections else []

        # DEBUG: Log parallel group execution context
        logger.info(f"[DEBUG] Parallel group '{group.name}': is_section_group={is_section_group}, context.sections={context.sections}, sections={sections}")

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
                    step_context.content_structure = section.get("content", {})

                step_names.append(f"{step.agent_name}_{idx}")
                step_output_types.append(step.output_type)
                section_indices.append(idx)
            else:
                # Non-section parallel execution (styling_interaction, etc.)
                # Use lightweight fork with shared HTML context for Alchemist/Physicist
                step_context = context.fork_for_parallel(step_index=idx)
                step_names.append(step.agent_name)
                step_output_types.append(step.output_type)
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

        for name, result, section_idx, output_type in zip(
            step_names, results, section_indices, step_output_types
        ):
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
                # DEBUG: Log each result for section architect
                logger.info(f"[DEBUG] Parallel result '{name}': section_idx={section_idx}, success={result.success}, output_len={len(result.output) if result.output else 0}")
                # Collect section HTML for merging
                if section_idx >= 0 and result.success:
                    section_htmls.append((section_idx, result.output))
                elif section_idx >= 0 and not result.success:
                    logger.warning(f"[DEBUG] Section architect '{name}' failed: {result.errors}")

        # === Merge Strategy: Section Architects (PAGE Pipeline) ===
        # DEBUG: Log section_htmls and section_indices
        logger.info(f"[DEBUG] section_htmls count={len(section_htmls)}, section_indices={section_indices}")
        if section_htmls:
            section_htmls.sort(key=lambda x: x[0])
            merged_html = "\n\n".join(html for _, html in section_htmls)
            context.html_output = merged_html
            context.previous_output = merged_html
            logger.info(f"Merged {len(section_htmls)} section HTMLs, total chars={len(merged_html)}")
        elif is_section_group and section_indices:
            # BUG #16 FIX: Fallback when all parallel section architects fail
            logger.warning(f"[BUG16-FIX] All {len(section_indices)} section architects failed! Attempting sequential fallback...")
            
            # Collect error info from failed results
            failed_sections = []
            for name, result in result_map.items():
                if not result.success:
                    error_msg = result.errors[0][:100] if result.errors else 'No error message'
                    failed_sections.append(f"{name}: {error_msg}")
            
            if failed_sections:
                logger.error(f"[BUG16-FIX] Failed sections:\n" + "\n".join(failed_sections))
            
            # SEQUENTIAL FALLBACK: Try running sections one by one
            sequential_htmls = []
            sections = context.sections if context.sections else []
            
            for idx, section in enumerate(sections):
                try:
                    section_type = section.get("type", f"section_{idx}")
                    logger.info(f"[BUG16-FIX] Sequential fallback - attempting section {idx}: {section_type}")
                    
                    # Create context for this section
                    step_context = context.fork_for_parallel(
                        step_index=idx,
                        section_type=section_type,
                    )
                    step_context.component_type = section_type
                    
                    # Get architect agent and execute
                    architect = self.get_agent("architect")
                    if architect:
                        seq_result = await architect.execute(step_context)
                        if seq_result.success and seq_result.output:
                            sequential_htmls.append((idx, seq_result.output))
                            logger.info(f"[BUG16-FIX] Sequential section {idx} SUCCESS: {len(seq_result.output)} chars")
                        else:
                            logger.warning(f"[BUG16-FIX] Sequential section {idx} FAILED: {seq_result.errors}")
                except Exception as e:
                    logger.error(f"[BUG16-FIX] Sequential section {idx} EXCEPTION: {e}")
            
            if sequential_htmls:
                # Sequential fallback succeeded - use those results
                sequential_htmls.sort(key=lambda x: x[0])
                merged_html = "\n\n".join(html for _, html in sequential_htmls)
                context.html_output = merged_html
                context.previous_output = merged_html
                logger.info(f"[BUG16-FIX] Sequential fallback SUCCESS: merged {len(sequential_htmls)} sections, {len(merged_html)} chars")
            else:
                # Even sequential failed - set error HTML
                fallback_html = f'''<!-- SECTION: error -->
<div class="min-h-screen flex items-center justify-center bg-slate-100 dark:bg-slate-900">
    <div class="text-center p-8 bg-white dark:bg-slate-800 rounded-xl shadow-lg max-w-md">
        <svg class="w-16 h-16 mx-auto text-amber-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">Sayfa Oluşturulamadı</h2>
        <p class="text-slate-600 dark:text-slate-300 mb-4">Paralel ve sequential oluşturma başarısız oldu. Lütfen <code class="bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">use_trifecta=False</code> ile tekrar deneyin.</p>
        <p class="text-xs text-slate-400">Hata: {len(section_indices)} section hem paralel hem sequential olarak başarısız</p>
    </div>
</div>
<!-- /SECTION: error -->'''
                context.html_output = fallback_html
                context.previous_output = fallback_html
                logger.warning(f"[BUG16-FIX] Both parallel and sequential failed, set error HTML ({len(fallback_html)} chars)")
        else:
            logger.warning(f"[DEBUG] No section HTMLs to merge! is_section_group={is_section_group}, section_indices={section_indices}")

        # === Merge Strategy: Styling + Interaction (COMPONENT Pipeline) ===
        if is_styling_group:
            self._merge_styling_interaction_results(result_map, context)

        return result_map

    def _merge_styling_interaction_results(
        self,
        results: dict[str, "AgentResult"],
        context: AgentContext,
    ) -> None:
        """
        Merge CSS and JS outputs from parallel Alchemist + Physicist execution.

        This is the core merge strategy for COMPONENT pipeline parallel execution.
        Each agent's output is stored in the appropriate context field:
        - Alchemist output → context.css_output
        - Physicist output → context.js_output

        Args:
            results: Map of agent_name → AgentResult from parallel execution
            context: Pipeline context to update with merged outputs
        """
        css_merged = False
        js_merged = False

        for agent_name, result in results.items():
            if not result.success:
                continue

            # Alchemist → CSS output
            if agent_name == "alchemist" and result.output:
                context.css_output = result.output
                context.set_output("alchemist", result.output)
                css_merged = True
                logger.debug(
                    f"[ParallelMerge] CSS merged: {len(result.output)} chars"
                )

            # Physicist → JS output
            elif agent_name == "physicist" and result.output:
                context.js_output = result.output
                context.set_output("physicist", result.output)
                js_merged = True
                logger.debug(
                    f"[ParallelMerge] JS merged: {len(result.output)} chars"
                )

        logger.info(
            f"[ParallelMerge] Styling+Interaction complete. "
            f"CSS: {'✓' if css_merged else '✗'}, "
            f"JS: {'✓' if js_merged else '✗'}"
        )

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
