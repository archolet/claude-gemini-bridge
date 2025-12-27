"""
Component Tier System for Enterprise UI Components.

Tier sistemi, component complexity'ye göre agent davranışlarını ayarlar:
- Tier 1: Basit componentler, minimal ARIA, tek state
- Tier 2: Orta componentler, keyboard nav, çoklu state
- Tier 3: Kompleks componentler, virtual scroll, CRUD, nested state
- Tier 4: Enterprise componentler, drag-drop, real-time, aggregation

Reference: component.md - Enterprise UI Component Direktifleri
"""

from enum import IntEnum
from typing import Optional


class ComponentTier(IntEnum):
    """Component complexity tier enumeration."""

    BASIC = 1  # Button, Badge, Avatar, Toggle
    STANDARD = 2  # Dropdown, Modal, Tabs, Toast
    COMPLEX = 3  # Data Grid, Tree Grid, Form Builder
    ENTERPRISE = 4  # Pivot Table, Dashboard Builder


# Component type to tier mapping
TIER_MAPPING: dict[str, int] = {
    # ═══════════════════════════════════════════════════════════════
    # TIER 1 - Basit: Tek state, minimal etkileşim
    # ═══════════════════════════════════════════════════════════════
    "button": 1,
    "badge": 1,
    "avatar": 1,
    "toggle": 1,
    "icon": 1,
    "divider": 1,
    "chip": 1,
    "spinner": 1,
    "progress": 1,
    "slider": 1,
    # ═══════════════════════════════════════════════════════════════
    # TIER 2 - Orta: Çoklu state, keyboard navigation
    # ═══════════════════════════════════════════════════════════════
    "dropdown": 2,
    "modal": 2,
    "tabs": 2,
    "toast": 2,
    "card": 2,
    "accordion": 2,
    "alert": 2,
    "tooltip": 2,
    "breadcrumb": 2,
    "pagination": 2,
    "search_bar": 2,
    "stat_card": 2,
    "pricing_card": 2,
    "stepper": 2,
    "timeline": 2,
    "rating": 2,
    "color_picker": 2,
    # ═══════════════════════════════════════════════════════════════
    # TIER 3 - Kompleks: Nested state, virtual scroll, CRUD
    # ═══════════════════════════════════════════════════════════════
    "data_table": 3,
    "table": 3,
    "tree_grid": 3,
    "form_builder": 3,
    "calendar": 3,
    "kanban_board": 3,
    "file_upload": 3,
    "carousel": 3,
    "chat_widget": 3,
    "user_profile": 3,
    "settings_panel": 3,
    # ═══════════════════════════════════════════════════════════════
    # TIER 4 - Enterprise: Drag-drop, aggregation, real-time
    # ═══════════════════════════════════════════════════════════════
    "pivot_table": 4,
    "dashboard_builder": 4,
    "command_palette": 4,
    "notification_center": 4,
    "dashboard": 4,
    "dashboard_header": 4,
}

# Tier-specific feature requirements
TIER_FEATURES: dict[int, dict] = {
    1: {
        "aria_level": "basic",  # role, aria-label
        "keyboard_nav": False,
        "focus_management": "native",
        "state_complexity": "single",
        "performance_concern": "none",
    },
    2: {
        "aria_level": "standard",  # + aria-expanded, aria-selected, aria-controls
        "keyboard_nav": True,  # Arrow keys, Enter, Escape
        "focus_management": "roving_tabindex",
        "state_complexity": "multi",
        "performance_concern": "low",
    },
    3: {
        "aria_level": "advanced",  # + aria-rowcount, aria-colcount, aria-sort, live regions
        "keyboard_nav": True,  # Full APG pattern
        "focus_management": "aria_activedescendant",
        "state_complexity": "nested",
        "performance_concern": "moderate",
        "virtual_scroll": True,
    },
    4: {
        "aria_level": "enterprise",  # + complex live regions, drag-drop announcements
        "keyboard_nav": True,  # Full APG + custom shortcuts
        "focus_management": "hybrid",  # Both roving and activedescendant
        "state_complexity": "distributed",
        "performance_concern": "high",
        "virtual_scroll": True,
        "real_time": True,
    },
}

# Quality thresholds per tier (for Critic agent)
TIER_QUALITY_THRESHOLDS: dict[int, float] = {
    1: 7.0,  # Basic components - standard quality
    2: 7.5,  # Standard components - good quality
    3: 8.0,  # Complex components - high quality
    4: 8.5,  # Enterprise components - premium quality
}


def get_component_tier(
    component_type: str, override_tier: Optional[int] = None
) -> int:
    """
    Get the complexity tier for a component type.

    Args:
        component_type: The type of component (e.g., 'button', 'data_table')
        override_tier: Optional manual tier override (1-4)

    Returns:
        Component tier (1-4), defaults to 2 (STANDARD) if unknown
    """
    if override_tier is not None and 1 <= override_tier <= 4:
        return override_tier
    return TIER_MAPPING.get(component_type.lower().replace("-", "_"), 2)


def get_tier_features(tier: int) -> dict:
    """Get the feature requirements for a specific tier."""
    return TIER_FEATURES.get(tier, TIER_FEATURES[2])


def get_tier_quality_threshold(tier: int) -> float:
    """Get the minimum quality threshold for a specific tier."""
    return TIER_QUALITY_THRESHOLDS.get(tier, 7.5)


def get_tier_name(tier: int) -> str:
    """Get the human-readable name for a tier."""
    names = {
        1: "Basic",
        2: "Standard",
        3: "Complex",
        4: "Enterprise",
    }
    return names.get(tier, "Unknown")
