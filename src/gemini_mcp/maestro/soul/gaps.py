"""
MAESTRO v2 Gap Detector

Identifies missing information in design briefs and generates
targeted questions to fill those gaps.

Gap Categories (from GapCategory enum):
- INTENT: Project purpose and goals
- SCOPE: Project constraints, timeline, budget
- CONTEXT: Market, competitors, references
- VISUAL: Theme, layout, aesthetics, colors
- TECHNICAL: Platforms, accessibility, requirements
- CONTENT: Copy, imagery, sections, localization
- AUDIENCE: Demographics, psychographics, tech level
- BRAND: Logo, colors, typography, personality
- EMOTIONAL: Feelings, tone, experience goals
- FUNCTIONAL: Navigation, flows, interactions

Usage:
    >>> from gemini_mcp.maestro.soul.gaps import GapDetector
    >>> detector = GapDetector()
    >>> gaps = detector.detect(parsed_brief)
    >>> for gap in gaps.critical_gaps:
    ...     print(gap.suggested_question)
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from gemini_mcp.maestro.brief.parser import ParsedBrief
from gemini_mcp.maestro.brief.extractor import ExtractedEntities
from gemini_mcp.maestro.models.gap import (
    GapAnalysis,
    GapCategory,
    GapInfo,
    GapSeverity,
)
from gemini_mcp.maestro.config import get_config


@dataclass
class GapRule:
    """
    A rule for detecting a specific gap.

    Attributes:
        category: Gap category
        severity: Default severity
        condition: Condition function
        question_en: English question template
        question_tr: Turkish question template
        default_value: Default if not asked
        priority: Higher = asked first
    """

    category: GapCategory
    severity: GapSeverity
    condition: str  # Condition description (evaluated dynamically)
    question_en: str
    question_tr: str
    default_value: Optional[str] = None
    priority: int = 50


class GapDetector:
    """
    Detects gaps in design briefs and generates questions.

    Analyzes parsed briefs to identify missing information,
    prioritizes gaps by severity, and generates targeted questions.

    Example:
        >>> detector = GapDetector()
        >>> gaps = detector.detect(parsed_brief)
        >>> print(len(gaps.all_gaps))
        5
        >>> print(gaps.critical_gaps[0].suggested_question)
        'Projenin hedef kitlesini tanımlar mısınız?'
    """

    def __init__(self, language: str = "tr"):
        """
        Initialize detector.

        Args:
            language: Default question language ("tr" or "en")
        """
        self.language = language
        self._config = get_config()

        # Initialize rules
        self._rules = self._build_rules()

    def _build_rules(self) -> List[GapRule]:
        """Build gap detection rules."""
        return [
            # === BRAND_IDENTITY ===
            GapRule(
                category=GapCategory.BRAND,
                severity=GapSeverity.HIGH,
                condition="no_colors",
                question_en="What color palette would you like for your design?",
                question_tr="Tasarımınız için hangi renk paletini tercih edersiniz?",
                default_value="modern-minimal palette",
                priority=80,
            ),
            GapRule(
                category=GapCategory.BRAND,
                severity=GapSeverity.MEDIUM,
                condition="no_typography",
                question_en="Do you have typography preferences (font style)?",
                question_tr="Tipografi tercihiniz var mı (font stili)?",
                default_value="system fonts",
                priority=40,
            ),

            # === TARGET_AUDIENCE ===
            GapRule(
                category=GapCategory.AUDIENCE,
                severity=GapSeverity.CRITICAL,
                condition="no_audience",
                question_en="Who is the target audience for this design?",
                question_tr="Bu tasarımın hedef kitlesi kimdir?",
                priority=100,
            ),
            GapRule(
                category=GapCategory.AUDIENCE,
                severity=GapSeverity.MEDIUM,
                condition="no_tech_level",
                question_en="What is the technical proficiency of your users?",
                question_tr="Kullanıcılarınızın teknik yetkinlik seviyesi nedir?",
                default_value="average",
                priority=35,
            ),

            # === VISUAL_STYLE ===
            GapRule(
                category=GapCategory.VISUAL,
                severity=GapSeverity.HIGH,
                condition="no_tone",
                question_en="What visual style or tone do you want (modern, minimal, bold)?",
                question_tr="Hangi görsel stil veya ton istiyorsunuz (modern, minimal, cesur)?",
                default_value="modern professional",
                priority=75,
            ),
            GapRule(
                category=GapCategory.VISUAL,
                severity=GapSeverity.MEDIUM,
                condition="no_theme",
                question_en="Do you prefer light mode, dark mode, or both?",
                question_tr="Açık tema, koyu tema veya ikisini birden mi tercih edersiniz?",
                default_value="light with dark support",
                priority=50,
            ),
            GapRule(
                category=GapCategory.VISUAL,
                severity=GapSeverity.LOW,
                condition="no_density",
                question_en="Do you prefer compact or spacious layouts?",
                question_tr="Kompakt mı yoksa geniş boşluklu layout mu tercih edersiniz?",
                default_value="comfortable",
                priority=20,
            ),

            # === TECHNICAL_REQUIREMENTS ===
            GapRule(
                category=GapCategory.TECHNICAL,
                severity=GapSeverity.HIGH,
                condition="no_platform",
                question_en="What platforms should the design support?",
                question_tr="Tasarım hangi platformları desteklemeli?",
                default_value="responsive web",
                priority=70,
            ),
            GapRule(
                category=GapCategory.TECHNICAL,
                severity=GapSeverity.MEDIUM,
                condition="no_accessibility",
                question_en="What accessibility level do you need (AA, AAA)?",
                question_tr="Hangi erişilebilirlik seviyesine ihtiyacınız var (AA, AAA)?",
                default_value="WCAG AA",
                priority=45,
            ),

            # === CONTENT_STRUCTURE ===
            GapRule(
                category=GapCategory.CONTENT,
                severity=GapSeverity.MEDIUM,
                condition="no_sections",
                question_en="What sections should the page include?",
                question_tr="Sayfa hangi bölümleri içermeli?",
                default_value="hero, features, cta",
                priority=55,
            ),
            GapRule(
                category=GapCategory.CONTENT,
                severity=GapSeverity.LOW,
                condition="no_cta",
                question_en="What is the primary call-to-action?",
                question_tr="Birincil çağrı-eylemi (CTA) nedir?",
                default_value="Get Started",
                priority=25,
            ),

            # === EMOTIONAL_GOALS ===
            GapRule(
                category=GapCategory.EMOTIONAL,
                severity=GapSeverity.HIGH,
                condition="no_emotions",
                question_en="What feeling should users get from this design?",
                question_tr="Kullanıcılar bu tasarımdan nasıl bir duygu edinmeli?",
                default_value="trust and confidence",
                priority=65,
            ),
            GapRule(
                category=GapCategory.EMOTIONAL,
                severity=GapSeverity.MEDIUM,
                condition="no_personality",
                question_en="How would you describe the brand personality?",
                question_tr="Marka kişiliğini nasıl tanımlarsınız?",
                default_value="professional yet approachable",
                priority=45,
            ),

            # === COMPETITIVE_CONTEXT ===
            GapRule(
                category=GapCategory.CONTEXT,
                severity=GapSeverity.LOW,
                condition="no_competitors",
                question_en="Are there any designs or brands you'd like to reference?",
                question_tr="Referans almak istediğiniz tasarımlar veya markalar var mı?",
                priority=15,
            ),

            # === PROJECT_CONSTRAINTS ===
            GapRule(
                category=GapCategory.SCOPE,
                severity=GapSeverity.MEDIUM,
                condition="no_scope",
                question_en="What is the scope of this design project?",
                question_tr="Bu tasarım projesinin kapsamı nedir?",
                default_value="single page",
                priority=60,
            ),

            # === INTERACTION_PATTERNS ===
            GapRule(
                category=GapCategory.FUNCTIONAL,
                severity=GapSeverity.MEDIUM,
                condition="no_interactions",
                question_en="What key interactions should the design include?",
                question_tr="Tasarım hangi temel etkileşimleri içermeli?",
                default_value="standard navigation",
                priority=40,
            ),

            # === LOCALIZATION ===
            GapRule(
                category=GapCategory.CONTENT,
                severity=GapSeverity.LOW,
                condition="no_language",
                question_en="What language(s) should the content be in?",
                question_tr="İçerik hangi dil(ler)de olmalı?",
                default_value="Turkish",
                priority=30,
            ),

            # === PROJECT_TYPE (CRITICAL) ===
            GapRule(
                category=GapCategory.CONTENT,
                severity=GapSeverity.CRITICAL,
                condition="no_project_type",
                question_en="What type of design do you need (dashboard, landing page, form)?",
                question_tr="Ne tür bir tasarıma ihtiyacınız var (dashboard, landing page, form)?",
                priority=100,
            ),

            # === INDUSTRY ===
            GapRule(
                category=GapCategory.BRAND,
                severity=GapSeverity.HIGH,
                condition="no_industry",
                question_en="What industry is this design for?",
                question_tr="Bu tasarım hangi sektör için?",
                default_value="technology",
                priority=85,
            ),
        ]

    def detect(
        self,
        brief: ParsedBrief,
        entities: Optional[ExtractedEntities] = None,
    ) -> GapAnalysis:
        """
        Detect gaps in a parsed brief.

        Args:
            brief: Parsed design brief
            entities: Extracted entities (optional)

        Returns:
            GapAnalysis with identified gaps
        """
        entities = entities or brief.entities
        gaps: List[GapInfo] = []

        # Build condition evaluator context
        context = self._build_context(brief, entities)

        # Evaluate each rule
        for rule in self._rules:
            if self._evaluate_condition(rule.condition, context):
                gap = self._create_gap(rule, brief)
                gaps.append(gap)

        # Create analysis
        analysis = GapAnalysis(gaps=gaps)

        return analysis

    def _build_context(
        self,
        brief: ParsedBrief,
        entities: ExtractedEntities,
    ) -> Dict[str, bool]:
        """Build evaluation context from brief."""
        return {
            # Project type
            "no_project_type": not entities.project_type,
            "has_project_type": bool(entities.project_type),

            # Industry
            "no_industry": not entities.industry,
            "has_industry": bool(entities.industry),

            # Audience
            "no_audience": not entities.audience_signals,
            "has_audience": bool(entities.audience_signals),
            "no_tech_level": True,  # Not extracted in MVP

            # Visual
            "no_colors": not entities.color_mentions,
            "has_colors": bool(entities.color_mentions),
            "no_tone": not entities.tone_keywords,
            "has_tone": bool(entities.tone_keywords),
            "no_theme": "dark" not in brief.raw_text.lower() and "light" not in brief.raw_text.lower(),
            "no_typography": True,  # Not extracted in MVP
            "no_density": True,  # Not extracted in MVP

            # Technical
            "no_platform": not entities.platform_mentions,
            "has_platform": bool(entities.platform_mentions),
            "no_accessibility": "accessibility" not in brief.raw_text.lower() and "wcag" not in brief.raw_text.lower(),

            # Content
            "no_sections": True,  # Not extracted in MVP
            "no_cta": "cta" not in brief.raw_text.lower() and "button" not in brief.raw_text.lower(),

            # Emotional
            "no_emotions": not entities.emotion_keywords,
            "has_emotions": bool(entities.emotion_keywords),
            "no_personality": True,  # Inferred from Aaker

            # Context
            "no_competitors": "like" not in brief.raw_text.lower() and "similar" not in brief.raw_text.lower(),
            "no_scope": True,  # Not extracted in MVP
            "no_interactions": True,  # Not extracted in MVP
            "no_language": True,  # Detected but not specified
        }

    def _evaluate_condition(self, condition: str, context: Dict[str, bool]) -> bool:
        """Evaluate a condition against context."""
        return context.get(condition, False)

    def _create_gap(self, rule: GapRule, brief: ParsedBrief) -> GapInfo:
        """Create a GapInfo from a rule."""
        # Select question based on language
        language = self.language or brief.language or "tr"
        question = rule.question_tr if language == "tr" else rule.question_en

        return GapInfo(
            id=f"gap_{uuid.uuid4().hex[:8]}",
            category=rule.category,
            severity=rule.severity,
            description=f"Missing {rule.category.value.replace('_', ' ')} information",
            suggested_question=question,
            default_value=rule.default_value,
            priority=rule.priority,
        )

    def detect_by_severity(
        self,
        brief: ParsedBrief,
        min_severity: GapSeverity = GapSeverity.MEDIUM,
    ) -> List[GapInfo]:
        """
        Detect gaps at or above a severity level.

        Args:
            brief: Parsed design brief
            min_severity: Minimum severity to include

        Returns:
            List of GapInfo at or above severity
        """
        analysis = self.detect(brief)

        severity_order = {
            GapSeverity.LOW: 0,
            GapSeverity.MEDIUM: 1,
            GapSeverity.HIGH: 2,
            GapSeverity.CRITICAL: 3,
        }

        min_level = severity_order[min_severity]

        return [
            gap for gap in analysis.all_gaps
            if severity_order[gap.severity] >= min_level
        ]

    def get_priority_questions(
        self,
        brief: ParsedBrief,
        max_questions: int = 5,
    ) -> List[str]:
        """
        Get prioritized questions for filling gaps.

        Args:
            brief: Parsed design brief
            max_questions: Maximum questions to return

        Returns:
            List of question strings, sorted by priority
        """
        analysis = self.detect(brief)
        prioritized = analysis.get_priority_queue()

        questions = []
        for gap in prioritized[:max_questions]:
            if gap.suggested_question:
                questions.append(gap.suggested_question)

        return questions

    def can_proceed(self, brief: ParsedBrief) -> Tuple[bool, List[str]]:
        """
        Check if we have enough information to proceed.

        Args:
            brief: Parsed design brief

        Returns:
            Tuple of (can_proceed, blocking_gaps)
        """
        analysis = self.detect(brief)

        # Check if any critical gaps
        critical = analysis.critical_gaps
        if critical:
            blocking = [gap.suggested_question or gap.description for gap in critical]
            return False, blocking

        # Check config for blocking on high gaps
        config = self._config
        if config.BLOCK_ON_CRITICAL_GAPS:
            # Only block on critical (already checked above)
            pass

        return True, []

    def apply_defaults(self, analysis: GapAnalysis) -> Dict[str, str]:
        """
        Get default values for gaps that can be auto-filled.

        Args:
            analysis: Gap analysis result

        Returns:
            Dict mapping gap_id to default_value
        """
        defaults = {}

        for gap in analysis.all_gaps:
            if gap.default_value:
                defaults[gap.id] = gap.default_value

        return defaults

    def resolve_with_defaults(self, analysis: GapAnalysis) -> None:
        """
        Resolve gaps with their default values.

        Modifies gaps in place.

        Args:
            analysis: Gap analysis to modify
        """
        for gap in analysis.all_gaps:
            if gap.default_value and not gap.is_resolved:
                gap.resolve(gap.default_value, source="default")

    def get_category_summary(self, analysis: GapAnalysis) -> Dict[str, int]:
        """
        Get count of gaps by category.

        Args:
            analysis: Gap analysis

        Returns:
            Dict mapping category name to count
        """
        summary: Dict[str, int] = {}

        for gap in analysis.all_gaps:
            category = gap.category.value
            summary[category] = summary.get(category, 0) + 1

        return summary
