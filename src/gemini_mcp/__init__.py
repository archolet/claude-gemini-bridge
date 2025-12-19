"""Gemini MCP Server - Vertex AI integration for Claude Code."""

__version__ = "0.1.0"

from .frontend_presets import (
    COMPONENT_PRESETS,
    THEME_PRESETS,
    get_available_components,
    get_available_themes,
    get_component_preset,
    get_theme_preset,
    build_style_guide,
)
