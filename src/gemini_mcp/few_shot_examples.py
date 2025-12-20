"""Few-shot examples for Gemini design prompts.

Provides high-quality example inputs and outputs to help Gemini
understand the expected format and quality of design responses.
"""

from typing import Dict, List, Any, Optional

# Example component designs with rich CSS/JS
COMPONENT_EXAMPLES: Dict[str, Dict[str, Any]] = {
    "button": {
        "input": {
            "component_type": "button",
            "context": "Primary CTA button for newsletter signup",
            "content_structure": {"text": "Subscribe Now", "icon": "mail"},
            "theme": "modern-minimal",
        },
        "output": {
            "design_thinking": "1. VISUAL DNA: High-impact CTA with material depth. Using complex shadow layering (colored shadow + standard shadow) to create a 'hovering' effect. 2. LAYER ARCHITECTURE: Gradient background with inner lightning (white/20 overlay) to simulate a polished surface. 3. INTERACTION MODEL: Magnetic lift effect (-translate-y-1) paired with shadow expansion for tactile feedback.",
            "component_id": "btn_newsletter_cta",
            "atomic_level": "atom",
            "html": """<button
  class="group relative inline-flex items-center justify-center gap-2 px-6 py-3
         bg-gradient-to-r from-blue-600 to-blue-700
         text-white font-medium rounded-lg
         shadow-lg shadow-blue-500/25
         hover:shadow-xl hover:shadow-blue-500/40
         hover:from-blue-500 hover:to-blue-600
         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
         active:scale-[0.98]
         transition-all duration-200 ease-out
         disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg"
  type="button"
  aria-label="Subscribe to newsletter"
>
  <!-- Icon with animation -->
  <svg
    class="w-5 h-5 transition-transform duration-200 group-hover:-translate-y-0.5"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>

  <!-- Text with subtle hover effect -->
  <span class="relative">
    Subscribe Now
    <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-white/50
                 transition-all duration-200 group-hover:w-full"></span>
  </span>

  <!-- Ripple effect container -->
  <span class="absolute inset-0 overflow-hidden rounded-lg">
    <span class="absolute inset-0 bg-white/10 scale-0 rounded-full
                 group-active:scale-100 transition-transform duration-300"></span>
  </span>
</button>""",
            "tailwind_classes_used": [
                "group", "relative", "inline-flex", "items-center", "justify-center",
                "gap-2", "px-6", "py-3", "bg-gradient-to-r", "from-blue-600", "to-blue-700",
                "text-white", "font-medium", "rounded-lg", "shadow-lg", "shadow-blue-500/25",
                "hover:shadow-xl", "hover:shadow-blue-500/40", "transition-all", "duration-200",
            ],
            "accessibility_features": [
                "aria-label for screen readers",
                "focus:ring for keyboard navigation",
                "disabled state styling",
                "sufficient color contrast",
            ],
            "dark_mode_support": True,
            "design_notes": "Premium button with gradient, shadow effects, and micro-interactions. Uses group hover for coordinated animations.",
        },
    },

    "hero": {
        "input": {
            "component_type": "hero",
            "context": "Landing page hero for a Turkish SaaS product",
            "content_structure": {
                "headline": "Isletmenizi Dijitallestirin",
                "subheadline": "Modern cozumlerle verimliligini artirin",
                "cta_primary": "Ucretsiz Deneyin",
                "cta_secondary": "Demo Izleyin",
            },
            "theme": "modern-minimal",
        },
        "output": {
            "design_thinking": "1. VISUAL DNA: Airy, expansive luxury SaaS aesthetic. Using 4-layer background (Gradient + Pulse Blobs + Grid + Noise) to create dense atmosphere. 2. TYPOGRAPHY PHYSICS: Heading uses 'tracking-tight' for authority and gradient clip for modernisation. 3. LAYOUT: Center-aligned for maximum focus, using 'staggered fade-in' for cinematic entrance.",
            "component_id": "hero_saas_landing",
            "atomic_level": "organism",
            "html": """<section class="relative min-h-[90vh] flex items-center overflow-hidden
                       bg-gradient-to-br from-slate-50 via-white to-blue-50
                       dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
  <!-- Animated background elements -->
  <div class="absolute inset-0 overflow-hidden pointer-events-none">
    <div class="absolute -top-40 -right-40 w-80 h-80 bg-blue-400/10 rounded-full blur-3xl
                animate-pulse" style="animation-duration: 4s;"></div>
    <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl
                animate-pulse" style="animation-duration: 6s; animation-delay: 1s;"></div>

    <!-- Grid pattern overlay -->
    <div class="absolute inset-0 bg-[linear-gradient(to_right,#8882_1px,transparent_1px),linear-gradient(to_bottom,#8882_1px,transparent_1px)]
                bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_110%)]"></div>
  </div>

  <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
    <div class="max-w-4xl mx-auto text-center">
      <!-- Badge -->
      <div class="inline-flex items-center gap-2 px-4 py-2 mb-8
                  bg-blue-100 dark:bg-blue-900/30
                  text-blue-700 dark:text-blue-300
                  rounded-full text-sm font-medium
                  animate-fade-in-up" style="animation-delay: 0.1s;">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
        </span>
        Yeni: Yapay Zeka Destekli Ozellikler
      </div>

      <!-- Headline with gradient text -->
      <h1 class="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold
                 text-slate-900 dark:text-white
                 leading-tight tracking-tight
                 animate-fade-in-up" style="animation-delay: 0.2s;">
        Isletmenizi
        <span class="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600
                     bg-clip-text text-transparent
                     bg-[length:200%_auto] animate-gradient">
          Dijitallestirin
        </span>
      </h1>

      <!-- Subheadline -->
      <p class="mt-6 text-lg sm:text-xl text-slate-600 dark:text-slate-300
                max-w-2xl mx-auto leading-relaxed
                animate-fade-in-up" style="animation-delay: 0.3s;">
        Modern cozumlerle isletmenizin verimliligi artirin.
        Kolay kullanim, guclu ozellikler, 7/24 destek.
      </p>

      <!-- CTA Buttons -->
      <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4
                  animate-fade-in-up" style="animation-delay: 0.4s;">
        <!-- Primary CTA -->
        <a href="#"
           class="group relative inline-flex items-center justify-center gap-2
                  px-8 py-4 w-full sm:w-auto
                  bg-blue-600 hover:bg-blue-700
                  text-white font-semibold text-lg
                  rounded-xl shadow-lg shadow-blue-500/25
                  hover:shadow-xl hover:shadow-blue-500/40
                  hover:-translate-y-0.5
                  transition-all duration-200">
          <span>Ucretsiz Deneyin</span>
          <svg class="w-5 h-5 transition-transform duration-200 group-hover:translate-x-1"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </a>

        <!-- Secondary CTA -->
        <a href="#"
           class="group inline-flex items-center justify-center gap-2
                  px-8 py-4 w-full sm:w-auto
                  text-slate-700 dark:text-slate-200
                  font-semibold text-lg
                  rounded-xl border-2 border-slate-200 dark:border-slate-700
                  hover:border-slate-300 dark:hover:border-slate-600
                  hover:bg-slate-50 dark:hover:bg-slate-800/50
                  transition-all duration-200">
          <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z"/>
          </svg>
          <span>Demo Izleyin</span>
        </a>
      </div>

      <!-- Trust indicators -->
      <div class="mt-12 flex flex-col items-center gap-4
                  animate-fade-in-up" style="animation-delay: 0.5s;">
        <p class="text-sm text-slate-500 dark:text-slate-400">
          500+ sirket tarafindan tercih ediliyor
        </p>
        <div class="flex items-center gap-8 opacity-60 grayscale hover:grayscale-0 hover:opacity-100 transition-all duration-300">
          <!-- Placeholder logos -->
          <div class="h-8 w-24 bg-slate-300 dark:bg-slate-700 rounded"></div>
          <div class="h-8 w-20 bg-slate-300 dark:bg-slate-700 rounded"></div>
          <div class="h-8 w-28 bg-slate-300 dark:bg-slate-700 rounded"></div>
          <div class="h-8 w-24 bg-slate-300 dark:bg-slate-700 rounded hidden sm:block"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Scroll indicator -->
  <div class="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
    <svg class="w-6 h-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
    </svg>
  </div>
</section>

<style>
  @keyframes fade-in-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .animate-fade-in-up {
    animation: fade-in-up 0.6s ease-out forwards;
    opacity: 0;
  }
  @keyframes gradient {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
  }
  .animate-gradient {
    animation: gradient 3s ease infinite;
  }
</style>""",
            "tailwind_classes_used": [
                "min-h-[90vh]", "bg-gradient-to-br", "from-slate-50", "via-white", "to-blue-50",
                "dark:from-slate-950", "blur-3xl", "animate-pulse", "container", "mx-auto",
                "text-4xl", "sm:text-5xl", "lg:text-6xl", "font-bold", "bg-clip-text",
                "text-transparent", "rounded-xl", "shadow-lg", "hover:shadow-xl",
                "transition-all", "duration-200", "group-hover:translate-x-1",
            ],
            "accessibility_features": [
                "semantic section element",
                "proper heading hierarchy",
                "sufficient color contrast",
                "focus-visible states on links",
                "reduced motion support via CSS",
            ],
            "dark_mode_support": True,
            "design_notes": "Premium hero with animated gradients, floating background elements, and staggered entrance animations. Uses custom CSS for smooth fade-in effects.",
        },
    },

    "pricing_card": {
        "input": {
            "component_type": "pricing_card",
            "context": "Premium tier pricing card for SaaS",
            "content_structure": {
                "tier": "Pro",
                "price": "299",
                "currency": "TL",
                "period": "ay",
                "features": ["Sinirsiz kullanici", "API erisimi", "Oncelikli destek"],
                "cta": "Hemen Basla",
                "popular": True,
            },
            "theme": "modern-minimal",
        },
        "output": {
            "component_id": "pricing_pro_tier",
            "atomic_level": "molecule",
            "html": """<div class="relative group">
  <!-- Popular badge -->
  <div class="absolute -top-4 left-1/2 -translate-x-1/2 z-10">
    <span class="inline-flex items-center px-4 py-1
                 bg-gradient-to-r from-blue-600 to-purple-600
                 text-white text-sm font-semibold
                 rounded-full shadow-lg">
      En Populer
    </span>
  </div>

  <!-- Card container -->
  <div class="relative p-8 pt-12
              bg-white dark:bg-slate-800
              border-2 border-blue-500 dark:border-blue-400
              rounded-2xl shadow-xl
              hover:shadow-2xl hover:-translate-y-1
              transition-all duration-300">

    <!-- Tier name -->
    <h3 class="text-xl font-bold text-slate-900 dark:text-white text-center">
      Pro
    </h3>

    <!-- Price -->
    <div class="mt-4 flex items-baseline justify-center gap-1">
      <span class="text-5xl font-extrabold text-slate-900 dark:text-white">
        299
      </span>
      <span class="text-xl font-medium text-slate-500 dark:text-slate-400">
        TL
      </span>
      <span class="text-slate-500 dark:text-slate-400">
        / ay
      </span>
    </div>

    <!-- Features list -->
    <ul class="mt-8 space-y-4">
      <li class="flex items-center gap-3">
        <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
        </svg>
        <span class="text-slate-700 dark:text-slate-300">Sinirsiz kullanici</span>
      </li>
      <li class="flex items-center gap-3">
        <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
        </svg>
        <span class="text-slate-700 dark:text-slate-300">API erisimi</span>
      </li>
      <li class="flex items-center gap-3">
        <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
        </svg>
        <span class="text-slate-700 dark:text-slate-300">Oncelikli destek</span>
      </li>
    </ul>

    <!-- CTA Button -->
    <button class="mt-8 w-full py-4 px-6
                   bg-gradient-to-r from-blue-600 to-purple-600
                   hover:from-blue-700 hover:to-purple-700
                   text-white font-semibold text-lg
                   rounded-xl shadow-lg shadow-blue-500/25
                   hover:shadow-xl hover:shadow-blue-500/40
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                   active:scale-[0.98]
                   transition-all duration-200">
      Hemen Basla
    </button>

    <!-- Money back guarantee -->
    <p class="mt-4 text-center text-sm text-slate-500 dark:text-slate-400">
      14 gun iade garantisi
    </p>
  </div>

  <!-- Decorative glow effect -->
  <div class="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600
              rounded-2xl blur-lg opacity-25 group-hover:opacity-40
              transition-opacity duration-300 -z-10"></div>
</div>""",
            "tailwind_classes_used": [
                "relative", "group", "absolute", "-top-4", "left-1/2", "-translate-x-1/2",
                "bg-gradient-to-r", "from-blue-600", "to-purple-600", "rounded-full",
                "shadow-lg", "p-8", "pt-12", "bg-white", "dark:bg-slate-800",
                "border-2", "border-blue-500", "rounded-2xl", "shadow-xl",
                "hover:shadow-2xl", "hover:-translate-y-1", "transition-all", "duration-300",
            ],
            "accessibility_features": [
                "semantic heading for tier name",
                "aria-label on button",
                "focus:ring for keyboard users",
                "sufficient color contrast",
            ],
            "dark_mode_support": True,
            "design_notes": "Premium pricing card with glow effect, gradient CTA, and subtle hover animations. Popular badge draws attention.",
        },
    },
}


# Section chain examples
SECTION_CHAIN_EXAMPLES: Dict[str, List[Dict[str, Any]]] = {
    "landing_page": [
        {
            "section_type": "hero",
            "design_tokens": {
                "colors": {"primary": "#3B82F6", "secondary": "#8B5CF6", "background": "#FFFFFF"},
                "typography": {"heading_size": "text-6xl", "body_size": "text-lg"},
                "spacing": {"section_padding": "py-20", "element_gap": "gap-6"},
            },
        },
        {
            "section_type": "features",
            "design_tokens": "extracted from hero",
            "note": "Maintains same color palette and typography scale",
        },
        {
            "section_type": "pricing",
            "design_tokens": "extracted from features",
            "note": "Continues visual consistency",
        },
    ],
}


def get_few_shot_example(component_type: str) -> Optional[Dict[str, Any]]:
    """Get a few-shot example for a component type.

    Args:
        component_type: The type of component.

    Returns:
        Example dict with input and output, or None if not available.
    """
    return COMPONENT_EXAMPLES.get(component_type)


def get_few_shot_examples_for_prompt(
    component_type: str,
    include_similar: bool = True,
) -> str:
    """Generate few-shot examples formatted for inclusion in prompts.

    Args:
        component_type: The type of component being designed.
        include_similar: Whether to include examples of similar components.

    Returns:
        Formatted string with examples.
    """
    examples = []

    # Get exact match
    exact = COMPONENT_EXAMPLES.get(component_type)
    if exact:
        examples.append((component_type, exact))

    # Get similar components if requested
    if include_similar:
        similar_map = {
            "button": ["cta"],
            "hero": ["banner"],
            "card": ["pricing_card", "stat_card"],
            "pricing_card": ["card"],
            "navbar": ["header"],
            "footer": [],
        }
        similar_types = similar_map.get(component_type, [])
        for similar in similar_types[:1]:  # Limit to 1 similar
            if similar in COMPONENT_EXAMPLES:
                examples.append((similar, COMPONENT_EXAMPLES[similar]))

    if not examples:
        return ""

    # Format examples
    lines = ["## Reference Examples", ""]
    for comp_type, example in examples:
        lines.append(f"### Example: {comp_type}")
        lines.append(f"**Input:** {example['input']}")
        lines.append("**Key Output Features:**")
        output = example["output"]
        lines.append(f"- Uses rich Tailwind classes: {', '.join(output['tailwind_classes_used'][:5])}...")
        lines.append(f"- Includes accessibility: {', '.join(output['accessibility_features'][:2])}")
        lines.append(f"- Has dark mode: {output['dark_mode_support']}")
        lines.append(f"- Design notes: {output['design_notes'][:100]}...")
        lines.append("")

    return "\n".join(lines)


def get_section_chain_example(page_type: str) -> Optional[List[Dict[str, Any]]]:
    """Get a section chain example for a page type.

    Args:
        page_type: The type of page (e.g., "landing_page").

    Returns:
        List of section examples, or None if not available.
    """
    return SECTION_CHAIN_EXAMPLES.get(page_type)
