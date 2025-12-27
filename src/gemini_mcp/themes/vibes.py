"""
Design Vibes - Personality and Aesthetic Personas

This module defines design vibes (personalities) that can be applied to any theme.
Vibes influence the overall feel, motion, and aesthetic choices beyond just colors.

Enterprise vibes (swiss_precision, sap_fiori, ibm_carbon) are specifically designed
for data-dense, professional interfaces that avoid AI design cliches.
"""

from typing import Dict, Any, List

# =============================================================================
# CORE VIBES (Original 4)
# =============================================================================

CORE_VIBES: Dict[str, Dict[str, Any]] = {
    "elite_corporate": {
        "name": "Elite Corporate",
        "description": "Ultra-precision, luxury, CFO-level polish",
        "philosophy": "Confidence through restraint",
        "characteristics": [
            "Precise spacing (8px grid)",
            "Conservative color palette",
            "Subtle micro-interactions",
            "Professional typography",
        ],
        "typography": {
            "primary": "Inter, SF Pro Display, system-ui",
            "heading_weight": "600",
            "body_weight": "400",
            "letter_spacing": "-0.01em",
        },
        "spacing": {
            "base_unit": "8px",
            "density": "medium",
            "padding_scale": [8, 16, 24, 32, 48],
        },
        "motion": {
            "timing": "150ms ease-in-out",
            "hover": "scale(1.02)",
            "transition": "smooth",
        },
        "colors": {
            "saturation": "low",
            "brightness": "medium",
            "accent_usage": "minimal",
        },
        "radius": {
            "default": "4px",
            "card": "8px",
            "button": "4px",
        },
        "shadows": {
            "intensity": "subtle",
            "blur": "4-8px",
            "spread": "minimal",
        },
        "suitable_for": ["finance", "legal", "enterprise", "consulting"],
    },
    "playful_funny": {
        "name": "Playful & Funny",
        "description": "Bouncy physics, Neo-Brutalism, emoji-friendly",
        "philosophy": "Joy through movement",
        "characteristics": [
            "Exaggerated animations",
            "Bold color combinations",
            "Playful micro-interactions",
            "Rounded, friendly shapes",
        ],
        "typography": {
            "primary": "Nunito, Poppins, Quicksand",
            "heading_weight": "700-800",
            "body_weight": "400-500",
            "letter_spacing": "0",
        },
        "spacing": {
            "base_unit": "8px",
            "density": "spacious",
            "padding_scale": [12, 20, 28, 40, 56],
        },
        "motion": {
            "timing": "300ms cubic-bezier(0.68, -0.55, 0.265, 1.55)",
            "hover": "scale(1.05) rotate(-1deg)",
            "transition": "bouncy",
        },
        "colors": {
            "saturation": "high",
            "brightness": "high",
            "accent_usage": "liberal",
        },
        "radius": {
            "default": "12px",
            "card": "20px",
            "button": "full",
        },
        "shadows": {
            "intensity": "strong",
            "blur": "20-30px",
            "spread": "generous",
        },
        "suitable_for": ["gaming", "kids", "entertainment", "social"],
    },
    "cyberpunk_edge": {
        "name": "Cyberpunk Edge",
        "description": "High contrast, neon on black, glitch effects",
        "philosophy": "Tension through contrast",
        "characteristics": [
            "Neon accent colors",
            "Dark backgrounds",
            "Glitch/scan-line effects",
            "Futuristic typography",
        ],
        "typography": {
            "primary": "JetBrains Mono, Fira Code, monospace",
            "heading_weight": "700",
            "body_weight": "400",
            "letter_spacing": "0.05em",
        },
        "spacing": {
            "base_unit": "8px",
            "density": "tight",
            "padding_scale": [8, 12, 16, 24, 32],
        },
        "motion": {
            "timing": "100ms linear",
            "hover": "text-shadow glow",
            "transition": "sharp",
        },
        "colors": {
            "saturation": "ultra-high",
            "brightness": "extreme contrast",
            "accent_usage": "neon highlights",
        },
        "radius": {
            "default": "2px",
            "card": "4px",
            "button": "2px",
        },
        "shadows": {
            "intensity": "glow",
            "blur": "20px neon",
            "spread": "colorful",
        },
        "suitable_for": ["tech", "gaming", "crypto", "creative agencies"],
    },
    "luxury_editorial": {
        "name": "Luxury Editorial",
        "description": "Haute couture, wide whitespace, serif typography",
        "philosophy": "Elegance through space",
        "characteristics": [
            "Generous whitespace",
            "Editorial typography",
            "Minimal decoration",
            "Sophisticated color palette",
        ],
        "typography": {
            "primary": "Playfair Display, Cormorant, Georgia",
            "heading_weight": "500",
            "body_weight": "300-400",
            "letter_spacing": "0.02em",
        },
        "spacing": {
            "base_unit": "16px",
            "density": "generous",
            "padding_scale": [24, 48, 64, 96, 128],
        },
        "motion": {
            "timing": "400ms ease",
            "hover": "subtle opacity change",
            "transition": "elegant fade",
        },
        "colors": {
            "saturation": "muted",
            "brightness": "soft",
            "accent_usage": "single refined hue",
        },
        "radius": {
            "default": "0px",
            "card": "0px",
            "button": "0px",
        },
        "shadows": {
            "intensity": "none",
            "blur": "0",
            "spread": "none",
        },
        "suitable_for": ["fashion", "luxury", "architecture", "art galleries"],
    },
}


# =============================================================================
# ENTERPRISE VIBES (New - Anti-AI-Cliche)
# =============================================================================

ENTERPRISE_VIBES: Dict[str, Dict[str, Any]] = {
    "swiss_precision": {
        "name": "Swiss Precision",
        "description": "Clarity through restraint - International Typographic Style",
        "philosophy": "Maximum clarity, minimum decoration",
        "design_system_reference": "Swiss Style / International Typographic Style",
        "characteristics": [
            "Strict 8px baseline grid",
            "Mathematical proportions",
            "Asymmetric but balanced layouts",
            "Sans-serif typography only",
            "Grid-based information hierarchy",
        ],
        "typography": {
            "primary": "Helvetica Neue, Inter, system-ui",
            "heading_weight": "700",
            "body_weight": "400",
            "letter_spacing": "-0.02em",
            "line_height": "1.5 (body), 1.2 (headings)",
            "number_format": "tabular-nums lining-nums",
        },
        "spacing": {
            "base_unit": "8px",
            "density": "compact",
            "padding_scale": [8, 16, 24, 32, 40],
            "gutter": "16px",
        },
        "grid": {
            "columns": 12,
            "unit": "8px",
            "max_width": "1280px",
            "alignment": "left",
        },
        "motion": {
            "timing": "150ms ease-out",
            "hover": "opacity: 0.8",
            "transition": "functional only",
            "max_duration": "200ms",
        },
        "colors": {
            "primary": "black",
            "secondary": "white",
            "accent": "single strong hue (blue-600 or red-600)",
            "grays": "true neutral grays",
            "saturation": "low",
        },
        "radius": {
            "default": "0px",
            "card": "4px max",
            "button": "4px",
            "input": "2px",
        },
        "shadows": {
            "intensity": "minimal",
            "blur": "1-2px max",
            "usage": "functional separation only",
        },
        "anti_patterns": [
            "NO gradients except for data visualization",
            "NO rounded corners > 8px",
            "NO decorative shadows",
            "NO animations > 200ms",
        ],
        "data_density": {
            "target": "20+ data points per viewport",
            "row_height": "32-40px",
            "cell_padding": "8-12px",
        },
        "suitable_for": [
            "financial dashboards",
            "data analytics",
            "scientific tools",
            "government portals",
        ],
    },
    "sap_fiori": {
        "name": "SAP Fiori",
        "description": "Business-first, role-based, task-oriented design",
        "philosophy": "Simplify complexity, focus on tasks",
        "design_system_reference": "SAP Fiori Design Guidelines",
        "characteristics": [
            "Object-page paradigm",
            "Flat, borderless cards",
            "Blue as primary action color",
            "High information density",
            "Consistent semantic colors",
        ],
        "typography": {
            "primary": "'72', Inter, -apple-system",
            "heading_weight": "400-500",
            "body_weight": "400",
            "letter_spacing": "0",
            "base_size": "14px",
            "number_format": "tabular-nums",
        },
        "spacing": {
            "base_unit": "8px",
            "density": "compact",
            "padding_scale": [4, 8, 16, 24, 32],
            "row_height": "32px (compact), 40px (default), 48px (cozy)",
        },
        "grid": {
            "columns": "12 or 16",
            "unit": "8px",
            "max_width": "1440px",
            "alignment": "left",
        },
        "motion": {
            "timing": "100ms ease-out",
            "hover": "background-color change",
            "transition": "instant feedback",
            "max_duration": "150ms",
        },
        "colors": {
            "primary": "#0070F2",  # SAP Blue
            "secondary": "#354A5F",  # Shell color
            "positive": "#107E3E",  # Semantic green
            "negative": "#BB0000",  # Semantic red
            "warning": "#E9730C",  # Semantic orange
            "neutral": "#6A6D70",  # Neutral gray
            "background": "#F7F7F7",  # Shell background
        },
        "radius": {
            "default": "4px",
            "card": "8px",
            "button": "4px",
            "input": "4px",
        },
        "shadows": {
            "intensity": "minimal",
            "card": "0 0 0 1px rgba(0,0,0,0.1)",
            "elevated": "0 4px 8px rgba(0,0,0,0.1)",
        },
        "components": {
            "kpi_card": {
                "anatomy": ["label", "value", "trend", "target"],
                "value_size": "28-32px",
                "trend_position": "right of value",
            },
            "data_table": {
                "row_height": "32px",
                "header_sticky": True,
                "row_actions": "on hover",
                "selection": "checkbox",
            },
            "shell": {
                "header_height": "48px",
                "sidebar_width": "240px (expanded), 48px (collapsed)",
            },
        },
        "anti_patterns": [
            "NO decorative icons",
            "NO gradient backgrounds",
            "NO rounded corners > 8px",
            "NO glass/blur effects",
        ],
        "data_density": {
            "target": "15-20 data points per viewport",
            "row_height": "32px",
            "cell_padding": "8px",
        },
        "suitable_for": [
            "ERP dashboards",
            "supply chain management",
            "HR portals",
            "CRM interfaces",
        ],
    },
    "ibm_carbon": {
        "name": "IBM Carbon",
        "description": "Systematic clarity - accessible and consistent",
        "philosophy": "Clarity through system",
        "design_system_reference": "IBM Carbon Design System",
        "characteristics": [
            "16-column grid",
            "Gray 100 scale",
            "Productive vs Expressive motion",
            "Strong accessibility focus",
            "Data table excellence",
        ],
        "typography": {
            "primary": "IBM Plex Sans, Inter, system-ui",
            "mono": "IBM Plex Mono, JetBrains Mono",
            "heading_weight": "600",
            "body_weight": "400",
            "letter_spacing": "0",
            "base_size": "14px",
            "scale": [12, 14, 16, 20, 28, 36],
        },
        "spacing": {
            "base_unit": "8px",
            "density": "compact",
            "padding_scale": [0, 2, 4, 8, 12, 16, 24, 32, 48, 64],
            "container_padding": "16px (sm), 32px (md), 64px (lg)",
        },
        "grid": {
            "columns": 16,
            "gutter": "32px",
            "margin": "16px (sm), 32px (md)",
            "max_width": "1584px",
            "breakpoints": {
                "sm": "320px",
                "md": "672px",
                "lg": "1056px",
                "xl": "1312px",
                "max": "1584px",
            },
        },
        "motion": {
            "productive": {
                "duration": "70-150ms",
                "easing": "ease-out",
                "usage": "micro-interactions",
            },
            "expressive": {
                "duration": "150-400ms",
                "easing": "ease-in-out",
                "usage": "page transitions",
            },
        },
        "colors": {
            "gray_scale": [
                "#f4f4f4",  # Gray 10
                "#e0e0e0",  # Gray 20
                "#c6c6c6",  # Gray 30
                "#a8a8a8",  # Gray 40
                "#8d8d8d",  # Gray 50
                "#6f6f6f",  # Gray 60
                "#525252",  # Gray 70
                "#393939",  # Gray 80
                "#262626",  # Gray 90
                "#161616",  # Gray 100
            ],
            "interactive": "#0f62fe",  # Blue 60
            "support_error": "#da1e28",  # Red 60
            "support_success": "#24a148",  # Green 50
            "support_warning": "#f1c21b",  # Yellow 30
            "background": "#ffffff",
            "background_alt": "#f4f4f4",
        },
        "radius": {
            "default": "4px",
            "card": "4px",
            "button": "4px",
            "tag": "full (pills)",
        },
        "shadows": {
            "raised": "0 2px 6px rgba(0,0,0,0.2)",
            "overlay": "0 4px 8px rgba(0,0,0,0.1)",
        },
        "components": {
            "data_table": {
                "row_height": {
                    "compact": "24px",
                    "short": "32px",
                    "default": "48px",
                    "tall": "64px",
                },
                "features": [
                    "column sorting",
                    "row selection",
                    "batch actions",
                    "inline editing",
                    "expansion",
                ],
                "zebra_striping": True,
            },
            "structured_list": {
                "selectable": True,
                "row_height": "40px",
            },
        },
        "accessibility": {
            "minimum_contrast": "4.5:1 (AA)",
            "focus_indicator": "2px solid #0f62fe",
            "keyboard_navigation": "full support",
        },
        "anti_patterns": [
            "NO saturated gradients",
            "NO decorative animations",
            "NO shadows > 8px blur",
            "NO border-radius > 8px (except pills)",
        ],
        "data_density": {
            "target": "20+ data points per viewport",
            "row_height": "32-48px",
            "cell_padding": "16px",
        },
        "suitable_for": [
            "enterprise applications",
            "cloud platforms",
            "data dashboards",
            "developer tools",
        ],
    },
}


# =============================================================================
# COMBINED VIBES REGISTRY
# =============================================================================

ALL_VIBES: Dict[str, Dict[str, Any]] = {
    **CORE_VIBES,
    **ENTERPRISE_VIBES,
}


# =============================================================================
# VIBE HELPERS
# =============================================================================


def get_vibe(vibe_name: str) -> Dict[str, Any]:
    """Get a vibe configuration by name."""
    if vibe_name not in ALL_VIBES:
        raise ValueError(
            f"Unknown vibe: {vibe_name}. "
            f"Available vibes: {list(ALL_VIBES.keys())}"
        )
    return ALL_VIBES[vibe_name]


def list_vibes() -> List[str]:
    """List all available vibe names."""
    return list(ALL_VIBES.keys())


def list_enterprise_vibes() -> List[str]:
    """List enterprise-specific vibes."""
    return list(ENTERPRISE_VIBES.keys())


def get_vibe_for_industry(industry: str) -> str:
    """Suggest a vibe based on industry."""
    industry_vibe_map = {
        "finance": "sap_fiori",
        "banking": "sap_fiori",
        "legal": "swiss_precision",
        "healthcare": "ibm_carbon",
        "government": "swiss_precision",
        "enterprise": "ibm_carbon",
        "consulting": "elite_corporate",
        "tech": "ibm_carbon",
        "startup": "elite_corporate",
        "gaming": "playful_funny",
        "entertainment": "playful_funny",
        "fashion": "luxury_editorial",
        "luxury": "luxury_editorial",
        "crypto": "cyberpunk_edge",
        "creative": "cyberpunk_edge",
    }
    return industry_vibe_map.get(industry.lower(), "elite_corporate")


def get_vibe_prompt_segment(vibe_name: str) -> str:
    """Generate a prompt segment for a specific vibe."""
    vibe = get_vibe(vibe_name)

    lines = [
        f"## VIBE: {vibe['name'].upper()}",
        f"Philosophy: {vibe['philosophy']}",
        f"Description: {vibe['description']}",
        "",
        "### Characteristics",
    ]

    for char in vibe.get("characteristics", []):
        lines.append(f"- {char}")

    # Add anti-patterns if present
    if "anti_patterns" in vibe:
        lines.append("")
        lines.append("### Anti-Patterns (FORBIDDEN)")
        for ap in vibe["anti_patterns"]:
            lines.append(f"- {ap}")

    # Add typography
    if "typography" in vibe:
        lines.append("")
        lines.append("### Typography")
        typo = vibe["typography"]
        lines.append(f"- Font: {typo.get('primary', 'system-ui')}")
        lines.append(f"- Heading weight: {typo.get('heading_weight', '600')}")
        if "number_format" in typo:
            lines.append(f"- Numbers: {typo['number_format']}")

    # Add motion guidelines
    if "motion" in vibe:
        lines.append("")
        lines.append("### Motion")
        motion = vibe["motion"]
        if isinstance(motion, dict) and "timing" in motion:
            lines.append(f"- Timing: {motion['timing']}")
            lines.append(f"- Max duration: {motion.get('max_duration', '400ms')}")

    # Add data density for enterprise vibes
    if "data_density" in vibe:
        lines.append("")
        lines.append("### Data Density")
        density = vibe["data_density"]
        lines.append(f"- Target: {density.get('target', 'medium')}")
        lines.append(f"- Row height: {density.get('row_height', '40px')}")

    return "\n".join(lines)


# =============================================================================
# VIBE-THEME COMPATIBILITY EXTENSIONS
# =============================================================================

# Compatibility scores for enterprise vibes with existing themes
# Scale: 1 (poor) to 5 (excellent)
ENTERPRISE_VIBE_COMPATIBILITY: Dict[str, Dict[str, int]] = {
    "modern-minimal": {
        "swiss_precision": 5,
        "sap_fiori": 4,
        "ibm_carbon": 5,
    },
    "brutalist": {
        "swiss_precision": 3,
        "sap_fiori": 2,
        "ibm_carbon": 3,
    },
    "glassmorphism": {
        "swiss_precision": 1,
        "sap_fiori": 2,
        "ibm_carbon": 2,
    },
    "neo-brutalism": {
        "swiss_precision": 2,
        "sap_fiori": 1,
        "ibm_carbon": 2,
    },
    "soft-ui": {
        "swiss_precision": 2,
        "sap_fiori": 3,
        "ibm_carbon": 3,
    },
    "corporate": {
        "swiss_precision": 5,
        "sap_fiori": 5,
        "ibm_carbon": 5,
    },
    "gradient": {
        "swiss_precision": 1,
        "sap_fiori": 2,
        "ibm_carbon": 2,
    },
    "cyberpunk": {
        "swiss_precision": 2,
        "sap_fiori": 1,
        "ibm_carbon": 2,
    },
    "retro": {
        "swiss_precision": 3,
        "sap_fiori": 1,
        "ibm_carbon": 2,
    },
    "pastel": {
        "swiss_precision": 2,
        "sap_fiori": 2,
        "ibm_carbon": 3,
    },
    "dark_mode_first": {
        "swiss_precision": 4,
        "sap_fiori": 4,
        "ibm_carbon": 5,
    },
    "high_contrast": {
        "swiss_precision": 5,
        "sap_fiori": 4,
        "ibm_carbon": 5,
    },
    "nature": {
        "swiss_precision": 2,
        "sap_fiori": 2,
        "ibm_carbon": 3,
    },
    "startup": {
        "swiss_precision": 3,
        "sap_fiori": 3,
        "ibm_carbon": 4,
    },
}
