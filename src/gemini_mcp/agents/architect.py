"""
The Architect - HTML Structure Specialist

The Architect is responsible for generating semantic, accessible HTML structure
using Tailwind CSS classes. It NEVER writes CSS or JavaScript.

Responsibilities:
- Semantic HTML5 structure (nav, main, section, article, aside)
- Tailwind CSS class application
- Unique ID generation for interactive elements
- ARIA attributes for accessibility
- Responsive class application
- Dark mode class support

Boundaries:
- NO <style> tags
- NO <script> tags
- NO inline styles
- NO event handler attributes
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Optional

from gemini_mcp.agents.base import AgentConfig, AgentResult, AgentRole, BaseAgent
from gemini_mcp.prompts import ARCHITECT_SYSTEM_PROMPT

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient
    from gemini_mcp.orchestration.context import AgentContext

logger = logging.getLogger(__name__)


class ArchitectAgent(BaseAgent):
    """
    The Architect - HTML Structure Specialist.

    Generates semantic HTML with Tailwind classes, unique IDs for interactivity,
    and accessibility attributes. Never outputs CSS or JavaScript.
    """

    role = AgentRole.ARCHITECT

    def __init__(
        self,
        client: "GeminiClient",
        config: Optional[AgentConfig] = None,
    ):
        """
        Initialize The Architect.

        Args:
            client: GeminiClient for API calls
            config: Optional custom configuration
        """
        super().__init__(config)
        self.client = client

    @classmethod
    def _default_config(cls) -> AgentConfig:
        """Architect-specific default configuration."""
        return AgentConfig(
            model="gemini-3-pro-preview",
            thinking_budget=8192,
            temperature=0.7,
            max_output_tokens=16384,
            strict_mode=True,
            auto_fix=True,
        )

    def get_system_prompt(self) -> str:
        """Return The Architect's system prompt."""
        return ARCHITECT_SYSTEM_PROMPT

    async def execute(self, context: "AgentContext") -> AgentResult:
        """
        Generate HTML structure based on context.

        Args:
            context: Pipeline context with design requirements

        Returns:
            AgentResult containing the generated HTML
        """
        import time

        start_time = time.time()

        try:
            # Build the prompt
            prompt = self._build_architect_prompt(context)

            # Call Gemini API
            response = await self.client.generate_text(
                prompt=prompt,
                system_instruction=self.get_system_prompt(),
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
            )

            # Extract HTML from response
            html_output = self._extract_html(response)

            # Validate output
            is_valid, issues = self.validate_output(html_output)

            # Create result
            result = AgentResult(
                success=True,
                output=html_output,
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                warnings=issues if not is_valid else [],
            )

            # Post-process to extract metadata
            result = self.post_process(result, html_output)

            if not is_valid and self.config.strict_mode:
                result.success = False
                result.errors = issues

            logger.info(
                f"[Architect] Generated HTML with {len(result.extracted_ids)} IDs, "
                f"{len(result.extracted_classes)} unique classes"
            )

            return result

        except Exception as e:
            logger.error(f"[Architect] Execution failed: {e}")
            return AgentResult(
                success=False,
                output="",
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                errors=[str(e)],
            )

    def _build_architect_prompt(self, context: "AgentContext") -> str:
        """Build the prompt for HTML generation."""
        parts = []

        # Component type
        if context.component_type:
            parts.append(f"## Component Type\n{context.component_type}")

        # Theme
        if context.theme:
            parts.append(f"## Theme\n{context.theme}")

        # Content language
        if context.content_language:
            parts.append(f"## Content Language\n{context.content_language}")

        # User content structure
        if context.content_structure:
            parts.append(f"## User Content\n{context.content_structure}")

        # Design DNA
        if context.design_dna:
            import json

            dna_json = json.dumps(
                context.design_dna.to_dict(), indent=2, ensure_ascii=False
            )
            parts.append(f"## Design DNA (Follow These Tokens)\n{dna_json}")

        # Section-specific (for design_page)
        if context.sections:
            import json

            sections_json = json.dumps(context.sections, indent=2, ensure_ascii=False)
            parts.append(f"## Sections to Generate\n{sections_json}")

        # Target section (for replace_section_in_page)
        if context.target_section:
            parts.append(
                f"## Target Section\nReplace ONLY the {context.target_section} section"
            )

        # Previous HTML context (for refinement)
        if context.previous_html:
            # Compress to reduce tokens
            compressed = self._compress_html_context(context.previous_html)
            parts.append(f"## Previous HTML (Reference)\n{compressed}")

        # === PHASE 7: Interaction Hints ===
        # Suggest data-* attributes based on component type
        interaction_suggestions = self._get_interaction_suggestions(context.component_type)
        if interaction_suggestions:
            parts.append(
                f"## Suggested Interactions (Add data-* Attributes)\n"
                f"{interaction_suggestions}"
            )

        # Correction feedback (for retry)
        if context.correction_feedback:
            parts.append(
                f"## CORRECTION REQUIRED\n"
                f"Previous output had issues:\n{context.correction_feedback}\n"
                f"Fix these issues in this attempt."
            )

        return "\n\n".join(parts)

    def _get_interaction_suggestions(self, component_type: str | None) -> str:
        """
        Get suggested data-* attributes based on component type.

        Returns formatted suggestions for the Architect prompt.
        """
        if not component_type:
            return ""

        # Component-specific interaction suggestions
        suggestions_map = {
            # Organisms
            "hero": [
                ('section', 'parallax', 'scroll', '0.3', 'Hero background parallax'),
                ('h1', 'reveal', 'intersect', '1.0', 'Title reveal on scroll'),
                ('button', 'magnetic', 'hover', '0.8', 'CTA magnetic effect'),
            ],
            "navbar": [
                ('nav', 'reveal', 'load', '1.0', 'Navbar fade-in on load'),
                ('a', 'glow', 'hover', '0.5', 'Link glow on hover'),
            ],
            "footer": [
                ('footer', 'reveal', 'intersect', '0.8', 'Footer reveal'),
            ],
            # Molecules
            "card": [
                ('div', 'tilt', 'hover', '0.6', '3D tilt on hover'),
                ('div', 'glow', 'hover', '0.4', 'Glow effect'),
            ],
            "pricing_card": [
                ('div', 'tilt', 'hover', '0.5', 'Subtle 3D tilt'),
                ('button', 'magnetic', 'hover', '0.7', 'Magnetic CTA'),
                ('span', 'morph', 'hover', '0.8', 'Price morph effect'),
            ],
            "testimonial": [
                ('blockquote', 'reveal', 'intersect', '0.9', 'Quote reveal'),
                ('div', 'float', 'load', '0.3', 'Avatar float'),
            ],
            # Atoms
            "button": [
                ('button', 'magnetic', 'hover', '0.8', 'Magnetic effect'),
                ('button', 'ripple', 'click', '1.0', 'Click ripple'),
            ],
            "input": [
                ('input', 'glow', 'focus', '0.5', 'Focus glow'),
            ],
        }

        suggestions = suggestions_map.get(component_type.lower(), [])
        if not suggestions:
            return ""

        lines = [
            "Add these data-* attributes to appropriate elements:",
            "",
        ]
        for element, interaction, trigger, intensity, desc in suggestions:
            lines.append(
                f"- `<{element} data-interaction=\"{interaction}\" "
                f"data-trigger=\"{trigger}\" data-intensity=\"{intensity}\">` → {desc}"
            )

        return "\n".join(lines)

    def _extract_html(self, response: str) -> str:
        """
        Extract HTML from the response.

        The response might contain markdown code blocks or raw HTML.
        """
        # Try to extract from code blocks
        html_pattern = r"```html?\s*([\s\S]*?)```"
        matches = re.findall(html_pattern, response, re.IGNORECASE)
        if matches:
            return matches[0].strip()

        # If no code blocks, assume raw HTML
        # Remove any markdown artifacts
        cleaned = response.strip()
        cleaned = re.sub(r"^#+\s*.*$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        return cleaned

    def _compress_html_context(self, html: str, max_chars: int = 2000) -> str:
        """
        Compress HTML for context passing to reduce tokens.

        Extracts structure and key classes without full content.
        """
        if len(html) <= max_chars:
            return html

        # Extract structure summary
        structure_parts = []

        # Extract section markers
        section_pattern = r"<!-- SECTION: (\w+) -->"
        sections = re.findall(section_pattern, html)
        if sections:
            structure_parts.append(f"Sections: {', '.join(sections)}")

        # Extract IDs
        ids = self.extract_ids(html)
        if ids:
            structure_parts.append(f"IDs: {', '.join(ids[:20])}")

        # Extract key Tailwind patterns
        classes = self.extract_tailwind_classes(html)
        key_patterns = [c for c in classes if any(p in c for p in ["bg-", "text-", "font-", "rounded-"])]
        if key_patterns:
            structure_parts.append(f"Key classes: {', '.join(key_patterns[:30])}")

        return "\n".join(structure_parts) if structure_parts else html[:max_chars]

    def validate_output(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate HTML output against Architect constraints.

        Checks:
        1. No <style> tags
        2. No <script> tags
        3. No inline styles
        4. No event handler attributes
        5. Has proper HTML structure
        """
        issues: list[str] = []

        if not output or not output.strip():
            return False, ["Output is empty"]

        # Check for forbidden elements
        if "<style" in output.lower():
            issues.append("Contains <style> tag - Architect cannot write CSS")

        if "<script" in output.lower():
            issues.append("Contains <script> tag - Architect cannot write JS")

        # Check for inline styles
        inline_style_pattern = r'style\s*=\s*["\'][^"\']+["\']'
        if re.search(inline_style_pattern, output, re.IGNORECASE):
            issues.append("Contains inline style attribute")

        # Check for event handlers
        event_handlers = [
            "onclick", "onmouseover", "onmouseout", "onmouseenter",
            "onmouseleave", "onkeydown", "onkeyup", "onkeypress",
            "onchange", "onsubmit", "onfocus", "onblur", "onload",
        ]
        for handler in event_handlers:
            if re.search(rf'{handler}\s*=', output, re.IGNORECASE):
                issues.append(f"Contains {handler} event handler")
                break  # Only report first one

        # Check for basic HTML structure
        if not re.search(r"<[a-z]", output, re.IGNORECASE):
            issues.append("Does not appear to contain HTML elements")

        # Check for ID uniqueness
        ids = self.extract_ids(output)
        unique_ids = set(ids)
        if len(ids) != len(unique_ids):
            duplicates = [id for id in ids if ids.count(id) > 1]
            issues.append(f"Duplicate IDs found: {', '.join(set(duplicates))}")

        return len(issues) == 0, issues

    def auto_fix_output(self, output: str) -> str:
        """
        Attempt to auto-fix common issues in output.

        Returns the fixed output.
        """
        fixed = output

        # Remove style tags
        fixed = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", fixed, flags=re.IGNORECASE)

        # Remove script tags
        fixed = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", fixed, flags=re.IGNORECASE)

        # Remove inline styles
        fixed = re.sub(r'\s*style\s*=\s*["\'][^"\']*["\']', "", fixed, flags=re.IGNORECASE)

        # Remove event handlers
        event_pattern = r'\s*on\w+\s*=\s*["\'][^"\']*["\']'
        fixed = re.sub(event_pattern, "", fixed, flags=re.IGNORECASE)

        return fixed.strip()
