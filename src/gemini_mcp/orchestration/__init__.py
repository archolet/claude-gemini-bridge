"""
Orchestration Module - Multi-Agent Pipeline Coordination

This module handles the coordination of multiple agents in design pipelines:
- AgentContext: Shared context passed between agents
- PipelineType: Different pipeline configurations per tool
- AgentOrchestrator: Main coordinator for running pipelines
- CheckpointManager: Error recovery and state management
- PipelineTelemetry: Metrics collection and observability

Phase 7 Additions:
- InteractionSpec: Structural map for Architect→Physicist communication
- InteractionType, TriggerType: Enums for interaction specifications
"""

from gemini_mcp.orchestration.context import (
    AgentContext,
    CompressedOutput,
    DesignDNA,
    InteractionSpec,
    InteractionType,
    QualityTarget,
    TriggerType,
)
from gemini_mcp.orchestration.pipelines import PipelineType, PipelineStep, Pipeline
from gemini_mcp.orchestration.orchestrator import (
    AgentOrchestrator,
    PipelineResult,
    get_orchestrator,
)
from gemini_mcp.orchestration.telemetry import (
    PipelineTelemetry,
    get_telemetry,
    reset_telemetry,
)
from gemini_mcp.orchestration.dna_store import (
    DNAStore,
    DNAEntry,
    get_dna_store,
    reset_dna_store,
)

__all__ = [
    # Context classes
    "AgentContext",
    "CompressedOutput",
    "DesignDNA",
    "QualityTarget",
    # Phase 7: Structural Map
    "InteractionSpec",
    "InteractionType",
    "TriggerType",
    # Pipeline classes
    "PipelineType",
    "PipelineStep",
    "Pipeline",
    # Orchestrator
    "AgentOrchestrator",
    "PipelineResult",
    "get_orchestrator",
    # Telemetry
    "PipelineTelemetry",
    "get_telemetry",
    "reset_telemetry",
    # DNA Persistence (Phase 7)
    "DNAStore",
    "DNAEntry",
    "get_dna_store",
    "reset_dna_store",
]
