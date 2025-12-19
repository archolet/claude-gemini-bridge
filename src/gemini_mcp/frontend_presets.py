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
