"""
AgentContext - Shared Context for Multi-Agent Pipelines

This module defines the context object that is passed between agents
in a pipeline. It contains:
- User requirements (component type, theme, content)
- Design DNA (extracted design tokens for consistency)
- Pipeline state (current step, errors, checkpoints)
- Previous agent outputs
- Performance hints (token budget, quality target)

Token Optimization:
    Instead of passing full HTML/CSS between agents, we use compressed
    metadata (IDs, class lists, CSS variables) to reduce token usage
    by 30-50%.
"""

from __future__ import annotations

import json
import uuid
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional


class QualityTarget(Enum):
    """Quality target affects validation strictness and retry behavior."""

    DRAFT = "draft"  # Lenient validation, fewer retries
    PRODUCTION = "production"  # Strict validation, more retries


class InteractionType(Enum):
    """Types of interactions that Physicist can implement."""

    PARALLAX = "parallax"  # Scroll-based depth effect
    MAGNETIC = "magnetic"  # Cursor attraction effect
    REVEAL = "reveal"  # Scroll-triggered reveal animation
    TILT = "tilt"  # 3D tilt on hover
    GLOW = "glow"  # Dynamic glow effect
    MORPH = "morph"  # Shape morphing animation
    FLOAT = "float"  # Floating/bobbing animation
    RIPPLE = "ripple"  # Click ripple effect


class TriggerType(Enum):
    """Event triggers for interactions."""

    SCROLL = "scroll"  # Scroll position/velocity
    HOVER = "hover"  # Mouse hover
    CLICK = "click"  # Mouse click
    LOAD = "load"  # Page load
    INTERSECT = "intersect"  # IntersectionObserver


@dataclass
class InteractionSpec:
    """
    Specification for element interactions (Architect → Physicist protocol).

    This dataclass represents the data-* attributes that Architect adds to HTML
    elements. Physicist reads these specs to generate appropriate JavaScript.

    Example HTML:
        <button id="cta-btn"
                data-interaction="magnetic"
                data-trigger="hover"
                data-intensity="0.8">
          Başla
        </button>

    Corresponding InteractionSpec:
        InteractionSpec(
            element_id="cta-btn",
            interaction_type="magnetic",
            trigger="hover",
            intensity=0.8
        )
    """

    element_id: str  # The ID of the element
    interaction_type: str  # parallax, magnetic, reveal, tilt, glow, morph, float, ripple
    trigger: str  # scroll, hover, click, load, intersect
    intensity: float = 0.5  # 0.1-1.0, effect strength
    delay: int = 0  # milliseconds before effect starts
    group: str = ""  # synchronization group for coordinated animations
    duration: int = 300  # milliseconds for animation duration
    easing: str = "ease-out"  # CSS easing function

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "element_id": self.element_id,
            "interaction_type": self.interaction_type,
            "trigger": self.trigger,
            "intensity": self.intensity,
            "delay": self.delay,
            "group": self.group,
            "duration": self.duration,
            "easing": self.easing,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InteractionSpec":
        """Create from dictionary."""
        return cls(
            element_id=data.get("element_id", ""),
            interaction_type=data.get("interaction_type", "reveal"),
            trigger=data.get("trigger", "scroll"),
            intensity=data.get("intensity", 0.5),
            delay=data.get("delay", 0),
            group=data.get("group", ""),
            duration=data.get("duration", 300),
            easing=data.get("easing", "ease-out"),
        )

    @classmethod
    def from_data_attributes(
        cls, element_id: str, attrs: dict[str, str]
    ) -> "InteractionSpec":
        """
        Create from HTML data-* attributes.

        Args:
            element_id: The element's ID
            attrs: Dictionary of data-* attributes (without 'data-' prefix)
                   e.g., {"interaction": "parallax", "trigger": "scroll"}
        """
        return cls(
            element_id=element_id,
            interaction_type=attrs.get("interaction", "reveal"),
            trigger=attrs.get("trigger", "scroll"),
            intensity=float(attrs.get("intensity", "0.5")),
            delay=int(attrs.get("delay", "0")),
            group=attrs.get("group", ""),
            duration=int(attrs.get("duration", "300")),
            easing=attrs.get("easing", "ease-out"),
        )


@dataclass
class DesignDNA:
    """
    Extracted design tokens that maintain consistency across agents.

    DNA is extracted by the Strategist agent (or from previous_html)
    and passed to all subsequent agents to ensure visual coherence.
    """

    # Color palette
    colors: dict[str, str] = field(default_factory=dict)
    # e.g., {"primary": "#E11D48", "accent": "#06B6D4", "background": "#0F172A"}

    # Typography settings
    typography: dict[str, str] = field(default_factory=dict)
    # e.g., {"heading": "font-bold", "body": "font-normal", "scale": "lg"}

    # Spacing preferences
    spacing: dict[str, str] = field(default_factory=dict)
    # e.g., {"density": "compact", "section_gap": "py-24"}

    # Border styles
    borders: dict[str, str] = field(default_factory=dict)
    # e.g., {"radius": "rounded-xl", "width": "border-2", "style": "border-solid"}

    # Animation style
    animation: dict[str, str] = field(default_factory=dict)
    # e.g., {"style": "smooth", "duration": "300ms", "easing": "ease-out"}

    # Overall mood/aesthetic
    mood: str = ""
    # e.g., "cyberpunk-futuristic", "minimal-professional", "playful-colorful"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "colors": self.colors,
            "typography": self.typography,
            "spacing": self.spacing,
            "borders": self.borders,
            "animation": self.animation,
            "mood": self.mood,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DesignDNA":
        """Create from dictionary."""
        return cls(
            colors=data.get("colors", {}),
            typography=data.get("typography", {}),
            spacing=data.get("spacing", {}),
            borders=data.get("borders", {}),
            animation=data.get("animation", {}),
            mood=data.get("mood", ""),
        )

    def merge_with(self, other: "DesignDNA") -> "DesignDNA":
        """Merge with another DNA, preferring other's values."""
        return DesignDNA(
            colors={**self.colors, **other.colors},
            typography={**self.typography, **other.typography},
            spacing={**self.spacing, **other.spacing},
            borders={**self.borders, **other.borders},
            animation={**self.animation, **other.animation},
            mood=other.mood or self.mood,
        )


@dataclass
class CompressedOutput:
    """
    Compressed representation of agent output for token optimization.

    Instead of passing full HTML to subsequent agents, we extract
    only the metadata they need.
    """

    # Element IDs for JS targeting
    element_ids: list[str] = field(default_factory=list)

    # CSS variable names defined
    css_variables: list[str] = field(default_factory=list)

    # Tailwind classes used (for style reference)
    tailwind_classes: list[str] = field(default_factory=list)

    # DOM structure outline (simplified)
    structure_summary: str = ""

    # Section markers if applicable
    section_markers: list[str] = field(default_factory=list)

    # === PHASE 7: Structural Map ===
    # Interaction specifications extracted from data-* attributes
    # Maps element_id → InteractionSpec
    interaction_map: dict[str, "InteractionSpec"] = field(default_factory=dict)

    def get_interactions_by_type(
        self, interaction_type: str
    ) -> list["InteractionSpec"]:
        """Get all interactions of a specific type."""
        return [
            spec
            for spec in self.interaction_map.values()
            if spec.interaction_type == interaction_type
        ]

    def get_interactions_by_trigger(self, trigger: str) -> list["InteractionSpec"]:
        """Get all interactions with a specific trigger."""
        return [
            spec for spec in self.interaction_map.values() if spec.trigger == trigger
        ]

    def get_interactions_by_group(self, group: str) -> list["InteractionSpec"]:
        """Get all interactions in a specific group."""
        return [
            spec for spec in self.interaction_map.values() if spec.group == group
        ]

    def has_interactions(self) -> bool:
        """Check if there are any interactions defined."""
        return len(self.interaction_map) > 0


@dataclass
class AgentContext:
    """
    Shared context passed between agents in a pipeline.

    This is the main data structure that flows through the pipeline,
    accumulating outputs from each agent while maintaining state.
    """

    # === User Requirements ===
    component_type: str = ""
    theme: str = "modern-minimal"
    content_structure: dict[str, Any] = field(default_factory=dict)  # Content JSON
    content_language: str = "tr"
    user_requirements: str = ""  # Usage context from user
    project_context: str = ""  # Project-specific context

    # === Style Guide (from theme factories) ===
    style_guide: dict[str, Any] = field(default_factory=dict)

    # === Pipeline Configuration ===
    pipeline_type: str = ""  # COMPONENT, PAGE, SECTION, etc.

    # === Design DNA ===
    design_dna: Optional[DesignDNA] = None

    # === Previous Agent Outputs ===
    # Full outputs (kept for final assembly)
    html_output: str = ""
    css_output: str = ""
    js_output: str = ""

    # Compressed metadata for token optimization
    compressed: Optional[CompressedOutput] = None

    # Raw previous output (for agents that need full context)
    previous_output: str = ""

    # === Pipeline State ===
    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    step_index: int = 0
    total_steps: int = 0
    current_agent: str = ""

    # === Error Handling ===
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    correction_feedback: str = ""  # Syntax validation feedback
    attempt: int = 0

    # === Refiner Loop (Gemini 3 Quality Loop) ===
    # critic_feedback is separate from correction_feedback:
    # - correction_feedback: Syntax/validation errors (agent.validate_output failed)
    # - critic_feedback: Design quality improvements (CriticScores < threshold)
    critic_feedback: list[str] = field(default_factory=list)
    refiner_iteration: int = 0  # Current iteration in refiner loop

    # === Performance ===
    quality_target: QualityTarget = QualityTarget.PRODUCTION
    token_budget: int = 32768
    skip_agents: list[str] = field(default_factory=list)

    # === Timestamps ===
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # === Gemini 3 Thought Signatures (REQUIRED for multi-turn) ===
    # Thought signatures maintain reasoning continuity across API calls.
    # Without them, Gemini 3 may return 4xx validation errors.
    thought_signatures: list[str] = field(default_factory=list)

    # === Section-specific (for design_page, replace_section_in_page) ===
    sections: list[dict[str, Any]] = field(default_factory=list)
    target_section: str = ""  # For replace_section_in_page
    current_section_index: int = -1  # For parallel section generation
    current_section_type: str = ""  # Current section type being generated

    # === Reference-specific (for design_from_reference) ===
    reference_image_path: str = ""
    reference_analysis: str = ""

    # === Refinement-specific (for refine_frontend) ===
    modification_request: str = ""  # User's modification/refinement request
    previous_html: str = ""  # Original HTML to refine

    def copy(self) -> "AgentContext":
        """Create a deep copy of this context."""
        return deepcopy(self)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()

    def add_error(self, error: str) -> None:
        """Add an error to the context."""
        self.errors.append(error)
        self.update_timestamp()

    def add_warning(self, warning: str) -> None:
        """Add a warning to the context."""
        self.warnings.append(warning)
        self.update_timestamp()

    def add_thought_signature(self, signature: str) -> None:
        """
        Add a thought signature from Gemini 3 response.

        Thought signatures are REQUIRED for multi-turn conversations
        with Gemini 3. They maintain reasoning continuity and must be
        passed back in subsequent requests.

        Args:
            signature: The thought signature string from API response
        """
        if signature and signature.strip():
            self.thought_signatures.append(signature.strip())
            self.update_timestamp()

    def get_latest_signatures(self, count: int = 3) -> list[str]:
        """
        Get the most recent thought signatures.

        Args:
            count: Number of signatures to return (default 3)

        Returns:
            List of most recent signatures (newest last)
        """
        if not self.thought_signatures:
            return []
        return self.thought_signatures[-count:]

    def get_signatures_for_request(self) -> str:
        """
        Format thought signatures for inclusion in API request.

        Returns a formatted string suitable for system prompt injection.
        """
        signatures = self.get_latest_signatures()
        if not signatures:
            return ""

        formatted = "\n".join(f"[{i+1}] {sig}" for i, sig in enumerate(signatures))
        return f"## Previous Thought Signatures\n{formatted}"

    def set_output(self, agent_type: str, output: str) -> None:
        """Set the output for a specific agent type."""
        if agent_type == "architect":
            self.html_output = output
        elif agent_type == "alchemist":
            self.css_output = output
        elif agent_type == "physicist":
            self.js_output = output

        self.previous_output = output
        self.update_timestamp()

    def compress_current_output(self, output: str, output_type: str) -> None:
        """
        Compress the current output for token-efficient passing.

        Args:
            output: The full output string
            output_type: One of 'html', 'css', 'js'
        """
        import re

        if self.compressed is None:
            self.compressed = CompressedOutput()

        if output_type == "html":
            # Extract IDs
            id_pattern = r'id=["\']([^"\']+)["\']'
            self.compressed.element_ids = re.findall(id_pattern, output)

            # Extract Tailwind classes
            class_pattern = r'class=["\']([^"\']+)["\']'
            matches = re.findall(class_pattern, output)
            classes = []
            for match in matches:
                classes.extend(match.split())
            self.compressed.tailwind_classes = list(set(classes))

            # Extract section markers
            marker_pattern = r"<!-- SECTION: (\w+) -->"
            self.compressed.section_markers = re.findall(marker_pattern, output)

            # Create structure summary (first 500 chars of cleaned HTML)
            summary = re.sub(r"<[^>]+>", " ", output)
            summary = " ".join(summary.split())[:500]
            self.compressed.structure_summary = summary

            # === PHASE 7: Extract Structural Map (data-* attributes) ===
            self._extract_interaction_map(output)

        elif output_type == "css":
            # Extract CSS variables
            var_pattern = r"--([a-zA-Z0-9-]+)"
            self.compressed.css_variables = list(set(re.findall(var_pattern, output)))

    def _extract_interaction_map(self, html: str) -> None:
        """
        Extract interaction specifications from HTML data-* attributes.

        Scans HTML for elements with data-interaction attribute and builds
        an interaction_map for Physicist to consume.

        Supported attributes:
            - data-interaction: parallax, magnetic, reveal, tilt, glow, morph
            - data-trigger: scroll, hover, click, load, intersect
            - data-intensity: 0.1-1.0
            - data-delay: milliseconds
            - data-group: synchronization group
            - data-duration: milliseconds
            - data-easing: CSS easing function
        """
        import re

        if self.compressed is None:
            self.compressed = CompressedOutput()

        # Pattern to match elements with both id and data-interaction
        # This regex captures the entire opening tag
        element_pattern = r"<(\w+)([^>]*?)>"

        for match in re.finditer(element_pattern, html):
            tag_name = match.group(1)
            attributes_str = match.group(2)

            # Skip if no data-interaction attribute
            if "data-interaction" not in attributes_str:
                continue

            # Extract element ID
            id_match = re.search(r'id=["\']([^"\']+)["\']', attributes_str)
            if not id_match:
                continue  # Skip elements without ID

            element_id = id_match.group(1)

            # Extract all data-* attributes
            data_attrs = {}
            data_pattern = r'data-(\w+)=["\']([^"\']+)["\']'
            for attr_match in re.finditer(data_pattern, attributes_str):
                attr_name = attr_match.group(1)
                attr_value = attr_match.group(2)
                data_attrs[attr_name] = attr_value

            # Create InteractionSpec from data attributes
            if "interaction" in data_attrs:
                spec = InteractionSpec.from_data_attributes(element_id, data_attrs)
                self.compressed.interaction_map[element_id] = spec

    def get_interaction_summary(self) -> dict[str, list[str]]:
        """
        Get a summary of interactions grouped by type.

        Returns:
            Dict mapping interaction types to lists of element IDs
            e.g., {"parallax": ["hero-bg", "section-2"], "magnetic": ["cta-btn"]}
        """
        if not self.compressed or not self.compressed.interaction_map:
            return {}

        summary: dict[str, list[str]] = {}
        for element_id, spec in self.compressed.interaction_map.items():
            itype = spec.interaction_type
            if itype not in summary:
                summary[itype] = []
            summary[itype].append(element_id)

        return summary

    def get_design_dna_dict(self) -> dict[str, Any]:
        """Get design DNA as dictionary for prompt injection."""
        if self.design_dna:
            return self.design_dna.to_dict()
        return {}

    def should_skip_agent(self, agent_name: str) -> bool:
        """Check if an agent should be skipped based on configuration."""
        return agent_name in self.skip_agents

    def get_combined_output(self) -> str:
        """
        Get the combined HTML with embedded CSS and JS.

        This is used for the final MCP tool response.
        """
        parts = []

        if self.css_output:
            parts.append(f"<style>\n{self.css_output}\n</style>")

        parts.append(self.html_output)

        if self.js_output:
            parts.append(f"<script>\n{self.js_output}\n</script>")

        return "\n\n".join(parts)

    def serialize(self) -> str:
        """Serialize context to JSON string for checkpointing."""
        data = {
            # User requirements
            "component_type": self.component_type,
            "theme": self.theme,
            "content_structure": self.content_structure,
            "content_language": self.content_language,
            "user_requirements": self.user_requirements,
            "project_context": self.project_context,
            # Style guide and pipeline
            "style_guide": self.style_guide,
            "pipeline_type": self.pipeline_type,
            # Design DNA
            "design_dna": self.design_dna.to_dict() if self.design_dna else None,
            # Agent outputs
            "html_output": self.html_output,
            "css_output": self.css_output,
            "js_output": self.js_output,
            "previous_output": self.previous_output,
            # Pipeline state
            "pipeline_id": self.pipeline_id,
            "step_index": self.step_index,
            "total_steps": self.total_steps,
            "current_agent": self.current_agent,
            # Error handling
            "errors": self.errors,
            "warnings": self.warnings,
            # Performance
            "quality_target": self.quality_target.value,
            "token_budget": self.token_budget,
            "skip_agents": self.skip_agents,
            # Section-specific
            "sections": self.sections,
            "target_section": self.target_section,
            "current_section_index": self.current_section_index,
            "current_section_type": self.current_section_type,
            # Refinement-specific
            "modification_request": self.modification_request,
            "previous_html": self.previous_html,
            # Gemini 3 thought signatures
            "thought_signatures": self.thought_signatures,
        }
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def deserialize(cls, data_str: str) -> "AgentContext":
        """Deserialize context from JSON string."""
        data = json.loads(data_str)

        context = cls(
            # User requirements
            component_type=data.get("component_type", ""),
            theme=data.get("theme", "modern-minimal"),
            content_structure=data.get("content_structure", {}),
            content_language=data.get("content_language", "tr"),
            user_requirements=data.get("user_requirements", ""),
            project_context=data.get("project_context", ""),
            # Style guide and pipeline
            style_guide=data.get("style_guide", {}),
            pipeline_type=data.get("pipeline_type", ""),
            # Agent outputs
            html_output=data.get("html_output", ""),
            css_output=data.get("css_output", ""),
            js_output=data.get("js_output", ""),
            previous_output=data.get("previous_output", ""),
            # Pipeline state
            pipeline_id=data.get("pipeline_id", ""),
            step_index=data.get("step_index", 0),
            total_steps=data.get("total_steps", 0),
            current_agent=data.get("current_agent", ""),
            # Error handling
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            # Performance
            quality_target=QualityTarget(data.get("quality_target", "production")),
            token_budget=data.get("token_budget", 32768),
            skip_agents=data.get("skip_agents", []),
            # Section-specific
            sections=data.get("sections", []),
            target_section=data.get("target_section", ""),
            current_section_index=data.get("current_section_index", -1),
            current_section_type=data.get("current_section_type", ""),
            # Refinement-specific
            modification_request=data.get("modification_request", ""),
            previous_html=data.get("previous_html", ""),
            # Gemini 3 thought signatures
            thought_signatures=data.get("thought_signatures", []),
        )

        if data.get("design_dna"):
            context.design_dna = DesignDNA.from_dict(data["design_dna"])

        return context
