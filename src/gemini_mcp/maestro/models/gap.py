"""
Gap Info Model - Missing Information Detection

Tracks gaps and missing information during the interview process.
Used by MAESTRO to generate targeted follow-up questions.

Categories:
- INTENT: What the user wants to achieve
- SCOPE: What's included/excluded
- CONTEXT: Background and constraints
- VISUAL: Design preferences
- TECHNICAL: Implementation requirements
- CONTENT: Text, images, data
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class GapCategory(str, Enum):
    """
    Categories of missing information.

    Each category corresponds to a different aspect of the design brief
    and triggers different question types.
    """

    INTENT = "intent"  # What is the goal? What problem are we solving?
    SCOPE = "scope"  # What's in/out? Boundaries and limits
    CONTEXT = "context"  # Background, industry, competition
    VISUAL = "visual"  # Colors, typography, imagery preferences
    TECHNICAL = "technical"  # Platform, performance, accessibility
    CONTENT = "content"  # Text, data, media assets
    AUDIENCE = "audience"  # Who is the target user?
    BRAND = "brand"  # Brand personality, values, voice
    EMOTIONAL = "emotional"  # Desired emotional response
    FUNCTIONAL = "functional"  # Features, interactions, workflows


class GapSeverity(str, Enum):
    """
    Severity levels for missing information.

    Determines priority for follow-up questions and impacts
    the overall confidence score.
    """

    CRITICAL = "critical"  # Cannot proceed without this (blocks design)
    HIGH = "high"  # Significantly impacts quality
    MEDIUM = "medium"  # Would improve the design
    LOW = "low"  # Nice to have, defaults available


class GapResolutionStatus(str, Enum):
    """Status of gap resolution."""

    OPEN = "open"  # Not yet addressed
    PENDING = "pending"  # Question asked, awaiting answer
    RESOLVED = "resolved"  # Answered by user
    INFERRED = "inferred"  # Auto-filled from context
    DEFAULTED = "defaulted"  # Used reasonable default


class GapInfo(BaseModel):
    """
    Represents a gap in the design brief - missing or incomplete information.

    MAESTRO uses this to:
    1. Track what information is missing
    2. Prioritize questions during the interview
    3. Calculate overall confidence scores
    4. Determine when enough info is gathered

    Example:
        >>> gap = GapInfo(
        ...     id="gap_color_preference",
        ...     category=GapCategory.VISUAL,
        ...     severity=GapSeverity.MEDIUM,
        ...     description="Primary brand color not specified",
        ...     suggested_question="What is your brand's primary color? (hex code or color name)",
        ... )
    """

    # Identification
    id: str = Field(
        description="Benzersiz gap ID (örn: 'gap_target_audience')",
    )
    category: GapCategory = Field(
        description="Gap kategorisi",
    )
    severity: GapSeverity = Field(
        default=GapSeverity.MEDIUM,
        description="Gap şiddeti/önemi",
    )

    # Description
    description: str = Field(
        description="Eksik bilginin açıklaması",
    )
    detail: Optional[str] = Field(
        default=None,
        description="Ek detaylar (neden önemli, ne etkilenir)",
    )

    # Resolution
    status: GapResolutionStatus = Field(
        default=GapResolutionStatus.OPEN,
        description="Çözüm durumu",
    )
    resolution_value: Optional[str] = Field(
        default=None,
        description="Çözüm değeri (kullanıcı cevabı veya çıkarım)",
    )
    resolution_source: Optional[str] = Field(
        default=None,
        description="Çözüm kaynağı (user, inference, default)",
    )

    # Question generation
    suggested_question: Optional[str] = Field(
        default=None,
        description="Bu gap'i kapatmak için önerilen soru (Türkçe)",
    )
    question_options: List[str] = Field(
        default_factory=list,
        description="Çoktan seçmeli soru için seçenekler",
    )
    allows_free_text: bool = Field(
        default=True,
        description="Serbest metin girişine izin ver",
    )

    # Default handling
    default_value: Optional[str] = Field(
        default=None,
        description="Varsayılan değer (cevap alınamazsa)",
    )
    default_reasoning: Optional[str] = Field(
        default=None,
        description="Varsayılan değer gerekçesi",
    )

    # Dependencies
    depends_on: List[str] = Field(
        default_factory=list,
        description="Bu gap'in çözümü için gereken diğer gap ID'leri",
    )
    blocks: List[str] = Field(
        default_factory=list,
        description="Bu gap çözülmeden sorulmaması gereken gap ID'leri",
    )

    # Confidence impact
    confidence_impact: float = Field(
        default=0.1,
        ge=0.0,
        le=0.5,
        description="Bu gap'in çözülmemesi halinde güven etkisi (0-0.5)",
    )

    # Priority for question ordering (higher = asked first)
    priority: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Soru önceliği (0-100, yüksek = önce sorulur)",
    )

    def is_blocking(self) -> bool:
        """Check if this gap blocks progress."""
        return self.severity == GapSeverity.CRITICAL and self.status == GapResolutionStatus.OPEN

    def is_resolved(self) -> bool:
        """Check if this gap has been resolved."""
        return self.status in [
            GapResolutionStatus.RESOLVED,
            GapResolutionStatus.INFERRED,
            GapResolutionStatus.DEFAULTED,
        ]

    def resolve(self, value: str, source: str = "user") -> None:
        """
        Mark this gap as resolved with the given value.

        Args:
            value: The resolution value
            source: Where the resolution came from (user, inference, default)
        """
        self.resolution_value = value
        self.resolution_source = source

        if source == "user":
            self.status = GapResolutionStatus.RESOLVED
        elif source == "inference":
            self.status = GapResolutionStatus.INFERRED
        else:
            self.status = GapResolutionStatus.DEFAULTED

    def apply_default(self) -> bool:
        """
        Apply the default value if available.

        Returns True if default was applied, False otherwise.
        """
        if self.default_value and not self.is_resolved():
            self.resolve(self.default_value, source="default")
            return True
        return False

    def to_question_dict(self) -> dict:
        """
        Convert to a question dictionary for the interview system.

        Returns a dict compatible with the Question model.
        """
        return {
            "id": self.id,
            "text": self.suggested_question or f"Please provide: {self.description}",
            "category": self.category.value,
            "options": self.question_options if self.question_options else None,
            "allows_free_text": self.allows_free_text,
            "priority": {
                GapSeverity.CRITICAL: 1,
                GapSeverity.HIGH: 2,
                GapSeverity.MEDIUM: 3,
                GapSeverity.LOW: 4,
            }.get(self.severity, 3),
        }


class GapAnalysis(BaseModel):
    """
    Complete gap analysis for a design brief.

    Aggregates all identified gaps and provides summary statistics.

    Example:
        >>> analysis = GapAnalysis(gaps=[gap1, gap2, gap3])
        >>> analysis.completion_rate
        0.33
    """

    gaps: List[GapInfo] = Field(
        default_factory=list,
        description="Tespit edilen tüm gap'ler",
    )
    analysis_timestamp: Optional[str] = Field(
        default=None,
        description="Analiz zamanı (ISO format)",
    )
    source_brief_hash: Optional[str] = Field(
        default=None,
        description="Kaynak brief hash'i (değişiklik takibi için)",
    )

    @property
    def total_gaps(self) -> int:
        """Total number of gaps."""
        return len(self.gaps)

    @property
    def open_gaps(self) -> int:
        """Number of unresolved gaps."""
        return len([g for g in self.gaps if not g.is_resolved()])

    @property
    def blocking_gaps(self) -> int:
        """Number of blocking (critical + open) gaps."""
        return len([g for g in self.gaps if g.is_blocking()])

    @property
    def completion_rate(self) -> float:
        """Percentage of resolved gaps (0.0 - 1.0)."""
        if not self.gaps:
            return 1.0
        resolved = len([g for g in self.gaps if g.is_resolved()])
        return resolved / len(self.gaps)

    @property
    def confidence_penalty(self) -> float:
        """Total confidence penalty from unresolved gaps."""
        return sum(g.confidence_impact for g in self.gaps if not g.is_resolved())

    @property
    def all_gaps(self) -> List[GapInfo]:
        """Alias for gaps property (backward compatibility)."""
        return self.gaps

    @property
    def critical_gaps(self) -> List[GapInfo]:
        """Get all critical severity gaps."""
        return self.get_gaps_by_severity(GapSeverity.CRITICAL)

    @property
    def high_gaps(self) -> List[GapInfo]:
        """Get all high severity gaps."""
        return self.get_gaps_by_severity(GapSeverity.HIGH)

    def get_priority_queue(self) -> List[GapInfo]:
        """
        Get gaps sorted by priority (severity first, then by priority field).

        Returns gaps in order: CRITICAL → HIGH → MEDIUM → LOW,
        with higher priority values first within each severity level.
        """
        severity_order = {
            GapSeverity.CRITICAL: 0,
            GapSeverity.HIGH: 1,
            GapSeverity.MEDIUM: 2,
            GapSeverity.LOW: 3,
        }
        return sorted(
            self.gaps,
            key=lambda g: (severity_order.get(g.severity, 2), -getattr(g, 'priority', 50))
        )

    def get_gaps_by_category(self, category: GapCategory) -> List[GapInfo]:
        """Get all gaps in a specific category."""
        return [g for g in self.gaps if g.category == category]

    def get_gaps_by_severity(self, severity: GapSeverity) -> List[GapInfo]:
        """Get all gaps with a specific severity."""
        return [g for g in self.gaps if g.severity == severity]

    def get_next_question(self) -> Optional[GapInfo]:
        """
        Get the next gap to ask about.

        Priority:
        1. Critical unresolved gaps
        2. High severity unresolved gaps with no dependencies
        3. Medium severity gaps
        4. Low severity gaps
        """
        open_gaps = [g for g in self.gaps if g.status == GapResolutionStatus.OPEN]

        if not open_gaps:
            return None

        # Sort by severity priority
        severity_order = {
            GapSeverity.CRITICAL: 0,
            GapSeverity.HIGH: 1,
            GapSeverity.MEDIUM: 2,
            GapSeverity.LOW: 3,
        }

        # Filter out gaps with unresolved dependencies
        resolved_ids = {g.id for g in self.gaps if g.is_resolved()}
        available_gaps = [
            g for g in open_gaps
            if all(dep in resolved_ids for dep in g.depends_on)
        ]

        if not available_gaps:
            # Fall back to any open gap if all have dependencies
            available_gaps = open_gaps

        # Sort by severity
        available_gaps.sort(key=lambda g: severity_order.get(g.severity, 2))

        return available_gaps[0] if available_gaps else None

    def apply_all_defaults(self) -> int:
        """
        Apply default values to all unresolved gaps that have defaults.

        Returns the number of gaps defaulted.
        """
        count = 0
        for gap in self.gaps:
            if gap.apply_default():
                count += 1
        return count

    def to_summary(self) -> dict:
        """
        Generate a summary dictionary.

        Returns stats and status overview for the gap analysis.
        """
        by_category = {}
        for category in GapCategory:
            gaps = self.get_gaps_by_category(category)
            if gaps:
                by_category[category.value] = {
                    "total": len(gaps),
                    "resolved": len([g for g in gaps if g.is_resolved()]),
                }

        by_severity = {}
        for severity in GapSeverity:
            gaps = self.get_gaps_by_severity(severity)
            if gaps:
                by_severity[severity.value] = {
                    "total": len(gaps),
                    "resolved": len([g for g in gaps if g.is_resolved()]),
                }

        return {
            "total_gaps": self.total_gaps,
            "open_gaps": self.open_gaps,
            "blocking_gaps": self.blocking_gaps,
            "completion_rate": round(self.completion_rate, 2),
            "confidence_penalty": round(self.confidence_penalty, 3),
            "by_category": by_category,
            "by_severity": by_severity,
        }
