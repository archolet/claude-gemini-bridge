"""Section manipulation utilities for iterative component replacement.

This module provides functions to extract, replace, and manage HTML sections
marked with structured comments for iteration support.

Section Marker Format:
    <!-- SECTION: {section_type} -->
    ...section content...
    <!-- /SECTION: {section_type} -->
"""

import functools
import re
from typing import Dict, List, Optional, Tuple

# Pattern to match section markers (precompiled for extract_all_sections)
SECTION_PATTERN = re.compile(r'<!-- SECTION: (\w+) -->(.*?)<!-- /SECTION: \1 -->', re.DOTALL)

# Precompiled class extraction pattern
_CLASS_PATTERN = re.compile(r'class="([^"]*)"')

# =============================================================================
# Performance Fix: Cached Regex Patterns (Issue 6)
# =============================================================================

@functools.lru_cache(maxsize=64)
def _get_section_pattern(section_name: str) -> re.Pattern[str]:
    """Get compiled regex pattern for extracting a specific section's content."""
    return re.compile(
        rf'<!-- SECTION: {re.escape(section_name)} -->(.*?)<!-- /SECTION: {re.escape(section_name)} -->',
        re.DOTALL
    )

@functools.lru_cache(maxsize=64)
def _get_section_with_groups_pattern(section_name: str) -> re.Pattern[str]:
    """Get compiled pattern with groups for replace operations."""
    return re.compile(
        rf'(<!-- SECTION: {re.escape(section_name)} -->)(.*?)(<!-- /SECTION: {re.escape(section_name)} -->)',
        re.DOTALL
    )

@functools.lru_cache(maxsize=64)
def _get_section_boundaries_pattern(section_name: str) -> re.Pattern[str]:
    """Get compiled pattern for section boundary detection."""
    return re.compile(
        rf'<!-- SECTION: {re.escape(section_name)} -->.*?<!-- /SECTION: {re.escape(section_name)} -->',
        re.DOTALL
    )

# =============================================================================
# Performance Fix: Prefix Tuples for O(1) Matching (Issue 2)
# Centralized in constants/colors.py
# =============================================================================

from gemini_mcp.constants.colors import (
    COLOR_PREFIXES as _COLOR_PREFIXES,
    TEXT_COLOR_PREFIXES as _TEXT_COLOR_PREFIXES,
    TYPOGRAPHY_PREFIXES as _TYPOGRAPHY_PREFIXES,
    SPACING_PREFIXES as _SPACING_PREFIXES,
    EFFECTS_PREFIXES as _EFFECTS_PREFIXES,
)

# Valid section types (for validation)
VALID_SECTION_TYPES = {
    "navbar",
    "hero",
    "stats",
    "features",
    "testimonials",
    "pricing",
    "cta",
    "footer",
    "content",
    "gallery",
    "faq",
    "team",
    "contact",
}


def extract_section(html: str, section_name: str) -> Optional[str]:
    """Extract a specific section's content from HTML.

    Args:
        html: The full HTML content.
        section_name: The section type to extract (e.g., 'navbar', 'hero').

    Returns:
        The section content (without markers) if found, None otherwise.

    Example:
        >>> html = '''<!-- SECTION: navbar -->
        ... <nav>Navigation</nav>
        ... <!-- /SECTION: navbar -->'''
        >>> extract_section(html, 'navbar')
        '<nav>Navigation</nav>'
    """
    # Use cached compiled pattern (Issue 6 fix)
    pattern = _get_section_pattern(section_name)
    match = pattern.search(html)
    return match.group(1).strip() if match else None


def replace_section(html: str, section_name: str, new_content: str) -> str:
    """Replace a section with new content, preserving markers.

    Args:
        html: The full HTML content.
        section_name: The section type to replace.
        new_content: The new content to insert (without markers).

    Returns:
        The updated HTML with the section replaced.

    Raises:
        ValueError: If the section is not found in the HTML.

    Example:
        >>> html = '''<!-- SECTION: navbar -->
        ... <nav>Old Nav</nav>
        ... <!-- /SECTION: navbar -->'''
        >>> replace_section(html, 'navbar', '<nav>New Nav</nav>')
        '<!-- SECTION: navbar -->\\n<nav>New Nav</nav>\\n<!-- /SECTION: navbar -->'
    """
    # Use cached compiled pattern (Issue 6 fix)
    pattern = _get_section_with_groups_pattern(section_name)

    if not pattern.search(html):
        raise ValueError(f"Section '{section_name}' not found in HTML")

    # Clean up the new content
    new_content = new_content.strip()
    replacement = rf'\1\n{new_content}\n\3'

    return pattern.sub(replacement, html)


def list_sections(html: str) -> List[str]:
    """List all section names in the HTML.

    Args:
        html: The full HTML content.

    Returns:
        List of section names found in the HTML.

    Example:
        >>> html = '''<!-- SECTION: navbar -->...<!-- /SECTION: navbar -->
        ... <!-- SECTION: hero -->...<!-- /SECTION: hero -->'''
        >>> list_sections(html)
        ['navbar', 'hero']
    """
    return re.findall(r'<!-- SECTION: (\w+) -->', html)


def get_section_boundaries(html: str, section_name: str) -> Optional[Tuple[int, int]]:
    """Get start and end character positions of a section.

    Args:
        html: The full HTML content.
        section_name: The section type to locate.

    Returns:
        Tuple of (start_position, end_position) if found, None otherwise.

    Example:
        >>> html = '<!-- SECTION: navbar --><nav>Nav</nav><!-- /SECTION: navbar -->'
        >>> get_section_boundaries(html, 'navbar')
        (0, 64)
    """
    # Use cached compiled pattern (Issue 6 fix)
    pattern = _get_section_boundaries_pattern(section_name)
    match = pattern.search(html)
    return (match.start(), match.end()) if match else None


def validate_section_type(section_type: str) -> bool:
    """Check if a section type is valid.

    Args:
        section_type: The section type to validate.

    Returns:
        True if the section type is valid, False otherwise.
    """
    return section_type.lower() in VALID_SECTION_TYPES


def get_section_with_markers(html: str, section_name: str) -> Optional[str]:
    """Extract a section including its markers.

    Args:
        html: The full HTML content.
        section_name: The section type to extract.

    Returns:
        The complete section including markers if found, None otherwise.
    """
    # Use cached compiled pattern (Issue 6 fix)
    pattern = _get_section_boundaries_pattern(section_name)
    match = pattern.search(html)
    return match.group(0) if match else None


def insert_section_after(
    html: str,
    after_section: str,
    new_section_type: str,
    new_content: str
) -> str:
    """Insert a new section after an existing section.

    Args:
        html: The full HTML content.
        after_section: The section type after which to insert.
        new_section_type: The type of the new section.
        new_content: The content for the new section.

    Returns:
        The updated HTML with the new section inserted.

    Raises:
        ValueError: If the reference section is not found.
    """
    pattern = rf'(<!-- /SECTION: {after_section} -->)'

    if not re.search(pattern, html):
        raise ValueError(f"Section '{after_section}' not found in HTML")

    new_section = f"""
<!-- SECTION: {new_section_type} -->
{new_content.strip()}
<!-- /SECTION: {new_section_type} -->"""

    return re.sub(pattern, rf'\1{new_section}', html)


def remove_section(html: str, section_name: str) -> str:
    """Remove a section completely from the HTML.

    Args:
        html: The full HTML content.
        section_name: The section type to remove.

    Returns:
        The updated HTML with the section removed.

    Raises:
        ValueError: If the section is not found.
    """
    # Use cached compiled pattern (Issue 6 fix)
    pattern = _get_section_boundaries_pattern(section_name)

    if not pattern.search(html):
        raise ValueError(f"Section '{section_name}' not found in HTML")

    # Remove the section and any trailing newlines
    # Note: We need a separate pattern for the trailing newlines
    full_pattern = re.compile(
        rf'<!-- SECTION: {re.escape(section_name)} -->.*?<!-- /SECTION: {re.escape(section_name)} -->\n*',
        re.DOTALL
    )
    result = full_pattern.sub('', html)
    return result.strip()


def extract_design_tokens_from_section(html: str, section_name: str) -> Dict[str, List[str]]:
    """Extract design-relevant Tailwind classes from a section.

    Useful for maintaining style consistency when regenerating a section.

    Args:
        html: The full HTML content.
        section_name: The section to analyze.

    Returns:
        Dictionary with categorized Tailwind classes found in the section.
    """
    section_content = extract_section(html, section_name)
    if not section_content:
        return {}

    # Extract all class attributes using precompiled pattern
    all_classes = ' '.join(_CLASS_PATTERN.findall(section_content))

    # Use sets for O(1) deduplication (Issue 2 fix)
    colors: set[str] = set()
    typography: set[str] = set()
    spacing: set[str] = set()
    effects: set[str] = set()

    for cls in all_classes.split():
        # Colors - check common prefixes first, then text-color variants
        if cls.startswith(_COLOR_PREFIXES):
            colors.add(cls)
        elif cls.startswith(_TEXT_COLOR_PREFIXES):
            colors.add(cls)
        # Typography
        elif cls.startswith(_TYPOGRAPHY_PREFIXES):
            typography.add(cls)
        # Spacing
        elif cls.startswith(_SPACING_PREFIXES):
            spacing.add(cls)
        # Effects
        elif cls.startswith(_EFFECTS_PREFIXES):
            effects.add(cls)

    return {
        "colors": list(colors),
        "typography": list(typography),
        "spacing": list(spacing),
        "effects": list(effects),
    }


def wrap_content_with_markers(content: str, section_type: str) -> str:
    """Wrap content with section markers.

    Args:
        content: The HTML content to wrap.
        section_type: The section type for the markers.

    Returns:
        Content wrapped with appropriate markers.
    """
    return f"""<!-- SECTION: {section_type} -->
{content.strip()}
<!-- /SECTION: {section_type} -->"""


def has_section_markers(html: str) -> bool:
    """Check if HTML contains any section markers.

    Args:
        html: The HTML content to check.

    Returns:
        True if section markers are found, False otherwise.
    """
    return bool(re.search(r'<!-- SECTION: \w+ -->', html))


def migrate_to_markers(html: str, section_mapping: Dict[str, str]) -> str:
    """Add section markers to HTML without markers.

    This is a helper for migrating existing HTML to use section markers.
    It requires a mapping of CSS selectors or patterns to section types.

    Args:
        html: The HTML content without markers.
        section_mapping: Dict mapping patterns to section types.
                        Example: {"<nav": "navbar", "<footer": "footer"}

    Returns:
        HTML with section markers added.

    Note:
        This is a simple implementation. For complex cases,
        manual adjustment may be needed.
    """
    # Issue 7 fix: Collect all replacements first, then apply in reverse order
    # This avoids O(n^2) string concatenation in loop
    replacements: List[Tuple[int, int, str]] = []  # (start, end, wrapped_content)

    for pattern, section_type in section_mapping.items():
        # Find the element and wrap it
        # This is a simplified approach - real implementation might need HTML parsing
        if pattern.startswith("<"):
            tag = pattern[1:]
            # Match opening to closing tag
            element_pattern = re.compile(
                rf'(<{tag}[^>]*>.*?</{tag}>)',
                re.DOTALL | re.IGNORECASE
            )
            match = element_pattern.search(html)
            if match:
                wrapped = wrap_content_with_markers(match.group(1), section_type)
                replacements.append((match.start(), match.end(), wrapped))

    if not replacements:
        return html

    # Sort by position (descending) to apply from end to start
    # This way earlier positions remain valid after each replacement
    replacements.sort(key=lambda x: x[0], reverse=True)

    result = html
    for start, end, wrapped in replacements:
        result = result[:start] + wrapped + result[end:]

    return result


# =============================================================================
# GAP 2 Fix: Section Marker Enforcement
# =============================================================================

def ensure_section_markers(html: str, section_type: str) -> str:
    """Ensure HTML content has proper section markers.

    If the content already has markers, validates and returns as-is.
    If not, wraps the content with appropriate markers.

    Args:
        html: The HTML content (may or may not have markers).
        section_type: The expected section type.

    Returns:
        HTML with guaranteed section markers.

    Example:
        >>> ensure_section_markers('<nav>Nav</nav>', 'navbar')
        '<!-- SECTION: navbar -->\\n<nav>Nav</nav>\\n<!-- /SECTION: navbar -->'
    """
    html = html.strip()

    # Check if already has this section's markers
    pattern = rf'<!-- SECTION: {section_type} -->'
    if re.search(pattern, html):
        # Validate closing marker exists
        closing_pattern = rf'<!-- /SECTION: {section_type} -->'
        if re.search(closing_pattern, html):
            return html
        # Has opening but not closing - add closing
        return html + f"\n<!-- /SECTION: {section_type} -->"

    # No markers - wrap the content
    return wrap_content_with_markers(html, section_type)


def combine_sections(sections: List[Tuple[str, str]], page_wrapper: bool = True) -> str:
    """Combine multiple sections into a complete page HTML.

    Each section is wrapped with markers if not already wrapped.
    Sections are combined in the order provided.

    Args:
        sections: List of (section_type, html_content) tuples.
                  Example: [("navbar", "<nav>...</nav>"), ("hero", "<section>...</section>")]
        page_wrapper: If True, wrap the combined sections in a basic page structure.

    Returns:
        Complete HTML with all sections properly marked.

    Example:
        >>> sections = [
        ...     ("navbar", "<nav>Navigation</nav>"),
        ...     ("hero", "<section>Hero</section>"),
        ...     ("footer", "<footer>Footer</footer>")
        ... ]
        >>> combine_sections(sections)
        # Returns complete HTML with all sections marked
    """
    marked_sections = []

    for section_type, content in sections:
        marked = ensure_section_markers(content, section_type)
        marked_sections.append(marked)

    combined = "\n\n".join(marked_sections)

    if page_wrapper:
        return f"""<!DOCTYPE html>
<html lang="tr" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="min-h-screen bg-white dark:bg-gray-900">
{combined}
</body>
</html>"""

    return combined


def extract_all_sections(html: str) -> Dict[str, str]:
    """Extract all sections from HTML into a dictionary.

    Args:
        html: The full HTML content with section markers.

    Returns:
        Dictionary mapping section types to their content (without markers).

    Example:
        >>> html = '''<!-- SECTION: navbar --><nav>Nav</nav><!-- /SECTION: navbar -->
        ... <!-- SECTION: hero --><section>Hero</section><!-- /SECTION: hero -->'''
        >>> extract_all_sections(html)
        {'navbar': '<nav>Nav</nav>', 'hero': '<section>Hero</section>'}
    """
    sections = {}
    # SECTION_PATTERN is precompiled at module level
    for match in SECTION_PATTERN.finditer(html):
        section_type = match.group(1)
        content = match.group(2).strip()
        sections[section_type] = content
    return sections


def extract_design_tokens_batch(
    html: str,
    exclude_section: str = ""
) -> Dict[str, Dict[str, List[str]]]:
    """Extract design tokens from all sections in a single pass.

    This is more efficient than calling extract_design_tokens_from_section()
    multiple times, as it scans the HTML only once.

    Args:
        html: Full HTML content with section markers.
        exclude_section: Optional section name to skip (e.g., the one being replaced).

    Returns:
        Dict mapping section_name -> design_tokens dict.
        Each design_tokens dict has keys: 'colors', 'typography', 'spacing', 'effects'.

    Example:
        >>> html = '''<!-- SECTION: navbar --><nav class="bg-blue-600">...<!-- /SECTION: navbar -->
        ... <!-- SECTION: hero --><section class="py-16">...<!-- /SECTION: hero -->'''
        >>> tokens = extract_design_tokens_batch(html, exclude_section="hero")
        >>> tokens.keys()
        dict_keys(['navbar'])
    """
    # Single pass: extract all sections at once
    all_sections = extract_all_sections(html)

    result: Dict[str, Dict[str, List[str]]] = {}

    for section_name, content in all_sections.items():
        if section_name == exclude_section:
            continue

        # Extract all classes from this section
        all_classes = ' '.join(_CLASS_PATTERN.findall(content))

        # Use sets for O(1) deduplication
        colors: set[str] = set()
        typography: set[str] = set()
        spacing: set[str] = set()
        effects: set[str] = set()

        for cls in all_classes.split():
            if cls.startswith(_COLOR_PREFIXES):
                colors.add(cls)
            elif cls.startswith(_TEXT_COLOR_PREFIXES):
                colors.add(cls)
            elif cls.startswith(_TYPOGRAPHY_PREFIXES):
                typography.add(cls)
            elif cls.startswith(_SPACING_PREFIXES):
                spacing.add(cls)
            elif cls.startswith(_EFFECTS_PREFIXES):
                effects.add(cls)

        # Only include sections that have at least some tokens
        if colors or typography or spacing or effects:
            result[section_name] = {
                "colors": list(colors),
                "typography": list(typography),
                "spacing": list(spacing),
                "effects": list(effects),
            }

    return result


def validate_page_structure(html: str, required_sections: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """Validate that a page has the required section structure.

    Args:
        html: The full HTML content.
        required_sections: List of section types that must be present.
                          If None, just checks for any valid section structure.

    Returns:
        Tuple of (is_valid, list of missing or invalid sections).

    Example:
        >>> html = '''<!-- SECTION: navbar -->...<!-- /SECTION: navbar -->
        ... <!-- SECTION: hero -->...<!-- /SECTION: hero -->'''
        >>> validate_page_structure(html, ['navbar', 'hero', 'footer'])
        (False, ['footer'])
    """
    found_sections = set(list_sections(html))
    issues = []

    if required_sections:
        missing = set(required_sections) - found_sections
        issues.extend([f"missing:{s}" for s in missing])

    # Check for unclosed markers
    opening_markers = set(re.findall(r'<!-- SECTION: (\w+) -->', html))
    closing_markers = set(re.findall(r'<!-- /SECTION: (\w+) -->', html))

    unclosed = opening_markers - closing_markers
    issues.extend([f"unclosed:{s}" for s in unclosed])

    unopened = closing_markers - opening_markers
    issues.extend([f"unopened:{s}" for s in unopened])

    return len(issues) == 0, issues


def reorder_sections(html: str, section_order: List[str]) -> str:
    """Reorder sections in HTML according to a specified order.

    Sections not in the order list are appended at the end.

    Args:
        html: The full HTML content with section markers.
        section_order: Desired order of sections.

    Returns:
        HTML with sections reordered.

    Example:
        >>> html = '''<!-- SECTION: footer -->...<!-- /SECTION: footer -->
        ... <!-- SECTION: navbar -->...<!-- /SECTION: navbar -->'''
        >>> reorder_sections(html, ['navbar', 'footer'])
        # Returns with navbar before footer
    """
    all_sections = extract_all_sections(html)

    # Build ordered list
    ordered_sections = []

    # First, add sections in specified order
    for section_type in section_order:
        if section_type in all_sections:
            ordered_sections.append((section_type, all_sections[section_type]))

    # Then, add any remaining sections
    for section_type, content in all_sections.items():
        if section_type not in section_order:
            ordered_sections.append((section_type, content))

    return combine_sections(ordered_sections, page_wrapper=False)
