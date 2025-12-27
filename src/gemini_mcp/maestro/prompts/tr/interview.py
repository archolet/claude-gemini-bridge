"""
MAESTRO Turkish Interview Prompts - Phase 4

Interview phase prompts, transition messages, and progress indicators
in Turkish language.
"""

from typing import Dict, Optional

from gemini_mcp.maestro.models.soul import InterviewPhase


# =============================================================================
# PHASE PROMPTS
# =============================================================================

PHASE_PROMPTS: Dict[InterviewPhase, Dict[str, str]] = {
    InterviewPhase.BRIEF_INGESTION: {
        "title": "Brief Analizi",
        "emoji": "📋",
        "intro": "Projenizi anlamak için brief'inizi analiz ediyorum...",
        "description": (
            "Tasarım brief'inizi okuyorum ve temel bilgileri çıkarıyorum. "
            "Bu aşamada proje adı, hedef kitle ve genel ton belirleniyor."
        ),
        "tip": "Detaylı bir brief, daha iyi tasarım kararları demektir.",
    },
    InterviewPhase.SOUL_EXTRACTION: {
        "title": "Proje Ruhu",
        "emoji": "✨",
        "intro": "Projenizin kimliğini keşfediyorum...",
        "description": (
            "Marka kişiliği, duygusal çerçeve ve görsel dil tercihlerinizi "
            "analiz ederek projenizin 'ruhunu' oluşturuyorum."
        ),
        "tip": "Her projenin benzersiz bir kişiliği vardır.",
    },
    InterviewPhase.CONTEXT_GATHERING: {
        "title": "Bağlam Toplama",
        "emoji": "🔍",
        "intro": "Projeniz hakkında daha fazla bilgi topluyorum...",
        "description": (
            "Mevcut tasarımlar, rakipler ve sektör beklentileri hakkında "
            "bilgi topluyorum. Bu bilgiler tasarım kararlarını yönlendirecek."
        ),
        "tip": "Bağlam bilgisi, daha uygun tasarımlar üretmemizi sağlar.",
    },
    InterviewPhase.DEEP_DIVE: {
        "title": "Derinlemesine Analiz",
        "emoji": "🎯",
        "intro": "Spesifik tercihlerinizi öğreniyorum...",
        "description": (
            "Tema, stil, renk paleti ve tipografi gibi detaylı tasarım "
            "tercihlerinizi belirliyorum."
        ),
        "tip": "Bu aşamadaki kararlar tasarımın görsel kimliğini belirler.",
    },
    InterviewPhase.VISUAL_EXPLORATION: {
        "title": "Görsel Keşif",
        "emoji": "🎨",
        "intro": "Görsel tercihlerinizi keşfediyorum...",
        "description": (
            "Animasyonlar, geçişler, ikonlar ve görsel efektler hakkında "
            "tercihlerinizi belirliyorum."
        ),
        "tip": "Görsel detaylar, kullanıcı deneyimini zenginleştirir.",
    },
    InterviewPhase.VALIDATION: {
        "title": "Doğrulama",
        "emoji": "✅",
        "intro": "Topladığım bilgileri doğruluyorum...",
        "description": (
            "Şu ana kadar öğrendiğim bilgileri size sunuyorum. "
            "Eksik veya yanlış bir şey varsa düzeltme şansınız var."
        ),
        "tip": "Doğrulama, hataları önlemenin en iyi yoludur.",
    },
    InterviewPhase.SYNTHESIS: {
        "title": "Sentez",
        "emoji": "🧩",
        "intro": "Tasarım kararlarını oluşturuyorum...",
        "description": (
            "Tüm bilgileri birleştirerek nihai tasarım kararlarını "
            "oluşturuyorum. Bu kararlar tasarım sürecini yönlendirecek."
        ),
        "tip": "Sentez aşaması, tüm bilgilerin birleştiği noktadır.",
    },
    InterviewPhase.COMPLETE: {
        "title": "Tamamlandı",
        "emoji": "🎉",
        "intro": "Interview tamamlandı!",
        "description": (
            "Tüm bilgiler toplandı ve tasarım kararları oluşturuldu. "
            "Artık tasarım sürecine geçebiliriz."
        ),
        "tip": "Harika! Şimdi tasarıma başlayabiliriz.",
    },
}


# =============================================================================
# TRANSITION MESSAGES
# =============================================================================

TRANSITION_MESSAGES: Dict[str, str] = {
    # Phase transitions
    "brief_to_soul": (
        "Brief analizi tamamlandı! Şimdi projenizin ruhunu keşfediyorum..."
    ),
    "soul_to_context": (
        "Proje kimliği belirlendi. Bağlam bilgilerini toplamaya geçiyorum..."
    ),
    "context_to_deep": (
        "Bağlam bilgileri toplandı. Detaylı tercihlerinizi öğrenmeye geçiyorum..."
    ),
    "context_to_validation": (
        "Yeterli bilgiye sahibim! Doğrulama aşamasına geçiyorum..."
    ),
    "deep_to_visual": (
        "Temel tercihler belirlendi. Görsel detaylara geçiyorum..."
    ),
    "deep_to_validation": (
        "Detaylı bilgiler toplandı. Doğrulama aşamasına geçiyorum..."
    ),
    "visual_to_validation": (
        "Görsel tercihler tamamlandı. Son doğrulamaya geçiyorum..."
    ),
    "validation_to_synthesis": (
        "Bilgiler doğrulandı! Tasarım kararlarını oluşturuyorum..."
    ),
    "validation_to_deep": (
        "Eksik bilgiler tespit ettim. Birkaç soru daha sormam gerekiyor..."
    ),
    "synthesis_to_complete": (
        "Tüm kararlar oluşturuldu! Interview başarıyla tamamlandı."
    ),

    # Skip messages
    "skipping_deep_dive": (
        "Yeterli bilgiye sahibim, detaylı sorular aşamasını atlıyorum."
    ),
    "skipping_visual": (
        "Görsel tercihleri brief'ten çıkarabildim, bu aşamayı atlıyorum."
    ),

    # Error/fallback messages
    "transition_failed": (
        "Bir sorun oluştu. Lütfen soruyu tekrar yanıtlayın."
    ),
    "returning_to_previous": (
        "Bir önceki aşamaya dönüyorum..."
    ),
}


# =============================================================================
# PROGRESS MESSAGES
# =============================================================================

PROGRESS_MESSAGES: Dict[str, str] = {
    # Progress indicators
    "progress_low": "Başlangıç aşamasındayız",
    "progress_medium": "İyi ilerliyoruz",
    "progress_high": "Neredeyse tamamlandı",
    "progress_complete": "Tamamlandı!",

    # Confidence indicators
    "confidence_low": "Daha fazla bilgiye ihtiyacım var",
    "confidence_medium": "İyi bir anlayışa sahibim",
    "confidence_high": "Projeyi çok iyi anlıyorum",

    # Time estimates
    "time_remaining_short": "Birkaç soru kaldı",
    "time_remaining_medium": "Yaklaşık 5 soru kaldı",
    "time_remaining_long": "10+ soru kaldı",

    # Encouragement
    "keep_going": "Harika gidiyorsunuz!",
    "almost_done": "Neredeyse bitti!",
    "great_answers": "Çok yararlı bilgiler, teşekkürler!",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_phase_prompt(
    phase: InterviewPhase,
    key: str = "intro",
) -> str:
    """
    Get a specific prompt for a phase.

    Args:
        phase: Interview phase
        key: Prompt key (title, emoji, intro, description, tip)

    Returns:
        Prompt text or empty string
    """
    phase_data = PHASE_PROMPTS.get(phase, {})
    return phase_data.get(key, "")


def get_transition_message(
    from_phase: InterviewPhase,
    to_phase: InterviewPhase,
) -> str:
    """
    Get transition message between phases.

    Args:
        from_phase: Source phase
        to_phase: Target phase

    Returns:
        Transition message
    """
    # Build key from phase names
    from_key = from_phase.value.replace("_", "").lower()
    to_key = to_phase.value.replace("_", "").lower()

    # Map to message keys
    key_map = {
        ("briefingestion", "soulextraction"): "brief_to_soul",
        ("soulextraction", "contextgathering"): "soul_to_context",
        ("contextgathering", "deepdive"): "context_to_deep",
        ("contextgathering", "validation"): "context_to_validation",
        ("deepdive", "visualexploration"): "deep_to_visual",
        ("deepdive", "validation"): "deep_to_validation",
        ("visualexploration", "validation"): "visual_to_validation",
        ("validation", "synthesis"): "validation_to_synthesis",
        ("validation", "deepdive"): "validation_to_deep",
        ("synthesis", "complete"): "synthesis_to_complete",
    }

    msg_key = key_map.get((from_key, to_key))
    if msg_key:
        return TRANSITION_MESSAGES.get(msg_key, "")

    # Default message
    to_prompt = PHASE_PROMPTS.get(to_phase, {})
    return to_prompt.get("intro", f"{to_phase.value} aşamasına geçiliyor...")


def get_progress_message(progress: float, confidence: float) -> str:
    """
    Get appropriate progress message.

    Args:
        progress: Overall progress (0.0 - 1.0)
        confidence: Confidence score (0.0 - 1.0)

    Returns:
        Combined progress message
    """
    # Progress message
    if progress < 0.3:
        prog_msg = PROGRESS_MESSAGES["progress_low"]
    elif progress < 0.7:
        prog_msg = PROGRESS_MESSAGES["progress_medium"]
    elif progress < 1.0:
        prog_msg = PROGRESS_MESSAGES["progress_high"]
    else:
        prog_msg = PROGRESS_MESSAGES["progress_complete"]

    # Confidence message
    if confidence < 0.4:
        conf_msg = PROGRESS_MESSAGES["confidence_low"]
    elif confidence < 0.7:
        conf_msg = PROGRESS_MESSAGES["confidence_medium"]
    else:
        conf_msg = PROGRESS_MESSAGES["confidence_high"]

    return f"{prog_msg}. {conf_msg}."
