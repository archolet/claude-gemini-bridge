# Gemini MCP - Stress Test Bug Report
**Date**: 2025-12-25
**Test Session**: 6 Mode Stress Test

---

## BUG #1: Trifecta Pipeline Returns Empty HTML ✅ FIXED

**Severity**: 🔴 CRITICAL → ✅ RESOLVED

**Reproduction Steps**:
```python
mcp__gemini__design_section(
    section_type="hero",
    context="Hero section for a bold fintech startup",
    theme="brutalist",
    use_trifecta=True  # <-- Previously bugged, NOW WORKS
)
```

**Error Messages** (before fix):
```
'str' object has no attribute 'get'
'str' object has no attribute 'get'
'str' object has no attribute 'get'
```

### Root Cause Analysis

**Problem**: Type mismatch in few-shot examples handling.

| Location | Expected | Actual |
|----------|----------|--------|
| `context.few_shot_examples` | `list[dict[str, Any]]` | `list[str]` (characters!) |
| `get_few_shot_examples_for_prompt()` | N/A | Returns `str` for prompts |

**Bug Mechanism**:
```python
# In orchestrator._prepare_few_shot_examples (BEFORE FIX):
component_examples = get_few_shot_examples_for_prompt(...)  # Returns STRING
examples.extend(component_examples)  # String.extend() adds CHARACTERS!
# Result: examples = ['<', '!', 'D', 'O', 'C', 'T', ...]

# In architect.py:
for example in context.few_shot_examples:
    example.get("component_type")  # '<'.get() → AttributeError!
```

### Fix Applied

**File**: `src/gemini_mcp/orchestration/orchestrator.py`

**Changes**:
1. Added import: `from gemini_mcp.few_shot_examples import COMPONENT_EXAMPLES`
2. Rewrote `_prepare_few_shot_examples()` to extract dicts directly:

```python
# AFTER FIX:
if component_type and component_type in COMPONENT_EXAMPLES:
    example_data = COMPONENT_EXAMPLES[component_type]
    output = example_data.get("output", {})
    examples.append({  # append dict, not extend string!
        "component_type": component_type,
        "html": output.get("html", ""),
        "css": output.get("css", ""),
        "js": output.get("js", ""),
    })
```

**Verification**: All component types now pass `example.get()` calls.

**Fix Date**: 2025-12-25

---

## BUG #2: External Resource SSL Error (Minor)

**Severity**: 🟡 LOW

**Issue**: Grainy gradient texture fails to load
```
Failed to load resource: net::ERR_SSL_PROTOCOL_ERROR
@ https://grainy-gradients.vercel.app/noise.svg
```

**Impact**: Visual texture missing, not critical
**Fix**: Use local base64 encoded SVG or different CDN

---

## Tests Completed Successfully ✅

| Test | Mode | Theme/Task | Result |
|------|------|------------|--------|
| TEST 1 | design_frontend | Cyberpunk pricing card | ✅ PASSED (trifecta=true worked) |
| TEST 2 | design_page | SaaS landing page | ✅ PASSED |
| TEST 3 | design_section | Brutalist fintech hero | ✅ PASSED (trifecta=true NOW WORKS) |
| TEST 4 | refine_frontend | Fintech → Wellness transform | ✅ PASSED |
| TEST 5 | replace_section_in_page | Surgical cyberpunk hero | ✅ PASSED |
| TEST 6 | design_from_reference | Vision-based pricing card | ✅ PASSED |

**Summary**: 6/6 modes working. 1 critical bug found and FIXED (Trifecta + design_section combo).
