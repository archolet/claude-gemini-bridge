"""
Workflow Orchestration Module for Gemini MCP Server.

GAP 11: Provides structured workflows for multi-step design generation
with parallel execution support and approval checkpoints.

This module enables:
- Declarative workflow definition
- Parallel section generation
- Approval checkpoints between phases
- Progress tracking and resumability
- Error recovery and rollback
"""

from dataclasses import dataclass, field
from typing import (
    Dict, List, Optional, Any, Callable, Awaitable
)
from enum import Enum
from datetime import datetime
import asyncio
import uuid


# =============================================================================
# TYPES AND ENUMS
# =============================================================================

class StepStatus(Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    """Overall workflow status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"          # Waiting for approval
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CheckpointType(Enum):
    """Types of approval checkpoints."""
    NONE = "none"                     # No approval needed
    REVIEW = "review"                 # Show output, continue on any response
    APPROVE_REJECT = "approve_reject" # Must explicitly approve to continue
    MODIFY = "modify"                 # Allow modifications before continuing


# =============================================================================
# STEP DEFINITIONS
# =============================================================================

@dataclass
class StepResult:
    """Result of a workflow step execution."""
    step_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """
    Definition of a single workflow step.

    Attributes:
        id: Unique step identifier
        name: Human-readable step name
        description: What this step does
        action: The action to execute (callable or tool name)
        params: Parameters for the action
        depends_on: List of step IDs this step depends on
        parallel_group: Steps in same group can run in parallel
        checkpoint: Type of approval checkpoint after step
        optional: If True, workflow continues even if step fails
        retry_count: Number of retries on failure
    """
    id: str
    name: str
    description: str = ""
    action: str = ""  # Tool name or callable identifier
    params: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None
    checkpoint: CheckpointType = CheckpointType.NONE
    optional: bool = False
    retry_count: int = 0

    # Runtime state
    status: StepStatus = StepStatus.PENDING
    result: Optional[StepResult] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ParallelGroup:
    """Group of steps that can execute in parallel."""
    id: str
    step_ids: List[str]
    checkpoint_after: CheckpointType = CheckpointType.NONE


# =============================================================================
# WORKFLOW DEFINITION
# =============================================================================

@dataclass
class WorkflowDefinition:
    """
    Complete workflow definition.

    Example:
        workflow = WorkflowDefinition(
            name="Landing Page Design",
            steps=[
                WorkflowStep(id="hero", name="Design Hero", action="design_section", params={"section_type": "hero"}),
                WorkflowStep(id="features", name="Design Features", action="design_section", params={"section_type": "features"}, parallel_group="content"),
                WorkflowStep(id="pricing", name="Design Pricing", action="design_section", params={"section_type": "pricing"}, parallel_group="content"),
                WorkflowStep(id="combine", name="Combine Sections", depends_on=["hero", "features", "pricing"]),
            ],
            parallel_groups=[
                ParallelGroup(id="content", step_ids=["features", "pricing"])
            ]
        )
    """
    name: str
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    parallel_groups: List[ParallelGroup] = field(default_factory=list)

    # Configuration
    stop_on_failure: bool = True
    global_timeout_seconds: int = 600  # 10 minutes
    checkpoint_before_combine: bool = True

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_parallel_group(self, group_id: str) -> Optional[ParallelGroup]:
        """Get parallel group by ID."""
        for group in self.parallel_groups:
            if group.id == group_id:
                return group
        return None

    def get_execution_order(self) -> List[List[str]]:
        """
        Get step execution order respecting dependencies and parallel groups.

        Returns:
            List of lists - each inner list contains step IDs that can run in parallel
        """
        completed = set()
        order = []
        remaining = {step.id for step in self.steps}

        while remaining:
            # Find steps whose dependencies are all complete
            ready = []
            for step in self.steps:
                if step.id not in remaining:
                    continue
                if all(dep in completed for dep in step.depends_on):
                    ready.append(step.id)

            if not ready:
                # Circular dependency or error
                raise ValueError(f"Cannot resolve dependencies for steps: {remaining}")

            # Group by parallel_group
            parallel_batch = []
            serial_steps = []

            for step_id in ready:
                step = self.get_step(step_id)
                if step.parallel_group:
                    # Check if all steps in the group are ready
                    group = self.get_parallel_group(step.parallel_group)
                    if group and all(gid in ready for gid in group.step_ids):
                        if step_id not in parallel_batch:
                            parallel_batch.extend(group.step_ids)
                    else:
                        serial_steps.append(step_id)
                else:
                    serial_steps.append(step_id)

            # Add parallel batch first
            if parallel_batch:
                order.append(list(set(parallel_batch)))
                for sid in parallel_batch:
                    completed.add(sid)
                    remaining.discard(sid)

            # Then serial steps
            for sid in serial_steps:
                if sid not in completed:
                    order.append([sid])
                    completed.add(sid)
                    remaining.discard(sid)

        return order


# =============================================================================
# WORKFLOW EXECUTOR
# =============================================================================

# Callback types
ApprovalCallback = Callable[[WorkflowStep, Any], Awaitable[bool]]
ProgressCallback = Callable[[str, WorkflowStep, float], Awaitable[None]]
ActionExecutor = Callable[[str, Dict[str, Any]], Awaitable[Any]]


@dataclass
class WorkflowContext:
    """Runtime context for workflow execution."""
    workflow_id: str
    definition: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.NOT_STARTED
    current_step_id: Optional[str] = None
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0  # 0.0 to 1.0

    def get_output(self, step_id: str) -> Any:
        """Get output from a completed step."""
        return self.outputs.get(step_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.definition.name,
            "status": self.status.value,
            "current_step_id": self.current_step_id,
            "progress": self.progress,
            "errors": self.errors,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "status": step.status.value,
                    "has_output": step.id in self.outputs,
                }
                for step in self.definition.steps
            ],
        }


class WorkflowExecutor:
    """
    Executes workflow definitions with parallel support and checkpoints.

    Example:
        executor = WorkflowExecutor(
            action_executor=my_action_handler,
            on_approval=my_approval_handler,
            on_progress=my_progress_handler
        )

        context = await executor.execute(workflow_definition)
        print(context.outputs)
    """

    def __init__(
        self,
        action_executor: ActionExecutor,
        on_approval: Optional[ApprovalCallback] = None,
        on_progress: Optional[ProgressCallback] = None,
    ):
        """
        Initialize workflow executor.

        Args:
            action_executor: Async function that executes actions
            on_approval: Callback for approval checkpoints
            on_progress: Callback for progress updates
        """
        self.action_executor = action_executor
        self.on_approval = on_approval
        self.on_progress = on_progress
        self._contexts: Dict[str, WorkflowContext] = {}

    async def execute(
        self,
        definition: WorkflowDefinition,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> WorkflowContext:
        """
        Execute a workflow definition.

        Args:
            definition: The workflow to execute
            initial_context: Initial values to inject into step params

        Returns:
            WorkflowContext with all outputs and status
        """
        workflow_id = str(uuid.uuid4())
        context = WorkflowContext(
            workflow_id=workflow_id,
            definition=definition,
            started_at=datetime.now()
        )
        self._contexts[workflow_id] = context

        try:
            context.status = WorkflowStatus.IN_PROGRESS
            execution_order = definition.get_execution_order()
            total_steps = len(definition.steps)

            for _batch_idx, batch in enumerate(execution_order):
                # Execute batch (possibly in parallel)
                if len(batch) > 1:
                    # Parallel execution
                    results = await self._execute_parallel(
                        context, batch, initial_context
                    )
                else:
                    # Single step
                    step_id = batch[0]
                    result = await self._execute_step(
                        context, step_id, initial_context
                    )
                    results = [result]

                # Check for failures
                for result in results:
                    if not result.success:
                        context.errors.append(
                            f"Step '{result.step_id}' failed: {result.error}"
                        )
                        if definition.stop_on_failure:
                            step = definition.get_step(result.step_id)
                            if step and not step.optional:
                                context.status = WorkflowStatus.FAILED
                                return context

                # Update progress
                completed = sum(
                    1 for s in definition.steps
                    if s.status == StepStatus.COMPLETED
                )
                context.progress = completed / total_steps

                if self.on_progress:
                    await self.on_progress(
                        workflow_id,
                        definition.steps[0],
                        context.progress
                    )

                # Handle checkpoints
                for step_id in batch:
                    step = definition.get_step(step_id)
                    if step and step.checkpoint != CheckpointType.NONE:
                        approved = await self._handle_checkpoint(context, step)
                        if not approved:
                            context.status = WorkflowStatus.CANCELLED
                            return context

            context.status = WorkflowStatus.COMPLETED
            context.completed_at = datetime.now()

        except asyncio.CancelledError:
            context.status = WorkflowStatus.CANCELLED
            raise
        except Exception as e:
            context.status = WorkflowStatus.FAILED
            context.errors.append(str(e))

        return context

    async def _execute_step(
        self,
        context: WorkflowContext,
        step_id: str,
        initial_context: Optional[Dict[str, Any]]
    ) -> StepResult:
        """Execute a single workflow step."""
        step = context.definition.get_step(step_id)
        if not step:
            return StepResult(
                step_id=step_id,
                success=False,
                error=f"Step '{step_id}' not found"
            )

        step.status = StepStatus.RUNNING
        step.started_at = datetime.now()
        context.current_step_id = step_id

        try:
            # Prepare params with initial context and previous outputs
            params = {**step.params}
            if initial_context:
                params["_context"] = initial_context

            # Inject outputs from dependencies
            for dep_id in step.depends_on:
                if dep_id in context.outputs:
                    params[f"_{dep_id}_output"] = context.outputs[dep_id]

            # Execute action with retries
            retries = 0
            last_error = None

            while retries <= step.retry_count:
                try:
                    start_time = datetime.now()
                    output = await self.action_executor(step.action, params)
                    duration = int((datetime.now() - start_time).total_seconds() * 1000)

                    # Success
                    step.status = StepStatus.COMPLETED
                    step.completed_at = datetime.now()
                    context.outputs[step_id] = output

                    result = StepResult(
                        step_id=step_id,
                        success=True,
                        output=output,
                        duration_ms=duration
                    )
                    step.result = result
                    return result

                except Exception as e:
                    last_error = str(e)
                    retries += 1
                    if retries <= step.retry_count:
                        await asyncio.sleep(1 * retries)  # Exponential backoff

            # All retries failed
            step.status = StepStatus.FAILED
            step.completed_at = datetime.now()
            result = StepResult(
                step_id=step_id,
                success=False,
                error=last_error
            )
            step.result = result
            return result

        except Exception as e:
            step.status = StepStatus.FAILED
            step.completed_at = datetime.now()
            result = StepResult(
                step_id=step_id,
                success=False,
                error=str(e)
            )
            step.result = result
            return result

    async def _execute_parallel(
        self,
        context: WorkflowContext,
        step_ids: List[str],
        initial_context: Optional[Dict[str, Any]]
    ) -> List[StepResult]:
        """Execute multiple steps in parallel."""
        tasks = [
            self._execute_step(context, step_id, initial_context)
            for step_id in step_ids
        ]
        return await asyncio.gather(*tasks)

    async def _handle_checkpoint(
        self,
        context: WorkflowContext,
        step: WorkflowStep
    ) -> bool:
        """Handle approval checkpoint."""
        if step.checkpoint == CheckpointType.NONE:
            return True

        step.status = StepStatus.WAITING_APPROVAL
        context.status = WorkflowStatus.PAUSED

        if self.on_approval:
            output = context.outputs.get(step.id)
            approved = await self.on_approval(step, output)

            if approved:
                step.status = StepStatus.APPROVED
                context.status = WorkflowStatus.IN_PROGRESS
                return True
            else:
                step.status = StepStatus.SKIPPED
                return False

        # No approval callback - auto-approve
        step.status = StepStatus.APPROVED
        context.status = WorkflowStatus.IN_PROGRESS
        return True

    def get_context(self, workflow_id: str) -> Optional[WorkflowContext]:
        """Get workflow context by ID."""
        return self._contexts.get(workflow_id)

    def cancel(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        context = self._contexts.get(workflow_id)
        if context and context.status == WorkflowStatus.IN_PROGRESS:
            context.status = WorkflowStatus.CANCELLED
            return True
        return False


# =============================================================================
# PREDEFINED WORKFLOWS
# =============================================================================

def create_landing_page_workflow(
    sections: List[str] = None,
    theme: str = "modern-minimal",
    parallel_content: bool = True
) -> WorkflowDefinition:
    """
    Create a standard landing page workflow.

    Args:
        sections: List of section types (default: hero, features, pricing, cta, footer)
        theme: Theme to use for all sections
        parallel_content: Whether to generate content sections in parallel

    Returns:
        WorkflowDefinition for landing page generation
    """
    if sections is None:
        sections = ["hero", "features", "testimonials", "pricing", "cta", "footer"]

    steps = []
    content_sections = []

    # Hero always comes first
    steps.append(WorkflowStep(
        id="hero",
        name="Design Hero Section",
        description="Create the main hero/banner section",
        action="design_section",
        params={"section_type": "hero", "theme": theme},
        checkpoint=CheckpointType.REVIEW
    ))

    # Content sections can be parallel
    for section in sections:
        if section == "hero":
            continue

        step = WorkflowStep(
            id=section,
            name=f"Design {section.title()} Section",
            description=f"Create the {section} section",
            action="design_section",
            params={"section_type": section, "theme": theme},
            depends_on=["hero"],  # Need hero for design tokens
            parallel_group="content" if parallel_content and section not in ["footer"] else None
        )
        steps.append(step)

        if parallel_content and section not in ["footer"]:
            content_sections.append(section)

    # Combine step
    steps.append(WorkflowStep(
        id="combine",
        name="Combine Sections",
        description="Merge all sections into final page",
        action="combine_sections",
        params={},
        depends_on=[s.id for s in steps],
        checkpoint=CheckpointType.APPROVE_REJECT
    ))

    # Define parallel groups
    parallel_groups = []
    if parallel_content and content_sections:
        parallel_groups.append(ParallelGroup(
            id="content",
            step_ids=content_sections
        ))

    return WorkflowDefinition(
        name="Landing Page Design",
        description=f"Generate a complete landing page with {len(sections)} sections",
        steps=steps,
        parallel_groups=parallel_groups,
        checkpoint_before_combine=True
    )


def create_component_library_workflow(
    components: List[str],
    theme: str = "modern-minimal",
    with_variants: bool = True
) -> WorkflowDefinition:
    """
    Create a component library generation workflow.

    Args:
        components: List of component types to generate
        theme: Theme to use
        with_variants: Generate size/state variants

    Returns:
        WorkflowDefinition for component library generation
    """
    steps = []

    for component in components:
        # Base component
        steps.append(WorkflowStep(
            id=f"{component}_base",
            name=f"Design {component.title()} Base",
            action="design_frontend",
            params={"component_type": component, "theme": theme},
            parallel_group="components"
        ))

        if with_variants:
            # Size variants
            for size in ["sm", "lg"]:
                steps.append(WorkflowStep(
                    id=f"{component}_{size}",
                    name=f"Design {component.title()} {size.upper()}",
                    action="design_frontend",
                    params={
                        "component_type": component,
                        "theme": theme,
                        "context": f"Size variant: {size}"
                    },
                    depends_on=[f"{component}_base"],
                    parallel_group=f"{component}_variants"
                ))

    # Documentation step
    steps.append(WorkflowStep(
        id="docs",
        name="Generate Documentation",
        action="generate_docs",
        params={},
        depends_on=[s.id for s in steps],
        optional=True
    ))

    # Build parallel groups
    parallel_groups = [
        ParallelGroup(id="components", step_ids=[
            f"{c}_base" for c in components
        ])
    ]

    if with_variants:
        for component in components:
            parallel_groups.append(ParallelGroup(
                id=f"{component}_variants",
                step_ids=[f"{component}_sm", f"{component}_lg"]
            ))

    return WorkflowDefinition(
        name="Component Library",
        description=f"Generate {len(components)} components with variants",
        steps=steps,
        parallel_groups=parallel_groups
    )


def create_iterative_design_workflow(
    component_type: str,
    max_iterations: int = 3,
    theme: str = "modern-minimal"
) -> WorkflowDefinition:
    """
    Create an iterative design refinement workflow.

    Each iteration allows for user feedback and refinement.
    """
    steps = []

    # Initial design
    steps.append(WorkflowStep(
        id="initial",
        name="Initial Design",
        action="design_frontend",
        params={"component_type": component_type, "theme": theme},
        checkpoint=CheckpointType.MODIFY
    ))

    # Refinement iterations
    for i in range(1, max_iterations + 1):
        steps.append(WorkflowStep(
            id=f"iteration_{i}",
            name=f"Refinement {i}",
            action="refine_frontend",
            params={},
            depends_on=[f"iteration_{i-1}" if i > 1 else "initial"],
            checkpoint=CheckpointType.MODIFY if i < max_iterations else CheckpointType.APPROVE_REJECT,
            optional=True
        ))

    return WorkflowDefinition(
        name=f"Iterative {component_type.title()} Design",
        description=f"Design {component_type} with up to {max_iterations} refinement iterations",
        steps=steps,
        stop_on_failure=False
    )


# =============================================================================
# WORKFLOW UTILITIES
# =============================================================================

def workflow_to_mermaid(definition: WorkflowDefinition) -> str:
    """
    Generate Mermaid diagram from workflow definition.

    Returns:
        Mermaid flowchart string
    """
    lines = ["graph TD"]

    for step in definition.steps:
        # Node
        shape_start = "((" if step.checkpoint != CheckpointType.NONE else "["
        shape_end = "))" if step.checkpoint != CheckpointType.NONE else "]"
        lines.append(f"    {step.id}{shape_start}\"{step.name}\"{shape_end}")

        # Dependencies
        for dep in step.depends_on:
            lines.append(f"    {dep} --> {step.id}")

    # Style parallel groups
    for group in definition.parallel_groups:
        lines.append(f"    subgraph {group.id}[Parallel]")
        for step_id in group.step_ids:
            lines.append(f"        {step_id}")
        lines.append("    end")

    return "\n".join(lines)


def estimate_workflow_time(definition: WorkflowDefinition) -> Dict[str, Any]:
    """
    Estimate workflow execution time.

    Returns:
        Dict with estimated times
    """
    # Rough estimates per action type (in seconds)
    time_estimates = {
        "design_section": 15,
        "design_frontend": 10,
        "design_page": 30,
        "refine_frontend": 8,
        "combine_sections": 2,
        "generate_docs": 5,
    }

    execution_order = definition.get_execution_order()

    total_serial = 0
    total_parallel_saved = 0

    for batch in execution_order:
        batch_times = []
        for step_id in batch:
            step = definition.get_step(step_id)
            if step:
                est = time_estimates.get(step.action, 10)
                batch_times.append(est)

        if len(batch) > 1:
            # Parallel - take max
            total_serial += max(batch_times)
            total_parallel_saved += sum(batch_times) - max(batch_times)
        else:
            total_serial += sum(batch_times)

    return {
        "estimated_seconds": total_serial,
        "parallel_savings_seconds": total_parallel_saved,
        "step_count": len(definition.steps),
        "parallel_group_count": len(definition.parallel_groups),
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "StepStatus",
    "WorkflowStatus",
    "CheckpointType",

    # Core classes
    "StepResult",
    "WorkflowStep",
    "ParallelGroup",
    "WorkflowDefinition",
    "WorkflowContext",
    "WorkflowExecutor",

    # Predefined workflows
    "create_landing_page_workflow",
    "create_component_library_workflow",
    "create_iterative_design_workflow",

    # Utilities
    "workflow_to_mermaid",
    "estimate_workflow_time",
]
