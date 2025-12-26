"""
MAESTRO Question Bank - Phase 2

Central repository for all interview questions across 10 categories.
Questions are organized by priority and can be accessed by ID or category.
"""

from __future__ import annotations

from typing import ClassVar

from gemini_mcp.maestro.models import (
    Question,
    QuestionCategory,
    QuestionOption,
    QuestionType,
)


class QuestionBank:
    """
    Central repository of all MAESTRO interview questions.

    Questions are organized into 10 categories with priority ordering.
    The bank provides methods to retrieve questions by ID, category,
    or based on context.

    Usage:
        bank = QuestionBank()
        question = bank.get_question("q_intent_main")
        required = bank.get_required_questions()
    """

    # Category configuration with priority (1 = highest) and required flag
    CATEGORY_CONFIG: ClassVar[dict[QuestionCategory, dict]] = {
        QuestionCategory.INTENT: {"priority": 1, "required": True},
        QuestionCategory.SCOPE: {"priority": 2, "required": True},
        QuestionCategory.EXISTING_CONTEXT: {"priority": 3, "required": False},
        QuestionCategory.INDUSTRY: {"priority": 4, "required": False},
        QuestionCategory.THEME_STYLE: {"priority": 5, "required": True},
        QuestionCategory.VIBE_MOOD: {"priority": 6, "required": False},
        QuestionCategory.CONTENT: {"priority": 7, "required": False},
        QuestionCategory.TECHNICAL: {"priority": 8, "required": False},
        QuestionCategory.ACCESSIBILITY: {"priority": 9, "required": False},
        QuestionCategory.LANGUAGE: {"priority": 10, "required": True},
    }

    def __init__(self) -> None:
        """Initialize the QuestionBank and load all questions."""
        self._questions: dict[str, Question] = {}
        self._by_category: dict[QuestionCategory, list[Question]] = {
            cat: [] for cat in QuestionCategory
        }
        self._load_questions()

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def get_question(self, question_id: str) -> Question | None:
        """Get a question by its ID."""
        return self._questions.get(question_id)

    def get_questions_by_category(
        self, category: QuestionCategory
    ) -> list[Question]:
        """Get all questions in a category."""
        return self._by_category.get(category, [])

    def get_required_questions(self) -> list[Question]:
        """Get all questions from required categories."""
        required = []
        for cat, config in self.CATEGORY_CONFIG.items():
            if config["required"]:
                required.extend(self._by_category[cat])
        return required

    def get_initial_question(self, has_existing_context: bool = False) -> Question:
        """
        Get the first question based on context.

        Args:
            has_existing_context: Whether there's existing HTML to work with

        Returns:
            The appropriate starting question
        """
        if has_existing_context:
            return self._questions["q_existing_action"]
        return self._questions["q_intent_main"]

    def get_categories_by_priority(self) -> list[QuestionCategory]:
        """Get categories sorted by priority (ascending)."""
        return sorted(
            self.CATEGORY_CONFIG.keys(),
            key=lambda c: self.CATEGORY_CONFIG[c]["priority"],
        )

    def get_all_question_ids(self) -> list[str]:
        """Get all question IDs."""
        return list(self._questions.keys())

    def validate_follow_up_targets(self) -> list[str]:
        """
        Validate that all follow_up_map targets exist.

        Returns:
            List of missing question IDs (should be empty)
        """
        missing = []
        for question in self._questions.values():
            for target_id in question.follow_up_map.values():
                if target_id not in self._questions:
                    missing.append(target_id)
        return missing

    # =========================================================================
    # QUESTION LOADING
    # =========================================================================

    def _add_question(self, question: Question) -> None:
        """Add a question to the bank."""
        self._questions[question.id] = question
        self._by_category[question.category].append(question)

    def _load_questions(self) -> None:
        """Load all questions into the bank."""
        self._load_intent_questions()
        self._load_scope_questions()
        self._load_existing_context_questions()
        self._load_industry_questions()
        self._load_theme_style_questions()
        self._load_vibe_mood_questions()
        self._load_content_questions()
        self._load_technical_questions()
        self._load_accessibility_questions()
        self._load_language_questions()

    # =========================================================================
    # INTENT QUESTIONS (Priority 1)
    # =========================================================================

    def _load_intent_questions(self) -> None:
        """Load INTENT category questions."""
        self._add_question(
            Question(
                id="q_intent_main",
                category=QuestionCategory.INTENT,
                text="Bugün nasıl bir tasarım yapmak istiyorsunuz?",
                options=[
                    QuestionOption(
                        id="opt_new_design",
                        label="Sıfırdan Tasarım",
                        description="Yepyeni bir sayfa veya component oluştur",
                        icon="✨",
                    ),
                    QuestionOption(
                        id="opt_refine_existing",
                        label="Mevcut Tasarımı Geliştir",
                        description="Var olan HTML'i iyileştir veya güncelle",
                        icon="🔧",
                    ),
                    QuestionOption(
                        id="opt_from_reference",
                        label="Referanstan Tasarım",
                        description="Görsel referansa bakarak tasarla",
                        icon="🖼️",
                    ),
                ],
                follow_up_map={
                    "opt_new_design": "q_scope_type",
                    "opt_refine_existing": "q_existing_action",
                    "opt_from_reference": "q_reference_upload",
                },
            )
        )

    # =========================================================================
    # SCOPE QUESTIONS (Priority 2)
    # =========================================================================

    def _load_scope_questions(self) -> None:
        """Load SCOPE category questions."""
        # Main scope question
        self._add_question(
            Question(
                id="q_scope_type",
                category=QuestionCategory.SCOPE,
                text="Ne tür bir tasarım yapacağız?",
                options=[
                    QuestionOption(
                        id="opt_full_page",
                        label="Tam Sayfa",
                        description="Landing page, dashboard gibi komple sayfa",
                        icon="📄",
                    ),
                    QuestionOption(
                        id="opt_section",
                        label="Section",
                        description="Hero, pricing, footer gibi sayfa bölümü",
                        icon="📐",
                    ),
                    QuestionOption(
                        id="opt_component",
                        label="Component",
                        description="Button, card, form gibi tek bir bileşen",
                        icon="🧩",
                    ),
                ],
                follow_up_map={
                    "opt_full_page": "q_page_type",
                    "opt_section": "q_section_type",
                    "opt_component": "q_component_type",
                },
            )
        )

        # Page type question
        self._add_question(
            Question(
                id="q_page_type",
                category=QuestionCategory.SCOPE,
                text="Hangi tür sayfa tasarlayacağız?",
                options=[
                    QuestionOption(
                        id="opt_landing_page",
                        label="Landing Page",
                        description="Pazarlama ve tanıtım sayfası",
                        icon="🚀",
                    ),
                    QuestionOption(
                        id="opt_dashboard",
                        label="Dashboard",
                        description="Yönetim paneli ve veri görünümleri",
                        icon="📊",
                    ),
                    QuestionOption(
                        id="opt_auth_page",
                        label="Auth Page",
                        description="Giriş, kayıt, şifre sıfırlama",
                        icon="🔐",
                    ),
                    QuestionOption(
                        id="opt_pricing_page",
                        label="Pricing Page",
                        description="Fiyatlandırma ve plan karşılaştırma",
                        icon="💰",
                    ),
                    QuestionOption(
                        id="opt_blog_post",
                        label="Blog Post",
                        description="Makale ve blog içeriği sayfası",
                        icon="📝",
                    ),
                    QuestionOption(
                        id="opt_product_page",
                        label="Product Page",
                        description="E-ticaret ürün detay sayfası",
                        icon="🛍️",
                    ),
                    QuestionOption(
                        id="opt_portfolio",
                        label="Portfolio",
                        description="Showcase ve proje galerisi",
                        icon="🎨",
                    ),
                    QuestionOption(
                        id="opt_documentation",
                        label="Documentation",
                        description="API docs ve teknik dökümantasyon",
                        icon="📚",
                    ),
                ],
                show_when="q_scope_type == 'opt_full_page'",
            )
        )

        # Section type question
        self._add_question(
            Question(
                id="q_section_type",
                category=QuestionCategory.SCOPE,
                text="Hangi section'ı tasarlayacağız?",
                options=[
                    QuestionOption(
                        id="opt_hero",
                        label="Hero",
                        description="Ana banner ve açılış bölümü",
                        icon="🦸",
                    ),
                    QuestionOption(
                        id="opt_features",
                        label="Features",
                        description="Özellik tanıtım grid'i",
                        icon="⭐",
                    ),
                    QuestionOption(
                        id="opt_pricing_section",
                        label="Pricing",
                        description="Fiyat kartları bölümü",
                        icon="💳",
                    ),
                    QuestionOption(
                        id="opt_testimonials",
                        label="Testimonials",
                        description="Müşteri yorumları",
                        icon="💬",
                    ),
                    QuestionOption(
                        id="opt_cta",
                        label="CTA",
                        description="Call-to-action bölümü",
                        icon="📣",
                    ),
                    QuestionOption(
                        id="opt_footer",
                        label="Footer",
                        description="Site alt bilgi alanı",
                        icon="📋",
                    ),
                    QuestionOption(
                        id="opt_stats",
                        label="Stats",
                        description="İstatistik ve metrik gösterimi",
                        icon="📈",
                    ),
                    QuestionOption(
                        id="opt_faq",
                        label="FAQ",
                        description="Sıkça sorulan sorular",
                        icon="❓",
                    ),
                    QuestionOption(
                        id="opt_team",
                        label="Team",
                        description="Ekip tanıtımı",
                        icon="👥",
                    ),
                    QuestionOption(
                        id="opt_contact",
                        label="Contact",
                        description="İletişim formu bölümü",
                        icon="📧",
                    ),
                ],
                show_when="q_scope_type == 'opt_section'",
            )
        )

        # Component type question
        self._add_question(
            Question(
                id="q_component_type",
                category=QuestionCategory.SCOPE,
                text="Hangi component'ı tasarlayacağız?",
                options=[
                    # Atoms
                    QuestionOption(
                        id="opt_button",
                        label="Button",
                        description="Tıklanabilir buton elementi",
                        icon="🔘",
                    ),
                    QuestionOption(
                        id="opt_input",
                        label="Input",
                        description="Form giriş alanı",
                        icon="📝",
                    ),
                    QuestionOption(
                        id="opt_badge",
                        label="Badge",
                        description="Etiket ve rozet",
                        icon="🏷️",
                    ),
                    QuestionOption(
                        id="opt_avatar",
                        label="Avatar",
                        description="Kullanıcı profil resmi",
                        icon="👤",
                    ),
                    # Molecules
                    QuestionOption(
                        id="opt_card",
                        label="Card",
                        description="İçerik kartı",
                        icon="🃏",
                    ),
                    QuestionOption(
                        id="opt_form",
                        label="Form",
                        description="Form bileşeni",
                        icon="📋",
                    ),
                    QuestionOption(
                        id="opt_modal",
                        label="Modal",
                        description="Popup dialog penceresi",
                        icon="🪟",
                    ),
                    QuestionOption(
                        id="opt_tabs",
                        label="Tabs",
                        description="Sekme navigasyonu",
                        icon="📑",
                    ),
                    QuestionOption(
                        id="opt_table",
                        label="Table",
                        description="Veri tablosu",
                        icon="📊",
                    ),
                    # Organisms
                    QuestionOption(
                        id="opt_navbar",
                        label="Navbar",
                        description="Navigasyon çubuğu",
                        icon="🧭",
                    ),
                    QuestionOption(
                        id="opt_sidebar",
                        label="Sidebar",
                        description="Yan menü",
                        icon="📌",
                    ),
                    QuestionOption(
                        id="opt_data_table",
                        label="Data Table",
                        description="Sıralama ve filtreleme ile gelişmiş tablo",
                        icon="📈",
                    ),
                ],
                show_when="q_scope_type == 'opt_component'",
            )
        )

    # =========================================================================
    # EXISTING CONTEXT QUESTIONS (Priority 3)
    # =========================================================================

    def _load_existing_context_questions(self) -> None:
        """Load EXISTING_CONTEXT category questions."""
        self._add_question(
            Question(
                id="q_existing_action",
                category=QuestionCategory.EXISTING_CONTEXT,
                text="Mevcut tasarımla ne yapmak istiyorsunuz?",
                options=[
                    QuestionOption(
                        id="opt_refine",
                        label="Geliştir",
                        description="Mevcut tasarımı iyileştir",
                        icon="✨",
                    ),
                    QuestionOption(
                        id="opt_replace_section",
                        label="Bölüm Değiştir",
                        description="Belirli bir section'ı yeniden tasarla",
                        icon="🔄",
                    ),
                    QuestionOption(
                        id="opt_match_style",
                        label="Stil Eşle",
                        description="Bu stile uygun yeni tasarım yap",
                        icon="🎨",
                    ),
                ],
                required=False,
            )
        )

        self._add_question(
            Question(
                id="q_reference_upload",
                category=QuestionCategory.EXISTING_CONTEXT,
                text="Referans görseli yükleyin veya dosya yolunu belirtin",
                question_type=QuestionType.TEXT_INPUT,
                options=[],
                required=False,
                help_text="PNG, JPG veya WEBP formatında görsel yükleyebilirsiniz",
            )
        )

        self._add_question(
            Question(
                id="q_reference_adherence",
                category=QuestionCategory.EXISTING_CONTEXT,
                text="Referansa ne kadar sadık kalmalıyız?",
                options=[
                    QuestionOption(
                        id="opt_strict",
                        label="Birebir",
                        description="Mümkün olduğunca aynı görünüm",
                        icon="🎯",
                    ),
                    QuestionOption(
                        id="opt_inspired",
                        label="İlham Al",
                        description="Genel havayı yakala, detaylar değişebilir",
                        icon="💡",
                    ),
                    QuestionOption(
                        id="opt_extract_tokens",
                        label="Sadece Stil Çıkar",
                        description="Renk ve tipografiyi al, layout farklı olabilir",
                        icon="🎨",
                    ),
                ],
                show_when="q_intent_main == 'opt_from_reference'",
                required=False,
            )
        )

    # =========================================================================
    # INDUSTRY QUESTIONS (Priority 4)
    # =========================================================================

    def _load_industry_questions(self) -> None:
        """Load INDUSTRY category questions."""
        self._add_question(
            Question(
                id="q_target_audience",
                category=QuestionCategory.INDUSTRY,
                text="Hedef kitleniz kim?",
                options=[
                    QuestionOption(
                        id="opt_b2b",
                        label="B2B",
                        description="İşletmeler ve kurumsal müşteriler",
                        icon="🏢",
                    ),
                    QuestionOption(
                        id="opt_b2c",
                        label="B2C",
                        description="Son kullanıcılar ve tüketiciler",
                        icon="👥",
                    ),
                    QuestionOption(
                        id="opt_internal",
                        label="İç Kullanım",
                        description="Şirket içi araçlar ve paneller",
                        icon="🔒",
                    ),
                    QuestionOption(
                        id="opt_developer",
                        label="Developer",
                        description="Yazılım geliştiriciler",
                        icon="👨‍💻",
                    ),
                ],
                required=False,
            )
        )

        self._add_question(
            Question(
                id="q_industry_type",
                category=QuestionCategory.INDUSTRY,
                text="Hangi sektör için tasarım yapıyorsunuz?",
                options=[
                    QuestionOption(
                        id="opt_tech_saas",
                        label="Teknoloji / SaaS",
                        description="Yazılım, uygulama, dijital ürün",
                        icon="💻",
                    ),
                    QuestionOption(
                        id="opt_finance",
                        label="Finans",
                        description="Banka, sigorta, fintech",
                        icon="💰",
                    ),
                    QuestionOption(
                        id="opt_health",
                        label="Sağlık",
                        description="Hastane, klinik, sağlık teknolojisi",
                        icon="🏥",
                    ),
                    QuestionOption(
                        id="opt_ecommerce",
                        label="E-Ticaret",
                        description="Online mağaza, marketplace",
                        icon="🛒",
                    ),
                    QuestionOption(
                        id="opt_education",
                        label="Eğitim",
                        description="EdTech, online kurs, okul",
                        icon="📚",
                    ),
                    QuestionOption(
                        id="opt_food",
                        label="Yiyecek & İçecek",
                        description="Restoran, cafe, food delivery",
                        icon="🍽️",
                    ),
                    QuestionOption(
                        id="opt_travel",
                        label="Seyahat",
                        description="Otel, uçak, tur operatörleri",
                        icon="✈️",
                    ),
                    QuestionOption(
                        id="opt_general",
                        label="Genel",
                        description="Belirli bir sektör yok",
                        icon="🌐",
                    ),
                ],
                required=False,
                show_when="q_target_audience in ['opt_b2b', 'opt_internal']",
            )
        )

        self._add_question(
            Question(
                id="q_formality_level",
                category=QuestionCategory.INDUSTRY,
                text="Tasarım ne kadar resmi olmalı?",
                options=[
                    QuestionOption(
                        id="opt_formal",
                        label="Resmi",
                        description="Kurumsal, ciddi, profesyonel",
                        icon="👔",
                    ),
                    QuestionOption(
                        id="opt_semi_formal",
                        label="Yarı Resmi",
                        description="Profesyonel ama samimi",
                        icon="👕",
                    ),
                    QuestionOption(
                        id="opt_casual",
                        label="Rahat",
                        description="Arkadaşça, samimi, eğlenceli",
                        icon="👟",
                    ),
                ],
                required=False,
            )
        )

    # =========================================================================
    # THEME & STYLE QUESTIONS (Priority 5)
    # =========================================================================

    def _load_theme_style_questions(self) -> None:
        """Load THEME_STYLE category questions."""
        self._add_question(
            Question(
                id="q_theme_preference",
                category=QuestionCategory.THEME_STYLE,
                text="Hangi görsel stili tercih ediyorsunuz?",
                options=[
                    QuestionOption(
                        id="opt_modern_minimal",
                        label="Modern Minimal",
                        description="Temiz, profesyonel, çok beyaz alan",
                        icon="✨",
                    ),
                    QuestionOption(
                        id="opt_corporate",
                        label="Kurumsal",
                        description="Ciddi, güven veren, geleneksel",
                        icon="🏢",
                    ),
                    QuestionOption(
                        id="opt_startup",
                        label="Startup",
                        description="Modern, yenilikçi, teknoloji odaklı",
                        icon="🚀",
                    ),
                    QuestionOption(
                        id="opt_brutalist",
                        label="Brutalist",
                        description="Cesur, kontrast, dikkat çekici",
                        icon="⬛",
                    ),
                    QuestionOption(
                        id="opt_glassmorphism",
                        label="Glassmorphism",
                        description="Buzlu cam efekti, modern ve şık",
                        icon="🪟",
                    ),
                    QuestionOption(
                        id="opt_neo_brutalism",
                        label="Neo-Brutalism",
                        description="Eğlenceli, renkli, cesur",
                        icon="🎨",
                    ),
                    QuestionOption(
                        id="opt_cyberpunk",
                        label="Cyberpunk",
                        description="Neon renkler, koyu tema, fütüristik",
                        icon="🌆",
                    ),
                    QuestionOption(
                        id="opt_nature",
                        label="Doğal",
                        description="Toprak tonları, organik hissiyat",
                        icon="🌿",
                    ),
                ],
            )
        )

        self._add_question(
            Question(
                id="q_color_mode",
                category=QuestionCategory.THEME_STYLE,
                text="Renk modu tercihiniz nedir?",
                options=[
                    QuestionOption(
                        id="opt_light",
                        label="Light Mode",
                        description="Açık arka plan, koyu metin",
                        icon="☀️",
                    ),
                    QuestionOption(
                        id="opt_dark",
                        label="Dark Mode",
                        description="Koyu arka plan, açık metin",
                        icon="🌙",
                    ),
                    QuestionOption(
                        id="opt_both",
                        label="Her İkisi",
                        description="Light ve dark mode desteği",
                        icon="🌓",
                    ),
                ],
            )
        )

        self._add_question(
            Question(
                id="q_color_preference",
                category=QuestionCategory.THEME_STYLE,
                text="Renk paleti tercihiniz?",
                options=[
                    QuestionOption(
                        id="opt_brand_colors",
                        label="Marka Renkleri",
                        description="Kendi marka renklerinizi kullanın",
                        icon="🎨",
                    ),
                    QuestionOption(
                        id="opt_blue_corporate",
                        label="Mavi Kurumsal",
                        description="Güven veren mavi tonları",
                        icon="💙",
                    ),
                    QuestionOption(
                        id="opt_green_nature",
                        label="Yeşil Doğal",
                        description="Sürdürülebilir, doğal hissiyat",
                        icon="💚",
                    ),
                    QuestionOption(
                        id="opt_purple_creative",
                        label="Mor Yaratıcı",
                        description="Premium, yaratıcı, farklı",
                        icon="💜",
                    ),
                    QuestionOption(
                        id="opt_warm_sunset",
                        label="Sıcak Tonlar",
                        description="Turuncu, kırmızı, sıcak",
                        icon="🧡",
                    ),
                    QuestionOption(
                        id="opt_monochrome",
                        label="Monokrom",
                        description="Siyah, beyaz, gri tonları",
                        icon="⬛",
                    ),
                ],
                required=False,
            )
        )

        self._add_question(
            Question(
                id="q_brand_primary_color",
                category=QuestionCategory.THEME_STYLE,
                text="Ana marka renginizi girin (hex kodu)",
                question_type=QuestionType.COLOR_PICKER,
                options=[],
                required=False,
                show_when="q_color_preference == 'opt_brand_colors'",
                help_text="Örnek: #E11D48 veya #3B82F6",
            )
        )

    # =========================================================================
    # VIBE & MOOD QUESTIONS (Priority 6)
    # =========================================================================

    def _load_vibe_mood_questions(self) -> None:
        """Load VIBE_MOOD category questions."""
        self._add_question(
            Question(
                id="q_design_vibe",
                category=QuestionCategory.VIBE_MOOD,
                text="Tasarımın genel havası nasıl olsun?",
                options=[
                    QuestionOption(
                        id="opt_elite_corporate",
                        label="Elite Kurumsal",
                        description="Lüks, prestijli, üst segment",
                        icon="👑",
                    ),
                    QuestionOption(
                        id="opt_playful_funny",
                        label="Eğlenceli",
                        description="Neşeli, enerjik, samimi",
                        icon="🎉",
                    ),
                    QuestionOption(
                        id="opt_cyberpunk_edge",
                        label="Siber Punk",
                        description="Fütüristik, keskin, teknolojik",
                        icon="🤖",
                    ),
                    QuestionOption(
                        id="opt_luxury_editorial",
                        label="Lüks Editöryal",
                        description="Dergi tarzı, zarif, tipografi odaklı",
                        icon="📰",
                    ),
                ],
                required=False,
            )
        )

    # =========================================================================
    # CONTENT QUESTIONS (Priority 7)
    # =========================================================================

    def _load_content_questions(self) -> None:
        """Load CONTENT category questions."""
        self._add_question(
            Question(
                id="q_content_ready",
                category=QuestionCategory.CONTENT,
                text="İçerik hazır mı?",
                options=[
                    QuestionOption(
                        id="opt_content_ready",
                        label="Evet, İçerik Hazır",
                        description="Başlık, metin ve görseller mevcut",
                        icon="✅",
                    ),
                    QuestionOption(
                        id="opt_placeholder",
                        label="Placeholder Kullan",
                        description="Örnek içerik ile tasarla",
                        icon="📝",
                    ),
                    QuestionOption(
                        id="opt_generate",
                        label="İçerik Üret",
                        description="AI ile içerik oluştur",
                        icon="🤖",
                    ),
                ],
                required=False,
            )
        )

        self._add_question(
            Question(
                id="q_content_input",
                category=QuestionCategory.CONTENT,
                text="İçerik detaylarını girin (JSON formatında)",
                question_type=QuestionType.TEXT_INPUT,
                options=[],
                required=False,
                show_when="q_content_ready == 'opt_content_ready'",
                help_text='Örnek: {"title": "Başlık", "subtitle": "Alt başlık"}',
            )
        )

    # =========================================================================
    # TECHNICAL QUESTIONS (Priority 8)
    # =========================================================================

    def _load_technical_questions(self) -> None:
        """Load TECHNICAL category questions."""
        self._add_question(
            Question(
                id="q_technical_level",
                category=QuestionCategory.TECHNICAL,
                text="Teknik özellikler belirlemek ister misiniz?",
                options=[
                    QuestionOption(
                        id="opt_yes_technical",
                        label="Evet",
                        description="Border radius, spacing vb. belirleyeceğim",
                        icon="⚙️",
                    ),
                    QuestionOption(
                        id="opt_no_technical",
                        label="Hayır, Otomatik",
                        description="Varsayılan ayarları kullan",
                        icon="🤖",
                    ),
                ],
                required=False,
            )
        )

        self._add_question(
            Question(
                id="q_border_radius",
                category=QuestionCategory.TECHNICAL,
                text="Köşe yuvarlaklığı (border-radius) tercihiniz?",
                options=[
                    QuestionOption(
                        id="opt_sharp",
                        label="Keskin",
                        description="Köşeler yuvarlak değil",
                        icon="⬛",
                    ),
                    QuestionOption(
                        id="opt_subtle",
                        label="Hafif",
                        description="rounded-md seviyesi",
                        icon="🔲",
                    ),
                    QuestionOption(
                        id="opt_rounded",
                        label="Yuvarlak",
                        description="rounded-xl seviyesi",
                        icon="⬜",
                    ),
                    QuestionOption(
                        id="opt_pill",
                        label="Pill",
                        description="Tamamen yuvarlak (rounded-full)",
                        icon="💊",
                    ),
                ],
                show_when="q_technical_level == 'opt_yes_technical'",
                required=False,
            )
        )

        self._add_question(
            Question(
                id="q_animation_level",
                category=QuestionCategory.TECHNICAL,
                text="Animasyon seviyesi ne olsun?",
                options=[
                    QuestionOption(
                        id="opt_none_anim",
                        label="Yok",
                        description="Animasyon kullanma",
                        icon="🚫",
                    ),
                    QuestionOption(
                        id="opt_subtle_anim",
                        label="Minimal",
                        description="Sadece hover efektleri",
                        icon="✨",
                    ),
                    QuestionOption(
                        id="opt_moderate_anim",
                        label="Orta",
                        description="Geçişler ve micro-interactions",
                        icon="🌊",
                    ),
                    QuestionOption(
                        id="opt_rich_anim",
                        label="Zengin",
                        description="Scroll animasyonları dahil",
                        icon="🎬",
                    ),
                ],
                show_when="q_technical_level == 'opt_yes_technical'",
                required=False,
            )
        )

    # =========================================================================
    # ACCESSIBILITY QUESTIONS (Priority 9)
    # =========================================================================

    def _load_accessibility_questions(self) -> None:
        """Load ACCESSIBILITY category questions."""
        self._add_question(
            Question(
                id="q_accessibility_level",
                category=QuestionCategory.ACCESSIBILITY,
                text="Erişilebilirlik seviyesi nedir?",
                options=[
                    QuestionOption(
                        id="opt_wcag_aa",
                        label="WCAG AA",
                        description="Standart erişilebilirlik (4.5:1 kontrast)",
                        icon="✅",
                    ),
                    QuestionOption(
                        id="opt_wcag_aaa",
                        label="WCAG AAA",
                        description="Yüksek erişilebilirlik (7:1 kontrast)",
                        icon="🏆",
                    ),
                    QuestionOption(
                        id="opt_basic_a11y",
                        label="Temel",
                        description="Semantic HTML ve alt text",
                        icon="📋",
                    ),
                ],
                required=False,
            )
        )

    # =========================================================================
    # LANGUAGE QUESTIONS (Priority 10)
    # =========================================================================

    def _load_language_questions(self) -> None:
        """Load LANGUAGE category questions."""
        self._add_question(
            Question(
                id="q_content_language",
                category=QuestionCategory.LANGUAGE,
                text="İçerik hangi dilde olacak?",
                options=[
                    QuestionOption(
                        id="opt_turkish",
                        label="Türkçe",
                        description="Türkçe içerik",
                        icon="🇹🇷",
                    ),
                    QuestionOption(
                        id="opt_english",
                        label="English",
                        description="English content",
                        icon="🇬🇧",
                    ),
                    QuestionOption(
                        id="opt_german",
                        label="Deutsch",
                        description="Deutsche Inhalte",
                        icon="🇩🇪",
                    ),
                ],
            )
        )
