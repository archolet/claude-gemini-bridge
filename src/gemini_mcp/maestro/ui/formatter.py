"""
MAESTRO Formatter - Rich formatting for MAESTRO outputs.

Provides formatted output for:
- Questions with category hints
- Decisions with confidence visualization
- Execution results with file listings
- Progress indicators

All output is MCP-compatible (dict format).
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from gemini_mcp.maestro.ui.summary import (
    MODE_DESCRIPTIONS,
    CONFIDENCE_LEVELS,
    _get_confidence_display,
    _generate_confidence_bar,
)

if TYPE_CHECKING:
    from gemini_mcp.maestro.models import MaestroDecision, Question


# Category tips in Turkish for user guidance
CATEGORY_TIPS: dict[str, str] = {
    "intent": "💡 Ne yapmak istediğinizi seçin",
    "scope": "📐 Tasarımın kapsamını belirleyin",
    "existing_context": "📁 Mevcut projelerinizi kullanabilirsiniz",
    "industry": "🏢 Hedef sektörü belirleyin",
    "theme_style": "🎨 Görsel stil tercihlerinizi seçin",
    "vibe_mood": "✨ Tasarımın ruh halini belirleyin",
    "content": "📝 İçerik bilgilerini girin",
    "technical": "⚙️ Teknik gereksinimleri belirtin",
    "accessibility": "♿ Erişilebilirlik ihtiyaçlarını seçin",
    "language": "🌍 İçerik dilini seçin",
}

# Parameter display labels in Turkish
PARAMETER_LABELS: dict[str, str] = {
    "component_type": "Component Tipi",
    "template_type": "Sayfa Şablonu",
    "section_type": "Section Tipi",
    "theme": "Tema",
    "content_language": "İçerik Dili",
    "dark_mode": "Dark Mode",
    "quality_target": "Kalite Hedefi",
    "use_trifecta": "Trifecta Pipeline",
    "project_context": "Proje Bağlamı",
    "vibe": "Tasarım Vibes",
    "industry": "Sektör",
}

# Question type icons
QUESTION_TYPE_ICONS: dict[str, str] = {
    "single_choice": "⚪",
    "multi_choice": "☑️",
    "slider": "🎚️",
    "text_input": "✏️",
    "color_picker": "🎨",
}


class MaestroFormatter:
    """
    Rich formatter for MAESTRO wizard outputs.

    Generates structured, MCP-compatible output with:
    - Visual indicators (emojis, progress bars)
    - Turkish localization
    - Consistent formatting across all output types

    Usage:
        formatter = MaestroFormatter()
        formatted = formatter.format_question(question)
        formatted = formatter.format_decision(decision)
        formatted = formatter.format_execution_result(result)
    """

    def format_question(
        self,
        question: "Question | dict[str, Any]",
        current_step: int = 0,
        total_steps: int = 0,
    ) -> dict[str, Any]:
        """
        Format a question for display.

        Args:
            question: Question object or dict to format
            current_step: Current question number (1-based)
            total_steps: Total expected questions

        Returns:
            Formatted dict with question display data
        """
        # Handle dict input
        if isinstance(question, dict):
            return self._format_question_dict(question, current_step, total_steps)

        # Get category tip
        category_value = (
            question.category.value
            if hasattr(question.category, "value")
            else str(question.category)
        )
        tip = CATEGORY_TIPS.get(category_value, "")

        # Get question type icon
        qtype_value = (
            question.question_type.value
            if hasattr(question.question_type, "value")
            else str(question.question_type)
        )
        type_icon = QUESTION_TYPE_ICONS.get(qtype_value, "❓")

        # Format options
        formatted_options = []
        for opt in question.options:
            formatted_options.append({
                "id": opt.id,
                "label": opt.label,
                "description": opt.description or "",
                "display": f"▸ {opt.label}",
            })

        result: dict[str, Any] = {
            "formatted": True,
            "type": "question",
            "question_id": question.id,
            "header": f"{type_icon} {question.text}",
            "text": question.text,
            "category": category_value,
            "question_type": qtype_value,
            "options": formatted_options,
            "tip": tip,
        }

        # Add progress if available
        if total_steps > 0:
            progress = current_step / total_steps
            result["progress"] = {
                "current": current_step,
                "total": total_steps,
                "percent": f"%{int(progress * 100)}",
                "bar": _generate_confidence_bar(progress),
                "message": f"Soru {current_step}/{total_steps}",
            }

        return result

    def format_decision(
        self,
        decision: "MaestroDecision",
        include_alternatives: bool = True,
        compact: bool = False,
    ) -> dict[str, Any]:
        """
        Format a decision summary for display.

        Args:
            decision: MaestroDecision object
            include_alternatives: Include alternative mode suggestions
            compact: Use compact format (less detail)

        Returns:
            Formatted dict with decision display data
        """
        # Get confidence display
        icon, label = _get_confidence_display(decision.confidence)
        mode_name = MODE_DESCRIPTIONS.get(decision.mode, decision.mode)

        result: dict[str, Any] = {
            "formatted": True,
            "type": "decision",
            "header": f"🎯 Karar: {mode_name}",
            "mode": {
                "id": decision.mode,
                "display_name": mode_name,
            },
            "confidence": {
                "value": round(decision.confidence, 2),
                "percent": f"%{int(decision.confidence * 100)}",
                "icon": icon,
                "label": label,
            },
        }

        if not compact:
            result["confidence"]["bar"] = _generate_confidence_bar(decision.confidence)
            result["reasoning"] = decision.reasoning
            result["parameters"] = self._format_parameters(decision.parameters)

        # Add alternatives
        if include_alternatives and decision.alternatives:
            result["alternatives"] = [
                {
                    "mode": alt.get("mode", ""),
                    "display_name": MODE_DESCRIPTIONS.get(
                        alt.get("mode", ""), alt.get("mode", "")
                    ),
                    "reason": alt.get("reason", ""),
                }
                for alt in decision.alternatives[:3]
            ]

        return result

    def format_execution_result(
        self,
        result: dict[str, Any],
        include_preview: bool = True,
        preview_length: int = 500,
    ) -> dict[str, Any]:
        """
        Format execution result for display.

        Args:
            result: Execution result dict
            include_preview: Include HTML preview
            preview_length: Max length for HTML preview

        Returns:
            Formatted dict with execution display data
        """
        # Handle error case
        if result.get("error"):
            return {
                "formatted": True,
                "type": "error",
                "status": "failed",
                "header": "❌ Hata Oluştu",
                "error": {
                    "message": result["error"],
                    "mode": result.get("mode", "unknown"),
                },
                "suggestion": "Parametreleri kontrol edip tekrar deneyin",
            }

        mode = result.get("mode", "unknown")
        mode_name = MODE_DESCRIPTIONS.get(mode, mode)

        formatted: dict[str, Any] = {
            "formatted": True,
            "type": "success",
            "status": "complete",
            "header": f"✅ {mode_name} Tamamlandı",
            "mode": {
                "id": mode,
                "display_name": mode_name,
            },
        }

        # Pipeline info
        if result.get("trifecta_enabled"):
            formatted["pipeline"] = {
                "type": "Trifecta",
                "enabled": True,
                "quality_target": result.get("quality_target", "production"),
                "agents_executed": result.get("agents_executed", []),
            }
        else:
            formatted["pipeline"] = {
                "type": "Direct",
                "enabled": False,
            }

        # Generated files
        files = self._list_generated_files(result)
        if files:
            formatted["outputs"] = {
                "files": files,
                "total_files": len(files),
            }

        # HTML preview
        if include_preview and result.get("html"):
            html = result["html"]
            formatted["preview"] = {
                "html": html[:preview_length] + "..." if len(html) > preview_length else html,
                "full_length": len(html),
                "truncated": len(html) > preview_length,
            }

        # Design notes
        if result.get("design_notes"):
            formatted["design_notes"] = result["design_notes"]

        return formatted

    def format_progress(
        self,
        stage: str,
        progress: float,
        message: str = "",
    ) -> dict[str, Any]:
        """
        Format a progress update.

        Args:
            stage: Current stage name
            progress: Progress value (0.0-1.0)
            message: Optional progress message

        Returns:
            Formatted progress dict
        """
        return {
            "formatted": True,
            "type": "progress",
            "stage": stage,
            "progress": round(progress, 2),
            "percent": f"%{int(progress * 100)}",
            "bar": _generate_confidence_bar(progress),
            "message": message or f"{stage} ({int(progress * 100)}%)",
        }

    def format_session_summary(
        self,
        session_metrics: dict[str, Any],
        cost_breakdown: dict[str, Any] | None = None,
        quality_score: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Format a complete session summary.

        Args:
            session_metrics: Session metrics dict
            cost_breakdown: Optional cost breakdown dict
            quality_score: Optional quality score dict

        Returns:
            Formatted session summary
        """
        summary: dict[str, Any] = {
            "formatted": True,
            "type": "session_summary",
            "header": "📊 MAESTRO Oturum Özeti",
        }

        # Duration
        duration = session_metrics.get("duration_seconds", 0)
        summary["duration"] = {
            "seconds": duration,
            "display": f"{duration:.1f}s" if duration < 60 else f"{duration/60:.1f}m",
        }

        # Questions
        questions = session_metrics.get("questions", {})
        summary["questions"] = {
            "asked": questions.get("asked", 0),
            "answered": questions.get("answered", 0),
            "completion_rate": f"%{int(questions.get('completion_rate', 0) * 100)}",
        }

        # Cost
        if cost_breakdown:
            cost_usd = cost_breakdown.get("cost_usd", {})
            summary["cost"] = {
                "total_usd": f"${cost_usd.get('total', 0):.4f}",
                "tokens": cost_breakdown.get("tokens", {}),
            }

        # Quality
        if quality_score:
            weighted_avg = quality_score.get("weighted_average", 0)
            summary["quality"] = {
                "score": round(weighted_avg, 2),
                "display": f"{weighted_avg:.1f}/10",
                "meets_production": quality_score.get("meets_production", False),
                "status_icon": "✅" if weighted_avg >= 7.0 else "🟡" if weighted_avg >= 6.0 else "🔴",
            }

        return summary

    def _format_parameters(self, params: dict[str, Any]) -> list[dict[str, str]]:
        """Format parameters for display."""
        display_params = []

        for key, value in params.items():
            if key in PARAMETER_LABELS:
                # Format boolean values
                if isinstance(value, bool):
                    formatted_value = "Aktif" if value else "Pasif"
                else:
                    formatted_value = str(value)

                display_params.append({
                    "key": key,
                    "label": PARAMETER_LABELS[key],
                    "value": formatted_value,
                })

        return display_params

    def _format_question_dict(
        self,
        question: dict[str, Any],
        current_step: int = 0,
        total_steps: int = 0,
    ) -> dict[str, Any]:
        """Format a question dict for display (when Question object not available)."""
        # Get category tip
        category_value = question.get("category", "")
        tip = CATEGORY_TIPS.get(category_value, "")

        # Get question type icon
        qtype_value = question.get("question_type", "single_choice")
        type_icon = QUESTION_TYPE_ICONS.get(qtype_value, "❓")

        # Format options
        formatted_options = []
        for opt in question.get("options", []):
            if isinstance(opt, dict):
                formatted_options.append({
                    "id": opt.get("id", ""),
                    "label": opt.get("label", ""),
                    "description": opt.get("description", ""),
                    "display": f"▸ {opt.get('label', '')}",
                })
            else:
                # Handle Option objects if passed
                formatted_options.append({
                    "id": getattr(opt, "id", ""),
                    "label": getattr(opt, "label", ""),
                    "description": getattr(opt, "description", "") or "",
                    "display": f"▸ {getattr(opt, 'label', '')}",
                })

        result: dict[str, Any] = {
            "formatted": True,
            "type": "question",
            "question_id": question.get("id", ""),
            "header": f"{type_icon} {question.get('text', '')}",
            "text": question.get("text", ""),
            "category": category_value,
            "question_type": qtype_value,
            "options": formatted_options,
            "tip": tip,
        }

        # Add progress if available
        if total_steps > 0:
            progress = current_step / total_steps
            result["progress"] = {
                "current": current_step,
                "total": total_steps,
                "percent": f"%{int(progress * 100)}",
                "bar": _generate_confidence_bar(progress),
                "message": f"Soru {current_step}/{total_steps}",
            }

        return result

    def _list_generated_files(self, result: dict[str, Any]) -> list[dict[str, Any]]:
        """List generated files with metadata."""
        files = []

        if result.get("html"):
            html_length = len(result["html"])
            files.append({
                "type": "html",
                "name": "index.html",
                "size": f"{html_length:,} karakter",
                "icon": "📄",
            })

        if result.get("css_output"):
            css_length = len(result["css_output"])
            files.append({
                "type": "css",
                "name": "styles.css",
                "size": f"{css_length:,} karakter",
                "icon": "🎨",
            })

        if result.get("js_output"):
            js_length = len(result["js_output"])
            files.append({
                "type": "js",
                "name": "script.js",
                "size": f"{js_length:,} karakter",
                "icon": "⚡",
            })

        return files
