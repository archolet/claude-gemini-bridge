"""
The Physicist - JavaScript Interaction Specialist

The Physicist is responsible for generating performant, vanilla JavaScript
interactions. It NEVER uses frameworks or libraries.

Responsibilities:
- Mouse/touch interactions (parallax, magnetic buttons, tilt)
- Scroll-based animations (IntersectionObserver)
- Performance-optimized code (requestAnimationFrame, throttle)
- Event handling with proper cleanup
- Error isolation (try-catch)
- Self-contained IIFE modules

Boundaries:
- NO frameworks (React, Vue, Angular)
- NO libraries (jQuery, GSAP, Lodash)
- NO unsafe code execution patterns
- NO global namespace pollution
- Vanilla JavaScript only
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Optional

from gemini_mcp.agents.base import AgentConfig, AgentResult, AgentRole, BaseAgent
from gemini_mcp.prompts import PHYSICIST_SYSTEM_PROMPT
from gemini_mcp.validation import JSValidator

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient
    from gemini_mcp.orchestration.context import AgentContext

logger = logging.getLogger(__name__)


class PhysicistAgent(BaseAgent):
    """
    The Physicist - JavaScript Interaction Specialist.

    Generates performant vanilla JavaScript for interactions: parallax, scroll
    reveals, magnetic buttons, tilt effects. Never uses frameworks or libraries.
    """

    role = AgentRole.PHYSICIST

    def __init__(
        self,
        client: "GeminiClient",
        config: Optional[AgentConfig] = None,
    ):
        """
        Initialize The Physicist.

        Args:
            client: GeminiClient for API calls
            config: Optional custom configuration
        """
        super().__init__(config)
        self.client = client
        # Phase 3: Centralized Validator Integration
        self._js_validator = JSValidator(strict_mode=False)

    @classmethod
    def _default_config(cls) -> AgentConfig:
        """Physicist-specific default configuration."""
        return AgentConfig(
            model="gemini-3-pro-preview",
            thinking_level="low",  # JS generation - focused output
            thinking_budget=4096,  # Deprecated
            temperature=1.0,  # Gemini 3 optimized
            max_output_tokens=8192,
            strict_mode=True,
            auto_fix=True,
        )

    def get_system_prompt(self) -> str:
        """Return The Physicist's system prompt."""
        return PHYSICIST_SYSTEM_PROMPT

    async def execute(self, context: "AgentContext") -> AgentResult:
        """
        Generate JavaScript interactions based on context.

        Args:
            context: Pipeline context with HTML/CSS from previous agents

        Returns:
            AgentResult containing the generated JavaScript
        """
        import time

        start_time = time.time()

        try:
            # Build the prompt
            prompt = self._build_physicist_prompt(context)

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

            # Extract JS from response
            js_output = self._extract_js(response_text)

            # Validate output
            is_valid, issues = self.validate_output(js_output)

            # Auto-fix if enabled
            if not is_valid and self.config.auto_fix:
                js_output = self.auto_fix_output(js_output)
                is_valid, issues = self.validate_output(js_output)

            # Create result
            result = AgentResult(
                success=True,
                output=js_output,
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                warnings=issues if not is_valid else [],
            )

            if not is_valid and self.config.strict_mode:
                result.success = False
                result.errors = issues

            logger.info(f"[Physicist] Generated JS ({len(js_output)} chars)")

            return result

        except Exception as e:
            logger.error(f"[Physicist] Execution failed: {e}")
            return AgentResult(
                success=False,
                output="",
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                errors=[str(e)],
            )

    def _build_physicist_prompt(self, context: "AgentContext") -> str:
        """Build the prompt for JS generation."""
        parts = []

        # Theme context (affects interaction style)
        if context.theme:
            parts.append(f"## Theme\n{context.theme}")

        # === UX Enhancement: Vibe Animation Parameters ===
        # Ensures all JS animations use consistent timing/easing across the design
        if context.vibe or context.vibe_timing != "300ms":
            vibe_section = "## Animation Timing (MUST FOLLOW)\n"
            vibe_section += f"- **Duration**: {context.vibe_timing} (use for all transitions)\n"
            vibe_section += f"- **Easing**: {context.vibe_easing}\n"
            vibe_section += f"- **Intensity**: {context.vibe_intensity}\n"
            if context.vibe:
                vibe_section += f"- **Vibe**: {context.vibe}\n"
            vibe_section += "\n**CRITICAL**: All requestAnimationFrame lerp factors and "
            vibe_section += "setTimeout delays MUST align with these timing values.\n"
            vibe_section += "Example: For 300ms duration, use lerp factor ~0.1 (reaches 95% in ~300ms)"
            parts.append(vibe_section)

        # Pass vibe CSS variables for dynamic styling
        if context.vibe_css_variables:
            css_vars = [f"{k}: {v}" for k, v in context.vibe_css_variables.items()]
            parts.append(f"## Vibe CSS Variables (Reference Only)\n{chr(10).join(css_vars)}")

        # Available element IDs - critical for targeting
        ids_to_target = []

        # From compressed context
        if context.compressed and context.compressed.element_ids:
            ids_to_target.extend(context.compressed.element_ids)

        # From HTML output
        if context.html_output:
            html_ids = self.extract_ids(context.html_output)
            ids_to_target.extend(html_ids)

        # Deduplicate
        ids_to_target = list(set(ids_to_target))

        if ids_to_target:
            parts.append(f"## Available Element IDs\n{', '.join(ids_to_target)}")
        else:
            parts.append("## Note\nNo specific IDs provided - create general interaction patterns")

        # Design DNA for animation style
        if context.design_dna:
            import json

            # Only pass animation-related DNA
            animation_dna = {
                "animation": context.design_dna.animation,
                "mood": context.design_dna.mood,
            }
            dna_json = json.dumps(animation_dna, indent=2, ensure_ascii=False)
            parts.append(f"## Animation Style (From DNA)\n{dna_json}")

        # === Phase 1: Few-Shot Examples ===
        # JS examples to guide interaction implementation
        if context.few_shot_examples:
            examples_section = "## REFERENCE JS EXAMPLES (Follow This Quality Level)\n"
            for i, example in enumerate(context.few_shot_examples, 1):
                example_type = example.get("component_type", "example")
                example_js = example.get("js", "")
                if example_js:
                    examples_section += f"\n### Example {i}: {example_type.upper()} Interactions\n"
                    examples_section += f"```javascript\n{example_js[:1500]}\n```\n"
            if "Example 1:" in examples_section:  # Only add if we have actual JS
                parts.append(examples_section)

        # === UX Enhancement: Micro-Interaction Presets ===
        # Provides preset definitions for JS implementation
        if context.micro_interaction_presets:
            presets_section = "## MICRO-INTERACTION PRESETS (Implement as JS)\n"
            presets_section += "Handle these data-interaction attributes with JS:\n\n"
            # Show presets that need JS implementation
            js_presets = [
                ("hover_lift", "translateY(-4px) on hover"),
                ("hover_scale", "scale(1.05) on hover, scale(0.95) on click"),
                ("magnetic", "element follows cursor with easing"),
                ("shimmer", "gradient animation sweep"),
                ("parallax", "scroll-based Y translation"),
                ("scroll_reveal", "fade/slide in on viewport enter"),
            ]
            for name, behavior in js_presets:
                if name in context.micro_interaction_presets:
                    preset = context.micro_interaction_presets[name]
                    desc = preset.get("description", behavior)
                    presets_section += f"**data-interaction=\"{name}\"**: {desc}\n"
            presets_section += "\n**RULES**:\n"
            presets_section += f"1. Use {context.vibe_timing} duration for all animations\n"
            presets_section += f"2. Use {context.vibe_easing} easing curve\n"
            presets_section += "3. Check `shouldAnimate()` before running animations\n"
            presets_section += "4. Use lerp factor matching the duration (300ms → 0.1)"
            parts.append(presets_section)

        # CSS variables available (for dynamic styling)
        if context.compressed and context.compressed.css_variables:
            parts.append(f"## Available CSS Variables\n{', '.join(context.compressed.css_variables[:20])}")

        # === PHASE 7: Structural Map - Use interaction_map from Architect ===
        interaction_specs = self._build_interaction_specs(context)
        if interaction_specs:
            parts.append(interaction_specs)

        # Correction feedback
        if context.correction_feedback:
            parts.append(
                f"## CORRECTION REQUIRED\n"
                f"Previous output had issues:\n{context.correction_feedback}\n"
                f"Fix these issues in this attempt."
            )

        return "\n\n".join(parts)

    def _build_interaction_specs(self, context: "AgentContext") -> str:
        """
        Build interaction specifications from Architect's data-* attributes.

        Uses the interaction_map from compressed context (Phase 7 Structural Map).
        Falls back to component-type hints if no interaction_map available.
        """
        import json

        lines = []

        # === PRIMARY: Use Architect's interaction_map ===
        if context.compressed and context.compressed.interaction_map:
            interaction_map = context.compressed.interaction_map
            lines.append("## Element Interactions (From Architect)")
            lines.append("")
            lines.append(
                "The Architect has specified these interactions via data-* attributes:"
            )
            lines.append("")

            # Group by interaction type for better organization
            by_type: dict[str, list[tuple[str, any]]] = {}
            for element_id, spec in interaction_map.items():
                itype = spec.interaction_type
                if itype not in by_type:
                    by_type[itype] = []
                by_type[itype].append((element_id, spec))

            for interaction_type, specs in by_type.items():
                lines.append(f"### {interaction_type.upper()} Effects")
                for element_id, spec in specs:
                    lines.append(
                        f"- `#{element_id}`: trigger={spec.trigger}, "
                        f"intensity={spec.intensity}, delay={spec.delay}ms"
                    )
                    if spec.group:
                        lines.append(f"  - Sync group: {spec.group}")
                    if spec.duration != 300:
                        lines.append(f"  - Duration: {spec.duration}ms")
                    if spec.easing != "ease-out":
                        lines.append(f"  - Easing: {spec.easing}")
                lines.append("")

            lines.append(
                "**CRITICAL**: Implement ONLY the interactions listed above. "
                "Each element's ID and parameters are pre-defined by The Architect."
            )

            return "\n".join(lines)

        # === FALLBACK: Component-type based hints ===
        fallback_map = {
            "hero": ["parallax", "scroll-reveal", "magnetic-cta"],
            "navbar": ["scroll-hide", "mobile-menu"],
            "card": ["tilt-effect", "hover-glow"],
            "pricing": ["toggle-animation", "highlight-effect"],
            "pricing_card": ["tilt-effect", "magnetic-button"],
            "testimonial": ["carousel", "auto-scroll"],
            "modal": ["open-close", "backdrop-click"],
            "form": ["validation-feedback", "submit-animation"],
        }

        component_type = context.component_type or ""
        if component_type.lower() in fallback_map:
            hints = fallback_map[component_type.lower()]
            return f"## Suggested Interactions (Fallback)\n{', '.join(hints)}"

        return ""

    def _extract_js(self, response: str) -> str:
        """
        Extract JavaScript from the response.

        The response might contain markdown code blocks or raw JS.
        """
        # Try to extract from javascript code blocks
        js_pattern = r"```(?:javascript|js)\s*([\s\S]*?)```"
        matches = re.findall(js_pattern, response, re.IGNORECASE)
        if matches:
            return matches[0].strip()

        # Try generic code blocks
        code_pattern = r"```\s*([\s\S]*?)```"
        matches = re.findall(code_pattern, response)
        if matches:
            # Check if it looks like JS
            for match in matches:
                if any(kw in match for kw in ["function", "const ", "let ", "=>"]):
                    return match.strip()

        # If no code blocks, assume raw JS
        cleaned = response.strip()
        cleaned = re.sub(r"^#+\s*.*$", "", cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    def validate_output(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate JavaScript output against Physicist constraints.

        Uses centralized JSValidator for comprehensive checks:
        1. No framework/library imports
        2. No global namespace pollution
        3. No unsafe code patterns (eval, dynamic Function)
        4. Basic syntax validity
        5. Performance patterns (rAF, throttle)
        6. Error handling (try-catch)
        7. Event listener cleanup
        """
        # Phase 3: Use centralized JSValidator
        result = self._js_validator.validate(output)

        # Convert ValidationResult to tuple[bool, list[str]] for backward compatibility
        issues = [
            issue.message
            for issue in result.issues
            if issue.severity.value == "error"  # Only report errors as issues
        ]

        return result.valid, issues

    def auto_fix_output(self, output: str) -> str:
        """
        Attempt to auto-fix common issues in JS output.

        Returns the fixed output.
        """
        fixed = output

        # Remove import statements
        fixed = re.sub(r"^\s*import\s+.*$", "", fixed, flags=re.MULTILINE)

        # Remove require statements
        fixed = re.sub(r"^\s*const\s+\w+\s*=\s*require\s*\([^)]+\).*$", "", fixed, flags=re.MULTILINE)

        # Wrap in IIFE if not already wrapped
        if not re.search(r"^\s*\(function\s*\(", fixed) and not re.search(r"^\s*\(\s*\(\s*\)\s*=>", fixed):
            fixed = f"(function() {{\n  'use strict';\n\n  document.addEventListener('DOMContentLoaded', () => {{\n{self._indent(fixed, 4)}\n  }});\n}})();"

        return fixed.strip()

    def _indent(self, text: str, spaces: int) -> str:
        """Indent all lines by given number of spaces."""
        prefix = " " * spaces
        lines = text.split("\n")
        return "\n".join(prefix + line if line.strip() else line for line in lines)

    def get_interaction_patterns(self) -> dict[str, str]:
        """
        Get pre-built interaction patterns for common use cases.

        Returns a dictionary of pattern name to code snippet.
        All patterns include reduced-motion accessibility checks.
        """
        return {
            "reduced-motion-utils": """
// ============================================
// ACCESSIBILITY: Reduced Motion Utilities
// WCAG 2.1 SC 2.3.3 - Animation from Interactions
// ============================================
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Helper to check reduced motion preference
function shouldAnimate() {
  return !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// Listen for preference changes (user might toggle during session)
window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
  document.body.classList.toggle('reduce-motion', e.matches);
});
""",
            "scroll-reveal": """
// Scroll Reveal with IntersectionObserver (Reduced-Motion Safe)
if (shouldAnimate()) {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('[data-reveal]').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 400ms ease-out, transform 400ms ease-out';
    revealObserver.observe(el);
  });
} else {
  // Reduced motion: Show immediately without animation
  document.querySelectorAll('[data-reveal]').forEach(el => {
    el.style.opacity = '1';
    el.classList.add('revealed');
  });
}
""",
            "parallax": """
// Mouse Parallax Effect (Reduced-Motion Safe)
if (shouldAnimate()) {
  const parallaxElements = document.querySelectorAll('[data-parallax]');
  let mouseX = 0, mouseY = 0;
  let currentX = 0, currentY = 0;

  document.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  function animateParallax() {
    // Lerp factor 0.1 = ~300ms to reach 95%
    currentX += (mouseX - currentX) * 0.1;
    currentY += (mouseY - currentY) * 0.1;

    parallaxElements.forEach(el => {
      const depth = parseFloat(el.dataset.parallax) || 20;
      const x = currentX * depth;
      const y = currentY * depth;
      el.style.transform = `translate3d(${x}px, ${y}px, 0)`;
    });

    requestAnimationFrame(animateParallax);
  }
  animateParallax();
}
""",
            "magnetic-button": """
// Magnetic Button Effect (Reduced-Motion Safe)
if (shouldAnimate()) {
  document.querySelectorAll('[data-magnetic]').forEach(button => {
    button.addEventListener('mousemove', (e) => {
      const rect = button.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      button.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
    });

    button.addEventListener('mouseleave', () => {
      button.style.transform = 'translate(0, 0)';
      button.style.transition = 'transform 200ms ease-out';
    });

    button.addEventListener('mouseenter', () => {
      button.style.transition = 'none';
    });
  });
}
""",
            "tilt-effect": """
// 3D Tilt Effect (Reduced-Motion Safe)
if (shouldAnimate()) {
  document.querySelectorAll('[data-tilt]').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;

      const tiltX = (y - 0.5) * 20;
      const tiltY = (x - 0.5) * -20;

      card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
      card.style.transition = 'transform 300ms ease-out';
    });
  });
}
""",
            "throttle": """
// Throttle Utility (Performance Optimization)
function throttle(fn, delay) {
  let lastCall = 0;
  return function(...args) {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      return fn.apply(this, args);
    }
  };
}
""",
        }
