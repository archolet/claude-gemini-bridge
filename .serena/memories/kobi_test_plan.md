# KOBİ.COM.TR - Gemini MCP 6 Mod Kapsamlı Test Planı

**Tarih:** 2025-12-25
**Amaç:** 6 tasarım modunun limitlerine kadar test edilmesi, bug tespiti

## Senaryo

kobi.com.tr - KOBİ'lere Yönelik SaaS Platformu

### Hizmet Yelpazesi
1. Fatura & Muhasebe (e-Fatura, e-Arşiv)
2. Stok Yönetimi (depo, barkod)
3. CRM & Müşteri İlişkileri
4. İnsan Kaynakları (izin, bordro)
5. Proje Yönetimi (Gantt, zaman takibi)
6. E-Ticaret Entegrasyonu
7. Raporlama & BI
8. Mobil Uygulama

## 6 Test Modu

| # | Mod | Açıklama | Test Sayısı |
|---|-----|----------|-------------|
| 1 | design_frontend | Component tasarımı | 5+ |
| 2 | design_page | Tam sayfa layout | 5 |
| 3 | design_section | Section chain | 5 |
| 4 | refine_frontend | İteratif iyileştirme | 5 |
| 5 | replace_section_in_page | Cerrahi değişiklik | 4 |
| 6 | design_from_reference | Vision-based design | 5 |

## Bug Severity Tanımları

- 🔴 **CRITICAL**: Tool çöküyor, hata fırlatıyor
- 🟠 **HIGH**: HTML üretilmiyor veya boş
- 🟡 **MEDIUM**: Eksik özellik (dark mode yok, responsive bozuk)
- 🟢 **LOW**: Kozmetik sorunlar

## Execution Phases

### PHASE 1: Baseline Tests
- Her mod 1 kez temel test

### PHASE 2: Stress Tests
- Kompleks senaryolar
- Chain testleri
- Çoklu iterasyon

### PHASE 3: Theme Coverage
- 14 tema testi

### PHASE 4: Edge Cases
- Hata senaryoları

### PHASE 5: Quality Validation
- Browser preview
- Accessibility audit

## Progress Tracking

- [ ] MODE 1: design_frontend
- [ ] MODE 2: design_page  
- [ ] MODE 3: design_section
- [ ] MODE 4: refine_frontend
- [ ] MODE 5: replace_section_in_page
- [ ] MODE 6: design_from_reference
