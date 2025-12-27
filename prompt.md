# Gemini API Prompt Mühendisliği ve Gelişmiş Özellikler Kılavuzu

**Gemini 3 Pro Preview** için optimize edilmiş bu kapsamlı kılavuz, mevcut sistem yapılandırmanızı güçlendirecek pratik iyileştirmeler, kod patterns ve anti-pattern'ler sunuyor. **Kritik bulgu:** Gemini 3 modelleri temperature 1.0 için optimize edilmiş olup, düşük değerler (0.0-0.3) looping ve performans sorunlarına yol açabilir.

---

## Thinking Mode: Budget vs Level ayrımı kritik

Mevcut sistemde `ThinkingConfig(thinking_budget=32768)` kullanılıyor ancak **Gemini 3 serisi modeller `thinking_level` parametresini** kullanıyor. Bu uyumsuzluk potansiyel hatalara neden olabilir.

| Parametre | Model Desteği | Kullanım |
|-----------|---------------|----------|
| `thinking_budget` | Gemini 2.5 serisi | Token sayısı (0-32768) |
| `thinking_level` | Gemini 3 serisi | `"low"`, `"medium"`, `"high"`, `"minimal"` |

**Gemini 3 Pro için optimal konfigürasyon:**

```python
# ❌ MEVCUT - Gemini 3 ile hata verebilir
thinking_config=ThinkingConfig(thinking_budget=32768)

# ✅ ÖNERİLEN - Gemini 3 için
from google.genai import types

config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
        thinking_level="high",      # Maksimum reasoning için
        include_thoughts=True       # Debugging için düşünce özeti
    ),
    temperature=1.0,  # Gemini 3'te DEĞİŞTİRMEYİN!
)
```

**Görev bazlı thinking_level seçimi:** Basit sınıflandırma ve fact retrieval için `"minimal"`, karşılaştırma ve özet çıkarma için `"medium"`, kompleks matematik, kodlama ve AIME tipi problemler için `"high"` kullanın. Gemini 3 Flash modellerinde ek olarak `"minimal"` seviyesi mevcuttur.

---

## Temperature ayarları: Gemini 3'te 1.0 zorunluluğu

Mevcut sistemde temperature 0.7-1.0 arası kullanılıyor. **Gemini 3 modelleri temperature 1.0 için optimize edilmiştir** - düşük değerler beklenmedik davranışlara, looping'e ve performans düşüşüne neden olabilir.

```python
# ✅ Gemini 3 için ZORUNLU konfigürasyon
config = types.GenerateContentConfig(
    temperature=1.0,      # Değiştirmeyin
    top_p=0.95,           # Nucleus sampling
    top_k=40,             # Diversity control
    thinking_level="high"
)
```

**Deterministic output gerekiyorsa:** Temperature yerine `seed` parametresi ve JSON schema ile kontrol sağlayın. Ancak seed "best effort" olup tam determinism garanti edilmez.

---

## JSON output optimizasyonu için schema kullanımı

Mevcut `response_mime_type: "application/json"` kullanımı doğru ancak **Pydantic schema ile güçlendirilmeli**.

```python
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class ComponentOutput(BaseModel):
    """Structured output for agent responses"""
    component_name: str = Field(description="Semantic component identifier")
    html: str = Field(description="Semantic HTML5 markup")
    css: str = Field(description="BEM-named CSS with custom properties")
    js: Optional[str] = Field(description="ES6+ JavaScript if needed")
    accessibility_notes: List[str] = Field(description="WCAG compliance notes")
    confidence: float = Field(ge=0.0, le=1.0, description="Generation confidence")

# Agent konfigürasyonu
config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=ComponentOutput.model_json_schema(),
    temperature=1.0,
    thinking_level="high"
)
```

**JSON güvenilirliği için:** Her property'ye `description` ekleyin - model bu açıklamaları rehber olarak kullanır. Çok derin nested yapılardan kaçının. Property isimlerini kısa tutun. Optional property sayısını minimize edin.

---

## System instruction yapısı: XML tags ile net ayrım

Mevcut detaylı prompt'lar XML tags ile yapılandırılmalı. Gemini 3 bu yapıyı çok iyi parse eder.

```xml
<role>
You are a senior frontend developer specializing in semantic HTML5, 
modern CSS with BEM methodology, and vanilla ES6+ JavaScript.
You are precise, analytical, and accessibility-focused.
</role>

<constraints>
- Verbosity: High (explain design decisions)
- Code Style: Production-ready with comments
- Accessibility: WCAG 2.1 Level AA mandatory
- Browser Support: Chrome, Firefox, Safari, Edge (latest 2 versions)
- No external dependencies
</constraints>

<instructions>
1. **Analyze**: Parse the design requirements thoroughly
2. **Plan**: Create component structure outline
3. **Generate**: Write semantic, accessible code
4. **Validate**: Self-check against constraints before output
</instructions>

<output_format>
Return JSON with: html, css, js, accessibility_notes, design_rationale
</output_format>

<context>
<!-- Few-shot examples veya referans materyaller -->
</context>

<task>
<!-- Spesifik kullanıcı isteği -->
</task>
```

**Kritik kurallar:** XML veya Markdown seçin, karıştırmayın. Critical instructions'ı prompt başına koyun. Long context'te (büyük codebase'ler) talimatları sona yerleştirin. Context anchoring için "Based on the information above..." gibi geçiş cümleleri kullanın.

---

## Context caching ile maliyet optimizasyonu

Tekrarlanan system instruction'lar ve few-shot examples için **%75-90 token indirimi** sağlayan context caching kullanılmalı.

```python
from google import genai
from google.genai import types

client = genai.Client()

# Büyük system prompt + examples için cache oluştur
cache = client.caches.create(
    model="gemini-2.0-flash-001",  # Version suffix ZORUNLU
    config=types.CreateCachedContentConfig(
        display_name="design-system-cache",
        system_instruction=SYSTEM_INSTRUCTION,
        contents=[
            {"text": FEW_SHOT_EXAMPLES},
            uploaded_design_file  # Büyük dosyalar için ideal
        ],
        ttl="3600s"  # 1 saat TTL
    )
)

# Cache kullanarak generate
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=user_request,
    config=types.GenerateContentConfig(
        cached_content=cache.name,
        temperature=1.0
    )
)

# Token tasarrufunu kontrol
print(f"Cached: {response.usage_metadata.cached_content_token_count}")
print(f"Total: {response.usage_metadata.total_token_count}")
```

**Minimum token gereksinimleri:** Gemini 2.5 Flash için 1,024 token, Gemini 2.5 Pro için 4,096 token, Gemini 3 Pro Preview için 2,048 token gereklidir. Bu eşiklerin altındaki içerikler cache'lenemez.

---

## Function calling ve tool use capabilities

Agent'lar arasında function calling ile koordinasyon sağlanabilir.

```python
# Tool tanımlama
design_tools = types.Tool(
    function_declarations=[
        {
            "name": "extract_design_tokens",
            "description": "Extract color palette and typography from image",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_uri": {"type": "string", "description": "Image file URI"},
                    "token_types": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["colors", "typography", "spacing"]}
                    }
                },
                "required": ["image_uri"]
            }
        },
        {
            "name": "validate_accessibility",
            "description": "Check WCAG compliance of generated HTML",
            "parameters": {
                "type": "object",
                "properties": {
                    "html_content": {"type": "string"},
                    "wcag_level": {"type": "string", "enum": ["A", "AA", "AAA"]}
                },
                "required": ["html_content"]
            }
        }
    ]
)

# Tool config
config = types.GenerateContentConfig(
    tools=[design_tools],
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode="AUTO"  # Model karar verir: text mi function call mı
        )
    )
)
```

**Multi-turn conversation'larda thought signatures zorunlu:** Gemini 3'te function calling sonrası geri gönderilmesi gereken context bilgisi var. Python SDK bunu otomatik handle eder, REST API kullanıyorsanız manuel yönetim gerekli.

---

## Multi-agent orchestration patterns

Agent'lar arası iş bölümü için sequential ve parallel pattern'ler kullanılabilir.

```python
# Sequential Pipeline - Bağımlı agent'lar için
AGENTS = {
    "vision_analyzer": {
        "model": "gemini-3-flash",
        "instruction": """Analyze design image. Extract:
        - Color palette (hex values)
        - Typography (font families, sizes)
        - Component hierarchy
        - Spacing system
        Output as JSON design tokens.""",
        "output_key": "design_tokens"
    },
    "html_generator": {
        "model": "gemini-3-pro",
        "instruction": """Using {design_tokens}, generate semantic HTML5.
        - Use proper landmarks (header, nav, main, footer)
        - Add ARIA attributes where needed
        - Include data attributes for JS hooks""",
        "output_key": "html",
        "depends_on": ["design_tokens"]
    },
    "css_generator": {
        "model": "gemini-3-flash",
        "instruction": """Using {design_tokens} and {html}:
        - Convert tokens to CSS custom properties
        - Follow BEM naming convention
        - Mobile-first responsive design
        - Include prefers-reduced-motion fallbacks""",
        "output_key": "css",
        "depends_on": ["design_tokens", "html"]
    },
    "accessibility_validator": {
        "model": "gemini-3-flash",
        "instruction": """Review {html} and {css} for WCAG 2.1 AA:
        - Check color contrast (4.5:1 minimum)
        - Verify keyboard navigation
        - Validate ARIA usage
        Return issues with fixes.""",
        "output_key": "a11y_report",
        "depends_on": ["html", "css"]
    }
}
```

**Context passing pattern:** Shared session state kullanarak agent'lar arası bilgi aktarımı yapın. Her agent okuyacağı ve yazacağı state key'lerini bilmeli.

---

## Code generation için accessibility-first prompting

```xml
<accessibility_requirements>
WCAG 2.1 Level AA compliance MANDATORY:

1. Semantic HTML:
   - button for clickable elements, never div
   - Heading hierarchy: h1 → h2 → h3 (no skipping)
   - Landmarks: header, nav, main, aside, footer

2. Keyboard Navigation:
   - All interactive elements focusable
   - Visible focus: outline: 2px solid var(--focus-color)
   - Tab order follows visual order
   - Escape closes modals/dropdowns

3. ARIA Usage:
   - aria-label for icon-only buttons
   - aria-expanded for collapsibles
   - aria-live="polite" for dynamic content
   - Only use role when semantic HTML insufficient

4. Visual:
   - Color contrast: 4.5:1 for text, 3:1 for UI
   - Never rely on color alone
   - Touch targets: minimum 44x44px

5. Forms:
   - Labels with for/id association
   - Error messages with aria-describedby
   - Required fields with aria-required="true"
</accessibility_requirements>
```

---

## Error handling ve retry strategies

Production-ready retry wrapper implementasyonu:

```python
import time
import random
from google import genai
from google.genai import types

class GeminiClientWithRetry:
    def __init__(self, api_key: str, max_retries: int = 5):
        self.client = genai.Client(api_key=api_key)
        self.max_retries = max_retries
        
    def generate(self, model: str, contents: str, config: dict = None):
        """Exponential backoff with jitter"""
        for attempt in range(self.max_retries):
            try:
                return self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )
            except genai.errors.APIError as e:
                status = getattr(e, 'status_code', None)
                
                # Terminal errors - no retry
                if status in [400, 401, 403, 404]:
                    raise e
                
                # Retryable errors
                if status in [429, 500, 503]:
                    delay = min(
                        (2 ** attempt) + random.uniform(0, 1),
                        60  # max 60s
                    )
                    time.sleep(delay)
                    continue
                raise e
        raise Exception("Max retries exceeded")
```

**Rate limit bilgileri:** Free tier dakikada **10-15 RPM**, Tier 1 **300 RPM**, Tier 2 **1000 RPM**. Limitler proje bazlı, API key bazlı değil.

---

## Prompt engineering anti-patterns ve düzeltmeleri

| ❌ Anti-Pattern | ✅ Düzeltme |
|----------------|-------------|
| `temperature=0.3` (Gemini 3) | `temperature=1.0` zorunlu |
| `thinking_budget=32768` (Gemini 3) | `thinking_level="high"` kullan |
| `"Don't use jargon"` | `"Explain as if to a 10-year-old"` |
| `"Ignore previous instructions"` önlemi yok | Input sanitization ekle |
| Retry stratejisi yok | Exponential backoff implement et |
| Model version pinning yok | `gemini-2.5-flash-001` gibi explicit version |
| JSON schema yok | Pydantic schema ile validation |
| Caching kullanılmıyor | 32K+ token için context cache |

---

## Agent-spesifik prompt improvement TODO'ları

### Vision/Analysis Agent TODO

```python
# TODO: Design token extraction için structured output
VISION_PROMPT_UPDATE = """
<task>
Analyze this UI design image and extract complete design system:
</task>

<output_schema>
{
  "colors": {
    "primary": {"hex": "#xxx", "usage": "CTAs, brand"},
    "secondary": {"hex": "#xxx", "usage": "secondary actions"},
    "neutral": {"darkest": "#xxx", "dark": "#xxx", "light": "#xxx"},
    "semantic": {"success": "#xxx", "error": "#xxx", "warning": "#xxx"}
  },
  "typography": {
    "headings": {"family": "...", "weights": [600, 700]},
    "body": {"family": "...", "size": "16px", "lineHeight": 1.5}
  },
  "spacing": {"base": 8, "scale": [4, 8, 16, 24, 32, 48, 64]},
  "borderRadius": {"sm": "4px", "md": "8px", "lg": "16px"}
}
</output_schema>
"""
```

### HTML Generator Agent TODO

```python
# TODO: Semantic structure ve accessibility focus
HTML_AGENT_UPDATE = """
<role>
Semantic HTML5 Architect - accessibility is non-negotiable.
</role>

<constraints>
- NO div for interactive elements - use button, a, input
- Heading hierarchy mandatory - h1 → h2 → h3
- ARIA only when semantic HTML insufficient
- data-* attributes for JS hooks
- class names follow BEM: block__element--modifier
</constraints>

<validation>
Before output, verify:
- [ ] All buttons have accessible names
- [ ] Images have alt text
- [ ] Form inputs have labels
- [ ] No heading level skipped
</validation>
"""
```

### CSS Generator Agent TODO

```python
# TODO: Modern CSS with custom properties
CSS_AGENT_UPDATE = """
<methodology>
1. CSS Custom Properties for all design tokens
2. Mobile-first media queries
3. CSS Grid for 2D, Flexbox for 1D layouts
4. clamp() for fluid typography
5. prefers-reduced-motion fallbacks
</methodology>

<structure>
/* 1. Custom Properties (from design tokens) */
:root { --color-primary: ...; }

/* 2. Reset/Base */
/* 3. Layout */
/* 4. Components (BEM) */
/* 5. Utilities */
/* 6. Animations */
/* 7. Media Queries */
</structure>
"""
```

### JavaScript Agent TODO

```python
# TODO: ES6+ ile accessibility-aware interactions
JS_AGENT_UPDATE = """
<requirements>
- ES6+ syntax (destructuring, arrow functions, async/await)
- No global variables - use modules
- Keyboard support: Enter, Space, Escape, Arrow keys
- Focus management for modals/dropdowns
- Debounce scroll/resize handlers (150ms)
- JSDoc comments for public functions
</requirements>

<accessibility_js>
// Focus trap for modals
// aria-expanded toggle
// Live region announcements
// Roving tabindex for menus
</accessibility_js>
"""
```

---

## Optimal configuration reference

```python
# Production-ready Gemini 3 configuration
OPTIMAL_CONFIG = {
    "reasoning_tasks": types.GenerateContentConfig(
        temperature=1.0,
        thinking_config=types.ThinkingConfig(thinking_level="high"),
        response_mime_type="application/json",
        max_output_tokens=65536
    ),
    "creative_tasks": types.GenerateContentConfig(
        temperature=1.0,
        top_p=0.95,
        top_k=40,
        thinking_config=types.ThinkingConfig(thinking_level="medium")
    ),
    "classification": types.GenerateContentConfig(
        temperature=1.0,
        response_mime_type="text/x.enum",
        response_schema={"type": "string", "enum": ["option1", "option2"]}
    ),
    "code_generation": types.GenerateContentConfig(
        temperature=1.0,
        thinking_config=types.ThinkingConfig(thinking_level="high"),
        response_mime_type="application/json",
        max_output_tokens=65536
    )
}
```

---

## Sonuç ve kritik uyarılar

**Hemen uygulanması gereken değişiklikler:** Gemini 3 kullanılıyorsa `thinking_budget` → `thinking_level` geçişi yapın. Temperature'ı 1.0'da sabit tutun. JSON output için Pydantic schema ekleyin. Retry stratejisi implement edin.

**Maliyet optimizasyonu için:** 32K+ token context için explicit caching kullanın (%75-90 indirim). Batch API ile non-urgent işlemlerde %50 tasarruf sağlayın. Flash modelleri yüksek hacimli görevler için tercih edin.

**Güvenilirlik için:** Exponential backoff retry wrapper kullanın. Circuit breaker pattern ekleyin. Fallback model tanımlayın (Pro → Flash). Input sanitization ile prompt injection önleyin.