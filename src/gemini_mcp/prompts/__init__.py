"""
Prompts Module - Agent System Prompts and Templates

This module contains the specialized prompts for each Trifecta agent.
Each prompt enforces strict boundaries on what the agent can/cannot do.

Features:
- YAML-based prompt templates with hot-reload support
- Variable substitution ({{variable}} syntax)
- Conditional sections for theme/component-specific content
- Auto-include of anti_laziness segment for all agents
"""

from gemini_mcp.prompts.agent_prompts import (
    AGENT_NAMES,
    get_agent_prompt,
    get_all_prompts,
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


def get_file_watcher():
    """Get the FileWatcher class for hot-reload functionality."""
    from gemini_mcp.prompts.file_watcher import FileWatcher

    return FileWatcher


def get_debounce_wrapper():
    """Get the DebounceWrapper class for debounced callbacks."""
    from gemini_mcp.prompts.file_watcher import DebounceWrapper

    return DebounceWrapper


__all__ = [
    # Agent list
    "AGENT_NAMES",
    # Primary API (YAML-based)
    "get_agent_prompt",
    "get_all_prompts",
    # Loader access
    "get_prompt_loader",
    "reload_prompt",
    "reload_all_prompts",
    # File watcher (hot-reload)
    "get_file_watcher",
    "get_debounce_wrapper",
]
