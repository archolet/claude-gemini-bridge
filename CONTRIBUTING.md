# Katki Rehberi

Claude Gemini Bridge projesine katki sagladiginiz icin tesekkur ederiz!

## Nasil Katki Saglanir

### Hata Bildirimi

1. Oncelikle [mevcut issue'lari](https://github.com/serkanozdogan/claude-gemini-bridge/issues) kontrol edin
2. Ayni hata bildirilmemisse yeni bir issue acin
3. Issue'da sunlari belirtin:
   - Hatanin acik tanimi
   - Hatanin nasil tekrarlanacagi
   - Beklenen davranis
   - Gerceklesen davranis
   - Python ve paket surumleri

### Ozellik Onerisi

1. Issue acarak onerinizi aciklayin
2. Kullanim senaryolarini belirtin
3. Tartisma sonrasinda implementasyona gecin

### Pull Request

1. Repository'yi fork edin
2. Feature branch olusturun:
   ```bash
   git checkout -b feature/yeni-ozellik
   ```
3. Degisikliklerinizi commit edin:
   ```bash
   git commit -m "feat: yeni ozellik eklendi"
   ```
4. Branch'inizi push edin:
   ```bash
   git push origin feature/yeni-ozellik
   ```
5. Pull Request acin

## Gelistirme Ortami

### Kurulum

```bash
# Repository'yi klonlayin
git clone https://github.com/serkanozdogan/claude-gemini-bridge.git
cd claude-gemini-bridge

# Bagimliliklari yukleyin
uv sync

# Gelistirme bagimlilikLarini yukleyin
uv sync --dev
```

### Testler

```bash
# Testleri calistirin
uv run pytest

# Coverage ile
uv run pytest --cov=gemini_mcp
```

### Kod Stili

- Python 3.10+ ozellikleri kullanilabilir
- Type hints kullanilmalidir
- Docstring'ler Google stilinde yazilmalidir

## Commit Mesajlari

[Conventional Commits](https://www.conventionalcommits.org/) formatini kullanin:

- `feat:` - Yeni ozellik
- `fix:` - Hata duzeltmesi
- `docs:` - Dokumantasyon
- `refactor:` - Kod yeniden duzenleme
- `test:` - Test ekleme/duzeltme
- `chore:` - Bakim islemleri

## Lisans

Katkilariniz MIT lisansi altinda yayinlanacaktir.
