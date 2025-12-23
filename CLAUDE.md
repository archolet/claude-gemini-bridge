# Claude Gemini Bridge

## Quick Start

```bash
# Install dependencies
uv sync

# Run MCP server
uv run gemini-mcp

# Run tests (excludes API-dependent tests)
uv run pytest --ignore=tests/test_phase4_ux.py

# Run specific test file
uv run pytest tests/test_phase1_gaps.py -v
```

## Environment

```bash
# Required
export GOOGLE_CLOUD_PROJECT="your-project-id"
gcloud auth application-default login

# Optional
export GOOGLE_CLOUD_LOCATION="global"
export GEMINI_DRAFT_DIR="./temp_designs"
```

## Gemini 3 API Configuration

### Critical Settings
- **Temperature**: MUST be `1.0` (Gemini 3's reasoning engine is optimized for this; lowering may cause looping)
- **thinking_level**: Controls reasoning depth
  - `high`: Complex tasks requiring deep analysis
  - `low`: Latency-sensitive generation tasks
  - `minimal`: Flash model only (not used in this project)

### Thought Signatures
Required for multi-turn Gemini 3 conversations. Managed in `AgentContext`:
```python
context.add_thought_signature(signature)      # Store signature from response
context.get_latest_signatures(count=3)        # Get recent signatures
context.get_signatures_for_request()          # Format for next API call
```

## Architecture

### Entry Point
- `src/gemini_mcp/server.py` - Main MCP server with all design tools

### Design Tools (MCP)
| Tool | Purpose |
|------|---------|
| `design_frontend` | Component design (button, card, navbar, etc.) |
| `design_page` | Full page layouts (landing, dashboard, auth) |
| `design_section` | Single section with style consistency |
| `refine_frontend` | Iterate on existing designs |
| `replace_section_in_page` | Surgical section replacement |
| `design_from_reference` | Design based on reference images |
| `generate_image` | Image asset generation |
| `validate_theme_contrast` | WCAG accessibility validation |

### Multi-Agent System (Trifecta Engine)
Located in `src/gemini_mcp/agents/`:

| Agent | File | Role | thinking_level |
|-------|------|------|----------------|
| Architect | `architect.py` | HTML structure + Tailwind classes | high |
| Alchemist | `alchemist.py` | Premium CSS effects | low |
| Physicist | `physicist.py` | Vanilla JS interactions | low |
| Strategist | `strategist.py` | Planning & Design DNA extraction | high |
| QualityGuard | `quality_guard.py` | QA validation | low |
| Critic | `critic.py` | Art direction & scoring | high |
| Visionary | `visionary.py` | Vision API image analysis | high |

### Orchestration
Located in `src/gemini_mcp/orchestration/`:

| File | Purpose |
|------|---------|
| `orchestrator.py` | Pipeline execution & agent coordination |
| `pipelines.py` | Pipeline definitions (COMPONENT, PAGE, SECTION, REFINE, REFERENCE, REPLACE) |
| `context.py` | Agent context & thought signature management |
| `dna_store.py` | Design DNA storage |
| `telemetry.py` | Pipeline metrics & observability |

### Validation
Located in `src/gemini_mcp/validation/`:
- `html_validator.py` - HTML structure validation
- `css_validator.py` - CSS validation
- `js_validator.py` - JavaScript validation
- `id_validator.py` - ID conflict detection

### State Management
- `src/gemini_mcp/state.py` - DraftManager for auto-save to `temp_designs/`

## Key Patterns

### 1. Pipeline Pattern
Each design tool maps to a pipeline that orchestrates multiple agents:
```
design_frontend → COMPONENT pipeline → Architect → Alchemist → Physicist → QualityGuard
design_page     → PAGE pipeline      → Strategist → [Architect x N] → Alchemist → Physicist → QualityGuard
```

### 2. Design DNA
Style tokens (colors, typography, spacing) extracted and propagated across agents for visual consistency.

### 3. Auto-Save
All design outputs automatically saved to `temp_designs/` with:
- HTML file (`.html`)
- CSS file (`.css`) - if Trifecta enabled
- JS file (`.js`) - if Trifecta enabled
- Metadata sidecar (`.meta.json`)
- Project manifest (`manifest.json`)

### 4. CSS Quality Refinement Loop
Critic-driven iterative improvement for CSS quality:
```
Alchemist → Critic (score) → if < 8.0 → Alchemist (with feedback) → Critic → ...
```
- `QUALITY_THRESHOLD = 8.0` - Minimum acceptable score
- `MAX_REFINER_ITERATIONS = 3` - Maximum retry attempts
- **5-dimension scoring**:
  - Layout (25%) - Visual hierarchy, spacing, alignment
  - Typography (15%) - Font choices, readability
  - Color (20%) - Palette harmony, contrast
  - Interaction (15%) - Hover states, animations
  - Accessibility (25%) - WCAG compliance, focus states

## Testing

```bash
# All tests (excludes API-dependent tests)
uv run pytest --ignore=tests/test_phase4_ux.py

# Specific phase tests
uv run pytest tests/test_phase1_gaps.py -v
uv run pytest tests/test_phase2_validation.py -v
uv run pytest tests/test_phase3_performance.py -v

# With API (requires GOOGLE_CLOUD_PROJECT)
uv run pytest tests/test_phase4_ux.py -v
```

## Development

### Adding a New Design Tool
1. Add tool function in `server.py`
2. Create pipeline in `orchestration/pipelines.py` (if using Trifecta)
3. Integrate auto-save with `_auto_save_design_output()`

### Theme System
14 available themes in `frontend_presets.py`:
- modern-minimal, brutalist, glassmorphism, neo-brutalism
- soft-ui, corporate, gradient, cyberpunk
- retro, pastel, dark_mode_first, high_contrast
- nature, startup

### Vibe System
4 vibes for design persona:
- elite_corporate, playful_funny, cyberpunk_edge, luxury_editorial
