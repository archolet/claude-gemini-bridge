# Degisiklik Gunlugu

Bu proje [Semantic Versioning](https://semver.org/) kullanir.

## [0.1.0] - 2024-12-19

### Eklenenler

- Ilk surum
- `ask_gemini` - Gemini 3'e soru sorma (streaming destekli)
- `chat_gemini` - Cok turlu konusmalar
- `generate_image` - Gemini 3 Pro Image ile gorsel uretimi
- `list_models` - Kullanilabilir modelleri listeleme
- `clear_chat_session` - Chat oturumunu temizleme
- OAuth/ADC ile otomatik kimlik dogrulama
- Token suresi dolunca otomatik yenileme
- Gemini 3 thinking level destegi (minimal, low, medium, high)

### Desteklenen Modeller

- `gemini-3-flash-preview` - Hizli text generation
- `gemini-3-pro-preview` - Guclu reasoning
- `gemini-3-pro-image-preview` - 4096px gorsel uretimi
