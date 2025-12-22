"""Gemini MCP Server - Design-Focused FastMCP implementation.

Provides frontend design tools powered by Gemini models on Vertex AI:
- design_frontend: High-quality UI component design with TailwindCSS
- design_page: Full page layout generation
- design_section: Section-by-section page building
- design_from_reference: Design based on reference images
- refine_frontend: Iterative design improvements
- generate_image: Design asset generation (hero images, product visuals)
- validate_theme_contrast: WCAG accessibility validation
- list_models: Available models and capabilities
"""

import json
import logging

from mcp.server.fastmcp import FastMCP

from .client import get_gemini_client, fix_js_fallbacks
from .config import AVAILABLE_MODELS, get_config
from .frontend_presets import (
    build_style_guide,
    get_available_components,
    get_available_templates,
    get_page_template,
    PAGE_TEMPLATES,
    THEME_PRESETS,
    SECTION_TYPES,
    # MAXIMUM_RICHNESS mode support
    MICRO_INTERACTIONS,
    VISUAL_EFFECTS,
    SVG_ICONS,
    get_available_icon_names,
    get_icons_by_category,
)

# =============================================================================
# THEME FACTORY IMPORTS - Advanced Theme Customization
# =============================================================================
from .theme_factories import (
    # Factory Functions (14 themes)
    create_modern_minimal_theme,
    create_brutalist_theme,
    create_glassmorphism_theme,
    create_neo_brutalism_theme,
    create_soft_ui_theme,
    create_corporate_theme,
    create_gradient_theme,
    create_cyberpunk_theme,
    create_retro_theme,
    create_pastel_theme,
    create_dark_mode_first_theme,
    create_high_contrast_theme,
    create_nature_theme,
    create_startup_theme,
    # Utility Classes
    BrandColors,
    # Utility Functions
    validate_contrast,
    list_gradients_by_category,
    # Constants - Presets
    BRUTALIST_CONTRAST_PAIRS,
    NEOBRUTALISM_GRADIENTS,
    GRADIENT_ANIMATIONS,
    GRADIENT_LIBRARY,
    NEON_COLORS,
    GLOW_INTENSITIES,
    RETRO_FONT_PAIRINGS,
    PASTEL_ACCESSIBLE_PAIRS,
    NATURE_SEASONS,
    STARTUP_ARCHETYPES,
    CORPORATE_INDUSTRIES,
    CORPORATE_LAYOUTS,
)

from .section_utils import (
    extract_section,
    replace_section,
    list_sections,
    extract_design_tokens_from_section,
    wrap_content_with_markers,
    has_section_markers,
)

# Logger instance - configured in main() to use stderr (not stdout)
# IMPORTANT: Do NOT use logging.basicConfig() here - it breaks MCP stdio protocol
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP(
    "Gemini MCP",
    instructions="""
    Gemini MCP Server - Design-Focused Frontend Development

    This MCP server is specialized for high-quality frontend UI/UX design using
    Gemini models on Vertex AI. All tools are optimized for generating production-ready
    HTML components with TailwindCSS.

    Available Design Tools:
    - design_frontend: Create UI components (buttons, cards, forms, etc.) with 14 themes
    - design_page: Generate complete page layouts (landing, dashboard, auth, etc.)
    - design_section: Build pages section-by-section with style consistency
    - design_from_reference: Design based on reference images using Gemini Vision
    - refine_frontend: Iterate and improve existing designs
    - replace_section_in_page: Update specific sections while preserving others
    - generate_image: Create design assets (hero backgrounds, product images)
    - validate_theme_contrast: Check WCAG accessibility compliance
    - list_frontend_options: See all available components, themes, and customization options
    - list_models: View available Gemini models

    Features:
    - 14 customizable themes (modern-minimal, cyberpunk, glassmorphism, etc.)
    - MAXIMUM_RICHNESS mode for detailed, realistic outputs
    - Turkish content by default, with EN/DE support
    - WCAG AA/AAA accessibility compliance
    - Dark mode support in all designs

    Authentication is handled automatically via Application Default Credentials
    or gcloud CLI token.
    """,
)


# =============================================================================
# THEME FACTORY HELPER
# =============================================================================

def build_advanced_style_guide(
    theme: str,
    dark_mode: bool = True,
    border_radius: str = "",
    # Modern-Minimal customization
    brand_primary: str = "",
    neutral_base: str = "slate",
    # Brutalist customization
    contrast_mode: str = "standard",
    # Glassmorphism customization
    blur_intensity: str = "xl",
    glass_opacity: float = 0.7,
    performance_mode: str = "balanced",
    # Neo-Brutalism customization
    gradient_preset: str = "sunset",
    gradient_animation: str = "flow",
    # Soft-UI customization
    neumorphism_intensity: str = "medium",
    # Corporate customization
    industry: str = "consulting",
    layout_style: str = "modern",
    formality: str = "semi-formal",
    # Gradient customization
    primary_gradient: str = "aurora",
    # Cyberpunk customization
    primary_neon: str = "cyan",
    neon_intensity: str = "medium",
    scanline_effect: bool = False,
    # Retro customization
    retro_era: str = "80s_neon",
    retro_color_scheme: str = "neon",
    # Pastel customization
    primary_pastel: str = "rose",
    wcag_level: str = "AA",
    # Dark Mode First customization
    primary_glow: str = "emerald",
    light_mode_style: str = "minimal",
    # High Contrast customization
    softness_level: str = "balanced",
    hc_color_scheme: str = "blue",
    # Nature customization
    season: str = "spring",
    organic_shapes: bool = True,
    eco_friendly_mode: bool = False,
    archetype: str = "disruptor",
    startup_stage: str = "growth",
    vibe: str = "",
) -> dict:
    """
    Build style guide using advanced theme factories.
    
    Falls back to basic build_style_guide for simple cases.
    """
    # 1. First, compute the base theme from factory
    style_guide = {}
    
    if theme == "modern-minimal":
        if brand_primary:
            try:
                brand = BrandColors.from_hex(brand_primary)
            except Exception:
                brand = None
        else:
            brand = None
        
        style_guide = create_modern_minimal_theme(
            brand=brand,
            neutral_base=neutral_base if neutral_base in ["slate", "gray", "zinc", "neutral", "stone"] else "slate",
            border_radius=border_radius.replace("rounded-", "") if border_radius else "lg",
            shadow_intensity="sm",
        )
    
    elif theme == "brutalist":
        style_guide = create_brutalist_theme(
            contrast_mode=contrast_mode if contrast_mode in ["standard", "high", "maximum"] else "high",
            accent_color="yellow-400",
            include_focus_indicators=True,
        )
    
    elif theme == "glassmorphism":
        style_guide = create_glassmorphism_theme(
            blur_intensity=blur_intensity if blur_intensity in ["sm", "md", "lg", "xl", "2xl", "3xl"] else "xl",
            opacity=glass_opacity if 0.3 <= glass_opacity <= 0.95 else 0.7,
            tint_color="white",
            enable_fallback=True,
            performance_mode=performance_mode if performance_mode in ["quality", "balanced", "performance"] else "balanced",
        )
    
    elif theme == "neo-brutalism":
        style_guide = create_neo_brutalism_theme(
            gradient_preset=gradient_preset if gradient_preset in ["sunset", "ocean", "forest", "candy", "fire"] else "sunset",
            animation=gradient_animation if gradient_animation in ["none", "flow", "pulse", "shimmer", "wave"] else "flow",
            animation_speed="normal",
            shadow_color="black",
            include_hover_animations=True,
        )
    
    elif theme == "soft-ui":
        style_guide = create_soft_ui_theme(
            base_color_light="slate-100",
            base_color_dark="slate-800",
            primary_color="blue-500",
            intensity=neumorphism_intensity if neumorphism_intensity in ["subtle", "medium", "strong"] else "medium",
        )
    
    elif theme == "corporate":
        style_guide = create_corporate_theme(
            industry=industry if industry in ["finance", "healthcare", "legal", "tech", "manufacturing", "consulting"] else "consulting",
            layout=layout_style if layout_style in ["traditional", "modern", "editorial"] else "modern",
            formality=formality if formality in ["formal", "semi-formal", "approachable"] else "semi-formal",
            include_accent_gradients=False,
        )
    
    elif theme == "gradient":
        style_guide = create_gradient_theme(
            primary_gradient=primary_gradient if primary_gradient in GRADIENT_LIBRARY else "aurora",
            secondary_gradient="ocean",
            button_style="gradient",
            card_style="subtle",
            include_animations=True,
        )
    
    elif theme == "cyberpunk":
        style_guide = create_cyberpunk_theme(
            primary_neon=primary_neon if primary_neon in NEON_COLORS else "cyan",
            secondary_neon="fuchsia",
            glow_intensity=neon_intensity if neon_intensity in ["subtle", "medium", "strong", "intense", "extreme"] else "medium",
            enable_animations=True,
            scanline_effect=scanline_effect,
        )
    
    elif theme == "retro":
        style_guide = create_retro_theme(
            era=retro_era if retro_era in ["80s_tech", "80s_neon", "90s_grunge", "90s_web", "retro_futurism", "vintage_americana"] else "80s_neon",
            color_scheme=retro_color_scheme if retro_color_scheme in ["neon", "pastel", "earthy", "chrome"] else "neon",
            enable_crt_effects=False,
        )
    
    elif theme == "pastel":
        style_guide = create_pastel_theme(
            primary_pastel=primary_pastel if primary_pastel in ["rose", "pink", "sky", "violet", "teal", "amber", "lime"] else "rose",
            secondary_pastel="sky",
            wcag_level=wcag_level if wcag_level in ["AA", "AAA"] else "AA",
            dark_mode_handling="desaturate",
        )
    
    elif theme == "dark_mode_first":
        style_guide = create_dark_mode_first_theme(
            primary_glow=primary_glow if primary_glow in ["emerald", "cyan", "violet", "amber"] else "emerald",
            contrast_level="high" if contrast_mode == "high" else "normal",
            light_mode_style=light_mode_style if light_mode_style in ["minimal", "warm", "cool", "inverted"] else "minimal",
        )
    
    elif theme == "high_contrast":
        style_guide = create_high_contrast_theme(
            softness_level=softness_level if softness_level in ["sharp", "balanced", "smooth"] else "balanced",
            color_scheme=hc_color_scheme if hc_color_scheme in ["blue", "purple", "green", "neutral"] else "blue",
            animation_preference="reduced",
        )
    
    elif theme == "nature":
        style_guide = create_nature_theme(
            season=season if season in ["spring", "summer", "autumn", "winter"] else "spring",
            organic_shapes=organic_shapes,
            eco_friendly_mode=eco_friendly_mode,
        )
    
    elif theme == "startup":
        style_guide = create_startup_theme(
            archetype=archetype if archetype in ["disruptor", "enterprise", "consumer", "fintech", "healthtech", "ai_ml", "sustainability"] else "disruptor",
            stage=startup_stage if startup_stage in ["seed", "growth", "scale"] else "growth",
            enable_motion=True,
        )
    
    else:
        # Fallback to basic style guide
        style_guide = build_style_guide(
            theme=theme,
            dark_mode=dark_mode,
            border_radius=border_radius,
        )
    
    # 2. Add Vibe Specifications if requested
    if vibe:
        from .theme_factories import get_vibe_specs
        vibe_specs = get_vibe_specs(vibe)
        style_guide["vibe_specs"] = vibe_specs
        style_guide["vibe"] = vibe
        
        # Inject vibe-specific CSS variables
        if "css_variables" not in style_guide:
            style_guide["css_variables"] = {}
        
        style_guide["css_variables"].update({
            "--vibe-easing": vibe_specs.get("easing", "ease-in-out"),
            "--vibe-duration": vibe_specs.get("duration", "300ms"),
            "--vibe-shadow-glow": vibe_specs.get("shadow_glow", "transparent"),
        })
        
    return style_guide


@mcp.tool()
async def generate_image(
    prompt: str,
    model: str = "gemini-3-pro-image-preview",
    aspect_ratio: str = "1:1",
    output_format: str = "base64",
    output_dir: str = "./images",
    number_of_images: int = 1,
    output_resolution: str = "1K",
) -> dict:
    """Generate design assets using Gemini or Imagen models.
    
    Args:
        prompt: Description of the asset.
        model: Model name.
        aspect_ratio: Image ratio.
        output_format: base64 or file.
        output_dir: Save directory.
        number_of_images: Image count.
        output_resolution: Resolution (1K/2K).
    """
    try:
        client = get_gemini_client()
        result = await client.generate_image(
            prompt=prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            output_format=output_format,
            output_dir=output_dir,
            number_of_images=number_of_images,
            output_resolution=output_resolution,
        )
        logger.info(f"generate_image completed with model {result['model_used']}")
        return result

    except Exception as e:
        logger.error(f"generate_image failed: {e}")
        return {
            "error": str(e),
            "model_used": model,
            "prompt": prompt,
        }


@mcp.tool()
async def design_frontend(
    component_type: str,
    context: str = "",
    content_structure: str = "{}",
    theme: str = "modern-minimal",
    dark_mode: bool = True,
    border_radius: str = "",
    responsive_breakpoints: str = "sm,md,lg",
    accessibility_level: str = "AA",
    micro_interactions: bool = True,
    max_width: str = "",
    project_context: str = "",
    auto_fix: bool = True,
    content_language: str = "tr",
    # =================================================================
    # NEW: Advanced Theme Customization Parameters
    # =================================================================
    # Modern-Minimal
    brand_primary: str = "",
    neutral_base: str = "slate",
    # Brutalist
    contrast_mode: str = "standard",
    # Glassmorphism
    blur_intensity: str = "xl",
    glass_opacity: float = 0.7,
    performance_mode: str = "balanced",
    # Neo-Brutalism
    gradient_preset: str = "sunset",
    gradient_animation: str = "flow",
    # Soft-UI
    neumorphism_intensity: str = "medium",
    # Corporate
    industry: str = "consulting",
    layout_style: str = "modern",
    formality: str = "semi-formal",
    # Gradient Theme
    primary_gradient: str = "aurora",
    # Cyberpunk
    primary_neon: str = "cyan",
    neon_intensity: str = "medium",
    scanline_effect: bool = False,
    # Retro
    retro_era: str = "80s_neon",
    retro_color_scheme: str = "neon",
    # Pastel
    primary_pastel: str = "rose",
    wcag_level: str = "AA",
    # Dark Mode First
    primary_glow: str = "emerald",
    light_mode_style: str = "minimal",
    # High Contrast
    softness_level: str = "balanced",
    hc_color_scheme: str = "blue",
    # Nature
    season: str = "spring",
    organic_shapes: bool = True,
    eco_friendly_mode: bool = False,
    # Startup
    archetype: str = "disruptor",
    startup_stage: str = "growth",
    vibe: str = "",
) -> dict:
    """Design a frontend UI component using Gemini 3 Pro.

    This tool generates high-quality, production-ready HTML components with
    TailwindCSS. Always uses gemini-3-pro-preview for best design quality.
    Perfect for creating UI components that Claude Code can then integrate
    into a larger application.

    IMPORTANT: Content language defaults to Turkish (tr). Use content_language
    parameter to generate content in other languages (en, de).

    ADVANCED THEME CUSTOMIZATION:
    Each theme now supports deep customization via factory parameters.
    See theme-specific parameters below.

    Workflow:
    1. Claude analyzes the feature requirements
    2. Claude breaks down into atomic components (atoms, molecules, organisms)
    3. Claude calls design_frontend for each component with the same theme
    4. Gemini 3 Pro generates high-quality HTML with TailwindCSS
    5. Claude assembles the components into a complete page

    Args:
        component_type: Type of component to design. Options:
            Atoms: button, input, badge, avatar, icon, dropdown, toggle, tooltip,
                   slider, spinner, progress, chip, divider
            Molecules: card, form, modal, tabs, table, accordion, alert, breadcrumb,
                      pagination, search_bar, stat_card, pricing_card, carousel,
                      stepper, timeline, file_upload, rating, color_picker
            Organisms: navbar, hero, sidebar, footer, data_table, login_form,
                      signup_form, contact_form, feature_section, testimonial_section,
                      pricing_table, dashboard_header, kanban_board, calendar,
                      chat_widget, notification_center, user_profile, settings_panel
        context: Usage context explaining where/how the component will be used.
                Example: "Primary CTA button for newsletter signup on landing page"
        content_structure: JSON string with component content. Example:
                          '{"text": "Abone Ol", "icon": "mail"}'
                          '{"tier": "Pro", "price": "₺299/ay", "features": ["Sınırsız kullanıcı"]}'
        theme: Visual style preset. Options:
               - modern-minimal: Clean, professional (default)
               - brutalist: Bold, high-contrast, sharp edges
               - glassmorphism: Frosted glass, transparency
               - neo-brutalism: Playful with bold colors
               - soft-ui: Neumorphic, soft depth
               - corporate: Professional, trustworthy
               - gradient: Gradient-heavy modern design
               - cyberpunk: Neon colors, dark background
               - retro: 80s/90s inspired
               - pastel: Soft pastel colors
               - dark_mode_first: Dark mode optimized
               - high_contrast: WCAG AAA accessible
               - nature: Earth tones, organic feel
               - startup: Tech startup aesthetic
        vibe: Optional design spirit / persona. Options:
               - elite_corporate: Precise, luxury corporate
               - playful_funny: High energy, bouncy, witty
               - cyberpunk_edge: High contrast, neon, industrial
               - luxury_editorial: Elegant, spacious, serif-heavy
        dark_mode: Include dark: variants for dark mode support (default: True)
        border_radius: Custom border radius override (e.g., "rounded-xl")
        responsive_breakpoints: Comma-separated breakpoints (default: "sm,md,lg")
        accessibility_level: WCAG level - "AA" or "AAA" (default: "AA")
        micro_interactions: Include hover/focus animations (default: True)
        max_width: Maximum width constraint (e.g., "1280px", "max-w-7xl")
        project_context: Project-specific context for design consistency.
        auto_fix: Apply JS fallback fixes automatically (default: True)
        content_language: Language for generated content (default: "tr")
        
        --- THEME-SPECIFIC CUSTOMIZATION ---
        
        MODERN-MINIMAL:
            brand_primary: Hex color for brand (e.g., "#E11D48"). Auto-generates palette.
            neutral_base: Gray family - "slate", "gray", "zinc", "neutral", "stone"
        
        BRUTALIST:
            contrast_mode: "standard" (4.5:1), "high" (7:1), "maximum" (10:1+)
        
        GLASSMORPHISM:
            blur_intensity: "sm", "md", "lg", "xl", "2xl", "3xl"
            glass_opacity: 0.3 to 0.95 (default: 0.7)
            performance_mode: "quality", "balanced", "performance" (Safari optimization)
        
        NEO-BRUTALISM:
            gradient_preset: "sunset", "ocean", "forest", "candy", "fire"
            gradient_animation: "none", "flow", "pulse", "shimmer", "wave"
        
        SOFT-UI:
            neumorphism_intensity: "subtle", "medium", "strong"
        
        CORPORATE:
            industry: "finance", "healthcare", "legal", "tech", "manufacturing", "consulting"
            layout_style: "traditional", "modern", "editorial"
            formality: "formal", "semi-formal", "approachable"
        
        GRADIENT:
            primary_gradient: "aurora", "sunset", "ocean", "forest", "fire", 
                             "slate_subtle", "mesh_purple", "dark_aurora", etc. (20+ options)
        
        CYBERPUNK:
            primary_neon: "cyan", "fuchsia", "yellow", "green", "pink", "blue", "purple", "red", "orange"
            neon_intensity: "subtle", "medium", "strong", "intense", "extreme"
            scanline_effect: True/False for CRT-style scanlines
        
        RETRO:
            retro_era: "80s_tech", "80s_neon", "90s_grunge", "90s_web", "retro_futurism", "vintage_americana"
            retro_color_scheme: "neon", "pastel", "earthy", "chrome"
        
        PASTEL:
            primary_pastel: "rose", "pink", "sky", "violet", "teal", "amber", "lime"
            wcag_level: "AA" (4.5:1) or "AAA" (7:1) contrast
        
        DARK_MODE_FIRST:
            primary_glow: "emerald", "cyan", "violet", "amber"
            light_mode_style: "minimal", "warm", "cool", "inverted"
        
        HIGH_CONTRAST:
            softness_level: "sharp" (no radius), "balanced", "smooth"
            hc_color_scheme: "blue", "purple", "green", "neutral"
        
        NATURE:
            season: "spring", "summer", "autumn", "winter"
            organic_shapes: True for blob-like rounded corners
            eco_friendly_mode: True for simpler visuals (less energy)
        
        STARTUP:
            archetype: "disruptor", "enterprise", "consumer", "fintech", 
                      "healthtech", "ai_ml", "sustainability"
            startup_stage: "seed" (bold), "growth" (balanced), "scale" (refined)

    Returns:
        Dict containing:
        - component_id: Unique identifier for the component
        - atomic_level: atom, molecule, or organism
        - html: Self-contained HTML with TailwindCSS (ready to use)
        - tailwind_classes_used: List of Tailwind classes used
        - accessibility_features: A11y features implemented
        - responsive_breakpoints: Breakpoints used
        - dark_mode_support: Whether dark mode is supported
        - micro_interactions: Animation/transition classes
        - design_notes: Gemini's explanation of design decisions
        - theme_config: Advanced theme configuration used
        - model_used: Always gemini-3-pro-preview

    Examples:
        # Custom Brand Colors (Modern-Minimal)
        design_frontend(
            component_type="button",
            theme="modern-minimal",
            brand_primary="#E11D48",  # Rose brand color
            neutral_base="zinc"
        )

        # High Contrast Brutalist
        design_frontend(
            component_type="card",
            theme="brutalist",
            contrast_mode="maximum"  # WCAG AAA+
        )

        # Cyberpunk with Intense Glow
        design_frontend(
            component_type="navbar",
            theme="cyberpunk",
            primary_neon="fuchsia",
            neon_intensity="intense",
            scanline_effect=True
        )

        # Nature Theme - Autumn Season
        design_frontend(
            component_type="hero",
            theme="nature",
            season="autumn",
            organic_shapes=True
        )

        # Startup - Fintech Archetype
        design_frontend(
            component_type="pricing_card",
            theme="startup",
            archetype="fintech",
            startup_stage="growth"
        )
    """
    try:
        # Parse content_structure from JSON string
        try:
            content = json.loads(content_structure) if content_structure else {}
        except json.JSONDecodeError:
            content = {"raw": content_structure}

        # Build design specification
        design_spec = {
            "context": context,
            "content_structure": content,
        }

        # Build ADVANCED style guide using theme factories
        style_guide = build_advanced_style_guide(
            theme=theme,
            dark_mode=dark_mode,
            border_radius=border_radius,
            # Modern-Minimal
            brand_primary=brand_primary,
            neutral_base=neutral_base,
            # Brutalist
            contrast_mode=contrast_mode,
            # Glassmorphism
            blur_intensity=blur_intensity,
            glass_opacity=glass_opacity,
            performance_mode=performance_mode,
            # Neo-Brutalism
            gradient_preset=gradient_preset,
            gradient_animation=gradient_animation,
            # Soft-UI
            neumorphism_intensity=neumorphism_intensity,
            # Corporate
            industry=industry,
            layout_style=layout_style,
            formality=formality,
            # Gradient
            primary_gradient=primary_gradient,
            # Cyberpunk
            primary_neon=primary_neon,
            neon_intensity=neon_intensity,
            scanline_effect=scanline_effect,
            # Retro
            retro_era=retro_era,
            retro_color_scheme=retro_color_scheme,
            # Pastel
            primary_pastel=primary_pastel,
            wcag_level=wcag_level,
            # Dark Mode First
            primary_glow=primary_glow,
            light_mode_style=light_mode_style,
            # High Contrast
            softness_level=softness_level,
            hc_color_scheme=hc_color_scheme,
            # Nature
            season=season,
            organic_shapes=organic_shapes,
            eco_friendly_mode=eco_friendly_mode,
            # Startup
            archetype=archetype,
            startup_stage=startup_stage,
            vibe=vibe,
        )

        # Build constraints
        constraints = {
            "responsive_breakpoints": [bp.strip() for bp in responsive_breakpoints.split(",")],
            "accessibility_level": accessibility_level,
            "micro_interactions": micro_interactions,
            # MAXIMUM_RICHNESS mode directives
            "output_mode": "MAXIMUM_RICHNESS",
            "min_table_rows": 8,
            "min_list_items": 6,
            "generate_all_states": True,  # hover, focus, active, disabled, loading, error
            "inline_svgs": True,  # Use real SVG markup, not placeholders
            "realistic_turkish_content": True,
            "available_effects": list(VISUAL_EFFECTS.keys()),
            "available_icons": list(SVG_ICONS.keys())[:25],  # Top 25 icons for reference
        }
        if max_width:
            constraints["max_width"] = max_width

        # Call the design method
        client = get_gemini_client()
        result = await client.design_component(
            component_type=component_type,
            design_spec=design_spec,
            style_guide=style_guide,
            constraints=constraints,
            project_context=project_context,
            content_language=content_language,
        )

        # Apply JS fallback fixes if enabled
        if auto_fix and "html" in result:
            result["html"], fixes = fix_js_fallbacks(result["html"])
            if fixes:
                result["js_fixes_applied"] = fixes
                logger.info(f"Applied {len(fixes)} JS fallback fixes")

        # Add theme configuration to result
        result["theme_config"] = {
            "theme": theme,
            "customizations_applied": _get_applied_customizations(
                theme, brand_primary, contrast_mode, blur_intensity, 
                gradient_preset, neon_intensity, retro_era, season, archetype
            ),
        }

        logger.info(f"design_frontend completed: {component_type} -> {result.get('component_id', 'unknown')}")
        return result

    except Exception as e:
        logger.error(f"design_frontend failed: {e}")
        return {
            "error": str(e),
            "component_type": component_type,
            "model_used": "gemini-3-pro-preview",
        }


def _get_applied_customizations(
    theme: str,
    brand_primary: str,
    contrast_mode: str,
    blur_intensity: str,
    gradient_preset: str,
    neon_intensity: str,
    retro_era: str,
    season: str,
    archetype: str,
) -> dict:
    """Get customizations that were applied based on theme."""
    customizations = {}
    
    if theme == "modern-minimal" and brand_primary:
        customizations["brand_primary"] = brand_primary
    elif theme == "brutalist" and contrast_mode != "standard":
        customizations["contrast_mode"] = contrast_mode
    elif theme == "glassmorphism":
        customizations["blur_intensity"] = blur_intensity
    elif theme == "neo-brutalism":
        customizations["gradient_preset"] = gradient_preset
    elif theme == "cyberpunk":
        customizations["neon_intensity"] = neon_intensity
    elif theme == "retro":
        customizations["era"] = retro_era
    elif theme == "nature":
        customizations["season"] = season
    elif theme == "startup":
        customizations["archetype"] = archetype
    
    return customizations


@mcp.tool()
def list_frontend_options() -> dict:
    """List available frontend design options including advanced theme customization.

    Returns all available component types, themes, templates, section types,
    and NEW: advanced theme factory options for deep customization.

    Returns:
        Dict containing:
        - components: List of available component types (atoms, molecules, organisms)
        - themes: List of available theme presets with descriptions
        - templates: List of available page templates
        - sections: List of available section types for design_section
        - theme_factories: NEW - Advanced customization options for each theme
        - micro_interactions: Available interaction presets
        - visual_effects: Available visual effect presets
        - icons: Available SVG icons
    """
    # Get theme details
    themes_with_details = {
        name: {"description": preset.get("description", "")}
        for name, preset in THEME_PRESETS.items()
    }

    # Get template details
    templates_with_details = {
        name: {
            "description": preset.get("description", ""),
            "sections": preset.get("sections", []),
        }
        for name, preset in PAGE_TEMPLATES.items()
    }

    # Get section details
    sections_with_details = {
        name: {
            "description": info.get("description", ""),
            "typical_elements": info.get("typical_elements", []),
        }
        for name, info in SECTION_TYPES.items()
    }

    # Get micro-interaction details
    interactions_with_details = {
        name: {
            "classes": preset.get("classes", ""),
            "description": preset.get("description", ""),
        }
        for name, preset in MICRO_INTERACTIONS.items()
    }

    # Get visual effect details
    effects_with_details = {
        name: {
            "classes": preset.get("classes", ""),
            "description": preset.get("description", ""),
        }
        for name, preset in VISUAL_EFFECTS.items()
    }

    # NEW: Advanced Theme Factory Options
    theme_factory_options = {
        "modern-minimal": {
            "description": "Dynamic brand color customization",
            "parameters": {
                "brand_primary": "Hex color (e.g., '#E11D48'). Auto-generates full palette.",
                "neutral_base": ["slate", "gray", "zinc", "neutral", "stone"],
            },
            "example": 'brand_primary="#E11D48", neutral_base="zinc"',
        },
        "brutalist": {
            "description": "WCAG-compliant contrast levels",
            "parameters": {
                "contrast_mode": ["standard (4.5:1)", "high (7:1)", "maximum (10:1+)"],
            },
            "contrast_pairs": list(BRUTALIST_CONTRAST_PAIRS.keys()),
        },
        "glassmorphism": {
            "description": "Safari-optimized frosted glass with fallbacks",
            "parameters": {
                "blur_intensity": ["sm", "md", "lg", "xl", "2xl", "3xl"],
                "glass_opacity": "0.3 to 0.95 (default: 0.7)",
                "performance_mode": ["quality", "balanced", "performance"],
            },
        },
        "neo-brutalism": {
            "description": "Animated gradient system",
            "parameters": {
                "gradient_preset": list(NEOBRUTALISM_GRADIENTS.keys()),
                "gradient_animation": list(GRADIENT_ANIMATIONS.keys()),
            },
        },
        "soft-ui": {
            "description": "Dual-mode neumorphism with calculated shadows",
            "parameters": {
                "neumorphism_intensity": ["subtle", "medium", "strong"],
            },
        },
        "corporate": {
            "description": "Industry-specific professional themes",
            "parameters": {
                "industry": list(CORPORATE_INDUSTRIES.keys()),
                "layout_style": list(CORPORATE_LAYOUTS.keys()),
                "formality": ["formal", "semi-formal", "approachable"],
            },
            "industries": {k: v.get("personality", "") for k, v in CORPORATE_INDUSTRIES.items()},
        },
        "gradient": {
            "description": "Comprehensive gradient library (20+ presets)",
            "parameters": {
                "primary_gradient": list(GRADIENT_LIBRARY.keys()),
            },
            "categories": {
                "vibrant": list_gradients_by_category("vibrant"),
                "subtle": list_gradients_by_category("subtle"),
                "mesh": list_gradients_by_category("mesh"),
                "dark": list_gradients_by_category("dark"),
                "animated": list_gradients_by_category("animated"),
            },
        },
        "cyberpunk": {
            "description": "Configurable neon glow system",
            "parameters": {
                "primary_neon": list(NEON_COLORS.keys()),
                "neon_intensity": list(GLOW_INTENSITIES.keys()),
                "scanline_effect": "True/False",
            },
        },
        "retro": {
            "description": "Era-specific font pairings and aesthetics",
            "parameters": {
                "retro_era": list(RETRO_FONT_PAIRINGS.keys()),
                "retro_color_scheme": ["neon", "pastel", "earthy", "chrome"],
            },
            "eras": {k: v.get("era", "") for k, v in RETRO_FONT_PAIRINGS.items()},
        },
        "pastel": {
            "description": "WCAG-compliant pastel with guaranteed contrast",
            "parameters": {
                "primary_pastel": list(PASTEL_ACCESSIBLE_PAIRS.keys()),
                "wcag_level": ["AA (4.5:1)", "AAA (7:1)"],
            },
        },
        "dark_mode_first": {
            "description": "Dark-optimized with polished light mode",
            "parameters": {
                "primary_glow": ["emerald", "cyan", "violet", "amber"],
                "light_mode_style": ["minimal", "warm", "cool", "inverted"],
            },
        },
        "high_contrast": {
            "description": "WCAG AAA with adjustable visual softness",
            "parameters": {
                "softness_level": ["sharp", "balanced", "smooth"],
                "hc_color_scheme": ["blue", "purple", "green", "neutral"],
            },
        },
        "nature": {
            "description": "Four seasons with organic shapes",
            "parameters": {
                "season": list(NATURE_SEASONS.keys()),
                "organic_shapes": "True/False",
                "eco_friendly_mode": "True/False (simpler = less energy)",
            },
            "seasons": {k: v.get("mood", "") for k, v in NATURE_SEASONS.items()},
        },
        "startup": {
            "description": "Archetype-based startup identity",
            "parameters": {
                "archetype": list(STARTUP_ARCHETYPES.keys()),
                "startup_stage": ["seed (bold)", "growth (balanced)", "scale (refined)"],
            },
            "archetypes": {k: v.get("tagline", "") for k, v in STARTUP_ARCHETYPES.items()},
        },
        "vibes": {
            "elite_corporate": "Precise, luxury corporate",
            "playful_funny": "High energy, bouncy, witty",
            "cyberpunk_edge": "High contrast, neon, industrial",
            "luxury_editorial": "Elegant, spacious, serif-heavy",
        },
    }

    return {
        "components": get_available_components(),
        "themes": themes_with_details,
        "templates": templates_with_details,
        "sections": sections_with_details,
        # NEW: Advanced Theme Factory Options
        "theme_factories": theme_factory_options,
        # MAXIMUM_RICHNESS mode resources
        "micro_interactions": interactions_with_details,
        "visual_effects": effects_with_details,
        "icons": {
            "available": get_available_icon_names(),
            "by_category": get_icons_by_category(),
            "total_count": len(SVG_ICONS),
        },
        "richness_mode": {
            "enabled": True,
            "directives": {
                "min_table_rows": 8,
                "min_list_items": 6,
                "generate_all_states": True,
                "inline_svgs": True,
                "realistic_turkish_content": True,
            },
        },
        "note": "Use design_frontend() for components with advanced theme customization. "
               "Each theme supports factory parameters for deep customization. "
               "MAXIMUM_RICHNESS mode is enabled by default.",
    }


@mcp.tool()
async def design_page(
    template_type: str,
    context: str = "",
    content_structure: str = "{}",
    theme: str = "modern-minimal",
    dark_mode: bool = True,
    project_context: str = "",
    content_language: str = "tr",
) -> dict:
    """Design a full page layout using Gemini 3 Pro.

    This tool generates complete page layouts with multiple sections.
    Content language is configurable (default: Turkish).

    Args:
        template_type: Type of page template. Options:
            - landing_page: Marketing landing page with hero, features, CTA
            - dashboard: Admin dashboard with sidebar, stats, data views
            - auth_page: Login/signup page with form and branding
            - pricing_page: Pricing comparison with tiers and FAQ
            - blog_post: Blog article layout with content and sidebar
            - product_page: E-commerce product page with gallery
            - portfolio: Portfolio/showcase page with projects grid
            - documentation: Docs page with navigation and content
            - error_page: 404/500 error page with helpful actions
            - coming_soon: Coming soon/maintenance page with countdown
        context: Usage context explaining the page purpose.
                Example: "Landing page for a Turkish SaaS product"
        content_structure: JSON string with page content. Example:
                          '{"title": "Hoş Geldiniz", "subtitle": "En iyi çözüm"}'
        theme: Visual style preset (same as design_frontend)
        dark_mode: Include dark mode support (default: True)
        project_context: Project-specific context for design consistency.
        content_language: Language code for content generation (default: "tr").
                         Supported: "tr" (Turkish), "en" (English), "de" (German).

    Returns:
        Dict containing:
        - page_id: Unique identifier for the page
        - template_type: The template used
        - html: Complete HTML with TailwindCSS
        - sections: List of sections included
        - design_notes: Gemini's explanation of design decisions
        - model_used: Always gemini-3-pro-preview
    """
    try:
        template = get_page_template(template_type)
        if not template:
            return {
                "error": f"Unknown template: {template_type}",
                "available_templates": get_available_templates(),
            }

        # Parse content_structure
        try:
            content = json.loads(content_structure) if content_structure else {}
        except json.JSONDecodeError:
            content = {"raw": content_structure}

        # Build design specification for a page
        design_spec = {
            "context": context,
            "content_structure": content,
            "template_info": template,
        }

        # Build style guide
        style_guide = build_style_guide(theme=theme, dark_mode=dark_mode)

        # Build constraints
        constraints = {
            "sections": template.get("sections", []),
            "layouts": template.get("layouts", []),
            "is_full_page": True,
        }

        # Call the design method with page template
        client = get_gemini_client()
        result = await client.design_component(
            component_type=f"page:{template_type}",
            design_spec=design_spec,
            style_guide=style_guide,
            constraints=constraints,
            project_context=project_context,
            content_language=content_language,
        )

        # Add template info to result
        result["template_type"] = template_type
        result["sections"] = template.get("sections", [])

        logger.info(f"design_page completed: {template_type}")
        return result

    except Exception as e:
        logger.error(f"design_page failed: {e}")
        return {
            "error": str(e),
            "template_type": template_type,
            "model_used": "gemini-3-pro-preview",
        }


@mcp.tool()
async def refine_frontend(
    previous_html: str,
    modifications: str,
    project_context: str = "",
    auto_fix: bool = True,
) -> dict:
    """Refine an existing component design based on feedback.

    Use this tool to iterate on a design without starting from scratch.
    Send the previous HTML and describe the changes you want.
    All content will be generated in Turkish.

    Args:
        previous_html: The existing HTML code to refine.
                      This should be the complete HTML from a previous
                      design_frontend or design_page call.
        modifications: Natural language description of desired changes.
                      Examples:
                      - "Buton rengini maviden yeşile çevir"
                      - "Header'ı daha kompakt yap"
                      - "Dark mode desteği ekle"
                      - "Mobil responsive sorunlarını düzelt"
                      - "Hover efektlerini daha belirgin yap"
        project_context: Optional project context for consistency.

    Returns:
        Dict containing:
        - component_id: Identifier for the refined component
        - html: The modified HTML with TailwindCSS
        - changes_made: Summary of changes applied
        - design_notes: Explanation of modifications
        - model_used: Always gemini-3-pro-preview

    Example:
        refine_frontend(
            previous_html='<button class="bg-blue-600...">Gönder</button>',
            modifications="Buton boyutunu büyüt ve hover efekti ekle"
        )
    """
    try:
        client = get_gemini_client()
        result = await client.refine_component(
            previous_html=previous_html,
            modifications=modifications,
            project_context=project_context,
        )

        # Apply JS fallback fixes if enabled
        if auto_fix and "html" in result:
            result["html"], fixes = fix_js_fallbacks(result["html"])
            if fixes:
                result["js_fixes_applied"] = fixes
                logger.info(f"Applied {len(fixes)} JS fallback fixes")

        logger.info(f"refine_frontend completed: {result.get('component_id', 'unknown')}")
        return result

    except Exception as e:
        logger.error(f"refine_frontend failed: {e}")
        return {
            "error": str(e),
            "modifications": modifications,
            "model_used": "gemini-3-pro-preview",
        }


@mcp.tool()
async def design_section(
    section_type: str,
    context: str = "",
    previous_html: str = "",
    design_tokens: str = "{}",
    content_structure: str = "{}",
    theme: str = "modern-minimal",
    project_context: str = "",
    auto_fix: bool = True,
    content_language: str = "tr",
) -> dict:
    """Design a single page section that matches previous sections.

    Use this tool to build large pages section-by-section, where each section
    maintains visual consistency with previous ones. This solves the token limit
    problem by designing one section at a time.

    Content language is configurable (default: Turkish).

    Chain Workflow:
    1. Design first section (e.g., hero) - no previous_html needed
    2. Design second section with previous_html from step 1
    3. Continue chain, each section matches the previous style
    4. Combine all sections into a complete page

    Args:
        section_type: Type of section to design. Options:
            - hero: Hero/banner section with headline and CTA
            - features: Feature showcase grid or list
            - pricing: Pricing tiers/cards
            - testimonials: Customer testimonials/reviews
            - cta: Call-to-action section
            - footer: Page footer with links
            - stats: Statistics/metrics display
            - faq: FAQ accordion section
            - team: Team members grid
            - contact: Contact form section
            - gallery: Image/portfolio gallery
            - newsletter: Newsletter signup section
        context: Usage context explaining where/how the section will be used.
                Example: "Hero section for a Turkish SaaS landing page"
        previous_html: HTML from previous section for style matching.
                      When provided, Gemini will analyze and match:
                      - Color palette (primary, secondary, background)
                      - Typography (fonts, weights, sizes)
                      - Spacing patterns (padding, margins)
                      - Border radius
                      - Shadow styles
                      - Animation patterns
        design_tokens: JSON string with explicit design tokens to use.
                      If not provided but previous_html is given, tokens
                      will be extracted automatically.
                      Format: '{"colors": {...}, "typography": {...}, "spacing": {...}}'
        content_structure: JSON string with section content. Example:
                          '{"headline": "Başlık", "subheadline": "Alt başlık", "cta": "Başla"}'
        theme: Visual style preset (modern-minimal, brutalist, etc.)
        project_context: Project-specific context for design consistency.
        content_language: Language code for content generation (default: "tr").
                         Supported: "tr" (Turkish), "en" (English), "de" (German).

    Returns:
        Dict containing:
        - section_type: Type of section designed
        - html: Self-contained HTML with TailwindCSS classes
        - design_tokens: Extracted design tokens for next section in chain
        - tailwind_classes_used: List of Tailwind classes used
        - accessibility_features: A11y features implemented
        - responsive_breakpoints: Breakpoints used
        - dark_mode_support: Whether dark mode is supported
        - design_notes: Gemini's design decisions explanation
        - model_used: Always gemini-3-pro-preview

    Example Chain:
        # 1. Start with hero
        hero = design_section(
            section_type="hero",
            context="Landing page for B2B SaaS"
        )

        # 2. Features section matching hero style
        features = design_section(
            section_type="features",
            previous_html=hero["html"],
            design_tokens=json.dumps(hero["design_tokens"])
        )

        # 3. Pricing section continuing the chain
        pricing = design_section(
            section_type="pricing",
            previous_html=features["html"],
            design_tokens=json.dumps(features["design_tokens"])
        )

        # 4. Combine all sections
        full_page = hero["html"] + features["html"] + pricing["html"]
    """
    try:
        # Parse design_tokens from JSON string
        try:
            tokens = json.loads(design_tokens) if design_tokens and design_tokens != "{}" else None
        except json.JSONDecodeError:
            tokens = None

        # Parse content_structure from JSON string
        try:
            content = json.loads(content_structure) if content_structure else {}
        except json.JSONDecodeError:
            content = {"raw": content_structure}

        # Call the design_section method
        client = get_gemini_client()
        result = await client.design_section(
            section_type=section_type,
            context=context,
            previous_html=previous_html,
            design_tokens=tokens,
            content_structure=content,
            theme=theme,
            project_context=project_context,
            content_language=content_language,
        )

        # Apply JS fallback fixes if enabled
        if auto_fix and "html" in result:
            result["html"], fixes = fix_js_fallbacks(result["html"])
            if fixes:
                result["js_fixes_applied"] = fixes
                logger.info(f"Applied {len(fixes)} JS fallback fixes")

        logger.info(
            f"design_section completed: {section_type} "
            f"(chain_mode={'yes' if previous_html else 'no'})"
        )
        return result

    except Exception as e:
        logger.error(f"design_section failed: {e}")
        return {
            "error": str(e),
            "section_type": section_type,
            "model_used": "gemini-3-pro-preview",
        }


@mcp.tool()
async def design_from_reference(
    image_path: str,
    component_type: str = "",
    instructions: str = "",
    context: str = "",
    project_context: str = "",
    extract_only: bool = False,
    auto_fix: bool = True,
    content_language: str = "tr",
) -> dict:
    """Design a component based on a reference image using Gemini Vision.

    This tool analyzes a screenshot or design reference image and creates
    a similar component with matching visual style. Uses Gemini's vision
    capabilities to extract design tokens (colors, typography, spacing, etc.)
    and then generates HTML matching those tokens.

    Two modes:
    - extract_only=True: Only extract design tokens, don't generate HTML
    - extract_only=False: Extract tokens AND generate matching component

    Content language is configurable (default: Turkish).

    Args:
        image_path: Path to the reference image file.
                   Supported formats: PNG, JPG, JPEG, WEBP, GIF.
                   Example: "/path/to/screenshot.png"
        component_type: Type of component to design based on the reference.
                       If empty and extract_only=False, will auto-detect from image.
                       Options: hero, navbar, card, pricing_card, footer, etc.
        instructions: Additional instructions for modifications.
                     Examples:
                     - "Buna benzer ama mavi tonlarında"
                     - "Daha minimalist bir versiyon"
                     - "Aynı stilde ama dark mode"
                     - "Spacing'i daha geniş tut"
        context: Usage context for the component.
                Example: "Hero section for a Turkish restaurant website"
        project_context: Project-specific context for design consistency.
                        Example: "Project: KokoreçUsta - Traditional restaurant.
                                 Target: Local customers. Tone: Warm, nostalgic."
        extract_only: If True, only extract and return design tokens.
                     If False, also generate a matching HTML component.
                     Default: False
        auto_fix: Apply JavaScript fallback fixes to generated HTML.
                 Default: True
        content_language: Language code for content generation (default: "tr").
                         Supported: "tr" (Turkish), "en" (English), "de" (German).

    Returns:
        Dict containing:
        - design_tokens: Extracted design tokens from the reference image
            - colors: Color palette with hex codes
            - typography: Font sizes, weights, line heights
            - spacing: Padding, margin, gap patterns
            - borders: Border radius, border styles
            - shadows: Shadow styles
            - layout: Grid/flex patterns detected
        - aesthetic: Overall design aesthetic (minimal, bold, etc.)
        - component_hints: Detected UI component types in the image
        - html: Generated HTML (only if extract_only=False)
        - design_notes: How the reference was interpreted
        - modifications: Changes made based on instructions
        - model_used: Always gemini-3-pro-preview

    Examples:
        # Extract only - useful for understanding a design
        design_from_reference(
            image_path="/path/to/inspiration.png",
            extract_only=True
        )

        # Full design from reference
        design_from_reference(
            image_path="/path/to/competitor-hero.png",
            component_type="hero",
            instructions="Buna benzer ama marka renklerimizle",
            project_context="Project: TeknoSoft - B2B SaaS"
        )

        # Match style but different component
        design_from_reference(
            image_path="/path/to/navbar-design.png",
            component_type="footer",  # Use navbar's style for footer
            instructions="Aynı stilde footer tasarla"
        )

    Workflow:
        1. Gemini Vision analyzes the reference image
        2. Extracts design tokens (colors, typography, spacing, etc.)
        3. Identifies aesthetic and component types
        4. (If extract_only=False) Generates matching HTML with TailwindCSS
        5. Applies JS fallback fixes if auto_fix=True
    """
    try:
        client = get_gemini_client()

        if extract_only:
            # Only extract design tokens, don't generate HTML
            result = await client.analyze_reference_image(
                image_path=image_path,
                extract_only=True,
            )
        else:
            # Extract tokens AND generate matching component
            result = await client.design_from_reference(
                image_path=image_path,
                component_type=component_type,
                instructions=instructions,
                context=context,
                project_context=project_context,
                content_language=content_language,
            )

            # Apply JS fallback fixes if enabled and HTML was generated
            if auto_fix and "html" in result:
                result["html"], fixes = fix_js_fallbacks(result["html"])
                if fixes:
                    result["js_fixes_applied"] = fixes
                    logger.info(f"Applied {len(fixes)} JS fallback fixes")

        logger.info(
            f"design_from_reference completed: "
            f"image={image_path}, extract_only={extract_only}, "
            f"component={component_type or 'auto'}"
        )
        return result

    except Exception as e:
        logger.error(f"design_from_reference failed: {e}")
        return {
            "error": str(e),
            "image_path": image_path,
            "component_type": component_type,
            "model_used": "gemini-3-pro-preview",
        }


@mcp.tool()
def list_models() -> dict:
    """List available Gemini models for design tasks.

    Returns information about image generation models available on Vertex AI.
    This MCP server is design-focused - use image models for creating
    design assets like hero backgrounds, product images, and illustrations.

    Returns:
        Dict containing image models with their specifications.
    """
    return {
        "image_models": AVAILABLE_MODELS["image"],
        "default_image_model": get_config().default_image_model if _config_valid() else "gemini-3-pro-image-preview",
        "note": "This MCP server is design-focused. Use generate_image for design assets.",
    }


@mcp.tool()
async def replace_section_in_page(
    page_html: str,
    section_type: str,
    modifications: str,
    preserve_design_tokens: bool = True,
    theme: str = "modern-minimal",
    content_language: str = "tr",
) -> dict:
    """Replace a single section in an existing page with an improved version.

    This tool enables iterative design improvement by replacing only the
    specified section while preserving all other sections. The new section
    maintains visual consistency with the rest of the page.

    CRITICAL: The page HTML must use section markers in this format:
    <!-- SECTION: {type} --> ... content ... <!-- /SECTION: {type} -->

    Args:
        page_html: Full HTML of the existing page with section markers.
        section_type: Section to replace. Valid types:
            - navbar: Navigation bars, headers
            - hero: Hero sections, landing areas
            - stats: Statistics, metrics sections
            - features: Feature grids, benefit lists
            - testimonials: Customer reviews, social proof
            - pricing: Pricing tables, plans
            - cta: Call-to-action sections
            - footer: Site footers
        modifications: Detailed description of desired changes.
                      Example: "Add mega menu, search bar, and announcement banner"
        preserve_design_tokens: Keep colors/typography consistent with page (default: True)
        theme: Visual style preset for the new section
        content_language: Language code for content (default: "tr")

    Returns:
        Dict containing:
        - html: Updated full page HTML with only the target section changed
        - modified_section: Which section was replaced
        - preserved_sections: List of sections that were NOT modified
        - design_notes: Explanation of design decisions
        - error: Error message if the operation failed

    Example:
        # Update only the navbar in an existing landing page
        result = replace_section_in_page(
            page_html=existing_page,
            section_type="navbar",
            modifications="Add mega menu with 4 columns, search bar, dark mode toggle"
        )

        # The result contains the complete updated page
        updated_page = result["html"]
        # Hero, Features, Pricing, Footer etc. are unchanged
    """
    try:
        # 1. Validate page has section markers
        if not has_section_markers(page_html):
            return {
                "error": "Page HTML does not contain section markers. "
                        "Section markers must be in format: <!-- SECTION: type --> ... <!-- /SECTION: type -->",
                "html": page_html,
                "modified_section": None,
            }

        # 2. List available sections
        available_sections = list_sections(page_html)

        if section_type not in available_sections:
            return {
                "error": f"Section '{section_type}' not found in page. "
                        f"Available sections: {available_sections}",
                "html": page_html,
                "modified_section": None,
                "available_sections": available_sections,
            }

        # 3. Extract current section content
        current_section = extract_section(page_html, section_type)

        # 4. Extract design tokens for consistency
        design_tokens = {}
        if preserve_design_tokens:
            # Try to extract tokens from adjacent sections for consistency
            for section_name in available_sections:
                if section_name != section_type:
                    tokens = extract_design_tokens_from_section(page_html, section_name)
                    if tokens:
                        design_tokens = tokens
                        break

        # 5. Generate new section using design_section
        client = get_gemini_client()
        new_section_result = await client.design_section(
            section_type=section_type,
            context=f"Replacing existing {section_type} section. Modifications: {modifications}",
            previous_html=current_section,
            design_tokens=design_tokens if design_tokens else None,
            content_structure={},
            theme=theme,
            project_context="This is part of an existing page. Maintain visual consistency.",
            content_language=content_language,
        )

        if "error" in new_section_result:
            return {
                "error": f"Failed to generate new section: {new_section_result['error']}",
                "html": page_html,
                "modified_section": None,
            }

        # 6. Get the new HTML (ensure it has markers)
        new_html = new_section_result.get("html", "")
        if not new_html:
            return {
                "error": "Generated section has no HTML content",
                "html": page_html,
                "modified_section": None,
            }

        # 7. Wrap with markers if not present
        if f"<!-- SECTION: {section_type} -->" not in new_html:
            new_html_content = new_html
        else:
            # Extract just the content without markers
            new_html_content = extract_section(
                wrap_content_with_markers(new_html, section_type),
                section_type
            ) or new_html

        # 8. Replace the section in the page
        try:
            updated_page = replace_section(page_html, section_type, new_html_content)
        except ValueError as e:
            return {
                "error": str(e),
                "html": page_html,
                "modified_section": None,
            }

        # 9. Return the result
        preserved = [s for s in available_sections if s != section_type]

        logger.info(
            f"replace_section_in_page completed: {section_type} replaced, "
            f"{len(preserved)} sections preserved"
        )

        return {
            "html": updated_page,
            "modified_section": section_type,
            "preserved_sections": preserved,
            "design_notes": new_section_result.get("design_notes", ""),
            "design_tokens_used": design_tokens if preserve_design_tokens else None,
            "model_used": new_section_result.get("model_used", "gemini-3-pro-preview"),
        }

    except Exception as e:
        logger.error(f"replace_section_in_page failed: {e}")
        return {
            "error": str(e),
            "html": page_html,
            "modified_section": None,
        }


@mcp.tool()
def validate_theme_contrast(
    foreground: str,
    background: str,
    wcag_level: str = "AA",
    text_size: str = "normal",
) -> dict:
    """Validate color contrast ratio for WCAG compliance.

    Use this tool to check if your color combinations meet accessibility
    standards before using them in designs.

    Args:
        foreground: Foreground (text) color in hex format (e.g., "#000000")
        background: Background color in hex format (e.g., "#FFFFFF")
        wcag_level: Target WCAG level - "AA" or "AAA"
        text_size: Text size category - "normal" or "large"
                  (large = 18pt+ or 14pt+ bold)

    Returns:
        Dict containing:
        - passes: Boolean indicating if contrast meets requirements
        - ratio: Calculated contrast ratio (e.g., 7.5)
        - required_ratio: Minimum required ratio for the level/size
        - message: Human-readable result message
        - recommendations: Suggestions if contrast fails

    Example:
        validate_theme_contrast(
            foreground="#FFFFFF",
            background="#3B82F6",  # blue-500
            wcag_level="AA"
        )
    """
    try:
        passes, ratio, message = validate_contrast(
            foreground=foreground,
            background=background,
            level=wcag_level,
            text_size=text_size,
        )

        requirements = {
            ("AA", "normal"): 4.5,
            ("AA", "large"): 3.0,
            ("AAA", "normal"): 7.0,
            ("AAA", "large"): 4.5,
        }
        required = requirements.get((wcag_level, text_size), 4.5)

        result = {
            "passes": passes,
            "ratio": round(ratio, 2),
            "required_ratio": required,
            "wcag_level": wcag_level,
            "text_size": text_size,
            "message": message,
        }

        if not passes:
            # Add recommendations
            result["recommendations"] = [
                f"Current ratio ({ratio:.2f}:1) is below required ({required}:1)",
                "Try darker foreground or lighter background for better contrast",
                "Consider using WCAG-compliant color pairs from theme factories",
            ]

        return result

    except Exception as e:
        return {
            "error": str(e),
            "foreground": foreground,
            "background": background,
        }


def _config_valid() -> bool:
    """Check if configuration is valid without raising errors."""
    try:
        get_config()
        return True
    except ValueError:
        return False


def main():
    """Entry point for the Gemini MCP server."""
    import sys

    # Configure logging to stderr (NOT stdout - stdout is for MCP protocol)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,  # CRITICAL: Use stderr, not stdout
    )

    logger.info("Starting Gemini MCP Server...")

    # Validate configuration on startup
    try:
        config = get_config()
        logger.info(f"Configuration loaded: project={config.project_id}, location={config.location}")
    except ValueError as e:
        logger.warning(f"Configuration incomplete: {e}")
        logger.warning("Server will start but tools may fail until GOOGLE_CLOUD_PROJECT is set")

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()