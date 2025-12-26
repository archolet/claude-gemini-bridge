"""
MAESTRO Recommender - Phase 6.3 + Phase 7 DNA Integration

Provides intelligent recommendations and defaults based on:
- User preferences
- Project context
- Industry best practices
- Session history
- DNA history (Phase 7)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TYPE_CHECKING

from gemini_mcp.maestro.intelligence.adaptive_flow import AdaptiveFlow, FlowContext
from gemini_mcp.maestro.intelligence.preference_learner import (
    PreferenceLearner,
    PreferenceType,
)

if TYPE_CHECKING:
    from gemini_mcp.orchestration.dna_store import DNAStore


class RecommendationType(Enum):
    """Types of recommendations."""
    THEME = "theme"
    MODE = "mode"
    COMPONENT = "component"
    QUALITY = "quality"
    DEFAULT_VALUES = "default_values"
    WORKFLOW = "workflow"


@dataclass
class Recommendation:
    """A recommendation with reasoning."""
    recommendation_type: RecommendationType
    value: Any
    confidence: float
    reasoning: str
    alternatives: list[Any] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "type": self.recommendation_type.value,
            "value": self.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "alternatives": self.alternatives,
        }


# Industry-specific theme recommendations
INDUSTRY_THEME_MAP: dict[str, dict[str, Any]] = {
    "fintech": {
        "primary": "corporate",
        "alternatives": ["modern-minimal", "dark_mode_first"],
        "reasoning": "Fintech sektörü güven ve profesyonellik gerektirir",
    },
    "healthcare": {
        "primary": "soft-ui",
        "alternatives": ["modern-minimal", "high_contrast"],
        "reasoning": "Sağlık sektörü güvenilir ve erişilebilir tasarım ister",
    },
    "startup": {
        "primary": "gradient",
        "alternatives": ["modern-minimal", "neo-brutalism"],
        "reasoning": "Startuplar modern ve enerjik görünüm sever",
    },
    "e-commerce": {
        "primary": "modern-minimal",
        "alternatives": ["corporate", "pastel"],
        "reasoning": "E-ticaret temiz ve ürün odaklı tasarım gerektirir",
    },
    "gaming": {
        "primary": "cyberpunk",
        "alternatives": ["dark_mode_first", "neo-brutalism"],
        "reasoning": "Oyun sektörü cesur ve dinamik tasarımı sever",
    },
    "education": {
        "primary": "pastel",
        "alternatives": ["soft-ui", "modern-minimal"],
        "reasoning": "Eğitim sektörü dostça ve erişilebilir tasarım ister",
    },
}

# Component type recommendations based on purpose
PURPOSE_COMPONENT_MAP: dict[str, dict[str, Any]] = {
    "conversion": {
        "components": ["hero", "pricing_card", "cta", "testimonials"],
        "reasoning": "Dönüşüm odaklı sayfalar için en etkili componentler",
    },
    "information": {
        "components": ["features", "faq", "stats", "timeline"],
        "reasoning": "Bilgi aktarımı için ideal componentler",
    },
    "interaction": {
        "components": ["form", "chat_widget", "modal", "tabs"],
        "reasoning": "Kullanıcı etkileşimi için en uygun componentler",
    },
    "branding": {
        "components": ["hero", "navbar", "footer", "team"],
        "reasoning": "Marka kimliği oluşturmak için temel componentler",
    },
}

# Quality level recommendations
QUALITY_RECOMMENDATIONS: dict[str, dict[str, Any]] = {
    "prototype": {
        "level": "draft",
        "reasoning": "Hızlı prototip için draft kalite yeterli",
    },
    "mvp": {
        "level": "production",
        "reasoning": "MVP için production kalite ideal denge",
    },
    "production": {
        "level": "premium",
        "reasoning": "Canlıya çıkacak ürün için premium kalite önerilir",
    },
    "enterprise": {
        "level": "enterprise",
        "reasoning": "Kurumsal projeler için enterprise kalite şart",
    },
}


class Recommender:
    """
    Intelligent recommendation engine for MAESTRO.

    Combines multiple signals to provide smart recommendations:
    - User history (via PreferenceLearner)
    - Context analysis (via AdaptiveFlow)
    - Industry best practices
    - DNA history (via DNAStore - Phase 7)
    """

    def __init__(
        self,
        preference_learner: PreferenceLearner | None = None,
        adaptive_flow: AdaptiveFlow | None = None,
        dna_store: "DNAStore | None" = None,
    ) -> None:
        """
        Initialize recommender.

        Args:
            preference_learner: Optional preference learner instance
            adaptive_flow: Optional adaptive flow instance
            dna_store: Optional DNA store for historical recommendations (Phase 7)
        """
        self._learner = preference_learner or PreferenceLearner()
        self._flow = adaptive_flow or AdaptiveFlow()
        self._dna_store = dna_store
        self._context: FlowContext | None = None

    def set_context(self, context: FlowContext) -> None:
        """Set the context for recommendations."""
        self._context = context
        self._flow.set_context(context)

    def set_dna_store(self, dna_store: "DNAStore") -> None:
        """
        Set the DNA store for historical recommendations (Phase 7).

        Args:
            dna_store: DNAStore instance for accessing design history
        """
        self._dna_store = dna_store

    def recommend_theme(self) -> Recommendation:
        """
        Recommend a theme based on all available signals.

        Returns:
            Theme recommendation with reasoning
        """
        signals: list[tuple[str, float, str]] = []

        # Signal 1: User preference history
        user_pref = self._learner.get_preference(PreferenceType.THEME)
        if user_pref:
            signals.append((
                user_pref.value,
                user_pref.confidence * 0.4,  # 40% weight
                "Tercih geçmişinden"
            ))

        # Signal 2: Industry detection from context
        if self._context and self._context.project_context:
            industry = self._detect_industry(self._context.project_context)
            if industry and industry in INDUSTRY_THEME_MAP:
                rec = INDUSTRY_THEME_MAP[industry]
                signals.append((
                    rec["primary"],
                    0.7,  # 70% confidence for industry match
                    rec["reasoning"]
                ))

        # Signal 3 (Phase 7): DNA history from same project
        if self._dna_store and self._context and self._context.project_context:
            try:
                recent_entries = self._dna_store.search(
                    project_id=self._context.project_context,
                    limit=3,  # Look at last 3 designs
                )
                if recent_entries:
                    # Count theme occurrences
                    theme_counts: dict[str, int] = {}
                    for entry in recent_entries:
                        theme = entry.theme
                        theme_counts[theme] = theme_counts.get(theme, 0) + 1

                    # Get most used theme
                    if theme_counts:
                        most_used = max(theme_counts.items(), key=lambda x: x[1])
                        consistency_ratio = most_used[1] / len(recent_entries)
                        signals.append((
                            most_used[0],
                            0.6 * consistency_ratio,  # Up to 60% confidence
                            f"Proje geçmişinden ({most_used[1]}/{len(recent_entries)} tasarım)"
                        ))
            except Exception:
                # DNA store errors shouldn't break recommendations
                pass

        # Combine signals
        if not signals:
            # Default recommendation
            return Recommendation(
                recommendation_type=RecommendationType.THEME,
                value="modern-minimal",
                confidence=0.5,
                reasoning="Varsayılan olarak modern-minimal önerilir",
                alternatives=["corporate", "gradient"],
            )

        # Pick highest confidence signal
        signals.sort(key=lambda x: x[1], reverse=True)
        best = signals[0]

        # Get alternatives from industry map or defaults
        alternatives = ["modern-minimal", "corporate"]
        if self._context and self._context.project_context:
            industry = self._detect_industry(self._context.project_context)
            if industry and industry in INDUSTRY_THEME_MAP:
                alternatives = INDUSTRY_THEME_MAP[industry]["alternatives"]

        return Recommendation(
            recommendation_type=RecommendationType.THEME,
            value=best[0],
            confidence=best[1],
            reasoning=best[2],
            alternatives=alternatives,
        )

    def recommend_mode(self) -> Recommendation:
        """
        Recommend design mode (design_frontend, design_page, etc.).

        Returns:
            Mode recommendation
        """
        if not self._context:
            return Recommendation(
                recommendation_type=RecommendationType.MODE,
                value="design_frontend",
                confidence=0.5,
                reasoning="Bağlam olmadan component tasarımı önerilir",
                alternatives=["design_page", "design_section"],
            )

        context_lower = self._context.project_context.lower()

        # Check for page-level indicators
        page_keywords = ["landing", "dashboard", "auth", "login", "pricing", "page", "sayfa"]
        if any(kw in context_lower for kw in page_keywords):
            return Recommendation(
                recommendation_type=RecommendationType.MODE,
                value="design_page",
                confidence=0.8,
                reasoning="Sayfa düzeyinde tasarım gerekli görünüyor",
                alternatives=["design_section", "design_frontend"],
            )

        # Check for component indicators
        component_keywords = ["button", "card", "form", "modal", "navbar", "component", "buton"]
        if any(kw in context_lower for kw in component_keywords):
            return Recommendation(
                recommendation_type=RecommendationType.MODE,
                value="design_frontend",
                confidence=0.85,
                reasoning="Component düzeyinde tasarım uygun",
                alternatives=["design_page"],
            )

        # Check for existing HTML (refine mode)
        if self._context.existing_html:
            return Recommendation(
                recommendation_type=RecommendationType.MODE,
                value="refine_frontend",
                confidence=0.9,
                reasoning="Mevcut HTML var, iyileştirme modu önerilir",
                alternatives=["design_frontend"],
            )

        # Default
        return Recommendation(
            recommendation_type=RecommendationType.MODE,
            value="design_frontend",
            confidence=0.6,
            reasoning="Genel kullanım için component modu önerilir",
            alternatives=["design_page", "design_section"],
        )

    def recommend_quality(self) -> Recommendation:
        """
        Recommend quality level based on context.

        Returns:
            Quality recommendation
        """
        # Check user preference first
        user_pref = self._learner.get_preference(PreferenceType.QUALITY_LEVEL)
        if user_pref and user_pref.confidence > 0.7:
            return Recommendation(
                recommendation_type=RecommendationType.QUALITY,
                value=user_pref.value,
                confidence=user_pref.confidence,
                reasoning="Tercih geçmişinden",
                alternatives=["production", "premium"],
            )

        # Detect from context
        if self._context and self._context.project_context:
            context_lower = self._context.project_context.lower()

            for stage, rec in QUALITY_RECOMMENDATIONS.items():
                if stage in context_lower:
                    return Recommendation(
                        recommendation_type=RecommendationType.QUALITY,
                        value=rec["level"],
                        confidence=0.75,
                        reasoning=rec["reasoning"],
                        alternatives=["production", "premium"],
                    )

        # Default to production
        return Recommendation(
            recommendation_type=RecommendationType.QUALITY,
            value="production",
            confidence=0.6,
            reasoning="Varsayılan olarak production kalite önerilir",
            alternatives=["draft", "premium"],
        )

    def recommend_components(self, purpose: str = "") -> Recommendation:
        """
        Recommend components for a page based on purpose.

        Args:
            purpose: Page purpose (conversion, information, etc.)

        Returns:
            Component recommendations
        """
        purpose_lower = purpose.lower() if purpose else ""

        # Try to detect purpose from context if not provided
        if not purpose_lower and self._context:
            context_lower = self._context.project_context.lower()

            purpose_keywords = {
                "conversion": ["satış", "dönüşüm", "signup", "conversion", "cta"],
                "information": ["bilgi", "about", "hakkında", "info"],
                "interaction": ["form", "input", "chat", "iletişim", "contact"],
                "branding": ["marka", "brand", "tanıtım", "kurumsal"],
            }

            for p, keywords in purpose_keywords.items():
                if any(kw in context_lower for kw in keywords):
                    purpose_lower = p
                    break

        if purpose_lower in PURPOSE_COMPONENT_MAP:
            rec = PURPOSE_COMPONENT_MAP[purpose_lower]
            return Recommendation(
                recommendation_type=RecommendationType.COMPONENT,
                value=rec["components"],
                confidence=0.8,
                reasoning=rec["reasoning"],
                alternatives=[["hero", "features", "cta"]],
            )

        # Default recommendations
        return Recommendation(
            recommendation_type=RecommendationType.COMPONENT,
            value=["hero", "features", "cta", "footer"],
            confidence=0.6,
            reasoning="Genel sayfa yapısı için temel componentler",
            alternatives=[["navbar", "hero", "pricing", "footer"]],
        )

    def get_default_values(self) -> dict[str, Any]:
        """
        Get recommended default values for all parameters.

        Returns:
            Dictionary of recommended defaults
        """
        theme_rec = self.recommend_theme()
        quality_rec = self.recommend_quality()

        return {
            "theme": theme_rec.value,
            "quality_target": quality_rec.value,
            "dark_mode": True,
            "accessibility_level": "AA",
            "content_language": "tr",
            "micro_interactions": True,
            "use_trifecta": quality_rec.value in ["premium", "enterprise"],
        }

    def _detect_industry(self, context: str) -> str | None:
        """Detect industry from context text."""
        context_lower = context.lower()

        industry_keywords = {
            "fintech": ["fintech", "finance", "bank", "payment", "ödeme", "banka"],
            "healthcare": ["health", "medical", "hospital", "sağlık", "hastane"],
            "startup": ["startup", "girişim", "yeni", "innovative"],
            "e-commerce": ["e-commerce", "shop", "store", "mağaza", "ticaret", "satış"],
            "gaming": ["game", "oyun", "gaming", "esport"],
            "education": ["education", "eğitim", "school", "okul", "course", "kurs"],
        }

        for industry, keywords in industry_keywords.items():
            if any(kw in context_lower for kw in keywords):
                return industry

        return None

    def get_all_recommendations(self) -> dict[str, Any]:
        """
        Get all recommendations at once.

        Returns:
            Dictionary with all recommendation types
        """
        return {
            "theme": self.recommend_theme().to_dict(),
            "mode": self.recommend_mode().to_dict(),
            "quality": self.recommend_quality().to_dict(),
            "defaults": self.get_default_values(),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert recommender state to dictionary."""
        return {
            "has_context": self._context is not None,
            "learner_state": self._learner.to_dict(),
        }
