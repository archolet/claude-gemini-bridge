"""
Theme Factory Functions for Gemini MCP Server.

This module provides factory functions for creating customizable themes.
Each theme factory allows extensive customization while maintaining
design consistency and accessibility standards.

This is a backward-compatible wrapper that delegates to the unified
`create_theme()` function in the `themes` package.
"""

from typing import Dict, Any, Optional, Literal, List
from dataclasses import dataclass

# Import from the new themes package
from .themes import (
    create_theme,
    list_themes,
    hex_to_rgb,
    rgb_to_hex,
    hex_to_hsl,
    hsl_to_hex,
    relative_luminance,
    contrast_ratio,
    validate_contrast,
)

# Import constants for re-export (backward compatibility)
from .themes.constants import (
    BRUTALIST_CONTRAST_PAIRS,
    NEOBRUTALISM_GRADIENTS,
    GRADIENT_ANIMATIONS,
    CORPORATE_INDUSTRIES,
    CORPORATE_LAYOUTS,
    FORMALITY_TYPOGRAPHY,
    GRADIENT_LIBRARY,
    NEON_COLORS,
    GLOW_INTENSITIES,
    RETRO_FONT_PAIRINGS,
    PASTEL_ACCESSIBLE_PAIRS,
    NATURE_SEASONS,
    STARTUP_ARCHETYPES,
    THEME_VIBE_COMPATIBILITY,
    CORPORATE_PRESETS,
)


# =============================================================================
# HELPER FUNCTIONS (for backward compatibility)
# =============================================================================

def calculate_neumorphism_shadows(
    base_color: str,
    intensity: Literal["subtle", "medium", "strong"] = "medium",
    is_dark_mode: bool = False,
) -> Dict[str, str]:
    """Calculate proper neumorphism shadows for any base color."""
    intensity_map = {
        "subtle": {"light_offset": 8, "dark_offset": 12, "blur": 15},
        "medium": {"light_offset": 15, "dark_offset": 20, "blur": 20},
        "strong": {"light_offset": 20, "dark_offset": 25, "blur": 25},
    }

    settings = intensity_map[intensity]

    neumorphism_colors = {
        "slate-100": {"light": "#ffffff", "dark": "#c8d0db", "bg": "#f1f5f9"},
        "slate-200": {"light": "#ffffff", "dark": "#b8c2cf", "bg": "#e2e8f0"},
        "gray-100": {"light": "#ffffff", "dark": "#c7ccd1", "bg": "#f3f4f6"},
        "slate-800": {"light": "#3d4a5c", "dark": "#0f1623", "bg": "#1e293b"},
        "slate-900": {"light": "#283548", "dark": "#000000", "bg": "#0f172a"},
        "zinc-800": {"light": "#3f3f46", "dark": "#0a0a0b", "bg": "#27272a"},
        "zinc-900": {"light": "#2d2d31", "dark": "#000000", "bg": "#18181b"},
    }

    colors = neumorphism_colors.get(base_color, neumorphism_colors["slate-100"])
    offset = settings["light_offset"]
    blur = settings["blur"]

    return {
        "shadow": f"shadow-[{offset}px_{offset}px_{blur}px_{colors['dark']},-{offset}px_-{offset}px_{blur}px_{colors['light']}]",
        "shadow_inset": f"shadow-[inset_{offset}px_{offset}px_{blur}px_{colors['dark']},inset_-{offset}px_-{offset}px_{blur}px_{colors['light']}]",
        "background_color": colors["bg"],
    }


def generate_neon_glow(
    color: str,
    intensity: Literal["subtle", "medium", "strong", "intense", "extreme"] = "medium",
    animated: bool = False,
) -> str:
    """Generate multi-layer neon glow shadow."""
    neon = NEON_COLORS.get(color, NEON_COLORS["cyan"])
    settings = GLOW_INTENSITIES.get(intensity, GLOW_INTENSITIES["medium"])

    rgb = neon["rgb"]
    base_opacity = settings["opacity"]
    base_blur = int(settings["blur"].replace("px", ""))
    layers = settings["layers"]

    shadows = []

    if layers >= 1:
        shadows.append(f"0_0_{base_blur // 2}px_rgba({rgb},{base_opacity + 0.1})")
    if layers >= 2:
        shadows.append(f"0_0_{base_blur}px_rgba({rgb},{base_opacity})")
    if layers >= 3:
        shadows.append(f"0_0_{base_blur * 2}px_rgba({rgb},{base_opacity - 0.1})")

    shadow_class = f"shadow-[{','.join(shadows)}]"

    if animated:
        shadow_class += " animate-glow-pulse"

    return shadow_class


def get_gradient(name: str) -> Dict[str, Any]:
    """Get a specific gradient from the library."""
    return GRADIENT_LIBRARY.get(name, GRADIENT_LIBRARY["aurora"])


def list_gradients_by_category(category: str) -> List[str]:
    """List gradients by category."""
    return [name for name, g in GRADIENT_LIBRARY.items() if g.get("category") == category]


def get_formality_typography(formality: str) -> Dict[str, Any]:
    """Get typography settings for a formality level."""
    return FORMALITY_TYPOGRAPHY.get(formality, FORMALITY_TYPOGRAPHY.get("semi-formal", {}))


# =============================================================================
# VIBE COMPATIBILITY FUNCTIONS
# =============================================================================

def get_recommended_vibes(theme: str, top_n: int = 4) -> List[tuple]:
    """
    Get recommended vibes for a theme, sorted by compatibility score.

    Args:
        theme: Theme name (e.g., "cyberpunk", "corporate")
        top_n: Number of top recommendations to return

    Returns:
        List of (vibe_name, score) tuples sorted by score descending
    """
    theme_key = theme.replace("-", "_") if "-" in theme else theme
    if theme_key not in THEME_VIBE_COMPATIBILITY:
        # Try with hyphen
        theme_key = theme.replace("_", "-")

    vibes = THEME_VIBE_COMPATIBILITY.get(theme_key, {})
    sorted_vibes = sorted(vibes.items(), key=lambda x: x[1], reverse=True)
    return sorted_vibes[:top_n]


def get_vibe_compatibility(theme: str, vibe) -> tuple:
    """
    Get compatibility score and message for a theme-vibe pair.

    Args:
        theme: Theme name
        vibe: Vibe name (str) or tuple from get_recommended_vibes (vibe_name, score)

    Returns:
        Tuple of (score, message)
    """
    # Handle tuple input from get_recommended_vibes
    if isinstance(vibe, tuple):
        vibe = vibe[0]

    theme_key = theme.replace("-", "_") if "-" in theme else theme
    if theme_key not in THEME_VIBE_COMPATIBILITY:
        theme_key = theme.replace("_", "-")

    vibes = THEME_VIBE_COMPATIBILITY.get(theme_key, {})
    score = vibes.get(vibe, 0)

    if score >= 5:
        message = "Perfect match! This vibe amplifies this theme's essence."
    elif score >= 4:
        message = "Great compatibility. This combination works very well."
    elif score >= 3:
        message = "Good compatibility. This combination is acceptable."
    elif score >= 2:
        message = "Low compatibility. Consider a different vibe."
    else:
        message = "Style conflict. This combination creates visual tension."

    return (score, message)


# =============================================================================
# CORPORATE PRESET FUNCTIONS
# =============================================================================

def get_corporate_preset(name: str) -> Optional[Dict[str, Any]]:
    """Get a corporate preset by name."""
    return CORPORATE_PRESETS.get(name)


def list_corporate_presets() -> List[str]:
    """List all available corporate presets."""
    return list(CORPORATE_PRESETS.keys())


def apply_corporate_preset(preset_name: str) -> Dict[str, Any]:
    """
    Apply a corporate preset and return theme settings.

    Args:
        preset_name: Name of the preset (e.g., "enterprise_bank")

    Returns:
        Theme configuration dict with preset settings applied
    """
    preset = CORPORATE_PRESETS.get(preset_name)
    if not preset:
        return {}

    theme_name = preset.get("theme", "corporate")
    kwargs = {k: v for k, v in preset.items() if k != "theme"}

    return create_theme(theme_name, **kwargs)


# Re-export utilities for backward compatibility
__all__ = [
    # Utilities
    "hex_to_rgb",
    "rgb_to_hex",
    "hex_to_hsl",
    "hsl_to_hex",
    "relative_luminance",
    "contrast_ratio",
    "validate_contrast",
    # Brand colors
    "BrandColors",
    # Factory functions
    "create_modern_minimal_theme",
    "create_brutalist_theme",
    "create_glassmorphism_theme",
    "create_neo_brutalism_theme",
    "create_soft_ui_theme",
    "create_corporate_theme",
    "create_gradient_theme",
    "create_cyberpunk_theme",
    "create_retro_theme",
    "create_pastel_theme",
    "create_dark_mode_first_theme",
    "create_high_contrast_theme",
    "create_nature_theme",
    "create_startup_theme",
    # Unified factory
    "create_theme",
    "list_themes",
    # Constants
    "BRUTALIST_CONTRAST_PAIRS",
    "NEOBRUTALISM_GRADIENTS",
    "GRADIENT_ANIMATIONS",
    "CORPORATE_INDUSTRIES",
    "CORPORATE_LAYOUTS",
    "FORMALITY_TYPOGRAPHY",
    "GRADIENT_LIBRARY",
    "NEON_COLORS",
    "GLOW_INTENSITIES",
    "RETRO_FONT_PAIRINGS",
    "PASTEL_ACCESSIBLE_PAIRS",
    "NATURE_SEASONS",
    "STARTUP_ARCHETYPES",
    "THEME_VIBE_COMPATIBILITY",
    "CORPORATE_PRESETS",
    # Helper functions
    "calculate_neumorphism_shadows",
    "generate_neon_glow",
    "get_gradient",
    "list_gradients_by_category",
    "get_formality_typography",
    # Vibe compatibility functions
    "get_recommended_vibes",
    "get_vibe_compatibility",
    # Corporate preset functions
    "get_corporate_preset",
    "list_corporate_presets",
    "apply_corporate_preset",
]


# =============================================================================
# BRAND COLORS
# =============================================================================

@dataclass
class BrandColors:
    """Type-safe brand color structure for Modern-Minimal theme."""
    primary: str
    primary_hover: str
    primary_light: str
    primary_dark: str
    secondary: str
    accent: str

    @classmethod
    def from_hex(cls, primary_hex: str) -> "BrandColors":
        """Generate complete color palette from a single hex color."""
        h, s, lum = hex_to_hsl(primary_hex)
        return cls(
            primary=primary_hex,
            primary_hover=hsl_to_hex(h, s, max(lum - 10, 0)),
            primary_light=hsl_to_hex(h, s * 0.3, 95),
            primary_dark=hsl_to_hex(h, s, max(lum - 30, 15)),
            secondary=hsl_to_hex((h + 30) % 360, s * 0.7, lum),
            accent=hsl_to_hex((h + 180) % 360, s, lum),
        )


# =============================================================================
# FACTORY FUNCTIONS (Backward-Compatible Wrappers)
# =============================================================================

def create_modern_minimal_theme(
    brand: Optional[BrandColors] = None,
    neutral_base: Literal["slate", "gray", "zinc", "neutral", "stone"] = "slate",
    border_radius: Literal["none", "sm", "md", "lg", "xl", "2xl", "full"] = "lg",
    shadow_intensity: Literal["none", "sm", "md", "lg"] = "sm",
) -> Dict[str, Any]:
    """
    Customizable Modern Minimal theme factory.

    Args:
        brand: Brand colors. If None, uses default blue.
        neutral_base: Base gray color family.
        border_radius: Global border radius.
        shadow_intensity: Shadow intensity level.

    Example:
        # Custom brand colors
        theme = create_modern_minimal_theme(
            brand=BrandColors.from_hex("#E11D48"),  # Rose
            neutral_base="zinc",
            border_radius="xl"
        )
    """
    return create_theme(
        "modern-minimal",
        brand=brand,
        neutral_base=neutral_base,
        border_radius=border_radius,
        shadow_intensity=shadow_intensity,
    )


def create_brutalist_theme(
    contrast_mode: Literal["standard", "high", "maximum"] = "high",
    accent_color: Literal["yellow", "red", "cyan", "pink", "lime"] = "yellow",
    include_focus_indicators: bool = True,
    enable_animations: bool = False,
    border_width: Literal["2", "4", "8"] = "4",
    shadow_offset: Literal["sm", "md", "lg"] = "md",
) -> Dict[str, Any]:
    """
    WCAG-compliant Brutalist theme with bold aesthetics.

    Maintains the bold brutalist aesthetic while ensuring accessibility.

    Args:
        contrast_mode: Contrast level - "standard" (AA), "high" (AAA), "maximum" (AAA+)
        accent_color: Accent color choice.
        include_focus_indicators: Whether to include focus indicators.
        enable_animations: Enable animations.
        border_width: Border width.
        shadow_offset: Shadow offset size.
    """
    return create_theme(
        "brutalist",
        contrast_mode=contrast_mode,
        accent_color=accent_color,
        include_focus_indicators=include_focus_indicators,
        enable_animations=enable_animations,
        border_width=border_width,
        shadow_offset=shadow_offset,
    )


def create_glassmorphism_theme(
    blur_intensity: Literal["sm", "md", "lg", "xl", "2xl", "3xl"] = "xl",
    opacity: float = 0.7,
    tint_color: str = "white",
    enable_fallback: bool = True,
    performance_mode: Literal["quality", "balanced", "performance"] = "balanced",
) -> Dict[str, Any]:
    """
    Safari-compatible Glassmorphism with progressive enhancement.

    Generates CSS with backdrop-filter when supported and falls back
    to semi-transparent backgrounds when not.

    Args:
        blur_intensity: Blur intensity level.
        opacity: Glass opacity (0.3 to 0.95).
        tint_color: Tint color for glass effect.
        enable_fallback: Enable fallback for unsupported browsers.
        performance_mode: Performance mode (quality/balanced/performance).
    """
    return create_theme(
        "glassmorphism",
        blur_intensity=blur_intensity,
        opacity=opacity,
        tint_color=tint_color,
        enable_fallback=enable_fallback,
        performance_mode=performance_mode,
    )


def create_neo_brutalism_theme(
    gradient_preset: Literal["sunset", "ocean", "forest", "candy", "fire"] = "sunset",
    animation: Literal["none", "flow", "pulse", "shimmer", "wave"] = "flow",
    animation_speed: Literal["slow", "normal", "fast"] = "normal",
    shadow_color: str = "black",
    include_hover_animations: bool = True,
) -> Dict[str, Any]:
    """
    Neo-Brutalism with animated gradients and playful effects.

    Args:
        gradient_preset: Gradient color preset.
        animation: Animation type for gradients.
        animation_speed: Animation speed.
        shadow_color: Shadow color.
        include_hover_animations: Include hover animations.
    """
    return create_theme(
        "neo-brutalism",
        gradient_preset=gradient_preset,
        animation=animation,
        animation_speed=animation_speed,
        shadow_color=shadow_color,
        include_hover_animations=include_hover_animations,
    )


def create_soft_ui_theme(
    base_color_light: str = "slate-100",
    base_color_dark: str = "slate-800",
    primary_color: str = "blue-500",
    intensity: Literal["subtle", "medium", "strong"] = "medium",
    color_temperature: Literal["cool", "neutral", "warm"] = "neutral",
    surface_variant: Literal["flat", "raised", "inset"] = "raised",
    glow_color: Optional[str] = None,
    enable_inner_shadow: bool = True,
) -> Dict[str, Any]:
    """
    Proper dual-mode neumorphism with calculated shadows.

    Args:
        base_color_light: Light mode base color.
        base_color_dark: Dark mode base color.
        primary_color: Primary accent color.
        intensity: Neumorphism intensity (subtle/medium/strong).
        color_temperature: Color temperature (cool/neutral/warm).
        surface_variant: Surface variant (flat/raised/inset).
        glow_color: Optional glow color.
        enable_inner_shadow: Enable inner shadow effect.
    """
    return create_theme(
        "soft-ui",
        base_color_light=base_color_light,
        base_color_dark=base_color_dark,
        primary_color=primary_color,
        intensity=intensity,
        color_temperature=color_temperature,
        surface_variant=surface_variant,
        glow_color=glow_color,
        enable_inner_shadow=enable_inner_shadow,
    )


def create_corporate_theme(
    industry: Literal["finance", "healthcare", "legal", "tech", "manufacturing", "consulting"] = "consulting",
    layout: Literal["traditional", "modern", "editorial"] = "modern",
    formality: Literal["formal", "semi-formal", "approachable"] = "semi-formal",
    include_accent_gradients: bool = False,
) -> Dict[str, Any]:
    """
    Industry-specific corporate theme with personality.

    Args:
        industry: Industry vertical for color/style customization.
        layout: Layout style.
        formality: Formality level.
        include_accent_gradients: Include accent gradients.
    """
    return create_theme(
        "corporate",
        industry=industry,
        layout=layout,
        formality=formality,
        include_accent_gradients=include_accent_gradients,
    )


def create_gradient_theme(
    primary_gradient: str = "aurora",
    secondary_gradient: str = "ocean",
    button_style: Literal["gradient", "solid_with_gradient_hover", "gradient_border"] = "gradient",
    card_style: Literal["subtle", "bordered", "glass"] = "subtle",
    dark_mode_gradient: str = "dark_aurora",
    include_animations: bool = True,
) -> Dict[str, Any]:
    """
    Comprehensive gradient theme with multiple presets.

    Args:
        primary_gradient: Primary gradient preset name.
        secondary_gradient: Secondary gradient preset name.
        button_style: Button styling approach.
        card_style: Card styling approach.
        dark_mode_gradient: Dark mode gradient preset.
        include_animations: Include gradient animations.
    """
    return create_theme(
        "gradient",
        primary_gradient=primary_gradient,
        secondary_gradient=secondary_gradient,
        button_style=button_style,
        card_style=card_style,
        dark_mode_gradient=dark_mode_gradient,
        include_animations=include_animations,
    )


def create_cyberpunk_theme(
    primary_neon: str = "cyan",
    secondary_neon: str = "fuchsia",
    glow_intensity: Literal["subtle", "medium", "strong", "intense", "extreme"] = "medium",
    enable_animations: bool = True,
    scanline_effect: bool = False,
) -> Dict[str, Any]:
    """
    Cyberpunk theme with configurable neon effects.

    Args:
        primary_neon: Primary neon color.
        secondary_neon: Secondary neon color.
        glow_intensity: Glow effect intensity.
        enable_animations: Enable neon animations.
        scanline_effect: Enable CRT scanline effect.
    """
    return create_theme(
        "cyberpunk",
        primary_neon=primary_neon,
        secondary_neon=secondary_neon,
        glow_intensity=glow_intensity,
        enable_animations=enable_animations,
        scanline_effect=scanline_effect,
    )


def create_retro_theme(
    era: Literal["80s_tech", "80s_neon", "90s_grunge", "90s_web", "retro_futurism", "vintage_americana"] = "80s_neon",
    color_scheme: Literal["neon", "pastel", "earthy", "chrome"] = "neon",
    enable_crt_effects: bool = False,
) -> Dict[str, Any]:
    """
    Retro theme with era-specific font pairings.

    Args:
        era: Era style (80s_tech, 80s_neon, 90s_grunge, etc.)
        color_scheme: Color scheme (neon, pastel, earthy, chrome).
        enable_crt_effects: Enable CRT visual effects.
    """
    return create_theme(
        "retro",
        era=era,
        color_scheme=color_scheme,
        enable_crt_effects=enable_crt_effects,
    )


def create_pastel_theme(
    primary_pastel: Literal["rose", "pink", "sky", "violet", "teal", "amber", "lime"] = "rose",
    secondary_pastel: Literal["rose", "pink", "sky", "violet", "teal", "amber", "lime"] = "sky",
    wcag_level: Literal["AA", "AAA"] = "AA",
    dark_mode_handling: Literal["invert", "desaturate", "vibrant"] = "desaturate",
) -> Dict[str, Any]:
    """
    WCAG-compliant pastel theme with guaranteed contrast ratios.

    Args:
        primary_pastel: Primary pastel color.
        secondary_pastel: Secondary pastel color.
        wcag_level: WCAG compliance level (AA or AAA).
        dark_mode_handling: Dark mode color handling strategy.
    """
    return create_theme(
        "pastel",
        primary_pastel=primary_pastel,
        secondary_pastel=secondary_pastel,
        wcag_level=wcag_level,
        dark_mode_handling=dark_mode_handling,
    )


def create_dark_mode_first_theme(
    primary_glow: str = "emerald",
    contrast_level: Literal["normal", "high"] = "normal",
    light_mode_style: Literal["minimal", "warm", "cool", "inverted"] = "minimal",
) -> Dict[str, Any]:
    """
    Dark mode optimized theme with equally polished light mode.

    Args:
        primary_glow: Primary glow color.
        contrast_level: Contrast level (normal/high).
        light_mode_style: Light mode styling approach.
    """
    return create_theme(
        "dark-mode-first",
        primary_glow=primary_glow,
        contrast_level=contrast_level,
        light_mode_style=light_mode_style,
    )


def create_high_contrast_theme(
    softness_level: Literal["sharp", "balanced", "smooth"] = "balanced",
    color_scheme: Literal["blue", "purple", "green", "neutral"] = "blue",
    animation_preference: Literal["full", "reduced", "none"] = "reduced",
) -> Dict[str, Any]:
    """
    WCAG AAA compliant theme with adjustable visual softness.

    Args:
        softness_level: Visual softness level.
        color_scheme: Color scheme.
        animation_preference: Animation preference for accessibility.
    """
    return create_theme(
        "high-contrast",
        softness_level=softness_level,
        color_scheme=color_scheme,
        animation_preference=animation_preference,
    )


def create_nature_theme(
    season: Literal["spring", "summer", "autumn", "winter"] = "spring",
    organic_shapes: bool = True,
    eco_friendly_mode: bool = False,
) -> Dict[str, Any]:
    """
    Nature-inspired theme with seasonal variations.

    Args:
        season: Season for color palette.
        organic_shapes: Use organic/blob-like shapes.
        eco_friendly_mode: Reduce animations for energy efficiency.
    """
    return create_theme(
        "nature",
        season=season,
        organic_shapes=organic_shapes,
        eco_friendly_mode=eco_friendly_mode,
    )


def create_startup_theme(
    archetype: Literal["disruptor", "enterprise", "consumer", "fintech", "healthtech", "ai_ml", "sustainability"] = "disruptor",
    stage: Literal["seed", "growth", "scale"] = "growth",
    enable_motion: bool = True,
) -> Dict[str, Any]:
    """
    Startup-specific theme with archetype-based differentiation.

    Args:
        archetype: Startup archetype for styling.
        stage: Company stage for visual boldness.
        enable_motion: Enable motion/animations.
    """
    return create_theme(
        "startup",
        archetype=archetype,
        stage=stage,
        enable_motion=enable_motion,
    )
