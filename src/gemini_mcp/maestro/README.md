# MAESTRO Design Wizard

**MAESTRO** (Mode-Aware Expert System for Theme Resolution and Orchestration) is an intelligent design wizard that guides users through frontend design decisions via an interview-based approach.

## Overview

MAESTRO asks smart questions to understand design intent, then automatically selects the optimal design mode and parameters. It's built for the Gemini MCP server and integrates with all design tools.

### v1 Flow (Static Questions)
```
User Intent  -->  Interview  -->  Decision  -->  Execution
    |               |               |               |
    v               v               v               v
"I need a     "Landing page   design_page    Complete
 landing       or component?"  mode with      HTML output
 page"         "Theme?"        parameters
```

### v2 Flow (Soul-Aware Interview)
```
Design Brief  -->  Soul Extraction  -->  Dynamic Interview  -->  Execution
    |                    |                      |                    |
    v                    v                      v                    v
"B2B SaaS       ProjectSoul with        Context-aware         Design with
 dashboard      brand personality,       gap-filling           brand DNA
 for fintech"   audience, visual lang    questions             integrated
```

## MAESTRO v2: Soul-Aware Interview System

Version 2 introduces **intelligent brief analysis** powered by Gemini. Instead of static questions, MAESTRO v2:

1. **Extracts ProjectSoul** from design briefs using Gemini
2. **Identifies gaps** in the brief automatically
3. **Generates dynamic questions** to fill only missing information
4. **Maintains brand consistency** through the entire design process

### Key v2 Components

| Component | Purpose |
|-----------|---------|
| `ProjectSoul` | Core model capturing project essence |
| `SoulExtractor` | Gemini-powered brief analyzer |
| `GapDetector` | Identifies missing information |
| `DynamicQuestionGenerator` | Creates targeted questions |
| `SoulAwareSession` | Session with soul integration |
| `MAESTROv2Wrapper` | Backward-compatible wrapper |

### ProjectSoul Model

```python
class ProjectSoul:
    """The 'soul' of a project - drives all design decisions"""

    # Metadata
    metadata: ProjectMetadata  # name, tagline, type, industry

    # Brand Personality (Aaker Framework)
    brand_personality: BrandPersonality
    # - sincerity, excitement, competence, sophistication, ruggedness
    # - dominant_trait, archetype ("The Hero", "The Sage", etc.)

    # Target Audience
    target_audience: AudienceProfile
    # - age_range, tech_level, industry, needs

    # Visual Language
    visual_language: VisualLanguage
    # - theme, colors, typography, density

    # Emotional Framework
    emotional_framework: EmotionalFramework
    # - primary_emotion, secondary_emotion, avoid_emotions

    # Confidence Scores
    confidence_scores: ConfidenceScores
    # - brand, audience, visual, emotion, overall

    # Gap Analysis
    gap_analysis: GapAnalysis
    # - gaps list with priority and suggested questions
```

### v2 Quick Start

```python
from gemini_mcp.maestro import MAESTROv2Wrapper

# Initialize with v2 wrapper
wrapper = MAESTROv2Wrapper(client=gemini_client)

# Start with design brief (NEW in v2)
session_id, result = await wrapper.start_session(
    design_brief="""
    B2B SaaS dashboard için yönetim paneli.
    Hedef kitle: Fintech şirketlerinin IT yöneticileri.
    Profesyonel ve güvenilir bir görünüm istiyoruz.
    """
)

# v2 returns soul extraction result first
if result.soul:
    print(f"Project: {result.soul.metadata.project_name}")
    print(f"Confidence: {result.soul.confidence_scores.overall:.0%}")

# Continue with dynamic questions...
```

### InterviewPhase State Machine

v2 uses a sophisticated state machine for interview flow:

```python
class InterviewPhase(Enum):
    INITIAL = "initial"              # Session created
    SOUL_EXTRACTION = "extraction"    # Analyzing design brief
    CONTEXT_GATHERING = "gathering"   # Filling gaps from soul
    DEEP_DIVE = "deep_dive"          # Detailed exploration
    VISUAL_EXPLORATION = "visual"     # Visual preferences
    VALIDATION = "validation"         # Confirming decisions
    SYNTHESIS = "synthesis"           # Final preparation
    EXECUTION = "execution"           # Design generation
    COMPLETE = "complete"             # Session finished
```

State transitions are managed by `InterviewStateMachine`:

```python
# Valid transitions
INITIAL → SOUL_EXTRACTION
SOUL_EXTRACTION → CONTEXT_GATHERING
CONTEXT_GATHERING → DEEP_DIVE | VALIDATION
DEEP_DIVE → VISUAL_EXPLORATION | VALIDATION
VISUAL_EXPLORATION → VALIDATION
VALIDATION → SYNTHESIS | DEEP_DIVE (backtrack)
SYNTHESIS → EXECUTION
EXECUTION → COMPLETE
```

## Quick Start

```python
from gemini_mcp.maestro.core import Maestro

# Initialize
maestro = Maestro(client=gemini_client)

# Start interview session
session_id, first_question = await maestro.start_session(
    project_context="B2B SaaS landing page"
)

# Answer questions
from gemini_mcp.maestro.models import Answer

answer = Answer(
    question_id=first_question.id,
    selected_options=["opt_new_design"]
)
result = await maestro.process_answer(session_id, answer)

# Result is either next Question or MaestroDecision
if isinstance(result, MaestroDecision):
    # Ready to execute!
    html_output = await maestro.execute(session_id)
```

## MCP Tools

MAESTRO is exposed via 4 MCP tools:

| Tool | Purpose |
|------|---------|
| `maestro_start_session` | Begin a new design wizard session |
| `maestro_answer` | Submit answer to current question |
| `maestro_get_decision` | Force decision with current answers |
| `maestro_execute` | Generate the design output |

### Example MCP Flow

```json
// 1. Start session
{
  "tool": "maestro_start_session",
  "arguments": {
    "project_context": "E-commerce product page"
  }
}

// Response includes first question
{
  "session_id": "maestro_abc123",
  "question": {
    "id": "q_intent_main",
    "text": "Ne tür bir tasarım yapmak istiyorsunuz?",
    "options": [...]
  }
}

// 2. Answer question
{
  "tool": "maestro_answer",
  "arguments": {
    "session_id": "maestro_abc123",
    "question_id": "q_intent_main",
    "selected_options": ["opt_new_design"]
  }
}

// 3. Continue until decision...
// 4. Execute
{
  "tool": "maestro_execute",
  "arguments": {
    "session_id": "maestro_abc123",
    "use_trifecta": true
  }
}
```

## Architecture

```
maestro/
├── core.py              # Main Maestro class & MCP integration
├── models.py            # All data models (Question, Answer, Decision)
│
├── v2/                  # NEW: MAESTRO v2 Soul-Aware System
│   ├── wrapper.py       # MAESTROv2Wrapper - backward compatible
│   ├── session.py       # SoulAwareSession - soul integration
│   └── fallback.py      # Graceful degradation to v1
│
├── models/              # NEW: v2 Data Models
│   ├── soul.py          # ProjectSoul - core model
│   ├── brand.py         # BrandPersonality (Aaker Framework)
│   ├── audience.py      # AudienceProfile
│   ├── visual.py        # VisualLanguage
│   ├── emotion.py       # EmotionalFramework, EmotionalTone
│   └── gap.py           # GapInfo, GapAnalysis
│
├── soul/                # NEW: Soul Extraction Engine
│   ├── extractor.py     # SoulExtractor - Gemini-powered
│   ├── aaker.py         # AakerAnalyzer - brand personality
│   ├── confidence.py    # ConfidenceCalculator
│   └── gaps.py          # GapDetector
│
├── prompts/             # NEW: Turkish Prompt Library
│   └── tr/
│       ├── extraction.py    # Soul extraction prompts
│       ├── feedback.py      # Validation/error messages
│       ├── interview.py     # Interview question templates
│       └── synthesis.py     # Final synthesis prompts
│
├── questions/
│   ├── bank.py          # QuestionBank - 24 questions across 10 categories
│   ├── validators.py    # Answer validation
│   └── generator.py     # NEW: DynamicQuestionGenerator
│
├── interview/
│   ├── engine.py        # InterviewEngine - question flow orchestration
│   ├── flow_controller.py  # Skip rules, show_when, follow-ups
│   ├── state_machine.py # NEW: InterviewStateMachine
│   ├── transitions.py   # NEW: StateTransitionManager
│   └── progress.py      # NEW: ProgressTracker with analytics
│
├── decision/
│   └── tree.py          # DecisionTree - 6-dimension scoring, mode selection
├── execution/
│   └── adapters.py      # Mode-specific parameter adapters
├── intelligence/
│   ├── adaptive_flow.py     # Context-aware question skipping
│   ├── preference_learner.py # User preference learning
│   └── recommender.py       # Smart recommendations
├── analytics/
│   ├── session_tracker.py   # Session metrics
│   ├── cost_analyzer.py     # Token cost analysis
│   └── quality_metrics.py   # Design quality scoring
├── ui/
│   └── formatter.py     # Output formatting for MCP responses
└── session_manager.py   # TTL-based session management
```

## Question Categories

| Category | Priority | Description |
|----------|----------|-------------|
| Intent | 1 | What do you want to do? (new/refine/reference) |
| Scope | 2 | Page, section, or component? |
| Existing Context | 3 | Do you have existing HTML? |
| Industry | 4 | Target audience and industry |
| Theme/Style | 5 | Visual theme preferences |
| Vibe/Mood | 6 | Design personality |
| Content | 7 | Content structure |
| Technical | 8 | Technical requirements |
| Accessibility | 9 | WCAG level |
| Language | 10 | Content language |

## Decision Modes

MAESTRO can select from 6 design modes:

| Mode | Description |
|------|-------------|
| `design_frontend` | Single component (button, card, form) |
| `design_page` | Full page layout (landing, dashboard) |
| `design_section` | Single section with style consistency |
| `refine_frontend` | Improve existing HTML |
| `replace_section_in_page` | Surgical section replacement |
| `design_from_reference` | Design from reference image |

## Decision Algorithm

The DecisionTree uses 6-dimension scoring:

1. **Intent Clarity** (25%) - How clear is the user's goal?
2. **Scope Definition** (20%) - Page/section/component determined?
3. **Style Specification** (15%) - Theme and vibe defined?
4. **Context Availability** (15%) - Existing HTML or reference?
5. **Technical Completeness** (10%) - Technical requirements clear?
6. **Content Readiness** (15%) - Content structure defined?

```
Total Score = Σ (dimension_score × weight)
Confidence = min(1.0, score / threshold)
```

## Skip Rules

MAESTRO intelligently skips questions based on context:

```python
# If user has existing HTML, skip intent question
# (they clearly want to refine)
if context.previous_html:
    skip("q_intent_main")

# If scope is "component", skip page type question
if answer("q_scope_type") == "opt_component":
    skip("q_page_type")
```

## DNA Integration (Phase 7)

MAESTRO integrates with DNAStore for design consistency:

- **Load**: On session start, loads previous design DNA for the project
- **Save**: After execution, saves extracted design tokens
- **Recommend**: Uses DNA history to suggest themes

```python
# Recommender uses DNA history
recommender.set_dna_store(dna_store)
theme_rec = recommender.recommend_theme()
# Returns theme from project history if consistent
```

## Intelligence Layer

### Adaptive Flow
- Skips questions when context provides the answer
- Detects industry from project context
- Infers scope from existing HTML

### Preference Learner
- Tracks user choices over time
- Builds confidence scores for preferences
- Suggests defaults based on history

### Recommender
- Combines multiple signals for recommendations
- Industry-specific theme suggestions
- Quality level based on project stage

## Testing

```bash
# Run all MAESTRO tests
uv run pytest tests/maestro/ -v

# Run specific test file
uv run pytest tests/maestro/test_phase7_flows.py -v

# Run with coverage
uv run pytest tests/maestro/ --cov=src/gemini_mcp/maestro
```

## Configuration

```python
# Session TTL (default: 1 hour)
SessionManager(ttl_seconds=3600)

# Max concurrent sessions (default: 100)
SessionManager(max_sessions=100)

# Quality thresholds
QualityMetrics.THRESHOLDS = {
    "draft": 6.0,
    "production": 7.0,
    "premium": 8.5,
    "enterprise": 9.0,
}
```

## Error Handling

MAESTRO handles errors gracefully:

```python
# Invalid session
result = await maestro.process_answer("invalid_id", answer)
# Returns error with clear message

# Unknown question
answer = Answer(question_id="unknown", ...)
# Validation returns error

# Empty answers
decision = await tree.make_decision(empty_state)
# Returns default mode with low confidence
```

## Performance

- Average interview: 5-8 questions (2-4 seconds)
- Decision calculation: <50ms
- Session cleanup: Automatic via TTL
- Memory: O(n) where n = active sessions

## License

Part of the Gemini MCP Server project.
