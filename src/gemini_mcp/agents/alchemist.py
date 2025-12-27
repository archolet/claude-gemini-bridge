"""
The Alchemist - CSS Effects Specialist

The Alchemist is responsible for generating premium CSS effects that go beyond
what Tailwind provides out of the box. It NEVER modifies HTML or writes JavaScript.

Responsibilities:
- Custom @keyframes animations
- Glassmorphism effects (backdrop-filter)
- Neon glow effects (text-shadow, box-shadow)
- Gradient animations
- CSS variables for theming
- Vendor prefixes for compatibility
- Performance optimizations (will-change)

Boundaries:
- NO HTML output
- NO JavaScript output
- NO !important (unless absolutely necessary)
- Uses only class/ID selectors (no element selectors)
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, Optional

from gemini_mcp.agents.base import AgentConfig, AgentResult, AgentRole, BaseAgent
from gemini_mcp.prompts.prompt_loader import get_prompt
from gemini_mcp.validation import CSSValidator

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient
    from gemini_mcp.orchestration.context import AgentContext

logger = logging.getLogger(__name__)


class AlchemistAgent(BaseAgent):
    """
    The Alchemist - CSS Effects Specialist.

    Generates premium CSS effects: glassmorphism, neon glows, custom animations,
    and gradient effects. Never outputs HTML or JavaScript.
    """

    role = AgentRole.ALCHEMIST

    def __init__(
        self,
        client: "GeminiClient",
        config: Optional[AgentConfig] = None,
    ):
        """
        Initialize The Alchemist.

        Args:
            client: GeminiClient for API calls
            config: Optional custom configuration
        """
        super().__init__(config)
        self.client = client
        # Phase 3: Centralized Validator Integration
        self._css_validator = CSSValidator(strict_mode=False)

    @classmethod
    def _default_config(cls) -> AgentConfig:
        """Alchemist-specific default configuration."""
        return AgentConfig(
            model="gemini-3-pro-preview",
            thinking_level="high",  # Maximum reasoning for premium CSS effects
            temperature=1.0,  # Gemini 3 optimized
            max_output_tokens=8192,
            strict_mode=True,
            auto_fix=True,
        )

    def get_system_prompt(self, variables: dict[str, Any] | None = None) -> str:
        """Return The Alchemist's system prompt from YAML template."""
        return get_prompt(
            agent_name="alchemist",
            variables=variables or {},
        )

    async def execute(self, context: "AgentContext") -> AgentResult:
        """
        Generate CSS effects based on context.

        Args:
            context: Pipeline context with HTML from Architect

        Returns:
            AgentResult containing the generated CSS
        """
        import time

        start_time = time.time()

        try:
            # Build the prompt
            prompt = self._build_alchemist_prompt(context)

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

            # Extract CSS from response
            css_output = self._extract_css(response_text)

            # Validate output
            is_valid, issues = self.validate_output(css_output)

            # Auto-fix if enabled
            if not is_valid and self.config.auto_fix:
                css_output = self.auto_fix_output(css_output)
                is_valid, issues = self.validate_output(css_output)

            # Create result
            result = AgentResult(
                success=True,
                output=css_output,
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                warnings=issues if not is_valid else [],
            )

            # Post-process to extract CSS variables
            result = self.post_process(result, css_output)

            if not is_valid and self.config.strict_mode:
                result.success = False
                result.errors = issues

            logger.info(
                f"[Alchemist] Generated CSS with {len(result.extracted_css_vars)} variables"
            )

            return result

        except Exception as e:
            logger.error(f"[Alchemist] Execution failed: {e}")
            return AgentResult(
                success=False,
                output="",
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                errors=[str(e)],
            )

    def _build_alchemist_prompt(self, context: "AgentContext") -> str:
        """Build the prompt for CSS generation."""
        parts = []

        # Theme context
        if context.theme:
            parts.append(f"## Theme\n{context.theme}")

        # Content language (for comment style)
        if context.content_language:
            parts.append(f"## Content Language\n{context.content_language}")

        # === UX Enhancement: Vibe Animation Parameters ===
        # Ensures all CSS animations use consistent timing/easing across the design
        if context.vibe or context.vibe_timing != "300ms":
            vibe_section = "## Animation Timing (MUST FOLLOW)\n"
            vibe_section += f"- **transition-duration**: {context.vibe_timing}\n"
            vibe_section += f"- **animation-duration**: Use {context.vibe_timing} as base (2x for complex)\n"
            vibe_section += f"- **easing**: {context.vibe_easing}\n"
            vibe_section += f"- **intensity**: {context.vibe_intensity}\n"
            if context.vibe:
                vibe_section += f"- **vibe**: {context.vibe}\n"
            vibe_section += "\n**CRITICAL CSS RULES**:\n"
            vibe_section += f"1. ALL transitions MUST use: `transition: all {context.vibe_timing} {context.vibe_easing}`\n"
            vibe_section += "2. Hover effects: Use the specified duration\n"
            vibe_section += "3. @keyframes: Duration should be 2-3x the base for complex animations\n"
            vibe_section += f"4. Define CSS variable: `--vibe-transition: all {context.vibe_timing} {context.vibe_easing};`"
            parts.append(vibe_section)

        # Pass vibe CSS variables for consistent theming
        if context.vibe_css_variables:
            css_vars_section = "## Vibe CSS Variables (INCLUDE IN :root)\n```css\n:root {\n"
            for key, value in context.vibe_css_variables.items():
                css_vars_section += f"  {key}: {value};\n"
            css_vars_section += "}\n```"
            parts.append(css_vars_section)

        # Design DNA - critical for color/animation consistency
        if context.design_dna:
            import json

            dna_json = json.dumps(
                context.design_dna.to_dict(), indent=2, ensure_ascii=False
            )
            parts.append(f"## Design DNA (Use These Tokens)\n{dna_json}")

        # === Phase 1: Few-Shot Examples ===
        # CSS examples to guide animation and effect quality
        if context.few_shot_examples:
            examples_section = "## REFERENCE CSS EXAMPLES (Follow This Quality Level)\n"
            for i, example in enumerate(context.few_shot_examples, 1):
                example_type = example.get("component_type", "example")
                example_css = example.get("css", "")
                if example_css:
                    examples_section += f"\n### Example {i}: {example_type.upper()} CSS\n"
                    examples_section += f"```css\n{example_css[:1500]}\n```\n"
            if "Example 1:" in examples_section:  # Only add if we have actual CSS
                parts.append(examples_section)

        # === UX Enhancement: Micro-Interaction Presets ===
        # Provides Tailwind-based preset classes for CSS conversion
        if context.micro_interaction_presets:
            presets_section = "## MICRO-INTERACTION PRESETS (Convert to CSS)\n"
            presets_section += "These Tailwind-based presets should be converted to pure CSS:\n\n"
            # Show top 8 most commonly used presets
            priority_presets = [
                "hover_lift", "hover_glow", "hover_scale", "focus_ring",
                "button_press", "shimmer", "pulse", "fade_in"
            ]
            for name in priority_presets:
                if name in context.micro_interaction_presets:
                    preset = context.micro_interaction_presets[name]
                    classes = preset.get("classes", "")
                    desc = preset.get("description", "")
                    presets_section += f"**{name}**: {desc}\n"
                    presets_section += f"Tailwind: `{classes}`\n\n"
            presets_section += "**RULE**: Convert these to CSS with consistent timing using vibe variables.\n"
            presets_section += "Example: `hover:-translate-y-1` → `transform: translateY(-4px);`"
            parts.append(presets_section)

        # HTML context - the Alchemist needs to know what to style
        if context.html_output:
            # Compress HTML to just IDs and classes
            compressed = self._compress_html_for_css(context.html_output)
            parts.append(f"## HTML Context (Target These Selectors)\n{compressed}")
        elif context.previous_output:
            compressed = self._compress_html_for_css(context.previous_output)
            parts.append(f"## HTML Context (Target These Selectors)\n{compressed}")

        # Compressed metadata if available
        if context.compressed:
            if context.compressed.element_ids:
                parts.append(f"## Available IDs\n{', '.join(context.compressed.element_ids)}")
            if context.compressed.tailwind_classes:
                # Filter to key classes for theming
                theme_classes = [
                    c for c in context.compressed.tailwind_classes
                    if any(p in c for p in ["bg-", "text-", "border-", "shadow-"])
                ]
                if theme_classes:
                    parts.append(f"## Key Tailwind Classes\n{', '.join(theme_classes[:30])}")

        # Correction feedback (syntax validation errors)
        if context.correction_feedback:
            parts.append(
                f"## CORRECTION REQUIRED\n"
                f"Previous output had issues:\n{context.correction_feedback}\n"
                f"Fix these issues in this attempt."
            )

        # Critic feedback (design quality improvements from refiner loop)
        if context.critic_feedback:
            iteration_info = f" (Iteration {context.refiner_iteration})" if context.refiner_iteration else ""
            feedback_list = "\n".join(f"- {item}" for item in context.critic_feedback)
            parts.append(
                f"## DESIGN IMPROVEMENT REQUIRED{iteration_info}\n"
                f"The Critic agent scored the previous CSS below quality threshold.\n"
                f"Address these design improvements:\n{feedback_list}\n\n"
                f"Focus on the highest-impact improvements first."
            )

        return "\n\n".join(parts)

    def _compress_html_for_css(self, html: str) -> str:
        """
        Compress HTML to just the selectors needed for CSS targeting.
        """
        parts = []

        # Extract IDs
        ids = self.extract_ids(html)
        if ids:
            parts.append(f"IDs: #{', #'.join(ids)}")

        # Extract classes
        classes = self.extract_tailwind_classes(html)

        # Filter to custom classes (non-Tailwind)
        tailwind_prefixes = [
            "bg-", "text-", "font-", "p-", "m-", "w-", "h-", "flex",
            "grid", "gap-", "rounded-", "shadow-", "border-", "hover:",
            "focus:", "dark:", "sm:", "md:", "lg:", "xl:", "2xl:",
        ]
        custom_classes = [
            c for c in classes
            if not any(c.startswith(p) for p in tailwind_prefixes)
        ]
        if custom_classes:
            parts.append(f"Custom classes: .{', .'.join(custom_classes[:20])}")

        # Extract animation targets (elements with transform, transition)
        animation_classes = [c for c in classes if "transform" in c or "transition" in c]
        if animation_classes:
            parts.append(f"Animation targets: {', '.join(animation_classes[:10])}")

        return "\n".join(parts) if parts else "No specific selectors provided - create general effect classes"

    def _extract_css(self, response: str) -> str:
        """
        Extract CSS from the response.

        The response might contain markdown code blocks or raw CSS.
        """
        # Try to extract from code blocks
        css_pattern = r"```css\s*([\s\S]*?)```"
        matches = re.findall(css_pattern, response, re.IGNORECASE)
        if matches:
            return matches[0].strip()

        # Try generic code blocks
        code_pattern = r"```\s*([\s\S]*?)```"
        matches = re.findall(code_pattern, response)
        if matches:
            # Check if it looks like CSS
            for match in matches:
                if "{" in match and "}" in match and ":" in match:
                    return match.strip()

        # If no code blocks, assume raw CSS
        cleaned = response.strip()
        cleaned = re.sub(r"^#+\s*.*$", "", cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    def validate_output(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate CSS output against Alchemist constraints.

        Uses centralized CSSValidator for comprehensive checks:
        1. No HTML elements
        2. No JavaScript code
        3. Valid CSS syntax (balanced braces, quotes)
        4. No !important abuse
        5. Uses class/ID selectors appropriately
        6. Vendor prefix validation
        7. Animation/keyframe validation
        8. CSS variable consistency
        """
        # Phase 3: Use centralized CSSValidator
        result = self._css_validator.validate(output)

        # Convert ValidationResult to tuple[bool, list[str]] for backward compatibility
        issues = [
            issue.message
            for issue in result.issues
            if issue.severity.value == "error"  # Only report errors as issues
        ]

        return result.valid, issues

    def auto_fix_output(self, output: str) -> str:
        """
        Attempt to auto-fix common issues in CSS output.

        Returns the fixed output.
        """
        fixed = output

        # Remove any HTML tags
        fixed = re.sub(r"<[^>]+>", "", fixed)

        # Remove JavaScript-like code blocks
        fixed = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", fixed, flags=re.IGNORECASE)

        # Remove excessive !important (keep first 3)
        important_matches = list(re.finditer(r"!important", fixed, re.IGNORECASE))
        if len(important_matches) > 3:
            # Remove !important from matches after the first 3
            for match in reversed(important_matches[3:]):
                fixed = fixed[:match.start()] + fixed[match.end():]

        return fixed.strip()

    def get_effect_library(self, theme: str) -> str:
        """
        Get pre-built effect library for common patterns.

        This provides a starting point for the Alchemist.
        Always includes reduced-motion accessibility wrapper.
        """
        # === UX Enhancement: Reduced-Motion Accessibility ===
        # This MUST be included in ALL CSS outputs for accessibility
        reduced_motion_base = """
/* ============================================
   ACCESSIBILITY: Reduced Motion Support
   WCAG 2.1 SC 2.3.3 - Animation from Interactions
   ============================================ */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}

/* Safe animation class - respects user preference */
.animate-safe {
    animation-play-state: running;
}
@media (prefers-reduced-motion: reduce) {
    .animate-safe {
        animation-play-state: paused;
    }
}
"""

        effects = {
            "glassmorphism": """
/* Glassmorphism Effect */
.glass-effect {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}
""",
            "neon-glow": """
/* Neon Glow Effect */
.neon-glow {
    text-shadow:
        0 0 10px var(--neon-color, #00ffff),
        0 0 20px var(--neon-color, #00ffff),
        0 0 40px var(--neon-color, #00ffff);
}
.neon-box-glow {
    box-shadow:
        0 0 10px var(--neon-color, #00ffff),
        0 0 20px var(--neon-color, #00ffff);
}
""",
            "gradient-animation": """
/* Gradient Animation
   EXCEPTION: 3s duration is intentional for ambient background effects.
   Nielsen Norman: Decorative loops can exceed 500ms optimal range. */
@keyframes gradient-shift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
.animated-gradient {
    background-size: 200% 200%;
    animation: gradient-shift 3s ease infinite;
}
""",
            "morphing-blob": """
/* Morphing Blob
   EXCEPTION: 8s duration is intentional for organic ambient effects.
   Slow, continuous loops don't require user attention. */
@keyframes blob-morph {
    0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
    50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
}
.morphing-blob {
    animation: blob-morph 8s ease-in-out infinite;
}
""",
            "hover-transitions": """
/* Standard Hover Transitions (2025 Best Practices) */
.hover-lift {
    transition: transform var(--vibe-duration, 300ms) var(--vibe-easing, ease-out);
}
.hover-lift:hover {
    transform: translateY(-4px);
}

.hover-glow {
    transition: box-shadow var(--vibe-duration, 300ms) var(--vibe-easing, ease-out);
}
.hover-glow:hover {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.hover-scale {
    transition: transform var(--vibe-duration, 300ms) var(--vibe-easing, ease-out);
}
.hover-scale:hover {
    transform: scale(1.02);
}
""",
        }

        theme_effects = {
            "cyberpunk": ["neon-glow", "gradient-animation", "hover-transitions"],
            "glassmorphism": ["glassmorphism", "gradient-animation", "hover-transitions"],
            "neo-brutalism": ["morphing-blob", "hover-transitions"],
            "dark_mode_first": ["neon-glow", "glassmorphism", "hover-transitions"],
            "modern-minimal": ["hover-transitions"],
            "brutalist": ["hover-transitions"],
            "soft-ui": ["hover-transitions"],
            "corporate": ["hover-transitions"],
            "gradient": ["gradient-animation", "hover-transitions"],
            "startup": ["hover-transitions"],
        }

        effect_names = theme_effects.get(theme, ["hover-transitions"])
        theme_css = "\n".join(effects.get(name, "") for name in effect_names)

        # Always include reduced-motion accessibility wrapper
        return reduced_motion_base + theme_css
