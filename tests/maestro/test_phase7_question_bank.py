"""
Phase 7 Tests - QuestionBank Unit Tests

Comprehensive tests for MAESTRO QuestionBank:
- All 10 question categories
- Follow-up mappings validation
- Question retrieval methods
- Category configuration
"""
import pytest

from gemini_mcp.maestro.questions.bank import QuestionBank
from gemini_mcp.maestro.models import (
    Question,
    QuestionCategory,
    QuestionType,
)


class TestQuestionBankInitialization:
    """Tests for QuestionBank initialization and structure."""

    def test_singleton_creates_questions(self):
        """QuestionBank loads all questions on init."""
        bank = QuestionBank()
        assert len(bank.get_all_question_ids()) > 0

    def test_all_categories_have_questions(self):
        """Each QuestionCategory has at least one question."""
        bank = QuestionBank()
        for category in QuestionCategory:
            questions = bank.get_questions_by_category(category)
            assert (
                len(questions) >= 1
            ), f"Category {category} has no questions"

    def test_category_config_completeness(self):
        """CATEGORY_CONFIG covers all QuestionCategory values."""
        for category in QuestionCategory:
            assert category in QuestionBank.CATEGORY_CONFIG, (
                f"Missing config for {category}"
            )

    def test_category_config_structure(self):
        """Each category config has required keys."""
        for category, config in QuestionBank.CATEGORY_CONFIG.items():
            assert "priority" in config, f"Missing priority for {category}"
            assert "required" in config, f"Missing required for {category}"
            assert isinstance(config["priority"], int)
            assert isinstance(config["required"], bool)


class TestCategoryConfiguration:
    """Tests for category priority and required flags."""

    def test_intent_is_highest_priority(self):
        """INTENT category has priority 1."""
        config = QuestionBank.CATEGORY_CONFIG[QuestionCategory.INTENT]
        assert config["priority"] == 1

    def test_required_categories(self):
        """Verify which categories are required."""
        bank = QuestionBank()
        required_cats = [
            QuestionCategory.INTENT,
            QuestionCategory.SCOPE,
            QuestionCategory.THEME_STYLE,
            QuestionCategory.LANGUAGE,
        ]
        for cat in required_cats:
            assert QuestionBank.CATEGORY_CONFIG[cat]["required"] is True

    def test_optional_categories(self):
        """Verify which categories are optional."""
        optional_cats = [
            QuestionCategory.EXISTING_CONTEXT,
            QuestionCategory.INDUSTRY,
            QuestionCategory.VIBE_MOOD,
            QuestionCategory.CONTENT,
            QuestionCategory.TECHNICAL,
            QuestionCategory.ACCESSIBILITY,
        ]
        for cat in optional_cats:
            assert QuestionBank.CATEGORY_CONFIG[cat]["required"] is False

    def test_get_categories_by_priority_ordering(self):
        """Categories are sorted by priority."""
        bank = QuestionBank()
        ordered = bank.get_categories_by_priority()

        # First should be INTENT (priority 1)
        assert ordered[0] == QuestionCategory.INTENT
        # Last should be LANGUAGE (priority 10)
        assert ordered[-1] == QuestionCategory.LANGUAGE

        # Verify ascending order
        for i in range(len(ordered) - 1):
            p1 = QuestionBank.CATEGORY_CONFIG[ordered[i]]["priority"]
            p2 = QuestionBank.CATEGORY_CONFIG[ordered[i + 1]]["priority"]
            assert p1 <= p2


class TestQuestionRetrieval:
    """Tests for question retrieval methods."""

    def test_get_question_by_id(self):
        """Retrieve a specific question by ID."""
        bank = QuestionBank()
        question = bank.get_question("q_intent_main")

        assert question is not None
        assert question.id == "q_intent_main"
        assert question.category == QuestionCategory.INTENT

    def test_get_question_invalid_id(self):
        """Return None for invalid question ID."""
        bank = QuestionBank()
        result = bank.get_question("nonexistent_question")
        assert result is None

    def test_get_questions_by_category(self):
        """Get all questions in a category."""
        bank = QuestionBank()
        intent_questions = bank.get_questions_by_category(QuestionCategory.INTENT)

        assert len(intent_questions) >= 1
        for q in intent_questions:
            assert q.category == QuestionCategory.INTENT

    def test_get_required_questions(self):
        """Get questions from required categories only."""
        bank = QuestionBank()
        required = bank.get_required_questions()

        required_categories = {
            QuestionCategory.INTENT,
            QuestionCategory.SCOPE,
            QuestionCategory.THEME_STYLE,
            QuestionCategory.LANGUAGE,
        }

        # All returned questions should be from required categories
        for q in required:
            assert q.category in required_categories

    def test_get_all_question_ids(self):
        """Get list of all question IDs."""
        bank = QuestionBank()
        ids = bank.get_all_question_ids()

        assert isinstance(ids, list)
        assert len(ids) > 0
        assert "q_intent_main" in ids
        assert "q_scope_type" in ids


class TestInitialQuestion:
    """Tests for initial question selection."""

    def test_initial_question_new_design(self):
        """New design starts with intent question."""
        bank = QuestionBank()
        question = bank.get_initial_question(has_existing_context=False)

        assert question.id == "q_intent_main"

    def test_initial_question_existing_context(self):
        """Existing context starts with existing action question."""
        bank = QuestionBank()
        question = bank.get_initial_question(has_existing_context=True)

        assert question.id == "q_existing_action"


class TestIntentQuestions:
    """Tests for INTENT category questions."""

    def test_intent_main_question_structure(self):
        """q_intent_main has correct structure."""
        bank = QuestionBank()
        q = bank.get_question("q_intent_main")

        assert q.text == "Bugün nasıl bir tasarım yapmak istiyorsunuz?"
        assert len(q.options) == 3

        # Check option IDs
        option_ids = [o.id for o in q.options]
        assert "opt_new_design" in option_ids
        assert "opt_refine_existing" in option_ids
        assert "opt_from_reference" in option_ids

    def test_intent_follow_up_map(self):
        """q_intent_main has correct follow-up mappings."""
        bank = QuestionBank()
        q = bank.get_question("q_intent_main")

        assert q.follow_up_map["opt_new_design"] == "q_scope_type"
        assert q.follow_up_map["opt_refine_existing"] == "q_existing_action"
        assert q.follow_up_map["opt_from_reference"] == "q_reference_upload"


class TestScopeQuestions:
    """Tests for SCOPE category questions."""

    def test_scope_type_options(self):
        """q_scope_type has full_page, section, component options."""
        bank = QuestionBank()
        q = bank.get_question("q_scope_type")

        option_ids = [o.id for o in q.options]
        assert "opt_full_page" in option_ids
        assert "opt_section" in option_ids
        assert "opt_component" in option_ids

    def test_page_type_options(self):
        """q_page_type has multiple page templates."""
        bank = QuestionBank()
        q = bank.get_question("q_page_type")

        assert q is not None
        assert len(q.options) >= 8  # landing, dashboard, auth, pricing, etc.

        option_ids = [o.id for o in q.options]
        assert "opt_landing_page" in option_ids
        assert "opt_dashboard" in option_ids

    def test_section_type_options(self):
        """q_section_type has all section options."""
        bank = QuestionBank()
        q = bank.get_question("q_section_type")

        option_ids = [o.id for o in q.options]
        expected = ["opt_hero", "opt_features", "opt_pricing_section", "opt_testimonials"]
        for opt in expected:
            assert opt in option_ids

    def test_component_type_options(self):
        """q_component_type has atoms, molecules, organisms."""
        bank = QuestionBank()
        q = bank.get_question("q_component_type")

        option_ids = [o.id for o in q.options]
        # Atoms
        assert "opt_button" in option_ids
        assert "opt_input" in option_ids
        # Molecules
        assert "opt_card" in option_ids
        assert "opt_modal" in option_ids
        # Organisms
        assert "opt_navbar" in option_ids
        assert "opt_sidebar" in option_ids


class TestThemeQuestions:
    """Tests for THEME_STYLE category questions."""

    def test_theme_preference_options(self):
        """q_theme_preference has all theme options."""
        bank = QuestionBank()
        q = bank.get_question("q_theme_preference")

        option_ids = [o.id for o in q.options]
        expected = [
            "opt_modern_minimal",
            "opt_corporate",
            "opt_startup",
            "opt_brutalist",
            "opt_glassmorphism",
            "opt_cyberpunk",
        ]
        for opt in expected:
            assert opt in option_ids

    def test_color_mode_options(self):
        """q_color_mode has light, dark, both options."""
        bank = QuestionBank()
        q = bank.get_question("q_color_mode")

        option_ids = [o.id for o in q.options]
        assert "opt_light" in option_ids
        assert "opt_dark" in option_ids
        assert "opt_both" in option_ids

    def test_brand_color_is_color_picker(self):
        """q_brand_primary_color uses COLOR_PICKER type."""
        bank = QuestionBank()
        q = bank.get_question("q_brand_primary_color")

        assert q.question_type == QuestionType.COLOR_PICKER


class TestLanguageQuestions:
    """Tests for LANGUAGE category questions."""

    def test_content_language_options(self):
        """q_content_language has TR, EN, DE options."""
        bank = QuestionBank()
        q = bank.get_question("q_content_language")

        option_ids = [o.id for o in q.options]
        assert "opt_turkish" in option_ids
        assert "opt_english" in option_ids
        assert "opt_german" in option_ids


class TestShowWhenConditions:
    """Tests for show_when conditional display rules."""

    def test_page_type_show_when(self):
        """q_page_type has show_when for full_page scope."""
        bank = QuestionBank()
        q = bank.get_question("q_page_type")

        assert q.show_when == "q_scope_type == 'opt_full_page'"

    def test_section_type_show_when(self):
        """q_section_type has show_when for section scope."""
        bank = QuestionBank()
        q = bank.get_question("q_section_type")

        assert q.show_when == "q_scope_type == 'opt_section'"

    def test_component_type_show_when(self):
        """q_component_type has show_when for component scope."""
        bank = QuestionBank()
        q = bank.get_question("q_component_type")

        assert q.show_when == "q_scope_type == 'opt_component'"


class TestFollowUpValidation:
    """Tests for follow-up mapping validation."""

    def test_all_follow_up_targets_exist(self):
        """All follow_up_map targets are valid question IDs."""
        bank = QuestionBank()
        missing = bank.validate_follow_up_targets()

        assert len(missing) == 0, f"Missing follow-up targets: {missing}"

    def test_intent_follow_ups_exist(self):
        """q_intent_main follow-up targets all exist."""
        bank = QuestionBank()
        q = bank.get_question("q_intent_main")

        for target in q.follow_up_map.values():
            assert bank.get_question(target) is not None, (
                f"Missing follow-up: {target}"
            )

    def test_scope_follow_ups_exist(self):
        """q_scope_type follow-up targets all exist."""
        bank = QuestionBank()
        q = bank.get_question("q_scope_type")

        for target in q.follow_up_map.values():
            assert bank.get_question(target) is not None, (
                f"Missing follow-up: {target}"
            )


class TestQuestionTypes:
    """Tests for different question types."""

    def test_default_is_single_choice(self):
        """Most questions default to SINGLE_CHOICE type."""
        bank = QuestionBank()
        q = bank.get_question("q_intent_main")

        assert q.question_type == QuestionType.SINGLE_CHOICE

    def test_text_input_questions(self):
        """Some questions use TEXT_INPUT type."""
        bank = QuestionBank()
        q = bank.get_question("q_reference_upload")

        assert q.question_type == QuestionType.TEXT_INPUT

    def test_color_picker_question(self):
        """Brand color question uses COLOR_PICKER type."""
        bank = QuestionBank()
        q = bank.get_question("q_brand_primary_color")

        assert q.question_type == QuestionType.COLOR_PICKER


class TestQuestionOptions:
    """Tests for question option structure."""

    def test_option_has_required_fields(self):
        """Each option has id, label, description."""
        bank = QuestionBank()
        q = bank.get_question("q_intent_main")

        for opt in q.options:
            assert opt.id is not None
            assert opt.label is not None
            assert len(opt.label) > 0

    def test_option_icons(self):
        """Options have emoji icons."""
        bank = QuestionBank()
        q = bank.get_question("q_intent_main")

        for opt in q.options:
            assert opt.icon is not None
            assert len(opt.icon) > 0

    def test_unique_option_ids(self):
        """Option IDs are unique within a question."""
        bank = QuestionBank()

        for qid in bank.get_all_question_ids():
            q = bank.get_question(qid)
            if q.options:
                ids = [o.id for o in q.options]
                assert len(ids) == len(set(ids)), (
                    f"Duplicate option IDs in {qid}"
                )


class TestAccessibilityQuestions:
    """Tests for ACCESSIBILITY category questions."""

    def test_accessibility_level_options(self):
        """q_accessibility_level has WCAG AA, AAA, basic options."""
        bank = QuestionBank()
        q = bank.get_question("q_accessibility_level")

        option_ids = [o.id for o in q.options]
        assert "opt_wcag_aa" in option_ids
        assert "opt_wcag_aaa" in option_ids
        assert "opt_basic_a11y" in option_ids


class TestTechnicalQuestions:
    """Tests for TECHNICAL category questions."""

    def test_technical_level_question(self):
        """q_technical_level offers yes/no for advanced options."""
        bank = QuestionBank()
        q = bank.get_question("q_technical_level")

        option_ids = [o.id for o in q.options]
        assert "opt_yes_technical" in option_ids
        assert "opt_no_technical" in option_ids

    def test_border_radius_options(self):
        """q_border_radius has sharp to pill options."""
        bank = QuestionBank()
        q = bank.get_question("q_border_radius")

        option_ids = [o.id for o in q.options]
        assert "opt_sharp" in option_ids
        assert "opt_subtle" in option_ids
        assert "opt_rounded" in option_ids
        assert "opt_pill" in option_ids

    def test_animation_level_options(self):
        """q_animation_level has none to rich options."""
        bank = QuestionBank()
        q = bank.get_question("q_animation_level")

        option_ids = [o.id for o in q.options]
        assert "opt_none_anim" in option_ids
        assert "opt_subtle_anim" in option_ids
        assert "opt_rich_anim" in option_ids


class TestIndustryQuestions:
    """Tests for INDUSTRY category questions."""

    def test_target_audience_options(self):
        """q_target_audience has B2B, B2C, internal, developer."""
        bank = QuestionBank()
        q = bank.get_question("q_target_audience")

        option_ids = [o.id for o in q.options]
        assert "opt_b2b" in option_ids
        assert "opt_b2c" in option_ids
        assert "opt_internal" in option_ids
        assert "opt_developer" in option_ids

    def test_industry_type_options(self):
        """q_industry_type has multiple sectors."""
        bank = QuestionBank()
        q = bank.get_question("q_industry_type")

        option_ids = [o.id for o in q.options]
        expected = [
            "opt_tech_saas",
            "opt_finance",
            "opt_health",
            "opt_ecommerce",
        ]
        for opt in expected:
            assert opt in option_ids


class TestExistingContextQuestions:
    """Tests for EXISTING_CONTEXT category questions."""

    def test_existing_action_options(self):
        """q_existing_action has refine, replace, match options."""
        bank = QuestionBank()
        q = bank.get_question("q_existing_action")

        option_ids = [o.id for o in q.options]
        assert "opt_refine" in option_ids
        assert "opt_replace_section" in option_ids
        assert "opt_match_style" in option_ids

    def test_reference_adherence_options(self):
        """q_reference_adherence has strict, inspired, extract options."""
        bank = QuestionBank()
        q = bank.get_question("q_reference_adherence")

        option_ids = [o.id for o in q.options]
        assert "opt_strict" in option_ids
        assert "opt_inspired" in option_ids
        assert "opt_extract_tokens" in option_ids


class TestVibeMoodQuestions:
    """Tests for VIBE_MOOD category questions."""

    def test_design_vibe_options(self):
        """q_design_vibe has 4 vibe options."""
        bank = QuestionBank()
        q = bank.get_question("q_design_vibe")

        option_ids = [o.id for o in q.options]
        assert "opt_elite_corporate" in option_ids
        assert "opt_playful_funny" in option_ids
        assert "opt_cyberpunk_edge" in option_ids
        assert "opt_luxury_editorial" in option_ids


class TestContentQuestions:
    """Tests for CONTENT category questions."""

    def test_content_ready_options(self):
        """q_content_ready has ready, placeholder, generate options."""
        bank = QuestionBank()
        q = bank.get_question("q_content_ready")

        option_ids = [o.id for o in q.options]
        assert "opt_content_ready" in option_ids
        assert "opt_placeholder" in option_ids
        assert "opt_generate" in option_ids

    def test_content_input_is_text(self):
        """q_content_input uses TEXT_INPUT type."""
        bank = QuestionBank()
        q = bank.get_question("q_content_input")

        assert q.question_type == QuestionType.TEXT_INPUT
