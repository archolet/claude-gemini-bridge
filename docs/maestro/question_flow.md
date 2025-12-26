# MAESTRO Question Flow Diagram

This document visualizes the MAESTRO interview flow and decision paths.

## Main Question Flow

```mermaid
flowchart TD
    subgraph START ["Session Start"]
        S[start_session]
        S --> HAS_HTML{existing_html?}
    end

    subgraph INTENT ["Intent Category"]
        HAS_HTML -->|Yes| Q_EXIST[q_existing_action]
        HAS_HTML -->|No| Q_INTENT[q_intent_main]

        Q_INTENT -->|opt_new_design| Q_SCOPE
        Q_INTENT -->|opt_refine| Q_EXIST
        Q_INTENT -->|opt_from_reference| Q_REF
    end

    subgraph EXISTING ["Existing Context"]
        Q_EXIST -->|opt_refine| DECIDE_REFINE
        Q_EXIST -->|opt_replace_section| Q_SECTION
        Q_EXIST -->|opt_start_fresh| Q_SCOPE

        Q_REF[q_reference_upload]
        Q_REF --> Q_ADHERENCE[q_reference_adherence]
        Q_ADHERENCE --> DECIDE_REF
    end

    subgraph SCOPE ["Scope Category"]
        Q_SCOPE[q_scope_type]
        Q_SCOPE -->|opt_full_page| Q_PAGE
        Q_SCOPE -->|opt_section| Q_SECTION
        Q_SCOPE -->|opt_component| Q_COMP
    end

    subgraph DETAIL ["Detail Questions"]
        Q_PAGE[q_page_type]
        Q_SECTION[q_section_type]
        Q_COMP[q_component_type]

        Q_PAGE --> Q_AUDIENCE
        Q_SECTION --> Q_THEME
        Q_COMP --> Q_THEME
    end

    subgraph INDUSTRY ["Industry Category"]
        Q_AUDIENCE[q_target_audience]
        Q_AUDIENCE --> Q_INDUSTRY[q_industry_type]
        Q_INDUSTRY --> Q_FORMALITY[q_formality_level]
        Q_FORMALITY --> Q_THEME
    end

    subgraph THEME ["Theme Category"]
        Q_THEME[q_theme_preference]
        Q_THEME --> Q_COLOR_MODE[q_color_mode]
        Q_COLOR_MODE --> Q_COLOR_PREF[q_color_preference]
        Q_COLOR_PREF --> Q_BRAND[q_brand_primary_color]
    end

    subgraph VIBE ["Vibe Category"]
        Q_BRAND --> Q_VIBE[q_design_vibe]
    end

    subgraph CONTENT ["Content Category"]
        Q_VIBE --> Q_CONTENT[q_content_ready]
        Q_CONTENT -->|opt_content_ready| Q_TECH
        Q_CONTENT -->|opt_need_content| Q_INPUT[q_content_input]
        Q_INPUT --> Q_TECH
    end

    subgraph TECHNICAL ["Technical Category"]
        Q_TECH[q_technical_level]
        Q_TECH --> Q_RADIUS[q_border_radius]
        Q_RADIUS --> Q_ANIM[q_animation_level]
    end

    subgraph A11Y ["Accessibility Category"]
        Q_ANIM --> Q_A11Y[q_accessibility_level]
    end

    subgraph LANGUAGE ["Language Category"]
        Q_A11Y --> Q_LANG[q_content_language]
    end

    subgraph DECISION ["Decision Phase"]
        Q_LANG --> DECIDE[DecisionTree]

        DECIDE_REFINE[Decision: refine_frontend]
        DECIDE_REF[Decision: design_from_reference]

        DECIDE --> MODE_PAGE[design_page]
        DECIDE --> MODE_SECTION[design_section]
        DECIDE --> MODE_COMP[design_frontend]
    end

    style S fill:#4CAF50,color:#fff
    style DECIDE fill:#2196F3,color:#fff
    style DECIDE_REFINE fill:#2196F3,color:#fff
    style DECIDE_REF fill:#2196F3,color:#fff
    style MODE_PAGE fill:#9C27B0,color:#fff
    style MODE_SECTION fill:#9C27B0,color:#fff
    style MODE_COMP fill:#9C27B0,color:#fff
```

## Skip Rules

```mermaid
flowchart LR
    subgraph SKIP_RULES ["Automatic Skip Rules"]
        R1[Previous HTML exists] -->|Skip| Q1[q_intent_main]
        R2[Scope = Component] -->|Skip| Q2[q_page_type]
        R3[Scope = Page] -->|Skip| Q3[q_component_type]
        R4[Scope = Section] -->|Skip| Q3
        R5[Industry = None] -->|Skip| Q4[q_formality_level]
    end

    style R1 fill:#FF9800,color:#fff
    style R2 fill:#FF9800,color:#fff
    style R3 fill:#FF9800,color:#fff
    style R4 fill:#FF9800,color:#fff
    style R5 fill:#FF9800,color:#fff
```

## Follow-Up Triggers

```mermaid
flowchart TB
    subgraph FOLLOWUPS ["Follow-up Question Triggers"]
        direction TB

        A1[q_intent_main: opt_new_design] --> F1[q_scope_type]
        A2[q_intent_main: opt_from_reference] --> F2[q_reference_upload]

        A3[q_scope_type: opt_full_page] --> F3[q_page_type]
        A4[q_scope_type: opt_section] --> F4[q_section_type]
        A5[q_scope_type: opt_component] --> F5[q_component_type]

        A6[q_existing_action: opt_replace_section] --> F6[q_section_type]
    end

    style A1 fill:#4CAF50,color:#fff
    style A2 fill:#4CAF50,color:#fff
    style A3 fill:#4CAF50,color:#fff
    style A4 fill:#4CAF50,color:#fff
    style A5 fill:#4CAF50,color:#fff
    style A6 fill:#4CAF50,color:#fff
```

## Category Priority

| Priority | Category | Questions | Description |
|----------|----------|-----------|-------------|
| 1 | Intent | q_intent_main | What do you want to do? |
| 2 | Scope | q_scope_type | Page, section, or component? |
| 3 | Existing Context | q_existing_action, q_reference_* | Existing HTML context |
| 4 | Industry | q_target_audience, q_industry_type, q_formality_level | Target audience |
| 5 | Theme/Style | q_theme_preference, q_color_* | Visual style |
| 6 | Vibe/Mood | q_design_vibe | Design personality |
| 7 | Content | q_content_ready, q_content_input | Content structure |
| 8 | Technical | q_technical_level, q_border_radius, q_animation_level | Tech requirements |
| 9 | Accessibility | q_accessibility_level | WCAG level |
| 10 | Language | q_content_language | Content language |

## Decision Tree Dimensions

```mermaid
pie title Decision Confidence Weights
    "Intent Clarity" : 25
    "Scope Definition" : 20
    "Style Specification" : 15
    "Context Availability" : 15
    "Content Readiness" : 15
    "Technical Completeness" : 10
```

## Mode Selection Rules

| Condition | Mode |
|-----------|------|
| opt_from_reference + image_path | `design_from_reference` |
| opt_refine + previous_html | `refine_frontend` |
| opt_replace_section + previous_html | `replace_section_in_page` |
| opt_full_page | `design_page` |
| opt_section | `design_section` |
| opt_component (default) | `design_frontend` |

## State Machine

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> ANALYZING: start_session()
    ANALYZING --> INTERVIEWING: first question ready
    INTERVIEWING --> AWAITING_ANSWER: question sent
    AWAITING_ANSWER --> INTERVIEWING: answer received
    INTERVIEWING --> DECIDING: all questions answered
    DECIDING --> CONFIRMING: decision made
    CONFIRMING --> EXECUTING: user confirms
    EXECUTING --> COMPLETE: HTML generated

    INTERVIEWING --> DECIDING: get_final_decision()
    AWAITING_ANSWER --> ABORTED: abort_session()
    DECIDING --> ABORTED: abort_session()

    COMPLETE --> [*]
    ABORTED --> [*]
```
