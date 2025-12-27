"""
Visual Language Model - Design System Tokens

Defines the visual language of a project including:
- Color Palette: Primary, secondary, accent, neutral colors
- Typography: Font families, scales, weights
- Spacing & Layout: Grid systems, whitespace rhythm
- Visual Effects: Shadows, borders, animations

Reference: Design Systems methodology (Atomic Design, Material Design).
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ColorHarmony(str, Enum):
    """Color harmony schemes for palette generation."""

    MONOCHROMATIC = "monochromatic"  # Single hue variations
    ANALOGOUS = "analogous"  # Adjacent colors on wheel
    COMPLEMENTARY = "complementary"  # Opposite colors
    SPLIT_COMPLEMENTARY = "split_complementary"  # Opposite + adjacent
    TRIADIC = "triadic"  # Three evenly spaced
    TETRADIC = "tetradic"  # Four colors (rectangle)


class ColorTemperature(str, Enum):
    """Overall color temperature of the palette."""

    WARM = "warm"  # Reds, oranges, yellows
    COOL = "cool"  # Blues, greens, purples
    NEUTRAL = "neutral"  # Grays, balanced mix
    VIBRANT = "vibrant"  # High saturation mix


class TypographyScale(str, Enum):
    """Typographic scale ratios for heading hierarchy."""

    MINOR_SECOND = "minor_second"  # 1.067 - Subtle
    MAJOR_SECOND = "major_second"  # 1.125 - Standard
    MINOR_THIRD = "minor_third"  # 1.200 - Comfortable
    MAJOR_THIRD = "major_third"  # 1.250 - Bold
    PERFECT_FOURTH = "perfect_fourth"  # 1.333 - Dramatic
    GOLDEN_RATIO = "golden_ratio"  # 1.618 - Classical


class FontCategory(str, Enum):
    """Font family categories."""

    SANS_SERIF = "sans_serif"  # Modern, clean
    SERIF = "serif"  # Traditional, authoritative
    DISPLAY = "display"  # Decorative, headlines only
    MONOSPACE = "monospace"  # Code, technical
    HANDWRITTEN = "handwritten"  # Casual, personal


class SpacingDensity(str, Enum):
    """Overall spacing density."""

    COMPACT = "compact"  # Tight spacing, data-dense
    COMFORTABLE = "comfortable"  # Standard spacing
    SPACIOUS = "spacious"  # Generous whitespace
    AIRY = "airy"  # Very open, editorial feel


class ColorPalette(BaseModel):
    """
    Complete color palette definition.

    Example:
        >>> palette = ColorPalette(
        ...     primary="#E11D48",
        ...     secondary="#06B6D4",
        ...     background="#0F172A",
        ...     foreground="#F8FAFC",
        ... )
    """

    # Core colors
    primary: str = Field(
        default="#3B82F6",
        description="Ana marka rengi (hex)",
    )
    primary_foreground: str = Field(
        default="#FFFFFF",
        description="Primary üzerindeki metin rengi",
    )

    secondary: str = Field(
        default="#64748B",
        description="İkincil renk (hex)",
    )
    secondary_foreground: str = Field(
        default="#FFFFFF",
        description="Secondary üzerindeki metin rengi",
    )

    accent: str = Field(
        default="#F59E0B",
        description="Vurgu rengi (dikkat çekici öğeler)",
    )
    accent_foreground: str = Field(
        default="#000000",
        description="Accent üzerindeki metin rengi",
    )

    # Background & Foreground
    background: str = Field(
        default="#FFFFFF",
        description="Ana arka plan rengi",
    )
    foreground: str = Field(
        default="#0F172A",
        description="Ana metin rengi",
    )

    # Semantic colors
    muted: str = Field(
        default="#F1F5F9",
        description="Soluk arka plan (secondary content)",
    )
    muted_foreground: str = Field(
        default="#64748B",
        description="Soluk metin rengi",
    )

    # State colors
    destructive: str = Field(
        default="#EF4444",
        description="Tehlike/silme rengi",
    )
    success: str = Field(
        default="#22C55E",
        description="Başarı rengi",
    )
    warning: str = Field(
        default="#F59E0B",
        description="Uyarı rengi",
    )
    info: str = Field(
        default="#3B82F6",
        description="Bilgi rengi",
    )

    # UI elements
    border: str = Field(
        default="#E2E8F0",
        description="Kenarlık rengi",
    )
    input: str = Field(
        default="#E2E8F0",
        description="Input kenarlık rengi",
    )
    ring: str = Field(
        default="#3B82F6",
        description="Focus ring rengi",
    )

    # Metadata
    harmony: ColorHarmony = Field(
        default=ColorHarmony.ANALOGOUS,
        description="Renk uyumu şeması",
    )
    temperature: ColorTemperature = Field(
        default=ColorTemperature.NEUTRAL,
        description="Renk sıcaklığı",
    )
    is_dark_mode: bool = Field(
        default=False,
        description="Dark mode palette mi?",
    )

    def to_css_variables(self) -> Dict[str, str]:
        """
        Convert palette to CSS custom properties.

        Returns a dictionary suitable for :root CSS block.
        """
        return {
            "--primary": self.primary,
            "--primary-foreground": self.primary_foreground,
            "--secondary": self.secondary,
            "--secondary-foreground": self.secondary_foreground,
            "--accent": self.accent,
            "--accent-foreground": self.accent_foreground,
            "--background": self.background,
            "--foreground": self.foreground,
            "--muted": self.muted,
            "--muted-foreground": self.muted_foreground,
            "--destructive": self.destructive,
            "--border": self.border,
            "--input": self.input,
            "--ring": self.ring,
        }

    def to_tailwind_config(self) -> Dict[str, str]:
        """
        Generate Tailwind config extend colors.

        Returns colors config suitable for tailwind.config.js.
        """
        return {
            "primary": {
                "DEFAULT": self.primary,
                "foreground": self.primary_foreground,
            },
            "secondary": {
                "DEFAULT": self.secondary,
                "foreground": self.secondary_foreground,
            },
            "accent": {
                "DEFAULT": self.accent,
                "foreground": self.accent_foreground,
            },
            "background": self.background,
            "foreground": self.foreground,
            "muted": {
                "DEFAULT": self.muted,
                "foreground": self.muted_foreground,
            },
            "destructive": {
                "DEFAULT": self.destructive,
            },
            "border": self.border,
            "input": self.input,
            "ring": self.ring,
        }


class TypographyStyle(BaseModel):
    """
    Typography system definition.

    Example:
        >>> typography = TypographyStyle(
        ...     heading_font="Inter",
        ...     body_font="Inter",
        ...     scale=TypographyScale.MAJOR_THIRD,
        ... )
    """

    # Font families
    heading_font: str = Field(
        default="Inter",
        description="Başlık font ailesi",
    )
    heading_category: FontCategory = Field(
        default=FontCategory.SANS_SERIF,
        description="Başlık font kategorisi",
    )

    body_font: str = Field(
        default="Inter",
        description="Gövde metin font ailesi",
    )
    body_category: FontCategory = Field(
        default=FontCategory.SANS_SERIF,
        description="Gövde font kategorisi",
    )

    mono_font: str = Field(
        default="JetBrains Mono",
        description="Monospace font (kod blokları)",
    )

    # Scale
    base_size: int = Field(
        default=16,
        ge=12,
        le=24,
        description="Temel font boyutu (px)",
    )
    scale: TypographyScale = Field(
        default=TypographyScale.MAJOR_THIRD,
        description="Tipografik ölçek oranı",
    )

    # Weights
    heading_weight: str = Field(
        default="bold",
        description="Başlık font ağırlığı (light, normal, medium, semibold, bold, black)",
    )
    body_weight: str = Field(
        default="normal",
        description="Gövde font ağırlığı",
    )

    # Line heights
    heading_line_height: float = Field(
        default=1.2,
        ge=1.0,
        le=2.0,
        description="Başlık satır yüksekliği",
    )
    body_line_height: float = Field(
        default=1.6,
        ge=1.0,
        le=2.5,
        description="Gövde satır yüksekliği",
    )

    # Letter spacing
    heading_tracking: str = Field(
        default="tight",
        description="Başlık harf aralığı (tighter, tight, normal, wide, wider)",
    )
    body_tracking: str = Field(
        default="normal",
        description="Gövde harf aralığı",
    )

    def get_scale_ratio(self) -> float:
        """Get the numeric ratio for the typography scale."""
        ratios = {
            TypographyScale.MINOR_SECOND: 1.067,
            TypographyScale.MAJOR_SECOND: 1.125,
            TypographyScale.MINOR_THIRD: 1.200,
            TypographyScale.MAJOR_THIRD: 1.250,
            TypographyScale.PERFECT_FOURTH: 1.333,
            TypographyScale.GOLDEN_RATIO: 1.618,
        }
        return ratios.get(self.scale, 1.250)

    def generate_size_scale(self) -> Dict[str, int]:
        """
        Generate a complete type size scale.

        Returns sizes for xs through 6xl based on the scale ratio.
        """
        ratio = self.get_scale_ratio()
        base = self.base_size

        return {
            "xs": int(base / (ratio ** 2)),
            "sm": int(base / ratio),
            "base": base,
            "lg": int(base * ratio),
            "xl": int(base * (ratio ** 2)),
            "2xl": int(base * (ratio ** 3)),
            "3xl": int(base * (ratio ** 4)),
            "4xl": int(base * (ratio ** 5)),
            "5xl": int(base * (ratio ** 6)),
            "6xl": int(base * (ratio ** 7)),
        }

    def to_tailwind_classes(self) -> Dict[str, str]:
        """
        Map typography settings to Tailwind classes.

        Returns class strings for headings and body text.
        """
        weight_map = {
            "light": "font-light",
            "normal": "font-normal",
            "medium": "font-medium",
            "semibold": "font-semibold",
            "bold": "font-bold",
            "black": "font-black",
        }

        tracking_map = {
            "tighter": "tracking-tighter",
            "tight": "tracking-tight",
            "normal": "tracking-normal",
            "wide": "tracking-wide",
            "wider": "tracking-wider",
        }

        return {
            "heading": f"{weight_map.get(self.heading_weight, 'font-bold')} {tracking_map.get(self.heading_tracking, 'tracking-tight')}",
            "body": f"{weight_map.get(self.body_weight, 'font-normal')} {tracking_map.get(self.body_tracking, 'tracking-normal')}",
            "leading_heading": f"leading-[{self.heading_line_height}]",
            "leading_body": f"leading-[{self.body_line_height}]",
        }


class VisualLanguage(BaseModel):
    """
    Complete visual language definition for a project.

    Combines color palette, typography, spacing, and effects into
    a cohesive design system.

    Example:
        >>> visual = VisualLanguage(
        ...     palette=ColorPalette(primary="#E11D48"),
        ...     typography=TypographyStyle(heading_font="Playfair Display"),
        ...     spacing_density=SpacingDensity.COMFORTABLE,
        ... )
    """

    # Core systems
    palette: ColorPalette = Field(
        default_factory=ColorPalette,
        description="Renk paleti",
    )
    typography: TypographyStyle = Field(
        default_factory=TypographyStyle,
        description="Tipografi sistemi",
    )

    # Spacing
    spacing_density: SpacingDensity = Field(
        default=SpacingDensity.COMFORTABLE,
        description="Boşluk yoğunluğu",
    )
    base_spacing: int = Field(
        default=4,
        ge=2,
        le=8,
        description="Temel spacing birimi (px)",
    )

    # Border radius
    border_radius: str = Field(
        default="rounded-lg",
        description="Varsayılan köşe yuvarlaklığı (Tailwind class)",
    )
    border_radius_scale: Dict[str, str] = Field(
        default_factory=lambda: {
            "none": "rounded-none",
            "sm": "rounded-sm",
            "md": "rounded-md",
            "lg": "rounded-lg",
            "xl": "rounded-xl",
            "2xl": "rounded-2xl",
            "full": "rounded-full",
        },
        description="Border radius scale",
    )

    # Shadows
    shadow_intensity: str = Field(
        default="medium",
        description="Gölge yoğunluğu (none, subtle, medium, dramatic)",
    )
    shadow_scale: Dict[str, str] = Field(
        default_factory=lambda: {
            "none": "shadow-none",
            "sm": "shadow-sm",
            "md": "shadow-md",
            "lg": "shadow-lg",
            "xl": "shadow-xl",
            "2xl": "shadow-2xl",
        },
        description="Shadow scale",
    )

    # Animations
    animation_preference: str = Field(
        default="normal",
        description="Animasyon tercihi (none, reduced, normal, playful)",
    )
    transition_duration: str = Field(
        default="duration-200",
        description="Varsayılan geçiş süresi (Tailwind class)",
    )

    # Theme hints
    closest_theme: Optional[str] = Field(
        default=None,
        description="En yakın hazır tema (modern-minimal, brutalist, vb.)",
    )
    vibe: Optional[str] = Field(
        default=None,
        description="Tasarım vibes (elite_corporate, playful_funny, vb.)",
    )

    # Confidence
    extraction_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Visual language çıkarım güveni",
    )

    def get_spacing_multipliers(self) -> Dict[str, float]:
        """
        Get spacing multipliers based on density.

        Returns multipliers for different spacing contexts.
        """
        multipliers = {
            SpacingDensity.COMPACT: {
                "section": 0.6,
                "component": 0.7,
                "element": 0.8,
            },
            SpacingDensity.COMFORTABLE: {
                "section": 1.0,
                "component": 1.0,
                "element": 1.0,
            },
            SpacingDensity.SPACIOUS: {
                "section": 1.4,
                "component": 1.3,
                "element": 1.2,
            },
            SpacingDensity.AIRY: {
                "section": 1.8,
                "component": 1.5,
                "element": 1.3,
            },
        }
        return multipliers.get(self.spacing_density, multipliers[SpacingDensity.COMFORTABLE])

    def to_design_tokens(self) -> Dict:
        """
        Export complete design tokens for design tools.

        Returns a comprehensive design token dictionary.
        """
        return {
            "colors": self.palette.to_css_variables(),
            "typography": {
                "fonts": {
                    "heading": self.typography.heading_font,
                    "body": self.typography.body_font,
                    "mono": self.typography.mono_font,
                },
                "scale": self.typography.generate_size_scale(),
                "weights": {
                    "heading": self.typography.heading_weight,
                    "body": self.typography.body_weight,
                },
            },
            "spacing": {
                "base": self.base_spacing,
                "density": self.spacing_density.value,
                "multipliers": self.get_spacing_multipliers(),
            },
            "borders": {
                "radius": self.border_radius,
                "scale": self.border_radius_scale,
            },
            "shadows": {
                "intensity": self.shadow_intensity,
                "scale": self.shadow_scale,
            },
            "motion": {
                "preference": self.animation_preference,
                "duration": self.transition_duration,
            },
        }

    def to_prompt_context(self) -> str:
        """
        Generate prompt-ready context string for AI agents.

        Returns formatted string for inclusion in system prompts.
        """
        lines = [
            "Visual Language:",
            f"  Primary Color: {self.palette.primary}",
            f"  Background: {self.palette.background}",
            f"  Heading Font: {self.typography.heading_font} ({self.typography.heading_weight})",
            f"  Body Font: {self.typography.body_font}",
            f"  Spacing: {self.spacing_density.value}",
            f"  Border Radius: {self.border_radius}",
            f"  Shadows: {self.shadow_intensity}",
            f"  Animation: {self.animation_preference}",
        ]

        if self.closest_theme:
            lines.append(f"  Closest Theme: {self.closest_theme}")

        if self.vibe:
            lines.append(f"  Vibe: {self.vibe}")

        return "\n".join(lines)
