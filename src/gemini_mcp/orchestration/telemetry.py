"""
Telemetry & Observability - Pipeline Metrics Collection

This module provides telemetry and observability for the Trifecta Engine:
1. Pipeline execution metrics (timing, success rate)
2. Token usage tracking per agent
3. Error rate monitoring
4. Performance insights

Usage:
    telemetry = PipelineTelemetry()
    telemetry.start_pipeline("component", "pipeline_123")
    telemetry.record_agent_execution("architect", 1500.0, 2048, True)
    telemetry.end_pipeline(True)
    report = telemetry.get_report("pipeline_123")
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Metrics for a single agent execution."""

    agent_name: str
    execution_time_ms: float
    tokens_used: int
    success: bool
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PipelineMetrics:
    """Metrics for a complete pipeline execution."""

    pipeline_id: str
    pipeline_type: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    # Agent-level metrics
    agent_metrics: list[AgentMetrics] = field(default_factory=list)

    # Aggregate metrics
    total_execution_time_ms: float = 0.0
    total_tokens: int = 0
    success: bool = False
    error_count: int = 0

    # Context info
    component_type: str = ""
    theme: str = ""
    quality_target: str = "production"

    # === Phase 5: Enhanced Metrics ===
    # Parallel execution metrics
    parallel_speedup_ms: float = 0.0  # Time saved by parallel execution
    parallel_agents_count: int = 0  # Number of agents run in parallel

    # Quality loop metrics (Critic-driven refinement)
    critic_iterations: int = 0  # Number of critic loop iterations
    initial_score: float = 0.0  # First critic score
    final_score: float = 0.0  # Final critic score after refinement
    score_improvement: float = 0.0  # final_score - initial_score

    # Fallback chain metrics
    fallbacks_triggered: int = 0  # Number of fallback levels used
    fallback_level_used: int = 0  # Highest fallback level reached (1-4)

    # Agent hints metrics
    hints_passed: int = 0  # Number of hints passed between agents

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_type": self.pipeline_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_execution_time_ms": self.total_execution_time_ms,
            "total_tokens": self.total_tokens,
            "success": self.success,
            "error_count": self.error_count,
            "agent_count": len(self.agent_metrics),
            "component_type": self.component_type,
            "theme": self.theme,
            "quality_target": self.quality_target,
            # Phase 5: Enhanced metrics
            "parallel_speedup_ms": self.parallel_speedup_ms,
            "parallel_agents_count": self.parallel_agents_count,
            "critic_iterations": self.critic_iterations,
            "initial_score": self.initial_score,
            "final_score": self.final_score,
            "score_improvement": self.score_improvement,
            "fallbacks_triggered": self.fallbacks_triggered,
            "fallback_level_used": self.fallback_level_used,
            "hints_passed": self.hints_passed,
            "agents": [
                {
                    "name": m.agent_name,
                    "time_ms": m.execution_time_ms,
                    "tokens": m.tokens_used,
                    "success": m.success,
                    "error": m.error_message,
                }
                for m in self.agent_metrics
            ],
        }


class PipelineTelemetry:
    """
    Telemetry collector for Trifecta Engine pipelines.

    Provides:
    - Real-time metrics collection during pipeline execution
    - Historical metrics storage for analysis
    - Performance insights and reports
    """

    def __init__(self, max_history: int = 100):
        """
        Initialize telemetry collector.

        Args:
            max_history: Maximum number of pipeline executions to keep in memory
        """
        self._current: dict[str, PipelineMetrics] = {}
        self._history: list[PipelineMetrics] = []
        self._max_history = max_history

        # Aggregate statistics
        self._total_pipelines = 0
        self._successful_pipelines = 0
        self._total_tokens_used = 0
        self._agent_stats: dict[str, dict[str, Any]] = {}

        logger.info("PipelineTelemetry initialized")

    def start_pipeline(
        self,
        pipeline_type: str,
        pipeline_id: str,
        component_type: str = "",
        theme: str = "",
        quality_target: str = "production",
    ) -> None:
        """Start tracking a new pipeline execution."""
        metrics = PipelineMetrics(
            pipeline_id=pipeline_id,
            pipeline_type=pipeline_type,
            component_type=component_type,
            theme=theme,
            quality_target=quality_target,
        )
        self._current[pipeline_id] = metrics
        logger.debug(f"[Telemetry] Started pipeline: {pipeline_id} ({pipeline_type})")

    def record_agent_execution(
        self,
        pipeline_id: str,
        agent_name: str,
        execution_time_ms: float,
        tokens_used: int,
        success: bool,
        error_message: str = "",
    ) -> None:
        """Record metrics for a single agent execution."""
        if pipeline_id not in self._current:
            logger.warning(f"[Telemetry] Unknown pipeline: {pipeline_id}")
            return

        metrics = self._current[pipeline_id]
        agent_metrics = AgentMetrics(
            agent_name=agent_name,
            execution_time_ms=execution_time_ms,
            tokens_used=tokens_used,
            success=success,
            error_message=error_message,
        )
        metrics.agent_metrics.append(agent_metrics)

        # Update aggregate stats
        self._update_agent_stats(agent_name, execution_time_ms, tokens_used, success)

        logger.debug(
            f"[Telemetry] Agent {agent_name}: {execution_time_ms:.0f}ms, "
            f"{tokens_used} tokens, success={success}"
        )

    # === Phase 5: Enhanced Metrics Recording ===

    def record_parallel_execution(
        self,
        pipeline_id: str,
        parallel_agents: list[str],
        parallel_time_ms: float,
        sequential_estimate_ms: float,
    ) -> None:
        """
        Record metrics for parallel agent execution.

        Args:
            pipeline_id: Pipeline ID
            parallel_agents: List of agents run in parallel (e.g., ["alchemist", "physicist"])
            parallel_time_ms: Actual time taken for parallel execution
            sequential_estimate_ms: Estimated time if run sequentially
        """
        if pipeline_id not in self._current:
            return

        metrics = self._current[pipeline_id]
        metrics.parallel_agents_count = len(parallel_agents)
        metrics.parallel_speedup_ms = sequential_estimate_ms - parallel_time_ms

        logger.debug(
            f"[Telemetry] Parallel execution: {parallel_agents}, "
            f"speedup={metrics.parallel_speedup_ms:.0f}ms"
        )

    def record_critic_iteration(
        self,
        pipeline_id: str,
        iteration: int,
        score: float,
        is_initial: bool = False,
    ) -> None:
        """
        Record metrics for a critic loop iteration.

        Args:
            pipeline_id: Pipeline ID
            iteration: Current iteration number (1, 2, 3, ...)
            score: Critic score for this iteration (0-10)
            is_initial: True if this is the first score before refinement
        """
        if pipeline_id not in self._current:
            return

        metrics = self._current[pipeline_id]
        metrics.critic_iterations = iteration

        if is_initial:
            metrics.initial_score = score
        metrics.final_score = score
        metrics.score_improvement = metrics.final_score - metrics.initial_score

        logger.debug(
            f"[Telemetry] Critic iteration {iteration}: score={score:.2f}, "
            f"improvement={metrics.score_improvement:+.2f}"
        )

    def record_fallback_usage(
        self,
        pipeline_id: str,
        fallback_level: int,
        agent_name: str = "",
    ) -> None:
        """
        Record when a fallback level is triggered.

        Args:
            pipeline_id: Pipeline ID
            fallback_level: Fallback level used (1-4)
            agent_name: Agent that triggered the fallback
        """
        if pipeline_id not in self._current:
            return

        metrics = self._current[pipeline_id]
        metrics.fallbacks_triggered += 1
        if fallback_level > metrics.fallback_level_used:
            metrics.fallback_level_used = fallback_level

        logger.warning(
            f"[Telemetry] Fallback L{fallback_level} triggered for {agent_name}"
        )

    def record_hints_passed(
        self,
        pipeline_id: str,
        from_agent: str,
        to_agent: str,
        hint_keys: list[str],
    ) -> None:
        """
        Record agent hints being passed between agents.

        Args:
            pipeline_id: Pipeline ID
            from_agent: Source agent
            to_agent: Target agent
            hint_keys: Keys in the hint dictionary
        """
        if pipeline_id not in self._current:
            return

        metrics = self._current[pipeline_id]
        metrics.hints_passed += 1

        logger.debug(
            f"[Telemetry] Hint passed: {from_agent} → {to_agent}, keys={hint_keys}"
        )

    def end_pipeline(self, pipeline_id: str, success: bool) -> Optional[PipelineMetrics]:
        """End tracking for a pipeline and compute final metrics."""
        if pipeline_id not in self._current:
            logger.warning(f"[Telemetry] Unknown pipeline: {pipeline_id}")
            return None

        metrics = self._current.pop(pipeline_id)
        metrics.end_time = datetime.now()
        metrics.success = success

        # Compute aggregate metrics
        metrics.total_execution_time_ms = sum(
            m.execution_time_ms for m in metrics.agent_metrics
        )
        metrics.total_tokens = sum(m.tokens_used for m in metrics.agent_metrics)
        metrics.error_count = sum(1 for m in metrics.agent_metrics if not m.success)

        # Update global stats
        self._total_pipelines += 1
        if success:
            self._successful_pipelines += 1
        self._total_tokens_used += metrics.total_tokens

        # Add to history
        self._history.append(metrics)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        logger.info(
            f"[Telemetry] Pipeline {pipeline_id} completed: "
            f"success={success}, time={metrics.total_execution_time_ms:.0f}ms, "
            f"tokens={metrics.total_tokens}, errors={metrics.error_count}"
        )

        return metrics

    def _update_agent_stats(
        self, agent_name: str, time_ms: float, tokens: int, success: bool
    ) -> None:
        """Update aggregate statistics for an agent."""
        if agent_name not in self._agent_stats:
            self._agent_stats[agent_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "total_time_ms": 0.0,
                "total_tokens": 0,
                "avg_time_ms": 0.0,
                "avg_tokens": 0.0,
                "success_rate": 0.0,
            }

        stats = self._agent_stats[agent_name]
        stats["total_executions"] += 1
        if success:
            stats["successful_executions"] += 1
        stats["total_time_ms"] += time_ms
        stats["total_tokens"] += tokens
        stats["avg_time_ms"] = stats["total_time_ms"] / stats["total_executions"]
        stats["avg_tokens"] = stats["total_tokens"] / stats["total_executions"]
        stats["success_rate"] = stats["successful_executions"] / stats["total_executions"]

    def get_report(self, pipeline_id: str) -> Optional[dict[str, Any]]:
        """Get detailed report for a specific pipeline."""
        # Check current pipelines
        if pipeline_id in self._current:
            return self._current[pipeline_id].to_dict()

        # Check history
        for metrics in reversed(self._history):
            if metrics.pipeline_id == pipeline_id:
                return metrics.to_dict()

        return None

    def get_summary(self) -> dict[str, Any]:
        """Get overall telemetry summary."""
        # Compute enhanced metrics from history
        total_parallel_speedup = sum(m.parallel_speedup_ms for m in self._history)
        total_critic_iterations = sum(m.critic_iterations for m in self._history)
        total_fallbacks = sum(m.fallbacks_triggered for m in self._history)
        total_hints = sum(m.hints_passed for m in self._history)

        # Average score improvement
        score_improvements = [
            m.score_improvement for m in self._history if m.initial_score > 0
        ]
        avg_score_improvement = (
            sum(score_improvements) / len(score_improvements)
            if score_improvements
            else 0.0
        )

        return {
            "total_pipelines": self._total_pipelines,
            "successful_pipelines": self._successful_pipelines,
            "success_rate": (
                self._successful_pipelines / self._total_pipelines
                if self._total_pipelines > 0
                else 0.0
            ),
            "total_tokens_used": self._total_tokens_used,
            "avg_tokens_per_pipeline": (
                self._total_tokens_used / self._total_pipelines
                if self._total_pipelines > 0
                else 0.0
            ),
            "agent_stats": self._agent_stats,
            "active_pipelines": len(self._current),
            "history_size": len(self._history),
            # Phase 5: Enhanced aggregate metrics
            "total_parallel_speedup_ms": total_parallel_speedup,
            "avg_parallel_speedup_ms": (
                total_parallel_speedup / self._total_pipelines
                if self._total_pipelines > 0
                else 0.0
            ),
            "total_critic_iterations": total_critic_iterations,
            "avg_score_improvement": avg_score_improvement,
            "total_fallbacks_triggered": total_fallbacks,
            "total_hints_passed": total_hints,
        }

    def get_agent_stats(self, agent_name: str) -> Optional[dict[str, Any]]:
        """Get statistics for a specific agent."""
        return self._agent_stats.get(agent_name)

    def get_recent_pipelines(self, count: int = 10) -> list[dict[str, Any]]:
        """Get the most recent pipeline executions."""
        recent = self._history[-count:]
        return [m.to_dict() for m in reversed(recent)]

    def export_metrics(self) -> str:
        """Export all metrics as JSON string."""
        return json.dumps(
            {
                "summary": self.get_summary(),
                "recent_pipelines": self.get_recent_pipelines(20),
            },
            indent=2,
            ensure_ascii=False,
        )

    def reset(self) -> None:
        """Reset all telemetry data."""
        self._current.clear()
        self._history.clear()
        self._total_pipelines = 0
        self._successful_pipelines = 0
        self._total_tokens_used = 0
        self._agent_stats.clear()
        logger.info("[Telemetry] Reset complete")


# Global telemetry instance
_telemetry: Optional[PipelineTelemetry] = None


def get_telemetry() -> PipelineTelemetry:
    """Get or create the global telemetry instance."""
    global _telemetry
    if _telemetry is None:
        _telemetry = PipelineTelemetry()
    return _telemetry


def reset_telemetry() -> None:
    """Reset the global telemetry instance."""
    global _telemetry
    if _telemetry:
        _telemetry.reset()
