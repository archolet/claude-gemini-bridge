"""
Prompts Module - Agent System Prompts and Templates

This module contains the specialized prompts for each Trifecta agent.
Each prompt enforces strict boundaries on what the agent can/cannot do.

Features:
- YAML-based prompt templates with hot-reload support
- Variable substitution ({{variable}} syntax)
- Conditional sections for theme/component-specific content
- Fallback to hardcoded prompts on YAML errors
"""

from gemini_mcp.prompts.agent_prompts import (
    AGENT_NAMES,
    ALCHEMIST_SYSTEM_PROMPT,
    ARCHITECT_SYSTEM_PROMPT,
    CRITIC_SYSTEM_PROMPT,
    PHYSICIST_SYSTEM_PROMPT,
    QUALITY_GUARD_SYSTEM_PROMPT,
    STRATEGIST_SYSTEM_PROMPT,
    VISIONARY_SYSTEM_PROMPT,
    get_agent_prompt,
    get_all_prompts,
    get_hardcoded_prompt,
)

# Lazy imports for loader components (optional, reduces startup time)
def get_prompt_loader():
    """Get the global PromptLoader instance."""
    from gemini_mcp.prompts.prompt_loader import get_loader
    return get_loader()


def reload_prompt(agent_name: str) -> bool:
    """Reload a specific agent's prompt template."""
    from gemini_mcp.prompts.prompt_loader import reload_prompt as _reload
    return _reload(agent_name)


def reload_all_prompts() -> dict:
    """Reload all prompt templates."""
    from gemini_mcp.prompts.prompt_loader import reload_all_prompts as _reload_all
    return _reload_all()


__all__ = [
    # Hardcoded prompts (backward compatibility)
    "ARCHITECT_SYSTEM_PROMPT",
    "ALCHEMIST_SYSTEM_PROMPT",
    "PHYSICIST_SYSTEM_PROMPT",
    "STRATEGIST_SYSTEM_PROMPT",
    "QUALITY_GUARD_SYSTEM_PROMPT",
    "CRITIC_SYSTEM_PROMPT",
    "VISIONARY_SYSTEM_PROMPT",
    # Agent list
    "AGENT_NAMES",
    # Primary API
    "get_agent_prompt",
    "get_all_prompts",
    "get_hardcoded_prompt",
    # Loader access
    "get_prompt_loader",
    "reload_prompt",
    "reload_all_prompts",
]
