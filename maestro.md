# MAESTRO İyileştirmeleri: Design Brief Parser ve Akıllı Interview Sistemi

**Projenin özü**: MAESTRO'yu statik soru-cevap sisteminden, kullanıcının design brief'ini anlayan ve dinamik, bağlama-duyarlı sorular soran akıllı bir interview sistemine dönüştürmek. Bu dönüşüm **5 ana modül** ile gerçekleşecek: Brief Ingestion, Soul Extractor, Dynamic Question Generator, Interview Intelligence Layer ve MAESTRO Integration.

---

## Mimari Genel Bakış

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MAESTRO v2.0 ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  /design-gemini komutu                                                      │
│       ↓                                                                     │
│  ┌──────────────────┐    ┌───────────────────┐    ┌────────────────────┐   │
│  │ Brief Ingestion  │ ─→ │  Soul Extractor   │ ─→ │ Question Generator │   │
│  │ Module           │    │  Engine           │    │ (Dynamic)          │   │
│  └──────────────────┘    └───────────────────┘    └────────────────────┘   │
│       ↓                         ↓                         ↓                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    Interview Intelligence Layer                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ State       │  │ Confidence  │  │ Gap         │  │ Follow-up   │  │  │
│  │  │ Machine     │  │ Scorer      │  │ Detector    │  │ Generator   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│       ↓                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    Mevcut MAESTRO Entegrasyonu                        │  │
│  │  flow_controller.py ← adaptive_flow.py ← tree.py ← session_tracker   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## MODÜL 1: Design Brief Ingestion Module

### 1.1 Brief Parser Oluşturma

**Dosya**: `maestro/ingestion/brief_parser.py`

**Rationale**: Kullanıcının yapıştırdığı veya upload ettiği design brief dökümanını parse edip normalize etmek gerekiyor. Brief farklı formatlarda gelebilir (düz metin, markdown, PDF).

**TODO Items**:

```python
# TODO 1.1.1: BriefParser class oluştur
# Neden: Farklı input formatlarını tek bir standart formata dönüştürmek için
# Yaklaşım: Factory pattern ile format-specific parser'lar

class BriefParser:
    """Design brief dökümanlarını parse eden ana sınıf"""
    
    async def parse(self, input_text: str, format: str = "auto") -> ParsedBrief:
        """
        Args:
            input_text: Ham brief metni veya dosya path'i
            format: "auto", "markdown", "plain", "pdf"
        Returns:
            ParsedBrief: Normalize edilmiş brief objesi
        """
        pass

# TODO 1.1.2: ParsedBrief data model oluştur
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ParsedBrief(BaseModel):
    """Normalize edilmiş brief yapısı"""
    raw_text: str
    sections: Dict[str, str]  # {"proje_ozeti": "...", "hedef_kitle": "..."}
    detected_entities: List[str]
    word_count: int
    language: str = "tr"
    parse_confidence: float
```

**Örnek Prompt Pattern**:
```python
BRIEF_SECTION_DETECTION_PROMPT = """
Bu design brief metnini analiz et ve aşağıdaki bölümleri tespit et:
- Proje Özeti/Tanımı
- Hedef Kitle
- Marka/Şirket Bilgisi
- Hedefler ve Beklentiler
- Kısıtlamalar (bütçe, zaman, teknik)
- Stil/Mood Tercihleri
- Referanslar/İlham Kaynakları
- Rakipler
- Deliverables/Çıktılar

Brief Metni:
{brief_text}

JSON formatında yanıt ver:
{
    "proje_ozeti": "...",
    "hedef_kitle": "...",
    ...
}
"""
```

### 1.2 Brief Validator ve Enricher

**Dosya**: `maestro/ingestion/brief_validator.py`

**Rationale**: Parse edilen brief'in yeterli bilgi içerip içermediğini kontrol etmek ve eksik alanları tespit etmek gerekiyor.

**TODO Items**:

```python
# TODO 1.2.1: BriefValidator class
class BriefValidator:
    """Brief'in kalitesini ve tamlığını değerlendirir"""
    
    REQUIRED_SECTIONS = [
        "proje_ozeti",
        "hedef_kitle", 
        "hedefler"
    ]
    
    OPTIONAL_SECTIONS = [
        "stil_tercihleri",
        "referanslar",
        "kisitlamalar",
        "rakipler"
    ]
    
    def validate(self, brief: ParsedBrief) -> ValidationResult:
        """
        Returns:
            ValidationResult: {
                "is_valid": bool,
                "completeness_score": float,  # 0-1
                "missing_required": List[str],
                "missing_optional": List[str],
                "suggestions": List[str]
            }
        """
        pass

# TODO 1.2.2: BriefEnricher - eksik bölümleri Gemini ile çıkarma
class BriefEnricher:
    """Brief'ten implicit bilgileri çıkarır"""
    
    async def enrich(self, brief: ParsedBrief) -> EnrichedBrief:
        """
        Ham metinden çıkarılabilecek implicit bilgileri ekler:
        - Industry/sektör tahmini
        - Proje tipi tahmini (website, mobile app, dashboard)
        - Ton/mood inference
        """
        pass
```

---

## MODÜL 2: Soul Extractor Engine

### 2.1 Project Soul Data Model

**Dosya**: `maestro/soul/models.py`

**Rationale**: Projenin "ruhu"nu temsil eden kapsamlı bir veri yapısı gerekiyor. Bu yapı tüm downstream modüllerin (soru üretimi, confidence scoring) temelini oluşturacak.

**TODO Items**:

```python
# TODO 2.1.1: Aaker Brand Personality Framework implementasyonu
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class BrandPersonalityDimension(str, Enum):
    """Aaker'in 5 marka kişilik boyutu"""
    SINCERITY = "sincerity"      # Samimi, dürüst, neşeli
    EXCITEMENT = "excitement"    # Cesur, canlı, yaratıcı
    COMPETENCE = "competence"    # Güvenilir, zeki, başarılı
    SOPHISTICATION = "sophistication"  # Şık, çekici, prestijli
    RUGGEDNESS = "ruggedness"    # Dayanıklı, sağlam, maskülen

class BrandPersonality(BaseModel):
    """Marka kişilik skorları"""
    sincerity: float = Field(ge=0, le=1, description="Samimiyet skoru")
    excitement: float = Field(ge=0, le=1, description="Heyecan skoru")
    competence: float = Field(ge=0, le=1, description="Yetkinlik skoru")
    sophistication: float = Field(ge=0, le=1, description="Sofistike skoru")
    ruggedness: float = Field(ge=0, le=1, description="Sağlamlık skoru")
    dominant_trait: BrandPersonalityDimension
    secondary_trait: Optional[BrandPersonalityDimension]

# TODO 2.1.2: Hedef Kitle Modeli
class TargetAudience(BaseModel):
    """Hedef kitle profili"""
    demographics: List[str]  # ["25-40 yaş", "şehirli", "profesyonel"]
    psychographics: List[str]  # ["teknoloji meraklısı", "verimlilik odaklı"]
    pain_points: List[str]  # ["karmaşık arayüzler", "yavaş sistemler"]
    goals: List[str]  # ["hızlı işlem", "kolay raporlama"]
    tech_savviness: str  # "beginner", "intermediate", "advanced"

# TODO 2.1.3: Visual Language Modeli
class VisualLanguage(BaseModel):
    """Görsel dil tercihleri"""
    style_keywords: List[str]  # ["minimal", "modern", "corporate"]
    color_mood: str  # "warm", "cool", "neutral", "vibrant"
    color_associations: List[str]  # ["mavi - güven", "yeşil - büyüme"]
    typography_style: str  # "modern sans", "classic serif", "playful"
    imagery_style: List[str]  # ["abstract", "photographic", "illustrated"]
    layout_preferences: List[str]  # ["spacious", "dense", "card-based"]

# TODO 2.1.4: Emotional Framework Modeli
class EmotionalFramework(BaseModel):
    """Duygusal çerçeve"""
    primary_emotion: str  # "güven", "heyecan", "huzur"
    supporting_emotions: List[str]
    emotions_to_avoid: List[str]
    energy_level: str  # "high", "medium", "low"
    formality_level: str  # "formal", "casual", "professional"

# TODO 2.1.5: Ana ProjectSoul Modeli
class ProjectSoul(BaseModel):
    """Projenin ruhunu temsil eden ana model"""
    # Kimlik
    project_id: str
    project_name: str
    project_type: str  # "erp_dashboard", "mobile_app", "website"
    industry: str
    
    # Hedef Kitle
    target_audience: TargetAudience
    
    # Marka Kişiliği
    brand_personality: BrandPersonality
    
    # Görsel Dil
    visual_language: VisualLanguage
    
    # Duygusal Çerçeve
    emotional_framework: EmotionalFramework
    
    # Stratejik Elementler
    value_propositions: List[str]
    differentiators: List[str]
    competitors: List[str]
    inspirations: List[str]
    
    # Kısıtlamalar
    constraints: Dict[str, str]  # {"timeline": "3 ay", "budget": "orta"}
    deliverables: List[str]
    
    # Meta
    extraction_confidence: float
    extraction_timestamp: str
    raw_brief_text: str
```

### 2.2 Soul Extractor Implementation

**Dosya**: `maestro/soul/extractor.py`

**Rationale**: Brief'ten ProjectSoul çıkarmak için Gemini API kullanılacak. Chain-of-thought prompting ile daha doğru sonuçlar alınacak.

**TODO Items**:

```python
# TODO 2.2.1: SoulExtractor ana class
import google.generativeai as genai
from pydantic import ValidationError

class SoulExtractor:
    """Design brief'ten proje ruhunu çıkarır"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    async def extract(self, brief: ParsedBrief) -> ProjectSoul:
        """
        Chain-of-thought ile kapsamlı extraction
        """
        # Step 1: Temel bilgi extraction
        basic_info = await self._extract_basic_info(brief)
        
        # Step 2: Brand personality analysis
        personality = await self._analyze_brand_personality(brief)
        
        # Step 3: Visual language inference
        visual = await self._infer_visual_language(brief)
        
        # Step 4: Emotional framework detection
        emotional = await self._detect_emotional_framework(brief)
        
        # Step 5: Combine and validate
        return self._combine_extractions(
            basic_info, personality, visual, emotional, brief
        )

# TODO 2.2.2: Chain-of-Thought Extraction Prompts
SOUL_EXTRACTION_COT_PROMPT = """
Sen bir tasarım stratejisti olarak bu design brief'i analiz edeceksin.
Chain-of-thought yaklaşımı kullan.

## Design Brief:
{brief_text}

## Analiz Süreci:

### Adım 1: Temel Amaç Tespiti
Önce projenin temel amacını belirle:
- Ne problemi çözüyor?
- Asıl hedef ne?
- Bu bir ERP dashboard mı, website mi, mobil uygulama mı?

### Adım 2: Hedef Kitle Analizi
Kimin için tasarlanıyor:
- Demografik özellikler
- Psikografik özellikler (değerler, yaşam tarzı)
- Mevcut sıkıntılar
- Beklentiler

### Adım 3: Marka Kişiliği (Aaker Modeli)
5 boyutta 0-1 arası skorla:
- Sincerity (samimi, dürüst)
- Excitement (cesur, yaratıcı)
- Competence (güvenilir, profesyonel)
- Sophistication (şık, premium)
- Ruggedness (sağlam, dayanıklı)

### Adım 4: Görsel Dil Çıkarımı
Metinden görsel tercihleri çıkar:
- Stil anahtar kelimeleri
- Renk duygusu
- Tipografi stili
- Görsel tarzı

### Adım 5: Duygusal Çerçeve
Tasarımın uyandırması gereken duygular:
- Ana duygu
- Destekleyici duygular
- Kaçınılması gereken duygular

JSON formatında structured output ver.
"""

# TODO 2.2.3: ERP Dashboard için özelleştirilmiş extraction
ERP_SPECIFIC_EXTRACTION_PROMPT = """
Bu bir ERP Dashboard projesi için design brief.
ERP sistemlerine özel aşağıdaki faktörleri de çıkar:

1. Dashboard Kullanım Senaryoları:
   - Hangi metriklerin gösterilmesi gerekiyor?
   - Karar verme süreçleri için hangi veriler kritik?
   - Drill-down ihtiyaçları var mı?

2. Kullanıcı Rolleri:
   - C-level yöneticiler için mi?
   - Operasyonel kullanıcılar için mi?
   - Multi-role support gerekiyor mu?

3. Veri Yoğunluğu Tercihi:
   - Dense/data-heavy mi?
   - Clean/minimal mi?
   - Balance tercih mi?

4. İnteraktivite Seviyesi:
   - Sadece görüntüleme?
   - Filtreleme/sorting?
   - Deep analytics?

Brief:
{brief_text}
"""
```

### 2.3 Keyword Extractor

**Dosya**: `maestro/soul/keyword_extractor.py`

**Rationale**: LLM extraction'ı desteklemek için geleneksel NLP keyword extraction da kullanılmalı. Bu, daha robust ve çeşitli insight'lar sağlar.

**TODO Items**:

```python
# TODO 2.3.1: DesignKeywordExtractor
from keybert import KeyBERT
from typing import List, Tuple

class DesignKeywordExtractor:
    """Tasarım odaklı keyword extraction"""
    
    def __init__(self):
        self.model = KeyBERT(model='paraphrase-multilingual-MiniLM-L12-v2')
        
        # Tasarım domain'ine özel seed keywords
        self.design_seeds = [
            "minimal", "modern", "bold", "elegant", "corporate",
            "playful", "professional", "clean", "vibrant", "subtle"
        ]
    
    def extract_keywords(
        self, 
        text: str, 
        top_n: int = 15
    ) -> List[Tuple[str, float]]:
        """
        Returns: [("minimal tasarım", 0.85), ("kurumsal", 0.72), ...]
        """
        keywords = self.model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),
            stop_words='turkish',  # Türkçe stop words
            top_n=top_n,
            use_mmr=True,  # Çeşitlilik için
            diversity=0.7,
            seed_keywords=self.design_seeds
        )
        return keywords
    
    def categorize_keywords(
        self, 
        keywords: List[Tuple[str, float]]
    ) -> Dict[str, List[str]]:
        """
        Anahtar kelimeleri kategorilere ayırır:
        - style: görsel stil
        - mood: duygusal ton
        - audience: hedef kitle
        - feature: özellik/işlevsellik
        """
        pass

# TODO 2.3.2: Sentiment/Mood Analyzer
from nltk.sentiment import SentimentIntensityAnalyzer

class MoodAnalyzer:
    """Brief'ten mood/vibe çıkarır"""
    
    def analyze_mood(self, text: str) -> Dict:
        """
        Returns: {
            "overall_sentiment": "positive",
            "energy_level": "medium",
            "formality": "professional",
            "warmth": 0.7
        }
        """
        pass
```

---

## MODÜL 3: Dynamic Question Generator

### 3.1 Context-Aware Question Engine

**Dosya**: `maestro/questions/dynamic_generator.py`

**Rationale**: Mevcut statik soru bankası yerine, ProjectSoul'a göre dinamik soru üreten bir engine gerekiyor. Sorular context-aware olmalı ve brief'te eksik olan bilgileri hedeflemeli.

**TODO Items**:

```python
# TODO 3.1.1: DynamicQuestionGenerator class
from typing import List, Optional
from maestro.soul.models import ProjectSoul

class DynamicQuestionGenerator:
    """ProjectSoul'a göre dinamik soru üretir"""
    
    def __init__(self, gemini_api_key: str):
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.question_templates = QuestionTemplateBank()
    
    async def generate_questions(
        self,
        soul: ProjectSoul,
        gaps: List[str],
        max_questions: int = 5
    ) -> List[DynamicQuestion]:
        """
        Args:
            soul: Çıkarılmış proje ruhu
            gaps: Eksik bilgi alanları
            max_questions: Üretilecek max soru sayısı
        
        Returns:
            List[DynamicQuestion]: Önceliklendirilmiş soru listesi
        """
        # Gap'lere göre soru üret
        questions = []
        for gap in gaps[:max_questions]:
            q = await self._generate_question_for_gap(soul, gap)
            questions.append(q)
        
        return self._prioritize_questions(questions)

# TODO 3.1.2: DynamicQuestion model
class DynamicQuestion(BaseModel):
    """Dinamik üretilmiş soru"""
    id: str
    question_text: str  # "ERP dashboard'unuzda en kritik KPI'lar neler?"
    question_type: str  # "open", "choice", "scale"
    context_reason: str  # Bu sorunun neden sorulduğu
    expected_insight: str  # Cevaptan ne çıkarılacak
    priority: int  # 1-5
    follow_ups: List[str]  # Olası takip soruları
    category: str  # "visual", "functional", "emotional", "strategic"
    
    # ERP Dashboard için özel
    erp_relevance: Optional[str]  # Bu sorunun ERP context'inde önemi

# TODO 3.1.3: Question Template Bank (Türkçe)
class QuestionTemplateBank:
    """Soru şablonları - dinamik olarak doldurulacak"""
    
    TEMPLATES = {
        "visual_style": [
            "{{project_type}} için görsel olarak hangi tarzı tercih ediyorsunuz? (örn: minimal, bold, corporate)",
            "{{competitor}} gibi rakiplerin tasarımlarında beğendiğiniz veya beğenmediğiniz ne var?",
            "Kullanıcılarınız {{target_audience}} olduğuna göre, onlar için en önemli görsel element ne olmalı?"
        ],
        "user_flow": [
            "{{target_audience}} kullanıcılarınız sisteme girdiğinde ilk ne görmeli?",
            "En sık kullanılan 3 aksiyon/işlem ne olacak?",
            "Kullanıcıların karar vermesi için hangi verileri tek bakışta görmesi gerekiyor?"
        ],
        "emotional": [
            "Kullanıcılar {{project_name}} kullandığında kendilerini nasıl hissetmeli?",
            "{{brand_personality}} kişiliğini yansıtmak için ne tür bir deneyim oluşturmalıyız?",
            "Kesinlikle vermemesi gereken bir his var mı?"
        ],
        "erp_specific": [
            "Dashboard'da kaç farklı kullanıcı rolü olacak?",
            "Real-time data mı yoksa periodic refresh mi tercih ediyorsunuz?",
            "Mobile erişim ne kadar kritik?",
            "En önemli 5 metrik/KPI ne olacak?",
            "Drill-down ve detay görüntüleme ihtiyacı var mı?"
        ]
    }
```

### 3.2 Gap Detection System

**Dosya**: `maestro/questions/gap_detector.py`

**Rationale**: Soul extraction sonrası hangi bilgilerin eksik veya düşük güvenilirlikli olduğunu tespit etmek gerekiyor. Bu gap'ler soru üretimini yönlendirecek.

**TODO Items**:

```python
# TODO 3.2.1: GapDetector class
class GapDetector:
    """ProjectSoul'daki eksik veya belirsiz alanları tespit eder"""
    
    # ERP Dashboard için kritik alanlar
    CRITICAL_FIELDS = [
        "target_audience.demographics",
        "target_audience.pain_points",
        "visual_language.style_keywords",
        "emotional_framework.primary_emotion",
        "deliverables"
    ]
    
    # Opsiyonel ama değerli alanlar
    VALUABLE_FIELDS = [
        "competitors",
        "inspirations",
        "constraints.timeline",
        "visual_language.color_mood"
    ]
    
    def detect_gaps(
        self, 
        soul: ProjectSoul,
        confidence_scores: Dict[str, float]
    ) -> GapAnalysis:
        """
        Returns:
            GapAnalysis: {
                "critical_missing": ["hedef_kitle.pain_points"],
                "low_confidence": [("visual_style", 0.4)],
                "incomplete": ["deliverables"],
                "priority_queue": [...]
            }
        """
        pass
    
    def prioritize_gaps(
        self, 
        gaps: GapAnalysis,
        interview_context: str
    ) -> List[str]:
        """
        Gap'leri soru sorma önceliğine göre sıralar.
        ERP Dashboard context'ini dikkate alır.
        """
        pass

# TODO 3.2.2: GapAnalysis model
class GapAnalysis(BaseModel):
    critical_missing: List[str]
    low_confidence: List[Tuple[str, float]]
    incomplete: List[str]
    priority_queue: List[str]
    completeness_score: float
    ready_for_design: bool
```

### 3.3 Question Personalization

**Dosya**: `maestro/questions/personalizer.py`

**Rationale**: Aynı gap için farklı projelere farklı sorular sorulmalı. Örneğin "visual style" gap'i için ERP dashboard'a farklı, e-commerce'e farklı soru sorulmalı.

**TODO Items**:

```python
# TODO 3.3.1: QuestionPersonalizer
class QuestionPersonalizer:
    """Soruları proje context'ine göre kişiselleştirir"""
    
    async def personalize(
        self,
        template_question: str,
        soul: ProjectSoul,
        previous_answers: List[str]
    ) -> str:
        """
        Template: "Görsel tarz tercihiniz nedir?"
        Personalized: "ERP Dashboard'unuz için şu ana kadar bahsettiğiniz 
        'minimal ve profesyonel' yaklaşıma ek olarak, data-heavy ekranlar 
        için özel bir görsel tercih var mı?"
        """
        prompt = f"""
        Aşağıdaki soru şablonunu bu proje context'ine göre kişiselleştir:
        
        Şablon Soru: {template_question}
        
        Proje Bilgileri:
        - Tip: {soul.project_type}
        - Sektör: {soul.industry}
        - Hedef Kitle: {soul.target_audience.demographics}
        - Marka Kişiliği: {soul.brand_personality.dominant_trait}
        
        Önceki Cevaplar:
        {previous_answers}
        
        Kişiselleştirilmiş soruyu Türkçe olarak yaz.
        Samimi ama profesyonel bir ton kullan.
        Soru tek cümle olsun, çok uzun olmasın.
        """
        
        response = await self.model.generate_content_async(prompt)
        return response.text
```

---

## MODÜL 4: Interview Intelligence Layer

### 4.1 Interview State Machine

**Dosya**: `maestro/intelligence/state_machine.py`

**Rationale**: Interview'ın hangi aşamada olduğunu takip etmek ve state transition'ları yönetmek gerekiyor. Bu, coherent bir interview deneyimi sağlar.

**TODO Items**:

```python
# TODO 4.1.1: InterviewStateMachine with transitions library
from transitions.extensions import HierarchicalAsyncMachine
from enum import Enum, auto

class InterviewPhase(Enum):
    """Interview aşamaları"""
    BRIEF_INGESTION = auto()     # Brief alımı
    SOUL_EXTRACTION = auto()      # Ruh çıkarımı
    CONTEXT_GATHERING = auto()    # Bağlam toplama
    DEEP_DIVE = auto()            # Derinlemesine sorular
    VISUAL_EXPLORATION = auto()   # Görsel tercihler
    VALIDATION = auto()           # Doğrulama
    SYNTHESIS = auto()            # Sentez
    COMPLETE = auto()             # Tamamlandı

class InterviewStateMachine:
    """Interview akışını yöneten state machine"""
    
    states = [
        {'name': 'brief_ingestion', 'on_enter': 'on_enter_brief'},
        {'name': 'soul_extraction', 'on_enter': 'on_enter_extraction'},
        {'name': 'context_gathering', 
         'children': ['project_context', 'user_context', 'business_context']},
        {'name': 'deep_dive',
         'children': ['functional_dive', 'visual_dive', 'emotional_dive']},
        {'name': 'visual_exploration'},
        {'name': 'validation', 'on_enter': 'validate_gathered_info'},
        {'name': 'synthesis', 'on_enter': 'generate_design_spec'},
        {'name': 'complete', 'final': True}
    ]
    
    transitions = [
        # Brief -> Extraction
        {'trigger': 'brief_received', 
         'source': 'brief_ingestion', 
         'dest': 'soul_extraction'},
        
        # Extraction -> Context (otomatik)
        {'trigger': 'extraction_complete', 
         'source': 'soul_extraction', 
         'dest': 'context_gathering',
         'after': 'generate_initial_questions'},
        
        # Context -> Deep Dive (yeterli context varsa)
        {'trigger': 'context_sufficient', 
         'source': 'context_gathering', 
         'dest': 'deep_dive',
         'conditions': 'has_sufficient_context'},
        
        # Deep Dive -> Visual
        {'trigger': 'dive_complete',
         'source': 'deep_dive',
         'dest': 'visual_exploration'},
        
        # Visual -> Validation
        {'trigger': 'visual_complete',
         'source': 'visual_exploration',
         'dest': 'validation'},
        
        # Validation geri dönüş
        {'trigger': 'needs_clarification',
         'source': 'validation',
         'dest': 'deep_dive'},
        
        # Validation -> Synthesis
        {'trigger': 'validation_passed',
         'source': 'validation',
         'dest': 'synthesis'},
        
        # Synthesis -> Complete
        {'trigger': 'synthesis_done',
         'source': 'synthesis',
         'dest': 'complete'}
    ]
    
    def __init__(self):
        self.gathered_insights = []
        self.soul: Optional[ProjectSoul] = None
        self.confidence_scores = {}
        
        self.machine = HierarchicalAsyncMachine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial='brief_ingestion',
            queued=True
        )
    
    def has_sufficient_context(self) -> bool:
        """Context gathering için minimum requirements"""
        return self.get_completeness_score() >= 0.6
    
    def get_completeness_score(self) -> float:
        """Toplanan bilginin tamlık skoru"""
        if not self.soul:
            return 0.0
        # Implement completeness logic
        pass
```

### 4.2 Confidence Scorer

**Dosya**: `maestro/intelligence/confidence_scorer.py`

**Rationale**: Her çıkarılan insight için güvenilirlik skoru hesaplamak gerekiyor. Düşük güvenilirlikli alanlar için ek sorular sorulacak.

**TODO Items**:

```python
# TODO 4.2.1: InsightConfidenceScorer
class InsightConfidenceScorer:
    """Çıkarılan insight'ların güvenilirliğini skorlar"""
    
    async def score_extraction(
        self,
        original_text: str,
        extracted_value: str,
        field_name: str
    ) -> ConfidenceScore:
        """
        Multi-signal confidence scoring:
        1. P(True) - LLM self-assessment
        2. Specificity - ne kadar spesifik?
        3. Evidence - destekleyen kanıt var mı?
        4. Consistency - önceki bilgilerle tutarlı mı?
        """
        scores = {
            'p_true': await self._assess_p_true(original_text, extracted_value),
            'specificity': self._calculate_specificity(extracted_value),
            'evidence': self._check_evidence(original_text, extracted_value),
            'consistency': await self._check_consistency(extracted_value, field_name)
        }
        
        weighted_score = (
            scores['p_true'] * 0.3 +
            scores['specificity'] * 0.25 +
            scores['evidence'] * 0.25 +
            scores['consistency'] * 0.2
        )
        
        return ConfidenceScore(
            overall=weighted_score,
            components=scores,
            needs_clarification=weighted_score < 0.6,
            suggested_followup=self._generate_followup_if_needed(
                field_name, weighted_score
            )
        )

# TODO 4.2.2: ConfidenceScore model
class ConfidenceScore(BaseModel):
    overall: float
    components: Dict[str, float]
    needs_clarification: bool
    suggested_followup: Optional[str]
```

### 4.3 Follow-up Question Generator

**Dosya**: `maestro/intelligence/followup_generator.py`

**Rationale**: Kullanıcı cevapları belirsiz veya eksik olduğunda akıllı takip soruları üretmek gerekiyor.

**TODO Items**:

```python
# TODO 4.3.1: FollowUpGenerator
class FollowUpGenerator:
    """Akıllı takip soruları üretir"""
    
    AMBIGUITY_STRATEGIES = {
        'too_vague': "Biraz daha detaylandırabilir misiniz? Örneğin {examples}",
        'missing_detail': "Çok güzel! Bir de {missing_aspect} konusunda ne düşünüyorsunuz?",
        'contradictory': "Daha önce {prev} demiştiniz, şimdi {current} dediniz. Hangisi daha doğru?",
        'off_topic': "İlginç bir nokta! Ana konumuza dönersek, {question}",
        'uncertain': "Henüz net değilse sorun yok. İlk düşünceleriniz neler?"
    }
    
    async def generate_followup(
        self,
        original_question: str,
        user_response: str,
        ambiguity_type: str,
        context: Dict
    ) -> str:
        """
        Belirsiz cevaba uygun takip sorusu üretir.
        Doğal ve sohbet havasında olmalı.
        """
        prompt = f"""
        Kullanıcıya bir tasarım sorusu sordun:
        "{original_question}"
        
        Kullanıcı şöyle cevap verdi:
        "{user_response}"
        
        Bu cevap {ambiguity_type} nedeniyle yeterli değil.
        
        Bağlam:
        - Proje: {context.get('project_type')}
        - Şimdiye kadar öğrenilen: {context.get('gathered_info')}
        
        Doğal, samimi ama profesyonel bir takip sorusu yaz.
        Kullanıcıyı eleştirme, destekleyici ol.
        Mümkünse somut seçenekler sun.
        
        Takip sorusu:
        """
        response = await self.model.generate_content_async(prompt)
        return response.text
```

### 4.4 Answer Quality Assessor

**Dosya**: `maestro/intelligence/answer_assessor.py`

**Rationale**: Kullanıcı cevaplarının kalitesini değerlendirmek ve gerekirse takip sorusu tetiklemek için.

**TODO Items**:

```python
# TODO 4.4.1: AnswerQualityAssessor
class AnswerQualityAssessor:
    """Kullanıcı cevaplarının kalitesini değerlendirir"""
    
    async def assess(
        self,
        question: DynamicQuestion,
        answer: str,
        context: InterviewContext
    ) -> AnswerAssessment:
        """
        Returns:
            AnswerAssessment: {
                "quality_score": 0.8,
                "completeness": "partial",
                "ambiguity_type": None | "too_vague" | "off_topic" | ...,
                "extracted_insights": [...],
                "needs_followup": False,
                "suggested_followup": None
            }
        """
        pass

# TODO 4.4.2: AnswerAssessment model
class AnswerAssessment(BaseModel):
    quality_score: float
    completeness: str  # "complete", "partial", "minimal"
    ambiguity_type: Optional[str]
    extracted_insights: List[Dict]
    needs_followup: bool
    suggested_followup: Optional[str]
```

---

## MODÜL 5: MAESTRO Entegrasyonu

### 5.1 Flow Controller Güncellemesi

**Dosya**: `maestro/interview/flow_controller.py` (güncelleme)

**Rationale**: Mevcut flow_controller'ı yeni intelligent system ile entegre etmek.

**TODO Items**:

```python
# TODO 5.1.1: FlowController güncelleme
# Mevcut: Statik soru sırası
# Yeni: Dinamik, soul-aware akış

class FlowController:
    """Güncellenmiş akış kontrolcüsü"""
    
    def __init__(self):
        # Yeni modüller
        self.brief_parser = BriefParser()
        self.soul_extractor = SoulExtractor(api_key=GEMINI_API_KEY)
        self.question_generator = DynamicQuestionGenerator(api_key=GEMINI_API_KEY)
        self.state_machine = InterviewStateMachine()
        self.confidence_scorer = InsightConfidenceScorer()
        
        # Mevcut uyumluluk
        self.legacy_question_bank = QuestionBank()  # Fallback için
    
    async def start_interview(self, brief_text: str) -> InterviewSession:
        """Yeni interview başlatma akışı"""
        # 1. Brief parse et
        parsed = await self.brief_parser.parse(brief_text)
        await self.state_machine.brief_received()
        
        # 2. Soul çıkar
        soul = await self.soul_extractor.extract(parsed)
        self.state_machine.soul = soul
        await self.state_machine.extraction_complete()
        
        # 3. Gap'leri tespit et
        gaps = GapDetector().detect_gaps(soul, {})
        
        # 4. İlk soruları üret
        questions = await self.question_generator.generate_questions(
            soul, gaps.priority_queue
        )
        
        return InterviewSession(
            soul=soul,
            current_questions=questions,
            state=self.state_machine.state
        )
    
    async def process_answer(
        self,
        session: InterviewSession,
        answer: str
    ) -> NextAction:
        """Cevap işleme ve sonraki adım"""
        # 1. Cevap kalitesini değerlendir
        assessment = await AnswerQualityAssessor().assess(
            session.current_question,
            answer,
            session.context
        )
        
        # 2. Insight'ları kaydet
        for insight in assessment.extracted_insights:
            confidence = await self.confidence_scorer.score_extraction(
                answer, insight['value'], insight['field']
            )
            session.add_insight(insight, confidence)
        
        # 3. Takip sorusu gerekli mi?
        if assessment.needs_followup:
            followup = await FollowUpGenerator().generate_followup(
                session.current_question.question_text,
                answer,
                assessment.ambiguity_type,
                session.context
            )
            return NextAction(type="followup", question=followup)
        
        # 4. Sonraki soruyu belirle
        return await self._determine_next_question(session)
```

### 5.2 Adaptive Flow Güncellemesi

**Dosya**: `maestro/intelligence/adaptive_flow.py` (güncelleme)

**Rationale**: Mevcut keyword-based skip logic'i soul-aware logic ile değiştirmek.

**TODO Items**:

```python
# TODO 5.2.1: SoulAwareAdaptiveFlow
class SoulAwareAdaptiveFlow:
    """Soul-based adaptive question flow"""
    
    def should_skip_question(
        self,
        question: DynamicQuestion,
        soul: ProjectSoul,
        gathered_insights: List[Dict]
    ) -> Tuple[bool, str]:
        """
        Soru atlanmalı mı?
        
        Returns:
            (should_skip, reason)
        """
        # Soul'dan zaten bilinen bilgi
        if self._already_known_from_soul(question, soul):
            return True, "brief'ten zaten çıkarıldı"
        
        # Önceki cevaplardan çıkarılabilir
        if self._inferable_from_answers(question, gathered_insights):
            return True, "önceki cevaplardan çıkarılabilir"
        
        # Irrelevant soru (örn: mobile soru web projesinde)
        if not self._is_relevant(question, soul):
            return True, "proje tipi için geçerli değil"
        
        return False, ""
    
    def reorder_questions(
        self,
        questions: List[DynamicQuestion],
        soul: ProjectSoul,
        current_context: Dict
    ) -> List[DynamicQuestion]:
        """
        Soruları bağlama göre yeniden sıralar.
        Information gain ve flow smoothness'ı optimize eder.
        """
        pass
```

### 5.3 Session Tracker Güncellemesi

**Dosya**: `maestro/analytics/session_tracker.py` (güncelleme)

**Rationale**: Yeni metrikleri track etmek için session tracker'ı güncellemek.

**TODO Items**:

```python
# TODO 5.3.1: Yeni metrikler ekleme
class EnhancedSessionTracker:
    """Geliştirilmiş session tracking"""
    
    def track_session(self, session: InterviewSession):
        metrics = {
            # Mevcut metrikler
            "session_duration": session.duration,
            "questions_asked": session.question_count,
            
            # Yeni metrikler
            "brief_quality_score": session.brief_quality,
            "soul_extraction_confidence": session.soul.extraction_confidence,
            "gap_coverage": session.gap_coverage,
            "followup_rate": session.followup_count / session.question_count,
            "user_satisfaction_proxy": self._calculate_satisfaction_proxy(session),
            
            # Phase metrics
            "phase_durations": {
                phase: duration 
                for phase, duration in session.phase_times.items()
            },
            
            # Question effectiveness
            "question_effectiveness": {
                q.id: q.insight_yield 
                for q in session.questions
            }
        }
        
        self._persist_metrics(metrics)
```

---

## MODÜL 6: Prompt Library

### 6.1 Türkçe Prompt Collection

**Dosya**: `maestro/prompts/turkish_prompts.py`

**Rationale**: Tüm promptlar Türkçe ve domain-specific olmalı.

**TODO Items**:

```python
# TODO 6.1.1: System Prompts
MAESTRO_SYSTEM_PROMPT_TR = """
Sen MAESTRO, profesyonel bir tasarım araştırma asistanısın.
Görevin: Kullanıcının design brief'ini anlayarak projenin "ruhunu" çıkarmak ve 
akıllı, bağlama uygun sorular sormak.

## Kişiliğin:
- Profesyonel ama samimi
- Sabırlı ve dikkatli dinleyen
- Tasarım ve UX konusunda uzman
- Türkçeyi akıcı kullanan

## İletişim Kuralların:
1. Her seferinde TEK soru sor
2. Cevapları önce kabul et, sonra soru sor
3. Önceki cevapları referans göster
4. Belirsiz cevaplara nazikçe açıklama iste
5. Jargon kullanma, anlaşılır ol

## Özel Uzmanlık Alanların:
- ERP Dashboard tasarımı
- Kurumsal yazılım UX'i
- Data visualization
- Enterprise-grade arayüzler
"""

# TODO 6.1.2: Extraction Prompts
SOUL_EXTRACTION_PROMPT_TR = """
Bu design brief'i analiz et ve aşağıdaki bilgileri çıkar:

## Brief:
{brief_text}

## Çıkarılacak Bilgiler:

### 1. Temel Bilgiler
- Proje adı
- Proje tipi (ERP Dashboard, Website, Mobile App, vb.)
- Sektör

### 2. Hedef Kitle
- Demografik özellikler (yaş, meslek, konum)
- Teknik yetkinlik seviyesi
- Ana ihtiyaçlar ve beklentiler
- Mevcut sıkıntılar (pain points)

### 3. Marka Kişiliği (0-1 arası skorla)
- Samimiyet (sincerity)
- Heyecan (excitement)  
- Yetkinlik (competence)
- Sofistike (sophistication)
- Sağlamlık (ruggedness)

### 4. Görsel Dil
- Stil anahtar kelimeleri
- Renk duygusu (sıcak/soğuk/nötr)
- Tipografi tercihi
- Layout yaklaşımı

### 5. Duygusal Çerçeve
- Ana duygu
- Destekleyici duygular
- Kaçınılması gereken duygular

### 6. Stratejik Elementler
- Değer önerileri
- Farklılaştırıcılar
- Rakipler
- İlham kaynakları

JSON formatında yanıt ver. Eksik bilgiler için null kullan.
"""

# TODO 6.1.3: Question Generation Prompts
DYNAMIC_QUESTION_PROMPT_TR = """
Aşağıdaki proje bağlamına göre bir tasarım sorusu üret:

## Proje Bilgileri:
- Tip: {project_type}
- Sektör: {industry}
- Hedef Kitle: {target_audience}
- Marka Kişiliği: {brand_personality}

## Eksik Bilgi Alanı:
{gap_description}

## Önceki Sohbet:
{conversation_history}

## Soru Üretim Kuralları:
1. Tek, net bir soru sor
2. Proje bağlamına özel ol
3. Önceki cevapları referans göster
4. Somut seçenekler sun (mümkünse)
5. Samimi ama profesyonel ol
6. 20 kelimeyi geçme

Türkçe soru:
"""
```

---

## Dosya Yapısı Özeti

```
maestro/
├── ingestion/
│   ├── __init__.py
│   ├── brief_parser.py         # TODO 1.1
│   ├── brief_validator.py      # TODO 1.2
│   └── models.py               # ParsedBrief, ValidationResult
│
├── soul/
│   ├── __init__.py
│   ├── models.py               # TODO 2.1 - ProjectSoul, BrandPersonality
│   ├── extractor.py            # TODO 2.2 - SoulExtractor
│   └── keyword_extractor.py    # TODO 2.3 - KeywordExtractor
│
├── questions/
│   ├── __init__.py
│   ├── bank.py                 # MEVCUT - statik sorular (korunacak)
│   ├── dynamic_generator.py    # TODO 3.1 - DynamicQuestionGenerator
│   ├── gap_detector.py         # TODO 3.2 - GapDetector
│   └── personalizer.py         # TODO 3.3 - QuestionPersonalizer
│
├── intelligence/
│   ├── __init__.py
│   ├── adaptive_flow.py        # MEVCUT -> TODO 5.2 güncelleme
│   ├── state_machine.py        # TODO 4.1 - InterviewStateMachine
│   ├── confidence_scorer.py    # TODO 4.2 - InsightConfidenceScorer
│   ├── followup_generator.py   # TODO 4.3 - FollowUpGenerator
│   └── answer_assessor.py      # TODO 4.4 - AnswerQualityAssessor
│
├── interview/
│   ├── __init__.py
│   └── flow_controller.py      # MEVCUT -> TODO 5.1 güncelleme
│
├── decision/
│   └── tree.py                 # MEVCUT - mod seçimi (korunacak)
│
├── analytics/
│   └── session_tracker.py      # MEVCUT -> TODO 5.3 güncelleme
│
├── prompts/
│   ├── __init__.py
│   └── turkish_prompts.py      # TODO 6.1 - Tüm Türkçe promptlar
│
└── utils/
    ├── __init__.py
    ├── gemini_client.py        # Async Gemini wrapper
    └── error_handler.py        # Resilience patterns
```

---

## Implementasyon Sırası (Önerilen)

### Faz 1: Foundation (Hafta 1-2)
1. `soul/models.py` - Data modelleri
2. `prompts/turkish_prompts.py` - Prompt library
3. `utils/gemini_client.py` - Async Gemini client

### Faz 2: Core Extraction (Hafta 3-4)
4. `ingestion/brief_parser.py` - Brief parsing
5. `soul/extractor.py` - Soul extraction
6. `soul/keyword_extractor.py` - NLP support

### Faz 3: Intelligence Layer (Hafta 5-6)
7. `intelligence/state_machine.py` - State management
8. `intelligence/confidence_scorer.py` - Confidence scoring
9. `questions/gap_detector.py` - Gap detection

### Faz 4: Dynamic Questions (Hafta 7-8)
10. `questions/dynamic_generator.py` - Question generation
11. `questions/personalizer.py` - Personalization
12. `intelligence/followup_generator.py` - Follow-ups

### Faz 5: Integration (Hafta 9-10)
13. `interview/flow_controller.py` - Updated controller
14. `intelligence/adaptive_flow.py` - Soul-aware flow
15. `analytics/session_tracker.py` - Enhanced metrics

---

## Kritik Başarı Faktörleri

**Doğru brief parsing** olmadan soul extraction anlamsız olur. Parser'ın farklı brief formatlarını handle edebilmesi kritik.

**Confidence scoring** interview kalitesini belirler. Düşük güvenilirlikli extraction'larda mutlaka follow-up sorulmalı.

**State machine** coherent interview deneyimi için şart. Kullanıcı hangi aşamada olduğunu bilmeli.

**Türkçe prompt kalitesi** doğrudan output kalitesini etkiler. Promptlar iteratif olarak optimize edilmeli.

**ERP Dashboard domain bilgisi** sorulara embedded olmalı. Generic sorular yerine domain-specific sorular sorulmalı.

Bu implementasyon planı, MAESTRO'yu basit bir soru-cevap sisteminden, kullanıcının design intent'ini gerçekten anlayan ve akıllıca sorgulayan bir sistem seviyesine çıkaracak.