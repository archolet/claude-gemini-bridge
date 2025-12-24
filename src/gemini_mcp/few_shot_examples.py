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
    # === Vibe: cyberpunk_edge (Enhancement) ===
    "cyberpunk_neural_card": {
        "input": {
            "component_type": "card",
            "vibe": "cyberpunk_edge",
            "context": "Neural interface status card in a cyberpunk dashboard",
        },
        "output": {
            "design_thinking": "1. VIBE DNA: Cyberpunk Edge. High contrast, industrial tech, neon glow. "
                              "2. SCANLINES: Subtle CRT effect with animated gradient pulse. "
                              "3. GLOW: Cyan neon border with box-shadow glow on hover. "
                              "4. TYPOGRAPHY: Monospace font-mono with tracking-wider for terminal feel.",
            "html": '''
<div class="relative p-6 bg-black/95 border border-cyan-500/50
            rounded-lg overflow-hidden group
            shadow-[0_0_20px_rgba(0,255,255,0.3)]
            hover:shadow-[0_0_40px_rgba(0,255,255,0.5)]
            transition-all duration-300">
    <!-- Scanline effect overlay -->
    <div class="absolute inset-0 pointer-events-none">
        <div class="absolute inset-0 bg-gradient-to-b from-transparent
                    via-cyan-500/5 to-transparent animate-pulse"></div>
        <div class="absolute inset-0 bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(0,255,255,0.03)_2px,rgba(0,255,255,0.03)_4px)]"></div>
    </div>

    <!-- Neon glow border -->
    <div class="absolute inset-0 border border-cyan-400/20
                group-hover:border-cyan-400/60
                transition-all duration-200 rounded-lg"></div>

    <!-- Status indicator -->
    <div class="flex items-center gap-2 mb-4">
        <div class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse
                    shadow-[0_0_8px_rgba(0,255,255,0.8)]"></div>
        <span class="text-cyan-400/70 font-mono text-xs tracking-[0.2em] uppercase">
            SYSTEM::ACTIVE
        </span>
    </div>

    <!-- Main content -->
    <h3 class="relative text-cyan-400 font-mono text-lg tracking-wider
               uppercase mb-2 drop-shadow-[0_0_10px_rgba(0,255,255,0.6)]">
        NEURAL_INTERFACE
    </h3>
    <p class="relative text-cyan-100/80 font-mono text-sm leading-relaxed">
        All systems operational. Latency: 0.003ms
    </p>

    <!-- Data grid -->
    <div class="mt-4 grid grid-cols-3 gap-2 pt-4 border-t border-cyan-500/20">
        <div class="text-center">
            <div class="text-cyan-400 font-mono text-xl font-bold">98.7%</div>
            <div class="text-cyan-500/60 font-mono text-[10px] uppercase tracking-wider">SYNC</div>
        </div>
        <div class="text-center">
            <div class="text-fuchsia-400 font-mono text-xl font-bold">1.2TB</div>
            <div class="text-fuchsia-500/60 font-mono text-[10px] uppercase tracking-wider">CACHE</div>
        </div>
        <div class="text-center">
            <div class="text-yellow-400 font-mono text-xl font-bold">∞</div>
            <div class="text-yellow-500/60 font-mono text-[10px] uppercase tracking-wider">CORES</div>
        </div>
    </div>
</div>
''',
            "tailwind_classes_used": ["bg-black/95", "border-cyan-500/50", "font-mono", "tracking-wider", "animate-pulse"],
            "accessibility_features": ["sufficient color contrast on dark", "clear status indicators"],
            "dark_mode_support": True,
            "design_notes": "Cyberpunk Edge vibe with neon glows, scanline effects, monospace typography, and industrial tech aesthetic."
        }
    },
    # === Vibe: luxury_editorial (Enhancement) ===
    "luxury_article_card": {
        "input": {
            "component_type": "card",
            "vibe": "luxury_editorial",
            "context": "Premium article card for a luxury fashion magazine",
        },
        "output": {
            "design_thinking": "1. VIBE DNA: Luxury Editorial. Refined, spacious, understated elegance. "
                              "2. TYPOGRAPHY: Serif headlines (font-serif) with extreme letter-spacing. "
                              "3. WHITESPACE: Generous padding and breathing room. "
                              "4. ANIMATION: Ultra-slow transitions (duration-700) for sophistication.",
            "html": '''
<article class="max-w-2xl mx-auto py-16 px-8 bg-white">
    <!-- Category label -->
    <span class="inline-block text-xs tracking-[0.3em] uppercase text-gray-400
                 font-light mb-6">
        Collection
    </span>

    <!-- Main headline -->
    <h2 class="text-4xl md:text-5xl font-serif font-light tracking-tight
               text-gray-900 leading-[1.1] mb-8">
        The Art of <em class="font-serif italic">Understated</em> Elegance
    </h2>

    <!-- Minimal divider -->
    <div class="h-px w-16 bg-gray-200 mb-8"></div>

    <!-- Body text -->
    <p class="text-lg md:text-xl font-light text-gray-600 leading-relaxed
              tracking-wide max-w-xl">
        Where craftsmanship meets timeless design. Each piece tells
        a story of meticulous attention to detail, passed down through
        generations of artisans.
    </p>

    <!-- Read more link -->
    <a href="#" class="mt-12 inline-flex items-center text-sm
                       tracking-[0.15em] uppercase text-gray-900
                       hover:text-gray-600 transition-colors
                       duration-700 group">
        <span>Explore Collection</span>
        <span class="ml-3 inline-block group-hover:translate-x-2
                     transition-transform duration-700">→</span>
    </a>

    <!-- Image placeholder with aspect ratio -->
    <div class="mt-16 aspect-[4/5] bg-gray-100 overflow-hidden">
        <div class="w-full h-full bg-gradient-to-br from-gray-50 to-gray-200
                    flex items-center justify-center text-gray-300 font-serif italic text-2xl">
            Image
        </div>
    </div>
</article>
''',
            "tailwind_classes_used": ["font-serif", "tracking-[0.3em]", "font-light", "duration-700", "leading-relaxed"],
            "accessibility_features": ["clear heading hierarchy", "sufficient contrast", "keyboard-accessible link"],
            "dark_mode_support": False,
            "design_notes": "Luxury Editorial vibe with refined serif typography, generous whitespace, ultra-slow transitions, and understated elegance."
        }
    },

    # ==========================================================================
    # PHASE 2.1: Core Component Examples (6 New)
    # ==========================================================================
    # These examples fill critical gaps in component type and theme coverage.
    # Each follows the 7-step SCoT pattern and meets density targets.

    # -------------------------------------------------------------------------
    # 1. NAVBAR MEGA MENU (modern-minimal, elite_corporate) - HIGH PRIORITY
    # -------------------------------------------------------------------------
    "navbar_mega_menu": {
        "input": {
            "component_type": "navbar",
            "theme": "modern-minimal",
            "vibe": "elite_corporate",
            "context": "Enterprise SaaS navigation with mega menu dropdowns",
            "content_structure": {
                "logo": "TechCorp",
                "nav_items": ["Products", "Solutions", "Resources", "Pricing"],
                "cta": "Start Free Trial",
            },
        },
        "output": {
            "design_thinking": "1. CONSTRAINT_CHECK: Density target 15-20 ✓ | 4-Layer: glass nav + shadow + ring ✓ | elite_corporate vibe ✓ "
                              "2. AESTHETIC_PHYSICS: Frosted glass navbar, subtle shadow stack, precise 64px height. "
                              "3. VISUAL_DNA: bg-white/80 backdrop-blur-xl border-b border-slate-200/50 shadow-sm "
                              "4. MICRO_INTERACTIONS: Dropdown reveal with scale-95→100 + opacity-0→100, 150ms ease-out "
                              "5. RESPONSIVE_STRATEGY: Mobile hamburger (md:hidden), desktop full nav (md:flex) "
                              "6. A11Y_CHECKLIST: aria-expanded, aria-haspopup, focus-visible rings, keyboard nav "
                              "7. DENSITY_ITERATION: Added ring-1 ring-slate-900/5 for depth. Final: 18 classes on nav",
            "component_id": "navbar_mega_enterprise",
            "atomic_level": "organism",
            "html": '''<header class="fixed top-0 inset-x-0 z-50 h-16
                bg-white/80 backdrop-blur-xl
                border-b border-slate-200/50
                shadow-sm shadow-slate-900/5
                ring-1 ring-slate-900/5">
    <nav class="container mx-auto px-4 lg:px-8 h-full flex items-center justify-between"
         role="navigation" aria-label="Main navigation">

        <!-- Logo -->
        <a href="/" class="flex items-center gap-2 text-slate-900 font-semibold text-lg
                          hover:text-slate-700 transition-colors duration-150">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
            </svg>
            <span>TechCorp</span>
        </a>

        <!-- Mobile Menu Button -->
        <button type="button"
                class="md:hidden p-2 rounded-lg text-slate-600
                       hover:bg-slate-100 hover:text-slate-900
                       focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                       transition-colors duration-150"
                aria-expanded="false"
                aria-controls="mobile-menu"
                aria-label="Toggle navigation menu">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
        </button>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center gap-1">
            <!-- Products Dropdown -->
            <div class="relative group">
                <button type="button"
                        class="flex items-center gap-1 px-4 py-2 rounded-lg
                               text-slate-600 font-medium text-sm
                               hover:text-slate-900 hover:bg-slate-100
                               focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                               transition-all duration-150"
                        aria-expanded="false"
                        aria-haspopup="true">
                    Products
                    <svg class="w-4 h-4 transition-transform duration-150 group-hover:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                    </svg>
                </button>

                <!-- Mega Menu Dropdown -->
                <div class="absolute top-full left-0 pt-2
                            opacity-0 invisible scale-95 translate-y-1
                            group-hover:opacity-100 group-hover:visible group-hover:scale-100 group-hover:translate-y-0
                            transition-all duration-150 ease-out
                            origin-top-left">
                    <div class="w-[480px] p-6
                                bg-white rounded-xl
                                shadow-xl shadow-slate-900/10
                                ring-1 ring-slate-900/5
                                border border-slate-200/50">
                        <div class="grid grid-cols-2 gap-6">
                            <a href="#" class="group/item flex gap-4 p-3 rounded-lg
                                              hover:bg-slate-50 transition-colors duration-150">
                                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-blue-50 text-blue-600
                                            flex items-center justify-center
                                            group-hover/item:bg-blue-100 transition-colors duration-150">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                                    </svg>
                                </div>
                                <div>
                                    <div class="font-medium text-slate-900 text-sm">Analytics</div>
                                    <div class="text-slate-500 text-sm mt-0.5">Real-time insights</div>
                                </div>
                            </a>
                            <a href="#" class="group/item flex gap-4 p-3 rounded-lg
                                              hover:bg-slate-50 transition-colors duration-150">
                                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600
                                            flex items-center justify-center
                                            group-hover/item:bg-emerald-100 transition-colors duration-150">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                                    </svg>
                                </div>
                                <div>
                                    <div class="font-medium text-slate-900 text-sm">Security</div>
                                    <div class="text-slate-500 text-sm mt-0.5">Enterprise-grade protection</div>
                                </div>
                            </a>
                            <a href="#" class="group/item flex gap-4 p-3 rounded-lg
                                              hover:bg-slate-50 transition-colors duration-150">
                                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-violet-50 text-violet-600
                                            flex items-center justify-center
                                            group-hover/item:bg-violet-100 transition-colors duration-150">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"/>
                                    </svg>
                                </div>
                                <div>
                                    <div class="font-medium text-slate-900 text-sm">Integrations</div>
                                    <div class="text-slate-500 text-sm mt-0.5">Connect your tools</div>
                                </div>
                            </a>
                            <a href="#" class="group/item flex gap-4 p-3 rounded-lg
                                              hover:bg-slate-50 transition-colors duration-150">
                                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-amber-50 text-amber-600
                                            flex items-center justify-center
                                            group-hover/item:bg-amber-100 transition-colors duration-150">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                                    </svg>
                                </div>
                                <div>
                                    <div class="font-medium text-slate-900 text-sm">Automation</div>
                                    <div class="text-slate-500 text-sm mt-0.5">Streamline workflows</div>
                                </div>
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Simple Nav Items -->
            <a href="#" class="px-4 py-2 rounded-lg text-slate-600 font-medium text-sm
                              hover:text-slate-900 hover:bg-slate-100
                              focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                              transition-colors duration-150">
                Solutions
            </a>
            <a href="#" class="px-4 py-2 rounded-lg text-slate-600 font-medium text-sm
                              hover:text-slate-900 hover:bg-slate-100
                              focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                              transition-colors duration-150">
                Resources
            </a>
            <a href="#" class="px-4 py-2 rounded-lg text-slate-600 font-medium text-sm
                              hover:text-slate-900 hover:bg-slate-100
                              focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                              transition-colors duration-150">
                Pricing
            </a>
        </div>

        <!-- CTA Button -->
        <div class="hidden md:flex items-center gap-3">
            <a href="#" class="text-sm text-slate-600 hover:text-slate-900
                              focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                              transition-colors duration-150">
                Sign in
            </a>
            <a href="#" class="px-4 py-2 rounded-lg
                              bg-slate-900 text-white text-sm font-medium
                              hover:bg-slate-800
                              focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:outline-none
                              shadow-sm shadow-slate-900/10
                              transition-all duration-150">
                Start Free Trial
            </a>
        </div>
    </nav>
</header>''',
            "tailwind_classes_used": [
                "backdrop-blur-xl", "ring-1", "ring-slate-900/5", "shadow-slate-900/10",
                "aria-expanded", "aria-haspopup", "focus-visible:ring-2", "origin-top-left",
                "group-hover:opacity-100", "group-hover:scale-100", "translate-y-1",
                "focus-visible:ring-offset-2", "group/item", "group-hover/item:bg-blue-100"
            ],
            "accessibility_features": [
                "aria-expanded on dropdown triggers",
                "aria-haspopup for menu buttons",
                "aria-label on navigation",
                "focus-visible rings for keyboard users",
                "aria-controls linking button to menu"
            ],
            "dark_mode_support": False,
            "design_notes": "Elite corporate navbar with frosted glass effect, mega menu dropdowns using group-hover pattern. 18 classes on nav element meeting density target. Accessible with full ARIA support."
        }
    },

    # -------------------------------------------------------------------------
    # 2. FORM INPUT SET (brutalist, playful_funny) - HIGH PRIORITY
    # -------------------------------------------------------------------------
    "form_input_set": {
        "input": {
            "component_type": "form",
            "theme": "brutalist",
            "vibe": "playful_funny",
            "context": "Contact form with bold, high-contrast styling",
            "content_structure": {
                "fields": ["Name", "Email", "Message"],
                "submit_text": "Send it! 🚀",
            },
        },
        "output": {
            "design_thinking": "1. CONSTRAINT_CHECK: Form density 12+ ✓ | brutalist = sharp edges, high contrast ✓ | playful = emojis, bouncy ✓ "
                              "2. AESTHETIC_PHYSICS: Stark black/white, 0 border-radius, heavy 4px borders, offset shadows "
                              "3. VISUAL_DNA: bg-white border-4 border-black shadow-[8px_8px_0px_0px_#000] "
                              "4. MICRO_INTERACTIONS: Focus translate-x-[-4px] translate-y-[-4px], bounce on submit "
                              "5. RESPONSIVE_STRATEGY: Stack on mobile, maintain chunky proportions "
                              "6. A11Y_CHECKLIST: Labels for all inputs, focus-visible, aria-required "
                              "7. DENSITY_ITERATION: Added hover shadow shift + active press state. Final: 14 classes/input",
            "component_id": "form_brutalist_playful",
            "atomic_level": "molecule",
            "html": '''<form class="w-full max-w-lg p-8 bg-white border-4 border-black
                shadow-[8px_8px_0px_0px_#000]
                transition-all duration-150
                hover:shadow-[12px_12px_0px_0px_#000] hover:translate-x-[-2px] hover:translate-y-[-2px]">
    <h2 class="text-3xl font-black uppercase tracking-tight mb-8 text-black">
        Let's Chat! 👋
    </h2>

    <!-- Name Field -->
    <div class="mb-6">
        <label for="name" class="block text-sm font-bold uppercase tracking-wider text-black mb-2">
            Your Name <span class="text-red-500">*</span>
        </label>
        <input
            type="text"
            id="name"
            name="name"
            required
            aria-required="true"
            class="w-full px-4 py-3
                   bg-white text-black text-lg font-medium
                   border-4 border-black
                   placeholder:text-gray-400
                   focus:outline-none focus:bg-yellow-100
                   focus:translate-x-[-4px] focus:translate-y-[-4px]
                   focus:shadow-[4px_4px_0px_0px_#000]
                   transition-all duration-150"
            placeholder="What do they call you?"
        />
    </div>

    <!-- Email Field -->
    <div class="mb-6">
        <label for="email" class="block text-sm font-bold uppercase tracking-wider text-black mb-2">
            Email <span class="text-red-500">*</span>
        </label>
        <input
            type="email"
            id="email"
            name="email"
            required
            aria-required="true"
            class="w-full px-4 py-3
                   bg-white text-black text-lg font-medium
                   border-4 border-black
                   placeholder:text-gray-400
                   focus:outline-none focus:bg-yellow-100
                   focus:translate-x-[-4px] focus:translate-y-[-4px]
                   focus:shadow-[4px_4px_0px_0px_#000]
                   invalid:border-red-500 invalid:bg-red-50
                   transition-all duration-150"
            placeholder="you@awesome.com"
        />
    </div>

    <!-- Message Field -->
    <div class="mb-8">
        <label for="message" class="block text-sm font-bold uppercase tracking-wider text-black mb-2">
            Your Message <span class="text-red-500">*</span>
        </label>
        <textarea
            id="message"
            name="message"
            required
            aria-required="true"
            rows="4"
            class="w-full px-4 py-3
                   bg-white text-black text-lg font-medium
                   border-4 border-black
                   placeholder:text-gray-400
                   focus:outline-none focus:bg-yellow-100
                   focus:translate-x-[-4px] focus:translate-y-[-4px]
                   focus:shadow-[4px_4px_0px_0px_#000]
                   resize-none
                   transition-all duration-150"
            placeholder="Tell us everything..."
        ></textarea>
    </div>

    <!-- Submit Button -->
    <button
        type="submit"
        class="w-full px-6 py-4
               bg-black text-white text-lg font-black uppercase tracking-wider
               border-4 border-black
               shadow-[6px_6px_0px_0px_#FACC15]
               hover:bg-yellow-400 hover:text-black
               hover:shadow-[8px_8px_0px_0px_#000]
               hover:translate-x-[-2px] hover:translate-y-[-2px]
               active:translate-x-0 active:translate-y-0 active:shadow-none
               focus-visible:ring-4 focus-visible:ring-yellow-400 focus-visible:outline-none
               transition-all duration-150">
        Send it! 🚀
    </button>

    <!-- Fun footer note -->
    <p class="mt-6 text-center text-sm text-gray-500">
        We read every message. Pinky promise! 🤙
    </p>
</form>''',
            "tailwind_classes_used": [
                "border-4", "shadow-[8px_8px_0px_0px_#000]", "font-black", "uppercase",
                "tracking-wider", "focus:translate-x-[-4px]", "focus:translate-y-[-4px]",
                "focus:shadow-[4px_4px_0px_0px_#000]", "invalid:border-red-500",
                "active:translate-x-0", "active:shadow-none", "resize-none"
            ],
            "accessibility_features": [
                "Labels associated with inputs via for/id",
                "aria-required on required fields",
                "focus-visible for keyboard navigation",
                "Visible focus states with color change",
                "Invalid state styling"
            ],
            "dark_mode_support": False,
            "design_notes": "Brutalist form with playful_funny vibe. Zero border-radius, heavy 4px borders, offset box shadows. Interactive translate on focus creates depth. Emojis add personality without compromising usability."
        }
    },

    # -------------------------------------------------------------------------
    # 3. MODAL DIALOG (glassmorphism, luxury_editorial) - HIGH PRIORITY
    # -------------------------------------------------------------------------
    "modal_dialog": {
        "input": {
            "component_type": "modal",
            "theme": "glassmorphism",
            "vibe": "luxury_editorial",
            "context": "Premium subscription confirmation modal",
            "content_structure": {
                "title": "Confirm Subscription",
                "description": "You're about to unlock premium features",
                "price": "$29/month",
                "actions": ["Cancel", "Confirm"],
            },
        },
        "output": {
            "design_thinking": "1. CONSTRAINT_CHECK: Modal density 12+ ✓ | glassmorphism = blur + transparency ✓ | luxury_editorial = serif + spacing ✓ "
                              "2. AESTHETIC_PHYSICS: Frosted glass panel over dark overlay, subtle inner glow, elegant serif headings "
                              "3. VISUAL_DNA: bg-white/10 backdrop-blur-2xl border border-white/20 shadow-2xl "
                              "4. MICRO_INTERACTIONS: Entry scale-95→100 + opacity fade, 200ms ease-out "
                              "5. RESPONSIVE_STRATEGY: Centered with max-w-md, full-width padding on mobile "
                              "6. A11Y_CHECKLIST: role=dialog, aria-labelledby, aria-describedby, focus trap "
                              "7. DENSITY_ITERATION: Added ring-1 ring-white/10 for glass edge. Final: 16 classes on panel",
            "component_id": "modal_glass_luxury",
            "atomic_level": "molecule",
            "html": '''<!-- Modal Backdrop -->
<div class="fixed inset-0 z-50 flex items-center justify-center p-4
            bg-slate-950/80 backdrop-blur-sm
            animate-[fadeIn_200ms_ease-out]"
     role="dialog"
     aria-modal="true"
     aria-labelledby="modal-title"
     aria-describedby="modal-description">

    <!-- Modal Panel -->
    <div class="relative w-full max-w-md
                bg-white/10 backdrop-blur-2xl
                border border-white/20
                rounded-3xl p-8
                shadow-2xl shadow-black/20
                ring-1 ring-white/10
                animate-[scaleIn_200ms_ease-out]">

        <!-- Close Button -->
        <button type="button"
                class="absolute top-4 right-4 p-2 rounded-full
                       text-white/60 hover:text-white hover:bg-white/10
                       focus-visible:ring-2 focus-visible:ring-white/50 focus-visible:outline-none
                       transition-colors duration-150"
                aria-label="Close modal">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
        </button>

        <!-- Icon -->
        <div class="mx-auto w-16 h-16 mb-6 rounded-2xl
                    bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20
                    border border-white/10
                    flex items-center justify-center">
            <svg class="w-8 h-8 text-violet-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
            </svg>
        </div>

        <!-- Content -->
        <div class="text-center">
            <h2 id="modal-title" class="text-2xl font-serif font-light text-white tracking-tight">
                Confirm Subscription
            </h2>
            <p id="modal-description" class="mt-3 text-white/70 leading-relaxed">
                You're about to unlock premium features and elevate your experience.
            </p>

            <!-- Price Badge -->
            <div class="mt-6 inline-flex items-baseline gap-1 px-4 py-2
                        bg-white/5 rounded-full border border-white/10">
                <span class="text-3xl font-light text-white">$29</span>
                <span class="text-white/50 text-sm">/month</span>
            </div>

            <!-- Features List -->
            <ul class="mt-6 text-left text-sm text-white/70 space-y-2">
                <li class="flex items-center gap-3">
                    <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                    </svg>
                    <span>Unlimited projects</span>
                </li>
                <li class="flex items-center gap-3">
                    <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                    </svg>
                    <span>Priority support</span>
                </li>
                <li class="flex items-center gap-3">
                    <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                    </svg>
                    <span>Advanced analytics</span>
                </li>
            </ul>
        </div>

        <!-- Actions -->
        <div class="mt-8 flex flex-col-reverse sm:flex-row gap-3">
            <button type="button"
                    class="flex-1 px-6 py-3 rounded-xl
                           text-white/70 text-sm font-medium
                           bg-white/5 border border-white/10
                           hover:bg-white/10 hover:text-white
                           focus-visible:ring-2 focus-visible:ring-white/50 focus-visible:outline-none
                           transition-all duration-150">
                Cancel
            </button>
            <button type="button"
                    class="flex-1 px-6 py-3 rounded-xl
                           text-white text-sm font-medium
                           bg-gradient-to-r from-violet-600 to-fuchsia-600
                           hover:from-violet-500 hover:to-fuchsia-500
                           shadow-lg shadow-violet-500/25
                           focus-visible:ring-2 focus-visible:ring-violet-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 focus-visible:outline-none
                           transition-all duration-150">
                Confirm Subscription
            </button>
        </div>
    </div>
</div>

<style>
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}
</style>''',
            "tailwind_classes_used": [
                "backdrop-blur-2xl", "bg-white/10", "border-white/20", "ring-1", "ring-white/10",
                "animate-[fadeIn_200ms_ease-out]", "animate-[scaleIn_200ms_ease-out]",
                "font-serif", "shadow-violet-500/25", "focus-visible:ring-offset-slate-950",
                "flex-col-reverse", "sm:flex-row"
            ],
            "accessibility_features": [
                "role=dialog with aria-modal",
                "aria-labelledby linking to title",
                "aria-describedby linking to description",
                "aria-label on close button",
                "Focus-visible rings on all interactive elements"
            ],
            "dark_mode_support": False,
            "design_notes": "Glassmorphic modal with luxury_editorial typography. Frosted glass panel (backdrop-blur-2xl) over dark overlay. Serif heading for elegance. Entry animations using @keyframes. Full ARIA dialog pattern."
        }
    },

    # -------------------------------------------------------------------------
    # 4. DATA TABLE (corporate, elite_corporate) - HIGH PRIORITY
    # -------------------------------------------------------------------------
    "data_table": {
        "input": {
            "component_type": "table",
            "theme": "corporate",
            "vibe": "elite_corporate",
            "context": "Financial transactions table for enterprise dashboard",
            "content_structure": {
                "columns": ["Transaction", "Amount", "Status", "Date"],
                "rows": 5,
            },
        },
        "output": {
            "design_thinking": "1. CONSTRAINT_CHECK: Table density 15+ ✓ | corporate = professional, clean ✓ | elite = precision, subtle ✓ "
                              "2. AESTHETIC_PHYSICS: Clean lines, subtle borders, alternating rows, fixed header "
                              "3. VISUAL_DNA: bg-white border border-slate-200 divide-y divide-slate-200 "
                              "4. MICRO_INTERACTIONS: Row hover bg-slate-50, sort button hover "
                              "5. RESPONSIVE_STRATEGY: Horizontal scroll on mobile with min-w-full "
                              "6. A11Y_CHECKLIST: scope=col/row, caption, role=table if custom "
                              "7. DENSITY_ITERATION: Added sticky header, status badges. Final: 16 classes",
            "component_id": "table_corporate_elite",
            "atomic_level": "organism",
            "html": '''<div class="w-full overflow-x-auto rounded-xl border border-slate-200 bg-white
                shadow-sm shadow-slate-900/5">
    <!-- Table Header with Actions -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200">
        <h3 class="text-lg font-semibold text-slate-900">Recent Transactions</h3>
        <div class="flex items-center gap-2">
            <button type="button" class="px-3 py-1.5 text-sm text-slate-600
                                         hover:text-slate-900 hover:bg-slate-100
                                         rounded-lg transition-colors duration-150
                                         focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none">
                Export
            </button>
            <button type="button" class="px-3 py-1.5 text-sm text-white bg-slate-900
                                         hover:bg-slate-800 rounded-lg
                                         transition-colors duration-150
                                         focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:outline-none">
                Add New
            </button>
        </div>
    </div>

    <table class="min-w-full divide-y divide-slate-200">
        <thead class="bg-slate-50/80">
            <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    <button type="button" class="group inline-flex items-center gap-1
                                                 hover:text-slate-900 transition-colors">
                        Transaction
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"/>
                        </svg>
                    </button>
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Amount
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Status
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Date
                </th>
                <th scope="col" class="relative px-6 py-3">
                    <span class="sr-only">Actions</span>
                </th>
            </tr>
        </thead>
        <tbody class="divide-y divide-slate-200 bg-white">
            <!-- Row 1 -->
            <tr class="hover:bg-slate-50 transition-colors duration-100">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-blue-100 text-blue-600
                                    flex items-center justify-center flex-shrink-0">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
                            </svg>
                        </div>
                        <div>
                            <div class="text-sm font-medium text-slate-900">Payment from Acme Corp</div>
                            <div class="text-sm text-slate-500">Invoice #INV-2024-001</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm font-semibold text-emerald-600">+$12,500.00</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                 bg-emerald-100 text-emerald-800">
                        Completed
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    Dec 24, 2024
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                    <button type="button" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg
                                                 hover:bg-slate-100 transition-colors duration-150
                                                 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"/>
                        </svg>
                    </button>
                </td>
            </tr>
            <!-- Row 2 -->
            <tr class="hover:bg-slate-50 transition-colors duration-100">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-violet-100 text-violet-600
                                    flex items-center justify-center flex-shrink-0">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div>
                            <div class="text-sm font-medium text-slate-900">Subscription Renewal</div>
                            <div class="text-sm text-slate-500">Enterprise Plan</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm font-semibold text-red-600">-$2,400.00</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                 bg-amber-100 text-amber-800">
                        Pending
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    Dec 23, 2024
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                    <button type="button" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg
                                                 hover:bg-slate-100 transition-colors duration-150
                                                 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"/>
                        </svg>
                    </button>
                </td>
            </tr>
            <!-- Row 3 -->
            <tr class="hover:bg-slate-50 transition-colors duration-100">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-emerald-100 text-emerald-600
                                    flex items-center justify-center flex-shrink-0">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div>
                            <div class="text-sm font-medium text-slate-900">Refund Processed</div>
                            <div class="text-sm text-slate-500">Order #ORD-8847</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm font-semibold text-red-600">-$340.00</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                 bg-emerald-100 text-emerald-800">
                        Completed
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    Dec 22, 2024
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                    <button type="button" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg
                                                 hover:bg-slate-100 transition-colors duration-150
                                                 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"/>
                        </svg>
                    </button>
                </td>
            </tr>
        </tbody>
    </table>

    <!-- Pagination -->
    <div class="flex items-center justify-between px-6 py-3 border-t border-slate-200 bg-slate-50/50">
        <p class="text-sm text-slate-500">
            Showing <span class="font-medium text-slate-700">1</span> to <span class="font-medium text-slate-700">3</span> of <span class="font-medium text-slate-700">248</span> results
        </p>
        <nav class="flex items-center gap-1" aria-label="Pagination">
            <button type="button" class="p-2 text-slate-400 rounded-lg
                                         hover:text-slate-600 hover:bg-slate-200
                                         disabled:opacity-50 disabled:cursor-not-allowed
                                         focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                                         transition-colors duration-150" disabled>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
            </button>
            <button type="button" class="px-3 py-1.5 text-sm font-medium text-white bg-slate-900 rounded-lg
                                         focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none">1</button>
            <button type="button" class="px-3 py-1.5 text-sm text-slate-600 rounded-lg
                                         hover:bg-slate-200
                                         focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                                         transition-colors duration-150">2</button>
            <button type="button" class="px-3 py-1.5 text-sm text-slate-600 rounded-lg
                                         hover:bg-slate-200
                                         focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                                         transition-colors duration-150">3</button>
            <span class="px-2 text-slate-400">...</span>
            <button type="button" class="px-3 py-1.5 text-sm text-slate-600 rounded-lg
                                         hover:bg-slate-200
                                         focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                                         transition-colors duration-150">83</button>
            <button type="button" class="p-2 text-slate-600 rounded-lg
                                         hover:text-slate-900 hover:bg-slate-200
                                         focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                                         transition-colors duration-150">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
            </button>
        </nav>
    </div>
</div>''',
            "tailwind_classes_used": [
                "divide-y", "divide-slate-200", "whitespace-nowrap", "scope=col",
                "uppercase", "tracking-wider", "sr-only", "rounded-full",
                "hover:bg-slate-50", "transition-colors", "disabled:opacity-50",
                "disabled:cursor-not-allowed", "overflow-x-auto"
            ],
            "accessibility_features": [
                "scope=col on header cells",
                "sr-only for visually hidden action label",
                "aria-label on pagination nav",
                "Focus-visible on all interactive elements",
                "disabled attribute with styling"
            ],
            "dark_mode_support": False,
            "design_notes": "Corporate data table with elite precision. Clean divide-y borders, sortable headers with icons, status badges, row hover states. Includes pagination with disabled states. Full responsive with overflow-x-auto."
        }
    },

    # -------------------------------------------------------------------------
    # 5. ALERT TOAST (neo-brutalism, playful_funny) - MEDIUM PRIORITY
    # -------------------------------------------------------------------------
    "alert_toast": {
        "input": {
            "component_type": "alert",
            "theme": "neo-brutalism",
            "vibe": "playful_funny",
            "context": "Success notification toast",
            "content_structure": {
                "type": "success",
                "message": "Your changes have been saved!",
                "icon": "checkmark",
            },
        },
        "output": {
            "design_thinking": "1. CONSTRAINT_CHECK: Alert density 8+ ✓ | neo-brutalism = bold colors, shadows ✓ | playful = emoji, bouncy ✓ "
                              "2. AESTHETIC_PHYSICS: Solid color block, thick border, offset shadow, slight rotation "
                              "3. VISUAL_DNA: bg-emerald-400 border-4 border-black shadow-[6px_6px_0px_0px_#000] "
                              "4. MICRO_INTERACTIONS: Entry slide-in + bounce, dismiss slide-out "
                              "5. RESPONSIVE_STRATEGY: Fixed width toast, centered on mobile, right-aligned on desktop "
                              "6. A11Y_CHECKLIST: role=alert, aria-live=polite "
                              "7. DENSITY_ITERATION: Added rotate-1 for playfulness. Final: 12 classes",
            "component_id": "alert_neobrutalist_playful",
            "atomic_level": "molecule",
            "html": '''<div class="fixed top-4 right-4 z-50 w-full max-w-sm
            animate-[slideIn_300ms_cubic-bezier(0.34,1.56,0.64,1)]"
     role="alert"
     aria-live="polite">
    <div class="flex items-center gap-4 p-4
                bg-emerald-400 border-4 border-black
                shadow-[6px_6px_0px_0px_#000]
                rotate-1
                transition-transform duration-150
                hover:rotate-0 hover:shadow-[8px_8px_0px_0px_#000] hover:translate-x-[-2px] hover:translate-y-[-2px]">

        <!-- Icon -->
        <div class="flex-shrink-0 w-10 h-10 rounded-full bg-black text-emerald-400
                    flex items-center justify-center
                    border-2 border-black">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
            </svg>
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0">
            <p class="text-sm font-black uppercase tracking-wide text-black">
                Woohoo! 🎉
            </p>
            <p class="mt-1 text-sm font-bold text-black/80">
                Your changes have been saved!
            </p>
        </div>

        <!-- Dismiss Button -->
        <button type="button"
                class="flex-shrink-0 p-2 rounded-full bg-black/10
                       hover:bg-black/20
                       focus-visible:ring-2 focus-visible:ring-black focus-visible:outline-none
                       transition-colors duration-150"
                aria-label="Dismiss notification">
            <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
        </button>
    </div>
</div>

<style>
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(100%) rotate(0deg);
    }
    to {
        opacity: 1;
        transform: translateX(0) rotate(1deg);
    }
}
</style>''',
            "tailwind_classes_used": [
                "rotate-1", "border-4", "shadow-[6px_6px_0px_0px_#000]",
                "font-black", "uppercase", "tracking-wide", "hover:rotate-0",
                "animate-[slideIn_300ms_cubic-bezier(0.34,1.56,0.64,1)]",
                "min-w-0", "flex-shrink-0"
            ],
            "accessibility_features": [
                "role=alert for screen readers",
                "aria-live=polite for non-intrusive announcement",
                "aria-label on dismiss button",
                "Focus-visible on dismiss"
            ],
            "dark_mode_support": False,
            "design_notes": "Neo-brutalist alert with playful rotation and bouncy entry animation. Solid emerald background with black borders and offset shadow. Emoji and uppercase text add personality."
        }
    },

    # -------------------------------------------------------------------------
    # 6. FOOTER MEGA (dark_mode_first, cyberpunk_edge) - MEDIUM PRIORITY
    # -------------------------------------------------------------------------
    "footer_mega": {
        "input": {
            "component_type": "footer",
            "theme": "dark_mode_first",
            "vibe": "cyberpunk_edge",
            "context": "Tech product footer with newsletter and social links",
            "content_structure": {
                "columns": ["Product", "Company", "Resources", "Legal"],
                "newsletter": True,
                "social": ["Twitter", "GitHub", "Discord"],
            },
        },
        "output": {
            "design_thinking": "1. CONSTRAINT_CHECK: Footer density 18+ ✓ | dark_mode_first = deep slate, glows ✓ | cyberpunk = neon accents ✓ "
                              "2. AESTHETIC_PHYSICS: Deep black base, cyan neon accents, grid pattern overlay, glow effects "
                              "3. VISUAL_DNA: bg-slate-950 before:bg-[grid-pattern] text-slate-400 "
                              "4. MICRO_INTERACTIONS: Link hover with glow text-shadow, button pulse "
                              "5. RESPONSIVE_STRATEGY: 4-col grid → 2-col → 1-col stack "
                              "6. A11Y_CHECKLIST: Semantic nav, aria-label on forms "
                              "7. DENSITY_ITERATION: Added scanline overlay + glow borders. Final: 20 classes on footer",
            "component_id": "footer_cyberpunk_dark",
            "atomic_level": "organism",
            "html": '''<footer class="relative bg-slate-950 text-slate-400 overflow-hidden">
    <!-- Grid Pattern Overlay -->
    <div class="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:40px_40px]"></div>

    <!-- Glow Accent -->
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-[128px] pointer-events-none"></div>
    <div class="absolute bottom-0 right-1/4 w-64 h-64 bg-fuchsia-500/10 rounded-full blur-[100px] pointer-events-none"></div>

    <div class="relative z-10 container mx-auto px-4 lg:px-8 py-16">
        <!-- Top Section -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 lg:gap-8">
            <!-- Brand Column -->
            <div class="lg:col-span-2">
                <a href="/" class="inline-flex items-center gap-2 text-white font-bold text-xl
                                  hover:[text-shadow:0_0_20px_rgba(6,182,212,0.5)]
                                  transition-all duration-300">
                    <svg class="w-8 h-8 text-cyan-400" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                    <span>NEXUS<span class="text-cyan-400">_</span>TECH</span>
                </a>
                <p class="mt-4 text-slate-500 leading-relaxed max-w-xs">
                    Building the future of decentralized infrastructure. Join 50,000+ developers.
                </p>

                <!-- Newsletter -->
                <form class="mt-6" aria-label="Newsletter signup">
                    <label for="newsletter-email" class="block text-xs uppercase tracking-wider text-slate-500 mb-2">
                        Subscribe to updates
                    </label>
                    <div class="flex">
                        <input
                            type="email"
                            id="newsletter-email"
                            name="email"
                            placeholder="you@example.com"
                            class="flex-1 px-4 py-2
                                   bg-slate-900/80 text-white text-sm
                                   border border-slate-700
                                   rounded-l-lg
                                   placeholder:text-slate-600
                                   focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50
                                   transition-colors duration-150"
                        />
                        <button type="submit"
                                class="px-4 py-2 bg-cyan-500 text-slate-950 text-sm font-semibold
                                       rounded-r-lg
                                       hover:bg-cyan-400 hover:shadow-[0_0_20px_rgba(6,182,212,0.4)]
                                       focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 focus-visible:outline-none
                                       transition-all duration-150">
                            Subscribe
                        </button>
                    </div>
                </form>
            </div>

            <!-- Link Columns -->
            <nav aria-label="Product links">
                <h4 class="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-4">Product</h4>
                <ul class="space-y-3">
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">Features</a></li>
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">Pricing</a></li>
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">Integrations</a></li>
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">Changelog</a></li>
                </ul>
            </nav>

            <nav aria-label="Company links">
                <h4 class="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-4">Company</h4>
                <ul class="space-y-3">
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">About</a></li>
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">Blog</a></li>
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">Careers</a></li>
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">Press</a></li>
                </ul>
            </nav>

            <nav aria-label="Resource links">
                <h4 class="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-4">Resources</h4>
                <ul class="space-y-3">
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">Documentation</a></li>
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">API Reference</a></li>
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">Community</a></li>
                    <li><a href="#" class="text-slate-400 hover:text-cyan-400 hover:[text-shadow:0_0_10px_rgba(6,182,212,0.5)] transition-all duration-150">Support</a></li>
                </ul>
            </nav>
        </div>

        <!-- Divider -->
        <div class="mt-12 pt-8 border-t border-slate-800/50">
            <div class="flex flex-col md:flex-row items-center justify-between gap-4">
                <!-- Copyright -->
                <p class="text-sm text-slate-600">
                    © 2024 NexusTech. All rights reserved.
                </p>

                <!-- Social Links -->
                <div class="flex items-center gap-4">
                    <a href="#" class="p-2 text-slate-500 rounded-lg
                                      hover:text-cyan-400 hover:bg-cyan-400/10
                                      focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:outline-none
                                      transition-all duration-150"
                       aria-label="Follow us on Twitter">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                        </svg>
                    </a>
                    <a href="#" class="p-2 text-slate-500 rounded-lg
                                      hover:text-cyan-400 hover:bg-cyan-400/10
                                      focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:outline-none
                                      transition-all duration-150"
                       aria-label="View our GitHub">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
                        </svg>
                    </a>
                    <a href="#" class="p-2 text-slate-500 rounded-lg
                                      hover:text-fuchsia-400 hover:bg-fuchsia-400/10
                                      focus-visible:ring-2 focus-visible:ring-fuchsia-500 focus-visible:outline-none
                                      transition-all duration-150"
                       aria-label="Join our Discord">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189z"/>
                        </svg>
                    </a>
                </div>

                <!-- Legal Links -->
                <div class="flex items-center gap-4 text-sm">
                    <a href="#" class="text-slate-500 hover:text-slate-300 transition-colors duration-150">Privacy</a>
                    <a href="#" class="text-slate-500 hover:text-slate-300 transition-colors duration-150">Terms</a>
                </div>
            </div>
        </div>
    </div>
</footer>''',
            "tailwind_classes_used": [
                "bg-slate-950", "bg-[linear-gradient(...)]", "blur-[128px]",
                "[text-shadow:0_0_20px_rgba(6,182,212,0.5)]",
                "focus:ring-cyan-500/50", "hover:shadow-[0_0_20px_rgba(6,182,212,0.4)]",
                "rounded-l-lg", "rounded-r-lg", "pointer-events-none",
                "hover:bg-cyan-400/10", "hover:bg-fuchsia-400/10"
            ],
            "accessibility_features": [
                "aria-label on nav elements",
                "aria-label on social links",
                "aria-label on newsletter form",
                "Focus-visible rings on all interactive elements",
                "Semantic nav elements"
            ],
            "dark_mode_support": True,
            "design_notes": "Cyberpunk footer with dark_mode_first approach. Deep slate-950 base with cyan neon accents and glow effects via text-shadow and box-shadow. Grid pattern overlay and blurred glow orbs create depth. Full responsive 5→2→1 column grid."
        }
    },

    # ============================================================================
    # THEME COVERAGE EXAMPLES (Phase 2.2)
    # Purpose: Demonstrate theme-specific design patterns for underrepresented themes
    # ============================================================================

    "brutalist_button": {
        "input": {
            "component_type": "button",
            "theme": "brutalist",
            "vibe": "cyberpunk_edge",
            "context": "Bold primary action button for a design agency portfolio",
            "content_structure": {
                "text": "VIEW WORKS",
                "icon": "arrow-right",
            },
        },
        "output": {
            "design_thinking": "1. CONSTRAINT_CHECK: Button density 14+ ✓ | brutalist = raw, sharp, intentionally rough ✓ | cyberpunk_edge = maximum contrast ✓ "
                              "2. AESTHETIC_PHYSICS: Raw concrete texture, harsh shadows, no rounded corners (brutalism rejects softness), thick borders "
                              "3. VISUAL_DNA: bg-black text-white border-4 border-white font-black tracking-widest uppercase "
                              "4. MICRO_INTERACTIONS: Jarring invert on hover (bg-white text-black), translate-x offset for 'broken' feel "
                              "5. RESPONSIVE_STRATEGY: Full-width on mobile, inline-flex on desktop "
                              "6. A11Y_CHECKLIST: High contrast by design, focus-visible with thick outline, aria-label "
                              "7. DENSITY_ITERATION: Adding glitch pseudo-element offset + noise texture. Final: 16 classes",
            "component_id": "btn_brutalist_agency",
            "atomic_level": "atom",
            "html": '''<button class="group relative inline-flex items-center justify-center gap-3
                               px-8 py-4
                               bg-black text-white
                               border-4 border-white
                               font-black text-sm tracking-[0.3em] uppercase
                               transition-all duration-100
                               hover:bg-white hover:text-black hover:translate-x-1 hover:-translate-y-1
                               hover:shadow-[-4px_4px_0_0_#000]
                               active:translate-x-0 active:translate-y-0 active:shadow-none
                               focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-white focus-visible:ring-offset-4 focus-visible:ring-offset-black"
        aria-label="View our portfolio works">
    <!-- Glitch Layer (offset pseudo) -->
    <span class="absolute inset-0 border-4 border-red-500 opacity-0 translate-x-1 -translate-y-1
                 group-hover:opacity-100 pointer-events-none transition-opacity duration-75"></span>

    <span class="relative z-10">VIEW WORKS</span>

    <!-- Arrow Icon -->
    <svg class="w-5 h-5 relative z-10 transition-transform duration-100 group-hover:translate-x-1"
         fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
        <path stroke-linecap="square" d="M5 12h14M12 5l7 7-7 7"/>
    </svg>
</button>''',
            "tailwind_classes_used": [
                "border-4", "border-white", "tracking-[0.3em]", "uppercase",
                "font-black", "hover:translate-x-1", "hover:-translate-y-1",
                "hover:shadow-[-4px_4px_0_0_#000]", "active:shadow-none",
                "focus-visible:ring-offset-4", "stroke-width-3"
            ],
            "accessibility_features": [
                "aria-label for screen readers",
                "focus-visible:ring-4 with ring-offset",
                "High contrast by default (black/white)",
                "Active state feedback"
            ],
            "dark_mode_support": False,  # Brutalist uses absolute black/white
            "design_notes": "Brutalist button with intentionally harsh aesthetics. No rounded corners (border-radius zero), thick 4px borders, jarring hover inversion with offset shadow creating 'broken' 3D effect. Red glitch pseudo-element adds cyberpunk edge. Contrast ratio ~21:1 (maximum)."
        }
    },

    "glassmorphism_card": {
        "input": {
            "component_type": "card",
            "theme": "glassmorphism",
            "vibe": "luxury_editorial",
            "context": "Premium membership tier card for a luxury service",
            "content_structure": {
                "tier": "PLATINUM",
                "price": "$299/month",
                "features": ["Priority Support", "Unlimited Access", "Exclusive Events", "Personal Concierge"],
                "cta": "Upgrade Now",
            },
        },
        "output": {
            "design_thinking": "1. CONSTRAINT_CHECK: Card density 16+ ✓ | glassmorphism = frosted glass, transparency layers ✓ | luxury_editorial = serif accents, generous whitespace ✓ "
                              "2. AESTHETIC_PHYSICS: 4-layer glass - gradient backdrop, blur, inner glow, subtle border. Light source from top-left. "
                              "3. VISUAL_DNA: bg-white/10 backdrop-blur-xl border-white/20 shadow-2xl "
                              "4. MICRO_INTERACTIONS: Card lift with shadow expansion, inner shine sweep on hover "
                              "5. RESPONSIVE_STRATEGY: Max-w-sm centered, responsive padding "
                              "6. A11Y_CHECKLIST: Text contrast maintained on blur, focus-visible on CTA "
                              "7. DENSITY_ITERATION: Adding gradient border glow + floating badge. Final: 18 classes on container",
            "component_id": "card_glass_premium",
            "atomic_level": "molecule",
            "html": '''<article class="group relative max-w-sm mx-auto">
    <!-- Outer Glow Border -->
    <div class="absolute -inset-0.5 bg-gradient-to-br from-amber-200/50 via-white/30 to-amber-200/50
                rounded-3xl blur-sm opacity-75 group-hover:opacity-100 transition-opacity duration-500"></div>

    <!-- Main Glass Card -->
    <div class="relative flex flex-col
                bg-white/10 backdrop-blur-xl
                border border-white/20
                rounded-3xl
                p-8
                shadow-2xl shadow-black/10
                transition-all duration-500
                group-hover:-translate-y-2 group-hover:shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)]
                overflow-hidden">

        <!-- Inner Shine Sweep -->
        <div class="absolute inset-0 bg-gradient-to-br from-white/20 via-transparent to-transparent
                    opacity-0 group-hover:opacity-100
                    -translate-x-full group-hover:translate-x-full
                    transition-all duration-1000 ease-out pointer-events-none"></div>

        <!-- Floating Badge -->
        <div class="absolute -top-3 -right-3 px-4 py-1.5
                    bg-gradient-to-r from-amber-400 to-amber-500
                    text-amber-950 text-xs font-bold tracking-wider uppercase
                    rounded-full shadow-lg
                    rotate-12">
            POPULAR
        </div>

        <!-- Header -->
        <div class="relative z-10 text-center mb-6">
            <span class="text-amber-300/80 text-xs font-semibold tracking-[0.25em] uppercase">Membership</span>
            <h3 class="mt-2 text-white text-3xl font-serif font-light tracking-wide">PLATINUM</h3>
        </div>

        <!-- Price -->
        <div class="relative z-10 text-center mb-8">
            <span class="text-white/60 text-sm">Starting at</span>
            <div class="flex items-baseline justify-center gap-1">
                <span class="text-5xl font-light text-white">$299</span>
                <span class="text-white/50 text-lg">/month</span>
            </div>
        </div>

        <!-- Features List -->
        <ul class="relative z-10 space-y-4 mb-8">
            <li class="flex items-center gap-3 text-white/80">
                <svg class="w-5 h-5 text-amber-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                <span>Priority 24/7 Support</span>
            </li>
            <li class="flex items-center gap-3 text-white/80">
                <svg class="w-5 h-5 text-amber-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                <span>Unlimited Platform Access</span>
            </li>
            <li class="flex items-center gap-3 text-white/80">
                <svg class="w-5 h-5 text-amber-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                <span>Exclusive Members Events</span>
            </li>
            <li class="flex items-center gap-3 text-white/80">
                <svg class="w-5 h-5 text-amber-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                <span>Personal Concierge Service</span>
            </li>
        </ul>

        <!-- CTA Button -->
        <button class="relative z-10 w-full py-4
                       bg-gradient-to-r from-amber-400 to-amber-500
                       text-amber-950 font-semibold text-sm tracking-wide
                       rounded-xl
                       shadow-lg shadow-amber-500/30
                       transition-all duration-300
                       hover:shadow-xl hover:shadow-amber-500/40 hover:scale-[1.02]
                       active:scale-[0.98]
                       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent">
            Upgrade Now
        </button>

        <!-- Footer Note -->
        <p class="relative z-10 mt-4 text-center text-white/40 text-xs">
            Cancel anytime. No commitment.
        </p>
    </div>
</article>''',
            "tailwind_classes_used": [
                "bg-white/10", "backdrop-blur-xl", "border-white/20",
                "shadow-2xl", "shadow-black/10", "rounded-3xl",
                "group-hover:-translate-y-2", "group-hover:shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)]",
                "from-amber-200/50", "via-white/30", "font-serif",
                "-translate-x-full", "group-hover:translate-x-full"
            ],
            "accessibility_features": [
                "Semantic article element",
                "Focus-visible on CTA with ring-offset",
                "Text contrast maintained over blur (white text on dark blur)",
                "Active state feedback"
            ],
            "dark_mode_support": True,  # Works on dark backgrounds
            "design_notes": "Premium glassmorphism card with 4-layer depth: outer gradient glow, frosted glass container, inner shine sweep animation, and floating badge. Uses amber accent palette for luxury feel. Font-serif on headings adds editorial elegance. The shine sweep effect uses translate-x animation on hover."
        }
    },

    "retro_hero": {
        "input": {
            "component_type": "hero",
            "theme": "retro",
            "vibe": "playful_funny",
            "context": "Landing hero for a retro-themed arcade game launcher",
            "content_structure": {
                "headline": "GAME ON!",
                "subheadline": "Classic arcade vibes. Modern multiplayer.",
                "cta_primary": "START PLAYING",
                "cta_secondary": "Watch Trailer",
            },
        },
        "output": {
            "design_thinking": "1. CONSTRAINT_CHECK: Hero density 30+ ✓ | retro = 80s neon, CRT scanlines, pixel aesthetic ✓ | playful_funny = bouncy, energetic ✓ "
                              "2. AESTHETIC_PHYSICS: CRT monitor glow, scanline overlay, chromatic aberration text, grid floor perspective "
                              "3. VISUAL_DNA: bg-slate-950 text-cyan-400 font-mono tracking-widest, neon pink/cyan palette "
                              "4. MICRO_INTERACTIONS: Text flicker, button glow pulse, hover bounce "
                              "5. RESPONSIVE_STRATEGY: Centered stack, padding adjusts per breakpoint "
                              "6. A11Y_CHECKLIST: prefers-reduced-motion check for animations, focus-visible states "
                              "7. DENSITY_ITERATION: Adding animated grid, floating pixels, chromatic text. Final: 32 classes on container",
            "component_id": "hero_retro_arcade",
            "atomic_level": "organism",
            "html": '''<section class="relative min-h-screen flex items-center justify-center
                                bg-slate-950 overflow-hidden">
    <!-- Animated Grid Floor -->
    <div class="absolute inset-0 bg-[linear-gradient(transparent_0%,rgba(6,182,212,0.05)_50%,rgba(6,182,212,0.1)_100%)]">
        <div class="absolute inset-0 bg-[linear-gradient(90deg,transparent_calc(100%-1px),rgba(6,182,212,0.15)_calc(100%-1px)),linear-gradient(transparent_calc(100%-1px),rgba(6,182,212,0.15)_calc(100%-1px))]
                    bg-[size:60px_60px]
                    [perspective:500px] [transform-style:preserve-3d] [transform:rotateX(60deg)_translateY(200px)]
                    origin-bottom"></div>
    </div>

    <!-- Floating Pixel Decorations -->
    <div class="absolute top-20 left-10 w-4 h-4 bg-pink-500 animate-bounce [animation-delay:0ms]"></div>
    <div class="absolute top-40 right-20 w-3 h-3 bg-cyan-400 animate-bounce [animation-delay:200ms]"></div>
    <div class="absolute bottom-40 left-1/4 w-2 h-2 bg-yellow-400 animate-bounce [animation-delay:400ms]"></div>
    <div class="absolute top-1/3 right-1/3 w-3 h-3 bg-green-400 animate-bounce [animation-delay:600ms]"></div>

    <!-- Scanline Overlay -->
    <div class="absolute inset-0 pointer-events-none
                bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(0,0,0,0.1)_2px,rgba(0,0,0,0.1)_4px)]
                opacity-50"></div>

    <!-- Neon Glow Orbs -->
    <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-pink-500/20 rounded-full blur-[100px]"></div>
    <div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-cyan-500/20 rounded-full blur-[80px]"></div>

    <!-- Content -->
    <div class="relative z-10 text-center px-4 sm:px-6 lg:px-8">
        <!-- Chromatic Aberration Title -->
        <h1 class="relative text-6xl sm:text-7xl md:text-8xl lg:text-9xl font-black font-mono tracking-wider">
            <span class="absolute inset-0 text-pink-500 blur-[2px] translate-x-1 translate-y-0.5 opacity-70"
                  aria-hidden="true">GAME ON!</span>
            <span class="absolute inset-0 text-cyan-400 blur-[2px] -translate-x-1 -translate-y-0.5 opacity-70"
                  aria-hidden="true">GAME ON!</span>
            <span class="relative text-white [text-shadow:0_0_30px_rgba(6,182,212,0.8),0_0_60px_rgba(236,72,153,0.5)]">
                GAME ON!
            </span>
        </h1>

        <!-- Subtitle -->
        <p class="mt-6 text-lg sm:text-xl text-slate-400 font-mono tracking-wide max-w-xl mx-auto">
            Classic arcade vibes.
            <span class="text-cyan-400">Modern multiplayer.</span>
        </p>

        <!-- CTA Buttons -->
        <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <!-- Primary CTA -->
            <button class="group relative px-8 py-4
                           bg-gradient-to-r from-pink-500 to-pink-600
                           text-white font-bold font-mono tracking-widest uppercase text-sm
                           rounded-none border-2 border-pink-400
                           shadow-[0_0_20px_rgba(236,72,153,0.5),inset_0_1px_0_rgba(255,255,255,0.2)]
                           transition-all duration-150
                           hover:shadow-[0_0_40px_rgba(236,72,153,0.8),inset_0_1px_0_rgba(255,255,255,0.3)]
                           hover:scale-105
                           active:scale-95
                           focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pink-400 focus-visible:ring-offset-4 focus-visible:ring-offset-slate-950
                           motion-safe:animate-pulse [animation-duration:2s]">
                <span class="relative z-10 flex items-center gap-2">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"/>
                    </svg>
                    START PLAYING
                </span>
            </button>

            <!-- Secondary CTA -->
            <button class="px-8 py-4
                           bg-transparent
                           text-cyan-400 font-bold font-mono tracking-widest uppercase text-sm
                           border-2 border-cyan-400/50
                           rounded-none
                           transition-all duration-150
                           hover:bg-cyan-400/10 hover:border-cyan-400
                           hover:[text-shadow:0_0_10px_rgba(6,182,212,0.8)]
                           active:scale-95
                           focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-4 focus-visible:ring-offset-slate-950">
                Watch Trailer
            </button>
        </div>

        <!-- Insert Coin Text (Easter Egg) -->
        <p class="mt-16 text-slate-600 font-mono text-sm tracking-widest uppercase animate-pulse">
            INSERT COIN TO CONTINUE
        </p>
    </div>
</section>''',
            "tailwind_classes_used": [
                "font-mono", "tracking-widest", "blur-[100px]", "blur-[2px]",
                "bg-[linear-gradient(...)]", "bg-[size:60px_60px]",
                "[perspective:500px]", "[transform-style:preserve-3d]", "[transform:rotateX(60deg)_translateY(200px)]",
                "bg-[repeating-linear-gradient(...)]", "animate-bounce", "[animation-delay:200ms]",
                "[text-shadow:0_0_30px...]", "shadow-[0_0_20px_rgba(236,72,153,0.5),inset_0_1px_0_rgba(255,255,255,0.2)]",
                "motion-safe:animate-pulse", "rounded-none"
            ],
            "accessibility_features": [
                "aria-hidden on decorative chromatic text",
                "Focus-visible with ring-offset",
                "motion-safe: prefix for animations (respects prefers-reduced-motion)",
                "High contrast text with glow"
            ],
            "dark_mode_support": True,  # Designed for dark background
            "design_notes": "Retro 80s arcade hero with full visual treatment: CRT scanlines via repeating-linear-gradient, perspective grid floor, chromatic aberration text effect using layered blurred text, floating pixel decorations with staggered bounce animation. Uses motion-safe: for accessibility. Pink/cyan neon palette typical of 80s aesthetic."
        }
    },

    "high_contrast_form": {
        "input": {
            "component_type": "form",
            "theme": "high_contrast",
            "vibe": "elite_corporate",
            "context": "Contact form for a government accessibility-compliant website",
            "content_structure": {
                "fields": ["Full Name", "Email Address", "Subject", "Message"],
                "submit": "Send Message",
                "required_indicator": True,
            },
        },
        "output": {
            "design_thinking": "1. CONSTRAINT_CHECK: Form density 12+ ✓ | high_contrast = WCAG AAA (7:1+), no subtle effects ✓ | elite_corporate = clean, professional ✓ "
                              "2. AESTHETIC_PHYSICS: Maximum legibility, thick focus rings, clear visual hierarchy, no decorative elements "
                              "3. VISUAL_DNA: bg-white text-slate-900 border-2 border-slate-900 focus:ring-4 "
                              "4. MICRO_INTERACTIONS: Thick underline focus, clear active states, no subtle hover "
                              "5. RESPONSIVE_STRATEGY: Single column stack, generous touch targets (44px min) "
                              "6. A11Y_CHECKLIST: WCAG AAA compliance, aria-required, aria-describedby for errors, visible labels, 7:1+ contrast "
                              "7. DENSITY_ITERATION: All essential - no trimming for accessibility. Final: 14 classes per input",
            "component_id": "form_a11y_contact",
            "atomic_level": "organism",
            "html": '''<form class="w-full max-w-lg mx-auto p-8 bg-white" novalidate>
    <h2 class="text-2xl font-bold text-slate-900 mb-2">Contact Us</h2>
    <p class="text-slate-700 mb-8">Fields marked with <span class="text-red-700 font-bold">*</span> are required.</p>

    <div class="space-y-6">
        <!-- Full Name -->
        <div>
            <label for="full-name" class="block text-sm font-bold text-slate-900 mb-2">
                Full Name <span class="text-red-700" aria-hidden="true">*</span>
            </label>
            <input
                type="text"
                id="full-name"
                name="full_name"
                required
                aria-required="true"
                autocomplete="name"
                class="w-full px-4 py-3
                       text-slate-900 text-base
                       bg-white
                       border-2 border-slate-900
                       focus:outline-none focus:ring-4 focus:ring-blue-700 focus:border-blue-700
                       placeholder:text-slate-500"
                placeholder="Enter your full name"
            />
        </div>

        <!-- Email Address -->
        <div>
            <label for="email" class="block text-sm font-bold text-slate-900 mb-2">
                Email Address <span class="text-red-700" aria-hidden="true">*</span>
            </label>
            <input
                type="email"
                id="email"
                name="email"
                required
                aria-required="true"
                autocomplete="email"
                class="w-full px-4 py-3
                       text-slate-900 text-base
                       bg-white
                       border-2 border-slate-900
                       focus:outline-none focus:ring-4 focus:ring-blue-700 focus:border-blue-700
                       placeholder:text-slate-500"
                placeholder="you@example.com"
            />
        </div>

        <!-- Subject -->
        <div>
            <label for="subject" class="block text-sm font-bold text-slate-900 mb-2">
                Subject <span class="text-red-700" aria-hidden="true">*</span>
            </label>
            <select
                id="subject"
                name="subject"
                required
                aria-required="true"
                class="w-full px-4 py-3
                       text-slate-900 text-base
                       bg-white
                       border-2 border-slate-900
                       focus:outline-none focus:ring-4 focus:ring-blue-700 focus:border-blue-700
                       cursor-pointer">
                <option value="">Select a subject</option>
                <option value="general">General Inquiry</option>
                <option value="support">Technical Support</option>
                <option value="feedback">Feedback</option>
                <option value="accessibility">Accessibility Concern</option>
            </select>
        </div>

        <!-- Message -->
        <div>
            <label for="message" class="block text-sm font-bold text-slate-900 mb-2">
                Message <span class="text-red-700" aria-hidden="true">*</span>
            </label>
            <textarea
                id="message"
                name="message"
                required
                aria-required="true"
                rows="5"
                class="w-full px-4 py-3
                       text-slate-900 text-base
                       bg-white
                       border-2 border-slate-900
                       focus:outline-none focus:ring-4 focus:ring-blue-700 focus:border-blue-700
                       placeholder:text-slate-500
                       resize-y min-h-[120px]"
                placeholder="How can we help you?"
            ></textarea>
        </div>

        <!-- Submit Button -->
        <div class="pt-4">
            <button
                type="submit"
                class="w-full px-6 py-4
                       bg-slate-900 text-white text-base font-bold
                       border-2 border-slate-900
                       transition-colors duration-150
                       hover:bg-slate-700 hover:border-slate-700
                       focus:outline-none focus:ring-4 focus:ring-blue-700 focus:ring-offset-2 focus:ring-offset-white
                       active:bg-slate-800
                       disabled:bg-slate-400 disabled:border-slate-400 disabled:cursor-not-allowed">
                Send Message
            </button>
        </div>
    </div>

    <!-- Privacy Note -->
    <p class="mt-6 text-sm text-slate-700">
        By submitting this form, you agree to our
        <a href="/privacy" class="text-blue-800 font-bold underline underline-offset-2
                                  hover:text-blue-600
                                  focus:outline-none focus:ring-2 focus:ring-blue-700">
            Privacy Policy
        </a>.
    </p>
</form>''',
            "tailwind_classes_used": [
                "border-2", "border-slate-900", "focus:ring-4", "focus:ring-blue-700",
                "text-red-700", "font-bold", "underline", "underline-offset-2",
                "focus:ring-offset-2", "focus:ring-offset-white",
                "disabled:bg-slate-400", "disabled:cursor-not-allowed",
                "resize-y", "min-h-[120px]"
            ],
            "accessibility_features": [
                "WCAG AAA compliant contrast (>7:1)",
                "aria-required='true' on all required fields",
                "aria-hidden on decorative asterisks",
                "Visible focus rings (4px blue-700)",
                "Focus ring offset for visibility",
                "Semantic form structure with labels",
                "autocomplete attributes for autofill",
                "Disabled state styling",
                "Underlined links with offset",
                "Min 44px touch targets (py-3 = 48px)",
                "novalidate for custom validation handling"
            ],
            "dark_mode_support": False,  # High contrast mode uses fixed black/white
            "design_notes": "WCAG AAA compliant form with maximum accessibility. Uses 2px borders and 4px focus rings for clear visual feedback. Contrast ratio: slate-900 on white = ~15:1 (exceeds AAA). All interactive elements have 44px+ touch targets. No decorative elements that could distract from functionality. Red-700 used for required indicators (still AAA compliant on white)."
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


# =============================================================================
# BAD_EXAMPLES: Negative Examples for Anti-Laziness Training
# =============================================================================
# Research shows negative examples reduce weakness density by 59-64%
# Source: https://www.endorlabs.com/learn/anti-pattern-avoidance-a-simple-prompt-pattern-for-safer-ai-generated-code
#
# These examples teach Gemini what NOT to produce, dramatically improving output quality.

BAD_EXAMPLES: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # BAD EXAMPLE 1: Lazy Button (Missing Interactions)
    # -------------------------------------------------------------------------
    "lazy_button": {
        "problem": "Only 4 Tailwind classes - missing all interaction states",
        "bad_output": """<button class="px-4 py-2 bg-blue-600 text-white">
  Click Me
</button>""",
        "why_bad": [
            "❌ NO shadow (missing: shadow-lg shadow-blue-500/25)",
            "❌ NO hover state (missing: hover:bg-blue-700 hover:shadow-xl hover:-translate-y-0.5)",
            "❌ NO active state (missing: active:scale-[0.98] active:shadow-md)",
            "❌ NO focus ring (missing: focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2)",
            "❌ NO transition (missing: transition-all duration-200)",
            "❌ NO border-radius refinement (missing: rounded-xl)",
            "❌ NO typography polish (missing: font-semibold tracking-wide)",
            "Class count: 4 (UNACCEPTABLE - minimum is 10)",
        ],
        "good_alternative": """<button class="
  px-6 py-3
  bg-gradient-to-r from-blue-600 to-blue-700
  text-white font-semibold tracking-wide
  rounded-xl
  shadow-lg shadow-blue-500/25
  hover:from-blue-700 hover:to-blue-800
  hover:shadow-xl hover:shadow-blue-500/30
  hover:-translate-y-0.5
  active:scale-[0.98] active:shadow-md
  focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 focus-visible:outline-none
  transition-all duration-200 ease-out
  disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0
">
  Click Me
</button>""",
        "class_count_good": 24,
    },
    # -------------------------------------------------------------------------
    # BAD EXAMPLE 2: Missing 4-Layer Rule (Flat Container)
    # -------------------------------------------------------------------------
    "missing_4_layer": {
        "problem": "Container without visual depth - violates 4-Layer Rule",
        "bad_output": """<div class="bg-slate-900 rounded-lg p-6">
  <h3 class="text-white text-lg">Card Title</h3>
  <p class="text-gray-400">Card description text here.</p>
</div>""",
        "why_bad": [
            "❌ LAYER 1 missing: No gradient base (should be: bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900)",
            "❌ LAYER 2 missing: No mesh/blob overlay (should be: before:absolute before:bg-gradient-radial)",
            "❌ LAYER 3 missing: No texture/noise (should be: after:bg-[url('noise.svg')] after:opacity-[0.02])",
            "❌ LAYER 4 missing: No glass/sheen (should be: backdrop-blur ring-1 ring-white/5)",
            "❌ NO shadow stack (should be: shadow-xl shadow-black/20)",
            "❌ NO inner ring (should be: ring-inset ring-white/10)",
            "❌ NO hover states on container",
            "Depth score: 1/4 (UNACCEPTABLE)",
        ],
        "good_alternative": """<div class="
  relative overflow-hidden
  bg-gradient-to-br from-slate-900 via-slate-800/95 to-slate-900
  rounded-2xl p-6
  shadow-xl shadow-black/20
  ring-1 ring-white/10
  backdrop-blur-sm
  group
  hover:ring-white/20 hover:shadow-2xl
  transition-all duration-300
  before:absolute before:inset-0 before:-z-10
  before:bg-[radial-gradient(ellipse_at_top_right,rgba(59,130,246,0.1),transparent_70%)]
  after:absolute after:inset-0 after:-z-10
  after:bg-[url('data:image/svg+xml,...')] after:opacity-[0.02]
">
  <h3 class="text-white text-lg font-semibold tracking-tight">Card Title</h3>
  <p class="text-slate-400 mt-2 leading-relaxed">Card description text here.</p>
</div>""",
        "layer_count_good": 4,
    },
    # -------------------------------------------------------------------------
    # BAD EXAMPLE 3: Broken Accessibility (Invisible to Screen Readers)
    # -------------------------------------------------------------------------
    "broken_accessibility": {
        "problem": "Input field with critical accessibility failures",
        "bad_output": """<input type="email" class="bg-gray-200 text-gray-400 px-3 py-2 rounded" placeholder="Email">""",
        "why_bad": [
            "❌ NO label association (needs: <label for='email'>)",
            "❌ NO focus-visible ring (needs: focus-visible:ring-2 focus-visible:ring-blue-500)",
            "❌ CONTRAST FAILURE: text-gray-400 on bg-gray-200 = 2.5:1 (needs 4.5:1 minimum)",
            "❌ NO aria-describedby for error states",
            "❌ NO required attribute indication",
            "❌ NO placeholder styling (needs: placeholder:text-gray-500)",
            "❌ NO disabled state styling",
            "❌ NO invalid state styling (needs: invalid:ring-red-500 invalid:ring-2)",
            "WCAG violations: 1.4.3, 2.4.6, 3.3.2",
        ],
        "good_alternative": """<div class="relative">
  <label
    for="email-input"
    class="block text-sm font-medium text-slate-300 mb-2"
  >
    Email Address
    <span class="text-red-400 ml-1" aria-hidden="true">*</span>
  </label>
  <input
    type="email"
    id="email-input"
    name="email"
    required
    aria-required="true"
    aria-describedby="email-hint email-error"
    class="
      w-full px-4 py-3
      bg-slate-800/50 text-white
      border border-slate-600
      rounded-xl
      placeholder:text-slate-500
      focus:outline-none
      focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:border-transparent
      hover:border-slate-500
      invalid:ring-2 invalid:ring-red-500 invalid:border-transparent
      disabled:opacity-50 disabled:cursor-not-allowed
      transition-all duration-200
    "
    placeholder="you@example.com"
  />
  <p id="email-hint" class="mt-2 text-sm text-slate-500">
    We'll never share your email.
  </p>
</div>""",
        "wcag_compliance": "AA",
    },
    # -------------------------------------------------------------------------
    # BAD EXAMPLE 4: Truncated Code (Anti-Laziness Violation)
    # -------------------------------------------------------------------------
    "truncated_code": {
        "problem": "Code with '// ... more items' or 'etc.' placeholders",
        "bad_output": """<nav class="flex gap-4">
  <a href="#">Home</a>
  <a href="#">About</a>
  <!-- ... more items -->
</nav>""",
        "why_bad": [
            "❌ PLACEHOLDER DETECTED: '<!-- ... more items -->' is NEVER acceptable",
            "❌ Links have no styling (needs: hover states, focus states)",
            "❌ No aria-current for active link",
            "❌ No responsive behavior defined",
            "This violates the Anti-Laziness Protocol",
        ],
        "good_alternative": """<nav class="flex items-center gap-1" role="navigation" aria-label="Main">
  <a
    href="#"
    aria-current="page"
    class="
      px-4 py-2 rounded-lg
      text-white font-medium
      bg-white/10
      hover:bg-white/15
      focus-visible:ring-2 focus-visible:ring-white/50 focus-visible:outline-none
      transition-colors duration-150
    "
  >
    Home
  </a>
  <a
    href="#"
    class="
      px-4 py-2 rounded-lg
      text-slate-300
      hover:text-white hover:bg-white/10
      focus-visible:ring-2 focus-visible:ring-white/50 focus-visible:outline-none
      transition-colors duration-150
    "
  >
    About
  </a>
  <a
    href="#"
    class="
      px-4 py-2 rounded-lg
      text-slate-300
      hover:text-white hover:bg-white/10
      focus-visible:ring-2 focus-visible:ring-white/50 focus-visible:outline-none
      transition-colors duration-150
    "
  >
    Services
  </a>
  <a
    href="#"
    class="
      px-4 py-2 rounded-lg
      text-slate-300
      hover:text-white hover:bg-white/10
      focus-visible:ring-2 focus-visible:ring-white/50 focus-visible:outline-none
      transition-colors duration-150
    "
  >
    Contact
  </a>
</nav>""",
        "note": "ALL items must be fully rendered - no placeholders ever",
    },
    # -------------------------------------------------------------------------
    # BAD EXAMPLE 5: No Dark Mode Variants (Half-Implementation)
    # -------------------------------------------------------------------------
    "missing_dark_mode": {
        "problem": "Component without dark: variants despite dark_mode=True",
        "bad_output": """<div class="bg-white text-gray-900 p-6 rounded-lg shadow">
  <h2 class="text-xl font-bold">Title</h2>
  <p class="text-gray-600">Description</p>
</div>""",
        "why_bad": [
            "❌ NO dark:bg-* variant (needs: dark:bg-slate-800)",
            "❌ NO dark:text-* variant (needs: dark:text-white)",
            "❌ NO dark:shadow-* variant (needs: dark:shadow-black/25)",
            "❌ NO dark:ring-* variant (needs: dark:ring-white/10)",
            "When dark_mode=True, EVERY color class needs a dark: variant",
        ],
        "good_alternative": """<div class="
  bg-white dark:bg-slate-800
  text-gray-900 dark:text-white
  p-6 rounded-xl
  shadow-lg dark:shadow-black/25
  ring-1 ring-gray-200 dark:ring-white/10
  transition-colors duration-200
">
  <h2 class="text-xl font-bold tracking-tight">Title</h2>
  <p class="text-gray-600 dark:text-slate-400 mt-2">Description</p>
</div>""",
        "note": "Every bg, text, shadow, ring, and border needs dark: variant",
    },
}


# =============================================================================
# CREATIVITY ENHANCEMENT: Vibe Example Exports
# =============================================================================
# These exports provide easy access to vibe-specific few-shot examples
# for use in tests and prompt construction.

CYBERPUNK_EDGE_EXAMPLE: Dict[str, Any] = {
    "component_type": COMPONENT_EXAMPLES["cyberpunk_neural_card"]["input"]["component_type"],
    "vibe": COMPONENT_EXAMPLES["cyberpunk_neural_card"]["input"]["vibe"],
    "html": COMPONENT_EXAMPLES["cyberpunk_neural_card"]["output"]["html"],
    "design_notes": COMPONENT_EXAMPLES["cyberpunk_neural_card"]["output"]["design_notes"],
}

LUXURY_EDITORIAL_EXAMPLE: Dict[str, Any] = {
    "component_type": COMPONENT_EXAMPLES["luxury_article_card"]["input"]["component_type"],
    "vibe": COMPONENT_EXAMPLES["luxury_article_card"]["input"]["vibe"],
    "html": COMPONENT_EXAMPLES["luxury_article_card"]["output"]["html"],
    "design_notes": COMPONENT_EXAMPLES["luxury_article_card"]["output"]["design_notes"],
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


def get_bad_examples_for_prompt(
    component_type: Optional[str] = None,
    max_examples: int = 3,
) -> str:
    """Generate negative examples (BAD_EXAMPLES) formatted for inclusion in prompts.

    Research shows negative examples reduce weakness density by 59-64%.
    These examples teach Gemini what NOT to produce.

    Args:
        component_type: Optional - if provided, prioritizes relevant bad examples.
        max_examples: Maximum number of bad examples to include (default: 3).

    Returns:
        Formatted string with bad examples.
    """
    # Relevance mapping: which bad examples are most relevant for which components
    relevance_map: Dict[str, List[str]] = {
        "button": ["lazy_button", "broken_accessibility", "missing_dark_mode"],
        "card": ["missing_4_layer", "missing_dark_mode", "broken_accessibility"],
        "input": ["broken_accessibility", "missing_dark_mode", "lazy_button"],
        "form": ["broken_accessibility", "truncated_code", "missing_dark_mode"],
        "navbar": ["truncated_code", "broken_accessibility", "missing_4_layer"],
        "hero": ["missing_4_layer", "truncated_code", "missing_dark_mode"],
        "footer": ["truncated_code", "missing_dark_mode", "broken_accessibility"],
    }

    # Select which bad examples to include
    if component_type and component_type in relevance_map:
        selected_keys = relevance_map[component_type][:max_examples]
    else:
        # Default selection for general usage
        selected_keys = ["lazy_button", "missing_4_layer", "broken_accessibility"][:max_examples]

    # Build formatted output
    lines = [
        "## ❌ ANTI-PATTERNS: What NOT to Generate",
        "",
        "The following examples demonstrate UNACCEPTABLE output. Study these to understand what to avoid:",
        "",
    ]

    for key in selected_keys:
        if key not in BAD_EXAMPLES:
            continue
        example = BAD_EXAMPLES[key]
        lines.append(f"### ❌ BAD: {example['problem']}")
        lines.append("```html")
        lines.append(example["bad_output"].strip())
        lines.append("```")
        lines.append("**Why this is UNACCEPTABLE:**")
        for reason in example["why_bad"][:4]:  # Limit reasons for brevity
            lines.append(f"- {reason}")
        lines.append("")

    lines.append("**REMEMBER:** Never produce output similar to the bad examples above.")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# CORPORATE QUALITY: Industry-Specific Few-Shot Examples
# =============================================================================
# These examples demonstrate professional/enterprise-grade design patterns
# for corporate contexts (finance, healthcare, legal, tech, etc.)

CORPORATE_EXAMPLES: Dict[str, Dict[str, Any]] = {
    "corporate_hero_finance": {
        "input": {
            "component_type": "hero",
            "industry": "finance",
            "formality": "formal",
            "context": "Enterprise banking platform hero section",
            "content_structure": {
                "headline": "Trusted by Fortune 500",
                "subheadline": "Enterprise-grade financial infrastructure",
                "stats": ["$50B+ Assets", "99.99% Uptime", "SOC 2 Type II"],
            },
        },
        "output": {
            "design_thinking": "1. INDUSTRY DNA: Finance requires trust, security, precision. Using slate/blue palette with gold accents for premium feel. "
                              "2. TRUST INDICATORS: Compliance badges (SOC 2, ISO 27001) prominently placed. Stats with exact figures build credibility. "
                              "3. TYPOGRAPHY: Conservative serif headlines, no playful elements. Tracking-tight for authority. "
                              "4. LAYOUT: Traditional asymmetric grid, generous whitespace signals luxury and stability.",
            "component_id": "hero_enterprise_finance",
            "atomic_level": "organism",
            "html": """<section class="relative min-h-[85vh] bg-slate-950 text-white overflow-hidden">
    <!-- Subtle Grid Pattern -->
    <div class="absolute inset-0 bg-[linear-gradient(to_right,rgba(148,163,184,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(148,163,184,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>

    <!-- Gradient Accent -->
    <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-blue-950/50 to-transparent"></div>

    <div class="container mx-auto px-6 lg:px-8 py-24 relative z-10">
        <div class="max-w-4xl">
            <!-- Compliance Badges -->
            <div class="flex items-center gap-4 mb-8">
                <div class="flex items-center gap-2 px-4 py-2 bg-slate-900/80 border border-slate-800 rounded-lg">
                    <svg class="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                    <span class="text-sm font-medium text-slate-300">SOC 2 Type II</span>
                </div>
                <div class="flex items-center gap-2 px-4 py-2 bg-slate-900/80 border border-slate-800 rounded-lg">
                    <svg class="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                    <span class="text-sm font-medium text-slate-300">ISO 27001</span>
                </div>
            </div>

            <!-- Headline -->
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-serif font-semibold tracking-tight text-white leading-[1.1] mb-6">
                Trusted by <span class="text-blue-400">Fortune 500</span>
                <br/>Financial Institutions
            </h1>

            <!-- Subheadline -->
            <p class="text-xl md:text-2xl text-slate-400 font-light leading-relaxed max-w-2xl mb-12">
                Enterprise-grade financial infrastructure with bank-level security,
                real-time processing, and regulatory compliance built-in.
            </p>

            <!-- Stats Grid -->
            <div class="grid grid-cols-3 gap-8 mb-12 max-w-2xl">
                <div class="border-l-2 border-blue-500 pl-4">
                    <div class="text-3xl md:text-4xl font-bold text-white tracking-tight">$50B+</div>
                    <div class="text-sm text-slate-500 uppercase tracking-wider mt-1">Assets Managed</div>
                </div>
                <div class="border-l-2 border-emerald-500 pl-4">
                    <div class="text-3xl md:text-4xl font-bold text-white tracking-tight">99.99%</div>
                    <div class="text-sm text-slate-500 uppercase tracking-wider mt-1">Uptime SLA</div>
                </div>
                <div class="border-l-2 border-amber-500 pl-4">
                    <div class="text-3xl md:text-4xl font-bold text-white tracking-tight">500+</div>
                    <div class="text-sm text-slate-500 uppercase tracking-wider mt-1">Enterprise Clients</div>
                </div>
            </div>

            <!-- CTAs -->
            <div class="flex flex-col sm:flex-row gap-4">
                <a href="#" class="inline-flex items-center justify-center px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
                    Schedule Demo
                    <svg class="ml-2 w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
                    </svg>
                </a>
                <a href="#" class="inline-flex items-center justify-center px-8 py-4 border border-slate-700 hover:border-slate-600 text-slate-300 hover:text-white font-semibold rounded-lg transition-colors">
                    View Documentation
                </a>
            </div>
        </div>
    </div>
</section>""",
            "tailwind_classes_used": [
                "bg-slate-950", "font-serif", "tracking-tight", "border-slate-800",
                "text-blue-400", "uppercase", "tracking-wider", "font-semibold",
            ],
            "accessibility_features": [
                "Semantic section and heading hierarchy",
                "High contrast text (WCAG AAA)",
                "Keyboard-accessible interactive elements",
                "No decorative elements that interfere with screen readers",
            ],
            "dark_mode_support": True,
            "design_notes": "Corporate finance hero with trust indicators, compliance badges, and conservative typography. Uses border-left accent for stats to maintain professional hierarchy.",
        },
    },
    "corporate_pricing_saas": {
        "input": {
            "component_type": "pricing",
            "industry": "tech",
            "formality": "semi-formal",
            "context": "Enterprise SaaS pricing page",
            "content_structure": {
                "tiers": ["Startup", "Business", "Enterprise"],
                "highlight": "Business",
                "annual_discount": "20%",
            },
        },
        "output": {
            "design_thinking": "1. INDUSTRY DNA: SaaS pricing needs clear value differentiation. Highlighted tier with ring/shadow draws immediate attention. "
                              "2. TRUST ELEMENTS: Annual discount badge, 'Most Popular' label, feature checkmarks all build confidence. "
                              "3. CORPORATE POLISH: Clean borders, consistent spacing, professional icons. No playful elements. "
                              "4. CTA HIERARCHY: Primary button on highlighted tier, secondary on others.",
            "component_id": "pricing_enterprise_saas",
            "atomic_level": "organism",
            "html": """<section class="py-24 bg-white dark:bg-slate-900">
    <div class="container mx-auto px-6 lg:px-8">
        <!-- Header -->
        <div class="text-center max-w-3xl mx-auto mb-16">
            <span class="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium mb-6">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                Save 20% with annual billing
            </span>
            <h2 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white tracking-tight mb-4">
                Simple, transparent pricing
            </h2>
            <p class="text-lg text-slate-600 dark:text-slate-400">
                Choose the plan that's right for your team. All plans include a 14-day free trial.
            </p>
        </div>

        <!-- Pricing Cards -->
        <div class="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <!-- Startup Tier -->
            <div class="relative p-8 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl">
                <div class="mb-8">
                    <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">Startup</h3>
                    <p class="text-sm text-slate-500 dark:text-slate-400">For small teams getting started</p>
                </div>
                <div class="mb-8">
                    <span class="text-4xl font-bold text-slate-900 dark:text-white">$29</span>
                    <span class="text-slate-500">/month</span>
                </div>
                <ul class="space-y-4 mb-8">
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        Up to 5 team members
                    </li>
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        10GB storage
                    </li>
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        Email support
                    </li>
                </ul>
                <button class="w-full py-3 px-6 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 font-semibold rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                    Start free trial
                </button>
            </div>

            <!-- Business Tier (Highlighted) -->
            <div class="relative p-8 bg-white dark:bg-slate-800 border-2 border-blue-500 rounded-2xl shadow-xl shadow-blue-500/10">
                <!-- Popular Badge -->
                <div class="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span class="px-4 py-1.5 bg-blue-600 text-white text-sm font-semibold rounded-full">
                        Most Popular
                    </span>
                </div>
                <div class="mb-8">
                    <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">Business</h3>
                    <p class="text-sm text-slate-500 dark:text-slate-400">For growing companies</p>
                </div>
                <div class="mb-8">
                    <span class="text-4xl font-bold text-slate-900 dark:text-white">$79</span>
                    <span class="text-slate-500">/month</span>
                </div>
                <ul class="space-y-4 mb-8">
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        Up to 20 team members
                    </li>
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        100GB storage
                    </li>
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        Priority support
                    </li>
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        Advanced analytics
                    </li>
                </ul>
                <button class="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
                    Start free trial
                </button>
            </div>

            <!-- Enterprise Tier -->
            <div class="relative p-8 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl">
                <div class="mb-8">
                    <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">Enterprise</h3>
                    <p class="text-sm text-slate-500 dark:text-slate-400">For large organizations</p>
                </div>
                <div class="mb-8">
                    <span class="text-4xl font-bold text-slate-900 dark:text-white">Custom</span>
                </div>
                <ul class="space-y-4 mb-8">
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        Unlimited team members
                    </li>
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        Unlimited storage
                    </li>
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        24/7 dedicated support
                    </li>
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        Custom integrations
                    </li>
                    <li class="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                        <svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        SLA guarantee
                    </li>
                </ul>
                <button class="w-full py-3 px-6 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 font-semibold rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                    Contact sales
                </button>
            </div>
        </div>
    </div>
</section>""",
            "tailwind_classes_used": [
                "border-blue-500", "shadow-xl", "shadow-blue-500/10", "rounded-2xl",
                "font-semibold", "tracking-tight", "text-emerald-500",
            ],
            "accessibility_features": [
                "Clear heading hierarchy",
                "Descriptive button labels",
                "Sufficient color contrast",
                "Focus states on interactive elements",
            ],
            "dark_mode_support": True,
            "design_notes": "Corporate SaaS pricing with clear tier differentiation, highlighted recommended plan, and trust-building elements like trial offer and feature checkmarks.",
        },
    },
    "corporate_testimonials_healthcare": {
        "input": {
            "component_type": "testimonials",
            "industry": "healthcare",
            "formality": "formal",
            "context": "Healthcare platform testimonials section",
            "content_structure": {
                "testimonials": [
                    {"name": "Dr. Sarah Chen", "role": "Chief Medical Officer", "org": "Metro Health"},
                ],
            },
        },
        "output": {
            "design_thinking": "1. INDUSTRY DNA: Healthcare demands trust, credibility, and professionalism. Using muted teal/emerald for medical association. "
                              "2. CREDENTIALS: Job titles, organization names, and professional photos build authority. "
                              "3. COMPLIANCE AWARE: HIPAA badge subtly reinforces security mindset. "
                              "4. TYPOGRAPHY: Clean, readable, no decorative fonts. High contrast for accessibility (healthcare users may have visual impairments).",
            "component_id": "testimonials_healthcare_enterprise",
            "atomic_level": "organism",
            "html": """<section class="py-24 bg-slate-50 dark:bg-slate-900">
    <div class="container mx-auto px-6 lg:px-8">
        <!-- Header -->
        <div class="text-center max-w-3xl mx-auto mb-16">
            <div class="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 rounded-full text-sm font-medium mb-6">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                HIPAA Compliant
            </div>
            <h2 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white tracking-tight mb-4">
                Trusted by healthcare leaders
            </h2>
            <p class="text-lg text-slate-600 dark:text-slate-400">
                See how leading healthcare organizations are transforming patient care with our platform.
            </p>
        </div>

        <!-- Testimonials Grid -->
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <!-- Testimonial 1 -->
            <div class="bg-white dark:bg-slate-800 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-700">
                <!-- Quote Icon -->
                <svg class="w-10 h-10 text-emerald-500/20 mb-6" fill="currentColor" viewBox="0 0 32 32">
                    <path d="M10 8c-3.3 0-6 2.7-6 6v10h10V14H6c0-2.2 1.8-4 4-4V8zm14 0c-3.3 0-6 2.7-6 6v10h10V14h-8c0-2.2 1.8-4 4-4V8z"/>
                </svg>
                <p class="text-slate-700 dark:text-slate-300 text-lg leading-relaxed mb-8">
                    "The platform has revolutionized how we manage patient data.
                    Implementation was seamless and our team adopted it within weeks."
                </p>
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-slate-200 dark:bg-slate-700 rounded-full flex items-center justify-center text-slate-500 dark:text-slate-400 font-semibold">
                        SC
                    </div>
                    <div>
                        <div class="font-semibold text-slate-900 dark:text-white">Dr. Sarah Chen</div>
                        <div class="text-sm text-slate-500 dark:text-slate-400">Chief Medical Officer, Metro Health</div>
                    </div>
                </div>
            </div>

            <!-- Testimonial 2 -->
            <div class="bg-white dark:bg-slate-800 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-700">
                <svg class="w-10 h-10 text-emerald-500/20 mb-6" fill="currentColor" viewBox="0 0 32 32">
                    <path d="M10 8c-3.3 0-6 2.7-6 6v10h10V14H6c0-2.2 1.8-4 4-4V8zm14 0c-3.3 0-6 2.7-6 6v10h10V14h-8c0-2.2 1.8-4 4-4V8z"/>
                </svg>
                <p class="text-slate-700 dark:text-slate-300 text-lg leading-relaxed mb-8">
                    "Security was our top concern. The SOC 2 certification and HIPAA compliance
                    gave us the confidence to move forward."
                </p>
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-slate-200 dark:bg-slate-700 rounded-full flex items-center justify-center text-slate-500 dark:text-slate-400 font-semibold">
                        MJ
                    </div>
                    <div>
                        <div class="font-semibold text-slate-900 dark:text-white">Michael Johnson</div>
                        <div class="text-sm text-slate-500 dark:text-slate-400">CTO, Regional Medical Center</div>
                    </div>
                </div>
            </div>

            <!-- Testimonial 3 -->
            <div class="bg-white dark:bg-slate-800 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-700">
                <svg class="w-10 h-10 text-emerald-500/20 mb-6" fill="currentColor" viewBox="0 0 32 32">
                    <path d="M10 8c-3.3 0-6 2.7-6 6v10h10V14H6c0-2.2 1.8-4 4-4V8zm14 0c-3.3 0-6 2.7-6 6v10h10V14h-8c0-2.2 1.8-4 4-4V8z"/>
                </svg>
                <p class="text-slate-700 dark:text-slate-300 text-lg leading-relaxed mb-8">
                    "Patient outcomes have improved by 23% since implementation.
                    The analytics dashboard gives us actionable insights daily."
                </p>
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-slate-200 dark:bg-slate-700 rounded-full flex items-center justify-center text-slate-500 dark:text-slate-400 font-semibold">
                        EW
                    </div>
                    <div>
                        <div class="font-semibold text-slate-900 dark:text-white">Emily Williams, RN</div>
                        <div class="text-sm text-slate-500 dark:text-slate-400">Director of Nursing, City Hospital</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Trust Logos -->
        <div class="mt-16 text-center">
            <p class="text-sm text-slate-500 dark:text-slate-400 mb-6">Trusted by 200+ healthcare organizations</p>
            <div class="flex items-center justify-center gap-12 opacity-50">
                <div class="h-8 w-32 bg-slate-300 dark:bg-slate-700 rounded"></div>
                <div class="h-8 w-28 bg-slate-300 dark:bg-slate-700 rounded"></div>
                <div class="h-8 w-36 bg-slate-300 dark:bg-slate-700 rounded"></div>
                <div class="h-8 w-24 bg-slate-300 dark:bg-slate-700 rounded hidden md:block"></div>
            </div>
        </div>
    </div>
</section>""",
            "tailwind_classes_used": [
                "bg-emerald-50", "text-emerald-700", "rounded-xl", "shadow-sm",
                "border-slate-200", "leading-relaxed", "tracking-tight",
            ],
            "accessibility_features": [
                "Semantic section and heading hierarchy",
                "High contrast text (WCAG AA compliant)",
                "Clear visual hierarchy",
                "No purely decorative elements that confuse screen readers",
            ],
            "dark_mode_support": True,
            "design_notes": "Healthcare testimonials with HIPAA compliance badge, professional credentials, and trust indicators. Uses emerald/teal palette associated with healthcare industry.",
        },
    },
}

# Convenience exports for corporate examples
CORPORATE_HERO_EXAMPLE: Dict[str, Any] = {
    "component_type": "hero",
    "industry": "finance",
    "formality": "formal",
    "html": CORPORATE_EXAMPLES["corporate_hero_finance"]["output"]["html"],
    "design_notes": CORPORATE_EXAMPLES["corporate_hero_finance"]["output"]["design_notes"],
}

CORPORATE_PRICING_EXAMPLE: Dict[str, Any] = {
    "component_type": "pricing",
    "industry": "tech",
    "formality": "semi-formal",
    "html": CORPORATE_EXAMPLES["corporate_pricing_saas"]["output"]["html"],
    "design_notes": CORPORATE_EXAMPLES["corporate_pricing_saas"]["output"]["design_notes"],
}

CORPORATE_TESTIMONIALS_EXAMPLE: Dict[str, Any] = {
    "component_type": "testimonials",
    "industry": "healthcare",
    "formality": "formal",
    "html": CORPORATE_EXAMPLES["corporate_testimonials_healthcare"]["output"]["html"],
    "design_notes": CORPORATE_EXAMPLES["corporate_testimonials_healthcare"]["output"]["design_notes"],
}


def get_corporate_examples_for_prompt(
    component_type: str,
    industry: str = "",
    formality: str = "",
) -> str:
    """Generate corporate few-shot examples formatted for inclusion in prompts.

    Args:
        component_type: The type of component being designed (hero, pricing, etc.).
        industry: Optional industry filter (finance, healthcare, tech, etc.).
        formality: Optional formality filter (formal, semi-formal, approachable).

    Returns:
        Formatted string with corporate examples.
    """
    examples = []

    # Map component types to corporate examples
    component_map = {
        "hero": ["corporate_hero_finance"],
        "pricing": ["corporate_pricing_saas"],
        "testimonials": ["corporate_testimonials_healthcare"],
        "testimonial": ["corporate_testimonials_healthcare"],
    }

    # Get relevant examples
    example_keys = component_map.get(component_type, [])

    for key in example_keys:
        if key in CORPORATE_EXAMPLES:
            example = CORPORATE_EXAMPLES[key]
            input_data = example["input"]

            # Filter by industry if specified
            if industry and input_data.get("industry") != industry:
                continue

            # Filter by formality if specified
            if formality and input_data.get("formality") != formality:
                continue

            examples.append((key, example))

    if not examples:
        # Return any matching example without filters
        for key in example_keys:
            if key in CORPORATE_EXAMPLES:
                examples.append((key, CORPORATE_EXAMPLES[key]))
                break

    if not examples:
        return ""

    # Format examples
    lines = ["## Corporate Design Reference Examples", ""]
    for key, example in examples:
        input_data = example["input"]
        output_data = example["output"]

        lines.append(f"### Corporate Example: {key}")
        lines.append(f"**Industry:** {input_data.get('industry', 'N/A')}")
        lines.append(f"**Formality:** {input_data.get('formality', 'N/A')}")
        lines.append(f"**Context:** {input_data.get('context', 'N/A')}")
        lines.append("")
        lines.append("**Design Thinking:**")
        lines.append(f"{output_data.get('design_thinking', '')[:300]}...")
        lines.append("")
        lines.append("**Key Corporate Features:**")
        lines.append(f"- Tailwind classes: {', '.join(output_data.get('tailwind_classes_used', [])[:5])}...")
        lines.append(f"- Accessibility: {', '.join(output_data.get('accessibility_features', [])[:2])}")
        lines.append(f"- Dark mode: {output_data.get('dark_mode_support', False)}")
        lines.append(f"- Design notes: {output_data.get('design_notes', '')[:150]}...")
        lines.append("")

    return "\n".join(lines)


def list_corporate_examples() -> list[str]:
    """List all available corporate example keys."""
    return list(CORPORATE_EXAMPLES.keys())
