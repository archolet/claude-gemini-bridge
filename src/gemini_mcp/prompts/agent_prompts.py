"""
Agent System Prompts - Wrapper Module for YAML-based Prompts.

This module provides backward-compatible access to agent prompts that are
now stored in YAML templates. All prompts are loaded dynamically via
the PromptLoader system.

Each agent has strict boundaries:
- Architect: HTML only, no CSS/JS
- Alchemist: CSS only, no HTML modification
- Physicist: JS only, no frameworks
- Strategist: Planning and DNA extraction
- Quality Guard: Validation and auto-fix
- Critic: Art direction for refinements
- Visionary: Vision API image analysis

For new code, prefer using prompt_loader.get_prompt() directly.
"""

from typing import Any, Dict, List, Optional

# Agent names for iteration and validation
AGENT_NAMES = [
    "architect",
    "alchemist",
    "physicist",
    "strategist",
    "quality_guard",
    "critic",
    "visionary",
]


def get_agent_prompt(
    agent_name: str,
    variables: Optional[Dict[str, Any]] = None,
    include_sections: Optional[List[str]] = None,
) -> str:
    """
    Get the system prompt for a specific agent.

    Loads the prompt from YAML templates via PromptLoader.

    Args:
        agent_name: Agent identifier (e.g., "architect", "alchemist").
        variables: Optional variable substitutions (e.g., {"theme": "cyberpunk"}).
        include_sections: Optional conditional sections to include.

    Returns:
        The system prompt string for the agent.

    Raises:
        PromptLoadError: If the template cannot be loaded.

    Example:
        # Simple usage
        prompt = get_agent_prompt("architect")

        # With variables
        prompt = get_agent_prompt("architect", {"theme": "cyberpunk"})
    """
    from gemini_mcp.prompts.prompt_loader import get_prompt

    return get_prompt(agent_name, variables, include_sections)


def get_all_prompts(variables: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Get all agent prompts as a dictionary.

    Loads each prompt from YAML templates.

    Args:
        variables: Optional variable substitutions applied to all prompts.

    Returns:
        Dictionary mapping agent names to their prompts.

    Example:
        all_prompts = get_all_prompts()
        print(len(all_prompts["architect"]))
    """
    from gemini_mcp.prompts.prompt_loader import get_prompt

    prompts = {}
    for agent_name in AGENT_NAMES:
        try:
            prompts[agent_name] = get_prompt(agent_name, variables)
        except Exception as e:
            # Log but don't fail - useful for debugging
            import logging
            logging.getLogger(__name__).warning(
                f"Failed to load prompt for {agent_name}: {e}"
            )
            prompts[agent_name] = ""

    return prompts
