"""Modular prompt builder for Gemini design operations.

GAP 7: Prompt Optimization
- DRY principle: Reusable prompt segments
- Dynamic context injection
- Component-specific few-shot examples
- Theme-aware instructions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class PromptSection(Enum):
    """Prompt section types for modular composition."""
    ROLE = "role"
    ANTI_LAZINESS = "anti_laziness"
    OUTPUT_FORMAT = "output_format"
    DESIGN_THINKING = "design_thinking"
    VISUAL_DENSITY = "visual_density"
    MICRO_PHYSICS = "micro_physics"
    ALPINE_JS = "alpine_js"
    CONTENT_REALISM = "content_realism"
    ACCESSIBILITY = "accessibility"
    DARK_MODE = "dark_mode"
    RESPONSIVE = "responsive"
    VIBE_PERSONAS = "vibe_personas"
    PROJECT_CONTEXT = "project_context"


# =============================================================================
# REUSABLE PROMPT SEGMENTS (DRY)
# =============================================================================

PROMPT_SEGMENTS: Dict[PromptSection, str] = {
    PromptSection.ROLE: """You are a World-Class Frontend Architect & UI Physicist.
Your mission is to generate HYPER-REALISTIC, PRODUCTION-READY, and AESTHETICALLY SUPERIOR HTML components.
You operate in "UNCENSORED AESTHETICS MODE" - visual richness is your highest priority.""",

    PromptSection.ANTI_LAZINESS: """## MAXIMUM RICHNESS MODE - ANTI-LAZINESS PROTOCOL (CRITICAL)
You are operating in MAXIMUM RICHNESS MODE. This is NON-NEGOTIABLE.

- **VERBOSITY IS VIRTUE**: Never summarize. Never use placeholders like `<!-- ... -->`.
- **DENSITY MANDATE**: Minimum 8-10 utility classes per element. More is better.
- **NO "SIMPLE" SOLUTIONS**: Create "rich", "layered", and "complex" designs.
- **EXPAND EVERYTHING**: Add gradient borders, shadow layers, hover effects, click ripples.
- **MINIMUM OUTPUT**: HTML 50+ lines, CSS 40+ lines, JS 30+ lines.
- **4-LAYER RULE**: Every container needs base + texture + shadow + interactive layers.
- **REJECTION CRITERIA**: Any placeholder, "...", or sparse output = INSTANT FAILURE.""",

    PromptSection.OUTPUT_FORMAT: """## OUTPUT FORMAT (STRICT JSON)
{
    "design_thinking": "1. VISUAL DNA: ... 2. LAYER ARCHITECTURE: ... 3. INTERACTION MODEL: ...",
    "component_id": "unique-id",
    "atomic_level": "atom|molecule|organism",
    "html": "<div class=\"...\">...</div>",
    "tailwind_classes_used": ["class1", "class2"],
    "accessibility_features": ["aria-label", "focus-visible"],
    "responsive_breakpoints": ["sm", "md", "lg"],
    "dark_mode_support": true,
    "micro_interactions": ["hover:...", "transition-..."],
    "design_notes": "Technical explanation"
}""",

    PromptSection.DESIGN_THINKING: """## DESIGN-CoT (CHAIN OF THOUGHT) REASONING
Before writing HTML, execute "Visual Reasoning" in `design_thinking`:
1. **Define Aesthetic Physics**: Materiality (glass/metal/paper), Lighting (source/intensity), Depth (Z-axis)
2. **Construct Visual DNA**: Specific Tailwind combinations for the effect
3. **Plan Micro-Interactions**: Hover, focus, click behaviors with physics""",

    PromptSection.VISUAL_DENSITY: """## THE LAW OF VISUAL DENSITY
"Good design is dense. Great design is infinitely detailed."

### The "4-Layer Rule" for containers:
1. Base Gradient layer
2. Mesh Gradients / Animated Blobs (2+ blobs)
3. Texture/Noise/Grid Overlay
4. Surface Polish (Glass/Highlight on hover)

### Compound Shadow Rule:
Never single shadow. Combine: `shadow-xl shadow-black/20 ring-1 ring-white/10`

### Inner Light & Edge Highlights:
`ring-1 ring-white/20 ring-inset` or multi-border technique.""",

    PromptSection.MICRO_PHYSICS: """## MICRO-INTERACTION PHYSICS
Animations must feel ORGANIC, not mechanical.
- **Easing**: `ease-[cubic-bezier(0.34,1.56,0.64,1)]` for bouncy feels
- **Duration**: `duration-300` to `duration-500` sweet spot
- **Staging**: Animate children with delays (`group-hover` + `delay-75`)""",

    PromptSection.ALPINE_JS: """## ALPINE.JS INTERACTIVITY (MANDATORY)
- **State**: `x-data="{ open: false, active: 1, search: '' }"`
- **Transitions**: COMPLETE enter/leave attributes required
- **Logic**: Tabs, modals, dropdowns MUST work""",

    PromptSection.CONTENT_REALISM: """## CONTENT REALISM
- **Language**: {language} (high quality, professional)
- **Data**: Realistic names, prices, dates
- **Tone**: Professional, trustworthy, modern""",

    PromptSection.ACCESSIBILITY: """## ACCESSIBILITY (WCAG AA)
- `focus-visible:ring-2` on all interactive elements
- `aria-label` on icon buttons
- Semantic HTML (nav, main, article, button)
- Color contrast 4.5:1 minimum""",

    PromptSection.DARK_MODE: """## DARK MODE (MANDATORY)
Every color class needs `dark:` variant:
- `bg-white dark:bg-slate-900`
- `text-slate-900 dark:text-white`
- `border-slate-200 dark:border-slate-800`""",

    PromptSection.RESPONSIVE: """## RESPONSIVE DESIGN
- Mobile-first approach (base classes for mobile)
- Breakpoints: `sm:`, `md:`, `lg:`, `xl:`
- Touch targets: minimum 44x44px
- Typography scaling: `text-base md:text-lg lg:text-xl`""",

    PromptSection.VIBE_PERSONAS: """## VIBE-PERSONAS
Available vibes for design personality:

### Core Vibes
- **elite_corporate**: Ultra-precision, luxury, CFO-level polish
- **playful_funny**: Bouncy physics, Neo-Brutalism, emoji-friendly
- **cyberpunk_edge**: High contrast, neon on black, glitch effects
- **luxury_editorial**: Haute couture, wide whitespace, serif typography

### Enterprise Vibes (Anti-AI-Cliche, Data-Dense)
- **swiss_precision**: International Typographic Style - strict 8px grid, black/white/one-accent, max 4px radius
- **sap_fiori**: SAP business design - #0070F2 blue, flat cards, 32px row height, semantic colors
- **ibm_carbon**: IBM Carbon system - 16-column grid, gray 100 scale, productive motion (70-150ms)""",

    PromptSection.PROJECT_CONTEXT: """## PROJECT CONTEXT
{project_context}""",
}


# =============================================================================
# COMPONENT-SPECIFIC INSTRUCTIONS
# =============================================================================

COMPONENT_INSTRUCTIONS: Dict[str, str] = {
    "button": """### BUTTON SPECIFICS
- Gradient border with `bg-gradient-to-r` wrapper technique
- Inner ring for glass edge: `ring-1 ring-white/20 ring-inset`
- Click effect: `active:scale-[0.97]`
- Loading state with spinner SVG""",

    "card": """### CARD SPECIFICS
- Apply 4-Layer Rule for background
- Hover lift: `hover:-translate-y-1 hover:shadow-2xl`
- Border glow on hover: `hover:ring-2 hover:ring-primary/50`
- Image with `aspect-video` and `object-cover`""",

    "navbar": """### NAVBAR SPECIFICS
- Sticky with backdrop blur: `sticky top-0 backdrop-blur-xl bg-white/80 dark:bg-slate-900/80`
- Logo + nav links + CTA button layout
- Mobile hamburger with Alpine.js toggle
- Active state indicator with animated underline""",

    "hero": """### HERO SPECIFICS
- Full viewport: `min-h-screen` or `min-h-[80vh]`
- Animated gradient background
- Headline with gradient text: `bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent`
- CTA buttons with hover animations
- Optional floating elements/testimonials""",

    "modal": """### MODAL SPECIFICS
- Backdrop: `fixed inset-0 bg-black/50 backdrop-blur-sm`
- Panel: centered, max-width, rounded-2xl
- Close button: absolute positioned, hover:rotate
- Alpine.js: x-show with transitions
- Focus trap: first focusable element on open""",

    "dropdown": """### DROPDOWN SPECIFICS
- Trigger button with chevron icon (rotates on open)
- Panel: absolute, shadow-2xl, rounded-xl
- Alpine.js: @click.away to close
- Transition: scale-95 -> scale-100
- Items with hover background""",

    "form": """### FORM SPECIFICS
- Labels: `font-medium text-sm text-slate-700 dark:text-slate-300`
- Inputs: `rounded-lg border-slate-300 focus:ring-2 focus:ring-primary focus:border-primary`
- Validation: red ring on error, green on success
- Submit button: full width, loading state""",

    "pricing": """### PRICING CARD SPECIFICS
- Popular tier: highlighted with ring and badge
- Price: large with /mo or /yıl suffix
- Features: checkmark list with icons
- CTA: full-width button at bottom
- Hover: slight lift and shadow increase""",

    "footer": """### FOOTER SPECIFICS
- Multi-column layout: 4 columns on desktop
- Links grouped by category
- Social icons row
- Copyright + legal links at bottom
- Newsletter signup optional""",

    "testimonial": """### TESTIMONIAL SPECIFICS
- Avatar with ring border
- Quote with large opening quotation mark
- Name + title + company
- Star rating if applicable
- Card with subtle background""",
}


# =============================================================================
# THEME-SPECIFIC INSTRUCTIONS
# =============================================================================

THEME_INSTRUCTIONS: Dict[str, str] = {
    "modern-minimal": """### MODERN-MINIMAL THEME
- Clean lines, ample whitespace
- Primary: blue-600, Neutral: slate
- Shadows: subtle, blur-heavy
- Borders: 1px slate-200/slate-800""",

    "brutalist": """### BRUTALIST THEME
- High contrast: black/white base
- Sharp corners (rounded-none)
- Bold borders: 2-4px solid black
- Offset shadows: `shadow-[4px_4px_0px_#000]`""",

    "glassmorphism": """### GLASSMORPHISM THEME
- Background: `bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl`
- Borders: `border border-white/20`
- Shadows: `shadow-xl shadow-black/10`
- Inner ring: `ring-1 ring-white/20 ring-inset`""",

    "neo-brutalism": """### NEO-BRUTALISM THEME
- Bright colors: yellow-400, pink-500, cyan-400
- Offset shadows: `shadow-[8px_8px_0px_#000]`
- Thick borders: 3-4px
- Bouncy hover animations""",

    "cyberpunk": """### CYBERPUNK THEME
- Dark base: slate-950, black
- Neon accents: cyan-400, fuchsia-500, yellow-400
- Glow effects: `shadow-[0_0_20px_var(--neon-color)]`
- Scanline overlays""",

    "corporate": """### CORPORATE THEME
- Professional palette: slate, blue, emerald
- Subtle gradients
- Conservative shadows
- Clear hierarchy""",

    "gradient": """### GRADIENT THEME
- Gradient backgrounds everywhere
- Text gradients: `bg-gradient-to-r ... bg-clip-text text-transparent`
- Animated gradient borders
- Mesh gradient blobs""",
}


# =============================================================================
# PROMPT BUILDER CLASS
# =============================================================================

@dataclass
class PromptBuilder:
    """Modular prompt builder with fluent interface.

    Example:
        >>> prompt = (PromptBuilder()
        ...     .with_role()
        ...     .with_output_format()
        ...     .with_component("button")
        ...     .with_theme("glassmorphism")
        ...     .with_language("tr")
        ...     .with_project_context("E-commerce checkout")
        ...     .build())
    """

    sections: List[str] = field(default_factory=list)
    language: str = "Turkish"
    project_context: str = ""
    component_type: Optional[str] = None
    theme: Optional[str] = None
    few_shot_examples: List[str] = field(default_factory=list)
    custom_instructions: List[str] = field(default_factory=list)

    def with_role(self) -> "PromptBuilder":
        """Add role definition."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.ROLE])
        return self

    def with_anti_laziness(self) -> "PromptBuilder":
        """Add anti-laziness protocol."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.ANTI_LAZINESS])
        return self

    def with_output_format(self) -> "PromptBuilder":
        """Add output format specification."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.OUTPUT_FORMAT])
        return self

    def with_design_thinking(self) -> "PromptBuilder":
        """Add design thinking instructions."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.DESIGN_THINKING])
        return self

    def with_visual_density(self) -> "PromptBuilder":
        """Add visual density rules."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.VISUAL_DENSITY])
        return self

    def with_micro_physics(self) -> "PromptBuilder":
        """Add micro-interaction physics."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.MICRO_PHYSICS])
        return self

    def with_alpine_js(self) -> "PromptBuilder":
        """Add Alpine.js requirements."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.ALPINE_JS])
        return self

    def with_accessibility(self) -> "PromptBuilder":
        """Add accessibility requirements."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.ACCESSIBILITY])
        return self

    def with_dark_mode(self) -> "PromptBuilder":
        """Add dark mode requirements."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.DARK_MODE])
        return self

    def with_responsive(self) -> "PromptBuilder":
        """Add responsive design requirements."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.RESPONSIVE])
        return self

    def with_language(self, language: str = "tr") -> "PromptBuilder":
        """Set content language."""
        language_map = {
            "tr": "Turkish",
            "en": "English",
            "de": "German",
        }
        self.language = language_map.get(language, "Turkish")
        content_section = PROMPT_SEGMENTS[PromptSection.CONTENT_REALISM].replace(
            "{language}", self.language
        )
        self.sections.append(content_section)
        return self

    def with_project_context(self, context: str) -> "PromptBuilder":
        """Add project context."""
        self.project_context = context
        if context:
            context_section = PROMPT_SEGMENTS[PromptSection.PROJECT_CONTEXT].replace(
                "{project_context}", context
            )
            self.sections.append(context_section)
        return self

    def with_component(self, component_type: str) -> "PromptBuilder":
        """Add component-specific instructions."""
        self.component_type = component_type
        instruction = COMPONENT_INSTRUCTIONS.get(component_type.lower())
        if instruction:
            self.sections.append(instruction)
        return self

    def with_theme(self, theme: str) -> "PromptBuilder":
        """Add theme-specific instructions."""
        self.theme = theme
        instruction = THEME_INSTRUCTIONS.get(theme.lower())
        if instruction:
            self.sections.append(instruction)
        return self

    def with_few_shot(self, examples: List[str]) -> "PromptBuilder":
        """Add few-shot examples."""
        self.few_shot_examples = examples
        if examples:
            examples_section = "## EXAMPLES\n\n" + "\n\n---\n\n".join(examples)
            self.sections.append(examples_section)
        return self

    def with_custom(self, instruction: str) -> "PromptBuilder":
        """Add custom instruction."""
        self.custom_instructions.append(instruction)
        self.sections.append(instruction)
        return self

    def with_vibe_personas(self) -> "PromptBuilder":
        """Add vibe persona options."""
        self.sections.append(PROMPT_SEGMENTS[PromptSection.VIBE_PERSONAS])
        return self

    def with_full_design_system(self) -> "PromptBuilder":
        """Add all design system sections (convenience method)."""
        return (
            self.with_role()
            .with_anti_laziness()
            .with_output_format()
            .with_design_thinking()
            .with_visual_density()
            .with_micro_physics()
            .with_alpine_js()
            .with_accessibility()
            .with_dark_mode()
            .with_responsive()
        )

    def build(self) -> str:
        """Build the final prompt string."""
        return "\n\n".join(self.sections)

    def build_with_task(self, task_description: str) -> str:
        """Build prompt with a specific task appended."""
        base = self.build()
        return f"{base}\n\n## YOUR TASK\n{task_description}"


# =============================================================================
# PRESET BUILDERS
# =============================================================================

def build_component_prompt(
    component_type: str,
    theme: str = "modern-minimal",
    language: str = "tr",
    project_context: str = "",
    few_shot_examples: Optional[List[str]] = None,
) -> str:
    """Build a complete prompt for component design.

    Args:
        component_type: Type of component (button, card, navbar, etc.)
        theme: Theme preset name
        language: Content language code
        project_context: Project-specific context
        few_shot_examples: Optional examples to include

    Returns:
        Complete prompt string
    """
    builder = (
        PromptBuilder()
        .with_full_design_system()
        .with_component(component_type)
        .with_theme(theme)
        .with_language(language)
    )

    if project_context:
        builder.with_project_context(project_context)

    if few_shot_examples:
        builder.with_few_shot(few_shot_examples)

    return builder.build()


def build_section_prompt_modular(
    section_type: str,
    theme: str = "modern-minimal",
    language: str = "tr",
    previous_tokens: Optional[Dict[str, Any]] = None,
    project_context: str = "",
) -> str:
    """Build a prompt for section design with style consistency.

    Args:
        section_type: Type of section (hero, features, pricing, etc.)
        theme: Theme preset name
        language: Content language code
        previous_tokens: Design tokens from previous sections for consistency
        project_context: Project-specific context

    Returns:
        Complete prompt string
    """
    builder = (
        PromptBuilder()
        .with_full_design_system()
        .with_theme(theme)
        .with_language(language)
    )

    if project_context:
        builder.with_project_context(project_context)

    # Add consistency instructions if previous tokens exist
    if previous_tokens:
        consistency_section = f"""## STYLE CONSISTENCY (MANDATORY)
You MUST match these design tokens from previous sections:
- Colors: {previous_tokens.get('colors', {})}
- Typography: {previous_tokens.get('typography', {})}
- Spacing: {previous_tokens.get('spacing', {})}
- Effects: {previous_tokens.get('effects', {})}"""
        builder.with_custom(consistency_section)

    # Add section-specific instructions
    section_instruction = f"""## SECTION: {section_type.upper()}
Generate a complete {section_type} section with:
- Section markers: `<!-- SECTION: {section_type} -->` and `<!-- /SECTION: {section_type} -->`
- Full responsive layout
- Dark mode support
- Alpine.js interactivity where appropriate"""
    builder.with_custom(section_instruction)

    return builder.build()


def build_refinement_prompt_modular(
    previous_html: str,
    modifications: str,
    project_context: str = "",
) -> str:
    """Build a prompt for refining existing HTML.

    Args:
        previous_html: The existing HTML to refine
        modifications: Description of desired changes
        project_context: Project-specific context

    Returns:
        Complete refinement prompt
    """
    builder = (
        PromptBuilder()
        .with_role()
        .with_anti_laziness()
        .with_output_format()
        .with_visual_density()
        .with_micro_physics()
    )

    if project_context:
        builder.with_project_context(project_context)

    refinement_section = f"""## HYPER-ITERATION TASK

You are in **HYPER-ITERATION MODE**. Elevate the design to "Master Class" level.

### THE CRITIQUE
Before coding, internally critique the `previous_html`:
- **Density Check**: Is it too sparse? Add texture overlays or gradient borders.
- **Physics Check**: Do shadows feel heavy? Is the hover lift organic?
- **Aesthetic Check**: Does the color palette vibrate?

### DENSITY INJECTION (Mandatory)
Increase visual density by at least 20% compared to previous_html.

### INPUT
**Current HTML**:
```html
{previous_html}
```

**Requested Modifications**:
> {modifications}

### INSTRUCTIONS
1. Apply requested modifications precisely
2. Inject density: Add new visual details not requested but needed
3. Preserve structure, enhance styling
4. Maintain Alpine.js interactivity"""

    builder.with_custom(refinement_section)

    return builder.build()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_available_sections() -> List[str]:
    """Get list of available prompt sections."""
    return [s.value for s in PromptSection]


def get_component_types() -> List[str]:
    """Get list of components with specific instructions."""
    return list(COMPONENT_INSTRUCTIONS.keys())


def get_supported_themes() -> List[str]:
    """Get list of themes with specific instructions."""
    return list(THEME_INSTRUCTIONS.keys())


def estimate_prompt_tokens(prompt: str) -> int:
    """Rough estimate of token count for a prompt.

    Uses ~4 chars per token approximation.
    """
    return len(prompt) // 4


def build_design_prompt(
    component_type: str,
    context: str = "",
    theme: str = "modern-minimal",
    style_guide: str = "",
    content_structure: str = "{}",
    project_context: str = "",
    content_language: str = "tr",
) -> str:
    """Build a complete prompt for design_frontend tool.

    This function constructs the full prompt by combining:
    - Component type specification
    - Theme and style guide
    - Content structure (JSON)
    - Project context
    - Language configuration

    Args:
        component_type: Type of component (button, card, navbar, etc.)
        context: Usage context for the component
        theme: Theme preset name
        style_guide: Additional style guide text
        content_structure: JSON string with component content
        project_context: Project-specific context
        content_language: Content language code (tr, en, de)

    Returns:
        Complete prompt string for Gemini API
    """
    builder = (
        PromptBuilder()
        .with_full_design_system()
        .with_component(component_type)
        .with_theme(theme)
        .with_language(content_language)
    )

    if context:
        builder.with_project_context(f"Context: {context}")

    if project_context:
        builder.with_project_context(project_context)

    if style_guide:
        builder.with_project_context(f"Style Guide: {style_guide}")

    if content_structure and content_structure != "{}":
        builder.with_project_context(f"Content Structure: {content_structure}")

    return builder.build()
