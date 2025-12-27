"""
Brand Personality Model - Aaker Framework

Jennifer Aaker's Brand Personality Framework defines 5 core dimensions
that capture human characteristics associated with brands.

Reference: Aaker, J. L. (1997). Dimensions of brand personality.
           Journal of Marketing Research, 34(3), 347-356.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PersonalityArchetype(str, Enum):
    """
    Brand personality archetypes based on Jungian psychology.
    These archetypes help define the brand's core character.
    """

    # Sincerity-aligned
    THE_INNOCENT = "the_innocent"  # Pure, optimistic, simple
    THE_EVERYMAN = "the_everyman"  # Relatable, down-to-earth
    THE_CAREGIVER = "the_caregiver"  # Nurturing, protective

    # Excitement-aligned
    THE_HERO = "the_hero"  # Courageous, determined
    THE_REBEL = "the_rebel"  # Revolutionary, rule-breaker
    THE_EXPLORER = "the_explorer"  # Adventurous, independent

    # Competence-aligned
    THE_SAGE = "the_sage"  # Wise, knowledgeable, trusted advisor
    THE_RULER = "the_ruler"  # Authoritative, leader, in control

    # Sophistication-aligned
    THE_LOVER = "the_lover"  # Passionate, sensual, intimate
    THE_MAGICIAN = "the_magician"  # Transformative, visionary

    # Ruggedness-aligned
    THE_OUTLAW = "the_outlaw"  # Wild, free-spirited
    THE_CREATOR = "the_creator"  # Innovative, artistic


class BrandPersonality(BaseModel):
    """
    Aaker's 5-dimension brand personality model.

    Each dimension is scored 0.0-1.0, with higher values indicating
    stronger presence of that trait in the brand's personality.

    Example:
        >>> personality = BrandPersonality(
        ...     sincerity=0.8,
        ...     excitement=0.3,
        ...     competence=0.9,
        ...     sophistication=0.4,
        ...     ruggedness=0.2,
        ... )
        >>> personality.dominant_trait
        'competence'
    """

    # Aaker's 5 Dimensions
    sincerity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Samimiyet - Down-to-earth, honest, wholesome, cheerful",
    )
    excitement: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Heyecan - Daring, spirited, imaginative, up-to-date",
    )
    competence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Yetkinlik - Reliable, intelligent, successful",
    )
    sophistication: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Sofistike - Upper class, charming, glamorous",
    )
    ruggedness: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Sağlamlık - Outdoorsy, tough, masculine",
    )

    # Derived properties
    dominant_trait: Optional[str] = Field(
        default=None,
        description="Auto-calculated: The highest-scoring dimension",
    )
    personality_archetype: Optional[PersonalityArchetype] = Field(
        default=None,
        description="The Jungian archetype that best matches this personality",
    )

    # Turkish-specific traits (optional extensions)
    warmth: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Sıcaklık - Hospitality, warmth (culturally relevant for TR)",
    )
    tradition: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Gelenek - Respect for tradition, heritage",
    )

    def model_post_init(self, __context) -> None:
        """Auto-calculate dominant trait and archetype after initialization."""
        if self.dominant_trait is None:
            self.dominant_trait = self._calculate_dominant_trait()
        if self.personality_archetype is None:
            self.personality_archetype = self._infer_archetype()

    def _calculate_dominant_trait(self) -> str:
        """Find the dimension with highest score."""
        dimensions = {
            "sincerity": self.sincerity,
            "excitement": self.excitement,
            "competence": self.competence,
            "sophistication": self.sophistication,
            "ruggedness": self.ruggedness,
        }
        return max(dimensions, key=dimensions.get)

    def _infer_archetype(self) -> PersonalityArchetype:
        """
        Infer the best-matching archetype based on dimension scores.

        Uses a weighted scoring system where each archetype has
        primary and secondary dimension associations.
        """
        dominant = self._calculate_dominant_trait()

        # Archetype mapping based on dominant dimension
        archetype_map = {
            "sincerity": {
                "high_secondary": PersonalityArchetype.THE_CAREGIVER,  # sincerity + warmth
                "default": PersonalityArchetype.THE_EVERYMAN,
            },
            "excitement": {
                "high_ruggedness": PersonalityArchetype.THE_EXPLORER,
                "high_sophistication": PersonalityArchetype.THE_REBEL,
                "default": PersonalityArchetype.THE_HERO,
            },
            "competence": {
                "high_sophistication": PersonalityArchetype.THE_RULER,
                "default": PersonalityArchetype.THE_SAGE,
            },
            "sophistication": {
                "high_excitement": PersonalityArchetype.THE_MAGICIAN,
                "default": PersonalityArchetype.THE_LOVER,
            },
            "ruggedness": {
                "high_excitement": PersonalityArchetype.THE_OUTLAW,
                "default": PersonalityArchetype.THE_CREATOR,
            },
        }

        mapping = archetype_map.get(dominant, {"default": PersonalityArchetype.THE_EVERYMAN})

        # Check secondary conditions
        if dominant == "sincerity" and (self.warmth or 0) > 0.7:
            return mapping.get("high_secondary", mapping["default"])
        if dominant == "excitement" and self.ruggedness > 0.6:
            return mapping.get("high_ruggedness", mapping["default"])
        if dominant == "excitement" and self.sophistication > 0.6:
            return mapping.get("high_sophistication", mapping["default"])
        if dominant == "competence" and self.sophistication > 0.6:
            return mapping.get("high_sophistication", mapping["default"])
        if dominant == "sophistication" and self.excitement > 0.6:
            return mapping.get("high_excitement", mapping["default"])
        if dominant == "ruggedness" and self.excitement > 0.6:
            return mapping.get("high_excitement", mapping["default"])

        return mapping["default"]

    def get_design_implications(self) -> dict:
        """
        Translate personality dimensions into design guidelines.

        Returns design tokens and recommendations based on the
        brand personality profile.
        """
        implications = {
            "color_temperature": "neutral",
            "typography_weight": "regular",
            "corner_radius": "medium",
            "shadow_depth": "subtle",
            "animation_speed": "normal",
            "imagery_style": "realistic",
        }

        # Adjust based on dominant traits
        if self.sincerity > 0.7:
            implications["color_temperature"] = "warm"
            implications["corner_radius"] = "rounded"
            implications["imagery_style"] = "authentic"

        if self.excitement > 0.7:
            implications["color_temperature"] = "vibrant"
            implications["animation_speed"] = "dynamic"
            implications["shadow_depth"] = "dramatic"

        if self.competence > 0.7:
            implications["typography_weight"] = "medium"
            implications["corner_radius"] = "subtle"
            implications["imagery_style"] = "professional"

        if self.sophistication > 0.7:
            implications["color_temperature"] = "cool"
            implications["typography_weight"] = "light"
            implications["corner_radius"] = "sharp"
            implications["imagery_style"] = "editorial"

        if self.ruggedness > 0.7:
            implications["typography_weight"] = "bold"
            implications["corner_radius"] = "minimal"
            implications["shadow_depth"] = "strong"
            implications["imagery_style"] = "raw"

        return implications

    def to_tailwind_hints(self) -> dict:
        """
        Generate Tailwind CSS class hints based on personality.

        Returns recommended Tailwind utility classes that align
        with the brand personality.
        """
        hints = {
            "rounded": "rounded-lg",  # Default
            "shadow": "shadow-md",
            "font_weight": "font-medium",
            "text_size": "text-base",
            "spacing": "p-4",
        }

        if self.sincerity > 0.7:
            hints["rounded"] = "rounded-2xl"
            hints["shadow"] = "shadow-lg"

        if self.excitement > 0.7:
            hints["shadow"] = "shadow-xl"
            hints["font_weight"] = "font-bold"

        if self.competence > 0.7:
            hints["rounded"] = "rounded-md"
            hints["font_weight"] = "font-semibold"

        if self.sophistication > 0.7:
            hints["rounded"] = "rounded-sm"
            hints["font_weight"] = "font-light"
            hints["text_size"] = "text-lg"

        if self.ruggedness > 0.7:
            hints["rounded"] = "rounded-none"
            hints["font_weight"] = "font-black"

        return hints
