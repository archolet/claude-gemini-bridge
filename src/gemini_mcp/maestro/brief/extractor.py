"""
NLP Extractor - Entity Extraction from Design Briefs

Uses regex patterns for MVP, with optional Gemini enhancement.
Extracts:
- Project name and type
- Target audience hints
- Color preferences
- Industry keywords
- Tone/personality indicators

This is a regex-based MVP. Gemini-powered extraction is available
when USE_GEMINI_FOR_EXTRACTION=true in config.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from gemini_mcp.maestro.config import get_config


@dataclass
class ExtractedEntities:
    """
    Container for entities extracted from a design brief.

    All fields are optional since extraction may not find all entities.

    Example:
        >>> entities = ExtractedEntities(
        ...     project_name="TechCorp Dashboard",
        ...     project_type="dashboard",
        ...     industry="fintech",
        ... )
    """

    # Project identification
    project_name: Optional[str] = None
    project_type: Optional[str] = None
    tagline: Optional[str] = None

    # Industry & context
    industry: Optional[str] = None
    industry_keywords: List[str] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)

    # Audience hints
    audience_age_hints: List[str] = field(default_factory=list)
    audience_profession_hints: List[str] = field(default_factory=list)
    audience_tech_level: Optional[str] = None

    # Visual preferences
    color_mentions: List[str] = field(default_factory=list)
    style_keywords: List[str] = field(default_factory=list)
    reference_sites: List[str] = field(default_factory=list)

    # Tone & personality
    tone_keywords: List[str] = field(default_factory=list)
    personality_hints: List[str] = field(default_factory=list)

    # Emotional hints
    emotion_keywords: List[str] = field(default_factory=list)

    # Constraints
    platform_hints: List[str] = field(default_factory=list)
    language_hints: List[str] = field(default_factory=list)
    accessibility_mentions: bool = False

    # Extraction metadata
    extraction_confidence: float = 0.0
    raw_text_length: int = 0
    matched_patterns: int = 0

    # =========================================================================
    # COMPUTED PROPERTIES (Backward Compatibility)
    # =========================================================================

    @property
    def audience_signals(self) -> List[str]:
        """
        Combined audience signals from age and profession hints.

        This is a computed property for backward compatibility with code
        that expects an `audience_signals` attribute.
        """
        return self.audience_age_hints + self.audience_profession_hints

    @property
    def platform_mentions(self) -> List[str]:
        """
        Alias for platform_hints.

        This is a computed property for backward compatibility with code
        that expects a `platform_mentions` attribute.
        """
        return self.platform_hints

    @property
    def confidence(self) -> float:
        """
        Alias for extraction_confidence.

        This is a computed property for backward compatibility with code
        that expects a `confidence` attribute.
        """
        return self.extraction_confidence

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "project_name": self.project_name,
            "project_type": self.project_type,
            "tagline": self.tagline,
            "industry": self.industry,
            "industry_keywords": self.industry_keywords,
            "competitors": self.competitors,
            "audience_age_hints": self.audience_age_hints,
            "audience_profession_hints": self.audience_profession_hints,
            "audience_tech_level": self.audience_tech_level,
            "color_mentions": self.color_mentions,
            "style_keywords": self.style_keywords,
            "reference_sites": self.reference_sites,
            "tone_keywords": self.tone_keywords,
            "personality_hints": self.personality_hints,
            "emotion_keywords": self.emotion_keywords,
            "platform_hints": self.platform_hints,
            "language_hints": self.language_hints,
            "accessibility_mentions": self.accessibility_mentions,
            "extraction_confidence": self.extraction_confidence,
        }


class NLPExtractor:
    """
    Extracts structured entities from design brief text.

    Uses regex patterns for MVP extraction. Patterns are designed to catch
    common phrases in both Turkish and English design briefs.

    Example:
        >>> extractor = NLPExtractor()
        >>> entities = extractor.extract("Design a modern fintech dashboard for young professionals")
        >>> entities.project_type
        'dashboard'
        >>> entities.industry
        'fintech'
    """

    def __init__(self):
        """Initialize the extractor with pattern definitions."""
        self._init_patterns()

    def _init_patterns(self):
        """Initialize regex patterns for entity extraction."""

        # Project type patterns (Turkish + English)
        self.project_type_patterns = {
            "landing_page": [
                r"\blanding\s*page\b",
                r"\blanding\b",
                r"\bana\s*sayfa\b",
                r"\bkarşılama\s*sayfası\b",
            ],
            "dashboard": [
                r"\bdashboard\b",
                r"\bpanel\b",
                r"\bkontrol\s*paneli\b",
                r"\byönetim\s*paneli\b",
            ],
            "e-commerce": [
                r"\be-commerce\b",
                r"\becommerce\b",
                r"\bonline\s*store\b",
                r"\be-ticaret\b",
                r"\bonline\s*mağaza\b",
            ],
            "blog": [
                r"\bblog\b",
                r"\bblog\s*sayfası\b",
            ],
            "portfolio": [
                r"\bportfolio\b",
                r"\bportföy\b",
                r"\bshowcase\b",
            ],
            "saas": [
                r"\bsaas\b",
                r"\bweb\s*app\b",
                r"\buygulama\b",
                r"\bplatform\b",
            ],
            "mobile_app": [
                r"\bmobile\s*app\b",
                r"\bmobil\s*uygulama\b",
                r"\bios\b",
                r"\bandroid\b",
            ],
            "admin": [
                r"\badmin\b",
                r"\bbackend\b",
                r"\byönetici\b",
            ],
        }

        # Industry patterns
        self.industry_patterns = {
            "fintech": [r"\bfintech\b", r"\bfinans\b", r"\bbanking\b", r"\bbanka\b", r"\bödeme\b", r"\bpayment\b"],
            "healthcare": [r"\bhealthcare\b", r"\bsağlık\b", r"\bmedical\b", r"\btıbbi\b", r"\bhastane\b"],
            "education": [r"\beducation\b", r"\beğitim\b", r"\blearning\b", r"\böğrenme\b", r"\bschool\b", r"\bokul\b"],
            "e-commerce": [r"\be-commerce\b", r"\be-ticaret\b", r"\bshopping\b", r"\balışveriş\b", r"\bretail\b"],
            "real_estate": [r"\breal\s*estate\b", r"\bemlak\b", r"\bgayrimenkul\b", r"\bproperty\b"],
            "travel": [r"\btravel\b", r"\bseyahat\b", r"\bturizm\b", r"\btourism\b", r"\bhotel\b", r"\botel\b"],
            "food": [r"\bfood\b", r"\byemek\b", r"\brestaurant\b", r"\brestoran\b", r"\bcafe\b", r"\bkafe\b"],
            "tech": [r"\btech\b", r"\bteknoloji\b", r"\bsoftware\b", r"\byazılım\b", r"\bstartup\b"],
            "legal": [r"\blegal\b", r"\bhukuk\b", r"\blaw\b", r"\bavukat\b", r"\blawyer\b"],
            "consulting": [r"\bconsulting\b", r"\bdanışmanlık\b", r"\badvisory\b"],
        }

        # Tone/style patterns
        self.tone_patterns = {
            "professional": [r"\bprofessional\b", r"\bprofesyonel\b", r"\bkurumsal\b", r"\bcorporate\b"],
            "modern": [r"\bmodern\b", r"\bcontemporary\b", r"\bçağdaş\b", r"\bminimal\b", r"\bminimalist\b"],
            "playful": [r"\bplayful\b", r"\beğlenceli\b", r"\bfun\b", r"\bcolorful\b", r"\brenkli\b"],
            "luxury": [r"\bluxury\b", r"\blüks\b", r"\bpremium\b", r"\bhigh-end\b", r"\belegant\b", r"\belegant\b"],
            "trustworthy": [r"\btrust\b", r"\bgüven\b", r"\breliable\b", r"\bgüvenilir\b", r"\bsecure\b"],
            "innovative": [r"\binnovative\b", r"\byenilikçi\b", r"\bcutting-edge\b", r"\bileri teknoloji\b"],
            "friendly": [r"\bfriendly\b", r"\bsamimi\b", r"\bwarm\b", r"\bsıcak\b", r"\bwelcoming\b"],
            "bold": [r"\bbold\b", r"\bcesur\b", r"\bimpactful\b", r"\betkili\b", r"\bstriking\b"],
        }

        # Color patterns (hex and names)
        self.color_patterns = [
            r"#[0-9a-fA-F]{6}\b",  # Hex codes
            r"#[0-9a-fA-F]{3}\b",  # Short hex
            r"\b(mavi|blue|kırmızı|red|yeşil|green|sarı|yellow|turuncu|orange|mor|purple|pembe|pink|siyah|black|beyaz|white|gri|gray|grey)\b",
        ]

        # Audience patterns
        self.audience_patterns = {
            "young": [r"\byoung\b", r"\bgenç\b", r"\bmillennial\b", r"\bgen\s*z\b", r"\b18-35\b", r"\b20-40\b"],
            "professional": [r"\bprofessional\b", r"\bprofesyonel\b", r"\bbusiness\b", r"\biş\s*insanı\b"],
            "senior": [r"\bsenior\b", r"\byaşlı\b", r"\b50\+\b", r"\b60\+\b", r"\bretired\b", r"\bemekli\b"],
            "tech_savvy": [r"\btech\s*savvy\b", r"\bteknoloji\s*meraklısı\b", r"\bdeveloper\b", r"\bgeliştirici\b"],
            "general": [r"\beveryone\b", r"\bherkes\b", r"\bgeneral\s*public\b", r"\bgenel\s*kitle\b"],
        }

        # Emotion patterns (Plutchik-aligned)
        self.emotion_patterns = {
            "joy": [r"\bhappy\b", r"\bmutlu\b", r"\bjoyful\b", r"\bneşeli\b", r"\bdelightful\b"],
            "trust": [r"\btrust\b", r"\bgüven\b", r"\breliable\b", r"\bgüvenilir\b", r"\bsafe\b", r"\bgüvenli\b"],
            "anticipation": [r"\bexciting\b", r"\bheyecanlı\b", r"\banticipation\b", r"\bbeklenti\b"],
            "surprise": [r"\bsurprise\b", r"\bşaşırtıcı\b", r"\bunexpected\b", r"\bbeklenmedik\b"],
        }

        # Platform patterns
        self.platform_patterns = [
            (r"\bdesktop\b", "desktop"),
            (r"\bmobile\b", "mobile"),
            (r"\btablet\b", "tablet"),
            (r"\bresponsive\b", "responsive"),
            (r"\bweb\b", "web"),
            (r"\bios\b", "ios"),
            (r"\bandroid\b", "android"),
        ]

        # URL pattern for reference sites
        self.url_pattern = r"https?://[^\s<>\"{}|\\^`\[\]]+"

    def extract(self, text: str) -> ExtractedEntities:
        """
        Extract entities from design brief text.

        Args:
            text: The design brief text to analyze.

        Returns:
            ExtractedEntities with all found information.
        """
        if not text or not text.strip():
            return ExtractedEntities()

        # Normalize text
        normalized = text.lower()
        entities = ExtractedEntities(raw_text_length=len(text))
        matched = 0

        # Extract project type
        project_type, type_matched = self._extract_project_type(normalized)
        if project_type:
            entities.project_type = project_type
            matched += type_matched

        # Extract industry
        industry, industry_keywords, ind_matched = self._extract_industry(normalized)
        if industry:
            entities.industry = industry
            entities.industry_keywords = industry_keywords
            matched += ind_matched

        # Extract tone/style
        tone_keywords, tone_matched = self._extract_tone(normalized)
        entities.tone_keywords = tone_keywords
        matched += tone_matched

        # Extract colors
        colors, color_matched = self._extract_colors(text)  # Use original case for hex
        entities.color_mentions = colors
        matched += color_matched

        # Extract audience hints
        audience_hints, audience_matched = self._extract_audience(normalized)
        entities.audience_age_hints = audience_hints.get("age", [])
        entities.audience_profession_hints = audience_hints.get("profession", [])
        matched += audience_matched

        # Extract emotions
        emotions, emotion_matched = self._extract_emotions(normalized)
        entities.emotion_keywords = emotions
        matched += emotion_matched

        # Extract platforms
        platforms, platform_matched = self._extract_platforms(normalized)
        entities.platform_hints = platforms
        matched += platform_matched

        # Extract URLs
        urls = self._extract_urls(text)
        entities.reference_sites = urls

        # Check accessibility mentions
        entities.accessibility_mentions = self._check_accessibility(normalized)

        # Try to extract project name
        entities.project_name = self._extract_project_name(text)

        # Calculate confidence
        entities.matched_patterns = matched
        entities.extraction_confidence = self._calculate_confidence(entities)

        return entities

    def _extract_project_type(self, text: str) -> Tuple[Optional[str], int]:
        """Extract project type from text."""
        for ptype, patterns in self.project_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return ptype, 1
        return None, 0

    def _extract_industry(self, text: str) -> Tuple[Optional[str], List[str], int]:
        """Extract industry and related keywords."""
        found_industries = []
        keywords = []

        for industry, patterns in self.industry_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    if industry not in found_industries:
                        found_industries.append(industry)
                    # Extract the actual matched word
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        keywords.append(match.group())

        primary = found_industries[0] if found_industries else None
        return primary, keywords, len(found_industries)

    def _extract_tone(self, text: str) -> Tuple[List[str], int]:
        """Extract tone/style keywords."""
        found_tones = []

        for tone, patterns in self.tone_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    if tone not in found_tones:
                        found_tones.append(tone)
                    break

        return found_tones, len(found_tones)

    def _extract_colors(self, text: str) -> Tuple[List[str], int]:
        """Extract color mentions."""
        colors = []

        for pattern in self.color_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                color = match if isinstance(match, str) else match[0]
                if color.lower() not in [c.lower() for c in colors]:
                    colors.append(color)

        return colors, len(colors)

    def _extract_audience(self, text: str) -> Tuple[Dict[str, List[str]], int]:
        """Extract audience hints."""
        hints = {"age": [], "profession": []}
        matched = 0

        for category, patterns in self.audience_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    if category in ["young", "senior", "general"]:
                        if category not in hints["age"]:
                            hints["age"].append(category)
                    else:
                        if category not in hints["profession"]:
                            hints["profession"].append(category)
                    matched += 1
                    break

        return hints, matched

    def _extract_emotions(self, text: str) -> Tuple[List[str], int]:
        """Extract emotion keywords."""
        emotions = []

        for emotion, patterns in self.emotion_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    if emotion not in emotions:
                        emotions.append(emotion)
                    break

        return emotions, len(emotions)

    def _extract_platforms(self, text: str) -> Tuple[List[str], int]:
        """Extract platform hints."""
        platforms = []

        for pattern, platform in self.platform_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                if platform not in platforms:
                    platforms.append(platform)

        return platforms, len(platforms)

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs for reference sites."""
        urls = re.findall(self.url_pattern, text)
        return list(set(urls))[:5]  # Limit to 5 URLs

    def _check_accessibility(self, text: str) -> bool:
        """Check for accessibility mentions."""
        patterns = [
            r"\baccessibility\b",
            r"\berişilebilirlik\b",
            r"\bwcag\b",
            r"\ba11y\b",
            r"\bscreen\s*reader\b",
            r"\bekran\s*okuyucu\b",
            r"\baria\b",
        ]

        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _extract_project_name(self, text: str) -> Optional[str]:
        """
        Try to extract project name from text.

        Looks for patterns like:
        - "for [Company Name]"
        - "[Company] needs a..."
        - "için [Şirket Adı]"
        """
        patterns = [
            r"(?:for|için)\s+([A-ZÀ-ÿ][A-Za-zÀ-ÿ0-9\s&]+?)(?:\s+(?:needs|wants|we|bir|bir|landing|dashboard))",
            r"([A-ZÀ-ÿ][A-Za-zÀ-ÿ0-9\s&]{2,30}?)(?:\s+(?:landing|dashboard|web|app|site|sayfa|panel))",
            r"^([A-ZÀ-ÿ][A-Za-zÀ-ÿ0-9\s&]{2,30}?)\s+[-–—]",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # Clean up
                if len(name) >= 2 and len(name) <= 50:
                    return name

        return None

    def _calculate_confidence(self, entities: ExtractedEntities) -> float:
        """
        Calculate extraction confidence based on matched patterns.

        Higher confidence when more entities are found.
        """
        # Base score
        score = 0.3

        # Add for each extracted entity type
        if entities.project_type:
            score += 0.15
        if entities.industry:
            score += 0.15
        if entities.tone_keywords:
            score += 0.1
        if entities.color_mentions:
            score += 0.1
        if entities.audience_age_hints or entities.audience_profession_hints:
            score += 0.1
        if entities.platform_hints:
            score += 0.05
        if entities.project_name:
            score += 0.05

        # Bonus for rich text
        if entities.raw_text_length > 500:
            score += 0.05
        if entities.raw_text_length > 1000:
            score += 0.05

        return min(score, 1.0)
