"""Frontend design presets and system prompts for Gemini 3 Pro.

This module contains:
- Component type presets (Atomic Design levels)
- Theme presets (visual styles)
- System prompt for Gemini to generate high-quality TailwindCSS/HTML
"""

from typing import Any, Dict, List, Optional

# =============================================================================
# MICRO-INTERACTIONS LIBRARY
# =============================================================================

MICRO_INTERACTIONS: Dict[str, Dict[str, Any]] = {
    # Hover Effects
    "hover_lift": {
        "classes": "hover:-translate-y-1 hover:shadow-xl transition-all duration-300 ease-out",
        "description": "Lifts element up on hover with shadow",
    },
    "hover_glow": {
        "classes": "hover:shadow-lg hover:shadow-primary/25 transition-shadow duration-300",
        "description": "Adds glowing shadow on hover",
    },
    "hover_scale": {
        "classes": "hover:scale-105 active:scale-95 transition-transform duration-200 ease-out",
        "description": "Scales up on hover, down on click",
    },
    "hover_brightness": {
        "classes": "hover:brightness-110 transition-all duration-200",
        "description": "Brightens element on hover",
    },
    "hover_rotate": {
        "classes": "hover:rotate-3 transition-transform duration-300",
        "description": "Slight rotation on hover",
    },
    # Focus Effects
    "focus_ring": {
        "classes": "focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 outline-none",
        "description": "Accessible focus ring indicator",
    },
    "focus_glow": {
        "classes": "focus:shadow-[0_0_0_3px_rgba(59,130,246,0.5)] outline-none transition-shadow duration-200",
        "description": "Glowing focus indicator",
    },
    # Animation Effects
    "shimmer": {
        "classes": "animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent",
        "description": "Shimmer loading effect",
    },
    "pulse": {
        "classes": "animate-pulse",
        "description": "Subtle pulsing animation",
    },
    "bounce": {
        "classes": "animate-bounce",
        "description": "Bouncing animation",
    },
    "spin": {
        "classes": "animate-spin",
        "description": "Spinning animation for loaders",
    },
    "ping": {
        "classes": "animate-ping",
        "description": "Expanding ping effect",
    },
    # Group Effects
    "group_reveal": {
        "classes": "opacity-0 group-hover:opacity-100 transition-opacity duration-300",
        "description": "Reveals on parent hover",
    },
    "group_slide": {
        "classes": "translate-y-2 group-hover:translate-y-0 opacity-0 group-hover:opacity-100 transition-all duration-300",
        "description": "Slides up and reveals on parent hover",
    },
    # Click Effects
    "click_ripple": {
        "classes": "relative overflow-hidden active:after:animate-ripple after:absolute after:inset-0 after:bg-white/30 after:rounded-full after:scale-0",
        "description": "Material-style ripple on click",
    },
    "press_down": {
        "classes": "active:scale-95 transition-transform duration-100",
        "description": "Scales down on press",
    },
    # State Transitions
    "smooth_all": {
        "classes": "transition-all duration-300 ease-in-out",
        "description": "Smooth transition for all properties",
    },
    "smooth_colors": {
        "classes": "transition-colors duration-200",
        "description": "Smooth color transitions",
    },
}

# =============================================================================
# VISUAL EFFECTS LIBRARY
# =============================================================================

VISUAL_EFFECTS: Dict[str, Dict[str, Any]] = {
    # Glassmorphism
    "glassmorphism_light": {
        "classes": "bg-white/70 backdrop-blur-xl border border-white/20 shadow-xl",
        "description": "Light frosted glass effect",
    },
    "glassmorphism_dark": {
        "classes": "bg-slate-900/70 backdrop-blur-xl border border-white/10 shadow-2xl",
        "description": "Dark frosted glass effect",
    },
    "glassmorphism_colored": {
        "classes": "bg-primary/20 backdrop-blur-xl border border-primary/20 shadow-xl",
        "description": "Colored glass effect",
    },
    # Neumorphism
    "neumorphism_raised": {
        "classes": "bg-slate-100 shadow-[8px_8px_16px_#d1d5db,-8px_-8px_16px_#ffffff]",
        "description": "Raised soft UI effect",
    },
    "neumorphism_pressed": {
        "classes": "bg-slate-100 shadow-[inset_8px_8px_16px_#d1d5db,inset_-8px_-8px_16px_#ffffff]",
        "description": "Pressed soft UI effect",
    },
    "neumorphism_dark": {
        "classes": "bg-slate-800 shadow-[8px_8px_16px_#1e293b,-8px_-8px_16px_#334155]",
        "description": "Dark mode soft UI effect",
    },
    # Neon/Glow
    "neon_glow_blue": {
        "classes": "shadow-[0_0_10px_#3b82f6,0_0_20px_#3b82f6,0_0_40px_#3b82f6]",
        "description": "Blue neon glow",
    },
    "neon_glow_purple": {
        "classes": "shadow-[0_0_10px_#8b5cf6,0_0_20px_#8b5cf6,0_0_40px_#8b5cf6]",
        "description": "Purple neon glow",
    },
    "neon_glow_pink": {
        "classes": "shadow-[0_0_10px_#ec4899,0_0_20px_#ec4899,0_0_40px_#ec4899]",
        "description": "Pink neon glow",
    },
    "neon_glow_green": {
        "classes": "shadow-[0_0_10px_#22c55e,0_0_20px_#22c55e,0_0_40px_#22c55e]",
        "description": "Green neon glow",
    },
    # Gradient Effects
    "gradient_border": {
        "classes": "relative before:absolute before:inset-0 before:p-[2px] before:rounded-inherit before:bg-gradient-to-r before:from-blue-500 before:to-purple-500 before:-z-10",
        "description": "Gradient border effect",
    },
    "gradient_text": {
        "classes": "bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent",
        "description": "Gradient text color",
    },
    "gradient_shine": {
        "classes": "bg-gradient-to-r from-transparent via-white/20 to-transparent bg-[length:200%_100%] animate-[shine_2s_infinite]",
        "description": "Animated shine effect",
    },
    # Shadow Effects
    "shadow_layered": {
        "classes": "shadow-[0_1px_2px_rgba(0,0,0,0.1),0_2px_4px_rgba(0,0,0,0.1),0_4px_8px_rgba(0,0,0,0.1),0_8px_16px_rgba(0,0,0,0.1)]",
        "description": "Multi-layer shadow for depth",
    },
    "shadow_colored": {
        "classes": "shadow-xl shadow-primary/20",
        "description": "Colored shadow matching theme",
    },
}

# =============================================================================
# SVG ICONS LIBRARY (Heroicons-style)
# =============================================================================

SVG_ICONS: Dict[str, str] = {
    # Navigation
    "arrow_right": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>',
    "arrow_left": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>',
    "arrow_up": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>',
    "arrow_down": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>',
    "chevron_right": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>',
    "chevron_down": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>',
    "external_link": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>',
    # Actions
    "check": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>',
    "x": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>',
    "plus": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>',
    "minus": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>',
    "edit": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>',
    "trash": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>',
    "copy": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>',
    "download": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>',
    "upload": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>',
    "refresh": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>',
    # UI Elements
    "search": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>',
    "menu": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>',
    "dots_vertical": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"/></svg>',
    "filter": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/></svg>',
    "settings": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>',
    # Status
    "check_circle": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "x_circle": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "exclamation_circle": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "info_circle": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "question_circle": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    # User
    "user": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>',
    "users": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>',
    # Communication
    "mail": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>',
    "phone": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>',
    "chat": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>',
    "bell": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>',
    # Commerce
    "cart": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/></svg>',
    "credit_card": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/></svg>',
    "tag": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/></svg>',
    # Media
    "photo": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
    "video": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>',
    "play": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    # Files
    "document": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>',
    "folder": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>',
    "clipboard": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>',
    # Misc
    "home": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>',
    "calendar": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
    "clock": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "location": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>',
    "star": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>',
    "star_filled": '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>',
    "heart": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>',
    "heart_filled": '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>',
    "globe": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/></svg>',
    "lock": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>',
    "unlock": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"/></svg>',
    "eye": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>',
    "eye_off": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/></svg>',
    "sun": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>',
    "moon": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>',
    "lightning": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>',
    "fire": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z"/></svg>',
    "sparkles": '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>',
    "loading": '<svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>',
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

## CSS RICHNESS & VISUAL DENSITY (CRITICAL)

Your output MUST be visually rich and CSS-heavy. This is NOT about adding more content/data,
but about creating sophisticated visual styling with dense Tailwind classes.

### MANDATORY Background Complexity
Every section MUST include rich background treatments:
```html
<!-- MINIMUM background structure for sections -->
<section class="relative overflow-hidden">
  <!-- Layer 1: Base gradient -->
  <div class="absolute inset-0 bg-gradient-to-br from-slate-50 via-white to-indigo-50/30 dark:from-slate-950 dark:via-slate-900 dark:to-indigo-950/20"></div>

  <!-- Layer 2: Animated blur blobs (at least 3) -->
  <div class="absolute top-0 left-1/4 w-96 h-96 bg-indigo-400/20 rounded-full blur-3xl animate-blob"></div>
  <div class="absolute top-1/3 right-1/4 w-80 h-80 bg-purple-400/20 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
  <div class="absolute bottom-0 left-1/2 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl animate-blob animation-delay-4000"></div>

  <!-- Layer 3: Grid/dot pattern overlay -->
  <div class="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,rgba(0,0,0,0.05)_1px,transparent_0)] bg-[length:24px_24px] dark:bg-[radial-gradient(circle_at_1px_1px,rgba(255,255,255,0.03)_1px,transparent_0)]"></div>

  <!-- Layer 4: Gradient overlay for depth -->
  <div class="absolute inset-0 bg-gradient-to-t from-white/80 via-transparent to-white/40 dark:from-slate-950/80 dark:to-slate-950/40"></div>

  <!-- Content wrapper with relative positioning -->
  <div class="relative z-10">
    <!-- Actual content here -->
  </div>
</section>
```

### MANDATORY Element Styling Depth
Each interactive element MUST have multiple layers of styling:
```html
<!-- Buttons: NOT just bg-indigo-600, but RICH styling -->
<button class="
  relative overflow-hidden
  bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600
  hover:from-indigo-500 hover:via-indigo-400 hover:to-purple-500
  text-white font-semibold
  px-8 py-4
  rounded-xl
  shadow-lg shadow-indigo-500/30
  hover:shadow-xl hover:shadow-indigo-500/40
  hover:-translate-y-0.5
  active:translate-y-0
  transition-all duration-300 ease-out
  focus:outline-none focus:ring-4 focus:ring-indigo-500/50 focus:ring-offset-2
  before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/20 before:to-transparent before:opacity-0 before:hover:opacity-100 before:transition-opacity
  group
">
  <span class="relative z-10 flex items-center gap-2">
    <span>Button Text</span>
    <svg class="w-5 h-5 transform group-hover:translate-x-1 transition-transform">...</svg>
  </span>
</button>

<!-- Cards: Multi-layer borders and shadows -->
<div class="
  relative
  bg-white dark:bg-slate-800
  rounded-2xl
  border border-slate-200/50 dark:border-slate-700/50
  shadow-xl shadow-slate-200/50 dark:shadow-slate-900/50
  hover:shadow-2xl hover:shadow-indigo-500/10
  hover:border-indigo-200 dark:hover:border-indigo-800
  transition-all duration-500
  overflow-hidden
  group
">
  <!-- Gradient border effect -->
  <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-transparent to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
  <!-- Content -->
  <div class="relative p-6">...</div>
</div>
```

### MANDATORY Rich Text Styling
Headings and text MUST use gradient text, decorative underlines, or glow effects:
```html
<!-- Gradient text -->
<h1 class="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight bg-gradient-to-r from-slate-900 via-indigo-900 to-slate-900 dark:from-white dark:via-indigo-200 dark:to-white bg-clip-text text-transparent">

<!-- With decorative underline -->
<h2 class="relative inline-block text-3xl font-bold text-slate-900 dark:text-white">
  <span>Feature Title</span>
  <span class="absolute -bottom-2 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full"></span>
</h2>

<!-- With glow effect -->
<span class="text-indigo-600 dark:text-indigo-400 drop-shadow-[0_0_15px_rgba(99,102,241,0.5)]">
```

### Visual Complexity Requirements
1. **Sections**: Minimum 4 background layers (gradient + blobs + pattern + overlay)
2. **Buttons**: Gradient background + shadow with color + hover transform + focus ring
3. **Cards**: Border + shadow + hover glow + gradient overlay on hover
4. **Inputs**: Ring on focus + border transition + icon animations
5. **Icons**: Background circles/squares + shadow + hover scale
6. **Dividers**: Gradient lines, not solid colors
7. **Badges**: Glow effects, gradient backgrounds

### Animation Requirements
Include these animation classes generously:
- `animate-pulse` for loading states and highlights
- `animate-bounce` for attention-grabbing elements
- `animate-blob` for background blobs (custom)
- `group-hover:` transitions for coordinated animations
- `hover:-translate-y-1` for lift effects
- `hover:scale-105` for grow effects
- `transition-all duration-300` on ALL interactive elements

### Shadow Layering
Use compound shadows for depth:
```html
<!-- Light mode -->
shadow-lg shadow-slate-200/50 hover:shadow-xl hover:shadow-indigo-500/25

<!-- Dark mode -->
dark:shadow-slate-900/50 dark:hover:shadow-indigo-500/20
```

### MINIMUM CLASS COUNT PER ELEMENT
- Sections: 15+ Tailwind classes
- Buttons: 20+ Tailwind classes
- Cards: 18+ Tailwind classes
- Inputs: 15+ Tailwind classes
- Text elements: 8+ Tailwind classes
- Icons: 10+ Tailwind classes

If your output has elements with fewer classes, ADD MORE VISUAL STYLING.

## JAVASCRIPT INTERACTIVITY (MANDATORY)

Your output MUST include interactive JavaScript behaviors. Use Alpine.js syntax for lightweight,
inline interactivity that works without build tools.

### MANDATORY Alpine.js Integration
ALWAYS include `x-data` on interactive containers. Every component MUST have at least one
interactive behavior.

```html
<!-- Required: Alpine.js CDN in production (not in output, but behaviors must be Alpine-ready) -->
<!-- Components use Alpine.js x-* attributes for interactivity -->

<!-- Dropdown with full state management -->
<div x-data="{ open: false, selected: null }" class="relative">
  <button @click="open = !open" class="...">
    <span x-text="selected || 'Seçiniz'"></span>
    <svg :class="{ 'rotate-180': open }" class="transform transition-transform duration-200">...</svg>
  </button>
  <div x-show="open"
       x-transition:enter="transition ease-out duration-200"
       x-transition:enter-start="opacity-0 translate-y-1"
       x-transition:enter-end="opacity-100 translate-y-0"
       x-transition:leave="transition ease-in duration-150"
       x-transition:leave-start="opacity-100 translate-y-0"
       x-transition:leave-end="opacity-0 translate-y-1"
       @click.outside="open = false"
       class="absolute mt-2 ...">
    <template x-for="item in ['Seçenek 1', 'Seçenek 2', 'Seçenek 3']">
      <button @click="selected = item; open = false" class="...">
        <span x-text="item"></span>
      </button>
    </template>
  </div>
</div>
```

### MANDATORY Interactive Patterns by Component Type

**Navigation/Menus:**
```html
<nav x-data="{ mobileOpen: false, activeDropdown: null }">
  <!-- Mobile toggle -->
  <button @click="mobileOpen = !mobileOpen" class="md:hidden">
    <span x-show="!mobileOpen">☰</span>
    <span x-show="mobileOpen">✕</span>
  </button>

  <!-- Dropdown menu -->
  <div @mouseenter="activeDropdown = 'products'" @mouseleave="activeDropdown = null">
    <button>Ürünler</button>
    <div x-show="activeDropdown === 'products'"
         x-transition:enter="transition ease-out duration-100"
         x-transition:enter-start="opacity-0 scale-95"
         x-transition:enter-end="opacity-100 scale-100">
      <!-- Dropdown content -->
    </div>
  </div>
</nav>
```

**Modals/Dialogs:**
```html
<div x-data="{ modalOpen: false }">
  <button @click="modalOpen = true">Modal Aç</button>

  <div x-show="modalOpen"
       x-transition:enter="transition ease-out duration-300"
       x-transition:enter-start="opacity-0"
       x-transition:enter-end="opacity-100"
       x-transition:leave="transition ease-in duration-200"
       x-transition:leave-start="opacity-100"
       x-transition:leave-end="opacity-0"
       class="fixed inset-0 z-50">
    <!-- Backdrop -->
    <div @click="modalOpen = false" class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>

    <!-- Modal content with separate animation -->
    <div x-show="modalOpen"
         x-transition:enter="transition ease-out duration-300 delay-75"
         x-transition:enter-start="opacity-0 scale-95 translate-y-4"
         x-transition:enter-end="opacity-100 scale-100 translate-y-0"
         class="relative ...">
      <button @click="modalOpen = false" class="absolute top-4 right-4">✕</button>
      <!-- Content -->
    </div>
  </div>
</div>
```

**Tabs:**
```html
<div x-data="{ activeTab: 'tab1' }">
  <div class="flex gap-2 border-b">
    <button @click="activeTab = 'tab1'"
            :class="{ 'border-b-2 border-indigo-500 text-indigo-600': activeTab === 'tab1' }"
            class="px-4 py-2 transition-all duration-200">
      Sekme 1
    </button>
    <button @click="activeTab = 'tab2'"
            :class="{ 'border-b-2 border-indigo-500 text-indigo-600': activeTab === 'tab2' }">
      Sekme 2
    </button>
  </div>

  <div x-show="activeTab === 'tab1'" x-transition.opacity.duration.200ms>Tab 1 içeriği</div>
  <div x-show="activeTab === 'tab2'" x-transition.opacity.duration.200ms>Tab 2 içeriği</div>
</div>
```

**Accordions:**
```html
<div x-data="{ openItem: null }">
  <div class="border rounded-lg overflow-hidden">
    <template x-for="(item, index) in [
      { q: 'Soru 1?', a: 'Cevap 1' },
      { q: 'Soru 2?', a: 'Cevap 2' },
      { q: 'Soru 3?', a: 'Cevap 3' }
    ]" :key="index">
      <div class="border-b last:border-b-0">
        <button @click="openItem = openItem === index ? null : index"
                class="w-full flex justify-between items-center p-4 hover:bg-slate-50 transition-colors">
          <span x-text="item.q" class="font-medium"></span>
          <svg :class="{ 'rotate-180': openItem === index }"
               class="w-5 h-5 transform transition-transform duration-300">
            <path d="M19 9l-7 7-7-7"/>
          </svg>
        </button>
        <div x-show="openItem === index"
             x-collapse
             x-transition:enter="transition-all ease-out duration-300"
             x-transition:leave="transition-all ease-in duration-200"
             class="px-4 pb-4 text-slate-600">
          <span x-text="item.a"></span>
        </div>
      </div>
    </template>
  </div>
</div>
```

**Form Validation:**
```html
<form x-data="{
  form: { email: '', password: '' },
  errors: {},
  loading: false,
  validate() {
    this.errors = {};
    if (!this.form.email) this.errors.email = 'E-posta gerekli';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.form.email))
      this.errors.email = 'Geçerli bir e-posta girin';
    if (!this.form.password) this.errors.password = 'Şifre gerekli';
    else if (this.form.password.length < 8)
      this.errors.password = 'Şifre en az 8 karakter olmalı';
    return Object.keys(this.errors).length === 0;
  },
  async submit() {
    if (!this.validate()) return;
    this.loading = true;
    // Simulated API call
    await new Promise(r => setTimeout(r, 1500));
    this.loading = false;
  }
}" @submit.prevent="submit">
  <div class="space-y-4">
    <div>
      <input type="email" x-model="form.email"
             :class="{ 'border-red-500 focus:ring-red-500': errors.email }"
             @input="errors.email = ''"
             placeholder="E-posta"
             class="w-full px-4 py-3 border rounded-lg transition-all duration-200
                    focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
      <p x-show="errors.email" x-text="errors.email"
         x-transition:enter="transition ease-out duration-200"
         x-transition:enter-start="opacity-0 -translate-y-1"
         class="mt-1 text-sm text-red-500"></p>
    </div>

    <button type="submit" :disabled="loading"
            :class="{ 'opacity-75 cursor-not-allowed': loading }"
            class="w-full py-3 bg-indigo-600 text-white rounded-lg transition-all duration-200
                   hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-500/50">
      <span x-show="!loading">Giriş Yap</span>
      <span x-show="loading" class="flex items-center justify-center gap-2">
        <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">...</svg>
        Yükleniyor...
      </span>
    </button>
  </div>
</form>
```

**Counters & Animating Numbers:**
```html
<div x-data="{ count: 0, target: 1234, animating: false }"
     x-intersect="if (!animating) { animating = true;
       let start = 0; const duration = 2000; const step = target / (duration / 16);
       const timer = setInterval(() => {
         count = Math.min(Math.ceil(count + step), target);
         if (count >= target) clearInterval(timer);
       }, 16);
     }">
  <span x-text="count.toLocaleString('tr-TR')" class="text-5xl font-bold"></span>
</div>
```

**Scroll Animations (Intersection Observer):**
```html
<div x-data="{ visible: false }"
     x-intersect:enter="visible = true"
     x-intersect:leave="visible = false"
     :class="{ 'opacity-100 translate-y-0': visible, 'opacity-0 translate-y-8': !visible }"
     class="transition-all duration-700 ease-out">
  <!-- Content animates in when scrolled into view -->
</div>
```

**Toast Notifications:**
```html
<div x-data="{ toasts: [] }" @notify.window="toasts.push($event.detail);
     setTimeout(() => toasts.shift(), 3000)">
  <template x-for="(toast, index) in toasts" :key="index">
    <div x-show="true"
         x-transition:enter="transition ease-out duration-300"
         x-transition:enter-start="opacity-0 translate-x-full"
         x-transition:enter-end="opacity-100 translate-x-0"
         x-transition:leave="transition ease-in duration-200"
         x-transition:leave-start="opacity-100 translate-x-0"
         x-transition:leave-end="opacity-0 translate-x-full"
         :class="{
           'bg-green-500': toast.type === 'success',
           'bg-red-500': toast.type === 'error',
           'bg-blue-500': toast.type === 'info'
         }"
         class="fixed bottom-4 right-4 px-6 py-3 text-white rounded-lg shadow-lg">
      <span x-text="toast.message"></span>
    </div>
  </template>
</div>
```

### MINIMUM JavaScript Requirements per Component

| Component Type | Required Interactions |
|----------------|----------------------|
| Navbar | Mobile menu toggle, dropdown hover/click |
| Hero | Optional: scroll indicator, typing animation |
| Cards | Hover reveal, expand/collapse |
| Forms | Live validation, loading states, error display |
| Modals | Open/close with transitions, backdrop click |
| Tabs | Tab switching with transitions |
| Accordions | Expand/collapse with smooth height |
| Dropdowns | Open/close, selection state |
| Pricing | Toggle billing (monthly/yearly) |
| Testimonials | Carousel navigation, auto-play |
| Stats | Counter animation on scroll |
| FAQ | Accordion behavior |

### JavaScript Transition Classes (ALWAYS Include)
```html
x-transition:enter="transition ease-out duration-200"
x-transition:enter-start="opacity-0 scale-95 translate-y-2"
x-transition:enter-end="opacity-100 scale-100 translate-y-0"
x-transition:leave="transition ease-in duration-150"
x-transition:leave-start="opacity-100 scale-100 translate-y-0"
x-transition:leave-end="opacity-0 scale-95 translate-y-2"
```

### DO NOT Generate Bare Static HTML
If a component has interactive potential, you MUST add Alpine.js behaviors:
- NO bare `<button>` without `@click` handler
- NO dropdown markup without `x-show` and `x-transition`
- NO tabs without `x-data` state management
- NO accordion without collapse/expand logic
- NO form without validation state

### GRACEFUL DEGRADATION (CRITICAL)
JavaScript may not load (CDN failure, file:// protocol, ad blockers). Your HTML MUST look good WITHOUT JS!

**CSS-First Animation Strategy:**
Instead of JS-only animations, prefer CSS animations with JS enhancement:

```html
<!-- BAD: JS-only typing effect - broken without Alpine.js -->
<span x-text="currentWord"></span>

<!-- GOOD: CSS animation with JS enhancement -->
<span class="inline-block">
  <!-- Fallback static text visible without JS -->
  <span class="animate-pulse bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
    Hızlandırın
  </span>
</span>

<!-- For typing effects, use CSS animation as fallback: -->
<style>
@keyframes typing {
  0%, 20% { content: "Hızlandırın"; }
  33%, 53% { content: "Otomatize Edin"; }
  66%, 86% { content: "Ölçekleyin"; }
}
</style>
```

**Always Include CSS-Only Alternatives:**
1. **Scroll animations**: Use `@keyframes` with `animation-delay` instead of `x-intersect`
   ```html
   <!-- CSS scroll-triggered via animation-timeline (modern browsers) -->
   <div class="animate-fade-in-up [animation-timeline:view()] [animation-range:entry_25%_cover_50%]">

   <!-- Fallback: simple fade-in on load -->
   <div class="opacity-0 animate-[fadeIn_0.6s_ease-out_0.3s_forwards]">
   ```

2. **Hover states**: CSS `:hover` works without JS
   ```html
   <div class="group">
     <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
       Revealed on hover (no JS needed)
     </div>
   </div>
   ```

3. **Accordions**: Use `<details>/<summary>` as base
   ```html
   <details class="group" x-data="{ open: false }">
     <summary @click="open = !open" class="cursor-pointer list-none">
       <span>Soru başlığı</span>
       <svg class="group-open:rotate-180 transition-transform">...</svg>
     </summary>
     <div class="group-open:animate-accordion-down">Cevap içeriği</div>
   </details>
   ```

4. **Modals**: Use `:target` pseudo-class as fallback
   ```html
   <a href="#modal">Modal Aç</a>
   <div id="modal" class="fixed inset-0 opacity-0 pointer-events-none target:opacity-100 target:pointer-events-auto transition-opacity">
     <a href="#" class="absolute inset-0 bg-black/50"></a>
     <div class="relative">Modal içeriği</div>
   </div>
   ```

5. **Tabs**: Use radio buttons as CSS-only fallback
   ```html
   <div class="tabs">
     <input type="radio" name="tabs" id="tab1" checked class="peer/tab1 hidden">
     <input type="radio" name="tabs" id="tab2" class="peer/tab2 hidden">
     <label for="tab1" class="peer-checked/tab1:border-b-2 peer-checked/tab1:border-indigo-500">Sekme 1</label>
     <label for="tab2" class="peer-checked/tab2:border-b-2 peer-checked/tab2:border-indigo-500">Sekme 2</label>
     <div class="hidden peer-checked/tab1:block">Tab 1 içeriği</div>
     <div class="hidden peer-checked/tab2:block">Tab 2 içeriği</div>
   </div>
   ```

**Mandatory Fallback Rules:**
- NEVER use `x-text` for critical content - always have visible fallback text
- NEVER hide essential UI with `x-show` only - use CSS classes as base state
- ALWAYS test mental model: "What does user see if JS fails?"
- Dynamic content (typing, counters) MUST show static fallback first
- Modals/dropdowns closed by default is OK (user can't open, but page works)

**@keyframes Definitions to Include:**
When using animations, define them inline or note they're needed:
```html
<!-- Include in <style> or note for Tailwind config -->
<style>
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes blob {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(30px, -50px) scale(1.1); }
    66% { transform: translate(-20px, 20px) scale(0.9); }
  }
  .animate-fade-in-up { animation: fadeInUp 0.6s ease-out forwards; }
  .animate-blob { animation: blob 7s infinite; }
  .animation-delay-2000 { animation-delay: 2s; }
  .animation-delay-4000 { animation-delay: 4s; }
</style>
```

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
USE ALL AVAILABLE TOKENS to create the most sophisticated, production-ready designs.
DO NOT hold back - generate MAXIMUM content with MAXIMUM detail.

### MAXIMUM RICHNESS Content Rules:
1. **Tables**: Generate 8-12 UNIQUE rows with realistic Turkish data
   - Names: Ahmet Yılmaz, Zeynep Kaya, Mehmet Demir, Ayşe Öztürk, etc.
   - Emails: ahmet.yilmaz@email.com, zeynep@sirket.com, etc.
   - Prices: ₺1.299, ₺2.450, ₺899, etc.
   - Dates: 15 Aralık 2024, 3 Ocak 2025, etc.
   - Each row MUST have unique, realistic content

2. **Lists/Cards**: Generate 6-10 items with FULL detail
   - Each item with unique content, icons, and states
   - Include variations in length and complexity
   - Never use placeholder text like "Item 1", "Item 2"

3. **EXHAUSTIVE Detail Depth**: Generate ALL of these:
   - EVERY hover state with smooth transitions
   - EVERY focus state with visible ring
   - EVERY active/pressed state
   - EVERY disabled state (opacity, cursor)
   - Loading states with skeleton/shimmer
   - Error states with red indicators
   - Success states with green indicators
   - Responsive variants: sm:, md:, lg:, xl:
   - Dark mode variants: dark:

4. **ADVANCED Micro-Interactions**: Use these patterns:
   - `hover:-translate-y-1` for lift effect
   - `hover:shadow-xl` for elevation
   - `hover:scale-105` for growth
   - `transition-all duration-300 ease-out`
   - `group-hover:opacity-100` for nested reveals
   - `focus-visible:ring-2 focus-visible:ring-offset-2`

5. **RICH Visual Effects**: Include when appropriate:
   - Glassmorphism: `bg-white/70 backdrop-blur-xl border border-white/20`
   - Neumorphism: `shadow-[8px_8px_16px_#d1d5db,-8px_-8px_16px_#fff]`
   - Neon glow: `shadow-[0_0_10px_#3b82f6,0_0_20px_#3b82f6]`
   - Gradient borders: `bg-gradient-to-r from-blue-500 to-purple-500`

6. **INLINE SVG Icons**: Generate FULL SVG markup
   - Never use placeholder icons like [icon] or (icon)
   - Use Heroicons-style paths: `<svg class="w-5 h-5" fill="none" stroke="currentColor"...>`
   - Include viewBox, strokeWidth, paths

### Quality Checklist (Internal):
Before finalizing output, ensure you've considered:
- Every interactive element has hover/focus/active states
- Spacing follows consistent scale (4px, 8px, 16px, 24px, 32px)
- Colors have sufficient contrast ratios
- Typography hierarchy is clear
- Component works at different viewport sizes
- Placeholder content is meaningful, not "Lorem ipsum"

## ITERATION/REFINEMENT MODE

When refining existing HTML (previous_html provided):
1. Preserve the overall structure unless explicitly asked to change
2. Only modify the specific elements mentioned in modifications
3. Maintain consistency with existing style choices
4. Keep all existing accessibility features
5. Return the COMPLETE modified HTML, not just the changed parts

## SECTION MARKERS (CRITICAL FOR ITERATIONS)

When generating multi-section layouts (pages, templates, or layouts with multiple components),
you MUST wrap each major section with structured markers for iteration support:

```html
<!-- SECTION: {section_type} -->
<section class="...">
  ...section content...
</section>
<!-- /SECTION: {section_type} -->
```

### Valid Section Types
- navbar: Navigation bars, headers, app bars
- hero: Hero sections, landing areas, above-the-fold content
- stats: Statistics, metrics, key numbers sections
- features: Feature grids, benefit lists, capability showcases
- testimonials: Customer reviews, quotes, social proof
- pricing: Pricing tables, plans, subscription options
- cta: Call-to-action sections, conversion areas
- footer: Site footers, bottom navigation
- content: Generic content sections
- gallery: Image galleries, portfolios
- faq: FAQ sections, accordions
- team: Team member sections
- contact: Contact forms, contact information

### Example Multi-Section Layout:
```html
<!-- SECTION: navbar -->
<nav class="fixed top-0 ...">...</nav>
<!-- /SECTION: navbar -->

<!-- SECTION: hero -->
<section class="min-h-screen ...">...</section>
<!-- /SECTION: hero -->

<!-- SECTION: features -->
<section class="py-24 ...">...</section>
<!-- /SECTION: features -->

<!-- SECTION: footer -->
<footer class="bg-slate-900 ...">...</footer>
<!-- /SECTION: footer -->
```

### Critical Rules for Markers:
1. ALWAYS use exact format: `<!-- SECTION: {type} -->` and `<!-- /SECTION: {type} -->`
2. Section type MUST match in opening and closing markers
3. Each section marker pair must be on its own line
4. Markers must be at the root level of the section, not nested inside
5. Do NOT include markers for single-component generation (only for multi-section layouts)

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
# MICRO-INTERACTION & EFFECT HELPERS
# =============================================================================


def get_micro_interaction(name: str) -> Dict[str, Any]:
    """Get a micro-interaction preset by name.

    Args:
        name: The interaction name (e.g., 'hover_lift', 'shimmer')

    Returns:
        Dict with interaction configuration, or empty dict if not found.

    Example:
        >>> get_micro_interaction("hover_lift")
        {'classes': 'hover:-translate-y-1 hover:shadow-xl transition-all duration-300', ...}
    """
    return MICRO_INTERACTIONS.get(name, {})


def get_all_micro_interactions() -> Dict[str, Dict[str, Any]]:
    """Get all available micro-interaction presets.

    Returns:
        Dict mapping interaction names to their configurations.
    """
    return MICRO_INTERACTIONS.copy()


def get_available_interaction_names() -> List[str]:
    """Get list of available micro-interaction names.

    Returns:
        List of interaction names (e.g., ['hover_lift', 'hover_glow', ...])
    """
    return list(MICRO_INTERACTIONS.keys())


def get_visual_effect(name: str) -> Dict[str, Any]:
    """Get a visual effect preset by name.

    Args:
        name: The effect name (e.g., 'glassmorphism_light', 'neon_glow_blue')

    Returns:
        Dict with effect configuration, or empty dict if not found.

    Example:
        >>> get_visual_effect("glassmorphism_light")
        {'classes': 'bg-white/70 backdrop-blur-xl border border-white/20 shadow-xl', ...}
    """
    return VISUAL_EFFECTS.get(name, {})


def get_all_visual_effects() -> Dict[str, Dict[str, Any]]:
    """Get all available visual effect presets.

    Returns:
        Dict mapping effect names to their configurations.
    """
    return VISUAL_EFFECTS.copy()


def get_available_effect_names() -> List[str]:
    """Get list of available visual effect names.

    Returns:
        List of effect names (e.g., ['glassmorphism_light', 'neon_glow_blue', ...])
    """
    return list(VISUAL_EFFECTS.keys())


def get_svg_icon(name: str) -> str:
    """Get an inline SVG icon by name.

    Args:
        name: The icon name (e.g., 'arrow_right', 'check', 'star')

    Returns:
        Complete SVG markup string, or empty string if not found.

    Example:
        >>> get_svg_icon("check")
        '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">...</svg>'
    """
    return SVG_ICONS.get(name, "")


def get_all_svg_icons() -> Dict[str, str]:
    """Get all available SVG icons.

    Returns:
        Dict mapping icon names to their SVG markup.
    """
    return SVG_ICONS.copy()


def get_available_icon_names() -> List[str]:
    """Get list of available SVG icon names.

    Returns:
        List of icon names (e.g., ['arrow_right', 'check', 'star', ...])
    """
    return list(SVG_ICONS.keys())


def get_icons_by_category() -> Dict[str, List[str]]:
    """Get SVG icons grouped by category.

    Returns:
        Dict mapping categories to lists of icon names.
    """
    categories: Dict[str, List[str]] = {
        "arrows": [],
        "actions": [],
        "status": [],
        "user": [],
        "commerce": [],
        "media": [],
        "navigation": [],
        "misc": [],
    }

    for name in SVG_ICONS.keys():
        if name.startswith("arrow") or name.startswith("chevron"):
            categories["arrows"].append(name)
        elif name in ["check", "x", "plus", "minus", "edit", "trash", "copy", "download", "upload", "refresh", "search", "filter", "settings", "menu", "external_link"]:
            categories["actions"].append(name)
        elif name in ["check_circle", "x_circle", "exclamation", "info", "warning", "spinner", "loading"]:
            categories["status"].append(name)
        elif name in ["user", "users", "user_plus", "user_circle", "lock", "unlock", "key", "shield"]:
            categories["user"].append(name)
        elif name in ["cart", "credit_card", "currency", "tag", "receipt", "package", "truck"]:
            categories["commerce"].append(name)
        elif name in ["play", "pause", "stop", "volume", "camera", "image", "video", "music"]:
            categories["media"].append(name)
        elif name in ["home", "globe", "map", "location", "phone", "mail", "calendar", "clock", "bookmark", "link"]:
            categories["navigation"].append(name)
        else:
            categories["misc"].append(name)

    return {k: v for k, v in categories.items() if v}


def build_rich_style_guide(
    theme: str,
    dark_mode: bool = True,
    border_radius: str = "",
    include_effects: bool = True,
    include_icons: bool = True,
    include_interactions: bool = True,
    custom_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build an enhanced style guide with effect libraries.

    This extends the basic style guide with micro-interactions,
    visual effects, and SVG icon references for MAXIMUM_RICHNESS mode.

    Args:
        theme: Theme name to use as base.
        dark_mode: Whether to include dark mode variants.
        border_radius: Custom border radius override.
        include_effects: Include visual effect presets.
        include_icons: Include SVG icon references.
        include_interactions: Include micro-interaction presets.
        custom_overrides: Additional style overrides.

    Returns:
        Enhanced style guide dictionary with all available resources.

    Example:
        >>> guide = build_rich_style_guide("modern-minimal", include_effects=True)
        >>> guide["available_effects"]["glassmorphism"]
        'bg-white/70 backdrop-blur-xl border border-white/20'
    """
    # Start with basic style guide
    style_guide = build_style_guide(theme, dark_mode, border_radius, custom_overrides)

    # Add MAXIMUM_RICHNESS mode flag
    style_guide["richness_mode"] = "MAXIMUM"

    # Add interaction presets
    if include_interactions:
        style_guide["available_interactions"] = {
            name: preset.get("classes", "")
            for name, preset in MICRO_INTERACTIONS.items()
        }
        style_guide["recommended_interactions"] = [
            "hover_lift",
            "hover_glow",
            "focus_ring",
            "button_press",
            "shimmer",
        ]

    # Add visual effect presets
    if include_effects:
        style_guide["available_effects"] = {
            name: preset.get("classes", "")
            for name, preset in VISUAL_EFFECTS.items()
        }
        # Match effects to theme
        theme_effects = {
            "modern-minimal": ["hover_lift", "focus_ring"],
            "brutalist": ["hover_scale", "focus_ring"],
            "glassmorphism": ["glassmorphism_light", "glassmorphism_dark", "hover_glow"],
            "neo-brutalism": ["neon_glow_blue", "hover_scale", "text_gradient"],
            "soft-ui": ["neumorphism_raised", "neumorphism_pressed", "hover_lift"],
            "corporate": ["hover_lift", "focus_ring", "subtle_shadow"],
            "dark-luxe": ["glassmorphism_dark", "neon_glow_purple", "shimmer"],
        }
        style_guide["theme_recommended_effects"] = theme_effects.get(theme, ["hover_lift"])

    # Add icon references (not full SVGs, just names)
    if include_icons:
        style_guide["available_icons"] = get_available_icon_names()
        style_guide["icons_by_category"] = get_icons_by_category()
        style_guide["icon_usage_note"] = "Use get_svg_icon(name) to get full SVG markup"

    # Add richness directives
    style_guide["richness_directives"] = {
        "min_table_rows": 8,
        "min_list_items": 6,
        "generate_all_states": True,
        "inline_svgs": True,
        "realistic_turkish_content": True,
        "exhaustive_responsive": True,
    }

    return style_guide


# =============================================================================
# SECTION CHAIN SYSTEM (for large pages)
# =============================================================================

SECTION_CHAIN_PROMPT = """
## SECTION CHAIN MODE

You are designing a SINGLE SECTION that must visually match previous sections.

### Previous Section Analysis
Analyze the previous HTML and EXTRACT these design patterns:

1. **Color Palette**:
   - Primary color (bg-*, text-*, border-*)
   - Secondary/accent colors
   - Background colors (light and dark mode)
   - Text colors (headings, body, muted)

2. **Typography**:
   - Font family (font-sans, font-serif, font-mono)
   - Heading sizes and weights
   - Body text size and line-height
   - Letter spacing

3. **Spacing**:
   - Section padding (py-*, px-*)
   - Container max-width
   - Gap/margin patterns
   - Consistent spacing scale

4. **Style Elements**:
   - Border radius (rounded-*)
   - Shadow style (shadow-*)
   - Border width and color
   - Hover/focus effects
   - Animation durations

### Design Continuity Rules
1. USE THE SAME color classes as the previous section
2. MATCH typography hierarchy exactly
3. MAINTAIN consistent spacing patterns
4. PRESERVE animation timing and easing
5. ENSURE responsive breakpoints align

### Output Requirements
Return JSON with:
- html: The new section HTML
- design_tokens: Extracted design tokens from YOUR output (for next section)
- design_notes: Explain how you matched the previous section's style
"""

# Available section types for design_section
SECTION_TYPES: Dict[str, Dict[str, Any]] = {
    "hero": {
        "description": "Hero/banner section with headline and CTA",
        "typical_elements": ["headline", "subheadline", "cta_buttons", "background_image"],
    },
    "features": {
        "description": "Feature grid or list showcasing product features",
        "typical_elements": ["feature_cards", "icons", "titles", "descriptions"],
    },
    "pricing": {
        "description": "Pricing cards/table comparing plans",
        "typical_elements": ["pricing_cards", "tier_names", "prices", "feature_lists", "cta"],
    },
    "testimonials": {
        "description": "Customer testimonials/reviews section",
        "typical_elements": ["quote", "avatar", "name", "role", "company"],
    },
    "cta": {
        "description": "Call-to-action section",
        "typical_elements": ["headline", "description", "buttons", "background"],
    },
    "footer": {
        "description": "Page footer with links and info",
        "typical_elements": ["logo", "nav_links", "social_icons", "copyright"],
    },
    "stats": {
        "description": "Statistics/metrics section",
        "typical_elements": ["stat_value", "stat_label", "icons", "trend_indicators"],
    },
    "faq": {
        "description": "FAQ accordion section",
        "typical_elements": ["questions", "answers", "accordion_controls"],
    },
    "team": {
        "description": "Team members grid",
        "typical_elements": ["avatar", "name", "role", "social_links", "bio"],
    },
    "contact": {
        "description": "Contact form section",
        "typical_elements": ["form_fields", "submit_button", "contact_info", "map"],
    },
    "gallery": {
        "description": "Image/media gallery",
        "typical_elements": ["images", "lightbox", "captions", "navigation"],
    },
    "newsletter": {
        "description": "Newsletter signup section",
        "typical_elements": ["headline", "description", "email_input", "submit_button"],
    },
}


def extract_design_tokens(html: str) -> Dict[str, Any]:
    """Extract design tokens from HTML for chain continuity.

    Analyzes TailwindCSS classes in HTML to extract design patterns.

    Args:
        html: HTML string with TailwindCSS classes.

    Returns:
        Dict with extracted design tokens.
    """
    import re

    tokens: Dict[str, Any] = {
        "colors": {},
        "typography": {},
        "spacing": {},
        "style": {},
    }

    # Extract color classes
    color_patterns = {
        "primary": r'bg-(blue|indigo|violet|purple|emerald|cyan|teal|green|red|orange|amber|yellow|pink|rose|fuchsia)-(\d{3})',
        "text": r'text-(slate|gray|zinc|neutral|stone)-(\d{3})',
        "border": r'border-(slate|gray|zinc|neutral|stone)-(\d{3})',
    }

    for key, pattern in color_patterns.items():
        matches = re.findall(pattern, html)
        if matches:
            # Get the most common color
            color_counts: Dict[str, int] = {}
            for color, shade in matches:
                full_color = f"{color}-{shade}"
                color_counts[full_color] = color_counts.get(full_color, 0) + 1
            if color_counts:
                tokens["colors"][key] = max(color_counts, key=color_counts.get)

    # Extract typography
    font_match = re.search(r'font-(sans|serif|mono)', html)
    if font_match:
        tokens["typography"]["font_family"] = f"font-{font_match.group(1)}"

    weight_match = re.search(r'font-(bold|semibold|medium|normal|light)', html)
    if weight_match:
        tokens["typography"]["heading_weight"] = f"font-{weight_match.group(1)}"

    # Extract spacing
    padding_match = re.search(r'py-(\d+)\s+(?:md:py-(\d+))?', html)
    if padding_match:
        tokens["spacing"]["section_padding"] = f"py-{padding_match.group(1)}"
        if padding_match.group(2):
            tokens["spacing"]["section_padding"] += f" md:py-{padding_match.group(2)}"

    max_width_match = re.search(r'max-w-(sm|md|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|full|screen-\w+)', html)
    if max_width_match:
        tokens["spacing"]["container_max"] = f"max-w-{max_width_match.group(1)}"

    # Extract style elements
    radius_match = re.search(r'rounded-(none|sm|md|lg|xl|2xl|3xl|full)', html)
    if radius_match:
        tokens["style"]["border_radius"] = f"rounded-{radius_match.group(1)}"

    shadow_match = re.search(r'shadow-(sm|md|lg|xl|2xl|inner|none)', html)
    if shadow_match:
        tokens["style"]["shadow"] = f"shadow-{shadow_match.group(1)}"

    # Extract custom hex colors if present
    hex_colors = re.findall(r'\[#([0-9a-fA-F]{6})\]', html)
    if hex_colors:
        tokens["colors"]["custom_hex"] = [f"#{c}" for c in set(hex_colors)]

    return tokens


def get_section_types() -> List[str]:
    """Get list of available section types.

    Returns:
        List of section type names.
    """
    return list(SECTION_TYPES.keys())


def get_section_info(section_type: str) -> Dict[str, Any]:
    """Get information about a section type.

    Args:
        section_type: The section type name.

    Returns:
        Dict with section info, or empty dict if not found.
    """
    return SECTION_TYPES.get(section_type, {})


def build_section_prompt(
    section_type: str,
    context: str = "",
    previous_html: str = "",
    design_tokens: Dict[str, Any] = None,
    project_context: str = "",
) -> str:
    """Build a prompt for designing a section in chain mode.

    Args:
        section_type: Type of section to design (hero, features, etc.)
        context: Usage context for the section.
        previous_html: HTML from the previous section (for style matching).
        design_tokens: Extracted design tokens from previous section.
        project_context: Project-specific context.

    Returns:
        Complete prompt for section design.
    """
    import json

    base_prompt = build_system_prompt(project_context)

    section_info = get_section_info(section_type)
    section_desc = section_info.get("description", f"{section_type} section")
    typical_elements = section_info.get("typical_elements", [])

    # Build section-specific prompt
    section_prompt = f"""
## SECTION DESIGN TASK

Design a **{section_type}** section: {section_desc}

### Context
{context if context else "No specific context provided."}

### Typical Elements
{", ".join(typical_elements) if typical_elements else "Standard section elements"}

"""

    # Add chain mode if previous HTML exists
    if previous_html:
        section_prompt += SECTION_CHAIN_PROMPT
        section_prompt += f"""
### Previous Section HTML
```html
{previous_html[:4000]}{"..." if len(previous_html) > 4000 else ""}
```

"""

    # Add design tokens if provided
    if design_tokens:
        section_prompt += f"""
### Design Tokens to Match
```json
{json.dumps(design_tokens, indent=2)}
```

You MUST use these exact design tokens to ensure visual consistency.

"""

    section_prompt += """
### Output Format
Return JSON with:
- section_id: Unique identifier
- html: Complete section HTML
- design_tokens: Extracted design tokens (for next section)
- design_notes: How you achieved visual consistency
"""

    return base_prompt + section_prompt
