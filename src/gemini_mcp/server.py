"""Gemini MCP Server - FastMCP implementation.

Provides tools for interacting with Gemini models on Vertex AI:
- ask_gemini: Text generation with context
- chat_gemini: Multi-turn conversations
- generate_image: Image generation
- design_frontend: Frontend component design with TailwindCSS
- list_models: Available models
"""

import asyncio
import json
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .client import get_gemini_client
from .config import AVAILABLE_MODELS, get_config
from .frontend_presets import (
    build_style_guide,
    get_available_components,
    get_available_themes,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
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
) -> dict:
    """Generate an image using Gemini 3 Pro Image model.

    Creates high-fidelity images from text descriptions with reasoning-enhanced
    composition. Supports multiple output formats and aspect ratios.

    Args:
        prompt: Text description of the image to generate. Be specific
                and descriptive for best results.
        model: Image model to use:
               - gemini-3-pro-image-preview: High-fidelity with reasoning (4096px)
        aspect_ratio: Image dimensions ratio (1:1, 16:9, 9:16, 4:3, 3:4).
        output_format: How to return the image:
                      - "base64": Return as base64 string (default)
                      - "file": Save to disk only
                      - "both": Return base64 AND save to disk
        output_dir: Directory to save files when using "file" or "both".

    Returns:
        Dict with base64 data and/or file_path, plus model info.

    Example:
        Generate a logo:
        prompt="A minimalist tech startup logo with geometric shapes, blue and white"
        model="gemini-3-pro-image-preview"
        output_format="both"
    """
    try:
        client = get_gemini_client()
        result = await client.generate_image(
            prompt=prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            output_format=output_format,
            output_dir=output_dir,
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
) -> dict:
    """Design a frontend UI component using Gemini 3 Pro.

    This tool generates high-quality, production-ready HTML components with
    TailwindCSS. Always uses gemini-3-pro-preview for best design quality.
    Perfect for creating UI components that Claude Code can then integrate
    into a larger application.

    Workflow:
    1. Claude analyzes the feature requirements
    2. Claude breaks down into atomic components (atoms, molecules, organisms)
    3. Claude calls design_frontend for each component with the same theme
    4. Gemini 3 Pro generates high-quality HTML with TailwindCSS
    5. Claude assembles the components into a complete page

    Args:
        component_type: Type of component to design. Options:
            Atoms: button, input, badge, avatar, icon, dropdown, toggle, tooltip
            Molecules: card, form, modal, tabs, table, accordion, alert, breadcrumb,
                      pagination, search_bar, stat_card, pricing_card
            Organisms: navbar, hero, sidebar, footer, data_table, login_form,
                      signup_form, contact_form, feature_section, testimonial_section,
                      pricing_table, dashboard_header
        context: Usage context explaining where/how the component will be used.
                Example: "Primary CTA button for newsletter signup on landing page"
        content_structure: JSON string with component content. Example:
                          '{"text": "Subscribe", "icon": "mail"}'
                          '{"tier": "Pro", "price": "$29/mo", "features": ["API access"]}'
        theme: Visual style preset. Options:
               - modern-minimal: Clean, professional (default)
               - brutalist: Bold, high-contrast, sharp edges
               - glassmorphism: Frosted glass, transparency
               - neo-brutalism: Playful with bold colors
               - soft-ui: Neumorphic, soft depth
               - corporate: Professional, trustworthy
        dark_mode: Include dark: variants for dark mode support (default: True)
        border_radius: Custom border radius override (e.g., "rounded-xl")
        responsive_breakpoints: Comma-separated breakpoints (default: "sm,md,lg")
        accessibility_level: WCAG level - "AA" or "AAA" (default: "AA")
        micro_interactions: Include hover/focus animations (default: True)
        max_width: Maximum width constraint (e.g., "1280px", "max-w-7xl")

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
        )

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

    Returns all available component types and themes for the design_frontend tool.

    Returns:
        Dict containing:
        - components: List of available component types (atoms, molecules, organisms)
        - themes: List of available theme presets with descriptions
    """
    return {
        "components": get_available_components(),
        "themes": get_available_themes(),
        "note": "Use design_frontend() with these options to generate components",
    }


@mcp.tool()
def list_models() -> dict:
    """List available Gemini models and their capabilities.

    Returns information about text generation and image generation models
    available on Vertex AI.

    Returns:
        Dict containing lists of text and image models with their specs.
    """
    return {
        "text_models": AVAILABLE_MODELS["text"],
        "image_models": AVAILABLE_MODELS["image"],
        "default_text_model": get_config().default_model if _config_valid() else "gemini-3-flash-preview",
        "default_image_model": get_config().default_image_model if _config_valid() else "gemini-3-pro-image-preview",
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


def _config_valid() -> bool:
    """Check if configuration is valid without raising errors."""
    try:
        get_config()
        return True
    except ValueError:
        return False


def main():
    """Entry point for the Gemini MCP server."""
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
