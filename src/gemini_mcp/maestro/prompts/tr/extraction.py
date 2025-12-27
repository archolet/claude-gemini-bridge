"""
MAESTRO Turkish Extraction Prompts - Phase 4

Prompts for Gemini API to extract ProjectSoul from design briefs.
These prompts guide the AI in understanding and analyzing design briefs.
"""

from typing import Dict, Optional


# =============================================================================
# SOUL EXTRACTION PROMPT
# =============================================================================

SOUL_EXTRACTION_PROMPT = """Sen profesyonel bir marka ve tasarım stratejistisin.
Aşağıdaki design brief'i analiz ederek projenin "ruhunu" (ProjectSoul) çıkar.

## Brief:
{brief}

## Çıkarılacak Bilgiler:

### 1. Proje Temel Bilgileri
- Proje adı
- Slogan/tagline (varsa)
- Proje türü (landing page, dashboard, e-commerce, vb.)

### 2. Marka Kişiliği (Aaker Framework - 5 Boyut)
Her boyut için 0-1 arası bir değer belirle:
- Sincerity (Samimiyet): Dürüst, samimi, gerçek
- Excitement (Heyecan): Cesur, enerjik, hayal gücü yüksek
- Competence (Yetkinlik): Güvenilir, başarılı, zeki
- Sophistication (Sofistike): Üst sınıf, çekici
- Ruggedness (Sağlamlık): Dayanıklı, güçlü, dış mekan

### 3. Hedef Kitle
- Yaş aralığı
- Teknoloji yetkinliği
- Sektör/alan
- Beklentiler ve ihtiyaçlar

### 4. Görsel Dil
- Tema önerisi (modern-minimal, brutalist, glassmorphism, vb.)
- Renk paleti önerisi
- Tipografi stili
- İçerik yoğunluğu

### 5. Duygusal Çerçeve
- Birincil duygu (ne hissetmeli?)
- İkincil duygu
- Kaçınılacak duygular

### 6. Güven Skorları
Her alan için 0-1 arası güven skoru:
- brand_confidence: Marka bilgilerinin netliği
- audience_confidence: Hedef kitle bilgilerinin netliği
- visual_confidence: Görsel tercihlerin netliği
- emotion_confidence: Duygusal çerçevenin netliği
- overall_confidence: Genel güven skoru

### 7. Tespit Edilen Eksikler (Gaps)
Brief'te eksik veya belirsiz olan alanları listele:
- Alan adı
- Önem seviyesi (critical, important, nice_to_have)
- Önerilen soru

## Yanıt Formatı:
JSON formatında yanıt ver. Türkçe değerler kullan.

```json
{{
  "project_name": "...",
  "tagline": "...",
  "project_type": "...",
  "brand_personality": {{
    "sincerity": 0.0,
    "excitement": 0.0,
    "competence": 0.0,
    "sophistication": 0.0,
    "ruggedness": 0.0,
    "dominant_trait": "...",
    "archetype": "..."
  }},
  "target_audience": {{
    "age_range": "...",
    "tech_level": "...",
    "industry": "...",
    "needs": ["..."]
  }},
  "visual_language": {{
    "theme": "...",
    "colors": {{
      "primary": "#...",
      "secondary": "#...",
      "accent": "#..."
    }},
    "typography": "...",
    "density": "..."
  }},
  "emotional_framework": {{
    "primary_emotion": "...",
    "secondary_emotion": "...",
    "avoid_emotions": ["..."]
  }},
  "confidence_scores": {{
    "brand": 0.0,
    "audience": 0.0,
    "visual": 0.0,
    "emotion": 0.0,
    "overall": 0.0
  }},
  "gaps": [
    {{
      "field": "...",
      "priority": "critical|important|nice_to_have",
      "suggested_question": "..."
    }}
  ]
}}
```
"""


# =============================================================================
# GAP DETECTION PROMPT
# =============================================================================

GAP_DETECTION_PROMPT = """Sen profesyonel bir UX araştırmacısısın.
Aşağıdaki ProjectSoul verisini analiz ederek eksik veya yetersiz bilgileri tespit et.

## Mevcut ProjectSoul:
{soul_json}

## Analiz Kriterleri:

### 1. Kritik Eksikler (Tasarımı engelleyen)
- Proje adı veya türü belirsiz mi?
- Hedef kitle tanımsız mı?
- Marka kişiliği belirsiz mi?

### 2. Önemli Eksikler (Kaliteyi etkileyen)
- Renk paleti belirlenmemiş mi?
- Tipografi tercihi yok mu?
- Animasyon tercihi belirsiz mi?

### 3. İyileştirme Fırsatları
- Daha detaylı hedef kitle analizi gerekiyor mu?
- Rakip analizi eksik mi?
- Duygusal çerçeve netleştirilmeli mi?

## Yanıt Formatı:
Her eksik için sormamız gereken en etkili soruyu öner.

```json
{{
  "gaps": [
    {{
      "field": "...",
      "current_value": "...",
      "priority": "critical|important|nice_to_have",
      "reason": "Neden önemli?",
      "suggested_question": {{
        "text": "...",
        "type": "single_choice|multi_choice|text",
        "options": ["..."]  // eğer choice ise
      }}
    }}
  ],
  "summary": {{
    "critical_count": 0,
    "important_count": 0,
    "total_gaps": 0,
    "recommendation": "..."
  }}
}}
```
"""


# =============================================================================
# BRIEF ANALYSIS PROMPT
# =============================================================================

BRIEF_ANALYSIS_PROMPT = """Sen profesyonel bir tasarım danışmanısın.
Verilen brief'i analiz ederek yapısal bir özet çıkar.

## Brief:
{brief}

## Analiz:

### 1. Brief Kalitesi
- Uzunluk yeterliliği (kısa/orta/detaylı)
- Netlik seviyesi (belirsiz/orta/net)
- Teknik detay seviyesi (düşük/orta/yüksek)

### 2. Anahtar Bilgiler
- Doğrudan belirtilen bilgiler
- İma edilen bilgiler
- Varsayılan bilgiler

### 3. Belirsizlikler
- Çelişkili ifadeler
- Eksik bağlam
- Açıklama gerektiren noktalar

### 4. Öneriler
- Hangi sorular sorulmalı?
- Hangi varsayımlar yapılabilir?
- Hangi alanlar öncelikli?

## Yanıt Formatı:
```json
{{
  "quality": {{
    "length": "short|medium|detailed",
    "clarity": "unclear|moderate|clear",
    "technical_depth": "low|medium|high",
    "overall_score": 0.0
  }},
  "extracted_info": {{
    "explicit": ["..."],
    "implied": ["..."],
    "assumed": ["..."]
  }},
  "ambiguities": [
    {{
      "text": "...",
      "type": "contradiction|missing_context|needs_clarification",
      "suggested_resolution": "..."
    }}
  ],
  "recommendations": {{
    "priority_questions": ["..."],
    "safe_assumptions": ["..."],
    "focus_areas": ["..."]
  }}
}}
```
"""


# =============================================================================
# ANSWER INTERPRETATION PROMPT
# =============================================================================

ANSWER_INTERPRETATION_PROMPT = """Sen profesyonel bir veri analisti ve UX uzmanısın.
Kullanıcının interview sorularına verdiği yanıtları yorumla.

## Soru:
{question}

## Kullanıcı Yanıtı:
{answer}

## Mevcut Context:
{context}

## Görev:
1. Yanıtı anlamlandır
2. ProjectSoul için güncellemeleri belirle
3. Takip soruları öner (gerekirse)

## Yanıt Formatı:
```json
{{
  "interpretation": {{
    "understood_value": "...",
    "confidence": 0.0,
    "notes": "..."
  }},
  "soul_updates": {{
    "field_path": "...",
    "new_value": "...",
    "reason": "..."
  }},
  "follow_up": {{
    "needed": true|false,
    "question": "...",
    "reason": "..."
  }}
}}
```
"""


# =============================================================================
# SYNTHESIS PROMPT
# =============================================================================

SYNTHESIS_PROMPT = """Sen profesyonel bir tasarım direktörüsün.
Tüm toplanan bilgileri sentezleyerek final tasarım kararlarını oluştur.

## ProjectSoul:
{soul_json}

## Interview Yanıtları:
{answers_json}

## Görev:
1. Tüm bilgileri birleştir
2. Çelişkileri çöz
3. Final tasarım parametrelerini belirle

## Çıktı:
```json
{{
  "design_parameters": {{
    "theme": "...",
    "vibe": "...",
    "color_palette": {{
      "primary": "#...",
      "secondary": "#...",
      "accent": "#...",
      "background": "#...",
      "text": "#..."
    }},
    "typography": {{
      "heading_font": "...",
      "body_font": "...",
      "style": "..."
    }},
    "spacing": {{
      "density": "spacious|balanced|compact",
      "border_radius": "sharp|slightly_rounded|rounded|pill"
    }},
    "interactions": {{
      "animation_level": "none|subtle|moderate|rich",
      "shadow_style": "none|subtle|medium|strong"
    }},
    "accessibility": {{
      "wcag_level": "AA|AAA",
      "dark_mode": true|false
    }}
  }},
  "confidence": 0.0,
  "notes": "..."
}}
```
"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_extraction_prompt(
    prompt_type: str = "soul",
    context: Optional[Dict[str, str]] = None,
) -> str:
    """
    Get extraction prompt with optional context.

    Args:
        prompt_type: Type of prompt (soul, gap, brief, answer, synthesis)
        context: Context dict for formatting

    Returns:
        Formatted prompt string
    """
    prompts = {
        "soul": SOUL_EXTRACTION_PROMPT,
        "gap": GAP_DETECTION_PROMPT,
        "brief": BRIEF_ANALYSIS_PROMPT,
        "answer": ANSWER_INTERPRETATION_PROMPT,
        "synthesis": SYNTHESIS_PROMPT,
    }

    template = prompts.get(prompt_type, SOUL_EXTRACTION_PROMPT)

    if context:
        try:
            return template.format(**context)
        except KeyError as e:
            # Return template with unfilled placeholders noted
            return f"# Missing context key: {e}\n\n{template}"

    return template


def build_soul_extraction_request(brief: str) -> str:
    """
    Build complete soul extraction request.

    Args:
        brief: Design brief text

    Returns:
        Formatted prompt for Gemini API
    """
    return get_extraction_prompt("soul", {"brief": brief})


def build_gap_detection_request(soul_json: str) -> str:
    """
    Build gap detection request.

    Args:
        soul_json: ProjectSoul as JSON string

    Returns:
        Formatted prompt for Gemini API
    """
    return get_extraction_prompt("gap", {"soul_json": soul_json})


def build_synthesis_request(soul_json: str, answers_json: str) -> str:
    """
    Build synthesis request.

    Args:
        soul_json: ProjectSoul as JSON string
        answers_json: Interview answers as JSON string

    Returns:
        Formatted prompt for Gemini API
    """
    return get_extraction_prompt("synthesis", {
        "soul_json": soul_json,
        "answers_json": answers_json,
    })
