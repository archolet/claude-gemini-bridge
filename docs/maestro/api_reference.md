# MAESTRO API Reference

Complete API reference for the MAESTRO design wizard system.

## MCP Tools

### maestro_start_session

Start a new MAESTRO design wizard session.

**Arguments:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_context` | string | No | Project description for context (v1 mode) |
| `existing_html` | string | No | Existing HTML for refinement |
| `design_brief` | string | No | **NEW in v2:** Design brief for soul extraction |

> **v2 Mode:** When `design_brief` is provided, MAESTRO v2 extracts a `ProjectSoul` using Gemini, enabling intelligent gap detection and dynamic question generation.

**Returns (v1 - no design_brief):**

```json
{
  "session_id": "maestro_abc123",
  "question": {
    "id": "q_intent_main",
    "text": "Ne tür bir tasarım yapmak istiyorsunuz?",
    "category": "intent",
    "question_type": "single_choice",
    "options": [
      {"id": "opt_new_design", "label": "Yeni Tasarım", "description": "..."},
      {"id": "opt_refine", "label": "Mevcut Tasarımı Geliştir", "description": "..."}
    ]
  },
  "progress": 0.0,
  "status": "interviewing"
}
```

**Returns (v2 - with design_brief):**

```json
{
  "session_id": "maestro_v2_abc123",
  "soul": {
    "metadata": {
      "project_name": "FinDash Pro",
      "project_type": "dashboard",
      "industry": "fintech"
    },
    "brand_personality": {
      "sincerity": 0.7,
      "excitement": 0.4,
      "competence": 0.9,
      "sophistication": 0.8,
      "ruggedness": 0.2,
      "dominant_trait": "competence",
      "archetype": "The Expert"
    },
    "confidence_scores": {
      "brand": 0.85,
      "audience": 0.72,
      "visual": 0.60,
      "emotion": 0.78,
      "overall": 0.74
    },
    "gap_analysis": {
      "gaps": [
        {
          "field": "visual_language.colors",
          "priority": "important",
          "suggested_question": "Marka renk paletiniz var mı?"
        }
      ],
      "critical_count": 0,
      "important_count": 1
    }
  },
  "question": {
    "id": "dyn_visual_colors",
    "text": "Marka renk paletiniz var mı?",
    "phase": "context_gathering",
    "options": [...]
  },
  "progress": 0.33,
  "status": "interviewing"
}
```

---

### maestro_answer

Submit an answer to the current MAESTRO question.

**Arguments:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Active session ID |
| `question_id` | string | Yes | ID of question being answered |
| `selected_options` | string[] | Conditional | Selected option IDs |
| `free_text` | string | Conditional | Free text input |

**Returns (Question):**

```json
{
  "question": {
    "id": "q_scope_type",
    "text": "Tasarım kapsamı nedir?",
    "options": [...]
  },
  "progress": 0.33,
  "status": "interviewing"
}
```

**Returns (Decision):**

```json
{
  "decision": {
    "mode": "design_page",
    "confidence": 0.92,
    "parameters": {
      "template_type": "landing_page",
      "theme": "modern-minimal",
      "dark_mode": true
    },
    "reasoning": "Landing page için design_page modu seçildi",
    "alternatives": ["design_section"]
  },
  "progress": 1.0,
  "status": "decided"
}
```

---

### maestro_get_decision

Force a design decision with current answers.

**Arguments:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Active session ID |

**Returns:**

```json
{
  "decision": {
    "mode": "design_frontend",
    "confidence": 0.75,
    "parameters": {...},
    "reasoning": "...",
    "alternatives": [...]
  },
  "status": "decided"
}
```

---

### maestro_execute

Execute the design decision and generate output.

**Arguments:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Session with ready decision |
| `use_trifecta` | boolean | No | Enable multi-agent pipeline (default: false) |
| `quality_target` | string | No | Quality level: draft/production/premium/enterprise |

**Returns:**

```json
{
  "html": "<div class=\"hero\">...</div>",
  "mode": "design_page",
  "trifecta_enabled": true,
  "css_output": "/* Generated CSS */",
  "js_output": "// Generated JS",
  "design_notes": "...",
  "status": "complete"
}
```

---

### maestro_abort

Abort and cleanup a MAESTRO session.

**Arguments:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Session ID to abort |

**Returns:**

```json
{
  "success": true,
  "message": "Session aborted successfully"
}
```

---

## Python API

### Maestro Class (v1)

```python
from gemini_mcp.maestro.core import Maestro
from gemini_mcp.maestro.models import Answer

class Maestro:
    def __init__(
        self,
        client: Any,  # GeminiClient
        dna_store: DNAStore | None = None,
    ) -> None: ...

    async def start_session(
        self,
        project_context: str = "",
        existing_html: str | None = None,
    ) -> tuple[str, Question]:
        """Start a new session, returns (session_id, first_question)."""

    async def process_answer(
        self,
        session_id: str,
        answer: Answer,
    ) -> Question | MaestroDecision:
        """Process an answer, returns next question or final decision."""

    async def get_final_decision(
        self,
        session_id: str,
    ) -> MaestroDecision:
        """Force decision with current answers."""

    async def execute(
        self,
        session_id: str,
        use_trifecta: bool = False,
        quality_target: str = "production",
    ) -> dict[str, Any]:
        """Execute the decision and generate design output."""

    def abort_session(self, session_id: str) -> bool:
        """Abort and cleanup session."""
```

---

### MAESTROv2Wrapper (v2 - NEW)

```python
from gemini_mcp.maestro import MAESTROv2Wrapper

class MAESTROv2Wrapper:
    """
    v2 wrapper with soul-aware interview capabilities.
    Creates legacy Maestro internally for backward compatibility.
    """

    def __init__(
        self,
        client: Any,  # GeminiClient
        config: MAESTROConfig | None = None,
    ) -> None:
        """
        Initialize v2 wrapper.

        Note: Creates legacy_maestro internally.
        """
        ...

    async def start_session(
        self,
        design_brief: str | None = None,
        project_context: str = "",
        existing_html: str | None = None,
    ) -> tuple[str, SoulAwareSessionResult]:
        """
        Start a soul-aware session.

        If design_brief is provided:
        - Extracts ProjectSoul using Gemini
        - Detects gaps and generates dynamic questions
        - Returns soul + first gap-filling question

        Falls back to v1 if design_brief is empty or extraction fails.
        """
        ...

    async def process_answer(
        self,
        session_id: str,
        answer: Answer,
    ) -> SoulAwareSessionResult:
        """Process answer and update soul with new information."""
        ...

    async def execute(
        self,
        session_id: str,
        use_trifecta: bool = False,
        quality_target: str = "production",
    ) -> dict[str, Any]:
        """Execute with soul-informed design parameters."""
        ...
```

---

### SoulAwareSession (v2 - NEW)

```python
from gemini_mcp.maestro import SoulAwareSession, SessionState

class SoulAwareSession:
    """
    Session with integrated ProjectSoul.
    Uses state machine for interview flow.
    """

    @property
    def state(self) -> SessionState:
        """Current session state."""

    @property
    def soul(self) -> ProjectSoul | None:
        """Extracted project soul (None until extraction)."""

    @property
    def current_phase(self) -> InterviewPhase:
        """Current interview phase."""

    def set_soul(self, soul: ProjectSoul) -> None:
        """
        Attach extracted soul to session.
        Automatically transitions to GATHERING_CONTEXT state.
        """
        ...

    def get_analytics(self) -> dict[str, Any]:
        """
        Get session analytics including:
        - phases_completed: list[str]
        - answers_collected: int
        - confidence_history: list[float]
        - duration_seconds: float
        """
        ...


class SessionState(Enum):
    """v2 Session states."""
    CREATED = "created"
    GATHERING_CONTEXT = "gathering_context"
    DEEP_DIVE = "deep_dive"
    VISUAL = "visual"
    VALIDATION = "validation"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETE = "complete"
    FAILED = "failed"
```

---

### Models

#### Question

```python
@dataclass
class Question:
    id: str                      # e.g., "q_intent_main"
    category: QuestionCategory   # Intent, Scope, Theme, etc.
    text: str                    # Question text (Turkish)
    options: list[QuestionOption]
    question_type: QuestionType  # single_choice, multi_choice, etc.
    required: bool = True
    show_when: str | None = None  # Condition expression
```

#### QuestionOption

```python
@dataclass
class QuestionOption:
    id: str          # e.g., "opt_new_design"
    label: str       # Display text
    description: str # Additional context
    icon: str        # Emoji or icon
```

#### Answer

```python
@dataclass
class Answer:
    question_id: str
    selected_options: list[str] = field(default_factory=list)
    free_text: str | None = None
    slider_value: float | None = None
```

#### MaestroDecision

```python
@dataclass
class MaestroDecision:
    mode: str              # design_frontend, design_page, etc.
    confidence: float      # 0.0 to 1.0
    parameters: dict       # Mode-specific parameters
    reasoning: str         # Decision explanation
    alternatives: list     # Alternative modes considered
```

---

### InterviewEngine

```python
class InterviewEngine:
    def __init__(
        self,
        question_bank: QuestionBank,
        flow_controller: FlowController,
        context: ContextData,
    ) -> None: ...

    def get_next_question(self, state: InterviewState) -> Question | None:
        """Get next question based on state and skip rules."""

    def process_answer(self, state: InterviewState, answer: Answer) -> AnswerResult:
        """Validate and process an answer."""

    def calculate_progress(self, state: InterviewState) -> float:
        """Calculate interview progress (0.0 to 1.0)."""

    def is_complete(self, state: InterviewState) -> bool:
        """Check if all required questions answered."""
```

---

### DecisionTree

```python
class DecisionTree:
    async def make_decision(
        self,
        state: InterviewState,
        previous_html: str | None = None,
        image_path: str | None = None,
    ) -> MaestroDecision:
        """
        Analyze answers and select optimal mode.

        Uses 6-dimension scoring:
        - Intent clarity (25%)
        - Scope definition (20%)
        - Style specification (15%)
        - Context availability (15%)
        - Content readiness (15%)
        - Technical completeness (10%)
        """
```

---

### FlowController

```python
class FlowController:
    def should_skip(
        self,
        question_id: str,
        category: QuestionCategory,
        state: InterviewState,
    ) -> bool:
        """Check if question should be skipped."""

    def evaluate_show_when(
        self,
        condition: str | None,
        state: InterviewState,
    ) -> bool:
        """Evaluate show_when condition."""

    def get_follow_ups(
        self,
        question_id: str,
        selected_options: list[str],
    ) -> list[str]:
        """Get follow-up questions triggered by answer."""
```

---

## Question IDs Reference

### Intent Category
- `q_intent_main` - Main intent (new/refine/reference)

### Scope Category
- `q_scope_type` - Design scope (page/section/component)
- `q_page_type` - Page type (landing/dashboard/auth/etc.)
- `q_section_type` - Section type (hero/features/pricing/etc.)
- `q_component_type` - Component type (button/card/form/etc.)

### Existing Context Category
- `q_existing_action` - Action for existing HTML
- `q_reference_upload` - Reference image path
- `q_reference_adherence` - How closely to match reference

### Industry Category
- `q_target_audience` - B2B/B2C/Internal
- `q_industry_type` - Industry vertical
- `q_formality_level` - Formal/Semi-formal/Casual

### Theme Category
- `q_theme_preference` - Theme preset selection
- `q_color_mode` - Light/Dark/Both
- `q_color_preference` - Warm/Cool/Neutral
- `q_brand_primary_color` - Brand color (color picker)

### Vibe Category
- `q_design_vibe` - Design personality

### Content Category
- `q_content_ready` - Content readiness
- `q_content_input` - Content details (text input)

### Technical Category
- `q_technical_level` - Beginner/Intermediate/Expert
- `q_border_radius` - Corner style
- `q_animation_level` - Animation intensity

### Accessibility Category
- `q_accessibility_level` - WCAG AA/AAA

### Language Category
- `q_content_language` - Turkish/English/German

---

## Option IDs Reference

### Intent Options
- `opt_new_design` - Create new design
- `opt_refine` - Refine existing
- `opt_from_reference` - Design from reference image

### Scope Options
- `opt_full_page` - Full page layout
- `opt_section` - Single section
- `opt_component` - Single component

### Theme Options
- `opt_modern_minimal` - Modern Minimal
- `opt_corporate` - Corporate
- `opt_gradient` - Gradient
- `opt_dark_mode_first` - Dark Mode First
- `opt_brutalist` - Brutalist
- `opt_glassmorphism` - Glassmorphism
- `opt_neo_brutalism` - Neo Brutalism
- `opt_soft_ui` - Soft UI (Neumorphism)
- `opt_cyberpunk` - Cyberpunk
- `opt_retro` - Retro
- `opt_pastel` - Pastel
- `opt_high_contrast` - High Contrast
- `opt_nature` - Nature
- `opt_startup` - Startup

---

## Error Handling

### Session Errors

```python
# Invalid session ID
result = await maestro.process_answer("invalid_id", answer)
# Returns: {"error": "Session not found: invalid_id", "status": "failed"}

# Session expired
result = await maestro.process_answer("maestro_expired", answer)
# Returns: {"error": "Session expired", "status": "failed"}
```

### Validation Errors

```python
# Unknown question ID
answer = Answer(question_id="unknown_q", selected_options=["opt_x"])
# Returns: {"error": "Soru bulunamadı: unknown_q", "is_valid": false}

# Invalid option for question
answer = Answer(question_id="q_intent_main", selected_options=["invalid_opt"])
# Returns: {"error": "Geçersiz seçenek: invalid_opt", "is_valid": false}
```

### Execution Errors

```python
# No decision ready
result = await maestro.execute("maestro_interviewing")
# Returns: {"error": "No decision ready", "status": "failed"}
```

---

## v2 Models Reference (NEW)

### ProjectSoul

```python
from gemini_mcp.maestro.models.soul import ProjectSoul

@dataclass
class ProjectSoul:
    """The 'soul' of a project - captures its essence."""

    # Unique identifier
    id: str

    # Core metadata
    metadata: ProjectMetadata

    # Brand personality (Aaker Framework)
    brand_personality: BrandPersonality

    # Target audience profile
    target_audience: AudienceProfile

    # Visual language preferences
    visual_language: VisualLanguage

    # Emotional framework
    emotional_framework: EmotionalFramework

    # Confidence scores (0.0 - 1.0)
    confidence_scores: ConfidenceScores

    # Gap analysis
    gap_analysis: GapAnalysis

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Source brief (original text)
    source_brief: str | None = None
```

---

### BrandPersonality (Aaker Framework)

```python
@dataclass
class BrandPersonality:
    """
    Aaker's 5-dimension brand personality model.
    Each dimension is scored 0.0 to 1.0.
    """

    sincerity: float       # Honest, wholesome, cheerful
    excitement: float      # Daring, spirited, imaginative
    competence: float      # Reliable, intelligent, successful
    sophistication: float  # Upper class, charming
    ruggedness: float      # Outdoorsy, tough

    # Derived traits
    dominant_trait: str    # "sincerity" | "excitement" | etc.
    archetype: str         # "The Hero", "The Sage", "The Creator", etc.
```

**Archetype Mapping:**

| Dominant Trait | Archetype |
|----------------|-----------|
| sincerity | "The Innocent", "The Caregiver" |
| excitement | "The Hero", "The Rebel" |
| competence | "The Sage", "The Expert" |
| sophistication | "The Ruler", "The Magician" |
| ruggedness | "The Explorer", "The Outlaw" |

---

### EmotionalFramework

```python
from gemini_mcp.maestro.models.emotion import (
    EmotionalFramework,
    EmotionalTone,
    Emotion
)

class EmotionalTone(Enum):
    """Available emotional tones for design."""
    PROFESSIONAL = "professional"
    OPTIMISTIC = "optimistic"
    INNOVATIVE = "innovative"
    TRUSTWORTHY = "trustworthy"
    PLAYFUL = "playful"
    BOLD = "bold"
    ELEGANT = "elegant"
    MINIMAL = "minimal"

@dataclass
class EmotionalFramework:
    """Emotional goals for the design."""

    primary_emotion: Emotion      # Main feeling to evoke
    secondary_emotion: Emotion    # Supporting emotion
    primary_tone: EmotionalTone   # Communication style
    secondary_tone: EmotionalTone
    avoid_emotions: list[str]     # Emotions to avoid
```

---

### GapAnalysis

```python
from gemini_mcp.maestro.models.gap import GapAnalysis, GapInfo, GapPriority

class GapPriority(Enum):
    """Priority levels for information gaps."""
    CRITICAL = "critical"      # Blocks design
    IMPORTANT = "important"    # Affects quality
    NICE_TO_HAVE = "nice_to_have"

@dataclass
class GapInfo:
    """Information about a specific gap."""

    field: str                 # e.g., "visual_language.colors"
    priority: GapPriority
    current_value: Any | None  # What we have (if anything)
    suggested_question: str    # Question to fill gap
    reason: str               # Why this gap matters

@dataclass
class GapAnalysis:
    """Analysis of all gaps in extracted soul."""

    gaps: list[GapInfo]
    critical_count: int
    important_count: int
    nice_to_have_count: int

    @property
    def total_gaps(self) -> int:
        return len(self.gaps)

    @property
    def has_critical_gaps(self) -> bool:
        return self.critical_count > 0
```

---

### ConfidenceScores

```python
@dataclass
class ConfidenceScores:
    """Confidence levels for each extraction dimension."""

    brand: float      # Brand personality confidence
    audience: float   # Target audience confidence
    visual: float     # Visual language confidence
    emotion: float    # Emotional framework confidence
    overall: float    # Weighted average

    def is_sufficient(self, threshold: float = 0.6) -> bool:
        """Check if overall confidence is above threshold."""
        return self.overall >= threshold
```

---

### InterviewPhase

```python
from gemini_mcp.maestro.models.soul import InterviewPhase

class InterviewPhase(Enum):
    """Interview phases for v2 state machine."""

    INITIAL = "initial"
    SOUL_EXTRACTION = "extraction"
    CONTEXT_GATHERING = "gathering"
    DEEP_DIVE = "deep_dive"
    VISUAL_EXPLORATION = "visual"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"
    EXECUTION = "execution"
    COMPLETE = "complete"
```

---

## Turkish Prompt Templates

v2 includes Turkish prompt templates for all user-facing messages:

### Extraction Prompts
- `SOUL_EXTRACTION_PROMPT` - Extract ProjectSoul from brief
- `GAP_DETECTION_PROMPT` - Identify missing information
- `BRIEF_ANALYSIS_PROMPT` - Analyze brief quality
- `SYNTHESIS_PROMPT` - Synthesize final design parameters

### Feedback Messages
- `VALIDATION_MESSAGES` - Field validation errors
- `ERROR_MESSAGES` - Error handling with recovery actions
- `SUCCESS_MESSAGES` - Success confirmations with emojis

### Helper Functions

```python
from gemini_mcp.maestro.prompts.tr.extraction import (
    build_soul_extraction_request,
    build_gap_detection_request,
    build_synthesis_request,
)

from gemini_mcp.maestro.prompts.tr.feedback import (
    get_validation_message,
    get_error_message,
    get_success_message,
    format_error_for_display,
    format_success_for_display,
)

# Example usage
error = get_error_message("session_expired")
# {"title": "Oturum Sona Erdi", "message": "...", "action": "Yeni Oturum"}

success = format_success_for_display("soul_extracted")
# "✨ Proje Ruhu Çıkarıldı: Projenizin kimliği başarıyla belirlendi."
```
