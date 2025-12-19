"""Error recovery mechanisms for Gemini MCP operations.

Provides retry logic, fallback strategies, and graceful degradation
for handling API errors and malformed responses.
"""

import asyncio
import logging
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Awaitable
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar("T")


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
    on_retry: Optional[Callable[[int, Exception], None]] = None,
) -> T:
    """Execute an async function with retry logic.

    Args:
        func: Async function to execute.
        strategy: Recovery strategy configuration.
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

            # Check if we should retry this error type
            if error_type not in strategy.retry_on:
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
