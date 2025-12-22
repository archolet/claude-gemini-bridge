"""
Design System Specification Module for Gemini MCP Server.

GAP 10: Provides standardized spacing, typography, and sizing scales
that all themes must use to ensure consistency across the design system.

This module defines:
- Spacing scale (Tailwind-aligned)
- Typography scale
- Icon sizes
- Breakpoints
- Z-index layers
- Animation presets
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


# =============================================================================
# SPACING SCALE
# =============================================================================

class SpacingScale(Enum):
    """
    Standardized spacing scale aligned with Tailwind CSS.

    Values represent pixels, mapped to Tailwind classes.
    Using a consistent 4px base unit system.
    """
    NONE = 0      # p-0, m-0
    PX = 1        # p-px, m-px
    XS = 4        # p-1, m-1 (0.25rem)
    SM = 8        # p-2, m-2 (0.5rem)
    MD = 12       # p-3, m-3 (0.75rem)
    BASE = 16     # p-4, m-4 (1rem)
    LG = 24       # p-6, m-6 (1.5rem)
    XL = 32       # p-8, m-8 (2rem)
    XXL = 48      # p-12, m-12 (3rem)
    XXXL = 64     # p-16, m-16 (4rem)
    HUGE = 96     # p-24, m-24 (6rem)
    MASSIVE = 128 # p-32, m-32 (8rem)


# Tailwind class mappings
SPACING_TO_TAILWIND: Dict[SpacingScale, str] = {
    SpacingScale.NONE: "0",
    SpacingScale.PX: "px",
    SpacingScale.XS: "1",
    SpacingScale.SM: "2",
    SpacingScale.MD: "3",
    SpacingScale.BASE: "4",
    SpacingScale.LG: "6",
    SpacingScale.XL: "8",
    SpacingScale.XXL: "12",
    SpacingScale.XXXL: "16",
    SpacingScale.HUGE: "24",
    SpacingScale.MASSIVE: "32",
}


def spacing_class(prefix: str, scale: SpacingScale) -> str:
    """Generate Tailwind spacing class.

    Args:
        prefix: Tailwind prefix (p, m, px, py, mx, my, gap, space-x, etc.)
        scale: Spacing scale value

    Returns:
        Tailwind class string (e.g., "p-4", "gap-6")
    """
    return f"{prefix}-{SPACING_TO_TAILWIND[scale]}"


# =============================================================================
# TYPOGRAPHY SCALE
# =============================================================================

@dataclass
class TypeStyle:
    """Individual typography style definition."""
    size_class: str      # text-xs, text-sm, text-base, etc.
    line_height: str     # leading-none, leading-tight, leading-normal, etc.
    letter_spacing: str  # tracking-tighter, tracking-normal, tracking-wide, etc.
    font_weight: str     # font-normal, font-medium, font-semibold, etc.

    def to_classes(self) -> str:
        """Convert to Tailwind class string."""
        return f"{self.size_class} {self.line_height} {self.letter_spacing} {self.font_weight}"


# Standard typography scale
TYPOGRAPHY_SCALE: Dict[str, TypeStyle] = {
    # Display styles - for hero headlines
    "display-2xl": TypeStyle(
        size_class="text-7xl md:text-8xl lg:text-9xl",
        line_height="leading-none",
        letter_spacing="tracking-tighter",
        font_weight="font-bold"
    ),
    "display-xl": TypeStyle(
        size_class="text-5xl md:text-6xl lg:text-7xl",
        line_height="leading-none",
        letter_spacing="tracking-tight",
        font_weight="font-bold"
    ),
    "display-lg": TypeStyle(
        size_class="text-4xl md:text-5xl lg:text-6xl",
        line_height="leading-tight",
        letter_spacing="tracking-tight",
        font_weight="font-bold"
    ),

    # Heading styles
    "heading-xl": TypeStyle(
        size_class="text-3xl md:text-4xl",
        line_height="leading-tight",
        letter_spacing="tracking-tight",
        font_weight="font-semibold"
    ),
    "heading-lg": TypeStyle(
        size_class="text-2xl md:text-3xl",
        line_height="leading-snug",
        letter_spacing="tracking-tight",
        font_weight="font-semibold"
    ),
    "heading-md": TypeStyle(
        size_class="text-xl md:text-2xl",
        line_height="leading-snug",
        letter_spacing="tracking-normal",
        font_weight="font-semibold"
    ),
    "heading-sm": TypeStyle(
        size_class="text-lg md:text-xl",
        line_height="leading-normal",
        letter_spacing="tracking-normal",
        font_weight="font-medium"
    ),

    # Body styles
    "body-xl": TypeStyle(
        size_class="text-xl",
        line_height="leading-relaxed",
        letter_spacing="tracking-normal",
        font_weight="font-normal"
    ),
    "body-lg": TypeStyle(
        size_class="text-lg",
        line_height="leading-relaxed",
        letter_spacing="tracking-normal",
        font_weight="font-normal"
    ),
    "body-base": TypeStyle(
        size_class="text-base",
        line_height="leading-relaxed",
        letter_spacing="tracking-normal",
        font_weight="font-normal"
    ),
    "body-sm": TypeStyle(
        size_class="text-sm",
        line_height="leading-normal",
        letter_spacing="tracking-normal",
        font_weight="font-normal"
    ),
    "body-xs": TypeStyle(
        size_class="text-xs",
        line_height="leading-normal",
        letter_spacing="tracking-normal",
        font_weight="font-normal"
    ),

    # UI styles
    "label": TypeStyle(
        size_class="text-sm",
        line_height="leading-none",
        letter_spacing="tracking-wide",
        font_weight="font-medium"
    ),
    "button": TypeStyle(
        size_class="text-sm",
        line_height="leading-none",
        letter_spacing="tracking-normal",
        font_weight="font-medium"
    ),
    "caption": TypeStyle(
        size_class="text-xs",
        line_height="leading-normal",
        letter_spacing="tracking-wide",
        font_weight="font-normal"
    ),
    "overline": TypeStyle(
        size_class="text-xs",
        line_height="leading-none",
        letter_spacing="tracking-widest",
        font_weight="font-semibold"
    ),
}


def get_type_classes(style_name: str) -> str:
    """Get Tailwind classes for a typography style.

    Args:
        style_name: Key from TYPOGRAPHY_SCALE

    Returns:
        Space-separated Tailwind classes
    """
    style = TYPOGRAPHY_SCALE.get(style_name)
    if style:
        return style.to_classes()
    return TYPOGRAPHY_SCALE["body-base"].to_classes()


# =============================================================================
# ICON SIZES
# =============================================================================

class IconSize(Enum):
    """Standardized icon sizes."""
    XS = 12    # w-3 h-3
    SM = 16    # w-4 h-4
    MD = 20    # w-5 h-5
    BASE = 24  # w-6 h-6
    LG = 32    # w-8 h-8
    XL = 40    # w-10 h-10
    XXL = 48   # w-12 h-12


ICON_SIZE_CLASSES: Dict[IconSize, str] = {
    IconSize.XS: "w-3 h-3",
    IconSize.SM: "w-4 h-4",
    IconSize.MD: "w-5 h-5",
    IconSize.BASE: "w-6 h-6",
    IconSize.LG: "w-8 h-8",
    IconSize.XL: "w-10 h-10",
    IconSize.XXL: "w-12 h-12",
}


def icon_classes(size: IconSize) -> str:
    """Get Tailwind classes for icon size."""
    return ICON_SIZE_CLASSES.get(size, ICON_SIZE_CLASSES[IconSize.BASE])


# =============================================================================
# BREAKPOINTS
# =============================================================================

@dataclass
class Breakpoint:
    """Responsive breakpoint definition."""
    name: str
    min_width: int
    prefix: str


BREAKPOINTS: List[Breakpoint] = [
    Breakpoint("mobile", 0, ""),
    Breakpoint("sm", 640, "sm:"),
    Breakpoint("md", 768, "md:"),
    Breakpoint("lg", 1024, "lg:"),
    Breakpoint("xl", 1280, "xl:"),
    Breakpoint("2xl", 1536, "2xl:"),
]


def responsive_class(base_class: str, breakpoint_overrides: Dict[str, str]) -> str:
    """Generate responsive class string.

    Args:
        base_class: Base (mobile) class
        breakpoint_overrides: Dict of breakpoint -> class overrides

    Returns:
        Full responsive class string

    Example:
        responsive_class("p-4", {"md": "p-6", "lg": "p-8"})
        # Returns: "p-4 md:p-6 lg:p-8"
    """
    classes = [base_class]
    for bp_name, override in breakpoint_overrides.items():
        classes.append(f"{bp_name}:{override}")
    return " ".join(classes)


# =============================================================================
# Z-INDEX LAYERS
# =============================================================================

class ZLayer(Enum):
    """Standardized z-index layers."""
    BASE = 0
    DROPDOWN = 10
    STICKY = 20
    FIXED = 30
    MODAL_BACKDROP = 40
    MODAL = 50
    POPOVER = 60
    TOOLTIP = 70
    TOAST = 80
    MAX = 9999


Z_INDEX_CLASSES: Dict[ZLayer, str] = {
    ZLayer.BASE: "z-0",
    ZLayer.DROPDOWN: "z-10",
    ZLayer.STICKY: "z-20",
    ZLayer.FIXED: "z-30",
    ZLayer.MODAL_BACKDROP: "z-40",
    ZLayer.MODAL: "z-50",
    ZLayer.POPOVER: "z-[60]",
    ZLayer.TOOLTIP: "z-[70]",
    ZLayer.TOAST: "z-[80]",
    ZLayer.MAX: "z-[9999]",
}


# =============================================================================
# ANIMATION PRESETS
# =============================================================================

@dataclass
class AnimationPreset:
    """Animation/transition preset."""
    duration: str      # duration-150, duration-300, etc.
    easing: str        # ease-in, ease-out, ease-in-out
    properties: str    # transition-all, transition-colors, etc.

    def to_classes(self) -> str:
        """Convert to Tailwind class string."""
        return f"{self.properties} {self.duration} {self.easing}"


ANIMATION_PRESETS: Dict[str, AnimationPreset] = {
    "instant": AnimationPreset(
        duration="duration-75",
        easing="ease-out",
        properties="transition-all"
    ),
    "fast": AnimationPreset(
        duration="duration-150",
        easing="ease-out",
        properties="transition-all"
    ),
    "normal": AnimationPreset(
        duration="duration-200",
        easing="ease-out",
        properties="transition-all"
    ),
    "slow": AnimationPreset(
        duration="duration-300",
        easing="ease-in-out",
        properties="transition-all"
    ),
    "slower": AnimationPreset(
        duration="duration-500",
        easing="ease-in-out",
        properties="transition-all"
    ),
    "color-only": AnimationPreset(
        duration="duration-200",
        easing="ease-out",
        properties="transition-colors"
    ),
    "transform-only": AnimationPreset(
        duration="duration-200",
        easing="ease-out",
        properties="transition-transform"
    ),
    "opacity-only": AnimationPreset(
        duration="duration-200",
        easing="ease-out",
        properties="transition-opacity"
    ),
    "bouncy": AnimationPreset(
        duration="duration-300",
        easing="ease-[cubic-bezier(0.34,1.56,0.64,1)]",
        properties="transition-all"
    ),
    "smooth": AnimationPreset(
        duration="duration-500",
        easing="ease-[cubic-bezier(0.25,1,0.5,1)]",
        properties="transition-all"
    ),
}


def animation_classes(preset_name: str) -> str:
    """Get Tailwind classes for animation preset."""
    preset = ANIMATION_PRESETS.get(preset_name)
    if preset:
        return preset.to_classes()
    return ANIMATION_PRESETS["normal"].to_classes()


# =============================================================================
# BORDER RADIUS SCALE
# =============================================================================

class BorderRadius(Enum):
    """Standardized border radius scale."""
    NONE = "none"
    SM = "sm"
    DEFAULT = "DEFAULT"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "2xl"
    XXXL = "3xl"
    FULL = "full"


BORDER_RADIUS_CLASSES: Dict[BorderRadius, str] = {
    BorderRadius.NONE: "rounded-none",
    BorderRadius.SM: "rounded-sm",
    BorderRadius.DEFAULT: "rounded",
    BorderRadius.MD: "rounded-md",
    BorderRadius.LG: "rounded-lg",
    BorderRadius.XL: "rounded-xl",
    BorderRadius.XXL: "rounded-2xl",
    BorderRadius.XXXL: "rounded-3xl",
    BorderRadius.FULL: "rounded-full",
}


# =============================================================================
# SHADOW SCALE
# =============================================================================

class ShadowSize(Enum):
    """Standardized shadow scale."""
    NONE = "none"
    SM = "sm"
    DEFAULT = "DEFAULT"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "2xl"
    INNER = "inner"


SHADOW_CLASSES: Dict[ShadowSize, str] = {
    ShadowSize.NONE: "shadow-none",
    ShadowSize.SM: "shadow-sm",
    ShadowSize.DEFAULT: "shadow",
    ShadowSize.MD: "shadow-md",
    ShadowSize.LG: "shadow-lg",
    ShadowSize.XL: "shadow-xl",
    ShadowSize.XXL: "shadow-2xl",
    ShadowSize.INNER: "shadow-inner",
}


# =============================================================================
# DESIGN SYSTEM SPECIFICATION
# =============================================================================

@dataclass
class DesignSystemSpec:
    """
    Complete design system specification.

    All themes should reference these standardized values
    to ensure consistency across the design system.
    """
    # Spacing
    spacing_unit: int = 4  # Base unit in pixels
    spacing_scale: List[int] = field(default_factory=lambda: [0, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128])

    # Typography
    base_font_size: int = 16
    type_scale_ratio: float = 1.25  # Major third

    # Touch targets
    min_touch_target: int = 44  # WCAG minimum

    # Border radius
    default_radius: BorderRadius = BorderRadius.LG

    # Shadows
    default_shadow: ShadowSize = ShadowSize.SM

    # Animations
    default_animation: str = "normal"

    # Colors (semantic)
    semantic_colors: Dict[str, str] = field(default_factory=lambda: {
        "success": "green",
        "warning": "amber",
        "error": "red",
        "info": "blue",
    })

    def get_spacing_class(self, prefix: str, index: int) -> str:
        """Get spacing class by scale index."""
        tailwind_values = ["0", "1", "2", "3", "4", "6", "8", "12", "16", "24", "32"]
        if 0 <= index < len(tailwind_values):
            return f"{prefix}-{tailwind_values[index]}"
        return f"{prefix}-4"

    def validate_touch_target(self, width_px: int, height_px: int) -> bool:
        """Check if dimensions meet minimum touch target."""
        return width_px >= self.min_touch_target and height_px >= self.min_touch_target


# Global design system instance
DESIGN_SYSTEM = DesignSystemSpec()


# =============================================================================
# THEME COMPLIANCE HELPERS
# =============================================================================

def validate_theme_spacing(theme_config: Dict[str, Any]) -> List[str]:
    """
    Validate that a theme uses standard spacing values.

    Returns list of warnings for non-standard values.
    """
    warnings = []
    standard_values = set(SPACING_TO_TAILWIND.values())

    # Check common spacing properties
    spacing_props = ["padding", "margin", "gap", "space"]

    for key, value in theme_config.items():
        if isinstance(value, str):
            for prop in spacing_props:
                if prop in key.lower():
                    # Extract numeric part
                    parts = value.split("-")
                    if len(parts) >= 2:
                        num_part = parts[-1]
                        if num_part not in standard_values and not num_part.startswith("["):
                            warnings.append(
                                f"Non-standard spacing '{num_part}' in {key}. "
                                f"Use standard scale: {sorted(standard_values)}"
                            )

    return warnings


def validate_theme_typography(theme_config: Dict[str, Any]) -> List[str]:
    """
    Validate that a theme uses standard typography scale.

    Returns list of warnings for non-standard values.
    """
    warnings = []
    standard_sizes = ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl", "6xl", "7xl", "8xl", "9xl"]

    for key, value in theme_config.items():
        if isinstance(value, str) and "text-" in value:
            # Extract size
            for part in value.split():
                if part.startswith("text-"):
                    size = part.replace("text-", "")
                    if size not in standard_sizes and not size.startswith("["):
                        warnings.append(
                            f"Non-standard text size '{size}' in {key}. "
                            f"Use standard scale: {standard_sizes}"
                        )

    return warnings


def apply_design_system_to_theme(
    theme_config: Dict[str, Any],
    spec: DesignSystemSpec = DESIGN_SYSTEM
) -> Dict[str, Any]:
    """
    Enhance a theme config with design system specifications.

    Adds standard scales and validates existing values.
    """
    enhanced = theme_config.copy()

    # Add design system reference
    enhanced["_design_system"] = {
        "spacing_unit": spec.spacing_unit,
        "min_touch_target": spec.min_touch_target,
        "base_font_size": spec.base_font_size,
        "type_scale_ratio": spec.type_scale_ratio,
    }

    # Add semantic colors if not present
    if "semantic_colors" not in enhanced:
        enhanced["semantic_colors"] = spec.semantic_colors

    # Add animation preset if not present
    if "transition" not in enhanced:
        enhanced["transition"] = animation_classes(spec.default_animation)

    return enhanced


# =============================================================================
# COMPONENT SIZE PRESETS
# =============================================================================

@dataclass
class ComponentSizes:
    """Standard component size definitions."""

    # Button sizes
    button_xs: str = "px-2 py-1 text-xs"
    button_sm: str = "px-3 py-1.5 text-sm"
    button_md: str = "px-4 py-2 text-sm"
    button_lg: str = "px-6 py-3 text-base"
    button_xl: str = "px-8 py-4 text-lg"

    # Input sizes
    input_sm: str = "px-3 py-1.5 text-sm"
    input_md: str = "px-4 py-2 text-base"
    input_lg: str = "px-4 py-3 text-lg"

    # Card padding
    card_sm: str = "p-4"
    card_md: str = "p-6"
    card_lg: str = "p-8"

    # Section padding
    section_sm: str = "py-12 px-4"
    section_md: str = "py-16 px-6"
    section_lg: str = "py-24 px-8"
    section_xl: str = "py-32 px-8"

    # Container max widths
    container_sm: str = "max-w-2xl"
    container_md: str = "max-w-4xl"
    container_lg: str = "max-w-6xl"
    container_xl: str = "max-w-7xl"
    container_full: str = "max-w-full"


# Global component sizes instance
COMPONENT_SIZES = ComponentSizes()


def get_component_size(component: str, size: str = "md") -> str:
    """
    Get size classes for a component.

    Args:
        component: Component type (button, input, card, section, container)
        size: Size variant (xs, sm, md, lg, xl)

    Returns:
        Tailwind classes for the component size
    """
    attr_name = f"{component}_{size}"
    return getattr(COMPONENT_SIZES, attr_name, getattr(COMPONENT_SIZES, f"{component}_md", ""))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Spacing
    "SpacingScale",
    "SPACING_TO_TAILWIND",
    "spacing_class",

    # Typography
    "TypeStyle",
    "TYPOGRAPHY_SCALE",
    "get_type_classes",

    # Icons
    "IconSize",
    "ICON_SIZE_CLASSES",
    "icon_classes",

    # Breakpoints
    "Breakpoint",
    "BREAKPOINTS",
    "responsive_class",

    # Z-index
    "ZLayer",
    "Z_INDEX_CLASSES",

    # Animations
    "AnimationPreset",
    "ANIMATION_PRESETS",
    "animation_classes",

    # Border radius
    "BorderRadius",
    "BORDER_RADIUS_CLASSES",

    # Shadows
    "ShadowSize",
    "SHADOW_CLASSES",

    # Design System
    "DesignSystemSpec",
    "DESIGN_SYSTEM",
    "validate_theme_spacing",
    "validate_theme_typography",
    "apply_design_system_to_theme",

    # Component sizes
    "ComponentSizes",
    "COMPONENT_SIZES",
    "get_component_size",
]
