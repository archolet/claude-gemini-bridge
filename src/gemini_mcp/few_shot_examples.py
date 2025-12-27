"""Few-shot examples for Gemini design prompts.

This module uses lazy loading to defer memory allocation until examples
are actually accessed. The raw example data is stored in examples/_data.py.

Usage:
    from gemini_mcp.few_shot_examples import COMPONENT_EXAMPLES, get_few_shot_examples_for_prompt

    # Lazy - data not loaded yet
    examples = COMPONENT_EXAMPLES

    # First access triggers load
    button_example = examples["button"]
"""

from __future__ import annotations

import random
from typing import Any, Optional

from .examples._loader import LazyDict


# =============================================================================
# LAZY LOADING FUNCTIONS
# =============================================================================

def _load_component_examples() -> dict[str, dict[str, Any]]:
    """Load component examples on first access."""
    from .examples._data import COMPONENT_EXAMPLES
    return COMPONENT_EXAMPLES


def _load_section_chain_examples() -> dict[str, dict[str, Any]]:
    """Load section chain examples on first access."""
    from .examples._data import SECTION_CHAIN_EXAMPLES
    return SECTION_CHAIN_EXAMPLES


def _load_bad_examples() -> dict[str, dict[str, Any]]:
    """Load bad examples on first access."""
    from .examples._data import BAD_EXAMPLES
    return BAD_EXAMPLES


def _load_corporate_examples() -> dict[str, dict[str, Any]]:
    """Load corporate examples on first access."""
    from .examples._data import CORPORATE_EXAMPLES
    return CORPORATE_EXAMPLES


# =============================================================================
# LAZY DICT INSTANCES
# =============================================================================

COMPONENT_EXAMPLES: LazyDict = LazyDict(_load_component_examples)
SECTION_CHAIN_EXAMPLES: LazyDict = LazyDict(_load_section_chain_examples)
BAD_EXAMPLES: LazyDict = LazyDict(_load_bad_examples)
CORPORATE_EXAMPLES: LazyDict = LazyDict(_load_corporate_examples)


# =============================================================================
# LAZY INDIVIDUAL EXPORTS
# =============================================================================

class _LazyExampleLoader:
    """Lazy loader for pre-computed example exports from _data.py."""

    __slots__ = ("_name", "_cache")

    def __init__(self, name: str):
        self._name = name
        self._cache: dict[str, Any] | None = None

    def _get(self) -> dict[str, Any]:
        if self._cache is None:
            from .examples import _data
            self._cache = getattr(_data, self._name)
        return self._cache

    def __getitem__(self, key: str) -> Any:
        return self._get()[key]

    def __contains__(self, key: object) -> bool:
        return key in self._get()

    def get(self, key: str, default: Any = None) -> Any:
        return self._get().get(key, default)

    def keys(self):
        return self._get().keys()

    def values(self):
        return self._get().values()

    def items(self):
        return self._get().items()


# Vibe examples (convenience exports) - lazily loaded from _data.py
CYBERPUNK_EDGE_EXAMPLE = _LazyExampleLoader("CYBERPUNK_EDGE_EXAMPLE")
LUXURY_EDITORIAL_EXAMPLE = _LazyExampleLoader("LUXURY_EDITORIAL_EXAMPLE")


# =============================================================================
# ACCESSOR FUNCTIONS
# =============================================================================

def get_few_shot_examples_for_prompt(
    component_type: str,
    theme: str = "modern-minimal",
    max_examples: int = 3,
    include_bad_examples: bool = True,
    vibe: str = "",
) -> str:
    """Get formatted few-shot examples for a design prompt.

    Args:
        component_type: Type of component being designed (e.g., "button", "card").
        theme: The theme being used.
        max_examples: Maximum number of examples to include.
        include_bad_examples: Whether to include examples of what NOT to do.
        vibe: Optional vibe for style guidance.

    Returns:
        Formatted string with few-shot examples for the prompt.
    """
    examples_text = []

    # Get examples from COMPONENT_EXAMPLES
    relevant_keys = []
    for key in COMPONENT_EXAMPLES.keys():
        example = COMPONENT_EXAMPLES[key]
        if isinstance(example.get("input"), dict):
            if example["input"].get("component_type") == component_type:
                relevant_keys.append(key)
        elif component_type.lower() in key.lower():
            relevant_keys.append(key)

    # Limit to max_examples
    selected_keys = relevant_keys[:max_examples] if relevant_keys else list(COMPONENT_EXAMPLES.keys())[:max_examples]

    for key in selected_keys:
        example = COMPONENT_EXAMPLES[key]
        output = example.get("output", {})
        html = output.get("html", "")
        design_thinking = output.get("design_thinking", "")

        if html:
            examples_text.append(f"### Example: {key}\n")
            if design_thinking:
                examples_text.append(f"**Design Thinking:** {design_thinking}\n")
            examples_text.append(f"```html\n{html.strip()}\n```\n")

    # Add bad examples if requested
    if include_bad_examples and BAD_EXAMPLES:
        examples_text.append("\n## What NOT to Do:\n")
        bad_keys = list(BAD_EXAMPLES.keys())[:2]
        for key in bad_keys:
            bad_example = BAD_EXAMPLES[key]
            # bad_output is a string (HTML directly), not a dict
            bad_html = bad_example.get("bad_output", "")
            # why_bad is a list of reasons
            why_bad = bad_example.get("why_bad", [])
            if bad_html:
                examples_text.append(f"### Bad Example: {key}\n")
                if why_bad:
                    reason_str = "; ".join(why_bad) if isinstance(why_bad, list) else str(why_bad)
                    examples_text.append(f"**Why this is bad:** {reason_str}\n")
                examples_text.append(f"```html\n{bad_html.strip()}\n```\n")

    return "\n".join(examples_text)


def get_bad_examples_for_prompt(
    component_type: str = "",
    max_examples: int = 2,
    include_corrections: bool = True,
) -> str:
    """Get formatted bad examples showing what NOT to do.

    Args:
        component_type: Optional filter by component type.
        max_examples: Maximum number of bad examples to include.
        include_corrections: Whether to include the corrected versions.

    Returns:
        Formatted string with bad examples for the prompt.
    """
    examples_text = ["## Common Mistakes to Avoid:\n"]

    # Filter by component type if specified
    relevant_keys = []
    for key in BAD_EXAMPLES.keys():
        example = BAD_EXAMPLES[key]
        if component_type:
            input_data = example.get("input", {})
            if isinstance(input_data, dict) and input_data.get("component_type") == component_type:
                relevant_keys.append(key)
            elif component_type.lower() in key.lower():
                relevant_keys.append(key)
        else:
            relevant_keys.append(key)

    selected_keys = relevant_keys[:max_examples]

    for key in selected_keys:
        example = BAD_EXAMPLES[key]
        # bad_output is a string (HTML directly), not a dict
        bad_html = example.get("bad_output", "")
        # why_bad is a list of reasons
        why_bad = example.get("why_bad", [])
        # good_alternative contains the corrected version
        good_alternative = example.get("good_alternative", "")

        if bad_html:
            examples_text.append(f"### Mistake: {key}\n")
            examples_text.append(f"```html\n{bad_html.strip()}\n```\n")

            if why_bad:
                if isinstance(why_bad, list):
                    examples_text.append("**Problems:**\n")
                    for reason in why_bad:
                        examples_text.append(f"- {reason}\n")
                else:
                    examples_text.append(f"**Problem:** {why_bad}\n")

            if include_corrections and good_alternative:
                examples_text.append("**Corrected version:**\n")
                examples_text.append(f"```html\n{good_alternative.strip()}\n```\n")

            examples_text.append("\n")

    return "\n".join(examples_text)


def get_corporate_examples_for_prompt(
    industry: str = "",
    formality: str = "semi-formal",
    max_examples: int = 2,
    include_design_tokens: bool = True,
) -> str:
    """Get formatted corporate theme examples for a design prompt.

    These examples demonstrate enterprise-grade design patterns with
    industry-specific considerations.

    Args:
        industry: Filter by industry (finance, healthcare, legal, tech, etc.).
        formality: Formality level (formal, semi-formal, approachable).
        max_examples: Maximum number of examples to include.
        include_design_tokens: Whether to include extracted design tokens.

    Returns:
        Formatted string with corporate examples for the prompt.
    """
    examples_text = ["## Enterprise Design Examples:\n"]

    # Filter by industry if specified
    relevant_keys = []
    for key in CORPORATE_EXAMPLES.keys():
        example = CORPORATE_EXAMPLES[key]
        input_data = example.get("input", {})

        if isinstance(input_data, dict):
            example_industry = input_data.get("industry", "")
            example_formality = input_data.get("formality", "semi-formal")

            # Match by industry if specified
            if industry and example_industry != industry:
                continue

            # Match by formality
            if formality and example_formality != formality:
                continue

            relevant_keys.append(key)
        else:
            # Include if no filter matches
            relevant_keys.append(key)

    # If no matches, include all
    if not relevant_keys:
        relevant_keys = list(CORPORATE_EXAMPLES.keys())

    selected_keys = relevant_keys[:max_examples]

    for key in selected_keys:
        example = CORPORATE_EXAMPLES[key]
        input_data = example.get("input", {})
        output = example.get("output", {})
        html = output.get("html", "")
        design_thinking = output.get("design_thinking", "")

        if html:
            examples_text.append(f"### Corporate Example: {key}\n")

            # Show input context
            if isinstance(input_data, dict):
                industry_str = input_data.get("industry", "general")
                formality_str = input_data.get("formality", "semi-formal")
                examples_text.append(f"**Industry:** {industry_str} | **Formality:** {formality_str}\n")

            if design_thinking:
                examples_text.append(f"**Design Thinking:** {design_thinking}\n")

            examples_text.append(f"```html\n{html.strip()}\n```\n")

            # Include design tokens if requested
            if include_design_tokens:
                tokens = output.get("design_tokens", {})
                if tokens:
                    examples_text.append("\n**Extracted Design Tokens:**\n")
                    examples_text.append("```json\n")

                    # Format tokens nicely
                    colors = tokens.get("colors", {})
                    if colors:
                        examples_text.append(f'  "colors": {colors},\n')

                    typography = tokens.get("typography", {})
                    if typography:
                        examples_text.append(f'  "typography": {typography},\n')

                    spacing = tokens.get("spacing", {})
                    if spacing:
                        examples_text.append(f'  "spacing": {spacing}\n')

                    examples_text.append("```\n")

            examples_text.append("\n")

    return "\n".join(examples_text)


def list_corporate_examples() -> list[str]:
    """List all available corporate example keys."""
    return list(CORPORATE_EXAMPLES.keys())


def get_section_chain_examples_for_prompt(
    section_type: str = "",
    max_examples: int = 1,
) -> str:
    """Get formatted section chain examples for design consistency.

    These examples demonstrate how to maintain visual consistency
    across multiple sections using design tokens.

    Args:
        section_type: Optional filter by section type (hero, features, etc.).
        max_examples: Maximum number of chain examples to include.

    Returns:
        Formatted string with section chain examples.
    """
    examples_text = ["## Section Chain Examples (Style Consistency):\n"]

    selected_keys = list(SECTION_CHAIN_EXAMPLES.keys())[:max_examples]

    for key in selected_keys:
        chain = SECTION_CHAIN_EXAMPLES[key]
        examples_text.append(f"### Chain: {key}\n")

        # Show sections in order
        sections = chain.get("sections", [])
        design_tokens = chain.get("design_tokens", {})

        if design_tokens:
            examples_text.append("**Shared Design Tokens:**\n```json\n")
            examples_text.append(str(design_tokens))
            examples_text.append("\n```\n")

        for i, section in enumerate(sections, 1):
            section_type_name = section.get("type", "unknown")
            html = section.get("html", "")

            if section_type and section_type != section_type_name:
                continue

            examples_text.append(f"\n**Section {i}: {section_type_name}**\n")
            if html:
                examples_text.append(f"```html\n{html.strip()}\n```\n")

        examples_text.append("\n")

    return "\n".join(examples_text)


def get_vibe_example(vibe: str) -> dict[str, Any] | None:
    """Get a specific vibe example.

    Args:
        vibe: The vibe name (cyberpunk_edge, luxury_editorial, etc.).

    Returns:
        The example dict or None if not found.
    """
    vibe_map = {
        "cyberpunk_edge": "cyberpunk_edge",
        "luxury_editorial": "luxury_editorial",
        "playful_funny": "playful_funny",
        "elite_corporate": "elite_corporate",
    }

    key = vibe_map.get(vibe)
    if key and key in COMPONENT_EXAMPLES:
        return COMPONENT_EXAMPLES[key]
    return None


def get_random_examples(count: int = 3) -> list[dict[str, Any]]:
    """Get random component examples for variety in prompts.

    Args:
        count: Number of random examples to return.

    Returns:
        List of randomly selected example dicts.
    """
    keys = list(COMPONENT_EXAMPLES.keys())
    selected = random.sample(keys, min(count, len(keys)))
    return [COMPONENT_EXAMPLES[k] for k in selected]
