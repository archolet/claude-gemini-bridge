"""
Base theme configurations for Gemini MCP Server.

Contains default ThemeConfig instances for all 14 supported themes.
These bases are registered with the factory and can be customized
using theme-specific parameters.
"""

from __future__ import annotations

from .config import (
    ThemeConfig,
    ThemeColors,
    ThemeBackgrounds,
    ThemeText,
    ThemeBorders,
    ThemeShadows,
    ThemeStyle,
)
from .factory import register_base


# =============================================================================
# 1. MODERN-MINIMAL THEME
# =============================================================================

MODERN_MINIMAL_BASE = ThemeConfig(
    name="modern-minimal",
    description="Clean, professional design with subtle shadows and rounded corners",
    colors=ThemeColors(
        primary="blue-600",
        primary_hover="blue-700",
        secondary="slate-600",
        accent="emerald-500",
    ),
    backgrounds=ThemeBackgrounds(
        background="white",
        background_dark="slate-900",
        surface="slate-50",
        surface_dark="slate-800",
    ),
    text=ThemeText(
        text="slate-900",
        text_dark="slate-100",
        text_muted="slate-500",
    ),
    borders=ThemeBorders(
        border="slate-200",
        border_dark="slate-700",
        border_radius="rounded-lg",
    ),
    shadows=ThemeShadows(
        shadow="shadow-sm",
        shadow_hover="shadow-md",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-200 ease-out",
    ),
    extras={
        "primary_light": "blue-50",
        "primary_dark": "blue-900",
    },
)


# =============================================================================
# 2. BRUTALIST THEME
# =============================================================================

BRUTALIST_BASE = ThemeConfig(
    name="brutalist",
    description="Bold, high-contrast design with sharp edges and strong typography",
    colors=ThemeColors(
        primary="black",
        primary_hover="slate-800",
        secondary="white",
        accent="yellow-400",
    ),
    backgrounds=ThemeBackgrounds(
        background="white",
        background_dark="black",
        surface="slate-100",
        surface_dark="slate-900",
    ),
    text=ThemeText(
        text="black",
        text_dark="white",
        text_muted="slate-700",
    ),
    borders=ThemeBorders(
        border="black",
        border_dark="white",
        border_radius="rounded-none",
        border_width="border-4",
    ),
    shadows=ThemeShadows(
        shadow="shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]",
        shadow_hover="shadow-[12px_12px_0px_0px_rgba(0,0,0,1)]",
    ),
    style=ThemeStyle(
        font="font-mono",
        transition="transition-none",
    ),
    extras={
        "uppercase_headings": True,
        "harsh_borders": True,
    },
)


# =============================================================================
# 3. GLASSMORPHISM THEME
# =============================================================================

GLASSMORPHISM_BASE = ThemeConfig(
    name="glassmorphism",
    description="Frosted glass effect with blur and transparency",
    colors=ThemeColors(
        primary="indigo-500",
        primary_hover="indigo-600",
        secondary="purple-500",
        accent="pink-500",
    ),
    backgrounds=ThemeBackgrounds(
        background="slate-900",
        background_dark="slate-950",
        surface="white/70",
        surface_dark="slate-900/70",
    ),
    text=ThemeText(
        text="white",
        text_dark="white",
        text_muted="slate-300",
    ),
    borders=ThemeBorders(
        border="white/20",
        border_dark="white/10",
        border_radius="rounded-2xl",
    ),
    shadows=ThemeShadows(
        shadow="shadow-lg shadow-black/10",
        shadow_hover="shadow-xl shadow-black/20",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-300",
    ),
    extras={
        "glass_effect": "bg-white/70 backdrop-blur-xl border-white/20 border ring-1 ring-white/20 ring-inset",
        "glass_effect_strong": "bg-white/80 backdrop-blur-2xl border-white/30 border ring-1 ring-white/40 ring-inset",
    },
)


# =============================================================================
# 4. NEO-BRUTALISM THEME
# =============================================================================

NEO_BRUTALISM_BASE = ThemeConfig(
    name="neo-brutalism",
    description="Playful brutalism with bold colors and hard shadows",
    colors=ThemeColors(
        primary="yellow-400",
        primary_hover="yellow-500",
        secondary="pink-500",
        accent="cyan-400",
    ),
    backgrounds=ThemeBackgrounds(
        background="amber-50",
        background_dark="slate-900",
        surface="white",
        surface_dark="slate-800",
    ),
    text=ThemeText(
        text="black",
        text_dark="white",
        text_muted="slate-700",
    ),
    borders=ThemeBorders(
        border="black",
        border_dark="white",
        border_radius="rounded-xl",
        border_width="border-2",
    ),
    shadows=ThemeShadows(
        shadow="shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]",
        shadow_hover="shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-200",
    ),
    extras={
        "gradient_primary": "bg-gradient-to-r from-yellow-400 via-orange-500 to-pink-500",
    },
)


# =============================================================================
# 5. SOFT-UI (NEUMORPHISM) THEME
# =============================================================================

SOFT_UI_BASE = ThemeConfig(
    name="soft-ui",
    description="Soft, extruded UI with subtle shadows and depth",
    colors=ThemeColors(
        primary="blue-500",
        primary_hover="blue-600",
        secondary="purple-500",
        accent="pink-500",
    ),
    backgrounds=ThemeBackgrounds(
        background="slate-200",
        background_dark="slate-800",
        surface="slate-200",
        surface_dark="slate-800",
    ),
    text=ThemeText(
        text="slate-700",
        text_dark="slate-200",
        text_muted="slate-500",
    ),
    borders=ThemeBorders(
        border="transparent",
        border_dark="transparent",
        border_radius="rounded-2xl",
    ),
    shadows=ThemeShadows(
        shadow="shadow-[8px_8px_16px_#b8c0c8,-8px_-8px_16px_#ffffff]",
        shadow_hover="shadow-[12px_12px_24px_#b8c0c8,-12px_-12px_24px_#ffffff]",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-300",
    ),
    extras={
        "inset_shadow": "shadow-[inset_4px_4px_8px_#b8c0c8,inset_-4px_-4px_8px_#ffffff]",
    },
)


# =============================================================================
# 6. CORPORATE THEME
# =============================================================================

CORPORATE_BASE = ThemeConfig(
    name="corporate",
    description="Professional, enterprise-grade design",
    colors=ThemeColors(
        primary="blue-700",
        primary_hover="blue-800",
        secondary="slate-600",
        accent="emerald-500",
    ),
    backgrounds=ThemeBackgrounds(
        background="white",
        background_dark="slate-900",
        surface="slate-50",
        surface_dark="slate-800",
    ),
    text=ThemeText(
        text="slate-800",
        text_dark="slate-100",
        text_muted="slate-500",
    ),
    borders=ThemeBorders(
        border="slate-200",
        border_dark="slate-700",
        border_radius="rounded-lg",
    ),
    shadows=ThemeShadows(
        shadow="shadow-md",
        shadow_hover="shadow-lg",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-200",
    ),
    extras={
        "heading_weight": "font-semibold",
        "button_style": "uppercase tracking-wider",
    },
)


# =============================================================================
# 7. GRADIENT THEME
# =============================================================================

GRADIENT_BASE = ThemeConfig(
    name="gradient",
    description="Vibrant gradient-heavy design",
    colors=ThemeColors(
        primary="violet-600",
        primary_hover="violet-700",
        secondary="fuchsia-500",
        accent="cyan-400",
    ),
    backgrounds=ThemeBackgrounds(
        background="white",
        background_dark="slate-950",
        surface="slate-50",
        surface_dark="slate-900",
    ),
    text=ThemeText(
        text="slate-900",
        text_dark="white",
        text_muted="slate-500",
    ),
    borders=ThemeBorders(
        border="slate-200",
        border_dark="slate-700",
        border_radius="rounded-2xl",
    ),
    shadows=ThemeShadows(
        shadow="shadow-lg shadow-violet-500/10",
        shadow_hover="shadow-xl shadow-violet-500/20",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-200",
    ),
    extras={
        "gradient_primary": "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500",
        "gradient_secondary": "bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500",
        "gradient_text": "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500 bg-clip-text text-transparent",
    },
)


# =============================================================================
# 8. CYBERPUNK THEME
# =============================================================================

CYBERPUNK_BASE = ThemeConfig(
    name="cyberpunk",
    description="Neon-lit, dark futuristic design",
    colors=ThemeColors(
        primary="cyan-400",
        primary_hover="cyan-300",
        secondary="fuchsia-500",
        accent="yellow-400",
    ),
    backgrounds=ThemeBackgrounds(
        background="slate-950",
        background_dark="black",
        surface="slate-900",
        surface_dark="slate-950",
    ),
    text=ThemeText(
        text="cyan-50",
        text_dark="cyan-50",
        text_muted="slate-400",
    ),
    borders=ThemeBorders(
        border="cyan-500/30",
        border_dark="cyan-400/20",
        border_radius="rounded-lg",
    ),
    shadows=ThemeShadows(
        shadow="shadow-lg shadow-cyan-500/20",
        shadow_hover="shadow-xl shadow-cyan-500/40",
    ),
    style=ThemeStyle(
        font="font-mono",
        transition="transition-all duration-200",
    ),
    extras={
        "glow_primary": "shadow-[0_0_15px_rgba(34,211,238,0.3)]",
        "text_neon": "text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]",
        "scanline_effect": False,
    },
)


# =============================================================================
# 9. RETRO THEME
# =============================================================================

RETRO_BASE = ThemeConfig(
    name="retro",
    description="80s/90s inspired nostalgic design",
    colors=ThemeColors(
        primary="fuchsia-500",
        primary_hover="fuchsia-600",
        secondary="cyan-400",
        accent="yellow-400",
    ),
    backgrounds=ThemeBackgrounds(
        background="slate-900",
        background_dark="black",
        surface="slate-800",
        surface_dark="slate-900",
    ),
    text=ThemeText(
        text="fuchsia-100",
        text_dark="fuchsia-100",
        text_muted="slate-400",
    ),
    borders=ThemeBorders(
        border="fuchsia-500/30",
        border_dark="fuchsia-400/20",
        border_radius="rounded-none",
    ),
    shadows=ThemeShadows(
        shadow="shadow-lg shadow-fuchsia-500/20",
        shadow_hover="shadow-xl shadow-fuchsia-500/40",
    ),
    style=ThemeStyle(
        font="font-mono",
        transition="transition-all duration-200",
    ),
    extras={
        "heading_style": "uppercase tracking-[0.2em]",
    },
)


# =============================================================================
# 10. PASTEL THEME
# =============================================================================

PASTEL_BASE = ThemeConfig(
    name="pastel",
    description="Soft, accessible pastel colors",
    colors=ThemeColors(
        primary="rose-600",
        primary_hover="rose-700",
        secondary="sky-600",
        accent="violet-600",
    ),
    backgrounds=ThemeBackgrounds(
        background="rose-50",
        background_dark="slate-800",
        surface="rose-100",
        surface_dark="slate-700",
    ),
    text=ThemeText(
        text="rose-900",
        text_dark="slate-200",
        text_muted="rose-700",
    ),
    borders=ThemeBorders(
        border="rose-200",
        border_dark="slate-600",
        border_radius="rounded-2xl",
    ),
    shadows=ThemeShadows(
        shadow="shadow-md shadow-rose-200/50",
        shadow_hover="shadow-lg shadow-rose-300/50",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-300",
    ),
    extras={
        "wcag_compliant": True,
    },
)


# =============================================================================
# 11. DARK MODE FIRST THEME
# =============================================================================

DARK_MODE_FIRST_BASE = ThemeConfig(
    name="dark-mode-first",
    description="Dark-optimized design with accent glows",
    colors=ThemeColors(
        primary="emerald-500",
        primary_hover="emerald-400",
        secondary="cyan-500",
        accent="amber-500",
    ),
    backgrounds=ThemeBackgrounds(
        background="slate-950",
        background_dark="black",
        surface="slate-900",
        surface_dark="slate-950",
    ),
    text=ThemeText(
        text="slate-100",
        text_dark="slate-100",
        text_muted="slate-400",
    ),
    borders=ThemeBorders(
        border="slate-700",
        border_dark="slate-800",
        border_radius="rounded-xl",
    ),
    shadows=ThemeShadows(
        shadow="shadow-lg shadow-emerald-500/10",
        shadow_hover="shadow-xl shadow-emerald-500/20",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-200",
    ),
    extras={
        "glow_primary": "shadow-[0_0_20px_rgba(16,185,129,0.2)]",
    },
)


# =============================================================================
# 12. HIGH CONTRAST THEME
# =============================================================================

HIGH_CONTRAST_BASE = ThemeConfig(
    name="high-contrast",
    description="WCAG AAA compliant high contrast design",
    colors=ThemeColors(
        primary="blue-700",
        primary_hover="blue-800",
        secondary="slate-900",
        accent="amber-600",
    ),
    backgrounds=ThemeBackgrounds(
        background="white",
        background_dark="black",
        surface="slate-50",
        surface_dark="slate-950",
    ),
    text=ThemeText(
        text="black",
        text_dark="white",
        text_muted="slate-700",
    ),
    borders=ThemeBorders(
        border="black",
        border_dark="white",
        border_radius="rounded-lg",
        border_width="border-2",
    ),
    shadows=ThemeShadows(
        shadow="shadow-md",
        shadow_hover="shadow-lg",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-150",
    ),
    extras={
        "focus_ring": "ring-4 ring-blue-700 ring-offset-2",
    },
    metadata={
        "wcag_level": "AAA",
        "min_contrast_ratio": 7.0,
    },
)


# =============================================================================
# 13. NATURE THEME
# =============================================================================

NATURE_BASE = ThemeConfig(
    name="nature",
    description="Earth-inspired organic design",
    colors=ThemeColors(
        primary="lime-500",
        primary_hover="lime-600",
        secondary="emerald-500",
        accent="pink-400",
    ),
    backgrounds=ThemeBackgrounds(
        background="lime-50",
        background_dark="stone-900",
        surface="white",
        surface_dark="stone-800",
    ),
    text=ThemeText(
        text="emerald-900",
        text_dark="stone-100",
        text_muted="emerald-600",
    ),
    borders=ThemeBorders(
        border="lime-200",
        border_dark="stone-700",
        border_radius="rounded-3xl",
    ),
    shadows=ThemeShadows(
        shadow="shadow-lg shadow-lime-500/10",
        shadow_hover="shadow-xl shadow-lime-500/20",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-300",
    ),
    extras={
        "organic_shapes": True,
        "border_radius_organic": "rounded-[30%_70%_70%_30%/30%_30%_70%_70%]",
    },
)


# =============================================================================
# 14. STARTUP THEME
# =============================================================================

STARTUP_BASE = ThemeConfig(
    name="startup",
    description="Modern tech startup aesthetic",
    colors=ThemeColors(
        primary="violet-600",
        primary_hover="violet-700",
        secondary="fuchsia-500",
        accent="lime-400",
    ),
    backgrounds=ThemeBackgrounds(
        background="white",
        background_dark="slate-950",
        surface="slate-50",
        surface_dark="slate-900",
    ),
    text=ThemeText(
        text="slate-900",
        text_dark="slate-100",
        text_muted="slate-500",
    ),
    borders=ThemeBorders(
        border="slate-200",
        border_dark="slate-700",
        border_radius="rounded-xl",
    ),
    shadows=ThemeShadows(
        shadow="shadow-lg shadow-violet-500/10",
        shadow_hover="shadow-xl shadow-violet-500/20",
    ),
    style=ThemeStyle(
        font="font-sans",
        transition="transition-all duration-200",
    ),
    extras={
        "gradient_primary": "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500",
        "personality": ["bold", "unconventional", "energetic"],
    },
)


# =============================================================================
# REGISTER ALL BASES
# =============================================================================

def _register_all_bases() -> None:
    """Register all base themes with the factory."""
    register_base("modern-minimal", MODERN_MINIMAL_BASE)
    register_base("brutalist", BRUTALIST_BASE)
    register_base("glassmorphism", GLASSMORPHISM_BASE)
    register_base("neo-brutalism", NEO_BRUTALISM_BASE)
    register_base("soft-ui", SOFT_UI_BASE)
    register_base("corporate", CORPORATE_BASE)
    register_base("gradient", GRADIENT_BASE)
    register_base("cyberpunk", CYBERPUNK_BASE)
    register_base("retro", RETRO_BASE)
    register_base("pastel", PASTEL_BASE)
    register_base("dark-mode-first", DARK_MODE_FIRST_BASE)
    register_base("dark_mode_first", DARK_MODE_FIRST_BASE)  # Alias with underscore
    register_base("high-contrast", HIGH_CONTRAST_BASE)
    register_base("high_contrast", HIGH_CONTRAST_BASE)  # Alias with underscore
    register_base("nature", NATURE_BASE)
    register_base("startup", STARTUP_BASE)


# Auto-register when module is imported
_register_all_bases()
