"""
MAESTRO Turkish Feedback Templates - Phase 4

Validation, error, and success messages for user feedback.
All messages are in Turkish for native UX.
"""

from typing import Dict, Optional


# =============================================================================
# VALIDATION MESSAGES
# =============================================================================

VALIDATION_MESSAGES: Dict[str, Dict[str, str]] = {
    # Field validation
    "required_field": {
        "message": "Bu alan zorunludur",
        "type": "error",
    },
    "invalid_format": {
        "message": "Geçersiz format",
        "type": "error",
    },
    "invalid_hex_color": {
        "message": "Geçersiz renk kodu. Lütfen #RRGGBB formatında girin (örn: #E11D48)",
        "type": "error",
    },
    "invalid_url": {
        "message": "Geçersiz URL formatı. Lütfen geçerli bir web adresi girin",
        "type": "error",
    },
    "text_too_short": {
        "message": "Metin çok kısa. En az {min_length} karakter girin",
        "type": "warning",
    },
    "text_too_long": {
        "message": "Metin çok uzun. Maksimum {max_length} karakter",
        "type": "warning",
    },

    # Selection validation
    "no_selection": {
        "message": "Lütfen bir seçenek seçin",
        "type": "error",
    },
    "invalid_selection": {
        "message": "Geçersiz seçenek. Lütfen listeden birini seçin",
        "type": "error",
    },
    "multi_select_min": {
        "message": "En az {min_count} seçenek seçmelisiniz",
        "type": "error",
    },
    "multi_select_max": {
        "message": "En fazla {max_count} seçenek seçebilirsiniz",
        "type": "warning",
    },

    # Confirmation validation
    "confirmation_required": {
        "message": "Devam etmek için onaylayın",
        "type": "info",
    },
    "changes_unsaved": {
        "message": "Kaydedilmemiş değişiklikleriniz var",
        "type": "warning",
    },

    # Soul validation
    "low_confidence": {
        "message": "Brief'ten yeterli bilgi çıkarılamadı. Daha fazla detay ekleyin",
        "type": "warning",
    },
    "missing_critical_info": {
        "message": "Kritik bilgi eksik: {missing_fields}",
        "type": "error",
    },
    "gaps_detected": {
        "message": "{gap_count} eksik alan tespit edildi. Ek sorular sorulacak",
        "type": "info",
    },
}


# =============================================================================
# ERROR MESSAGES
# =============================================================================

ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    # General errors
    "general_error": {
        "title": "Bir Hata Oluştu",
        "message": "Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.",
        "action": "Tekrar Dene",
    },
    "timeout_error": {
        "title": "Zaman Aşımı",
        "message": "İşlem zaman aşımına uğradı. Lütfen tekrar deneyin.",
        "action": "Tekrar Dene",
    },
    "network_error": {
        "title": "Bağlantı Hatası",
        "message": "Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.",
        "action": "Bağlantıyı Kontrol Et",
    },

    # Session errors
    "session_expired": {
        "title": "Oturum Sona Erdi",
        "message": "Oturumunuz sona erdi. Lütfen yeni bir oturum başlatın.",
        "action": "Yeni Oturum",
    },
    "session_not_found": {
        "title": "Oturum Bulunamadı",
        "message": "Belirtilen oturum bulunamadı.",
        "action": "Yeni Oturum Başlat",
    },
    "session_locked": {
        "title": "Oturum Kilitli",
        "message": "Bu oturum başka bir işlem tarafından kullanılıyor.",
        "action": "Bekle",
    },

    # Interview errors
    "invalid_phase": {
        "title": "Geçersiz Aşama",
        "message": "Bu aşamada bu işlem yapılamaz.",
        "action": "Geri Dön",
    },
    "transition_failed": {
        "title": "Geçiş Başarısız",
        "message": "Bir sonraki aşamaya geçilemedi. Eksik bilgiler var.",
        "action": "Eksikleri Tamamla",
    },
    "extraction_failed": {
        "title": "Analiz Başarısız",
        "message": "Brief analizi başarısız oldu. Lütfen brief'i kontrol edin.",
        "action": "Brief'i Düzenle",
    },

    # Input errors
    "invalid_input": {
        "title": "Geçersiz Giriş",
        "message": "Girdiğiniz değer geçerli değil.",
        "action": "Düzelt",
    },
    "file_too_large": {
        "title": "Dosya Çok Büyük",
        "message": "Dosya boyutu maksimum limiti aşıyor ({max_size}).",
        "action": "Daha Küçük Dosya Seç",
    },
    "unsupported_format": {
        "title": "Desteklenmeyen Format",
        "message": "Bu dosya formatı desteklenmiyor.",
        "action": "Farklı Format Kullan",
    },

    # API errors
    "api_error": {
        "title": "API Hatası",
        "message": "Gemini API'den yanıt alınamadı.",
        "action": "Tekrar Dene",
    },
    "rate_limit": {
        "title": "İstek Limiti",
        "message": "Çok fazla istek gönderildi. Lütfen bekleyin.",
        "action": "Bekle ve Tekrar Dene",
    },
    "quota_exceeded": {
        "title": "Kota Aşıldı",
        "message": "API kotası doldu. Daha sonra tekrar deneyin.",
        "action": "Sonra Dene",
    },
}


# =============================================================================
# SUCCESS MESSAGES
# =============================================================================

SUCCESS_MESSAGES: Dict[str, Dict[str, str]] = {
    # General success
    "operation_complete": {
        "title": "İşlem Tamamlandı",
        "message": "İşlem başarıyla tamamlandı.",
        "emoji": "✅",
    },
    "saved": {
        "title": "Kaydedildi",
        "message": "Değişiklikler başarıyla kaydedildi.",
        "emoji": "💾",
    },

    # Interview success
    "interview_started": {
        "title": "Interview Başladı",
        "message": "Tasarım yolculuğunuza hoş geldiniz!",
        "emoji": "🎉",
    },
    "interview_complete": {
        "title": "Interview Tamamlandı",
        "message": "Tüm bilgiler toplandı. Tasarıma hazırız!",
        "emoji": "🎊",
    },
    "phase_complete": {
        "title": "Aşama Tamamlandı",
        "message": "{phase_name} aşaması başarıyla tamamlandı.",
        "emoji": "✨",
    },

    # Soul extraction success
    "soul_extracted": {
        "title": "Proje Ruhu Çıkarıldı",
        "message": "Projenizin kimliği başarıyla belirlendi.",
        "emoji": "✨",
    },
    "high_confidence": {
        "title": "Yüksek Güven",
        "message": "Brief'ten zengin bilgiler çıkarıldı ({confidence}% güven).",
        "emoji": "🎯",
    },
    "gaps_filled": {
        "title": "Eksikler Tamamlandı",
        "message": "Tüm eksik bilgiler başarıyla toplandı.",
        "emoji": "🧩",
    },

    # Design success
    "design_ready": {
        "title": "Tasarım Hazır",
        "message": "Tasarım parametreleri oluşturuldu. Üretim başlayabilir!",
        "emoji": "🚀",
    },
    "design_generated": {
        "title": "Tasarım Üretildi",
        "message": "Tasarım başarıyla üretildi ve kaydedildi.",
        "emoji": "🎨",
    },

    # Validation success
    "validation_passed": {
        "title": "Doğrulama Başarılı",
        "message": "Tüm bilgiler doğrulandı.",
        "emoji": "✅",
    },
    "changes_confirmed": {
        "title": "Değişiklikler Onaylandı",
        "message": "Tercihleriniz kaydedildi.",
        "emoji": "👍",
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_validation_message(
    key: str,
    context: Optional[Dict[str, any]] = None,
) -> Dict[str, str]:
    """
    Get formatted validation message.

    Args:
        key: Validation message key
        context: Optional context for formatting

    Returns:
        Validation message dict
    """
    template = VALIDATION_MESSAGES.get(key, {
        "message": "Doğrulama hatası",
        "type": "error",
    })

    result = template.copy()
    if context:
        try:
            result["message"] = result["message"].format(**context)
        except KeyError:
            pass

    return result


def get_error_message(
    key: str,
    context: Optional[Dict[str, any]] = None,
) -> Dict[str, str]:
    """
    Get formatted error message.

    Args:
        key: Error message key
        context: Optional context for formatting

    Returns:
        Error message dict
    """
    template = ERROR_MESSAGES.get(key, {
        "title": "Hata",
        "message": "Beklenmeyen bir hata oluştu.",
        "action": "Tekrar Dene",
    })

    result = template.copy()
    if context:
        try:
            result["message"] = result["message"].format(**context)
        except KeyError:
            pass

    return result


def get_success_message(
    key: str,
    context: Optional[Dict[str, any]] = None,
) -> Dict[str, str]:
    """
    Get formatted success message.

    Args:
        key: Success message key
        context: Optional context for formatting

    Returns:
        Success message dict
    """
    template = SUCCESS_MESSAGES.get(key, {
        "title": "Başarılı",
        "message": "İşlem tamamlandı.",
        "emoji": "✅",
    })

    result = template.copy()
    if context:
        try:
            result["message"] = result["message"].format(**context)
        except KeyError:
            pass

    return result


def format_error_for_display(
    error_key: str,
    include_action: bool = True,
    context: Optional[Dict[str, any]] = None,
) -> str:
    """
    Format error message for UI display.

    Args:
        error_key: Error message key
        include_action: Whether to include action suggestion
        context: Optional context for formatting

    Returns:
        Formatted error string
    """
    error = get_error_message(error_key, context)
    result = f"❌ {error['title']}: {error['message']}"

    if include_action and error.get("action"):
        result += f" → {error['action']}"

    return result


def format_success_for_display(
    success_key: str,
    context: Optional[Dict[str, any]] = None,
) -> str:
    """
    Format success message for UI display.

    Args:
        success_key: Success message key
        context: Optional context for formatting

    Returns:
        Formatted success string
    """
    success = get_success_message(success_key, context)
    emoji = success.get("emoji", "✅")
    return f"{emoji} {success['title']}: {success['message']}"
