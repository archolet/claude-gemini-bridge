"""Telemetry and observability module for Gemini MCP design operations.

GAP 12: Observability
- Request ID tracking
- Token usage tracking (input, output, thinking)
- Latency metrics
- Operation tracking
- Structured logging and export

Usage:
    from gemini_mcp.telemetry import Telemetry, track_operation

    # Start tracking an operation
    with Telemetry.track("design_frontend") as ctx:
        ctx.set_component("navbar")
        ctx.set_theme("modern-minimal")
        # ... do work ...
        ctx.set_tokens(input=1500, output=3000, thinking=500)

    # Get metrics
    metrics = Telemetry.get_metrics()
"""

import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar
from functools import wraps

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of design operations being tracked."""
    DESIGN_FRONTEND = "design_frontend"
    DESIGN_PAGE = "design_page"
    DESIGN_SECTION = "design_section"
    REFINE_FRONTEND = "refine_frontend"
    DESIGN_FROM_REFERENCE = "design_from_reference"
    REPLACE_SECTION = "replace_section"
    GENERATE_IMAGE = "generate_image"
    GENERATE_VIDEO = "generate_video"
    ASK_GEMINI = "ask_gemini"
    CHAT_GEMINI = "chat_gemini"
    VALIDATION = "validation"
    CACHE_LOOKUP = "cache_lookup"
    TOKEN_EXTRACTION = "token_extraction"


class OperationStatus(Enum):
    """Status of an operation."""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"
    RETRYING = "retrying"


@dataclass
class TokenUsage:
    """Token usage breakdown for an operation."""
    input_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens + self.thinking_tokens

    def to_dict(self) -> Dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "thinking_tokens": self.thinking_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class OperationRecord:
    """Record of a single operation for telemetry."""
    request_id: str
    operation_type: str
    status: OperationStatus
    start_time: float
    end_time: Optional[float] = None
    latency_ms: Optional[float] = None
    tokens: TokenUsage = field(default_factory=TokenUsage)
    component_type: Optional[str] = None
    theme: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    cached: bool = False
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def complete(self, status: OperationStatus = OperationStatus.COMPLETED):
        """Mark operation as complete."""
        self.end_time = time.time()
        self.latency_ms = (self.end_time - self.start_time) * 1000
        self.status = status

    def fail(self, error: Exception):
        """Mark operation as failed."""
        self.end_time = time.time()
        self.latency_ms = (self.end_time - self.start_time) * 1000
        self.status = OperationStatus.FAILED
        self.error = str(error)
        self.error_type = type(error).__name__

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "request_id": self.request_id,
            "operation_type": self.operation_type,
            "status": self.status.value,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "latency_ms": round(self.latency_ms, 2) if self.latency_ms else None,
            "tokens": self.tokens.to_dict(),
            "component_type": self.component_type,
            "theme": self.theme,
            "model": self.model,
            "cached": self.cached,
            "retry_count": self.retry_count,
            "error": self.error,
            "error_type": self.error_type,
            "metadata": self.metadata,
        }


@dataclass
class OperationContext:
    """Context manager for tracking a single operation."""
    record: OperationRecord

    def set_tokens(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        thinking_tokens: int = 0,
    ):
        """Set token usage for this operation."""
        self.record.tokens = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thinking_tokens=thinking_tokens,
        )

    def set_component(self, component_type: str):
        """Set component type being designed."""
        self.record.component_type = component_type

    def set_theme(self, theme: str):
        """Set theme being used."""
        self.record.theme = theme

    def set_model(self, model: str):
        """Set model being used."""
        self.record.model = model

    def set_cached(self, cached: bool = True):
        """Mark if result was from cache."""
        self.record.cached = cached

    def increment_retry(self):
        """Increment retry count."""
        self.record.retry_count += 1
        self.record.status = OperationStatus.RETRYING

    def add_metadata(self, key: str, value: Any):
        """Add custom metadata."""
        self.record.metadata[key] = value


class TelemetryStore:
    """In-memory store for telemetry data."""

    def __init__(self, max_records: int = 1000):
        self._records: List[OperationRecord] = []
        self._max_records = max_records
        self._total_operations = 0
        self._total_tokens = TokenUsage()
        self._error_counts: Dict[str, int] = {}
        self._operation_counts: Dict[str, int] = {}

    def add_record(self, record: OperationRecord):
        """Add a record to the store."""
        self._records.append(record)
        self._total_operations += 1

        # Update aggregates
        self._total_tokens.input_tokens += record.tokens.input_tokens
        self._total_tokens.output_tokens += record.tokens.output_tokens
        self._total_tokens.thinking_tokens += record.tokens.thinking_tokens

        op_type = record.operation_type
        self._operation_counts[op_type] = self._operation_counts.get(op_type, 0) + 1

        if record.error_type:
            self._error_counts[record.error_type] = self._error_counts.get(record.error_type, 0) + 1

        # Evict old records if needed
        if len(self._records) > self._max_records:
            self._records = self._records[-self._max_records:]

    def get_recent_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent operation records."""
        return [r.to_dict() for r in self._records[-limit:]]

    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics."""
        completed_ops = [r for r in self._records if r.status == OperationStatus.COMPLETED]
        failed_ops = [r for r in self._records if r.status == OperationStatus.FAILED]
        cached_ops = [r for r in self._records if r.cached]

        # Calculate latency stats
        latencies = [r.latency_ms for r in completed_ops if r.latency_ms is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        max_latency = max(latencies) if latencies else 0
        min_latency = min(latencies) if latencies else 0
        p95_latency = self._percentile(latencies, 95) if latencies else 0

        return {
            "total_operations": self._total_operations,
            "completed_operations": len(completed_ops),
            "failed_operations": len(failed_ops),
            "cached_operations": len(cached_ops),
            "success_rate": len(completed_ops) / self._total_operations if self._total_operations > 0 else 0,
            "cache_hit_rate": len(cached_ops) / self._total_operations if self._total_operations > 0 else 0,
            "tokens": self._total_tokens.to_dict(),
            "latency": {
                "avg_ms": round(avg_latency, 2),
                "min_ms": round(min_latency, 2),
                "max_ms": round(max_latency, 2),
                "p95_ms": round(p95_latency, 2),
            },
            "operations_by_type": dict(self._operation_counts),
            "errors_by_type": dict(self._error_counts),
        }

    def get_metrics_by_operation(self, operation_type: str) -> Dict[str, Any]:
        """Get metrics for a specific operation type."""
        ops = [r for r in self._records if r.operation_type == operation_type]
        completed = [r for r in ops if r.status == OperationStatus.COMPLETED]
        failed = [r for r in ops if r.status == OperationStatus.FAILED]

        latencies = [r.latency_ms for r in completed if r.latency_ms is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0

        total_tokens = sum(r.tokens.total_tokens for r in ops)

        return {
            "operation_type": operation_type,
            "total": len(ops),
            "completed": len(completed),
            "failed": len(failed),
            "avg_latency_ms": round(avg_latency, 2),
            "total_tokens": total_tokens,
        }

    def clear(self):
        """Clear all records and reset counters."""
        self._records.clear()
        self._total_operations = 0
        self._total_tokens = TokenUsage()
        self._error_counts.clear()
        self._operation_counts.clear()

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of a list."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class Telemetry:
    """Main telemetry interface for the application."""

    _store: Optional[TelemetryStore] = None
    _enabled: bool = True
    _current_request_id: Optional[str] = None

    @classmethod
    def init(cls, max_records: int = 1000, enabled: bool = True):
        """Initialize telemetry system."""
        cls._store = TelemetryStore(max_records=max_records)
        cls._enabled = enabled
        logger.info(f"Telemetry initialized: enabled={enabled}, max_records={max_records}")

    @classmethod
    def _get_store(cls) -> TelemetryStore:
        """Get or create the telemetry store."""
        if cls._store is None:
            cls._store = TelemetryStore()
        return cls._store

    @classmethod
    def set_enabled(cls, enabled: bool):
        """Enable or disable telemetry."""
        cls._enabled = enabled
        logger.info(f"Telemetry {'enabled' if enabled else 'disabled'}")

    @classmethod
    def generate_request_id(cls) -> str:
        """Generate a unique request ID."""
        return str(uuid.uuid4())[:8]

    @classmethod
    @contextmanager
    def track(cls, operation_type: str, request_id: Optional[str] = None):
        """Context manager to track an operation.

        Args:
            operation_type: Type of operation being tracked
            request_id: Optional request ID (generated if not provided)

        Yields:
            OperationContext for adding metadata

        Example:
            with Telemetry.track("design_frontend") as ctx:
                ctx.set_component("navbar")
                ctx.set_tokens(input=1500, output=3000)
                # ... do work ...
        """
        if not cls._enabled:
            # Return a no-op context
            yield OperationContext(OperationRecord(
                request_id="",
                operation_type=operation_type,
                status=OperationStatus.STARTED,
                start_time=0,
            ))
            return

        request_id = request_id or cls.generate_request_id()
        cls._current_request_id = request_id

        record = OperationRecord(
            request_id=request_id,
            operation_type=operation_type,
            status=OperationStatus.STARTED,
            start_time=time.time(),
        )

        context = OperationContext(record)

        try:
            yield context
            record.complete()
        except Exception as e:
            record.fail(e)
            raise
        finally:
            cls._get_store().add_record(record)
            cls._current_request_id = None

            # Log operation summary
            status = "OK" if record.status == OperationStatus.COMPLETED else "FAIL"
            latency = f"{record.latency_ms:.0f}ms" if record.latency_ms else "N/A"
            tokens = record.tokens.total_tokens
            logger.debug(
                f"[{request_id}] {operation_type} {status} | "
                f"latency={latency} tokens={tokens}"
            )

    @classmethod
    def get_current_request_id(cls) -> Optional[str]:
        """Get the current request ID if in a tracked context."""
        return cls._current_request_id

    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        """Get aggregated telemetry metrics."""
        return cls._get_store().get_metrics()

    @classmethod
    def get_metrics_by_operation(cls, operation_type: str) -> Dict[str, Any]:
        """Get metrics for a specific operation type."""
        return cls._get_store().get_metrics_by_operation(operation_type)

    @classmethod
    def get_recent_operations(cls, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent operation records."""
        return cls._get_store().get_recent_records(limit)

    @classmethod
    def clear(cls):
        """Clear all telemetry data."""
        cls._get_store().clear()
        logger.info("Telemetry data cleared")

    @classmethod
    def export(cls) -> Dict[str, Any]:
        """Export all telemetry data for external analysis."""
        store = cls._get_store()
        return {
            "metrics": store.get_metrics(),
            "recent_operations": store.get_recent_records(limit=500),
            "exported_at": datetime.now().isoformat(),
        }


# Type variable for decorator
F = TypeVar("F", bound=Callable[..., Any])


def track_operation(operation_type: str) -> Callable[[F], F]:
    """Decorator to automatically track function execution.

    Args:
        operation_type: Type of operation being tracked

    Example:
        @track_operation("design_frontend")
        async def design_frontend_handler(component_type: str, theme: str):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with Telemetry.track(operation_type) as ctx:
                # Try to extract common parameters
                if "component_type" in kwargs:
                    ctx.set_component(kwargs["component_type"])
                if "theme" in kwargs:
                    ctx.set_theme(kwargs["theme"])
                if "model" in kwargs:
                    ctx.set_model(kwargs["model"])

                result = await func(*args, **kwargs)

                # Extract token usage from result if available
                if isinstance(result, dict):
                    if "usage" in result:
                        usage = result["usage"]
                        ctx.set_tokens(
                            input_tokens=usage.get("input_tokens", 0),
                            output_tokens=usage.get("output_tokens", 0),
                            thinking_tokens=usage.get("thinking_tokens", 0),
                        )
                    if "cached" in result:
                        ctx.set_cached(result["cached"])

                return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with Telemetry.track(operation_type) as ctx:
                if "component_type" in kwargs:
                    ctx.set_component(kwargs["component_type"])
                if "theme" in kwargs:
                    ctx.set_theme(kwargs["theme"])

                return func(*args, **kwargs)

        # Check if function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_telemetry_summary() -> str:
    """Get a human-readable telemetry summary."""
    metrics = Telemetry.get_metrics()

    lines = [
        "=== Telemetry Summary ===",
        f"Total Operations: {metrics['total_operations']}",
        f"Success Rate: {metrics['success_rate']:.1%}",
        f"Cache Hit Rate: {metrics['cache_hit_rate']:.1%}",
        "",
        "Token Usage:",
        f"  Input: {metrics['tokens']['input_tokens']:,}",
        f"  Output: {metrics['tokens']['output_tokens']:,}",
        f"  Thinking: {metrics['tokens']['thinking_tokens']:,}",
        f"  Total: {metrics['tokens']['total_tokens']:,}",
        "",
        "Latency:",
        f"  Avg: {metrics['latency']['avg_ms']:.0f}ms",
        f"  P95: {metrics['latency']['p95_ms']:.0f}ms",
        f"  Max: {metrics['latency']['max_ms']:.0f}ms",
    ]

    if metrics['errors_by_type']:
        lines.append("")
        lines.append("Errors by Type:")
        for error_type, count in metrics['errors_by_type'].items():
            lines.append(f"  {error_type}: {count}")

    return "\n".join(lines)


def log_operation_start(operation_type: str, **kwargs) -> str:
    """Log the start of an operation and return request ID."""
    request_id = Telemetry.generate_request_id()
    details = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"[{request_id}] Starting {operation_type}: {details}")
    return request_id


def log_operation_end(
    request_id: str,
    operation_type: str,
    success: bool,
    latency_ms: float,
    tokens: int = 0,
):
    """Log the end of an operation."""
    status = "completed" if success else "failed"
    logger.info(
        f"[{request_id}] {operation_type} {status} | "
        f"latency={latency_ms:.0f}ms tokens={tokens}"
    )
