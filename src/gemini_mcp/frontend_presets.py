"""Frontend design presets and system prompts for Gemini 3 Pro.

This module contains:
- Component type presets (Atomic Design levels)
- Theme presets (visual styles)
- System prompt for Gemini to generate high-quality TailwindCSS/HTML
"""

from typing import Any, Dict, List

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

## OUTPUT QUALITY OPTIMIZATION

### Token Allocation Strategy
You MUST produce detailed, comprehensive output that approaches your token limits.
However, use tokens WISELY - quality over repetition.

### Smart Content Generation Rules:
1. **Tables**: Use 3-5 representative rows, NOT 20 identical rows
   - BAD: 20 table rows with same pattern (wastes tokens)
   - GOOD: 3 unique rows + clear pattern indication

2. **Lists**: Show variety, not quantity
   - BAD: 15 similar list items to fill space
   - GOOD: 5 diverse items with rich detail

3. **Detail Depth**: Spend tokens on:
   - Subtle hover states and micro-interactions
   - Thoughtful spacing and visual hierarchy
   - Accessibility attributes (aria-labels, roles)
   - Responsive breakpoint considerations
   - Color variations for different states
   - Border styles, shadows, gradients
   - Typography refinements (line-height, letter-spacing)

4. **Think Deeply About**:
   - Edge cases (empty states, loading states, error states)
   - Visual balance and white space
   - Touch target sizes for mobile
   - Focus indicators for keyboard navigation
   - Animation timing and easing functions

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
