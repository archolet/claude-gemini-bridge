"""
Emotional Framework Model - Plutchik's Wheel of Emotions

Defines the emotional landscape of a design project using:
- Plutchik's 8 primary emotions
- Emotional intensity mapping
- User journey emotional arcs

Reference: Plutchik, R. (1980). A general psychoevolutionary theory of emotion.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PrimaryEmotion(str, Enum):
    """
    Plutchik's 8 primary emotions.

    These form the core emotional vocabulary for design decisions.
    Each emotion has design implications for color, typography, and motion.
    """

    JOY = "joy"  # Happiness, delight - Warm colors, rounded shapes
    TRUST = "trust"  # Confidence, reliability - Blues, clean lines
    FEAR = "fear"  # Anxiety, concern - Dark tones, sharp angles
    SURPRISE = "surprise"  # Unexpected, wonder - Vibrant accents, motion
    SADNESS = "sadness"  # Melancholy, reflection - Muted tones, soft edges
    DISGUST = "disgust"  # Rejection, avoidance - Rarely used in design
    ANGER = "anger"  # Urgency, power - Reds, bold typography
    ANTICIPATION = "anticipation"  # Excitement, expectation - Gradients, forward motion


class EmotionIntensity(str, Enum):
    """Intensity levels for emotional expression."""

    SUBTLE = "subtle"  # Barely perceptible, background emotion
    MODERATE = "moderate"  # Noticeable but balanced
    STRONG = "strong"  # Clearly expressed, dominant
    INTENSE = "intense"  # Overwhelming, primary focus


class EmotionalTone(str, Enum):
    """
    Overall emotional tone of the experience.

    Composite emotions derived from Plutchik's wheel combinations.
    """

    # Joy combinations
    OPTIMISTIC = "optimistic"  # Joy + Anticipation
    LOVING = "loving"  # Joy + Trust
    PLAYFUL = "playful"  # Joy + Surprise

    # Trust combinations
    ACCEPTING = "accepting"  # Trust + Joy
    SUBMISSIVE = "submissive"  # Trust + Fear (rarely used)

    # Fear combinations
    AWE = "awe"  # Fear + Surprise (wonder, respect)
    CAUTIOUS = "cautious"  # Fear + Anticipation

    # Surprise combinations
    CURIOUS = "curious"  # Surprise + Anticipation
    AMAZED = "amazed"  # Surprise + Joy

    # Anticipation combinations
    AGGRESSIVE = "aggressive"  # Anticipation + Anger (assertive, urgent)
    HOPEFUL = "hopeful"  # Anticipation + Trust

    # Professional tones
    PROFESSIONAL = "professional"  # Balanced trust + competence
    AUTHORITATIVE = "authoritative"  # Trust + controlled power
    INNOVATIVE = "innovative"  # Curiosity + anticipation

    # Neutral
    NEUTRAL = "neutral"  # No dominant emotion


class EmotionMapping(BaseModel):
    """
    Maps an emotion to design tokens.

    Provides concrete design recommendations for expressing
    a specific emotion in UI/UX.

    Example:
        >>> mapping = EmotionMapping(
        ...     emotion=PrimaryEmotion.JOY,
        ...     intensity=EmotionIntensity.MODERATE,
        ... )
        >>> mapping.get_color_hints()
        {'temperature': 'warm', 'saturation': 'high', 'suggested': ['#F59E0B', '#22C55E']}
    """

    emotion: PrimaryEmotion = Field(
        description="Birincil duygu",
    )
    intensity: EmotionIntensity = Field(
        default=EmotionIntensity.MODERATE,
        description="Duygu yoğunluğu",
    )
    context: Optional[str] = Field(
        default=None,
        description="Bu duygunun kullanılacağı bağlam (örn: 'onboarding', 'error_state')",
    )

    def get_color_hints(self) -> Dict:
        """
        Get color recommendations for this emotion.

        Returns color temperature, saturation, and suggested hex values.
        """
        emotion_colors = {
            PrimaryEmotion.JOY: {
                "temperature": "warm",
                "saturation": "high",
                "suggested": ["#F59E0B", "#22C55E", "#FBBF24"],
                "tailwind": ["amber-500", "green-500", "yellow-400"],
            },
            PrimaryEmotion.TRUST: {
                "temperature": "cool",
                "saturation": "medium",
                "suggested": ["#3B82F6", "#0EA5E9", "#6366F1"],
                "tailwind": ["blue-500", "sky-500", "indigo-500"],
            },
            PrimaryEmotion.FEAR: {
                "temperature": "cool",
                "saturation": "low",
                "suggested": ["#1E293B", "#334155", "#475569"],
                "tailwind": ["slate-800", "slate-700", "slate-600"],
            },
            PrimaryEmotion.SURPRISE: {
                "temperature": "neutral",
                "saturation": "very_high",
                "suggested": ["#EC4899", "#8B5CF6", "#06B6D4"],
                "tailwind": ["pink-500", "violet-500", "cyan-500"],
            },
            PrimaryEmotion.SADNESS: {
                "temperature": "cool",
                "saturation": "low",
                "suggested": ["#64748B", "#94A3B8", "#CBD5E1"],
                "tailwind": ["slate-500", "slate-400", "slate-300"],
            },
            PrimaryEmotion.DISGUST: {
                "temperature": "neutral",
                "saturation": "low",
                "suggested": ["#78716C", "#A8A29E", "#D6D3D1"],
                "tailwind": ["stone-500", "stone-400", "stone-300"],
            },
            PrimaryEmotion.ANGER: {
                "temperature": "warm",
                "saturation": "very_high",
                "suggested": ["#EF4444", "#DC2626", "#B91C1C"],
                "tailwind": ["red-500", "red-600", "red-700"],
            },
            PrimaryEmotion.ANTICIPATION: {
                "temperature": "warm",
                "saturation": "high",
                "suggested": ["#F97316", "#FB923C", "#FDBA74"],
                "tailwind": ["orange-500", "orange-400", "orange-300"],
            },
        }
        return emotion_colors.get(
            self.emotion,
            {"temperature": "neutral", "saturation": "medium", "suggested": []},
        )

    def get_motion_hints(self) -> Dict:
        """
        Get animation/motion recommendations for this emotion.

        Returns timing, easing, and effect suggestions.
        """
        intensity_timings = {
            EmotionIntensity.SUBTLE: {"duration": "300ms", "easing": "ease-out"},
            EmotionIntensity.MODERATE: {"duration": "200ms", "easing": "ease-in-out"},
            EmotionIntensity.STRONG: {"duration": "150ms", "easing": "ease-in"},
            EmotionIntensity.INTENSE: {"duration": "100ms", "easing": "linear"},
        }

        emotion_effects = {
            PrimaryEmotion.JOY: ["bounce", "scale", "fade-in"],
            PrimaryEmotion.TRUST: ["fade", "slide", "subtle-scale"],
            PrimaryEmotion.FEAR: ["shake", "pulse", "flash"],
            PrimaryEmotion.SURPRISE: ["pop", "zoom", "flip"],
            PrimaryEmotion.SADNESS: ["fade-slow", "slide-down", "blur"],
            PrimaryEmotion.DISGUST: ["none", "minimal"],
            PrimaryEmotion.ANGER: ["shake", "pulse-fast", "flash-red"],
            PrimaryEmotion.ANTICIPATION: ["slide-right", "progress", "pulse"],
        }

        return {
            **intensity_timings.get(self.intensity, {"duration": "200ms", "easing": "ease-out"}),
            "effects": emotion_effects.get(self.emotion, ["fade"]),
        }

    def get_typography_hints(self) -> Dict:
        """
        Get typography recommendations for this emotion.

        Returns weight, tracking, and style suggestions.
        """
        emotion_typography = {
            PrimaryEmotion.JOY: {
                "weight": "medium",
                "tracking": "normal",
                "style": "rounded",
            },
            PrimaryEmotion.TRUST: {
                "weight": "medium",
                "tracking": "normal",
                "style": "clean",
            },
            PrimaryEmotion.FEAR: {
                "weight": "light",
                "tracking": "wide",
                "style": "minimal",
            },
            PrimaryEmotion.SURPRISE: {
                "weight": "bold",
                "tracking": "tight",
                "style": "display",
            },
            PrimaryEmotion.SADNESS: {
                "weight": "light",
                "tracking": "normal",
                "style": "serif",
            },
            PrimaryEmotion.DISGUST: {
                "weight": "normal",
                "tracking": "normal",
                "style": "neutral",
            },
            PrimaryEmotion.ANGER: {
                "weight": "black",
                "tracking": "tight",
                "style": "condensed",
            },
            PrimaryEmotion.ANTICIPATION: {
                "weight": "semibold",
                "tracking": "normal",
                "style": "modern",
            },
        }
        return emotion_typography.get(
            self.emotion,
            {"weight": "normal", "tracking": "normal", "style": "clean"},
        )


class EmotionalFramework(BaseModel):
    """
    Complete emotional framework for a project.

    Defines the emotional strategy across the user journey,
    from initial impression to ongoing engagement.

    Example:
        >>> framework = EmotionalFramework(
        ...     primary_tone=EmotionalTone.OPTIMISTIC,
        ...     entry_emotion=EmotionMapping(emotion=PrimaryEmotion.JOY),
        ...     peak_emotion=EmotionMapping(emotion=PrimaryEmotion.SURPRISE, intensity=EmotionIntensity.STRONG),
        ... )
    """

    # Overall tone
    primary_tone: EmotionalTone = Field(
        default=EmotionalTone.PROFESSIONAL,
        description="Genel duygusal ton",
    )
    secondary_tone: Optional[EmotionalTone] = Field(
        default=None,
        description="İkincil duygusal ton (kontrast için)",
    )

    # Journey emotions
    entry_emotion: Optional[EmotionMapping] = Field(
        default=None,
        description="İlk izlenim duygusu (landing, hero)",
    )
    engagement_emotion: Optional[EmotionMapping] = Field(
        default=None,
        description="Etkileşim duygusu (aktif kullanım)",
    )
    peak_emotion: Optional[EmotionMapping] = Field(
        default=None,
        description="Doruk deneyim duygusu (başarı, tamamlama)",
    )
    exit_emotion: Optional[EmotionMapping] = Field(
        default=None,
        description="Çıkış duygusu (son izlenim)",
    )

    # Emotional targets by state
    state_emotions: Dict[str, EmotionMapping] = Field(
        default_factory=dict,
        description="Duruma özgü duygular (error, loading, success, vb.)",
    )

    # Brand emotion alignment
    brand_emotions: List[PrimaryEmotion] = Field(
        default_factory=list,
        description="Marka ile ilişkili duygular",
    )

    # Avoidance list
    emotions_to_avoid: List[PrimaryEmotion] = Field(
        default_factory=lambda: [PrimaryEmotion.FEAR, PrimaryEmotion.DISGUST, PrimaryEmotion.SADNESS],
        description="Kaçınılması gereken duygular",
    )

    # Confidence
    framework_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Framework çıkarım güveni",
    )

    def model_post_init(self, __context) -> None:
        """Set default state emotions if not provided."""
        default_state_emotions = {
            "loading": EmotionMapping(
                emotion=PrimaryEmotion.ANTICIPATION,
                intensity=EmotionIntensity.SUBTLE,
                context="loading",
            ),
            "success": EmotionMapping(
                emotion=PrimaryEmotion.JOY,
                intensity=EmotionIntensity.MODERATE,
                context="success",
            ),
            "error": EmotionMapping(
                emotion=PrimaryEmotion.SURPRISE,  # Not fear - surprise is less negative
                intensity=EmotionIntensity.MODERATE,
                context="error",
            ),
            "empty": EmotionMapping(
                emotion=PrimaryEmotion.ANTICIPATION,
                intensity=EmotionIntensity.SUBTLE,
                context="empty_state",
            ),
        }

        for state, emotion in default_state_emotions.items():
            if state not in self.state_emotions:
                self.state_emotions[state] = emotion

    def get_journey_arc(self) -> List[Dict]:
        """
        Get the emotional journey arc.

        Returns a sequence of emotion points suitable for visualization.
        """
        arc = []

        if self.entry_emotion:
            arc.append({
                "stage": "entry",
                "emotion": self.entry_emotion.emotion.value,
                "intensity": self.entry_emotion.intensity.value,
            })

        if self.engagement_emotion:
            arc.append({
                "stage": "engagement",
                "emotion": self.engagement_emotion.emotion.value,
                "intensity": self.engagement_emotion.intensity.value,
            })

        if self.peak_emotion:
            arc.append({
                "stage": "peak",
                "emotion": self.peak_emotion.emotion.value,
                "intensity": self.peak_emotion.intensity.value,
            })

        if self.exit_emotion:
            arc.append({
                "stage": "exit",
                "emotion": self.exit_emotion.emotion.value,
                "intensity": self.exit_emotion.intensity.value,
            })

        return arc

    def get_combined_design_hints(self) -> Dict:
        """
        Get aggregated design hints from all emotions.

        Returns consolidated color, motion, and typography hints.
        """
        hints = {
            "primary_colors": [],
            "motion_preference": "normal",
            "typography_weight": "medium",
        }

        # Collect from primary tone mapping
        tone_to_primary_emotion = {
            EmotionalTone.OPTIMISTIC: PrimaryEmotion.JOY,
            EmotionalTone.LOVING: PrimaryEmotion.JOY,
            EmotionalTone.PLAYFUL: PrimaryEmotion.JOY,
            EmotionalTone.ACCEPTING: PrimaryEmotion.TRUST,
            EmotionalTone.AWE: PrimaryEmotion.SURPRISE,
            EmotionalTone.CAUTIOUS: PrimaryEmotion.ANTICIPATION,
            EmotionalTone.CURIOUS: PrimaryEmotion.SURPRISE,
            EmotionalTone.AMAZED: PrimaryEmotion.SURPRISE,
            EmotionalTone.AGGRESSIVE: PrimaryEmotion.ANGER,
            EmotionalTone.HOPEFUL: PrimaryEmotion.ANTICIPATION,
            EmotionalTone.PROFESSIONAL: PrimaryEmotion.TRUST,
            EmotionalTone.AUTHORITATIVE: PrimaryEmotion.TRUST,
            EmotionalTone.INNOVATIVE: PrimaryEmotion.ANTICIPATION,
        }

        if self.primary_tone in tone_to_primary_emotion:
            primary_emotion = tone_to_primary_emotion[self.primary_tone]
            mapping = EmotionMapping(emotion=primary_emotion)
            color_hints = mapping.get_color_hints()
            hints["primary_colors"] = color_hints.get("suggested", [])

        return hints

    def to_prompt_context(self) -> str:
        """
        Generate prompt-ready context string for AI agents.

        Returns formatted string for inclusion in system prompts.
        """
        lines = [
            "Emotional Framework:",
            f"  Primary Tone: {self.primary_tone.value}",
        ]

        if self.secondary_tone:
            lines.append(f"  Secondary Tone: {self.secondary_tone.value}")

        if self.entry_emotion:
            lines.append(f"  Entry: {self.entry_emotion.emotion.value} ({self.entry_emotion.intensity.value})")

        if self.peak_emotion:
            lines.append(f"  Peak: {self.peak_emotion.emotion.value} ({self.peak_emotion.intensity.value})")

        if self.brand_emotions:
            lines.append(f"  Brand Emotions: {', '.join(e.value for e in self.brand_emotions[:3])}")

        if self.emotions_to_avoid:
            lines.append(f"  Avoid: {', '.join(e.value for e in self.emotions_to_avoid[:3])}")

        return "\n".join(lines)
