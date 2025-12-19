"""Pydantic schemas for Gemini MCP response validation.

This module provides type-safe validation for all design tool responses.
Uses Pydantic v2 for modern validation features.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# =============================================================================
# Design Tokens Schema
# =============================================================================

class ColorTokens(BaseModel):
    """Color palette extracted from design or reference image."""

    primary: str = Field(default="#3B82F6", description="Primary brand color")
    secondary: str = Field(default="#6B7280", description="Secondary color")
    accent: str = Field(default="#10B981", description="Accent/highlight color")
    background: str = Field(default="#FFFFFF", description="Background color")
    surface: str = Field(default="#F9FAFB", description="Surface/card color")
    text_primary: str = Field(default="#111827", description="Primary text color")
    text_secondary: str = Field(default="#6B7280", description="Secondary text color")
    border: str = Field(default="#E5E7EB", description="Border color")

    @field_validator("*", mode="before")
    @classmethod
    def validate_hex_color(cls, v: Any) -> str:
        """Validate hex color format."""
        if not isinstance(v, str):
            return "#000000"
        # Accept various formats
        v = v.strip()
        if not v.startswith("#"):
            v = f"#{v}"
        # Validate hex format
        if re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", v):
            return v.upper()
        return "#000000"


class TypographyTokens(BaseModel):
    """Typography settings extracted from design."""

    heading_size: str = Field(default="text-4xl", description="Heading size class")
    body_size: str = Field(default="text-base", description="Body text size class")
    font_weight_heading: str = Field(default="font-bold", description="Heading weight")
    font_weight_body: str = Field(default="font-normal", description="Body weight")
    line_height: str = Field(default="leading-relaxed", description="Line height class")


class SpacingTokens(BaseModel):
    """Spacing patterns extracted from design."""

    section_padding: str = Field(default="py-20", description="Section padding")
    element_gap: str = Field(default="gap-8", description="Gap between elements")
    container_padding: str = Field(default="px-6", description="Container padding")


class BorderTokens(BaseModel):
    """Border styles extracted from design."""

    radius: str = Field(default="rounded-xl", description="Border radius class")
    width: str = Field(default="border", description="Border width class")
    style: str = Field(default="solid", description="Border style")


class ShadowTokens(BaseModel):
    """Shadow styles extracted from design."""

    card: str = Field(default="shadow-lg", description="Card shadow")
    button: str = Field(default="shadow-md", description="Button shadow")
    hover: str = Field(default="hover:shadow-xl", description="Hover shadow")


class LayoutTokens(BaseModel):
    """Layout patterns extracted from design."""

    max_width: str = Field(default="max-w-7xl", description="Max width class")
    grid_cols: str = Field(default="grid-cols-3", description="Grid columns")
    flex_direction: str = Field(default="flex-row", description="Flex direction")


class DesignTokens(BaseModel):
    """Complete design tokens extracted from a design or reference image."""

    colors: ColorTokens = Field(default_factory=ColorTokens)
    typography: TypographyTokens = Field(default_factory=TypographyTokens)
    spacing: SpacingTokens = Field(default_factory=SpacingTokens)
    borders: BorderTokens = Field(default_factory=BorderTokens)
    shadows: ShadowTokens = Field(default_factory=ShadowTokens)
    layout: LayoutTokens = Field(default_factory=LayoutTokens)


# =============================================================================
# Design Response Schemas
# =============================================================================

class DesignResponse(BaseModel):
    """Response from design_frontend, design_section, design_page tools."""

    component_id: str = Field(..., min_length=1, description="Unique component ID")
    atomic_level: Literal["atom", "molecule", "organism", "page", "section"] = Field(
        default="molecule",
        description="Atomic design level"
    )
    html: str = Field(..., min_length=50, description="Generated HTML with TailwindCSS")
    tailwind_classes_used: List[str] = Field(
        default_factory=list,
        description="List of Tailwind classes used"
    )
    accessibility_features: List[str] = Field(
        default_factory=list,
        description="Accessibility features implemented"
    )
    responsive_breakpoints: List[str] = Field(
        default_factory=lambda: ["sm", "md", "lg"],
        description="Responsive breakpoints used"
    )
    dark_mode_support: bool = Field(default=True, description="Dark mode support")
    micro_interactions: List[str] = Field(
        default_factory=list,
        description="Animation/transition classes"
    )
    design_notes: str = Field(default="", description="Design decision notes")
    model_used: str = Field(default="gemini-3-pro-preview", description="Model used")

    # Optional fields
    design_tokens: Optional[DesignTokens] = Field(
        default=None,
        description="Extracted design tokens (for chain mode)"
    )
    section_type: Optional[str] = Field(
        default=None,
        description="Section type (for design_section)"
    )
    template_type: Optional[str] = Field(
        default=None,
        description="Template type (for design_page)"
    )
    sections: Optional[List[str]] = Field(
        default=None,
        description="Sections included (for design_page)"
    )
    js_fixes_applied: Optional[List[str]] = Field(
        default=None,
        description="JavaScript fixes applied"
    )

    @field_validator("html")
    @classmethod
    def validate_html(cls, v: str) -> str:
        """Validate HTML content."""
        # Check for inline scripts (security)
        if "<script" in v.lower() and "onclick" not in v.lower():
            # Allow inline event handlers but not script tags
            if re.search(r"<script[^>]*>", v, re.IGNORECASE):
                raise ValueError("Inline <script> tags not allowed for security")
        return v

    @field_validator("tailwind_classes_used", mode="before")
    @classmethod
    def parse_tailwind_classes(cls, v: Any) -> List[str]:
        """Parse Tailwind classes from string or list."""
        if isinstance(v, str):
            return [c.strip() for c in v.split(",") if c.strip()]
        if isinstance(v, list):
            return [str(c) for c in v]
        return []


class SectionDesignResponse(DesignResponse):
    """Response specifically from design_section tool."""

    section_type: str = Field(..., description="Type of section designed")
    design_tokens: DesignTokens = Field(
        default_factory=DesignTokens,
        description="Extracted design tokens for chain mode"
    )


class PageDesignResponse(DesignResponse):
    """Response specifically from design_page tool."""

    template_type: str = Field(..., description="Template type used")
    sections: List[str] = Field(default_factory=list, description="Sections included")


# =============================================================================
# Vision Analysis Response
# =============================================================================

class VisionAnalysisResponse(BaseModel):
    """Response from analyze_reference_image and design_from_reference."""

    design_tokens: DesignTokens = Field(
        default_factory=DesignTokens,
        description="Extracted design tokens"
    )
    aesthetic: str = Field(
        default="modern-minimal",
        description="Overall design aesthetic"
    )
    component_hints: List[str] = Field(
        default_factory=list,
        description="Detected UI component types"
    )
    mood: str = Field(default="professional", description="Design mood")
    special_effects: List[str] = Field(
        default_factory=list,
        description="Special effects detected"
    )
    design_description: Optional[str] = Field(
        default=None,
        description="Brief design description"
    )
    model_used: str = Field(default="gemini-3-pro-preview", description="Model used")


class ReferenceDesignResponse(VisionAnalysisResponse):
    """Response from design_from_reference with HTML generation."""

    extracted_tokens: DesignTokens = Field(
        default_factory=DesignTokens,
        description="Tokens extracted from reference"
    )
    html: str = Field(..., min_length=50, description="Generated HTML")
    design_notes: str = Field(default="", description="Design interpretation notes")
    modifications: str = Field(default="", description="Modifications applied")
    component_type: str = Field(default="", description="Component type designed")
    js_fixes_applied: Optional[List[str]] = Field(
        default=None,
        description="JavaScript fixes applied"
    )


# =============================================================================
# Refinement Response
# =============================================================================

class RefinementResponse(BaseModel):
    """Response from refine_frontend tool."""

    component_id: str = Field(..., min_length=1, description="Refined component ID")
    html: str = Field(..., min_length=50, description="Modified HTML")
    changes_made: List[str] = Field(
        default_factory=list,
        description="Summary of changes applied"
    )
    design_notes: str = Field(default="", description="Modification notes")
    model_used: str = Field(default="gemini-3-pro-preview", description="Model used")
    js_fixes_applied: Optional[List[str]] = Field(
        default=None,
        description="JavaScript fixes applied"
    )


# =============================================================================
# Design System State
# =============================================================================

class DesignSystemComponent(BaseModel):
    """A component registered in the design system."""

    component_id: str = Field(..., description="Unique component ID")
    component_type: str = Field(..., description="Type of component")
    atomic_level: str = Field(..., description="Atomic design level")
    html: str = Field(..., description="Component HTML")
    created_at: datetime = Field(default_factory=datetime.now)


class DesignSystemState(BaseModel):
    """State management for design system consistency.

    Tracks components designed within a project to ensure visual consistency.
    The design tokens from the first component become the baseline for all
    subsequent components in the same design system.
    """

    id: str = Field(..., min_length=1, description="Design system ID")
    name: str = Field(default="", description="Design system name")
    theme: str = Field(default="modern-minimal", description="Base theme")
    design_tokens: DesignTokens = Field(
        default_factory=DesignTokens,
        description="Baseline design tokens"
    )
    components: List[DesignSystemComponent] = Field(
        default_factory=list,
        description="Registered components"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def get_context(self) -> str:
        """Generate context string for Gemini prompts.

        This context ensures visual consistency across components.
        """
        if not self.components:
            return ""

        context_parts = [
            f"## Design System: {self.name or self.id}",
            f"Theme: {self.theme}",
            "",
            "### Baseline Design Tokens:",
            f"Colors: {self.design_tokens.colors.model_dump_json()}",
            f"Typography: {self.design_tokens.typography.model_dump_json()}",
            f"Spacing: {self.design_tokens.spacing.model_dump_json()}",
            "",
            f"### Existing Components ({len(self.components)}):",
        ]

        for comp in self.components[-5:]:  # Last 5 components
            context_parts.append(f"- {comp.component_type} ({comp.atomic_level})")

        context_parts.extend([
            "",
            "IMPORTANT: Match these design tokens for visual consistency.",
        ])

        return "\n".join(context_parts)

    def register_component(
        self,
        component_id: str,
        component_type: str,
        atomic_level: str,
        html: str,
        design_tokens: Optional[DesignTokens] = None,
    ) -> None:
        """Register a new component in the design system.

        If this is the first component, its tokens become the baseline.
        """
        # Update baseline tokens from first component
        if not self.components and design_tokens:
            self.design_tokens = design_tokens

        self.components.append(
            DesignSystemComponent(
                component_id=component_id,
                component_type=component_type,
                atomic_level=atomic_level,
                html=html,
            )
        )
        self.updated_at = datetime.now()


# =============================================================================
# Multi-Language Support
# =============================================================================

class LanguageConfig(BaseModel):
    """Language configuration for content generation."""

    code: str = Field(..., description="Language code (tr, en, de, etc.)")
    name: str = Field(..., description="Language name")
    cta_primary: List[str] = Field(
        default_factory=list,
        description="Primary CTA text options"
    )
    cta_secondary: List[str] = Field(
        default_factory=list,
        description="Secondary CTA text options"
    )
    navigation: List[str] = Field(
        default_factory=list,
        description="Navigation item labels"
    )
    form_labels: Dict[str, str] = Field(
        default_factory=dict,
        description="Form field labels"
    )
    validation_messages: Dict[str, str] = Field(
        default_factory=dict,
        description="Form validation messages"
    )
    common_phrases: Dict[str, str] = Field(
        default_factory=dict,
        description="Common UI phrases"
    )


# Pre-defined language configurations
LANGUAGE_CONFIGS: Dict[str, LanguageConfig] = {
    "tr": LanguageConfig(
        code="tr",
        name="Turkce",
        cta_primary=["Hemen Basla", "Ucretsiz Dene", "Satin Al", "Kayit Ol", "Iletisime Gec"],
        cta_secondary=["Daha Fazla", "Incele", "Detaylar", "Oku", "Kesfet"],
        navigation=["Ana Sayfa", "Hakkimizda", "Hizmetler", "Urunler", "Blog", "Iletisim"],
        form_labels={
            "name": "Ad Soyad",
            "email": "E-posta",
            "phone": "Telefon",
            "message": "Mesaj",
            "company": "Sirket",
            "password": "Sifre",
            "confirm_password": "Sifre Tekrar",
        },
        validation_messages={
            "required": "Bu alan zorunludur",
            "email": "Gecerli bir e-posta adresi girin",
            "phone": "Gecerli bir telefon numarasi girin",
            "min_length": "En az {min} karakter olmali",
            "max_length": "En fazla {max} karakter olmali",
        },
        common_phrases={
            "loading": "Yukleniyor...",
            "success": "Basarili!",
            "error": "Bir hata olustu",
            "submit": "Gonder",
            "cancel": "Iptal",
            "save": "Kaydet",
            "delete": "Sil",
            "edit": "Duzenle",
            "search": "Ara",
            "filter": "Filtrele",
            "sort": "Sirala",
            "close": "Kapat",
            "back": "Geri",
            "next": "Ileri",
            "previous": "Onceki",
        },
    ),
    "en": LanguageConfig(
        code="en",
        name="English",
        cta_primary=["Get Started", "Try Free", "Buy Now", "Sign Up", "Contact Us"],
        cta_secondary=["Learn More", "Explore", "Details", "Read", "Discover"],
        navigation=["Home", "About", "Services", "Products", "Blog", "Contact"],
        form_labels={
            "name": "Full Name",
            "email": "Email",
            "phone": "Phone",
            "message": "Message",
            "company": "Company",
            "password": "Password",
            "confirm_password": "Confirm Password",
        },
        validation_messages={
            "required": "This field is required",
            "email": "Please enter a valid email address",
            "phone": "Please enter a valid phone number",
            "min_length": "Must be at least {min} characters",
            "max_length": "Must be at most {max} characters",
        },
        common_phrases={
            "loading": "Loading...",
            "success": "Success!",
            "error": "An error occurred",
            "submit": "Submit",
            "cancel": "Cancel",
            "save": "Save",
            "delete": "Delete",
            "edit": "Edit",
            "search": "Search",
            "filter": "Filter",
            "sort": "Sort",
            "close": "Close",
            "back": "Back",
            "next": "Next",
            "previous": "Previous",
        },
    ),
    "de": LanguageConfig(
        code="de",
        name="Deutsch",
        cta_primary=["Jetzt starten", "Kostenlos testen", "Jetzt kaufen", "Registrieren", "Kontakt"],
        cta_secondary=["Mehr erfahren", "Entdecken", "Details", "Lesen", "Erkunden"],
        navigation=["Startseite", "Uber uns", "Dienstleistungen", "Produkte", "Blog", "Kontakt"],
        form_labels={
            "name": "Vollstandiger Name",
            "email": "E-Mail",
            "phone": "Telefon",
            "message": "Nachricht",
            "company": "Unternehmen",
            "password": "Passwort",
            "confirm_password": "Passwort bestatigen",
        },
        validation_messages={
            "required": "Dieses Feld ist erforderlich",
            "email": "Bitte geben Sie eine gultige E-Mail-Adresse ein",
            "phone": "Bitte geben Sie eine gultige Telefonnummer ein",
            "min_length": "Muss mindestens {min} Zeichen lang sein",
            "max_length": "Darf hochstens {max} Zeichen lang sein",
        },
        common_phrases={
            "loading": "Wird geladen...",
            "success": "Erfolgreich!",
            "error": "Ein Fehler ist aufgetreten",
            "submit": "Absenden",
            "cancel": "Abbrechen",
            "save": "Speichern",
            "delete": "Loschen",
            "edit": "Bearbeiten",
            "search": "Suchen",
            "filter": "Filtern",
            "sort": "Sortieren",
            "close": "Schliesen",
            "back": "Zuruck",
            "next": "Weiter",
            "previous": "Vorherige",
        },
    ),
}


def get_language_config(code: str) -> LanguageConfig:
    """Get language configuration by code.

    Falls back to Turkish if language not found.
    """
    return LANGUAGE_CONFIGS.get(code, LANGUAGE_CONFIGS["tr"])


def get_available_languages() -> List[str]:
    """Get list of available language codes."""
    return list(LANGUAGE_CONFIGS.keys())


# =============================================================================
# Validation Helpers
# =============================================================================

def validate_design_response(response: Dict[str, Any]) -> tuple[bool, Optional[DesignResponse], Optional[str]]:
    """Validate a design response dictionary.

    Returns:
        Tuple of (is_valid, validated_response, error_message)
    """
    try:
        validated = DesignResponse(**response)
        return True, validated, None
    except Exception as e:
        return False, None, str(e)


def validate_vision_response(response: Dict[str, Any]) -> tuple[bool, Optional[VisionAnalysisResponse], Optional[str]]:
    """Validate a vision analysis response dictionary.

    Returns:
        Tuple of (is_valid, validated_response, error_message)
    """
    try:
        validated = VisionAnalysisResponse(**response)
        return True, validated, None
    except Exception as e:
        return False, None, str(e)


def validate_design_tokens(tokens: Dict[str, Any]) -> tuple[bool, Optional[DesignTokens], Optional[str]]:
    """Validate design tokens dictionary.

    Returns:
        Tuple of (is_valid, validated_tokens, error_message)
    """
    try:
        validated = DesignTokens(**tokens)
        return True, validated, None
    except Exception as e:
        return False, None, str(e)
