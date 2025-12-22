"""Section manipulation utilities for iterative component replacement.

This module provides functions to extract, replace, and manage HTML sections
marked with structured comments for iteration support.

Section Marker Format:
    <!-- SECTION: {section_type} -->
    ...section content...
    <!-- /SECTION: {section_type} -->
"""

import re
from typing import Dict, List, Optional, Tuple

# Pattern to match section markers
SECTION_PATTERN = r'<!-- SECTION: (\w+) -->(.*?)<!-- /SECTION: \1 -->'

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
    pattern = rf'<!-- SECTION: {section_name} -->(.*?)<!-- /SECTION: {section_name} -->'
    match = re.search(pattern, html, re.DOTALL)
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
    pattern = rf'(<!-- SECTION: {section_name} -->)(.*?)(<!-- /SECTION: {section_name} -->)'

    if not re.search(pattern, html, re.DOTALL):
        raise ValueError(f"Section '{section_name}' not found in HTML")

    # Clean up the new content
    new_content = new_content.strip()
    replacement = rf'\1\n{new_content}\n\3'

    return re.sub(pattern, replacement, html, flags=re.DOTALL)


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
    pattern = rf'<!-- SECTION: {section_name} -->.*?<!-- /SECTION: {section_name} -->'
    match = re.search(pattern, html, re.DOTALL)
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
    pattern = rf'<!-- SECTION: {section_name} -->.*?<!-- /SECTION: {section_name} -->'
    match = re.search(pattern, html, re.DOTALL)
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
    pattern = rf'<!-- SECTION: {section_name} -->.*?<!-- /SECTION: {section_name} -->'

    if not re.search(pattern, html, re.DOTALL):
        raise ValueError(f"Section '{section_name}' not found in HTML")

    # Remove the section and any trailing newlines
    result = re.sub(pattern + r'\n*', '', html, flags=re.DOTALL)
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

    # Extract all class attributes
    class_pattern = r'class="([^"]*)"'
    all_classes = ' '.join(re.findall(class_pattern, section_content))

    # Categorize classes
    tokens: Dict[str, List[str]] = {
        "colors": [],
        "typography": [],
        "spacing": [],
        "effects": [],
    }

    for cls in all_classes.split():
        # Colors (bg-, text-, border-)
        if any(prefix in cls for prefix in ['bg-', 'text-', 'border-', 'ring-']):
            if cls not in tokens["colors"]:
                tokens["colors"].append(cls)
        # Typography
        elif any(prefix in cls for prefix in ['font-', 'text-', 'tracking-', 'leading-']):
            if cls not in tokens["typography"]:
                tokens["typography"].append(cls)
        # Spacing
        elif any(prefix in cls for prefix in ['p-', 'px-', 'py-', 'm-', 'mx-', 'my-', 'gap-', 'space-']):
            if cls not in tokens["spacing"]:
                tokens["spacing"].append(cls)
        # Effects
        elif any(prefix in cls for prefix in ['shadow-', 'rounded-', 'blur-', 'opacity-', 'transition-']):
            if cls not in tokens["effects"]:
                tokens["effects"].append(cls)

    return tokens


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
    result = html

    for pattern, section_type in section_mapping.items():
        # Find the element and wrap it
        # This is a simplified approach - real implementation might need HTML parsing
        if pattern.startswith("<"):
            tag = pattern[1:]
            # Match opening to closing tag
            element_pattern = rf'(<{tag}[^>]*>.*?</{tag}>)'
            match = re.search(element_pattern, result, re.DOTALL | re.IGNORECASE)
            if match:
                wrapped = wrap_content_with_markers(match.group(1), section_type)
                result = result[:match.start()] + wrapped + result[match.end():]

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
    for match in re.finditer(SECTION_PATTERN, html, re.DOTALL):
        section_type = match.group(1)
        content = match.group(2).strip()
        sections[section_type] = content
    return sections


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
