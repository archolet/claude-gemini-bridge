"""
Target Audience Model - Demographic & Psychographic Profiling

Captures the intended audience for design decisions, including:
- Demographics: Age, location, profession, income level
- Psychographics: Values, motivations, pain points, aspirations

Reference: Marketing persona frameworks + UX research best practices.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class GenerationCohort(str, Enum):
    """Generational cohorts with distinct digital behaviors."""

    GEN_ALPHA = "gen_alpha"  # 2013+ - AI natives
    GEN_Z = "gen_z"  # 1997-2012 - Mobile-first, short attention
    MILLENNIAL = "millennial"  # 1981-1996 - Digital adopters
    GEN_X = "gen_x"  # 1965-1980 - Desktop era
    BOOMER = "boomer"  # 1946-1964 - Late digital adopters
    SILENT = "silent"  # 1928-1945 - Traditional


class TechSavviness(str, Enum):
    """User's comfort level with technology."""

    EXPERT = "expert"  # Power users, developers
    ADVANCED = "advanced"  # Comfortable with complex UIs
    INTERMEDIATE = "intermediate"  # Typical user
    BASIC = "basic"  # Needs guidance
    NOVICE = "novice"  # Requires maximum simplicity


class DevicePreference(str, Enum):
    """Primary device usage patterns."""

    MOBILE_FIRST = "mobile_first"  # Smartphone primary
    DESKTOP_FIRST = "desktop_first"  # Laptop/Desktop primary
    TABLET_HEAVY = "tablet_heavy"  # iPad/Tablet primary
    MULTI_DEVICE = "multi_device"  # Equal across devices
    SMART_TV = "smart_tv"  # Large screen experiences


class DemographicProfile(BaseModel):
    """
    Demographic characteristics of the target audience.

    Example:
        >>> demo = DemographicProfile(
        ...     age_range=(25, 45),
        ...     primary_location="Turkey",
        ...     profession_category="Technology",
        ... )
    """

    # Age characteristics
    age_range: tuple[int, int] = Field(
        default=(18, 65),
        description="Yaş aralığı (min, max)",
    )
    generation: Optional[GenerationCohort] = Field(
        default=None,
        description="Kuşak kategorisi (Gen Z, Millennial, vb.)",
    )

    # Location
    primary_location: str = Field(
        default="Turkey",
        description="Birincil hedef bölge/ülke",
    )
    secondary_locations: List[str] = Field(
        default_factory=list,
        description="İkincil hedef bölgeler",
    )
    is_urban: bool = Field(
        default=True,
        description="Kentsel mi kırsal mı hedef kitle",
    )

    # Professional context
    profession_category: Optional[str] = Field(
        default=None,
        description="Meslek kategorisi (Teknoloji, Sağlık, Finans, vb.)",
    )
    income_level: Optional[str] = Field(
        default=None,
        description="Gelir seviyesi (low, medium, high, premium)",
    )
    education_level: Optional[str] = Field(
        default=None,
        description="Eğitim seviyesi (high_school, bachelor, master, phd)",
    )

    # Digital behavior
    tech_savviness: TechSavviness = Field(
        default=TechSavviness.INTERMEDIATE,
        description="Teknoloji yetkinlik seviyesi",
    )
    device_preference: DevicePreference = Field(
        default=DevicePreference.MOBILE_FIRST,
        description="Birincil cihaz tercihi",
    )

    def model_post_init(self, __context) -> None:
        """Auto-infer generation from age range if not set."""
        if self.generation is None:
            avg_age = (self.age_range[0] + self.age_range[1]) // 2
            birth_year = 2024 - avg_age

            if birth_year >= 2013:
                self.generation = GenerationCohort.GEN_ALPHA
            elif birth_year >= 1997:
                self.generation = GenerationCohort.GEN_Z
            elif birth_year >= 1981:
                self.generation = GenerationCohort.MILLENNIAL
            elif birth_year >= 1965:
                self.generation = GenerationCohort.GEN_X
            elif birth_year >= 1946:
                self.generation = GenerationCohort.BOOMER
            else:
                self.generation = GenerationCohort.SILENT

    def get_design_recommendations(self) -> dict:
        """
        Generate design recommendations based on demographics.

        Returns design guidelines tailored to the demographic profile.
        """
        recommendations = {
            "font_size_base": "16px",
            "touch_target_min": "44px",
            "animation_preference": "normal",
            "information_density": "medium",
            "onboarding_depth": "standard",
        }

        # Age-based adjustments
        avg_age = (self.age_range[0] + self.age_range[1]) // 2
        if avg_age > 50:
            recommendations["font_size_base"] = "18px"
            recommendations["touch_target_min"] = "48px"
            recommendations["animation_preference"] = "reduced"

        # Tech savviness adjustments
        if self.tech_savviness == TechSavviness.NOVICE:
            recommendations["information_density"] = "low"
            recommendations["onboarding_depth"] = "comprehensive"
        elif self.tech_savviness == TechSavviness.EXPERT:
            recommendations["information_density"] = "high"
            recommendations["onboarding_depth"] = "minimal"

        # Device preference adjustments
        if self.device_preference == DevicePreference.MOBILE_FIRST:
            recommendations["touch_target_min"] = "48px"
            recommendations["priority_breakpoint"] = "sm"
        elif self.device_preference == DevicePreference.DESKTOP_FIRST:
            recommendations["priority_breakpoint"] = "lg"

        return recommendations


class PsychographicProfile(BaseModel):
    """
    Psychographic characteristics - the "why" behind user behavior.

    Captures values, motivations, pain points, and aspirations that
    drive design decisions beyond demographics.

    Example:
        >>> psycho = PsychographicProfile(
        ...     core_values=["efficiency", "trust", "innovation"],
        ...     primary_motivation="saving_time",
        ...     pain_points=["slow loading", "complex navigation"],
        ... )
    """

    # Values and beliefs
    core_values: List[str] = Field(
        default_factory=list,
        description="Temel değerler (güven, yenilik, sürdürülebilirlik, vb.)",
    )
    brand_affinity: Optional[str] = Field(
        default=None,
        description="Benzer marka tercihleri (Apple-like, Google-like, vb.)",
    )

    # Motivations
    primary_motivation: Optional[str] = Field(
        default=None,
        description="Birincil motivasyon (saving_time, saving_money, status, vb.)",
    )
    secondary_motivations: List[str] = Field(
        default_factory=list,
        description="İkincil motivasyonlar",
    )

    # Pain points and frustrations
    pain_points: List[str] = Field(
        default_factory=list,
        description="Mevcut sorunlar ve hayal kırıklıkları",
    )
    deal_breakers: List[str] = Field(
        default_factory=list,
        description="Kesinlikle kabul edilemez özellikler",
    )

    # Aspirations
    aspirations: List[str] = Field(
        default_factory=list,
        description="Hedefler ve hayaller",
    )
    success_metrics: List[str] = Field(
        default_factory=list,
        description="Başarı kriterleri (user perspective)",
    )

    # Behavioral patterns
    decision_style: Optional[str] = Field(
        default=None,
        description="Karar verme stili (analytical, impulsive, consensus, vb.)",
    )
    risk_tolerance: Optional[str] = Field(
        default=None,
        description="Risk toleransı (low, medium, high)",
    )

    def get_ux_priorities(self) -> dict:
        """
        Map psychographic traits to UX priorities.

        Returns a weighted priority list for UX decisions.
        """
        priorities = {
            "speed": 0.5,
            "simplicity": 0.5,
            "trust_signals": 0.5,
            "social_proof": 0.5,
            "customization": 0.5,
            "guidance": 0.5,
        }

        # Value-based adjustments
        if "efficiency" in self.core_values or "hız" in self.core_values:
            priorities["speed"] = 0.9

        if "trust" in self.core_values or "güven" in self.core_values:
            priorities["trust_signals"] = 0.9

        if "simplicity" in self.core_values or "sadelik" in self.core_values:
            priorities["simplicity"] = 0.9

        # Motivation-based adjustments
        if self.primary_motivation == "saving_time":
            priorities["speed"] = max(priorities["speed"], 0.8)
            priorities["simplicity"] = max(priorities["simplicity"], 0.7)

        if self.primary_motivation == "status":
            priorities["customization"] = 0.8
            priorities["social_proof"] = 0.3  # Less reliance on others

        # Risk tolerance adjustments
        if self.risk_tolerance == "low":
            priorities["trust_signals"] = max(priorities["trust_signals"], 0.8)
            priorities["guidance"] = 0.8

        return priorities


class TargetAudience(BaseModel):
    """
    Complete target audience profile combining demographics and psychographics.

    This is the primary model used by MAESTRO for audience-aware design decisions.

    Example:
        >>> audience = TargetAudience(
        ...     persona_name="Tech-Savvy Professional",
        ...     demographic=DemographicProfile(
        ...         age_range=(28, 42),
        ...         profession_category="Technology",
        ...         tech_savviness=TechSavviness.ADVANCED,
        ...     ),
        ...     psychographic=PsychographicProfile(
        ...         core_values=["efficiency", "innovation"],
        ...         primary_motivation="saving_time",
        ...     ),
        ... )
        >>> audience.accessibility_level
        'standard'
    """

    # Persona identification
    persona_name: str = Field(
        default="Primary User",
        description="Persona adı (örn: 'Tech-Savvy Professional')",
    )
    persona_description: Optional[str] = Field(
        default=None,
        description="Persona'nın kısa tanımı",
    )

    # Profiles
    demographic: DemographicProfile = Field(
        default_factory=DemographicProfile,
        description="Demografik profil",
    )
    psychographic: PsychographicProfile = Field(
        default_factory=PsychographicProfile,
        description="Psikografik profil",
    )

    # Accessibility needs
    accessibility_level: str = Field(
        default="standard",
        description="Erişilebilirlik seviyesi: minimal, standard, enhanced, maximum",
    )
    special_needs: List[str] = Field(
        default_factory=list,
        description="Özel ihtiyaçlar (screen_reader, color_blind, motor_impairment, vb.)",
    )

    # Language and locale
    primary_language: str = Field(
        default="tr",
        description="Birincil dil kodu (ISO 639-1)",
    )
    content_preferences: List[str] = Field(
        default_factory=list,
        description="İçerik tercihleri (formal, casual, technical, vb.)",
    )

    # Confidence
    profile_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Profil güvenilirlik skoru",
    )

    def model_post_init(self, __context) -> None:
        """Auto-determine accessibility level based on demographics."""
        if self.accessibility_level == "standard":
            # Auto-enhance for older users or those with special needs
            avg_age = (
                self.demographic.age_range[0] + self.demographic.age_range[1]
            ) // 2
            if avg_age > 60 or self.special_needs:
                self.accessibility_level = "enhanced"

    def get_combined_recommendations(self) -> dict:
        """
        Merge demographic and psychographic recommendations.

        Returns comprehensive design guidelines for this audience.
        """
        demo_recs = self.demographic.get_design_recommendations()
        psycho_priorities = self.psychographic.get_ux_priorities()

        return {
            **demo_recs,
            "ux_priorities": psycho_priorities,
            "accessibility_level": self.accessibility_level,
            "special_needs": self.special_needs,
            "language": self.primary_language,
            "content_tone": (
                self.content_preferences[0]
                if self.content_preferences
                else "professional"
            ),
        }

    def to_prompt_context(self) -> str:
        """
        Generate a prompt-ready context string for AI agents.

        Returns a formatted string suitable for inclusion in system prompts.
        """
        lines = [
            f"Target Audience: {self.persona_name}",
            f"Age Range: {self.demographic.age_range[0]}-{self.demographic.age_range[1]}",
            f"Generation: {self.demographic.generation.value if self.demographic.generation else 'Unknown'}",
            f"Tech Level: {self.demographic.tech_savviness.value}",
            f"Device: {self.demographic.device_preference.value}",
            f"Accessibility: {self.accessibility_level}",
        ]

        if self.psychographic.core_values:
            lines.append(f"Values: {', '.join(self.psychographic.core_values[:3])}")

        if self.psychographic.primary_motivation:
            lines.append(f"Primary Goal: {self.psychographic.primary_motivation}")

        return "\n".join(lines)
