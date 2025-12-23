# Performance Anti-Patterns Analysis

This document identifies performance issues found in the codebase with specific file locations, explanations, and suggested fixes.

## Summary

| # | Issue | Severity | File | Lines |
|---|-------|----------|------|-------|
| 1 | N+1 section extraction | HIGH | server.py | 2158-2163 |
| 2 | O(n²) string classification | HIGH | section_utils.py | 240-256 |
| 3 | Deep copying in parallel loop | MEDIUM | orchestrator.py | 646 |
| 4 | Multiple regex per element | MEDIUM | context.py | 493-514 |
| 5 | Inefficient LRU cache eviction | MEDIUM | cache.py | 135-141 |
| 6 | Regex recompilation | LOW-MEDIUM | section_utils.py | 36-55 |
| 7 | String concatenation in loop | MEDIUM | section_utils.py | 308-318 |
| 8 | Redundant body tag scan | LOW-MEDIUM | server.py | 1201-1205 |

---

## 1. N+1 Section Extraction Pattern

**File:** `src/gemini_mcp/server.py:2158-2163`

```python
for section_name in available_sections:
    if section_name != section_type:
        tokens = extract_design_tokens_from_section(page_html, section_name)
        if tokens:
            design_tokens = tokens
            break
```

**Problem:** This loop iterates through sections and calls `extract_design_tokens_from_section()` for each one. Each call performs regex searches on the full page HTML.

**Impact:** For 6 sections, worst-case is 5 full HTML regex searches (O(n) each = O(n*m) total where m = HTML size).

**Fix:**
```python
# Extract all tokens in a single pass
all_tokens = extract_all_section_tokens(page_html)  # New function
design_tokens = next(
    (tokens for name, tokens in all_tokens.items()
     if name != section_type and tokens),
    {}
)
```

---

## 2. O(n²) String Classification with List Membership

**File:** `src/gemini_mcp/section_utils.py:240-256`

```python
for cls in all_classes.split():
    if any(prefix in cls for prefix in ['bg-', 'text-', 'border-', 'ring-']):
        if cls not in tokens["colors"]:  # O(n) list search!
            tokens["colors"].append(cls)
    elif any(prefix in cls for prefix in ['font-', 'text-', 'tracking-', 'leading-']):
        if cls not in tokens["typography"]:  # O(n) list search!
            tokens["typography"].append(cls)
    # ... more categories
```

**Problems:**
1. `any()` with inline list creation for every class
2. `if cls not in tokens[...]` is O(n) list membership check
3. Combined: O(n²) complexity for n classes

**Impact:** For 1000 CSS classes: ~4000+ `any()` calls and list membership searches.

**Fix:**
```python
# Use sets and precomputed prefix tuples
COLOR_PREFIXES = ('bg-', 'text-', 'border-', 'ring-')
TYPO_PREFIXES = ('font-', 'text-', 'tracking-', 'leading-')

tokens = {
    "colors": set(),      # O(1) membership
    "typography": set(),
    "spacing": set(),
    "effects": set(),
}

for cls in all_classes.split():
    if cls.startswith(COLOR_PREFIXES):  # Single tuple check
        tokens["colors"].add(cls)  # O(1) add with dedup
    elif cls.startswith(TYPO_PREFIXES):
        tokens["typography"].add(cls)
    # ...

# Convert back to lists if needed
return {k: list(v) for k, v in tokens.items()}
```

---

## 3. Deep Copying Context in Parallel Loop

**File:** `src/gemini_mcp/orchestration/orchestrator.py:646`

```python
for idx, step in enumerate(group.steps):
    # Create a copy of context for each parallel execution
    step_context = context.copy()  # Expensive deep copy
```

**Problem:** `context.copy()` performs a deep copy of `AgentContext`, which includes:
- Large dictionaries (`style_guide`, `content_structure`)
- Lists (`thought_signatures`, `sections`, `errors`, `warnings`)
- Nested dataclasses (`design_dna`, `compressed`)

**Impact:** For 6 parallel sections, 6 full deep copies are created, causing GC pressure and latency.

**Fix:**
```python
# Option 1: Copy-on-write with selective copying
step_context = context.shallow_copy()
step_context.current_section_index = idx  # Only copy what changes

# Option 2: Use frozen/immutable shared context with local overrides
step_context = context.with_overrides(
    current_section_index=idx,
    current_section_type=section_type,
)
```

---

## 4. Multiple Regex Searches Per HTML Element

**File:** `src/gemini_mcp/orchestration/context.py:493-514`

```python
element_pattern = r"<(\w+)([^>]*?)>"

for match in re.finditer(element_pattern, html):  # Pass 1
    attributes_str = match.group(2)

    if "data-interaction" not in attributes_str:
        continue

    id_match = re.search(r'id=["\']([^"\']+)["\']', attributes_str)  # Pass 2

    data_pattern = r'data-(\w+)=["\']([^"\']+)["\']'
    for attr_match in re.finditer(data_pattern, attributes_str):  # Pass 3+
        # ...
```

**Problem:** 3 separate regex operations per element with `data-interaction`:
1. Main element pattern
2. ID extraction
3. Data attribute extraction

**Impact:** For 100 interactive elements: 300+ regex operations.

**Fix:**
```python
# Combined single-pass regex with named groups
INTERACTIVE_PATTERN = re.compile(
    r'<(\w+)[^>]*?'
    r'id=["\'](?P<id>[^"\']+)["\']'
    r'[^>]*?data-interaction=["\'](?P<interaction>[^"\']+)["\']'
    r'[^>]*?(?:data-(?P<data_name>\w+)=["\'](?P<data_value>[^"\']+)["\'])*',
    re.DOTALL
)

# Or use an HTML parser for robustness
from html.parser import HTMLParser
```

---

## 5. Inefficient LRU Cache Eviction

**File:** `src/gemini_mcp/cache.py:135-141`

```python
while len(self._cache) >= self._max_entries:
    oldest_key = min(
        self._cache.keys(),  # O(n) key iteration
        key=lambda k: self._cache[k].last_accessed  # O(n) lookups
    )
    del self._cache[oldest_key]
```

**Problem:**
- `min()` is O(n) in cache size
- Called in a while loop for multiple evictions
- Evicting k entries from n cache = O(k × n)

**Impact:** Cache with 100 entries needing 10 evictions = 1000 comparisons.

**Fix:**
```python
from heapq import heappush, heappop

class DesignCache:
    def __init__(self, ...):
        self._cache: Dict[str, CacheEntry] = {}
        self._lru_heap: list[tuple[float, str]] = []  # (timestamp, key)

    def _evict_if_needed(self) -> int:
        evicted = 0
        while len(self._cache) >= self._max_entries and self._lru_heap:
            _, key = heappop(self._lru_heap)  # O(log n)
            if key in self._cache:
                del self._cache[key]
                evicted += 1
        return evicted
```

---

## 6. Repeated Regex Pattern Compilation

**File:** `src/gemini_mcp/section_utils.py:36-55`

```python
def extract_section(html: str, section_name: str) -> Optional[str]:
    pattern = rf'<!-- SECTION: {section_name} -->(.*?)<!-- /SECTION: {section_name} -->'
    match = re.search(pattern, html, re.DOTALL)  # Compiles each call
    return match.group(1).strip() if match else None
```

**Problem:** Regex pattern is recompiled on every function call, even for the same section name.

**Impact:** For 6 sections processed repeatedly, 10+ unnecessary regex compilations.

**Fix:**
```python
from functools import lru_cache

@lru_cache(maxsize=32)
def _get_section_pattern(section_name: str) -> re.Pattern:
    return re.compile(
        rf'<!-- SECTION: {section_name} -->(.*?)<!-- /SECTION: {section_name} -->',
        re.DOTALL
    )

def extract_section(html: str, section_name: str) -> Optional[str]:
    pattern = _get_section_pattern(section_name)
    match = pattern.search(html)
    return match.group(1).strip() if match else None
```

---

## 7. String Concatenation in Loop

**File:** `src/gemini_mcp/section_utils.py:308-318`

```python
def migrate_to_markers(html: str, section_mapping: Dict[str, str]) -> str:
    result = html

    for pattern, section_type in section_mapping.items():
        if pattern.startswith("<"):
            # ...
            if match:
                wrapped = wrap_content_with_markers(match.group(1), section_type)
                result = result[:match.start()] + wrapped + result[match.end():]  # O(n) copy
```

**Problem:** String concatenation creates a new string on each iteration, copying the entire HTML.

**Impact:** For 6 sections: 6 full HTML copies = O(n × m) where n = sections, m = HTML size.

**Fix:**
```python
def migrate_to_markers(html: str, section_mapping: Dict[str, str]) -> str:
    # Collect all replacements first
    replacements = []  # (start, end, wrapped_content)

    for pattern, section_type in section_mapping.items():
        if pattern.startswith("<"):
            tag = pattern[1:]
            element_pattern = rf'(<{tag}[^>]*>.*?</{tag}>)'
            match = re.search(element_pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                wrapped = wrap_content_with_markers(match.group(1), section_type)
                replacements.append((match.start(), match.end(), wrapped))

    # Sort by position (reverse) and apply all at once
    replacements.sort(reverse=True)
    result = html
    for start, end, wrapped in replacements:
        result = result[:start] + wrapped + result[end:]

    return result
```

Or better yet, build from parts:
```python
parts = []
last_pos = 0
for start, end, wrapped in sorted(replacements):
    parts.append(html[last_pos:start])
    parts.append(wrapped)
    last_pos = end
parts.append(html[last_pos:])
return ''.join(parts)  # Single allocation
```

---

## 8. Redundant Body Tag Scan

**File:** `src/gemini_mcp/server.py:1201-1205`

```python
if "<body" in content:  # First scan
    import re
    match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)  # Second scan
    if match:
        content = match.group(1)
```

**Problem:** Two passes over the same content:
1. `"<body" in content` - linear search
2. `re.search(...)` - regex search for same pattern

**Impact:** 2× scanning for each component (minor but easy to fix).

**Fix:**
```python
# Single regex search (regex returns None if no match)
match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
if match:
    content = match.group(1)
```

---

## Additional Recommendations

### 1. Add Caching for `extract_design_tokens_from_section`
Cache results when the same page HTML is analyzed multiple times.

### 2. Use `__slots__` on Dataclasses
Reduce memory overhead for frequently-instantiated classes like `CacheEntry`, `AgentContext`.

### 3. Consider Lazy Initialization
For `AgentContext.compressed` and `AgentContext.design_dna`, defer initialization until first access.

### 4. Profile API Calls
The biggest performance impact is likely Gemini API calls. Consider:
- Batching requests where possible
- Implementing request deduplication
- Adding circuit breakers for rate limiting

---

## Testing Performance Fixes

After implementing fixes, measure with:

```python
import cProfile
import pstats

# Profile section token extraction
profiler = cProfile.Profile()
profiler.enable()
# ... run code ...
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(20)
```

Or use `py-spy` for production profiling:
```bash
py-spy record -o profile.svg -- python -m gemini_mcp.server
```
