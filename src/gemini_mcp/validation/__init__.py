"""
Validation Module - Cross-Layer Validation for Trifecta Engine

This module provides validators that ensure consistency across
HTML, CSS, and JavaScript outputs from the Trifecta agents.

Key Validators:
- HTMLValidator: Validates HTML structure and accessibility
- CSSValidator: Validates CSS syntax and best practices
- JSValidator: Validates JavaScript safety and performance
- IDValidator: Cross-layer validation (HTML IDs vs JS selectors)
- ProfessionalValidator: Validates against corporate/professional standards
"""

from gemini_mcp.validation.html_validator import HTMLValidator
from gemini_mcp.validation.css_validator import CSSValidator
from gemini_mcp.validation.js_validator import JSValidator
from gemini_mcp.validation.id_validator import IDValidator
from gemini_mcp.validation.professional_validator import (
    ProfessionalValidator,
    ProfessionalValidationResult,
    ProfessionalDimensionScore,
    validate_professional,
    get_formality_rules,
    get_industry_patterns,
    FORMALITY_RULES,
    INDUSTRY_PATTERNS,
)
from gemini_mcp.validation.density_validator import (
    DensityValidator,
    DensityValidationResult,
    ElementDensity,
    validate_density,
)
from gemini_mcp.validation.contrast_checker import (
    ContrastResult,
    ContrastIssue,
    ContrastReport,
    calculate_contrast_ratio,
    check_contrast,
    check_wcag_compliance,
    validate_contrast,
    suggest_accessible_pair,
    tailwind_to_hex,
    TAILWIND_COLORS,
)
from gemini_mcp.validation.animation_validator import (
    AnimationValidator,
    AnimationValidationResult,
    AnimationIssue,
    AnimationSeverity,
    validate_animation_timing,
)

__all__ = [
    "HTMLValidator",
    "CSSValidator",
    "JSValidator",
    "IDValidator",
    # Professional Validator
    "ProfessionalValidator",
    "ProfessionalValidationResult",
    "ProfessionalDimensionScore",
    "validate_professional",
    "get_formality_rules",
    "get_industry_patterns",
    "FORMALITY_RULES",
    "INDUSTRY_PATTERNS",
    # Density Validator (Anti-Laziness)
    "DensityValidator",
    "DensityValidationResult",
    "ElementDensity",
    "validate_density",
    # Contrast Checker (WCAG Compliance)
    "ContrastResult",
    "ContrastIssue",
    "ContrastReport",
    "calculate_contrast_ratio",
    "check_contrast",
    "check_wcag_compliance",
    "validate_contrast",
    "suggest_accessible_pair",
    "tailwind_to_hex",
    "TAILWIND_COLORS",
    # Animation Validator (UX Enhancement)
    "AnimationValidator",
    "AnimationValidationResult",
    "AnimationIssue",
    "AnimationSeverity",
    "validate_animation_timing",
]
