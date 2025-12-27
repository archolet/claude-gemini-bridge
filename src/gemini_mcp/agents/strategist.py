"""
The Strategist - Planning & DNA Extraction Specialist

The Strategist is responsible for:
1. Extracting Design DNA from existing HTML (for chain consistency)
2. Planning section layouts for full pages
3. Providing style tokens to downstream agents

The Strategist NEVER generates HTML/CSS/JS - only analysis and planning data.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from gemini_mcp.agents.base import AgentConfig, AgentResult, AgentRole, BaseAgent
from gemini_mcp.orchestration.context import DesignDNA
from gemini_mcp.prompts.prompt_loader import get_prompt

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient
    from gemini_mcp.orchestration.context import AgentContext

# Import DNAStore lazily to avoid circular imports
def _get_dna_store():
    """Lazy import of DNAStore to avoid circular imports."""
    from gemini_mcp.orchestration.dna_store import get_dna_store
    return get_dna_store()

logger = logging.getLogger(__name__)


@dataclass
class SectionPlan:
    """Plan for a single section."""

    section_type: str
    key_elements: list[str] = field(default_factory=list)
    priority: int = 1
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "type": self.section_type,
            "key_elements": self.key_elements,
            "priority": self.priority,
            "notes": self.notes,
        }


class StrategistAgent(BaseAgent):
    """
    The Strategist - Planning & DNA Extraction Specialist.

    Extracts design tokens from existing HTML and plans section layouts.
    Never generates code - only analysis and planning data.
    """

    role = AgentRole.STRATEGIST

    def __init__(
        self,
        client: "GeminiClient",
        config: Optional[AgentConfig] = None,
    ):
        """
        Initialize The Strategist.

        Args:
            client: GeminiClient for API calls
            config: Optional custom configuration
        """
        super().__init__(config)
        self.client = client

    @classmethod
    def _default_config(cls) -> AgentConfig:
        """Strategist-specific default configuration."""
        return AgentConfig(
            model="gemini-3-pro-preview",
            thinking_level="high",  # Planning requires deep thinking
            temperature=1.0,  # Gemini 3 optimized
            max_output_tokens=4096,
            strict_mode=False,  # Strategist output is advisory
            auto_fix=False,
        )

    def get_system_prompt(self, variables: dict[str, Any] | None = None) -> str:
        """Return The Strategist's system prompt from YAML template."""
        return get_prompt(
            agent_name="strategist",
            variables=variables or {},
        )

    async def execute(self, context: "AgentContext") -> AgentResult:
        """
        Extract design DNA or plan sections based on context.

        Args:
            context: Pipeline context

        Returns:
            AgentResult with DNA/planning data
        """
        import time

        start_time = time.time()

        try:
            # Build the prompt
            prompt = self._build_strategist_prompt(context)

            # Call Gemini API with Gemini 3 optimizations
            response = await self.client.generate_text(
                prompt=prompt,
                system_instruction=self.get_system_prompt(),
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
                thinking_level=self.config.thinking_level,
            )

            # Extract text and thought signature from response
            response_text = response.get("text", "")

            # === GEMINI 3: Add thought signature to context ===
            if response.get("thought_signature"):
                context.add_thought_signature(response["thought_signature"])

            # Parse JSON response
            parsed_data = self._parse_response(response_text)

            # Extract DNA if present
            design_dna = None
            if "design_dna" in parsed_data:
                design_dna = DesignDNA.from_dict(parsed_data["design_dna"])

            # Extract section plans if present
            section_plans = []
            if "sections" in parsed_data:
                for section_data in parsed_data["sections"]:
                    section_plans.append(SectionPlan(
                        section_type=section_data.get("type", ""),
                        key_elements=section_data.get("key_elements", []),
                        priority=section_data.get("priority", 1),
                        notes=section_data.get("notes", ""),
                    ))

            # Create result
            result = AgentResult(
                success=True,
                output=json.dumps(parsed_data, indent=2, ensure_ascii=False),
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
            )

            # Attach extracted data
            result.metadata = {
                "design_dna": design_dna.to_dict() if design_dna else None,
                "section_plans": [s.to_dict() for s in section_plans],
            }

            # === PHASE 7: DNA Persistence ===
            # Save DNA to store for cross-session retrieval
            if design_dna:
                try:
                    dna_store = _get_dna_store()
                    project_id = self._extract_project_id(context)
                    component_type = context.component_type or "page"
                    theme = context.theme or "unknown"

                    dna_id = dna_store.save(
                        component_type=component_type,
                        theme=theme,
                        dna=design_dna,
                        project_id=project_id,
                    )
                    result.metadata["dna_id"] = dna_id
                    logger.info(f"[Strategist] Saved DNA to store: {dna_id}")
                except Exception as e:
                    logger.warning(f"[Strategist] Failed to save DNA: {e}")

            logger.info(
                f"[Strategist] Extracted DNA: {design_dna.mood if design_dna else 'None'}, "
                f"Sections: {len(section_plans)}"
            )

            return result

        except Exception as e:
            logger.error(f"[Strategist] Execution failed: {e}")
            return AgentResult(
                success=False,
                output="",
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                errors=[str(e)],
            )

    def _build_strategist_prompt(self, context: "AgentContext") -> str:
        """Build the prompt for DNA extraction or planning."""
        parts = []

        # Determine mode
        if context.previous_output or context.html_output:
            parts.append("## MODE: DNA Extraction")
            html_content = context.previous_output or context.html_output
            parts.append(f"### Existing HTML\n```html\n{html_content[:3000]}\n```")
            parts.append("Extract the design DNA from this HTML.")
        else:
            parts.append("## MODE: Section Planning")
            if context.theme:
                parts.append(f"### Theme\n{context.theme}")
            if context.component_type:
                parts.append(f"### Target Component\n{context.component_type}")
            parts.append("Plan the sections and define design DNA for this page.")

        # Add any existing DNA to build upon
        if context.design_dna:
            dna_json = json.dumps(context.design_dna.to_dict(), indent=2, ensure_ascii=False)
            parts.append(f"### Existing DNA (Extend This)\n```json\n{dna_json}\n```")

        # Content language hint
        if context.content_language:
            parts.append(f"### Content Language\n{context.content_language}")

        # User requirements
        if context.user_requirements:
            parts.append(f"### User Requirements\n{context.user_requirements}")

        return "\n\n".join(parts)

    def _parse_response(self, response: str) -> dict:
        """
        Parse JSON response from the Strategist.

        Handles various response formats including markdown code blocks.
        """
        # Try to extract JSON from code blocks
        json_pattern = r"```(?:json)?\s*(\{[\s\S]*?\})\s*```"
        matches = re.findall(json_pattern, response)
        if matches:
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        # Try raw JSON
        try:
            # Find first { and last }
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

        # Fallback: return empty structure
        logger.warning("[Strategist] Could not parse JSON response")
        return {"design_dna": {}, "sections": []}

    def validate_output(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate Strategist output.

        The Strategist outputs JSON, so we validate structure.
        """
        issues = []

        if not output or not output.strip():
            return True, []  # Empty is okay for Strategist

        try:
            data = json.loads(output)

            # Check for required fields
            if "design_dna" not in data and "sections" not in data:
                issues.append("Output should contain 'design_dna' or 'sections'")

            # Validate DNA structure if present
            if "design_dna" in data:
                dna = data["design_dna"]
                if not isinstance(dna, dict):
                    issues.append("'design_dna' should be an object")

        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON: {e}")

        return len(issues) == 0, issues

    def auto_fix_output(self, output: str) -> str:
        """
        Attempt to auto-fix common issues in Strategist output.
        """
        # For Strategist, we try to extract valid JSON
        try:
            parsed = self._parse_response(output)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except Exception:
            return output

    def extract_dna_from_html(self, html: str) -> DesignDNA:
        """
        Quick DNA extraction from HTML without API call.

        This is a fallback for when we need DNA but can't call the API.
        """
        dna = DesignDNA()

        # Extract colors from Tailwind classes
        color_pattern = r"(?:bg|text|border)-(\w+)-(\d+)"
        color_matches = re.findall(color_pattern, html)
        color_usage = {}
        for color, shade in color_matches:
            key = f"{color}-{shade}"
            color_usage[key] = color_usage.get(key, 0) + 1

        # Find most used colors
        sorted_colors = sorted(color_usage.items(), key=lambda x: -x[1])
        if len(sorted_colors) > 0:
            dna.colors["primary"] = sorted_colors[0][0]
        if len(sorted_colors) > 1:
            dna.colors["secondary"] = sorted_colors[1][0]

        # Extract spacing patterns
        spacing_pattern = r"(?:p|m|gap)-(\d+)"
        spacing_matches = re.findall(spacing_pattern, html)
        if spacing_matches:
            avg_spacing = sum(int(s) for s in spacing_matches) / len(spacing_matches)
            if avg_spacing < 4:
                dna.spacing["density"] = "compact"
            elif avg_spacing < 8:
                dna.spacing["density"] = "comfortable"
            else:
                dna.spacing["density"] = "spacious"

        # Extract border radius
        radius_pattern = r"rounded-(\w+)"
        radius_matches = re.findall(radius_pattern, html)
        if radius_matches:
            # Most common radius
            radius_usage = {}
            for r in radius_matches:
                radius_usage[r] = radius_usage.get(r, 0) + 1
            most_common = max(radius_usage.items(), key=lambda x: x[1])
            dna.borders["radius"] = f"rounded-{most_common[0]}"

        # Detect mood from class patterns
        if "neon" in html.lower() or "glow" in html.lower():
            dna.mood = "cyberpunk"
        elif "glass" in html.lower() or "backdrop-blur" in html:
            dna.mood = "glassmorphism"
        elif "shadow-brutal" in html or "border-4" in html:
            dna.mood = "neo-brutalism"
        else:
            dna.mood = "modern-minimal"

        return dna

    # === PHASE 7: DNA Persistence Helper Methods ===

    def _extract_project_id(self, context: "AgentContext") -> str:
        """
        Extract project ID from context.

        Uses project_context if available, otherwise generates from cwd or defaults.
        """
        if context.project_context:
            # Try to extract project name from context
            import re
            match = re.search(r"[Pp]roject:\s*([^\n,]+)", context.project_context)
            if match:
                return match.group(1).strip().lower().replace(" ", "-")

        # Default project
        return "default"

    def try_load_previous_dna(
        self,
        component_type: str,
        theme: Optional[str] = None,
        project_id: str = "default",
    ) -> Optional["DesignDNA"]:
        """
        Try to load previous DNA from store for a component type.

        Args:
            component_type: Component type to search for
            theme: Optional theme filter
            project_id: Project to search in

        Returns:
            DesignDNA if found, None otherwise
        """
        try:
            dna_store = _get_dna_store()
            context_dna = dna_store.get_latest(
                component_type=component_type,
                project_id=project_id,
                theme=theme,
            )

            if context_dna:
                # Convert context DNA to local DNA
                return DesignDNA(
                    colors=context_dna.colors,
                    typography=context_dna.typography,
                    spacing=context_dna.spacing,
                    borders=context_dna.borders,
                    animation=context_dna.animation,
                    mood=context_dna.mood,
                )
        except Exception as e:
            logger.warning(f"[Strategist] Failed to load DNA from store: {e}")

        return None

    def get_related_dna(
        self,
        component_type: str,
        project_id: str = "default",
        limit: int = 3,
    ) -> list[DesignDNA]:
        """
        Get related DNA entries for consistency reference.

        Useful when building a new component that should match existing ones.

        Args:
            component_type: Component type to search similar to
            project_id: Project to search in
            limit: Max entries to return

        Returns:
            List of related DesignDNA objects
        """
        try:
            dna_store = _get_dna_store()
            entries = dna_store.search(
                project_id=project_id,
                limit=limit,
            )

            dnas = []
            for entry in entries:
                dnas.append(DesignDNA(
                    colors=entry.dna.colors,
                    typography=entry.dna.typography,
                    spacing=entry.dna.spacing,
                    borders=entry.dna.borders,
                    animation=entry.dna.animation,
                    mood=entry.dna.mood,
                ))

            return dnas
        except Exception as e:
            logger.warning(f"[Strategist] Failed to get related DNA: {e}")
            return []
