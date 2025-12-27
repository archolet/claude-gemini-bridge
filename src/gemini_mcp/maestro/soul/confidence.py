"""
MAESTRO v2 Confidence Calculator

Multi-dimensional confidence scoring for ProjectSoul extraction.
Measures how confident we are in the extracted design parameters.

6 Confidence Dimensions:
1. intent_clarity - How clear is the user's intent?
2. scope_match - Does the brief match available design capabilities?
3. context_richness - How much context is available?
4. parameter_completeness - Are key parameters specified?
5. constraint_satisfaction - Can constraints be satisfied?
6. alternative_viability - Are there viable alternative interpretations?

Usage:
    >>> from gemini_mcp.maestro.soul.confidence import ConfidenceCalculator
    >>> calculator = ConfidenceCalculator()
    >>> scores = calculator.calculate(parsed_brief, entities)
    >>> print(scores.overall)
    0.75
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from gemini_mcp.maestro.brief.parser import ParsedBrief
from gemini_mcp.maestro.brief.extractor import ExtractedEntities
from gemini_mcp.maestro.models.soul import ConfidenceScores


@dataclass
class DimensionScore:
    """
    Score for a single confidence dimension.

    Attributes:
        dimension: Name of the dimension
        score: 0.0-1.0 score
        weight: Weight for overall calculation
        factors: Contributing factors with their scores
        notes: Explanatory notes
    """

    dimension: str
    score: float
    weight: float = 1.0
    factors: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "dimension": self.dimension,
            "score": round(self.score, 3),
            "weight": self.weight,
            "factors": {k: round(v, 3) for k, v in self.factors.items()},
            "notes": self.notes,
        }


class ConfidenceCalculator:
    """
    Calculates multi-dimensional confidence scores for soul extraction.

    Uses weighted scoring across 6 dimensions to produce an overall
    confidence score and dimension-specific breakdowns.

    Example:
        >>> calc = ConfidenceCalculator()
        >>> scores = calc.calculate(parsed_brief)
        >>> print(scores.overall)
        0.72
        >>> print(scores.intent_clarity)
        0.85
    """

    # Dimension weights (must sum to 1.0)
    DIMENSION_WEIGHTS = {
        "intent_clarity": 0.20,
        "scope_match": 0.15,
        "context_richness": 0.20,
        "parameter_completeness": 0.20,
        "constraint_satisfaction": 0.10,
        "alternative_viability": 0.15,
    }

    # Supported component types for scope matching
    SUPPORTED_COMPONENTS = {
        "dashboard", "landing", "landing_page", "form", "login", "signup",
        "auth", "pricing", "blog", "portfolio", "ecommerce", "e-commerce",
        "admin", "settings", "profile", "checkout", "cart", "product",
        "hero", "navbar", "footer", "sidebar", "card", "modal", "table",
        "button", "input", "tabs", "accordion", "carousel",
    }

    # Supported themes
    SUPPORTED_THEMES = {
        "modern-minimal", "brutalist", "glassmorphism", "neo-brutalism",
        "soft-ui", "corporate", "gradient", "cyberpunk", "retro",
        "pastel", "dark_mode_first", "high_contrast", "nature", "startup",
    }

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        min_confidence: float = 0.4,
    ):
        """
        Initialize calculator.

        Args:
            weights: Custom dimension weights (optional)
            min_confidence: Minimum confidence threshold
        """
        self.weights = weights or self.DIMENSION_WEIGHTS
        self.min_confidence = min_confidence

        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            # Normalize if not summing to 1
            self.weights = {k: v / total for k, v in self.weights.items()}

    def calculate(
        self,
        brief: ParsedBrief,
        entities: Optional[ExtractedEntities] = None,
    ) -> ConfidenceScores:
        """
        Calculate confidence scores for a parsed brief.

        Args:
            brief: Parsed design brief
            entities: Extracted entities (optional, uses brief.entities if not provided)

        Returns:
            ConfidenceScores model instance
        """
        entities = entities or brief.entities

        # Calculate each dimension
        dimensions = {
            "intent_clarity": self._calc_intent_clarity(brief, entities),
            "scope_match": self._calc_scope_match(brief, entities),
            "context_richness": self._calc_context_richness(brief, entities),
            "parameter_completeness": self._calc_parameter_completeness(brief, entities),
            "constraint_satisfaction": self._calc_constraint_satisfaction(brief, entities),
            "alternative_viability": self._calc_alternative_viability(brief, entities),
        }

        # Calculate weighted overall score
        overall = sum(
            dimensions[dim].score * self.weights[dim]
            for dim in dimensions
        )

        return ConfidenceScores(
            overall=overall,
            intent_clarity=dimensions["intent_clarity"].score,
            scope_match=dimensions["scope_match"].score,
            context_richness=dimensions["context_richness"].score,
            parameter_completeness=dimensions["parameter_completeness"].score,
            constraint_satisfaction=dimensions["constraint_satisfaction"].score,
            alternative_viability=dimensions["alternative_viability"].score,
        )

    def calculate_detailed(
        self,
        brief: ParsedBrief,
        entities: Optional[ExtractedEntities] = None,
    ) -> Dict[str, DimensionScore]:
        """
        Calculate detailed dimension scores with factors.

        Args:
            brief: Parsed design brief
            entities: Extracted entities (optional)

        Returns:
            Dict mapping dimension names to DimensionScore objects
        """
        entities = entities or brief.entities

        return {
            "intent_clarity": self._calc_intent_clarity(brief, entities),
            "scope_match": self._calc_scope_match(brief, entities),
            "context_richness": self._calc_context_richness(brief, entities),
            "parameter_completeness": self._calc_parameter_completeness(brief, entities),
            "constraint_satisfaction": self._calc_constraint_satisfaction(brief, entities),
            "alternative_viability": self._calc_alternative_viability(brief, entities),
        }

    def _calc_intent_clarity(
        self,
        brief: ParsedBrief,
        entities: ExtractedEntities,
    ) -> DimensionScore:
        """
        Calculate intent clarity score.

        Measures how clearly the user's design intent is expressed.
        """
        factors = {}
        notes = []

        # Factor 1: Project type clarity (0.4 weight)
        if entities.project_type:
            factors["project_type"] = 1.0
        else:
            factors["project_type"] = 0.3
            notes.append("No clear project type specified")

        # Factor 2: Action verb presence (0.3 weight)
        action_verbs = {"create", "design", "build", "make", "develop", "implement"}
        action_verbs_tr = {"oluştur", "tasarla", "yap", "geliştir", "hazırla"}
        text_lower = brief.raw_text.lower()

        has_action = any(v in text_lower for v in action_verbs | action_verbs_tr)
        factors["action_verb"] = 1.0 if has_action else 0.5

        # Factor 3: Specificity (0.3 weight)
        # More specific terms = clearer intent
        word_count = brief.word_count
        if word_count >= 30:
            factors["specificity"] = 1.0
        elif word_count >= 15:
            factors["specificity"] = 0.7
        elif word_count >= 5:
            factors["specificity"] = 0.5
        else:
            factors["specificity"] = 0.2
            notes.append("Brief is very short, intent may be unclear")

        # Weighted score
        score = (
            factors["project_type"] * 0.4 +
            factors["action_verb"] * 0.3 +
            factors["specificity"] * 0.3
        )

        return DimensionScore(
            dimension="intent_clarity",
            score=score,
            weight=self.weights["intent_clarity"],
            factors=factors,
            notes=notes,
        )

    def _calc_scope_match(
        self,
        brief: ParsedBrief,
        entities: ExtractedEntities,
    ) -> DimensionScore:
        """
        Calculate scope match score.

        Measures how well the request matches available capabilities.
        """
        factors = {}
        notes = []

        # Factor 1: Component type match (0.5 weight)
        if entities.project_type:
            if entities.project_type.lower() in self.SUPPORTED_COMPONENTS:
                factors["component_match"] = 1.0
            else:
                factors["component_match"] = 0.6
                notes.append(f"Component '{entities.project_type}' may not be fully supported")
        else:
            factors["component_match"] = 0.5

        # Factor 2: Industry support (0.3 weight)
        supported_industries = {
            "fintech", "banking", "healthcare", "education", "ecommerce",
            "saas", "startup", "technology", "retail", "real_estate",
        }
        if entities.industry:
            if entities.industry.lower() in supported_industries:
                factors["industry_match"] = 1.0
            else:
                factors["industry_match"] = 0.7
        else:
            factors["industry_match"] = 0.6

        # Factor 3: Platform support (0.2 weight)
        if entities.platform_mentions:
            web_platforms = {"web", "desktop", "responsive", "mobile", "tablet"}
            if any(p.lower() in web_platforms for p in entities.platform_mentions):
                factors["platform_match"] = 1.0
            else:
                factors["platform_match"] = 0.7
                notes.append("Some platforms may have limited support")
        else:
            factors["platform_match"] = 0.8  # Assume web by default

        score = (
            factors["component_match"] * 0.5 +
            factors["industry_match"] * 0.3 +
            factors["platform_match"] * 0.2
        )

        return DimensionScore(
            dimension="scope_match",
            score=score,
            weight=self.weights["scope_match"],
            factors=factors,
            notes=notes,
        )

    def _calc_context_richness(
        self,
        brief: ParsedBrief,
        entities: ExtractedEntities,
    ) -> DimensionScore:
        """
        Calculate context richness score.

        Measures how much context is available for design decisions.
        """
        factors = {}
        notes = []

        # Factor 1: Entity count (0.4 weight)
        entity_count = brief.entity_count
        if entity_count >= 10:
            factors["entity_count"] = 1.0
        elif entity_count >= 6:
            factors["entity_count"] = 0.8
        elif entity_count >= 3:
            factors["entity_count"] = 0.6
        else:
            factors["entity_count"] = 0.3
            notes.append("Few entities extracted, context is limited")

        # Factor 2: Keyword diversity (0.3 weight)
        keyword_count = len(brief.keywords)
        if keyword_count >= 15:
            factors["keyword_diversity"] = 1.0
        elif keyword_count >= 8:
            factors["keyword_diversity"] = 0.7
        elif keyword_count >= 4:
            factors["keyword_diversity"] = 0.5
        else:
            factors["keyword_diversity"] = 0.3

        # Factor 3: Validation quality (0.3 weight)
        factors["validation_quality"] = brief.quality_score

        score = (
            factors["entity_count"] * 0.4 +
            factors["keyword_diversity"] * 0.3 +
            factors["validation_quality"] * 0.3
        )

        return DimensionScore(
            dimension="context_richness",
            score=score,
            weight=self.weights["context_richness"],
            factors=factors,
            notes=notes,
        )

    def _calc_parameter_completeness(
        self,
        brief: ParsedBrief,
        entities: ExtractedEntities,
    ) -> DimensionScore:
        """
        Calculate parameter completeness score.

        Measures whether key design parameters are specified.
        """
        factors = {}
        notes = []

        # Check each key parameter
        parameters = {
            "project_type": bool(entities.project_type),
            "industry": bool(entities.industry),
            "tone": bool(entities.tone_keywords),
            "colors": bool(entities.color_mentions),
            "audience": bool(entities.audience_signals),
            "emotions": bool(entities.emotion_keywords),
            "platform": bool(entities.platform_mentions),
        }

        # Calculate factor for each
        for param, present in parameters.items():
            factors[param] = 1.0 if present else 0.0

        # Note missing critical parameters
        critical = ["project_type", "industry", "tone"]
        for param in critical:
            if not parameters[param]:
                notes.append(f"Missing {param} parameter")

        # Score: weighted average (critical params have higher weight)
        weights = {
            "project_type": 0.25,
            "industry": 0.15,
            "tone": 0.15,
            "colors": 0.10,
            "audience": 0.15,
            "emotions": 0.10,
            "platform": 0.10,
        }

        score = sum(factors[p] * weights[p] for p in parameters)

        return DimensionScore(
            dimension="parameter_completeness",
            score=score,
            weight=self.weights["parameter_completeness"],
            factors=factors,
            notes=notes,
        )

    def _calc_constraint_satisfaction(
        self,
        brief: ParsedBrief,
        entities: ExtractedEntities,
    ) -> DimensionScore:
        """
        Calculate constraint satisfaction score.

        Measures whether specified constraints can be satisfied.
        """
        factors = {}
        notes = []

        # Constraint 1: Accessibility (always satisfiable)
        factors["accessibility"] = 1.0

        # Constraint 2: Responsive (always satisfiable)
        factors["responsive"] = 1.0

        # Constraint 3: Dark mode support (check if explicitly requested)
        text_lower = brief.raw_text.lower()
        if "dark" in text_lower or "koyu" in text_lower:
            factors["dark_mode"] = 1.0
        else:
            factors["dark_mode"] = 0.8  # Supported but not requested

        # Constraint 4: Performance (always satisfiable with Tailwind)
        factors["performance"] = 1.0

        # Constraint 5: Browser compatibility
        factors["browser_compat"] = 0.95  # Very high but not 100%

        # Check for unsatisfiable constraints
        unsatisfiable_patterns = [
            ("native app", "Native app development"),
            ("ios app", "iOS native app"),
            ("android app", "Android native app"),
            ("3d", "3D graphics"),
            ("webgl", "WebGL graphics"),
        ]

        for pattern, desc in unsatisfiable_patterns:
            if pattern in text_lower:
                factors["special_requirements"] = 0.5
                notes.append(f"{desc} may not be fully supported")
                break
        else:
            factors["special_requirements"] = 1.0

        score = sum(factors.values()) / len(factors)

        return DimensionScore(
            dimension="constraint_satisfaction",
            score=score,
            weight=self.weights["constraint_satisfaction"],
            factors=factors,
            notes=notes,
        )

    def _calc_alternative_viability(
        self,
        brief: ParsedBrief,
        entities: ExtractedEntities,
    ) -> DimensionScore:
        """
        Calculate alternative viability score.

        High score means we're confident in ONE interpretation.
        Low score means multiple valid interpretations exist.

        Note: Lower is actually better for flexibility, but we invert
        to make it consistent (higher = more confident).
        """
        factors = {}
        notes = []

        # Factor 1: Specificity of project type
        if entities.project_type:
            factors["type_specificity"] = 0.9
        else:
            factors["type_specificity"] = 0.4
            notes.append("Multiple project types could apply")

        # Factor 2: Clarity of tone
        if entities.tone_keywords and len(entities.tone_keywords) <= 2:
            factors["tone_clarity"] = 0.9
        elif entities.tone_keywords:
            factors["tone_clarity"] = 0.6  # Multiple tones = ambiguity
            notes.append("Multiple tones mentioned, may need clarification")
        else:
            factors["tone_clarity"] = 0.5

        # Factor 3: Consistency check
        # Check for contradictory terms
        contradictions = self._check_contradictions(brief.raw_text)
        if contradictions:
            factors["consistency"] = 0.4
            notes.extend(contradictions)
        else:
            factors["consistency"] = 1.0

        score = (
            factors["type_specificity"] * 0.4 +
            factors["tone_clarity"] * 0.3 +
            factors["consistency"] * 0.3
        )

        return DimensionScore(
            dimension="alternative_viability",
            score=score,
            weight=self.weights["alternative_viability"],
            factors=factors,
            notes=notes,
        )

    def _check_contradictions(self, text: str) -> List[str]:
        """Check for contradictory requirements."""
        contradictions = []
        text_lower = text.lower()

        pairs = [
            ("minimal", "complex"),
            ("simple", "feature-rich"),
            ("dark", "light"),
            ("modern", "retro"),
            ("professional", "playful"),
        ]

        for term1, term2 in pairs:
            if term1 in text_lower and term2 in text_lower:
                contradictions.append(f"Contradiction: '{term1}' vs '{term2}'")

        return contradictions

    def meets_threshold(self, scores: ConfidenceScores) -> bool:
        """
        Check if confidence meets minimum threshold.

        Args:
            scores: Calculated confidence scores

        Returns:
            True if overall confidence >= min_confidence
        """
        return scores.overall >= self.min_confidence

    def get_low_dimensions(
        self,
        scores: ConfidenceScores,
        threshold: float = 0.5,
    ) -> List[str]:
        """
        Get dimensions with low scores.

        Args:
            scores: Calculated confidence scores
            threshold: Score below which is considered low

        Returns:
            List of dimension names with low scores
        """
        low = []

        if scores.intent_clarity < threshold:
            low.append("intent_clarity")
        if scores.scope_match < threshold:
            low.append("scope_match")
        if scores.context_richness < threshold:
            low.append("context_richness")
        if scores.parameter_completeness < threshold:
            low.append("parameter_completeness")
        if scores.constraint_satisfaction < threshold:
            low.append("constraint_satisfaction")
        if scores.alternative_viability < threshold:
            low.append("alternative_viability")

        return low
