"""Gemini MCP Server - Vertex AI integration for Claude Code."""

__version__ = "0.1.0"

from .frontend_presets import (
    COMPONENT_PRESETS,
    THEME_PRESETS,
    get_available_components,
    get_available_themes,
    get_component_preset,
    get_theme_preset,
    build_style_guide,
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
