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

    @classmethod
    def _default_config(cls) -> AgentConfig:
        """Physicist-specific default configuration."""
        return AgentConfig(
            model="gemini-3-pro-preview",
            thinking_budget=4096,
            temperature=0.7,
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

            # Call Gemini API
            response = await self.client.generate_text(
                prompt=prompt,
                system_instruction=self.get_system_prompt(),
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
            )

            # Extract JS from response
            js_output = self._extract_js(response)

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

        Checks:
        1. No framework imports
        2. No library usage
        3. No unsafe patterns
        4. No global namespace pollution
        5. Basic syntax validity
        """
        issues: list[str] = []

        if not output or not output.strip():
            # Empty JS is valid - not all components need JS
            return True, []

        # Check for frameworks/libraries
        forbidden_imports = [
            (r"\bimport\s+.*from\s+['\"]react", "React import detected"),
            (r"\bimport\s+.*from\s+['\"]vue", "Vue import detected"),
            (r"\bimport\s+.*from\s+['\"]angular", "Angular import detected"),
            (r"\bimport\s+.*from\s+['\"]jquery", "jQuery import detected"),
            (r"\bimport\s+.*from\s+['\"]gsap", "GSAP import detected"),
            (r"\brequire\s*\(\s*['\"]react", "React require detected"),
            (r"\$\s*\(", "jQuery usage detected"),
            (r"\bjQuery\s*\(", "jQuery usage detected"),
            (r"\bgsap\.", "GSAP usage detected"),
            (r"\bTweenMax\.", "GSAP TweenMax detected"),
            (r"\bReact\.", "React usage detected"),
            (r"\bVue\.", "Vue usage detected"),
            (r"\bAngular\.", "Angular usage detected"),
        ]

        for pattern, message in forbidden_imports:
            if re.search(pattern, output, re.IGNORECASE):
                issues.append(f"Framework/library detected: {message}")

        # Check for global pollution
        global_patterns = [
            (r"^\s*window\.\w+\s*=", "Global window property assignment"),
            (r"^\s*var\s+\w+\s*=", "Global var declaration (use const/let in IIFE)"),
        ]
        for pattern, message in global_patterns:
            if re.search(pattern, output, re.MULTILINE):
                issues.append(f"Global pollution: {message}")

        # Check for HTML/CSS in output
        if re.search(r"<[a-z]+[^>]*>", output, re.IGNORECASE):
            if not re.search(r"['\"`].*<.*>.*['\"`]", output):  # Not in a string
                issues.append("Contains HTML elements - Physicist only outputs JS")

        # Basic syntax check - balanced braces/brackets
        open_braces = output.count("{")
        close_braces = output.count("}")
        if open_braces != close_braces:
            issues.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")

        open_brackets = output.count("[")
        close_brackets = output.count("]")
        if open_brackets != close_brackets:
            issues.append(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")

        open_parens = output.count("(")
        close_parens = output.count(")")
        if open_parens != close_parens:
            issues.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")

        return len(issues) == 0, issues

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
        """
        return {
            "scroll-reveal": """
// Scroll Reveal with IntersectionObserver
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
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  revealObserver.observe(el);
});
""",
            "parallax": """
// Mouse Parallax Effect
const parallaxElements = document.querySelectorAll('[data-parallax]');
let mouseX = 0, mouseY = 0;
let currentX = 0, currentY = 0;

document.addEventListener('mousemove', (e) => {
  mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
  mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
});

function animateParallax() {
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
""",
            "magnetic-button": """
// Magnetic Button Effect
document.querySelectorAll('[data-magnetic]').forEach(button => {
  button.addEventListener('mousemove', (e) => {
    const rect = button.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;

    button.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
  });

  button.addEventListener('mouseleave', () => {
    button.style.transform = 'translate(0, 0)';
    button.style.transition = 'transform 0.3s ease';
  });

  button.addEventListener('mouseenter', () => {
    button.style.transition = 'none';
  });
});
""",
            "tilt-effect": """
// 3D Tilt Effect
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
    card.style.transition = 'transform 0.5s ease';
  });
});
""",
            "throttle": """
// Throttle Utility
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
