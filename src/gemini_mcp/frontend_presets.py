"""Frontend design presets and system prompts for Gemini 3 Pro.

This module contains:
- Component type presets (Atomic Design levels)
- Theme presets (visual styles)
- System prompt for Gemini to generate high-quality TailwindCSS/HTML
"""

from typing import Any, Dict, List

# =============================================================================
# COMPONENT PRESETS (Atomic Design)
# =============================================================================

COMPONENT_PRESETS: Dict[str, Dict[str, Any]] = {
    # ATOMS - Smallest building blocks
    "button": {
        "atomic_level": "atom",
        "variants": ["primary", "secondary", "outline", "ghost", "danger"],
        "sizes": ["sm", "md", "lg", "xl"],
        "states": ["default", "hover", "focus", "active", "disabled"],
    },
    "input": {
        "atomic_level": "atom",
        "variants": ["text", "email", "password", "number", "search"],
        "states": ["default", "focus", "error", "success", "disabled"],
    },
    "badge": {
        "atomic_level": "atom",
        "variants": ["default", "success", "warning", "error", "info"],
    },
    "avatar": {
        "atomic_level": "atom",
        "sizes": ["xs", "sm", "md", "lg", "xl"],
        "shapes": ["circle", "rounded", "square"],
    },
    "icon": {
        "atomic_level": "atom",
        "sizes": ["sm", "md", "lg"],
    },
    "dropdown": {
        "atomic_level": "atom",
        "sections": ["trigger", "menu", "item"],
    },
    "toggle": {
        "atomic_level": "atom",
        "states": ["on", "off", "disabled"],
    },
    "tooltip": {
        "atomic_level": "atom",
        "positions": ["top", "bottom", "left", "right"],
    },
    # MOLECULES - Combinations of atoms
    "card": {
        "atomic_level": "molecule",
        "sections": ["header", "body", "footer", "media"],
        "variants": ["default", "elevated", "bordered", "interactive"],
    },
    "form": {
        "atomic_level": "molecule",
        "elements": ["input", "label", "helper_text", "error_text"],
        "layouts": ["vertical", "horizontal", "inline"],
    },
    "modal": {
        "atomic_level": "molecule",
        "sections": ["header", "body", "footer", "overlay"],
        "sizes": ["sm", "md", "lg", "xl", "full"],
    },
    "tabs": {
        "atomic_level": "molecule",
        "variants": ["underline", "pills", "enclosed", "soft"],
    },
    "table": {
        "atomic_level": "molecule",
        "features": ["sortable", "pagination", "selectable", "striped"],
    },
    "accordion": {
        "atomic_level": "molecule",
        "variants": ["default", "bordered", "separated"],
    },
    "alert": {
        "atomic_level": "molecule",
        "variants": ["info", "success", "warning", "error"],
        "dismissable": True,
    },
    "breadcrumb": {
        "atomic_level": "molecule",
        "separators": ["slash", "chevron", "arrow"],
    },
    "pagination": {
        "atomic_level": "molecule",
        "variants": ["default", "simple", "compact"],
    },
    "search_bar": {
        "atomic_level": "molecule",
        "features": ["autocomplete", "voice", "filters"],
    },
    "stat_card": {
        "atomic_level": "molecule",
        "sections": ["value", "label", "trend", "icon"],
    },
    "pricing_card": {
        "atomic_level": "molecule",
        "sections": ["tier", "price", "features", "cta"],
    },
    # ORGANISMS - Complex components
    "navbar": {
        "atomic_level": "organism",
        "sections": ["logo", "navigation", "actions", "mobile_menu"],
        "variants": ["default", "sticky", "transparent"],
    },
    "hero": {
        "atomic_level": "organism",
        "sections": ["headline", "subheadline", "cta", "media", "badge"],
        "layouts": ["centered", "left", "right", "split"],
    },
    "sidebar": {
        "atomic_level": "organism",
        "sections": ["header", "navigation", "footer"],
        "collapsible": True,
    },
    "footer": {
        "atomic_level": "organism",
        "sections": ["logo", "links", "social", "copyright"],
        "layouts": ["simple", "columns", "centered"],
    },
    "data_table": {
        "atomic_level": "organism",
        "features": ["sorting", "filtering", "pagination", "selection", "export"],
    },
    "login_form": {
        "atomic_level": "organism",
        "elements": ["email", "password", "remember", "submit", "social"],
    },
    "signup_form": {
        "atomic_level": "organism",
        "elements": ["name", "email", "password", "terms", "submit"],
    },
    "contact_form": {
        "atomic_level": "organism",
        "elements": ["name", "email", "subject", "message", "submit"],
    },
    "feature_section": {
        "atomic_level": "organism",
        "layouts": ["grid", "list", "alternating"],
    },
    "testimonial_section": {
        "atomic_level": "organism",
        "layouts": ["carousel", "grid", "single"],
    },
    "pricing_table": {
        "atomic_level": "organism",
        "features": ["toggle", "comparison", "highlight"],
    },
    "dashboard_header": {
        "atomic_level": "organism",
        "sections": ["title", "breadcrumb", "actions", "search"],
    },
}

# =============================================================================
# THEME PRESETS
# =============================================================================

THEME_PRESETS: Dict[str, Dict[str, Any]] = {
    "modern-minimal": {
        "description": "Clean, professional design with subtle shadows",
        "primary": "blue-600",
        "primary_hover": "blue-700",
        "secondary": "slate-600",
        "background": "white",
        "background_dark": "slate-900",
        "surface": "slate-50",
        "surface_dark": "slate-800",
        "border": "slate-200",
        "border_dark": "slate-700",
        "text": "slate-900",
        "text_dark": "slate-100",
        "text_muted": "slate-500",
        "border_radius": "rounded-lg",
        "shadow": "shadow-sm",
        "shadow_hover": "shadow-md",
        "font": "font-sans",
    },
    "brutalist": {
        "description": "Bold, high-contrast design with sharp edges",
        "primary": "black",
        "primary_hover": "slate-800",
        "secondary": "white",
        "background": "white",
        "background_dark": "black",
        "surface": "slate-100",
        "surface_dark": "slate-900",
        "border": "black",
        "border_dark": "white",
        "text": "black",
        "text_dark": "white",
        "text_muted": "slate-600",
        "border_radius": "rounded-none",
        "border_width": "border-2",
        "shadow": "shadow-[4px_4px_0px_#000]",
        "shadow_hover": "shadow-[6px_6px_0px_#000]",
        "font": "font-mono",
    },
    "glassmorphism": {
        "description": "Frosted glass effect with transparency",
        "primary": "indigo-500",
        "primary_hover": "indigo-600",
        "secondary": "purple-500",
        "background": "slate-900",
        "background_dark": "slate-950",
        "surface": "white/10",
        "surface_dark": "white/5",
        "border": "white/20",
        "border_dark": "white/10",
        "text": "white",
        "text_dark": "white",
        "text_muted": "slate-300",
        "border_radius": "rounded-2xl",
        "backdrop_blur": "backdrop-blur-lg",
        "shadow": "shadow-lg",
        "shadow_hover": "shadow-xl",
        "font": "font-sans",
    },
    "neo-brutalism": {
        "description": "Playful brutalism with bold colors",
        "primary": "yellow-400",
        "primary_hover": "yellow-500",
        "secondary": "pink-400",
        "accent": "cyan-400",
        "background": "amber-50",
        "background_dark": "slate-900",
        "surface": "white",
        "surface_dark": "slate-800",
        "border": "black",
        "border_dark": "white",
        "text": "black",
        "text_dark": "white",
        "text_muted": "slate-600",
        "border_radius": "rounded-xl",
        "border_width": "border-2",
        "shadow": "shadow-[4px_4px_0px_#000]",
        "shadow_hover": "shadow-[6px_6px_0px_#000]",
        "font": "font-sans",
    },
    "soft-ui": {
        "description": "Soft, neumorphic design with subtle depth",
        "primary": "blue-500",
        "primary_hover": "blue-600",
        "secondary": "slate-400",
        "background": "slate-100",
        "background_dark": "slate-800",
        "surface": "slate-100",
        "surface_dark": "slate-700",
        "border": "transparent",
        "border_dark": "transparent",
        "text": "slate-700",
        "text_dark": "slate-200",
        "text_muted": "slate-400",
        "border_radius": "rounded-2xl",
        "shadow": "shadow-[8px_8px_16px_#d1d5db,-8px_-8px_16px_#ffffff]",
        "shadow_dark": "shadow-[8px_8px_16px_#1e293b,-8px_-8px_16px_#475569]",
        "font": "font-sans",
    },
    "corporate": {
        "description": "Professional, trustworthy design",
        "primary": "blue-700",
        "primary_hover": "blue-800",
        "secondary": "slate-600",
        "background": "white",
        "background_dark": "slate-900",
        "surface": "slate-50",
        "surface_dark": "slate-800",
        "border": "slate-300",
        "border_dark": "slate-600",
        "text": "slate-800",
        "text_dark": "slate-100",
        "text_muted": "slate-500",
        "border_radius": "rounded-md",
        "shadow": "shadow",
        "shadow_hover": "shadow-lg",
        "font": "font-sans",
    },
}

# =============================================================================
# SYSTEM PROMPT FOR GEMINI 3 PRO
# =============================================================================

FRONTEND_DESIGN_SYSTEM_PROMPT = """You are an expert frontend designer specializing in TailwindCSS.
Your task is to generate high-quality, production-ready HTML components.

## OUTPUT FORMAT

You MUST respond with valid JSON in this exact format:
{
    "component_id": "unique-component-id",
    "atomic_level": "atom|molecule|organism",
    "html": "<div class=\\"...\\">...</div>",
    "tailwind_classes_used": ["class1", "class2"],
    "accessibility_features": ["aria-label", "focus-visible"],
    "responsive_breakpoints": ["sm", "md", "lg"],
    "dark_mode_support": true,
    "micro_interactions": ["hover:...", "transition-..."],
    "design_notes": "Brief explanation of design decisions"
}

## CRITICAL RULES

1. **Self-Contained HTML**: Generate ONLY the component HTML fragment. Never include:
   - <!DOCTYPE>, <html>, <head>, <body> tags
   - <script> or <style> tags
   - External dependencies or imports

2. **TailwindCSS Only**: Use only TailwindCSS utility classes. Never:
   - Write custom CSS
   - Use inline styles (style="...")
   - Reference external stylesheets

3. **Responsive Design**: Always include responsive variants:
   - Mobile-first approach (base styles for mobile)
   - sm: for 640px+
   - md: for 768px+
   - lg: for 1024px+
   - xl: for 1280px+ (when appropriate)

4. **Dark Mode**: Always include dark: variants for all colors:
   - bg-white dark:bg-slate-800
   - text-slate-900 dark:text-slate-100
   - border-slate-200 dark:border-slate-700

5. **Accessibility (WCAG 2.1 AA)**:
   - aria-label for interactive elements
   - focus-visible:ring-2 for keyboard navigation
   - sr-only for screen reader text
   - Proper heading hierarchy
   - Sufficient color contrast (4.5:1 minimum)

6. **Micro-Interactions**: Include smooth transitions:
   - transition-all duration-200 ease-in-out
   - hover: states for interactive elements
   - focus: states for form elements
   - active: states for buttons

7. **Visual Depth**: Create depth through:
   - Shadows (shadow-sm, shadow-md, shadow-lg)
   - Color gradients where appropriate
   - Subtle borders for separation

8. **Typography**: Use consistent type scale:
   - text-xs, text-sm, text-base, text-lg, text-xl, text-2xl
   - font-medium, font-semibold, font-bold for emphasis
   - tracking-tight for headings
   - leading-relaxed for body text

## DESIGN PRINCIPLES

1. **Hierarchy**: Clear visual hierarchy through size, weight, and spacing
2. **Consistency**: Consistent spacing using Tailwind scale (p-4, gap-6, etc.)
3. **Balance**: Balanced whitespace and content density
4. **Contrast**: Sufficient contrast for readability
5. **Alignment**: Consistent alignment using flexbox/grid

## EXAMPLE OUTPUT

For a button component:
{
    "component_id": "primary-cta-button",
    "atomic_level": "atom",
    "html": "<button class=\\"inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-semibold text-white bg-blue-600 rounded-lg shadow-sm hover:bg-blue-700 hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 dark:bg-blue-500 dark:hover:bg-blue-600\\" aria-label=\\"Subscribe to newsletter\\"><svg class=\\"w-5 h-5\\" fill=\\"none\\" viewBox=\\"0 0 24 24\\" stroke=\\"currentColor\\"><path stroke-linecap=\\"round\\" stroke-linejoin=\\"round\\" stroke-width=\\"2\\" d=\\"M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z\\"/></svg>Subscribe</button>",
    "tailwind_classes_used": ["inline-flex", "items-center", "justify-center", "gap-2", "px-6", "py-3", "text-sm", "font-semibold", "text-white", "bg-blue-600", "rounded-lg", "shadow-sm", "hover:bg-blue-700", "hover:shadow-md", "focus:outline-none", "focus-visible:ring-2", "focus-visible:ring-blue-500", "focus-visible:ring-offset-2", "active:scale-[0.98]", "disabled:opacity-50", "disabled:cursor-not-allowed", "transition-all", "duration-200", "dark:bg-blue-500", "dark:hover:bg-blue-600"],
    "accessibility_features": ["aria-label", "focus-visible:ring", "disabled state"],
    "responsive_breakpoints": [],
    "dark_mode_support": true,
    "micro_interactions": ["hover:bg-blue-700", "hover:shadow-md", "active:scale-[0.98]", "transition-all duration-200"],
    "design_notes": "Primary CTA button with mail icon. Uses focus-visible for keyboard-only focus rings. Scale transform on active for tactile feedback."
}

Remember: Quality over quantity. Every class should serve a purpose."""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_component_preset(component_type: str) -> Dict[str, Any]:
    """Get preset configuration for a component type.

    Args:
        component_type: The type of component (e.g., 'button', 'card', 'navbar')

    Returns:
        Dict with component preset configuration, or empty dict if not found.
    """
    return COMPONENT_PRESETS.get(component_type, {})


def get_theme_preset(theme_name: str) -> Dict[str, Any]:
    """Get preset configuration for a theme.

    Args:
        theme_name: The theme name (e.g., 'modern-minimal', 'brutalist')

    Returns:
        Dict with theme preset configuration, or default theme if not found.
    """
    return THEME_PRESETS.get(theme_name, THEME_PRESETS["modern-minimal"])


def get_available_components() -> List[str]:
    """Get list of available component types.

    Returns:
        List of component type names.
    """
    return list(COMPONENT_PRESETS.keys())


def get_available_themes() -> List[str]:
    """Get list of available theme names.

    Returns:
        List of theme names.
    """
    return list(THEME_PRESETS.keys())


def build_style_guide(
    theme: str,
    dark_mode: bool = True,
    border_radius: str = "",
    custom_overrides: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Build a complete style guide from theme and customizations.

    Args:
        theme: Theme name to use as base.
        dark_mode: Whether to include dark mode variants.
        border_radius: Custom border radius override.
        custom_overrides: Additional style overrides.

    Returns:
        Complete style guide dictionary.
    """
    style_guide = get_theme_preset(theme).copy()
    style_guide["dark_mode_enabled"] = dark_mode

    if border_radius:
        style_guide["border_radius"] = border_radius

    if custom_overrides:
        style_guide.update(custom_overrides)

    return style_guide
