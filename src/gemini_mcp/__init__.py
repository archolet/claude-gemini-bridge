"""Gemini MCP Server - Vertex AI integration for Claude Code."""

__version__ = "0.1.0"

from .frontend_presets import (
    # Existing exports
    COMPONENT_PRESETS,
    THEME_PRESETS,
    get_available_components,
    get_available_themes,
    get_component_preset,
    get_theme_preset,
    build_style_guide,
    # MAXIMUM_RICHNESS mode - Effect Libraries
    MICRO_INTERACTIONS,
    VISUAL_EFFECTS,
    SVG_ICONS,
    # MAXIMUM_RICHNESS mode - Helper Functions
    get_micro_interaction,
    get_all_micro_interactions,
    get_available_interaction_names,
    get_visual_effect,
    get_all_visual_effects,
    get_available_effect_names,
    get_svg_icon,
    get_all_svg_icons,
    get_available_icon_names,
    get_icons_by_category,
    build_rich_style_guide,
)

from .schemas import (
    # Design Tokens
    DesignTokens,
    ColorTokens,
    TypographyTokens,
    SpacingTokens,
    BorderTokens,
    ShadowTokens,
    LayoutTokens,
    # Design Responses
    DesignResponse,
    SectionDesignResponse,
    PageDesignResponse,
    RefinementResponse,
    # Vision Responses
    VisionAnalysisResponse,
    ReferenceDesignResponse,
    # Design System State
    DesignSystemState,
    DesignSystemComponent,
    # Language Support
    LanguageConfig,
    LANGUAGE_CONFIGS,
    get_language_config,
    get_available_languages,
    # Validation Helpers
    validate_design_response,
    validate_vision_response,
    validate_design_tokens,
)

from .cache import (
    DesignCache,
    CacheEntry,
    get_design_cache,
    clear_design_cache,
)

from .error_recovery import (
    ErrorType,
    RecoveryStrategy,
    classify_error,
    calculate_delay,
    repair_json_response,
    extract_html_fallback,
    create_fallback_response,
    generate_fallback_html,
    with_retry,
    retry_async,
    ResponseValidator,
)

from .few_shot_examples import (
    COMPONENT_EXAMPLES,
    SECTION_CHAIN_EXAMPLES,
    get_few_shot_example,
    get_few_shot_examples_for_prompt,
)

from .section_utils import (
    # Section Marker Pattern
    SECTION_PATTERN,
    VALID_SECTION_TYPES,
    # Core Functions
    extract_section,
    replace_section,
    list_sections,
    get_section_boundaries,
    # Validation
    validate_section_type,
    # Extended Functions
    get_section_with_markers,
    insert_section_after,
    remove_section,
    extract_design_tokens_from_section,
    wrap_content_with_markers,
    has_section_markers,
    migrate_to_markers,
)

from .theme_factories import (
    # Color Utility Functions
    hex_to_rgb,
    rgb_to_hex,
    hex_to_hsl,
    hsl_to_hex,
    relative_luminance,
    contrast_ratio,
    validate_contrast,
    # Brand Colors
    BrandColors,
    # Theme Factory Functions (14 themes)
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
    # Theme-Specific Constants
    BRUTALIST_CONTRAST_PAIRS,
    NEOBRUTALISM_GRADIENTS,
    GRADIENT_ANIMATIONS,
    CORPORATE_INDUSTRIES,
    CORPORATE_LAYOUTS,
    GRADIENT_LIBRARY,
    NEON_COLORS,
    GLOW_INTENSITIES,
    RETRO_FONT_PAIRINGS,
    PASTEL_ACCESSIBLE_PAIRS,
    NATURE_SEASONS,
    STARTUP_ARCHETYPES,
    # Helper Functions
    calculate_neumorphism_shadows,
    generate_neon_glow,
    get_gradient,
    list_gradients_by_category,
)
