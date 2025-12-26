"""
Summary Generators - Creates decision and execution summaries.

Provides structured summaries for:
- Decision outcomes with confidence visualization
- Execution results with cost and quality metrics
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from gemini_mcp.maestro.models import MaestroDecision

# Mode descriptions in Turkish
MODE_DESCRIPTIONS: dict[str, str] = {
    "design_frontend": "Component Tasarımı",
    "design_page": "Sayfa Tasarımı",
    "design_section": "Section Tasarımı",
    "refine_frontend": "Tasarım İyileştirme",
    "replace_section_in_page": "Section Değiştirme",
    "design_from_reference": "Referanstan Tasarım",
}

# Confidence level descriptions
CONFIDENCE_LEVELS: dict[float, tuple[str, str]] = {
    0.90: ("🟢", "Yüksek Güven"),
    0.75: ("🟡", "Orta Güven"),
    0.60: ("🟠", "Düşük Güven"),
    0.00: ("🔴", "Çok Düşük Güven"),
}


def _get_confidence_display(confidence: float) -> tuple[str, str]:
    """Get confidence icon and label based on value."""
    for threshold, (icon, label) in sorted(
        CONFIDENCE_LEVELS.items(), reverse=True
    ):
        if confidence >= threshold:
            return icon, label
    return "🔴", "Çok Düşük Güven"


def _generate_confidence_bar(confidence: float, width: int = 20) -> str:
    """Generate a text-based confidence bar."""
    filled = int(confidence * width)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}] %{int(confidence * 100)}"


def generate_decision_summary(
    decision: "MaestroDecision",
    session_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate a comprehensive decision summary.

    Args:
        decision: MaestroDecision with mode, confidence, parameters
        session_metrics: Optional session metrics dict

    Returns:
        Dict with structured summary data
    """
    icon, label = _get_confidence_display(decision.confidence)
    mode_name = MODE_DESCRIPTIONS.get(decision.mode, decision.mode)

    summary: dict[str, Any] = {
        "type": "decision_summary",
        "title": "MAESTRO Karar Özeti",
        "mode": {
            "selected": decision.mode,
            "display_name": mode_name,
            "confidence": round(decision.confidence, 2),
            "confidence_percent": f"%{int(decision.confidence * 100)}",
            "confidence_icon": icon,
            "confidence_label": label,
            "confidence_bar": _generate_confidence_bar(decision.confidence),
        },
        "parameters": _format_parameters(decision.parameters),
        "reasoning": decision.reasoning,
    }

    # Add alternatives if available
    if decision.alternatives:
        summary["alternatives"] = [
            {
                "mode": alt.get("mode", ""),
                "display_name": MODE_DESCRIPTIONS.get(
                    alt.get("mode", ""), alt.get("mode", "")
                ),
                "reason": alt.get("reason", ""),
            }
            for alt in decision.alternatives[:3]
        ]

    # Add session info if available
    if session_metrics:
        questions = session_metrics.get("questions", {})
        summary["session"] = {
            "duration": f"{session_metrics.get('duration_seconds', 0):.1f}s",
            "questions_asked": questions.get("asked", 0),
            "questions_answered": questions.get("answered", 0),
            "completion_rate": f"%{int(questions.get('completion_rate', 0) * 100)}",
            "avg_response_time": f"{questions.get('avg_response_time', 0):.2f}s",
        }

    return summary


def _format_parameters(params: dict[str, Any]) -> list[dict[str, str]]:
    """Format parameters for display."""
    key_labels = {
        "component_type": "Component Tipi",
        "template_type": "Sayfa Şablonu",
        "section_type": "Section Tipi",
        "theme": "Tema",
        "content_language": "İçerik Dili",
        "dark_mode": "Dark Mode",
        "quality_target": "Kalite Hedefi",
        "use_trifecta": "Trifecta",
        "project_context": "Proje Bağlamı",
    }

    display_params = []
    for key, value in params.items():
        if key in key_labels:
            # Format boolean values
            if isinstance(value, bool):
                formatted_value = "Aktif" if value else "Pasif"
            else:
                formatted_value = str(value)

            display_params.append({
                "key": key,
                "label": key_labels[key],
                "value": formatted_value,
            })

    return display_params


def generate_execution_summary(
    result: dict[str, Any],
    cost_breakdown: dict[str, Any] | None = None,
    quality_score: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate execution result summary.

    Args:
        result: Execution result dict with html, mode, etc.
        cost_breakdown: Optional CostBreakdown.to_dict() output
        quality_score: Optional QualityScore.to_dict() output

    Returns:
        Dict with structured execution summary
    """
    is_success = not result.get("error")
    mode = result.get("mode", "unknown")
    mode_name = MODE_DESCRIPTIONS.get(mode, mode)

    summary: dict[str, Any] = {
        "type": "execution_summary",
        "title": "MAESTRO Çalıştırma Özeti",
        "status": "success" if is_success else "error",
        "status_icon": "✅" if is_success else "❌",
        "mode": {
            "selected": mode,
            "display_name": mode_name,
        },
    }

    # Error details
    if not is_success:
        summary["error"] = {
            "message": result.get("error", "Bilinmeyen hata"),
            "suggestion": "Parametreleri kontrol edip tekrar deneyin",
        }
        return summary

    # Pipeline info
    if result.get("trifecta_enabled"):
        summary["pipeline"] = {
            "type": "Trifecta",
            "enabled": True,
            "quality_target": result.get("quality_target", "production"),
            "pipeline_type": result.get("pipeline_type", ""),
            "agents_executed": result.get("agents_executed", []),
        }
    else:
        summary["pipeline"] = {
            "type": "Direct",
            "enabled": False,
        }

    # Output files
    files = []
    if result.get("html"):
        html_length = len(result["html"])
        files.append({
            "type": "html",
            "name": "index.html",
            "size": f"{html_length:,} karakter",
        })
    if result.get("css_output"):
        css_length = len(result["css_output"])
        files.append({
            "type": "css",
            "name": "styles.css",
            "size": f"{css_length:,} karakter",
        })
    if result.get("js_output"):
        js_length = len(result["js_output"])
        files.append({
            "type": "js",
            "name": "script.js",
            "size": f"{js_length:,} karakter",
        })

    if files:
        summary["outputs"] = {
            "files": files,
            "total_files": len(files),
        }

    # Cost breakdown
    if cost_breakdown:
        tokens = cost_breakdown.get("tokens", {})
        cost_usd = cost_breakdown.get("cost_usd", {})

        summary["cost"] = {
            "tokens": {
                "input": f"{tokens.get('input', 0):,}",
                "output": f"{tokens.get('output', 0):,}",
                "thinking": f"{tokens.get('thinking', 0):,}",
                "total": f"{tokens.get('total', 0):,}",
            },
            "usd": {
                "total": f"${cost_usd.get('total', 0):.4f}",
                "breakdown": (
                    f"Input: ${cost_usd.get('input', 0):.4f}, "
                    f"Output: ${cost_usd.get('output', 0):.4f}, "
                    f"Thinking: ${cost_usd.get('thinking', 0):.4f}"
                ),
            },
        }

    # Quality score
    if quality_score:
        dimensions = quality_score.get("dimensions", {})
        weighted_avg = quality_score.get("weighted_average", 0)

        # Determine quality status
        if weighted_avg >= 8.0:
            quality_status = ("🏆", "Mükemmel")
        elif weighted_avg >= 7.0:
            quality_status = ("✅", "Prodüksiyona Hazır")
        elif weighted_avg >= 6.0:
            quality_status = ("🟡", "İyileştirme Gerekli")
        else:
            quality_status = ("🔴", "Yetersiz")

        summary["quality"] = {
            "weighted_average": round(weighted_avg, 2),
            "status_icon": quality_status[0],
            "status_label": quality_status[1],
            "meets_production": quality_score.get("meets_production", False),
            "dimensions": {
                "layout": f"{dimensions.get('layout', 0):.1f}/10 (25%)",
                "accessibility": f"{dimensions.get('accessibility', 0):.1f}/10 (25%)",
                "color": f"{dimensions.get('color', 0):.1f}/10 (20%)",
                "typography": f"{dimensions.get('typography', 0):.1f}/10 (15%)",
                "interaction": f"{dimensions.get('interaction', 0):.1f}/10 (15%)",
            },
            "lowest_dimension": quality_score.get("lowest", ""),
            "highest_dimension": quality_score.get("highest", ""),
        }

    # Design notes
    if result.get("design_notes"):
        summary["design_notes"] = result["design_notes"]

    return summary


def generate_session_complete_summary(
    decision_summary: dict[str, Any],
    execution_summary: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate a complete session summary combining decision and execution.

    Args:
        decision_summary: Output from generate_decision_summary()
        execution_summary: Output from generate_execution_summary()

    Returns:
        Dict with combined session summary
    """
    is_success = execution_summary.get("status") == "success"

    return {
        "type": "session_complete_summary",
        "title": "MAESTRO Oturum Özeti",
        "status": "complete" if is_success else "failed",
        "status_icon": "🎉" if is_success else "❌",
        "headline": (
            f"{decision_summary['mode']['display_name']} başarıyla tamamlandı"
            if is_success
            else f"{decision_summary['mode']['display_name']} başarısız oldu"
        ),
        "decision": {
            "mode": decision_summary["mode"]["display_name"],
            "confidence": decision_summary["mode"]["confidence_percent"],
        },
        "execution": {
            "pipeline": execution_summary.get("pipeline", {}).get("type", "Direct"),
            "files_generated": execution_summary.get("outputs", {}).get("total_files", 0),
        },
        "cost": execution_summary.get("cost", {}).get("usd", {}).get("total", "N/A"),
        "quality": execution_summary.get("quality", {}).get("weighted_average", "N/A"),
        "full_decision": decision_summary,
        "full_execution": execution_summary,
    }
