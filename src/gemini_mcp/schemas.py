"""Pydantic schemas for Gemini MCP response validation.

This module provides type-safe validation for all design tool responses.
Uses Pydantic v2 for modern validation features.

Includes Unified Design Token Schema for consistent token handling across all tools:
- Tailwind ↔ HEX color conversion
- px ↔ rem spacing normalization
- Role-based token classification (primary, secondary, accent, muted, background)
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator


# =============================================================================
# Tailwind ↔ HEX Color Mapping
# =============================================================================

# Core Tailwind color palette with HEX values
TAILWIND_COLOR_MAP: Dict[str, str] = {
    # Slate
    "slate-50": "#F8FAFC", "slate-100": "#F1F5F9", "slate-200": "#E2E8F0",
    "slate-300": "#CBD5E1", "slate-400": "#94A3B8", "slate-500": "#64748B",
    "slate-600": "#475569", "slate-700": "#334155", "slate-800": "#1E293B",
    "slate-900": "#0F172A", "slate-950": "#020617",
    # Gray
    "gray-50": "#F9FAFB", "gray-100": "#F3F4F6", "gray-200": "#E5E7EB",
    "gray-300": "#D1D5DB", "gray-400": "#9CA3AF", "gray-500": "#6B7280",
    "gray-600": "#4B5563", "gray-700": "#374151", "gray-800": "#1F2937",
    "gray-900": "#111827", "gray-950": "#030712",
    # Zinc
    "zinc-50": "#FAFAFA", "zinc-100": "#F4F4F5", "zinc-200": "#E4E4E7",
    "zinc-300": "#D4D4D8", "zinc-400": "#A1A1AA", "zinc-500": "#71717A",
    "zinc-600": "#52525B", "zinc-700": "#3F3F46", "zinc-800": "#27272A",
    "zinc-900": "#18181B", "zinc-950": "#09090B",
    # Red
    "red-50": "#FEF2F2", "red-100": "#FEE2E2", "red-200": "#FECACA",
    "red-300": "#FCA5A5", "red-400": "#F87171", "red-500": "#EF4444",
    "red-600": "#DC2626", "red-700": "#B91C1C", "red-800": "#991B1B",
    "red-900": "#7F1D1D", "red-950": "#450A0A",
    # Orange
    "orange-50": "#FFF7ED", "orange-100": "#FFEDD5", "orange-200": "#FED7AA",
    "orange-300": "#FDBA74", "orange-400": "#FB923C", "orange-500": "#F97316",
    "orange-600": "#EA580C", "orange-700": "#C2410C", "orange-800": "#9A3412",
    "orange-900": "#7C2D12", "orange-950": "#431407",
    # Amber
    "amber-50": "#FFFBEB", "amber-100": "#FEF3C7", "amber-200": "#FDE68A",
    "amber-300": "#FCD34D", "amber-400": "#FBBF24", "amber-500": "#F59E0B",
    "amber-600": "#D97706", "amber-700": "#B45309", "amber-800": "#92400E",
    "amber-900": "#78350F", "amber-950": "#451A03",
    # Yellow
    "yellow-50": "#FEFCE8", "yellow-100": "#FEF9C3", "yellow-200": "#FEF08A",
    "yellow-300": "#FDE047", "yellow-400": "#FACC15", "yellow-500": "#EAB308",
    "yellow-600": "#CA8A04", "yellow-700": "#A16207", "yellow-800": "#854D0E",
    "yellow-900": "#713F12", "yellow-950": "#422006",
    # Lime
    "lime-50": "#F7FEE7", "lime-100": "#ECFCCB", "lime-200": "#D9F99D",
    "lime-300": "#BEF264", "lime-400": "#A3E635", "lime-500": "#84CC16",
    "lime-600": "#65A30D", "lime-700": "#4D7C0F", "lime-800": "#3F6212",
    "lime-900": "#365314", "lime-950": "#1A2E05",
    # Green
    "green-50": "#F0FDF4", "green-100": "#DCFCE7", "green-200": "#BBF7D0",
    "green-300": "#86EFAC", "green-400": "#4ADE80", "green-500": "#22C55E",
    "green-600": "#16A34A", "green-700": "#15803D", "green-800": "#166534",
    "green-900": "#14532D", "green-950": "#052E16",
    # Emerald
    "emerald-50": "#ECFDF5", "emerald-100": "#D1FAE5", "emerald-200": "#A7F3D0",
    "emerald-300": "#6EE7B7", "emerald-400": "#34D399", "emerald-500": "#10B981",
    "emerald-600": "#059669", "emerald-700": "#047857", "emerald-800": "#065F46",
    "emerald-900": "#064E3B", "emerald-950": "#022C22",
    # Teal
    "teal-50": "#F0FDFA", "teal-100": "#CCFBF1", "teal-200": "#99F6E4",
    "teal-300": "#5EEAD4", "teal-400": "#2DD4BF", "teal-500": "#14B8A6",
    "teal-600": "#0D9488", "teal-700": "#0F766E", "teal-800": "#115E59",
    "teal-900": "#134E4A", "teal-950": "#042F2E",
    # Cyan
    "cyan-50": "#ECFEFF", "cyan-100": "#CFFAFE", "cyan-200": "#A5F3FC",
    "cyan-300": "#67E8F9", "cyan-400": "#22D3EE", "cyan-500": "#06B6D4",
    "cyan-600": "#0891B2", "cyan-700": "#0E7490", "cyan-800": "#155E75",
    "cyan-900": "#164E63", "cyan-950": "#083344",
    # Sky
    "sky-50": "#F0F9FF", "sky-100": "#E0F2FE", "sky-200": "#BAE6FD",
    "sky-300": "#7DD3FC", "sky-400": "#38BDF8", "sky-500": "#0EA5E9",
    "sky-600": "#0284C7", "sky-700": "#0369A1", "sky-800": "#075985",
    "sky-900": "#0C4A6E", "sky-950": "#082F49",
    # Blue
    "blue-50": "#EFF6FF", "blue-100": "#DBEAFE", "blue-200": "#BFDBFE",
    "blue-300": "#93C5FD", "blue-400": "#60A5FA", "blue-500": "#3B82F6",
    "blue-600": "#2563EB", "blue-700": "#1D4ED8", "blue-800": "#1E40AF",
    "blue-900": "#1E3A8A", "blue-950": "#172554",
    # Indigo
    "indigo-50": "#EEF2FF", "indigo-100": "#E0E7FF", "indigo-200": "#C7D2FE",
    "indigo-300": "#A5B4FC", "indigo-400": "#818CF8", "indigo-500": "#6366F1",
    "indigo-600": "#4F46E5", "indigo-700": "#4338CA", "indigo-800": "#3730A3",
    "indigo-900": "#312E81", "indigo-950": "#1E1B4B",
    # Violet
    "violet-50": "#F5F3FF", "violet-100": "#EDE9FE", "violet-200": "#DDD6FE",
    "violet-300": "#C4B5FD", "violet-400": "#A78BFA", "violet-500": "#8B5CF6",
    "violet-600": "#7C3AED", "violet-700": "#6D28D9", "violet-800": "#5B21B6",
    "violet-900": "#4C1D95", "violet-950": "#2E1065",
    # Purple
    "purple-50": "#FAF5FF", "purple-100": "#F3E8FF", "purple-200": "#E9D5FF",
    "purple-300": "#D8B4FE", "purple-400": "#C084FC", "purple-500": "#A855F7",
    "purple-600": "#9333EA", "purple-700": "#7E22CE", "purple-800": "#6B21A8",
    "purple-900": "#581C87", "purple-950": "#3B0764",
    # Fuchsia
    "fuchsia-50": "#FDF4FF", "fuchsia-100": "#FAE8FF", "fuchsia-200": "#F5D0FE",
    "fuchsia-300": "#F0ABFC", "fuchsia-400": "#E879F9", "fuchsia-500": "#D946EF",
    "fuchsia-600": "#C026D3", "fuchsia-700": "#A21CAF", "fuchsia-800": "#86198F",
    "fuchsia-900": "#701A75", "fuchsia-950": "#4A044E",
    # Pink
    "pink-50": "#FDF2F8", "pink-100": "#FCE7F3", "pink-200": "#FBCFE8",
    "pink-300": "#F9A8D4", "pink-400": "#F472B6", "pink-500": "#EC4899",
    "pink-600": "#DB2777", "pink-700": "#BE185D", "pink-800": "#9D174D",
    "pink-900": "#831843", "pink-950": "#500724",
    # Rose
    "rose-50": "#FFF1F2", "rose-100": "#FFE4E6", "rose-200": "#FECDD3",
    "rose-300": "#FDA4AF", "rose-400": "#FB7185", "rose-500": "#F43F5E",
    "rose-600": "#E11D48", "rose-700": "#BE123C", "rose-800": "#9F1239",
    "rose-900": "#881337", "rose-950": "#4C0519",
    # Neutrals
    "white": "#FFFFFF", "black": "#000000",
    "transparent": "transparent",
}

# Reverse mapping: HEX → Tailwind color name
HEX_TO_TAILWIND_MAP: Dict[str, str] = {v.upper(): k for k, v in TAILWIND_COLOR_MAP.items() if v.startswith("#")}


# =============================================================================
# Unified Design Token Classes (GAP 1 Fix)
# =============================================================================

TokenRole = Literal["primary", "secondary", "accent", "muted", "background", "surface", "border", "text"]


class UnifiedColorToken(BaseModel):
    """A color token with both Tailwind class and HEX representation.

    Enables seamless conversion between:
    - Tailwind classes extracted from HTML (bg-blue-600, text-gray-900)
    - HEX values from reference images (#3B82F6, #111827)
    """

    tailwind_class: str = Field(..., description="Tailwind color class (e.g., 'blue-600')")
    hex_value: str = Field(..., description="HEX color value (e.g., '#3B82F6')")
    role: TokenRole = Field(default="primary", description="Semantic role of this color")
    opacity: Optional[float] = Field(default=None, ge=0, le=1, description="Opacity modifier (0-1)")

    @field_validator("hex_value", mode="before")
    @classmethod
    def validate_hex(cls, v: Any) -> str:
        """Normalize HEX value to uppercase #RRGGBB format."""
        if not isinstance(v, str):
            return "#000000"
        v = v.strip().upper()
        if not v.startswith("#"):
            v = f"#{v}"
        if re.match(r"^#([A-Fa-f0-9]{6})$", v):
            return v
        if re.match(r"^#([A-Fa-f0-9]{3})$", v):
            # Expand shorthand #RGB → #RRGGBB
            return f"#{v[1]*2}{v[2]*2}{v[3]*2}"
        return "#000000"

    @classmethod
    def from_tailwind(cls, tailwind_color: str, role: TokenRole = "primary") -> "UnifiedColorToken":
        """Create UnifiedColorToken from Tailwind color class.

        Args:
            tailwind_color: Tailwind color (e.g., 'blue-600', 'bg-blue-600/50')
            role: Semantic role for this color

        Returns:
            UnifiedColorToken with both representations
        """
        # Extract base color and opacity from patterns like 'bg-blue-600/50'
        opacity = None
        clean_color = tailwind_color

        # Remove prefix (bg-, text-, border-, ring-, etc.)
        prefixes = ["bg-", "text-", "border-", "ring-", "fill-", "stroke-", "from-", "via-", "to-"]
        for prefix in prefixes:
            if clean_color.startswith(prefix):
                clean_color = clean_color[len(prefix):]
                break

        # Extract opacity modifier (/50 → 0.5)
        if "/" in clean_color:
            clean_color, opacity_str = clean_color.rsplit("/", 1)
            try:
                opacity = int(opacity_str) / 100
            except ValueError:
                opacity = None

        # Look up HEX value
        hex_value = TAILWIND_COLOR_MAP.get(clean_color, "#000000")

        # Handle arbitrary values like '[#E11D48]'
        if clean_color.startswith("[") and clean_color.endswith("]"):
            hex_value = clean_color[1:-1]
            if not hex_value.startswith("#"):
                hex_value = f"#{hex_value}"

        return cls(
            tailwind_class=clean_color,
            hex_value=hex_value,
            role=role,
            opacity=opacity,
        )

    @classmethod
    def from_hex(cls, hex_value: str, role: TokenRole = "primary") -> "UnifiedColorToken":
        """Create UnifiedColorToken from HEX value.

        Args:
            hex_value: HEX color (e.g., '#3B82F6')
            role: Semantic role for this color

        Returns:
            UnifiedColorToken with closest Tailwind match
        """
        hex_upper = hex_value.upper()
        if not hex_upper.startswith("#"):
            hex_upper = f"#{hex_upper}"

        # Direct lookup
        tailwind_class = HEX_TO_TAILWIND_MAP.get(hex_upper)

        if not tailwind_class:
            # Find closest color by distance
            tailwind_class = cls._find_closest_tailwind_color(hex_upper)

        return cls(
            tailwind_class=tailwind_class or f"[{hex_upper}]",
            hex_value=hex_upper,
            role=role,
        )

    @staticmethod
    def _find_closest_tailwind_color(hex_value: str) -> Optional[str]:
        """Find the closest Tailwind color to a HEX value using color distance."""
        try:
            r1 = int(hex_value[1:3], 16)
            g1 = int(hex_value[3:5], 16)
            b1 = int(hex_value[5:7], 16)
        except (ValueError, IndexError):
            return None

        min_distance = float("inf")
        closest = None

        for tw_name, tw_hex in TAILWIND_COLOR_MAP.items():
            if not tw_hex.startswith("#") or len(tw_hex) != 7:
                continue
            try:
                r2 = int(tw_hex[1:3], 16)
                g2 = int(tw_hex[3:5], 16)
                b2 = int(tw_hex[5:7], 16)
            except (ValueError, IndexError):
                continue

            # Weighted Euclidean distance (human perception)
            distance = ((r1 - r2) ** 2 * 0.3 + (g1 - g2) ** 2 * 0.59 + (b1 - b2) ** 2 * 0.11) ** 0.5

            if distance < min_distance:
                min_distance = distance
                closest = tw_name

        return closest

    def to_bg_class(self) -> str:
        """Return as background Tailwind class."""
        base = f"bg-{self.tailwind_class}"
        if self.opacity:
            base += f"/{int(self.opacity * 100)}"
        return base

    def to_text_class(self) -> str:
        """Return as text Tailwind class."""
        base = f"text-{self.tailwind_class}"
        if self.opacity:
            base += f"/{int(self.opacity * 100)}"
        return base


class UnifiedSpacingToken(BaseModel):
    """Spacing token with Tailwind class, rem, and px values.

    Enables conversion between:
    - Tailwind spacing (p-4, gap-8, py-20)
    - rem values (1rem, 2rem)
    - px values (16px, 32px)
    """

    tailwind_class: str = Field(..., description="Tailwind spacing class (e.g., 'p-4', 'gap-8')")
    rem_value: float = Field(..., description="Value in rem units")
    px_value: float = Field(..., description="Value in pixels (assuming 16px base)")

    @classmethod
    def from_tailwind(cls, tailwind_class: str) -> "UnifiedSpacingToken":
        """Create from Tailwind spacing class."""
        # Tailwind spacing scale: 1 = 0.25rem = 4px
        TAILWIND_SPACING = {
            "0": 0, "px": 0.0625, "0.5": 0.125, "1": 0.25, "1.5": 0.375,
            "2": 0.5, "2.5": 0.625, "3": 0.75, "3.5": 0.875, "4": 1,
            "5": 1.25, "6": 1.5, "7": 1.75, "8": 2, "9": 2.25, "10": 2.5,
            "11": 2.75, "12": 3, "14": 3.5, "16": 4, "20": 5, "24": 6,
            "28": 7, "32": 8, "36": 9, "40": 10, "44": 11, "48": 12,
            "52": 13, "56": 14, "60": 15, "64": 16, "72": 18, "80": 20,
            "96": 24,
        }

        # Extract number from class like 'p-4', 'gap-8', 'py-20'
        match = re.search(r"(\d+\.?\d*)", tailwind_class)
        if match:
            num = match.group(1)
            rem_value = TAILWIND_SPACING.get(num, float(num) * 0.25)
        else:
            rem_value = 1.0  # Default

        return cls(
            tailwind_class=tailwind_class,
            rem_value=rem_value,
            px_value=rem_value * 16,
        )

    @classmethod
    def from_px(cls, px_value: float, prefix: str = "p") -> "UnifiedSpacingToken":
        """Create from pixel value with Tailwind prefix."""
        rem_value = px_value / 16

        # Find closest Tailwind spacing
        TAILWIND_SPACING_REVERSE = {
            0: "0", 1: "px", 2: "0.5", 4: "1", 6: "1.5", 8: "2", 10: "2.5",
            12: "3", 14: "3.5", 16: "4", 20: "5", 24: "6", 28: "7", 32: "8",
            36: "9", 40: "10", 44: "11", 48: "12", 56: "14", 64: "16",
            80: "20", 96: "24", 112: "28", 128: "32", 144: "36", 160: "40",
            176: "44", 192: "48", 208: "52", 224: "56", 240: "60", 256: "64",
            288: "72", 320: "80", 384: "96",
        }

        closest_px = min(TAILWIND_SPACING_REVERSE.keys(), key=lambda x: abs(x - px_value))
        tw_num = TAILWIND_SPACING_REVERSE[closest_px]

        return cls(
            tailwind_class=f"{prefix}-{tw_num}",
            rem_value=rem_value,
            px_value=px_value,
        )


class UnifiedDesignTokenSchema(BaseModel):
    """Complete unified design token schema for cross-tool consistency.

    This schema bridges the gap between different token formats:
    - design_section: extracts tokens as Tailwind classes via regex
    - design_from_reference: extracts tokens as HEX values from images
    - design_frontend: needs tokens for theme consistency

    All tools can now use this unified schema for interoperability.
    """

    # Color tokens with both Tailwind and HEX
    colors: Dict[TokenRole, UnifiedColorToken] = Field(
        default_factory=dict,
        description="Color tokens by role"
    )

    # Typography (Tailwind classes)
    typography: Dict[str, str] = Field(
        default_factory=lambda: {
            "heading": "text-4xl font-bold",
            "subheading": "text-xl font-semibold",
            "body": "text-base font-normal",
            "small": "text-sm font-normal",
            "caption": "text-xs font-light",
        },
        description="Typography class combinations"
    )

    # Spacing tokens
    spacing: Dict[str, UnifiedSpacingToken] = Field(
        default_factory=dict,
        description="Spacing tokens (section_padding, element_gap, etc.)"
    )

    # Border/radius (Tailwind classes)
    borders: Dict[str, str] = Field(
        default_factory=lambda: {
            "radius": "rounded-xl",
            "width": "border",
            "color": "border-gray-200",
        },
        description="Border styling classes"
    )

    # Effects (shadows, blur, etc.)
    effects: Dict[str, str] = Field(
        default_factory=lambda: {
            "shadow": "shadow-lg",
            "hover_shadow": "hover:shadow-xl",
            "blur": "",
        },
        description="Effect classes"
    )

    # Source metadata
    source: Literal["html_extraction", "reference_image", "theme_factory", "user_defined"] = Field(
        default="theme_factory",
        description="How these tokens were obtained"
    )

    def to_legacy_design_tokens(self) -> "DesignTokens":
        """Convert to legacy DesignTokens format for backward compatibility."""
        return DesignTokens(
            colors=ColorTokens(
                primary=self.colors.get("primary", UnifiedColorToken(tailwind_class="blue-600", hex_value="#2563EB", role="primary")).hex_value,
                secondary=self.colors.get("secondary", UnifiedColorToken(tailwind_class="gray-600", hex_value="#4B5563", role="secondary")).hex_value,
                accent=self.colors.get("accent", UnifiedColorToken(tailwind_class="emerald-500", hex_value="#10B981", role="accent")).hex_value,
                background=self.colors.get("background", UnifiedColorToken(tailwind_class="white", hex_value="#FFFFFF", role="background")).hex_value,
                surface=self.colors.get("surface", UnifiedColorToken(tailwind_class="gray-50", hex_value="#F9FAFB", role="surface")).hex_value,
                text_primary=self.colors.get("text", UnifiedColorToken(tailwind_class="gray-900", hex_value="#111827", role="text")).hex_value,
                text_secondary=self.colors.get("muted", UnifiedColorToken(tailwind_class="gray-600", hex_value="#4B5563", role="muted")).hex_value,
                border=self.colors.get("border", UnifiedColorToken(tailwind_class="gray-200", hex_value="#E5E7EB", role="border")).hex_value,
            ),
            typography=TypographyTokens(
                heading_size=self.typography.get("heading", "text-4xl font-bold").split()[0] if self.typography.get("heading") else "text-4xl",
                body_size=self.typography.get("body", "text-base font-normal").split()[0] if self.typography.get("body") else "text-base",
                font_weight_heading="font-bold",
                font_weight_body="font-normal",
                line_height="leading-relaxed",
            ),
            spacing=SpacingTokens(
                section_padding=self.spacing.get("section_padding", UnifiedSpacingToken(tailwind_class="py-20", rem_value=5, px_value=80)).tailwind_class if "section_padding" in self.spacing else "py-20",
                element_gap=self.spacing.get("element_gap", UnifiedSpacingToken(tailwind_class="gap-8", rem_value=2, px_value=32)).tailwind_class if "element_gap" in self.spacing else "gap-8",
                container_padding=self.spacing.get("container_padding", UnifiedSpacingToken(tailwind_class="px-6", rem_value=1.5, px_value=24)).tailwind_class if "container_padding" in self.spacing else "px-6",
            ),
            borders=BorderTokens(
                radius=self.borders.get("radius", "rounded-xl"),
            ),
            shadows=ShadowTokens(
                card=self.effects.get("shadow", "shadow-lg"),
                hover=self.effects.get("hover_shadow", "hover:shadow-xl"),
            ),
        )

    @classmethod
    def from_legacy_design_tokens(cls, tokens: "DesignTokens") -> "UnifiedDesignTokenSchema":
        """Create from legacy DesignTokens format."""
        return cls(
            colors={
                "primary": UnifiedColorToken.from_hex(tokens.colors.primary, "primary"),
                "secondary": UnifiedColorToken.from_hex(tokens.colors.secondary, "secondary"),
                "accent": UnifiedColorToken.from_hex(tokens.colors.accent, "accent"),
                "background": UnifiedColorToken.from_hex(tokens.colors.background, "background"),
                "surface": UnifiedColorToken.from_hex(tokens.colors.surface, "surface"),
                "text": UnifiedColorToken.from_hex(tokens.colors.text_primary, "text"),
                "muted": UnifiedColorToken.from_hex(tokens.colors.text_secondary, "muted"),
                "border": UnifiedColorToken.from_hex(tokens.colors.border, "border"),
            },
            typography={
                "heading": f"{tokens.typography.heading_size} {tokens.typography.font_weight_heading}",
                "body": f"{tokens.typography.body_size} {tokens.typography.font_weight_body}",
            },
            spacing={
                "section_padding": UnifiedSpacingToken.from_tailwind(tokens.spacing.section_padding),
                "element_gap": UnifiedSpacingToken.from_tailwind(tokens.spacing.element_gap),
                "container_padding": UnifiedSpacingToken.from_tailwind(tokens.spacing.container_padding),
            },
            borders={
                "radius": tokens.borders.radius,
                "width": tokens.borders.width,
            },
            effects={
                "shadow": tokens.shadows.card,
                "hover_shadow": tokens.shadows.hover,
            },
            source="user_defined",
        )


def normalize_tokens(
    raw_tokens: Dict[str, Any],
    source: Literal["html_extraction", "reference_image", "theme_factory", "user_defined"] = "html_extraction"
) -> UnifiedDesignTokenSchema:
    """Normalize tokens from any source into UnifiedDesignTokenSchema.

    Handles various input formats:
    - HTML extraction: {"colors": {"primary": "blue-600"}, ...}
    - Reference image: {"colors": {"#E11D48": "brand", ...}, ...}
    - Theme factory: DesignTokens object

    Args:
        raw_tokens: Raw token dictionary from any source
        source: Token source for metadata

    Returns:
        Normalized UnifiedDesignTokenSchema
    """
    colors: Dict[TokenRole, UnifiedColorToken] = {}
    typography: Dict[str, str] = {}
    spacing: Dict[str, UnifiedSpacingToken] = {}
    borders: Dict[str, str] = {}
    effects: Dict[str, str] = {}

    # Process colors
    if "colors" in raw_tokens:
        raw_colors = raw_tokens["colors"]
        if isinstance(raw_colors, dict):
            for key, value in raw_colors.items():
                # Determine if key is a role or a color value
                role: TokenRole = "primary"
                color_value = value

                if key in ("primary", "secondary", "accent", "muted", "background", "surface", "border", "text"):
                    role = key  # type: ignore
                    color_value = value
                elif key.startswith("#"):
                    # HEX key, value is role
                    color_value = key
                    if value in ("primary", "secondary", "accent", "muted", "background", "surface", "border", "text"):
                        role = value  # type: ignore

                # Create token based on format
                if isinstance(color_value, str):
                    if color_value.startswith("#"):
                        colors[role] = UnifiedColorToken.from_hex(color_value, role)
                    else:
                        colors[role] = UnifiedColorToken.from_tailwind(color_value, role)

    # Process typography
    if "typography" in raw_tokens:
        raw_typo = raw_tokens["typography"]
        if isinstance(raw_typo, dict):
            for key, value in raw_typo.items():
                if isinstance(value, str):
                    typography[key] = value

    # Process spacing
    if "spacing" in raw_tokens:
        raw_spacing = raw_tokens["spacing"]
        if isinstance(raw_spacing, dict):
            for key, value in raw_spacing.items():
                if isinstance(value, str):
                    spacing[key] = UnifiedSpacingToken.from_tailwind(value)
                elif isinstance(value, (int, float)):
                    spacing[key] = UnifiedSpacingToken.from_px(float(value))

    # Process borders
    if "borders" in raw_tokens:
        raw_borders = raw_tokens["borders"]
        if isinstance(raw_borders, dict):
            for key, value in raw_borders.items():
                if isinstance(value, str):
                    borders[key] = value

    # Process effects (shadows, etc.)
    if "effects" in raw_tokens or "shadows" in raw_tokens:
        raw_effects = raw_tokens.get("effects", raw_tokens.get("shadows", {}))
        if isinstance(raw_effects, dict):
            for key, value in raw_effects.items():
                if isinstance(value, str):
                    effects[key] = value

    return UnifiedDesignTokenSchema(
        colors=colors,
        typography=typography,
        spacing=spacing,
        borders=borders,
        effects=effects,
        source=source,
    )


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
    css: str = Field(default="", description="Custom CSS for keyframes/scrollbars (NO Tailwind)")
    javascript: str = Field(default="", description="Alpine.js or Vanilla JS logic (Clean separation)")
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
    design_thinking: str = Field(default="", description="Design-CoT reasoning step before generation")
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


# =============================================================================
# Design-CoT (Structured Chain of Thought) Schema
# =============================================================================

DESIGN_THINKING_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": [
        "constraint_check",
        "aesthetic_physics",
        "visual_dna",
        "micro_interactions",
        "responsive_strategy",
        "a11y_checklist",
    ],
    "properties": {
        "constraint_check": {
            "type": "string",
            "minLength": 20,
            "description": "Verify density targets and vibe consistency. Example: '4-Layer Rule? ✓ Density 8+? ✓ Vibe consistent? ✓'"
        },
        "aesthetic_physics": {
            "type": "string",
            "minLength": 30,
            "description": "Define materiality, lighting, and depth. Example: 'Materiality: frosted glass | Lighting: top-left glow | Depth: 4 layers'"
        },
        "visual_dna": {
            "type": "string",
            "minLength": 50,
            "description": "Core Tailwind class combinations. Example: 'bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900'"
        },
        "micro_interactions": {
            "type": "string",
            "minLength": 30,
            "description": "Hover, focus, and transition patterns. Example: 'hover:translateY(-4px) with 150ms ease-out, focus:ring-2'"
        },
        "responsive_strategy": {
            "type": "string",
            "minLength": 20,
            "description": "Mobile-first breakpoint approach. Example: 'Mobile-first, sm:grid-cols-1 → lg:grid-cols-3'"
        },
        "a11y_checklist": {
            "type": "string",
            "minLength": 20,
            "description": "Accessibility verification. Example: 'focus-visible ring ✓, aria-label ✓, contrast ≥4.5:1 ✓'"
        },
        "density_iteration": {
            "type": "string",
            "description": "Optional: Final density check. Example: 'Can I add 15% more without visual noise? Adding inner-ring. Final: 16 classes'"
        },
    },
    "additionalProperties": False,
}


class DesignThinking(BaseModel):
    """Structured Chain of Thought (SCoT) for design generation.

    This model enforces the 7-step design thinking process:
    1. CONSTRAINT_CHECK - Verify density and vibe targets
    2. AESTHETIC_PHYSICS - Define materiality and depth
    3. VISUAL_DNA - Core Tailwind combinations
    4. MICRO_INTERACTIONS - Hover/focus/transition patterns
    5. RESPONSIVE_STRATEGY - Breakpoint approach
    6. A11Y_CHECKLIST - Accessibility verification
    7. DENSITY_ITERATION - Final density optimization (optional)
    """

    constraint_check: str = Field(
        ...,
        min_length=20,
        description="Verify density targets and vibe consistency",
        examples=["4-Layer Rule? ✓ Density 8+? ✓ Vibe consistent? ✓"]
    )
    aesthetic_physics: str = Field(
        ...,
        min_length=30,
        description="Define materiality, lighting, and depth",
        examples=["Materiality: frosted glass | Lighting: top-left glow | Depth: 4 layers"]
    )
    visual_dna: str = Field(
        ...,
        min_length=50,
        description="Core Tailwind class combinations",
        examples=["bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"]
    )
    micro_interactions: str = Field(
        ...,
        min_length=30,
        description="Hover, focus, and transition patterns",
        examples=["hover:translateY(-4px) with 150ms ease-out, focus:ring-2"]
    )
    responsive_strategy: str = Field(
        ...,
        min_length=20,
        description="Mobile-first breakpoint approach",
        examples=["Mobile-first, sm:grid-cols-1 → lg:grid-cols-3"]
    )
    a11y_checklist: str = Field(
        ...,
        min_length=20,
        description="Accessibility verification",
        examples=["focus-visible ring ✓, aria-label ✓, contrast ≥4.5:1 ✓"]
    )
    density_iteration: Optional[str] = Field(
        default=None,
        description="Optional: Final density check",
        examples=["Can I add 15% more without visual noise? Adding inner-ring. Final: 16 classes"]
    )

    def to_formatted_string(self) -> str:
        """Format as numbered design thinking steps for prompts."""
        lines = [
            f"1. CONSTRAINT_CHECK: {self.constraint_check}",
            f"2. AESTHETIC_PHYSICS: {self.aesthetic_physics}",
            f"3. VISUAL_DNA: {self.visual_dna}",
            f"4. MICRO_INTERACTIONS: {self.micro_interactions}",
            f"5. RESPONSIVE_STRATEGY: {self.responsive_strategy}",
            f"6. A11Y_CHECKLIST: {self.a11y_checklist}",
        ]
        if self.density_iteration:
            lines.append(f"7. DENSITY_ITERATION: {self.density_iteration}")
        return " | ".join(lines)

    @classmethod
    def from_formatted_string(cls, text: str) -> "DesignThinking":
        """Parse from formatted design thinking string.

        Expected format:
        '1. CONSTRAINT_CHECK: ... | 2. AESTHETIC_PHYSICS: ... | ...'
        """
        parts = {}
        current_key = None
        current_value = []

        # Pattern: "N. KEY_NAME: value"
        import re
        pattern = r'(\d+)\.\s*([A-Z_]+):\s*'

        tokens = re.split(pattern, text)
        # tokens will be: ['', '1', 'CONSTRAINT_CHECK', 'value...', '2', ...]

        i = 1  # Skip empty first element
        while i < len(tokens) - 1:
            if i + 2 < len(tokens):
                key = tokens[i + 1].lower()  # CONSTRAINT_CHECK -> constraint_check
                value = tokens[i + 2].strip().rstrip('|').strip()
                parts[key] = value
            i += 3

        return cls(
            constraint_check=parts.get("constraint_check", "Not specified"),
            aesthetic_physics=parts.get("aesthetic_physics", "Not specified"),
            visual_dna=parts.get("visual_dna", "Not specified - using defaults"),
            micro_interactions=parts.get("micro_interactions", "Default hover effects"),
            responsive_strategy=parts.get("responsive_strategy", "Mobile-first approach"),
            a11y_checklist=parts.get("a11y_checklist", "Standard accessibility"),
            density_iteration=parts.get("density_iteration"),
        )


def validate_design_thinking(text: str) -> tuple[bool, List[str]]:
    """Validate a design_thinking string for completeness.

    Args:
        text: The design_thinking output from Gemini

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    required_steps = [
        ("CONSTRAINT_CHECK", 20),
        ("AESTHETIC_PHYSICS", 30),
        ("VISUAL_DNA", 50),
        ("MICRO_INTERACTIONS", 30),
        ("RESPONSIVE_STRATEGY", 20),
        ("A11Y_CHECKLIST", 20),
    ]

    for step_name, min_length in required_steps:
        # Check if step exists
        if step_name not in text.upper():
            issues.append(f"Missing required step: {step_name}")
        else:
            # Extract step content and check length
            import re
            pattern = rf'{step_name}:\s*([^|]+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if len(content) < min_length:
                    issues.append(
                        f"{step_name} content too short ({len(content)} chars, min {min_length})"
                    )
            else:
                issues.append(f"Could not extract content for {step_name}")

    return len(issues) == 0, issues


# =============================================================================
# Complexity Levels System
# =============================================================================

ComplexityLevel = Literal["low", "standard", "high", "ultra"]


class ComplexityConfig(BaseModel):
    """Configuration for a complexity level.

    Higher complexity = more Tailwind classes, more design thinking steps,
    more few-shot examples injected into prompts.
    """

    min_classes: int = Field(
        ...,
        ge=4,
        le=30,
        description="Minimum Tailwind classes per element"
    )
    target_classes: int = Field(
        ...,
        ge=6,
        le=40,
        description="Target Tailwind classes per element"
    )
    design_cot_steps: int = Field(
        ...,
        ge=3,
        le=7,
        description="Number of Design-CoT steps to enforce"
    )
    few_shot_count: int = Field(
        ...,
        ge=1,
        le=5,
        description="Number of few-shot examples to include"
    )
    use_case: str = Field(
        ...,
        description="Typical use case for this complexity level"
    )
    quality_threshold: float = Field(
        default=7.0,
        ge=5.0,
        le=10.0,
        description="Minimum quality score from Critic"
    )
    max_iterations: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum refinement iterations"
    )


COMPLEXITY_LEVELS: Dict[ComplexityLevel, ComplexityConfig] = {
    "low": ComplexityConfig(
        min_classes=6,
        target_classes=8,
        design_cot_steps=3,
        few_shot_count=1,
        use_case="Simple components, prototypes, quick mockups",
        quality_threshold=6.0,
        max_iterations=1,
    ),
    "standard": ComplexityConfig(
        min_classes=10,
        target_classes=14,
        design_cot_steps=5,
        few_shot_count=2,
        use_case="Production components, typical UI elements",
        quality_threshold=7.0,
        max_iterations=2,
    ),
    "high": ComplexityConfig(
        min_classes=14,
        target_classes=18,
        design_cot_steps=7,
        few_shot_count=3,
        use_case="Premium components, hero sections, key features",
        quality_threshold=8.0,
        max_iterations=3,
    ),
    "ultra": ComplexityConfig(
        min_classes=18,
        target_classes=24,
        design_cot_steps=7,
        few_shot_count=4,
        use_case="Showcase landing pages, marketing sites, portfolio pieces",
        quality_threshold=8.5,
        max_iterations=4,
    ),
}


def get_complexity_config(level: ComplexityLevel) -> ComplexityConfig:
    """Get complexity configuration by level.

    Args:
        level: One of 'low', 'standard', 'high', 'ultra'

    Returns:
        ComplexityConfig for the specified level
    """
    return COMPLEXITY_LEVELS.get(level, COMPLEXITY_LEVELS["standard"])


def infer_complexity_from_component(component_type: str) -> ComplexityLevel:
    """Infer appropriate complexity level from component type.

    Args:
        component_type: The type of component (button, hero, navbar, etc.)

    Returns:
        Recommended complexity level
    """
    # Ultra complexity components - maximum richness required
    ultra_components = {"hero", "landing_page", "pricing_table", "feature_section"}

    # High complexity components - premium treatment
    high_components = {
        "navbar", "footer", "testimonial_section", "dashboard_header",
        "pricing_card", "modal", "data_table", "kanban_board"
    }

    # Standard complexity components - typical production elements
    standard_components = {
        "card", "form", "tabs", "accordion", "carousel", "stepper",
        "timeline", "file_upload", "user_profile", "settings_panel"
    }

    # Everything else is low complexity (atoms, simple molecules)
    component_lower = component_type.lower()

    if component_lower in ultra_components:
        return "ultra"
    elif component_lower in high_components:
        return "high"
    elif component_lower in standard_components:
        return "standard"
    else:
        return "low"


def validate_output_density(
    html: str,
    complexity: ComplexityLevel,
    strict: bool = False
) -> tuple[bool, Dict[str, Any]]:
    """Validate HTML output meets density requirements for complexity level.

    Args:
        html: Generated HTML string
        complexity: The complexity level used
        strict: If True, fails on any violation. If False, warns.

    Returns:
        Tuple of (passes_validation, metrics_dict)
    """
    import re

    config = get_complexity_config(complexity)

    # Extract all class attributes
    class_pattern = r'class="([^"]*)"'
    matches = re.findall(class_pattern, html)

    if not matches:
        return False, {"error": "No class attributes found"}

    # Calculate metrics
    total_classes = 0
    element_count = 0
    min_element_classes = float('inf')
    max_element_classes = 0

    for class_str in matches:
        classes = [c.strip() for c in class_str.split() if c.strip()]
        class_count = len(classes)

        if class_count > 0:
            total_classes += class_count
            element_count += 1
            min_element_classes = min(min_element_classes, class_count)
            max_element_classes = max(max_element_classes, class_count)

    avg_classes = total_classes / element_count if element_count > 0 else 0

    metrics = {
        "element_count": element_count,
        "total_classes": total_classes,
        "avg_classes_per_element": round(avg_classes, 2),
        "min_classes_on_element": min_element_classes if min_element_classes != float('inf') else 0,
        "max_classes_on_element": max_element_classes,
        "required_min": config.min_classes,
        "target": config.target_classes,
        "complexity_level": complexity,
    }

    # Validation
    passes = avg_classes >= config.min_classes

    if strict:
        # In strict mode, every element must meet minimum
        passes = passes and (min_element_classes >= config.min_classes // 2)

    metrics["passes_validation"] = passes
    metrics["density_score"] = round((avg_classes / config.target_classes) * 10, 1)

    return passes, metrics
