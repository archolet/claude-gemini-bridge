"""
MAESTRO v2 Configuration

Feature flags and configuration for the intelligent interview system.
Environment variables take precedence over defaults.

Usage:
    >>> from gemini_mcp.maestro.config import MAESTROConfig
    >>> config = get_config()
    >>> if config.V2_ENABLED:
    ...     # Use new soul-based interview
    >>> else:
    ...     # Fall back to static Q&A

Environment Variables:
    MAESTRO_V2_ENABLED: Enable/disable v2 features (default: true)
    MAESTRO_GRACEFUL_FALLBACK: Fall back to v1 on v2 errors (default: true)
    MAESTRO_EXTRACTION_TIMEOUT: Soul extraction timeout in seconds (default: 10)
    MAESTRO_MIN_CONFIDENCE: Minimum confidence to proceed (default: 0.6)
    MAESTRO_MAX_QUESTIONS: Maximum interview questions (default: 10)
    MAESTRO_DEBUG: Enable debug logging (default: false)
"""

import os
from dataclasses import dataclass, field
from typing import Optional

# Environment variable prefix
ENV_PREFIX = "MAESTRO_"


def _get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean from environment variable."""
    value = os.environ.get(f"{ENV_PREFIX}{key}", "").lower()
    if value in ("true", "1", "yes", "on"):
        return True
    if value in ("false", "0", "no", "off"):
        return False
    return default


def _get_env_int(key: str, default: int) -> int:
    """Get integer from environment variable."""
    value = os.environ.get(f"{ENV_PREFIX}{key}")
    if value is not None:
        try:
            return int(value)
        except ValueError:
            pass
    return default


def _get_env_float(key: str, default: float) -> float:
    """Get float from environment variable."""
    value = os.environ.get(f"{ENV_PREFIX}{key}")
    if value is not None:
        try:
            return float(value)
        except ValueError:
            pass
    return default


def _get_env_str(key: str, default: str = "") -> str:
    """Get string from environment variable."""
    return os.environ.get(f"{ENV_PREFIX}{key}", default)


@dataclass
class MAESTROConfig:
    """
    MAESTRO v2 configuration with feature flags.

    All settings can be overridden via environment variables with MAESTRO_ prefix.

    Example:
        >>> config = MAESTROConfig()
        >>> config.V2_ENABLED
        True
        >>> config.MIN_CONFIDENCE
        0.6

        # Override via environment:
        $ export MAESTRO_V2_ENABLED=false
        $ export MAESTRO_MIN_CONFIDENCE=0.8
    """

    # === Core Feature Flags ===

    V2_ENABLED: bool = field(
        default_factory=lambda: _get_env_bool("V2_ENABLED", default=True)
    )
    """Enable MAESTRO v2 soul-based interview system."""

    GRACEFUL_FALLBACK: bool = field(
        default_factory=lambda: _get_env_bool("GRACEFUL_FALLBACK", default=True)
    )
    """Fall back to v1 static Q&A on v2 errors."""

    DEBUG: bool = field(
        default_factory=lambda: _get_env_bool("DEBUG", default=False)
    )
    """Enable debug logging for MAESTRO operations."""

    # === Interview Settings ===

    MAX_QUESTIONS: int = field(
        default_factory=lambda: _get_env_int("MAX_QUESTIONS", default=10)
    )
    """Maximum number of interview questions before forcing completion."""

    MIN_CONFIDENCE: float = field(
        default_factory=lambda: _get_env_float("MIN_CONFIDENCE", default=0.6)
    )
    """Minimum confidence score to proceed with design (0.0-1.0)."""

    AUTO_APPLY_DEFAULTS: bool = field(
        default_factory=lambda: _get_env_bool("AUTO_APPLY_DEFAULTS", default=True)
    )
    """Automatically apply default values for unanswered questions."""

    # === Extraction Settings ===

    EXTRACTION_TIMEOUT: int = field(
        default_factory=lambda: _get_env_int("EXTRACTION_TIMEOUT", default=10)
    )
    """Soul extraction timeout in seconds."""

    USE_GEMINI_FOR_EXTRACTION: bool = field(
        default_factory=lambda: _get_env_bool("USE_GEMINI_FOR_EXTRACTION", default=True)
    )
    """Use Gemini API for NLP extraction (vs. regex-only MVP)."""

    EXTRACTION_MODEL: str = field(
        default_factory=lambda: _get_env_str("EXTRACTION_MODEL", default="gemini-2.0-flash")
    )
    """Model to use for soul extraction (when USE_GEMINI_FOR_EXTRACTION=true)."""

    # === Gap Detection Settings ===

    MIN_GAP_SEVERITY_FOR_QUESTION: str = field(
        default_factory=lambda: _get_env_str("MIN_GAP_SEVERITY", default="medium")
    )
    """Minimum gap severity to generate a question (critical, high, medium, low)."""

    BLOCK_ON_CRITICAL_GAPS: bool = field(
        default_factory=lambda: _get_env_bool("BLOCK_ON_CRITICAL_GAPS", default=True)
    )
    """Block design if critical gaps are unresolved."""

    # === Performance Settings ===

    CACHE_SOULS: bool = field(
        default_factory=lambda: _get_env_bool("CACHE_SOULS", default=True)
    )
    """Cache extracted ProjectSouls for reuse."""

    SOUL_CACHE_TTL: int = field(
        default_factory=lambda: _get_env_int("SOUL_CACHE_TTL", default=3600)
    )
    """Soul cache TTL in seconds (default: 1 hour)."""

    # === Turkish Language Settings ===

    DEFAULT_LANGUAGE: str = field(
        default_factory=lambda: _get_env_str("DEFAULT_LANGUAGE", default="tr")
    )
    """Default content language for questions and prompts."""

    TURKISH_QUESTIONS: bool = field(
        default_factory=lambda: _get_env_bool("TURKISH_QUESTIONS", default=True)
    )
    """Generate interview questions in Turkish."""

    # === Telemetry ===

    COLLECT_METRICS: bool = field(
        default_factory=lambda: _get_env_bool("COLLECT_METRICS", default=True)
    )
    """Collect anonymized usage metrics for improvement."""

    def __post_init__(self):
        """Validate configuration values."""
        # Ensure MIN_CONFIDENCE is in valid range
        if not 0.0 <= self.MIN_CONFIDENCE <= 1.0:
            self.MIN_CONFIDENCE = 0.6

        # Ensure reasonable limits
        if self.MAX_QUESTIONS < 1:
            self.MAX_QUESTIONS = 1
        elif self.MAX_QUESTIONS > 50:
            self.MAX_QUESTIONS = 50

        if self.EXTRACTION_TIMEOUT < 1:
            self.EXTRACTION_TIMEOUT = 1
        elif self.EXTRACTION_TIMEOUT > 60:
            self.EXTRACTION_TIMEOUT = 60

        # Validate severity setting
        valid_severities = {"critical", "high", "medium", "low"}
        if self.MIN_GAP_SEVERITY_FOR_QUESTION not in valid_severities:
            self.MIN_GAP_SEVERITY_FOR_QUESTION = "medium"

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "v2_enabled": self.V2_ENABLED,
            "graceful_fallback": self.GRACEFUL_FALLBACK,
            "debug": self.DEBUG,
            "max_questions": self.MAX_QUESTIONS,
            "min_confidence": self.MIN_CONFIDENCE,
            "auto_apply_defaults": self.AUTO_APPLY_DEFAULTS,
            "extraction_timeout": self.EXTRACTION_TIMEOUT,
            "use_gemini_for_extraction": self.USE_GEMINI_FOR_EXTRACTION,
            "extraction_model": self.EXTRACTION_MODEL,
            "min_gap_severity": self.MIN_GAP_SEVERITY_FOR_QUESTION,
            "block_on_critical_gaps": self.BLOCK_ON_CRITICAL_GAPS,
            "cache_souls": self.CACHE_SOULS,
            "soul_cache_ttl": self.SOUL_CACHE_TTL,
            "default_language": self.DEFAULT_LANGUAGE,
            "turkish_questions": self.TURKISH_QUESTIONS,
            "collect_metrics": self.COLLECT_METRICS,
        }

    def is_v2_active(self) -> bool:
        """Check if v2 features should be used."""
        return self.V2_ENABLED

    def should_fallback(self) -> bool:
        """Check if fallback to v1 is enabled."""
        return self.GRACEFUL_FALLBACK


# Global configuration instance
_config: Optional[MAESTROConfig] = None


def get_config() -> MAESTROConfig:
    """
    Get the global MAESTRO configuration.

    Creates a new instance on first call, then returns the cached instance.

    Example:
        >>> config = get_config()
        >>> config.V2_ENABLED
        True
    """
    global _config
    if _config is None:
        _config = MAESTROConfig()
    return _config


def reset_config() -> MAESTROConfig:
    """
    Reset and reload the configuration.

    Useful for testing or after environment variable changes.

    Example:
        >>> import os
        >>> os.environ["MAESTRO_V2_ENABLED"] = "false"
        >>> config = reset_config()
        >>> config.V2_ENABLED
        False
    """
    global _config
    _config = MAESTROConfig()
    return _config


def disable_v2() -> None:
    """
    Emergency disable for v2 features.

    Call this to immediately disable v2 without restarting.

    Example:
        >>> disable_v2()
        >>> get_config().V2_ENABLED
        False
    """
    config = get_config()
    config.V2_ENABLED = False


def enable_v2() -> None:
    """
    Enable v2 features.

    Example:
        >>> enable_v2()
        >>> get_config().V2_ENABLED
        True
    """
    config = get_config()
    config.V2_ENABLED = True
