"""
Trifecta Engine - Multi-Agent Design System

This module contains specialized AI agents for the Trifecta design pipeline:
- BaseAgent: Abstract base class for all agents
- ArchitectAgent: HTML structure specialist
- AlchemistAgent: Premium CSS effects specialist
- PhysicistAgent: Vanilla JS interactions specialist
- StrategistAgent: Planning and DNA extraction
- QualityGuardAgent: QA validation and auto-fix
- CriticAgent: Art direction for refinements
"""

from gemini_mcp.agents.base import (
    BaseAgent,
    AgentResult,
    AgentConfig,
    AgentRole,
)

# Core Trifecta
from gemini_mcp.agents.architect import ArchitectAgent
from gemini_mcp.agents.alchemist import AlchemistAgent
from gemini_mcp.agents.physicist import PhysicistAgent

# Extended Agents
from gemini_mcp.agents.strategist import StrategistAgent, DesignDNA, SectionPlan
from gemini_mcp.agents.quality_guard import QualityGuardAgent, QAReport
from gemini_mcp.agents.critic import CriticAgent, CriticReport
from gemini_mcp.agents.visionary import VisionaryAgent, VisualAnalysis

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentResult",
    "AgentConfig",
    "AgentRole",
    # Core Trifecta agents
    "ArchitectAgent",
    "AlchemistAgent",
    "PhysicistAgent",
    # Extended agents
    "StrategistAgent",
    "QualityGuardAgent",
    "CriticAgent",
    "VisionaryAgent",
    # Data classes
    "DesignDNA",
    "SectionPlan",
    "QAReport",
    "CriticReport",
    "VisualAnalysis",
]
