"""
MAESTRO v2 Fallback Handler

Provides graceful degradation from v2 soul-based system
to v1 static Q&A when errors occur.

Fallback Reasons:
- EXTRACTION_TIMEOUT: Soul extraction took too long
- EXTRACTION_ERROR: Error during soul extraction
- LOW_CONFIDENCE: Confidence below threshold
- CRITICAL_GAPS: Unresolvable critical gaps
- USER_REQUEST: User explicitly requested v1
- CONFIG_DISABLED: V2 disabled via config

Usage:
    >>> from gemini_mcp.maestro.v2.fallback import FallbackHandler
    >>> handler = FallbackHandler()
    >>> if handler.should_fallback(exception):
    ...     return handler.execute_fallback()
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from gemini_mcp.maestro.config import get_config

logger = logging.getLogger(__name__)


class FallbackReason(Enum):
    """Reasons for falling back to v1."""

    EXTRACTION_TIMEOUT = "extraction_timeout"
    EXTRACTION_ERROR = "extraction_error"
    LOW_CONFIDENCE = "low_confidence"
    CRITICAL_GAPS = "critical_gaps"
    USER_REQUEST = "user_request"
    CONFIG_DISABLED = "config_disabled"
    UNKNOWN = "unknown"


@dataclass
class FallbackEvent:
    """
    Record of a fallback event.

    Attributes:
        reason: Why fallback occurred
        timestamp: When it happened
        original_error: The error that triggered fallback
        context: Additional context
    """

    reason: FallbackReason
    timestamp: datetime = field(default_factory=datetime.now)
    original_error: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "reason": self.reason.value,
            "timestamp": self.timestamp.isoformat(),
            "original_error": self.original_error,
            "context": self.context,
        }


class FallbackHandler:
    """
    Handles graceful degradation from v2 to v1.

    Decides when to fall back and executes the fallback
    while logging the event for debugging.

    Example:
        >>> handler = FallbackHandler()
        >>> try:
        ...     soul = await extractor.extract(brief)
        ... except ExtractionError as e:
        ...     if handler.should_fallback(e):
        ...         result = handler.execute_fallback(legacy_session)
        ...     else:
        ...         raise
    """

    # Exception types that trigger fallback
    RECOVERABLE_EXCEPTIONS: List[Type[Exception]] = [
        TimeoutError,
        ConnectionError,
        ValueError,
    ]

    def __init__(self):
        """Initialize handler."""
        self._config = get_config()
        self._fallback_history: List[FallbackEvent] = []

    @property
    def is_fallback_enabled(self) -> bool:
        """Check if fallback is enabled in config."""
        return self._config.GRACEFUL_FALLBACK

    @property
    def is_v2_enabled(self) -> bool:
        """Check if v2 is enabled."""
        return self._config.V2_ENABLED

    def should_fallback(
        self,
        exception: Optional[Exception] = None,
        confidence: Optional[float] = None,
        has_critical_gaps: bool = False,
    ) -> bool:
        """
        Determine if we should fall back to v1.

        Args:
            exception: Exception that occurred (if any)
            confidence: Current confidence score (if available)
            has_critical_gaps: Whether critical gaps exist

        Returns:
            True if fallback should occur
        """
        # If v2 is disabled, always "fallback" (use v1)
        if not self.is_v2_enabled:
            return True

        # If fallback is disabled, never fall back (let errors propagate)
        if not self.is_fallback_enabled:
            return False

        # Check exception type
        if exception is not None:
            # Timeout always triggers fallback
            if isinstance(exception, TimeoutError):
                self._record_fallback(
                    FallbackReason.EXTRACTION_TIMEOUT,
                    str(exception),
                )
                return True

            # Recoverable exceptions trigger fallback
            for exc_type in self.RECOVERABLE_EXCEPTIONS:
                if isinstance(exception, exc_type):
                    self._record_fallback(
                        FallbackReason.EXTRACTION_ERROR,
                        str(exception),
                    )
                    return True

        # Low confidence triggers fallback if below threshold
        if confidence is not None:
            if confidence < self._config.MIN_CONFIDENCE * 0.5:  # Very low
                self._record_fallback(
                    FallbackReason.LOW_CONFIDENCE,
                    context={"confidence": confidence},
                )
                return True

        # Critical gaps can trigger fallback
        if has_critical_gaps:
            # Only fallback if we can't ask questions
            # (This is a design decision - could also choose to ask)
            self._record_fallback(FallbackReason.CRITICAL_GAPS)
            return True

        return False

    def _record_fallback(
        self,
        reason: FallbackReason,
        error: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> None:
        """Record a fallback event."""
        event = FallbackEvent(
            reason=reason,
            original_error=error,
            context=context or {},
        )
        self._fallback_history.append(event)

        # Log the event
        logger.warning(
            f"MAESTRO v2 fallback triggered: {reason.value}",
            extra={
                "fallback_reason": reason.value,
                "error": error,
                "context": context,
            },
        )

    def get_fallback_reason(self) -> Optional[FallbackReason]:
        """Get the most recent fallback reason."""
        if self._fallback_history:
            return self._fallback_history[-1].reason
        return None

    def get_fallback_history(self) -> List[FallbackEvent]:
        """Get all fallback events."""
        return self._fallback_history.copy()

    def clear_history(self) -> None:
        """Clear fallback history."""
        self._fallback_history.clear()

    def get_fallback_message(self, language: str = "tr") -> str:
        """
        Get user-friendly fallback message.

        Args:
            language: Message language ("tr" or "en")

        Returns:
            Localized message
        """
        reason = self.get_fallback_reason()

        if language == "tr":
            messages = {
                FallbackReason.EXTRACTION_TIMEOUT: (
                    "Tasarım analizi uzun sürdü. Standart sorulara geçiliyor."
                ),
                FallbackReason.EXTRACTION_ERROR: (
                    "Tasarım analizinde bir hata oluştu. Standart sorulara geçiliyor."
                ),
                FallbackReason.LOW_CONFIDENCE: (
                    "Yeterli bilgi çıkarılamadı. Standart sorulara geçiliyor."
                ),
                FallbackReason.CRITICAL_GAPS: (
                    "Kritik bilgiler eksik. Standart sorulara geçiliyor."
                ),
                FallbackReason.USER_REQUEST: (
                    "İsteğiniz üzerine standart sorulara geçiliyor."
                ),
                FallbackReason.CONFIG_DISABLED: (
                    "Akıllı analiz devre dışı. Standart sorular kullanılıyor."
                ),
                FallbackReason.UNKNOWN: (
                    "Beklenmeyen bir durum oluştu. Standart sorulara geçiliyor."
                ),
            }
        else:
            messages = {
                FallbackReason.EXTRACTION_TIMEOUT: (
                    "Design analysis took too long. Switching to standard questions."
                ),
                FallbackReason.EXTRACTION_ERROR: (
                    "An error occurred during analysis. Switching to standard questions."
                ),
                FallbackReason.LOW_CONFIDENCE: (
                    "Couldn't extract enough information. Switching to standard questions."
                ),
                FallbackReason.CRITICAL_GAPS: (
                    "Critical information is missing. Switching to standard questions."
                ),
                FallbackReason.USER_REQUEST: (
                    "Switching to standard questions as requested."
                ),
                FallbackReason.CONFIG_DISABLED: (
                    "Intelligent analysis is disabled. Using standard questions."
                ),
                FallbackReason.UNKNOWN: (
                    "An unexpected situation occurred. Switching to standard questions."
                ),
            }

        if reason:
            return messages.get(reason, messages[FallbackReason.UNKNOWN])
        return messages[FallbackReason.UNKNOWN]

    def wrap_with_fallback(self, func):
        """
        Decorator to wrap async functions with fallback handling.

        Usage:
            @handler.wrap_with_fallback
            async def extract_soul(brief):
                ...
        """
        import functools

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not self.is_v2_enabled:
                # Return None to signal use of v1
                return None

            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if self.should_fallback(exception=e):
                    return None
                raise

        return wrapper
