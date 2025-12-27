"""Error recovery mechanisms for Gemini MCP operations.

Provides retry logic, fallback strategies, and graceful degradation
for handling API errors and malformed responses.

Includes both async and sync retry wrappers for use across the codebase.
"""

import asyncio
import functools
import logging
import json
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Awaitable

logger = logging.getLogger(__name__)

T = TypeVar("T")


# =============================================================================
# AUTH ERROR PATTERNS (Centralized from client.py)
# =============================================================================

AUTH_ERROR_PATTERNS: tuple[str, ...] = (
    "401",
    "403",
    "unauthorized",
    "unauthenticated",
    "token",
    "expired",
    "invalid_grant",
    "credentials",
)


def is_auth_error(error: Exception) -> bool:
    """Check if an error is related to authentication/token issues.

    This function centralizes auth error detection logic previously
    duplicated in client.py's _is_auth_error() method.

    Args:
        error: The exception to check.

    Returns:
        True if this appears to be an authentication error.
    """
    error_str = str(error).lower()
    return any(pattern in error_str for pattern in AUTH_ERROR_PATTERNS)


class ErrorType(Enum):
    """Types of errors that can occur during design operations."""

    # API Errors
    RATE_LIMIT = "rate_limit"
    QUOTA_EXCEEDED = "quota_exceeded"
    AUTH_ERROR = "auth_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"

    # Response Errors
    INVALID_JSON = "invalid_json"
    MISSING_FIELD = "missing_field"
    MALFORMED_HTML = "malformed_html"

    # Content Errors
    SAFETY_FILTER = "safety_filter"
    CONTENT_BLOCKED = "content_blocked"

    # Unknown
    UNKNOWN = "unknown"


@dataclass
class RecoveryStrategy:
    """Configuration for error recovery."""

    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    exponential_backoff: bool = True
    jitter: bool = True
    retry_on: List[ErrorType] = None

    def __post_init__(self):
        if self.retry_on is None:
            self.retry_on = [
                ErrorType.RATE_LIMIT,
                ErrorType.NETWORK_ERROR,
                ErrorType.TIMEOUT,
                ErrorType.INVALID_JSON,
            ]


def classify_error(error: Exception) -> ErrorType:
    """Classify an exception into an ErrorType.

    Args:
        error: The exception to classify.

    Returns:
        The classified ErrorType.
    """
    error_str = str(error).lower()

    # Rate limiting
    if any(x in error_str for x in ["429", "rate limit", "too many requests", "quota"]):
        if "quota" in error_str:
            return ErrorType.QUOTA_EXCEEDED
        return ErrorType.RATE_LIMIT

    # Authentication
    if any(x in error_str for x in ["401", "403", "unauthorized", "unauthenticated", "token expired"]):
        return ErrorType.AUTH_ERROR

    # Network
    if any(x in error_str for x in ["connection", "network", "dns", "socket"]):
        return ErrorType.NETWORK_ERROR

    # Timeout
    if any(x in error_str for x in ["timeout", "timed out", "deadline"]):
        return ErrorType.TIMEOUT

    # JSON parsing
    if any(x in error_str for x in ["json", "decode", "parse"]):
        return ErrorType.INVALID_JSON

    # Safety/Content
    if any(x in error_str for x in ["safety", "blocked", "harmful", "filter"]):
        if "blocked" in error_str:
            return ErrorType.CONTENT_BLOCKED
        return ErrorType.SAFETY_FILTER

    return ErrorType.UNKNOWN


def calculate_delay(
    attempt: int,
    strategy: RecoveryStrategy,
) -> float:
    """Calculate delay before next retry.

    Args:
        attempt: Current attempt number (0-indexed).
        strategy: Recovery strategy configuration.

    Returns:
        Delay in seconds before next retry.
    """
    import random

    if strategy.exponential_backoff:
        delay = strategy.base_delay_seconds * (2 ** attempt)
    else:
        delay = strategy.base_delay_seconds

    # Apply max delay cap
    delay = min(delay, strategy.max_delay_seconds)

    # Apply jitter (random factor between 0.5 and 1.5)
    if strategy.jitter:
        delay *= 0.5 + random.random()

    return delay


def repair_json_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Attempt to repair and parse malformed JSON response.

    Handles common issues like:
    - Markdown code blocks around JSON
    - Trailing commas
    - Single quotes instead of double quotes
    - Unquoted keys

    Args:
        raw_text: The raw response text.

    Returns:
        Parsed JSON dict if successful, None otherwise.
    """
    text = raw_text.strip()

    # Remove markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON object from text
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Fix common issues
    fixed = text

    # Replace single quotes with double quotes (careful with nested strings)
    # This is a simplified fix that may not work for all cases
    fixed = re.sub(r"(?<=[{,\s])(\w+)(?=\s*:)", r'"\1"', fixed)  # Unquoted keys

    # Remove trailing commas before } or ]
    fixed = re.sub(r',\s*([}\]])', r'\1', fixed)

    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    logger.debug(f"Failed to repair JSON: {text[:200]}...")
    return None


def extract_html_fallback(response_text: str) -> Optional[str]:
    """Extract HTML from a response even if JSON parsing fails.

    Args:
        response_text: The raw response text.

    Returns:
        Extracted HTML if found, None otherwise.
    """
    # Look for HTML content patterns
    patterns = [
        r'"html"\s*:\s*"((?:[^"\\]|\\.)*)"\s*[,}]',  # JSON html field
        r'<(?:div|section|header|main|article)[^>]*>[\s\S]*</(?:div|section|header|main|article)>',  # HTML tags
    ]

    for pattern in patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            html = match.group(1) if match.lastindex else match.group()
            # Unescape if from JSON
            if match.lastindex:
                html = html.encode().decode('unicode_escape')
            return html

    return None


def create_fallback_response(
    component_type: str,
    error: Exception,
    partial_result: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Create a fallback response when recovery fails.

    Args:
        component_type: The type of component that failed.
        error: The error that caused the failure.
        partial_result: Any partial result that was obtained.

    Returns:
        A fallback response with error information.
    """
    error_type = classify_error(error)

    response = {
        "component_id": f"fallback_{component_type}",
        "error": str(error),
        "error_type": error_type.value,
        "recovery_failed": True,
        "html": generate_fallback_html(component_type, str(error)),
        "design_notes": f"Fallback response due to {error_type.value} error",
        "model_used": "fallback",
    }

    # Merge any partial result
    if partial_result:
        for key in ["html", "tailwind_classes_used", "design_tokens"]:
            if key in partial_result and partial_result[key]:
                response[key] = partial_result[key]
                response["partial_recovery"] = True

    return response


def generate_fallback_html(component_type: str, error_message: str) -> str:
    """Generate minimal fallback HTML for a failed component.

    Args:
        component_type: The type of component.
        error_message: The error message to display.

    Returns:
        Minimal HTML that can be rendered.
    """
    # Map component types to basic fallback structures
    fallbacks = {
        "hero": """
<section class="min-h-[50vh] flex items-center justify-center bg-gray-100 dark:bg-gray-900">
    <div class="text-center p-8">
        <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-4">Hero Section</h1>
        <p class="text-gray-600 dark:text-gray-300">Content loading failed. Please try again.</p>
    </div>
</section>""",
        "navbar": """
<nav class="bg-white dark:bg-gray-900 shadow-sm p-4">
    <div class="container mx-auto flex justify-between items-center">
        <span class="font-bold text-xl">Logo</span>
        <div class="space-x-4">
            <a href="#" class="text-gray-600 hover:text-gray-900">Link</a>
        </div>
    </div>
</nav>""",
        "footer": """
<footer class="bg-gray-100 dark:bg-gray-900 p-8 text-center">
    <p class="text-gray-600 dark:text-gray-300">&copy; 2025 Company. All rights reserved.</p>
</footer>""",
        "card": """
<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
    <h3 class="text-lg font-semibold mb-2">Card Title</h3>
    <p class="text-gray-600 dark:text-gray-300">Card content placeholder.</p>
</div>""",
    }

    # Get specific fallback or generic
    html = fallbacks.get(component_type, f"""
<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
    <p class="text-yellow-800">
        <strong>{component_type}</strong> component could not be generated.
    </p>
    <p class="text-sm text-yellow-600 mt-2">Please try again or simplify your request.</p>
</div>""")

    return html.strip()


async def with_retry(
    func: Callable[..., Awaitable[T]],
    strategy: Optional[RecoveryStrategy] = None,
    on_auth_error: Optional[Callable[[], None]] = None,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
) -> T:
    """Execute an async function with retry logic.

    Args:
        func: Async function to execute.
        strategy: Recovery strategy configuration.
        on_auth_error: Optional callback invoked when auth error detected.
                      Typically used to refresh credentials.
        on_retry: Optional callback called on each retry.

    Returns:
        The result of the function.

    Raises:
        The last exception if all retries fail.
    """
    if strategy is None:
        strategy = RecoveryStrategy()

    last_error: Optional[Exception] = None

    for attempt in range(strategy.max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_error = e
            error_type = classify_error(e)

            # Handle auth errors with callback
            # Auth errors are ALWAYS retried when on_auth_error callback is provided
            auth_error_handled = False
            if is_auth_error(e) and on_auth_error is not None:
                logger.info("Auth error detected, invoking refresh callback")
                on_auth_error()
                auth_error_handled = True

            # Check if we should retry this error type
            # Skip this check if auth error was handled (credentials refreshed)
            if not auth_error_handled and error_type not in strategy.retry_on:
                logger.warning(f"Error type {error_type.value} not in retry list, failing immediately")
                raise

            # Check if we have retries left
            if attempt >= strategy.max_retries:
                logger.error(f"All {strategy.max_retries} retries exhausted")
                raise

            # Calculate delay and wait
            delay = calculate_delay(attempt, strategy)
            logger.warning(
                f"Attempt {attempt + 1}/{strategy.max_retries + 1} failed: {error_type.value}. "
                f"Retrying in {delay:.1f}s..."
            )

            if on_retry:
                on_retry(attempt, e)

            await asyncio.sleep(delay)

    # Should never reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError("Unexpected state in retry logic")


def retry_async(
    strategy: Optional[RecoveryStrategy] = None,
):
    """Decorator for adding retry logic to async functions.

    Args:
        strategy: Recovery strategy configuration.

    Returns:
        Decorated function with retry logic.
    """
    if strategy is None:
        strategy = RecoveryStrategy()

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            async def call():
                return await func(*args, **kwargs)

            return await with_retry(call, strategy)

        return wrapper

    return decorator


# =============================================================================
# SYNCHRONOUS RETRY UTILITIES (For client.py compatibility)
# =============================================================================


def with_retry_sync(
    func: Callable[[], T],
    strategy: Optional[RecoveryStrategy] = None,
    on_auth_error: Optional[Callable[[], None]] = None,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
) -> T:
    """Execute a synchronous function with retry logic.

    This is the sync counterpart to with_retry() for use in client.py
    where sync methods need retry capability with auth error handling.

    Args:
        func: Synchronous function to execute.
        strategy: Recovery strategy configuration.
        on_auth_error: Optional callback invoked when auth error detected.
                      Typically used to refresh credentials.
        on_retry: Optional callback called on each retry.

    Returns:
        The result of the function.

    Raises:
        The last exception if all retries fail.
    """
    if strategy is None:
        strategy = RecoveryStrategy()

    last_error: Optional[Exception] = None

    for attempt in range(strategy.max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_error = e
            error_type = classify_error(e)

            # Handle auth errors with callback
            # Auth errors are ALWAYS retried when on_auth_error callback is provided
            auth_error_handled = False
            if is_auth_error(e) and on_auth_error is not None:
                logger.info("Auth error detected, invoking refresh callback")
                on_auth_error()
                auth_error_handled = True

            # Check if we should retry this error type
            # Skip this check if auth error was handled (credentials refreshed)
            if not auth_error_handled and error_type not in strategy.retry_on:
                logger.warning(f"Error type {error_type.value} not in retry list, failing immediately")
                raise

            # Check if we have retries left
            if attempt >= strategy.max_retries:
                logger.error(f"All {strategy.max_retries} retries exhausted")
                raise

            # Calculate delay and wait
            delay = calculate_delay(attempt, strategy)
            logger.warning(
                f"Attempt {attempt + 1}/{strategy.max_retries + 1} failed: {error_type.value}. "
                f"Retrying in {delay:.1f}s..."
            )

            if on_retry:
                on_retry(attempt, e)

            time.sleep(delay)

    # Should never reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError("Unexpected state in retry logic")


def retry_sync(
    strategy: Optional[RecoveryStrategy] = None,
    on_auth_error: Optional[Callable[[], None]] = None,
):
    """Decorator for adding retry logic to synchronous functions.

    This is the sync counterpart to retry_async() for use in client.py.

    Args:
        strategy: Recovery strategy configuration.
        on_auth_error: Optional callback invoked when auth error detected.

    Returns:
        Decorated function with retry logic.

    Example:
        @retry_sync(
            strategy=RecoveryStrategy(max_retries=2),
            on_auth_error=lambda: refresh_credentials()
        )
        def call_api():
            return api.generate_text(prompt)
    """
    if strategy is None:
        strategy = RecoveryStrategy()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            def call():
                return func(*args, **kwargs)

            return with_retry_sync(call, strategy, on_auth_error)

        return wrapper

    return decorator


class ResponseValidator:
    """Validates and repairs API responses."""

    REQUIRED_FIELDS = {
        "design": ["html"],
        "section": ["html", "section_type"],
        "page": ["html", "template_type"],
        "reference": ["html", "extracted_tokens"],
        "vision": ["design_tokens"],
        "refinement": ["html"],
    }

    @classmethod
    def validate(
        cls,
        response: Dict[str, Any],
        response_type: str = "design",
    ) -> tuple[bool, List[str]]:
        """Validate a response has required fields.

        Args:
            response: The response to validate.
            response_type: Type of response (design, section, page, etc.)

        Returns:
            Tuple of (is_valid, list of missing fields).
        """
        required = cls.REQUIRED_FIELDS.get(response_type, ["html"])
        missing = [f for f in required if not response.get(f)]
        return len(missing) == 0, missing

    @classmethod
    def repair(
        cls,
        response: Dict[str, Any],
        response_type: str = "design",
        component_type: str = "unknown",
    ) -> Dict[str, Any]:
        """Attempt to repair a response with missing fields.

        Args:
            response: The response to repair.
            response_type: Type of response.
            component_type: Type of component for fallback generation.

        Returns:
            Repaired response.
        """
        is_valid, missing = cls.validate(response, response_type)

        if is_valid:
            return response

        repaired = response.copy()
        repaired["_repaired_fields"] = missing

        for field in missing:
            if field == "html":
                repaired["html"] = generate_fallback_html(component_type, "Missing HTML in response")
            elif field == "section_type":
                repaired["section_type"] = component_type
            elif field == "template_type":
                repaired["template_type"] = component_type
            elif field == "extracted_tokens":
                repaired["extracted_tokens"] = {}
            elif field == "design_tokens":
                repaired["design_tokens"] = {}

        logger.warning(f"Repaired response with missing fields: {missing}")
        return repaired


# =============================================================================
# CIRCUIT BREAKER PATTERN
# =============================================================================


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, requests go through
    OPEN = "open"  # Circuit tripped, requests fail immediately
    HALF_OPEN = "half_open"  # Testing recovery, limited requests allowed


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior.

    Attributes:
        failure_threshold: Number of failures before opening circuit.
        success_threshold: Number of successes in half-open to close.
        timeout_seconds: How long to wait before testing recovery.
        half_open_max_calls: Max concurrent calls in half-open state.
    """

    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 30.0
    half_open_max_calls: int = 1


@dataclass
class CircuitStats:
    """Statistics for a circuit breaker."""

    failures: int = 0
    successes: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changes: int = 0
    total_rejected: int = 0

    def record_failure(self) -> None:
        """Record a failure."""
        self.failures += 1
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        self.last_failure_time = time.time()

    def record_success(self) -> None:
        """Record a success."""
        self.successes += 1
        self.consecutive_successes += 1
        self.consecutive_failures = 0
        self.last_success_time = time.time()

    def reset_consecutive(self) -> None:
        """Reset consecutive counters (on state change)."""
        self.consecutive_failures = 0
        self.consecutive_successes = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "failures": self.failures,
            "successes": self.successes,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "state_changes": self.state_changes,
            "total_rejected": self.total_rejected,
        }


class CircuitBreakerError(Exception):
    """Raised when circuit is open and request is rejected."""

    def __init__(self, circuit_name: str, message: str = "Circuit is open"):
        self.circuit_name = circuit_name
        super().__init__(f"{circuit_name}: {message}")


class CircuitBreaker:
    """Circuit breaker for preventing cascading failures.

    Monitors failure rates and temporarily blocks requests when
    a service is unhealthy, allowing it time to recover.

    States:
    - CLOSED: Normal operation. Failures are counted.
    - OPEN: Too many failures. Requests are rejected immediately.
    - HALF_OPEN: Testing recovery. Limited requests allowed.

    Example:
        >>> breaker = CircuitBreaker("gemini-api")
        >>>
        >>> async def call_api():
        ...     async with breaker:
        ...         return await gemini.generate_content(...)
        >>>
        >>> try:
        ...     result = await call_api()
        ... except CircuitBreakerError:
        ...     # Circuit is open, use fallback
        ...     result = get_cached_response()
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ):
        """Initialize circuit breaker.

        Args:
            name: Unique name for this circuit (e.g., "gemini-api").
            config: Circuit breaker configuration.
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._stats = CircuitStats()
        self._opened_at: Optional[float] = None
        self._half_open_calls: int = 0
        self._lock = asyncio.Lock()

        logger.info(
            f"CircuitBreaker '{name}' initialized: "
            f"failure_threshold={self.config.failure_threshold}, "
            f"timeout={self.config.timeout_seconds}s"
        )

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, checking for timeout transitions."""
        if self._state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if self._opened_at and time.time() - self._opened_at >= self.config.timeout_seconds:
                logger.info(f"CircuitBreaker '{self.name}': timeout elapsed, transitioning to HALF_OPEN")
                self._transition_to(CircuitState.HALF_OPEN)
        return self._state

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (rejecting requests)."""
        return self.state == CircuitState.OPEN

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state
        self._stats.state_changes += 1
        self._stats.reset_consecutive()

        if new_state == CircuitState.OPEN:
            self._opened_at = time.time()
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
        elif new_state == CircuitState.CLOSED:
            self._opened_at = None

        logger.warning(
            f"CircuitBreaker '{self.name}': {old_state.value} -> {new_state.value}"
        )

    def _should_allow_request(self) -> bool:
        """Check if a request should be allowed."""
        state = self.state  # This may trigger timeout transition

        if state == CircuitState.CLOSED:
            return True

        if state == CircuitState.OPEN:
            return False

        # HALF_OPEN: Allow limited requests
        if self._half_open_calls < self.config.half_open_max_calls:
            self._half_open_calls += 1
            return True

        return False

    def record_success(self) -> None:
        """Record a successful call."""
        self._stats.record_success()

        if self._state == CircuitState.HALF_OPEN:
            if self._stats.consecutive_successes >= self.config.success_threshold:
                logger.info(
                    f"CircuitBreaker '{self.name}': recovery confirmed, closing circuit"
                )
                self._transition_to(CircuitState.CLOSED)

    def record_failure(self, error: Optional[Exception] = None) -> None:
        """Record a failed call."""
        self._stats.record_failure()

        if error:
            logger.debug(f"CircuitBreaker '{self.name}': failure recorded - {error}")

        if self._state == CircuitState.HALF_OPEN:
            # Any failure in half-open reopens the circuit
            logger.warning(
                f"CircuitBreaker '{self.name}': failure in HALF_OPEN, reopening circuit"
            )
            self._transition_to(CircuitState.OPEN)

        elif self._state == CircuitState.CLOSED:
            if self._stats.consecutive_failures >= self.config.failure_threshold:
                logger.warning(
                    f"CircuitBreaker '{self.name}': failure threshold reached, opening circuit"
                )
                self._transition_to(CircuitState.OPEN)

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout_seconds": self.config.timeout_seconds,
            },
            **self._stats.to_dict(),
        }

    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        self._state = CircuitState.CLOSED
        self._stats = CircuitStats()
        self._opened_at = None
        self._half_open_calls = 0
        logger.info(f"CircuitBreaker '{self.name}': reset to CLOSED")

    async def __aenter__(self) -> "CircuitBreaker":
        """Async context manager entry."""
        async with self._lock:
            if not self._should_allow_request():
                self._stats.total_rejected += 1
                raise CircuitBreakerError(
                    self.name,
                    f"Circuit is {self.state.value}, request rejected"
                )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Async context manager exit."""
        if exc_type is None:
            self.record_success()
        else:
            self.record_failure(exc_val)
        return False  # Don't suppress exceptions

    def __enter__(self) -> "CircuitBreaker":
        """Sync context manager entry."""
        if not self._should_allow_request():
            self._stats.total_rejected += 1
            raise CircuitBreakerError(
                self.name,
                f"Circuit is {self.state.value}, request rejected"
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Sync context manager exit."""
        if exc_type is None:
            self.record_success()
        else:
            self.record_failure(exc_val)
        return False


# =============================================================================
# CIRCUIT BREAKER REGISTRY
# =============================================================================


class CircuitBreakerRegistry:
    """Global registry for circuit breakers.

    Provides centralized management of circuit breakers across
    the application, with metrics aggregation.

    Example:
        >>> registry = get_circuit_registry()
        >>> breaker = registry.get_or_create("gemini-api")
        >>>
        >>> # Get all circuit stats
        >>> stats = registry.get_all_stats()
    """

    def __init__(self):
        """Initialize the registry."""
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

    def get_or_create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ) -> CircuitBreaker:
        """Get existing or create new circuit breaker.

        Args:
            name: Unique circuit name.
            config: Optional configuration (only used for new breakers).

        Returns:
            CircuitBreaker instance.
        """
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name, config)
        return self._breakers[name]

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        return self._breakers.get(name)

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get stats for all circuit breakers."""
        return {
            name: breaker.get_stats()
            for name, breaker in self._breakers.items()
        }

    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for breaker in self._breakers.values():
            breaker.reset()
        logger.info(f"Reset {len(self._breakers)} circuit breakers")

    def get_unhealthy(self) -> List[str]:
        """Get list of open/half-open circuit names."""
        return [
            name for name, breaker in self._breakers.items()
            if not breaker.is_closed
        ]


# Global registry instance
_circuit_registry: Optional[CircuitBreakerRegistry] = None


def get_circuit_registry() -> CircuitBreakerRegistry:
    """Get the global circuit breaker registry.

    Returns:
        The global CircuitBreakerRegistry instance.
    """
    global _circuit_registry
    if _circuit_registry is None:
        _circuit_registry = CircuitBreakerRegistry()
    return _circuit_registry


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None,
) -> CircuitBreaker:
    """Convenience function to get a circuit breaker.

    Args:
        name: Circuit breaker name.
        config: Optional configuration.

    Returns:
        CircuitBreaker instance.
    """
    return get_circuit_registry().get_or_create(name, config)
