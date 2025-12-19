"""Gemini MCP Server - FastMCP implementation.

Provides tools for interacting with Gemini models on Vertex AI:
- ask_gemini: Text generation with context
- chat_gemini: Multi-turn conversations
- generate_image: Image generation
- design_frontend: Frontend component design with TailwindCSS
- list_models: Available models
"""

import json
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .client import get_gemini_client, fix_js_fallbacks
from .config import AVAILABLE_MODELS, get_config
from .frontend_presets import (
    build_style_guide,
    build_system_prompt,
    build_refinement_prompt,
    get_available_components,
    get_available_themes,
    get_available_templates,
    get_page_template,
    get_section_types,
    get_section_info,
    PAGE_TEMPLATES,
    THEME_PRESETS,
    SECTION_TYPES,
    # MAXIMUM_RICHNESS mode support
    MICRO_INTERACTIONS,
    VISUAL_EFFECTS,
    SVG_ICONS,
    get_all_micro_interactions,
    get_all_visual_effects,
    get_available_icon_names,
    get_icons_by_category,
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
    Gemini MCP Server provides access to Google's Gemini models via Vertex AI.

    Available tools:
    - ask_gemini: Generate text with optional context and system instructions
    - chat_gemini: Have multi-turn conversations with session management
    - generate_image: Create images using Gemini or Imagen models
    - design_frontend: Design high-quality frontend components with TailwindCSS
    - list_models: See available models and their capabilities

    Authentication is handled automatically via Application Default Credentials
    or gcloud CLI token.
    """,
)


@mcp.tool()
async def ask_gemini(
    prompt: str,
    context: str = "",
    system_instruction: str = "",
    model: str = "gemini-3-flash-preview",
    temperature: float = 0.7,
    max_tokens: int = 65536,
    thinking_level: str = "medium",
    stream: bool = True,
) -> dict:
    """Ask Gemini 3 a question with optional context from Claude.

    Use this tool to get Gemini 3's perspective on a problem, code review,
    or any task where you want an alternative AI's input.

    Args:
        prompt: The question or task for Gemini.
        context: Background context or conversation history to provide.
        system_instruction: System-level instructions for how Gemini should respond.
        model: Gemini 3 model to use:
               - gemini-3-flash-preview: Fast, pro-grade reasoning (default)
               - gemini-3-pro-preview: Most capable for complex tasks
        temperature: Response creativity (0.0-1.0). Lower = more focused.
        max_tokens: Maximum response length.
        thinking_level: Reasoning depth (minimal, low, medium, high).
                       Higher = better quality but slower.
        stream: Whether to use streaming for faster first response.

    Returns:
        Dict with model_used, response text, and optional usage stats.

    Example:
        Ask Gemini to review code:
        prompt="Review this Python function for bugs"
        context="def add(a, b): return a + b"
        system_instruction="You are a senior Python developer"
        thinking_level="high"
    """
    try:
        client = get_gemini_client()
        result = await client.generate_text(
            prompt=prompt,
            context=context,
            system_instruction=system_instruction,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_level=thinking_level,
            stream=stream,
        )
        logger.info(f"ask_gemini completed with model {result['model_used']}")
        return result

    except Exception as e:
        logger.error(f"ask_gemini failed: {e}")
        return {
            "error": str(e),
            "model_used": model,
            "response": None,
        }


@mcp.tool()
async def chat_gemini(
    message: str,
    chat_id: str = "default",
    model: str = "gemini-3-flash-preview",
    system_instruction: str = "",
) -> dict:
    """Continue a multi-turn conversation with Gemini 3.

    Chat sessions maintain history, allowing for follow-up questions
    and context-aware responses across multiple messages.

    Args:
        message: The message to send to Gemini.
        chat_id: Unique identifier for the chat session. Use the same ID
                 to continue a conversation, or a new ID to start fresh.
        model: Gemini 3 model to use (gemini-3-flash-preview, gemini-3-pro-preview).
        system_instruction: System instructions (only used for new sessions).

    Returns:
        Dict with response, chat_id, history length, and recent messages.

    Example:
        Start a code review session:
        message="I need help reviewing my authentication module"
        chat_id="auth-review-session"
        system_instruction="You are a security expert"

        Continue the conversation:
        message="What about the password hashing?"
        chat_id="auth-review-session"
    """
    try:
        client = get_gemini_client()
        result = await client.chat(
            message=message,
            chat_id=chat_id,
            model=model,
            system_instruction=system_instruction,
        )
        logger.info(f"chat_gemini completed, session {chat_id}, history: {result['history_length']}")
        return result

    except Exception as e:
        logger.error(f"chat_gemini failed: {e}")
        return {
            "error": str(e),
            "chat_id": chat_id,
            "response": None,
        }


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
    """Generate an image using Gemini or Imagen models.

    Creates high-fidelity images from text descriptions. Supports both
    Gemini 3 Pro Image and Imagen 4 family models.

    Args:
        prompt: Text description of the image to generate. Be specific
                and descriptive for best results.
        model: Image model to use:
               - gemini-3-pro-image-preview: High-fidelity with reasoning (4096px)
               - imagen-4.0-ultra-generate-001: Highest quality ($0.06/image)
               - imagen-4.0-generate-001: Standard quality ($0.04/image)
               - imagen-4.0-fast-generate-001: Fast generation ($0.02/image)
        aspect_ratio: Image dimensions ratio (1:1, 16:9, 9:16, 4:3, 3:4).
        output_format: How to return the image:
                      - "base64": Return as base64 string (default)
                      - "file": Save to disk only
                      - "both": Return base64 AND save to disk
        output_dir: Directory to save files when using "file" or "both".
        number_of_images: Number of images to generate (1-4, Imagen 4 only).
        output_resolution: Output resolution "1K" or "2K" (Imagen 4 only).

    Returns:
        Dict with base64 data and/or file_path, plus model info.
        For multiple images, returns "images" list with each image's data.

    Example:
        Generate with Gemini:
        prompt="A minimalist tech startup logo with geometric shapes"
        model="gemini-3-pro-image-preview"

        Generate with Imagen 4 Ultra:
        prompt="Photorealistic mountain landscape at sunset"
        model="imagen-4.0-ultra-generate-001"
        number_of_images=4
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
async def generate_video(
    prompt: str,
    model: str = "veo-3.1-generate-001",
    output_gcs_uri: str = "",
    duration_seconds: int = 8,
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
    generate_audio: bool = True,
    number_of_videos: int = 1,
    auto_download: bool = True,
    output_dir: str = "./videos",
) -> dict:
    """Generate a video using Veo 3.1 models.

    Creates high-quality videos with native audio from text descriptions.
    Videos are saved to Google Cloud Storage and automatically downloaded locally.

    IMPORTANT: This is a long-running operation. Video generation takes
    1-10 minutes depending on duration and resolution.

    Args:
        prompt: Text description of the video to generate. Be specific
                about scenes, actions, camera movements, and mood.
        model: Veo model to use:
               - veo-3.1-generate-001: Highest quality (~$0.40/sec)
               - veo-3.1-fast-generate-001: Faster generation (~$0.15/sec)
        output_gcs_uri: GCS URI for output (e.g., "gs://my-bucket/videos/").
                       Optional. If not provided, auto-creates: {project-id}-gemini-videos
        duration_seconds: Video length (4, 6, or 8 seconds). Default: 8.
        aspect_ratio: "16:9" (landscape) or "9:16" (portrait). Default: "16:9".
        resolution: "720p" or "1080p". Default: "720p".
        generate_audio: Generate synchronized audio (dialogue, music, SFX). Default: True.
        number_of_videos: Number of video variations (1-4). Default: 1.
        auto_download: Automatically download videos to local directory. Default: True.
        output_dir: Local directory for downloaded videos. Default: "./videos".

    Returns:
        Dict with video_uris (GCS paths), local_paths (if auto_download), and generation info.

    Example:
        Generate a cinematic video (auto-downloaded to ./videos):
        prompt="A golden retriever running through a sunlit meadow, slow motion, cinematic"
        model="veo-3.1-generate-001"
        duration_seconds=8
        resolution="1080p"

    Note:
        GCS bucket is automatically created if not specified.
        Videos are automatically downloaded to output_dir when auto_download=True.
    """
    try:
        client = get_gemini_client()
        result = await client.generate_video(
            prompt=prompt,
            model=model,
            output_gcs_uri=output_gcs_uri if output_gcs_uri else None,
            duration_seconds=duration_seconds,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            generate_audio=generate_audio,
            number_of_videos=number_of_videos,
            auto_download=auto_download,
            output_dir=output_dir,
        )
        logger.info(f"generate_video completed with model {result['model_used']}")
        return result

    except Exception as e:
        logger.error(f"generate_video failed: {e}")
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
) -> dict:
    """Design a frontend UI component using Gemini 3 Pro.

    This tool generates high-quality, production-ready HTML components with
    TailwindCSS. Always uses gemini-3-pro-preview for best design quality.
    Perfect for creating UI components that Claude Code can then integrate
    into a larger application.

    IMPORTANT: Content language defaults to Turkish (tr). Use content_language
    parameter to generate content in other languages (en, de).

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
        dark_mode: Include dark: variants for dark mode support (default: True)
        border_radius: Custom border radius override (e.g., "rounded-xl")
        responsive_breakpoints: Comma-separated breakpoints (default: "sm,md,lg")
        accessibility_level: WCAG level - "AA" or "AAA" (default: "AA")
        micro_interactions: Include hover/focus animations (default: True)
        max_width: Maximum width constraint (e.g., "1280px", "max-w-7xl")
        project_context: Project-specific context for design consistency. Example:
                        "Project: InfoSYS - Enterprise ERP for Turkish businesses.
                         Target: Corporate users. Tone: Professional, trustworthy.
                         Industry: Business Software. Colors: Blue primary."

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
        - model_used: Always gemini-3-pro-preview

    Examples:
        # Button (Atom)
        design_frontend(
            component_type="button",
            context="Primary CTA for newsletter signup",
            content_structure='{"text": "Subscribe", "icon": "mail"}',
            theme="modern-minimal"
        )

        # Pricing Card (Molecule)
        design_frontend(
            component_type="pricing_card",
            context="SaaS pricing tier card",
            content_structure='{"tier": "Pro", "price": "$29/mo", "features": ["Unlimited users", "Priority support"], "cta": "Get Started"}',
            theme="modern-minimal"
        )

        # Navbar (Organism)
        design_frontend(
            component_type="navbar",
            context="Main navigation for documentation site",
            content_structure='{"logo": {"text": "DocsAI"}, "navigation": [{"label": "Docs", "href": "/docs"}], "actions": [{"type": "search"}, {"type": "theme-toggle"}]}',
            max_width="1280px"
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

        # Build style guide from theme
        style_guide = build_style_guide(
            theme=theme,
            dark_mode=dark_mode,
            border_radius=border_radius,
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

        logger.info(f"design_frontend completed: {component_type} -> {result.get('component_id', 'unknown')}")
        return result

    except Exception as e:
        logger.error(f"design_frontend failed: {e}")
        return {
            "error": str(e),
            "component_type": component_type,
            "model_used": "gemini-3-pro-preview",
        }


@mcp.tool()
def list_frontend_options() -> dict:
    """List available frontend design options.

    Returns all available component types, themes, templates, and section types
    for the design tools.

    Returns:
        Dict containing:
        - components: List of available component types (atoms, molecules, organisms)
        - themes: List of available theme presets with descriptions
        - templates: List of available page templates
        - sections: List of available section types for design_section
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

    return {
        "components": get_available_components(),
        "themes": themes_with_details,
        "templates": templates_with_details,
        "sections": sections_with_details,
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
        "note": "Use design_frontend() for components, design_page() for full pages, design_section() for chain-based large pages, refine_frontend() for iterations. MAXIMUM_RICHNESS mode is enabled by default.",
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
    """List available Gemini models and their capabilities.

    Returns information about text, image, and video generation models
    available on Vertex AI.

    Returns:
        Dict containing lists of text, image, and video models with their specs.
    """
    return {
        "text_models": AVAILABLE_MODELS["text"],
        "image_models": AVAILABLE_MODELS["image"],
        "video_models": AVAILABLE_MODELS.get("video", []),
        "default_text_model": get_config().default_model if _config_valid() else "gemini-3-flash-preview",
        "default_image_model": get_config().default_image_model if _config_valid() else "gemini-3-pro-image-preview",
        "default_video_model": "veo-3.1-generate-001",
    }


@mcp.tool()
def clear_chat_session(chat_id: str) -> dict:
    """Clear a chat session and its history.

    Use this to start fresh with a new conversation context.

    Args:
        chat_id: The chat session ID to clear.

    Returns:
        Dict indicating success or failure.
    """
    try:
        client = get_gemini_client()
        cleared = client.clear_chat(chat_id)
        return {
            "success": cleared,
            "chat_id": chat_id,
            "message": f"Chat session '{chat_id}' cleared" if cleared else f"Chat session '{chat_id}' not found",
        }
    except Exception as e:
        return {
            "success": False,
            "chat_id": chat_id,
            "error": str(e),
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
            project_context=f"This is part of an existing page. Maintain visual consistency.",
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
