# KOBİ Test - Bug Tracking

**Başlangıç:** 2025-12-25
**Son Güncelleme:** 2025-12-25

## Bug Özeti

| Severity | Sayı |
|----------|------|
| 🔴 CRITICAL | 0 |
| 🟠 HIGH | 0 |
| 🟡 MEDIUM | 0 |
| 🟢 LOW | 0 |

---

## Bug Özeti (Güncel)

| Severity | Sayı |
|----------|------|
| 🔴 CRITICAL | 2 |
| 🟠 HIGH | 0 |
| 🟡 MEDIUM | 0 |
| 🟢 LOW | 0 |

---

## Bulunan Buglar

### BUG-001: design_frontend Trifecta Pipeline Boş HTML Döndürüyor

**Severity:** 🔴 CRITICAL
**Mode:** design_frontend
**Status:** ✅ FIXED

**Fix:** `orchestrator.py:1381` - `section.get("content", "{}")` → `section.get("content", {})`
`content_structure` dict yerine string atanıyordu.

#### Reproduction
1. `design_frontend` çağır
2. `component_type`: "button"
3. `use_trifecta`: true
4. `content_structure`: {"text": "14 Gün Ücretsiz Dene", "icon": "arrow-right"}

#### Expected
Button HTML üretilmeli

#### Actual
- HTML boş string döndü
- validation_passed: false
- Sadece "architect" agent çalıştı

#### Errors
```
dictionary update sequence element #0 has length 1; 2 is required
'str' object has no attribute 'get'
```

#### Analysis
Pipeline Architect aşamasında çöküyor. content_structure parse edilirken dictionary hatası.

---

### BUG-002: fork_for_parallel Defensive Type Check Eksik

**Severity:** 🔴 CRITICAL
**Mode:** Tüm Trifecta Pipeline'ları
**Status:** ✅ FIXED

**Root Cause:** `context.py:504` - `dict(self.content_structure)` çağrısı
type check yapmadan string'i dict'e çevirmeye çalışıyor.

**Error:** `dictionary update sequence element #0 has length 1; 2 is required`

**Fix:** `context.py:504-514` - isinstance() kontrolü eklendi:
```python
forked.content_structure = (
    dict(self.content_structure)
    if isinstance(self.content_structure, dict)
    else {}
)
forked.style_guide = (
    dict(self.style_guide)
    if isinstance(self.style_guide, dict)
    else {}
)
```

**Relation:** BUG-001 ile birlikte çalışır. BUG-001 source'u düzeltir,
BUG-002 defensive layer ekler.

---

### BUG-003: design_frontend HTML Alanı Bazen List Döndürüyor

**Severity:** 🟠 HIGH
**Mode:** design_frontend
**Status:** ✅ FIXED

**Reproduction:**
1. `design_frontend` çağır
2. `component_type`: "card"
3. `use_trifecta`: false
4. Zengin content_structure ile

**Expected:** `"html": "<div>..."` (string)
**Actual:** `"html": ["<div>...", []]` (list)

**Error:** Preview açılırken: `'tuple' object has no attribute 'strip'`

**Analysis:** Gemini API'den gelen response bazen nested list olarak geliyor.
Post-processing sırasında bu handle edilmiyor.

---

### BUG-004: design_page Section Marker'ları Eklemiyor

**Severity:** 🟠 HIGH
**Mode:** design_page
**Status:** 🔍 OPEN

**Expected:** Sayfa HTML'inde section marker'lar olmalı:
```html
<!-- SECTION: hero -->
...hero content...
<!-- /SECTION: hero -->
```

**Actual:** `section_markers_validated: false` ve
`section_marker_issues: ["missing:hero", "missing:features", ...]`

**Impact:** `replace_section_in_page` tool'u çalışamaz çünkü section'ları
bulamaz.

**Root Cause:** `design_page` veya Gemini promptu section marker format'ını
doğru şekilde generate etmiyor.

---

(Devam eden testler)

---

## Bug Template

```markdown
### BUG-XXX: Başlık

**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**Mode:** design_frontend | design_page | design_section | refine_frontend | replace_section_in_page | design_from_reference
**Status:** OPEN | FIXED

#### Reproduction
1. ...

#### Expected
...

#### Actual
...

#### Error
...

#### Fix Suggestion
...
```
