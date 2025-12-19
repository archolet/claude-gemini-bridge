# Claude Gemini Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Claude Code için Vertex AI üzerinden Gemini 3 modellerine erişim sağlayan MCP sunucusu.

## Özellikler

- **Text Generation**: Context ve system instruction desteği ile metin üretimi
- **Multi-turn Chat**: Oturum yönetimi ile çok turlu konuşmalar
- **Image Generation**: Gemini 3 Pro Image ve Imagen 4 aileleri ile görsel üretimi
- **Video Generation**: Veo 3.1 ile yüksek kaliteli video üretimi (otomatik GCS bucket)
- **Frontend Design**: Gemini 3 Pro ile yüksek kaliteli TailwindCSS/HTML bileşen tasarımı
  - 49 component tipi (atoms, molecules, organisms)
  - 10 page template (landing, dashboard, auth, vb.)
  - 14 tema (modern-minimal, cyberpunk, glassmorphism, vb.)
  - Proje bağlamı desteği (projenin ruhunu Gemini'ye aktarma)
  - İterasyon desteği (mevcut tasarımları revize etme)
  - Türkçe içerik üretimi
- **Streaming**: Hızlı ilk yanıt için streaming desteği
- **OAuth Authentication**: ADC ve gcloud CLI ile otomatik kimlik doğrulama

## Gereksinimler

- Python 3.10+
- Google Cloud hesabı ve proje
- `gcloud` CLI kurulu ve yapılandırılmış
- `uv` package manager

## Kurulum

### 1. gcloud Kimlik Doğrulama

```bash
# Giriş yapın
gcloud auth login

# Application Default Credentials ayarlayın
gcloud auth application-default login

# Proje ayarlayın
gcloud config set project YOUR_PROJECT_ID
```

### 2. Bağımlılıkları Yükleyin

```bash
cd /path/to/claude-gemini-bridge
uv sync
```

### 3. Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
# NOT: Gemini 3 modelleri "global" location gerektirir (default)
export GOOGLE_CLOUD_LOCATION="global"  # Opsiyonel, default: global
```

### 4. Claude Code'a Ekleyin

`~/.claude/.mcp.json` dosyasına ekleyin:

```json
{
  "mcpServers": {
    "gemini": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/claude-gemini-bridge", "gemini-mcp"],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "YOUR_PROJECT_ID",
        "GOOGLE_CLOUD_LOCATION": "global"
      }
    }
  }
}
```

> **Not**: `/path/to/claude-gemini-bridge` kısmını projeyi klonladığınız gerçek dizin yolu ile değiştirin.

## MCP Tools

### `ask_gemini`

Gemini 3'e tek seferlik soru sorma.

**Parametreler:**
| Parametre | Tip | Default | Açıklama |
|-----------|-----|---------|----------|
| `prompt` | str | (zorunlu) | Soru veya görev |
| `context` | str | "" | Arka plan bilgisi |
| `system_instruction` | str | "" | Sistem talimatları |
| `model` | str | "gemini-3-flash-preview" | Kullanılacak model |
| `temperature` | float | 0.7 | Yaratıcılık (0-1) |
| `max_tokens` | int | 65536 | Maksimum yanıt uzunluğu |
| `thinking_level` | str | "medium" | Reasoning derinliği (minimal, low, medium, high) |
| `stream` | bool | true | Streaming kullanımı |

**Örnek:**
```
"Bu Python kodunu optimize et: [kod]. Context: Performans kritik."
```

### `chat_gemini`

Gemini 3 ile çok turlu konuşma.

**Parametreler:**
| Parametre | Tip | Default | Açıklama |
|-----------|-----|---------|----------|
| `message` | str | (zorunlu) | Gönderilecek mesaj |
| `chat_id` | str | "default" | Oturum kimliği |
| `model` | str | "gemini-3-flash-preview" | Kullanılacak model |
| `system_instruction` | str | "" | Yeni oturumlar için |

### `generate_image`

Gemini 3 Pro Image ile görsel üretimi (4096px yüksek kalite).

**Parametreler:**
| Parametre | Tip | Default | Açıklama |
|-----------|-----|---------|----------|
| `prompt` | str | (zorunlu) | Görsel açıklaması |
| `model` | str | "gemini-3-pro-image-preview" | Model |
| `aspect_ratio` | str | "1:1" | En boy oranı |
| `output_format` | str | "base64" | "base64", "file", "both" |
| `output_dir` | str | "./images" | Dosya çıktı dizini |
| `number_of_images` | int | 1 | Üretilecek görsel sayısı (1-4, Imagen 4) |
| `output_resolution` | str | "1K" | Çıktı çözünürlüğü (1K/2K, Imagen 4) |

### `generate_video`

Veo 3.1 ile video üretimi. GCS bucket otomatik oluşturulur.

**ÖNEMLİ**: Video üretimi 1-10 dakika sürebilir.

**Parametreler:**
| Parametre | Tip | Default | Açıklama |
|-----------|-----|---------|----------|
| `prompt` | str | (zorunlu) | Video açıklaması |
| `model` | str | "veo-3.1-generate-001" | Kullanılacak model |
| `output_gcs_uri` | str | "" | GCS URI (opsiyonel, otomatik oluşturulur) |
| `duration_seconds` | int | 8 | Video süresi (4, 6, 8 saniye) |
| `aspect_ratio` | str | "16:9" | En boy oranı (16:9, 9:16) |
| `resolution` | str | "720p" | Çözünürlük (720p, 1080p) |
| `generate_audio` | bool | true | Ses üretimi (diyalog, müzik, SFX) |
| `number_of_videos` | int | 1 | Video sayısı (1-4) |

**Örnek:**
```
prompt="A golden retriever running through a sunlit meadow, slow motion, cinematic"
duration_seconds=8
resolution="1080p"
```

### `design_frontend`

Gemini 3 Pro ile yüksek kaliteli frontend bileşen tasarımı.

**Parametreler:**
| Parametre | Tip | Default | Açıklama |
|-----------|-----|---------|----------|
| `component_type` | str | (zorunlu) | Bileşen tipi (button, card, navbar, hero, vb.) |
| `context` | str | "" | Kullanım bağlamı |
| `content_structure` | str | "{}" | JSON formatında bileşen içeriği |
| `theme` | str | "modern-minimal" | Görsel tema |
| `dark_mode` | bool | true | Dark mode desteği |
| `border_radius` | str | "" | Özel köşe yuvarlaklığı |
| `responsive_breakpoints` | str | "sm,md,lg" | Responsive breakpoints |
| `accessibility_level` | str | "AA" | WCAG seviyesi (AA/AAA) |
| `micro_interactions` | bool | true | Hover/focus animasyonları |
| `max_width` | str | "" | Maksimum genişlik |
| `project_context` | str | "" | Proje bağlamı (amaç, hedef kitle, ton, sektör) |

**Bileşen Tipleri (49 adet):**
- **Atoms (13)**: button, input, badge, avatar, icon, dropdown, toggle, tooltip, slider, spinner, progress, chip, divider
- **Molecules (18)**: card, form, modal, tabs, table, accordion, alert, breadcrumb, pagination, search_bar, stat_card, pricing_card, carousel, stepper, timeline, file_upload, rating, color_picker
- **Organisms (18)**: navbar, hero, sidebar, footer, data_table, login_form, signup_form, contact_form, feature_section, testimonial_section, pricing_table, dashboard_header, kanban_board, calendar, chat_widget, notification_center, user_profile, settings_panel

**Temalar (14 adet):**
- `modern-minimal` - Temiz, profesyonel
- `brutalist` - Kalın, yüksek kontrastlı
- `glassmorphism` - Buzlu cam efekti
- `neo-brutalism` - Eğlenceli, canlı renkler
- `soft-ui` - Neumorfik, yumuşak derinlik
- `corporate` - Kurumsal, güvenilir
- `gradient` - Gradient-ağırlıklı modern tasarım
- `cyberpunk` - Neon renkler, koyu arka plan
- `retro` - 80'ler/90'lar ilham
- `pastel` - Yumuşak pastel tonlar
- `dark_mode_first` - Dark mode optimizasyonlu
- `high_contrast` - WCAG AAA erişilebilirlik
- `nature` - Toprak tonları, organik his
- `startup` - Tech startup estetiği

**Örnek:**
```json
{
  "component_type": "pricing_card",
  "context": "SaaS fiyatlandırma sayfası için Pro tier kartı",
  "content_structure": "{\"tier\": \"Pro\", \"price\": \"$29/ay\", \"features\": [\"Sınırsız kullanıcı\", \"Öncelikli destek\"], \"cta\": \"Başla\"}",
  "theme": "modern-minimal",
  "dark_mode": true
}
```

**Çıktı:**
```json
{
  "component_id": "pricing-card-pro",
  "atomic_level": "molecule",
  "html": "<div class=\"bg-white dark:bg-slate-800...\">...</div>",
  "tailwind_classes_used": ["rounded-xl", "shadow-lg", "..."],
  "accessibility_features": ["aria-label", "focus-visible"],
  "responsive_breakpoints": ["sm", "md", "lg"],
  "dark_mode_support": true,
  "micro_interactions": ["hover:shadow-xl", "transition-all"],
  "design_notes": "...",
  "model_used": "gemini-3-pro-preview"
}
```

### `design_page`

Gemini 3 Pro ile tam sayfa template tasarımı.

**Parametreler:**
| Parametre | Tip | Default | Açıklama |
|-----------|-----|---------|----------|
| `template_type` | str | (zorunlu) | Template tipi |
| `context` | str | "" | Kullanım bağlamı |
| `content_structure` | str | "{}" | JSON formatında sayfa içeriği |
| `theme` | str | "modern-minimal" | Görsel tema |
| `dark_mode` | bool | true | Dark mode desteği |
| `project_context` | str | "" | Proje bağlamı |

**Template Tipleri (10 adet):**
- `landing_page` - Marketing landing page (hero, features, testimonials, pricing, CTA, footer)
- `dashboard` - Admin dashboard (sidebar, header, stats, charts, tables)
- `auth_page` - Login/signup sayfası (form, social login, branding)
- `pricing_page` - Fiyatlandırma karşılaştırma (tiers, features, FAQ)
- `blog_post` - Blog makale layout (header, content, sidebar, comments)
- `product_page` - E-commerce ürün sayfası (gallery, details, reviews, related)
- `portfolio` - Portfolio/showcase (hero, projects, about, contact)
- `documentation` - Docs sayfa layout (sidebar nav, content, TOC)
- `error_page` - 404/500 hata sayfaları
- `coming_soon` - Coming soon/maintenance sayfası

### `refine_frontend`

Mevcut bir tasarımı doğal dil ile revize etme.

**Parametreler:**
| Parametre | Tip | Default | Açıklama |
|-----------|-----|---------|----------|
| `previous_html` | str | (zorunlu) | Önceki HTML tasarımı |
| `modifications` | str | (zorunlu) | İstenen değişiklikler (doğal dilde) |
| `project_context` | str | "" | Proje bağlamı |

**Örnek Kullanım:**
```python
# İlk tasarımı al
result = design_frontend(component_type="button", context="CTA butonu")

# Değişiklik iste
refined = refine_frontend(
    previous_html=result["html"],
    modifications="Buton rengini maviden yeşile çevir, köşeleri daha yuvarlak yap"
)
```

**Örnek Modification İstekleri:**
- "Buton rengini maviden yeşile çevir"
- "Header'ı daha kompakt yap"
- "Dark mode desteği ekle"
- "Mobil responsive sorunlarını düzelt"
- "Font boyutunu büyüt"
- "Hover efektini daha belirgin yap"

### `list_frontend_options`

Kullanılabilir bileşen tiplerini, temaları ve template'leri listele.

### `list_models`

Kullanılabilir modelleri listele.

### `clear_chat_session`

Chat oturumunu temizle.

## Kullanılabilir Modeller

### Text Modelleri
- `gemini-3-flash-preview` - Pro-grade reasoning, Flash hızında (1M context)
- `gemini-3-pro-preview` - En güçlü reasoning, kompleks agentic workflows (1M context)

### Image Modelleri
- `gemini-3-pro-image-preview` - Yüksek kalite görsel üretimi (4096px, legible text, character consistency)
- `imagen-4.0-ultra-generate-001` - Ultra yüksek kalite ($0.06/görsel)
- `imagen-4.0-generate-001` - Standart yüksek kalite ($0.04/görsel)
- `imagen-4.0-fast-generate-001` - Hızlı üretim ($0.02/görsel)

### Video Modelleri
- `veo-3.1-generate-001` - Yüksek kalite, native audio (~$0.40/saniye)
- `veo-3.1-fast-generate-001` - Hızlı üretim (~$0.15/saniye)

### Thinking Level
Gemini 3 modelleri için reasoning derinliği:
- `minimal` - Hızlı, basit cevaplar
- `low` - Hafif düşünme
- `medium` - Dengeli yaklaşım (default)
- `high` - Derin reasoning, kompleks problemler

## Sorun Giderme

### "GOOGLE_CLOUD_PROJECT not set" hatası

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### Authentication hatası

```bash
gcloud auth application-default login
```

### Token süresi doldu

Token otomatik olarak yenilenir. Sorun devam ederse:

```bash
gcloud auth application-default print-access-token
```

## Test

```bash
# Token kontrolü
gcloud auth application-default print-access-token

# MCP server'ı manuel çalıştırma
uv run gemini-mcp
```

## Lisans

MIT
