"""
Unified theme factory for Gemini MCP Server.

Provides a single `create_theme()` function that can create any theme
with optional customizations, replacing 14 individual factory functions.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Callable

from .config import ThemeConfig


# Type alias for customizer functions
ThemeCustomizer = Callable[[ThemeConfig, Dict[str, Any]], ThemeConfig]

# Registry of theme customizers (populated by customizers.py)
THEME_CUSTOMIZERS: Dict[str, ThemeCustomizer] = {}

# Registry of base themes (populated by bases.py)
THEME_BASES: Dict[str, ThemeConfig] = {}


def register_base(name: str, config: ThemeConfig) -> None:
    """Register a base theme configuration."""
    THEME_BASES[name] = config


def register_customizer(name: str, customizer: ThemeCustomizer) -> None:
    """Register a theme customizer function."""
    THEME_CUSTOMIZERS[name] = customizer


def create_theme(
    base_name: str,
    overrides: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Universal theme factory function.

    Creates a theme based on a registered base configuration, optionally
    applying theme-specific customizations and direct overrides.

    Args:
        base_name: Name of the base theme (e.g., "modern-minimal", "cyberpunk")
        overrides: Direct key-value overrides to apply to the final dict
        **kwargs: Theme-specific customization parameters passed to the customizer

    Returns:
        Flat dictionary with all theme properties, compatible with existing usage.

    Raises:
        KeyError: If base_name is not a registered theme.

    Example:
        >>> # Create a basic theme
        >>> theme = create_theme("modern-minimal")
        >>>
        >>> # Create with customization parameters
        >>> theme = create_theme("cyberpunk", primary_neon="cyan", glow_intensity="strong")
        >>>
        >>> # Create with direct overrides
        >>> theme = create_theme("corporate", overrides={"primary": "custom-blue"})
    """
    if base_name not in THEME_BASES:
        available = ", ".join(sorted(THEME_BASES.keys()))
        raise KeyError(f"Unknown theme '{base_name}'. Available: {available}")

    # Start with a copy of the base theme
    config = THEME_BASES[base_name].copy()

    # Apply theme-specific customizations if a customizer is registered
    if base_name in THEME_CUSTOMIZERS and kwargs:
        config = THEME_CUSTOMIZERS[base_name](config, kwargs)

    # Convert to dict
    result = config.to_dict()

    # Apply direct overrides
    if overrides:
        result.update(overrides)

    return result


def get_theme_base(name: str) -> Optional[ThemeConfig]:
    """Get a copy of a registered base theme configuration."""
    if name in THEME_BASES:
        return THEME_BASES[name].copy()
    return None


def list_themes() -> list[str]:
    """List all registered theme names."""
    return sorted(THEME_BASES.keys())


def is_theme_registered(name: str) -> bool:
    """Check if a theme is registered."""
    return name in THEME_BASES
