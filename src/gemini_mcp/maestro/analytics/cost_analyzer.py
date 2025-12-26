"""
Cost Analyzer - Calculates API costs for MAESTRO sessions.

Based on Vertex AI Gemini pricing:
- Input tokens: $0.00025/1K
- Output tokens: $0.00125/1K
- Thinking tokens: $0.0025/1K (10x output)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, ClassVar

logger = logging.getLogger(__name__)

# Gemini 3 Pro pricing (per 1K tokens) - USD
PRICING: dict[str, float] = {
    "input": 0.00025,
    "output": 0.00125,
    "thinking": 0.0025,
}


@dataclass
class CostBreakdown:
    """Token usage and cost breakdown for a session."""

    input_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Total tokens used across all categories."""
        return self.input_tokens + self.output_tokens + self.thinking_tokens

    @property
    def input_cost(self) -> float:
        """Cost for input tokens in USD."""
        return (self.input_tokens / 1000) * PRICING["input"]

    @property
    def output_cost(self) -> float:
        """Cost for output tokens in USD."""
        return (self.output_tokens / 1000) * PRICING["output"]

    @property
    def thinking_cost(self) -> float:
        """Cost for thinking tokens in USD."""
        return (self.thinking_tokens / 1000) * PRICING["thinking"]

    @property
    def total_cost(self) -> float:
        """Total cost in USD."""
        return self.input_cost + self.output_cost + self.thinking_cost

    def add(self, other: "CostBreakdown") -> "CostBreakdown":
        """Add another breakdown to this one, returning new instance."""
        return CostBreakdown(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            thinking_tokens=self.thinking_tokens + other.thinking_tokens,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tokens": {
                "input": self.input_tokens,
                "output": self.output_tokens,
                "thinking": self.thinking_tokens,
                "total": self.total_tokens,
            },
            "cost_usd": {
                "input": round(self.input_cost, 6),
                "output": round(self.output_cost, 6),
                "thinking": round(self.thinking_cost, 6),
                "total": round(self.total_cost, 6),
            },
        }


class CostAnalyzer:
    """
    Analyzes API costs for MAESTRO sessions.

    Tracks token usage per session and provides cost estimates
    for Trifecta pipeline executions.

    Usage:
        analyzer = CostAnalyzer()
        analyzer.start_session("session_123")
        analyzer.record_api_call("session_123", input_tokens=1000, output_tokens=500)
        cost = analyzer.get_session_cost("session_123")
        print(f"Total cost: ${cost.total_cost:.4f}")
    """

    # Average token usage per agent (based on empirical data)
    # Format: (input_tokens, output_tokens, thinking_tokens)
    AGENT_TOKEN_ESTIMATES: ClassVar[dict[str, tuple[int, int, int]]] = {
        "architect": (2000, 4000, 1000),
        "alchemist": (3000, 2000, 500),
        "physicist": (2000, 1500, 500),
        "quality_guard": (4000, 1000, 500),
        "critic": (3000, 1000, 1000),
        "strategist": (2500, 3000, 1500),
        "visionary": (5000, 2000, 1000),
    }

    # Trifecta pipeline estimates by mode
    PIPELINE_ESTIMATES: ClassVar[dict[str, CostBreakdown]] = {
        "design_frontend": CostBreakdown(11000, 8500, 2500),
        "design_page": CostBreakdown(15000, 12000, 4000),
        "design_section": CostBreakdown(10000, 7000, 2000),
        "refine_frontend": CostBreakdown(8000, 5000, 1500),
        "replace_section_in_page": CostBreakdown(12000, 8000, 2500),
        "design_from_reference": CostBreakdown(14000, 10000, 3500),
    }

    def __init__(self):
        """Initialize CostAnalyzer."""
        self._session_costs: dict[str, CostBreakdown] = {}
        self._completed_costs: list[CostBreakdown] = []

    def start_session(self, session_id: str) -> None:
        """
        Start tracking costs for a new session.

        Args:
            session_id: Unique session identifier
        """
        self._session_costs[session_id] = CostBreakdown()
        logger.debug(f"[CostAnalyzer] Started tracking: {session_id}")

    def record_api_call(
        self,
        session_id: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        thinking_tokens: int = 0,
    ) -> None:
        """
        Record token usage from an API call.

        Args:
            session_id: Active session identifier
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            thinking_tokens: Number of thinking tokens used
        """
        if session_id not in self._session_costs:
            self.start_session(session_id)

        costs = self._session_costs[session_id]
        costs.input_tokens += input_tokens
        costs.output_tokens += output_tokens
        costs.thinking_tokens += thinking_tokens

        logger.debug(
            f"[CostAnalyzer] Recorded: {session_id} "
            f"+{input_tokens}in/{output_tokens}out/{thinking_tokens}think"
        )

    def record_agent_call(
        self,
        session_id: str,
        agent_name: str,
        multiplier: float = 1.0,
    ) -> None:
        """
        Record estimated token usage for an agent call.

        Args:
            session_id: Active session identifier
            agent_name: Name of the agent (e.g., "architect", "alchemist")
            multiplier: Scale factor for complexity (default: 1.0)
        """
        estimate = self.AGENT_TOKEN_ESTIMATES.get(agent_name)
        if estimate:
            input_t, output_t, thinking_t = estimate
            self.record_api_call(
                session_id,
                input_tokens=int(input_t * multiplier),
                output_tokens=int(output_t * multiplier),
                thinking_tokens=int(thinking_t * multiplier),
            )

    def get_session_cost(self, session_id: str) -> CostBreakdown | None:
        """
        Get cost breakdown for a session.

        Args:
            session_id: Session to look up

        Returns:
            CostBreakdown or None if session not found
        """
        return self._session_costs.get(session_id)

    def complete_session(self, session_id: str) -> CostBreakdown | None:
        """
        Mark session as complete and archive costs.

        Args:
            session_id: Session to complete

        Returns:
            Final CostBreakdown or None if not found
        """
        if costs := self._session_costs.pop(session_id, None):
            self._completed_costs.append(costs)
            logger.debug(
                f"[CostAnalyzer] Completed: {session_id} "
                f"Total: ${costs.total_cost:.4f}"
            )
            return costs
        return None

    def get_total_cost(self) -> float:
        """
        Get total cost across all sessions (active + completed).

        Returns:
            Total cost in USD
        """
        active_cost = sum(c.total_cost for c in self._session_costs.values())
        completed_cost = sum(c.total_cost for c in self._completed_costs)
        return active_cost + completed_cost

    def get_aggregate_stats(self) -> dict[str, Any]:
        """
        Get aggregate statistics across all completed sessions.

        Returns:
            Dict with total costs, averages, and token breakdown
        """
        if not self._completed_costs:
            return {"total_sessions": 0, "total_cost_usd": 0.0}

        total = len(self._completed_costs)
        total_breakdown = CostBreakdown()
        for cost in self._completed_costs:
            total_breakdown = total_breakdown.add(cost)

        return {
            "total_sessions": total,
            "total_cost_usd": round(total_breakdown.total_cost, 4),
            "avg_cost_per_session": round(total_breakdown.total_cost / total, 4),
            "total_tokens": total_breakdown.total_tokens,
            "avg_tokens_per_session": total_breakdown.total_tokens // total,
            "breakdown": total_breakdown.to_dict(),
        }

    def estimate_trifecta_cost(self, mode: str) -> CostBreakdown:
        """
        Estimate cost for a Trifecta pipeline execution.

        Based on average token usage per agent:
        - Architect: ~2K in, ~4K out, ~1K thinking
        - Alchemist: ~3K in, ~2K out, ~0.5K thinking
        - Physicist: ~2K in, ~1.5K out, ~0.5K thinking
        - QualityGuard: ~4K in, ~1K out, ~0.5K thinking
        - Critic (optional): ~3K in, ~1K out, ~1K thinking

        Args:
            mode: Design mode (e.g., "design_frontend", "design_page")

        Returns:
            Estimated CostBreakdown for the pipeline
        """
        return self.PIPELINE_ESTIMATES.get(
            mode,
            CostBreakdown(10000, 7000, 2000),  # Default estimate
        )

    def estimate_cost_range(self, mode: str) -> dict[str, float]:
        """
        Get cost range (min/max) for a mode.

        Args:
            mode: Design mode

        Returns:
            Dict with min_usd, max_usd, typical_usd
        """
        base = self.estimate_trifecta_cost(mode)

        return {
            "min_usd": round(base.total_cost * 0.7, 4),  # 30% below typical
            "typical_usd": round(base.total_cost, 4),
            "max_usd": round(base.total_cost * 1.5, 4),  # 50% above typical
        }

    def record_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        thinking_tokens: int = 0,
    ) -> None:
        """
        Record token usage without session tracking (simplified API).

        Args:
            model: Model name (for future per-model pricing)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            thinking_tokens: Number of thinking tokens (optional)
        """
        # Use a global session for simplified tracking
        self.record_api_call(
            "_global",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thinking_tokens=thinking_tokens,
        )

    def get_summary(self) -> dict[str, Any]:
        """
        Get cost summary (alias for get_aggregate_stats).

        Returns:
            Dict with total costs and averages
        """
        stats = self.get_aggregate_stats()
        # Add total_cost for convenience
        stats["total_cost"] = self.get_total_cost()
        return stats

    @property
    def active_session_count(self) -> int:
        """Number of currently tracked sessions."""
        return len(self._session_costs)

    @property
    def completed_session_count(self) -> int:
        """Number of completed sessions."""
        return len(self._completed_costs)
