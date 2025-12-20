14 Tema İçin Detaylı İyileştirme Rehberi
Her tema için mevcut eksiklikleri gidermek üzere kapsamlı bir analiz ve implementasyon planı hazırladım.
@
1. Modern-Minimal — Brand Color Customization
Mevcut Problem
python# Statik, değiştirilemeyen renkler
"primary": "blue-600",  # Hardcoded!
Çözüm Mimarisi
python# frontend_presets.py - YENİ: Dynamic Theme Factory

from typing import Optional, Literal
from dataclasses import dataclass

@dataclass
class BrandColors:
    """Marka renkleri için type-safe yapı"""
    primary: str           # Ana marka rengi (hex veya Tailwind)
    primary_hover: str     # Hover state
    primary_light: str     # Light variant (backgrounds)
    primary_dark: str      # Dark variant (text on light)
    secondary: str
    accent: str
    
    @classmethod
    def from_hex(cls, primary_hex: str) -> "BrandColors":
        """Tek hex renkten tüm palette'i oluştur"""
        # HSL dönüşümü ile auto-generate
        h, s, l = hex_to_hsl(primary_hex)
        return cls(
            primary=primary_hex,
            primary_hover=hsl_to_hex(h, s, max(l - 10, 0)),
            primary_light=hsl_to_hex(h, s * 0.3, 95),
            primary_dark=hsl_to_hex(h, s, max(l - 30, 15)),
            secondary=hsl_to_hex((h + 30) % 360, s * 0.7, l),
            accent=hsl_to_hex((h + 180) % 360, s, l),
        )


def create_modern_minimal_theme(
    brand: Optional[BrandColors] = None,
    neutral_base: Literal["slate", "gray", "zinc", "neutral", "stone"] = "slate",
    border_radius: Literal["none", "sm", "md", "lg", "xl", "2xl", "full"] = "lg",
    shadow_intensity: Literal["none", "sm", "md", "lg"] = "sm",
) -> Dict[str, Any]:
    """
    Customizable Modern Minimal tema oluşturucu.
    
    Args:
        brand: Marka renkleri. None ise default blue kullanılır.
        neutral_base: Gri tonları için baz renk.
        border_radius: Global border radius.
        shadow_intensity: Gölge yoğunluğu.
    
    Example:
        # Özel marka renkleriyle
        theme = create_modern_minimal_theme(
            brand=BrandColors.from_hex("#E11D48"),  # Rose
            neutral_base="zinc",
            border_radius="xl"
        )
        
        # Veya Tailwind renk adıyla
        theme = create_modern_minimal_theme(
            brand=BrandColors(
                primary="emerald-600",
                primary_hover="emerald-700",
                primary_light="emerald-50",
                primary_dark="emerald-900",
                secondary="teal-600",
                accent="amber-500"
            )
        )
    """
    # Default marka renkleri
    if brand is None:
        brand = BrandColors(
            primary="blue-600",
            primary_hover="blue-700",
            primary_light="blue-50",
            primary_dark="blue-900",
            secondary="slate-600",
            accent="emerald-500"
        )
    
    return {
        "name": "modern-minimal-custom",
        "description": "Customized modern minimal theme",
        
        # Brand Colors (dinamik)
        "primary": brand.primary,
        "primary_hover": brand.primary_hover,
        "primary_light": brand.primary_light,
        "primary_dark": brand.primary_dark,
        "secondary": brand.secondary,
        "accent": brand.accent,
        
        # Neutral Scale (configurable base)
        "background": "white",
        "background_dark": f"{neutral_base}-900",
        "surface": f"{neutral_base}-50",
        "surface_dark": f"{neutral_base}-800",
        "border": f"{neutral_base}-200",
        "border_dark": f"{neutral_base}-700",
        "text": f"{neutral_base}-900",
        "text_dark": f"{neutral_base}-100",
        "text_muted": f"{neutral_base}-500",
        
        # Configurable Style
        "border_radius": f"rounded-{border_radius}",
        "shadow": f"shadow-{shadow_intensity}" if shadow_intensity != "none" else "",
        "shadow_hover": f"shadow-{_next_shadow(shadow_intensity)}",
        
        # Fixed properties
        "font": "font-sans",
        "transition": "transition-all duration-200 ease-out",
        
        # CSS Custom Properties for runtime changes
        "css_variables": {
            "--color-primary": _to_css_color(brand.primary),
            "--color-primary-hover": _to_css_color(brand.primary_hover),
            "--color-accent": _to_css_color(brand.accent),
        },
        
        # Utility classes bundle
        "button_base": f"bg-{brand.primary} hover:bg-{brand.primary_hover} text-white rounded-{border_radius} shadow-{shadow_intensity} hover:shadow-{_next_shadow(shadow_intensity)} transition-all duration-200",
        "card_base": f"bg-white dark:bg-{neutral_base}-800 rounded-{border_radius} shadow-{shadow_intensity} border border-{neutral_base}-200 dark:border-{neutral_base}-700",
        "input_base": f"bg-white dark:bg-{neutral_base}-900 border border-{neutral_base}-300 dark:border-{neutral_base}-600 rounded-{border_radius} focus:ring-2 focus:ring-{brand.primary}/50 focus:border-{brand.primary}",
    }


def _next_shadow(current: str) -> str:
    """Shadow intensity'yi bir üst seviyeye çıkar"""
    scale = ["none", "sm", "md", "lg", "xl", "2xl"]
    idx = scale.index(current) if current in scale else 1
    return scale[min(idx + 1, len(scale) - 1)]


def _to_css_color(tailwind_color: str) -> str:
    """Tailwind color → CSS variable value"""
    # Bu mapping runtime'da Tailwind config'den alınabilir
    color_map = {
        "blue-600": "59 130 246",
        "emerald-600": "5 150 105",
        "rose-600": "225 29 72",
        # ... diğer renkler
    }
    return color_map.get(tailwind_color, "59 130 246")
Kullanım Örneği
python# server.py - design_frontend tool'unda

@mcp.tool()
async def design_frontend(
    component_type: str,
    theme: str = "modern-minimal",
    # YENİ: Brand customization
    brand_primary: str = "",      # "#E11D48" veya "rose-600"
    brand_secondary: str = "",
    brand_accent: str = "",
    ...
) -> dict:
    # Custom brand varsa, theme'i override et
    if brand_primary:
        if brand_primary.startswith("#"):
            brand = BrandColors.from_hex(brand_primary)
        else:
            brand = BrandColors(
                primary=brand_primary,
                primary_hover=_derive_hover(brand_primary),
                ...
            )
        style_guide = create_modern_minimal_theme(brand=brand)
    else:
        style_guide = build_style_guide(theme=theme, ...)

2. Brutalist — Accessibility Kontrast
Mevcut Problem
python"text": "black",
"background": "white",
# Sorun: İç elementlerde kontrast kaybolabiliyor
Çözüm: Kontrast Garantili Sistem
python# frontend_presets.py - Brutalist Theme Enhancement

BRUTALIST_CONTRAST_PAIRS = {
    # Her background için guaranteed readable text color
    "white": {"text": "black", "text_muted": "slate-700", "min_contrast": 7.0},
    "black": {"text": "white", "text_muted": "slate-300", "min_contrast": 7.0},
    "yellow-400": {"text": "black", "text_muted": "slate-800", "min_contrast": 4.5},
    "blue-600": {"text": "white", "text_muted": "blue-100", "min_contrast": 4.5},
    "red-600": {"text": "white", "text_muted": "red-100", "min_contrast": 4.5},
}

def create_brutalist_theme(
    contrast_mode: Literal["standard", "high", "maximum"] = "high",
    accent_color: str = "yellow-400",
    include_focus_indicators: bool = True,
) -> Dict[str, Any]:
    """
    WCAG AA (standard) veya AAA (high/maximum) uyumlu Brutalist tema.
    
    Brutalist'in cesur estetiğini korurken erişilebilirliği garanti eder.
    """
    
    # Contrast mode'a göre minimum oranlar
    contrast_requirements = {
        "standard": {"normal_text": 4.5, "large_text": 3.0, "ui": 3.0},
        "high": {"normal_text": 7.0, "large_text": 4.5, "ui": 4.5},
        "maximum": {"normal_text": 10.0, "large_text": 7.0, "ui": 7.0},
    }
    
    reqs = contrast_requirements[contrast_mode]
    
    theme = {
        "name": f"brutalist-{contrast_mode}",
        "description": f"Brutalist theme with {contrast_mode} contrast (WCAG {'AA' if contrast_mode == 'standard' else 'AAA'})",
        
        # Core brutalist aesthetic
        "primary": "black",
        "primary_hover": "slate-800",
        "secondary": "white",
        "accent": accent_color,
        
        # High contrast pairs
        "background": "white",
        "background_dark": "black",
        "surface": "slate-100",
        "surface_dark": "slate-900",
        
        # Guaranteed contrast text
        "text": "black",
        "text_dark": "white",
        "text_muted": "slate-700",  # 4.5:1 on white
        "text_muted_dark": "slate-300",  # 7:1 on black
        
        # Brutalist style markers
        "border": "black",
        "border_dark": "white",
        "border_radius": "rounded-none",
        "border_width": "border-2",
        
        # Signature brutalist shadows
        "shadow": "shadow-[4px_4px_0px_#000]",
        "shadow_hover": "shadow-[6px_6px_0px_#000]",
        "shadow_dark": "shadow-[4px_4px_0px_#fff]",
        
        "font": "font-mono",
        
        # Focus indicators (critical for accessibility)
        "focus_ring": "ring-4 ring-black ring-offset-2" if include_focus_indicators else "",
        "focus_ring_dark": "ring-4 ring-white ring-offset-2 ring-offset-black",
        
        # Contrast validation metadata
        "_contrast_mode": contrast_mode,
        "_min_contrast_ratios": reqs,
    }
    
    # Accent color için text pairing
    accent_pair = BRUTALIST_CONTRAST_PAIRS.get(accent_color, {"text": "black"})
    theme["accent_text"] = accent_pair["text"]
    
    return theme


# System Prompt'a eklenecek Brutalist-specific kurallar
BRUTALIST_DESIGN_RULES = """
## BRUTALIST ACCESSIBILITY RULES

When generating Brutalist designs, ALWAYS ensure:

1. **Text Contrast**: 
   - On white/light backgrounds: Use `text-black` or `text-slate-900`
   - On black/dark backgrounds: Use `text-white` or `text-slate-100`
   - NEVER use grays lighter than `slate-700` on white
   - NEVER use grays darker than `slate-300` on black

2. **Focus Indicators**:
   - All interactive elements MUST have visible focus rings
   - Use `focus:ring-4 focus:ring-black focus:ring-offset-2`
   - Brutalist focus can be MORE visible, not less

3. **Border Contrast**:
   - Always use `border-black` on light backgrounds
   - Always use `border-white` on dark backgrounds
   - Minimum `border-2` width for visibility

4. **Accent Colors**:
   - If using colored backgrounds (e.g., yellow-400), check text readability
   - Yellow/Lime backgrounds → Black text only
   - Blue/Purple backgrounds → White text only

5. **Link Differentiation**:
   - Underline ALL links: `underline underline-offset-4`
   - Hover: `hover:underline-offset-2` for subtle movement
"""
Contrast Checker Utility
python# utils/contrast.py - YENİ DOSYA

from typing import Tuple
import colorsys

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance per WCAG 2.1"""
    def adjust(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

def contrast_ratio(color1: str, color2: str) -> float:
    """Calculate contrast ratio between two colors"""
    l1 = relative_luminance(*hex_to_rgb(color1))
    l2 = relative_luminance(*hex_to_rgb(color2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def validate_contrast(
    foreground: str, 
    background: str, 
    level: str = "AA",
    text_size: str = "normal"
) -> Tuple[bool, float, str]:
    """
    Validate WCAG contrast requirements.
    
    Returns:
        (passes, ratio, message)
    """
    ratio = contrast_ratio(foreground, background)
    
    requirements = {
        ("AA", "normal"): 4.5,
        ("AA", "large"): 3.0,
        ("AAA", "normal"): 7.0,
        ("AAA", "large"): 4.5,
    }
    
    required = requirements.get((level, text_size), 4.5)
    passes = ratio >= required
    
    message = f"Contrast ratio: {ratio:.2f}:1 ({'✓ PASS' if passes else '✗ FAIL'} {level} {text_size})"
    
    return passes, ratio, message


# Tailwind color → hex mapping (subset)
TAILWIND_COLORS = {
    "black": "#000000",
    "white": "#FFFFFF",
    "slate-100": "#F1F5F9",
    "slate-300": "#CBD5E1",
    "slate-700": "#334155",
    "slate-900": "#0F172A",
    "yellow-400": "#FACC15",
    # ... extend as needed
}

def validate_theme_contrast(theme: Dict[str, Any]) -> List[Dict]:
    """Validate all color combinations in a theme"""
    issues = []
    
    # Check text on background
    text_color = TAILWIND_COLORS.get(theme.get("text", "black"), "#000000")
    bg_color = TAILWIND_COLORS.get(theme.get("background", "white"), "#FFFFFF")
    
    passes, ratio, msg = validate_contrast(text_color, bg_color, "AA", "normal")
    if not passes:
        issues.append({
            "pair": ("text", "background"),
            "ratio": ratio,
            "required": 4.5,
            "fix": f"Change text to a darker color or background to lighter"
        })
    
    # Check muted text
    muted_color = TAILWIND_COLORS.get(theme.get("text_muted", "slate-500"), "#64748B")
    passes, ratio, msg = validate_contrast(muted_color, bg_color, "AA", "normal")
    if not passes:
        issues.append({
            "pair": ("text_muted", "background"),
            "ratio": ratio,
            "required": 4.5,
            "fix": f"Use darker muted text: slate-600 or slate-700"
        })
    
    return issues

3. Glassmorphism — Safari Uyumluluğu
Mevcut Problem
python"backdrop_blur": "backdrop-blur-lg",
# Safari 14 öncesi: backdrop-filter desteklenmiyor
# Safari 14-15: Bazı kombinasyonlarda performans sorunları
Çözüm: Progressive Enhancement
python# frontend_presets.py - Glassmorphism Enhancement

def create_glassmorphism_theme(
    blur_intensity: Literal["sm", "md", "lg", "xl", "2xl", "3xl"] = "xl",
    opacity: float = 0.7,  # 0.0 - 1.0
    tint_color: str = "white",  # white, black, or Tailwind color
    enable_fallback: bool = True,
    performance_mode: Literal["quality", "balanced", "performance"] = "balanced",
) -> Dict[str, Any]:
    """
    Safari-compatible Glassmorphism with progressive enhancement.
    
    The theme generates CSS that:
    1. Uses backdrop-filter when supported
    2. Falls back to semi-transparent backgrounds when not
    3. Optimizes for Safari's specific quirks
    """
    
    # Safari performance optimizations
    performance_settings = {
        "quality": {
            "blur": blur_intensity,
            "will_change": "backdrop-filter",
            "transform": "translateZ(0)",  # GPU acceleration
        },
        "balanced": {
            "blur": min_blur(blur_intensity, "lg"),  # Cap at lg for Safari
            "will_change": "auto",
            "transform": "",
        },
        "performance": {
            "blur": "md",  # Minimal blur
            "will_change": "auto",
            "transform": "",
        }
    }
    
    perf = performance_settings[performance_mode]
    
    # Calculate fallback opacity (slightly higher when blur unavailable)
    fallback_opacity = min(opacity + 0.15, 0.95)
    
    # Tint color handling
    if tint_color == "white":
        glass_bg = f"bg-white/{int(opacity * 100)}"
        glass_bg_fallback = f"bg-white/{int(fallback_opacity * 100)}"
        border_color = "border-white/20"
    elif tint_color == "black":
        glass_bg = f"bg-black/{int(opacity * 100)}"
        glass_bg_fallback = f"bg-slate-900/{int(fallback_opacity * 100)}"
        border_color = "border-white/10"
    else:
        glass_bg = f"bg-{tint_color}/{int(opacity * 100)}"
        glass_bg_fallback = f"bg-{tint_color}/{int(fallback_opacity * 100)}"
        border_color = f"border-{tint_color}/20"
    
    theme = {
        "name": f"glassmorphism-{performance_mode}",
        "description": f"Safari-optimized glassmorphism ({performance_mode} mode)",
        
        # Primary glass effect
        "glass_effect": f"{glass_bg} backdrop-blur-{perf['blur']} {border_color} border",
        "glass_effect_strong": f"bg-white/{int(opacity * 100 + 10)} backdrop-blur-{blur_intensity} border-white/30 border",
        
        # Fallback for unsupported browsers
        "glass_fallback": f"{glass_bg_fallback} border {border_color}",
        
        # Surface colors
        "surface": f"white/{int(opacity * 100 - 10)}",
        "surface_dark": f"slate-900/{int(opacity * 100 - 10)}",
        
        # Core colors
        "primary": "indigo-500",
        "primary_hover": "indigo-600",
        "secondary": "purple-500",
        "background": "slate-900",
        "background_dark": "slate-950",
        "text": "white",
        "text_muted": "slate-300",
        
        # Borders and shadows
        "border": "white/20",
        "border_radius": "rounded-2xl",
        "shadow": "shadow-lg shadow-black/10",
        "shadow_hover": "shadow-xl shadow-black/20",
        
        # Safari-specific optimizations
        "_safari_optimizations": {
            "use_transform_hack": performance_mode == "quality",
            "limit_nested_blur": True,  # Avoid blur inside blur
            "prefer_opacity_over_rgba": True,
        },
        
        # CSS for fallback detection
        "_feature_detection_css": """
        /* Glassmorphism with fallback */
        @supports (backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)) {
            .glass {
                -webkit-backdrop-filter: blur(16px);
                backdrop-filter: blur(16px);
            }
        }
        @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
            .glass {
                background-color: rgba(255, 255, 255, 0.85);
            }
        }
        """,
    }
    
    if enable_fallback:
        theme["_fallback_styles"] = generate_glass_fallback_css(opacity, tint_color)
    
    return theme


def min_blur(requested: str, maximum: str) -> str:
    """Cap blur intensity at maximum"""
    scale = ["sm", "md", "lg", "xl", "2xl", "3xl"]
    req_idx = scale.index(requested) if requested in scale else 3
    max_idx = scale.index(maximum) if maximum in scale else 2
    return scale[min(req_idx, max_idx)]


# System Prompt'a eklenecek Glassmorphism kuralları
GLASSMORPHISM_DESIGN_RULES = """
## GLASSMORPHISM BROWSER COMPATIBILITY RULES

1. **Always Include Vendor Prefix**:
```html
   class="backdrop-blur-lg [-webkit-backdrop-filter:blur(16px)]"
```

2. **Provide Visual Fallback**:
   - Wrap glass elements: `@supports (backdrop-filter: blur(1px))`
   - Fallback: Higher opacity background without blur
```html
   <!-- Good: Has fallback -->
   <div class="bg-white/70 backdrop-blur-xl 
               supports-[backdrop-filter]:bg-white/50">
```

3. **Avoid Nested Blur**:
   - Never put backdrop-blur inside another backdrop-blur
   - Safari crashes or freezes with nested blur

4. **Performance on Mobile Safari**:
   - Limit blur to `backdrop-blur-lg` (16px) maximum
   - Avoid blur on scroll-containers
   - Use `will-change: backdrop-filter` sparingly

5. **Dark Glass Pattern**:
```html
   <div class="bg-slate-900/70 backdrop-blur-xl border border-white/10">
```

6. **Readable Text on Glass**:
   - Always use `text-shadow` or solid background for critical text
   - Glass behind text: minimum 60% opacity
"""
Fallback Generator
pythondef generate_glass_fallback_css(opacity: float, tint: str) -> str:
    """Generate CSS with @supports fallback"""
    return f"""
/* Glass effect with progressive enhancement */
.glass-container {{
    position: relative;
    overflow: hidden;
}}

/* Modern browsers with backdrop-filter */
@supports ((-webkit-backdrop-filter: blur(1px)) or (backdrop-filter: blur(1px))) {{
    .glass {{
        background: rgba(255, 255, 255, {opacity});
        -webkit-backdrop-filter: blur(16px);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
}}

/* Fallback for older browsers */
@supports not ((-webkit-backdrop-filter: blur(1px)) or (backdrop-filter: blur(1px))) {{
    .glass {{
        background: rgba(255, 255, 255, {min(opacity + 0.2, 0.95)});
        border: 1px solid rgba(255, 255, 255, 0.3);
    }}
    
    /* Optional: Pseudo-element blur simulation */
    .glass::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: inherit;
        filter: blur(20px);
        z-index: -1;
        margin: -20px;
    }}
}}

/* Safari-specific fixes */
@media not all and (min-resolution: 0.001dpcm) {{
    @supports (-webkit-appearance: none) {{
        .glass {{
            /* Force GPU acceleration */
            transform: translateZ(0);
            /* Prevent color banding */
            -webkit-backface-visibility: hidden;
        }}
    }}
}}
"""

4. Neo-Brutalism — Gradient Animation
Mevcut Problem
python"gradient_primary": "bg-gradient-to-r from-yellow-400 to-pink-400",
# Statik gradient, animasyon yok
Çözüm: Animated Gradient System
python# frontend_presets.py - Neo-Brutalism Enhancement

NEOBRUTALISM_GRADIENTS = {
    # Signature color combinations
    "sunset": {
        "colors": ["yellow-400", "orange-500", "pink-500"],
        "angle": "to-r",
    },
    "ocean": {
        "colors": ["cyan-400", "blue-500", "purple-500"],
        "angle": "to-r",
    },
    "forest": {
        "colors": ["lime-400", "emerald-500", "teal-500"],
        "angle": "to-r",
    },
    "candy": {
        "colors": ["pink-400", "purple-500", "indigo-500"],
        "angle": "to-r",
    },
    "fire": {
        "colors": ["yellow-400", "orange-500", "red-500"],
        "angle": "to-r",
    },
}

GRADIENT_ANIMATIONS = {
    "flow": {
        "keyframes": """
        @keyframes gradient-flow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        """,
        "class": "bg-[length:200%_200%] animate-[gradient-flow_3s_ease_infinite]",
        "description": "Smooth left-right flow",
    },
    "pulse": {
        "keyframes": """
        @keyframes gradient-pulse {
            0%, 100% { background-size: 100% 100%; opacity: 1; }
            50% { background-size: 120% 120%; opacity: 0.9; }
        }
        """,
        "class": "animate-[gradient-pulse_2s_ease-in-out_infinite]",
        "description": "Pulsing size change",
    },
    "rotate": {
        "keyframes": """
        @keyframes gradient-rotate {
            0% { --gradient-angle: 0deg; }
            100% { --gradient-angle: 360deg; }
        }
        """,
        "class": "animate-[gradient-rotate_4s_linear_infinite]",
        "description": "Full 360° rotation",
        "requires_css_variables": True,
    },
    "shimmer": {
        "keyframes": """
        @keyframes gradient-shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        """,
        "class": "bg-[length:200%_100%] animate-[gradient-shimmer_2s_linear_infinite]",
        "description": "Shine/shimmer effect",
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
        "description": "Circular wave movement",
    },
}


def create_neo_brutalism_theme(
    gradient_preset: Literal["sunset", "ocean", "forest", "candy", "fire"] = "sunset",
    animation: Literal["none", "flow", "pulse", "shimmer", "wave"] = "flow",
    animation_speed: Literal["slow", "normal", "fast"] = "normal",
    shadow_color: str = "black",
    include_hover_animations: bool = True,
) -> Dict[str, Any]:
    """
    Neo-Brutalism with animated gradients and playful effects.
    """
    
    gradient = NEOBRUTALISM_GRADIENTS[gradient_preset]
    colors = gradient["colors"]
    
    # Build gradient class
    gradient_class = f"bg-gradient-{gradient['angle']} from-{colors[0]} via-{colors[1]} to-{colors[2]}"
    
    # Animation speed multiplier
    speed_map = {"slow": 1.5, "normal": 1.0, "fast": 0.5}
    speed = speed_map[animation_speed]
    
    # Get animation config
    anim_config = GRADIENT_ANIMATIONS.get(animation, {"class": "", "keyframes": ""})
    
    # Modify animation duration based on speed
    anim_class = anim_config["class"]
    if speed != 1.0 and "animate-[" in anim_class:
        # Extract and modify duration
        import re
        anim_class = re.sub(
            r'(\d+(?:\.\d+)?)s',
            lambda m: f"{float(m.group(1)) * speed}s",
            anim_class
        )
    
    theme = {
        "name": f"neo-brutalism-{gradient_preset}",
        "description": f"Playful neo-brutalism with {gradient_preset} gradient",
        
        # Animated gradient
        "gradient_primary": gradient_class,
        "gradient_animated": f"{gradient_class} {anim_class}",
        "gradient_keyframes": anim_config.get("keyframes", ""),
        
        # Colors
        "primary": colors[0],
        "primary_hover": colors[1],
        "secondary": colors[2],
        "accent": colors[1],
        
        # Backgrounds
        "background": "amber-50",
        "background_dark": "slate-900",
        "surface": "white",
        "surface_dark": "slate-800",
        
        # Brutalist elements
        "border": shadow_color,
        "border_width": "border-2",
        "border_radius": "rounded-xl",
        
        # Signature offset shadows
        "shadow": f"shadow-[4px_4px_0px_#{_color_to_hex(shadow_color)}]",
        "shadow_hover": f"shadow-[6px_6px_0px_#{_color_to_hex(shadow_color)}]",
        "shadow_active": f"shadow-[2px_2px_0px_#{_color_to_hex(shadow_color)}]",
        
        # Text
        "text": "black",
        "text_dark": "white",
        "font": "font-sans",
        
        # Hover animations
        "hover_transform": "hover:-translate-y-1 hover:translate-x-1" if include_hover_animations else "",
        "active_transform": "active:translate-y-0 active:translate-x-0",
        
        # Button with animated gradient
        "button_gradient": f"""
            {gradient_class} {anim_class}
            text-{_contrast_text(colors[0])} font-bold
            px-6 py-3 rounded-xl
            border-2 border-black
            shadow-[4px_4px_0px_#000]
            hover:shadow-[6px_6px_0px_#000]
            hover:-translate-y-0.5 hover:translate-x-0.5
            active:shadow-[2px_2px_0px_#000]
            active:translate-y-0 active:translate-x-0
            transition-all duration-200
        """,
        
        # Card with gradient border
        "card_gradient_border": f"""
            relative bg-white rounded-xl border-2 border-black
            shadow-[4px_4px_0px_#000]
            before:absolute before:inset-0 before:-z-10
            before:{gradient_class} before:rounded-xl before:p-1
            hover:shadow-[6px_6px_0px_#000]
            hover:-translate-y-1
            transition-all duration-200
        """,
    }
    
    return theme


def _color_to_hex(color: str) -> str:
    """Convert color name to hex without #"""
    if color == "black":
        return "000"
    elif color == "white":
        return "fff"
    else:
        # Tailwind color - would need full mapping
        return "000"

def _contrast_text(bg_color: str) -> str:
    """Determine text color for contrast"""
    light_colors = ["yellow", "lime", "amber", "cyan"]
    if any(c in bg_color for c in light_colors):
        return "black"
    return "white"
Gradient Animation Keyframes
python# Tüm animasyonlar için tek CSS bundle
NEO_BRUTALISM_ANIMATIONS_CSS = """
/* Neo-Brutalism Gradient Animations */

/* Flow: Left-right movement */
@keyframes gradient-flow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Pulse: Size breathing */
@keyframes gradient-pulse {
    0%, 100% { 
        background-size: 100% 100%; 
        filter: brightness(1);
    }
    50% { 
        background-size: 110% 110%; 
        filter: brightness(1.05);
    }
}

/* Shimmer: Shine sweep */
@keyframes gradient-shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* Wave: Circular movement */
@keyframes gradient-wave {
    0%, 100% { background-position: 0% 0%; }
    25% { background-position: 100% 0%; }
    50% { background-position: 100% 100%; }
    75% { background-position: 0% 100%; }
}

/* Rotate: For conic gradients */
@property --gradient-angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
}
@keyframes gradient-rotate {
    to { --gradient-angle: 360deg; }
}

/* Utility classes */
.animate-gradient-flow {
    background-size: 200% 200%;
    animation: gradient-flow 3s ease infinite;
}
.animate-gradient-pulse {
    animation: gradient-pulse 2s ease-in-out infinite;
}
.animate-gradient-shimmer {
    background-size: 200% 100%;
    animation: gradient-shimmer 2s linear infinite;
}
.animate-gradient-wave {
    background-size: 200% 200%;
    animation: gradient-wave 4s ease infinite;
}
"""

5. Soft-UI — Dark Mode Neumorphism
Mevcut Problem
python"shadow": "shadow-[8px_8px_16px_#d1d5db,-8px_-8px_16px_#ffffff]",
# Dark mode: Bu renkler görünmez!
Çözüm: Dual-Mode Neumorphism
python# frontend_presets.py - Soft-UI Enhancement

def calculate_neumorphism_shadows(
    base_color: str,
    intensity: Literal["subtle", "medium", "strong"] = "medium",
    is_dark_mode: bool = False,
) -> Dict[str, str]:
    """
    Calculate proper neumorphism shadows for any base color.
    
    Neumorphism requires:
    - Light shadow (top-left highlight)
    - Dark shadow (bottom-right shadow)
    - Both relative to the base background color
    """
    
    intensity_map = {
        "subtle": {"light_offset": 8, "dark_offset": 12, "blur": 15},
        "medium": {"light_offset": 15, "dark_offset": 20, "blur": 20},
        "strong": {"light_offset": 20, "dark_offset": 25, "blur": 25},
    }
    
    settings = intensity_map[intensity]
    
    # Color calculations for different base colors
    neumorphism_colors = {
        # Light mode backgrounds
        "slate-100": {
            "light": "#ffffff",
            "dark": "#c8d0db",
            "bg": "#f1f5f9",
        },
        "slate-200": {
            "light": "#ffffff",
            "dark": "#b8c2cf",
            "bg": "#e2e8f0",
        },
        "gray-100": {
            "light": "#ffffff",
            "dark": "#c7ccd1",
            "bg": "#f3f4f6",
        },
        
        # Dark mode backgrounds
        "slate-800": {
            "light": "#3d4a5c",  # Lighter than bg
            "dark": "#0f1623",   # Darker than bg
            "bg": "#1e293b",
        },
        "slate-900": {
            "light": "#283548",
            "dark": "#000000",
            "bg": "#0f172a",
        },
        "zinc-800": {
            "light": "#3f3f46",
            "dark": "#0a0a0b",
            "bg": "#27272a",
        },
        "zinc-900": {
            "light": "#2d2d31",
            "dark": "#000000",
            "bg": "#18181b",
        },
    }
    
    colors = neumorphism_colors.get(base_color, neumorphism_colors["slate-100"])
    
    # Generate shadow strings
    offset = settings["light_offset"]
    blur = settings["blur"]
    dark_offset = settings["dark_offset"]
    
    return {
        "raised": f"shadow-[{offset}px_{offset}px_{blur}px_{colors['dark']},-{offset}px_-{offset}px_{blur}px_{colors['light']}]",
        "pressed": f"shadow-[inset_{offset}px_{offset}px_{blur}px_{colors['dark']},inset_-{offset}px_-{offset}px_{blur}px_{colors['light']}]",
        "flat": "shadow-none",
        "bg_color": colors["bg"],
    }


def create_soft_ui_theme(
    base_color_light: str = "slate-100",
    base_color_dark: str = "slate-800",
    primary_color: str = "blue-500",
    intensity: Literal["subtle", "medium", "strong"] = "medium",
    include_inset_variants: bool = True,
) -> Dict[str, Any]:
    """
    Proper dual-mode neumorphism with calculated shadows.
    """
    
    light_shadows = calculate_neumorphism_shadows(base_color_light, intensity, False)
    dark_shadows = calculate_neumorphism_shadows(base_color_dark, intensity, True)
    
    theme = {
        "name": f"soft-ui-{intensity}",
        "description": f"Neumorphic design with {intensity} shadows in both light and dark modes",
        
        # Primary colors
        "primary": primary_color,
        "primary_hover": primary_color.replace("-500", "-600"),
        
        # Backgrounds (must match shadow calculations)
        "background": base_color_light,
        "background_dark": base_color_dark,
        "surface": base_color_light,
        "surface_dark": base_color_dark,
        
        # Neumorphic shadows - Light mode
        "shadow_raised": light_shadows["raised"],
        "shadow_pressed": light_shadows["pressed"],
        
        # Neumorphic shadows - Dark mode
        "shadow_raised_dark": dark_shadows["raised"],
        "shadow_pressed_dark": dark_shadows["pressed"],
        
        # Combined class for auto dark mode
        "shadow_raised_auto": f"{light_shadows['raised']} dark:{dark_shadows['raised']}",
        "shadow_pressed_auto": f"{light_shadows['pressed']} dark:{dark_shadows['pressed']}",
        
        # Text colors
        "text": "slate-700",
        "text_dark": "slate-200",
        "text_muted": "slate-400",
        
        # Borders (subtle in neumorphism)
        "border": "transparent",
        "border_radius": "rounded-2xl",
        
        # Component-specific
        "button_raised": f"""
            bg-{base_color_light} dark:bg-{base_color_dark}
            {light_shadows['raised']} dark:{dark_shadows['raised']}
            text-{primary_color} font-medium
            px-6 py-3 rounded-2xl
            hover:{light_shadows['pressed'].replace('shadow-', 'shadow-')} 
            dark:hover:{dark_shadows['pressed']}
            active:{light_shadows['pressed']} 
            dark:active:{dark_shadows['pressed']}
            transition-all duration-150
        """,
        
        "button_pressed": f"""
            bg-{base_color_light} dark:bg-{base_color_dark}
            {light_shadows['pressed']} dark:{dark_shadows['pressed']}
            text-{primary_color} font-medium
            px-6 py-3 rounded-2xl
        """,
        
        "card_raised": f"""
            bg-{base_color_light} dark:bg-{base_color_dark}
            {light_shadows['raised']} dark:{dark_shadows['raised']}
            rounded-3xl p-6
        """,
        
        "input_inset": f"""
            bg-{base_color_light} dark:bg-{base_color_dark}
            {light_shadows['pressed']} dark:{dark_shadows['pressed']}
            rounded-xl px-4 py-3
            text-slate-700 dark:text-slate-200
            placeholder:text-slate-400
            focus:outline-none focus:ring-2 focus:ring-{primary_color}/50
        """,
        
        # Toggle switch (requires both states)
        "toggle_off": light_shadows["pressed"],
        "toggle_on": light_shadows["raised"],
        "toggle_off_dark": dark_shadows["pressed"],
        "toggle_on_dark": dark_shadows["raised"],
    }
    
    return theme


# System Prompt'a eklenecek Neumorphism kuralları
NEUMORPHISM_DESIGN_RULES = """
## NEUMORPHISM (SOFT-UI) RULES

1. **Background Color is Critical**:
   - Light mode: Use ONLY `bg-slate-100` or `bg-gray-100`
   - Dark mode: Use ONLY `bg-slate-800` or `bg-zinc-800`
   - Shadows are calculated relative to these exact colors

2. **Light Mode Shadows**:
```html
   <!-- Raised element -->
   shadow-[8px_8px_16px_#c8d0db,-8px_-8px_16px_#ffffff]
   
   <!-- Pressed/Inset element -->
   shadow-[inset_8px_8px_16px_#c8d0db,inset_-8px_-8px_16px_#ffffff]
```

3. **Dark Mode Shadows**:
```html
   <!-- Raised element -->
   dark:shadow-[8px_8px_16px_#0f1623,-8px_-8px_16px_#3d4a5c]
   
   <!-- Pressed/Inset element -->
   dark:shadow-[inset_8px_8px_16px_#0f1623,inset_-8px_-8px_16px_#3d4a5c]
```

4. **Never Use**:
   - Standard Tailwind shadows (`shadow-lg`) 
   - Borders (use shadows instead)
   - Pure white or black backgrounds

5. **Interactive States**:
   - Hover: Subtle shadow reduction
   - Active/Pressed: Switch to inset shadow
   - Focus: Add colored ring, not shadow change

6. **Accessibility**:
   - Add subtle borders (`border border-slate-200/50`) for low-vision users
   - Ensure text contrast meets WCAG AA
"""

6. Corporate — Generic'likten Kurtarma
Mevcut Problem
python# Çok standart, ayırt edici özellik yok
"primary": "blue-700",
"border_radius": "rounded-md",
Çözüm: Industry-Specific Corporate Themes
python# frontend_presets.py - Corporate Theme Enhancement

CORPORATE_INDUSTRIES = {
    "finance": {
        "name": "Corporate Finance",
        "primary": "blue-800",
        "secondary": "emerald-600",
        "accent": "amber-500",
        "personality": "trustworthy, stable, premium",
        "suggested_fonts": ["Inter", "SF Pro", "IBM Plex Sans"],
        "icon_style": "outline",
        "imagery": "abstract geometric, charts, upward arrows",
    },
    "healthcare": {
        "name": "Corporate Healthcare",
        "primary": "teal-600",
        "secondary": "blue-500",
        "accent": "rose-500",
        "personality": "caring, clean, professional",
        "suggested_fonts": ["Plus Jakarta Sans", "Source Sans Pro"],
        "icon_style": "outline",
        "imagery": "people, medical, nature",
    },
    "legal": {
        "name": "Corporate Legal",
        "primary": "slate-800",
        "secondary": "amber-700",
        "accent": "blue-600",
        "personality": "authoritative, traditional, refined",
        "suggested_fonts": ["Playfair Display", "Lora", "Libre Baskerville"],
        "icon_style": "solid",
        "imagery": "classical, scales, columns",
    },
    "tech": {
        "name": "Corporate Tech",
        "primary": "indigo-600",
        "secondary": "violet-500",
        "accent": "cyan-400",
        "personality": "innovative, modern, dynamic",
        "suggested_fonts": ["Outfit", "Space Grotesk", "Manrope"],
        "icon_style": "outline",
        "imagery": "abstract, connected nodes, gradients",
    },
    "manufacturing": {
        "name": "Corporate Manufacturing",
        "primary": "orange-600",
        "secondary": "slate-700",
        "accent": "yellow-500",
        "personality": "reliable, industrial, strong",
        "suggested_fonts": ["DM Sans", "Roboto", "Work Sans"],
        "icon_style": "solid",
        "imagery": "machinery, workers, precision",
    },
    "consulting": {
        "name": "Corporate Consulting",
        "primary": "blue-700",
        "secondary": "slate-600",
        "accent": "emerald-500",
        "personality": "expert, strategic, sophisticated",
        "suggested_fonts": ["Söhne", "Graphik", "Calibre"],
        "icon_style": "outline",
        "imagery": "abstract, people, data visualization",
    },
}

CORPORATE_LAYOUTS = {
    "traditional": {
        "max_width": "max-w-6xl",
        "spacing": "generous",  # py-20, gap-12
        "grid": "12-column",
        "header_style": "centered-logo",
    },
    "modern": {
        "max_width": "max-w-7xl",
        "spacing": "balanced",  # py-16, gap-8
        "grid": "flexible",
        "header_style": "left-logo-right-nav",
    },
    "editorial": {
        "max_width": "max-w-4xl",
        "spacing": "airy",  # py-24, gap-16
        "grid": "single-column-focused",
        "header_style": "minimal",
    },
}


def create_corporate_theme(
    industry: Literal["finance", "healthcare", "legal", "tech", "manufacturing", "consulting"] = "consulting",
    layout: Literal["traditional", "modern", "editorial"] = "modern",
    formality: Literal["formal", "semi-formal", "approachable"] = "semi-formal",
    include_accent_gradients: bool = False,
) -> Dict[str, Any]:
    """
    Industry-specific corporate theme with personality.
    """
    
    ind = CORPORATE_INDUSTRIES[industry]
    lay = CORPORATE_LAYOUTS[layout]
    
    # Formality affects typography and spacing
    formality_settings = {
        "formal": {
            "heading_weight": "font-semibold",
            "body_size": "text-base",
            "letter_spacing": "tracking-tight",
            "button_style": "uppercase tracking-wider",
        },
        "semi-formal": {
            "heading_weight": "font-bold",
            "body_size": "text-base",
            "letter_spacing": "tracking-normal",
            "button_style": "normal-case",
        },
        "approachable": {
            "heading_weight": "font-bold",
            "body_size": "text-lg",
            "letter_spacing": "tracking-normal",
            "button_style": "normal-case font-medium",
        },
    }
    
    form = formality_settings[formality]
    
    # Spacing based on layout
    spacing_map = {
        "generous": {"section": "py-20 md:py-28", "gap": "gap-12", "container": "px-6 md:px-12"},
        "balanced": {"section": "py-16 md:py-20", "gap": "gap-8", "container": "px-4 md:px-8"},
        "airy": {"section": "py-24 md:py-32", "gap": "gap-16", "container": "px-6 md:px-8"},
    }
    spacing = spacing_map.get(lay["spacing"], spacing_map["balanced"])
    
    theme = {
        "name": f"corporate-{industry}-{layout}",
        "description": f"{ind['name']} with {layout} layout - {ind['personality']}",
        
        # Industry colors
        "primary": ind["primary"],
        "primary_hover": ind["primary"].replace("-800", "-900").replace("-700", "-800").replace("-600", "-700"),
        "secondary": ind["secondary"],
        "accent": ind["accent"],
        
        # Neutral base
        "background": "white",
        "background_dark": "slate-900",
        "surface": "slate-50",
        "surface_dark": "slate-800",
        "border": "slate-200",
        "border_dark": "slate-700",
        
        # Typography
        "text": "slate-800",
        "text_dark": "slate-100",
        "text_muted": "slate-500",
        "font": "font-sans",
        "heading_weight": form["heading_weight"],
        "letter_spacing": form["letter_spacing"],
        
        # Layout
        "max_width": lay["max_width"],
        "section_padding": spacing["section"],
        "element_gap": spacing["gap"],
        "container_padding": spacing["container"],
        
        # Style
        "border_radius": "rounded-lg",
        "shadow": "shadow-sm",
        "shadow_hover": "shadow-md",
        
        # Distinctive element (what makes this NOT generic)
        "distinctive_element": _generate_distinctive_element(industry, ind["accent"]),
        
        # Button style
        "button_primary": f"""
            bg-{ind['primary']} hover:bg-{ind['primary'].replace('-700', '-800').replace('-600', '-700')}
            text-white {form['button_style']}
            px-6 py-3 rounded-lg
            shadow-sm hover:shadow-md
            transition-all duration-200
        """,
        
        # Accent gradient (optional)
        "accent_gradient": f"bg-gradient-to-r from-{ind['primary']} to-{ind['secondary']}" if include_accent_gradients else "",
        
        # Industry-specific metadata
        "_industry": industry,
        "_personality": ind["personality"],
        "_suggested_fonts": ind["suggested_fonts"],
        "_icon_style": ind["icon_style"],
    }
    
    return theme


def _generate_distinctive_element(industry: str, accent: str) -> str:
    """Generate a distinctive visual element for the industry"""
    elements = {
        "finance": f"border-l-4 border-{accent}",  # Left accent border
        "healthcare": f"before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-gradient-to-b before:from-{accent} before:to-transparent",
        "legal": f"border-b-2 border-{accent}",  # Underline accent
        "tech": f"ring-1 ring-{accent}/20 ring-offset-2",  # Subtle ring
        "manufacturing": f"shadow-[inset_0_-4px_0_0] shadow-{accent}",  # Bottom inset
        "consulting": f"after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-full after:bg-gradient-to-r after:from-{accent} after:to-transparent",
    }
    return elements.get(industry, "")

7. Gradient — Genişletilmiş Preset'ler
Mevcut Problem
python"gradient_primary": "bg-gradient-to-r from-violet-600 to-fuchsia-500",
# Sadece 2 gradient preset var
Çözüm: Comprehensive Gradient Library
python# frontend_presets.py - Gradient Theme Enhancement

GRADIENT_LIBRARY = {
    # Signature Gradients (Ana)
    "aurora": {
        "class": "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500",
        "text_contrast": "white",
        "category": "vibrant",
    },
    "sunset": {
        "class": "bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600",
        "text_contrast": "white",
        "category": "warm",
    },
    "ocean": {
        "class": "bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500",
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
    
    # Subtle Gradients (Kurumsal)
    "slate_subtle": {
        "class": "bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200",
        "text_contrast": "slate-800",
        "category": "subtle",
    },
    "blue_subtle": {
        "class": "bg-gradient-to-br from-blue-50 via-indigo-50 to-violet-50",
        "text_contrast": "slate-800",
        "category": "subtle",
    },
    "warm_subtle": {
        "class": "bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50",
        "text_contrast": "slate-800",
        "category": "subtle",
    },
    
    # Mesh Gradients (Modern)
    "mesh_purple": {
        "class": "bg-[radial-gradient(at_top_left,_#c084fc_0%,_transparent_50%),radial-gradient(at_bottom_right,_#f472b6_0%,_transparent_50%),radial-gradient(at_top_right,_#60a5fa_0%,_transparent_50%)]",
        "bg_color": "bg-slate-900",
        "text_contrast": "white",
        "category": "mesh",
    },
    "mesh_ocean": {
        "class": "bg-[radial-gradient(at_top_left,_#22d3ee_0%,_transparent_50%),radial-gradient(at_bottom_right,_#3b82f6_0%,_transparent_50%),radial-gradient(at_center,_#8b5cf6_0%,_transparent_60%)]",
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
    
    # Dark Mode Specific
    "dark_glow": {
        "class": "bg-gradient-to-r from-slate-900 via-purple-900/50 to-slate-900",
        "text_contrast": "white",
        "category": "dark",
    },
    "dark_aurora": {
        "class": "bg-[linear-gradient(to_right,#0f172a,#1e1b4b,#312e81,#1e1b4b,#0f172a)]",
        "text_contrast": "white",
        "category": "dark",
    },
    
    # Animated Gradients
    "animated_flow": {
        "class": "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500 bg-[length:200%_200%] animate-gradient-x",
        "text_contrast": "white",
        "category": "animated",
        "keyframes": "@keyframes gradient-x { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }",
    },
    "animated_pulse": {
        "class": "bg-gradient-to-r from-cyan-500 to-blue-500 animate-pulse-subtle",
        "text_contrast": "white",
        "category": "animated",
        "keyframes": "@keyframes pulse-subtle { 0%, 100% { opacity: 1; } 50% { opacity: 0.85; } }",
    },
    
    # Border Gradients
    "border_rainbow": {
        "class": "bg-gradient-to-r from-red-500 via-yellow-500 via-green-500 via-blue-500 to-purple-500",
        "usage": "For gradient borders using p-[2px] technique",
        "category": "border",
    },
    "border_accent": {
        "class": "bg-gradient-to-r from-violet-600 to-indigo-600",
        "usage": "Accent border gradient",
        "category": "border",
    },
    
    # Text Gradients
    "text_shimmer": {
        "class": "bg-gradient-to-r from-slate-900 via-slate-600 to-slate-900 bg-clip-text text-transparent bg-[length:200%_auto] animate-shimmer",
        "category": "text",
    },
    "text_vibrant": {
        "class": "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500 bg-clip-text text-transparent",
        "category": "text",
    },
}

GRADIENT_DIRECTIONS = {
    "r": "to-r",      # right
    "l": "to-l",      # left
    "t": "to-t",      # top
    "b": "to-b",      # bottom
    "tr": "to-tr",    # top-right
    "tl": "to-tl",    # top-left
    "br": "to-br",    # bottom-right
    "bl": "to-bl",    # bottom-left
}


def create_gradient_theme(
    primary_gradient: str = "aurora",
    secondary_gradient: str = "ocean",
    button_style: Literal["gradient", "solid_with_gradient_hover", "gradient_border"] = "gradient",
    card_style: Literal["subtle", "bordered", "glass"] = "subtle",
    dark_mode_gradient: str = "dark_aurora",
    include_animations: bool = True,
) -> Dict[str, Any]:
    """
    Comprehensive gradient theme with multiple presets.
    """
    
    primary = GRADIENT_LIBRARY[primary_gradient]
    secondary = GRADIENT_LIBRARY[secondary_gradient]
    dark_bg = GRADIENT_LIBRARY[dark_mode_gradient]
    
    # Collect all needed keyframes
    keyframes = []
    if include_animations:
        for g in [primary, secondary]:
            if "keyframes" in g:
                keyframes.append(g["keyframes"])
    
    theme = {
        "name": f"gradient-{primary_gradient}",
        "description": f"Gradient theme with {primary_gradient} primary",
        
        # Gradient presets
        "gradient_primary": primary["class"],
        "gradient_secondary": secondary["class"],
        "gradient_text": GRADIENT_LIBRARY["text_vibrant"]["class"],
        
        # Standard colors for non-gradient elements
        "primary": "violet-600",
        "primary_hover": "violet-700",
        "secondary": "fuchsia-500",
        "accent": "cyan-400",
        
        # Backgrounds
        "background": "white",
        "background_dark": "slate-950",
        "background_gradient_dark": dark_bg["class"],
        "surface": "slate-50",
        "surface_dark": "slate-900",
        
        # Text
        "text": "slate-900",
        "text_dark": "white",
        "text_muted": "slate-500",
        
        # Border & Style
        "border": "slate-200",
        "border_radius": "rounded-2xl",
        "shadow": "shadow-lg shadow-violet-500/10",
        "shadow_hover": "shadow-xl shadow-violet-500/20",
        
        # Button variants
        "button_gradient": f"""
            {primary['class']}
            text-{primary['text_contrast']} font-semibold
            px-6 py-3 rounded-xl
            shadow-lg shadow-violet-500/25
            hover:shadow-xl hover:shadow-violet-500/40
            hover:scale-[1.02]
            active:scale-[0.98]
            transition-all duration-200
        """,
        
        "button_gradient_border": f"""
            relative bg-white dark:bg-slate-900 text-slate-900 dark:text-white
            font-semibold px-6 py-3 rounded-xl
            before:absolute before:inset-0 before:rounded-xl before:p-[2px]
            before:{primary['class']} before:-z-10
            hover:before:p-[3px]
            transition-all duration-200
        """,
        
        # Card variants
        "card_subtle": f"""
            bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900
            border border-slate-200 dark:border-slate-700
            rounded-2xl shadow-lg
        """,
        
        "card_gradient_border": f"""
            relative bg-white dark:bg-slate-900 rounded-2xl
            before:absolute before:inset-0 before:rounded-2xl before:p-[1px]
            before:{primary['class']} before:-z-10
        """,
        
        # All available gradients
        "available_gradients": list(GRADIENT_LIBRARY.keys()),
        
        # Animation keyframes
        "_keyframes": "\n".join(keyframes),
    }
    
    return theme


def get_gradient(name: str) -> Dict[str, Any]:
    """Get a specific gradient from the library"""
    return GRADIENT_LIBRARY.get(name, GRADIENT_LIBRARY["aurora"])

def list_gradients_by_category(category: str) -> List[str]:
    """List gradients by category (vibrant, subtle, mesh, glass, dark, animated, border, text)"""
    return [name for name, g in GRADIENT_LIBRARY.items() if g.get("category") == category]

8. Cyberpunk — Glow Intensity Control
Mevcut Problem
python"shadow": "shadow-[0_0_15px_rgba(34,211,238,0.3)]",
# Sabit intensity, kontrol yok
Çözüm: Configurable Neon System
python# frontend_presets.py - Cyberpunk Theme Enhancement

NEON_COLORS = {
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

GLOW_INTENSITIES = {
    "subtle": {
        "blur": "10px",
        "opacity": 0.2,
        "spread": "0px",
        "layers": 1,
    },
    "medium": {
        "blur": "15px",
        "opacity": 0.3,
        "spread": "0px",
        "layers": 2,
    },
    "strong": {
        "blur": "20px",
        "opacity": 0.4,
        "spread": "5px",
        "layers": 2,
    },
    "intense": {
        "blur": "30px",
        "opacity": 0.5,
        "spread": "10px",
        "layers": 3,
    },
    "extreme": {
        "blur": "40px",
        "opacity": 0.6,
        "spread": "15px",
        "layers": 3,
    },
}


def generate_neon_glow(
    color: str,
    intensity: Literal["subtle", "medium", "strong", "intense", "extreme"] = "medium",
    animated: bool = False,
) -> str:
    """
    Generate multi-layer neon glow shadow.
    
    Multi-layer creates more realistic neon effect:
    - Inner layer: Sharp, bright
    - Middle layer: Medium blur
    - Outer layer: Wide, ambient
    """
    neon = NEON_COLORS.get(color, NEON_COLORS["cyan"])
    settings = GLOW_INTENSITIES[intensity]
    
    rgb = neon["rgb"]
    base_opacity = settings["opacity"]
    base_blur = int(settings["blur"].replace("px", ""))
    layers = settings["layers"]
    
    shadows = []
    
    if layers >= 1:
        # Inner glow (sharp)
        shadows.append(f"0_0_{base_blur // 2}px_rgba({rgb},{base_opacity + 0.1})")
    
    if layers >= 2:
        # Middle glow
        shadows.append(f"0_0_{base_blur}px_rgba({rgb},{base_opacity})")
    
    if layers >= 3:
        # Outer glow (ambient)
        shadows.append(f"0_0_{base_blur * 2}px_rgba({rgb},{base_opacity - 0.1})")
    
    shadow_class = f"shadow-[{','.join(shadows)}]"
    
    if animated:
        shadow_class += " animate-glow-pulse"
    
    return shadow_class


def create_cyberpunk_theme(
    primary_neon: str = "cyan",
    secondary_neon: str = "fuchsia",
    glow_intensity: Literal["subtle", "medium", "strong", "intense", "extreme"] = "medium",
    enable_animations: bool = True,
    scanline_effect: bool = False,
    chromatic_aberration: bool = False,
) -> Dict[str, Any]:
    """
    Cyberpunk theme with configurable neon effects.
    """
    
    primary = NEON_COLORS[primary_neon]
    secondary = NEON_COLORS[secondary_neon]
    
    # Generate glows
    primary_glow = generate_neon_glow(primary_neon, glow_intensity, enable_animations)
    secondary_glow = generate_neon_glow(secondary_neon, glow_intensity, False)
    
    # Hover intensified glow (one level up)
    intensity_order = list(GLOW_INTENSITIES.keys())
    current_idx = intensity_order.index(glow_intensity)
    hover_intensity = intensity_order[min(current_idx + 1, len(intensity_order) - 1)]
    hover_glow = generate_neon_glow(primary_neon, hover_intensity, False)
    
    theme = {
        "name": f"cyberpunk-{primary_neon}-{glow_intensity}",
        "description": f"Cyberpunk with {primary_neon} neon at {glow_intensity} intensity",
        
        # Neon colors
        "primary": primary["tailwind"],
        "primary_hex": primary["hex"],
        "secondary": secondary["tailwind"],
        "secondary_hex": secondary["hex"],
        "accent": "yellow-400",
        
        # Dark backgrounds (essential for neon)
        "background": "slate-950",
        "background_dark": "black",
        "surface": "slate-900",
        "surface_dark": "slate-950",
        
        # Neon text
        "text": "slate-100",
        "text_dark": "white",
        "text_muted": "slate-400",
        "text_neon": f"text-{primary['tailwind']} {primary_glow}",
        
        # Borders
        "border": f"{primary['tailwind']}/30",
        "border_radius": "rounded-none",  # Sharp cyberpunk edges
        "border_width": "border",
        
        # Glow effects (configurable)
        "glow_primary": primary_glow,
        "glow_secondary": secondary_glow,
        "glow_hover": hover_glow,
        
        # Shadows
        "shadow": primary_glow,
        "shadow_hover": hover_glow,
        
        # Typography
        "font": "font-mono",
        
        # Components with neon
        "button_neon": f"""
            bg-transparent
            text-{primary['tailwind']} font-bold uppercase tracking-wider
            px-6 py-3
            border-2 border-{primary['tailwind']}
            {primary_glow}
            hover:{hover_glow}
            hover:bg-{primary['tailwind']}/10
            active:bg-{primary['tailwind']}/20
            transition-all duration-300
        """,
        
        "button_neon_filled": f"""
            bg-{primary['tailwind']}
            text-black font-bold uppercase tracking-wider
            px-6 py-3
            {primary_glow}
            hover:{hover_glow}
            hover:brightness-110
            active:brightness-90
            transition-all duration-300
        """,
        
        "card_neon": f"""
            bg-slate-900/80 backdrop-blur-sm
            border border-{primary['tailwind']}/30
            {generate_neon_glow(primary_neon, "subtle")}
            hover:{primary_glow}
            transition-all duration-500
        """,
        
        "input_neon": f"""
            bg-slate-900
            text-{primary['tailwind']}
            border border-{primary['tailwind']}/30
            {generate_neon_glow(primary_neon, "subtle")}
            focus:border-{primary['tailwind']}
            focus:{primary_glow}
            placeholder:text-slate-500
            font-mono
            transition-all duration-300
        """,
        
        # Intensity levels for reference
        "available_intensities": list(GLOW_INTENSITIES.keys()),
        "current_intensity": glow_intensity,
        
        # Optional effects
        "_scanline_css": SCANLINE_CSS if scanline_effect else "",
        "_chromatic_css": CHROMATIC_CSS if chromatic_aberration else "",
    }
    
    # Animation keyframes
    if enable_animations:
        theme["_keyframes"] = f"""
        @keyframes glow-pulse {{
            0%, 100% {{ 
                box-shadow: 0 0 {GLOW_INTENSITIES[glow_intensity]['blur']} rgba({primary['rgb']},{GLOW_INTENSITIES[glow_intensity]['opacity']});
            }}
            50% {{ 
                box-shadow: 0 0 {int(GLOW_INTENSITIES[glow_intensity]['blur'].replace('px','')) * 1.5}px rgba({primary['rgb']},{GLOW_INTENSITIES[glow_intensity]['opacity'] + 0.1});
            }}
        }}
        .animate-glow-pulse {{
            animation: glow-pulse 2s ease-in-out infinite;
        }}
        """
    
    return theme


SCANLINE_CSS = """
/* CRT Scanline Effect */
.scanlines::after {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.1) 0px,
        rgba(0, 0, 0, 0.1) 1px,
        transparent 1px,
        transparent 2px
    );
    pointer-events: none;
}
"""

CHROMATIC_CSS = """
/* Chromatic Aberration Effect */
.chromatic {
    text-shadow: 
        -2px 0 rgba(255, 0, 0, 0.5),
        2px 0 rgba(0, 255, 255, 0.5);
}
.chromatic-hover:hover {
    animation: chromatic-shift 0.3s ease;
}
@keyframes chromatic-shift {
    0%, 100% { text-shadow: -2px 0 rgba(255,0,0,0.5), 2px 0 rgba(0,255,255,0.5); }
    25% { text-shadow: -4px 0 rgba(255,0,0,0.7), 4px 0 rgba(0,255,255,0.7); }
    50% { text-shadow: -2px 0 rgba(255,0,0,0.5), 2px 0 rgba(0,255,255,0.5); }
    75% { text-shadow: -3px 0 rgba(255,0,0,0.6), 3px 0 rgba(0,255,255,0.6); }
}
"""

9. Retro — Font Pairing System
Mevcut Problem
python"font": "font-sans",
# Retro feel için font pairing yok
Çözüm: Curated Font Pairing Library
python# frontend_presets.py - Retro Theme Enhancement

RETRO_FONT_PAIRINGS = {
    "80s_tech": {
        "heading": {
            "family": "'VT323', monospace",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');",
            "tailwind_class": "font-['VT323']",
            "fallback": "font-mono",
            "weight": "font-normal",  # VT323 only has regular
            "style": "uppercase tracking-[0.2em]",
        },
        "body": {
            "family": "'Share Tech Mono', monospace",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');",
            "tailwind_class": "font-['Share_Tech_Mono']",
            "fallback": "font-mono",
        },
        "accent": {
            "family": "'Orbitron', sans-serif",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');",
            "tailwind_class": "font-['Orbitron']",
        },
        "era": "1980s tech/sci-fi",
        "pair_reason": "Terminal-style heading with cleaner mono body",
    },
    
    "80s_neon": {
        "heading": {
            "family": "'Monoton', cursive",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Monoton&display=swap');",
            "tailwind_class": "font-['Monoton']",
            "fallback": "font-serif",
            "style": "uppercase",
        },
        "body": {
            "family": "'Rajdhani', sans-serif",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600&display=swap');",
            "tailwind_class": "font-['Rajdhani']",
            "fallback": "font-sans",
        },
        "accent": {
            "family": "'Audiowide', cursive",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Audiowide&display=swap');",
            "tailwind_class": "font-['Audiowide']",
        },
        "era": "1980s neon/arcade",
        "pair_reason": "Neon sign display heading with futuristic body",
    },
    
    "90s_grunge": {
        "heading": {
            "family": "'Bebas Neue', sans-serif",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');",
            "tailwind_class": "font-['Bebas_Neue']",
            "fallback": "font-sans",
            "style": "uppercase tracking-wide",
        },
        "body": {
            "family": "'Work Sans', sans-serif",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;500;600&display=swap');",
            "tailwind_class": "font-['Work_Sans']",
            "fallback": "font-sans",
        },
        "accent": {
            "family": "'Permanent Marker', cursive",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&display=swap');",
            "tailwind_class": "font-['Permanent_Marker']",
        },
        "era": "1990s grunge/alternative",
        "pair_reason": "Condensed bold heading with clean geometric body, handwritten accent",
    },
    
    "90s_web": {
        "heading": {
            "family": "'Comic Neue', cursive",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap');",
            "tailwind_class": "font-['Comic_Neue']",
            "fallback": "font-sans",
        },
        "body": {
            "family": "'Courier Prime', monospace",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');",
            "tailwind_class": "font-['Courier_Prime']",
            "fallback": "font-mono",
        },
        "accent": {
            "family": "'Press Start 2P', cursive",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');",
            "tailwind_class": "font-['Press_Start_2P']",
            "style": "text-xs",  # This font needs smaller size
        },
        "era": "1990s early web/Geocities",
        "pair_reason": "Playful Comic Sans alternative with typewriter body",
    },
    
    "retro_futurism": {
        "heading": {
            "family": "'Syncopate', sans-serif",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&display=swap');",
            "tailwind_class": "font-['Syncopate']",
            "fallback": "font-sans",
            "style": "uppercase tracking-widest",
        },
        "body": {
            "family": "'Exo 2', sans-serif",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@400;500;600&display=swap');",
            "tailwind_class": "font-['Exo_2']",
            "fallback": "font-sans",
        },
        "accent": {
            "family": "'Major Mono Display', monospace",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Major+Mono+Display&display=swap');",
            "tailwind_class": "font-['Major_Mono_Display']",
        },
        "era": "Retro-futurism (Space Age)",
        "pair_reason": "Wide-spaced geometric heading with tech body",
    },
    
    "vintage_americana": {
        "heading": {
            "family": "'Righteous', cursive",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Righteous&display=swap');",
            "tailwind_class": "font-['Righteous']",
            "fallback": "font-serif",
        },
        "body": {
            "family": "'Lato', sans-serif",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');",
            "tailwind_class": "font-['Lato']",
            "fallback": "font-sans",
        },
        "accent": {
            "family": "'Pacifico', cursive",
            "google_import": "@import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');",
            "tailwind_class": "font-['Pacifico']",
        },
        "era": "1950s-60s Americana",
        "pair_reason": "Groovy display with clean body, script accent",
    },
}


def create_retro_theme(
    era: Literal["80s_tech", "80s_neon", "90s_grunge", "90s_web", "retro_futurism", "vintage_americana"] = "80s_neon",
    color_scheme: Literal["neon", "pastel", "earthy", "chrome"] = "neon",
    enable_crt_effects: bool = False,
) -> Dict[str, Any]:
    """
    Retro theme with era-specific font pairings.
    """
    
    fonts = RETRO_FONT_PAIRINGS[era]
    
    # Color schemes by retro era
    color_schemes = {
        "neon": {
            "primary": "fuchsia-500",
            "secondary": "cyan-400",
            "accent": "yellow-400",
            "background": "slate-900",
            "surface": "slate-800",
        },
        "pastel": {
            "primary": "pink-400",
            "secondary": "sky-400",
            "accent": "lime-400",
            "background": "amber-50",
            "surface": "white",
        },
        "earthy": {
            "primary": "orange-600",
            "secondary": "teal-600",
            "accent": "amber-500",
            "background": "stone-100",
            "surface": "white",
        },
        "chrome": {
            "primary": "slate-400",
            "secondary": "blue-400",
            "accent": "amber-400",
            "background": "slate-900",
            "surface": "slate-800",
        },
    }
    
    colors = color_schemes[color_scheme]
    
    # Collect all font imports
    font_imports = [
        fonts["heading"]["google_import"],
        fonts["body"]["google_import"],
    ]
    if "accent" in fonts:
        font_imports.append(fonts["accent"]["google_import"])
    
    theme = {
        "name": f"retro-{era}-{color_scheme}",
        "description": f"{fonts['era']} aesthetic with {color_scheme} colors",
        
        # Typography
        "font_heading": fonts["heading"]["tailwind_class"],
        "font_heading_style": fonts["heading"].get("style", ""),
        "font_body": fonts["body"]["tailwind_class"],
        "font_accent": fonts.get("accent", {}).get("tailwind_class", fonts["heading"]["tailwind_class"]),
        "font_fallback_heading": fonts["heading"]["fallback"],
        "font_fallback_body": fonts["body"]["fallback"],
        
        # Colors
        "primary": colors["primary"],
        "secondary": colors["secondary"],
        "accent": colors["accent"],
        "background": colors["background"],
        "background_dark": "slate-950",
        "surface": colors["surface"],
        "surface_dark": "slate-800",
        
        # Era-specific styling
        "border": colors["primary"].split("-")[0] + "-300",
        "border_radius": "rounded-none" if era in ["80s_tech", "90s_grunge"] else "rounded-lg",
        
        # Retro shadows
        "shadow": f"shadow-[4px_4px_0px] shadow-{colors['primary']}",
        "shadow_hover": f"shadow-[6px_6px_0px] shadow-{colors['primary']}",
        
        # Font imports
        "_font_imports": "\n".join(font_imports),
        
        # Heading example
        "heading_classes": f"""
            {fonts["heading"]["tailwind_class"]}
            {fonts["heading"].get("style", "")}
            {fonts["heading"].get("weight", "font-bold")}
            text-{colors["primary"]}
        """,
        
        # Body example
        "body_classes": f"""
            {fonts["body"]["tailwind_class"]}
            text-slate-700 dark:text-slate-300
        """,
        
        # Button with era style
        "button_retro": f"""
            {fonts["heading"]["tailwind_class"]}
            {fonts["heading"].get("style", "")}
            bg-{colors["primary"]} text-white
            px-6 py-3
            shadow-[4px_4px_0px] shadow-black
            hover:shadow-[6px_6px_0px]
            hover:-translate-y-0.5 hover:translate-x-0.5
            active:shadow-[2px_2px_0px]
            active:translate-y-0 active:translate-x-0
            transition-all duration-150
        """,
    }
    
    # CRT effects (optional)
    if enable_crt_effects:
        theme["_crt_css"] = CRT_EFFECT_CSS
    
    return theme


CRT_EFFECT_CSS = """
/* CRT Monitor Effect */
.crt {
    position: relative;
    overflow: hidden;
}

.crt::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.15) 0px,
        rgba(0, 0, 0, 0.15) 1px,
        transparent 1px,
        transparent 2px
    );
    pointer-events: none;
    z-index: 10;
}

.crt::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(
        circle at center,
        transparent 0%,
        rgba(0, 0, 0, 0.2) 100%
    );
    pointer-events: none;
    z-index: 11;
}

/* Screen flicker */
@keyframes flicker {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.98; }
}
.crt-flicker {
    animation: flicker 0.1s infinite;
}
"""

10. Pastel — Contrast Ratio İyileştirmesi
Mevcut Problem
python"primary": "rose-400",
"text": "slate-700",
# Light pastel backgrounds üzerinde yetersiz kontrast
Çözüm: Accessible Pastel System
python# frontend_presets.py - Pastel Theme Enhancement

PASTEL_ACCESSIBLE_PAIRS = {
    # Her pastel için güvenli text renkleri
    "rose": {
        "bg": "rose-50",
        "bg_medium": "rose-100",
        "text_safe": "rose-900",      # 7:1+ contrast
        "text_medium": "rose-800",    # 4.5:1+ contrast
        "accent": "rose-600",         # For icons/borders
        "button_bg": "rose-600",      # Dark enough for white text
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
        "button_bg": "amber-700",  # Amber needs darker for contrast
    },
    "lime": {
        "bg": "lime-50",
        "bg_medium": "lime-100",
        "text_safe": "lime-900",
        "text_medium": "lime-800",
        "accent": "lime-700",     # Lime needs darker
        "button_bg": "lime-700",
    },
}


def create_pastel_theme(
    primary_pastel: Literal["rose", "pink", "sky", "violet", "teal", "amber", "lime"] = "rose",
    secondary_pastel: Literal["rose", "pink", "sky", "violet", "teal", "amber", "lime"] = "sky",
    wcag_level: Literal["AA", "AAA"] = "AA",
    dark_mode_handling: Literal["invert", "desaturate", "vibrant"] = "desaturate",
) -> Dict[str, Any]:
    """
    WCAG-compliant pastel theme with guaranteed contrast ratios.
    """
    
    primary = PASTEL_ACCESSIBLE_PAIRS[primary_pastel]
    secondary = PASTEL_ACCESSIBLE_PAIRS[secondary_pastel]
    
    # Text color based on WCAG level
    if wcag_level == "AAA":
        text_color = primary["text_safe"]  # 7:1 ratio
        muted_color = primary["text_medium"]
    else:
        text_color = primary["text_medium"]  # 4.5:1 ratio
        muted_color = f"{primary_pastel}-700"
    
    # Dark mode color strategy
    dark_mode_colors = {
        "invert": {
            "background": f"{primary_pastel}-900",
            "surface": f"{primary_pastel}-800",
            "text": f"{primary_pastel}-100",
        },
        "desaturate": {
            "background": "slate-800",
            "surface": "slate-700",
            "text": "slate-200",
        },
        "vibrant": {
            "background": f"{primary_pastel}-950",
            "surface": f"{primary_pastel}-900",
            "text": f"{primary_pastel}-200",
        },
    }
    
    dark = dark_mode_colors[dark_mode_handling]
    
    theme = {
        "name": f"pastel-{primary_pastel}-{wcag_level}",
        "description": f"Accessible pastel theme (WCAG {wcag_level} compliant)",
        
        # Primary colors
        "primary": primary["accent"],
        "primary_hover": primary["button_bg"],
        "secondary": secondary["accent"],
        "accent": secondary["button_bg"],
        
        # Light mode backgrounds
        "background": primary["bg"],
        "surface": primary["bg_medium"],
        
        # Dark mode backgrounds
        "background_dark": dark["background"],
        "surface_dark": dark["surface"],
        
        # Text (WCAG compliant)
        "text": text_color,
        "text_dark": dark["text"],
        "text_muted": muted_color,
        
        # Borders
        "border": secondary["bg_medium"],
        "border_dark": "slate-600",
        
        # Styling
        "border_radius": "rounded-2xl",
        "shadow": "shadow-sm",
        "shadow_hover": "shadow-md",
        
        # Contrast-safe button
        "button_primary": f"""
            bg-{primary['button_bg']} hover:bg-{primary['button_bg'].replace('-600', '-700').replace('-700', '-800')}
            text-white font-medium
            px-6 py-3 rounded-xl
            shadow-sm hover:shadow-md
            transition-all duration-200
        """,
        
        # Secondary button (pastel with dark text)
        "button_secondary": f"""
            bg-{primary['bg_medium']} hover:bg-{primary['bg']}
            text-{text_color} font-medium
            border border-{primary['accent']}/30
            px-6 py-3 rounded-xl
            transition-all duration-200
        """,
        
        # Card with guaranteed readable text
        "card_pastel": f"""
            bg-{primary['bg_medium']} dark:bg-{dark['surface']}
            text-{text_color} dark:text-{dark['text']}
            rounded-2xl p-6
            border border-{primary['accent']}/20
        """,
        
        # Input with visible focus
        "input_pastel": f"""
            bg-white dark:bg-{dark['surface']}
            text-{text_color} dark:text-{dark['text']}
            border border-{primary['accent']}/30
            rounded-xl px-4 py-3
            focus:border-{primary['accent']}
            focus:ring-2 focus:ring-{primary['accent']}/20
            placeholder:text-{muted_color}
        """,
        
        # WCAG metadata
        "_wcag_level": wcag_level,
        "_min_contrast_ratio": 7.0 if wcag_level == "AAA" else 4.5,
    }
    
    return theme


# System Prompt'a eklenecek Pastel kuralları
PASTEL_DESIGN_RULES = """
## PASTEL THEME ACCESSIBILITY RULES

Pastel themes require special attention to maintain WCAG compliance.

1. **Never use pastel colors for text on pastel backgrounds**:
   - ❌ `text-rose-400` on `bg-rose-50` (1.5:1 - FAIL)
   - ✓ `text-rose-900` on `bg-rose-50` (7.2:1 - PASS AAA)
   - ✓ `text-rose-800` on `bg-rose-50` (5.1:1 - PASS AA)

2. **Button text must be white or near-black**:
   - Use `bg-{color}-600` or darker for buttons with white text
   - For pastel button backgrounds, use `text-{color}-900`

3. **Muted text minimum**:
   - On pastel backgrounds: Use `{color}-700` minimum
   - Never use `{color}-400` or `{color}-500` for text

4. **Border visibility**:
   - Borders should be `{color}-300` minimum for visibility
   - Or use `{color}-600/30` for subtle but visible borders

5. **Dark mode strategy**:
   - Don't just invert pastels (becomes too saturated)
   - Use desaturated versions: `{color}-200` text on `slate-800`
"""

11. Dark Mode First — Light Mode İyileştirmesi
Mevcut Problem
python# Dark mode güçlü ama light mode düşünülmemiş
"background": "slate-900",
# Light mode için kaynak yok
Çözüm: Balanced Dual-Mode System
python# frontend_presets.py - Dark Mode First Enhancement

def create_dark_mode_first_theme(
    primary_glow: str = "emerald",
    contrast_level: Literal["normal", "high"] = "normal",
    light_mode_style: Literal["minimal", "warm", "cool", "inverted"] = "minimal",
) -> Dict[str, Any]:
    """
    Dark mode optimized theme with equally polished light mode.
    
    The key insight: "Dark mode first" doesn't mean light mode is an afterthought.
    It means dark mode is the PRIMARY experience, but light mode is still excellent.
    """
    
    # Primary glow color variations
    glow_colors = {
        "emerald": {
            "primary": "emerald-500",
            "primary_hover": "emerald-400",
            "glow": "emerald-500/20",
            "light_accent": "emerald-600",  # Darker for light mode
        },
        "cyan": {
            "primary": "cyan-400",
            "primary_hover": "cyan-300",
            "glow": "cyan-400/20",
            "light_accent": "cyan-600",
        },
        "violet": {
            "primary": "violet-500",
            "primary_hover": "violet-400",
            "glow": "violet-500/20",
            "light_accent": "violet-600",
        },
        "amber": {
            "primary": "amber-500",
            "primary_hover": "amber-400",
            "glow": "amber-500/20",
            "light_accent": "amber-600",
        },
    }
    
    glow = glow_colors.get(primary_glow, glow_colors["emerald"])
    
    # Light mode style variations
    light_styles = {
        "minimal": {
            "background": "white",
            "surface": "slate-50",
            "text": "slate-900",
            "text_muted": "slate-600",
            "border": "slate-200",
        },
        "warm": {
            "background": "amber-50",
            "surface": "white",
            "text": "stone-900",
            "text_muted": "stone-600",
            "border": "amber-200",
        },
        "cool": {
            "background": "slate-100",
            "surface": "white",
            "text": "slate-900",
            "text_muted": "slate-500",
            "border": "slate-300",
        },
        "inverted": {
            # Dark-ish light mode for consistency
            "background": "slate-200",
            "surface": "slate-100",
            "text": "slate-900",
            "text_muted": "slate-600",
            "border": "slate-300",
        },
    }
    
    light = light_styles[light_mode_style]
    
    theme = {
        "name": f"dark-first-{primary_glow}",
        "description": f"Dark mode optimized with {light_mode_style} light mode",
        
        # Primary (same for both modes)
        "primary": glow["primary"],
        "primary_hover": glow["primary_hover"],
        "primary_light": glow["light_accent"],  # For light mode usage
        
        # === DARK MODE (Primary) ===
        "background_dark": "slate-900",
        "background_darker": "slate-950",
        "surface_dark": "slate-800",
        "surface_elevated_dark": "slate-700",
        "text_dark": "white",
        "text_muted_dark": "slate-400",
        "border_dark": "slate-700",
        
        # Dark mode glow effects
        "glow_dark": f"shadow-lg shadow-{glow['glow']}",
        "glow_hover_dark": f"shadow-xl shadow-{glow['glow'].replace('/20', '/30')}",
        
        # === LIGHT MODE (Secondary but polished) ===
        "background": light["background"],
        "surface": light["surface"],
        "surface_elevated": "white",
        "text": light["text"],
        "text_muted": light["text_muted"],
        "border": light["border"],
        
        # Light mode shadows (no glow, subtle)
        "shadow": "shadow-sm",
        "shadow_hover": "shadow-md",
        
        # === RESPONSIVE CLASSES ===
        "border_radius": "rounded-xl",
        
        # Button that works in both modes
        "button_primary": f"""
            bg-{glow['primary']} hover:bg-{glow['primary_hover']}
            text-black dark:text-black font-medium
            px-6 py-3 rounded-xl
            shadow-sm hover:shadow-md
            dark:shadow-lg dark:shadow-{glow['glow']}
            dark:hover:shadow-xl dark:hover:shadow-{glow['glow'].replace('/20', '/30')}
            transition-all duration-200
        """,
        
        # Card that adapts well
        "card_adaptive": f"""
            bg-{light['surface']} dark:bg-slate-800
            text-{light['text']} dark:text-white
            border border-{light['border']} dark:border-slate-700
            rounded-xl p-6
            shadow-sm dark:shadow-lg dark:shadow-black/20
        """,
        
        # Surface with elevation
        "surface_elevated_classes": f"""
            bg-white dark:bg-slate-700
            shadow-md dark:shadow-lg dark:shadow-black/30
            rounded-xl
        """,
    }
    
    # High contrast adjustments
    if contrast_level == "high":
        theme["text"] = "black"
        theme["text_dark"] = "white"
        theme["text_muted"] = "slate-700"
        theme["text_muted_dark"] = "slate-300"
        theme["border"] = "slate-400"
        theme["border_dark"] = "slate-500"
    
    return theme


# Light mode için additional utility classes
DARK_FIRST_UTILITIES = """
/* Smooth mode transitions */
* {
    transition: background-color 0.2s ease, 
                border-color 0.2s ease, 
                color 0.1s ease;
}

/* Prevent flash on load */
html.dark {
    color-scheme: dark;
}

/* Elevation system for dark mode */
.dark .elevation-1 { background-color: rgb(30 41 59); }  /* slate-800 */
.dark .elevation-2 { background-color: rgb(51 65 85); }  /* slate-700 */
.dark .elevation-3 { background-color: rgb(71 85 105); } /* slate-600 */

/* Glow on dark, shadow on light */
.glow-shadow {
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}
.dark .glow-shadow {
    box-shadow: 0 0 20px rgb(16 185 129 / 0.2);
}
"""

12. High Contrast — Smooth Transition System
Mevcut Problem
python"border_width": "border-2",
# Çok sert geçişler, harsh görünüm
Çözüm: Smooth High Contrast
python# frontend_presets.py - High Contrast Enhancement

def create_high_contrast_theme(
    softness_level: Literal["sharp", "balanced", "smooth"] = "balanced",
    color_scheme: Literal["blue", "purple", "green", "neutral"] = "blue",
    animation_preference: Literal["full", "reduced", "none"] = "reduced",
) -> Dict[str, Any]:
    """
    WCAG AAA compliant theme with adjustable visual softness.
    
    High contrast doesn't have to mean harsh. This theme maintains
    7:1+ contrast ratios while offering visual comfort options.
    """
    
    # Softness affects border radius and transitions
    softness_settings = {
        "sharp": {
            "radius": "rounded-none",
            "transition": "transition-none",
            "shadow": "shadow-none",
            "border_style": "border-2",
        },
        "balanced": {
            "radius": "rounded-md",
            "transition": "transition-colors duration-150",
            "shadow": "shadow-sm",
            "border_style": "border-2",
        },
        "smooth": {
            "radius": "rounded-lg",
            "transition": "transition-all duration-200 ease-out",
            "shadow": "shadow-md",
            "border_style": "border",
        },
    }
    
    soft = softness_settings[softness_level]
    
    # Color schemes with 7:1+ contrast guaranteed
    schemes = {
        "blue": {
            "primary": "blue-800",
            "primary_hover": "blue-900",
            "focus_ring": "blue-600",
            "link": "blue-700",
            "link_visited": "purple-800",
        },
        "purple": {
            "primary": "purple-800",
            "primary_hover": "purple-900",
            "focus_ring": "purple-600",
            "link": "purple-700",
            "link_visited": "fuchsia-800",
        },
        "green": {
            "primary": "emerald-800",
            "primary_hover": "emerald-900",
            "focus_ring": "emerald-600",
            "link": "emerald-700",
            "link_visited": "teal-800",
        },
        "neutral": {
            "primary": "slate-800",
            "primary_hover": "slate-900",
            "focus_ring": "slate-600",
            "link": "slate-900",
            "link_visited": "slate-700",
        },
    }
    
    colors = schemes[color_scheme]
    
    # Animation handling
    animation_css = {
        "full": "",
        "reduced": "@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }",
        "none": "*, *::before, *::after { animation: none !important; transition: none !important; }",
    }
    
    theme = {
        "name": f"high-contrast-{color_scheme}-{softness_level}",
        "description": f"WCAG AAA theme ({softness_level} style)",
        
        # Colors with 7:1+ contrast
        "primary": colors["primary"],
        "primary_hover": colors["primary_hover"],
        "secondary": "slate-700",
        
        # Maximum contrast backgrounds
        "background": "white",
        "background_dark": "black",
        "surface": "slate-50",
        "surface_dark": "slate-950",
        
        # Text colors
        "text": "black",
        "text_dark": "white",
        "text_muted": "slate-700",  # 4.5:1 on white
        "text_muted_dark": "slate-300",  # 7:1 on black
        
        # Borders (always visible)
        "border": "slate-900",
        "border_dark": "white",
        "border_width": soft["border_style"],
        "border_radius": soft["radius"],
        
        # Focus indicators (extra prominent)
        "focus_ring": f"ring-4 ring-{colors['focus_ring']} ring-offset-2",
        "focus_ring_dark": f"ring-4 ring-{colors['focus_ring'].replace('-600', '-400')} ring-offset-2 ring-offset-black",
        
        # Links (underlined by default)
        "link_color": colors["link"],
        "link_visited": colors["link_visited"],
        "link_decoration": "underline underline-offset-4 decoration-2",
        
        # Shadows
        "shadow": soft["shadow"],
        "shadow_hover": "shadow-lg" if softness_level != "sharp" else "shadow-none",
        
        # Transitions
        "transition": soft["transition"],
        
        # Components
        "button_primary": f"""
            bg-{colors['primary']} hover:bg-{colors['primary_hover']}
            text-white font-semibold
            px-6 py-3 {soft['radius']} {soft['border_style']} border-black
            {soft['transition']}
            focus:outline-none {theme.get('focus_ring', '')}
        """,
        
        "button_secondary": f"""
            bg-white hover:bg-slate-100
            text-black font-semibold
            px-6 py-3 {soft['radius']} {soft['border_style']} border-black
            {soft['transition']}
            focus:outline-none focus:ring-4 focus:ring-{colors['focus_ring']} focus:ring-offset-2
        """,
        
        "input_accessible": f"""
            bg-white text-black
            {soft['radius']} {soft['border_style']} border-black
            px-4 py-3
            focus:outline-none focus:ring-4 focus:ring-{colors['focus_ring']} focus:ring-offset-2
            placeholder:text-slate-600
            {soft['transition']}
        """,
        
        # Link styling
        "link_classes": f"""
            text-{colors['link']} visited:text-{colors['link_visited']}
            underline underline-offset-4 decoration-2
            hover:decoration-4
            focus:outline-none focus:ring-2 focus:ring-{colors['focus_ring']} focus:rounded
            {soft['transition']}
        """,
        
        # Reduced motion CSS
        "_animation_css": animation_css[animation_preference],
        
        # WCAG metadata
        "_wcag_level": "AAA",
        "_min_contrast_ratio": 7.0,
        "_supports_reduced_motion": True,
    }
    
    return theme


HIGH_CONTRAST_UTILITIES = """
/* High Contrast Utilities */

/* Skip link for keyboard users */
.skip-link {
    position: absolute;
    top: -100%;
    left: 0;
    padding: 1rem;
    background: white;
    border: 2px solid black;
    z-index: 9999;
}
.skip-link:focus {
    top: 0;
}

/* Focus visible only for keyboard */
:focus:not(:focus-visible) {
    outline: none;
    ring: none;
}
:focus-visible {
    outline: 4px solid currentColor;
    outline-offset: 2px;
}

/* Forced colors mode support */
@media (forced-colors: active) {
    .btn {
        border: 2px solid currentColor;
    }
    .card {
        border: 2px solid currentColor;
    }
}

/* Ensure minimum touch target size */
button, a, input, select, textarea {
    min-height: 44px;
    min-width: 44px;
}
"""

13. Nature — Seasonal Variants
Mevcut Problem
python# Sadece tek bir nature stili var
"primary": "emerald-600",
Çözüm: Four Seasons System
python# frontend_presets.py - Nature Theme Enhancement

NATURE_SEASONS = {
    "spring": {
        "name": "İlkbahar",
        "mood": "Fresh, renewal, growth",
        "primary": "lime-500",
        "secondary": "emerald-500",
        "accent": "pink-400",
        "background": "lime-50",
        "surface": "white",
        "text": "emerald-900",
        "flora": ["cherry blossom", "tulips", "new leaves"],
        "palette_inspiration": "Cherry blossoms, fresh grass, morning dew",
    },
    "summer": {
        "name": "Yaz",
        "mood": "Vibrant, warm, energetic",
        "primary": "amber-500",
        "secondary": "orange-500",
        "accent": "sky-400",
        "background": "amber-50",
        "surface": "white",
        "text": "stone-900",
        "flora": ["sunflowers", "tropical leaves", "citrus"],
        "palette_inspiration": "Sunflowers, golden hour, ocean",
    },
    "autumn": {
        "name": "Sonbahar",
        "mood": "Warm, cozy, harvest",
        "primary": "orange-600",
        "secondary": "red-600",
        "accent": "amber-400",
        "background": "orange-50",
        "surface": "white",
        "text": "stone-900",
        "flora": ["maple leaves", "pumpkins", "wheat"],
        "palette_inspiration": "Fall foliage, harvest, warm earth",
    },
    "winter": {
        "name": "Kış",
        "mood": "Cool, serene, minimal",
        "primary": "slate-600",
        "secondary": "sky-400",
        "accent": "red-500",
        "background": "slate-50",
        "surface": "white",
        "text": "slate-900",
        "flora": ["pine", "holly", "frost"],
        "palette_inspiration": "Snow, evergreens, cozy interiors",
    },
}

NATURE_ELEMENTS = {
    "leaf_pattern": {
        "css": """
        .leaf-pattern {
            background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0c5 10 5 20 0 30s-5 20 0 30' stroke='%2322c55e' stroke-width='1' fill='none' opacity='0.1'/%3E%3C/svg%3E");
            background-size: 60px 60px;
        }
        """,
        "tailwind": "bg-[url('...')] bg-repeat",
    },
    "wave_pattern": {
        "tailwind": "bg-[url(\"data:image/svg+xml,...\")]",
    },
    "organic_blob": {
        "tailwind": "rounded-[30%_70%_70%_30%/30%_30%_70%_70%]",
    },
}


def create_nature_theme(
    season: Literal["spring", "summer", "autumn", "winter"] = "spring",
    organic_shapes: bool = True,
    include_patterns: bool = False,
    eco_friendly_mode: bool = False,  # Reduces visual complexity for sustainability
) -> Dict[str, Any]:
    """
    Nature-inspired theme with seasonal variations.
    
    Each season has its own carefully curated color palette
    inspired by real-world natural phenomena.
    """
    
    s = NATURE_SEASONS[season]
    
    # Organic vs geometric
    if organic_shapes:
        radius = "rounded-[30%_70%_70%_30%/30%_30%_70%_70%]"  # Blob shape
        radius_subtle = "rounded-3xl"
        radius_button = "rounded-full"
    else:
        radius = "rounded-xl"
        radius_subtle = "rounded-lg"
        radius_button = "rounded-lg"
    
    theme = {
        "name": f"nature-{season}",
        "description": f"{s['name']} - {s['mood']}",
        "palette_inspiration": s["palette_inspiration"],
        
        # Season colors
        "primary": s["primary"],
        "primary_hover": s["primary"].replace("-500", "-600").replace("-600", "-700"),
        "secondary": s["secondary"],
        "accent": s["accent"],
        
        # Backgrounds
        "background": s["background"],
        "background_dark": "stone-900",
        "surface": s["surface"],
        "surface_dark": "stone-800",
        
        # Text
        "text": s["text"],
        "text_dark": "stone-100",
        "text_muted": s["text"].replace("-900", "-600"),
        
        # Organic styling
        "border": s["primary"].replace("-500", "-200").replace("-600", "-200"),
        "border_radius": radius_subtle,
        "border_radius_organic": radius,
        "border_radius_button": radius_button,
        
        # Shadows (soft, natural)
        "shadow": f"shadow-lg shadow-{s['primary'].split('-')[0]}-500/10",
        "shadow_hover": f"shadow-xl shadow-{s['primary'].split('-')[0]}-500/20",
        
        # Font
        "font": "font-sans",
        
        # Organic button
        "button_organic": f"""
            bg-{s['primary']} hover:bg-{s['primary'].replace('-500', '-600')}
            text-white font-medium
            px-8 py-3 {radius_button}
            shadow-lg shadow-{s['primary'].split('-')[0]}-500/30
            hover:shadow-xl
            hover:-translate-y-0.5
            transition-all duration-300
        """,
        
        # Card with organic shape
        "card_organic": f"""
            bg-{s['surface']} dark:bg-stone-800
            {radius_subtle}
            shadow-lg shadow-{s['primary'].split('-')[0]}-500/5
            border border-{s['primary'].split('-')[0]}-100
            overflow-hidden
        """,
        
        # Decorative blob
        "decorative_blob": f"""
            absolute -z-10
            w-96 h-96
            bg-{s['primary']}/10
            {radius}
            blur-3xl
        """,
        
        # Season metadata
        "_season": season,
        "_flora": s["flora"],
    }
    
    # Eco-friendly mode: simpler visuals = less rendering = less energy
    if eco_friendly_mode:
        theme["shadow"] = "shadow-sm"
        theme["shadow_hover"] = "shadow-md"
        theme["border_radius"] = "rounded-lg"
        theme["_decorative_blob"] = ""  # Remove decorative elements
        theme["_eco_note"] = "Simplified visuals for reduced energy consumption"
    
    # Optional patterns
    if include_patterns:
        theme["_pattern_css"] = NATURE_ELEMENTS["leaf_pattern"]["css"]
    
    return theme


# Seasonal color palette reference
SEASONAL_PALETTES = """
## Seasonal Color Inspiration

### 🌸 Spring (İlkbahar)
- Primary: Fresh lime/yellow-green (#84cc16)
- Secondary: Young emerald (#10b981)
- Accent: Cherry blossom pink (#f472b6)
- Feeling: Renewal, freshness, hope

### ☀️ Summer (Yaz)
- Primary: Warm amber (#f59e0b)
- Secondary: Vibrant orange (#f97316)
- Accent: Ocean sky blue (#38bdf8)
- Feeling: Energy, warmth, adventure

### 🍂 Autumn (Sonbahar)
- Primary: Rich orange (#ea580c)
- Secondary: Deep red (#dc2626)
- Accent: Golden amber (#fbbf24)
- Feeling: Harvest, coziness, warmth

### ❄️ Winter (Kış)
- Primary: Cool slate (#475569)
- Secondary: Icy sky blue (#38bdf8)
- Accent: Holly berry red (#ef4444)
- Feeling: Serenity, minimalism, rest
"""

14. Startup — Differentiation Strategy
Mevcut Problem
python# Diğer temalardan yetersiz farklılaşma
"primary": "indigo-600",  # Modern-minimal ile aynı
Çözüm: Startup Identity Kit
python# frontend_presets.py - Startup Theme Enhancement

STARTUP_ARCHETYPES = {
    "disruptor": {
        "name": "Disruptor",
        "tagline": "Challenge the status quo",
        "primary": "violet-600",
        "secondary": "fuchsia-500",
        "accent": "lime-400",
        "personality": ["bold", "unconventional", "energetic"],
        "gradient": "from-violet-600 via-fuchsia-500 to-pink-500",
        "typography": "sharp, modern, impactful",
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
        "typography": "clean, authoritative",
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
        "typography": "rounded, warm",
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
        "typography": "precise, modern",
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
        "typography": "friendly, clear",
        "motion": "calm, reassuring",
    },
    "ai_ml": {
        "name": "AI/ML Startup",
        "tagline": "Intelligence amplified",
        "primary": "purple-600",
        "secondary": "blue-500",
        "accent": "cyan-400",
        "personality": ["cutting-edge", "intelligent", "futuristic"],
        "gradient": "from-purple-600 via-blue-500 to-cyan-400",
        "typography": "geometric, tech",
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
        "typography": "organic, approachable",
        "motion": "flowing, natural",
    },
}

STARTUP_COMPONENTS = {
    "hero_cta": {
        "disruptor": "Gradient button with arrow, bold text",
        "enterprise": "Solid button with subtle shadow",
        "consumer": "Rounded pill button with icon",
    },
    "pricing_badge": {
        "disruptor": "Tilted badge with gradient border",
        "enterprise": "Subtle badge with checkmark",
        "consumer": "Colorful badge with emoji",
    },
}


def create_startup_theme(
    archetype: Literal["disruptor", "enterprise", "consumer", "fintech", "healthtech", "ai_ml", "sustainability"] = "disruptor",
    stage: Literal["seed", "growth", "scale"] = "growth",
    enable_motion: bool = True,
) -> Dict[str, Any]:
    """
    Startup-specific theme with archetype-based differentiation.
    
    Each archetype has a distinct visual identity that communicates
    the startup's positioning and values.
    """
    
    arch = STARTUP_ARCHETYPES[archetype]
    
    # Stage affects visual maturity
    stage_settings = {
        "seed": {
            "boldness": "high",  # Stand out more
            "animation": "playful",
            "shadow_intensity": "lg",
        },
        "growth": {
            "boldness": "medium",
            "animation": "balanced",
            "shadow_intensity": "md",
        },
        "scale": {
            "boldness": "refined",  # More mature look
            "animation": "subtle",
            "shadow_intensity": "sm",
        },
    }
    
    stg = stage_settings[stage]
    
    # Motion settings by personality
    motion_styles = {
        "dynamic, fast": "transition-all duration-200",
        "subtle, professional": "transition-all duration-300 ease-out",
        "bouncy, fun": "transition-all duration-300 ease-[cubic-bezier(0.68,-0.55,0.265,1.55)]",
        "smooth, confident": "transition-all duration-400 ease-out",
        "calm, reassuring": "transition-all duration-500 ease-out",
        "algorithmic, precise": "transition-all duration-150 ease-linear",
        "flowing, natural": "transition-all duration-600 ease-in-out",
    }
    
    motion = motion_styles.get(arch["motion"], "transition-all duration-300")
    
    theme = {
        "name": f"startup-{archetype}-{stage}",
        "description": f"{arch['name']} - {arch['tagline']}",
        "personality": arch["personality"],
        
        # Core colors
        "primary": arch["primary"],
        "primary_hover": arch["primary"].replace("-600", "-700").replace("-500", "-600"),
        "secondary": arch["secondary"],
        "accent": arch["accent"],
        
        # Gradient
        "gradient_primary": f"bg-gradient-to-r {arch['gradient']}",
        "gradient_text": f"bg-gradient-to-r {arch['gradient']} bg-clip-text text-transparent",
        
        # Backgrounds
        "background": "white",
        "background_dark": "slate-950",
        "surface": "slate-50",
        "surface_dark": "slate-900",
        
        # Text
        "text": "slate-900",
        "text_dark": "white",
        "text_muted": "slate-500",
        
        # Style
        "border": "slate-200",
        "border_radius": "rounded-xl",
        "shadow": f"shadow-{stg['shadow_intensity']}",
        "shadow_hover": f"shadow-{_next_shadow(stg['shadow_intensity'])}",
        
        # Motion
        "transition": motion if enable_motion else "transition-none",
        
        # Hero CTA (distinctive)
        "hero_cta": _generate_hero_cta(archetype, arch, stg),
        
        # Signature button
        "button_signature": _generate_signature_button(archetype, arch, motion),
        
        # Badge style
        "badge_style": _generate_badge_style(archetype, arch),
        
        # Feature card
        "feature_card": f"""
            bg-white dark:bg-slate-800
            rounded-2xl p-6
            border border-slate-100 dark:border-slate-700
            shadow-{stg['shadow_intensity']} hover:shadow-{_next_shadow(stg['shadow_intensity'])}
            {motion}
            group
        """,
        
        # Startup-specific elements
        "product_hunt_badge": f"bg-{arch['accent']} text-white px-4 py-1 rounded-full text-sm font-medium",
        "beta_badge": f"bg-{arch['primary']}/10 text-{arch['primary']} px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider",
        
        # Metadata
        "_archetype": archetype,
        "_stage": stage,
        "_personality": arch["personality"],
    }
    
    return theme


def _generate_hero_cta(archetype: str, arch: dict, stage: dict) -> str:
    """Generate archetype-specific hero CTA"""
    
    if archetype == "disruptor":
        return f"""
            bg-gradient-to-r {arch['gradient']}
            text-white font-bold text-lg
            px-8 py-4 rounded-xl
            shadow-lg shadow-{arch['primary'].split('-')[0]}-500/30
            hover:shadow-xl hover:shadow-{arch['primary'].split('-')[0]}-500/40
            hover:-translate-y-1
            active:translate-y-0
            transition-all duration-200
            group
        """
    elif archetype == "enterprise":
        return f"""
            bg-{arch['primary']} hover:bg-{arch['primary'].replace('-700', '-800')}
            text-white font-semibold text-lg
            px-8 py-4 rounded-lg
            shadow-md hover:shadow-lg
            transition-all duration-300
        """
    elif archetype == "consumer":
        return f"""
            bg-gradient-to-r {arch['gradient']}
            text-white font-bold text-lg
            px-10 py-4 rounded-full
            shadow-lg hover:shadow-xl
            hover:scale-105
            active:scale-95
            transition-all duration-200
        """
    else:
        return f"""
            bg-{arch['primary']} hover:bg-{arch['primary'].replace('-600', '-700')}
            text-white font-semibold
            px-8 py-4 rounded-xl
            shadow-md hover:shadow-lg
            transition-all duration-300
        """


def _generate_signature_button(archetype: str, arch: dict, motion: str) -> str:
    """Generate archetype-specific button"""
    
    base = f"font-medium px-6 py-3 {motion}"
    
    styles = {
        "disruptor": f"{base} bg-gradient-to-r {arch['gradient']} text-white rounded-lg shadow-lg hover:shadow-xl hover:-translate-y-0.5",
        "enterprise": f"{base} bg-{arch['primary']} text-white rounded-md shadow hover:shadow-md",
        "consumer": f"{base} bg-{arch['primary']} text-white rounded-full shadow-md hover:shadow-lg hover:scale-[1.02]",
        "fintech": f"{base} bg-{arch['primary']} text-white rounded-lg shadow hover:shadow-md border border-{arch['primary'].replace('-600', '-700')}",
        "healthtech": f"{base} bg-{arch['primary']} text-white rounded-xl shadow hover:shadow-md",
        "ai_ml": f"{base} bg-gradient-to-r {arch['gradient']} text-white rounded-lg shadow-lg hover:shadow-xl",
        "sustainability": f"{base} bg-{arch['primary']} text-white rounded-full shadow hover:shadow-md",
    }
    
    return styles.get(archetype, styles["enterprise"])


def _generate_badge_style(archetype: str, arch: dict) -> str:
    """Generate archetype-specific badge"""
    
    styles = {
        "disruptor": f"bg-gradient-to-r {arch['gradient']} text-white px-4 py-1 rounded-full text-sm font-bold uppercase tracking-wider -rotate-2",
        "enterprise": f"bg-{arch['accent']}/10 text-{arch['accent'].replace('-500', '-700')} px-3 py-1 rounded-md text-sm font-medium",
        "consumer": f"bg-{arch['accent']} text-white px-4 py-1 rounded-full text-sm font-medium",
        "fintech": f"bg-{arch['primary']}/10 text-{arch['primary']} px-3 py-1 rounded text-xs font-semibold uppercase tracking-wider border border-{arch['primary']}/20",
        "healthtech": f"bg-{arch['accent']}/10 text-{arch['accent'].replace('-400', '-600')} px-3 py-1 rounded-full text-sm font-medium",
        "ai_ml": f"bg-gradient-to-r {arch['gradient']} text-white px-4 py-1 rounded-md text-sm font-medium",
        "sustainability": f"bg-{arch['primary']}/10 text-{arch['primary']} px-4 py-1 rounded-full text-sm font-medium border border-{arch['primary']}/20",
    }
    
    return styles.get(archetype, styles["enterprise"])

📊 Özet: Tema İyileştirme Matrisi
TemaAna SorunÇözüm YaklaşımıÖncelikModern-MinimalStatic colorsDynamic Theme Factory🔴 P0BrutalistContrast issuesWCAG validation system🔴 P0GlassmorphismSafari compatProgressive enhancement🟠 P1Neo-BrutalismNo animationGradient animation library🟠 P1Soft-UIDark mode brokenDual-mode shadow calculator🔴 P0CorporateToo genericIndustry-specific variants🟡 P2GradientFew presetsComprehensive gradient library🟠 P1CyberpunkFixed glowIntensity control system🟡 P2RetroNo font pairingCurated font pairing library🟡 P2PastelLow contrastWCAG-safe pastel pairs🔴 P0Dark Mode FirstWeak light modeBalanced dual-mode system🟡 P2High ContrastHarsh visualsSoftness level options🟠 P1NatureSingle variantFour seasons system🟢 P3StartupNo differentiationArchetype-based identity🟡 P2