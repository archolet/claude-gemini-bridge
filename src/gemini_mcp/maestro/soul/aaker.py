"""
MAESTRO v2 Aaker Brand Personality Analyzer

Implements Aaker's 5-dimension brand personality framework for
analyzing design briefs and extracting brand personality traits.

Aaker Framework Dimensions:
1. Sincerity - Down-to-earth, honest, wholesome, cheerful
2. Excitement - Daring, spirited, imaginative, up-to-date
3. Competence - Reliable, intelligent, successful
4. Sophistication - Upper-class, charming, elegant
5. Ruggedness - Outdoorsy, tough, strong

Reference:
    Aaker, J. L. (1997). Dimensions of Brand Personality.
    Journal of Marketing Research, 34(3), 347-356.

Usage:
    >>> from gemini_mcp.maestro.soul.aaker import AakerAnalyzer
    >>> analyzer = AakerAnalyzer()
    >>> scores = analyzer.analyze("modern, professional, reliable dashboard")
    >>> print(scores.dominant_trait)
    'competence'
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from gemini_mcp.maestro.models.brand import (
    BrandPersonality,
    PersonalityArchetype,
)


@dataclass
class AakerScores:
    """
    Raw Aaker dimension scores before normalization.

    Attributes:
        sincerity: Raw sincerity score
        excitement: Raw excitement score
        competence: Raw competence score
        sophistication: Raw sophistication score
        ruggedness: Raw ruggedness score
        matched_keywords: Keywords that contributed to scores
        confidence: Overall confidence in the analysis
    """

    sincerity: float = 0.0
    excitement: float = 0.0
    competence: float = 0.0
    sophistication: float = 0.0
    ruggedness: float = 0.0
    matched_keywords: Dict[str, List[str]] = field(default_factory=dict)
    confidence: float = 0.5

    def normalize(self) -> "AakerScores":
        """
        Normalize scores to 0-1 range.

        Returns a new AakerScores with normalized values.
        """
        max_score = max(
            self.sincerity,
            self.excitement,
            self.competence,
            self.sophistication,
            self.ruggedness,
            1.0,  # Prevent division by zero
        )

        return AakerScores(
            sincerity=self.sincerity / max_score,
            excitement=self.excitement / max_score,
            competence=self.competence / max_score,
            sophistication=self.sophistication / max_score,
            ruggedness=self.ruggedness / max_score,
            matched_keywords=self.matched_keywords,
            confidence=self.confidence,
        )

    @property
    def dominant_dimension(self) -> str:
        """Get the dominant personality dimension."""
        scores = {
            "sincerity": self.sincerity,
            "excitement": self.excitement,
            "competence": self.competence,
            "sophistication": self.sophistication,
            "ruggedness": self.ruggedness,
        }
        return max(scores, key=scores.get)

    @property
    def top_dimensions(self) -> List[Tuple[str, float]]:
        """Get dimensions sorted by score (descending)."""
        scores = [
            ("sincerity", self.sincerity),
            ("excitement", self.excitement),
            ("competence", self.competence),
            ("sophistication", self.sophistication),
            ("ruggedness", self.ruggedness),
        ]
        return sorted(scores, key=lambda x: x[1], reverse=True)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "sincerity": round(self.sincerity, 3),
            "excitement": round(self.excitement, 3),
            "competence": round(self.competence, 3),
            "sophistication": round(self.sophistication, 3),
            "ruggedness": round(self.ruggedness, 3),
            "dominant": self.dominant_dimension,
            "matched_keywords": self.matched_keywords,
            "confidence": round(self.confidence, 3),
        }


class AakerAnalyzer:
    """
    Analyzes text for Aaker brand personality dimensions.

    Uses keyword matching with weighted scores for MVP.
    Future: Use Gemini for semantic analysis.

    Example:
        >>> analyzer = AakerAnalyzer()
        >>> scores = analyzer.analyze("Create a professional, reliable dashboard")
        >>> print(scores.dominant_dimension)
        'competence'

        >>> personality = analyzer.to_brand_personality(scores)
        >>> print(personality.archetype)
        <PersonalityArchetype.THE_SAGE: 'the_sage'>
    """

    # Keyword weights: (keyword, weight)
    # Higher weights indicate stronger association

    # === SINCERITY ===
    # Down-to-earth, honest, wholesome, cheerful
    SINCERITY_KEYWORDS: Dict[str, float] = {
        # English
        "friendly": 1.0,
        "warm": 1.0,
        "welcoming": 1.0,
        "honest": 1.0,
        "authentic": 1.0,
        "genuine": 1.0,
        "sincere": 1.0,
        "trustworthy": 0.9,
        "reliable": 0.7,  # Also competence
        "simple": 0.8,
        "clean": 0.6,
        "minimal": 0.5,
        "cheerful": 0.9,
        "happy": 0.8,
        "joyful": 0.8,
        "positive": 0.7,
        "caring": 1.0,
        "helpful": 0.9,
        "community": 0.8,
        "family": 0.9,
        "home": 0.8,
        "natural": 0.7,
        "organic": 0.8,
        "sustainable": 0.7,
        "green": 0.6,
        "eco": 0.7,
        # Turkish
        "samimi": 1.0,
        "sıcak": 1.0,
        "dürüst": 1.0,
        "güvenilir": 0.8,
        "doğal": 0.8,
        "sade": 0.7,
        "temiz": 0.6,
        "mutlu": 0.8,
        "pozitif": 0.7,
        "aile": 0.9,
        "topluluk": 0.8,
    }

    # === EXCITEMENT ===
    # Daring, spirited, imaginative, up-to-date
    EXCITEMENT_KEYWORDS: Dict[str, float] = {
        # English
        "exciting": 1.0,
        "dynamic": 1.0,
        "bold": 1.0,
        "daring": 1.0,
        "innovative": 1.0,
        "creative": 0.9,
        "modern": 0.8,
        "trendy": 0.9,
        "cool": 0.8,
        "fun": 0.9,
        "playful": 1.0,
        "energetic": 1.0,
        "vibrant": 1.0,
        "colorful": 0.8,
        "animated": 0.8,
        "interactive": 0.7,
        "cutting-edge": 1.0,
        "futuristic": 0.9,
        "unique": 0.8,
        "fresh": 0.8,
        "young": 0.7,
        "youthful": 0.8,
        "startup": 0.8,
        "disruptive": 0.9,
        "experimental": 0.8,
        "adventurous": 0.9,
        # Turkish
        "heyecanlı": 1.0,
        "dinamik": 1.0,
        "yenilikçi": 1.0,
        "yaratıcı": 0.9,
        "modern": 0.8,
        "eğlenceli": 0.9,
        "enerjik": 1.0,
        "canlı": 0.9,
        "renkli": 0.8,
        "genç": 0.7,
        "taze": 0.8,
    }

    # === COMPETENCE ===
    # Reliable, intelligent, successful
    COMPETENCE_KEYWORDS: Dict[str, float] = {
        # English
        "professional": 1.0,
        "reliable": 1.0,
        "dependable": 1.0,
        "trustworthy": 0.9,
        "secure": 0.9,
        "safe": 0.8,
        "stable": 0.9,
        "robust": 0.9,
        "solid": 0.8,
        "quality": 0.8,
        "premium": 0.7,
        "expert": 1.0,
        "intelligent": 1.0,
        "smart": 0.9,
        "efficient": 0.9,
        "effective": 0.8,
        "successful": 1.0,
        "leading": 0.8,
        "enterprise": 0.9,
        "corporate": 0.9,
        "business": 0.8,
        "b2b": 0.8,
        "fintech": 0.9,
        "banking": 0.9,
        "finance": 0.9,
        "healthcare": 0.8,
        "technical": 0.8,
        "data-driven": 0.9,
        "analytical": 0.9,
        "dashboard": 0.7,
        "admin": 0.7,
        # Turkish
        "profesyonel": 1.0,
        "güvenli": 0.9,
        "sağlam": 0.9,
        "kaliteli": 0.8,
        "uzman": 1.0,
        "akıllı": 0.9,
        "verimli": 0.9,
        "kurumsal": 0.9,
        "iş": 0.7,
    }

    # === SOPHISTICATION ===
    # Upper-class, charming, elegant
    SOPHISTICATION_KEYWORDS: Dict[str, float] = {
        # English
        "elegant": 1.0,
        "sophisticated": 1.0,
        "luxury": 1.0,
        "luxurious": 1.0,
        "premium": 0.9,
        "exclusive": 0.9,
        "refined": 1.0,
        "polished": 0.9,
        "sleek": 0.9,
        "chic": 0.9,
        "stylish": 0.8,
        "fashionable": 0.8,
        "glamorous": 0.9,
        "charming": 0.8,
        "beautiful": 0.7,
        "aesthetic": 0.8,
        "minimal": 0.6,
        "minimalist": 0.7,
        "boutique": 0.9,
        "haute": 1.0,
        "prestige": 1.0,
        "upscale": 0.9,
        "high-end": 0.9,
        "designer": 0.8,
        "artisan": 0.8,
        "curated": 0.8,
        # Turkish
        "şık": 1.0,
        "zarif": 1.0,
        "lüks": 1.0,
        "premium": 0.9,
        "özel": 0.8,
        "sofistike": 1.0,
        "estetik": 0.8,
        "minimalist": 0.7,
        "butik": 0.9,
    }

    # === RUGGEDNESS ===
    # Outdoorsy, tough, strong
    RUGGEDNESS_KEYWORDS: Dict[str, float] = {
        # English
        "rugged": 1.0,
        "tough": 1.0,
        "strong": 1.0,
        "powerful": 0.9,
        "robust": 0.8,
        "durable": 0.9,
        "solid": 0.7,
        "sturdy": 0.9,
        "masculine": 0.8,
        "bold": 0.7,
        "industrial": 0.9,
        "outdoor": 1.0,
        "adventure": 0.9,
        "extreme": 0.8,
        "sport": 0.7,
        "athletic": 0.8,
        "active": 0.7,
        "military": 0.9,
        "tactical": 0.9,
        "brutalist": 0.8,
        "raw": 0.8,
        "unpolished": 0.7,
        "gritty": 0.8,
        "edgy": 0.7,
        "dark": 0.5,
        # Turkish
        "güçlü": 1.0,
        "sağlam": 0.9,
        "dayanıklı": 0.9,
        "cesur": 0.8,
        "endüstriyel": 0.9,
        "macera": 0.9,
        "spor": 0.7,
        "aktif": 0.7,
    }

    # Archetype mappings based on dominant traits
    ARCHETYPE_MAPPING: Dict[str, Dict[str, PersonalityArchetype]] = {
        "sincerity": {
            "primary": PersonalityArchetype.THE_CAREGIVER,
            "secondary": PersonalityArchetype.THE_EVERYMAN,
        },
        "excitement": {
            "primary": PersonalityArchetype.THE_MAGICIAN,
            "secondary": PersonalityArchetype.THE_REBEL,  # Changed from THE_JESTER (not defined)
        },
        "competence": {
            "primary": PersonalityArchetype.THE_SAGE,
            "secondary": PersonalityArchetype.THE_RULER,
        },
        "sophistication": {
            "primary": PersonalityArchetype.THE_LOVER,
            "secondary": PersonalityArchetype.THE_CREATOR,
        },
        "ruggedness": {
            "primary": PersonalityArchetype.THE_HERO,
            "secondary": PersonalityArchetype.THE_OUTLAW,
        },
    }

    def __init__(self, use_semantic: bool = False):
        """
        Initialize analyzer.

        Args:
            use_semantic: If True, use Gemini for semantic analysis (future)
        """
        self.use_semantic = use_semantic

    def analyze(self, text: str) -> AakerScores:
        """
        Analyze text for Aaker dimensions.

        Args:
            text: Text to analyze (brief, keywords, etc.)

        Returns:
            AakerScores with dimension values
        """
        if not text:
            return AakerScores(confidence=0.0)

        # Normalize text
        text_lower = text.lower()
        words = set(re.findall(r'\b[a-zA-ZçğıöşüÇĞİÖŞÜ]+\b', text_lower))

        # Calculate scores
        matched: Dict[str, List[str]] = {
            "sincerity": [],
            "excitement": [],
            "competence": [],
            "sophistication": [],
            "ruggedness": [],
        }

        sincerity = 0.0
        excitement = 0.0
        competence = 0.0
        sophistication = 0.0
        ruggedness = 0.0

        # Score each dimension
        for word in words:
            if word in self.SINCERITY_KEYWORDS:
                sincerity += self.SINCERITY_KEYWORDS[word]
                matched["sincerity"].append(word)

            if word in self.EXCITEMENT_KEYWORDS:
                excitement += self.EXCITEMENT_KEYWORDS[word]
                matched["excitement"].append(word)

            if word in self.COMPETENCE_KEYWORDS:
                competence += self.COMPETENCE_KEYWORDS[word]
                matched["competence"].append(word)

            if word in self.SOPHISTICATION_KEYWORDS:
                sophistication += self.SOPHISTICATION_KEYWORDS[word]
                matched["sophistication"].append(word)

            if word in self.RUGGEDNESS_KEYWORDS:
                ruggedness += self.RUGGEDNESS_KEYWORDS[word]
                matched["ruggedness"].append(word)

        # Calculate confidence based on matches
        total_matches = sum(len(v) for v in matched.values())
        if total_matches == 0:
            confidence = 0.3  # Low confidence, no matches
        elif total_matches < 3:
            confidence = 0.5  # Medium confidence
        elif total_matches < 6:
            confidence = 0.7  # Good confidence
        else:
            confidence = 0.9  # High confidence

        return AakerScores(
            sincerity=sincerity,
            excitement=excitement,
            competence=competence,
            sophistication=sophistication,
            ruggedness=ruggedness,
            matched_keywords=matched,
            confidence=confidence,
        )

    def to_brand_personality(
        self,
        scores: AakerScores,
        normalize: bool = True,
    ) -> BrandPersonality:
        """
        Convert AakerScores to BrandPersonality model.

        Args:
            scores: Raw or normalized scores
            normalize: Whether to normalize scores first

        Returns:
            BrandPersonality model instance
        """
        if normalize:
            scores = scores.normalize()

        # Get dominant trait
        dominant = scores.dominant_dimension

        # Get archetype
        archetype = self.ARCHETYPE_MAPPING[dominant]["primary"]

        # Build trait tags from matched keywords
        trait_tags = []
        for dimension, keywords in scores.matched_keywords.items():
            if keywords:
                trait_tags.extend(keywords[:2])  # Top 2 from each

        return BrandPersonality(
            sincerity=scores.sincerity,
            excitement=scores.excitement,
            competence=scores.competence,
            sophistication=scores.sophistication,
            ruggedness=scores.ruggedness,
            dominant_trait=dominant,
            archetype=archetype,
            trait_tags=trait_tags[:10],  # Limit to 10
            confidence=scores.confidence,
        )

    def analyze_to_personality(self, text: str) -> BrandPersonality:
        """
        Convenience method: Analyze text and return BrandPersonality directly.

        Args:
            text: Text to analyze

        Returns:
            BrandPersonality model instance
        """
        scores = self.analyze(text)
        return self.to_brand_personality(scores)

    def get_industry_baseline(self, industry: str) -> AakerScores:
        """
        Get baseline Aaker scores for an industry.

        Different industries have different personality expectations.

        Args:
            industry: Industry name (e.g., "fintech", "healthcare")

        Returns:
            Baseline AakerScores for the industry
        """
        baselines = {
            "fintech": AakerScores(
                sincerity=0.3, excitement=0.4, competence=0.9,
                sophistication=0.6, ruggedness=0.1, confidence=0.8
            ),
            "banking": AakerScores(
                sincerity=0.4, excitement=0.2, competence=0.95,
                sophistication=0.7, ruggedness=0.1, confidence=0.8
            ),
            "healthcare": AakerScores(
                sincerity=0.8, excitement=0.2, competence=0.9,
                sophistication=0.4, ruggedness=0.1, confidence=0.8
            ),
            "startup": AakerScores(
                sincerity=0.5, excitement=0.9, competence=0.6,
                sophistication=0.4, ruggedness=0.3, confidence=0.8
            ),
            "ecommerce": AakerScores(
                sincerity=0.5, excitement=0.6, competence=0.7,
                sophistication=0.5, ruggedness=0.2, confidence=0.8
            ),
            "luxury": AakerScores(
                sincerity=0.3, excitement=0.5, competence=0.6,
                sophistication=0.95, ruggedness=0.1, confidence=0.8
            ),
            "sports": AakerScores(
                sincerity=0.4, excitement=0.8, competence=0.5,
                sophistication=0.3, ruggedness=0.9, confidence=0.8
            ),
            "education": AakerScores(
                sincerity=0.7, excitement=0.5, competence=0.8,
                sophistication=0.4, ruggedness=0.1, confidence=0.8
            ),
        }

        return baselines.get(
            industry.lower(),
            # Default baseline (balanced)
            AakerScores(
                sincerity=0.5, excitement=0.5, competence=0.5,
                sophistication=0.5, ruggedness=0.5, confidence=0.5
            )
        )

    def blend_with_baseline(
        self,
        scores: AakerScores,
        industry: str,
        blend_ratio: float = 0.3,
    ) -> AakerScores:
        """
        Blend analyzed scores with industry baseline.

        Useful when brief doesn't specify strong personality.

        Args:
            scores: Analyzed scores from text
            industry: Industry for baseline
            blend_ratio: How much baseline to mix in (0-1)

        Returns:
            Blended AakerScores
        """
        baseline = self.get_industry_baseline(industry)
        inv_ratio = 1.0 - blend_ratio

        return AakerScores(
            sincerity=scores.sincerity * inv_ratio + baseline.sincerity * blend_ratio,
            excitement=scores.excitement * inv_ratio + baseline.excitement * blend_ratio,
            competence=scores.competence * inv_ratio + baseline.competence * blend_ratio,
            sophistication=scores.sophistication * inv_ratio + baseline.sophistication * blend_ratio,
            ruggedness=scores.ruggedness * inv_ratio + baseline.ruggedness * blend_ratio,
            matched_keywords=scores.matched_keywords,
            confidence=min(scores.confidence, baseline.confidence),
        )
