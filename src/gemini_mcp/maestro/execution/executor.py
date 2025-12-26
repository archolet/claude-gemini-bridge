"""
ToolExecutor - Executes design tools based on MaestroDecision.

This module bridges MAESTRO decisions to actual GeminiClient calls,
handling parameter transformation and result formatting.

Pattern: Handler dispatch similar to FlowController's lambda rules.

Phase 5 Additions:
- Trifecta pipeline integration via `use_trifecta` parameter
- Quality target configuration (draft, production, high, premium, enterprise)
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

from gemini_mcp.maestro.execution.adapters import (
    adapt_for_design_frontend,
    adapt_for_design_from_reference,
    adapt_for_design_page,
    adapt_for_design_section,
    adapt_for_refine_frontend,
    adapt_for_replace_section,
)
from gemini_mcp.maestro.models import ContextData, MaestroDecision
from gemini_mcp.orchestration import (
    AgentContext,
    PipelineType,
    get_orchestrator,
)

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient

logger = logging.getLogger(__name__)


# =============================================================================
# TRIFECTA PIPELINE CONFIGURATION
# =============================================================================

# Mode → PipelineType mapping
MODE_TO_PIPELINE: dict[str, PipelineType] = {
    "design_frontend": PipelineType.COMPONENT,
    "design_page": PipelineType.PAGE,
    "design_section": PipelineType.SECTION,
    "refine_frontend": PipelineType.REFINE,
    "replace_section_in_page": PipelineType.REPLACE,
    "design_from_reference": PipelineType.REFERENCE,
}

# Quality target configurations
# Each target defines threshold and max iterations for the refinement loop
QUALITY_CONFIGS: dict[str, dict[str, Any]] = {
    "draft": {
        "threshold": 6.0,
        "max_iterations": 1,
        "description": "Quick output with minimal refinement",
    },
    "production": {
        "threshold": 7.0,
        "max_iterations": 2,
        "description": "Standard quality for production use",
    },
    "standard": {  # Alias for production
        "threshold": 7.0,
        "max_iterations": 2,
        "description": "Same as production",
    },
    "high": {
        "threshold": 8.0,
        "max_iterations": 3,
        "description": "High quality with Critic refinement",
    },
    "premium": {
        "threshold": 8.5,
        "max_iterations": 4,
        "description": "Premium quality with extended refinement",
    },
    "enterprise": {
        "threshold": 9.0,
        "max_iterations": 5,
        "description": "Enterprise-grade with full validation",
    },
}


class ToolExecutor:
    """
    Executes design tools based on MaestroDecision.

    Uses GeminiClient methods directly (not MCP tool wrappers)
    to avoid circular imports and enable clean testing.

    Architecture:
        MaestroDecision → Adapter → GeminiClient method → Result

    Usage:
        executor = ToolExecutor(client)
        result = await executor.execute(decision, session_context)
    """

    # Mode → handler method name mapping
    MODE_HANDLERS: dict[str, str] = {
        "design_frontend": "_execute_design_frontend",
        "design_page": "_execute_design_page",
        "design_section": "_execute_design_section",
        "refine_frontend": "_execute_refine_frontend",
        "replace_section_in_page": "_execute_replace_section",
        "design_from_reference": "_execute_design_from_reference",
    }

    def __init__(self, client: "GeminiClient"):
        """
        Initialize ToolExecutor.

        Args:
            client: GeminiClient for API calls
        """
        self.client = client

    async def execute(
        self,
        decision: MaestroDecision,
        context: ContextData,
        use_trifecta: bool = False,
        quality_target: str = "production",
    ) -> dict[str, Any]:
        """
        Execute the design tool based on decision.mode.

        Args:
            decision: MaestroDecision with mode and parameters
            context: Session context with previous_html, project_context
            use_trifecta: Use multi-agent Trifecta pipeline for higher quality
            quality_target: Quality level (draft, production, high, premium, enterprise)

        Returns:
            Design tool result dict with 'html', 'mode', and other metadata

        Note:
            On error, returns {"error": str, "mode": str, "status": "failed"}
        """
        logger.info(
            f"[ToolExecutor] Executing mode: {decision.mode} "
            f"(trifecta={use_trifecta}, quality={quality_target})"
        )

        # Dispatch to appropriate execution path
        if use_trifecta:
            return await self._execute_with_pipeline(decision, context, quality_target)
        else:
            return await self._execute_direct(decision, context)

    async def _execute_direct(
        self,
        decision: MaestroDecision,
        context: ContextData,
    ) -> dict[str, Any]:
        """
        Execute using direct GeminiClient calls (original behavior).

        This is the fast path without multi-agent coordination.
        """
        handler_name = self.MODE_HANDLERS.get(decision.mode)
        if not handler_name:
            logger.error(f"[ToolExecutor] Unknown mode: {decision.mode}")
            return {
                "error": f"Unknown mode: {decision.mode}. Valid modes: {list(self.MODE_HANDLERS.keys())}",
                "mode": decision.mode,
                "status": "failed",
            }

        handler = getattr(self, handler_name)

        try:
            result = await handler(decision, context)
            logger.info(f"[ToolExecutor] Direct execution complete for: {decision.mode}")
            result["trifecta_enabled"] = False
            return result
        except ValueError as e:
            # Validation errors from adapters
            logger.error(f"[ToolExecutor] Validation error: {e}")
            return {
                "error": str(e),
                "mode": decision.mode,
                "status": "failed",
            }
        except Exception as e:
            # Unexpected errors
            logger.error(f"[ToolExecutor] Execution failed: {e}")
            return {
                "error": str(e),
                "mode": decision.mode,
                "status": "failed",
            }

    async def _execute_with_pipeline(
        self,
        decision: MaestroDecision,
        context: ContextData,
        quality_target: str,
    ) -> dict[str, Any]:
        """
        Execute using Trifecta multi-agent pipeline.

        This path coordinates Architect, Alchemist, Physicist, and QualityGuard
        agents for higher quality output with validation and refinement loops.
        """
        # Get pipeline type for this mode
        pipeline_type = MODE_TO_PIPELINE.get(decision.mode)
        if not pipeline_type:
            logger.warning(
                f"[ToolExecutor] No pipeline for mode: {decision.mode}, "
                f"falling back to direct execution"
            )
            result = await self._execute_direct(decision, context)
            result["fallback_reason"] = "no_pipeline_for_mode"
            return result

        # Get quality configuration
        quality_config = QUALITY_CONFIGS.get(
            quality_target,
            QUALITY_CONFIGS["production"],
        )

        # Build AgentContext from MAESTRO context
        agent_context = self._build_agent_context(decision, context, quality_config)

        try:
            # Get or create orchestrator
            orchestrator = get_orchestrator(self.client)

            # Run the pipeline
            logger.info(
                f"[ToolExecutor] Running {pipeline_type.value} pipeline "
                f"with {quality_target} quality target"
            )
            pipeline_result = await orchestrator.run_pipeline(
                pipeline_type=pipeline_type,
                context=agent_context,
            )

            # Convert to MCP response format
            result = pipeline_result.to_mcp_response()

            # Add MAESTRO-specific metadata
            result["mode"] = decision.mode
            result["trifecta_enabled"] = True
            result["quality_target"] = quality_target
            result["quality_threshold"] = quality_config["threshold"]
            result["agents_executed"] = [
                step.agent_name for step in pipeline_result.step_results
                if hasattr(step, "agent_name")
            ]

            logger.info(
                f"[ToolExecutor] Pipeline execution complete: "
                f"success={pipeline_result.success}, "
                f"steps={pipeline_result.completed_steps}/{pipeline_result.total_steps}"
            )

            return result

        except Exception as e:
            logger.error(f"[ToolExecutor] Pipeline execution failed: {e}")
            return {
                "error": str(e),
                "mode": decision.mode,
                "status": "failed",
                "trifecta_enabled": True,
                "quality_target": quality_target,
            }

    def _build_agent_context(
        self,
        decision: MaestroDecision,
        context: ContextData,
        quality_config: dict[str, Any],
    ) -> AgentContext:
        """
        Build AgentContext from MAESTRO decision and session context.

        AgentContext is the shared state passed between Trifecta agents.
        """
        params = decision.parameters

        # Extract component type based on mode
        component_type = ""
        if decision.mode == "design_frontend":
            component_type = params.get("component_type", "card")
        elif decision.mode == "design_page":
            component_type = f"page:{params.get('template_type', 'landing_page')}"
        elif decision.mode == "design_section":
            component_type = f"section:{params.get('section_type', 'hero')}"
        elif decision.mode == "refine_frontend":
            component_type = "refine"
        elif decision.mode == "replace_section_in_page":
            component_type = f"replace:{params.get('section_type', 'hero')}"
        elif decision.mode == "design_from_reference":
            component_type = params.get("component_type", "reference")

        # Build design spec
        design_spec = {
            "context": params.get("context", ""),
            "content_structure": params.get("content_structure", {}),
            "theme": params.get("theme", "modern-minimal"),
            "dark_mode": params.get("dark_mode", True),
        }

        return AgentContext(
            component_type=component_type,
            design_spec=design_spec,
            project_context=params.get("project_context", context.project_context or ""),
            content_language=params.get("content_language", "tr"),
            # Previous HTML for refinement/matching
            previous_html=context.previous_html or params.get("previous_html", ""),
            # Quality settings
            quality_threshold=quality_config["threshold"],
            max_iterations=quality_config["max_iterations"],
            # Reference image for design_from_reference
            reference_image_path=params.get("image_path", ""),
            instructions=params.get("instructions", ""),
            modifications=params.get("modifications", ""),
        )

    # =========================================================================
    # MODE HANDLERS
    # =========================================================================

    async def _execute_design_frontend(
        self,
        decision: MaestroDecision,
        context: ContextData,
    ) -> dict[str, Any]:
        """Execute design_frontend mode."""
        params = adapt_for_design_frontend(decision.parameters, context)

        # Build style guide from theme
        theme = decision.parameters.get("theme", "modern-minimal")
        style_guide = self._build_style_guide(theme)

        result = await self.client.design_component(
            component_type=params["component_type"],
            design_spec=params["design_spec"],
            style_guide=style_guide,
            project_context=params["project_context"],
            content_language=params["content_language"],
        )

        result["mode"] = "design_frontend"
        result["theme_used"] = theme
        return result

    async def _execute_design_page(
        self,
        decision: MaestroDecision,
        context: ContextData,
    ) -> dict[str, Any]:
        """Execute design_page mode."""
        params = adapt_for_design_page(decision.parameters, context)

        theme = decision.parameters.get("theme", "modern-minimal")
        style_guide = self._build_style_guide(theme)

        result = await self.client.design_component(
            component_type=params["component_type"],
            design_spec=params["design_spec"],
            style_guide=style_guide,
            project_context=params["project_context"],
            content_language=params["content_language"],
        )

        result["mode"] = "design_page"
        result["template_type"] = decision.parameters.get("template_type", "landing_page")
        result["theme_used"] = theme
        return result

    async def _execute_design_section(
        self,
        decision: MaestroDecision,
        context: ContextData,
    ) -> dict[str, Any]:
        """Execute design_section mode."""
        params = adapt_for_design_section(decision.parameters, context)

        result = await self.client.design_section(
            section_type=params["section_type"],
            context=params["context"],
            previous_html=params["previous_html"],
            design_tokens=params["design_tokens"],
            content_structure=params["content_structure"],
            theme=params["theme"],
            project_context=params["project_context"],
            content_language=params["content_language"],
        )

        result["mode"] = "design_section"
        return result

    async def _execute_refine_frontend(
        self,
        decision: MaestroDecision,
        context: ContextData,
    ) -> dict[str, Any]:
        """Execute refine_frontend mode."""
        params = adapt_for_refine_frontend(decision.parameters, context)

        result = await self.client.refine_component(
            previous_html=params["previous_html"],
            modifications=params["modifications"],
            project_context=params["project_context"],
        )

        result["mode"] = "refine_frontend"
        return result

    async def _execute_replace_section(
        self,
        decision: MaestroDecision,
        context: ContextData,
    ) -> dict[str, Any]:
        """
        Execute replace_section_in_page mode.

        This is a compound operation:
        1. Extract existing section from page HTML
        2. Design new section matching page style
        3. Replace old section with new one
        """
        params = adapt_for_replace_section(decision.parameters, context)

        # Extract existing section content for context
        existing_section = self._extract_section(
            params["page_html"],
            params["section_type"],
        )

        # Design new section
        new_section = await self.client.design_section(
            section_type=params["section_type"],
            context=params["modifications"],
            previous_html=existing_section,
            design_tokens={},  # Will extract from existing section
            content_structure={},
            theme=params["theme"],
            project_context="",
            content_language=params["content_language"],
        )

        # Replace section in page HTML
        new_section_html = new_section.get("html", "")
        updated_html = self._replace_section_html(
            params["page_html"],
            params["section_type"],
            new_section_html,
        )

        return {
            "html": updated_html,
            "mode": "replace_section_in_page",
            "modified_section": params["section_type"],
            "new_section_html": new_section_html,
            "design_notes": new_section.get("design_notes", ""),
            "preserved_sections": self._list_sections(params["page_html"]),
        }

    async def _execute_design_from_reference(
        self,
        decision: MaestroDecision,
        context: ContextData,
    ) -> dict[str, Any]:
        """Execute design_from_reference mode."""
        params = adapt_for_design_from_reference(decision.parameters, context)

        result = await self.client.design_from_reference(
            image_path=params["image_path"],
            component_type=params["component_type"],
            instructions=params["instructions"],
            context=params["context"],
            project_context=params["project_context"],
            content_language=params["content_language"],
        )

        result["mode"] = "design_from_reference"
        return result

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _build_style_guide(self, theme: str) -> dict[str, Any]:
        """
        Build style guide from theme name.

        Import is done here to avoid circular dependency.
        """
        try:
            from gemini_mcp.frontend_presets import build_style_guide
            return build_style_guide(theme)
        except ImportError:
            logger.warning(f"Could not import build_style_guide, using empty guide")
            return {}

    def _extract_section(self, html: str, section_type: str) -> str:
        """
        Extract a section from page HTML using section markers.

        Expected format:
            <!-- SECTION: {type} --> ... content ... <!-- /SECTION: {type} -->

        Args:
            html: Full page HTML
            section_type: Type of section to extract

        Returns:
            Section content (without markers), or empty string if not found
        """
        pattern = rf'<!-- SECTION: {section_type} -->(.*?)<!-- /SECTION: {section_type} -->'
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _replace_section_html(
        self,
        page_html: str,
        section_type: str,
        new_section_html: str,
    ) -> str:
        """
        Replace a section in page HTML with new content.

        Preserves section markers.

        Args:
            page_html: Full page HTML with section markers
            section_type: Type of section to replace
            new_section_html: New section content

        Returns:
            Updated page HTML with replaced section
        """
        pattern = rf'(<!-- SECTION: {section_type} -->).*?(<!-- /SECTION: {section_type} -->)'
        replacement = rf'\1\n{new_section_html}\n\2'
        return re.sub(pattern, replacement, page_html, flags=re.DOTALL | re.IGNORECASE)

    def _list_sections(self, html: str) -> list[str]:
        """
        List all section types found in page HTML.

        Args:
            html: Page HTML with section markers

        Returns:
            List of section type names
        """
        pattern = r'<!-- SECTION: (\w+) -->'
        matches = re.findall(pattern, html, re.IGNORECASE)
        return list(set(matches))
