"""Public API functions for JavaScript fallbacks.

This module provides the public interface for:
- Getting JavaScript code for specific modules
- Detecting needed modules from HTML
- Injecting fallbacks into HTML
- Getting module information
"""

import re
from typing import Dict, List, Optional, Set

from ._modules import JS_MODULES, COMPONENT_JS_REQUIREMENTS, JSModule


def get_js_module(module_name: str) -> Optional[str]:
    """Get JavaScript code for a specific module.

    Args:
        module_name: Name of the module (e.g., 'modal', 'dropdown')

    Returns:
        JavaScript code string or None if not found
    """
    module = JS_MODULES.get(module_name)
    if not module:
        return None

    # Get dependencies first
    code_parts = []
    for dep in module.dependencies:
        dep_module = JS_MODULES.get(dep)
        if dep_module:
            code_parts.append(f"// === {dep.upper()} ===\n{dep_module.code}")

    # Add main module
    code_parts.append(f"// === {module_name.upper()} ===\n{module.code}")

    return "\n\n".join(code_parts)


def get_js_for_component(component_type: str) -> str:
    """Get all JavaScript needed for a component type.

    Args:
        component_type: Component type (e.g., 'modal', 'carousel', 'navbar')

    Returns:
        Combined JavaScript code string
    """
    modules_needed = COMPONENT_JS_REQUIREMENTS.get(component_type.lower(), [])

    if not modules_needed:
        return ""

    # Collect unique modules including dependencies
    all_modules: Set[str] = set()

    def add_with_deps(name: str):
        if name not in all_modules:
            module = JS_MODULES.get(name)
            if module:
                for dep in module.dependencies:
                    add_with_deps(dep)
                all_modules.add(name)

    for module_name in modules_needed:
        add_with_deps(module_name)

    # Generate code in dependency order
    code_parts = []

    # Utils always first if needed
    if "utils" in all_modules:
        code_parts.append(JS_MODULES["utils"].code)
        all_modules.remove("utils")

    # Then rest of modules
    for name in all_modules:
        module = JS_MODULES.get(name)
        if module:
            code_parts.append(f"// === {name.upper()} ===\n{module.code}")

    return "\n\n".join(code_parts)


def detect_needed_modules(html: str) -> Set[str]:
    """Detect which JS modules are needed based on HTML content.

    Args:
        html: HTML content to analyze

    Returns:
        Set of module names that are needed
    """
    needed = set()

    for name, module in JS_MODULES.items():
        for pattern in module.auto_detect_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                needed.add(name)
                # Add dependencies
                for dep in module.dependencies:
                    needed.add(dep)
                break

    return needed


def inject_js_fallbacks(
    html: str,
    modules: Optional[List[str]] = None,
    detect_needed: bool = True,
) -> str:
    """Inject JavaScript fallbacks into HTML.

    Args:
        html: HTML content
        modules: Specific modules to inject (optional)
        detect_needed: Auto-detect needed modules from HTML

    Returns:
        HTML with JavaScript injected before </body>
    """
    # Determine which modules to include
    modules_to_inject: Set[str] = set()

    if modules:
        for m in modules:
            modules_to_inject.add(m)
            # Add dependencies
            module = JS_MODULES.get(m)
            if module:
                modules_to_inject.update(module.dependencies)

    if detect_needed:
        modules_to_inject.update(detect_needed_modules(html))

    if not modules_to_inject:
        return html

    # Build JS code
    code_parts = []

    # Utils first
    if "utils" in modules_to_inject:
        code_parts.append(JS_MODULES["utils"].code)
        modules_to_inject.remove("utils")

    for name in sorted(modules_to_inject):
        module = JS_MODULES.get(name)
        if module:
            code_parts.append(module.code)

    js_code = "\n\n".join(code_parts)

    # Wrap in script tag
    script_tag = f"""
<script>
(function() {{
{js_code}
}})();
</script>
"""

    # Inject before </body> or at end
    if "</body>" in html.lower():
        # Use lambda to avoid regex escape issues in JS code
        html = re.sub(
            r"(</body>)",
            lambda m: f"{script_tag}{m.group(1)}",
            html,
            flags=re.IGNORECASE,
        )
    else:
        html = html + script_tag

    return html


def get_all_module_names() -> List[str]:
    """Get list of all available module names."""
    return list(JS_MODULES.keys())


def get_module_info(module_name: str) -> Optional[Dict]:
    """Get information about a specific module.

    Args:
        module_name: Name of the module

    Returns:
        Dict with module info or None
    """
    module = JS_MODULES.get(module_name)
    if not module:
        return None

    return {
        "name": module.name,
        "description": module.description,
        "dependencies": module.dependencies,
        "auto_detect_patterns": module.auto_detect_patterns,
        "code_size": len(module.code),
    }


def get_bundle_stats() -> Dict:
    """Get size statistics for all modules.

    Returns:
        Dict with module sizes and total bundle size
    """
    return {
        "modules": {name: len(m.code) for name, m in JS_MODULES.items()},
        "total_chars": sum(len(m.code) for m in JS_MODULES.values()),
        "estimated_kb": sum(len(m.code) for m in JS_MODULES.values()) / 1024,
    }
