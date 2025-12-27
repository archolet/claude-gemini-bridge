"""
Theme constants for Gemini MCP Server.

Contains all theme-related constants including color palettes,
gradient definitions, typography settings, and theme-specific presets.
"""

from __future__ import annotations

from typing import Any, Dict


# =============================================================================
# BRUTALIST THEME CONSTANTS
# =============================================================================

BRUTALIST_CONTRAST_PAIRS: Dict[str, Dict[str, Any]] = {
    "white": {"text": "black", "text_muted": "slate-700", "min_contrast": 7.0},
    "black": {"text": "white", "text_muted": "slate-300", "min_contrast": 7.0},
    "yellow-400": {"text": "black", "text_muted": "slate-800", "min_contrast": 4.5},
    "blue-600": {"text": "white", "text_muted": "blue-100", "min_contrast": 4.5},
    "red-600": {"text": "white", "text_muted": "red-100", "min_contrast": 4.5},
}


# =============================================================================
# NEO-BRUTALISM THEME CONSTANTS
# =============================================================================

NEOBRUTALISM_GRADIENTS: Dict[str, Dict[str, Any]] = {
    "sunset": {"colors": ["yellow-400", "orange-500", "pink-500"], "angle": "to-r"},
    "ocean": {"colors": ["cyan-400", "blue-500", "purple-500"], "angle": "to-r"},
    "forest": {"colors": ["lime-400", "emerald-500", "teal-500"], "angle": "to-r"},
    "candy": {"colors": ["pink-400", "purple-500", "indigo-500"], "angle": "to-r"},
    "fire": {"colors": ["yellow-400", "orange-500", "red-500"], "angle": "to-r"},
}

GRADIENT_ANIMATIONS: Dict[str, Dict[str, str]] = {
    "flow": {
        "keyframes": """
        @keyframes gradient-flow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        """,
        "class": "bg-[length:200%_200%] animate-[gradient-flow_3s_ease_infinite]",
    },
    "pulse": {
        "keyframes": """
        @keyframes gradient-pulse {
            0%, 100% { background-size: 100% 100%; opacity: 1; }
            50% { background-size: 120% 120%; opacity: 0.9; }
        }
        """,
        "class": "animate-[gradient-pulse_2s_ease-in-out_infinite]",
    },
    "shimmer": {
        "keyframes": """
        @keyframes gradient-shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        """,
        "class": "bg-[length:200%_100%] animate-[gradient-shimmer_2s_linear_infinite]",
    },
    "wave": {
        "keyframes": """
        @keyframes gradient-wave {
            0%, 100% { background-position: 0% 0%; }
            25% { background-position: 100% 0%; }
            50% { background-position: 100% 100%; }
            75% { background-position: 0% 100%; }
        }
        """,
        "class": "bg-[length:200%_200%] animate-[gradient-wave_4s_ease_infinite]",
    },
}


# =============================================================================
# CORPORATE THEME CONSTANTS
# =============================================================================

CORPORATE_INDUSTRIES: Dict[str, Dict[str, Any]] = {
    "finance": {
        "name": "Corporate Finance",
        "primary": "blue-800",
        "secondary": "emerald-600",
        "accent": "amber-500",
        "personality": "trustworthy, stable, premium",
        "suggested_fonts": ["Inter", "SF Pro", "IBM Plex Sans"],
        "icon_style": "outline",
    },
    "healthcare": {
        "name": "Corporate Healthcare",
        "primary": "teal-600",
        "secondary": "blue-500",
        "accent": "rose-500",
        "personality": "caring, clean, professional",
        "suggested_fonts": ["Plus Jakarta Sans", "Source Sans Pro"],
        "icon_style": "outline",
    },
    "legal": {
        "name": "Corporate Legal",
        "primary": "slate-800",
        "secondary": "amber-700",
        "accent": "blue-600",
        "personality": "authoritative, traditional, refined",
        "suggested_fonts": ["Playfair Display", "Lora", "Libre Baskerville"],
        "icon_style": "solid",
    },
    "tech": {
        "name": "Corporate Tech",
        "primary": "blue-600",
        "secondary": "slate-500",
        "accent": "cyan-400",
        "personality": "innovative, modern, dynamic",
        "suggested_fonts": ["Inter", "Space Grotesk", "Manrope"],
        "icon_style": "outline",
    },
    "manufacturing": {
        "name": "Corporate Manufacturing",
        "primary": "orange-600",
        "secondary": "slate-700",
        "accent": "yellow-500",
        "personality": "reliable, industrial, strong",
        "suggested_fonts": ["DM Sans", "Roboto", "Work Sans"],
        "icon_style": "solid",
    },
    "consulting": {
        "name": "Corporate Consulting",
        "primary": "blue-700",
        "secondary": "slate-600",
        "accent": "emerald-500",
        "personality": "expert, strategic, sophisticated",
        "suggested_fonts": ["Graphik", "Calibre"],
        "icon_style": "outline",
    },
}

CORPORATE_LAYOUTS: Dict[str, Dict[str, str]] = {
    "traditional": {"max_width": "max-w-6xl", "spacing": "generous"},
    "modern": {"max_width": "max-w-7xl", "spacing": "balanced"},
    "editorial": {"max_width": "max-w-4xl", "spacing": "airy"},
}


# =============================================================================
# TYPOGRAPHY CONSTANTS
# =============================================================================

FORMALITY_TYPOGRAPHY: Dict[str, Dict[str, Any]] = {
    "formal": {
        "description": "Conservative, traditional, authoritative typography",
        "heading_font": "font-serif",
        "heading_weight": "font-semibold",
        "body_font": "font-sans",
        "body_weight": "font-normal",
        "button_case": "uppercase tracking-wider",
        "h1": "text-3xl md:text-4xl lg:text-5xl",
        "h2": "text-2xl md:text-3xl lg:text-4xl",
        "h3": "text-xl md:text-2xl",
        "body": "text-base md:text-lg",
        "small": "text-sm",
        "letter_spacing": {
            "heading": "tracking-tight",
            "body": "tracking-normal",
            "label": "tracking-wider",
        },
        "line_height": {
            "heading": "leading-tight",
            "body": "leading-relaxed",
        },
        "styles": {
            "headline": "font-serif font-semibold tracking-tight",
            "subheadline": "font-sans font-light tracking-normal",
            "cta_button": "font-sans font-medium uppercase tracking-wider",
            "label": "font-sans text-xs uppercase tracking-[0.15em]",
            "quote": "font-serif italic",
        },
    },
    "semi-formal": {
        "description": "Modern, professional, balanced typography",
        "heading_font": "font-sans",
        "heading_weight": "font-bold",
        "body_font": "font-sans",
        "body_weight": "font-normal",
        "button_case": "normal-case",
        "h1": "text-4xl md:text-5xl lg:text-6xl",
        "h2": "text-3xl md:text-4xl",
        "h3": "text-xl md:text-2xl",
        "body": "text-base md:text-lg",
        "small": "text-sm",
        "letter_spacing": {
            "heading": "tracking-tight",
            "body": "tracking-normal",
            "label": "tracking-wide",
        },
        "line_height": {
            "heading": "leading-tight",
            "body": "leading-relaxed",
        },
        "styles": {
            "headline": "font-sans font-bold tracking-tight",
            "subheadline": "font-sans font-normal",
            "cta_button": "font-sans font-semibold",
            "label": "font-sans text-sm font-medium",
            "quote": "font-sans italic",
        },
    },
    "approachable": {
        "description": "Friendly, expressive, energetic typography",
        "heading_font": "font-sans",
        "heading_weight": "font-extrabold",
        "body_font": "font-sans",
        "body_weight": "font-normal",
        "button_case": "normal-case",
        "h1": "text-4xl md:text-6xl lg:text-7xl",
        "h2": "text-3xl md:text-4xl lg:text-5xl",
        "h3": "text-2xl md:text-3xl",
        "body": "text-lg md:text-xl",
        "small": "text-base",
        "letter_spacing": {
            "heading": "tracking-tighter",
            "body": "tracking-normal",
            "label": "tracking-normal",
        },
        "line_height": {
            "heading": "leading-none",
            "body": "leading-relaxed",
        },
        "styles": {
            "headline": "font-sans font-extrabold tracking-tighter",
            "subheadline": "font-sans font-medium",
            "cta_button": "font-sans font-bold",
            "label": "font-sans text-sm font-semibold",
            "quote": "font-sans font-medium",
        },
    },
}


# =============================================================================
# GRADIENT THEME CONSTANTS
# =============================================================================

GRADIENT_LIBRARY: Dict[str, Dict[str, Any]] = {
    # Enterprise Gradients (Anti-AI-Cliche)
    "enterprise_slate": {
        "class": "bg-gradient-to-br from-slate-100 to-slate-200",
        "text_contrast": "slate-800",
        "category": "enterprise",
    },
    "corporate_blue_subtle": {
        "class": "bg-gradient-to-br from-blue-50 to-slate-100",
        "text_contrast": "slate-800",
        "category": "enterprise",
    },
    "data_neutral": {
        "class": "bg-gradient-to-br from-zinc-50 to-zinc-100",
        "text_contrast": "zinc-800",
        "category": "enterprise",
    },
    "enterprise_dark": {
        "class": "bg-gradient-to-br from-slate-800 to-slate-900",
        "text_contrast": "white",
        "category": "enterprise",
    },
    # Signature Gradients (Non-Purple)
    "sunset": {
        "class": "bg-gradient-to-r from-orange-500 via-rose-500 to-red-600",
        "text_contrast": "white",
        "category": "warm",
    },
    "ocean": {
        "class": "bg-gradient-to-r from-cyan-500 via-blue-500 to-blue-700",
        "text_contrast": "white",
        "category": "cool",
    },
    "forest": {
        "class": "bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500",
        "text_contrast": "white",
        "category": "nature",
    },
    "fire": {
        "class": "bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500",
        "text_contrast": "white",
        "category": "warm",
    },
    # Subtle Gradients
    "slate_subtle": {
        "class": "bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200",
        "text_contrast": "slate-800",
        "category": "subtle",
    },
    "blue_subtle": {
        "class": "bg-gradient-to-br from-blue-50 via-sky-50 to-slate-50",
        "text_contrast": "slate-800",
        "category": "subtle",
    },
    "warm_subtle": {
        "class": "bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50",
        "text_contrast": "slate-800",
        "category": "subtle",
    },
    # Mesh Gradients (Enterprise-Safe)
    "mesh_blue": {
        "class": "bg-[radial-gradient(at_top_left,_#60a5fa_0%,_transparent_50%),radial-gradient(at_bottom_right,_#0ea5e9_0%,_transparent_50%),radial-gradient(at_top_right,_#64748b_0%,_transparent_50%)]",
        "bg_color": "bg-slate-900",
        "text_contrast": "white",
        "category": "mesh",
    },
    "mesh_ocean": {
        "class": "bg-[radial-gradient(at_top_left,_#22d3ee_0%,_transparent_50%),radial-gradient(at_bottom_right,_#3b82f6_0%,_transparent_50%),radial-gradient(at_center,_#0891b2_0%,_transparent_60%)]",
        "bg_color": "bg-slate-950",
        "text_contrast": "white",
        "category": "mesh",
    },
    # Glass Gradients
    "glass_light": {
        "class": "bg-gradient-to-br from-white/60 via-white/40 to-white/20 backdrop-blur-xl",
        "text_contrast": "slate-800",
        "category": "glass",
    },
    "glass_dark": {
        "class": "bg-gradient-to-br from-slate-900/80 via-slate-800/60 to-slate-900/40 backdrop-blur-xl",
        "text_contrast": "white",
        "category": "glass",
    },
    # Dark Mode (Enterprise-Safe)
    "dark_glow": {
        "class": "bg-gradient-to-r from-slate-900 via-blue-900/50 to-slate-900",
        "text_contrast": "white",
        "category": "dark",
    },
    "dark_corporate": {
        "class": "bg-[linear-gradient(to_right,#0f172a,#1e3a5f,#1e3a5f,#0f172a)]",
        "text_contrast": "white",
        "category": "dark",
    },
    # Animated (Enterprise-Safe)
    "animated_flow": {
        "class": "bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 bg-[length:200%_200%] animate-gradient-x",
        "text_contrast": "white",
        "category": "animated",
        "keyframes": "@keyframes gradient-x { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }",
    },
    # Text Gradients (Enterprise-Safe)
    "text_vibrant": {
        "class": "bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 bg-clip-text text-transparent",
        "category": "text",
    },
    "text_corporate": {
        "class": "bg-gradient-to-r from-slate-700 via-blue-700 to-slate-700 bg-clip-text text-transparent",
        "category": "text",
    },
}


# =============================================================================
# CYBERPUNK THEME CONSTANTS
# =============================================================================

NEON_COLORS: Dict[str, Dict[str, str]] = {
    "cyan": {"hex": "#22d3ee", "rgb": "34, 211, 238", "tailwind": "cyan-400"},
    "fuchsia": {"hex": "#e879f9", "rgb": "232, 121, 249", "tailwind": "fuchsia-400"},
    "yellow": {"hex": "#facc15", "rgb": "250, 204, 21", "tailwind": "yellow-400"},
    "green": {"hex": "#4ade80", "rgb": "74, 222, 128", "tailwind": "green-400"},
    "pink": {"hex": "#f472b6", "rgb": "244, 114, 182", "tailwind": "pink-400"},
    "blue": {"hex": "#60a5fa", "rgb": "96, 165, 250", "tailwind": "blue-400"},
    "purple": {"hex": "#a78bfa", "rgb": "167, 139, 250", "tailwind": "violet-400"},
    "red": {"hex": "#f87171", "rgb": "248, 113, 113", "tailwind": "red-400"},
    "orange": {"hex": "#fb923c", "rgb": "251, 146, 60", "tailwind": "orange-400"},
}

GLOW_INTENSITIES: Dict[str, Dict[str, Any]] = {
    "subtle": {"blur": "10px", "opacity": 0.2, "spread": "0px", "layers": 1},
    "medium": {"blur": "15px", "opacity": 0.3, "spread": "0px", "layers": 2},
    "strong": {"blur": "20px", "opacity": 0.4, "spread": "5px", "layers": 2},
    "intense": {"blur": "30px", "opacity": 0.5, "spread": "10px", "layers": 3},
    "extreme": {"blur": "40px", "opacity": 0.6, "spread": "15px", "layers": 3},
}


# =============================================================================
# RETRO THEME CONSTANTS
# =============================================================================

RETRO_FONT_PAIRINGS: Dict[str, Dict[str, Any]] = {
    "80s_tech": {
        "heading": {
            "family": "'VT323', monospace",
            "tailwind_class": "font-['VT323']",
            "fallback": "font-mono",
            "style": "uppercase tracking-[0.2em]",
        },
        "body": {
            "family": "'Share Tech Mono', monospace",
            "tailwind_class": "font-['Share_Tech_Mono']",
            "fallback": "font-mono",
        },
        "era": "1980s tech/sci-fi",
    },
    "80s_neon": {
        "heading": {
            "family": "'Monoton', cursive",
            "tailwind_class": "font-['Monoton']",
            "fallback": "font-serif",
            "style": "uppercase",
        },
        "body": {
            "family": "'Rajdhani', sans-serif",
            "tailwind_class": "font-['Rajdhani']",
            "fallback": "font-sans",
        },
        "era": "1980s neon/arcade",
    },
    "90s_grunge": {
        "heading": {
            "family": "'Bebas Neue', sans-serif",
            "tailwind_class": "font-['Bebas_Neue']",
            "fallback": "font-sans",
            "style": "uppercase tracking-wide",
        },
        "body": {
            "family": "'Work Sans', sans-serif",
            "tailwind_class": "font-['Work_Sans']",
            "fallback": "font-sans",
        },
        "era": "1990s grunge/alternative",
    },
    "90s_web": {
        "heading": {
            "family": "'Comic Neue', cursive",
            "tailwind_class": "font-['Comic_Neue']",
            "fallback": "font-sans",
        },
        "body": {
            "family": "'Courier Prime', monospace",
            "tailwind_class": "font-['Courier_Prime']",
            "fallback": "font-mono",
        },
        "era": "1990s early web/Geocities",
    },
    "retro_futurism": {
        "heading": {
            "family": "'Syncopate', sans-serif",
            "tailwind_class": "font-['Syncopate']",
            "fallback": "font-sans",
            "style": "uppercase tracking-widest",
        },
        "body": {
            "family": "'Exo 2', sans-serif",
            "tailwind_class": "font-['Exo_2']",
            "fallback": "font-sans",
        },
        "era": "Retro-futurism (Space Age)",
    },
    "vintage_americana": {
        "heading": {
            "family": "'Righteous', cursive",
            "tailwind_class": "font-['Righteous']",
            "fallback": "font-serif",
        },
        "body": {
            "family": "'Lato', sans-serif",
            "tailwind_class": "font-['Lato']",
            "fallback": "font-sans",
        },
        "era": "1950s-60s Americana",
    },
}


# =============================================================================
# PASTEL THEME CONSTANTS
# =============================================================================

PASTEL_ACCESSIBLE_PAIRS: Dict[str, Dict[str, str]] = {
    "rose": {
        "bg": "rose-50",
        "bg_medium": "rose-100",
        "text_safe": "rose-900",
        "text_medium": "rose-800",
        "accent": "rose-600",
        "button_bg": "rose-600",
    },
    "pink": {
        "bg": "pink-50",
        "bg_medium": "pink-100",
        "text_safe": "pink-900",
        "text_medium": "pink-800",
        "accent": "pink-600",
        "button_bg": "pink-600",
    },
    "sky": {
        "bg": "sky-50",
        "bg_medium": "sky-100",
        "text_safe": "sky-900",
        "text_medium": "sky-800",
        "accent": "sky-600",
        "button_bg": "sky-600",
    },
    "violet": {
        "bg": "violet-50",
        "bg_medium": "violet-100",
        "text_safe": "violet-900",
        "text_medium": "violet-800",
        "accent": "violet-600",
        "button_bg": "violet-600",
    },
    "teal": {
        "bg": "teal-50",
        "bg_medium": "teal-100",
        "text_safe": "teal-900",
        "text_medium": "teal-800",
        "accent": "teal-600",
        "button_bg": "teal-600",
    },
    "amber": {
        "bg": "amber-50",
        "bg_medium": "amber-100",
        "text_safe": "amber-900",
        "text_medium": "amber-800",
        "accent": "amber-600",
        "button_bg": "amber-700",
    },
    "lime": {
        "bg": "lime-50",
        "bg_medium": "lime-100",
        "text_safe": "lime-900",
        "text_medium": "lime-800",
        "accent": "lime-700",
        "button_bg": "lime-700",
    },
}


# =============================================================================
# NATURE THEME CONSTANTS
# =============================================================================

NATURE_SEASONS: Dict[str, Dict[str, str]] = {
    "spring": {
        "name": "Spring",
        "mood": "Fresh, renewal, growth",
        "primary": "lime-500",
        "secondary": "emerald-500",
        "accent": "pink-400",
        "background": "lime-50",
        "surface": "white",
        "text": "emerald-900",
    },
    "summer": {
        "name": "Summer",
        "mood": "Vibrant, warm, energetic",
        "primary": "amber-500",
        "secondary": "orange-500",
        "accent": "sky-400",
        "background": "amber-50",
        "surface": "white",
        "text": "stone-900",
    },
    "autumn": {
        "name": "Autumn",
        "mood": "Warm, cozy, harvest",
        "primary": "orange-600",
        "secondary": "red-600",
        "accent": "amber-400",
        "background": "orange-50",
        "surface": "white",
        "text": "stone-900",
    },
    "winter": {
        "name": "Winter",
        "mood": "Cool, serene, minimal",
        "primary": "slate-600",
        "secondary": "sky-400",
        "accent": "red-500",
        "background": "slate-50",
        "surface": "white",
        "text": "slate-900",
    },
}


# =============================================================================
# STARTUP THEME CONSTANTS
# =============================================================================

STARTUP_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "disruptor": {
        "name": "Disruptor",
        "tagline": "Challenge the status quo",
        "primary": "rose-600",
        "secondary": "orange-500",
        "accent": "lime-400",
        "personality": ["bold", "unconventional", "energetic"],
        "gradient": "from-rose-600 via-orange-500 to-amber-500",
        "motion": "dynamic, fast",
    },
    "enterprise": {
        "name": "Enterprise SaaS",
        "tagline": "Trusted by industry leaders",
        "primary": "blue-700",
        "secondary": "slate-600",
        "accent": "emerald-500",
        "personality": ["reliable", "professional", "scalable"],
        "gradient": "from-blue-700 to-blue-900",
        "motion": "subtle, professional",
    },
    "consumer": {
        "name": "Consumer App",
        "tagline": "Delightful everyday experiences",
        "primary": "pink-500",
        "secondary": "orange-400",
        "accent": "cyan-400",
        "personality": ["friendly", "playful", "accessible"],
        "gradient": "from-pink-500 via-orange-400 to-yellow-400",
        "motion": "bouncy, fun",
    },
    "fintech": {
        "name": "Fintech",
        "tagline": "The future of finance",
        "primary": "emerald-600",
        "secondary": "teal-500",
        "accent": "amber-400",
        "personality": ["trustworthy", "innovative", "secure"],
        "gradient": "from-emerald-600 to-teal-600",
        "motion": "smooth, confident",
    },
    "healthtech": {
        "name": "Healthtech",
        "tagline": "Better health through technology",
        "primary": "sky-600",
        "secondary": "teal-500",
        "accent": "rose-400",
        "personality": ["caring", "scientific", "approachable"],
        "gradient": "from-sky-500 to-teal-500",
        "motion": "calm, reassuring",
    },
    "ai_ml": {
        "name": "AI/ML Startup",
        "tagline": "Intelligence amplified",
        "primary": "blue-600",
        "secondary": "cyan-500",
        "accent": "teal-400",
        "personality": ["cutting-edge", "intelligent", "futuristic"],
        "gradient": "from-blue-600 via-cyan-500 to-teal-400",
        "motion": "algorithmic, precise",
    },
    "sustainability": {
        "name": "Sustainability/Green",
        "tagline": "Building a better tomorrow",
        "primary": "green-600",
        "secondary": "lime-500",
        "accent": "amber-400",
        "personality": ["conscious", "hopeful", "natural"],
        "gradient": "from-green-600 to-emerald-500",
        "motion": "flowing, natural",
    },
}


# =============================================================================
# THEME-VIBE COMPATIBILITY MATRIX
# =============================================================================

THEME_VIBE_COMPATIBILITY: Dict[str, Dict[str, int]] = {
    "modern-minimal": {
        "elite_corporate": 5,
        "playful_funny": 2,
        "cyberpunk_edge": 2,
        "luxury_editorial": 4,
        # Enterprise vibes
        "swiss_precision": 5,
        "sap_fiori": 4,
        "ibm_carbon": 5,
    },
    "brutalist": {
        "elite_corporate": 2,
        "playful_funny": 3,
        "cyberpunk_edge": 4,
        "luxury_editorial": 2,
        # Enterprise vibes
        "swiss_precision": 3,
        "sap_fiori": 2,
        "ibm_carbon": 3,
    },
    "glassmorphism": {
        "elite_corporate": 4,
        "playful_funny": 3,
        "cyberpunk_edge": 3,
        "luxury_editorial": 4,
        # Enterprise vibes
        "swiss_precision": 1,
        "sap_fiori": 2,
        "ibm_carbon": 2,
    },
    "neo-brutalism": {
        "elite_corporate": 1,
        "playful_funny": 5,
        "cyberpunk_edge": 3,
        "luxury_editorial": 2,
        # Enterprise vibes
        "swiss_precision": 2,
        "sap_fiori": 1,
        "ibm_carbon": 2,
    },
    "soft-ui": {
        "elite_corporate": 3,
        "playful_funny": 4,
        "cyberpunk_edge": 1,
        "luxury_editorial": 3,
        # Enterprise vibes
        "swiss_precision": 2,
        "sap_fiori": 3,
        "ibm_carbon": 3,
    },
    "corporate": {
        "elite_corporate": 5,
        "playful_funny": 1,
        "cyberpunk_edge": 1,
        "luxury_editorial": 4,
        # Enterprise vibes
        "swiss_precision": 5,
        "sap_fiori": 5,
        "ibm_carbon": 5,
    },
    "gradient": {
        "elite_corporate": 3,
        "playful_funny": 4,
        "cyberpunk_edge": 4,
        "luxury_editorial": 3,
        # Enterprise vibes
        "swiss_precision": 1,
        "sap_fiori": 2,
        "ibm_carbon": 2,
    },
    "cyberpunk": {
        "elite_corporate": 1,
        "playful_funny": 2,
        "cyberpunk_edge": 5,
        "luxury_editorial": 1,
        # Enterprise vibes
        "swiss_precision": 2,
        "sap_fiori": 1,
        "ibm_carbon": 2,
    },
    "retro": {
        "elite_corporate": 2,
        "playful_funny": 5,
        "cyberpunk_edge": 3,
        "luxury_editorial": 2,
        # Enterprise vibes
        "swiss_precision": 3,
        "sap_fiori": 1,
        "ibm_carbon": 2,
    },
    "pastel": {
        "elite_corporate": 2,
        "playful_funny": 5,
        "cyberpunk_edge": 1,
        "luxury_editorial": 3,
        # Enterprise vibes
        "swiss_precision": 2,
        "sap_fiori": 2,
        "ibm_carbon": 3,
    },
    "dark_mode_first": {
        "elite_corporate": 4,
        "playful_funny": 2,
        "cyberpunk_edge": 4,
        "luxury_editorial": 3,
        # Enterprise vibes
        "swiss_precision": 4,
        "sap_fiori": 4,
        "ibm_carbon": 5,
    },
    "high_contrast": {
        "elite_corporate": 3,
        "playful_funny": 2,
        "cyberpunk_edge": 3,
        "luxury_editorial": 2,
        # Enterprise vibes
        "swiss_precision": 5,
        "sap_fiori": 4,
        "ibm_carbon": 5,
    },
    "nature": {
        "elite_corporate": 2,
        "playful_funny": 3,
        "cyberpunk_edge": 1,
        "luxury_editorial": 4,
        # Enterprise vibes
        "swiss_precision": 2,
        "sap_fiori": 2,
        "ibm_carbon": 3,
    },
    "startup": {
        "elite_corporate": 3,
        "playful_funny": 4,
        "cyberpunk_edge": 3,
        "luxury_editorial": 2,
        # Enterprise vibes
        "swiss_precision": 3,
        "sap_fiori": 3,
        "ibm_carbon": 4,
    },
}


# =============================================================================
# CORPORATE PRESETS (One-Click Enterprise Configurations)
# =============================================================================

CORPORATE_PRESETS: Dict[str, Dict[str, Any]] = {
    "enterprise_bank": {
        "theme": "corporate",
        "industry": "finance",
        "formality": "formal",
        "layout_style": "traditional",
        "accessibility_level": "AAA",
        "quality_target": "premium",
        "vibe": "elite_corporate",
    },
    "fintech_startup": {
        "theme": "startup",
        "industry": "finance",
        "archetype": "fintech",
        "formality": "semi-formal",
        "layout_style": "modern",
        "quality_target": "production",
        "vibe": "elite_corporate",
    },
    "hospital_portal": {
        "theme": "corporate",
        "industry": "healthcare",
        "formality": "formal",
        "layout_style": "traditional",
        "accessibility_level": "AAA",
        "quality_target": "premium",
        "vibe": "elite_corporate",
    },
    "law_firm": {
        "theme": "corporate",
        "industry": "legal",
        "formality": "formal",
        "layout_style": "editorial",
        "quality_target": "premium",
        "vibe": "luxury_editorial",
    },
    "saas_enterprise": {
        "theme": "corporate",
        "industry": "tech",
        "formality": "semi-formal",
        "layout_style": "modern",
        "quality_target": "premium",
        "vibe": "elite_corporate",
    },
    "developer_tools": {
        "theme": "cyberpunk",
        "industry": "tech",
        "formality": "approachable",
        "layout_style": "modern",
        "quality_target": "production",
        "vibe": "cyberpunk_edge",
    },
    "industrial_b2b": {
        "theme": "corporate",
        "industry": "manufacturing",
        "formality": "formal",
        "layout_style": "traditional",
        "quality_target": "production",
        "vibe": "elite_corporate",
    },
    "management_consulting": {
        "theme": "corporate",
        "industry": "consulting",
        "formality": "formal",
        "layout_style": "editorial",
        "quality_target": "premium",
        "vibe": "luxury_editorial",
    },
    "boutique_agency": {
        "theme": "gradient",
        "industry": "consulting",
        "formality": "semi-formal",
        "layout_style": "modern",
        "quality_target": "production",
        "vibe": "playful_funny",
    },
}
