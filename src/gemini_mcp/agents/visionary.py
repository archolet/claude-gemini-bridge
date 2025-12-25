"""
The Visionary - Vision API Specialist

The Visionary is responsible for:
1. Analyzing reference images using Gemini Vision API
2. Extracting design tokens from visual references
3. Identifying UI patterns and components
4. Providing style guidance to downstream agents

The Visionary NEVER generates HTML/CSS/JS - only visual analysis and design tokens.
"""

from __future__ import annotations

import base64
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from gemini_mcp.agents.base import AgentConfig, AgentResult, AgentRole, BaseAgent
from gemini_mcp.prompts import VISIONARY_SYSTEM_PROMPT

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient
    from gemini_mcp.orchestration.context import AgentContext

logger = logging.getLogger(__name__)


@dataclass
class VisualAnalysis:
    """Analysis results from visual reference."""

    design_tokens: dict = field(default_factory=dict)
    detected_components: list[str] = field(default_factory=list)
    layout_patterns: list[str] = field(default_factory=list)
    color_palette: list[str] = field(default_factory=list)
    typography_hints: dict = field(default_factory=dict)
    mood: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "design_tokens": self.design_tokens,
            "detected_components": self.detected_components,
            "layout_patterns": self.layout_patterns,
            "color_palette": self.color_palette,
            "typography_hints": self.typography_hints,
            "mood": self.mood,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VisualAnalysis":
        return cls(
            design_tokens=data.get("design_tokens", {}),
            detected_components=data.get("detected_components", []),
            layout_patterns=data.get("layout_patterns", []),
            color_palette=data.get("color_palette", []),
            typography_hints=data.get("typography_hints", {}),
            mood=data.get("mood", ""),
            confidence=data.get("confidence", 0.0),
        )


class VisionaryAgent(BaseAgent):
    """
    The Visionary - Vision API Specialist.

    Analyzes reference images to extract design tokens and visual patterns.
    Uses Gemini Vision API for multimodal understanding.
    """

    role = AgentRole.VISIONARY

    def __init__(
        self,
        client: "GeminiClient",
        config: Optional[AgentConfig] = None,
    ):
        """
        Initialize The Visionary.

        Args:
            client: GeminiClient for API calls (supports vision)
            config: Optional custom configuration
        """
        super().__init__(config)
        self.client = client

    @classmethod
    def _default_config(cls) -> AgentConfig:
        """Visionary-specific default configuration."""
        return AgentConfig(
            model="gemini-3-pro-preview",  # Pro for vision capabilities
            thinking_level="high",  # Vision analysis is complex
            temperature=1.0,  # Gemini 3 optimized
            max_output_tokens=4096,
            strict_mode=False,  # Advisory output
            auto_fix=False,
        )

    def get_system_prompt(self) -> str:
        """Return The Visionary's system prompt."""
        return VISIONARY_SYSTEM_PROMPT

    async def execute(self, context: "AgentContext") -> AgentResult:
        """
        Analyze a reference image and extract design tokens.

        Args:
            context: Pipeline context with image_path

        Returns:
            AgentResult with VisualAnalysis
        """
        import time

        start_time = time.time()

        try:
            # Get image path from context
            image_path = getattr(context, "image_path", None)
            if not image_path:
                return AgentResult(
                    success=False,
                    output="",
                    agent_role=self.role,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    errors=["No image_path provided in context"],
                )

            # Load and encode image
            image_data = self._load_image(image_path)
            if not image_data:
                return AgentResult(
                    success=False,
                    output="",
                    agent_role=self.role,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    errors=[f"Failed to load image: {image_path}"],
                )

            # Build the prompt
            prompt = self._build_vision_prompt(context)

            # Call Gemini Vision API (now includes thought signature handling)
            response = await self._call_vision_api(prompt, image_data, context)

            # Parse response
            parsed_data = self._parse_response(response)
            visual_analysis = VisualAnalysis.from_dict(parsed_data)

            # Create result
            result = AgentResult(
                success=True,
                output=json.dumps(visual_analysis.to_dict(), indent=2, ensure_ascii=False),
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
            )

            # Attach analysis to metadata
            result.metadata = {
                "visual_analysis": visual_analysis.to_dict(),
                "image_path": image_path,
                "confidence": visual_analysis.confidence,
            }

            logger.info(
                f"[Visionary] Analysis complete. Mood: {visual_analysis.mood}, "
                f"Components: {len(visual_analysis.detected_components)}, "
                f"Confidence: {visual_analysis.confidence:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"[Visionary] Execution failed: {e}")
            return AgentResult(
                success=False,
                output="",
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                errors=[str(e)],
            )

    def _load_image(self, image_path: str) -> Optional[dict]:
        """Load and encode image for Vision API."""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.error(f"[Visionary] Image not found: {image_path}")
                return None

            # Read file
            with open(path, "rb") as f:
                image_bytes = f.read()

            # Determine MIME type
            suffix = path.suffix.lower()
            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif",
            }
            mime_type = mime_types.get(suffix, "image/png")

            # Encode to base64
            image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")

            return {
                "data": image_base64,
                "mime_type": mime_type,
            }

        except Exception as e:
            logger.error(f"[Visionary] Failed to load image: {e}")
            return None

    async def _call_vision_api(
        self, prompt: str, image_data: dict, context: "AgentContext"
    ) -> str:
        """Call Gemini Vision API with image and prompt.

        Returns the response text. Thought signatures are added to context.
        """
        try:
            # Use client's vision method if available
            if hasattr(self.client, "generate_with_image"):
                response = await self.client.generate_with_image(
                    prompt=prompt,
                    image_data=image_data["data"],
                    mime_type=image_data["mime_type"],
                    system_instruction=self.get_system_prompt(),
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                )
                # Handle both string and dict responses
                if isinstance(response, dict):
                    # === GEMINI 3: Add thought signature to context ===
                    if response.get("thought_signature"):
                        context.add_thought_signature(response["thought_signature"])
                    return response.get("text", "")
                return response
            else:
                # Fallback: Use standard generate with image in prompt
                # Note: This requires client to handle multimodal content
                response = await self.client.generate_text(
                    prompt=f"[IMAGE ANALYSIS REQUEST]\n\n{prompt}",
                    system_instruction=self.get_system_prompt(),
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                    thinking_level=self.config.thinking_level,
                )

                # === GEMINI 3: Extract text and thought signature ===
                response_text = response.get("text", "")
                if response.get("thought_signature"):
                    context.add_thought_signature(response["thought_signature"])

                return response_text

        except Exception as e:
            logger.error(f"[Visionary] Vision API call failed: {e}")
            raise

    def _build_vision_prompt(self, context: "AgentContext") -> str:
        """Build the prompt for visual analysis."""
        parts = ["## VISUAL ANALYSIS REQUEST"]

        # User instructions
        if hasattr(context, "instructions") and context.instructions:
            parts.append(f"### User Instructions\n{context.instructions}")

        # Component type hint
        if context.component_type:
            parts.append(f"### Target Component\n{context.component_type}")

        # Context
        if context.user_requirements:
            parts.append(f"### Context\n{context.user_requirements}")

        # Task
        parts.append("""
### Task
Analyze this image and extract:
1. Design tokens (colors, typography, spacing, borders)
2. Detected UI components
3. Layout patterns
4. Overall mood/aesthetic
5. Tailwind class suggestions

Output JSON format as specified in your system prompt.
""")

        return "\n\n".join(parts)

    def _parse_response(self, response: str) -> dict:
        """Parse JSON response from Vision API."""
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

        # Fallback: return basic structure
        logger.warning("[Visionary] Could not parse JSON response")
        return {
            "design_tokens": {},
            "detected_components": [],
            "layout_patterns": [],
            "color_palette": [],
            "typography_hints": {},
            "mood": "unknown",
            "confidence": 0.5,
        }

    def validate_output(self, output: str) -> tuple[bool, list[str]]:
        """Validate Visionary output (JSON analysis)."""
        issues = []

        if not output or not output.strip():
            return True, []

        try:
            data = json.loads(output)
            if "design_tokens" not in data:
                issues.append("Missing 'design_tokens' field")
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON: {e}")

        return len(issues) == 0, issues

    def auto_fix_output(self, output: str) -> str:
        """Visionary output doesn't need auto-fix."""
        return output

    def quick_analyze_colors(self, image_path: str) -> list[str]:
        """
        Quick color extraction without API call.

        Uses basic image processing to extract dominant colors.
        This is a fallback when API call is not desired.
        """
        # This would require PIL/Pillow for actual implementation
        # For now, return empty list as placeholder
        logger.warning("[Visionary] quick_analyze_colors requires PIL - returning empty")
        return []
