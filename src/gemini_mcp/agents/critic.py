"""
The Critic - Art Direction Specialist

The Critic is used exclusively in the refine_frontend pipeline:
1. Analyzes user modification requests
2. Evaluates current design strengths/weaknesses
3. Recommends minimal change strategy
4. Guides the Trifecta on which layers to modify

The Critic NEVER generates code - only analysis and recommendations.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from gemini_mcp.agents.base import AgentConfig, AgentResult, AgentRole, BaseAgent
from gemini_mcp.prompts import CRITIC_SYSTEM_PROMPT

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient
    from gemini_mcp.orchestration.context import AgentContext

logger = logging.getLogger(__name__)


@dataclass
class DesignAnalysis:
    """Analysis of current design."""

    current_strengths: list[str] = field(default_factory=list)
    current_weaknesses: list[str] = field(default_factory=list)
    user_intent: str = ""


# === PHASE 3: Quality Scoring Dataclass ===
@dataclass
class CriticScores:
    """Quality scores for design evaluation (1-10 scale)."""

    layout: float = 5.0       # Layout hierarchy, spacing, alignment
    typography: float = 5.0   # Font choices, readability, hierarchy
    color: float = 5.0        # Color harmony, contrast, consistency
    interaction: float = 5.0  # Hover states, animations, feedback
    accessibility: float = 5.0  # WCAG compliance, semantic HTML

    @property
    def overall(self) -> float:
        """Calculate weighted average score."""
        # Weights: accessibility highest, then layout and color
        weights = {
            "layout": 0.25,
            "typography": 0.15,
            "color": 0.20,
            "interaction": 0.15,
            "accessibility": 0.25,
        }
        return (
            self.layout * weights["layout"]
            + self.typography * weights["typography"]
            + self.color * weights["color"]
            + self.interaction * weights["interaction"]
            + self.accessibility * weights["accessibility"]
        )

    def to_dict(self) -> dict:
        return {
            "layout": self.layout,
            "typography": self.typography,
            "color": self.color,
            "interaction": self.interaction,
            "accessibility": self.accessibility,
            "overall": round(self.overall, 2),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CriticScores":
        return cls(
            layout=data.get("layout", 5.0),
            typography=data.get("typography", 5.0),
            color=data.get("color", 5.0),
            interaction=data.get("interaction", 5.0),
            accessibility=data.get("accessibility", 5.0),
        )


# === CREATIVITY ENHANCEMENT: Reference Adherence Scores ===
@dataclass
class ReferenceAdherenceScores:
    """Scores for reference-based design adherence (1-10 scale)."""

    color_match: float = 5.0       # Colors match the reference palette
    typography_match: float = 5.0  # Typography matches reference style
    spacing_match: float = 5.0     # Spacing feels similar to reference
    aesthetic_match: float = 5.0   # Overall aesthetic similarity

    @property
    def overall(self) -> float:
        """Calculate average adherence score."""
        return (
            self.color_match + self.typography_match +
            self.spacing_match + self.aesthetic_match
        ) / 4.0

    def to_dict(self) -> dict:
        return {
            "color_match": self.color_match,
            "typography_match": self.typography_match,
            "spacing_match": self.spacing_match,
            "aesthetic_match": self.aesthetic_match,
            "overall": round(self.overall, 2),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReferenceAdherenceScores":
        return cls(
            color_match=data.get("color_match", 5.0),
            typography_match=data.get("typography_match", 5.0),
            spacing_match=data.get("spacing_match", 5.0),
            aesthetic_match=data.get("aesthetic_match", 5.0),
        )


@dataclass
class ChangeRecommendations:
    """Recommendations for design changes."""

    html_changes: list[str] = field(default_factory=list)
    css_changes: list[str] = field(default_factory=list)
    js_changes: list[str] = field(default_factory=list)
    priority_layer: str = "css"  # Most impacted layer


@dataclass
class CriticReport:
    """Full report from The Critic."""

    analysis: DesignAnalysis = field(default_factory=DesignAnalysis)
    recommendations: ChangeRecommendations = field(default_factory=ChangeRecommendations)
    minimal_change_strategy: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "analysis": {
                "current_strengths": self.analysis.current_strengths,
                "current_weaknesses": self.analysis.current_weaknesses,
                "user_intent": self.analysis.user_intent,
            },
            "recommendations": {
                "html_changes": self.recommendations.html_changes,
                "css_changes": self.recommendations.css_changes,
                "js_changes": self.recommendations.js_changes,
                "priority": self.recommendations.priority_layer,
            },
            "minimal_change_strategy": self.minimal_change_strategy,
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CriticReport":
        analysis = DesignAnalysis(
            current_strengths=data.get("analysis", {}).get("current_strengths", []),
            current_weaknesses=data.get("analysis", {}).get("current_weaknesses", []),
            user_intent=data.get("analysis", {}).get("user_intent", ""),
        )
        recommendations = ChangeRecommendations(
            html_changes=data.get("recommendations", {}).get("html_changes", []),
            css_changes=data.get("recommendations", {}).get("css_changes", []),
            js_changes=data.get("recommendations", {}).get("js_changes", []),
            priority_layer=data.get("recommendations", {}).get("priority", "css"),
        )
        return cls(
            analysis=analysis,
            recommendations=recommendations,
            minimal_change_strategy=data.get("minimal_change_strategy", ""),
            warnings=data.get("warnings", []),
        )


class CriticAgent(BaseAgent):
    """
    The Critic - Art Direction Specialist.

    Analyzes user modification requests and guides the Trifecta on changes.
    Used exclusively in refine_frontend pipeline.
    """

    role = AgentRole.CRITIC

    def __init__(
        self,
        client: "GeminiClient",
        config: Optional[AgentConfig] = None,
    ):
        """
        Initialize The Critic.

        Args:
            client: GeminiClient for API calls
            config: Optional custom configuration
        """
        super().__init__(config)
        self.client = client

    @classmethod
    def _default_config(cls) -> AgentConfig:
        """Critic-specific default configuration."""
        return AgentConfig(
            model="gemini-3-pro-preview",
            thinking_level="high",  # Art direction requires deep analysis
            thinking_budget=4096,  # Deprecated
            temperature=1.0,  # Gemini 3 optimized
            max_output_tokens=4096,
            strict_mode=False,  # Advisory output
            auto_fix=False,
        )

    def get_system_prompt(self) -> str:
        """Return The Critic's system prompt."""
        return CRITIC_SYSTEM_PROMPT

    async def execute(self, context: "AgentContext") -> AgentResult:
        """
        Analyze modification request and recommend changes.

        Args:
            context: Pipeline context with current HTML and user modifications

        Returns:
            AgentResult with CriticReport
        """
        import time

        start_time = time.time()

        try:
            # Build the prompt
            prompt = self._build_critic_prompt(context)

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

            # Parse response
            parsed_data = self._parse_response(response_text)
            critic_report = CriticReport.from_dict(parsed_data)

            # Create result
            result = AgentResult(
                success=True,
                output=json.dumps(critic_report.to_dict(), indent=2, ensure_ascii=False),
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                warnings=critic_report.warnings,
            )

            # Attach report to metadata
            result.metadata = {
                "critic_report": critic_report.to_dict(),
                "priority_layer": critic_report.recommendations.priority_layer,
            }

            logger.info(
                f"[Critic] Analysis complete. Priority: {critic_report.recommendations.priority_layer}, "
                f"HTML changes: {len(critic_report.recommendations.html_changes)}, "
                f"CSS changes: {len(critic_report.recommendations.css_changes)}, "
                f"JS changes: {len(critic_report.recommendations.js_changes)}"
            )

            return result

        except Exception as e:
            logger.error(f"[Critic] Execution failed: {e}")
            return AgentResult(
                success=False,
                output="",
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                errors=[str(e)],
            )

    def _build_critic_prompt(self, context: "AgentContext") -> str:
        """Build the prompt for design analysis."""
        parts = []

        # User's modification request
        if context.modification_request:
            parts.append(f"## User Modification Request\n{context.modification_request}")
        elif context.user_requirements:
            parts.append(f"## User Requirements\n{context.user_requirements}")

        # Current HTML to analyze
        if context.previous_output:
            # Truncate for token efficiency
            html_preview = context.previous_output[:4000]
            parts.append(f"## Current HTML\n```html\n{html_preview}\n```")

        # Current CSS if available
        if context.css_output:
            css_preview = context.css_output[:2000]
            parts.append(f"## Current CSS\n```css\n{css_preview}\n```")

        # Current JS if available
        if context.js_output:
            js_preview = context.js_output[:2000]
            parts.append(f"## Current JS\n```javascript\n{js_preview}\n```")

        # Design context
        if context.theme:
            parts.append(f"## Theme\n{context.theme}")

        if context.design_dna:
            dna_json = json.dumps(context.design_dna.to_dict(), indent=2, ensure_ascii=False)
            parts.append(f"## Design DNA\n```json\n{dna_json}\n```")

        # Content language
        if context.content_language:
            parts.append(f"## Content Language\n{context.content_language}")

        # Task
        parts.append("""
## Task
Analyze the current design and the user's modification request.
Provide:
1. Analysis of current strengths and weaknesses
2. Interpretation of user intent
3. Recommendations for minimal changes (HTML/CSS/JS)
4. Strategy for achieving the changes with minimal disruption

Output JSON format as specified in your system prompt.
""")

        return "\n\n".join(parts)

    def _parse_response(self, response: str) -> dict:
        """
        Parse JSON response from The Critic.
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
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

        # Fallback: return empty structure
        logger.warning("[Critic] Could not parse JSON response")
        return {
            "analysis": {
                "current_strengths": [],
                "current_weaknesses": [],
                "user_intent": "Unknown",
            },
            "recommendations": {
                "html_changes": [],
                "css_changes": [],
                "js_changes": [],
                "priority": "css",
            },
            "minimal_change_strategy": "Unable to analyze",
            "warnings": ["Failed to parse Critic response"],
        }

    def validate_output(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate Critic output (JSON report).
        """
        issues = []

        if not output or not output.strip():
            return True, []

        try:
            data = json.loads(output)
            if "analysis" not in data:
                issues.append("Missing 'analysis' field in report")
            if "recommendations" not in data:
                issues.append("Missing 'recommendations' field in report")
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON report: {e}")

        return len(issues) == 0, issues

    def auto_fix_output(self, output: str) -> str:
        """Critic output doesn't need auto-fix."""
        return output

    def quick_analyze(self, html: str, modification: str) -> dict:  # noqa: ARG002
        """
        Quick analysis without API call.

        Uses heuristics to determine likely changes needed.
        """
        modification_lower = modification.lower()
        result = {
            "priority_layer": "css",
            "likely_html_changes": False,
            "likely_css_changes": False,
            "likely_js_changes": False,
        }

        # Color-related keywords
        color_keywords = ["renk", "color", "palette", "tema", "theme", "dark", "light"]
        if any(kw in modification_lower for kw in color_keywords):
            result["likely_css_changes"] = True
            result["priority_layer"] = "css"

        # Layout keywords
        layout_keywords = ["layout", "yerleşim", "grid", "flex", "column", "row", "hizala", "align"]
        if any(kw in modification_lower for kw in layout_keywords):
            result["likely_html_changes"] = True
            result["priority_layer"] = "html"

        # Animation keywords
        animation_keywords = ["animasyon", "animation", "hover", "transition", "efekt", "effect"]
        if any(kw in modification_lower for kw in animation_keywords):
            result["likely_css_changes"] = True
            result["likely_js_changes"] = True

        # Interaction keywords
        interaction_keywords = ["click", "tıkla", "mouse", "scroll", "parallax", "interaktif"]
        if any(kw in modification_lower for kw in interaction_keywords):
            result["likely_js_changes"] = True
            result["priority_layer"] = "js"

        # Size/spacing keywords
        size_keywords = ["büyüt", "küçült", "size", "padding", "margin", "spacing", "boşluk"]
        if any(kw in modification_lower for kw in size_keywords):
            result["likely_css_changes"] = True

        # Content keywords
        content_keywords = ["metin", "text", "başlık", "heading", "buton", "button", "ekle", "add"]
        if any(kw in modification_lower for kw in content_keywords):
            result["likely_html_changes"] = True
            result["priority_layer"] = "html"

        return result

    def determine_change_scope(self, modification: str) -> str:
        """
        Determine the scope of changes based on modification request.

        Returns: "minimal", "moderate", or "extensive"
        """
        modification_lower = modification.lower()

        # Extensive change indicators
        extensive_keywords = ["tamamen", "completely", "yeniden", "redesign", "rebuild", "overhaul"]
        if any(kw in modification_lower for kw in extensive_keywords):
            return "extensive"

        # Moderate change indicators
        moderate_keywords = ["değiştir", "change", "güncelle", "update", "revize", "revise"]
        if any(kw in modification_lower for kw in moderate_keywords):
            return "moderate"

        # Minimal change indicators (or default)
        return "minimal"

    # === PHASE 3: Quality Evaluation for Refiner Loop ===

    async def evaluate(
        self,
        html: str,
        css: str,
        js: str = "",
        context: Optional["AgentContext"] = None,
    ) -> tuple[CriticScores, list[str]]:
        """
        Evaluate design quality and return scores with improvements.

        Used in the refiner loop to determine if quality threshold is met.

        Args:
            html: HTML output to evaluate
            css: CSS output to evaluate
            js: Optional JS output to evaluate
            context: Optional context for thought signature handling

        Returns:
            Tuple of (CriticScores, list of improvement suggestions)
        """
        import time

        start_time = time.time()

        try:
            # Build evaluation prompt
            prompt = self._build_evaluation_prompt(html, css, js)

            # Call Gemini API with Gemini 3 optimizations
            response = await self.client.generate_text(
                prompt=prompt,
                system_instruction=self._get_evaluation_system_prompt(),
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
                thinking_level=self.config.thinking_level,
            )

            # Extract text and thought signature
            response_text = response.get("text", "")

            # Add thought signature to context if provided
            if context and response.get("thought_signature"):
                context.add_thought_signature(response["thought_signature"])

            # Parse scores and improvements
            scores, improvements = self._parse_evaluation_response(response_text)

            logger.info(
                f"[Critic] Evaluation complete. Overall: {scores.overall:.2f}, "
                f"Improvements: {len(improvements)}, "
                f"Time: {(time.time() - start_time) * 1000:.0f}ms"
            )

            return scores, improvements

        except Exception as e:
            logger.error(f"[Critic] Evaluation failed: {e}")
            # Return default scores on error
            return CriticScores(), [f"Evaluation error: {str(e)}"]

    def _build_evaluation_prompt(self, html: str, css: str, js: str = "") -> str:
        """Build prompt for design quality evaluation."""
        parts = [
            "## DESIGN QUALITY EVALUATION",
            "",
            "Evaluate the following design on a 1-10 scale for each category.",
            "",
        ]

        # HTML (truncate if too long)
        html_preview = html[:4000] if len(html) > 4000 else html
        parts.append(f"### HTML\n```html\n{html_preview}\n```")

        # CSS
        if css:
            css_preview = css[:3000] if len(css) > 3000 else css
            parts.append(f"### CSS\n```css\n{css_preview}\n```")

        # JS
        if js:
            js_preview = js[:2000] if len(js) > 2000 else js
            parts.append(f"### JavaScript\n```javascript\n{js_preview}\n```")

        # Scoring criteria
        parts.append("""
### Evaluation Criteria (1-10 scale)

1. **Layout (25%)**: Visual hierarchy, spacing consistency, alignment, responsive design
2. **Typography (15%)**: Font choices, readability, text hierarchy, line heights
3. **Color (20%)**: Color harmony, contrast ratios, palette consistency, dark mode
4. **Interaction (15%)**: Hover states, transitions, animations, feedback cues
5. **Accessibility (25%)**: WCAG compliance, semantic HTML, ARIA labels, focus states

### Output Format

Return JSON with scores and specific improvements:
```json
{
    "scores": {
        "layout": 8.5,
        "typography": 7.0,
        "color": 9.0,
        "interaction": 6.5,
        "accessibility": 8.0
    },
    "improvements": [
        "Add more spacing between sections (gap-8 → gap-12)",
        "Improve contrast on secondary text (#9ca3af → #6b7280)",
        "Add hover:scale-105 to CTA buttons for better feedback"
    ]
}
```

Be specific in improvements - include exact Tailwind classes or CSS values to change.
""")

        return "\n".join(parts)

    def _get_evaluation_system_prompt(self) -> str:
        """System prompt for design quality evaluation."""
        return """You are an expert UI/UX design critic specializing in:
- Visual design principles (Gestalt, hierarchy, balance)
- Tailwind CSS optimization
- WCAG 2.1 accessibility guidelines
- Modern web design patterns

Your role is to:
1. Objectively score design quality on a 1-10 scale
2. Identify specific, actionable improvements
3. Focus on high-impact changes first
4. Reference Tailwind classes when suggesting CSS changes

Be critical but constructive. A score of 10 is reserved for exceptional designs.
Average designs should score 5-6. Good designs score 7-8. Excellent designs 9+.

IMPORTANT: Output ONLY valid JSON. No markdown, no explanation, just the JSON object."""

    def _parse_evaluation_response(self, response: str) -> tuple[CriticScores, list[str]]:
        """Parse evaluation response into scores and improvements."""
        # Try to extract JSON
        json_pattern = r"```(?:json)?\s*(\{[\s\S]*?\})\s*```"
        matches = re.findall(json_pattern, response)

        parsed_data = None
        if matches:
            for match in matches:
                try:
                    parsed_data = json.loads(match)
                    break
                except json.JSONDecodeError:
                    continue

        # Try raw JSON if no code blocks
        if not parsed_data:
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    parsed_data = json.loads(response[start:end])
            except json.JSONDecodeError:
                pass

        # Parse or use defaults
        if parsed_data:
            scores_data = parsed_data.get("scores", {})
            scores = CriticScores(
                layout=float(scores_data.get("layout", 5.0)),
                typography=float(scores_data.get("typography", 5.0)),
                color=float(scores_data.get("color", 5.0)),
                interaction=float(scores_data.get("interaction", 5.0)),
                accessibility=float(scores_data.get("accessibility", 5.0)),
            )
            improvements = parsed_data.get("improvements", [])
        else:
            logger.warning("[Critic] Could not parse evaluation response")
            scores = CriticScores()
            improvements = ["Unable to parse evaluation - manual review recommended"]

        return scores, improvements

    # === CREATIVITY ENHANCEMENT: Reference Adherence Evaluation ===

    async def evaluate_reference_adherence(
        self,
        reference_tokens: dict,
        generated_html: str,
        generated_css: str,
        context: Optional["AgentContext"] = None,
    ) -> tuple[float, list[str]]:
        """
        Evaluate how well generated design matches reference tokens.

        Used in REFERENCE pipeline to ensure design fidelity to image reference.

        Args:
            reference_tokens: Design tokens from Visionary (colors, typography, etc.)
            generated_html: HTML output from Architect
            generated_css: CSS output from Alchemist
            context: Optional context for thought signature handling

        Returns:
            Tuple of (overall score 1-10, list of improvement suggestions)
        """
        import time

        start_time = time.time()

        try:
            # Build reference adherence prompt
            prompt = self._build_reference_adherence_prompt(
                reference_tokens, generated_html, generated_css
            )

            # Call Gemini API
            response = await self.client.generate_text(
                prompt=prompt,
                system_instruction=self._get_reference_adherence_system_prompt(),
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
                thinking_level=self.config.thinking_level,
            )

            # Extract text and thought signature
            response_text = response.get("text", "")

            # Add thought signature to context if provided
            if context and response.get("thought_signature"):
                context.add_thought_signature(response["thought_signature"])

            # Parse scores and improvements
            scores, improvements = self._parse_reference_adherence_response(response_text)

            logger.info(
                f"[Critic] Reference adherence evaluation complete. "
                f"Overall: {scores:.2f}, Improvements: {len(improvements)}, "
                f"Time: {(time.time() - start_time) * 1000:.0f}ms"
            )

            return scores, improvements

        except Exception as e:
            logger.error(f"[Critic] Reference adherence evaluation failed: {e}")
            return 5.0, [f"Reference adherence evaluation error: {str(e)}"]

    def _build_reference_adherence_prompt(
        self,
        reference_tokens: dict,
        generated_html: str,
        generated_css: str,
    ) -> str:
        """Build prompt for reference adherence evaluation."""
        parts = [
            "## REFERENCE ADHERENCE EVALUATION",
            "",
            "Evaluate how well the generated design matches the reference design tokens.",
            "",
        ]

        # Reference tokens from Visionary
        parts.append(f"### Reference Design Tokens\n```json\n{json.dumps(reference_tokens, indent=2)}\n```")

        # Generated HTML (truncate if needed)
        html_preview = generated_html[:4000] if len(generated_html) > 4000 else generated_html
        parts.append(f"### Generated HTML\n```html\n{html_preview}\n```")

        # Generated CSS
        if generated_css:
            css_preview = generated_css[:3000] if len(generated_css) > 3000 else generated_css
            parts.append(f"### Generated CSS\n```css\n{css_preview}\n```")

        # Scoring criteria
        parts.append("""
### Evaluation Criteria (1-10 scale)

1. **Color Match**: Do the generated colors match the reference palette?
   - Check background colors, text colors, accent colors
   - Consider if similar shades/tones are used

2. **Typography Match**: Does typography match reference style?
   - Font sizes, weights, line heights
   - Text hierarchy consistency

3. **Spacing Match**: Does spacing feel similar to reference?
   - Padding, margins, gap values
   - Overall density and breathing room

4. **Aesthetic Match**: Overall visual similarity?
   - General mood and feel
   - Design language consistency

### Output Format

Return JSON with scores and specific improvements:
```json
{
    "scores": {
        "color_match": 8.0,
        "typography_match": 7.5,
        "spacing_match": 8.0,
        "aesthetic_match": 7.0
    },
    "overall": 7.6,
    "improvements": [
        "Use bg-indigo-600 instead of bg-blue-600 to match reference palette",
        "Increase letter-spacing (tracking-wide) to match reference typography",
        "Add more vertical padding (py-6 → py-8) to match reference spacing"
    ]
}
```

Be specific - reference the exact Tailwind classes or CSS values to change.
""")

        return "\n".join(parts)

    def _get_reference_adherence_system_prompt(self) -> str:
        """System prompt for reference adherence evaluation."""
        return """You are an expert visual design analyst specializing in:
- Color theory and palette matching
- Typography systems and hierarchies
- Spacing and layout consistency
- Visual design fidelity assessment

Your role is to:
1. Compare generated design against reference design tokens
2. Score adherence on a 1-10 scale for each category
3. Identify specific deviations from reference
4. Suggest Tailwind CSS classes to improve adherence

Scoring guidance:
- 9-10: Nearly identical to reference
- 7-8: Strong adherence with minor deviations
- 5-6: Moderate adherence, noticeable differences
- 3-4: Weak adherence, significant differences
- 1-2: Poor adherence, looks like different design

IMPORTANT: Output ONLY valid JSON. No markdown, no explanation."""

    def _parse_reference_adherence_response(
        self, response: str
    ) -> tuple[float, list[str]]:
        """Parse reference adherence response into score and improvements."""
        # Try to extract JSON from code blocks
        json_pattern = r"```(?:json)?\s*(\{[\s\S]*?\})\s*```"
        matches = re.findall(json_pattern, response)

        parsed_data = None
        if matches:
            for match in matches:
                try:
                    parsed_data = json.loads(match)
                    break
                except json.JSONDecodeError:
                    continue

        # Try raw JSON if no code blocks
        if not parsed_data:
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    parsed_data = json.loads(response[start:end])
            except json.JSONDecodeError:
                pass

        # Parse or use defaults
        if parsed_data:
            # Get overall score (or calculate from individual scores)
            if "overall" in parsed_data:
                overall = float(parsed_data["overall"])
            elif "scores" in parsed_data:
                scores = parsed_data["scores"]
                overall = (
                    float(scores.get("color_match", 5.0)) +
                    float(scores.get("typography_match", 5.0)) +
                    float(scores.get("spacing_match", 5.0)) +
                    float(scores.get("aesthetic_match", 5.0))
                ) / 4.0
            else:
                overall = 5.0

            improvements = parsed_data.get("improvements", [])
        else:
            logger.warning("[Critic] Could not parse reference adherence response")
            overall = 5.0
            improvements = ["Unable to parse evaluation - manual review recommended"]

        return overall, improvements

    def quick_evaluate(self, html: str, css: str = "") -> CriticScores:
        """
        Quick heuristic-based evaluation without API call.

        Useful for initial filtering before full evaluation.
        """
        scores = CriticScores()

        # Layout scoring heuristics
        if "flex" in html or "grid" in html:
            scores.layout += 1.0
        if "gap-" in html:
            scores.layout += 0.5
        if any(bp in html for bp in ["sm:", "md:", "lg:", "xl:"]):
            scores.layout += 1.5  # Responsive

        # Typography scoring
        if "font-" in html:
            scores.typography += 0.5
        if "text-" in html:
            scores.typography += 0.5
        if "leading-" in html:
            scores.typography += 0.5

        # Color scoring
        if "bg-" in html and "text-" in html:
            scores.color += 1.0
        if "dark:" in html:
            scores.color += 1.5  # Dark mode support

        # Interaction scoring
        if "hover:" in html:
            scores.interaction += 1.0
        if "transition" in html or "transition" in css:
            scores.interaction += 1.0
        if "@keyframes" in css:
            scores.interaction += 0.5

        # Accessibility scoring
        if 'aria-' in html:
            scores.accessibility += 1.0
        if 'role=' in html:
            scores.accessibility += 0.5
        semantic_tags = ["<nav", "<main", "<section", "<article", "<aside", "<footer", "<header"]
        if any(tag in html for tag in semantic_tags):
            scores.accessibility += 1.5

        return scores

    # === CORPORATE QUALITY ENHANCEMENT ===

    async def evaluate_corporate_quality(
        self,
        html: str,
        css: str,
        industry: str = "consulting",
        formality: str = "semi-formal",
        context: Optional["AgentContext"] = None,
    ) -> tuple[CriticScores, list[str], dict]:
        """
        Evaluate design against corporate/professional standards.

        This method extends the standard evaluation with corporate-specific
        dimensions for enterprise-grade design quality.

        Args:
            html: HTML content to evaluate
            css: CSS content to evaluate
            industry: Industry context (finance, healthcare, legal, tech, manufacturing, consulting)
            formality: Formality level (formal, semi-formal, approachable)
            context: Optional context for thought signature handling

        Returns:
            Tuple of:
            - CriticScores: Standard 5-dimension scores
            - list[str]: Improvement suggestions
            - dict: Corporate-specific metrics including:
                - brand_consistency: 0-10 score
                - industry_appropriateness: 0-10 score
                - formality_adherence: 0-10 score
                - professional_validator_result: Full validation result
        """
        import time

        start_time = time.time()

        # Step 1: Run standard evaluation
        scores, improvements = await self.evaluate(html, css, "", context)

        # Step 2: Run ProfessionalValidator
        from gemini_mcp.validation.professional_validator import (
            ProfessionalValidator,
            validate_professional,
        )

        pro_result = validate_professional(
            html=html,
            css=css,
            formality=formality,
            industry=industry,
            accessibility_level="AAA" if formality == "formal" else "AA",
        )

        # Step 3: Build corporate evaluation prompt
        corporate_prompt = self._build_corporate_evaluation_prompt(
            html, css, industry, formality, pro_result
        )

        try:
            # Call Gemini API for corporate-specific evaluation
            response = await self.client.generate_text(
                prompt=corporate_prompt,
                system_instruction=self._get_corporate_system_prompt(industry, formality),
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
                thinking_level=self.config.thinking_level,
            )

            response_text = response.get("text", "")

            # Add thought signature to context
            if context and response.get("thought_signature"):
                context.add_thought_signature(response["thought_signature"])

            # Parse corporate metrics
            corporate_metrics = self._parse_corporate_response(
                response_text, pro_result
            )

            # Add professional validator issues to improvements
            for issue in pro_result.issues:
                if issue.message not in improvements:
                    improvements.append(f"[{formality.upper()}] {issue.message}")

            # Add recommendations
            for rec in pro_result.recommendations[:3]:  # Limit to top 3
                improvements.append(f"[REC] {rec}")

            logger.info(
                f"[Critic] Corporate evaluation complete. "
                f"Industry: {industry}, Formality: {formality}, "
                f"Pro Score: {pro_result.overall_score:.1f}/100, "
                f"Time: {(time.time() - start_time) * 1000:.0f}ms"
            )

            return scores, improvements, corporate_metrics

        except Exception as e:
            logger.error(f"[Critic] Corporate evaluation failed: {e}")
            # Return basic metrics from ProfessionalValidator
            return scores, improvements, {
                "brand_consistency": 5.0,
                "industry_appropriateness": 5.0,
                "formality_adherence": 5.0,
                "professional_validator_result": pro_result.to_dict(),
                "error": str(e),
            }

    def _build_corporate_evaluation_prompt(
        self,
        html: str,
        css: str,
        industry: str,
        formality: str,
        pro_result,
    ) -> str:
        """Build prompt for corporate quality evaluation."""
        # Truncate if too long
        html_preview = html[:4000] if len(html) > 4000 else html
        css_preview = css[:2000] if len(css) > 2000 else css

        return f"""## CORPORATE DESIGN QUALITY EVALUATION

### Context
- **Industry**: {industry}
- **Formality Level**: {formality}
- **Professional Validator Score**: {pro_result.overall_score:.1f}/100
- **Issues Found**: {pro_result.error_count} errors, {pro_result.warning_count} warnings

### Design to Evaluate

**HTML:**
```html
{html_preview}
```

**CSS:**
```css
{css_preview}
```

### Professional Validator Dimension Scores
{chr(10).join(f'- {name}: {dim.score:.0f}/100' for name, dim in pro_result.dimension_scores.items())}

### Evaluation Criteria

Rate each dimension 1-10:

1. **Brand Consistency** (Does design feel unified and professional?)
   - Color palette cohesion
   - Typography consistency
   - Visual language uniformity

2. **Industry Appropriateness** (Does design fit {industry} expectations?)
   - Industry-standard patterns
   - Trust indicators (if needed)
   - Appropriate imagery/iconography choices

3. **Formality Adherence** (Does design match {formality} level?)
   - Animation appropriateness
   - Color vibrancy level
   - Typography weight/style
   - Overall professional tone

### Output Format

Return ONLY valid JSON:
```json
{{
    "brand_consistency": 8.0,
    "industry_appropriateness": 7.5,
    "formality_adherence": 8.0,
    "corporate_improvements": [
        "Specific improvement 1",
        "Specific improvement 2"
    ]
}}
```
"""

    def _get_corporate_system_prompt(self, industry: str, formality: str) -> str:
        """System prompt for corporate evaluation."""
        industry_context = {
            "finance": "banks, insurance, investment firms - trust, security, precision",
            "healthcare": "hospitals, medical practices - calm, caring, accessible",
            "legal": "law firms, legal services - authoritative, prestigious, traditional",
            "tech": "software companies, SaaS - innovative, clean, modern",
            "manufacturing": "industrial, B2B - reliable, practical, efficient",
            "consulting": "advisory firms, agencies - professional, knowledgeable, refined",
        }

        formality_context = {
            "formal": "Fortune 500, conservative, serif typography, minimal animation, muted colors",
            "semi-formal": "Professional but approachable, balanced design, moderate animation",
            "approachable": "Startup-friendly, energetic, allows more creative expression",
        }

        return f"""You are an expert corporate design evaluator specializing in:
- Enterprise UI/UX standards
- Industry-specific design patterns
- Professional brand consistency
- Corporate visual identity

Context for this evaluation:
- Industry: {industry} ({industry_context.get(industry, 'professional sector')})
- Formality: {formality} ({formality_context.get(formality, 'professional standards')})

Evaluate the design against these corporate standards.
Be specific in your feedback - reference exact CSS classes or HTML elements.
IMPORTANT: Output ONLY valid JSON. No markdown formatting, no explanation."""

    def _parse_corporate_response(
        self, response: str, pro_result
    ) -> dict:
        """Parse corporate evaluation response."""
        # Try to extract JSON
        json_pattern = r"```(?:json)?\s*(\{[\s\S]*?\})\s*```"
        matches = re.findall(json_pattern, response)

        parsed_data = None
        if matches:
            for match in matches:
                try:
                    parsed_data = json.loads(match)
                    break
                except json.JSONDecodeError:
                    continue

        # Try raw JSON if no code blocks
        if not parsed_data:
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    parsed_data = json.loads(response[start:end])
            except json.JSONDecodeError:
                pass

        # Build result
        if parsed_data:
            result = {
                "brand_consistency": float(parsed_data.get("brand_consistency", 5.0)),
                "industry_appropriateness": float(parsed_data.get("industry_appropriateness", 5.0)),
                "formality_adherence": float(parsed_data.get("formality_adherence", 5.0)),
                "corporate_improvements": parsed_data.get("corporate_improvements", []),
                "professional_validator_result": pro_result.to_dict(),
            }
        else:
            logger.warning("[Critic] Could not parse corporate response")
            result = {
                "brand_consistency": 5.0,
                "industry_appropriateness": 5.0,
                "formality_adherence": 5.0,
                "corporate_improvements": [],
                "professional_validator_result": pro_result.to_dict(),
            }

        # Calculate aggregate corporate score
        result["corporate_score"] = (
            result["brand_consistency"] +
            result["industry_appropriateness"] +
            result["formality_adherence"]
        ) / 3.0

        # Is it corporate-grade?
        result["is_corporate_grade"] = (
            result["corporate_score"] >= 7.0 and
            pro_result.is_professional
        )

        return result
