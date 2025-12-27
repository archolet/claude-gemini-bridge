"""
Theme configuration dataclasses for Gemini MCP Server.

Provides a structured, type-safe way to define themes using nested dataclasses.
Each theme is composed of sub-configurations for colors, backgrounds, text, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict


@dataclass
class ThemeColors:
    """Color configuration for a theme."""

    primary: str
    primary_hover: str
    secondary: str
    accent: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to flat dict with prefixed keys."""
        return {
            "primary": self.primary,
            "primary_hover": self.primary_hover,
            "secondary": self.secondary,
            "accent": self.accent,
        }


@dataclass
class ThemeBackgrounds:
    """Background configuration for a theme."""

    background: str
    background_dark: str
    surface: str
    surface_dark: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to flat dict."""
        return {
            "background": self.background,
            "background_dark": self.background_dark,
            "surface": self.surface,
            "surface_dark": self.surface_dark,
        }


@dataclass
class ThemeText:
    """Text/typography color configuration for a theme."""

    text: str
    text_dark: str
    text_muted: str
    text_muted_dark: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Convert to flat dict."""
        result = {
            "text": self.text,
            "text_dark": self.text_dark,
            "text_muted": self.text_muted,
        }
        if self.text_muted_dark:
            result["text_muted_dark"] = self.text_muted_dark
        return result


@dataclass
class ThemeBorders:
    """Border configuration for a theme."""

    border: str
    border_dark: str = ""
    border_radius: str = "rounded-lg"
    border_width: str = "border"

    def to_dict(self) -> Dict[str, str]:
        """Convert to flat dict."""
        result = {
            "border": self.border,
            "border_radius": self.border_radius,
        }
        if self.border_dark:
            result["border_dark"] = self.border_dark
        if self.border_width != "border":
            result["border_width"] = self.border_width
        return result


@dataclass
class ThemeShadows:
    """Shadow configuration for a theme."""

    shadow: str
    shadow_hover: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to flat dict."""
        return {
            "shadow": self.shadow,
            "shadow_hover": self.shadow_hover,
        }


@dataclass
class ThemeStyle:
    """General style configuration for a theme."""

    font: str = "font-sans"
    transition: str = "transition-all duration-200"

    def to_dict(self) -> Dict[str, str]:
        """Convert to flat dict."""
        return {
            "font": self.font,
            "transition": self.transition,
        }


@dataclass
class ThemeConfig:
    """
    Complete theme configuration.

    This is the main dataclass that composes all sub-configurations.
    Use the `to_dict()` method to get a flat dictionary compatible
    with the existing theme factory output format.

    Attributes:
        name: Theme identifier (e.g., "modern-minimal", "cyberpunk")
        description: Human-readable theme description
        colors: Primary, secondary, and accent colors
        backgrounds: Background and surface colors
        text: Text and muted text colors
        borders: Border colors and radius
        shadows: Shadow styles for normal and hover states
        style: Font and transition settings
        extras: Theme-specific additional properties
        metadata: Internal metadata (prefixed with _ in output)

    Example:
        >>> config = ThemeConfig(
        ...     name="my-theme",
        ...     description="A custom theme",
        ...     colors=ThemeColors(
        ...         primary="blue-600",
        ...         primary_hover="blue-700",
        ...         secondary="slate-600",
        ...         accent="amber-500",
        ...     ),
        ...     backgrounds=ThemeBackgrounds(
        ...         background="white",
        ...         background_dark="slate-900",
        ...         surface="slate-50",
        ...         surface_dark="slate-800",
        ...     ),
        ...     text=ThemeText(
        ...         text="slate-900",
        ...         text_dark="slate-100",
        ...         text_muted="slate-500",
        ...     ),
        ...     borders=ThemeBorders(border="slate-200"),
        ...     shadows=ThemeShadows(
        ...         shadow="shadow-md",
        ...         shadow_hover="shadow-lg",
        ...     ),
        ... )
        >>> theme_dict = config.to_dict()
    """

    name: str
    description: str
    colors: ThemeColors
    backgrounds: ThemeBackgrounds
    text: ThemeText
    borders: ThemeBorders
    shadows: ThemeShadows
    style: ThemeStyle = field(default_factory=ThemeStyle)
    extras: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to flat dictionary format.

        This produces output compatible with existing theme factory functions.
        All sub-configurations are flattened into a single dict, and metadata
        keys are prefixed with underscore.

        Returns:
            Flat dictionary with all theme properties.
        """
        result: Dict[str, Any] = {
            "name": self.name,
            "description": self.description,
        }

        # Merge all sub-configurations
        result.update(self.colors.to_dict())
        result.update(self.backgrounds.to_dict())
        result.update(self.text.to_dict())
        result.update(self.borders.to_dict())
        result.update(self.shadows.to_dict())
        result.update(self.style.to_dict())

        # Add extras directly
        result.update(self.extras)

        # Add metadata with underscore prefix
        for key, value in self.metadata.items():
            prefixed_key = key if key.startswith("_") else f"_{key}"
            result[prefixed_key] = value

        return result

    def copy(self) -> "ThemeConfig":
        """Create a deep copy of this configuration."""
        return ThemeConfig(
            name=self.name,
            description=self.description,
            colors=ThemeColors(**asdict(self.colors)),
            backgrounds=ThemeBackgrounds(**asdict(self.backgrounds)),
            text=ThemeText(**asdict(self.text)),
            borders=ThemeBorders(**asdict(self.borders)),
            shadows=ThemeShadows(**asdict(self.shadows)),
            style=ThemeStyle(**asdict(self.style)),
            extras=dict(self.extras),
            metadata=dict(self.metadata),
        )

    def with_colors(self, **kwargs: str) -> "ThemeConfig":
        """Return a copy with updated colors."""
        config = self.copy()
        for key, value in kwargs.items():
            if hasattr(config.colors, key):
                setattr(config.colors, key, value)
        return config

    def with_backgrounds(self, **kwargs: str) -> "ThemeConfig":
        """Return a copy with updated backgrounds."""
        config = self.copy()
        for key, value in kwargs.items():
            if hasattr(config.backgrounds, key):
                setattr(config.backgrounds, key, value)
        return config

    def with_extras(self, **kwargs: Any) -> "ThemeConfig":
        """Return a copy with updated extras."""
        config = self.copy()
        config.extras.update(kwargs)
        return config

    def with_metadata(self, **kwargs: Any) -> "ThemeConfig":
        """Return a copy with updated metadata."""
        config = self.copy()
        config.metadata.update(kwargs)
        return config
