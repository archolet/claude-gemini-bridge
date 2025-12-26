# 🎼 MAESTRO - Akıllı Orkestra Şefi Uygulama Planı

## Versiyon: 1.0
## Tarih: 2025-12-25
## Hazırlayan: Claude (Opus 4.5 için yol haritası)

---

# 📋 İÇİNDEKİLER

1. [Vizyon ve Amaç](#1-vizyon-ve-amaç)
2. [Mimari Tasarım](#2-mimari-tasarım)
3. [Dosya Yapısı](#3-dosya-yapısı)
4. [Modül Detayları](#4-modül-detayları)
5. [Soru Akış Sistemi](#5-soru-akış-sistemi)
6. [Karar Ağacı Algoritması](#6-karar-ağacı-algoritması)
7. [Entegrasyon Noktaları](#7-entegrasyon-noktaları)
8. [TODO Listesi](#8-todo-listesi)
9. [Test Senaryoları](#9-test-senaryoları)
10. [Gelecek Geliştirmeler](#10-gelecek-geliştirmeler)

---

# 1. VİZYON VE AMAÇ

## 1.1 Problem
Kullanıcılar `/design-gemini` komutunu kullanırken:
- Hangi modu seçeceklerini bilmiyorlar
- Tüm parametreleri prompt'ta ifade edemiyorlar
- Mevcut projeleriyle nasıl devam edeceklerini bilemiyorlar
- Optimal tema/vibe/industry kombinasyonlarını keşfedemiyorlar

## 1.2 Çözüm
**Maestro**: Akıllı bir interview sistemi ile kullanıcının gerçek niyetini anlayan, 
doğru modu seçen ve optimal parametreleri belirleyen bir orkestra şefi.

## 1.3 Temel Prensipler
1. **Dinamik Soru Akışı**: Sabit soru listesi değil, cevaplara göre adapte olan sorular
2. **Minimum Sürtünme**: Gereksiz soru sorma, akıllıca atla
3. **Context-Aware**: Mevcut projeleri, draft'ları ve geçmişi göz önünde bulundur
4. **Expert Guidance**: Kullanıcıyı en iyi pratiklere yönlendir
5. **Şeffaflık**: Son kararı göster ve onay al

---

# 2. MİMARİ TASARIM

## 2.1 Yüksek Seviye Mimari

```
┌─────────────────────────────────────────────────────────────────┐
│                         MAESTRO LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │  Interview   │  │   Decision   │  │     Context        │    │
│  │   Engine     │──│     Tree     │──│     Analyzer       │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
│          │                │                    │                │
│          └────────────────┼────────────────────┘                │
│                           ▼                                     │
│              ┌────────────────────────┐                        │
│              │   Parameter Builder    │                        │
│              └────────────────────────┘                        │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXISTING GEMINI_MCP                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │    server    │  │ orchestrator │  │      agents        │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 2.2 Veri Akışı

```
User Input: "/design-gemini"
         │
         ▼
┌─────────────────┐
│  Maestro.start()│
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│ Context Analyzer│────▶│ Existing Projects│
└────────┬────────┘     │ Current Drafts   │
         │              │ Design DNA       │
         ▼              └──────────────────┘
┌─────────────────┐
│Interview Engine │◀──────┐
└────────┬────────┘       │
         │                │
         ▼                │
┌─────────────────┐       │
│  Ask Question   │───────┘ (loop until complete)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Decision Tree  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Parameter Builder│
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│  Final Summary  │────▶│ User Confirmation│
└────────┬────────┘     └──────────────────┘
         │
         ▼
┌─────────────────┐
│ Execute Mode    │───▶ design_frontend / design_page / etc.
└─────────────────┘
```

## 2.3 State Machine

```
                    ┌─────────────┐
                    │    IDLE     │
                    └──────┬──────┘
                           │ /design-gemini
                           ▼
                    ┌─────────────┐
                    │  ANALYZING  │ (context analysis)
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
            ┌──────▶│INTERVIEWING │◀─────┐
            │       └──────┬──────┘      │
            │              │             │
            │         question      answer
            │              │             │
            │              ▼             │
            │       ┌─────────────┐      │
            └───────│  AWAITING   │──────┘
                    │   ANSWER    │
                    └──────┬──────┘
                           │ all questions done
                           ▼
                    ┌─────────────┐
                    │  DECIDING   │ (mode selection)
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ CONFIRMING  │
                    └──────┬──────┘
                           │ user confirms
                           ▼
                    ┌─────────────┐
                    │  EXECUTING  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  COMPLETE   │
                    └─────────────┘
```

---

# 3. DOSYA YAPISI

```
gemini_mcp/
├── maestro/                          # YENİ ANA KLASÖR
│   ├── __init__.py                   # Public API exports
│   ├── core.py                       # Maestro ana sınıfı
│   ├── interview/                    # Interview alt-sistemi
│   │   ├── __init__.py
│   │   ├── engine.py                 # InterviewEngine sınıfı
│   │   ├── state.py                  # InterviewState, SessionState
│   │   └── flow_controller.py        # Soru akış kontrolü
│   ├── questions/                    # Soru yönetimi
│   │   ├── __init__.py
│   │   ├── bank.py                   # QuestionBank - tüm sorular
│   │   ├── categories.py             # Soru kategorileri enum
│   │   ├── models.py                 # Question, Answer dataclass'ları
│   │   └── validators.py             # Cevap validasyonu
│   ├── decision/                     # Karar mekanizması
│   │   ├── __init__.py
│   │   ├── tree.py                   # DecisionTree algoritması
│   │   ├── mode_selector.py          # 6 mod seçim mantığı
│   │   ├── parameter_builder.py      # Parametre oluşturma
│   │   └── rules.py                  # Karar kuralları
│   ├── context/                      # Context analizi
│   │   ├── __init__.py
│   │   ├── analyzer.py               # ContextAnalyzer
│   │   ├── project_scanner.py        # Mevcut proje tarama
│   │   └── dna_extractor.py          # Design DNA çıkarma
│   ├── ui/                           # Kullanıcı arayüzü
│   │   ├── __init__.py
│   │   ├── formatter.py              # Soru/cevap formatlama
│   │   ├── summary.py                # Final özet oluşturma
│   │   └── templates.py              # UI şablonları
│   └── integration/                  # Entegrasyon
│       ├── __init__.py
│       ├── mcp_bridge.py             # MCP server entegrasyonu
│       └── mode_executor.py          # Mod çalıştırma
│
├── server.py                         # MEVCUT - maestro tool eklenecek
├── orchestration/                    # MEVCUT - dokunulmayacak
└── ...
```

---

# 4. MODÜL DETAYLARI

## 4.1 `core.py` - Ana Maestro Sınıfı

```python
"""
Maestro'nun ana giriş noktası.
Tüm alt sistemleri koordine eder.
"""

class Maestro:
    """
    Akıllı orkestra şefi - kullanıcı niyetini anlar ve doğru moda yönlendirir.
    
    Kullanım:
        maestro = Maestro()
        result = await maestro.start_session()
    """
    
    def __init__(self, draft_manager=None, config=None):
        """
        Args:
            draft_manager: Mevcut DraftManager instance (opsiyonel)
            config: MaestroConfig instance (opsiyonel)
        """
        pass
    
    async def start_session(self) -> MaestroSession:
        """Yeni bir Maestro oturumu başlatır."""
        pass
    
    async def process_answer(self, session_id: str, answer: str) -> InterviewResponse:
        """Kullanıcı cevabını işler ve sonraki adımı döner."""
        pass
    
    async def get_final_decision(self, session_id: str) -> MaestroDecision:
        """Tüm cevaplar toplandıktan sonra final kararı döner."""
        pass
    
    async def execute(self, session_id: str, confirmed: bool = True) -> ExecutionResult:
        """Onaylanan kararı çalıştırır."""
        pass
    
    async def abort_session(self, session_id: str) -> None:
        """Oturumu iptal eder."""
        pass
```

## 4.2 `interview/engine.py` - Interview Engine

```python
"""
Soru sorma ve cevap toplama motoru.
Dinamik akış kontrolü sağlar.
"""

class InterviewEngine:
    """
    Dinamik interview yöneticisi.
    Cevaplara göre sonraki soruları belirler.
    """
    
    def __init__(self, question_bank: QuestionBank, context: ContextData):
        pass
    
    def get_next_question(self, current_state: InterviewState) -> Optional[Question]:
        """
        Mevcut state'e göre sonraki soruyu belirler.
        None dönerse interview tamamlanmıştır.
        """
        pass
    
    def process_answer(self, question_id: str, answer: Answer) -> AnswerResult:
        """
        Cevabı validate eder ve state'i günceller.
        """
        pass
    
    def should_skip_question(self, question: Question, state: InterviewState) -> bool:
        """
        Bu sorunun atlanıp atlanmayacağını belirler.
        Örn: "Tek bileşen" seçildiyse sayfa layout soruları atlanır.
        """
        pass
    
    def get_follow_up_questions(self, answer: Answer) -> List[Question]:
        """
        Cevaba göre ek sorular üretir.
        Örn: "E-commerce" seçildiyse "Hangi ödeme sistemleri?" sorusu eklenir.
        """
        pass
    
    def calculate_progress(self, state: InterviewState) -> float:
        """Interview ilerleme yüzdesi (0.0 - 1.0)"""
        pass
```

## 4.3 `questions/bank.py` - Soru Bankası

```python
"""
Tüm soruların merkezi deposu.
Kategorize edilmiş, önceliklendirilmiş sorular.
"""

class QuestionBank:
    """
    Maestro soru havuzu.
    Kategorilere göre organize edilmiş tüm sorular.
    """
    
    # Soru kategorileri ve öncelikleri
    CATEGORIES = {
        "intent": {
            "priority": 1,  # İlk sorulacak
            "required": True,
            "description": "Kullanıcının temel niyetini anla"
        },
        "scope": {
            "priority": 2,
            "required": True,
            "description": "İşin kapsamını belirle"
        },
        "existing_context": {
            "priority": 3,
            "required": False,  # Mevcut proje varsa
            "description": "Mevcut proje ile ilişkiyi anla"
        },
        "industry": {
            "priority": 4,
            "required": False,  # B2B/Corporate ise
            "description": "Sektör ve profesyonellik seviyesi"
        },
        "theme_style": {
            "priority": 5,
            "required": True,
            "description": "Görsel stil ve tema tercihi"
        },
        "vibe_mood": {
            "priority": 6,
            "required": False,  # Yaratıcı projeler için
            "description": "Tasarımın hissi ve havası"
        },
        "content": {
            "priority": 7,
            "required": False,  # İçerik detayı gerekiyorsa
            "description": "İçerik yapısı ve metinler"
        },
        "technical": {
            "priority": 8,
            "required": False,  # Advanced kullanıcılar için
            "description": "Teknik gereksinimler"
        },
        "accessibility": {
            "priority": 9,
            "required": False,  # Corporate/B2B ise
            "description": "Erişilebilirlik gereksinimleri"
        },
        "language": {
            "priority": 10,
            "required": True,
            "description": "İçerik dili"
        }
    }
    
    def get_questions_by_category(self, category: str) -> List[Question]:
        pass
    
    def get_required_questions(self) -> List[Question]:
        pass
    
    def get_conditional_questions(self, conditions: Dict) -> List[Question]:
        pass
```

## 4.4 `decision/tree.py` - Karar Ağacı

```python
"""
Toplanan cevaplardan mod ve parametreleri belirleyen karar ağacı.
"""

class DecisionTree:
    """
    6 mod arasında seçim yapan karar algoritması.
    
    Modlar:
        1. design_frontend - Tek bileşen
        2. design_page - Tam sayfa
        3. design_section - Sayfa bölümü
        4. refine_frontend - İyileştirme
        5. replace_section_in_page - Bölüm değiştirme
        6. design_from_reference - Referanstan tasarım
    """
    
    def evaluate(self, interview_data: InterviewData) -> ModeDecision:
        """
        Interview verilerini değerlendirir ve mod kararı verir.
        
        Returns:
            ModeDecision: Seçilen mod ve parametreler
        """
        pass
    
    def _determine_mode(self, data: InterviewData) -> DesignMode:
        """
        Karar kurallarına göre modu belirler.
        
        Karar Mantığı:
        
        1. Referans görsel var mı?
           └─ Evet → MODE 6: design_from_reference
        
        2. Mevcut tasarım üzerinde çalışma mı?
           ├─ Evet + İyileştirme → MODE 4: refine_frontend
           └─ Evet + Bölüm değiştirme → MODE 5: replace_section_in_page
        
        3. Sıfırdan yeni tasarım:
           ├─ Tek bileşen → MODE 1: design_frontend
           ├─ Tam sayfa → MODE 2: design_page
           └─ Sayfa bölümü → MODE 3: design_section
        """
        pass
    
    def _build_parameters(self, mode: DesignMode, data: InterviewData) -> Dict[str, Any]:
        """
        Seçilen mod için optimal parametreleri oluşturur.
        """
        pass
```

## 4.5 `context/analyzer.py` - Context Analyzer

```python
"""
Mevcut projeleri ve geçmişi analiz eder.
"""

class ContextAnalyzer:
    """
    Kullanıcının mevcut projelerini ve design DNA'sını analiz eder.
    """
    
    def __init__(self, draft_manager: DraftManager):
        pass
    
    async def analyze(self) -> ContextData:
        """
        Tam context analizi yapar.
        
        Returns:
            ContextData: Mevcut projeler, draft'lar, stil bilgileri
        """
        pass
    
    def get_existing_projects(self) -> List[ProjectSummary]:
        """
        Mevcut projeleri listeler.
        
        Returns:
            List[ProjectSummary]: Proje özetleri
                - project_name
                - last_modified
                - section_count
                - theme_used
                - completion_percentage
        """
        pass
    
    def extract_design_dna(self, project_name: str) -> Optional[DesignDNA]:
        """
        Belirli bir projeden design DNA çıkarır.
        
        Returns:
            DesignDNA: Renk paleti, tipografi, spacing, efektler
        """
        pass
    
    def suggest_continuation(self) -> Optional[ContinuationSuggestion]:
        """
        Son çalışılan projeye devam önerisi.
        
        Mantık:
        - Son 24 saat içinde çalışılan proje varsa öner
        - Tamamlanmamış projeler öncelikli
        """
        pass
    
    def find_similar_projects(self, intent: str) -> List[ProjectSummary]:
        """
        Yeni istek ile benzer projeleri bulur.
        Örn: "landing page" istendi, mevcut landing page'ler listelenir.
        """
        pass
```

---

# 5. SORU AKIŞ SİSTEMİ

## 5.1 Soru Kategorileri ve Soruları

### Kategori 1: INTENT (Niyet) - Zorunlu
```yaml
questions:
  - id: "intent_main"
    text: "Ne yapmak istiyorsunuz?"
    type: "single_choice"
    options:
      - value: "new"
        label: "🆕 Sıfırdan yeni bir tasarım"
        leads_to: "scope"
      - value: "continue"
        label: "🔄 Mevcut proje üzerinde devam"
        leads_to: "existing_context"
        condition: "has_existing_projects"
      - value: "reference"
        label: "🎨 Bir referans görselden ilham al"
        leads_to: "reference_upload"
      - value: "improve"
        label: "✏️ Var olan tasarımı iyileştir"
        leads_to: "improvement_type"
```

### Kategori 2: SCOPE (Kapsam) - Zorunlu
```yaml
questions:
  - id: "scope_type"
    text: "Ne ölçekte bir tasarım düşünüyorsunuz?"
    type: "single_choice"
    show_when: "intent == 'new'"
    options:
      - value: "component"
        label: "🧩 Tek bileşen (button, card, form, modal, vb.)"
        follow_up: "component_type"
      - value: "page"
        label: "📄 Tam sayfa (landing, dashboard, portfolio, vb.)"
        follow_up: "page_type"
      - value: "section"
        label: "📑 Sayfa bölümü (hero, pricing, testimonials, vb.)"
        follow_up: "section_type"
        
  - id: "component_type"
    text: "Hangi tür bileşen?"
    type: "single_choice_with_other"
    show_when: "scope_type == 'component'"
    options:
      - "Button / CTA"
      - "Card (Product, Profile, Info)"
      - "Form (Login, Contact, Newsletter)"
      - "Navigation (Navbar, Sidebar, Tabs)"
      - "Modal / Dialog"
      - "Hero Banner"
      - "Pricing Table"
      - "Testimonial"
      - "Footer"
      - "Diğer (açıklayın)"

  - id: "page_type"
    text: "Hangi tür sayfa?"
    type: "single_choice_with_other"
    show_when: "scope_type == 'page'"
    options:
      - "Landing Page"
      - "Dashboard"
      - "Portfolio / Showcase"
      - "E-commerce Product Page"
      - "Blog / Article Page"
      - "About / Company Page"
      - "Contact Page"
      - "Authentication (Login/Register)"
      - "Diğer (açıklayın)"
      
  - id: "section_type"
    text: "Hangi tür bölüm?"
    type: "single_choice"
    show_when: "scope_type == 'section'"
    options:
      - "Hero / Header"
      - "Features / Services"
      - "Pricing"
      - "Testimonials / Reviews"
      - "Team"
      - "FAQ"
      - "CTA (Call to Action)"
      - "Footer"
      - "Stats / Metrics"
      - "Gallery / Portfolio"
```

### Kategori 3: EXISTING CONTEXT (Mevcut Bağlam) - Koşullu
```yaml
questions:
  - id: "existing_project_select"
    text: "Hangi proje üzerinde çalışmak istiyorsunuz?"
    type: "dynamic_choice"  # Mevcut projelerden liste
    show_when: "intent == 'continue'"
    data_source: "existing_projects"
    
  - id: "existing_action"
    text: "Bu proje ile ne yapmak istiyorsunuz?"
    type: "single_choice"
    show_when: "existing_project_select != null"
    options:
      - value: "add_section"
        label: "➕ Yeni bölüm ekle"
        mode: "design_section"
      - value: "replace_section"
        label: "🔄 Mevcut bölümü değiştir"
        mode: "replace_section_in_page"
      - value: "refine"
        label: "✨ Tasarımı iyileştir"
        mode: "refine_frontend"
      - value: "continue_building"
        label: "🏗️ Kaldığım yerden devam et"
        mode: "design_section"
```

### Kategori 4: INDUSTRY (Sektör) - Koşullu
```yaml
questions:
  - id: "target_audience"
    text: "Hedef kitle kim?"
    type: "single_choice"
    options:
      - value: "b2c"
        label: "👤 Bireysel kullanıcılar (B2C)"
      - value: "b2b"
        label: "🏢 İş dünyası / Kurumsal (B2B)"
        follow_up: "industry_type"
      - value: "internal"
        label: "🔒 İç kullanım (şirket içi araç)"
      - value: "creative"
        label: "🎨 Yaratıcı / Portfolyo"
        
  - id: "industry_type"
    text: "Hangi sektör için?"
    type: "single_choice_with_other"
    show_when: "target_audience == 'b2b'"
    options:
      - value: "finance"
        label: "💰 Finans / Bankacılık"
        preset: "corporate_finance"
      - value: "healthcare"
        label: "🏥 Sağlık"
        preset: "corporate_healthcare"
      - value: "legal"
        label: "⚖️ Hukuk"
        preset: "corporate_legal"
      - value: "tech"
        label: "💻 Teknoloji / SaaS"
        preset: "corporate_tech"
      - value: "manufacturing"
        label: "🏭 Üretim / Endüstri"
        preset: "corporate_manufacturing"
      - value: "consulting"
        label: "📊 Danışmanlık"
        preset: "corporate_consulting"
      - value: "education"
        label: "📚 Eğitim"
      - value: "other"
        label: "Diğer"
        
  - id: "formality_level"
    text: "Ne kadar resmi/formal bir görünüm istiyorsunuz?"
    type: "slider"
    show_when: "target_audience == 'b2b'"
    min: 1
    max: 5
    labels:
      1: "Casual / Samimi"
      3: "Profesyonel"
      5: "Ultra Corporate / Çok Resmi"
```

### Kategori 5: THEME & STYLE (Tema ve Stil) - Zorunlu
```yaml
questions:
  - id: "theme_preference"
    text: "Görsel stil tercihiniz nedir?"
    type: "single_choice"
    options:
      - value: "modern_minimal"
        label: "✨ Modern Minimal"
        description: "Temiz çizgiler, bol beyaz alan"
      - value: "glassmorphism"
        label: "🪟 Glassmorphism"
        description: "Cam efekti, bulanıklık, şeffaflık"
      - value: "brutalist"
        label: "🔲 Brutalist"
        description: "Sert kenarlıklar, yüksek kontrast"
      - value: "neo_brutalism"
        label: "🎨 Neo-Brutalism"
        description: "Playful, offset gölgeler, canlı renkler"
      - value: "soft_ui"
        label: "☁️ Soft UI (Neumorphism)"
        description: "Yumuşak 3D, içe/dışa gölgeler"
      - value: "gradient"
        label: "🌈 Gradient Heavy"
        description: "Canlı gradyanlar, modern"
      - value: "cyberpunk"
        label: "🌆 Cyberpunk / Neon"
        description: "Karanlık, neon ışıklar, glow efektleri"
      - value: "retro"
        label: "📼 Retro / Nostaljik"
        description: "80s, 90s veya Y2K estetiği"
      - value: "pastel"
        label: "🎀 Pastel / Soft"
        description: "Yumuşak renkler, hafif"
      - value: "dark_mode"
        label: "🌙 Dark Mode First"
        description: "Karanlık tema öncelikli"
      - value: "corporate"
        label: "💼 Corporate / Profesyonel"
        description: "Kurumsal, güvenilir"
      - value: "auto"
        label: "🤖 Benim için seç"
        description: "Diğer cevaplarıma göre öner"

  - id: "color_preference"
    text: "Renk tercihiniz var mı?"
    type: "multi_choice_with_other"
    options:
      - "Mavi tonları (güven, profesyonellik)"
      - "Yeşil tonları (doğa, büyüme)"
      - "Mor/Pembe (yaratıcılık, lüks)"
      - "Turuncu/Sarı (enerji, neşe)"
      - "Kırmızı (tutku, aciliyet)"
      - "Nötr/Monokrom (minimal, elegant)"
      - "Belirli bir marka rengim var"
      - "Kararı sana bırakıyorum"
```

### Kategori 6: VIBE & MOOD (His ve Hava) - Koşullu
```yaml
questions:
  - id: "design_vibe"
    text: "Tasarımın hangi hissi vermesini istiyorsunuz?"
    type: "multi_choice"
    max_selections: 3
    show_when: "target_audience != 'b2b' OR formality_level < 4"
    options:
      - value: "professional"
        label: "💼 Profesyonel & Güvenilir"
      - value: "playful"
        label: "🎮 Eğlenceli & Oyunsu"
      - value: "luxurious"
        label: "✨ Lüks & Premium"
      - value: "friendly"
        label: "😊 Samimi & Sıcak"
      - value: "bold"
        label: "💪 Cesur & Dikkat Çekici"
      - value: "calm"
        label: "🧘 Sakin & Huzurlu"
      - value: "innovative"
        label: "🚀 Yenilikçi & Teknolojik"
      - value: "nostalgic"
        label: "📻 Nostaljik & Retro"
      - value: "minimalist"
        label: "⬜ Minimalist & Sade"
      - value: "energetic"
        label: "⚡ Enerjik & Dinamik"
```

### Kategori 7: CONTENT (İçerik) - Koşullu
```yaml
questions:
  - id: "content_ready"
    text: "İçerikleriniz hazır mı?"
    type: "single_choice"
    options:
      - value: "yes"
        label: "✅ Evet, metinlerim hazır"
        follow_up: "content_input"
      - value: "partial"
        label: "📝 Kısmen hazır"
        follow_up: "content_partial"
      - value: "no"
        label: "❌ Hayır, placeholder kullan"
      - value: "generate"
        label: "🤖 Benim için üret"
        follow_up: "content_generate_context"

  - id: "content_input"
    text: "Temel içerikleri girebilir misiniz?"
    type: "structured_input"
    show_when: "content_ready == 'yes'"
    fields:
      - name: "headline"
        label: "Ana başlık"
        required: true
      - name: "subheadline"
        label: "Alt başlık"
        required: false
      - name: "cta_text"
        label: "CTA butonu metni"
        required: false
      - name: "features"
        label: "Özellikler (virgülle ayırın)"
        required: false
        type: "textarea"
```

### Kategori 8: TECHNICAL (Teknik) - Koşullu (Advanced)
```yaml
questions:
  - id: "technical_level"
    text: "Teknik detaylarla ilgilenir misiniz?"
    type: "single_choice"
    options:
      - value: "no"
        label: "Hayır, varsayılanları kullan"
      - value: "yes"
        label: "Evet, kontrol etmek istiyorum"
        follow_up: "technical_details"

  - id: "technical_details"
    text: "Teknik tercihler:"
    type: "multi_toggle"
    show_when: "technical_level == 'yes'"
    options:
      - name: "dark_mode_support"
        label: "Dark mode desteği"
        default: true
      - name: "responsive"
        label: "Responsive tasarım"
        default: true
      - name: "animations"
        label: "Animasyonlar"
        default: true
      - name: "micro_interactions"
        label: "Mikro etkileşimler"
        default: true
      - name: "alpine_js"
        label: "Alpine.js interaktivite"
        default: true

  - id: "complexity_preference"
    text: "Görsel yoğunluk tercihiniz?"
    type: "slider"
    show_when: "technical_level == 'yes'"
    min: 1
    max: 5
    labels:
      1: "Basit & Temiz"
      3: "Dengeli"
      5: "Ultra Detaylı & Zengin"
```

### Kategori 9: ACCESSIBILITY (Erişilebilirlik) - Koşullu
```yaml
questions:
  - id: "accessibility_required"
    text: "Erişilebilirlik gereksinimleri var mı?"
    type: "single_choice"
    show_when: "target_audience == 'b2b' OR industry_type in ['healthcare', 'legal', 'finance']"
    options:
      - value: "standard"
        label: "Standart (WCAG AA)"
        sets: { "a11y_level": "AA" }
      - value: "strict"
        label: "Yüksek (WCAG AAA)"
        sets: { "a11y_level": "AAA" }
      - value: "basic"
        label: "Temel"
        sets: { "a11y_level": "A" }
```

### Kategori 10: LANGUAGE (Dil) - Zorunlu
```yaml
questions:
  - id: "content_language"
    text: "İçerik dili?"
    type: "single_choice"
    default: "tr"
    options:
      - value: "tr"
        label: "🇹🇷 Türkçe"
      - value: "en"
        label: "🇬🇧 English"
      - value: "de"
        label: "🇩🇪 Deutsch"
```

## 5.2 Soru Atlama Kuralları

```python
SKIP_RULES = {
    # Mevcut proje yoksa existing_context kategorisi atlanır
    "existing_context": lambda state: not state.has_existing_projects,
    
    # B2C/Creative ise industry soruları atlanır
    "industry": lambda state: state.answers.get("target_audience") not in ["b2b", "internal"],
    
    # Basit bileşen ise vibe/mood soruları minimal
    "vibe_mood": lambda state: state.answers.get("scope_type") == "component" and 
                               state.answers.get("component_type") in ["button", "form"],
    
    # Technical level "no" ise detaylar atlanır
    "technical_details": lambda state: state.answers.get("technical_level") == "no",
    
    # Non-B2B ise accessibility detay soruları atlanır
    "accessibility_required": lambda state: state.answers.get("target_audience") != "b2b",
}
```

## 5.3 Follow-up Soru Mantığı

```python
FOLLOW_UP_TRIGGERS = {
    # E-commerce seçilirse ödeme/sepet soruları
    "page_type:e-commerce": [
        "ecommerce_product_count",
        "ecommerce_payment_display",
        "ecommerce_cart_visibility"
    ],
    
    # SaaS seçilirse pricing tier soruları
    "page_type:saas": [
        "saas_pricing_tiers",
        "saas_free_trial",
        "saas_feature_comparison"
    ],
    
    # Referans modu seçilirse upload soruları
    "intent:reference": [
        "reference_upload",
        "reference_adherence_level",
        "reference_elements_to_keep"
    ],
    
    # Brand rengi varsa detay soruları
    "color_preference:brand": [
        "brand_primary_color",
        "brand_secondary_color",
        "brand_logo_upload"
    ]
}
```

---

# 6. KARAR AĞACI ALGORİTMASI

## 6.1 Mod Seçim Flowchart

```
                            START
                              │
                              ▼
                    ┌─────────────────┐
                    │ Referans görsel │
                    │     var mı?     │
                    └────────┬────────┘
                             │
               ┌─────────────┴─────────────┐
               │ EVET                      │ HAYIR
               ▼                           ▼
    ┌──────────────────┐         ┌─────────────────┐
    │ MODE 6:          │         │ Mevcut tasarım  │
    │ design_from_     │         │ üzerinde mi?    │
    │ reference        │         └────────┬────────┘
    └──────────────────┘                  │
                              ┌───────────┴───────────┐
                              │ EVET                  │ HAYIR
                              ▼                       ▼
                    ┌─────────────────┐     ┌─────────────────┐
                    │ İyileştirme mi? │     │ Kapsam nedir?   │
                    │ Değiştirme mi?  │     └────────┬────────┘
                    └────────┬────────┘              │
                             │              ┌────────┼────────┐
               ┌─────────────┴──────┐       │        │        │
               │ İYİLEŞTİRME        │ DEĞİŞTİRME     │        │
               ▼                    ▼       │        │        │
    ┌──────────────────┐  ┌──────────────┐  │        │        │
    │ MODE 4:          │  │ MODE 5:      │  │        │        │
    │ refine_frontend  │  │ replace_     │  │        │        │
    └──────────────────┘  │ section_in_  │  │        │        │
                          │ page         │  │        │        │
                          └──────────────┘  │        │        │
                                            ▼        ▼        ▼
                                         BİLEŞEN  SAYFA   BÖLÜM
                                            │        │        │
                                            ▼        ▼        ▼
                                 ┌──────────┐ ┌──────┐ ┌──────────┐
                                 │ MODE 1:  │ │MODE 2│ │ MODE 3:  │
                                 │ design_  │ │design│ │ design_  │
                                 │ frontend │ │_page │ │ section  │
                                 └──────────┘ └──────┘ └──────────┘
```

## 6.2 Parametre Oluşturma Matrisi

```python
PARAMETER_MAPPING = {
    "design_frontend": {
        # Interview Answer → Parameter mapping
        "component_type": lambda a: a.get("component_type", "card"),
        "theme": lambda a: a.get("theme_preference", "modern-minimal"),
        "vibe": lambda a: a.get("design_vibe", [None])[0],
        "industry": lambda a: a.get("industry_type") if a.get("target_audience") == "b2b" else None,
        "formality": lambda a: ["casual", "neutral", "formal", "corporate", "ultra_corporate"][a.get("formality_level", 3) - 1] if a.get("target_audience") == "b2b" else None,
        "content_structure": lambda a: build_content_structure(a),
        "content_language": lambda a: a.get("content_language", "tr"),
        "use_trifecta": lambda a: True,  # Her zaman Trifecta kullan
        "quality_target": lambda a: "corporate" if a.get("target_audience") == "b2b" else "standard",
        # Teknik tercihler
        "dark_mode": lambda a: a.get("dark_mode_support", True),
        "responsive": lambda a: a.get("responsive", True),
        "animations": lambda a: a.get("animations", True),
    },
    
    "design_page": {
        "page_type": lambda a: a.get("page_type", "landing"),
        "theme": lambda a: a.get("theme_preference", "modern-minimal"),
        "sections": lambda a: determine_sections(a),
        "industry": lambda a: a.get("industry_type"),
        "content_language": lambda a: a.get("content_language", "tr"),
        "project_name": lambda a: generate_project_name(a),
    },
    
    "design_section": {
        "section_type": lambda a: a.get("section_type", "hero"),
        "previous_html": lambda a: a.get("existing_project_html"),
        "match_existing_style": lambda a: True,
        "content_language": lambda a: a.get("content_language", "tr"),
    },
    
    "refine_frontend": {
        "existing_html": lambda a: a.get("existing_project_html"),
        "modification_request": lambda a: build_modification_request(a),
        "preserve_structure": lambda a: a.get("preserve_structure", True),
    },
    
    "replace_section_in_page": {
        "full_page_html": lambda a: a.get("existing_project_html"),
        "section_to_replace": lambda a: a.get("section_to_replace"),
        "new_section_type": lambda a: a.get("new_section_type"),
    },
    
    "design_from_reference": {
        "reference_image": lambda a: a.get("reference_image_path"),
        "adherence_level": lambda a: a.get("reference_adherence_level", "inspired"),
        "elements_to_keep": lambda a: a.get("reference_elements_to_keep", []),
        "content_language": lambda a: a.get("content_language", "tr"),
    },
}
```

## 6.3 Akıllı Öneri Sistemi

```python
class SmartRecommender:
    """
    Kullanıcı cevaplarına göre optimal değerleri önerir.
    """
    
    def recommend_theme(self, answers: Dict) -> str:
        """
        Cevaplara göre tema önerir.
        """
        rules = [
            # B2B + Finance → Corporate tema
            (lambda a: a.get("industry_type") == "finance", "corporate"),
            
            # Playful vibe → Neo-Brutalism
            (lambda a: "playful" in a.get("design_vibe", []), "neo_brutalism"),
            
            # Luxurious vibe → Glassmorphism
            (lambda a: "luxurious" in a.get("design_vibe", []), "glassmorphism"),
            
            # Tech/SaaS → Gradient veya Modern Minimal
            (lambda a: a.get("industry_type") == "tech", "gradient"),
            
            # Dark mode preference → Dark mode first
            (lambda a: a.get("dark_mode_preference") == "dark_only", "dark_mode_first"),
            
            # Default
            (lambda a: True, "modern_minimal"),
        ]
        
        for condition, theme in rules:
            if condition(answers):
                return theme
        return "modern_minimal"
    
    def recommend_sections(self, answers: Dict) -> List[str]:
        """
        Sayfa tipine göre section önerir.
        """
        page_type = answers.get("page_type", "landing")
        
        section_templates = {
            "landing": ["navbar", "hero", "features", "testimonials", "pricing", "cta", "footer"],
            "dashboard": ["sidebar", "header", "stats", "charts", "activity", "settings"],
            "portfolio": ["navbar", "hero", "gallery", "about", "contact", "footer"],
            "e-commerce": ["navbar", "hero", "featured_products", "categories", "testimonials", "footer"],
            "blog": ["navbar", "hero", "featured_posts", "categories", "newsletter", "footer"],
        }
        
        return section_templates.get(page_type, section_templates["landing"])
```

---

# 7. ENTEGRASYON NOKTALARI

## 7.1 MCP Server Entegrasyonu (`server.py`)

```python
# server.py'ye eklenecek yeni tool

@mcp.tool()
async def design_wizard() -> Dict[str, Any]:
    """
    🎼 Maestro - Akıllı Tasarım Asistanı
    
    Interaktif bir soru-cevap süreci ile ne istediğinizi anlar ve
    en uygun tasarım modunu sizin için seçer.
    
    Kullanım: Bu tool'u çağırdığınızda Maestro sizinle konuşmaya başlar.
    
    Returns:
        İlk soru ve mevcut proje bilgileri
    """
    from .maestro import Maestro
    
    maestro = Maestro(draft_manager=draft_manager)
    session = await maestro.start_session()
    
    return {
        "session_id": session.id,
        "greeting": session.greeting,
        "context_summary": session.context_summary,
        "first_question": session.current_question,
        "existing_projects": session.existing_projects,
    }


@mcp.tool()
async def wizard_answer(session_id: str, answer: str) -> Dict[str, Any]:
    """
    Maestro'ya cevap ver.
    
    Args:
        session_id: Aktif oturum ID'si
        answer: Kullanıcı cevabı (seçenek harfi veya metin)
    
    Returns:
        Sonraki soru veya final karar özeti
    """
    from .maestro import get_session
    
    session = get_session(session_id)
    result = await session.process_answer(answer)
    
    if result.is_complete:
        return {
            "status": "complete",
            "decision": result.decision.to_dict(),
            "summary": result.summary,
            "ready_to_execute": True,
        }
    else:
        return {
            "status": "in_progress",
            "progress": result.progress,
            "next_question": result.next_question,
        }


@mcp.tool()
async def wizard_execute(session_id: str, confirmed: bool = True) -> Dict[str, Any]:
    """
    Maestro kararını çalıştır.
    
    Args:
        session_id: Aktif oturum ID'si
        confirmed: Kullanıcı onayı
    
    Returns:
        Seçilen mod'un çıktısı
    """
    from .maestro import get_session
    
    if not confirmed:
        return {"status": "cancelled", "message": "Kullanıcı iptal etti"}
    
    session = get_session(session_id)
    result = await session.execute()
    
    return result
```

## 7.2 Mevcut Modüllerle Entegrasyon

```python
# maestro/integration/mode_executor.py

class ModeExecutor:
    """
    Maestro kararını mevcut MCP tool'larına yönlendirir.
    """
    
    def __init__(self, mcp_server):
        self.server = mcp_server
        
        # Mod → Fonksiyon mapping
        self.mode_handlers = {
            "design_frontend": self._execute_design_frontend,
            "design_page": self._execute_design_page,
            "design_section": self._execute_design_section,
            "refine_frontend": self._execute_refine_frontend,
            "replace_section_in_page": self._execute_replace_section,
            "design_from_reference": self._execute_from_reference,
        }
    
    async def execute(self, decision: MaestroDecision) -> Dict[str, Any]:
        """
        Kararı çalıştırır.
        """
        handler = self.mode_handlers.get(decision.mode)
        if not handler:
            raise ValueError(f"Unknown mode: {decision.mode}")
        
        return await handler(decision.parameters)
    
    async def _execute_design_frontend(self, params: Dict) -> Dict:
        """design_frontend tool'unu çağırır."""
        # Mevcut design_frontend fonksiyonunu import et ve çağır
        from ..server import design_frontend
        return await design_frontend(**params)
    
    # ... diğer handler'lar
```

## 7.3 Draft Manager Entegrasyonu

```python
# maestro/context/project_scanner.py

class ProjectScanner:
    """
    Mevcut projeleri tarar ve analiz eder.
    """
    
    def __init__(self, draft_manager: DraftManager):
        self.draft_manager = draft_manager
    
    def scan_all_projects(self) -> List[ProjectInfo]:
        """
        Tüm projeleri tarar.
        """
        projects = []
        
        # draft_manager'dan tüm projeleri al
        for project_name in self.draft_manager.list_projects():
            drafts = self.draft_manager.list_drafts(project_name)
            
            if not drafts:
                continue
            
            # Son draft'tan bilgi çıkar
            latest_draft = max(drafts, key=lambda d: d.get("timestamp", 0))
            
            projects.append(ProjectInfo(
                name=project_name,
                draft_count=len(drafts),
                last_modified=latest_draft.get("timestamp"),
                sections=self._extract_sections(latest_draft),
                theme=self._detect_theme(latest_draft),
                completion=self._estimate_completion(drafts),
            ))
        
        return sorted(projects, key=lambda p: p.last_modified, reverse=True)
    
    def get_project_html(self, project_name: str) -> Optional[str]:
        """
        Projenin son HTML'ini döner.
        """
        return self.draft_manager.get_latest_html(project_name)
    
    def _extract_sections(self, draft: Dict) -> List[str]:
        """
        HTML'den section listesi çıkarır.
        """
        html = draft.get("content", "")
        return list_sections(html)  # section_utils'den
    
    def _detect_theme(self, draft: Dict) -> Optional[str]:
        """
        Kullanılan temayı tespit eder.
        """
        metadata = draft.get("metadata", {})
        return metadata.get("theme")
    
    def _estimate_completion(self, drafts: List[Dict]) -> float:
        """
        Projenin tamamlanma yüzdesini tahmin eder.
        """
        # Basit heuristik: section sayısına göre
        sections = set()
        for draft in drafts:
            sections.update(self._extract_sections(draft))
        
        # Tipik bir sayfa 5-7 section içerir
        return min(1.0, len(sections) / 6.0)
```

---

# 8. TODO LİSTESİ

## 🔴 Faz 1: Temel Altyapı (Öncelik: Yüksek)

### 1.1 Klasör Yapısını Oluştur
- [ ] `gemini_mcp/maestro/` klasörünü oluştur
- [ ] `__init__.py` dosyalarını oluştur
- [ ] Alt klasörleri oluştur: `interview/`, `questions/`, `decision/`, `context/`, `ui/`, `integration/`

### 1.2 Data Models (Pydantic)
- [ ] `maestro/models.py` oluştur
- [ ] `Question` dataclass tanımla
- [ ] `Answer` dataclass tanımla
- [ ] `InterviewState` dataclass tanımla
- [ ] `MaestroSession` dataclass tanımla
- [ ] `MaestroDecision` dataclass tanımla
- [ ] `ProjectInfo` dataclass tanımla
- [ ] `ContextData` dataclass tanımla

### 1.3 Core Maestro Class
- [ ] `maestro/core.py` oluştur
- [ ] `Maestro` class'ını implement et
- [ ] `start_session()` metodunu yaz
- [ ] `process_answer()` metodunu yaz
- [ ] `get_final_decision()` metodunu yaz
- [ ] `execute()` metodunu yaz
- [ ] Session management (create, get, delete)

---

## 🟠 Faz 2: Interview Sistemi (Öncelik: Yüksek)

### 2.1 Question Bank
- [ ] `maestro/questions/bank.py` oluştur
- [ ] `QuestionBank` class'ını implement et
- [ ] Kategori 1: INTENT sorularını ekle
- [ ] Kategori 2: SCOPE sorularını ekle
- [ ] Kategori 3: EXISTING CONTEXT sorularını ekle
- [ ] Kategori 4: INDUSTRY sorularını ekle
- [ ] Kategori 5: THEME & STYLE sorularını ekle
- [ ] Kategori 6: VIBE & MOOD sorularını ekle
- [ ] Kategori 7: CONTENT sorularını ekle
- [ ] Kategori 8: TECHNICAL sorularını ekle
- [ ] Kategori 9: ACCESSIBILITY sorularını ekle
- [ ] Kategori 10: LANGUAGE sorularını ekle

### 2.2 Interview Engine
- [ ] `maestro/interview/engine.py` oluştur
- [ ] `InterviewEngine` class'ını implement et
- [ ] `get_next_question()` metodunu yaz
- [ ] `process_answer()` metodunu yaz
- [ ] `should_skip_question()` metodunu yaz
- [ ] `get_follow_up_questions()` metodunu yaz
- [ ] `calculate_progress()` metodunu yaz

### 2.3 Flow Controller
- [ ] `maestro/interview/flow_controller.py` oluştur
- [ ] Skip rules'ları implement et
- [ ] Follow-up triggers'ları implement et
- [ ] Kategori önceliklendirmesi implement et

### 2.4 Answer Validators
- [ ] `maestro/questions/validators.py` oluştur
- [ ] Single choice validator
- [ ] Multi choice validator
- [ ] Text input validator
- [ ] Slider validator
- [ ] File upload validator

---

## 🟡 Faz 3: Karar Sistemi (Öncelik: Orta)

### 3.1 Decision Tree
- [ ] `maestro/decision/tree.py` oluştur
- [ ] `DecisionTree` class'ını implement et
- [ ] `evaluate()` metodunu yaz
- [ ] `_determine_mode()` metodunu yaz
- [ ] Mod seçim kurallarını implement et

### 3.2 Mode Selector
- [ ] `maestro/decision/mode_selector.py` oluştur
- [ ] 6 mod için seçim mantığını yaz
- [ ] Conflict resolution (birden fazla mod uygunsa)

### 3.3 Parameter Builder
- [ ] `maestro/decision/parameter_builder.py` oluştur
- [ ] `ParameterBuilder` class'ını implement et
- [ ] Her mod için parameter mapping'i yaz
- [ ] Content structure builder
- [ ] Section list builder

### 3.4 Smart Recommender
- [ ] `maestro/decision/recommender.py` oluştur
- [ ] `SmartRecommender` class'ını implement et
- [ ] `recommend_theme()` metodunu yaz
- [ ] `recommend_sections()` metodunu yaz
- [ ] `recommend_vibe()` metodunu yaz

---

## 🟢 Faz 4: Context Sistemi (Öncelik: Orta)

### 4.1 Context Analyzer
- [ ] `maestro/context/analyzer.py` oluştur
- [ ] `ContextAnalyzer` class'ını implement et
- [ ] `analyze()` metodunu yaz

### 4.2 Project Scanner
- [ ] `maestro/context/project_scanner.py` oluştur
- [ ] `ProjectScanner` class'ını implement et
- [ ] `scan_all_projects()` metodunu yaz
- [ ] `get_project_html()` metodunu yaz

### 4.3 DNA Extractor
- [ ] `maestro/context/dna_extractor.py` oluştur
- [ ] `DNAExtractor` class'ını implement et
- [ ] Renk paleti çıkarma
- [ ] Tipografi çıkarma
- [ ] Spacing pattern çıkarma

---

## 🔵 Faz 5: UI & Output (Öncelik: Orta)

### 5.1 Formatter
- [ ] `maestro/ui/formatter.py` oluştur
- [ ] Soru formatlama (emoji, box drawing)
- [ ] Seçenek listesi formatlama
- [ ] Progress bar oluşturma

### 5.2 Summary Generator
- [ ] `maestro/ui/summary.py` oluştur
- [ ] Final karar özeti oluşturma
- [ ] Parametre listesi formatlama
- [ ] Onay ekranı oluşturma

### 5.3 Templates
- [ ] `maestro/ui/templates.py` oluştur
- [ ] Greeting template
- [ ] Question templates
- [ ] Summary template
- [ ] Error templates

---

## 🟣 Faz 6: Entegrasyon (Öncelik: Yüksek)

### 6.1 MCP Bridge
- [ ] `maestro/integration/mcp_bridge.py` oluştur
- [ ] Tool registration helper
- [ ] Response formatter

### 6.2 Mode Executor
- [ ] `maestro/integration/mode_executor.py` oluştur
- [ ] `ModeExecutor` class'ını implement et
- [ ] Her mod için handler yaz

### 6.3 Server.py Güncellemeleri
- [ ] `design_wizard` tool ekle
- [ ] `wizard_answer` tool ekle
- [ ] `wizard_execute` tool ekle
- [ ] Import'ları düzenle

---

## ⚪ Faz 7: Test & Polish (Öncelik: Düşük)

### 7.1 Unit Tests
- [ ] Question bank tests
- [ ] Interview engine tests
- [ ] Decision tree tests
- [ ] Parameter builder tests

### 7.2 Integration Tests
- [ ] Full flow test (sıfırdan tasarım)
- [ ] Mevcut proje devam test
- [ ] Refine flow test
- [ ] Reference flow test

### 7.3 Documentation
- [ ] README.md for maestro/
- [ ] Soru akışı diyagramı
- [ ] API documentation

---

# 9. TEST SENARYOLARI

## Senaryo 1: Sıfırdan Landing Page
```
Input Sequence:
1. /design-gemini
2. "A" (Sıfırdan yeni)
3. "B" (Tam sayfa)
4. "A" (Landing Page)
5. "B" (B2B)
6. "D" (Teknoloji/SaaS)
7. "3" (Profesyonel formality)
8. "A" (Modern Minimal)
9. "D" (Kararı sana bırakıyorum - renk)
10. "A,G" (Profesyonel, Yenilikçi)
11. "C" (Placeholder kullan)
12. "A" (Varsayılanlar - teknik)
13. "A" (Türkçe)

Expected Output:
- Mode: design_page
- Theme: modern_minimal
- Page Type: landing
- Industry: tech
- Formality: professional
- Sections: [navbar, hero, features, testimonials, pricing, cta, footer]
- Language: tr
```

## Senaryo 2: Mevcut Projeye Devam
```
Input Sequence:
1. /design-gemini
2. "B" (Mevcut proje üzerinde devam)
3. "1" (burger_landing seçildi)
4. "A" (Yeni bölüm ekle)
5. "E" (Testimonials)
...

Expected Output:
- Mode: design_section
- Section Type: testimonials
- Previous HTML: [existing project HTML]
- Match Existing Style: true
```

## Senaryo 3: Referanstan Tasarım
```
Input Sequence:
1. /design-gemini
2. "C" (Referans görselden ilham al)
3. [Görsel yüklendi]
4. "B" (İlham al ama birebir kopyalama)
5. "A,C" (Renkleri ve layout'u koru)
...

Expected Output:
- Mode: design_from_reference
- Reference Image: [path]
- Adherence Level: inspired
- Elements to Keep: [colors, layout]
```

---

# 10. GELECEK GELİŞTİRMELER

## v1.1 - Akıllı Öğrenme
- [ ] Kullanıcı tercihlerini hatırlama
- [ ] Sık kullanılan kombinasyonları önerme
- [ ] A/B test sonuçlarından öğrenme

## v1.2 - Gelişmiş UI
- [ ] Görsel tema önizleme
- [ ] Renk paleti picker
- [ ] Section drag & drop sıralama

## v1.3 - Collaboration
- [ ] Takım şablonları
- [ ] Shared presets
- [ ] Design system import

## v2.0 - AI-Powered
- [ ] Doğal dil anlama (soru yerine serbest metin)
- [ ] Otomatik soru atlama (intent'ten çıkarım)
- [ ] Conversation memory

---

# 📎 EKLER

## Ek A: Soru Tipleri Referansı

| Tip | Açıklama | Örnek |
|-----|----------|-------|
| `single_choice` | Tek seçim | A, B, C, D |
| `multi_choice` | Çoklu seçim | A, C, D |
| `single_choice_with_other` | Tek seçim + özel | A veya "diğer: xyz" |
| `text_input` | Serbest metin | "Marka adım XYZ" |
| `slider` | Sayısal değer | 1-5 arası |
| `dynamic_choice` | Dinamik liste | Mevcut projeler listesi |
| `structured_input` | Form alanları | Başlık, alt başlık, CTA |
| `file_upload` | Dosya | Referans görsel |
| `multi_toggle` | On/Off seçenekler | Dark mode: ✓, Animations: ✗ |

## Ek B: Hata Kodları

| Kod | Açıklama | Çözüm |
|-----|----------|-------|
| `MAESTRO_001` | Session bulunamadı | Yeni session başlat |
| `MAESTRO_002` | Geçersiz cevap formatı | Doğru format göster |
| `MAESTRO_003` | Required soru atlandı | Soruya geri dön |
| `MAESTRO_004` | Mode execution failed | Fallback mode dene |
| `MAESTRO_005` | Context analysis failed | Manual input iste |

---

*Plan Sonu - Versiyon 1.0*
*Tahmini Geliştirme Süresi: 3-5 gün*
*Toplam Tahmini Kod Satırı: ~3000-4000*
