#!/usr/bin/env python3
"""
Demo Script: All Phase 1-4 Features

This script demonstrates all the features implemented across 4 phases:
- Phase 1: Token Schema, Section Markers, Error Handling
- Phase 2: Token Extraction, Responsive Validation, A11y Enforcement
- Phase 3: Prompt Builder, JS Fallbacks, Caching, Telemetry
- Phase 4: Design System, Workflow Orchestration

Run: python examples/demo_all_features.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gemini_mcp.design_system import (
    DESIGN_SYSTEM,
    TYPOGRAPHY_SCALE,
    COMPONENT_SIZES,
    SpacingScale,
    spacing_class,
    get_type_classes,
    get_component_size,
    responsive_class,
    animation_classes,
    apply_design_system_to_theme,
    validate_theme_spacing,
)

from gemini_mcp.workflow import (
    WorkflowDefinition,
    WorkflowStep,
    ParallelGroup,
    WorkflowExecutor,
    CheckpointType,
    StepStatus,
    create_landing_page_workflow,
    workflow_to_mermaid,
    estimate_workflow_time,
)

from gemini_mcp.js_fallbacks import (
    get_js_module,
    inject_js_fallbacks,
    detect_needed_modules,
    get_all_module_names,
)

from gemini_mcp.telemetry import (
    Telemetry,
    get_telemetry_summary,
)

from gemini_mcp.validators import (
    validate_design_output,
    auto_fix_design,
    A11yValidator,
    validate_responsive,
)

from gemini_mcp.prompt_builder import (
    PromptBuilder,
    build_component_prompt,
)

from gemini_mcp.cache import (
    DesignCache,
    get_design_cache,
)


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_design_system():
    """Demonstrate Design System features (GAP 10)."""
    print_header("PHASE 4 - GAP 10: Design System")

    # Spacing
    print("\n📏 Spacing Scale:")
    print(f"  Base unit: {DESIGN_SYSTEM.spacing_unit}px")
    print(f"  p-4 (BASE): {spacing_class('p', SpacingScale.BASE)}")
    print(f"  gap-6 (LG): {spacing_class('gap', SpacingScale.LG)}")
    print(f"  m-8 (XL): {spacing_class('m', SpacingScale.XL)}")

    # Typography
    print("\n📝 Typography Scale:")
    print(f"  Display XL: {get_type_classes('display-xl')[:50]}...")
    print(f"  Heading LG: {get_type_classes('heading-lg')[:50]}...")
    print(f"  Body Base: {get_type_classes('body-base')}")

    # Component Sizes
    print("\n📦 Component Sizes:")
    print(f"  Button MD: {get_component_size('button', 'md')}")
    print(f"  Card LG: {get_component_size('card', 'lg')}")
    print(f"  Section XL: {get_component_size('section', 'xl')}")

    # Responsive Classes
    print("\n📱 Responsive Classes:")
    resp = responsive_class("p-4", {"md": "p-6", "lg": "p-8"})
    print(f"  Responsive padding: {resp}")

    # Animation Presets
    print("\n✨ Animation Presets:")
    print(f"  Normal: {animation_classes('normal')}")
    print(f"  Bouncy: {animation_classes('bouncy')}")

    # Touch Target Validation
    print("\n👆 Touch Target Validation:")
    print(f"  44x44px valid: {DESIGN_SYSTEM.validate_touch_target(44, 44)}")
    print(f"  32x32px valid: {DESIGN_SYSTEM.validate_touch_target(32, 32)}")


def demo_workflow():
    """Demonstrate Workflow Orchestration (GAP 11)."""
    print_header("PHASE 4 - GAP 11: Workflow Orchestration")

    # Create landing page workflow
    workflow = create_landing_page_workflow(
        sections=["hero", "features", "pricing", "footer"],
        theme="modern-minimal",
        parallel_content=True
    )

    print(f"\n📋 Workflow: {workflow.name}")
    print(f"   Steps: {len(workflow.steps)}")
    print(f"   Parallel Groups: {len(workflow.parallel_groups)}")

    # Show execution order
    print("\n🔄 Execution Order:")
    try:
        order = workflow.get_execution_order()
        for i, batch in enumerate(order):
            if len(batch) > 1:
                print(f"   {i+1}. [PARALLEL] {', '.join(batch)}")
            else:
                print(f"   {i+1}. {batch[0]}")
    except Exception as e:
        print(f"   Error: {e}")

    # Time estimation
    estimate = estimate_workflow_time(workflow)
    print(f"\n⏱️ Time Estimation:")
    print(f"   Estimated: {estimate['estimated_seconds']}s")
    print(f"   Parallel savings: {estimate['parallel_savings_seconds']}s")

    # Mermaid diagram
    print("\n📊 Mermaid Diagram (first 10 lines):")
    mermaid = workflow_to_mermaid(workflow)
    for line in mermaid.split('\n')[:10]:
        print(f"   {line}")


def demo_js_fallbacks():
    """Demonstrate JS Fallbacks (GAP 8)."""
    print_header("PHASE 3 - GAP 8: JS Fallbacks")

    # Available modules
    print("\n📦 Available JS Modules:")
    for module in get_all_module_names():
        code = get_js_module(module)
        size = len(code) if code else 0
        print(f"   - {module}: {size} bytes")

    # Detection
    sample_html = '''
    <div class="modal" data-modal-trigger="test">Open</div>
    <div class="tabs" role="tablist">
        <button role="tab">Tab 1</button>
    </div>
    <div class="accordion">Content</div>
    '''

    print("\n🔍 Auto-detection from HTML:")
    detected = detect_needed_modules(sample_html)
    print(f"   Detected modules: {detected}")

    # Injection
    print("\n💉 JS Injection:")
    injected = inject_js_fallbacks("<body><div>Test</div></body>", modules=["utils"])
    has_script = "<script>" in injected
    print(f"   Script injected: {has_script}")
    print(f"   Output size: {len(injected)} bytes")


def demo_telemetry():
    """Demonstrate Telemetry (GAP 12)."""
    print_header("PHASE 3 - GAP 12: Telemetry")

    # Track some operations
    print("\n📊 Tracking Operations:")

    with Telemetry.track("design_frontend") as ctx:
        ctx.set_component("button")
        ctx.set_theme("modern-minimal")
        # Simulate work
        import time
        time.sleep(0.1)
        ctx.set_tokens(input_tokens=500, output_tokens=1500)
    print("   ✓ Tracked: design_frontend")

    with Telemetry.track("design_section") as ctx:
        ctx.add_metadata("section", "hero")
        time.sleep(0.05)
        ctx.set_tokens(input_tokens=800, output_tokens=2000)
    print("   ✓ Tracked: design_section")

    # Get metrics
    metrics = Telemetry.get_metrics()
    print(f"\n📈 Metrics:")
    print(f"   Total operations: {metrics.get('total_operations', 0)}")
    print(f"   Success rate: {metrics.get('success_rate', 0):.1%}")

    # Summary
    print(f"\n📝 Summary:")
    summary = get_telemetry_summary()
    for line in summary.split('\n')[:8]:
        print(f"   {line}")


def demo_validators():
    """Demonstrate Validators (GAP 4, 5, 6)."""
    print_header("PHASE 2 - GAP 4, 5, 6: Validators")

    # Sample HTML with issues
    sample_html = '''
    <div class="p-4 md:p-6">
        <h1 class="text-2xl">Title</h1>
        <h3 class="text-lg">Skipped h2!</h3>
        <button class="bg-blue-500 text-white">No focus</button>
        <img src="hero.jpg">
        <a href="#">Click here</a>
    </div>
    '''

    # A11y Validation
    print("\n♿ Accessibility Validation:")
    validator = A11yValidator()
    a11y_report = validator.validate(sample_html)
    print(f"   Score: {a11y_report.score}/100")
    print(f"   Errors: {len(a11y_report.errors)}")
    print(f"   Warnings: {len(a11y_report.warnings)}")

    if a11y_report.issues:
        print("   Issues found:")
        for issue in a11y_report.issues[:3]:
            print(f"     - [{issue.rule}] {issue.message[:50]}...")

    # Responsive Validation
    print("\n📱 Responsive Validation:")
    resp_report = validate_responsive(sample_html, required_breakpoints=["sm", "md", "lg"])
    print(f"   Valid: {resp_report.is_valid}")
    print(f"   Missing breakpoints: {resp_report.missing_breakpoints}")

    # Auto-fix
    print("\n🔧 Auto-fix:")
    fixed, fixes = auto_fix_design(sample_html)
    print(f"   Fixes applied: {len(fixes)}")
    for fix in fixes[:3]:
        print(f"     - {fix}")

    # Combined validation
    print("\n📋 Combined Validation:")
    report = validate_design_output(sample_html)
    print(f"   Overall score: {report.overall_score}/100")
    print(f"   Tokens extracted: {report.tokens_extracted}")


def demo_prompt_builder():
    """Demonstrate Prompt Builder (GAP 7)."""
    print_header("PHASE 3 - GAP 7: Prompt Builder")

    # Build a prompt
    prompt = (
        PromptBuilder()
        .with_component("button")
        .with_theme("cyberpunk")
        .with_language("tr")
        .with_project_context("E-commerce checkout flow")
        .build_with_task("Create a primary action button")
    )

    print("\n📝 Generated Prompt (first 500 chars):")
    print(f"   {prompt[:500]}...")
    print(f"\n   Total length: {len(prompt)} chars")

    # Helper function
    print("\n🔧 Helper Function:")
    component_prompt = build_component_prompt(
        component_type="card",
        theme="glassmorphism",
        project_context="Product showcase"
    )
    print(f"   Component prompt length: {len(component_prompt)} chars")


def demo_cache():
    """Demonstrate Cache (GAP 9)."""
    print_header("PHASE 3 - GAP 9: Caching")

    cache = get_design_cache()
    cache.clear()  # Start fresh

    # Cache operations
    print("\n💾 Cache Operations:")

    # Set - uses kwargs for params
    cache.set({"html": "<button>Click</button>"}, component_type="button", theme="modern")
    cache.set({"html": "<div class='card'>Content</div>"}, component_type="card", theme="glass")
    print("   ✓ Set 2 items")

    # Get - uses same kwargs
    result = cache.get(component_type="button", theme="modern")
    hit = result is not None
    print(f"   Get button+modern: {'HIT' if hit else 'MISS'}")

    result = cache.get(component_type="nonexistent", theme="test")
    hit = result is not None
    print(f"   Get nonexistent: {'HIT' if hit else 'MISS'}")

    # Stats
    stats = cache.get_stats()
    print(f"\n📊 Cache Stats:")
    print(f"   Entries: {stats['entries']}")
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Hit rate: {stats['hit_rate']:.1%}")


async def demo_workflow_execution():
    """Demonstrate async workflow execution."""
    print_header("ASYNC WORKFLOW EXECUTION")

    execution_log = []

    async def mock_action_executor(action: str, params: dict):
        """Mock action executor for demo."""
        execution_log.append(action)
        await asyncio.sleep(0.1)  # Simulate API call
        return f"<section data-action='{action}'>{action} content</section>"

    async def mock_approval(step, output):
        """Auto-approve for demo."""
        print(f"   📋 Checkpoint: {step.name} - Auto-approved")
        return True

    async def mock_progress(workflow_id, step, progress):
        """Log progress."""
        print(f"   📈 Progress: {progress:.0%}")

    # Create simple workflow
    workflow = WorkflowDefinition(
        name="Demo Workflow",
        steps=[
            WorkflowStep(
                id="hero",
                name="Design Hero",
                action="design_hero",
                checkpoint=CheckpointType.REVIEW
            ),
            WorkflowStep(
                id="features",
                name="Design Features",
                action="design_features",
                depends_on=["hero"],
                parallel_group="content"
            ),
            WorkflowStep(
                id="pricing",
                name="Design Pricing",
                action="design_pricing",
                depends_on=["hero"],
                parallel_group="content"
            ),
            WorkflowStep(
                id="combine",
                name="Combine All",
                action="combine",
                depends_on=["hero", "features", "pricing"]
            ),
        ],
        parallel_groups=[
            ParallelGroup(id="content", step_ids=["features", "pricing"])
        ]
    )

    executor = WorkflowExecutor(
        action_executor=mock_action_executor,
        on_approval=mock_approval,
        on_progress=mock_progress
    )

    print("\n🚀 Executing workflow...")
    context = await executor.execute(workflow)

    print(f"\n✅ Workflow Status: {context.status.value}")
    print(f"   Outputs: {list(context.outputs.keys())}")
    print(f"   Execution order: {execution_log}")


def generate_sample_page():
    """Generate a sample HTML page using all features."""
    print_header("GENERATING SAMPLE PAGE")

    # Get design system values
    section_padding = get_component_size("section", "lg")
    heading_classes = get_type_classes("heading-xl")
    body_classes = get_type_classes("body-lg")
    button_classes = get_component_size("button", "lg")
    animation = animation_classes("normal")

    # Build HTML
    html = f'''<!DOCTYPE html>
<html lang="tr" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini MCP Demo - All Features</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100">

<!-- SECTION: hero -->
<section class="{section_padding} bg-gradient-to-br from-blue-600 to-indigo-700 text-white">
    <div class="max-w-6xl mx-auto text-center">
        <h1 class="{heading_classes} mb-6">
            Gemini MCP Design Tools
        </h1>
        <p class="{body_classes} text-blue-100 mb-8 max-w-2xl mx-auto">
            Phase 1-4 tamamlandı. 12 GAP, 155 test, 4 yeni modül.
        </p>
        <button class="{button_classes} bg-white text-blue-600 rounded-lg {animation} hover:bg-blue-50 focus-visible:ring-2 focus-visible:ring-white">
            Başla
        </button>
    </div>
</section>
<!-- /SECTION: hero -->

<!-- SECTION: features -->
<section class="{section_padding}">
    <div class="max-w-6xl mx-auto">
        <h2 class="{get_type_classes('heading-lg')} text-center mb-12">Özellikler</h2>
        <div class="grid md:grid-cols-3 gap-8">
            <div class="bg-white dark:bg-slate-800 {get_component_size('card', 'md')} rounded-xl shadow-sm">
                <h3 class="{get_type_classes('heading-sm')} mb-2">Design System</h3>
                <p class="{get_type_classes('body-sm')} text-slate-600 dark:text-slate-400">
                    Spacing, typography, component sizes standardizasyonu.
                </p>
            </div>
            <div class="bg-white dark:bg-slate-800 {get_component_size('card', 'md')} rounded-xl shadow-sm">
                <h3 class="{get_type_classes('heading-sm')} mb-2">Workflow</h3>
                <p class="{get_type_classes('body-sm')} text-slate-600 dark:text-slate-400">
                    Parallel execution, checkpoints, progress tracking.
                </p>
            </div>
            <div class="bg-white dark:bg-slate-800 {get_component_size('card', 'md')} rounded-xl shadow-sm">
                <h3 class="{get_type_classes('heading-sm')} mb-2">Validators</h3>
                <p class="{get_type_classes('body-sm')} text-slate-600 dark:text-slate-400">
                    A11y, responsive, token extraction validation.
                </p>
            </div>
        </div>
    </div>
</section>
<!-- /SECTION: features -->

<!-- SECTION: stats -->
<section class="{section_padding} bg-slate-100 dark:bg-slate-800">
    <div class="max-w-6xl mx-auto">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
                <div class="text-4xl font-bold text-blue-600">4</div>
                <div class="{get_type_classes('label')} text-slate-600">Phase</div>
            </div>
            <div>
                <div class="text-4xl font-bold text-blue-600">12</div>
                <div class="{get_type_classes('label')} text-slate-600">GAP</div>
            </div>
            <div>
                <div class="text-4xl font-bold text-blue-600">155</div>
                <div class="{get_type_classes('label')} text-slate-600">Test</div>
            </div>
            <div>
                <div class="text-4xl font-bold text-blue-600">4</div>
                <div class="{get_type_classes('label')} text-slate-600">Yeni Modül</div>
            </div>
        </div>
    </div>
</section>
<!-- /SECTION: stats -->

<!-- Interactive Demo with Tabs -->
<section class="{section_padding}">
    <div class="max-w-4xl mx-auto">
        <h2 class="{get_type_classes('heading-lg')} text-center mb-8">Interactive Demo</h2>

        <!-- Tabs -->
        <div class="tabs" role="tablist" aria-label="Demo tabs">
            <div class="flex border-b border-slate-200 dark:border-slate-700 mb-6">
                <button role="tab" aria-selected="true" aria-controls="panel-1"
                    class="px-4 py-2 font-medium text-blue-600 border-b-2 border-blue-600">
                    Design System
                </button>
                <button role="tab" aria-selected="false" aria-controls="panel-2"
                    class="px-4 py-2 font-medium text-slate-500 hover:text-slate-700">
                    Workflow
                </button>
                <button role="tab" aria-selected="false" aria-controls="panel-3"
                    class="px-4 py-2 font-medium text-slate-500 hover:text-slate-700">
                    Telemetry
                </button>
            </div>

            <div id="panel-1" role="tabpanel" class="bg-slate-100 dark:bg-slate-800 p-6 rounded-lg">
                <pre class="text-sm overflow-auto"><code>from gemini_mcp.design_system import DESIGN_SYSTEM

# Spacing
spacing_class("p", SpacingScale.BASE)  # "p-4"

# Typography
get_type_classes("heading-lg")  # "text-2xl md:text-3xl..."

# Component sizes
get_component_size("button", "lg")  # "px-6 py-3 text-base"</code></pre>
            </div>
        </div>
    </div>
</section>

<!-- Modal Demo -->
<div class="text-center py-8">
    <button data-modal-trigger="demo-modal"
        class="{button_classes} bg-blue-600 text-white rounded-lg {animation} hover:bg-blue-700 focus-visible:ring-2 focus-visible:ring-blue-500">
        Modal Aç
    </button>
</div>

<div id="demo-modal" class="modal hidden fixed inset-0 bg-black/50 flex items-center justify-center z-50" role="dialog" aria-modal="true">
    <div class="bg-white dark:bg-slate-800 rounded-xl p-8 max-w-md mx-4 shadow-2xl">
        <h3 class="{get_type_classes('heading-md')} mb-4">JS Fallback Demo</h3>
        <p class="{get_type_classes('body-base')} text-slate-600 dark:text-slate-400 mb-6">
            Bu modal vanilla JS ile çalışıyor. innerHTML kullanılmadı (XSS güvenliği).
        </p>
        <button data-modal-close class="{get_component_size('button', 'md')} bg-slate-200 dark:bg-slate-700 rounded-lg {animation} hover:bg-slate-300">
            Kapat
        </button>
    </div>
</div>

<!-- SECTION: footer -->
<footer class="py-12 px-8 bg-slate-900 text-slate-400 text-center">
    <p class="{get_type_classes('body-sm')}">
        Gemini MCP Design Tools © 2024 | Phase 1-4 Complete
    </p>
</footer>
<!-- /SECTION: footer -->

</body>
</html>'''

    # Inject JS fallbacks
    html = inject_js_fallbacks(html, modules=["utils", "modal", "tabs"])

    # Validate
    print("\n🔍 Validating generated page...")
    report = validate_design_output(html)
    print(f"   Overall score: {report.overall_score}/100")
    print(f"   Responsive valid: {report.responsive.is_valid}")
    print(f"   A11y errors: {len(report.accessibility.errors)}")

    # Save
    output_path = Path(__file__).parent / "demo_output.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"\n💾 Saved to: {output_path}")
    print(f"   Size: {len(html):,} bytes")

    return html


def main():
    """Run all demos."""
    print("\n" + "🚀" * 30)
    print("  GEMINI MCP - ALL FEATURES DEMO")
    print("  Phase 1-4 Implementation Test")
    print("🚀" * 30)

    # Phase 4 demos
    demo_design_system()
    demo_workflow()

    # Phase 3 demos
    demo_js_fallbacks()
    demo_telemetry()
    demo_prompt_builder()
    demo_cache()

    # Phase 2 demos
    demo_validators()

    # Async workflow demo
    asyncio.run(demo_workflow_execution())

    # Generate sample page
    generate_sample_page()

    print_header("DEMO COMPLETE")
    print("\n✅ All features demonstrated successfully!")
    print("📁 Check examples/demo_output.html for the generated page.\n")


if __name__ == "__main__":
    main()
