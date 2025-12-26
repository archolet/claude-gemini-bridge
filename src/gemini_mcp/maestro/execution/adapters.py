"""
Parameter adapters for transforming MaestroDecision parameters
to format expected by GeminiClient methods.

Each adapter function takes raw decision parameters and session context,
returning a dict ready for the corresponding GeminiClient method.
"""
from __future__ import annotations

import json
from typing import Any

from gemini_mcp.maestro.models import ContextData


def adapt_for_design_frontend(
    params: dict[str, Any],
    context: ContextData,
) -> dict[str, Any]:
    """
    Adapt parameters for client.design_component().

    Args:
        params: Raw parameters from MaestroDecision
        context: Session context with previous_html, project_context

    Returns:
        Dict ready for design_component() call
    """
    return {
        "component_type": params.get("component_type", "card"),
        "design_spec": {
            "context": params.get("context", ""),
            "content_structure": _ensure_dict(params.get("content_structure", {})),
        },
        "style_guide": None,  # Will be built by caller from theme
        "project_context": params.get("project_context", context.project_context or ""),
        "content_language": params.get("content_language", "tr"),
    }


def adapt_for_design_page(
    params: dict[str, Any],
    context: ContextData,
) -> dict[str, Any]:
    """
    Adapt parameters for client.design_component() in page mode.

    Page mode uses "page:{template_type}" as component_type.

    Args:
        params: Raw parameters from MaestroDecision
        context: Session context

    Returns:
        Dict ready for design_component() call
    """
    template = params.get("template_type", "landing_page")
    return {
        "component_type": f"page:{template}",
        "design_spec": {
            "context": params.get("context", ""),
            "content_structure": _ensure_dict(params.get("content_structure", {})),
        },
        "style_guide": None,
        "project_context": params.get("project_context", context.project_context or ""),
        "content_language": params.get("content_language", "tr"),
    }


def adapt_for_design_section(
    params: dict[str, Any],
    context: ContextData,
) -> dict[str, Any]:
    """
    Adapt parameters for client.design_section().

    Args:
        params: Raw parameters from MaestroDecision
        context: Session context

    Returns:
        Dict ready for design_section() call
    """
    return {
        "section_type": params.get("section_type", "hero"),
        "context": params.get("context", ""),
        "previous_html": context.previous_html or params.get("previous_html", ""),
        "design_tokens": _ensure_dict(params.get("design_tokens", {})),
        "content_structure": _ensure_dict(params.get("content_structure", {})),
        "theme": params.get("theme", "modern-minimal"),
        "project_context": params.get("project_context", context.project_context or ""),
        "content_language": params.get("content_language", "tr"),
    }


def adapt_for_refine_frontend(
    params: dict[str, Any],
    context: ContextData,
) -> dict[str, Any]:
    """
    Adapt parameters for client.refine_component().

    CRITICAL: previous_html must come from session context.

    Args:
        params: Raw parameters from MaestroDecision
        context: Session context with previous_html

    Returns:
        Dict ready for refine_component() call

    Raises:
        ValueError: If previous_html is not available in context
    """
    previous_html = context.previous_html
    if not previous_html:
        raise ValueError(
            "refine_frontend requires previous_html in session context. "
            "Start session with existing_html parameter."
        )

    return {
        "previous_html": previous_html,
        "modifications": params.get("modifications", ""),
        "project_context": params.get("project_context", context.project_context or ""),
    }


def adapt_for_replace_section(
    params: dict[str, Any],
    context: ContextData,
) -> dict[str, Any]:
    """
    Adapt parameters for replace_section_in_page mode.

    CRITICAL: page_html must come from session context.

    Args:
        params: Raw parameters from MaestroDecision
        context: Session context with page HTML

    Returns:
        Dict ready for section replacement

    Raises:
        ValueError: If page HTML is not available in context
    """
    page_html = context.previous_html
    if not page_html:
        raise ValueError(
            "replace_section_in_page requires page_html in session context. "
            "Start session with existing_html parameter containing the full page."
        )

    return {
        "page_html": page_html,
        "section_type": params.get("section_type", "hero"),
        "modifications": params.get("modifications", ""),
        "preserve_design_tokens": params.get("preserve_design_tokens", True),
        "theme": params.get("theme", "modern-minimal"),
        "content_language": params.get("content_language", "tr"),
    }


def adapt_for_design_from_reference(
    params: dict[str, Any],
    context: ContextData,
) -> dict[str, Any]:
    """
    Adapt parameters for client.design_from_reference().

    CRITICAL: image_path is required.

    Args:
        params: Raw parameters from MaestroDecision
        context: Session context

    Returns:
        Dict ready for design_from_reference() call

    Raises:
        ValueError: If image_path is not provided
    """
    image_path = params.get("image_path")
    if not image_path:
        raise ValueError(
            "design_from_reference requires image_path parameter. "
            "Provide the path to the reference image."
        )

    return {
        "image_path": image_path,
        "component_type": params.get("component_type", ""),
        "instructions": params.get("instructions", ""),
        "context": params.get("context", ""),
        "project_context": params.get("project_context", context.project_context or ""),
        "content_language": params.get("content_language", "tr"),
    }


def _ensure_dict(value: Any) -> dict:
    """
    Ensure value is a dict, parsing JSON string if needed.

    Args:
        value: Value that should be a dict

    Returns:
        Dict version of value, or empty dict if conversion fails
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    return {}
