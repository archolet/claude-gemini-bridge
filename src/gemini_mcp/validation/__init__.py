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
- AntiPatternValidator: Enterprise anti-pattern detection with auto-fix

Shared Types:
- ValidationSeverity: ERROR, WARNING, INFO
- ValidationIssue: Single validation issue
- ValidationResult: Collection of issues with validity status
"""

# Shared types (import first to avoid circular imports)
from gemini_mcp.validation.types import (
    ValidationSeverity,
    ValidationIssue,
    ValidationResult,
    AnimationSeverity,  # Backward compat alias
)

# Shared utilities
from gemini_mcp.validation.utils import (
    hex_to_rgb,
    rgb_to_hex,
    hex_to_hsl,
    hsl_to_hex,
    relative_luminance,
    contrast_ratio as utils_contrast_ratio,  # Avoid name collision
    extract_classes_from_html,
    extract_tailwind_colors,
    extract_color_pairs,
)

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
from gemini_mcp.validation.anti_pattern_validator import (
    AntiPatternValidator,
    AntiPatternCategory,
    AntiPattern,
    validate_antipatterns,
    fix_antipatterns,
    get_antipattern_report,
    ALL_ANTIPATTERNS,
    ACCESSIBILITY_ANTIPATTERNS,
    PERFORMANCE_ANTIPATTERNS,
    STYLING_ANTIPATTERNS,
    ALPINE_ANTIPATTERNS,
)

__all__ = [
    # Shared Types
    "ValidationSeverity",
    "ValidationIssue",
    "ValidationResult",
    # Core Validators
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
    # Anti-Pattern Validator (Enterprise)
    "AntiPatternValidator",
    "AntiPatternCategory",
    "AntiPattern",
    "validate_antipatterns",
    "fix_antipatterns",
    "get_antipattern_report",
    "ALL_ANTIPATTERNS",
    "ACCESSIBILITY_ANTIPATTERNS",
    "PERFORMANCE_ANTIPATTERNS",
    "STYLING_ANTIPATTERNS",
    "ALPINE_ANTIPATTERNS",
]
