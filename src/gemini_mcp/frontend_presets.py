"""Frontend design presets and system prompts for Gemini 3 Pro.

This module contains:
- Component type presets (Atomic Design levels)
- Theme presets (visual styles)
- System prompt for Gemini to generate high-quality TailwindCSS/HTML
"""

from typing import Any, Dict, List

# =============================================================================
# ADVANCED MICRO-INTERACTIONS LIBRARY
# =============================================================================

MICRO_INTERACTIONS: Dict[str, Dict[str, Any]] = {
    "hover_lift": {
        "classes": "hover:-translate-y-1 hover:shadow-xl transition-all duration-300 ease-out",
        "description": "Subtle lift effect on hover with shadow enhancement",
    },
    "hover_glow": {
        "classes": "hover:shadow-lg hover:shadow-primary/25 transition-shadow duration-300",
        "description": "Glowing shadow effect on hover",
    },
    "hover_scale": {
        "classes": "hover:scale-105 active:scale-95 transition-transform duration-200 ease-out",
        "description": "Scale up on hover, scale down on press",
    },
    "hover_brightness": {
        "classes": "hover:brightness-110 active:brightness-90 transition-all duration-200",
        "description": "Brightness change for image/card hover",
    },
    "focus_ring": {
        "classes": "focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:outline-none",
        "description": "Accessible focus indicator with ring",
    },
    "focus_glow": {
        "classes": "focus:shadow-lg focus:shadow-primary/30 transition-shadow duration-200",
        "description": "Glowing focus state",
    },
    "press_feedback": {
        "classes": "active:scale-[0.98] active:shadow-inner transition-all duration-100",
        "description": "Physical press feedback",
    },
    "slide_in_right": {
        "classes": "animate-[slideInRight_0.3s_ease-out]",
        "keyframes": "@keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }",
    },
    "slide_in_up": {
        "classes": "animate-[slideInUp_0.3s_ease-out]",
        "keyframes": "@keyframes slideInUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }",
    },
    "fade_in": {
        "classes": "animate-[fadeIn_0.3s_ease-out]",
        "keyframes": "@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }",
    },
    "bounce_in": {
        "classes": "animate-[bounceIn_0.5s_cubic-bezier(0.68,-0.55,0.265,1.55)]",
        "keyframes": "@keyframes bounceIn { 0% { transform: scale(0); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }",
    },
    "pulse_subtle": {
        "classes": "animate-[pulse_2s_ease-in-out_infinite]",
        "description": "Subtle pulsing for attention",
    },
    "shimmer": {
        "classes": "animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent bg-[length:200%_100%]",
        "keyframes": "@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }",
    },
    "skeleton_loading": {
        "classes": "animate-pulse bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200 dark:from-slate-700 dark:via-slate-600 dark:to-slate-700",
        "description": "Skeleton loading placeholder",
    },
    "rotate_on_hover": {
        "classes": "hover:rotate-12 transition-transform duration-300 ease-out",
        "description": "Subtle rotation for icons",
    },
    "underline_grow": {
        "classes": "relative after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 after:bg-current hover:after:w-full after:transition-all after:duration-300",
        "description": "Growing underline effect for links",
    },
    "border_glow": {
        "classes": "hover:border-primary/50 hover:shadow-[0_0_15px_rgba(var(--color-primary),0.3)] transition-all duration-300",
        "description": "Border glow effect",
    },
    "card_tilt": {
        "classes": "hover:[transform:perspective(1000px)_rotateX(2deg)_rotateY(-2deg)] transition-transform duration-300",
        "description": "3D tilt effect for cards",
    },
    "text_gradient_animate": {
        "classes": "bg-gradient-to-r from-primary via-secondary to-primary bg-[length:200%_auto] animate-[gradient_3s_linear_infinite] bg-clip-text text-transparent",
        "keyframes": "@keyframes gradient { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }",
    },
}

# =============================================================================
# ADVANCED VISUAL EFFECTS LIBRARY
# =============================================================================

VISUAL_EFFECTS: Dict[str, Dict[str, Any]] = {
    "glassmorphism_light": {
        "classes": "bg-white/70 backdrop-blur-xl border border-white/20 shadow-xl",
        "description": "Light glassmorphism effect",
    },
    "glassmorphism_dark": {
        "classes": "bg-slate-900/70 backdrop-blur-xl border border-white/10 shadow-2xl",
        "description": "Dark glassmorphism effect",
    },
    "neumorphism_raised": {
        "classes": "bg-slate-100 shadow-[8px_8px_16px_#d1d5db,-8px_-8px_16px_#ffffff] dark:bg-slate-800 dark:shadow-[8px_8px_16px_#1e293b,-8px_-8px_16px_#334155]",
        "description": "Raised neumorphic surface",
    },
    "neumorphism_pressed": {
        "classes": "bg-slate-100 shadow-[inset_4px_4px_8px_#d1d5db,inset_-4px_-4px_8px_#ffffff] dark:bg-slate-800 dark:shadow-[inset_4px_4px_8px_#1e293b,inset_-4px_-4px_8px_#334155]",
        "description": "Pressed neumorphic surface",
    },
    "gradient_border": {
        "classes": "relative before:absolute before:inset-0 before:rounded-[inherit] before:p-[1px] before:bg-gradient-to-r before:from-primary before:to-secondary before:-z-10",
        "description": "Gradient border effect",
    },
    "neon_glow_blue": {
        "classes": "shadow-[0_0_10px_#3b82f6,0_0_20px_#3b82f6,0_0_40px_#3b82f6] border border-blue-500/50",
        "description": "Neon blue glow",
    },
    "neon_glow_purple": {
        "classes": "shadow-[0_0_10px_#a855f7,0_0_20px_#a855f7,0_0_40px_#a855f7] border border-purple-500/50",
        "description": "Neon purple glow",
    },
    "neon_glow_cyan": {
        "classes": "shadow-[0_0_10px_#22d3ee,0_0_20px_#22d3ee,0_0_40px_#22d3ee] border border-cyan-500/50",
        "description": "Neon cyan glow",
    },
    "layered_shadow": {
        "classes": "shadow-sm shadow-black/5 hover:shadow-xl hover:shadow-black/10 dark:shadow-black/20 dark:hover:shadow-black/40",
        "description": "Multi-layer shadow with hover enhancement",
    },
    "frosted_card": {
        "classes": "bg-gradient-to-br from-white/80 to-white/40 backdrop-blur-lg border border-white/30 shadow-xl shadow-black/5",
        "description": "Frosted glass card effect",
    },
    "gradient_mesh": {
        "classes": "bg-[radial-gradient(at_40%_20%,#3b82f6_0px,transparent_50%),radial-gradient(at_80%_0%,#a855f7_0px,transparent_50%),radial-gradient(at_0%_50%,#22d3ee_0px,transparent_50%)]",
        "description": "Mesh gradient background",
    },
    "noise_texture": {
        "classes": "relative before:absolute before:inset-0 before:bg-[url('data:image/svg+xml,...')] before:opacity-5 before:pointer-events-none",
        "description": "Subtle noise texture overlay",
    },
    "dot_pattern": {
        "classes": "bg-[radial-gradient(circle,_currentColor_1px,_transparent_1px)] bg-[size:20px_20px]",
        "description": "Dot pattern background",
    },
    "grid_pattern": {
        "classes": "bg-[linear-gradient(to_right,_currentColor_1px,_transparent_1px),linear-gradient(to_bottom,_currentColor_1px,_transparent_1px)] bg-[size:24px_24px] [mask-image:linear-gradient(to_bottom,white,transparent)]",
        "description": "Grid pattern background with fade",
    },
}

# =============================================================================
# SVG ICON LIBRARY (Inline SVGs)
# =============================================================================

SVG_ICONS: Dict[str, str] = {
    "arrow_right": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>',
    "arrow_left": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16l-4-4m0 0l4-4m-4 4h18"/></svg>',
    "arrow_up": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7l4-4m0 0l4 4m-4-4v18"/></svg>',
    "arrow_down": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 17l-4 4m0 0l-4-4m4 4V3"/></svg>',
    "check": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>',
    "check_circle": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "x": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>',
    "x_circle": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "menu": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>',
    "search": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>',
    "user": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>',
    "users": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>',
    "mail": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>',
    "phone": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>',
    "home": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>',
    "cog": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>',
    "bell": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>',
    "heart": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>',
    "heart_solid": '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>',
    "star": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>',
    "star_solid": '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>',
    "shopping_cart": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/></svg>',
    "plus": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>',
    "minus": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>',
    "trash": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>',
    "edit": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>',
    "eye": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>',
    "eye_off": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/></svg>',
    "download": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>',
    "upload": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>',
    "calendar": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
    "clock": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "location": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>',
    "chart_bar": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>',
    "chart_pie": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"/></svg>',
    "trending_up": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>',
    "trending_down": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6"/></svg>',
    "filter": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/></svg>',
    "sort": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"/></svg>',
    "refresh": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>',
    "external_link": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>',
    "clipboard": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>',
    "document": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>',
    "folder": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>',
    "image": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
    "video": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>',
    "lock": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>',
    "unlock": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"/></svg>',
    "shield": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>',
    "info": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "warning": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
    "error": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "spinner": '<svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>',
    "dots_vertical": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"/></svg>',
    "dots_horizontal": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z"/></svg>',
    "chevron_down": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>',
    "chevron_up": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>',
    "chevron_left": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>',
    "chevron_right": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>',
    "sun": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>',
    "moon": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>',
    "globe": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "lightning": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>',
    "fire": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z"/></svg>',
    "sparkles": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>',
}

# =============================================================================
# COMPONENT PRESETS (Atomic Design)
# =============================================================================

COMPONENT_PRESETS: Dict[str, Dict[str, Any]] = {
    # ATOMS - Smallest building blocks
    "button": {
        "atomic_level": "atom",
        "variants": ["primary", "secondary", "outline", "ghost", "danger"],
        "sizes": ["sm", "md", "lg", "xl"],
        "states": ["default", "hover", "focus", "active", "disabled"],
    },
    "input": {
        "atomic_level": "atom",
        "variants": ["text", "email", "password", "number", "search"],
        "states": ["default", "focus", "error", "success", "disabled"],
    },
    "badge": {
        "atomic_level": "atom",
        "variants": ["default", "success", "warning", "error", "info"],
    },
    "avatar": {
        "atomic_level": "atom",
        "sizes": ["xs", "sm", "md", "lg", "xl"],
        "shapes": ["circle", "rounded", "square"],
    },
    "icon": {
        "atomic_level": "atom",
        "sizes": ["sm", "md", "lg"],
    },
    "dropdown": {
        "atomic_level": "atom",
        "sections": ["trigger", "menu", "item"],
    },
    "toggle": {
        "atomic_level": "atom",
        "states": ["on", "off", "disabled"],
    },
    "tooltip": {
        "atomic_level": "atom",
        "positions": ["top", "bottom", "left", "right"],
    },
    "slider": {
        "atomic_level": "atom",
        "variants": ["default", "range", "stepped"],
        "sizes": ["sm", "md", "lg"],
        "states": ["default", "focus", "disabled"],
    },
    "spinner": {
        "atomic_level": "atom",
        "variants": ["default", "dots", "bars", "pulse"],
        "sizes": ["xs", "sm", "md", "lg", "xl"],
    },
    "progress": {
        "atomic_level": "atom",
        "variants": ["linear", "circular", "stepped"],
        "states": ["default", "success", "warning", "error"],
    },
    "chip": {
        "atomic_level": "atom",
        "variants": ["default", "outlined", "filled"],
        "sizes": ["sm", "md", "lg"],
        "dismissable": True,
    },
    "divider": {
        "atomic_level": "atom",
        "variants": ["solid", "dashed", "dotted"],
        "orientations": ["horizontal", "vertical"],
        "with_text": True,
    },
    # MOLECULES - Combinations of atoms
    "card": {
        "atomic_level": "molecule",
        "sections": ["header", "body", "footer", "media"],
        "variants": ["default", "elevated", "bordered", "interactive"],
    },
    "form": {
        "atomic_level": "molecule",
        "elements": ["input", "label", "helper_text", "error_text"],
        "layouts": ["vertical", "horizontal", "inline"],
    },
    "modal": {
        "atomic_level": "molecule",
        "sections": ["header", "body", "footer", "overlay"],
        "sizes": ["sm", "md", "lg", "xl", "full"],
    },
    "tabs": {
        "atomic_level": "molecule",
        "variants": ["underline", "pills", "enclosed", "soft"],
    },
    "table": {
        "atomic_level": "molecule",
        "features": ["sortable", "pagination", "selectable", "striped"],
    },
    "accordion": {
        "atomic_level": "molecule",
        "variants": ["default", "bordered", "separated"],
    },
    "alert": {
        "atomic_level": "molecule",
        "variants": ["info", "success", "warning", "error"],
        "dismissable": True,
    },
    "breadcrumb": {
        "atomic_level": "molecule",
        "separators": ["slash", "chevron", "arrow"],
    },
    "pagination": {
        "atomic_level": "molecule",
        "variants": ["default", "simple", "compact"],
    },
    "search_bar": {
        "atomic_level": "molecule",
        "features": ["autocomplete", "voice", "filters"],
    },
    "stat_card": {
        "atomic_level": "molecule",
        "sections": ["value", "label", "trend", "icon"],
    },
    "pricing_card": {
        "atomic_level": "molecule",
        "sections": ["tier", "price", "features", "cta"],
    },
    "carousel": {
        "atomic_level": "molecule",
        "variants": ["default", "fade", "slide", "cards"],
        "features": ["autoplay", "indicators", "arrows", "thumbnails"],
    },
    "stepper": {
        "atomic_level": "molecule",
        "variants": ["horizontal", "vertical", "compact"],
        "states": ["completed", "active", "pending", "error"],
    },
    "timeline": {
        "atomic_level": "molecule",
        "variants": ["vertical", "horizontal", "alternating"],
        "styles": ["default", "connected", "dotted"],
    },
    "file_upload": {
        "atomic_level": "molecule",
        "variants": ["dropzone", "button", "inline"],
        "features": ["drag_drop", "preview", "progress", "multiple"],
    },
    "rating": {
        "atomic_level": "molecule",
        "variants": ["stars", "hearts", "thumbs", "numeric"],
        "sizes": ["sm", "md", "lg"],
        "interactive": True,
    },
    "color_picker": {
        "atomic_level": "molecule",
        "variants": ["default", "compact", "inline", "popover"],
        "features": ["presets", "custom", "opacity"],
    },
    # ORGANISMS - Complex components
    "navbar": {
        "atomic_level": "organism",
        "sections": ["logo", "navigation", "actions", "mobile_menu"],
        "variants": ["default", "sticky", "transparent"],
    },
    "hero": {
        "atomic_level": "organism",
        "sections": ["headline", "subheadline", "cta", "media", "badge"],
        "layouts": ["centered", "left", "right", "split"],
    },
    "sidebar": {
        "atomic_level": "organism",
        "sections": ["header", "navigation", "footer"],
        "collapsible": True,
    },
    "footer": {
        "atomic_level": "organism",
        "sections": ["logo", "links", "social", "copyright"],
        "layouts": ["simple", "columns", "centered"],
    },
    "data_table": {
        "atomic_level": "organism",
        "features": ["sorting", "filtering", "pagination", "selection", "export"],
    },
    "login_form": {
        "atomic_level": "organism",
        "elements": ["email", "password", "remember", "submit", "social"],
    },
    "signup_form": {
        "atomic_level": "organism",
        "elements": ["name", "email", "password", "terms", "submit"],
    },
    "contact_form": {
        "atomic_level": "organism",
        "elements": ["name", "email", "subject", "message", "submit"],
    },
    "feature_section": {
        "atomic_level": "organism",
        "layouts": ["grid", "list", "alternating"],
    },
    "testimonial_section": {
        "atomic_level": "organism",
        "layouts": ["carousel", "grid", "single"],
    },
    "pricing_table": {
        "atomic_level": "organism",
        "features": ["toggle", "comparison", "highlight"],
    },
    "dashboard_header": {
        "atomic_level": "organism",
        "sections": ["title", "breadcrumb", "actions", "search"],
    },
    "kanban_board": {
        "atomic_level": "organism",
        "sections": ["columns", "cards", "header", "add_button"],
        "features": ["drag_drop", "filters", "search", "labels"],
    },
    "calendar": {
        "atomic_level": "organism",
        "variants": ["month", "week", "day", "agenda"],
        "features": ["events", "navigation", "today_button", "mini_calendar"],
    },
    "chat_widget": {
        "atomic_level": "organism",
        "sections": ["header", "messages", "input", "typing_indicator"],
        "variants": ["floating", "embedded", "fullscreen"],
    },
    "notification_center": {
        "atomic_level": "organism",
        "sections": ["header", "list", "empty_state", "settings"],
        "features": ["mark_read", "filters", "clear_all"],
    },
    "user_profile": {
        "atomic_level": "organism",
        "sections": ["avatar", "info", "stats", "actions", "tabs"],
        "variants": ["card", "page", "sidebar"],
    },
    "settings_panel": {
        "atomic_level": "organism",
        "sections": ["sidebar", "content", "header", "save_actions"],
        "features": ["sections", "search", "reset"],
    },
}

# =============================================================================
# PAGE TEMPLATES (Full Page Designs)
# =============================================================================

PAGE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "landing_page": {
        "description": "Marketing landing page with hero, features, and CTA",
        "sections": ["hero", "features", "testimonials", "pricing", "cta", "footer"],
        "layouts": ["single_column", "multi_section"],
        "recommended_theme": "modern-minimal",
    },
    "dashboard": {
        "description": "Admin dashboard with sidebar, stats, and data views",
        "sections": ["sidebar", "header", "stats_row", "charts", "data_table"],
        "layouts": ["sidebar_left", "sidebar_right", "top_nav"],
        "recommended_theme": "corporate",
    },
    "auth_page": {
        "description": "Login/signup page with form and branding",
        "sections": ["branding", "form", "social_login", "footer_links"],
        "layouts": ["centered", "split", "full_image"],
        "recommended_theme": "modern-minimal",
    },
    "pricing_page": {
        "description": "Pricing comparison page with tiers and FAQ",
        "sections": ["header", "toggle", "pricing_cards", "comparison_table", "faq"],
        "layouts": ["cards", "table", "hybrid"],
        "recommended_theme": "modern-minimal",
    },
    "blog_post": {
        "description": "Blog article layout with content and sidebar",
        "sections": ["header", "featured_image", "content", "author", "related", "comments"],
        "layouts": ["full_width", "with_sidebar", "magazine"],
        "recommended_theme": "modern-minimal",
    },
    "product_page": {
        "description": "E-commerce product page with gallery and details",
        "sections": ["gallery", "info", "variants", "add_to_cart", "reviews", "related"],
        "layouts": ["split", "stacked", "immersive"],
        "recommended_theme": "modern-minimal",
    },
    "portfolio": {
        "description": "Portfolio/showcase page with projects grid",
        "sections": ["hero", "about", "projects_grid", "skills", "contact"],
        "layouts": ["grid", "masonry", "carousel"],
        "recommended_theme": "modern-minimal",
    },
    "documentation": {
        "description": "Docs page with navigation and content",
        "sections": ["sidebar_nav", "breadcrumb", "content", "toc", "prev_next"],
        "layouts": ["three_column", "two_column", "single"],
        "recommended_theme": "corporate",
    },
    "error_page": {
        "description": "404/500 error page with helpful actions",
        "sections": ["illustration", "message", "actions", "search"],
        "layouts": ["centered", "split", "minimal"],
        "recommended_theme": "modern-minimal",
    },
    "coming_soon": {
        "description": "Coming soon/maintenance page with countdown",
        "sections": ["logo", "countdown", "email_signup", "social_links"],
        "layouts": ["centered", "split_image", "video_background"],
        "recommended_theme": "glassmorphism",
    },
}

# =============================================================================
# THEME PRESETS
# =============================================================================

THEME_PRESETS: Dict[str, Dict[str, Any]] = {
    "modern-minimal": {
        "description": "Clean, professional design with subtle shadows",
        "primary": "blue-600",
        "primary_hover": "blue-700",
        "secondary": "slate-600",
        "background": "white",
        "background_dark": "slate-900",
        "surface": "slate-50",
        "surface_dark": "slate-800",
        "border": "slate-200",
        "border_dark": "slate-700",
        "text": "slate-900",
        "text_dark": "slate-100",
        "text_muted": "slate-500",
        "border_radius": "rounded-lg",
        "shadow": "shadow-sm",
        "shadow_hover": "shadow-md",
        "font": "font-sans",
    },
    "brutalist": {
        "description": "Bold, high-contrast design with sharp edges",
        "primary": "black",
        "primary_hover": "slate-800",
        "secondary": "white",
        "background": "white",
        "background_dark": "black",
        "surface": "slate-100",
        "surface_dark": "slate-900",
        "border": "black",
        "border_dark": "white",
        "text": "black",
        "text_dark": "white",
        "text_muted": "slate-600",
        "border_radius": "rounded-none",
        "border_width": "border-2",
        "shadow": "shadow-[4px_4px_0px_#000]",
        "shadow_hover": "shadow-[6px_6px_0px_#000]",
        "font": "font-mono",
    },
    "glassmorphism": {
        "description": "Frosted glass effect with transparency",
        "primary": "indigo-500",
        "primary_hover": "indigo-600",
        "secondary": "purple-500",
        "background": "slate-900",
        "background_dark": "slate-950",
        "surface": "white/10",
        "surface_dark": "white/5",
        "border": "white/20",
        "border_dark": "white/10",
        "text": "white",
        "text_dark": "white",
        "text_muted": "slate-300",
        "border_radius": "rounded-2xl",
        "backdrop_blur": "backdrop-blur-lg",
        "shadow": "shadow-lg",
        "shadow_hover": "shadow-xl",
        "font": "font-sans",
    },
    "neo-brutalism": {
        "description": "Playful brutalism with bold colors",
        "primary": "yellow-400",
        "primary_hover": "yellow-500",
        "secondary": "pink-400",
        "accent": "cyan-400",
        "background": "amber-50",
        "background_dark": "slate-900",
        "surface": "white",
        "surface_dark": "slate-800",
        "border": "black",
        "border_dark": "white",
        "text": "black",
        "text_dark": "white",
        "text_muted": "slate-600",
        "border_radius": "rounded-xl",
        "border_width": "border-2",
        "shadow": "shadow-[4px_4px_0px_#000]",
        "shadow_hover": "shadow-[6px_6px_0px_#000]",
        "font": "font-sans",
    },
    "soft-ui": {
        "description": "Soft, neumorphic design with subtle depth",
        "primary": "blue-500",
        "primary_hover": "blue-600",
        "secondary": "slate-400",
        "background": "slate-100",
        "background_dark": "slate-800",
        "surface": "slate-100",
        "surface_dark": "slate-700",
        "border": "transparent",
        "border_dark": "transparent",
        "text": "slate-700",
        "text_dark": "slate-200",
        "text_muted": "slate-400",
        "border_radius": "rounded-2xl",
        "shadow": "shadow-[8px_8px_16px_#d1d5db,-8px_-8px_16px_#ffffff]",
        "shadow_dark": "shadow-[8px_8px_16px_#1e293b,-8px_-8px_16px_#475569]",
        "font": "font-sans",
    },
    "corporate": {
        "description": "Professional, trustworthy design",
        "primary": "blue-700",
        "primary_hover": "blue-800",
        "secondary": "slate-600",
        "background": "white",
        "background_dark": "slate-900",
        "surface": "slate-50",
        "surface_dark": "slate-800",
        "border": "slate-300",
        "border_dark": "slate-600",
        "text": "slate-800",
        "text_dark": "slate-100",
        "text_muted": "slate-500",
        "border_radius": "rounded-md",
        "shadow": "shadow",
        "shadow_hover": "shadow-lg",
        "font": "font-sans",
    },
    # New themes added
    "gradient": {
        "description": "Modern gradient-heavy design with vibrant colors",
        "primary": "violet-600",
        "primary_hover": "violet-700",
        "secondary": "fuchsia-500",
        "accent": "cyan-400",
        "background": "white",
        "background_dark": "slate-950",
        "surface": "slate-50",
        "surface_dark": "slate-900",
        "border": "slate-200",
        "border_dark": "slate-700",
        "text": "slate-900",
        "text_dark": "slate-100",
        "text_muted": "slate-500",
        "border_radius": "rounded-2xl",
        "gradient_primary": "bg-gradient-to-r from-violet-600 to-fuchsia-500",
        "gradient_accent": "bg-gradient-to-r from-cyan-400 to-violet-500",
        "shadow": "shadow-lg",
        "shadow_hover": "shadow-xl",
        "font": "font-sans",
    },
    "cyberpunk": {
        "description": "Neon colors on dark background, futuristic aesthetic",
        "primary": "cyan-400",
        "primary_hover": "cyan-300",
        "secondary": "fuchsia-500",
        "accent": "yellow-400",
        "background": "slate-950",
        "background_dark": "black",
        "surface": "slate-900",
        "surface_dark": "slate-950",
        "border": "cyan-500/30",
        "border_dark": "cyan-400/20",
        "text": "slate-100",
        "text_dark": "white",
        "text_muted": "slate-400",
        "border_radius": "rounded-none",
        "border_width": "border",
        "shadow": "shadow-[0_0_15px_rgba(34,211,238,0.3)]",
        "shadow_hover": "shadow-[0_0_25px_rgba(34,211,238,0.5)]",
        "font": "font-mono",
        "glow": True,
    },
    "retro": {
        "description": "80s/90s inspired with warm colors and bold shapes",
        "primary": "orange-500",
        "primary_hover": "orange-600",
        "secondary": "pink-500",
        "accent": "teal-400",
        "background": "amber-50",
        "background_dark": "slate-900",
        "surface": "white",
        "surface_dark": "slate-800",
        "border": "orange-300",
        "border_dark": "orange-600",
        "text": "slate-800",
        "text_dark": "amber-50",
        "text_muted": "slate-600",
        "border_radius": "rounded-lg",
        "border_width": "border-2",
        "shadow": "shadow-[4px_4px_0px_#f97316]",
        "shadow_hover": "shadow-[6px_6px_0px_#f97316]",
        "font": "font-sans",
    },
    "pastel": {
        "description": "Soft pastel colors with gentle aesthetic",
        "primary": "rose-400",
        "primary_hover": "rose-500",
        "secondary": "sky-400",
        "accent": "violet-400",
        "background": "rose-50",
        "background_dark": "slate-800",
        "surface": "white",
        "surface_dark": "slate-700",
        "border": "rose-200",
        "border_dark": "slate-600",
        "text": "slate-700",
        "text_dark": "slate-200",
        "text_muted": "slate-400",
        "border_radius": "rounded-2xl",
        "shadow": "shadow-sm",
        "shadow_hover": "shadow-md",
        "font": "font-sans",
    },
    "dark_mode_first": {
        "description": "Dark mode optimized design with high contrast",
        "primary": "emerald-500",
        "primary_hover": "emerald-400",
        "secondary": "slate-600",
        "background": "slate-900",
        "background_dark": "slate-950",
        "surface": "slate-800",
        "surface_dark": "slate-900",
        "border": "slate-700",
        "border_dark": "slate-600",
        "text": "slate-100",
        "text_dark": "white",
        "text_muted": "slate-400",
        "border_radius": "rounded-xl",
        "shadow": "shadow-lg shadow-black/20",
        "shadow_hover": "shadow-xl shadow-black/30",
        "font": "font-sans",
    },
    "high_contrast": {
        "description": "WCAG AAA accessible with maximum contrast",
        "primary": "blue-800",
        "primary_hover": "blue-900",
        "secondary": "slate-700",
        "background": "white",
        "background_dark": "black",
        "surface": "slate-50",
        "surface_dark": "slate-900",
        "border": "slate-900",
        "border_dark": "white",
        "text": "black",
        "text_dark": "white",
        "text_muted": "slate-700",
        "border_radius": "rounded-md",
        "border_width": "border-2",
        "shadow": "shadow-md",
        "shadow_hover": "shadow-lg",
        "font": "font-sans",
        "contrast_ratio": "7:1",
    },
    "nature": {
        "description": "Earth tones with organic, natural feel",
        "primary": "emerald-600",
        "primary_hover": "emerald-700",
        "secondary": "amber-600",
        "accent": "sky-500",
        "background": "stone-50",
        "background_dark": "stone-900",
        "surface": "white",
        "surface_dark": "stone-800",
        "border": "stone-300",
        "border_dark": "stone-600",
        "text": "stone-800",
        "text_dark": "stone-100",
        "text_muted": "stone-500",
        "border_radius": "rounded-xl",
        "shadow": "shadow-md",
        "shadow_hover": "shadow-lg",
        "font": "font-sans",
    },
    "startup": {
        "description": "Tech startup aesthetic with bold accents",
        "primary": "indigo-600",
        "primary_hover": "indigo-700",
        "secondary": "slate-600",
        "accent": "amber-500",
        "background": "white",
        "background_dark": "slate-900",
        "surface": "slate-50",
        "surface_dark": "slate-800",
        "border": "slate-200",
        "border_dark": "slate-700",
        "text": "slate-900",
        "text_dark": "slate-100",
        "text_muted": "slate-500",
        "border_radius": "rounded-xl",
        "shadow": "shadow-lg",
        "shadow_hover": "shadow-xl",
        "font": "font-sans",
        "gradient_cta": "bg-gradient-to-r from-indigo-600 to-violet-600",
    },
}

# =============================================================================
# SYSTEM PROMPT FOR GEMINI 3 PRO
# =============================================================================

FRONTEND_DESIGN_SYSTEM_PROMPT = """You are an expert frontend designer specializing in TailwindCSS.
Your task is to generate high-quality, production-ready HTML components.

## OUTPUT FORMAT

You MUST respond with valid JSON in this exact format:
{
    "component_id": "unique-component-id",
    "atomic_level": "atom|molecule|organism",
    "html": "<div class=\\"...\\">...</div>",
    "tailwind_classes_used": ["class1", "class2"],
    "accessibility_features": ["aria-label", "focus-visible"],
    "responsive_breakpoints": ["sm", "md", "lg"],
    "dark_mode_support": true,
    "micro_interactions": ["hover:...", "transition-..."],
    "design_notes": "Brief explanation of design decisions"
}

## CRITICAL RULES

1. **Self-Contained HTML**: Generate ONLY the component HTML fragment. Never include:
   - <!DOCTYPE>, <html>, <head>, <body> tags
   - <script> or <style> tags
   - External dependencies or imports

2. **TailwindCSS Only**: Use only TailwindCSS utility classes. Never:
   - Write custom CSS
   - Use inline styles (style="...")
   - Reference external stylesheets

3. **Responsive Design**: Always include responsive variants:
   - Mobile-first approach (base styles for mobile)
   - sm: for 640px+
   - md: for 768px+
   - lg: for 1024px+
   - xl: for 1280px+ (when appropriate)

4. **Dark Mode**: Always include dark: variants for all colors:
   - bg-white dark:bg-slate-800
   - text-slate-900 dark:text-slate-100
   - border-slate-200 dark:border-slate-700

5. **Accessibility (WCAG 2.1 AA)**:
   - aria-label for interactive elements
   - focus-visible:ring-2 for keyboard navigation
   - sr-only for screen reader text
   - Proper heading hierarchy
   - Sufficient color contrast (4.5:1 minimum)

6. **Micro-Interactions**: Include smooth transitions:
   - transition-all duration-200 ease-in-out
   - hover: states for interactive elements
   - focus: states for form elements
   - active: states for buttons

7. **Visual Depth**: Create depth through:
   - Shadows (shadow-sm, shadow-md, shadow-lg)
   - Color gradients where appropriate
   - Subtle borders for separation

8. **Typography**: Use consistent type scale:
   - text-xs, text-sm, text-base, text-lg, text-xl, text-2xl
   - font-medium, font-semibold, font-bold for emphasis
   - tracking-tight for headings
   - leading-relaxed for body text

## DESIGN PRINCIPLES

1. **Hierarchy**: Clear visual hierarchy through size, weight, and spacing
2. **Consistency**: Consistent spacing using Tailwind scale (p-4, gap-6, etc.)
3. **Balance**: Balanced whitespace and content density
4. **Contrast**: Sufficient contrast for readability
5. **Alignment**: Consistent alignment using flexbox/grid

## CONTENT LANGUAGE

All placeholder text, labels, and content MUST be in Turkish:
- Button text: "Gönder", "İptal", "Kaydet", "Devam Et", "Geri"
- Form labels: "E-posta", "Şifre", "Ad Soyad", "Telefon"
- Navigation: "Ana Sayfa", "Hakkımızda", "İletişim", "Hizmetler"
- Auth: "Giriş Yap", "Kayıt Ol", "Şifremi Unuttum"
- Actions: "Ara...", "Filtrele", "Sırala", "Dışa Aktar"
- Feedback: "Başarılı", "Hata", "Uyarı", "Bilgi"
- Use proper Turkish characters: ş, ğ, ü, ö, ç, ı, İ

## OUTPUT QUALITY OPTIMIZATION - MAXIMUM RICHNESS MODE

### Token Allocation Strategy
You MUST produce the MOST DETAILED, COMPREHENSIVE, and RICHEST output possible.
USE ALL AVAILABLE TOKENS to create the most sophisticated design.
More detail = better design. Do NOT economize on output.

### MAXIMUM RICHNESS Content Rules:
1. **Tables**: Generate FULL realistic data
   - Include 8-12 unique, realistic rows with varied data
   - Each row should have different content patterns
   - Include sorting indicators, action buttons per row
   - Add inline status badges, avatars, and icons

2. **Lists/Cards**: Generate COMPLETE content
   - 8-10 fully detailed items with unique content
   - Each item with icon, title, description, metadata
   - Include varied states (new, popular, featured badges)

3. **EXHAUSTIVE Detail Depth** - Spend tokens generously on:
   - EVERY possible hover/focus/active/disabled state
   - Complex multi-layer shadows (shadow-sm AND shadow-inner)
   - Gradient backgrounds with multiple color stops
   - backdrop-blur and glassmorphism effects
   - Ring effects for focus states (ring-2 ring-offset-2)
   - Transform effects (scale, rotate, translate on hover)
   - Multiple transition properties with custom durations
   - Before/after pseudo-element effects via Tailwind
   - SVG icons inline (not just placeholder)
   - Full ARIA attributes (aria-label, aria-describedby, role, etc.)
   - All responsive variants (sm:, md:, lg:, xl:, 2xl:)
   - All dark mode variants (dark:)
   - Print variants where applicable (print:)
   - Motion-safe/motion-reduce variants

4. **ADVANCED Micro-Interactions** - Include ALL of these:
   - hover:scale-105 or hover:scale-[1.02] for subtle zoom
   - hover:-translate-y-1 for lift effects
   - hover:shadow-xl hover:shadow-primary/20 for glow
   - active:scale-95 for press feedback
   - focus-visible:ring-2 focus-visible:ring-offset-2
   - group-hover: for parent-child interactions
   - peer-checked: for sibling interactions
   - transition-all duration-300 ease-out
   - animate-pulse for loading states
   - animate-bounce for attention
   - Custom cubic-bezier via [timing] when needed

5. **RICH Visual Effects** - Always include:
   - Layered shadows: shadow-lg shadow-black/10 dark:shadow-black/30
   - Gradient text: bg-gradient-to-r from-X to-Y bg-clip-text text-transparent
   - Gradient borders: bg-gradient-to-r ... with p-[1px] wrapper
   - Glassmorphism: bg-white/80 backdrop-blur-xl
   - Neumorphism options: shadow-[inset_...]
   - Decorative elements (dots, lines, shapes via absolute positioning)
   - Pattern backgrounds (via SVG or gradient patterns)

6. **INLINE SVG Icons** - Generate actual SVG code:
   - Do NOT use placeholder text like "[icon]"
   - Include FULL SVG markup with proper viewBox
   - Use currentColor for stroke/fill to inherit text color
   - Common icons: arrow, check, x, menu, search, user, etc.

7. **STATE Variations** - Generate HTML for multiple states:
   - Default state
   - Hover state classes
   - Focus state classes
   - Active/pressed state
   - Disabled state (opacity-50 cursor-not-allowed)
   - Loading state (with spinner)
   - Error state (red borders, icons)
   - Success state (green indicators)

8. **REALISTIC Content** - Use meaningful Turkish content:
   - Real product names, prices (₺299,99)
   - Real dates (19 Aralık 2025)
   - Real percentages (+%12,5)
   - Real user names (Ahmet Yılmaz, Ayşe Kaya)
   - Real email formats (ahmet@sirket.com.tr)
   - Real phone formats (+90 532 123 45 67)
   - Real addresses (Kadıköy, İstanbul)

### Quality Maximization Checklist:
Before finalizing, ensure you've MAXIMIZED:
✓ Every interactive element has ALL state variations
✓ Every color has dark: variant
✓ Every spacing is responsive (p-4 md:p-6 lg:p-8)
✓ Every text has proper line-height and letter-spacing
✓ Shadows have color tinting (shadow-primary/20)
✓ Borders have subtle gradients or varied opacity
✓ Icons are REAL SVG, not placeholders
✓ Content is REALISTIC Turkish, not lorem ipsum
✓ Animations use appropriate easing (ease-out, ease-in-out)
✓ Focus indicators are visible and styled
✓ Touch targets are minimum 44x44px
✓ Decorative elements add visual interest

## ITERATION/REFINEMENT MODE

When refining existing HTML (previous_html provided):
1. Preserve the overall structure unless explicitly asked to change
2. Only modify the specific elements mentioned in modifications
3. Maintain consistency with existing style choices
4. Keep all existing accessibility features
5. Return the COMPLETE modified HTML, not just the changed parts

## PROJECT CONTEXT

{project_context}

## RESPONSE GUIDELINES

- Generate unique, creative designs for each request
- Do not copy or reuse example patterns
- Tailor every component to the specific context provided
- Focus on the user's exact requirements and style guide
- Every class should serve a purpose - no redundant styles"""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_component_preset(component_type: str) -> Dict[str, Any]:
    """Get preset configuration for a component type.

    Args:
        component_type: The type of component (e.g., 'button', 'card', 'navbar')

    Returns:
        Dict with component preset configuration, or empty dict if not found.
    """
    return COMPONENT_PRESETS.get(component_type, {})


def get_theme_preset(theme_name: str) -> Dict[str, Any]:
    """Get preset configuration for a theme.

    Args:
        theme_name: The theme name (e.g., 'modern-minimal', 'brutalist')

    Returns:
        Dict with theme preset configuration, or default theme if not found.
    """
    return THEME_PRESETS.get(theme_name, THEME_PRESETS["modern-minimal"])


def get_available_components() -> List[str]:
    """Get list of available component types.

    Returns:
        List of component type names.
    """
    return list(COMPONENT_PRESETS.keys())


def get_available_themes() -> List[str]:
    """Get list of available theme names.

    Returns:
        List of theme names.
    """
    return list(THEME_PRESETS.keys())


def get_page_template(template_name: str) -> Dict[str, Any]:
    """Get preset configuration for a page template.

    Args:
        template_name: The template name (e.g., 'landing_page', 'dashboard')

    Returns:
        Dict with template preset configuration, or empty dict if not found.
    """
    return PAGE_TEMPLATES.get(template_name, {})


def get_available_templates() -> List[str]:
    """Get list of available page template names.

    Returns:
        List of template names.
    """
    return list(PAGE_TEMPLATES.keys())


def build_style_guide(
    theme: str,
    dark_mode: bool = True,
    border_radius: str = "",
    custom_overrides: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Build a complete style guide from theme and customizations.

    Args:
        theme: Theme name to use as base.
        dark_mode: Whether to include dark mode variants.
        border_radius: Custom border radius override.
        custom_overrides: Additional style overrides.

    Returns:
        Complete style guide dictionary.
    """
    style_guide = get_theme_preset(theme).copy()
    style_guide["dark_mode_enabled"] = dark_mode

    if border_radius:
        style_guide["border_radius"] = border_radius

    if custom_overrides:
        style_guide.update(custom_overrides)

    return style_guide


def build_system_prompt(project_context: str = "") -> str:
    """Build the system prompt with project context.

    Args:
        project_context: Project-specific context to inject into the prompt.
            Should describe the project's purpose, target audience, tone, etc.

    Returns:
        Complete system prompt with project context.
    """
    if not project_context:
        project_context = "No specific project context provided. Generate a generic, professional design."

    # Use replace() instead of format() to avoid issues with JSON curly braces
    return FRONTEND_DESIGN_SYSTEM_PROMPT.replace("{project_context}", project_context)


def build_refinement_prompt(previous_html: str, modifications: str, project_context: str = "") -> str:
    """Build a prompt for refining existing HTML.

    Args:
        previous_html: The existing HTML to refine.
        modifications: Natural language description of desired changes.
        project_context: Optional project context.

    Returns:
        Complete refinement prompt.
    """
    base_prompt = build_system_prompt(project_context)

    refinement_section = f"""
## REFINEMENT TASK

You are refining an existing component. Here is the current HTML:

```html
{previous_html}
```

### Requested Modifications:
{modifications}

### Instructions:
1. Apply ONLY the requested modifications
2. Preserve all other styling, structure, and accessibility features
3. Return the COMPLETE modified HTML in the standard JSON format
4. Explain what changes you made in design_notes
"""

    return base_prompt + refinement_section


# =============================================================================
# ADVANCED LIBRARY HELPER FUNCTIONS
# =============================================================================


def get_micro_interaction(interaction_name: str) -> Dict[str, Any]:
    """Get a micro-interaction preset by name.

    Args:
        interaction_name: Name of the interaction (e.g., 'hover_lift', 'focus_ring')

    Returns:
        Dict with classes and description, or empty dict if not found.
    """
    return MICRO_INTERACTIONS.get(interaction_name, {})


def get_all_micro_interactions() -> Dict[str, Dict[str, Any]]:
    """Get all available micro-interactions.

    Returns:
        Complete MICRO_INTERACTIONS dictionary.
    """
    return MICRO_INTERACTIONS


def get_visual_effect(effect_name: str) -> Dict[str, Any]:
    """Get a visual effect preset by name.

    Args:
        effect_name: Name of the effect (e.g., 'glassmorphism_light', 'neon_glow_blue')

    Returns:
        Dict with classes and description, or empty dict if not found.
    """
    return VISUAL_EFFECTS.get(effect_name, {})


def get_all_visual_effects() -> Dict[str, Dict[str, Any]]:
    """Get all available visual effects.

    Returns:
        Complete VISUAL_EFFECTS dictionary.
    """
    return VISUAL_EFFECTS


def get_svg_icon(icon_name: str) -> str:
    """Get an SVG icon by name.

    Args:
        icon_name: Name of the icon (e.g., 'arrow_right', 'check', 'user')

    Returns:
        SVG string or empty string if not found.
    """
    return SVG_ICONS.get(icon_name, "")


def get_all_svg_icons() -> Dict[str, str]:
    """Get all available SVG icons.

    Returns:
        Complete SVG_ICONS dictionary.
    """
    return SVG_ICONS


def get_available_icon_names() -> List[str]:
    """Get list of available icon names.

    Returns:
        List of icon names.
    """
    return list(SVG_ICONS.keys())


def build_rich_style_guide(
    theme: str,
    dark_mode: bool = True,
    border_radius: str = "",
    include_micro_interactions: bool = True,
    include_visual_effects: bool = True,
    custom_overrides: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Build a comprehensive style guide with all available effects.

    This enhanced style guide includes micro-interactions and visual effects
    references for maximum design richness.

    Args:
        theme: Theme name to use as base.
        dark_mode: Whether to include dark mode variants.
        border_radius: Custom border radius override.
        include_micro_interactions: Include micro-interaction presets.
        include_visual_effects: Include visual effect presets.
        custom_overrides: Additional style overrides.

    Returns:
        Comprehensive style guide dictionary.
    """
    style_guide = get_theme_preset(theme).copy()
    style_guide["dark_mode_enabled"] = dark_mode

    if border_radius:
        style_guide["border_radius"] = border_radius

    if include_micro_interactions:
        style_guide["micro_interactions_library"] = {
            name: preset["classes"]
            for name, preset in MICRO_INTERACTIONS.items()
            if "classes" in preset
        }

    if include_visual_effects:
        style_guide["visual_effects_library"] = {
            name: preset["classes"]
            for name, preset in VISUAL_EFFECTS.items()
            if "classes" in preset
        }

    if custom_overrides:
        style_guide.update(custom_overrides)

    return style_guide
