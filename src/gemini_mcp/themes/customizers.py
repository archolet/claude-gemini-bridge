"""
Theme customizer functions for Gemini MCP Server.

Each customizer function takes a ThemeConfig and kwargs, then returns
a modified ThemeConfig with the customizations applied.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .config import ThemeConfig, ThemeColors, ThemeBorders, ThemeShadows, ThemeStyle
from .constants import (
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
)
from .factory import register_customizer


def _customize_modern_minimal(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for modern-minimal theme."""
    neutral_base = kwargs.get("neutral_base", "slate")
    border_radius = kwargs.get("border_radius", "lg")
    shadow_intensity = kwargs.get("shadow_intensity", "sm")
    brand = kwargs.get("brand")

    # Update neutral colors based on neutral_base
    neutral_map = {
        "slate": {"bg": "white", "bg_dark": "slate-900", "surface": "slate-50", "surface_dark": "slate-800", "border": "slate-200", "text": "slate-900", "text_dark": "slate-100", "muted": "slate-500"},
        "gray": {"bg": "white", "bg_dark": "gray-900", "surface": "gray-50", "surface_dark": "gray-800", "border": "gray-200", "text": "gray-900", "text_dark": "gray-100", "muted": "gray-500"},
        "zinc": {"bg": "white", "bg_dark": "zinc-900", "surface": "zinc-50", "surface_dark": "zinc-800", "border": "zinc-200", "text": "zinc-900", "text_dark": "zinc-100", "muted": "zinc-500"},
        "neutral": {"bg": "white", "bg_dark": "neutral-900", "surface": "neutral-50", "surface_dark": "neutral-800", "border": "neutral-200", "text": "neutral-900", "text_dark": "neutral-100", "muted": "neutral-500"},
        "stone": {"bg": "white", "bg_dark": "stone-900", "surface": "stone-50", "surface_dark": "stone-800", "border": "stone-200", "text": "stone-900", "text_dark": "stone-100", "muted": "stone-500"},
    }

    colors = neutral_map.get(neutral_base, neutral_map["slate"])

    config.backgrounds.background = colors["bg"]
    config.backgrounds.background_dark = colors["bg_dark"]
    config.backgrounds.surface = colors["surface"]
    config.backgrounds.surface_dark = colors["surface_dark"]
    config.borders.border = colors["border"]
    config.text.text = colors["text"]
    config.text.text_dark = colors["text_dark"]
    config.text.text_muted = colors["muted"]

    # Apply border radius
    radius_map = {
        "none": "rounded-none",
        "sm": "rounded-sm",
        "md": "rounded-md",
        "lg": "rounded-lg",
        "xl": "rounded-xl",
        "2xl": "rounded-2xl",
        "full": "rounded-full",
    }
    config.borders.border_radius = radius_map.get(border_radius, "rounded-lg")

    # Apply shadow intensity
    shadow_map = {
        "none": ("shadow-none", "shadow-none"),
        "sm": ("shadow-sm", "shadow-md"),
        "md": ("shadow-md", "shadow-lg"),
        "lg": ("shadow-lg", "shadow-xl"),
    }
    shadows = shadow_map.get(shadow_intensity, ("shadow-sm", "shadow-md"))
    config.shadows.shadow = shadows[0]
    config.shadows.shadow_hover = shadows[1]

    # Apply brand colors if provided
    if brand:
        config.colors.primary = brand.primary
        config.colors.primary_hover = brand.primary_hover
        config.colors.secondary = brand.secondary
        config.colors.accent = brand.accent

    return config


def _customize_brutalist(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for brutalist theme."""
    contrast_mode = kwargs.get("contrast_mode", "standard")
    accent_color = kwargs.get("accent_color", "yellow")
    enable_animations = kwargs.get("enable_animations", False)
    border_width = kwargs.get("border_width", "4")
    shadow_offset = kwargs.get("shadow_offset", "md")

    # Map contrast modes to color configurations
    # BRUTALIST_CONTRAST_PAIRS has color keys like "white", "black"
    # but we accept mode names like "standard", "high", "maximum"
    contrast_configs = {
        "standard": {
            "primary": "black",
            "secondary": "white",
            "background": "white",
            "text": "black",
        },
        "high": {
            "primary": "black",
            "secondary": "white",
            "background": "white",
            "text": "black",
        },
        "maximum": {
            "primary": "black",
            "secondary": "yellow-400",
            "background": "yellow-400",
            "text": "black",
        },
    }
    contrast_config = contrast_configs.get(contrast_mode, contrast_configs["standard"])
    config.colors.primary = contrast_config["primary"]
    config.colors.secondary = contrast_config["secondary"]
    config.text.text = contrast_config["text"]
    config.backgrounds.background = contrast_config["background"]

    # Apply accent color
    accent_map = {
        "yellow": "yellow-400",
        "red": "red-500",
        "cyan": "cyan-400",
        "pink": "pink-500",
        "lime": "lime-400",
    }
    config.colors.accent = accent_map.get(accent_color, "yellow-400")

    # Apply border width
    config.borders.border_width = f"border-{border_width}"

    # Apply shadow offset
    offset_map = {
        "sm": ("shadow-[2px_2px_0px_#000]", "shadow-[4px_4px_0px_#000]"),
        "md": ("shadow-[4px_4px_0px_#000]", "shadow-[6px_6px_0px_#000]"),
        "lg": ("shadow-[6px_6px_0px_#000]", "shadow-[8px_8px_0px_#000]"),
    }
    shadows = offset_map.get(shadow_offset, offset_map["md"])
    config.shadows.shadow = shadows[0]
    config.shadows.shadow_hover = shadows[1]

    # Apply animations
    if enable_animations:
        config.style.transition = "transition-all duration-150 ease-out"
    else:
        config.style.transition = "transition-none"

    # Store metadata for configuration parameters
    config.metadata["enable_animations"] = enable_animations
    config.metadata["border_width"] = border_width
    config.metadata["shadow_offset"] = shadow_offset

    return config


def _customize_glassmorphism(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for glassmorphism theme."""
    blur_intensity = kwargs.get("blur_intensity", "xl")
    opacity = kwargs.get("opacity", 0.7)
    tint_color = kwargs.get("tint_color", "white")
    performance_mode = kwargs.get("performance_mode", "balanced")

    # Clamp opacity
    opacity = max(0.3, min(0.95, opacity))

    # Apply blur based on performance mode
    performance_blur_limits = {
        "quality": "3xl",
        "balanced": "2xl",
        "performance": "lg",
    }

    blur_scale = ["sm", "md", "lg", "xl", "2xl", "3xl"]
    max_blur = performance_blur_limits.get(performance_mode, "2xl")
    max_idx = blur_scale.index(max_blur) if max_blur in blur_scale else 4
    req_idx = blur_scale.index(blur_intensity) if blur_intensity in blur_scale else 3
    actual_blur = blur_scale[min(req_idx, max_idx)]

    # Update extras
    config.extras["blur"] = f"backdrop-blur-{actual_blur}"
    config.extras["opacity"] = opacity
    config.extras["tint_color"] = tint_color
    config.extras["glass_surface"] = f"bg-{tint_color}/[{opacity}]"

    return config


def _customize_neo_brutalism(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for neo-brutalism theme."""
    gradient_preset = kwargs.get("gradient_preset", "sunset")
    animation = kwargs.get("animation", "flow")
    animation_speed = kwargs.get("animation_speed", "normal")
    shadow_color = kwargs.get("shadow_color", "black")
    include_hover_animations = kwargs.get("include_hover_animations", True)

    # Apply gradient
    gradient = NEOBRUTALISM_GRADIENTS.get(gradient_preset, NEOBRUTALISM_GRADIENTS["sunset"])
    colors = gradient["colors"]
    gradient_class = f"bg-gradient-{gradient['angle']} from-{colors[0]} via-{colors[1]} to-{colors[2]}"

    config.extras["gradient_class"] = gradient_class
    config.extras["gradient_colors"] = colors

    # Apply animation
    # GRADIENT_ANIMATIONS structure: {"keyframes": "...", "class": "..."}
    if animation != "none":
        anim_config = GRADIENT_ANIMATIONS.get(animation, GRADIENT_ANIMATIONS["flow"])
        config.extras["animation"] = animation
        config.extras["animation_class"] = anim_config["class"]
        config.extras["animation_keyframes"] = anim_config["keyframes"]

    # Apply shadow color
    if shadow_color != "black":
        config.shadows.shadow = f"shadow-[4px_4px_0px_{shadow_color}]"
        config.shadows.shadow_hover = f"shadow-[6px_6px_0px_{shadow_color}]"

    # Apply hover animations
    if include_hover_animations:
        config.style.transition = "transition-all duration-200 ease-out"
        config.extras["hover_transform"] = "hover:-translate-y-1"

    return config


def _customize_soft_ui(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for soft-ui (neumorphism) theme."""
    base_color_light = kwargs.get("base_color_light", "slate-100")
    base_color_dark = kwargs.get("base_color_dark", "slate-800")
    primary_color = kwargs.get("primary_color", "blue-500")
    intensity = kwargs.get("intensity", "medium")
    color_temperature = kwargs.get("color_temperature", "neutral")
    surface_variant = kwargs.get("surface_variant", "raised")
    glow_color = kwargs.get("glow_color")
    enable_inner_shadow = kwargs.get("enable_inner_shadow", True)

    # Update name to include configuration
    config.name = f"{color_temperature} {intensity}"

    # Apply base colors
    config.backgrounds.background = base_color_light
    config.backgrounds.background_dark = base_color_dark
    config.colors.primary = primary_color

    # Apply intensity
    intensity_settings = {
        "subtle": {
            "shadow_light": "shadow-[3px_3px_6px_#b8b9be,-3px_-3px_6px_#ffffff]",
            "shadow_dark": "shadow-[3px_3px_6px_#1a1a1a,-3px_-3px_6px_#262626]",
            "inset_shadow": "shadow-[inset_2px_2px_4px_#b8b9be,inset_-2px_-2px_4px_#ffffff]",
        },
        "medium": {
            "shadow_light": "shadow-[5px_5px_10px_#b8b9be,-5px_-5px_10px_#ffffff]",
            "shadow_dark": "shadow-[5px_5px_10px_#1a1a1a,-5px_-5px_10px_#262626]",
            "inset_shadow": "shadow-[inset_3px_3px_6px_#b8b9be,inset_-3px_-3px_6px_#ffffff]",
        },
        "strong": {
            "shadow_light": "shadow-[8px_8px_16px_#b8b9be,-8px_-8px_16px_#ffffff]",
            "shadow_dark": "shadow-[8px_8px_16px_#1a1a1a,-8px_-8px_16px_#262626]",
            "inset_shadow": "shadow-[inset_4px_4px_8px_#b8b9be,inset_-4px_-4px_8px_#ffffff]",
        },
    }

    settings = intensity_settings.get(intensity, intensity_settings["medium"])
    config.extras["shadow_light"] = settings["shadow_light"]
    config.extras["shadow_dark"] = settings["shadow_dark"]

    # Apply color temperature
    temp_settings = {
        "cool": {"surface": "slate-50", "accent": "blue", "text": "blue-800", "text_muted": "blue-600"},
        "neutral": {"surface": "gray-50", "accent": "slate", "text": "slate-700", "text_muted": "slate-500"},
        "warm": {"surface": "stone-50", "accent": "amber", "text": "amber-900", "text_muted": "amber-700"},
    }
    temp = temp_settings.get(color_temperature, temp_settings["neutral"])
    config.backgrounds.surface = temp["surface"]
    config.text.text = temp["text"]
    config.text.text_muted = temp["text_muted"]

    # Apply surface variant
    if surface_variant == "inset":
        config.extras["surface_style"] = "inset"
    elif surface_variant == "flat":
        config.extras["surface_style"] = "flat"
    else:
        config.extras["surface_style"] = "raised"

    # Apply glow - only set if explicitly provided
    if glow_color is not None:
        config.extras["glow_color"] = glow_color

    # Apply inner shadow
    config.extras["enable_inner_shadow"] = enable_inner_shadow

    # Generate card variants
    config.extras["card_raised"] = settings["shadow_light"]
    config.extras["card_flat"] = "shadow-none"
    config.extras["card_inset"] = settings["inset_shadow"]

    # Store metadata for configuration parameters
    config.metadata["color_temperature"] = color_temperature
    config.metadata["surface_variant"] = surface_variant
    config.metadata["glow_color"] = glow_color  # Keep None if not specified
    config.metadata["enable_inner_shadow"] = enable_inner_shadow

    return config


def _customize_corporate(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for corporate theme."""
    industry = kwargs.get("industry", "consulting")
    layout = kwargs.get("layout", "modern")
    formality = kwargs.get("formality", "semi-formal")
    include_accent_gradients = kwargs.get("include_accent_gradients", False)

    # Apply industry settings
    ind = CORPORATE_INDUSTRIES.get(industry, CORPORATE_INDUSTRIES["consulting"])
    config.colors.primary = ind["primary"]
    config.colors.secondary = ind["secondary"]
    config.colors.accent = ind["accent"]
    config.extras["industry_icon"] = ind.get("icon", "")

    # Apply layout settings
    lay = CORPORATE_LAYOUTS.get(layout, CORPORATE_LAYOUTS["modern"])
    config.extras["max_width"] = lay.get("max_width", "max-w-7xl")
    config.extras["grid_cols"] = lay.get("grid_cols", "3")
    config.extras["spacing"] = lay.get("spacing", "space-y-8")

    # Apply formality settings
    form = FORMALITY_TYPOGRAPHY.get(formality, FORMALITY_TYPOGRAPHY["semi-formal"])
    config.style.font = form.get("font", "font-sans")
    config.extras["heading_weight"] = form.get("heading_weight", "font-bold")
    config.extras["button_style"] = form.get("button_style", "normal-case")

    # Apply accent gradients
    if include_accent_gradients:
        config.extras["accent_gradient"] = f"bg-gradient-to-r from-{config.colors.primary} to-{config.colors.accent}"

    return config


def _customize_gradient(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for gradient theme."""
    primary_gradient = kwargs.get("primary_gradient", "aurora")
    secondary_gradient = kwargs.get("secondary_gradient", "ocean")
    button_style = kwargs.get("button_style", "gradient")
    card_style = kwargs.get("card_style", "subtle")
    dark_mode_gradient = kwargs.get("dark_mode_gradient", "dark_aurora")
    include_animations = kwargs.get("include_animations", True)

    # Get gradient configs
    primary = GRADIENT_LIBRARY.get(primary_gradient, GRADIENT_LIBRARY["aurora"])
    secondary = GRADIENT_LIBRARY.get(secondary_gradient, GRADIENT_LIBRARY["ocean"])
    dark_bg = GRADIENT_LIBRARY.get(dark_mode_gradient, GRADIENT_LIBRARY.get("dark_aurora", GRADIENT_LIBRARY["aurora"]))

    # Apply gradients
    config.extras["primary_gradient"] = primary
    config.extras["secondary_gradient"] = secondary
    config.extras["dark_gradient"] = dark_bg
    config.extras["button_style"] = button_style
    config.extras["card_style"] = card_style

    # Apply animations
    if include_animations:
        config.extras["gradient_animation"] = "animate-gradient"
        config.style.transition = "transition-all duration-300"

    return config


def _customize_cyberpunk(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for cyberpunk theme."""
    primary_neon = kwargs.get("primary_neon", "cyan")
    secondary_neon = kwargs.get("secondary_neon", "fuchsia")
    glow_intensity = kwargs.get("glow_intensity", "medium")
    enable_animations = kwargs.get("enable_animations", True)
    scanline_effect = kwargs.get("scanline_effect", False)

    # Get neon colors
    # NEON_COLORS structure: {"hex": "#...", "rgb": "r, g, b", "tailwind": "color-shade"}
    primary = NEON_COLORS.get(primary_neon, NEON_COLORS["cyan"])
    secondary = NEON_COLORS.get(secondary_neon, NEON_COLORS["fuchsia"])

    # Apply neon colors using tailwind values
    config.colors.primary = primary["tailwind"]
    # Create brighter versions for hover states
    config.colors.primary_hover = primary["tailwind"].replace("-400", "-300").replace("-500", "-400")
    config.colors.secondary = secondary["tailwind"]
    config.colors.accent = secondary["tailwind"].replace("-400", "-300").replace("-500", "-400")

    # Apply glow intensity
    glow = GLOW_INTENSITIES.get(glow_intensity, GLOW_INTENSITIES["medium"])
    config.extras["glow_blur"] = glow["blur"]
    config.extras["glow_spread"] = glow["spread"]
    config.extras["primary_glow"] = f"shadow-[0_0_{glow['blur']}_rgba({primary['rgb']},{glow['opacity']})]"
    config.extras["secondary_glow"] = f"shadow-[0_0_{glow['blur']}_rgba({secondary['rgb']},{glow['opacity']})]"

    # Apply animations
    if enable_animations:
        config.extras["neon_animation"] = "animate-pulse"
        config.style.transition = "transition-all duration-300"

    # Apply scanline effect
    if scanline_effect:
        config.extras["scanline"] = True
        config.extras["scanline_opacity"] = "0.1"

    return config


def _customize_retro(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for retro theme."""
    era = kwargs.get("era", "80s_neon")
    color_scheme = kwargs.get("color_scheme", "neon")
    enable_crt_effects = kwargs.get("enable_crt_effects", False)

    # Apply font pairing
    fonts = RETRO_FONT_PAIRINGS.get(era, RETRO_FONT_PAIRINGS["80s_neon"])
    config.style.font = fonts.get("heading", "font-mono")
    config.extras["body_font"] = fonts.get("body", "font-sans")
    config.extras["accent_font"] = fonts.get("accent", "font-mono")

    # Apply color scheme
    color_schemes = {
        "neon": {"primary": "fuchsia-500", "secondary": "cyan-400", "accent": "yellow-400", "background": "slate-900", "surface": "slate-800"},
        "pastel": {"primary": "pink-400", "secondary": "sky-400", "accent": "lime-400", "background": "amber-50", "surface": "white"},
        "earthy": {"primary": "orange-600", "secondary": "teal-600", "accent": "amber-500", "background": "stone-100", "surface": "white"},
        "chrome": {"primary": "slate-400", "secondary": "blue-400", "accent": "amber-400", "background": "slate-900", "surface": "slate-800"},
    }

    scheme = color_schemes.get(color_scheme, color_schemes["neon"])
    config.colors.primary = scheme["primary"]
    config.colors.secondary = scheme["secondary"]
    config.colors.accent = scheme["accent"]
    config.backgrounds.background = scheme["background"]
    config.backgrounds.surface = scheme["surface"]

    # Apply CRT effects
    if enable_crt_effects:
        config.extras["crt_effect"] = True
        config.extras["crt_scanlines"] = True
        config.extras["crt_curvature"] = True

    return config


def _customize_pastel(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for pastel theme."""
    primary_pastel = kwargs.get("primary_pastel", "rose")
    secondary_pastel = kwargs.get("secondary_pastel", "sky")
    wcag_level = kwargs.get("wcag_level", "AA")
    dark_mode_handling = kwargs.get("dark_mode_handling", "desaturate")

    # Get pastel color pairs
    primary = PASTEL_ACCESSIBLE_PAIRS.get(primary_pastel, PASTEL_ACCESSIBLE_PAIRS["rose"])
    secondary = PASTEL_ACCESSIBLE_PAIRS.get(secondary_pastel, PASTEL_ACCESSIBLE_PAIRS["sky"])

    # Apply colors
    config.colors.primary = primary["bg"]
    config.colors.primary_hover = primary.get("hover", primary["bg"])
    config.colors.secondary = secondary["bg"]
    config.colors.accent = secondary.get("accent", primary["bg"])

    # Apply WCAG-compliant text colors
    if wcag_level == "AAA":
        config.text.text = primary.get("text_safe", "slate-900")
        config.text.text_muted = primary.get("text_medium", "slate-600")
    else:
        config.text.text = primary.get("text_safe", "slate-800")
        config.text.text_muted = primary.get("text_medium", "slate-500")

    # Apply dark mode handling
    config.extras["dark_mode_handling"] = dark_mode_handling
    if dark_mode_handling == "vibrant":
        config.extras["dark_saturation"] = "saturate-150"
    elif dark_mode_handling == "invert":
        config.extras["dark_invert"] = True

    return config


def _customize_dark_mode_first(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for dark-mode-first theme."""
    primary_glow = kwargs.get("primary_glow", "emerald")
    contrast_level = kwargs.get("contrast_level", "normal")
    light_mode_style = kwargs.get("light_mode_style", "minimal")

    # Glow color configurations
    glow_colors = {
        "emerald": {"primary": "emerald-500", "primary_hover": "emerald-400", "glow": "emerald-500/20", "light_accent": "emerald-600"},
        "cyan": {"primary": "cyan-400", "primary_hover": "cyan-300", "glow": "cyan-400/20", "light_accent": "cyan-600"},
        "violet": {"primary": "violet-500", "primary_hover": "violet-400", "glow": "violet-500/20", "light_accent": "violet-600"},
        "amber": {"primary": "amber-500", "primary_hover": "amber-400", "glow": "amber-500/20", "light_accent": "amber-600"},
    }

    glow = glow_colors.get(primary_glow, glow_colors["emerald"])

    config.colors.primary = glow["primary"]
    config.colors.primary_hover = glow["primary_hover"]
    config.extras["glow_class"] = f"shadow-lg shadow-{glow['glow']}"
    config.extras["light_accent"] = glow["light_accent"]

    # Apply contrast level
    if contrast_level == "high":
        config.text.text_dark = "white"
        config.backgrounds.background_dark = "black"

    # Apply light mode style
    light_styles = {
        "minimal": {"background": "white", "surface": "slate-50"},
        "warm": {"background": "amber-50", "surface": "orange-50"},
        "cool": {"background": "sky-50", "surface": "blue-50"},
        "inverted": {"background": "slate-100", "surface": "slate-200"},
    }

    style = light_styles.get(light_mode_style, light_styles["minimal"])
    config.backgrounds.background = style["background"]
    config.backgrounds.surface = style["surface"]

    return config


def _customize_high_contrast(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for high-contrast theme."""
    softness_level = kwargs.get("softness_level", "balanced")
    color_scheme = kwargs.get("color_scheme", "blue")
    animation_preference = kwargs.get("animation_preference", "reduced")

    # Apply softness
    softness_settings = {
        "sharp": {"radius": "rounded-none", "transition": "transition-none", "shadow": "shadow-none", "border_style": "border-2"},
        "balanced": {"radius": "rounded-md", "transition": "transition-colors duration-150", "shadow": "shadow-sm", "border_style": "border-2"},
        "smooth": {"radius": "rounded-lg", "transition": "transition-all duration-200 ease-out", "shadow": "shadow-md", "border_style": "border"},
    }

    soft = softness_settings.get(softness_level, softness_settings["balanced"])
    config.borders.border_radius = soft["radius"]
    config.style.transition = soft["transition"]
    config.shadows.shadow = soft["shadow"]
    config.borders.border_width = soft["border_style"]

    # Apply color scheme
    color_schemes = {
        "blue": {"primary": "blue-700", "secondary": "blue-900", "accent": "amber-500"},
        "purple": {"primary": "purple-700", "secondary": "purple-900", "accent": "yellow-500"},
        "green": {"primary": "green-700", "secondary": "green-900", "accent": "orange-500"},
        "neutral": {"primary": "slate-900", "secondary": "slate-700", "accent": "blue-600"},
    }

    scheme = color_schemes.get(color_scheme, color_schemes["blue"])
    config.colors.primary = scheme["primary"]
    config.colors.secondary = scheme["secondary"]
    config.colors.accent = scheme["accent"]

    # Apply animation preference
    if animation_preference == "none":
        config.style.transition = "transition-none"
        config.extras["prefers_reduced_motion"] = True
    elif animation_preference == "reduced":
        config.style.transition = "transition-colors duration-100"
        config.extras["prefers_reduced_motion"] = True

    return config


def _customize_nature(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for nature theme."""
    season = kwargs.get("season", "spring")
    organic_shapes = kwargs.get("organic_shapes", True)
    eco_friendly_mode = kwargs.get("eco_friendly_mode", False)

    # Get season config
    s = NATURE_SEASONS.get(season, NATURE_SEASONS["spring"])

    config.colors.primary = s["primary"]
    config.colors.secondary = s["secondary"]
    config.colors.accent = s["accent"]
    config.backgrounds.background = s["background"]
    config.backgrounds.surface = s["surface"]

    # Apply organic shapes
    if organic_shapes:
        config.borders.border_radius = "rounded-3xl"
        config.extras["organic_radius"] = "rounded-[30%_70%_70%_30%/30%_30%_70%_70%]"
        config.extras["button_radius"] = "rounded-full"
    else:
        config.borders.border_radius = "rounded-lg"

    # Apply eco-friendly mode (reduced animations, simpler visuals)
    if eco_friendly_mode:
        config.style.transition = "transition-none"
        config.shadows.shadow = "shadow-none"
        config.shadows.shadow_hover = "shadow-sm"
        config.extras["eco_mode"] = True

    return config


def _customize_startup(config: ThemeConfig, kwargs: Dict[str, Any]) -> ThemeConfig:
    """Customizer for startup theme."""
    archetype = kwargs.get("archetype", "disruptor")
    stage = kwargs.get("stage", "growth")
    enable_motion = kwargs.get("enable_motion", True)

    # Get archetype config
    arch = STARTUP_ARCHETYPES.get(archetype, STARTUP_ARCHETYPES["disruptor"])

    config.colors.primary = arch["primary"]
    config.colors.secondary = arch["secondary"]
    config.colors.accent = arch["accent"]
    config.style.font = arch.get("font", "font-sans")

    # Apply stage settings
    stage_settings = {
        "seed": {"boldness": "high", "shadow": "shadow-lg", "shadow_hover": "shadow-xl"},
        "growth": {"boldness": "medium", "shadow": "shadow-md", "shadow_hover": "shadow-lg"},
        "scale": {"boldness": "refined", "shadow": "shadow-sm", "shadow_hover": "shadow-md"},
    }

    st = stage_settings.get(stage, stage_settings["growth"])
    config.shadows.shadow = st["shadow"]
    config.shadows.shadow_hover = st["shadow_hover"]
    config.extras["stage"] = stage
    config.extras["boldness"] = st["boldness"]

    # Apply motion
    if enable_motion:
        config.style.transition = "transition-all duration-300 ease-out"
        config.extras["enable_motion"] = True
    else:
        config.style.transition = "transition-colors duration-150"

    return config


def _register_all_customizers() -> None:
    """Register all theme customizers."""
    register_customizer("modern-minimal", _customize_modern_minimal)
    register_customizer("brutalist", _customize_brutalist)
    register_customizer("glassmorphism", _customize_glassmorphism)
    register_customizer("neo-brutalism", _customize_neo_brutalism)
    register_customizer("soft-ui", _customize_soft_ui)
    register_customizer("corporate", _customize_corporate)
    register_customizer("gradient", _customize_gradient)
    register_customizer("cyberpunk", _customize_cyberpunk)
    register_customizer("retro", _customize_retro)
    register_customizer("pastel", _customize_pastel)
    register_customizer("dark-mode-first", _customize_dark_mode_first)
    register_customizer("dark_mode_first", _customize_dark_mode_first)  # Alias
    register_customizer("high-contrast", _customize_high_contrast)
    register_customizer("high_contrast", _customize_high_contrast)  # Alias
    register_customizer("nature", _customize_nature)
    register_customizer("startup", _customize_startup)


# Auto-register on import
_register_all_customizers()
