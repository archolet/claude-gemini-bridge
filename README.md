# Claude Gemini Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Claude Code için Vertex AI üzerinden Gemini 3 modellerine erişim sağlayan MCP sunucusu.

## Özellikler

- **Text Generation**: Context ve system instruction desteği ile metin üretimi
- **Multi-turn Chat**: Oturum yönetimi ile çok turlu konuşmalar
- **Image Generation**: Gemini ve Imagen modelleri ile görsel üretimi
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

### `list_models`

Kullanılabilir modelleri listele.

### `clear_chat_session`

Chat oturumunu temizle.

## Kullanılabilir Modeller (Gemini 3 Only)

### Text Modelleri
- `gemini-3-flash-preview` - Pro-grade reasoning, Flash hızında (1M context)
- `gemini-3-pro-preview` - En güçlü reasoning, kompleks agentic workflows (1M context)

### Image Modelleri
- `gemini-3-pro-image-preview` - Yüksek kalite görsel üretimi (4096px, legible text, character consistency)

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
