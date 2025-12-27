"""
MAESTRO Data Models

Combined module containing:
- Legacy dataclasses (MaestroSession, Question, Answer, etc.) for backward compatibility
- V2 Pydantic models (ProjectSoul, BrandPersonality, etc.) for intelligent interview system

Model Hierarchy (V2):
    ProjectSoul (master)
    ├── ProjectMetadata
    ├── BrandPersonality (Aaker Framework)
    │   └── PersonalityArchetype (Jungian)
    ├── TargetAudience
    │   ├── DemographicProfile
    │   └── PsychographicProfile
    ├── VisualLanguage
    │   ├── ColorPalette
    │   └── TypographyStyle
    ├── EmotionalFramework (Plutchik)
    │   └── EmotionMapping
    ├── ProjectConstraints
    ├── GapAnalysis
    │   └── GapInfo
    └── ConfidenceScores

Usage:
    # Legacy models
    >>> from gemini_mcp.maestro.models import MaestroSession, MaestroStatus
    >>> session = MaestroSession(session_id="abc123")

    # V2 models
    >>> from gemini_mcp.maestro.models import ProjectSoul, BrandPersonality
    >>> soul = ProjectSoul.from_brief("Design a modern fintech dashboard...")
    >>> soul.brand_personality.dominant_trait
    'competence'
"""

# =============================================================================
# LEGACY MODELS (Backward Compatibility)
# =============================================================================
from gemini_mcp.maestro.models_legacy import (
    # Enums
    MaestroStatus,
    QuestionCategory,
    QuestionType,
    # Question dataclasses
    QuestionOption,
    Question,
    Answer,
    # State dataclasses
    InterviewState,
    ContextData,
    ProjectInfo,
    # Session
    MaestroSession,
    # Decision
    MaestroDecision,
    # Validation
    ValidationResult,
    AnswerResult,
)

# =============================================================================
# V2 MODELS (Soul-based Design)
# =============================================================================

# Brand Personality (Aaker Framework)
from gemini_mcp.maestro.models.brand import (
    BrandPersonality,
    PersonalityArchetype,
)

# Target Audience
from gemini_mcp.maestro.models.audience import (
    TargetAudience,
    DemographicProfile,
    PsychographicProfile,
    GenerationCohort,
    TechSavviness,
    DevicePreference,
)

# Visual Language
from gemini_mcp.maestro.models.visual import (
    VisualLanguage,
    ColorPalette,
    TypographyStyle,
    ColorHarmony,
    ColorTemperature,
    TypographyScale,
    FontCategory,
    SpacingDensity,
)

# Emotional Framework (Plutchik)
from gemini_mcp.maestro.models.emotion import (
    EmotionalFramework,
    EmotionMapping,
    PrimaryEmotion,
    EmotionIntensity,
    EmotionalTone,
)

# Gap Analysis
from gemini_mcp.maestro.models.gap import (
    GapInfo,
    GapCategory,
    GapSeverity,
    GapResolutionStatus,
    GapAnalysis,
)

# Project Soul (Master Model)
from gemini_mcp.maestro.models.soul import (
    ProjectSoul,
    InterviewPhase,
    ConfidenceScores,
    ProjectMetadata,
    ProjectConstraints,
)


__all__ = [
    # ==========================================================================
    # LEGACY MODELS (Backward Compatibility)
    # ==========================================================================
    # Enums
    "MaestroStatus",
    "QuestionCategory",
    "QuestionType",
    # Question dataclasses
    "QuestionOption",
    "Question",
    "Answer",
    # State dataclasses
    "InterviewState",
    "ContextData",
    "ProjectInfo",
    # Session
    "MaestroSession",
    # Decision
    "MaestroDecision",
    # Validation
    "ValidationResult",
    "AnswerResult",
    # ==========================================================================
    # V2 MODELS (Soul-based Design)
    # ==========================================================================
    # === Core Soul ===
    "ProjectSoul",
    "InterviewPhase",
    "ConfidenceScores",
    "ProjectMetadata",
    "ProjectConstraints",
    # === Brand ===
    "BrandPersonality",
    "PersonalityArchetype",
    # === Audience ===
    "TargetAudience",
    "DemographicProfile",
    "PsychographicProfile",
    "GenerationCohort",
    "TechSavviness",
    "DevicePreference",
    # === Visual ===
    "VisualLanguage",
    "ColorPalette",
    "TypographyStyle",
    "ColorHarmony",
    "ColorTemperature",
    "TypographyScale",
    "FontCategory",
    "SpacingDensity",
    # === Emotion ===
    "EmotionalFramework",
    "EmotionMapping",
    "PrimaryEmotion",
    "EmotionIntensity",
    "EmotionalTone",
    # === Gap ===
    "GapInfo",
    "GapCategory",
    "GapSeverity",
    "GapResolutionStatus",
    "GapAnalysis",
]
