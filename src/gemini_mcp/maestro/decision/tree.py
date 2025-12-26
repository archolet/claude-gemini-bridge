"""
MAESTRO Decision Tree - Phase 3

AI-powered decision tree for selecting design mode.
Uses lambda-based MODE_RULES combined with weighted scoring
and optional Gemini reasoning for edge cases.

Pattern Reference: interview/flow_controller.py (Lambda Rules)
"""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any, Callable

from gemini_mcp.maestro.decision.context_analyzer import ContextAnalyzer
from gemini_mcp.maestro.decision.models import (
    ContextAnalysis,
    DecisionAnalysis,
    DecisionScores,
    EnrichedContext,
)
from gemini_mcp.maestro.models import InterviewState, MaestroDecision

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient

logger = logging.getLogger(__name__)


# Type alias for mode rule lambda
ModeRule = Callable[[EnrichedContext], bool]


class DecisionTree:
    """
    AI-powered decision tree for selecting design mode.

    Uses lambda-based MODE_RULES (similar to FlowController pattern)
    combined with weighted scoring and optional Gemini reasoning.

    Features:
    - Priority-based rule evaluation
    - 6-dimension confidence scoring
    - Gemini fallback for low-confidence decisions
    - Automatic parameter extraction

    Usage:
        tree = DecisionTree(client=gemini_client)
        decision = await tree.make_decision(
            state=interview_state,
            previous_html="<div>...</div>",
            project_context="B2B SaaS dashboard"
        )
    """

    # =========================================================================
    # MODE SELECTION RULES
    # =========================================================================

    # Mode rules: mode → (condition_lambda, priority)
    # Higher priority = evaluated first
    # Rules are checked in priority order, first match wins
    MODE_RULES: dict[str, tuple[ModeRule, int]] = {
        # === REFINEMENT MODES (highest priority - user has existing context) ===
        "refine_frontend": (
            lambda ctx: (
                ctx.html_analysis.has_html
                and ctx.get_answer("q_existing_action") == "opt_refine"
            ),
            100,
        ),
        "replace_section_in_page": (
            lambda ctx: (
                ctx.html_analysis.has_html
                and ctx.get_answer("q_existing_action") == "opt_replace_section"
            ),
            95,
        ),
        # === REFERENCE-BASED DESIGN ===
        "design_from_reference": (
            lambda ctx: ctx.get_answer("q_intent_main") == "opt_from_reference",
            90,
        ),
        # === SCOPE-BASED MODES ===
        "design_page": (
            lambda ctx: (
                ctx.get_answer("q_intent_main") == "opt_new_design"
                and ctx.get_answer("q_scope_type") == "opt_full_page"
            ),
            80,
        ),
        "design_section": (
            lambda ctx: (
                (
                    ctx.get_answer("q_intent_main") == "opt_new_design"
                    and ctx.get_answer("q_scope_type") == "opt_section"
                )
                or (
                    ctx.html_analysis.has_html
                    and ctx.get_answer("q_existing_action") == "opt_match_style"
                )
            ),
            70,
        ),
        # === DEFAULT FALLBACK ===
        "design_frontend": (
            lambda ctx: True,  # Always matches as fallback
            0,
        ),
    }

    # =========================================================================
    # PARAMETER EXTRACTORS
    # =========================================================================

    # Mode-specific parameter extraction
    PARAMETER_EXTRACTORS: dict[str, Callable[[EnrichedContext], dict[str, Any]]] = {
        "design_page": lambda ctx: {
            "template_type": _map_page_type(ctx.get_answer("q_page_type")),
        },
        "design_section": lambda ctx: {
            "section_type": _map_section_type(ctx.get_answer("q_section_type")),
        },
        "design_frontend": lambda ctx: {
            "component_type": _map_component_type(ctx.get_answer("q_component_type")),
        },
        "refine_frontend": lambda ctx: {},
        "replace_section_in_page": lambda ctx: {
            "section_type": _map_section_type(ctx.get_answer("q_section_type")),
        },
        "design_from_reference": lambda ctx: {},
    }

    # =========================================================================
    # CONFIDENCE THRESHOLDS
    # =========================================================================

    HIGH_CONFIDENCE_THRESHOLD = 0.85
    GEMINI_TRIGGER_THRESHOLD = 0.70

    def __init__(self, client: "GeminiClient | None" = None) -> None:
        """
        Initialize DecisionTree.

        Args:
            client: Optional GeminiClient for AI-powered reasoning.
                   If None, Gemini reasoning is disabled.
        """
        self.client = client
        self.context_analyzer = ContextAnalyzer()

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    async def make_decision(
        self,
        state: InterviewState,
        previous_html: str | None = None,
        project_context: str = "",
    ) -> MaestroDecision:
        """
        Make a design mode decision based on interview answers.

        Args:
            state: Interview state with collected answers
            previous_html: Optional existing HTML for context analysis
            project_context: Optional project description

        Returns:
            MaestroDecision with selected mode and parameters
        """
        logger.info("[DecisionTree] Making decision...")

        # Build enriched context
        html_analysis = self.context_analyzer.analyze(previous_html)
        enriched = EnrichedContext(
            answers=self._state_to_answer_dict(state),
            html_analysis=html_analysis,
            project_context=project_context,
        )

        logger.debug(
            f"[DecisionTree] Context: {enriched.answer_count} answers, "
            f"html={html_analysis.has_html}"
        )

        # Evaluate rules and select mode
        mode = self._evaluate_rules(enriched)
        logger.info(f"[DecisionTree] Rule-based selection: {mode}")

        # Calculate confidence scores
        scores = self._calculate_scores(mode, enriched)
        confidence = scores.overall

        logger.info(f"[DecisionTree] Confidence: {confidence:.2f}")

        # Use Gemini for low-confidence decisions
        used_gemini = False
        reasoning = self._build_basic_reasoning(mode, enriched, scores)

        if scores.needs_gemini() and self.client:
            logger.info(
                f"[DecisionTree] Low confidence ({confidence:.2f}), "
                "using Gemini for reasoning"
            )
            gemini_result = await self._gemini_reasoning(enriched, mode, scores)
            if gemini_result:
                # Gemini may suggest a different mode
                if gemini_result.get("mode") and gemini_result["mode"] != mode:
                    logger.info(
                        f"[DecisionTree] Gemini suggests: {gemini_result['mode']}"
                    )
                    mode = gemini_result["mode"]
                reasoning = gemini_result.get("reasoning", reasoning)
                used_gemini = True

        # Extract parameters for selected mode
        parameters = self._extract_parameters(mode, enriched)

        # Add common parameters (theme, dark_mode, language, etc.)
        parameters.update(self._extract_common_parameters(enriched))

        # Add HTML context if available
        if html_analysis.has_html:
            if mode == "refine_frontend":
                parameters["previous_html"] = previous_html
            elif mode == "replace_section_in_page":
                parameters["page_html"] = previous_html
            elif mode == "design_section" and enriched.get_answer("q_existing_action"):
                parameters["previous_html"] = previous_html
            # Add design tokens for style matching
            parameters["design_tokens"] = json.dumps(html_analysis.to_design_tokens())

        # Build alternatives
        alternatives = self._get_alternatives(mode)

        decision = MaestroDecision(
            mode=mode,
            confidence=confidence,
            parameters=parameters,
            reasoning=reasoning,
            alternatives=alternatives,
        )

        logger.info(
            f"[DecisionTree] Decision: {mode} "
            f"(confidence={confidence:.2f}, gemini={used_gemini})"
        )

        return decision

    def analyze_context(self, html: str | None) -> ContextAnalysis:
        """
        Analyze HTML context without making a decision.

        Useful for understanding existing design before interview.

        Args:
            html: HTML string to analyze

        Returns:
            ContextAnalysis with extracted tokens
        """
        return self.context_analyzer.analyze(html)

    # =========================================================================
    # RULE EVALUATION
    # =========================================================================

    def _evaluate_rules(self, context: EnrichedContext) -> str:
        """
        Evaluate MODE_RULES to select mode.

        Rules are evaluated in priority order (descending).
        First matching rule wins.

        Args:
            context: Enriched context with answers and HTML analysis

        Returns:
            Selected mode string
        """
        # Sort rules by priority (descending)
        sorted_rules = sorted(
            self.MODE_RULES.items(),
            key=lambda x: x[1][1],
            reverse=True,
        )

        for mode, (condition, priority) in sorted_rules:
            try:
                if condition(context):
                    logger.debug(f"[DecisionTree] Rule matched: {mode} (priority={priority})")
                    return mode
            except Exception as e:
                logger.warning(f"[DecisionTree] Rule evaluation error for {mode}: {e}")
                continue

        # Should never reach here due to fallback rule
        return "design_frontend"

    # =========================================================================
    # SCORE CALCULATION
    # =========================================================================

    def _calculate_scores(
        self,
        mode: str,
        context: EnrichedContext,
    ) -> DecisionScores:
        """
        Calculate 6-dimension confidence scores.

        Each dimension evaluates a different aspect of decision quality.

        Args:
            mode: Selected mode
            context: Enriched context

        Returns:
            DecisionScores with all dimensions
        """
        scores = DecisionScores()

        # === Intent Clarity (25%) ===
        # How clearly did user express their intent?
        intent_answer = context.get_answer("q_intent_main")
        if intent_answer:
            scores.intent_clarity = 0.9
        elif context.answer_count >= 2:
            scores.intent_clarity = 0.7
        else:
            scores.intent_clarity = 0.5

        # === Scope Match (20%) ===
        # Does selected mode match user's scope preference?
        scope_answer = context.get_answer("q_scope_type")
        scope_mode_map = {
            "opt_full_page": "design_page",
            "opt_section": "design_section",
            "opt_component": "design_frontend",
        }
        if scope_answer:
            expected_mode = scope_mode_map.get(scope_answer)
            if expected_mode == mode:
                scores.scope_match = 1.0
            elif expected_mode:
                scores.scope_match = 0.6
            else:
                scores.scope_match = 0.7
        else:
            scores.scope_match = 0.5

        # === Context Richness (15%) ===
        # How much context do we have to work with?
        context_score = 0.3
        if context.has_html_context():
            context_score += 0.3
        if context.has_project_context():
            context_score += 0.2
        if context.answer_count >= 5:
            context_score += 0.2
        scores.context_richness = min(context_score, 1.0)

        # === Parameter Completeness (20%) ===
        # Are all required parameters available?
        required_params = self._get_required_params(mode)
        if required_params:
            available = sum(1 for p in required_params if context.has_answer(p))
            scores.parameter_completeness = available / len(required_params)
        else:
            scores.parameter_completeness = 0.8

        # === Constraint Satisfaction (10%) ===
        # Are any constraints violated?
        # Currently simplified - could check accessibility, dark mode requirements
        scores.constraint_satisfaction = 0.8

        # === Alternative Viability (10%) ===
        # How viable are other options?
        # Lower = more certain about selected mode
        scores.alternative_viability = 0.7

        return scores

    def _get_required_params(self, mode: str) -> list[str]:
        """Get required answer keys for a mode."""
        required: dict[str, list[str]] = {
            "design_page": ["q_page_type"],
            "design_section": ["q_section_type"],
            "design_frontend": ["q_component_type"],
            "refine_frontend": [],
            "replace_section_in_page": ["q_section_type"],
            "design_from_reference": [],
        }
        return required.get(mode, [])

    # =========================================================================
    # PARAMETER EXTRACTION
    # =========================================================================

    def _extract_parameters(
        self,
        mode: str,
        context: EnrichedContext,
    ) -> dict[str, Any]:
        """
        Extract mode-specific parameters from context.

        Args:
            mode: Selected mode
            context: Enriched context

        Returns:
            Parameters dictionary for the mode
        """
        extractor = self.PARAMETER_EXTRACTORS.get(mode)
        if extractor:
            try:
                return extractor(context)
            except Exception as e:
                logger.warning(f"[DecisionTree] Parameter extraction error: {e}")
        return {}

    def _extract_common_parameters(
        self,
        context: EnrichedContext,
    ) -> dict[str, Any]:
        """
        Extract parameters common to all modes.

        Args:
            context: Enriched context

        Returns:
            Common parameters dictionary
        """
        params: dict[str, Any] = {}

        # Theme
        theme = context.get_answer("q_theme_preference")
        if theme:
            params["theme"] = _map_theme(theme)
        elif context.html_analysis.detected_theme:
            params["theme"] = context.html_analysis.detected_theme

        # Dark mode
        color_mode = context.get_answer("q_color_mode")
        if color_mode:
            params["dark_mode"] = color_mode in ("opt_dark", "opt_both")

        # Language
        language = context.get_answer("q_content_language")
        if language:
            params["content_language"] = _map_language(language)

        # Project context
        if context.project_context:
            params["project_context"] = context.project_context

        return params

    # =========================================================================
    # GEMINI REASONING
    # =========================================================================

    async def _gemini_reasoning(
        self,
        context: EnrichedContext,
        current_mode: str,
        scores: DecisionScores,
    ) -> dict[str, Any] | None:
        """
        Use Gemini for edge case reasoning.

        Called when confidence is below GEMINI_TRIGGER_THRESHOLD.

        Args:
            context: Enriched context
            current_mode: Currently selected mode
            scores: Calculated confidence scores

        Returns:
            Dict with mode and reasoning, or None on error
        """
        if not self.client:
            return None

        # Get lowest dimensions for targeted prompt
        weak_dims = scores.get_lowest_dimensions(2)
        weak_dims_str = ", ".join(f"{dim}={score:.2f}" for dim, score in weak_dims)

        prompt = f"""Kullanıcının tasarım ihtiyacını analiz et ve en uygun modu seç.

## Kullanıcı Cevapları
{json.dumps(context.answers, ensure_ascii=False, indent=2)}

## Mevcut Bağlam
- HTML var mı: {"Evet" if context.has_html_context() else "Hayır"}
- Tespit edilen tema: {context.html_analysis.detected_theme or "belirsiz"}
- Tespit edilen componentler: {context.html_analysis.detected_components}
- Proje bağlamı: {context.project_context or "belirtilmemiş"}

## Mevcut Seçim
- Mod: {current_mode}
- Güven skoru: {scores.overall:.2f}
- Zayıf boyutlar: {weak_dims_str}

## Görev
En uygun tasarım modunu seç ve kısa bir neden belirt.

Modlar:
- design_frontend: Tekil component (button, card, form, etc.)
- design_page: Tam sayfa (landing, dashboard, auth, etc.)
- design_section: Tek section (hero, features, pricing, etc.)
- refine_frontend: Mevcut HTML'i geliştir
- replace_section_in_page: Sayfa içi section değiştir
- design_from_reference: Referans görselinden tasarla

JSON formatında cevap ver (başka bir şey yazma):
{{"mode": "...", "reasoning": "..."}}
"""

        try:
            result = await self.client.generate_text(
                prompt=prompt,
                thinking_level="high",
                max_output_tokens=500,
            )

            # Extract text from result
            text = result.get("text", "")
            if not text:
                return None

            # Parse JSON from response
            json_match = re.search(r"\{[^{}]+\}", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except json.JSONDecodeError as e:
            logger.warning(f"[DecisionTree] Gemini JSON parse error: {e}")
        except Exception as e:
            logger.error(f"[DecisionTree] Gemini reasoning error: {e}")

        return None

    # =========================================================================
    # REASONING & ALTERNATIVES
    # =========================================================================

    def _build_basic_reasoning(
        self,
        mode: str,
        context: EnrichedContext,
        scores: DecisionScores,
    ) -> str:
        """
        Build human-readable reasoning without Gemini.

        Args:
            mode: Selected mode
            context: Enriched context
            scores: Confidence scores

        Returns:
            Turkish reasoning string
        """
        answer_count = context.answer_count
        confidence = scores.overall
        confidence_pct = int(confidence * 100)

        # Build reason parts
        reasons: list[str] = []

        if context.has_html_context():
            reasons.append("mevcut HTML analiz edildi")
        if context.get_answer("q_intent_main"):
            reasons.append("kullanıcı amacı belirlendi")
        if context.get_answer("q_scope_type"):
            reasons.append("kapsam tercihi alındı")

        reason_text = ", ".join(reasons) if reasons else "genel değerlendirme"

        # Mode descriptions
        mode_names = {
            "design_frontend": "component tasarımı",
            "design_page": "tam sayfa tasarımı",
            "design_section": "section tasarımı",
            "refine_frontend": "mevcut tasarımı geliştirme",
            "replace_section_in_page": "section değiştirme",
            "design_from_reference": "referanstan tasarım",
        }
        mode_desc = mode_names.get(mode, mode)

        return (
            f"Toplam {answer_count} cevap değerlendirildi. "
            f"{reason_text.capitalize()} sonucu '{mode_desc}' modu "
            f"%{confidence_pct} güvenle seçildi."
        )

    def _get_alternatives(self, mode: str) -> list[dict[str, Any]]:
        """
        Get alternative modes the user could consider.

        Args:
            mode: Selected mode

        Returns:
            List of alternative mode dicts
        """
        mode_descriptions = {
            "design_frontend": "Tekil component tasarımı",
            "design_page": "Tam sayfa tasarımı",
            "design_section": "Section tasarımı",
            "refine_frontend": "Mevcut tasarımı geliştir",
            "replace_section_in_page": "Bölüm değiştir",
            "design_from_reference": "Referanstan tasarla",
        }

        alternatives = []
        for alt_mode, desc in mode_descriptions.items():
            if alt_mode != mode:
                alternatives.append({"mode": alt_mode, "reason": desc})

        return alternatives[:2]  # Top 2 alternatives

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _state_to_answer_dict(self, state: InterviewState) -> dict[str, str]:
        """
        Convert InterviewState answers to simple dict.

        Takes first selected option for each answer.

        Args:
            state: Interview state with answers

        Returns:
            Dict of question_id → first selected option
        """
        result: dict[str, str] = {}
        for answer in state.answers:
            if answer.selected_options:
                result[answer.question_id] = answer.selected_options[0]
        return result


# =============================================================================
# MAPPING FUNCTIONS (module-level for PARAMETER_EXTRACTORS lambdas)
# =============================================================================


def _map_page_type(value: str | None) -> str:
    """Map page type answer to template_type parameter."""
    if not value:
        return "landing_page"

    mapping = {
        "opt_landing_page": "landing_page",
        "opt_dashboard": "dashboard",
        "opt_auth_page": "auth_page",
        "opt_pricing_page": "pricing_page",
        "opt_blog_post": "blog_post",
        "opt_product_page": "product_page",
        "opt_portfolio": "portfolio",
        "opt_documentation": "documentation",
        "opt_error_page": "error_page",
        "opt_coming_soon": "coming_soon",
    }
    return mapping.get(value, value.replace("opt_", ""))


def _map_section_type(value: str | None) -> str:
    """Map section type answer to section_type parameter."""
    if not value:
        return "hero"

    mapping = {
        "opt_hero": "hero",
        "opt_features": "features",
        "opt_pricing_section": "pricing",
        "opt_testimonials": "testimonials",
        "opt_cta": "cta",
        "opt_footer": "footer",
        "opt_stats": "stats",
        "opt_faq": "faq",
        "opt_team": "team",
        "opt_contact": "contact",
        "opt_gallery": "gallery",
        "opt_newsletter": "newsletter",
    }
    return mapping.get(value, value.replace("opt_", ""))


def _map_component_type(value: str | None) -> str:
    """Map component type answer to component_type parameter."""
    if not value:
        return "card"

    mapping = {
        "opt_button": "button",
        "opt_input": "input",
        "opt_badge": "badge",
        "opt_avatar": "avatar",
        "opt_card": "card",
        "opt_form": "form",
        "opt_modal": "modal",
        "opt_tabs": "tabs",
        "opt_table": "table",
        "opt_navbar": "navbar",
        "opt_sidebar": "sidebar",
        "opt_data_table": "data_table",
    }
    return mapping.get(value, value.replace("opt_", ""))


def _map_theme(value: str | None) -> str:
    """Map theme answer to theme parameter."""
    if not value:
        return "modern-minimal"

    mapping = {
        "opt_modern_minimal": "modern-minimal",
        "opt_corporate": "corporate",
        "opt_startup": "startup",
        "opt_brutalist": "brutalist",
        "opt_glassmorphism": "glassmorphism",
        "opt_neo_brutalism": "neo-brutalism",
        "opt_cyberpunk": "cyberpunk",
        "opt_nature": "nature",
        "opt_pastel": "pastel",
        "opt_gradient": "gradient",
        "opt_soft_ui": "soft-ui",
        "opt_dark_mode_first": "dark_mode_first",
        "opt_high_contrast": "high_contrast",
        "opt_retro": "retro",
    }
    return mapping.get(value, value.replace("opt_", "").replace("_", "-"))


def _map_language(value: str | None) -> str:
    """Map language answer to content_language parameter."""
    if not value:
        return "tr"

    mapping = {
        "opt_turkish": "tr",
        "opt_english": "en",
        "opt_german": "de",
    }
    return mapping.get(value, "tr")
