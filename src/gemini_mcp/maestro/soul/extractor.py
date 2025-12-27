"""
MAESTRO v2 Soul Extractor

Main orchestrator for extracting ProjectSoul from design briefs.
Combines BriefParser, AakerAnalyzer, ConfidenceCalculator, and GapDetector
to produce a complete ProjectSoul.

Pipeline:
    Brief (str)
        ↓
    BriefParser → ParsedBrief
        ↓
    ┌───────────────────────────────────────────┐
    │              SoulExtractor                 │
    │                                            │
    │  ┌─────────────┐  ┌─────────────────────┐  │
    │  │AakerAnalyzer│  │ConfidenceCalculator │  │
    │  └─────────────┘  └─────────────────────┘  │
    │         ↓                  ↓               │
    │  ┌─────────────┐  ┌─────────────────────┐  │
    │  │GapDetector  │  │   Soul Builder      │  │
    │  └─────────────┘  └─────────────────────┘  │
    │                        ↓                   │
    │              ┌─────────────────┐           │
    │              │  ProjectSoul    │           │
    │              └─────────────────┘           │
    └───────────────────────────────────────────┘

Usage:
    >>> from gemini_mcp.maestro.soul import SoulExtractor
    >>> extractor = SoulExtractor()
    >>> soul = await extractor.extract("Design a modern fintech dashboard")
    >>> print(soul.brand_personality.dominant_trait)
    'competence'
    >>> print(soul.confidence_scores.overall)
    0.75
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from gemini_mcp.maestro.brief.parser import BriefParser, ParsedBrief
from gemini_mcp.maestro.brief.extractor import ExtractedEntities
from gemini_mcp.maestro.config import get_config, MAESTROConfig
from gemini_mcp.maestro.models import (
    # Soul
    ProjectSoul,
    InterviewPhase,
    ConfidenceScores,
    ProjectMetadata,
    ProjectConstraints,
    # Brand
    BrandPersonality,
    PersonalityArchetype,
    # Audience
    TargetAudience,
    DemographicProfile,
    PsychographicProfile,
    TechSavviness,
    DevicePreference,
    # Visual
    VisualLanguage,
    ColorPalette,
    TypographyStyle,
    ColorHarmony,
    SpacingDensity,
    # Emotion
    EmotionalFramework,
    EmotionMapping,
    PrimaryEmotion,
    EmotionalTone,
    # Gap
    GapAnalysis,
    GapInfo,
)
from gemini_mcp.maestro.soul.aaker import AakerAnalyzer
from gemini_mcp.maestro.soul.confidence import ConfidenceCalculator
from gemini_mcp.maestro.soul.gaps import GapDetector

logger = logging.getLogger(__name__)


class SoulExtractorError(Exception):
    """Base exception for soul extraction errors."""
    pass


class ExtractionResult:
    """
    Result of soul extraction.

    Attributes:
        soul: Extracted ProjectSoul (may be partial)
        is_complete: Whether extraction is fully complete
        confidence: Overall confidence score
        gaps: Identified information gaps
        blocking_gaps: Gaps that prevent proceeding
        warnings: Non-blocking issues
    """

    def __init__(
        self,
        soul: ProjectSoul,
        is_complete: bool = False,
        gaps: Optional[GapAnalysis] = None,
        blocking_gaps: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
    ):
        self.soul = soul
        self.is_complete = is_complete
        self.gaps = gaps
        self.blocking_gaps = blocking_gaps or []
        self.warnings = warnings or []

    @property
    def confidence(self) -> float:
        """Get overall confidence score."""
        return self.soul.confidence_scores.overall

    @property
    def can_proceed(self) -> bool:
        """Check if we can proceed with design."""
        return len(self.blocking_gaps) == 0

    @property
    def needs_questions(self) -> bool:
        """Check if we need to ask more questions."""
        return self.gaps is not None and len(self.gaps.unresolved_gaps) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "soul": self.soul.model_dump(),
            "is_complete": self.is_complete,
            "confidence": self.confidence,
            "can_proceed": self.can_proceed,
            "needs_questions": self.needs_questions,
            "blocking_gaps": self.blocking_gaps,
            "warnings": self.warnings,
            "gap_count": len(self.gaps.all_gaps) if self.gaps else 0,
        }


class SoulExtractor:
    """
    Extracts ProjectSoul from design briefs.

    Main orchestrator that combines parsing, Aaker analysis,
    confidence calculation, and gap detection to produce
    a complete ProjectSoul.

    Example:
        >>> extractor = SoulExtractor()
        >>> result = await extractor.extract("Design a modern fintech dashboard")
        >>> print(result.soul.project_name)
        'Fintech Dashboard'
        >>> print(result.confidence)
        0.72
        >>> if result.needs_questions:
        ...     for gap in result.gaps.critical_gaps:
        ...         print(gap.suggested_question)
    """

    def __init__(
        self,
        parser: Optional[BriefParser] = None,
        aaker: Optional[AakerAnalyzer] = None,
        confidence_calc: Optional[ConfidenceCalculator] = None,
        gap_detector: Optional[GapDetector] = None,
        config: Optional[MAESTROConfig] = None,
    ):
        """
        Initialize extractor with optional custom components.

        Args:
            parser: Custom BriefParser
            aaker: Custom AakerAnalyzer
            confidence_calc: Custom ConfidenceCalculator
            gap_detector: Custom GapDetector
            config: Custom configuration
        """
        self._parser = parser or BriefParser()
        self._aaker = aaker or AakerAnalyzer()
        self._confidence = confidence_calc or ConfidenceCalculator()
        self._gaps = gap_detector or GapDetector()
        self._config = config or get_config()

    async def extract(
        self,
        brief: str,
        existing_html: Optional[str] = None,
        project_context: Optional[str] = None,
    ) -> ExtractionResult:
        """
        Extract ProjectSoul from a design brief.

        This is the main entry point for soul extraction.

        Args:
            brief: Design brief text
            existing_html: Optional existing HTML for refinement
            project_context: Optional project context

        Returns:
            ExtractionResult with soul and metadata
        """
        warnings: List[str] = []

        # Step 1: Parse brief
        logger.debug("Parsing design brief...")
        parsed = self._parser.parse_sync(brief)

        if not parsed.is_valid:
            # Log validation issues
            for issue in parsed.validation.issues:
                if issue.severity.value == "error":
                    warnings.append(f"Validation: {issue.message}")

        # Step 2: Analyze brand personality
        logger.debug("Analyzing brand personality...")
        personality = self._extract_personality(parsed)

        # Step 3: Build target audience
        logger.debug("Building target audience...")
        audience = self._extract_audience(parsed)

        # Step 4: Build visual language
        logger.debug("Building visual language...")
        visual = self._extract_visual_language(parsed)

        # Step 5: Build emotional framework
        logger.debug("Building emotional framework...")
        emotional = self._extract_emotional_framework(parsed)

        # Step 6: Calculate confidence
        logger.debug("Calculating confidence scores...")
        confidence = self._confidence.calculate(parsed)

        # Step 7: Detect gaps
        logger.debug("Detecting information gaps...")
        gap_analysis = self._gaps.detect(parsed)

        # Step 8: Check if we can proceed
        can_proceed, blocking_gaps = self._gaps.can_proceed(parsed)

        # Step 9: Determine current phase
        if not can_proceed:
            current_phase = InterviewPhase.CONTEXT_GATHERING
        elif confidence.overall < self._config.MIN_CONFIDENCE:
            current_phase = InterviewPhase.DEEP_DIVE
        else:
            current_phase = InterviewPhase.VALIDATION

        # Step 10: Build ProjectSoul
        soul = ProjectSoul(
            metadata=ProjectMetadata(
                project_name=parsed.project_name,
                source_brief=brief,
                source_type="design_brief",
                language=parsed.language,
            ),
            brand_personality=personality,
            target_audience=audience,
            visual_language=visual,
            emotional_framework=emotional,
            confidence_scores=confidence,
            current_phase=current_phase,
            constraints=ProjectConstraints(
                accessibility_level="WCAG_AA",
                supported_browsers=["chrome", "firefox", "safari", "edge"],
                performance_budget="FCP < 1.5s, LCP < 2.5s",
            ),
            gap_analysis=gap_analysis,
        )

        # Determine if complete
        is_complete = (
            can_proceed and
            confidence.overall >= self._config.MIN_CONFIDENCE and
            len(gap_analysis.critical_gaps) == 0
        )

        return ExtractionResult(
            soul=soul,
            is_complete=is_complete,
            gaps=gap_analysis,
            blocking_gaps=blocking_gaps,
            warnings=warnings,
        )

    def extract_sync(
        self,
        brief: str,
        existing_html: Optional[str] = None,
        project_context: Optional[str] = None,
    ) -> ExtractionResult:
        """
        Synchronous wrapper for extract().

        Args:
            brief: Design brief text
            existing_html: Optional existing HTML
            project_context: Optional project context

        Returns:
            ExtractionResult
        """
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.extract(brief, existing_html, project_context)
            )
        finally:
            loop.close()

    def _extract_personality(self, parsed: ParsedBrief) -> BrandPersonality:
        """Extract brand personality from parsed brief."""
        # Combine raw text and extracted keywords for analysis
        analysis_text = parsed.raw_text

        # Add tone keywords for stronger signal
        if parsed.entities.tone_keywords:
            analysis_text += " " + " ".join(parsed.entities.tone_keywords)

        # Get Aaker scores
        personality = self._aaker.analyze_to_personality(analysis_text)

        # Blend with industry baseline if industry is known
        if parsed.entities.industry:
            scores = self._aaker.analyze(analysis_text)
            blended = self._aaker.blend_with_baseline(
                scores,
                parsed.entities.industry,
                blend_ratio=0.3,  # 30% industry baseline
            )
            personality = self._aaker.to_brand_personality(blended)

        return personality

    def _extract_audience(self, parsed: ParsedBrief) -> TargetAudience:
        """Extract target audience from parsed brief."""
        audience = TargetAudience()

        # Set persona name from signals
        if parsed.entities.audience_signals:
            signals = parsed.entities.audience_signals
            if signals:
                audience.persona_name = signals[0].title()

        # Infer tech savviness from industry
        industry = parsed.entities.industry
        if industry:
            tech_industries = {"fintech", "saas", "technology", "startup"}
            if industry.lower() in tech_industries:
                audience.demographic.tech_savviness = TechSavviness.ADVANCED
            else:
                audience.demographic.tech_savviness = TechSavviness.INTERMEDIATE

        # Infer device preference from platform mentions
        platforms = parsed.entities.platform_mentions
        if platforms:
            if "mobile" in [p.lower() for p in platforms]:
                audience.demographic.device_preference = DevicePreference.MOBILE_FIRST
            elif "desktop" in [p.lower() for p in platforms]:
                audience.demographic.device_preference = DevicePreference.DESKTOP_FIRST
            else:
                audience.demographic.device_preference = DevicePreference.RESPONSIVE

        return audience

    def _extract_visual_language(self, parsed: ParsedBrief) -> VisualLanguage:
        """Extract visual language from parsed brief."""
        visual = VisualLanguage()

        # Set colors from mentions
        colors = parsed.entities.color_mentions
        if colors:
            # Map color names to palette
            color_mapping = {
                "blue": "#3B82F6",
                "mavi": "#3B82F6",
                "red": "#EF4444",
                "kırmızı": "#EF4444",
                "green": "#10B981",
                "yeşil": "#10B981",
                "purple": "#8B5CF6",
                "mor": "#8B5CF6",
                "orange": "#F97316",
                "turuncu": "#F97316",
                "teal": "#14B8A6",
                "cyan": "#06B6D4",
                "pink": "#EC4899",
                "yellow": "#EAB308",
                "sarı": "#EAB308",
            }

            for color in colors:
                color_lower = color.lower()
                if color_lower in color_mapping:
                    visual.palette.primary = color_mapping[color_lower]
                    break

        # Determine color harmony from tone
        tones = parsed.entities.tone_keywords
        if tones:
            tone_lower = " ".join(tones).lower()
            if "minimal" in tone_lower or "modern" in tone_lower:
                visual.palette.harmony = ColorHarmony.MONOCHROMATIC
            elif "bold" in tone_lower or "vibrant" in tone_lower:
                visual.palette.harmony = ColorHarmony.COMPLEMENTARY
            elif "warm" in tone_lower or "sıcak" in tone_lower:
                visual.palette.harmony = ColorHarmony.ANALOGOUS

        # Set spacing density
        text_lower = parsed.raw_text.lower()
        if "compact" in text_lower or "dense" in text_lower:
            visual.spacing_density = SpacingDensity.COMPACT
        elif "spacious" in text_lower or "airy" in text_lower:
            visual.spacing_density = SpacingDensity.SPACIOUS

        return visual

    def _extract_emotional_framework(self, parsed: ParsedBrief) -> EmotionalFramework:
        """Extract emotional framework from parsed brief."""
        framework = EmotionalFramework()

        # Map emotion keywords to primary emotions
        emotions = parsed.entities.emotion_keywords
        if emotions:
            emotion_mapping = {
                # Joy
                "happy": PrimaryEmotion.JOY,
                "joyful": PrimaryEmotion.JOY,
                "cheerful": PrimaryEmotion.JOY,
                "mutlu": PrimaryEmotion.JOY,
                "neşeli": PrimaryEmotion.JOY,
                # Trust
                "trust": PrimaryEmotion.TRUST,
                "reliable": PrimaryEmotion.TRUST,
                "secure": PrimaryEmotion.TRUST,
                "güvenilir": PrimaryEmotion.TRUST,
                "güvenli": PrimaryEmotion.TRUST,
                # Anticipation
                "exciting": PrimaryEmotion.ANTICIPATION,
                "innovative": PrimaryEmotion.ANTICIPATION,
                "heyecanlı": PrimaryEmotion.ANTICIPATION,
                # Surprise
                "surprising": PrimaryEmotion.SURPRISE,
                "unique": PrimaryEmotion.SURPRISE,
                "şaşırtıcı": PrimaryEmotion.SURPRISE,
            }

            for emotion in emotions:
                emotion_lower = emotion.lower()
                if emotion_lower in emotion_mapping:
                    primary = emotion_mapping[emotion_lower]
                    framework.entry_emotion = EmotionMapping(
                        emotion=primary,
                        description=f"Initial {primary.value} from design",
                    )
                    break

        # Set tone from keywords
        tones = parsed.entities.tone_keywords
        if tones:
            tone_lower = " ".join(tones).lower()
            if "professional" in tone_lower or "corporate" in tone_lower:
                framework.primary_tone = EmotionalTone.PROFESSIONAL
            elif "playful" in tone_lower or "fun" in tone_lower:
                framework.primary_tone = EmotionalTone.PLAYFUL
            elif "luxury" in tone_lower or "premium" in tone_lower:
                framework.primary_tone = EmotionalTone.LUXURIOUS
            elif "warm" in tone_lower or "friendly" in tone_lower:
                framework.primary_tone = EmotionalTone.WARM

        return framework

    def update_soul(
        self,
        soul: ProjectSoul,
        answer: str,
        gap_id: str,
    ) -> ProjectSoul:
        """
        Update a ProjectSoul with an answer to a gap.

        Args:
            soul: Existing ProjectSoul
            answer: User's answer
            gap_id: ID of the gap being resolved

        Returns:
            Updated ProjectSoul
        """
        # Find and resolve the gap
        if soul.gap_analysis:
            for gap in soul.gap_analysis.all_gaps:
                if gap.id == gap_id:
                    gap.resolve(answer, source="user")

                    # Update soul based on gap category
                    self._apply_answer(soul, gap, answer)
                    break

        # Recalculate phase
        self._update_phase(soul)

        return soul

    def _apply_answer(self, soul: ProjectSoul, gap: GapInfo, answer: str) -> None:
        """Apply an answer to the appropriate soul component."""
        from gemini_mcp.maestro.models.gap import GapCategory

        category = gap.category

        if category == GapCategory.TARGET_AUDIENCE:
            # Update audience
            soul.target_audience.persona_name = answer

        elif category == GapCategory.BRAND_IDENTITY:
            # Update visual or brand
            if "color" in gap.description.lower():
                soul.visual_language.palette.primary = answer

        elif category == GapCategory.VISUAL_STYLE:
            # Update visual language
            pass  # Complex update based on answer content

        elif category == GapCategory.EMOTIONAL_GOALS:
            # Update emotional framework
            pass

        # Log the update
        logger.debug(f"Applied answer to {category.value}: {answer[:50]}...")

    def _update_phase(self, soul: ProjectSoul) -> None:
        """Update soul phase based on current state."""
        if soul.gap_analysis:
            critical = soul.gap_analysis.critical_gaps
            unresolved = soul.gap_analysis.unresolved_gaps

            if critical:
                soul.current_phase = InterviewPhase.CONTEXT_GATHERING
            elif unresolved:
                soul.current_phase = InterviewPhase.DEEP_DIVE
            elif soul.confidence_scores.overall < 0.7:
                soul.current_phase = InterviewPhase.VALIDATION
            else:
                soul.current_phase = InterviewPhase.SYNTHESIS

    def get_next_question(self, soul: ProjectSoul) -> Optional[str]:
        """
        Get the next question to ask based on gaps.

        Args:
            soul: Current ProjectSoul

        Returns:
            Question string or None if complete
        """
        if not soul.gap_analysis:
            return None

        prioritized = soul.gap_analysis.get_priority_queue()
        unresolved = [g for g in prioritized if not g.is_resolved]

        if unresolved:
            return unresolved[0].suggested_question

        return None

    def is_complete(self, soul: ProjectSoul) -> bool:
        """
        Check if soul extraction is complete.

        Args:
            soul: ProjectSoul to check

        Returns:
            True if complete
        """
        if soul.gap_analysis:
            if soul.gap_analysis.critical_gaps:
                return False
            if soul.gap_analysis.high_priority_gaps:
                return False

        if soul.confidence_scores.overall < self._config.MIN_CONFIDENCE:
            return False

        return True
