"""
Complexity Configuration - Adaptive Agent Thinking Levels

This module provides complexity-based configuration for the Trifecta Engine.
Different component types require different levels of reasoning depth:
- Simple components (button, badge): Quick generation, low thinking
- Complex components (navbar, hero): Deep analysis, high thinking
- Ultra components (dashboard, kanban): Sequential precision, high thinking

Gemini 3 API Notes:
    - thinking_level (str): "low" | "high" for Pro, "minimal"|"low"|"medium"|"high" for Flash
    - thinking_budget (int): DEPRECATED - do not use
    - temperature: MUST be 1.0 for Gemini 3 reasoning engine

References:
    - https://ai.google.dev/gemini-api/docs/gemini-3
    - https://ai.google.dev/gemini-api/docs/thinking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ComplexityLevel(Enum):
    """
    Component complexity levels that determine agent configurations.

    Each level has optimized thinking_level, token budgets, and quality settings.
    """

    SIMPLE = "simple"      # button, badge, divider, chip, spinner, progress
    MEDIUM = "medium"      # card, dropdown, tabs, accordion, modal (simple)
    COMPLEX = "complex"    # navbar, hero, sidebar, footer, data_table
    ULTRA = "ultra"        # dashboard, kanban, calendar, chat_widget


# Component type to complexity level mapping
COMPONENT_COMPLEXITY_MAP: dict[str, ComplexityLevel] = {
    # === SIMPLE (Atoms) ===
    "button": ComplexityLevel.SIMPLE,
    "badge": ComplexityLevel.SIMPLE,
    "divider": ComplexityLevel.SIMPLE,
    "chip": ComplexityLevel.SIMPLE,
    "spinner": ComplexityLevel.SIMPLE,
    "progress": ComplexityLevel.SIMPLE,
    "avatar": ComplexityLevel.SIMPLE,
    "icon": ComplexityLevel.SIMPLE,
    "toggle": ComplexityLevel.SIMPLE,
    "tooltip": ComplexityLevel.SIMPLE,
    "slider": ComplexityLevel.SIMPLE,

    # === MEDIUM (Molecules) ===
    "card": ComplexityLevel.MEDIUM,
    "dropdown": ComplexityLevel.MEDIUM,
    "tabs": ComplexityLevel.MEDIUM,
    "accordion": ComplexityLevel.MEDIUM,
    "alert": ComplexityLevel.MEDIUM,
    "breadcrumb": ComplexityLevel.MEDIUM,
    "pagination": ComplexityLevel.MEDIUM,
    "search_bar": ComplexityLevel.MEDIUM,
    "stat_card": ComplexityLevel.MEDIUM,
    "rating": ComplexityLevel.MEDIUM,
    "color_picker": ComplexityLevel.MEDIUM,
    "file_upload": ComplexityLevel.MEDIUM,
    "form": ComplexityLevel.MEDIUM,
    "modal": ComplexityLevel.MEDIUM,
    "table": ComplexityLevel.MEDIUM,
    "stepper": ComplexityLevel.MEDIUM,
    "timeline": ComplexityLevel.MEDIUM,
    "carousel": ComplexityLevel.MEDIUM,
    "input": ComplexityLevel.MEDIUM,

    # === COMPLEX (Organisms) ===
    "navbar": ComplexityLevel.COMPLEX,
    "hero": ComplexityLevel.COMPLEX,
    "sidebar": ComplexityLevel.COMPLEX,
    "footer": ComplexityLevel.COMPLEX,
    "data_table": ComplexityLevel.COMPLEX,
    "login_form": ComplexityLevel.COMPLEX,
    "signup_form": ComplexityLevel.COMPLEX,
    "contact_form": ComplexityLevel.COMPLEX,
    "feature_section": ComplexityLevel.COMPLEX,
    "testimonial_section": ComplexityLevel.COMPLEX,
    "pricing_card": ComplexityLevel.COMPLEX,
    "pricing_table": ComplexityLevel.COMPLEX,
    "user_profile": ComplexityLevel.COMPLEX,
    "settings_panel": ComplexityLevel.COMPLEX,
    "notification_center": ComplexityLevel.COMPLEX,

    # === ULTRA (Complex Organisms) ===
    "dashboard": ComplexityLevel.ULTRA,
    "dashboard_header": ComplexityLevel.ULTRA,
    "kanban_board": ComplexityLevel.ULTRA,
    "calendar": ComplexityLevel.ULTRA,
    "chat_widget": ComplexityLevel.ULTRA,
}

# Section type to complexity level mapping
SECTION_COMPLEXITY_MAP: dict[str, ComplexityLevel] = {
    # === MEDIUM Sections ===
    "cta": ComplexityLevel.MEDIUM,
    "newsletter": ComplexityLevel.MEDIUM,
    "stats": ComplexityLevel.MEDIUM,
    "faq": ComplexityLevel.MEDIUM,

    # === COMPLEX Sections ===
    "hero": ComplexityLevel.COMPLEX,
    "navbar": ComplexityLevel.COMPLEX,
    "features": ComplexityLevel.COMPLEX,
    "testimonials": ComplexityLevel.COMPLEX,
    "pricing": ComplexityLevel.COMPLEX,
    "footer": ComplexityLevel.COMPLEX,
    "team": ComplexityLevel.COMPLEX,
    "contact": ComplexityLevel.COMPLEX,
    "gallery": ComplexityLevel.COMPLEX,
}


@dataclass
class ComplexityConfig:
    """
    Configuration for a specific complexity level.

    All thinking levels use Gemini 3 string format ("low" | "high").

    Attributes:
        architect_thinking_level: Thinking depth for HTML structure (high for complex)
        alchemist_thinking_level: Thinking depth for CSS effects (usually low)
        physicist_thinking_level: Thinking depth for JS interactions (usually low)
        max_html_tokens: Maximum output tokens for HTML generation
        max_css_tokens: Maximum output tokens for CSS generation
        max_js_tokens: Maximum output tokens for JS generation
        enable_critic_loop: Whether to run Critic quality evaluation
        quality_threshold: Minimum quality score to accept (1-10 scale)
        max_refiner_iterations: Maximum refinement loop iterations
        enable_parallel_styling: Whether Alchemist+Physicist can run in parallel
    """

    # Agent thinking levels (Gemini 3 API)
    # MAXIMUM RICHNESS: All agents use high thinking by default
    architect_thinking_level: str = "high"
    alchemist_thinking_level: str = "high"
    physicist_thinking_level: str = "high"

    # Token budgets per agent
    max_html_tokens: int = 16384
    max_css_tokens: int = 8192
    max_js_tokens: int = 8192

    # Quality control settings
    enable_critic_loop: bool = True
    quality_threshold: float = 8.0
    max_refiner_iterations: int = 3

    # Parallel execution
    enable_parallel_styling: bool = True

    def get_agent_thinking_level(self, agent_name: str) -> str:
        """Get thinking level for a specific agent."""
        levels = {
            "architect": self.architect_thinking_level,
            "alchemist": self.alchemist_thinking_level,
            "physicist": self.physicist_thinking_level,
            "strategist": "high",  # Always high for planning
            "critic": "high",  # Always high for evaluation
            "visionary": "high",  # Always high for image analysis
            "quality_guard": "low",  # Validation is straightforward
        }
        return levels.get(agent_name, "high")

    def get_agent_max_tokens(self, agent_name: str) -> int:
        """Get max output tokens for a specific agent."""
        tokens = {
            "architect": self.max_html_tokens,
            "alchemist": self.max_css_tokens,
            "physicist": self.max_js_tokens,
            "strategist": 4096,  # DNA extraction
            "critic": 4096,  # Analysis
            "visionary": 4096,  # Image description
            "quality_guard": 2048,  # Validation report
        }
        return tokens.get(agent_name, 8192)


# Predefined configurations for each complexity level
COMPLEXITY_CONFIGS: dict[ComplexityLevel, ComplexityConfig] = {
    ComplexityLevel.SIMPLE: ComplexityConfig(
        # MAXIMUM RICHNESS: All agents use high thinking for dense output
        architect_thinking_level="high",
        alchemist_thinking_level="high",
        physicist_thinking_level="high",
        max_html_tokens=4096,
        max_css_tokens=2048,
        max_js_tokens=2048,
        enable_critic_loop=False,  # Skip quality loop
        quality_threshold=7.0,
        max_refiner_iterations=1,
        enable_parallel_styling=True,
    ),
    ComplexityLevel.MEDIUM: ComplexityConfig(
        # MAXIMUM RICHNESS: All agents use high thinking for dense output
        architect_thinking_level="high",
        alchemist_thinking_level="high",
        physicist_thinking_level="high",
        max_html_tokens=8192,
        max_css_tokens=4096,
        max_js_tokens=4096,
        enable_critic_loop=True,
        quality_threshold=8.0,
        max_refiner_iterations=2,
        enable_parallel_styling=True,
    ),
    ComplexityLevel.COMPLEX: ComplexityConfig(
        # MAXIMUM RICHNESS: All agents use high thinking for dense output
        architect_thinking_level="high",
        alchemist_thinking_level="high",
        physicist_thinking_level="high",
        max_html_tokens=16384,
        max_css_tokens=8192,
        max_js_tokens=8192,
        enable_critic_loop=True,
        quality_threshold=8.5,
        max_refiner_iterations=3,
        enable_parallel_styling=True,
    ),
    ComplexityLevel.ULTRA: ComplexityConfig(
        # Maximum precision for ultra-complex components
        architect_thinking_level="high",
        alchemist_thinking_level="high",
        physicist_thinking_level="high",  # Complex interactions
        max_html_tokens=24000,
        max_css_tokens=12000,
        max_js_tokens=12000,
        enable_critic_loop=True,
        quality_threshold=9.0,
        max_refiner_iterations=4,
        enable_parallel_styling=False,  # Sequential for precision
    ),
}


def get_complexity_level(component_type: str) -> ComplexityLevel:
    """
    Determine complexity level for a component type.

    Args:
        component_type: The component type string (e.g., "button", "navbar")

    Returns:
        ComplexityLevel for the component
    """
    # Normalize component type
    normalized = component_type.lower().strip()

    # Check component map first
    if normalized in COMPONENT_COMPLEXITY_MAP:
        return COMPONENT_COMPLEXITY_MAP[normalized]

    # Check section map
    if normalized in SECTION_COMPLEXITY_MAP:
        return SECTION_COMPLEXITY_MAP[normalized]

    # Default to MEDIUM for unknown types
    return ComplexityLevel.MEDIUM


def get_complexity_config(component_type: str) -> ComplexityConfig:
    """
    Get the complexity configuration for a component type.

    Args:
        component_type: The component type string

    Returns:
        ComplexityConfig with optimized settings
    """
    level = get_complexity_level(component_type)
    return COMPLEXITY_CONFIGS[level]


def get_thinking_level_for_component(
    component_type: str,
    agent_name: str,
) -> str:
    """
    Get the appropriate thinking level for an agent processing a component.

    This is the main API for the orchestrator to use.

    Args:
        component_type: The component being generated
        agent_name: The agent processing the component

    Returns:
        Gemini 3 thinking level string ("low" | "high")
    """
    config = get_complexity_config(component_type)
    return config.get_agent_thinking_level(agent_name)


def get_quality_threshold_for_component(component_type: str) -> float:
    """
    Get the quality threshold for a component type.

    Args:
        component_type: The component being generated

    Returns:
        Quality threshold score (1-10)
    """
    config = get_complexity_config(component_type)
    return config.quality_threshold


def should_enable_parallel_styling(component_type: str) -> bool:
    """
    Check if Alchemist and Physicist should run in parallel.

    Args:
        component_type: The component being generated

    Returns:
        True if parallel execution is enabled for this complexity level
    """
    config = get_complexity_config(component_type)
    return config.enable_parallel_styling


def should_enable_critic_loop(component_type: str) -> bool:
    """
    Check if the Critic quality evaluation loop should run.

    Args:
        component_type: The component being generated

    Returns:
        True if critic loop is enabled for this complexity level
    """
    config = get_complexity_config(component_type)
    return config.enable_critic_loop


# === Quality Target Integration ===

def get_config_for_quality_target(
    component_type: str,
    quality_target: str,
) -> ComplexityConfig:
    """
    Get complexity config adjusted for a specific quality target.

    Quality targets can override default complexity settings:
    - "draft": Lower thresholds, fewer iterations
    - "production": Default settings
    - "high": Higher thresholds, more iterations
    - "premium": Enable professional validator
    - "enterprise": Full corporate evaluation

    Args:
        component_type: The component being generated
        quality_target: Quality target string

    Returns:
        Adjusted ComplexityConfig
    """
    base_config = get_complexity_config(component_type)

    # Adjust based on quality target
    if quality_target == "draft":
        return ComplexityConfig(
            # MAXIMUM RICHNESS: Even drafts use high thinking for quality
            architect_thinking_level="high",
            alchemist_thinking_level="high",
            physicist_thinking_level="high",
            max_html_tokens=base_config.max_html_tokens,
            max_css_tokens=base_config.max_css_tokens,
            max_js_tokens=base_config.max_js_tokens,
            enable_critic_loop=False,
            quality_threshold=6.0,
            max_refiner_iterations=1,
            enable_parallel_styling=True,
        )

    elif quality_target in ("high", "premium", "enterprise"):
        # Increase quality requirements
        threshold_boost = {
            "high": 0.5,
            "premium": 1.0,
            "enterprise": 1.5,
        }
        iteration_boost = {
            "high": 1,
            "premium": 2,
            "enterprise": 3,
        }

        return ComplexityConfig(
            architect_thinking_level="high",
            alchemist_thinking_level="high",
            physicist_thinking_level=base_config.physicist_thinking_level,
            max_html_tokens=base_config.max_html_tokens,
            max_css_tokens=base_config.max_css_tokens,
            max_js_tokens=base_config.max_js_tokens,
            enable_critic_loop=True,
            quality_threshold=min(10.0, base_config.quality_threshold + threshold_boost.get(quality_target, 0)),
            max_refiner_iterations=base_config.max_refiner_iterations + iteration_boost.get(quality_target, 0),
            enable_parallel_styling=base_config.enable_parallel_styling,
        )

    # Default: return base config
    return base_config
