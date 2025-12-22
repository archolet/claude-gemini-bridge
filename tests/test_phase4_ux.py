"""Tests for Phase 4 UX implementations.

GAP 10: Design System Consistency - spacing, typography, component sizes
GAP 11: Workflow Orchestration - parallel execution, checkpoints, predefined workflows
"""

import pytest
import asyncio

from gemini_mcp.design_system import (
    # Spacing
    SpacingScale,
    SPACING_TO_TAILWIND,
    spacing_class,
    # Typography
    TypeStyle,
    TYPOGRAPHY_SCALE,
    get_type_classes,
    # Icons
    IconSize,
    ICON_SIZE_CLASSES,
    icon_classes,
    # Breakpoints
    Breakpoint,
    BREAKPOINTS,
    responsive_class,
    # Z-index
    ZLayer,
    Z_INDEX_CLASSES,
    # Animations
    AnimationPreset,
    ANIMATION_PRESETS,
    animation_classes,
    # Border radius
    BorderRadius,
    BORDER_RADIUS_CLASSES,
    # Shadows
    ShadowSize,
    SHADOW_CLASSES,
    # Design System
    DesignSystemSpec,
    DESIGN_SYSTEM,
    validate_theme_spacing,
    validate_theme_typography,
    apply_design_system_to_theme,
    # Component sizes
    ComponentSizes,
    COMPONENT_SIZES,
    get_component_size,
)

from gemini_mcp.workflow import (
    # Enums
    StepStatus,
    WorkflowStatus,
    CheckpointType,
    # Core classes
    StepResult,
    WorkflowStep,
    ParallelGroup,
    WorkflowDefinition,
    WorkflowContext,
    WorkflowExecutor,
    # Predefined workflows
    create_landing_page_workflow,
    create_component_library_workflow,
    create_iterative_design_workflow,
    # Utilities
    workflow_to_mermaid,
    estimate_workflow_time,
)


# =============================================================================
# GAP 10: Design System Consistency Tests
# =============================================================================

class TestGAP10SpacingScale:
    """Tests for spacing scale consistency."""

    def test_spacing_scale_values(self):
        """Test that spacing scale follows 4px base unit."""
        # Core values should be multiples of 4 (except px)
        assert SpacingScale.NONE.value == 0
        assert SpacingScale.XS.value == 4
        assert SpacingScale.SM.value == 8
        assert SpacingScale.MD.value == 12
        assert SpacingScale.BASE.value == 16
        assert SpacingScale.LG.value == 24
        assert SpacingScale.XL.value == 32

    def test_spacing_to_tailwind_mapping(self):
        """Test Tailwind class mappings."""
        assert SPACING_TO_TAILWIND[SpacingScale.NONE] == "0"
        assert SPACING_TO_TAILWIND[SpacingScale.BASE] == "4"
        assert SPACING_TO_TAILWIND[SpacingScale.LG] == "6"
        assert SPACING_TO_TAILWIND[SpacingScale.XL] == "8"

    def test_spacing_class_generation(self):
        """Test spacing class helper."""
        assert spacing_class("p", SpacingScale.BASE) == "p-4"
        assert spacing_class("m", SpacingScale.LG) == "m-6"
        assert spacing_class("gap", SpacingScale.SM) == "gap-2"
        assert spacing_class("px", SpacingScale.XL) == "px-8"


class TestGAP10Typography:
    """Tests for typography scale consistency."""

    def test_typography_scale_coverage(self):
        """Test that all major typography styles are defined."""
        required_styles = [
            "display-xl", "display-lg",
            "heading-xl", "heading-lg", "heading-md", "heading-sm",
            "body-xl", "body-lg", "body-base", "body-sm", "body-xs",
            "label", "button", "caption", "overline"
        ]

        for style in required_styles:
            assert style in TYPOGRAPHY_SCALE, f"Missing typography style: {style}"

    def test_type_style_structure(self):
        """Test TypeStyle has all required fields."""
        style = TYPOGRAPHY_SCALE["body-base"]

        assert isinstance(style, TypeStyle)
        assert style.size_class
        assert style.line_height
        assert style.letter_spacing
        assert style.font_weight

    def test_get_type_classes(self):
        """Test type classes helper."""
        classes = get_type_classes("heading-lg")

        assert "text-" in classes
        assert "leading-" in classes
        assert "font-" in classes

    def test_type_classes_fallback(self):
        """Test fallback for unknown style."""
        classes = get_type_classes("nonexistent-style")

        # Should fall back to body-base
        assert "text-base" in classes


class TestGAP10Icons:
    """Tests for icon size consistency."""

    def test_icon_sizes_defined(self):
        """Test all icon sizes are defined."""
        assert len(IconSize) >= 6

    def test_icon_size_classes(self):
        """Test icon class generation."""
        assert icon_classes(IconSize.SM) == "w-4 h-4"
        assert icon_classes(IconSize.BASE) == "w-6 h-6"
        assert icon_classes(IconSize.LG) == "w-8 h-8"


class TestGAP10Breakpoints:
    """Tests for responsive breakpoint consistency."""

    def test_breakpoints_ordered(self):
        """Test breakpoints are in ascending order."""
        widths = [bp.min_width for bp in BREAKPOINTS]
        assert widths == sorted(widths)

    def test_responsive_class_generation(self):
        """Test responsive class helper."""
        result = responsive_class("p-4", {"md": "p-6", "lg": "p-8"})

        assert "p-4" in result
        assert "md:p-6" in result
        assert "lg:p-8" in result

    def test_standard_breakpoints_exist(self):
        """Test standard Tailwind breakpoints exist."""
        bp_names = [bp.name for bp in BREAKPOINTS]

        assert "sm" in bp_names
        assert "md" in bp_names
        assert "lg" in bp_names
        assert "xl" in bp_names


class TestGAP10ZIndex:
    """Tests for z-index layer consistency."""

    def test_z_layers_hierarchy(self):
        """Test z-index layers are properly ordered."""
        assert ZLayer.BASE.value < ZLayer.DROPDOWN.value
        assert ZLayer.DROPDOWN.value < ZLayer.MODAL.value
        assert ZLayer.MODAL.value < ZLayer.TOOLTIP.value
        assert ZLayer.TOOLTIP.value < ZLayer.TOAST.value

    def test_z_index_classes(self):
        """Test z-index class mapping."""
        assert Z_INDEX_CLASSES[ZLayer.MODAL] == "z-50"
        assert Z_INDEX_CLASSES[ZLayer.TOOLTIP] == "z-[70]"


class TestGAP10Animations:
    """Tests for animation presets."""

    def test_animation_presets_defined(self):
        """Test essential animation presets exist."""
        assert "fast" in ANIMATION_PRESETS
        assert "normal" in ANIMATION_PRESETS
        assert "slow" in ANIMATION_PRESETS
        assert "bouncy" in ANIMATION_PRESETS

    def test_animation_classes(self):
        """Test animation class generation."""
        classes = animation_classes("normal")

        assert "transition-" in classes
        assert "duration-" in classes
        assert "ease-" in classes


class TestGAP10DesignSystemSpec:
    """Tests for DesignSystemSpec class."""

    def test_global_design_system_exists(self):
        """Test global design system is available."""
        assert DESIGN_SYSTEM is not None
        assert isinstance(DESIGN_SYSTEM, DesignSystemSpec)

    def test_design_system_defaults(self):
        """Test design system default values."""
        assert DESIGN_SYSTEM.spacing_unit == 4
        assert DESIGN_SYSTEM.base_font_size == 16
        assert DESIGN_SYSTEM.min_touch_target == 44

    def test_validate_touch_target(self):
        """Test touch target validation."""
        assert DESIGN_SYSTEM.validate_touch_target(44, 44) is True
        assert DESIGN_SYSTEM.validate_touch_target(40, 40) is False
        assert DESIGN_SYSTEM.validate_touch_target(48, 32) is False


class TestGAP10ThemeValidation:
    """Tests for theme validation helpers."""

    def test_validate_theme_spacing(self):
        """Test spacing validation."""
        # Good theme
        good_theme = {"padding": "p-4", "margin": "m-6"}
        warnings = validate_theme_spacing(good_theme)
        assert len(warnings) == 0

    def test_validate_theme_typography(self):
        """Test typography validation."""
        # Good theme
        good_theme = {"title": "text-xl font-bold"}
        warnings = validate_theme_typography(good_theme)
        assert len(warnings) == 0

    def test_apply_design_system_to_theme(self):
        """Test design system application."""
        theme = {"name": "test-theme"}
        enhanced = apply_design_system_to_theme(theme)

        assert "_design_system" in enhanced
        assert "semantic_colors" in enhanced
        assert enhanced["_design_system"]["spacing_unit"] == 4


class TestGAP10ComponentSizes:
    """Tests for component size presets."""

    def test_component_sizes_exist(self):
        """Test component sizes are defined."""
        assert COMPONENT_SIZES.button_sm
        assert COMPONENT_SIZES.button_md
        assert COMPONENT_SIZES.button_lg

    def test_get_component_size(self):
        """Test component size helper."""
        btn_md = get_component_size("button", "md")
        assert "px-" in btn_md
        assert "py-" in btn_md

        card_lg = get_component_size("card", "lg")
        assert "p-" in card_lg


# =============================================================================
# GAP 11: Workflow Orchestration Tests
# =============================================================================

class TestGAP11WorkflowDefinition:
    """Tests for WorkflowDefinition class."""

    def test_workflow_definition_basic(self):
        """Test basic workflow definition."""
        workflow = WorkflowDefinition(
            name="Test Workflow",
            steps=[
                WorkflowStep(id="step1", name="Step 1"),
                WorkflowStep(id="step2", name="Step 2", depends_on=["step1"]),
            ]
        )

        assert workflow.name == "Test Workflow"
        assert len(workflow.steps) == 2

    def test_get_step(self):
        """Test step retrieval by ID."""
        workflow = WorkflowDefinition(
            name="Test",
            steps=[WorkflowStep(id="step1", name="Step 1")]
        )

        step = workflow.get_step("step1")
        assert step is not None
        assert step.name == "Step 1"

        missing = workflow.get_step("nonexistent")
        assert missing is None

    def test_execution_order_simple(self):
        """Test execution order with simple dependencies."""
        workflow = WorkflowDefinition(
            name="Test",
            steps=[
                WorkflowStep(id="a", name="A"),
                WorkflowStep(id="b", name="B", depends_on=["a"]),
                WorkflowStep(id="c", name="C", depends_on=["b"]),
            ]
        )

        order = workflow.get_execution_order()

        assert len(order) == 3
        assert order[0] == ["a"]
        assert order[1] == ["b"]
        assert order[2] == ["c"]

    def test_execution_order_parallel(self):
        """Test execution order with parallel steps."""
        workflow = WorkflowDefinition(
            name="Test",
            steps=[
                WorkflowStep(id="a", name="A"),
                WorkflowStep(id="b", name="B", depends_on=["a"], parallel_group="p1"),
                WorkflowStep(id="c", name="C", depends_on=["a"], parallel_group="p1"),
                WorkflowStep(id="d", name="D", depends_on=["b", "c"]),
            ],
            parallel_groups=[
                ParallelGroup(id="p1", step_ids=["b", "c"])
            ]
        )

        order = workflow.get_execution_order()

        # a should be first
        assert order[0] == ["a"]

        # b and c should be in same batch (parallel)
        parallel_batch = order[1]
        assert "b" in parallel_batch
        assert "c" in parallel_batch


class TestGAP11WorkflowStep:
    """Tests for WorkflowStep class."""

    def test_step_defaults(self):
        """Test step default values."""
        step = WorkflowStep(id="test", name="Test Step")

        assert step.status == StepStatus.PENDING
        assert step.checkpoint == CheckpointType.NONE
        assert step.optional is False
        assert step.retry_count == 0

    def test_step_with_checkpoint(self):
        """Test step with approval checkpoint."""
        step = WorkflowStep(
            id="test",
            name="Test Step",
            checkpoint=CheckpointType.APPROVE_REJECT
        )

        assert step.checkpoint == CheckpointType.APPROVE_REJECT


class TestGAP11WorkflowExecutor:
    """Tests for WorkflowExecutor class."""

    @pytest.mark.asyncio
    async def test_executor_simple_workflow(self):
        """Test executing a simple workflow."""
        results = {}

        async def action_executor(action: str, params: dict):
            results[action] = params
            return f"Result for {action}"

        executor = WorkflowExecutor(action_executor=action_executor)

        workflow = WorkflowDefinition(
            name="Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", action="action1"),
            ]
        )

        context = await executor.execute(workflow)

        assert context.status == WorkflowStatus.COMPLETED
        assert "step1" in context.outputs
        assert "action1" in results

    @pytest.mark.asyncio
    async def test_executor_with_dependencies(self):
        """Test executor respects dependencies."""
        execution_order = []

        async def action_executor(action: str, params: dict):
            execution_order.append(action)
            return f"Result for {action}"

        executor = WorkflowExecutor(action_executor=action_executor)

        workflow = WorkflowDefinition(
            name="Test",
            steps=[
                WorkflowStep(id="a", name="A", action="action_a"),
                WorkflowStep(id="b", name="B", action="action_b", depends_on=["a"]),
            ]
        )

        await executor.execute(workflow)

        assert execution_order.index("action_a") < execution_order.index("action_b")

    @pytest.mark.asyncio
    async def test_executor_handles_failure(self):
        """Test executor handles step failure."""
        async def action_executor(action: str, params: dict):
            if action == "fail_action":
                raise ValueError("Intentional failure")
            return "Success"

        executor = WorkflowExecutor(action_executor=action_executor)

        workflow = WorkflowDefinition(
            name="Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", action="fail_action"),
            ],
            stop_on_failure=True
        )

        context = await executor.execute(workflow)

        assert context.status == WorkflowStatus.FAILED
        assert len(context.errors) > 0

    @pytest.mark.asyncio
    async def test_executor_progress_tracking(self):
        """Test progress tracking."""
        progress_updates = []

        async def action_executor(action: str, params: dict):
            return "Success"

        async def on_progress(workflow_id: str, step, progress: float):
            progress_updates.append(progress)

        executor = WorkflowExecutor(
            action_executor=action_executor,
            on_progress=on_progress
        )

        workflow = WorkflowDefinition(
            name="Test",
            steps=[
                WorkflowStep(id="s1", name="S1", action="a1"),
                WorkflowStep(id="s2", name="S2", action="a2", depends_on=["s1"]),
            ]
        )

        context = await executor.execute(workflow)

        assert context.progress == 1.0
        assert len(progress_updates) >= 1


class TestGAP11PredefinedWorkflows:
    """Tests for predefined workflow factories."""

    def test_landing_page_workflow(self):
        """Test landing page workflow creation."""
        workflow = create_landing_page_workflow()

        assert workflow.name == "Landing Page Design"
        assert len(workflow.steps) >= 6  # hero + sections + combine

        # Check hero is first step with no dependencies
        hero_step = workflow.get_step("hero")
        assert hero_step is not None
        assert len(hero_step.depends_on) == 0

    def test_landing_page_workflow_custom_sections(self):
        """Test landing page workflow with custom sections."""
        workflow = create_landing_page_workflow(
            sections=["hero", "features", "footer"],
            theme="cyberpunk"
        )

        assert len(workflow.steps) == 4  # 3 sections + combine

        features = workflow.get_step("features")
        assert features.params["theme"] == "cyberpunk"

    def test_component_library_workflow(self):
        """Test component library workflow creation."""
        workflow = create_component_library_workflow(
            components=["button", "card"],
            with_variants=True
        )

        assert "Component Library" in workflow.name

        # Should have base + variants for each component
        assert workflow.get_step("button_base") is not None
        assert workflow.get_step("button_sm") is not None
        assert workflow.get_step("button_lg") is not None

    def test_iterative_design_workflow(self):
        """Test iterative design workflow creation."""
        workflow = create_iterative_design_workflow(
            component_type="button",
            max_iterations=3
        )

        # Should have initial + 3 iterations
        assert workflow.get_step("initial") is not None
        assert workflow.get_step("iteration_1") is not None
        assert workflow.get_step("iteration_3") is not None


class TestGAP11WorkflowUtilities:
    """Tests for workflow utility functions."""

    def test_workflow_to_mermaid(self):
        """Test Mermaid diagram generation."""
        workflow = WorkflowDefinition(
            name="Test",
            steps=[
                WorkflowStep(id="a", name="Step A"),
                WorkflowStep(id="b", name="Step B", depends_on=["a"]),
            ]
        )

        mermaid = workflow_to_mermaid(workflow)

        assert "graph TD" in mermaid
        assert "Step A" in mermaid
        assert "Step B" in mermaid
        assert "a --> b" in mermaid

    def test_estimate_workflow_time(self):
        """Test workflow time estimation."""
        workflow = create_landing_page_workflow()
        estimate = estimate_workflow_time(workflow)

        assert "estimated_seconds" in estimate
        assert "step_count" in estimate
        assert estimate["step_count"] == len(workflow.steps)
        assert estimate["estimated_seconds"] > 0


class TestGAP11WorkflowContext:
    """Tests for WorkflowContext class."""

    def test_context_to_dict(self):
        """Test context serialization."""
        workflow = WorkflowDefinition(
            name="Test",
            steps=[WorkflowStep(id="s1", name="S1")]
        )

        context = WorkflowContext(
            workflow_id="test-123",
            definition=workflow,
            status=WorkflowStatus.IN_PROGRESS
        )

        data = context.to_dict()

        assert data["workflow_id"] == "test-123"
        assert data["name"] == "Test"
        assert data["status"] == "in_progress"
        assert len(data["steps"]) == 1


# =============================================================================
# Integration Tests
# =============================================================================

class TestPhase4Integration:
    """Integration tests for Phase 4 modules."""

    def test_design_system_with_workflow(self):
        """Test design system can be used in workflow params."""
        section_padding = get_component_size("section", "lg")

        workflow = create_landing_page_workflow()
        hero_step = workflow.get_step("hero")

        # Can inject design system values
        hero_step.params["padding"] = section_padding
        assert "py-" in hero_step.params["padding"]

    def test_modules_importable(self):
        """Test all Phase 4 modules can be imported."""
        from gemini_mcp import design_system
        from gemini_mcp import workflow

        assert hasattr(design_system, "DESIGN_SYSTEM")
        assert hasattr(workflow, "WorkflowExecutor")

    def test_workflow_with_checkpoints(self):
        """Test workflow definition with approval checkpoints."""
        workflow = create_landing_page_workflow()

        # Hero should have review checkpoint
        hero = workflow.get_step("hero")
        assert hero.checkpoint == CheckpointType.REVIEW

        # Combine should have approve/reject
        combine = workflow.get_step("combine")
        assert combine.checkpoint == CheckpointType.APPROVE_REJECT

    @pytest.mark.asyncio
    async def test_full_workflow_execution(self):
        """Test complete workflow execution flow."""
        outputs = {}

        async def action_executor(action: str, params: dict):
            result = f"<div>HTML for {action}</div>"
            outputs[action] = result
            return result

        async def on_approval(step, output):
            # Auto-approve all
            return True

        executor = WorkflowExecutor(
            action_executor=action_executor,
            on_approval=on_approval
        )

        workflow = WorkflowDefinition(
            name="Test",
            steps=[
                WorkflowStep(id="s1", name="S1", action="a1", checkpoint=CheckpointType.REVIEW),
                WorkflowStep(id="s2", name="S2", action="a2", depends_on=["s1"]),
            ]
        )

        context = await executor.execute(workflow)

        assert context.status == WorkflowStatus.COMPLETED
        assert "s1" in context.outputs
        assert "s2" in context.outputs
