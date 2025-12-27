"""
Themes subpackage for Gemini MCP Server.

This package provides a structured, dataclass-based theme system
with reduced code duplication and improved maintainability.

Usage:
    from gemini_mcp.themes import create_theme, ThemeConfig

    # Using unified factory
    theme = create_theme("cyberpunk", primary_neon="cyan")

    # Or using legacy factory functions (backward compatible)
    from gemini_mcp.theme_factories import create_cyberpunk_theme
    theme = create_cyberpunk_theme(primary_neon="cyan")
"""

from .config import (
    ThemeConfig,
    ThemeColors,
    ThemeBackgrounds,
    ThemeText,
    ThemeBorders,
    ThemeShadows,
    ThemeStyle,
)
from .factory import (
    create_theme,
    list_themes,
    is_theme_registered,
    get_theme_base,
    THEME_BASES,
    THEME_CUSTOMIZERS,
)
from .utils import (
    hex_to_rgb,
    rgb_to_hex,
    hex_to_hsl,
    hsl_to_hex,
    relative_luminance,
    contrast_ratio,
    validate_contrast,
)

# Import bases to trigger automatic registration of all base themes
from . import bases  # noqa: F401

# Import customizers to trigger automatic registration
from . import customizers  # noqa: F401

# Import constants for external use
from . import constants  # noqa: F401

# Import vibes for design personality
from . import vibes  # noqa: F401
from .vibes import (
    get_vibe,
    list_vibes,
    list_enterprise_vibes,
    get_vibe_for_industry,
    get_vibe_prompt_segment,
    ALL_VIBES,
    CORE_VIBES,
    ENTERPRISE_VIBES,
    ENTERPRISE_VIBE_COMPATIBILITY,
)

__all__ = [
    # Config dataclasses
    "ThemeConfig",
    "ThemeColors",
    "ThemeBackgrounds",
    "ThemeText",
    "ThemeBorders",
    "ThemeShadows",
    "ThemeStyle",
    # Factory
    "create_theme",
    "list_themes",
    "is_theme_registered",
    "get_theme_base",
    "THEME_BASES",
    "THEME_CUSTOMIZERS",
    # Utils
    "hex_to_rgb",
    "rgb_to_hex",
    "hex_to_hsl",
    "hsl_to_hex",
    "relative_luminance",
    "contrast_ratio",
    "validate_contrast",
    # Submodules
    "bases",
    "customizers",
    "constants",
    "vibes",
    # Vibes exports
    "get_vibe",
    "list_vibes",
    "list_enterprise_vibes",
    "get_vibe_for_industry",
    "get_vibe_prompt_segment",
    "ALL_VIBES",
    "CORE_VIBES",
    "ENTERPRISE_VIBES",
    "ENTERPRISE_VIBE_COMPATIBILITY",
]
