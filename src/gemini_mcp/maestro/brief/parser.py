"""
MAESTRO v2 Brief Parser

Main orchestrator for parsing design briefs into structured data.
Combines NLPExtractor and BriefValidator to produce ParsedBrief.

The ParsedBrief is the input to SoulExtractor which generates ProjectSoul.

Pipeline:
    Brief (str) → BriefParser → ParsedBrief → SoulExtractor → ProjectSoul

Usage:
    >>> from gemini_mcp.maestro.brief import BriefParser
    >>> parser = BriefParser()
    >>> result = await parser.parse("Design a modern fintech dashboard...")
    >>> print(result.project_name)
    'Fintech Dashboard'
    >>> print(result.is_valid)
    True
"""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from gemini_mcp.maestro.brief.extractor import ExtractedEntities, NLPExtractor
from gemini_mcp.maestro.brief.validator import (
    BriefValidator,
    ValidationResult,
    ValidationSeverity,
)
from gemini_mcp.maestro.config import get_config


@dataclass
class ParsedBrief:
    """
    Structured representation of a parsed design brief.

    This is the primary output of BriefParser and serves as input
    to SoulExtractor for generating ProjectSoul.

    Attributes:
        raw_text: Original brief text
        project_name: Inferred project name
        entities: Extracted entities from NLP
        validation: Validation result
        language: Detected language ("tr" or "en")
        keywords: Key terms extracted
        summary: Brief summary for display
        hash: Content hash for caching
        parsed_at: Timestamp of parsing
        metadata: Additional metadata
    """

    raw_text: str
    project_name: str
    entities: ExtractedEntities
    validation: ValidationResult
    language: str = "en"
    keywords: List[str] = field(default_factory=list)
    summary: str = ""
    hash: str = ""
    parsed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Generate hash if not provided."""
        if not self.hash:
            self.hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate content hash for caching."""
        content = self.raw_text.strip().lower()
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @property
    def is_valid(self) -> bool:
        """Check if brief passed validation."""
        return self.validation.is_valid

    @property
    def quality_score(self) -> float:
        """Get quality score from validation."""
        return self.validation.quality_score

    @property
    def word_count(self) -> int:
        """Get word count."""
        return self.validation.word_count

    @property
    def entity_count(self) -> int:
        """Get entity count."""
        return self.validation.entity_count

    def get_design_hints(self) -> Dict[str, Any]:
        """
        Get design hints for AI agents.

        Returns a structured dict that can be injected into agent prompts.
        """
        hints = {
            "project_name": self.project_name,
            "language": self.language,
            "quality_level": self._get_quality_level(),
        }

        # Add entity-based hints
        if self.entities.project_type:
            hints["component_type"] = self.entities.project_type

        if self.entities.industry:
            hints["industry"] = self.entities.industry

        if self.entities.tone_keywords:
            hints["tone"] = self.entities.tone_keywords

        if self.entities.color_mentions:
            hints["colors"] = self.entities.color_mentions

        if self.entities.audience_signals:
            hints["audience"] = self.entities.audience_signals

        if self.entities.platform_mentions:
            hints["platforms"] = self.entities.platform_mentions

        return hints

    def _get_quality_level(self) -> str:
        """Get quality level string."""
        score = self.quality_score
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "basic"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "raw_text": self.raw_text,
            "project_name": self.project_name,
            "entities": self.entities.to_dict(),
            "validation": self.validation.to_dict(),
            "language": self.language,
            "keywords": self.keywords,
            "summary": self.summary,
            "hash": self.hash,
            "parsed_at": self.parsed_at.isoformat(),
            "metadata": self.metadata,
        }

    def to_prompt_context(self) -> str:
        """
        Generate context string for AI agents.

        Returns a formatted string suitable for injection into prompts.
        """
        lines = [
            "=== Parsed Design Brief ===",
            f"Project: {self.project_name}",
            f"Language: {self.language.upper()}",
            f"Quality: {self._get_quality_level().title()} ({self.quality_score:.0%})",
        ]

        if self.entities.project_type:
            lines.append(f"Type: {self.entities.project_type}")

        if self.entities.industry:
            lines.append(f"Industry: {self.entities.industry}")

        if self.entities.tone_keywords:
            lines.append(f"Tone: {', '.join(self.entities.tone_keywords)}")

        if self.entities.color_mentions:
            lines.append(f"Colors: {', '.join(self.entities.color_mentions)}")

        if self.entities.audience_signals:
            lines.append(f"Audience: {', '.join(self.entities.audience_signals)}")

        if self.entities.platform_mentions:
            lines.append(f"Platforms: {', '.join(self.entities.platform_mentions)}")

        if self.keywords:
            lines.append(f"Keywords: {', '.join(self.keywords[:10])}")

        if not self.is_valid:
            lines.append("")
            lines.append("⚠️ Validation Issues:")
            for issue in self.validation.issues[:3]:
                if issue.severity == ValidationSeverity.ERROR:
                    lines.append(f"  ❌ {issue.message}")
                else:
                    lines.append(f"  ⚠️ {issue.message}")

        if self.summary:
            lines.append("")
            lines.append(f"Summary: {self.summary}")

        return "\n".join(lines)


class BriefParser:
    """
    Main parser for design briefs.

    Orchestrates NLPExtractor and BriefValidator to produce
    a structured ParsedBrief ready for soul extraction.

    Example:
        >>> parser = BriefParser()
        >>> brief = await parser.parse("Design a modern fintech dashboard for young professionals")
        >>> print(brief.project_name)
        'Fintech Dashboard'
        >>> print(brief.entities.industry)
        'fintech'
        >>> print(brief.is_valid)
        True

    Sync Example:
        >>> parser = BriefParser()
        >>> brief = parser.parse_sync("Create a landing page")
        >>> print(brief.project_name)
        'Landing Page'
    """

    # Project name inference patterns
    PROJECT_TYPE_NAMES = {
        "dashboard": "Dashboard",
        "landing": "Landing Page",
        "landing_page": "Landing Page",
        "form": "Form",
        "login": "Login",
        "signup": "Signup",
        "auth": "Authentication",
        "pricing": "Pricing Page",
        "blog": "Blog",
        "portfolio": "Portfolio",
        "e-commerce": "E-Commerce",
        "ecommerce": "E-Commerce",
        "admin": "Admin Panel",
        "settings": "Settings",
        "profile": "Profile",
        "checkout": "Checkout",
        "cart": "Shopping Cart",
        "product": "Product Page",
    }

    # Industry name mappings
    INDUSTRY_NAMES = {
        "fintech": "Fintech",
        "finance": "Finance",
        "banking": "Banking",
        "healthcare": "Healthcare",
        "health": "Health",
        "education": "Education",
        "ecommerce": "E-Commerce",
        "e-commerce": "E-Commerce",
        "retail": "Retail",
        "saas": "SaaS",
        "technology": "Technology",
        "tech": "Tech",
        "real_estate": "Real Estate",
        "travel": "Travel",
        "food": "Food & Beverage",
        "logistics": "Logistics",
        "media": "Media",
        "entertainment": "Entertainment",
    }

    def __init__(
        self,
        extractor: Optional[NLPExtractor] = None,
        validator: Optional[BriefValidator] = None,
    ):
        """
        Initialize parser with optional custom extractor and validator.

        Args:
            extractor: Custom NLPExtractor instance
            validator: Custom BriefValidator instance
        """
        self._extractor = extractor or NLPExtractor()
        self._validator = validator or BriefValidator()
        self._config = get_config()

    async def parse(self, brief: str) -> ParsedBrief:
        """
        Parse a design brief asynchronously.

        Args:
            brief: The design brief text

        Returns:
            ParsedBrief with structured data

        Note:
            This is async for future Gemini API integration.
            Currently wraps sync implementation.
        """
        # For MVP, parsing is synchronous
        # Future: Use Gemini API for advanced extraction
        return self.parse_sync(brief)

    def parse_sync(self, brief: str) -> ParsedBrief:
        """
        Parse a design brief synchronously.

        Args:
            brief: The design brief text

        Returns:
            ParsedBrief with structured data
        """
        # Normalize input
        brief = brief.strip() if brief else ""

        # Extract entities
        entities = self._extractor.extract(brief)

        # Validate brief
        validation = self._validator.validate(brief, entities)

        # Infer project name
        project_name = self._infer_project_name(brief, entities)

        # Extract keywords
        keywords = self._extract_keywords(brief)

        # Generate summary
        summary = self._generate_summary(brief, entities)

        # Build ParsedBrief
        return ParsedBrief(
            raw_text=brief,
            project_name=project_name,
            entities=entities,
            validation=validation,
            language=validation.detected_language,
            keywords=keywords,
            summary=summary,
            metadata={
                "extractor_confidence": entities.confidence,
                "validation_quality": validation.quality_score,
                "parser_version": "2.0.0",
            },
        )

    def _infer_project_name(self, brief: str, entities: ExtractedEntities) -> str:
        """
        Infer a project name from the brief.

        Uses project type and industry to generate a meaningful name.
        """
        parts = []

        # Add industry if available
        if entities.industry:
            industry_name = self.INDUSTRY_NAMES.get(
                entities.industry.lower(),
                entities.industry.title()
            )
            parts.append(industry_name)

        # Add project type
        if entities.project_type:
            type_name = self.PROJECT_TYPE_NAMES.get(
                entities.project_type.lower(),
                entities.project_type.replace("_", " ").title()
            )
            parts.append(type_name)
        else:
            # Default to "Design Project" if no type found
            parts.append("Design Project")

        return " ".join(parts)

    def _extract_keywords(self, brief: str) -> List[str]:
        """
        Extract key terms from the brief.

        Uses simple TF-based extraction for MVP.
        Future: Use KeyBERT or Gemini for better extraction.
        """
        # Normalize
        text = brief.lower()

        # Remove common stop words
        stop_words = {
            "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "this", "that", "these", "those", "i", "you", "he", "she", "it", "we",
            "they", "me", "him", "her", "us", "them", "my", "your", "his", "her",
            "its", "our", "their", "what", "which", "who", "whom", "when", "where",
            "why", "how", "all", "each", "every", "both", "few", "more", "most",
            "other", "some", "such", "no", "not", "only", "own", "same", "so",
            "than", "too", "very", "just", "also", "now", "here", "there",
            # Turkish stop words
            "bir", "bu", "şu", "o", "ve", "veya", "ama", "için", "ile", "de", "da",
            "ki", "ne", "nasıl", "neden", "nerede", "ne zaman", "gibi", "kadar",
            "daha", "en", "çok", "az", "hiç", "her", "tüm", "bazı", "biri",
        }

        # Extract words
        words = re.findall(r'\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{3,}\b', text)

        # Filter stop words
        keywords = [w for w in words if w not in stop_words]

        # Count frequency
        word_counts: Dict[str, int] = {}
        for word in keywords:
            word_counts[word] = word_counts.get(word, 0) + 1

        # Sort by frequency and take top 20
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:20]]

    def _generate_summary(self, brief: str, entities: ExtractedEntities) -> str:
        """
        Generate a brief summary.

        Creates a concise summary based on extracted entities.
        """
        parts = []

        if entities.project_type:
            parts.append(entities.project_type.replace("_", " ").title())

        if entities.industry:
            parts.append(f"for {entities.industry}")

        if entities.tone_keywords:
            tone = entities.tone_keywords[0] if len(entities.tone_keywords) == 1 else \
                   f"{entities.tone_keywords[0]} and {entities.tone_keywords[1]}"
            parts.append(f"with {tone} style")

        if entities.audience_signals:
            audience = entities.audience_signals[0]
            parts.append(f"targeting {audience}")

        if parts:
            return " ".join(parts)

        # Fallback: First sentence of brief
        sentences = re.split(r'[.!?]', brief)
        if sentences:
            first = sentences[0].strip()
            if len(first) > 100:
                first = first[:100] + "..."
            return first

        return "Design project"

    def validate_only(self, brief: str) -> ValidationResult:
        """
        Validate a brief without full parsing.

        Useful for quick validation before committing to full parse.

        Args:
            brief: The design brief text

        Returns:
            ValidationResult
        """
        entities = self._extractor.extract(brief)
        return self._validator.validate(brief, entities)

    def extract_only(self, brief: str) -> ExtractedEntities:
        """
        Extract entities without validation.

        Useful for quick entity extraction.

        Args:
            brief: The design brief text

        Returns:
            ExtractedEntities
        """
        return self._extractor.extract(brief)


# Convenience functions
def parse_brief(brief: str) -> ParsedBrief:
    """
    Quick parsing of a design brief.

    Args:
        brief: The design brief text

    Returns:
        ParsedBrief

    Example:
        >>> result = parse_brief("Design a modern dashboard for fintech")
        >>> print(result.project_name)
        'Fintech Dashboard'
    """
    parser = BriefParser()
    return parser.parse_sync(brief)


async def parse_brief_async(brief: str) -> ParsedBrief:
    """
    Async parsing of a design brief.

    Args:
        brief: The design brief text

    Returns:
        ParsedBrief
    """
    parser = BriefParser()
    return await parser.parse(brief)
