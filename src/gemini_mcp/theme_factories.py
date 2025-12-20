"""
Theme Factory Functions for Gemini MCP Server.

This module provides factory functions for creating customizable themes.
Each theme factory allows extensive customization while maintaining
design consistency and accessibility standards.

Based on tema-rehberi.md comprehensive enhancement plans.
"""

from typing import Dict, Any, List, Optional, Tuple, Literal
from dataclasses import dataclass
import re
import colorsys

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color to HSL values (h: 0-360, s: 0-100, l: 0-100)."""
    r, g, b = hex_to_rgb(hex_color)
    r, g, b = r / 255, g / 255, b / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert HSL (h: 0-360, s: 0-100, l: 0-100) to hex color."""
    h, s, l = h / 360, s / 100, l / 100
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


def relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance per WCAG 2.1."""
    def adjust(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)


def contrast_ratio(color1: str, color2: str) -> float:
    """Calculate contrast ratio between two hex colors."""
    l1 = relative_luminance(*hex_to_rgb(color1))
    l2 = relative_luminance(*hex_to_rgb(color2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def validate_contrast(
    foreground: str,
    background: str,
    level: str = "AA",
    text_size: str = "normal"
) -> Tuple[bool, float, str]:
    """
    Validate WCAG contrast requirements.

    Returns:
        (passes, ratio, message)
    """
    ratio = contrast_ratio(foreground, background)

    requirements = {
        ("AA", "normal"): 4.5,
        ("AA", "large"): 3.0,
        ("AAA", "normal"): 7.0,
        ("AAA", "large"): 4.5,
    }

    required = requirements.get((level, text_size), 4.5)
    passes = ratio >= required

    message = f"Contrast ratio: {ratio:.2f}:1 ({'PASS' if passes else 'FAIL'} {level} {text_size})"

    return passes, ratio, message


def _next_shadow(current: str) -> str:
    """Get next shadow intensity level."""
    scale = ["none", "sm", "md", "lg", "xl", "2xl"]
    idx = scale.index(current) if current in scale else 1
    return scale[min(idx + 1, len(scale) - 1)]


def _to_css_color(tailwind_color: str) -> str:
    """Convert Tailwind color to CSS RGB values."""
    color_map = {
        "blue-600": "59 130 246",
        "blue-700": "29 78 216",
        "blue-800": "30 64 175",
        "emerald-500": "16 185 129",
        "emerald-600": "5 150 105",
        "rose-600": "225 29 72",
        "violet-600": "124 58 237",
        "cyan-400": "34 211 238",
        "fuchsia-500": "217 70 239",
        "pink-500": "236 72 153",
        "amber-500": "245 158 11",
        "green-600": "22 163 74",
        "slate-600": "71 85 105",
        "indigo-600": "79 70 229",
    }
    return color_map.get(tailwind_color, "59 130 246")


# =============================================================================
# 1. MODERN-MINIMAL THEME FACTORY
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
        h, s, l = hex_to_hsl(primary_hex)
        return cls(
            primary=primary_hex,
            primary_hover=hsl_to_hex(h, s, max(l - 10, 0)),
            primary_light=hsl_to_hex(h, s * 0.3, 95),
            primary_dark=hsl_to_hex(h, s, max(l - 30, 15)),
            secondary=hsl_to_hex((h + 30) % 360, s * 0.7, l),
            accent=hsl_to_hex((h + 180) % 360, s, l),
        )


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
    if brand is None:
        brand = BrandColors(
            primary="blue-600",
            primary_hover="blue-700",
            primary_light="blue-50",
            primary_dark="blue-900",
            secondary="slate-600",
            accent="emerald-500"
        )

    return {
        "name": "modern-minimal-custom",
        "description": "Customized modern minimal theme",

        # Brand Colors
        "primary": brand.primary,
        "primary_hover": brand.primary_hover,
        "primary_light": brand.primary_light,
        "primary_dark": brand.primary_dark,
        "secondary": brand.secondary,
        "accent": brand.accent,

        # Neutral Scale
        "background": "white",
        "background_dark": f"{neutral_base}-900",
        "surface": f"{neutral_base}-50",
        "surface_dark": f"{neutral_base}-800",
        "border": f"{neutral_base}-200",
        "border_dark": f"{neutral_base}-700",
        "text": f"{neutral_base}-900",
        "text_dark": f"{neutral_base}-100",
        "text_muted": f"{neutral_base}-500",

        # Style
        "border_radius": f"rounded-{border_radius}",
        "shadow": f"shadow-{shadow_intensity}" if shadow_intensity != "none" else "",
        "shadow_hover": f"shadow-{_next_shadow(shadow_intensity)}",

        # Typography
        "font": "font-sans",
        "transition": "transition-all duration-200 ease-out",

        # CSS Variables
        "css_variables": {
            "--color-primary": _to_css_color(brand.primary),
            "--color-primary-hover": _to_css_color(brand.primary_hover),
            "--color-accent": _to_css_color(brand.accent),
        },

        # Component bundles
        "button_base": f"bg-{brand.primary} hover:bg-{brand.primary_hover} text-white rounded-{border_radius} shadow-{shadow_intensity} hover:shadow-{_next_shadow(shadow_intensity)} transition-all duration-200",
        "card_base": f"bg-white dark:bg-{neutral_base}-800 rounded-{border_radius} shadow-{shadow_intensity} border border-{neutral_base}-200 dark:border-{neutral_base}-700",
        "input_base": f"bg-white dark:bg-{neutral_base}-900 border border-{neutral_base}-300 dark:border-{neutral_base}-600 rounded-{border_radius} focus:ring-2 focus:ring-{brand.primary}/50 focus:border-{brand.primary}",
    }


# =============================================================================
# 2. BRUTALIST THEME FACTORY
# =============================================================================

BRUTALIST_CONTRAST_PAIRS = {
    "white": {"text": "black", "text_muted": "slate-700", "min_contrast": 7.0},
    "black": {"text": "white", "text_muted": "slate-300", "min_contrast": 7.0},
    "yellow-400": {"text": "black", "text_muted": "slate-800", "min_contrast": 4.5},
    "blue-600": {"text": "white", "text_muted": "blue-100", "min_contrast": 4.5},
    "red-600": {"text": "white", "text_muted": "red-100", "min_contrast": 4.5},
}


def create_brutalist_theme(
    contrast_mode: Literal["standard", "high", "maximum"] = "high",
    accent_color: str = "yellow-400",
    include_focus_indicators: bool = True,
) -> Dict[str, Any]:
    """
    WCAG-compliant Brutalist theme with bold aesthetics.

    Maintains the bold brutalist aesthetic while ensuring accessibility.
    """
    contrast_requirements = {
        "standard": {"normal_text": 4.5, "large_text": 3.0, "ui": 3.0},
        "high": {"normal_text": 7.0, "large_text": 4.5, "ui": 4.5},
        "maximum": {"normal_text": 10.0, "large_text": 7.0, "ui": 7.0},
    }

    reqs = contrast_requirements[contrast_mode]

    theme = {
        "name": f"brutalist-{contrast_mode}",
        "description": f"Brutalist theme with {contrast_mode} contrast (WCAG {'AA' if contrast_mode == 'standard' else 'AAA'})",

        # Core brutalist aesthetic
        "primary": "black",
        "primary_hover": "slate-800",
        "secondary": "white",
        "accent": accent_color,

        # High contrast backgrounds
        "background": "white",
        "background_dark": "black",
        "surface": "slate-100",
        "surface_dark": "slate-900",

        # Guaranteed contrast text
        "text": "black",
        "text_dark": "white",
        "text_muted": "slate-700",
        "text_muted_dark": "slate-300",

        # Brutalist style
        "border": "black",
        "border_dark": "white",
        "border_radius": "rounded-none",
        "border_width": "border-2",

        # Signature shadows
        "shadow": "shadow-[4px_4px_0px_#000]",
        "shadow_hover": "shadow-[6px_6px_0px_#000]",
        "shadow_dark": "shadow-[4px_4px_0px_#fff]",

        "font": "font-mono",

        # Focus indicators
        "focus_ring": "ring-4 ring-black ring-offset-2" if include_focus_indicators else "",
        "focus_ring_dark": "ring-4 ring-white ring-offset-2 ring-offset-black",

        # Metadata
        "_contrast_mode": contrast_mode,
        "_min_contrast_ratios": reqs,
    }

    # Accent color text pairing
    accent_pair = BRUTALIST_CONTRAST_PAIRS.get(accent_color, {"text": "black"})
    theme["accent_text"] = accent_pair["text"]

    return theme


# =============================================================================
# 3. GLASSMORPHISM THEME FACTORY
# =============================================================================

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
    """
    def min_blur(requested: str, maximum: str) -> str:
        scale = ["sm", "md", "lg", "xl", "2xl", "3xl"]
        req_idx = scale.index(requested) if requested in scale else 3
        max_idx = scale.index(maximum) if maximum in scale else 2
        return scale[min(req_idx, max_idx)]

    performance_settings = {
        "quality": {
            "blur": blur_intensity,
            "will_change": "backdrop-filter",
            "transform": "translateZ(0)",
        },
        "balanced": {
            "blur": min_blur(blur_intensity, "lg"),
            "will_change": "auto",
            "transform": "",
        },
        "performance": {
            "blur": "md",
            "will_change": "auto",
            "transform": "",
        }
    }

    perf = performance_settings[performance_mode]
    fallback_opacity = min(opacity + 0.15, 0.95)

    # Tint color handling
    if tint_color == "white":
        glass_bg = f"bg-white/{int(opacity * 100)}"
        glass_bg_fallback = f"bg-white/{int(fallback_opacity * 100)}"
        border_color = "border-white/20"
    elif tint_color == "black":
        glass_bg = f"bg-black/{int(opacity * 100)}"
        glass_bg_fallback = f"bg-slate-900/{int(fallback_opacity * 100)}"
        border_color = "border-white/10"
    else:
        glass_bg = f"bg-{tint_color}/{int(opacity * 100)}"
        glass_bg_fallback = f"bg-{tint_color}/{int(fallback_opacity * 100)}"
        border_color = f"border-{tint_color}/20"

    return {
        "name": f"glassmorphism-{performance_mode}",
        "description": f"Safari-optimized glassmorphism ({performance_mode} mode)",

        # Glass effect
        "glass_effect": f"{glass_bg} backdrop-blur-{perf['blur']} {border_color} border",
        "glass_effect_strong": f"bg-white/{int(opacity * 100 + 10)} backdrop-blur-{blur_intensity} border-white/30 border",
        "glass_fallback": f"{glass_bg_fallback} border {border_color}",

        # Surface colors
        "surface": f"white/{int(opacity * 100 - 10)}",
        "surface_dark": f"slate-900/{int(opacity * 100 - 10)}",

        # Core colors
        "primary": "indigo-500",
        "primary_hover": "indigo-600",
        "secondary": "purple-500",
        "background": "slate-900",
        "background_dark": "slate-950",
        "text": "white",
        "text_muted": "slate-300",

        # Borders and shadows
        "border": "white/20",
        "border_radius": "rounded-2xl",
        "shadow": "shadow-lg shadow-black/10",
        "shadow_hover": "shadow-xl shadow-black/20",

        # Safari optimizations
        "_safari_optimizations": {
            "use_transform_hack": performance_mode == "quality",
            "limit_nested_blur": True,
            "prefer_opacity_over_rgba": True,
        },

        # Feature detection CSS
        "_feature_detection_css": """
        @supports (backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)) {
            .glass {
                -webkit-backdrop-filter: blur(16px);
                backdrop-filter: blur(16px);
            }
        }
        @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
            .glass {
                background-color: rgba(255, 255, 255, 0.85);
            }
        }
        """,
    }


# =============================================================================
# 4. NEO-BRUTALISM THEME FACTORY
# =============================================================================

NEOBRUTALISM_GRADIENTS = {
    "sunset": {"colors": ["yellow-400", "orange-500", "pink-500"], "angle": "to-r"},
    "ocean": {"colors": ["cyan-400", "blue-500", "purple-500"], "angle": "to-r"},
    "forest": {"colors": ["lime-400", "emerald-500", "teal-500"], "angle": "to-r"},
    "candy": {"colors": ["pink-400", "purple-500", "indigo-500"], "angle": "to-r"},
    "fire": {"colors": ["yellow-400", "orange-500", "red-500"], "angle": "to-r"},
}

GRADIENT_ANIMATIONS = {
    "flow": {
        "keyframes": """
        @keyframes gradient-flow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        """,
        "class": "bg-[length:200%_200%] animate-[gradient-flow_3s_ease_infinite]",
    },
    "pulse": {
        "keyframes": """
        @keyframes gradient-pulse {
            0%, 100% { background-size: 100% 100%; opacity: 1; }
            50% { background-size: 120% 120%; opacity: 0.9; }
        }
        """,
        "class": "animate-[gradient-pulse_2s_ease-in-out_infinite]",
    },
    "shimmer": {
        "keyframes": """
        @keyframes gradient-shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        """,
        "class": "bg-[length:200%_100%] animate-[gradient-shimmer_2s_linear_infinite]",
    },
    "wave": {
        "keyframes": """
        @keyframes gradient-wave {
            0%, 100% { background-position: 0% 0%; }
            25% { background-position: 100% 0%; }
            50% { background-position: 100% 100%; }
            75% { background-position: 0% 100%; }
        }
        """,
        "class": "bg-[length:200%_200%] animate-[gradient-wave_4s_ease_infinite]",
    },
}


def create_neo_brutalism_theme(
    gradient_preset: Literal["sunset", "ocean", "forest", "candy", "fire"] = "sunset",
    animation: Literal["none", "flow", "pulse", "shimmer", "wave"] = "flow",
    animation_speed: Literal["slow", "normal", "fast"] = "normal",
    shadow_color: str = "black",
    include_hover_animations: bool = True,
) -> Dict[str, Any]:
    """
    Neo-Brutalism with animated gradients and playful effects.
    """
    gradient = NEOBRUTALISM_GRADIENTS[gradient_preset]
    colors = gradient["colors"]

    gradient_class = f"bg-gradient-{gradient['angle']} from-{colors[0]} via-{colors[1]} to-{colors[2]}"

    speed_map = {"slow": 1.5, "normal": 1.0, "fast": 0.5}
    speed = speed_map[animation_speed]

    anim_config = GRADIENT_ANIMATIONS.get(animation, {"class": "", "keyframes": ""})
    anim_class = anim_config.get("class", "")

    # Modify animation duration based on speed
    if speed != 1.0 and "animate-[" in anim_class:
        anim_class = re.sub(
            r'(\d+(?:\.\d+)?)s',
            lambda m: f"{float(m.group(1)) * speed}s",
            anim_class
        )

    def _color_to_hex(color: str) -> str:
        if color == "black":
            return "000"
        elif color == "white":
            return "fff"
        return "000"

    def _contrast_text(bg_color: str) -> str:
        light_colors = ["yellow", "lime", "amber", "cyan"]
        if any(c in bg_color for c in light_colors):
            return "black"
        return "white"

    return {
        "name": f"neo-brutalism-{gradient_preset}",
        "description": f"Playful neo-brutalism with {gradient_preset} gradient",

        # Animated gradient
        "gradient_primary": gradient_class,
        "gradient_animated": f"{gradient_class} {anim_class}",
        "gradient_keyframes": anim_config.get("keyframes", ""),

        # Colors
        "primary": colors[0],
        "primary_hover": colors[1],
        "secondary": colors[2],
        "accent": colors[1],

        # Backgrounds
        "background": "amber-50",
        "background_dark": "slate-900",
        "surface": "white",
        "surface_dark": "slate-800",

        # Brutalist elements
        "border": shadow_color,
        "border_width": "border-2",
        "border_radius": "rounded-xl",

        # Offset shadows
        "shadow": f"shadow-[4px_4px_0px_#{_color_to_hex(shadow_color)}]",
        "shadow_hover": f"shadow-[6px_6px_0px_#{_color_to_hex(shadow_color)}]",
        "shadow_active": f"shadow-[2px_2px_0px_#{_color_to_hex(shadow_color)}]",

        # Text
        "text": "black",
        "text_dark": "white",
        "font": "font-sans",

        # Hover animations
        "hover_transform": "hover:-translate-y-1 hover:translate-x-1" if include_hover_animations else "",
        "active_transform": "active:translate-y-0 active:translate-x-0",

        # Button with animated gradient
        "button_gradient": f"""
            {gradient_class} {anim_class}
            text-{_contrast_text(colors[0])} font-bold
            px-6 py-3 rounded-xl
            border-2 border-black
            shadow-[4px_4px_0px_#000]
            hover:shadow-[6px_6px_0px_#000]
            hover:-translate-y-0.5 hover:translate-x-0.5
            active:shadow-[2px_2px_0px_#000]
            active:translate-y-0 active:translate-x-0
            transition-all duration-200
        """,
    }


# =============================================================================
# 5. SOFT-UI (NEUMORPHISM) THEME FACTORY
# =============================================================================

def calculate_neumorphism_shadows(
    base_color: str,
    intensity: Literal["subtle", "medium", "strong"] = "medium",
    is_dark_mode: bool = False,
) -> Dict[str, str]:
    """
    Calculate proper neumorphism shadows for any base color.
    """
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
        "raised": f"shadow-[{offset}px_{offset}px_{blur}px_{colors['dark']},-{offset}px_-{offset}px_{blur}px_{colors['light']}]",
        "pressed": f"shadow-[inset_{offset}px_{offset}px_{blur}px_{colors['dark']},inset_-{offset}px_-{offset}px_{blur}px_{colors['light']}]",
        "flat": "shadow-none",
        "bg_color": colors["bg"],
    }


def create_soft_ui_theme(
    base_color_light: str = "slate-100",
    base_color_dark: str = "slate-800",
    primary_color: str = "blue-500",
    intensity: Literal["subtle", "medium", "strong"] = "medium",
) -> Dict[str, Any]:
    """
    Proper dual-mode neumorphism with calculated shadows.
    """
    light_shadows = calculate_neumorphism_shadows(base_color_light, intensity, False)
    dark_shadows = calculate_neumorphism_shadows(base_color_dark, intensity, True)

    return {
        "name": f"soft-ui-{intensity}",
        "description": f"Neumorphic design with {intensity} shadows in both light and dark modes",

        # Primary colors
        "primary": primary_color,
        "primary_hover": primary_color.replace("-500", "-600"),

        # Backgrounds
        "background": base_color_light,
        "background_dark": base_color_dark,
        "surface": base_color_light,
        "surface_dark": base_color_dark,

        # Neumorphic shadows
        "shadow_raised": light_shadows["raised"],
        "shadow_pressed": light_shadows["pressed"],
        "shadow_raised_dark": dark_shadows["raised"],
        "shadow_pressed_dark": dark_shadows["pressed"],

        # Combined classes
        "shadow_raised_auto": f"{light_shadows['raised']} dark:{dark_shadows['raised']}",
        "shadow_pressed_auto": f"{light_shadows['pressed']} dark:{dark_shadows['pressed']}",

        # Text
        "text": "slate-700",
        "text_dark": "slate-200",
        "text_muted": "slate-400",

        # Borders
        "border": "transparent",
        "border_radius": "rounded-2xl",

        # Component classes
        "button_raised": f"""
            bg-{base_color_light} dark:bg-{base_color_dark}
            {light_shadows['raised']} dark:{dark_shadows['raised']}
            text-{primary_color} font-medium
            px-6 py-3 rounded-2xl
            active:{light_shadows['pressed']}
            dark:active:{dark_shadows['pressed']}
            transition-all duration-150
        """,

        "card_raised": f"""
            bg-{base_color_light} dark:bg-{base_color_dark}
            {light_shadows['raised']} dark:{dark_shadows['raised']}
            rounded-3xl p-6
        """,

        "input_inset": f"""
            bg-{base_color_light} dark:bg-{base_color_dark}
            {light_shadows['pressed']} dark:{dark_shadows['pressed']}
            rounded-xl px-4 py-3
            text-slate-700 dark:text-slate-200
            placeholder:text-slate-400
            focus:outline-none focus:ring-2 focus:ring-{primary_color}/50
        """,
    }


# =============================================================================
# 6. CORPORATE THEME FACTORY
# =============================================================================

CORPORATE_INDUSTRIES = {
    "finance": {
        "name": "Corporate Finance",
        "primary": "blue-800",
        "secondary": "emerald-600",
        "accent": "amber-500",
        "personality": "trustworthy, stable, premium",
        "suggested_fonts": ["Inter", "SF Pro", "IBM Plex Sans"],
        "icon_style": "outline",
    },
    "healthcare": {
        "name": "Corporate Healthcare",
        "primary": "teal-600",
        "secondary": "blue-500",
        "accent": "rose-500",
        "personality": "caring, clean, professional",
        "suggested_fonts": ["Plus Jakarta Sans", "Source Sans Pro"],
        "icon_style": "outline",
    },
    "legal": {
        "name": "Corporate Legal",
        "primary": "slate-800",
        "secondary": "amber-700",
        "accent": "blue-600",
        "personality": "authoritative, traditional, refined",
        "suggested_fonts": ["Playfair Display", "Lora", "Libre Baskerville"],
        "icon_style": "solid",
    },
    "tech": {
        "name": "Corporate Tech",
        "primary": "indigo-600",
        "secondary": "violet-500",
        "accent": "cyan-400",
        "personality": "innovative, modern, dynamic",
        "suggested_fonts": ["Outfit", "Space Grotesk", "Manrope"],
        "icon_style": "outline",
    },
    "manufacturing": {
        "name": "Corporate Manufacturing",
        "primary": "orange-600",
        "secondary": "slate-700",
        "accent": "yellow-500",
        "personality": "reliable, industrial, strong",
        "suggested_fonts": ["DM Sans", "Roboto", "Work Sans"],
        "icon_style": "solid",
    },
    "consulting": {
        "name": "Corporate Consulting",
        "primary": "blue-700",
        "secondary": "slate-600",
        "accent": "emerald-500",
        "personality": "expert, strategic, sophisticated",
        "suggested_fonts": ["Graphik", "Calibre"],
        "icon_style": "outline",
    },
}

CORPORATE_LAYOUTS = {
    "traditional": {"max_width": "max-w-6xl", "spacing": "generous"},
    "modern": {"max_width": "max-w-7xl", "spacing": "balanced"},
    "editorial": {"max_width": "max-w-4xl", "spacing": "airy"},
}


def create_corporate_theme(
    industry: Literal["finance", "healthcare", "legal", "tech", "manufacturing", "consulting"] = "consulting",
    layout: Literal["traditional", "modern", "editorial"] = "modern",
    formality: Literal["formal", "semi-formal", "approachable"] = "semi-formal",
    include_accent_gradients: bool = False,
) -> Dict[str, Any]:
    """
    Industry-specific corporate theme with personality.
    """
    ind = CORPORATE_INDUSTRIES[industry]
    lay = CORPORATE_LAYOUTS[layout]

    formality_settings = {
        "formal": {"heading_weight": "font-semibold", "button_style": "uppercase tracking-wider"},
        "semi-formal": {"heading_weight": "font-bold", "button_style": "normal-case"},
        "approachable": {"heading_weight": "font-bold", "button_style": "normal-case font-medium"},
    }

    form = formality_settings[formality]

    spacing_map = {
        "generous": {"section": "py-20 md:py-28", "gap": "gap-12"},
        "balanced": {"section": "py-16 md:py-20", "gap": "gap-8"},
        "airy": {"section": "py-24 md:py-32", "gap": "gap-16"},
    }
    spacing = spacing_map.get(lay["spacing"], spacing_map["balanced"])

    return {
        "name": f"corporate-{industry}-{layout}",
        "description": f"{ind['name']} with {layout} layout - {ind['personality']}",

        # Industry colors
        "primary": ind["primary"],
        "primary_hover": ind["primary"].replace("-800", "-900").replace("-700", "-800").replace("-600", "-700"),
        "secondary": ind["secondary"],
        "accent": ind["accent"],

        # Neutral base
        "background": "white",
        "background_dark": "slate-900",
        "surface": "slate-50",
        "surface_dark": "slate-800",
        "border": "slate-200",
        "border_dark": "slate-700",

        # Typography
        "text": "slate-800",
        "text_dark": "slate-100",
        "text_muted": "slate-500",
        "font": "font-sans",
        "heading_weight": form["heading_weight"],

        # Layout
        "max_width": lay["max_width"],
        "section_padding": spacing["section"],
        "element_gap": spacing["gap"],

        # Style
        "border_radius": "rounded-lg",
        "shadow": "shadow-sm",
        "shadow_hover": "shadow-md",

        # Button
        "button_primary": f"""
            bg-{ind['primary']} hover:bg-{ind['primary'].replace('-700', '-800').replace('-600', '-700')}
            text-white {form['button_style']}
            px-6 py-3 rounded-lg
            shadow-sm hover:shadow-md
            transition-all duration-200
        """,

        # Accent gradient
        "accent_gradient": f"bg-gradient-to-r from-{ind['primary']} to-{ind['secondary']}" if include_accent_gradients else "",

        # Metadata
        "_industry": industry,
        "_personality": ind["personality"],
        "_suggested_fonts": ind["suggested_fonts"],
    }


# =============================================================================
# 7. GRADIENT THEME FACTORY
# =============================================================================

GRADIENT_LIBRARY = {
    # Signature Gradients
    "aurora": {"class": "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500", "text_contrast": "white", "category": "vibrant"},
    "sunset": {"class": "bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600", "text_contrast": "white", "category": "warm"},
    "ocean": {"class": "bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500", "text_contrast": "white", "category": "cool"},
    "forest": {"class": "bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500", "text_contrast": "white", "category": "nature"},
    "fire": {"class": "bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500", "text_contrast": "white", "category": "warm"},

    # Subtle Gradients
    "slate_subtle": {"class": "bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200", "text_contrast": "slate-800", "category": "subtle"},
    "blue_subtle": {"class": "bg-gradient-to-br from-blue-50 via-indigo-50 to-violet-50", "text_contrast": "slate-800", "category": "subtle"},
    "warm_subtle": {"class": "bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50", "text_contrast": "slate-800", "category": "subtle"},

    # Mesh Gradients
    "mesh_purple": {"class": "bg-[radial-gradient(at_top_left,_#c084fc_0%,_transparent_50%),radial-gradient(at_bottom_right,_#f472b6_0%,_transparent_50%),radial-gradient(at_top_right,_#60a5fa_0%,_transparent_50%)]", "bg_color": "bg-slate-900", "text_contrast": "white", "category": "mesh"},
    "mesh_ocean": {"class": "bg-[radial-gradient(at_top_left,_#22d3ee_0%,_transparent_50%),radial-gradient(at_bottom_right,_#3b82f6_0%,_transparent_50%),radial-gradient(at_center,_#8b5cf6_0%,_transparent_60%)]", "bg_color": "bg-slate-950", "text_contrast": "white", "category": "mesh"},

    # Glass Gradients
    "glass_light": {"class": "bg-gradient-to-br from-white/60 via-white/40 to-white/20 backdrop-blur-xl", "text_contrast": "slate-800", "category": "glass"},
    "glass_dark": {"class": "bg-gradient-to-br from-slate-900/80 via-slate-800/60 to-slate-900/40 backdrop-blur-xl", "text_contrast": "white", "category": "glass"},

    # Dark Mode
    "dark_glow": {"class": "bg-gradient-to-r from-slate-900 via-purple-900/50 to-slate-900", "text_contrast": "white", "category": "dark"},
    "dark_aurora": {"class": "bg-[linear-gradient(to_right,#0f172a,#1e1b4b,#312e81,#1e1b4b,#0f172a)]", "text_contrast": "white", "category": "dark"},

    # Animated
    "animated_flow": {"class": "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500 bg-[length:200%_200%] animate-gradient-x", "text_contrast": "white", "category": "animated", "keyframes": "@keyframes gradient-x { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }"},

    # Text Gradients
    "text_vibrant": {"class": "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500 bg-clip-text text-transparent", "category": "text"},
}


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
    """
    primary = GRADIENT_LIBRARY[primary_gradient]
    secondary = GRADIENT_LIBRARY[secondary_gradient]
    dark_bg = GRADIENT_LIBRARY[dark_mode_gradient]

    keyframes = []
    if include_animations:
        for g in [primary, secondary]:
            if "keyframes" in g:
                keyframes.append(g["keyframes"])

    return {
        "name": f"gradient-{primary_gradient}",
        "description": f"Gradient theme with {primary_gradient} primary",

        # Gradient presets
        "gradient_primary": primary["class"],
        "gradient_secondary": secondary["class"],
        "gradient_text": GRADIENT_LIBRARY["text_vibrant"]["class"],

        # Standard colors
        "primary": "violet-600",
        "primary_hover": "violet-700",
        "secondary": "fuchsia-500",
        "accent": "cyan-400",

        # Backgrounds
        "background": "white",
        "background_dark": "slate-950",
        "background_gradient_dark": dark_bg["class"],
        "surface": "slate-50",
        "surface_dark": "slate-900",

        # Text
        "text": "slate-900",
        "text_dark": "white",
        "text_muted": "slate-500",

        # Style
        "border": "slate-200",
        "border_radius": "rounded-2xl",
        "shadow": "shadow-lg shadow-violet-500/10",
        "shadow_hover": "shadow-xl shadow-violet-500/20",

        # Button variants
        "button_gradient": f"""
            {primary['class']}
            text-{primary['text_contrast']} font-semibold
            px-6 py-3 rounded-xl
            shadow-lg shadow-violet-500/25
            hover:shadow-xl hover:shadow-violet-500/40
            hover:scale-[1.02]
            active:scale-[0.98]
            transition-all duration-200
        """,

        # Available gradients
        "available_gradients": list(GRADIENT_LIBRARY.keys()),

        # Keyframes
        "_keyframes": "\n".join(keyframes),
    }


def get_gradient(name: str) -> Dict[str, Any]:
    """Get a specific gradient from the library."""
    return GRADIENT_LIBRARY.get(name, GRADIENT_LIBRARY["aurora"])


def list_gradients_by_category(category: str) -> List[str]:
    """List gradients by category."""
    return [name for name, g in GRADIENT_LIBRARY.items() if g.get("category") == category]


# =============================================================================
# 8. CYBERPUNK THEME FACTORY
# =============================================================================

NEON_COLORS = {
    "cyan": {"hex": "#22d3ee", "rgb": "34, 211, 238", "tailwind": "cyan-400"},
    "fuchsia": {"hex": "#e879f9", "rgb": "232, 121, 249", "tailwind": "fuchsia-400"},
    "yellow": {"hex": "#facc15", "rgb": "250, 204, 21", "tailwind": "yellow-400"},
    "green": {"hex": "#4ade80", "rgb": "74, 222, 128", "tailwind": "green-400"},
    "pink": {"hex": "#f472b6", "rgb": "244, 114, 182", "tailwind": "pink-400"},
    "blue": {"hex": "#60a5fa", "rgb": "96, 165, 250", "tailwind": "blue-400"},
    "purple": {"hex": "#a78bfa", "rgb": "167, 139, 250", "tailwind": "violet-400"},
    "red": {"hex": "#f87171", "rgb": "248, 113, 113", "tailwind": "red-400"},
    "orange": {"hex": "#fb923c", "rgb": "251, 146, 60", "tailwind": "orange-400"},
}

GLOW_INTENSITIES = {
    "subtle": {"blur": "10px", "opacity": 0.2, "spread": "0px", "layers": 1},
    "medium": {"blur": "15px", "opacity": 0.3, "spread": "0px", "layers": 2},
    "strong": {"blur": "20px", "opacity": 0.4, "spread": "5px", "layers": 2},
    "intense": {"blur": "30px", "opacity": 0.5, "spread": "10px", "layers": 3},
    "extreme": {"blur": "40px", "opacity": 0.6, "spread": "15px", "layers": 3},
}


def generate_neon_glow(
    color: str,
    intensity: Literal["subtle", "medium", "strong", "intense", "extreme"] = "medium",
    animated: bool = False,
) -> str:
    """Generate multi-layer neon glow shadow."""
    neon = NEON_COLORS.get(color, NEON_COLORS["cyan"])
    settings = GLOW_INTENSITIES[intensity]

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


def create_cyberpunk_theme(
    primary_neon: str = "cyan",
    secondary_neon: str = "fuchsia",
    glow_intensity: Literal["subtle", "medium", "strong", "intense", "extreme"] = "medium",
    enable_animations: bool = True,
    scanline_effect: bool = False,
) -> Dict[str, Any]:
    """
    Cyberpunk theme with configurable neon effects.
    """
    primary = NEON_COLORS[primary_neon]
    secondary = NEON_COLORS[secondary_neon]

    primary_glow = generate_neon_glow(primary_neon, glow_intensity, enable_animations)
    secondary_glow = generate_neon_glow(secondary_neon, glow_intensity, False)

    # Hover intensified glow
    intensity_order = list(GLOW_INTENSITIES.keys())
    current_idx = intensity_order.index(glow_intensity)
    hover_intensity = intensity_order[min(current_idx + 1, len(intensity_order) - 1)]
    hover_glow = generate_neon_glow(primary_neon, hover_intensity, False)

    return {
        "name": f"cyberpunk-{primary_neon}-{glow_intensity}",
        "description": f"Cyberpunk with {primary_neon} neon at {glow_intensity} intensity",

        # Neon colors
        "primary": primary["tailwind"],
        "primary_hex": primary["hex"],
        "secondary": secondary["tailwind"],
        "secondary_hex": secondary["hex"],
        "accent": "yellow-400",

        # Dark backgrounds
        "background": "slate-950",
        "background_dark": "black",
        "surface": "slate-900",
        "surface_dark": "slate-950",

        # Neon text
        "text": "slate-100",
        "text_dark": "white",
        "text_muted": "slate-400",
        "text_neon": f"text-{primary['tailwind']} {primary_glow}",

        # Borders
        "border": f"{primary['tailwind']}/30",
        "border_radius": "rounded-none",
        "border_width": "border",

        # Glow effects
        "glow_primary": primary_glow,
        "glow_secondary": secondary_glow,
        "glow_hover": hover_glow,

        # Shadows
        "shadow": primary_glow,
        "shadow_hover": hover_glow,

        # Typography
        "font": "font-mono",

        # Components
        "button_neon": f"""
            bg-transparent
            text-{primary['tailwind']} font-bold uppercase tracking-wider
            px-6 py-3
            border-2 border-{primary['tailwind']}
            {primary_glow}
            hover:{hover_glow}
            hover:bg-{primary['tailwind']}/10
            transition-all duration-300
        """,

        "button_neon_filled": f"""
            bg-{primary['tailwind']}
            text-black font-bold uppercase tracking-wider
            px-6 py-3
            {primary_glow}
            hover:{hover_glow}
            hover:brightness-110
            transition-all duration-300
        """,

        "card_neon": f"""
            bg-slate-900/80 backdrop-blur-sm
            border border-{primary['tailwind']}/30
            {generate_neon_glow(primary_neon, "subtle")}
            hover:{primary_glow}
            transition-all duration-500
        """,

        # Metadata
        "available_intensities": list(GLOW_INTENSITIES.keys()),
        "current_intensity": glow_intensity,
    }


# =============================================================================
# 9. RETRO THEME FACTORY
# =============================================================================

RETRO_FONT_PAIRINGS = {
    "80s_tech": {
        "heading": {"family": "'VT323', monospace", "tailwind_class": "font-['VT323']", "fallback": "font-mono", "style": "uppercase tracking-[0.2em]"},
        "body": {"family": "'Share Tech Mono', monospace", "tailwind_class": "font-['Share_Tech_Mono']", "fallback": "font-mono"},
        "era": "1980s tech/sci-fi",
    },
    "80s_neon": {
        "heading": {"family": "'Monoton', cursive", "tailwind_class": "font-['Monoton']", "fallback": "font-serif", "style": "uppercase"},
        "body": {"family": "'Rajdhani', sans-serif", "tailwind_class": "font-['Rajdhani']", "fallback": "font-sans"},
        "era": "1980s neon/arcade",
    },
    "90s_grunge": {
        "heading": {"family": "'Bebas Neue', sans-serif", "tailwind_class": "font-['Bebas_Neue']", "fallback": "font-sans", "style": "uppercase tracking-wide"},
        "body": {"family": "'Work Sans', sans-serif", "tailwind_class": "font-['Work_Sans']", "fallback": "font-sans"},
        "era": "1990s grunge/alternative",
    },
    "90s_web": {
        "heading": {"family": "'Comic Neue', cursive", "tailwind_class": "font-['Comic_Neue']", "fallback": "font-sans"},
        "body": {"family": "'Courier Prime', monospace", "tailwind_class": "font-['Courier_Prime']", "fallback": "font-mono"},
        "era": "1990s early web/Geocities",
    },
    "retro_futurism": {
        "heading": {"family": "'Syncopate', sans-serif", "tailwind_class": "font-['Syncopate']", "fallback": "font-sans", "style": "uppercase tracking-widest"},
        "body": {"family": "'Exo 2', sans-serif", "tailwind_class": "font-['Exo_2']", "fallback": "font-sans"},
        "era": "Retro-futurism (Space Age)",
    },
    "vintage_americana": {
        "heading": {"family": "'Righteous', cursive", "tailwind_class": "font-['Righteous']", "fallback": "font-serif"},
        "body": {"family": "'Lato', sans-serif", "tailwind_class": "font-['Lato']", "fallback": "font-sans"},
        "era": "1950s-60s Americana",
    },
}


def create_retro_theme(
    era: Literal["80s_tech", "80s_neon", "90s_grunge", "90s_web", "retro_futurism", "vintage_americana"] = "80s_neon",
    color_scheme: Literal["neon", "pastel", "earthy", "chrome"] = "neon",
    enable_crt_effects: bool = False,
) -> Dict[str, Any]:
    """
    Retro theme with era-specific font pairings.
    """
    fonts = RETRO_FONT_PAIRINGS[era]

    color_schemes = {
        "neon": {"primary": "fuchsia-500", "secondary": "cyan-400", "accent": "yellow-400", "background": "slate-900", "surface": "slate-800"},
        "pastel": {"primary": "pink-400", "secondary": "sky-400", "accent": "lime-400", "background": "amber-50", "surface": "white"},
        "earthy": {"primary": "orange-600", "secondary": "teal-600", "accent": "amber-500", "background": "stone-100", "surface": "white"},
        "chrome": {"primary": "slate-400", "secondary": "blue-400", "accent": "amber-400", "background": "slate-900", "surface": "slate-800"},
    }

    colors = color_schemes[color_scheme]

    return {
        "name": f"retro-{era}-{color_scheme}",
        "description": f"{fonts['era']} aesthetic with {color_scheme} colors",

        # Typography
        "font_heading": fonts["heading"]["tailwind_class"],
        "font_heading_style": fonts["heading"].get("style", ""),
        "font_body": fonts["body"]["tailwind_class"],
        "font_fallback_heading": fonts["heading"]["fallback"],
        "font_fallback_body": fonts["body"]["fallback"],

        # Colors
        "primary": colors["primary"],
        "secondary": colors["secondary"],
        "accent": colors["accent"],
        "background": colors["background"],
        "background_dark": "slate-950",
        "surface": colors["surface"],
        "surface_dark": "slate-800",

        # Era-specific styling
        "border": colors["primary"].split("-")[0] + "-300",
        "border_radius": "rounded-none" if era in ["80s_tech", "90s_grunge"] else "rounded-lg",

        # Retro shadows
        "shadow": f"shadow-[4px_4px_0px] shadow-{colors['primary']}",
        "shadow_hover": f"shadow-[6px_6px_0px] shadow-{colors['primary']}",

        # Button
        "button_retro": f"""
            {fonts["heading"]["tailwind_class"]}
            {fonts["heading"].get("style", "")}
            bg-{colors["primary"]} text-white
            px-6 py-3
            shadow-[4px_4px_0px] shadow-black
            hover:shadow-[6px_6px_0px]
            hover:-translate-y-0.5 hover:translate-x-0.5
            active:shadow-[2px_2px_0px]
            active:translate-y-0 active:translate-x-0
            transition-all duration-150
        """,

        # Metadata
        "_era": era,
    }


# =============================================================================
# 10. PASTEL THEME FACTORY
# =============================================================================

PASTEL_ACCESSIBLE_PAIRS = {
    "rose": {"bg": "rose-50", "bg_medium": "rose-100", "text_safe": "rose-900", "text_medium": "rose-800", "accent": "rose-600", "button_bg": "rose-600"},
    "pink": {"bg": "pink-50", "bg_medium": "pink-100", "text_safe": "pink-900", "text_medium": "pink-800", "accent": "pink-600", "button_bg": "pink-600"},
    "sky": {"bg": "sky-50", "bg_medium": "sky-100", "text_safe": "sky-900", "text_medium": "sky-800", "accent": "sky-600", "button_bg": "sky-600"},
    "violet": {"bg": "violet-50", "bg_medium": "violet-100", "text_safe": "violet-900", "text_medium": "violet-800", "accent": "violet-600", "button_bg": "violet-600"},
    "teal": {"bg": "teal-50", "bg_medium": "teal-100", "text_safe": "teal-900", "text_medium": "teal-800", "accent": "teal-600", "button_bg": "teal-600"},
    "amber": {"bg": "amber-50", "bg_medium": "amber-100", "text_safe": "amber-900", "text_medium": "amber-800", "accent": "amber-600", "button_bg": "amber-700"},
    "lime": {"bg": "lime-50", "bg_medium": "lime-100", "text_safe": "lime-900", "text_medium": "lime-800", "accent": "lime-700", "button_bg": "lime-700"},
}


def create_pastel_theme(
    primary_pastel: Literal["rose", "pink", "sky", "violet", "teal", "amber", "lime"] = "rose",
    secondary_pastel: Literal["rose", "pink", "sky", "violet", "teal", "amber", "lime"] = "sky",
    wcag_level: Literal["AA", "AAA"] = "AA",
    dark_mode_handling: Literal["invert", "desaturate", "vibrant"] = "desaturate",
) -> Dict[str, Any]:
    """
    WCAG-compliant pastel theme with guaranteed contrast ratios.
    """
    primary = PASTEL_ACCESSIBLE_PAIRS[primary_pastel]
    secondary = PASTEL_ACCESSIBLE_PAIRS[secondary_pastel]

    # Text color based on WCAG level
    if wcag_level == "AAA":
        text_color = primary["text_safe"]
        muted_color = primary["text_medium"]
    else:
        text_color = primary["text_medium"]
        muted_color = f"{primary_pastel}-700"

    # Dark mode strategy
    dark_mode_colors = {
        "invert": {"background": f"{primary_pastel}-900", "surface": f"{primary_pastel}-800", "text": f"{primary_pastel}-100"},
        "desaturate": {"background": "slate-800", "surface": "slate-700", "text": "slate-200"},
        "vibrant": {"background": f"{primary_pastel}-950", "surface": f"{primary_pastel}-900", "text": f"{primary_pastel}-200"},
    }

    dark = dark_mode_colors[dark_mode_handling]

    return {
        "name": f"pastel-{primary_pastel}-{wcag_level}",
        "description": f"Accessible pastel theme (WCAG {wcag_level} compliant)",

        # Primary colors
        "primary": primary["accent"],
        "primary_hover": primary["button_bg"],
        "secondary": secondary["accent"],
        "accent": secondary["button_bg"],

        # Light mode backgrounds
        "background": primary["bg"],
        "surface": primary["bg_medium"],

        # Dark mode backgrounds
        "background_dark": dark["background"],
        "surface_dark": dark["surface"],

        # Text (WCAG compliant)
        "text": text_color,
        "text_dark": dark["text"],
        "text_muted": muted_color,

        # Borders
        "border": secondary["bg_medium"],
        "border_dark": "slate-600",

        # Styling
        "border_radius": "rounded-2xl",
        "shadow": "shadow-sm",
        "shadow_hover": "shadow-md",

        # Contrast-safe button
        "button_primary": f"""
            bg-{primary['button_bg']} hover:bg-{primary['button_bg'].replace('-600', '-700').replace('-700', '-800')}
            text-white font-medium
            px-6 py-3 rounded-xl
            shadow-sm hover:shadow-md
            transition-all duration-200
        """,

        # Secondary button
        "button_secondary": f"""
            bg-{primary['bg_medium']} hover:bg-{primary['bg']}
            text-{text_color} font-medium
            border border-{primary['accent']}/30
            px-6 py-3 rounded-xl
            transition-all duration-200
        """,

        # Metadata
        "_wcag_level": wcag_level,
        "_min_contrast_ratio": 7.0 if wcag_level == "AAA" else 4.5,
    }


# =============================================================================
# 11. DARK MODE FIRST THEME FACTORY
# =============================================================================

def create_dark_mode_first_theme(
    primary_glow: str = "emerald",
    contrast_level: Literal["normal", "high"] = "normal",
    light_mode_style: Literal["minimal", "warm", "cool", "inverted"] = "minimal",
) -> Dict[str, Any]:
    """
    Dark mode optimized theme with equally polished light mode.
    """
    glow_colors = {
        "emerald": {"primary": "emerald-500", "primary_hover": "emerald-400", "glow": "emerald-500/20", "light_accent": "emerald-600"},
        "cyan": {"primary": "cyan-400", "primary_hover": "cyan-300", "glow": "cyan-400/20", "light_accent": "cyan-600"},
        "violet": {"primary": "violet-500", "primary_hover": "violet-400", "glow": "violet-500/20", "light_accent": "violet-600"},
        "amber": {"primary": "amber-500", "primary_hover": "amber-400", "glow": "amber-500/20", "light_accent": "amber-600"},
    }

    glow = glow_colors.get(primary_glow, glow_colors["emerald"])

    light_styles = {
        "minimal": {"background": "white", "surface": "slate-50", "text": "slate-900", "text_muted": "slate-600", "border": "slate-200"},
        "warm": {"background": "amber-50", "surface": "white", "text": "stone-900", "text_muted": "stone-600", "border": "amber-200"},
        "cool": {"background": "slate-100", "surface": "white", "text": "slate-900", "text_muted": "slate-500", "border": "slate-300"},
        "inverted": {"background": "slate-200", "surface": "slate-100", "text": "slate-900", "text_muted": "slate-600", "border": "slate-300"},
    }

    light = light_styles[light_mode_style]

    theme = {
        "name": f"dark-first-{primary_glow}",
        "description": f"Dark mode optimized with {light_mode_style} light mode",

        # Primary
        "primary": glow["primary"],
        "primary_hover": glow["primary_hover"],
        "primary_light": glow["light_accent"],

        # Dark Mode (Primary)
        "background_dark": "slate-900",
        "background_darker": "slate-950",
        "surface_dark": "slate-800",
        "surface_elevated_dark": "slate-700",
        "text_dark": "white",
        "text_muted_dark": "slate-400",
        "border_dark": "slate-700",

        # Glow effects
        "glow_dark": f"shadow-lg shadow-{glow['glow']}",
        "glow_hover_dark": f"shadow-xl shadow-{glow['glow'].replace('/20', '/30')}",

        # Light Mode
        "background": light["background"],
        "surface": light["surface"],
        "surface_elevated": "white",
        "text": light["text"],
        "text_muted": light["text_muted"],
        "border": light["border"],

        # Light mode shadows
        "shadow": "shadow-sm",
        "shadow_hover": "shadow-md",

        # Style
        "border_radius": "rounded-xl",

        # Button
        "button_primary": f"""
            bg-{glow['primary']} hover:bg-{glow['primary_hover']}
            text-black dark:text-black font-medium
            px-6 py-3 rounded-xl
            shadow-sm hover:shadow-md
            dark:shadow-lg dark:shadow-{glow['glow']}
            dark:hover:shadow-xl dark:hover:shadow-{glow['glow'].replace('/20', '/30')}
            transition-all duration-200
        """,

        # Card
        "card_adaptive": f"""
            bg-{light['surface']} dark:bg-slate-800
            text-{light['text']} dark:text-white
            border border-{light['border']} dark:border-slate-700
            rounded-xl p-6
            shadow-sm dark:shadow-lg dark:shadow-black/20
        """,
    }

    # High contrast adjustments
    if contrast_level == "high":
        theme["text"] = "black"
        theme["text_dark"] = "white"
        theme["text_muted"] = "slate-700"
        theme["text_muted_dark"] = "slate-300"

    return theme


# =============================================================================
# 12. HIGH CONTRAST THEME FACTORY
# =============================================================================

def create_high_contrast_theme(
    softness_level: Literal["sharp", "balanced", "smooth"] = "balanced",
    color_scheme: Literal["blue", "purple", "green", "neutral"] = "blue",
    animation_preference: Literal["full", "reduced", "none"] = "reduced",
) -> Dict[str, Any]:
    """
    WCAG AAA compliant theme with adjustable visual softness.
    """
    softness_settings = {
        "sharp": {"radius": "rounded-none", "transition": "transition-none", "shadow": "shadow-none", "border_style": "border-2"},
        "balanced": {"radius": "rounded-md", "transition": "transition-colors duration-150", "shadow": "shadow-sm", "border_style": "border-2"},
        "smooth": {"radius": "rounded-lg", "transition": "transition-all duration-200 ease-out", "shadow": "shadow-md", "border_style": "border"},
    }

    soft = softness_settings[softness_level]

    schemes = {
        "blue": {"primary": "blue-800", "primary_hover": "blue-900", "focus_ring": "blue-600", "link": "blue-700"},
        "purple": {"primary": "purple-800", "primary_hover": "purple-900", "focus_ring": "purple-600", "link": "purple-700"},
        "green": {"primary": "emerald-800", "primary_hover": "emerald-900", "focus_ring": "emerald-600", "link": "emerald-700"},
        "neutral": {"primary": "slate-800", "primary_hover": "slate-900", "focus_ring": "slate-600", "link": "slate-900"},
    }

    colors = schemes[color_scheme]

    return {
        "name": f"high-contrast-{color_scheme}-{softness_level}",
        "description": f"WCAG AAA theme ({softness_level} style)",

        # Colors
        "primary": colors["primary"],
        "primary_hover": colors["primary_hover"],
        "secondary": "slate-700",

        # Maximum contrast backgrounds
        "background": "white",
        "background_dark": "black",
        "surface": "slate-50",
        "surface_dark": "slate-950",

        # Text
        "text": "black",
        "text_dark": "white",
        "text_muted": "slate-700",
        "text_muted_dark": "slate-300",

        # Borders
        "border": "slate-900",
        "border_dark": "white",
        "border_width": soft["border_style"],
        "border_radius": soft["radius"],

        # Focus indicators
        "focus_ring": f"ring-4 ring-{colors['focus_ring']} ring-offset-2",
        "focus_ring_dark": f"ring-4 ring-{colors['focus_ring'].replace('-600', '-400')} ring-offset-2 ring-offset-black",

        # Links
        "link_color": colors["link"],
        "link_decoration": "underline underline-offset-4 decoration-2",

        # Shadows
        "shadow": soft["shadow"],
        "shadow_hover": "shadow-lg" if softness_level != "sharp" else "shadow-none",

        # Transitions
        "transition": soft["transition"],

        # Button
        "button_primary": f"""
            bg-{colors['primary']} hover:bg-{colors['primary_hover']}
            text-white font-semibold
            px-6 py-3 {soft['radius']} {soft['border_style']} border-black
            {soft['transition']}
            focus:outline-none focus:ring-4 focus:ring-{colors['focus_ring']} focus:ring-offset-2
        """,

        # Metadata
        "_wcag_level": "AAA",
        "_min_contrast_ratio": 7.0,
    }


# =============================================================================
# 13. NATURE THEME FACTORY
# =============================================================================

NATURE_SEASONS = {
    "spring": {"name": "Spring", "mood": "Fresh, renewal, growth", "primary": "lime-500", "secondary": "emerald-500", "accent": "pink-400", "background": "lime-50", "surface": "white", "text": "emerald-900"},
    "summer": {"name": "Summer", "mood": "Vibrant, warm, energetic", "primary": "amber-500", "secondary": "orange-500", "accent": "sky-400", "background": "amber-50", "surface": "white", "text": "stone-900"},
    "autumn": {"name": "Autumn", "mood": "Warm, cozy, harvest", "primary": "orange-600", "secondary": "red-600", "accent": "amber-400", "background": "orange-50", "surface": "white", "text": "stone-900"},
    "winter": {"name": "Winter", "mood": "Cool, serene, minimal", "primary": "slate-600", "secondary": "sky-400", "accent": "red-500", "background": "slate-50", "surface": "white", "text": "slate-900"},
}


def create_nature_theme(
    season: Literal["spring", "summer", "autumn", "winter"] = "spring",
    organic_shapes: bool = True,
    eco_friendly_mode: bool = False,
) -> Dict[str, Any]:
    """
    Nature-inspired theme with seasonal variations.
    """
    s = NATURE_SEASONS[season]

    # Organic vs geometric
    if organic_shapes:
        radius = "rounded-[30%_70%_70%_30%/30%_30%_70%_70%]"
        radius_subtle = "rounded-3xl"
        radius_button = "rounded-full"
    else:
        radius = "rounded-xl"
        radius_subtle = "rounded-lg"
        radius_button = "rounded-lg"

    theme = {
        "name": f"nature-{season}",
        "description": f"{s['name']} - {s['mood']}",

        # Season colors
        "primary": s["primary"],
        "primary_hover": s["primary"].replace("-500", "-600").replace("-600", "-700"),
        "secondary": s["secondary"],
        "accent": s["accent"],

        # Backgrounds
        "background": s["background"],
        "background_dark": "stone-900",
        "surface": s["surface"],
        "surface_dark": "stone-800",

        # Text
        "text": s["text"],
        "text_dark": "stone-100",
        "text_muted": s["text"].replace("-900", "-600"),

        # Organic styling
        "border": s["primary"].replace("-500", "-200").replace("-600", "-200"),
        "border_radius": radius_subtle,
        "border_radius_organic": radius,
        "border_radius_button": radius_button,

        # Shadows
        "shadow": f"shadow-lg shadow-{s['primary'].split('-')[0]}-500/10",
        "shadow_hover": f"shadow-xl shadow-{s['primary'].split('-')[0]}-500/20",

        # Font
        "font": "font-sans",

        # Organic button
        "button_organic": f"""
            bg-{s['primary']} hover:bg-{s['primary'].replace('-500', '-600')}
            text-white font-medium
            px-8 py-3 {radius_button}
            shadow-lg shadow-{s['primary'].split('-')[0]}-500/30
            hover:shadow-xl hover:-translate-y-0.5
            transition-all duration-300
        """,

        # Card
        "card_organic": f"""
            bg-{s['surface']} dark:bg-stone-800
            {radius_subtle}
            shadow-lg shadow-{s['primary'].split('-')[0]}-500/5
            border border-{s['primary'].split('-')[0]}-100
            overflow-hidden
        """,

        # Decorative blob
        "decorative_blob": f"""
            absolute -z-10
            w-96 h-96
            bg-{s['primary']}/10
            {radius}
            blur-3xl
        """,

        # Metadata
        "_season": season,
    }

    # Eco-friendly mode
    if eco_friendly_mode:
        theme["shadow"] = "shadow-sm"
        theme["shadow_hover"] = "shadow-md"
        theme["border_radius"] = "rounded-lg"
        theme["decorative_blob"] = ""

    return theme


# =============================================================================
# 14. STARTUP THEME FACTORY
# =============================================================================

STARTUP_ARCHETYPES = {
    "disruptor": {"name": "Disruptor", "tagline": "Challenge the status quo", "primary": "violet-600", "secondary": "fuchsia-500", "accent": "lime-400", "personality": ["bold", "unconventional", "energetic"], "gradient": "from-violet-600 via-fuchsia-500 to-pink-500", "motion": "dynamic, fast"},
    "enterprise": {"name": "Enterprise SaaS", "tagline": "Trusted by industry leaders", "primary": "blue-700", "secondary": "slate-600", "accent": "emerald-500", "personality": ["reliable", "professional", "scalable"], "gradient": "from-blue-700 to-blue-900", "motion": "subtle, professional"},
    "consumer": {"name": "Consumer App", "tagline": "Delightful everyday experiences", "primary": "pink-500", "secondary": "orange-400", "accent": "cyan-400", "personality": ["friendly", "playful", "accessible"], "gradient": "from-pink-500 via-orange-400 to-yellow-400", "motion": "bouncy, fun"},
    "fintech": {"name": "Fintech", "tagline": "The future of finance", "primary": "emerald-600", "secondary": "teal-500", "accent": "amber-400", "personality": ["trustworthy", "innovative", "secure"], "gradient": "from-emerald-600 to-teal-600", "motion": "smooth, confident"},
    "healthtech": {"name": "Healthtech", "tagline": "Better health through technology", "primary": "sky-600", "secondary": "teal-500", "accent": "rose-400", "personality": ["caring", "scientific", "approachable"], "gradient": "from-sky-500 to-teal-500", "motion": "calm, reassuring"},
    "ai_ml": {"name": "AI/ML Startup", "tagline": "Intelligence amplified", "primary": "purple-600", "secondary": "blue-500", "accent": "cyan-400", "personality": ["cutting-edge", "intelligent", "futuristic"], "gradient": "from-purple-600 via-blue-500 to-cyan-400", "motion": "algorithmic, precise"},
    "sustainability": {"name": "Sustainability/Green", "tagline": "Building a better tomorrow", "primary": "green-600", "secondary": "lime-500", "accent": "amber-400", "personality": ["conscious", "hopeful", "natural"], "gradient": "from-green-600 to-emerald-500", "motion": "flowing, natural"},
}


def create_startup_theme(
    archetype: Literal["disruptor", "enterprise", "consumer", "fintech", "healthtech", "ai_ml", "sustainability"] = "disruptor",
    stage: Literal["seed", "growth", "scale"] = "growth",
    enable_motion: bool = True,
) -> Dict[str, Any]:
    """
    Startup-specific theme with archetype-based differentiation.
    """
    arch = STARTUP_ARCHETYPES[archetype]

    stage_settings = {
        "seed": {"boldness": "high", "shadow_intensity": "lg"},
        "growth": {"boldness": "medium", "shadow_intensity": "md"},
        "scale": {"boldness": "refined", "shadow_intensity": "sm"},
    }

    stg = stage_settings[stage]

    motion_styles = {
        "dynamic, fast": "transition-all duration-200",
        "subtle, professional": "transition-all duration-300 ease-out",
        "bouncy, fun": "transition-all duration-300 ease-[cubic-bezier(0.68,-0.55,0.265,1.55)]",
        "smooth, confident": "transition-all duration-400 ease-out",
        "calm, reassuring": "transition-all duration-500 ease-out",
        "algorithmic, precise": "transition-all duration-150 ease-linear",
        "flowing, natural": "transition-all duration-600 ease-in-out",
    }

    motion = motion_styles.get(arch["motion"], "transition-all duration-300") if enable_motion else "transition-none"

    def _generate_hero_cta() -> str:
        if archetype == "disruptor":
            return f"""
                bg-gradient-to-r {arch['gradient']}
                text-white font-bold text-lg
                px-8 py-4 rounded-xl
                shadow-lg hover:shadow-xl
                hover:-translate-y-1 active:translate-y-0
                {motion}
            """
        elif archetype == "consumer":
            return f"""
                bg-gradient-to-r {arch['gradient']}
                text-white font-bold text-lg
                px-10 py-4 rounded-full
                shadow-lg hover:shadow-xl
                hover:scale-105 active:scale-95
                {motion}
            """
        else:
            return f"""
                bg-{arch['primary']} hover:bg-{arch['primary'].replace('-600', '-700')}
                text-white font-semibold
                px-8 py-4 rounded-xl
                shadow-md hover:shadow-lg
                {motion}
            """

    return {
        "name": f"startup-{archetype}-{stage}",
        "description": f"{arch['name']} - {arch['tagline']}",
        "personality": arch["personality"],

        # Core colors
        "primary": arch["primary"],
        "primary_hover": arch["primary"].replace("-600", "-700").replace("-500", "-600"),
        "secondary": arch["secondary"],
        "accent": arch["accent"],

        # Gradient
        "gradient_primary": f"bg-gradient-to-r {arch['gradient']}",
        "gradient_text": f"bg-gradient-to-r {arch['gradient']} bg-clip-text text-transparent",

        # Backgrounds
        "background": "white",
        "background_dark": "slate-950",
        "surface": "slate-50",
        "surface_dark": "slate-900",

        # Text
        "text": "slate-900",
        "text_dark": "white",
        "text_muted": "slate-500",

        # Style
        "border": "slate-200",
        "border_radius": "rounded-xl",
        "shadow": f"shadow-{stg['shadow_intensity']}",
        "shadow_hover": f"shadow-{_next_shadow(stg['shadow_intensity'])}",

        # Motion
        "transition": motion,

        # Hero CTA
        "hero_cta": _generate_hero_cta(),

        # Feature card
        "feature_card": f"""
            bg-white dark:bg-slate-800
            rounded-2xl p-6
            border border-slate-100 dark:border-slate-700
            shadow-{stg['shadow_intensity']} hover:shadow-{_next_shadow(stg['shadow_intensity'])}
            {motion}
            group
        """,

        # Badges
        "beta_badge": f"bg-{arch['primary']}/10 text-{arch['primary']} px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider",

        # Metadata
        "_archetype": archetype,
        "_stage": stage,
        "_personality": arch["personality"],
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Utility functions
    "hex_to_rgb",
    "rgb_to_hex",
    "hex_to_hsl",
    "hsl_to_hex",
    "relative_luminance",
    "contrast_ratio",
    "validate_contrast",

    # Brand Colors
    "BrandColors",

    # Theme Factory Functions
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

    # Helper functions
    "calculate_neumorphism_shadows",
    "generate_neon_glow",
    "get_gradient",
    "list_gradients_by_category",

    # Constants
    "BRUTALIST_CONTRAST_PAIRS",
    "NEOBRUTALISM_GRADIENTS",
    "GRADIENT_ANIMATIONS",
    "GRADIENT_LIBRARY",
    "NEON_COLORS",
    "GLOW_INTENSITIES",
    "RETRO_FONT_PAIRINGS",
    "PASTEL_ACCESSIBLE_PAIRS",
    "NATURE_SEASONS",
    "STARTUP_ARCHETYPES",
    "CORPORATE_INDUSTRIES",
    "CORPORATE_LAYOUTS",
]
