"""Few-shot examples for Gemini design prompts.

Provides high-quality example inputs and outputs to help Gemini
understand the expected format and quality of design responses.
"""

from typing import Dict, List, Any, Optional

# Example component designs with rich CSS/JS
COMPONENT_EXAMPLES: Dict[str, Dict[str, Any]] = {

    "ultra_dense_card": {
        "input": "Create a glassmorphic NFT card with holographic effects",
        "output": {
            "design_thinking": "1. VISUAL DNA: Cyberpunk luxury. Needs iridescence. 2. LAYERS: 5 layers (Base + Mesh + Noise + Holograph + Glass). 3. PHYSICS: Tilt effect on hover.",
            "component_id": "nft_holo_card",
            "atomic_level": "molecule",
            "html": """
<div class="group relative w-full max-w-sm rounded-[2.5rem] p-0.5 transition-all duration-500 hover:scale-105 hover:shadow-[0_0_80px_-10px_rgba(168,85,247,0.4)]">
    <!-- HOLOGRAPHIC BORDER GRADIENT -->
    <div class="absolute inset-0 rounded-[2.5rem] bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 opacity-100 blur-sm transition-all duration-500 group-hover:opacity-100 group-hover:blur-md animate-gradient bg-[length:200%_200%]"></div>
    
    <!-- MAIN CARD CONTAINER -->
    <div class="relative h-full w-full overflow-hidden rounded-[2.4rem] bg-slate-900/90 backdrop-blur-3xl ring-1 ring-white/10">
        
        <!-- LAYER 1: NOISE TEXTURE -->
        <div class="absolute inset-0 z-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
        
        <!-- LAYER 2: INTERACTIVE BLOB BACKGROUND -->
        <div class="absolute -top-24 -right-24 h-64 w-64 rounded-full bg-purple-600/30 blur-[80px] transition-all duration-700 group-hover:bg-purple-600/50"></div>
        <div class="absolute -bottom-24 -left-24 h-64 w-64 rounded-full bg-indigo-600/30 blur-[80px] transition-all duration-700 group-hover:bg-indigo-600/50"></div>
        
        <!-- CARD CONTENT -->
        <div class="relative z-10 flex flex-col p-6">
            
            <!-- IMAGE CONTAINER with Inner Shadow & Reflection -->
            <div class="relative mb-6 overflow-hidden rounded-[2rem] shadow-2xl ring-1 ring-white/10 group-hover:shadow-purple-500/20">
                <div class="absolute inset-0 z-20 bg-gradient-to-tr from-transparent via-transparent to-white/20 opacity-0 transition-opacity duration-500 group-hover:opacity-100"></div>
                <img src="https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/961163155700689.635a9c049d569.jpg" alt="NFT" class="h-64 w-full object-cover transition-transform duration-700 ease-[cubic-bezier(0.25,1,0.5,1)] group-hover:scale-110">
                
                <!-- Floating Badge -->
                <div class="absolute top-4 right-4 z-30 flex items-center gap-2 rounded-full border border-white/20 bg-black/40 px-3 py-1.5 backdrop-blur-md">
                    <span class="relative flex h-2 w-2">
                      <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75"></span>
                      <span class="relative inline-flex h-2 w-2 rounded-full bg-green-500"></span>
                    </span>
                    <span class="text-xs font-bold tracking-wider text-white">LIVE</span>
                </div>
            </div>
            
            <!-- TEXT DETAILS -->
            <div class="mb-4">
                <h3 class="bg-gradient-to-r from-white to-white/60 bg-clip-text text-2xl font-black tracking-tight text-transparent drop-shadow-sm">Cosmic Traveler #1337</h3>
                <p class="text-sm font-medium text-slate-400">Created by <span class="text-purple-400 group-hover:underline">Neo_Artist</span></p>
            </div>
            
            <!-- STATS ROW with Glass Capsules -->
            <div class="mb-6 grid grid-cols-2 gap-3">
                <div class="flex flex-col items-center justify-center rounded-2xl border border-white/5 bg-white/5 py-3 transition-colors hover:bg-white/10">
                    <span class="text-xs font-bold uppercase tracking-widest text-slate-500">Current Bid</span>
                    <span class="text-lg font-black text-white">4.2 ETH</span>
                </div>
                <div class="flex flex-col items-center justify-center rounded-2xl border border-white/5 bg-white/5 py-3 transition-colors hover:bg-white/10">
                    <span class="text-xs font-bold uppercase tracking-widest text-slate-500">Ending In</span>
                    <span class="text-lg font-black text-white">08h 12m</span>
                </div>
            </div>
            
            <!-- ACTION BUTTON with Complex Hover Physics -->
            <button class="group/btn relative w-full overflow-hidden rounded-xl bg-white py-4 text-center font-bold text-slate-900 transition-all hover:scale-[1.02] hover:shadow-lg hover:shadow-white/20 active:scale-95">
                <span class="relative z-10">Place Bid</span>
                <div class="absolute inset-0 -translate-x-full bg-gradient-to-r from-purple-400 to-indigo-400 transition-transform duration-300 group-hover/btn:translate-x-0"></div>
                <span class="absolute inset-0 z-20 flex items-center justify-center opacity-0 transition-opacity duration-300 group-hover/btn:opacity-100 text-white">Confirm Transaction</span>
            </button>
        </div>
    </div>
</div>
""",
            "tailwind_classes_used": ["bg-slate-900", "backdrop-blur-3xl", "animate-gradient"],
            "accessibility_features": ["alt text"],
            "responsive_breakpoints": [],
            "dark_mode_support": True,
            "micro_interactions": ["hover:scale-105", "group-hover"],
            "design_notes": "Dense layering used."
        }
    },


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

    "elite_dashboard_stat": {
        "input": {
            "component_type": "stat_card",
            "context": "C-Level Financial Dashboard",
            "vibe": "elite_corporate",
            "content": {"label": "Net Profit Margin", "value": "24.8%", "trend": "+2.1%"}
        },
        "output": {
            "design_thinking": "1. VIBE DNA: Elite Corporate. Precision is paramount. Using 1px border highlights to define a 'glass slab' aesthetic. 2. TYPOGRAPHY: Inter SemiBold with -0.02em tracking for that 'Swiss Design' premium feel. 3. PHYSICS: Micro-transitions only. Hover lifts the slab by exactly 2px with an indigo-500 shadow-glow.",
            "component_id": "stat_profit_margin",
            "atomic_level": "molecule",
            "html": """
<div class="group relative overflow-hidden rounded-xl bg-slate-900 border border-white/10 p-6 transition-all duration-500 hover:-translate-y-0.5 hover:shadow-[0_20px_40px_-15px_rgba(79,70,229,0.3)]">
    <!-- Subtle Edge Highlight -->
    <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
    
    <div class="flex items-center justify-between mb-4">
        <span class="text-xs font-bold uppercase tracking-[0.1em] text-slate-500 font-sans">Financial Matrix</span>
        <div class="h-8 w-8 rounded-lg bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
            <svg class="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
        </div>
    </div>
    
    <div class="flex flex-col">
        <h3 class="text-sm font-medium text-slate-400 mb-1">Net Profit Margin</h3>
        <div class="flex items-baseline gap-2">
            <span class="text-3xl font-bold tracking-tight text-white font-sans">24.8%</span>
            <span class="text-xs font-semibold text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-full border border-emerald-400/20">+2.1%</span>
        </div>
    </div>
    
    <!-- Data Stream Particle (Atmospheric) -->
    <div class="mt-6 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
        <div class="h-full bg-indigo-500 w-[70%] animate-pulse"></div>
    </div>
</div>
""",
            "tailwind_classes_used": ["bg-slate-900", "border-white/10", "tracking-tight", "backdrop-blur-3xl"],
            "accessibility_features": ["semantic HTML", "high contrast for metrics"],
            "dark_mode_support": True,
            "design_notes": "Premium corporate vibe with high-density detail and subtle data visualization elements."
        }
    },

    "playful_video_card": {
        "input": {
            "component_type": "action_card",
            "context": "AI Video Generator for kids",
            "vibe": "playful_funny",
            "content": {"title": "Make Magic Video!", "emoji": "🪄"}
        },
        "output": {
            "design_thinking": "1. VIBE DNA: Playful AI. Needs to feel alive and bouncy. Using Neo-Brutalism shadows with unusual colors. 2. PHYSICS: Spring-based hover (scale-110 + rotate-3). 3. ATOMIZATION: Floating sparkles as decoration.",
            "component_id": "card_magic_video",
            "atomic_level": "molecule",
            "html": """
<div class="group relative inline-block p-1">
    <!-- Offset Shadow (Neo-Brutalism) -->
    <div class="absolute inset-0 bg-pink-500 rounded-[2rem] translate-x-3 translate-y-3 transition-transform group-hover:translate-x-1 group-hover:translate-y-1"></div>
    
    <!-- Main Card -->
    <div class="relative bg-yellow-400 border-[3px] border-black rounded-[2rem] p-8 transition-transform duration-300 group-hover:scale-[1.05] group-hover:-rotate-2">
        <!-- Floating Sparkle 1 -->
        <span class="absolute -top-4 -left-4 text-3xl animate-bounce">✨</span>
        <!-- Floating Sparkle 2 -->
        <span class="absolute -bottom-2 -right-4 text-3xl animate-pulse delay-500">🌈</span>
        
        <div class="space-y-4 text-center">
            <div class="text-6xl group-hover:animate-spin-slow">🪄</div>
            <h3 class="text-2xl font-black italic tracking-tighter text-black uppercase">Süper Video Yap!</h3>
            <p class="text-sm font-bold text-black/60">Yapay zeka senin için dans etsin! 💃</p>
            
            <button class="w-full bg-black text-white py-4 rounded-full font-black text-xl hover:bg-pink-600 active:scale-95 transition-all shadow-[4px_4px_0px_#fff] hover:shadow-none translate-y-0 hover:translate-y-1">
                BAŞLA BAKALIM!
            </button>
        </div>
    </div>
</div>
<style>
@keyframes spin-slow {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
.animate-spin-slow {
    animation: spin-slow 8s linear infinite;
}
</style>
""",
            "tailwind_classes_used": ["bg-yellow-400", "border-black", "rounded-[2rem]", "font-black"],
            "accessibility_features": ["clear target size", "descriptive labels"],
            "dark_mode_support": False,
            "design_notes": "Funny/Playful vibe with high energy, bouncy physics, and bold typography."
        }
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
