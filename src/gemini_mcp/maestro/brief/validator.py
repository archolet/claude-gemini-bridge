"""
MAESTRO v2 Brief Validator

Validates design brief structure, completeness, and quality.
Provides actionable suggestions for improving briefs.

Validation Rules:
    - Minimum length: 20 characters (configurable)
    - Required elements: At least 1 identifiable entity
    - Quality scoring: Based on entity diversity and specificity
    - Language detection: Turkish vs English

Usage:
    >>> from gemini_mcp.maestro.brief import BriefValidator, ValidationResult
    >>> validator = BriefValidator()
    >>> result = validator.validate("Design a fintech dashboard...")
    >>> if result.is_valid:
    ...     print("Brief is valid!")
    >>> else:
    ...     for issue in result.issues:
    ...         print(f"Issue: {issue}")
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set

from gemini_mcp.maestro.brief.extractor import ExtractedEntities, NLPExtractor


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    ERROR = "error"      # Must be fixed - blocks processing
    WARNING = "warning"  # Should be fixed - reduces quality
    INFO = "info"        # Nice to have - optional improvement


class ValidationCategory(Enum):
    """Categories of validation issues."""

    LENGTH = "length"
    STRUCTURE = "structure"
    CONTENT = "content"
    CLARITY = "clarity"
    SPECIFICITY = "specificity"
    LANGUAGE = "language"


@dataclass
class ValidationIssue:
    """
    A single validation issue found in the brief.

    Attributes:
        code: Unique identifier (e.g., "BRIEF_TOO_SHORT")
        message: Human-readable description
        severity: ERROR, WARNING, or INFO
        category: Type of issue
        suggestion: How to fix this issue
        details: Additional context (optional)
    """
    code: str
    message: str
    severity: ValidationSeverity
    category: ValidationCategory
    suggestion: str
    details: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "suggestion": self.suggestion,
            "details": self.details,
        }


@dataclass
class ValidationResult:
    """
    Result of brief validation.

    Attributes:
        is_valid: Whether the brief passes minimum requirements
        quality_score: 0.0-1.0 quality assessment
        issues: List of validation issues found
        suggestions: Actionable improvement suggestions
        detected_language: "tr", "en", or "unknown"
        entity_count: Number of entities extracted
        word_count: Total word count
    """
    is_valid: bool
    quality_score: float
    issues: List[ValidationIssue] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    detected_language: str = "unknown"
    entity_count: int = 0
    word_count: int = 0

    @property
    def error_count(self) -> int:
        """Count of ERROR severity issues."""
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of WARNING severity issues."""
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING)

    @property
    def has_errors(self) -> bool:
        """Check if there are any ERROR severity issues."""
        return self.error_count > 0

    def get_issues_by_category(self, category: ValidationCategory) -> List[ValidationIssue]:
        """Get all issues of a specific category."""
        return [i for i in self.issues if i.category == category]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "quality_score": self.quality_score,
            "issues": [i.to_dict() for i in self.issues],
            "suggestions": self.suggestions,
            "detected_language": self.detected_language,
            "entity_count": self.entity_count,
            "word_count": self.word_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
        }

    def get_summary(self) -> str:
        """Get human-readable summary."""
        status = "✅ Valid" if self.is_valid else "❌ Invalid"
        return (
            f"{status} | Quality: {self.quality_score:.0%} | "
            f"Errors: {self.error_count} | Warnings: {self.warning_count} | "
            f"Entities: {self.entity_count}"
        )


class BriefValidator:
    """
    Validates design briefs for completeness and quality.

    Performs structural and content validation, providing
    actionable suggestions for improvement.

    Example:
        >>> validator = BriefValidator(min_length=30)
        >>> result = validator.validate("Create a modern dashboard")
        >>> print(result.is_valid)
        True
        >>> print(result.quality_score)
        0.45
    """

    # Configurable thresholds
    DEFAULT_MIN_LENGTH = 20
    DEFAULT_MIN_WORDS = 5
    EXCELLENT_QUALITY_THRESHOLD = 0.8
    GOOD_QUALITY_THRESHOLD = 0.6

    # Quality weights for scoring
    QUALITY_WEIGHTS = {
        "entity_diversity": 0.30,   # Different types of entities
        "specificity": 0.25,        # Specific vs vague terms
        "completeness": 0.25,       # Core elements present
        "clarity": 0.20,            # Clear language, no ambiguity
    }

    # Turkish indicators
    TURKISH_INDICATORS = {
        "için", "ile", "ve", "bir", "bu", "oluştur", "tasarla",
        "modern", "şık", "profesyonel", "kullanıcı", "sayfa",
        "bileşen", "tema", "renk", "koyu", "açık", "responsive",
        "mobil", "masaüstü", "tablet", "uygulaması", "sistemi",
    }

    # Vague terms that reduce quality
    VAGUE_TERMS = {
        "nice", "good", "great", "cool", "awesome", "beautiful",
        "güzel", "iyi", "harika", "süper", "hoş", "şık",
        "something", "stuff", "thing", "bir şey", "şeyler",
    }

    # Specific terms that increase quality
    SPECIFIC_TERMS = {
        # Colors
        "blue", "red", "green", "purple", "orange", "teal", "cyan",
        "mavi", "kırmızı", "yeşil", "mor", "turuncu",
        # Industries
        "fintech", "e-commerce", "saas", "healthcare", "education",
        "banking", "retail", "logistics", "real estate",
        # Styles
        "minimal", "brutalist", "glassmorphism", "corporate", "startup",
        "modern", "retro", "futuristic", "elegant", "playful",
        # Components
        "dashboard", "landing", "form", "table", "chart", "navbar",
        "sidebar", "modal", "card", "button", "input",
    }

    def __init__(
        self,
        min_length: int = DEFAULT_MIN_LENGTH,
        min_words: int = DEFAULT_MIN_WORDS,
        strict_mode: bool = False,
    ):
        """
        Initialize validator with configuration.

        Args:
            min_length: Minimum character count
            min_words: Minimum word count
            strict_mode: If True, warnings become errors
        """
        self.min_length = min_length
        self.min_words = min_words
        self.strict_mode = strict_mode
        self._extractor = NLPExtractor()

    def validate(self, brief: str, entities: Optional[ExtractedEntities] = None) -> ValidationResult:
        """
        Validate a design brief.

        Args:
            brief: The design brief text
            entities: Pre-extracted entities (optional, will extract if not provided)

        Returns:
            ValidationResult with issues and quality score
        """
        issues: List[ValidationIssue] = []
        suggestions: List[str] = []

        # Normalize text
        brief = brief.strip() if brief else ""
        word_count = len(brief.split())

        # Extract entities if not provided
        if entities is None:
            entities = self._extractor.extract(brief)

        # Detect language
        language = self._detect_language(brief)

        # === Structural Validation ===

        # Check length
        if len(brief) < self.min_length:
            issues.append(ValidationIssue(
                code="BRIEF_TOO_SHORT",
                message=f"Brief is too short ({len(brief)} chars, minimum {self.min_length})",
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.LENGTH,
                suggestion="Provide more details about the design requirements",
                details={"actual": len(brief), "required": self.min_length},
            ))

        # Check word count
        if word_count < self.min_words:
            issues.append(ValidationIssue(
                code="BRIEF_TOO_FEW_WORDS",
                message=f"Brief has too few words ({word_count}, minimum {self.min_words})",
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.LENGTH,
                suggestion="Add more descriptive content to the brief",
                details={"actual": word_count, "required": self.min_words},
            ))

        # === Content Validation ===

        # Check entity count
        entity_count = self._count_entities(entities)
        if entity_count == 0:
            issues.append(ValidationIssue(
                code="NO_ENTITIES_FOUND",
                message="No identifiable design elements found",
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.CONTENT,
                suggestion="Include specific details like project type, industry, colors, or audience",
            ))
        elif entity_count < 3:
            issues.append(ValidationIssue(
                code="FEW_ENTITIES_FOUND",
                message=f"Only {entity_count} design elements identified",
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.CONTENT,
                suggestion="Add more specific details for better design results",
                details={"entity_count": entity_count},
            ))

        # Check for missing core elements
        missing_elements = self._check_missing_elements(entities)
        for element in missing_elements:
            severity = ValidationSeverity.WARNING
            if self.strict_mode:
                severity = ValidationSeverity.ERROR

            issues.append(ValidationIssue(
                code=f"MISSING_{element.upper()}",
                message=f"No {element} information found",
                severity=severity,
                category=ValidationCategory.COMPLETENESS if hasattr(ValidationCategory, 'COMPLETENESS') else ValidationCategory.CONTENT,
                suggestion=f"Consider specifying the {element} for your design",
            ))

        # === Clarity Validation ===

        # Check for vague terms
        vague_found = self._find_vague_terms(brief)
        if vague_found:
            issues.append(ValidationIssue(
                code="VAGUE_TERMS_FOUND",
                message=f"Brief contains vague terms: {', '.join(vague_found)}",
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.CLARITY,
                suggestion="Replace vague terms with specific requirements",
                details={"vague_terms": list(vague_found)},
            ))

        # Check for contradictions
        contradictions = self._detect_contradictions(brief)
        if contradictions:
            issues.append(ValidationIssue(
                code="CONTRADICTIONS_DETECTED",
                message="Brief contains potentially contradictory requirements",
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.CLARITY,
                suggestion="Clarify the conflicting requirements",
                details={"contradictions": contradictions},
            ))

        # === Calculate Quality Score ===
        quality_score = self._calculate_quality(brief, entities, entity_count)

        # === Generate Suggestions ===
        suggestions = self._generate_suggestions(
            brief, entities, entity_count, issues, language
        )

        # === Determine Validity ===
        # Valid if no ERROR severity issues
        is_valid = not any(i.severity == ValidationSeverity.ERROR for i in issues)

        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            issues=issues,
            suggestions=suggestions,
            detected_language=language,
            entity_count=entity_count,
            word_count=word_count,
        )

    def _detect_language(self, text: str) -> str:
        """Detect if text is Turkish or English."""
        text_lower = text.lower()
        words = set(text_lower.split())

        # Count Turkish indicators
        turkish_count = len(words & self.TURKISH_INDICATORS)

        # Check for Turkish characters
        turkish_chars = set("çğıöşüÇĞİÖŞÜ")
        has_turkish_chars = any(c in text for c in turkish_chars)

        if turkish_count >= 2 or has_turkish_chars:
            return "tr"

        return "en"

    def _count_entities(self, entities: ExtractedEntities) -> int:
        """Count total non-empty entities."""
        count = 0

        if entities.project_type:
            count += 1
        if entities.industry:
            count += 1
        if entities.tone_keywords:
            count += len(entities.tone_keywords)
        if entities.color_mentions:
            count += len(entities.color_mentions)
        if entities.audience_signals:
            count += len(entities.audience_signals)
        if entities.emotion_keywords:
            count += len(entities.emotion_keywords)
        if entities.platform_mentions:
            count += len(entities.platform_mentions)

        return count

    def _check_missing_elements(self, entities: ExtractedEntities) -> List[str]:
        """Check for missing core elements."""
        missing = []

        # Core elements that should ideally be present
        if not entities.project_type:
            missing.append("project type")
        if not entities.industry:
            missing.append("industry")
        if not entities.tone_keywords:
            missing.append("tone/style")
        if not entities.audience_signals:
            missing.append("target audience")

        return missing

    def _find_vague_terms(self, text: str) -> Set[str]:
        """Find vague terms in the text."""
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        return words & self.VAGUE_TERMS

    def _detect_contradictions(self, text: str) -> List[str]:
        """Detect potentially contradictory requirements."""
        contradictions = []
        text_lower = text.lower()

        # Contradiction patterns
        contradiction_pairs = [
            ("minimal", "complex"),
            ("simple", "feature-rich"),
            ("dark", "light"),
            ("modern", "retro"),
            ("professional", "playful"),
            ("corporate", "casual"),
            ("fast", "detailed"),
            ("minimalist", "maximalist"),
        ]

        for term1, term2 in contradiction_pairs:
            if term1 in text_lower and term2 in text_lower:
                contradictions.append(f"'{term1}' vs '{term2}'")

        return contradictions

    def _calculate_quality(
        self,
        text: str,
        entities: ExtractedEntities,
        entity_count: int,
    ) -> float:
        """Calculate quality score (0.0-1.0)."""
        scores = {}
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))

        # Entity diversity (0-1)
        # More diverse entity types = higher score
        entity_types = 0
        if entities.project_type:
            entity_types += 1
        if entities.industry:
            entity_types += 1
        if entities.tone_keywords:
            entity_types += 1
        if entities.color_mentions:
            entity_types += 1
        if entities.audience_signals:
            entity_types += 1
        if entities.emotion_keywords:
            entity_types += 1
        if entities.platform_mentions:
            entity_types += 1

        scores["entity_diversity"] = min(entity_types / 5, 1.0)  # Cap at 5 types

        # Specificity (0-1)
        # Ratio of specific terms to vague terms
        specific_count = len(words & self.SPECIFIC_TERMS)
        vague_count = len(words & self.VAGUE_TERMS)

        if specific_count + vague_count > 0:
            scores["specificity"] = specific_count / (specific_count + vague_count + 1)
        else:
            scores["specificity"] = 0.5  # Neutral if no terms found

        # Completeness (0-1)
        # Core elements present
        core_elements = ["project_type", "industry", "tone_keywords", "audience_signals"]
        present = 0
        if entities.project_type:
            present += 1
        if entities.industry:
            present += 1
        if entities.tone_keywords:
            present += 1
        if entities.audience_signals:
            present += 1

        scores["completeness"] = present / len(core_elements)

        # Clarity (0-1)
        # Based on sentence structure and contradiction absence
        word_count = len(text.split())
        avg_word_length = sum(len(w) for w in text.split()) / max(word_count, 1)

        # Penalize very short or very long average word length
        if 4 <= avg_word_length <= 8:
            clarity_base = 0.8
        elif 3 <= avg_word_length <= 10:
            clarity_base = 0.6
        else:
            clarity_base = 0.4

        # Penalize contradictions
        contradictions = self._detect_contradictions(text)
        clarity_penalty = len(contradictions) * 0.1

        scores["clarity"] = max(clarity_base - clarity_penalty, 0.0)

        # Calculate weighted average
        total_score = sum(
            scores[key] * self.QUALITY_WEIGHTS[key]
            for key in self.QUALITY_WEIGHTS
        )

        return min(max(total_score, 0.0), 1.0)

    def _generate_suggestions(
        self,
        text: str,
        entities: ExtractedEntities,
        entity_count: int,
        issues: List[ValidationIssue],
        language: str,
    ) -> List[str]:
        """Generate actionable improvement suggestions."""
        suggestions = []

        # Language-specific suggestions
        if language == "tr":
            if not entities.project_type:
                suggestions.append("Proje türünü belirtin (dashboard, landing page, form vb.)")
            if not entities.industry:
                suggestions.append("Sektörü belirtin (fintech, e-ticaret, sağlık vb.)")
            if not entities.color_mentions:
                suggestions.append("Renk tercihinizi belirtin (mavi, yeşil, koyu tema vb.)")
            if not entities.audience_signals:
                suggestions.append("Hedef kitleyi tanımlayın (genç profesyoneller, kurumsal kullanıcılar vb.)")
            if entity_count < 5:
                suggestions.append("Daha fazla detay ekleyerek tasarım kalitesini artırın")
        else:
            if not entities.project_type:
                suggestions.append("Specify the project type (dashboard, landing page, form, etc.)")
            if not entities.industry:
                suggestions.append("Mention the industry (fintech, e-commerce, healthcare, etc.)")
            if not entities.color_mentions:
                suggestions.append("Include color preferences (blue, green, dark theme, etc.)")
            if not entities.audience_signals:
                suggestions.append("Define the target audience (young professionals, enterprise users, etc.)")
            if entity_count < 5:
                suggestions.append("Add more specific details to improve design quality")

        # Add suggestions from issues
        for issue in issues:
            if issue.suggestion and issue.suggestion not in suggestions:
                # Avoid duplicates
                suggestions.append(issue.suggestion)

        # Limit suggestions
        return suggestions[:5]

    def get_quality_label(self, score: float) -> str:
        """Get human-readable quality label."""
        if score >= self.EXCELLENT_QUALITY_THRESHOLD:
            return "Excellent"
        elif score >= self.GOOD_QUALITY_THRESHOLD:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Needs Improvement"


# Convenience function
def validate_brief(brief: str, strict: bool = False) -> ValidationResult:
    """
    Quick validation of a design brief.

    Args:
        brief: The design brief text
        strict: If True, warnings become errors

    Returns:
        ValidationResult

    Example:
        >>> result = validate_brief("Design a modern fintech dashboard")
        >>> print(result.is_valid)
        True
    """
    validator = BriefValidator(strict_mode=strict)
    return validator.validate(brief)
