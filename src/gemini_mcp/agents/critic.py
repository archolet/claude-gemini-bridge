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
from typing import TYPE_CHECKING, Any, Optional

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
            thinking_budget=4096,
            temperature=0.5,  # Balanced for analysis
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

            # Call Gemini API
            response = await self.client.generate_text(
                prompt=prompt,
                system_instruction=self.get_system_prompt(),
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
            )

            # Parse response
            parsed_data = self._parse_response(response)
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

    def quick_analyze(self, html: str, modification: str) -> dict:
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
