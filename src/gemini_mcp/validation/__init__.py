"""
Validation Module - Cross-Layer Validation for Trifecta Engine

This module provides validators that ensure consistency across
HTML, CSS, and JavaScript outputs from the Trifecta agents.

Key Validators:
- HTMLValidator: Validates HTML structure and accessibility
- CSSValidator: Validates CSS syntax and best practices
- JSValidator: Validates JavaScript safety and performance
- IDValidator: Cross-layer validation (HTML IDs vs JS selectors)
"""

from gemini_mcp.validation.html_validator import HTMLValidator
from gemini_mcp.validation.css_validator import CSSValidator
from gemini_mcp.validation.js_validator import JSValidator
from gemini_mcp.validation.id_validator import IDValidator

__all__ = [
    "HTMLValidator",
    "CSSValidator",
    "JSValidator",
    "IDValidator",
]
