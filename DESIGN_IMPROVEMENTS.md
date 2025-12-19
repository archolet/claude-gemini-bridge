# Design-Gemini Optimizasyon Raporu

## Mevcut Durum Analizi

### Güçlü Yanlar
- **49 bileşen tipi** (Atomic Design metodolojisi)
- **14 tema preset'i** (modern-minimal'den cyberpunk'a)
- **10 sayfa şablonu** (landing, dashboard, auth, etc.)
- **WCAG 2.1 AA/AAA** erişilebilirlik desteği
- **Responsive design** (sm, md, lg, xl breakpoints)
- **Dark mode** tüm bileşenlerde
- **Gemini 3 Pro** her zaman en kaliteli model

### Tespit Edilen Sorunlar

| Sorun | Etki | Öncelik |
|-------|------|---------|
| Thinking budget her zaman MAX | Yüksek maliyet, gereksiz gecikme | YÜKSEK |
| Türkçe hardcoded | Uluslararası kullanım engeli | YÜKSEK |
| Response validation yok | Hatalı çıktılar sessizce geçiyor | ORTA |
| Cache mekanizması yok | Tekrar eden API çağrıları | ORTA |
| Design system tutarlılığı yok | Bileşenler arası uyumsuzluk | ORTA |
| Streaming desteği yok | Yavaş ilk yanıt | DÜŞÜK |

---

## Önerilen İyileştirmeler

### 1. Kalite Seviyeleri (quality_level)

**Amaç**: Maliyet ve hız optimizasyonu

```python
# server.py - design_frontend parametrelerine ekle
quality_level: str = "standard"  # draft, standard, high, ultra
```

**Konfigürasyon**:
```python
QUALITY_CONFIGS = {
    "draft": {
        "thinking_budget": 8192,
        "temperature": 0.8,
        "description": "Hızlı iterasyon için"
    },
    "standard": {
        "thinking_budget": 16384,
        "temperature": 0.7,
        "description": "Genel kullanım (varsayılan)"
    },
    "high": {
        "thinking_budget": 32768,
        "temperature": 0.6,
        "description": "Final tasarımlar için"
    },
    "ultra": {
        "thinking_budget": 32768,
        "temperature": 0.5,
        "max_output_tokens": 65536,
        "description": "Karmaşık organizmalar için"
    }
}
```

**Fayda**: %50-75 maliyet düşürme (draft kullanımda)

---

### 2. Dil Desteği (content_language)

**Amaç**: Çoklu dil desteği

```python
# server.py - design_frontend parametrelerine ekle
content_language: str = "tr"  # tr, en, de, fr, es, pt, ja, ko, zh
```

**Sistem Prompt Güncellemesi**:
```python
# frontend_presets.py
LANGUAGE_CONFIGS = {
    "tr": {
        "button_labels": ["Gönder", "İptal", "Kaydet", "Devam Et"],
        "form_labels": ["E-posta", "Şifre", "Ad Soyad"],
        "navigation": ["Ana Sayfa", "Hakkımızda", "İletişim"],
    },
    "en": {
        "button_labels": ["Submit", "Cancel", "Save", "Continue"],
        "form_labels": ["Email", "Password", "Full Name"],
        "navigation": ["Home", "About", "Contact"],
    },
    # ...
}

def build_language_section(language: str) -> str:
    config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["en"])
    return f"""
## CONTENT LANGUAGE: {language.upper()}

Use these labels and terms:
- Buttons: {', '.join(config['button_labels'])}
- Forms: {', '.join(config['form_labels'])}
- Navigation: {', '.join(config['navigation'])}
"""
```

---

### 3. Response Validation (Pydantic)

**Amaç**: Güvenilir çıktı garantisi

```python
# Yeni dosya: src/gemini_mcp/schemas.py
from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional

class DesignResponse(BaseModel):
    component_id: str = Field(..., min_length=1, max_length=100)
    atomic_level: Literal["atom", "molecule", "organism"]
    html: str = Field(..., min_length=10)
    tailwind_classes_used: List[str] = Field(default_factory=list)
    accessibility_features: List[str] = Field(default_factory=list)
    responsive_breakpoints: List[str] = Field(default_factory=list)
    dark_mode_support: bool = True
    micro_interactions: List[str] = Field(default_factory=list)
    design_notes: str = ""
    model_used: str = ""

    @validator('html')
    def html_must_not_contain_forbidden(cls, v):
        forbidden = ['<!DOCTYPE', '<html', '<head', '<script', '<style']
        for tag in forbidden:
            if tag.lower() in v.lower():
                raise ValueError(f"HTML must not contain {tag}")
        return v

    @validator('tailwind_classes_used')
    def classes_must_be_valid(cls, v):
        # Basit Tailwind class validation
        for cls_name in v:
            if not cls_name or ' ' in cls_name:
                raise ValueError(f"Invalid class: {cls_name}")
        return v
```

**client.py Güncellemesi**:
```python
from .schemas import DesignResponse

# design_component içinde:
try:
    validated = DesignResponse(**result)
    return validated.dict()
except ValidationError as e:
    logger.warning(f"Response validation failed: {e}")
    # Fallback to unvalidated
    return result
```

---

### 4. Design System Tutarlılığı

**Amaç**: Bileşenler arası görsel tutarlılık

```python
# Yeni dosya: src/gemini_mcp/design_system.py
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class DesignSystemState:
    id: str
    theme: str
    components: List[Dict] = field(default_factory=list)
    custom_rules: List[str] = field(default_factory=list)

    def add_component(self, component: Dict):
        self.components.append({
            "type": component.get("component_type"),
            "id": component.get("component_id"),
            "classes_summary": component.get("tailwind_classes_used", [])[:10]
        })

    def get_context_for_prompt(self) -> str:
        if not self.components:
            return ""

        return f"""
## DESIGN SYSTEM CONTEXT

This project uses design system: {self.id}
Theme: {self.theme}

Previously designed components (maintain consistency):
{self._format_components()}

Custom rules:
{chr(10).join(f'- {rule}' for rule in self.custom_rules)}
"""

    def _format_components(self) -> str:
        lines = []
        for c in self.components[-5:]:  # Son 5 bileşen
            lines.append(f"- {c['type']}: {c['id']}")
        return chr(10).join(lines)


# Global design systems storage
_design_systems: Dict[str, DesignSystemState] = {}

def get_or_create_design_system(
    design_system_id: str,
    theme: str = "modern-minimal"
) -> DesignSystemState:
    if design_system_id not in _design_systems:
        _design_systems[design_system_id] = DesignSystemState(
            id=design_system_id,
            theme=theme
        )
    return _design_systems[design_system_id]
```

**Kullanım**:
```python
# server.py - design_frontend parametrelerine ekle
design_system_id: str = ""  # Tutarlı tasarım için

# Prompt'a ekleme:
if design_system_id:
    ds = get_or_create_design_system(design_system_id, theme)
    project_context += ds.get_context_for_prompt()

# Sonuç döndükten sonra:
if design_system_id:
    ds.add_component(result)
```

---

### 5. Caching Mekanizması

**Amaç**: Tekrar eden isteklerde maliyet tasarrufu

```python
# Yeni dosya: src/gemini_mcp/cache.py
import hashlib
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
from functools import lru_cache

class DesignCache:
    def __init__(self, max_size: int = 100, ttl_hours: int = 24):
        self._cache: Dict[str, Dict] = {}
        self._max_size = max_size
        self._ttl = timedelta(hours=ttl_hours)

    def _hash_request(self,
                      component_type: str,
                      design_spec: Dict,
                      style_guide: Dict,
                      constraints: Dict) -> str:
        key_data = {
            "component_type": component_type,
            "design_spec": design_spec,
            "style_guide": style_guide,
            "constraints": constraints
        }
        return hashlib.sha256(
            json.dumps(key_data, sort_keys=True).encode()
        ).hexdigest()[:16]

    def get(self,
            component_type: str,
            design_spec: Dict,
            style_guide: Dict,
            constraints: Dict) -> Optional[Dict]:
        key = self._hash_request(component_type, design_spec, style_guide, constraints)
        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() - entry["timestamp"] < self._ttl:
                return entry["result"]
            else:
                del self._cache[key]
        return None

    def set(self,
            component_type: str,
            design_spec: Dict,
            style_guide: Dict,
            constraints: Dict,
            result: Dict):
        if len(self._cache) >= self._max_size:
            # Remove oldest entry
            oldest = min(self._cache, key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest]

        key = self._hash_request(component_type, design_spec, style_guide, constraints)
        self._cache[key] = {
            "result": result,
            "timestamp": datetime.now()
        }

# Global cache instance
design_cache = DesignCache()
```

**client.py Güncellemesi**:
```python
from .cache import design_cache

async def design_component(self, ...):
    # Cache kontrolü
    cached = design_cache.get(component_type, design_spec, style_guide, constraints)
    if cached:
        logger.info(f"Cache hit for {component_type}")
        return cached

    # Normal API çağrısı...
    result = ...

    # Cache'e kaydet
    design_cache.set(component_type, design_spec, style_guide, constraints, result)
    return result
```

---

### 6. Few-shot Examples

**Amaç**: Daha tutarlı ve kaliteli çıktılar

```python
# frontend_presets.py'ye ekle
FEW_SHOT_EXAMPLES = {
    "button": {
        "input": {
            "component_type": "button",
            "context": "Primary CTA for newsletter signup",
            "content_structure": {"text": "Abone Ol", "icon": "mail"},
            "theme": "modern-minimal"
        },
        "output": {
            "component_id": "btn-newsletter-cta",
            "atomic_level": "atom",
            "html": '''<button
  class="inline-flex items-center justify-center gap-2 px-6 py-3
         bg-blue-600 hover:bg-blue-700 active:bg-blue-800
         text-white font-medium text-sm
         rounded-lg shadow-sm hover:shadow-md
         transition-all duration-200 ease-in-out
         focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
         dark:bg-blue-500 dark:hover:bg-blue-600"
  aria-label="Bültene abone ol"
>
  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
  </svg>
  <span>Abone Ol</span>
</button>''',
            "tailwind_classes_used": ["inline-flex", "items-center", "bg-blue-600", "hover:bg-blue-700"],
            "accessibility_features": ["aria-label", "focus-visible:ring-2"],
            "responsive_breakpoints": [],
            "dark_mode_support": True,
            "micro_interactions": ["hover:shadow-md", "transition-all duration-200"],
            "design_notes": "Clean, accessible button with icon and smooth hover transition."
        }
    },
    "card": {
        "input": {
            "component_type": "card",
            "context": "Product feature highlight card",
            "theme": "modern-minimal"
        },
        "output": {
            # Similar detailed example...
        }
    }
}

def get_few_shot_example(component_type: str) -> Optional[str]:
    if component_type in FEW_SHOT_EXAMPLES:
        example = FEW_SHOT_EXAMPLES[component_type]
        return f"""
## REFERENCE EXAMPLE

Here's an example of a well-designed {component_type}:

Input:
```json
{json.dumps(example["input"], indent=2)}
```

Expected Output Format:
```json
{json.dumps(example["output"], indent=2)}
```

Follow this quality standard and output format.
"""
    return ""
```

---

## Kullanım Önerileri (Best Practices)

### 1. project_context Optimizasyonu

En iyi sonuçlar için project_context'e şunları ekleyin:

```python
project_context = """
## Proje Bilgileri
- **Proje Adı**: InfoSYS ERP
- **Sektör**: B2B Kurumsal Yazılım
- **Hedef Kitle**: Türk işletmeleri, muhasebe departmanları
- **Ton**: Profesyonel, güvenilir, modern

## Marka Stilleri
- **Primary**: blue-600 (güven, kurumsal)
- **Secondary**: slate-500 (nötr, okunabilir)
- **Accent**: emerald-500 (başarı durumları)
- **Hata**: red-500

## Tasarım Kuralları
- Tüm butonlar rounded-lg olmalı
- Shadow-sm hover'da shadow-md olmalı
- Minimum touch target: 44x44px
- Tablo satırları hover:bg-slate-50

## Daha Önce Tasarlanan Bileşenler
- navbar-main: Sticky, beyaz arka plan
- sidebar-nav: 280px genişlik, koyu tema
- btn-primary: blue-600, rounded-lg
"""
```

### 2. İteratif Tasarım Workflow

```python
# Adım 1: Hızlı draft
result = await design_frontend(
    component_type="navbar",
    context="Ana navigasyon",
    quality_level="draft"  # Hızlı, düşük maliyet
)

# Adım 2: Feedback sonrası iyileştirme
refined = await refine_frontend(
    previous_html=result["html"],
    modifications="Logo'yu sola al, arama çubuğu ekle"
)

# Adım 3: Final polish
final = await refine_frontend(
    previous_html=refined["html"],
    modifications="Micro-interactions'ları zenginleştir, dark mode'u optimize et",
    quality_level="high"  # Yüksek kalite
)
```

### 3. Batch Design (Tutarlılık için)

```python
# Aynı design_system_id ile bileşenleri tasarla
design_system_id = "my-project-v1"

components = [
    ("button", "Primary CTA"),
    ("card", "Feature card"),
    ("navbar", "Main navigation"),
]

for comp_type, context in components:
    await design_frontend(
        component_type=comp_type,
        context=context,
        design_system_id=design_system_id,  # Tutarlılık
        theme="modern-minimal"
    )
```

---

## Sonraki Adımlar

1. **Öncelik 1**: quality_level parametresi ekle (maliyet optimizasyonu)
2. **Öncelik 2**: content_language parametresi ekle (uluslararası kullanım)
3. **Öncelik 3**: Response validation (Pydantic) ekle
4. **Öncelik 4**: Design system tutarlılığı ekle
5. **Öncelik 5**: Caching mekanizması ekle

---

## Tahmini Etkiler

| İyileştirme | Maliyet Etkisi | Kalite Etkisi | Geliştirme Süresi |
|-------------|----------------|---------------|-------------------|
| quality_level | -50% (draft) | Değişken | 2-4 saat |
| content_language | - | +Uluslararası | 2-3 saat |
| Response validation | - | +Güvenilirlik | 3-4 saat |
| Design system | - | +Tutarlılık | 4-6 saat |
| Caching | -30% | - | 2-3 saat |
| Few-shot examples | +5% | +Kalite | 3-4 saat |

---

*Bu doküman design_frontend optimizasyonu için hazırlanmıştır.*
*Tarih: 2025-12-19*
