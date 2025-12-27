"""
ProjectSoul Model - The Core Design Intelligence

ProjectSoul is the central model that captures the complete "essence" of a
design project. It aggregates all extracted information from the design brief
and interview process, providing a unified context for design decisions.

The Soul drives:
- Dynamic question generation based on gaps
- Context-aware design recommendations
- Confidence-based decision making
- Agent prompt enhancement

Reference: This implements the "Soul-based Design" methodology for MAESTRO v2.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from gemini_mcp.maestro.models.audience import TargetAudience
from gemini_mcp.maestro.models.brand import BrandPersonality
from gemini_mcp.maestro.models.emotion import EmotionalFramework
from gemini_mcp.maestro.models.gap import GapAnalysis, GapCategory
from gemini_mcp.maestro.models.visual import VisualLanguage


class InterviewPhase(str, Enum):
    """
    Interview state machine phases.

    Note: Named InterviewPhase to avoid collision with existing InterviewState
    dataclass in maestro/models.py.
    """

    BRIEF_INGESTION = "brief_ingestion"  # Initial brief parsing
    SOUL_EXTRACTION = "soul_extraction"  # Extracting project soul
    CONTEXT_GATHERING = "context_gathering"  # Gathering additional context
    DEEP_DIVE = "deep_dive"  # Deep diving into specific areas
    VISUAL_EXPLORATION = "visual_exploration"  # Visual preferences
    VALIDATION = "validation"  # Validating understanding
    SYNTHESIS = "synthesis"  # Synthesizing final soul
    COMPLETE = "complete"  # Interview complete


class ConfidenceScores(BaseModel):
    """
    6-dimension confidence scoring for design decisions.

    Each dimension is scored 0.0-1.0, where:
    - < 0.3: Low confidence, needs more information
    - 0.3-0.6: Medium confidence, can proceed with defaults
    - 0.6-0.8: Good confidence, solid understanding
    - > 0.8: High confidence, comprehensive understanding
    """

    intent_clarity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Projenin amacı ne kadar net? (0-1)",
    )
    scope_match: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Kapsam tanımı ne kadar iyi? (0-1)",
    )
    context_richness: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Bağlam bilgisi ne kadar zengin? (0-1)",
    )
    parameter_completeness: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Tasarım parametreleri ne kadar tam? (0-1)",
    )
    constraint_satisfaction: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Kısıtlamalar ne kadar iyi anlaşıldı? (0-1)",
    )
    alternative_viability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Alternatif çözümler ne kadar değerlendirildi? (0-1)",
    )

    @property
    def overall(self) -> float:
        """Calculate weighted overall confidence score."""
        weights = {
            "intent_clarity": 0.25,  # Most important
            "scope_match": 0.20,
            "context_richness": 0.15,
            "parameter_completeness": 0.15,
            "constraint_satisfaction": 0.15,
            "alternative_viability": 0.10,
        }

        score = (
            self.intent_clarity * weights["intent_clarity"]
            + self.scope_match * weights["scope_match"]
            + self.context_richness * weights["context_richness"]
            + self.parameter_completeness * weights["parameter_completeness"]
            + self.constraint_satisfaction * weights["constraint_satisfaction"]
            + self.alternative_viability * weights["alternative_viability"]
        )

        return round(score, 3)

    @property
    def is_sufficient(self) -> bool:
        """Check if confidence is sufficient to proceed."""
        return self.overall >= 0.6 and self.intent_clarity >= 0.5

    @property
    def weakest_dimension(self) -> str:
        """Find the dimension with lowest confidence."""
        dimensions = {
            "intent_clarity": self.intent_clarity,
            "scope_match": self.scope_match,
            "context_richness": self.context_richness,
            "parameter_completeness": self.parameter_completeness,
            "constraint_satisfaction": self.constraint_satisfaction,
            "alternative_viability": self.alternative_viability,
        }
        return min(dimensions, key=dimensions.get)

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            "intent_clarity": self.intent_clarity,
            "scope_match": self.scope_match,
            "context_richness": self.context_richness,
            "parameter_completeness": self.parameter_completeness,
            "constraint_satisfaction": self.constraint_satisfaction,
            "alternative_viability": self.alternative_viability,
            "overall": self.overall,
        }


class ProjectMetadata(BaseModel):
    """Project-level metadata."""

    name: str = Field(
        default="Untitled Project",
        description="Proje adı",
    )
    tagline: Optional[str] = Field(
        default=None,
        description="Kısa slogan veya açıklama",
    )
    industry: Optional[str] = Field(
        default=None,
        description="Sektör (e-commerce, fintech, healthcare, vb.)",
    )
    project_type: Optional[str] = Field(
        default=None,
        description="Proje tipi (landing_page, dashboard, mobile_app, vb.)",
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Anahtar kelimeler",
    )
    competitors: List[str] = Field(
        default_factory=list,
        description="Rakip isimler/URL'ler",
    )


class ProjectConstraints(BaseModel):
    """Technical and business constraints."""

    # Technical
    target_platforms: List[str] = Field(
        default_factory=lambda: ["web"],
        description="Hedef platformlar (web, mobile, desktop)",
    )
    browser_support: List[str] = Field(
        default_factory=lambda: ["chrome", "firefox", "safari", "edge"],
        description="Desteklenecek tarayıcılar",
    )
    performance_budget: Optional[str] = Field(
        default=None,
        description="Performance budget (örn: 'LCP < 2.5s')",
    )

    # Accessibility
    wcag_level: str = Field(
        default="AA",
        description="WCAG uyumluluk seviyesi (A, AA, AAA)",
    )
    accessibility_requirements: List[str] = Field(
        default_factory=list,
        description="Özel erişilebilirlik gereksinimleri",
    )

    # Content
    supported_languages: List[str] = Field(
        default_factory=lambda: ["tr"],
        description="Desteklenecek diller",
    )
    rtl_support: bool = Field(
        default=False,
        description="RTL dil desteği gerekli mi?",
    )

    # Business
    deadline: Optional[str] = Field(
        default=None,
        description="Proje son tarihi (ISO format)",
    )
    budget_tier: Optional[str] = Field(
        default=None,
        description="Bütçe seviyesi (low, medium, high, enterprise)",
    )


class ProjectSoul(BaseModel):
    """
    The complete "soul" of a design project.

    This is the master model that aggregates all extracted information
    and provides a unified context for design decisions. It's the central
    data structure for MAESTRO v2.

    Example:
        >>> soul = ProjectSoul(
        ...     metadata=ProjectMetadata(name="TechCorp Landing Page"),
        ...     brand_personality=BrandPersonality(competence=0.9, sophistication=0.7),
        ...     target_audience=TargetAudience(persona_name="B2B Decision Maker"),
        ... )
        >>> soul.confidence_scores.overall
        0.5
        >>> soul.is_ready_for_design
        True
    """

    # Core identification
    id: str = Field(
        default_factory=lambda: f"soul_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        description="Benzersiz soul ID",
    )

    # Metadata
    metadata: ProjectMetadata = Field(
        default_factory=ProjectMetadata,
        description="Proje metadata",
    )

    # Core models
    brand_personality: BrandPersonality = Field(
        default_factory=BrandPersonality,
        description="Marka kişiliği (Aaker Framework)",
    )
    target_audience: TargetAudience = Field(
        default_factory=TargetAudience,
        description="Hedef kitle profili",
    )
    visual_language: VisualLanguage = Field(
        default_factory=VisualLanguage,
        description="Görsel dil sistemi",
    )
    emotional_framework: EmotionalFramework = Field(
        default_factory=EmotionalFramework,
        description="Duygusal çerçeve",
    )

    # Constraints
    constraints: ProjectConstraints = Field(
        default_factory=ProjectConstraints,
        description="Proje kısıtlamaları",
    )

    # Gap tracking
    gap_analysis: GapAnalysis = Field(
        default_factory=GapAnalysis,
        description="Eksik bilgi analizi",
    )

    # Confidence
    confidence_scores: ConfidenceScores = Field(
        default_factory=ConfidenceScores,
        description="Güven skorları",
    )

    # Interview state
    current_phase: InterviewPhase = Field(
        default=InterviewPhase.BRIEF_INGESTION,
        description="Mevcut mülakat fazı",
    )
    interview_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Soru-cevap geçmişi",
    )

    # Source tracking
    source_brief: Optional[str] = Field(
        default=None,
        description="Orijinal design brief metni",
    )
    extraction_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Soul çıkarım zamanı",
    )
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="Son güncelleme zamanı",
    )

    # Version tracking
    version: int = Field(
        default=1,
        ge=1,
        description="Soul versiyonu (her güncelleme +1)",
    )

    @property
    def is_ready_for_design(self) -> bool:
        """Check if soul has enough information to start design."""
        return (
            self.confidence_scores.is_sufficient
            and self.gap_analysis.blocking_gaps == 0
        )

    # =========================================================================
    # CONVENIENCE PROPERTIES (Shortcuts to nested fields)
    # =========================================================================

    @property
    def project_name(self) -> str:
        """Shortcut to metadata.name."""
        return self.metadata.name

    @property
    def tagline(self) -> Optional[str]:
        """Shortcut to metadata.tagline."""
        return self.metadata.tagline

    @property
    def industry(self) -> Optional[str]:
        """Shortcut to metadata.industry."""
        return self.metadata.industry

    @property
    def project_type(self) -> Optional[str]:
        """Shortcut to metadata.project_type."""
        return self.metadata.project_type

    @property
    def identified_gaps(self) -> List["GapInfo"]:
        """Shortcut to gap_analysis.gaps (backward compatibility)."""
        from gemini_mcp.maestro.models.gap import GapInfo
        return self.gap_analysis.gaps

    @property
    def completion_percentage(self) -> float:
        """Overall completion percentage based on gaps and confidence."""
        gap_completion = self.gap_analysis.completion_rate * 0.5
        confidence_score = self.confidence_scores.overall * 0.5
        return round((gap_completion + confidence_score) * 100, 1)

    def get_priority_gaps(self, limit: int = 5) -> List[str]:
        """Get top priority gaps that need resolution."""
        from gemini_mcp.maestro.models.gap import GapSeverity

        gaps = []
        for severity in [GapSeverity.CRITICAL, GapSeverity.HIGH, GapSeverity.MEDIUM]:
            severity_gaps = self.gap_analysis.get_gaps_by_severity(severity)
            for gap in severity_gaps:
                if not gap.is_resolved():
                    gaps.append(gap.id)
                    if len(gaps) >= limit:
                        return gaps
        return gaps

    def update_confidence_from_gaps(self) -> None:
        """Recalculate confidence scores based on gap analysis."""
        # Map gap categories to confidence dimensions
        category_dimension_map = {
            GapCategory.INTENT: "intent_clarity",
            GapCategory.SCOPE: "scope_match",
            GapCategory.CONTEXT: "context_richness",
            GapCategory.VISUAL: "parameter_completeness",
            GapCategory.TECHNICAL: "parameter_completeness",
            GapCategory.AUDIENCE: "context_richness",
            GapCategory.BRAND: "context_richness",
            GapCategory.EMOTIONAL: "parameter_completeness",
            GapCategory.CONTENT: "constraint_satisfaction",
            GapCategory.FUNCTIONAL: "scope_match",
        }

        # Calculate per-dimension scores
        dimension_scores = {
            "intent_clarity": [],
            "scope_match": [],
            "context_richness": [],
            "parameter_completeness": [],
            "constraint_satisfaction": [],
        }

        for gap in self.gap_analysis.gaps:
            dimension = category_dimension_map.get(gap.category)
            if dimension and dimension in dimension_scores:
                # Resolved gaps contribute positively
                score = 1.0 if gap.is_resolved() else 0.0
                dimension_scores[dimension].append(score)

        # Update confidence scores
        for dimension, scores in dimension_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                # Blend with existing score (80% gap-based, 20% existing)
                current = getattr(self.confidence_scores, dimension)
                new_score = avg_score * 0.8 + current * 0.2
                setattr(self.confidence_scores, dimension, round(new_score, 3))

        self.last_updated = datetime.now()
        self.version += 1

    def add_interview_response(
        self,
        question_id: str,
        response: str,
        gap_id: Optional[str] = None,
    ) -> None:
        """Record an interview response and update related gap."""
        self.interview_history.append({
            "question_id": question_id,
            "response": response,
            "gap_id": gap_id,
            "timestamp": datetime.now().isoformat(),
        })

        # Resolve the related gap
        if gap_id:
            for gap in self.gap_analysis.gaps:
                if gap.id == gap_id:
                    gap.resolve(response, source="user")
                    break

        self.update_confidence_from_gaps()

    def transition_phase(self, new_phase: InterviewPhase) -> bool:
        """
        Transition to a new interview phase.

        Returns True if transition is valid, False otherwise.
        """
        valid_transitions = {
            InterviewPhase.BRIEF_INGESTION: [InterviewPhase.SOUL_EXTRACTION],
            InterviewPhase.SOUL_EXTRACTION: [InterviewPhase.CONTEXT_GATHERING],
            InterviewPhase.CONTEXT_GATHERING: [
                InterviewPhase.DEEP_DIVE,
                InterviewPhase.VALIDATION,
            ],
            InterviewPhase.DEEP_DIVE: [
                InterviewPhase.VISUAL_EXPLORATION,
                InterviewPhase.VALIDATION,
            ],
            InterviewPhase.VISUAL_EXPLORATION: [InterviewPhase.VALIDATION],
            InterviewPhase.VALIDATION: [
                InterviewPhase.SYNTHESIS,
                InterviewPhase.DEEP_DIVE,  # Can go back if validation fails
            ],
            InterviewPhase.SYNTHESIS: [InterviewPhase.COMPLETE],
            InterviewPhase.COMPLETE: [],  # Terminal state
        }

        if new_phase in valid_transitions.get(self.current_phase, []):
            self.current_phase = new_phase
            self.last_updated = datetime.now()
            return True
        return False

    def to_agent_context(self) -> str:
        """
        Generate a comprehensive context string for AI agents.

        This context is injected into agent system prompts to provide
        soul-aware design capabilities.
        """
        sections = [
            "=" * 60,
            "PROJECT SOUL CONTEXT",
            "=" * 60,
            "",
            f"Project: {self.metadata.name}",
        ]

        if self.metadata.tagline:
            sections.append(f"Tagline: {self.metadata.tagline}")

        if self.metadata.industry:
            sections.append(f"Industry: {self.metadata.industry}")

        sections.append("")
        sections.append("-" * 40)
        sections.append("BRAND PERSONALITY (Aaker Framework)")
        sections.append("-" * 40)
        sections.append(f"Dominant: {self.brand_personality.dominant_trait}")
        sections.append(f"Archetype: {self.brand_personality.personality_archetype.value if self.brand_personality.personality_archetype else 'Unknown'}")
        sections.append(f"  Sincerity: {self.brand_personality.sincerity:.1%}")
        sections.append(f"  Excitement: {self.brand_personality.excitement:.1%}")
        sections.append(f"  Competence: {self.brand_personality.competence:.1%}")
        sections.append(f"  Sophistication: {self.brand_personality.sophistication:.1%}")
        sections.append(f"  Ruggedness: {self.brand_personality.ruggedness:.1%}")

        sections.append("")
        sections.append(self.target_audience.to_prompt_context())

        sections.append("")
        sections.append(self.visual_language.to_prompt_context())

        sections.append("")
        sections.append(self.emotional_framework.to_prompt_context())

        sections.append("")
        sections.append("-" * 40)
        sections.append("CONSTRAINTS")
        sections.append("-" * 40)
        sections.append(f"WCAG Level: {self.constraints.wcag_level}")
        sections.append(f"Languages: {', '.join(self.constraints.supported_languages)}")
        sections.append(f"Platforms: {', '.join(self.constraints.target_platforms)}")

        sections.append("")
        sections.append("-" * 40)
        sections.append("CONFIDENCE")
        sections.append("-" * 40)
        sections.append(f"Overall: {self.confidence_scores.overall:.1%}")
        sections.append(f"Ready for Design: {'Yes' if self.is_ready_for_design else 'No'}")
        sections.append(f"Completion: {self.completion_percentage}%")

        sections.append("")
        sections.append("=" * 60)

        return "\n".join(sections)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize soul to dictionary for storage.

        Returns a JSON-serializable dictionary.
        """
        return {
            "id": self.id,
            "metadata": self.metadata.model_dump(),
            "brand_personality": self.brand_personality.model_dump(),
            "target_audience": self.target_audience.model_dump(),
            "visual_language": self.visual_language.model_dump(),
            "emotional_framework": self.emotional_framework.model_dump(),
            "constraints": self.constraints.model_dump(),
            "confidence_scores": self.confidence_scores.to_dict(),
            "current_phase": self.current_phase.value,
            "gap_analysis": self.gap_analysis.to_summary(),
            "is_ready": self.is_ready_for_design,
            "completion": self.completion_percentage,
            "version": self.version,
            "extraction_timestamp": self.extraction_timestamp.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_brief(cls, brief: str, project_name: str = "Untitled") -> "ProjectSoul":
        """
        Create a minimal ProjectSoul from a design brief.

        This is a placeholder for the SoulExtractor which will do the
        actual NLP extraction. For now, just stores the brief.
        """
        soul = cls(
            metadata=ProjectMetadata(name=project_name),
            source_brief=brief,
            current_phase=InterviewPhase.BRIEF_INGESTION,
        )
        return soul
