"""
Pipeline Definitions - Multi-Agent Workflow Configuration

This module defines the different pipelines used by MCP design tools.
Each pipeline specifies which agents run in what order.

Pipeline Types:
    COMPONENT: design_frontend → Architect → Alchemist → Physicist → QualityGuard
    PAGE: design_page → Strategist → [Architect × N] → Alchemist → Physicist → QualityGuard
    SECTION: design_section → Strategist(DNA) → Architect → Alchemist → Physicist
    REFINE: refine_frontend → Critic → Architect → Alchemist → Physicist → QualityGuard
    REFERENCE: design_from_reference → Visionary → Strategist → Architect → Alchemist → Physicist
    REPLACE: replace_section_in_page → Strategist(Surgeon) → Architect → Alchemist → Physicist → QualityGuard
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from gemini_mcp.agents.base import AgentRole, BaseAgent
    from gemini_mcp.orchestration.context import AgentContext


class PipelineType(Enum):
    """Types of pipelines corresponding to MCP design tools."""

    COMPONENT = "component"  # design_frontend
    PAGE = "page"  # design_page
    SECTION = "section"  # design_section
    REFINE = "refine"  # refine_frontend
    REFERENCE = "reference"  # design_from_reference
    REPLACE = "replace"  # replace_section_in_page


@dataclass
class PipelineStep:
    """
    A single step in a pipeline.

    Attributes:
        agent_name: Name of the agent to execute (e.g., "architect")
        output_type: Type of output this agent produces ("html", "css", "js", "dna")
        required: Whether this step must succeed for pipeline to continue
        recoverable: Whether errors in this step can be recovered from
        compress_output: Whether to compress output for next agent
        parallel: Whether this step can run in parallel with others
        condition: Optional function to check if step should run
    """

    agent_name: str
    output_type: str = "html"
    required: bool = True
    recoverable: bool = True
    compress_output: bool = True
    parallel: bool = False
    condition: Optional[Callable[["AgentContext"], bool]] = None

    def should_run(self, context: "AgentContext") -> bool:
        """Check if this step should run given the context."""
        # Check skip list
        if context.should_skip_agent(self.agent_name):
            return False

        # Check custom condition
        if self.condition and not self.condition(context):
            return False

        return True


@dataclass
class ParallelGroup:
    """
    A group of steps that can run in parallel.

    Used for design_page where multiple sections can be generated concurrently.
    """

    steps: list[PipelineStep] = field(default_factory=list)
    name: str = ""

    def add_step(self, step: PipelineStep) -> None:
        """Add a step to this parallel group."""
        step.parallel = True
        self.steps.append(step)


@dataclass
class Pipeline:
    """
    A complete pipeline definition.

    A pipeline is a sequence of steps (and parallel groups) that defines
    which agents run in what order to complete a design task.
    """

    pipeline_type: PipelineType
    name: str
    description: str
    steps: list[PipelineStep | ParallelGroup] = field(default_factory=list)

    # Configuration
    max_retries: int = 2
    timeout_seconds: float = 300.0
    enable_checkpoints: bool = True

    def add_step(self, step: PipelineStep) -> "Pipeline":
        """Add a sequential step to the pipeline."""
        self.steps.append(step)
        return self

    def add_parallel_group(self, group: ParallelGroup) -> "Pipeline":
        """Add a parallel group to the pipeline."""
        self.steps.append(group)
        return self

    def get_agent_sequence(self) -> list[str]:
        """Get flat list of agent names in execution order."""
        agents = []
        for step in self.steps:
            if isinstance(step, ParallelGroup):
                agents.extend([s.agent_name for s in step.steps])
            else:
                agents.append(step.agent_name)
        return agents

    def count_steps(self) -> int:
        """Count total number of agent executions."""
        count = 0
        for step in self.steps:
            if isinstance(step, ParallelGroup):
                count += len(step.steps)
            else:
                count += 1
        return count


# === Pipeline Factory Functions ===


def create_component_pipeline() -> Pipeline:
    """
    Create pipeline for design_frontend.

    Flow: Architect → Alchemist → Physicist → QualityGuard
    """
    return Pipeline(
        pipeline_type=PipelineType.COMPONENT,
        name="Component Pipeline",
        description="Generate a single UI component with HTML, CSS, and JS",
        steps=[
            PipelineStep(
                agent_name="architect",
                output_type="html",
                compress_output=True,
            ),
            PipelineStep(
                agent_name="alchemist",
                output_type="css",
                compress_output=True,
                # Skip for simple themes
                condition=lambda ctx: ctx.theme not in ["modern-minimal"],
            ),
            PipelineStep(
                agent_name="physicist",
                output_type="js",
                compress_output=False,  # Final JS doesn't need compression
            ),
            PipelineStep(
                agent_name="quality_guard",
                output_type="validation",
                required=False,  # Validation failures don't block output
                recoverable=True,
            ),
        ],
    )


def create_page_pipeline(section_count: int = 1) -> Pipeline:
    """
    Create pipeline for design_page.

    Flow: Strategist → [Architect × N] → Alchemist → Physicist → QualityGuard
    """
    pipeline = Pipeline(
        pipeline_type=PipelineType.PAGE,
        name="Page Pipeline",
        description="Generate a complete page with multiple sections",
        steps=[
            PipelineStep(
                agent_name="strategist",
                output_type="dna",
                compress_output=False,
            ),
        ],
    )

    # Add parallel group for section architects
    if section_count > 1:
        parallel = ParallelGroup(name="section_architects")
        for i in range(section_count):
            parallel.add_step(
                PipelineStep(
                    agent_name="architect",
                    output_type="html",
                    compress_output=True,
                )
            )
        pipeline.add_parallel_group(parallel)
    else:
        pipeline.add_step(
            PipelineStep(
                agent_name="architect",
                output_type="html",
                compress_output=True,
            )
        )

    # Add remaining steps
    pipeline.add_step(
        PipelineStep(
            agent_name="alchemist",
            output_type="css",
            compress_output=True,
        )
    ).add_step(
        PipelineStep(
            agent_name="physicist",
            output_type="js",
            compress_output=False,
        )
    ).add_step(
        PipelineStep(
            agent_name="quality_guard",
            output_type="validation",
            required=False,
        )
    )

    return pipeline


def create_section_pipeline() -> Pipeline:
    """
    Create pipeline for design_section.

    Flow: Strategist(DNA) → Architect → Alchemist → Physicist
    """
    return Pipeline(
        pipeline_type=PipelineType.SECTION,
        name="Section Pipeline",
        description="Generate a single page section matching existing style",
        steps=[
            PipelineStep(
                agent_name="strategist",
                output_type="dna",
                compress_output=False,
                # Only run if there's previous HTML to extract DNA from
                condition=lambda ctx: bool(ctx.previous_html),
            ),
            PipelineStep(
                agent_name="architect",
                output_type="html",
                compress_output=True,
            ),
            PipelineStep(
                agent_name="alchemist",
                output_type="css",
                compress_output=True,
            ),
            PipelineStep(
                agent_name="physicist",
                output_type="js",
                compress_output=False,
            ),
        ],
    )


def create_refine_pipeline() -> Pipeline:
    """
    Create pipeline for refine_frontend.

    Flow: Critic → Architect → Alchemist → Physicist → QualityGuard
    """
    return Pipeline(
        pipeline_type=PipelineType.REFINE,
        name="Refine Pipeline",
        description="Refine existing design based on user feedback",
        steps=[
            PipelineStep(
                agent_name="critic",
                output_type="analysis",
                compress_output=False,
            ),
            PipelineStep(
                agent_name="architect",
                output_type="html",
                compress_output=True,
            ),
            PipelineStep(
                agent_name="alchemist",
                output_type="css",
                compress_output=True,
            ),
            PipelineStep(
                agent_name="physicist",
                output_type="js",
                compress_output=False,
            ),
            PipelineStep(
                agent_name="quality_guard",
                output_type="validation",
                required=False,
            ),
        ],
    )


def create_reference_pipeline() -> Pipeline:
    """
    Create pipeline for design_from_reference.

    Flow: Visionary → Strategist → Architect → Alchemist → Physicist
    """
    return Pipeline(
        pipeline_type=PipelineType.REFERENCE,
        name="Reference Pipeline",
        description="Generate design based on reference image",
        steps=[
            PipelineStep(
                agent_name="visionary",
                output_type="analysis",
                compress_output=False,
            ),
            PipelineStep(
                agent_name="strategist",
                output_type="dna",
                compress_output=False,
            ),
            PipelineStep(
                agent_name="architect",
                output_type="html",
                compress_output=True,
            ),
            PipelineStep(
                agent_name="alchemist",
                output_type="css",
                compress_output=True,
            ),
            PipelineStep(
                agent_name="physicist",
                output_type="js",
                compress_output=False,
            ),
        ],
    )


def create_replace_pipeline() -> Pipeline:
    """
    Create pipeline for replace_section_in_page.

    Flow: Strategist(Surgeon) → Architect → Alchemist → Physicist → QualityGuard
    """
    return Pipeline(
        pipeline_type=PipelineType.REPLACE,
        name="Replace Section Pipeline",
        description="Replace a single section in an existing page",
        steps=[
            PipelineStep(
                agent_name="strategist",
                output_type="dna",
                compress_output=False,
            ),
            PipelineStep(
                agent_name="architect",
                output_type="html",
                compress_output=True,
            ),
            PipelineStep(
                agent_name="alchemist",
                output_type="css",
                compress_output=True,
            ),
            PipelineStep(
                agent_name="physicist",
                output_type="js",
                compress_output=False,
            ),
            PipelineStep(
                agent_name="quality_guard",
                output_type="validation",
                required=False,
            ),
        ],
    )


def get_pipeline(pipeline_type: PipelineType, **kwargs) -> Pipeline:
    """
    Factory function to get a pipeline by type.

    Args:
        pipeline_type: Type of pipeline to create
        **kwargs: Additional arguments (e.g., section_count for PAGE)

    Returns:
        Configured Pipeline instance
    """
    factories = {
        PipelineType.COMPONENT: create_component_pipeline,
        PipelineType.PAGE: create_page_pipeline,
        PipelineType.SECTION: create_section_pipeline,
        PipelineType.REFINE: create_refine_pipeline,
        PipelineType.REFERENCE: create_reference_pipeline,
        PipelineType.REPLACE: create_replace_pipeline,
    }

    factory = factories.get(pipeline_type)
    if factory is None:
        raise ValueError(f"Unknown pipeline type: {pipeline_type}")

    if pipeline_type == PipelineType.PAGE and "section_count" in kwargs:
        return factory(section_count=kwargs["section_count"])

    return factory()
