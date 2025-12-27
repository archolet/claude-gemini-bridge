"""
MAESTRO Turkish Question Templates - Phase 4

Dynamic question templates for the interview system.
Questions are context-aware and adapt based on ProjectSoul gaps.
"""

from typing import Dict, List, Optional

from gemini_mcp.maestro.models.soul import InterviewPhase


# =============================================================================
# QUESTION TEMPLATES BY CATEGORY
# =============================================================================

QUESTION_TEMPLATES: Dict[str, Dict[str, any]] = {
    # -------------------------------------------------------------------------
    # BRIEF INGESTION QUESTIONS
    # -------------------------------------------------------------------------
    "project_name": {
        "phase": InterviewPhase.BRIEF_INGESTION,
        "text": "Projenizin adı nedir?",
        "hint": "Marka veya ürün adını girebilirsiniz",
        "required": True,
        "type": "text",
    },
    "project_tagline": {
        "phase": InterviewPhase.BRIEF_INGESTION,
        "text": "Projeniz için kısa bir slogan veya açıklama var mı?",
        "hint": "Örn: 'Herkes için finansal özgürlük'",
        "required": False,
        "type": "text",
    },
    "project_type": {
        "phase": InterviewPhase.BRIEF_INGESTION,
        "text": "Ne tür bir proje üzerinde çalışıyorsunuz?",
        "options": [
            {"id": "landing", "label": "Landing Page", "emoji": "🚀"},
            {"id": "dashboard", "label": "Dashboard / Admin Panel", "emoji": "📊"},
            {"id": "ecommerce", "label": "E-ticaret", "emoji": "🛒"},
            {"id": "portfolio", "label": "Portfolyo / Kişisel Site", "emoji": "💼"},
            {"id": "saas", "label": "SaaS Ürünü", "emoji": "☁️"},
            {"id": "mobile_app", "label": "Mobil Uygulama Arayüzü", "emoji": "📱"},
            {"id": "other", "label": "Diğer", "emoji": "✨"},
        ],
        "required": True,
        "type": "single_choice",
    },

    # -------------------------------------------------------------------------
    # SOUL EXTRACTION QUESTIONS
    # -------------------------------------------------------------------------
    "brand_personality": {
        "phase": InterviewPhase.SOUL_EXTRACTION,
        "text": "Markanızı bir kişi olarak tanımlamanız gerekse, nasıl birisi olurdu?",
        "options": [
            {"id": "sincere", "label": "Samimi ve Güvenilir", "emoji": "🤝", "trait": "sincerity"},
            {"id": "exciting", "label": "Heyecanlı ve Cesur", "emoji": "⚡", "trait": "excitement"},
            {"id": "competent", "label": "Profesyonel ve Yetkin", "emoji": "💼", "trait": "competence"},
            {"id": "sophisticated", "label": "Sofistike ve Zarif", "emoji": "✨", "trait": "sophistication"},
            {"id": "rugged", "label": "Sağlam ve Dayanıklı", "emoji": "🏔️", "trait": "ruggedness"},
        ],
        "required": True,
        "type": "single_choice",
        "aaker_mapping": True,
    },
    "brand_archetype": {
        "phase": InterviewPhase.SOUL_EXTRACTION,
        "text": "Markanız hangi arketipi temsil ediyor?",
        "options": [
            {"id": "hero", "label": "Kahraman", "desc": "Cesur, güçlü, ilham verici", "emoji": "🦸"},
            {"id": "sage", "label": "Bilge", "desc": "Akıllı, güvenilir, uzman", "emoji": "🎓"},
            {"id": "explorer", "label": "Kaşif", "desc": "Maceracı, özgür, keşifçi", "emoji": "🧭"},
            {"id": "creator", "label": "Yaratıcı", "desc": "Yenilikçi, hayal gücü yüksek", "emoji": "🎨"},
            {"id": "caregiver", "label": "Koruyucu", "desc": "Şefkatli, destekleyici", "emoji": "💝"},
            {"id": "magician", "label": "Büyücü", "desc": "Dönüştürücü, vizyoner", "emoji": "✨"},
            {"id": "ruler", "label": "Lider", "desc": "Otoriter, prestijli", "emoji": "👑"},
            {"id": "everyman", "label": "Sıradan İnsan", "desc": "Erişilebilir, samimi", "emoji": "🙋"},
            {"id": "jester", "label": "Soytarı", "desc": "Eğlenceli, neşeli", "emoji": "🎭"},
            {"id": "lover", "label": "Aşık", "desc": "Tutkulu, çekici", "emoji": "❤️"},
            {"id": "innocent", "label": "Masum", "desc": "Saf, iyimser", "emoji": "🌸"},
            {"id": "outlaw", "label": "Asi", "desc": "Kural yıkıcı, özgün", "emoji": "🔥"},
        ],
        "required": False,
        "type": "single_choice",
    },

    # -------------------------------------------------------------------------
    # CONTEXT GATHERING QUESTIONS
    # -------------------------------------------------------------------------
    "target_audience_age": {
        "phase": InterviewPhase.CONTEXT_GATHERING,
        "text": "Hedef kitlenizin yaş aralığı nedir?",
        "options": [
            {"id": "gen_z", "label": "Gen Z (18-25)", "emoji": "🎮"},
            {"id": "millennials", "label": "Millennials (26-40)", "emoji": "💻"},
            {"id": "gen_x", "label": "Gen X (41-55)", "emoji": "📱"},
            {"id": "boomers", "label": "Baby Boomers (55+)", "emoji": "📰"},
            {"id": "all_ages", "label": "Tüm Yaşlar", "emoji": "🌍"},
        ],
        "required": True,
        "type": "single_choice",
    },
    "target_audience_tech": {
        "phase": InterviewPhase.CONTEXT_GATHERING,
        "text": "Hedef kitlenizin teknoloji bilgisi ne seviyede?",
        "options": [
            {"id": "beginner", "label": "Başlangıç", "desc": "Temel kullanıcılar", "emoji": "🌱"},
            {"id": "intermediate", "label": "Orta", "desc": "Rahat kullanıcılar", "emoji": "🌿"},
            {"id": "advanced", "label": "İleri", "desc": "Deneyimli kullanıcılar", "emoji": "🌳"},
            {"id": "expert", "label": "Uzman", "desc": "Profesyoneller", "emoji": "🚀"},
        ],
        "required": True,
        "type": "single_choice",
    },
    "industry": {
        "phase": InterviewPhase.CONTEXT_GATHERING,
        "text": "Hangi sektörde faaliyet gösteriyorsunuz?",
        "options": [
            {"id": "finance", "label": "Finans & Bankacılık", "emoji": "🏦"},
            {"id": "healthcare", "label": "Sağlık", "emoji": "🏥"},
            {"id": "technology", "label": "Teknoloji", "emoji": "💻"},
            {"id": "education", "label": "Eğitim", "emoji": "📚"},
            {"id": "ecommerce", "label": "E-ticaret", "emoji": "🛍️"},
            {"id": "real_estate", "label": "Gayrimenkul", "emoji": "🏠"},
            {"id": "travel", "label": "Seyahat & Turizm", "emoji": "✈️"},
            {"id": "food", "label": "Yiyecek & İçecek", "emoji": "🍽️"},
            {"id": "entertainment", "label": "Eğlence & Medya", "emoji": "🎬"},
            {"id": "other", "label": "Diğer", "emoji": "📌"},
        ],
        "required": True,
        "type": "single_choice",
    },
    "competitors": {
        "phase": InterviewPhase.CONTEXT_GATHERING,
        "text": "Rakipleriniz kimler? (Varsa web sitelerini paylaşabilirsiniz)",
        "hint": "Örn: stripe.com, notion.so",
        "required": False,
        "type": "text",
    },

    # -------------------------------------------------------------------------
    # DEEP DIVE QUESTIONS
    # -------------------------------------------------------------------------
    "theme_preference": {
        "phase": InterviewPhase.DEEP_DIVE,
        "text": "Hangi görsel tema sizin için en uygun?",
        "options": [
            {"id": "modern-minimal", "label": "Modern Minimal", "desc": "Temiz, profesyonel", "emoji": "⚪"},
            {"id": "brutalist", "label": "Brutalist", "desc": "Cesur, yüksek kontrast", "emoji": "⬛"},
            {"id": "glassmorphism", "label": "Glassmorphism", "desc": "Şeffaf, modern", "emoji": "💎"},
            {"id": "neo-brutalism", "label": "Neo-Brutalism", "desc": "Canlı, eğlenceli", "emoji": "🎨"},
            {"id": "soft-ui", "label": "Soft UI", "desc": "Yumuşak, neumorphic", "emoji": "☁️"},
            {"id": "corporate", "label": "Kurumsal", "desc": "Profesyonel, güvenilir", "emoji": "🏢"},
            {"id": "gradient", "label": "Gradient", "desc": "Renkli geçişler", "emoji": "🌈"},
            {"id": "cyberpunk", "label": "Cyberpunk", "desc": "Neon, fütüristik", "emoji": "🌃"},
            {"id": "retro", "label": "Retro", "desc": "80s/90s nostalji", "emoji": "📼"},
            {"id": "pastel", "label": "Pastel", "desc": "Yumuşak renkler", "emoji": "🌸"},
            {"id": "dark_mode_first", "label": "Dark Mode First", "desc": "Koyu tema öncelikli", "emoji": "🌙"},
            {"id": "nature", "label": "Doğa", "desc": "Organik, toprak tonları", "emoji": "🌿"},
            {"id": "startup", "label": "Startup", "desc": "Teknoloji startup estetiği", "emoji": "🚀"},
        ],
        "required": True,
        "type": "single_choice",
    },
    "color_preference": {
        "phase": InterviewPhase.DEEP_DIVE,
        "text": "Ana renk tercihiniz nedir?",
        "options": [
            {"id": "blue", "label": "Mavi", "hex": "#3B82F6", "emoji": "💙"},
            {"id": "green", "label": "Yeşil", "hex": "#10B981", "emoji": "💚"},
            {"id": "purple", "label": "Mor", "hex": "#8B5CF6", "emoji": "💜"},
            {"id": "red", "label": "Kırmızı", "hex": "#EF4444", "emoji": "❤️"},
            {"id": "orange", "label": "Turuncu", "hex": "#F97316", "emoji": "🧡"},
            {"id": "teal", "label": "Turkuaz", "hex": "#14B8A6", "emoji": "💎"},
            {"id": "pink", "label": "Pembe", "hex": "#EC4899", "emoji": "💗"},
            {"id": "neutral", "label": "Nötr / Gri", "hex": "#6B7280", "emoji": "⚪"},
            {"id": "custom", "label": "Özel Renk", "emoji": "🎨"},
        ],
        "required": True,
        "type": "single_choice",
    },
    "custom_color": {
        "phase": InterviewPhase.DEEP_DIVE,
        "text": "Özel renginizi giriniz (hex formatında)",
        "hint": "Örn: #E11D48",
        "required": False,
        "type": "text",
        "condition": {"question": "color_preference", "value": "custom"},
    },
    "typography_preference": {
        "phase": InterviewPhase.DEEP_DIVE,
        "text": "Tipografi tercihiniz nedir?",
        "options": [
            {"id": "modern_sans", "label": "Modern Sans-Serif", "desc": "Inter, Poppins", "emoji": "Aa"},
            {"id": "classic_serif", "label": "Klasik Serif", "desc": "Playfair, Lora", "emoji": "𝒜𝒶"},
            {"id": "geometric", "label": "Geometrik", "desc": "Montserrat, Raleway", "emoji": "◉"},
            {"id": "humanist", "label": "Humanist", "desc": "Open Sans, Lato", "emoji": "✍️"},
            {"id": "monospace", "label": "Monospace", "desc": "JetBrains Mono, Fira Code", "emoji": "💻"},
        ],
        "required": True,
        "type": "single_choice",
    },
    "density_preference": {
        "phase": InterviewPhase.DEEP_DIVE,
        "text": "İçerik yoğunluğu nasıl olsun?",
        "options": [
            {"id": "spacious", "label": "Ferah", "desc": "Çok boşluk, minimal", "emoji": "🌊"},
            {"id": "balanced", "label": "Dengeli", "desc": "Orta yoğunluk", "emoji": "⚖️"},
            {"id": "compact", "label": "Kompakt", "desc": "Yoğun, veri odaklı", "emoji": "📊"},
        ],
        "required": True,
        "type": "single_choice",
    },

    # -------------------------------------------------------------------------
    # VISUAL EXPLORATION QUESTIONS
    # -------------------------------------------------------------------------
    "animation_preference": {
        "phase": InterviewPhase.VISUAL_EXPLORATION,
        "text": "Animasyon ve geçiş tercihiniz nedir?",
        "options": [
            {"id": "none", "label": "Minimal / Yok", "desc": "Sade, hızlı", "emoji": "⚡"},
            {"id": "subtle", "label": "İnce", "desc": "Hafif hover efektleri", "emoji": "✨"},
            {"id": "moderate", "label": "Orta", "desc": "Sayfa geçişleri, micro-interactions", "emoji": "🎭"},
            {"id": "rich", "label": "Zengin", "desc": "Scroll animasyonları, parallax", "emoji": "🎬"},
        ],
        "required": True,
        "type": "single_choice",
    },
    "icon_style": {
        "phase": InterviewPhase.VISUAL_EXPLORATION,
        "text": "İkon stili tercihiniz nedir?",
        "options": [
            {"id": "outline", "label": "Outline", "desc": "İnce çizgiler", "emoji": "○"},
            {"id": "solid", "label": "Solid", "desc": "Dolgulu", "emoji": "●"},
            {"id": "duotone", "label": "Duotone", "desc": "İki renk", "emoji": "◐"},
            {"id": "gradient", "label": "Gradient", "desc": "Renkli geçişli", "emoji": "🌈"},
        ],
        "required": False,
        "type": "single_choice",
    },
    "corner_style": {
        "phase": InterviewPhase.VISUAL_EXPLORATION,
        "text": "Köşe stili tercihiniz nedir?",
        "options": [
            {"id": "sharp", "label": "Keskin", "desc": "rounded-none", "emoji": "⬜"},
            {"id": "slightly_rounded", "label": "Hafif Yuvarlak", "desc": "rounded-sm", "emoji": "▢"},
            {"id": "rounded", "label": "Yuvarlak", "desc": "rounded-lg", "emoji": "⬜"},
            {"id": "pill", "label": "Hap Şekli", "desc": "rounded-full", "emoji": "💊"},
        ],
        "required": False,
        "type": "single_choice",
    },
    "shadow_preference": {
        "phase": InterviewPhase.VISUAL_EXPLORATION,
        "text": "Gölge kullanımı nasıl olsun?",
        "options": [
            {"id": "none", "label": "Gölge Yok", "desc": "Düz tasarım", "emoji": "⬜"},
            {"id": "subtle", "label": "İnce Gölge", "desc": "shadow-sm", "emoji": "🌥️"},
            {"id": "medium", "label": "Orta Gölge", "desc": "shadow-md", "emoji": "☁️"},
            {"id": "strong", "label": "Belirgin Gölge", "desc": "shadow-xl", "emoji": "🌫️"},
        ],
        "required": False,
        "type": "single_choice",
    },

    # -------------------------------------------------------------------------
    # VALIDATION QUESTIONS
    # -------------------------------------------------------------------------
    "confirm_theme": {
        "phase": InterviewPhase.VALIDATION,
        "text": "Seçtiğiniz temayı onaylıyor musunuz?",
        "template": "Tema: {theme} | Renk: {color} | Tipografi: {typography}",
        "options": [
            {"id": "confirm", "label": "Evet, Onaylıyorum", "emoji": "✅"},
            {"id": "modify", "label": "Değişiklik Yapmak İstiyorum", "emoji": "✏️"},
        ],
        "required": True,
        "type": "single_choice",
    },
    "confirm_audience": {
        "phase": InterviewPhase.VALIDATION,
        "text": "Hedef kitle bilgilerini onaylıyor musunuz?",
        "template": "Yaş: {age} | Teknoloji: {tech_level} | Sektör: {industry}",
        "options": [
            {"id": "confirm", "label": "Evet, Onaylıyorum", "emoji": "✅"},
            {"id": "modify", "label": "Değişiklik Yapmak İstiyorum", "emoji": "✏️"},
        ],
        "required": True,
        "type": "single_choice",
    },
    "additional_notes": {
        "phase": InterviewPhase.VALIDATION,
        "text": "Eklemek istediğiniz başka bir şey var mı?",
        "hint": "Özel istekler, kısıtlamalar veya notlar",
        "required": False,
        "type": "text",
    },
}


# =============================================================================
# CATEGORY HEADERS
# =============================================================================

CATEGORY_HEADERS: Dict[str, Dict[str, str]] = {
    "project_info": {
        "title": "Proje Bilgileri",
        "emoji": "📋",
        "description": "Projeniz hakkında temel bilgiler",
    },
    "brand_identity": {
        "title": "Marka Kimliği",
        "emoji": "✨",
        "description": "Markanızın kişiliği ve değerleri",
    },
    "target_audience": {
        "title": "Hedef Kitle",
        "emoji": "👥",
        "description": "Kullanıcılarınız hakkında bilgiler",
    },
    "visual_design": {
        "title": "Görsel Tasarım",
        "emoji": "🎨",
        "description": "Renk, tipografi ve stil tercihleri",
    },
    "interactions": {
        "title": "Etkileşimler",
        "emoji": "⚡",
        "description": "Animasyonlar ve kullanıcı deneyimi",
    },
    "validation": {
        "title": "Doğrulama",
        "emoji": "✅",
        "description": "Bilgilerin son kontrolü",
    },
}


# =============================================================================
# OPTION LABELS (for dynamic option generation)
# =============================================================================

OPTION_LABELS: Dict[str, str] = {
    # Yes/No
    "yes": "Evet",
    "no": "Hayır",
    "maybe": "Belki",

    # Intensity
    "low": "Düşük",
    "medium": "Orta",
    "high": "Yüksek",

    # Priority
    "critical": "Kritik",
    "important": "Önemli",
    "nice_to_have": "Olsa İyi Olur",

    # Satisfaction
    "very_satisfied": "Çok Memnun",
    "satisfied": "Memnun",
    "neutral": "Nötr",
    "dissatisfied": "Memnun Değil",

    # Confirmation
    "confirm": "Onayla",
    "cancel": "İptal",
    "skip": "Atla",
    "back": "Geri",
    "next": "İleri",
    "finish": "Bitir",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_question_text(
    question_id: str,
    context: Optional[Dict[str, any]] = None,
) -> str:
    """
    Get formatted question text.

    Args:
        question_id: Question identifier
        context: Optional context for template formatting

    Returns:
        Formatted question text
    """
    template = QUESTION_TEMPLATES.get(question_id, {})
    text = template.get("text", "")

    if context and "{" in text:
        try:
            text = text.format(**context)
        except KeyError:
            pass

    return text


def get_category_header(category: str) -> Dict[str, str]:
    """
    Get category header information.

    Args:
        category: Category identifier

    Returns:
        Category header dict with title, emoji, description
    """
    return CATEGORY_HEADERS.get(category, {
        "title": category.title(),
        "emoji": "📌",
        "description": "",
    })


def get_questions_for_phase(phase: InterviewPhase) -> List[Dict[str, any]]:
    """
    Get all questions for a specific interview phase.

    Args:
        phase: Interview phase

    Returns:
        List of question templates for the phase
    """
    return [
        {"id": qid, **qdata}
        for qid, qdata in QUESTION_TEMPLATES.items()
        if qdata.get("phase") == phase
    ]


def get_required_questions(phase: Optional[InterviewPhase] = None) -> List[str]:
    """
    Get IDs of required questions.

    Args:
        phase: Optional phase filter

    Returns:
        List of required question IDs
    """
    questions = []
    for qid, qdata in QUESTION_TEMPLATES.items():
        if qdata.get("required", False):
            if phase is None or qdata.get("phase") == phase:
                questions.append(qid)
    return questions
