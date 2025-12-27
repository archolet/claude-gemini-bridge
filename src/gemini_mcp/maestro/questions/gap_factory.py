"""
MAESTRO Gap-Based Question Factory - Phase 3

Creates Question objects from GapInfo instances.
This is the bridge between gap analysis and the interview system.

The factory:
1. Converts GapInfo → Question with appropriate type and options
2. Maps GapCategory → QuestionCategory
3. Maps GapSeverity → Question priority
4. Generates smart options based on gap context

Usage:
    >>> from gemini_mcp.maestro.questions.gap_factory import GapBasedQuestionFactory
    >>> factory = GapBasedQuestionFactory()
    >>> gap = GapInfo(id="gap_color", category=GapCategory.VISUAL, ...)
    >>> question = factory.create_question(gap)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional

from gemini_mcp.maestro.models import (
    Question,
    QuestionCategory,
    QuestionOption,
    QuestionType,
)
from gemini_mcp.maestro.models.gap import (
    GapCategory,
    GapInfo,
    GapSeverity,
)

if TYPE_CHECKING:
    from gemini_mcp.maestro.models.soul import ProjectSoul

logger = logging.getLogger(__name__)


class GapBasedQuestionFactory:
    """
    Creates Question objects from GapInfo.

    This factory bridges the gap analysis system with the interview system,
    converting detected gaps into askable questions.

    Features:
    - Smart category mapping
    - Severity-based priority assignment
    - Context-aware option generation
    - Turkish and English question support

    Example:
        >>> factory = GapBasedQuestionFactory()
        >>> gap = GapInfo(
        ...     id="gap_audience",
        ...     category=GapCategory.AUDIENCE,
        ...     severity=GapSeverity.CRITICAL,
        ...     description="Target audience not specified",
        ...     suggested_question="Bu tasarımın hedef kitlesi kimdir?",
        ... )
        >>> question = factory.create_question(gap)
        >>> question.id
        'q_gap_audience'
    """

    # =========================================================================
    # CATEGORY MAPPING
    # =========================================================================

    # Map GapCategory → QuestionCategory
    CATEGORY_MAP: ClassVar[Dict[GapCategory, QuestionCategory]] = {
        GapCategory.INTENT: QuestionCategory.INTENT,
        GapCategory.SCOPE: QuestionCategory.SCOPE,
        GapCategory.CONTEXT: QuestionCategory.EXISTING_CONTEXT,
        GapCategory.VISUAL: QuestionCategory.THEME_STYLE,
        GapCategory.TECHNICAL: QuestionCategory.TECHNICAL,
        GapCategory.CONTENT: QuestionCategory.CONTENT,
        GapCategory.AUDIENCE: QuestionCategory.INDUSTRY,  # Closest match
        GapCategory.BRAND: QuestionCategory.THEME_STYLE,  # Brand → Visual theme
        GapCategory.EMOTIONAL: QuestionCategory.VIBE_MOOD,
        GapCategory.FUNCTIONAL: QuestionCategory.TECHNICAL,
    }

    # =========================================================================
    # SEVERITY → PRIORITY MAPPING
    # =========================================================================

    # Higher priority = asked first (100 = max priority)
    SEVERITY_PRIORITY: ClassVar[Dict[GapSeverity, int]] = {
        GapSeverity.CRITICAL: 100,
        GapSeverity.HIGH: 80,
        GapSeverity.MEDIUM: 50,
        GapSeverity.LOW: 20,
    }

    # =========================================================================
    # SMART OPTIONS BY CATEGORY
    # =========================================================================

    # Default options for each gap category (Türkçe)
    CATEGORY_OPTIONS_TR: ClassVar[Dict[GapCategory, List[Dict]]] = {
        GapCategory.AUDIENCE: [
            {"id": "opt_b2b", "label": "B2B", "description": "İşletmeler ve kurumsal müşteriler", "icon": "🏢"},
            {"id": "opt_b2c", "label": "B2C", "description": "Son kullanıcılar ve tüketiciler", "icon": "👥"},
            {"id": "opt_internal", "label": "İç Kullanım", "description": "Şirket içi araçlar", "icon": "🔒"},
            {"id": "opt_developer", "label": "Developer", "description": "Yazılım geliştiriciler", "icon": "👨‍💻"},
        ],
        GapCategory.VISUAL: [
            {"id": "opt_modern", "label": "Modern Minimal", "description": "Temiz, profesyonel", "icon": "✨"},
            {"id": "opt_bold", "label": "Cesur", "description": "Dikkat çekici, kontrast", "icon": "⚡"},
            {"id": "opt_elegant", "label": "Şık", "description": "Sofistike, zarif", "icon": "💎"},
            {"id": "opt_playful", "label": "Eğlenceli", "description": "Neşeli, enerjik", "icon": "🎉"},
        ],
        GapCategory.BRAND: [
            {"id": "opt_corporate", "label": "Kurumsal", "description": "Ciddi, güven veren", "icon": "🏢"},
            {"id": "opt_startup", "label": "Startup", "description": "Yenilikçi, dinamik", "icon": "🚀"},
            {"id": "opt_creative", "label": "Yaratıcı", "description": "Farklı, dikkat çekici", "icon": "🎨"},
            {"id": "opt_premium", "label": "Premium", "description": "Lüks, üst segment", "icon": "👑"},
        ],
        GapCategory.EMOTIONAL: [
            {"id": "opt_trust", "label": "Güven", "description": "Güvenilir, kararlı", "icon": "🤝"},
            {"id": "opt_excitement", "label": "Heyecan", "description": "Enerjik, dinamik", "icon": "⚡"},
            {"id": "opt_calm", "label": "Huzur", "description": "Sakin, rahatlatıcı", "icon": "🌿"},
            {"id": "opt_joy", "label": "Neşe", "description": "Mutlu, pozitif", "icon": "😊"},
        ],
        GapCategory.TECHNICAL: [
            {"id": "opt_web", "label": "Web", "description": "Responsive web uygulaması", "icon": "🌐"},
            {"id": "opt_mobile_first", "label": "Mobile First", "description": "Önce mobil tasarım", "icon": "📱"},
            {"id": "opt_desktop", "label": "Desktop", "description": "Masaüstü odaklı", "icon": "🖥️"},
            {"id": "opt_all_platforms", "label": "Tüm Platformlar", "description": "Universal tasarım", "icon": "🔗"},
        ],
        GapCategory.CONTENT: [
            {"id": "opt_minimal", "label": "Minimal", "description": "Az metin, görsel ağırlıklı", "icon": "📸"},
            {"id": "opt_balanced", "label": "Dengeli", "description": "Metin ve görsel dengesi", "icon": "⚖️"},
            {"id": "opt_content_heavy", "label": "İçerik Yoğun", "description": "Metin ağırlıklı", "icon": "📄"},
            {"id": "opt_data_driven", "label": "Veri Odaklı", "description": "Tablo, grafik ağırlıklı", "icon": "📊"},
        ],
        GapCategory.SCOPE: [
            {"id": "opt_full_page", "label": "Tam Sayfa", "description": "Komple sayfa tasarımı", "icon": "📄"},
            {"id": "opt_section", "label": "Section", "description": "Sayfa bölümü", "icon": "📐"},
            {"id": "opt_component", "label": "Component", "description": "Tek bileşen", "icon": "🧩"},
        ],
    }

    def __init__(self, language: str = "tr") -> None:
        """
        Initialize the factory.

        Args:
            language: Default language for questions ("tr" or "en")
        """
        self.language = language

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def create_question(
        self,
        gap: GapInfo,
        soul: Optional["ProjectSoul"] = None,
    ) -> Question:
        """
        Create a Question from a GapInfo.

        Args:
            gap: The gap to create a question for
            soul: Optional ProjectSoul for context-aware generation

        Returns:
            A Question object ready for the interview system
        """
        # Map category
        question_category = self._map_category(gap.category)

        # Generate question ID
        question_id = f"q_{gap.id}" if not gap.id.startswith("q_") else gap.id

        # Get question text
        question_text = gap.suggested_question or self._generate_question_text(gap)

        # Determine question type and options
        question_type, options = self._determine_type_and_options(gap, soul)

        # Calculate priority
        priority = self._calculate_priority(gap)

        return Question(
            id=question_id,
            category=question_category,
            text=question_text,
            question_type=question_type,
            options=options,
            required=gap.severity in [GapSeverity.CRITICAL, GapSeverity.HIGH],
            help_text=gap.detail,
        )

    def create_questions_from_gaps(
        self,
        gaps: List[GapInfo],
        soul: Optional["ProjectSoul"] = None,
    ) -> List[Question]:
        """
        Create multiple Questions from a list of GapInfo.

        Args:
            gaps: List of gaps to convert
            soul: Optional ProjectSoul for context

        Returns:
            List of Question objects
        """
        questions = []
        for gap in gaps:
            try:
                question = self.create_question(gap, soul)
                questions.append(question)
            except Exception as e:
                logger.warning(f"Failed to create question from gap {gap.id}: {e}")
        return questions

    def create_follow_up_question(
        self,
        parent_gap: GapInfo,
        answer_context: str,
    ) -> Optional[Question]:
        """
        Create a follow-up question based on an answer.

        Args:
            parent_gap: The gap that was just addressed
            answer_context: The user's answer for context

        Returns:
            A follow-up Question or None if no follow-up needed
        """
        # Only create follow-ups for certain categories
        if parent_gap.category not in [
            GapCategory.VISUAL,
            GapCategory.BRAND,
            GapCategory.AUDIENCE,
        ]:
            return None

        # Generate follow-up based on category
        follow_up_text = self._generate_follow_up_text(parent_gap, answer_context)
        if not follow_up_text:
            return None

        return Question(
            id=f"{parent_gap.id}_followup",
            category=self._map_category(parent_gap.category),
            text=follow_up_text,
            question_type=QuestionType.TEXT_INPUT,
            options=[],
            required=False,
            help_text="Daha detaylı bilgi vermek için kullanabilirsiniz",
        )

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _map_category(self, gap_category: GapCategory) -> QuestionCategory:
        """Map GapCategory to QuestionCategory."""
        return self.CATEGORY_MAP.get(gap_category, QuestionCategory.CONTENT)

    def _calculate_priority(self, gap: GapInfo) -> int:
        """Calculate question priority from gap severity and priority."""
        base_priority = self.SEVERITY_PRIORITY.get(gap.severity, 50)
        gap_priority = gap.priority if hasattr(gap, 'priority') else 50
        # Combine: severity weight (70%) + gap priority weight (30%)
        return int(base_priority * 0.7 + gap_priority * 0.3)

    def _determine_type_and_options(
        self,
        gap: GapInfo,
        soul: Optional["ProjectSoul"],
    ) -> tuple[QuestionType, List[QuestionOption]]:
        """
        Determine question type and generate options.

        Returns:
            Tuple of (QuestionType, options list)
        """
        # If gap has predefined options, use them
        if gap.question_options:
            options = [
                QuestionOption(
                    id=f"opt_{i}",
                    label=opt,
                    description="",
                    icon="",
                )
                for i, opt in enumerate(gap.question_options)
            ]
            return QuestionType.SINGLE_CHOICE, options

        # Use category-based defaults
        category_options = self.CATEGORY_OPTIONS_TR.get(gap.category)
        if category_options:
            options = [
                QuestionOption(**opt_dict)
                for opt_dict in category_options
            ]
            return QuestionType.SINGLE_CHOICE, options

        # Default to text input
        return QuestionType.TEXT_INPUT, []

    def _generate_question_text(self, gap: GapInfo) -> str:
        """Generate question text from gap description."""
        # Default Turkish question templates by category
        templates = {
            GapCategory.AUDIENCE: "Hedef kitleniz kimdir?",
            GapCategory.VISUAL: "Görsel stil tercihiniz nedir?",
            GapCategory.BRAND: "Marka kişiliğinizi nasıl tanımlarsınız?",
            GapCategory.EMOTIONAL: "Kullanıcılarda hangi duyguyu uyandırmak istiyorsunuz?",
            GapCategory.TECHNICAL: "Teknik gereksinimleriniz nelerdir?",
            GapCategory.CONTENT: "İçerik yapınız nasıl olmalı?",
            GapCategory.SCOPE: "Projenin kapsamı nedir?",
            GapCategory.CONTEXT: "Mevcut bağlam hakkında bilgi verir misiniz?",
            GapCategory.INTENT: "Projenin amacı nedir?",
            GapCategory.FUNCTIONAL: "Temel fonksiyonlar neler olmalı?",
        }
        return templates.get(gap.category, f"Lütfen belirtin: {gap.description}")

    def _generate_follow_up_text(
        self,
        parent_gap: GapInfo,
        answer_context: str,
    ) -> Optional[str]:
        """Generate follow-up question text."""
        follow_up_templates = {
            GapCategory.VISUAL: "Bu stili daha detaylı açıklar mısınız?",
            GapCategory.BRAND: "Marka değerlerinizi eklemek ister misiniz?",
            GapCategory.AUDIENCE: "Hedef kitlenizin özel ihtiyaçları var mı?",
        }
        return follow_up_templates.get(parent_gap.category)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_questions_from_analysis(
    gaps: List[GapInfo],
    language: str = "tr",
    soul: Optional["ProjectSoul"] = None,
) -> List[Question]:
    """
    Convenience function to create questions from gap analysis.

    Args:
        gaps: List of GapInfo from gap analysis
        language: Question language
        soul: Optional ProjectSoul for context

    Returns:
        List of Question objects
    """
    factory = GapBasedQuestionFactory(language=language)
    return factory.create_questions_from_gaps(gaps, soul)
