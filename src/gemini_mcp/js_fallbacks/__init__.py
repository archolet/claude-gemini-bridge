"""Lazy-loaded JavaScript fallback library for frontend components.

This module is lazy-loaded to avoid importing ~1000+ lines of JavaScript code
when not needed. Modern projects using React/Vue/Alpine.js typically don't
need these vanilla JS fallbacks.

The module provides JavaScript implementations for:
- Modal dialogs with focus trap
- Dropdown menus with collision detection
- Carousel/slider with touch support
- Tabs with keyboard navigation
- Accordion with smooth animations
- Toast notifications
- Scroll animations via Intersection Observer

Usage:
    # Import only loads the module when accessed
    from gemini_mcp.js_fallbacks import inject_js_fallbacks

    # Inject needed JS into HTML (auto-detects required modules)
    html_with_js = inject_js_fallbacks(html, detect_needed=True)

    # Get JS for a specific component type
    from gemini_mcp.js_fallbacks import get_js_for_component
    js = get_js_for_component("modal")

    # Get bundle statistics
    from gemini_mcp.js_fallbacks import get_bundle_stats
    stats = get_bundle_stats()
    print(f"Total size: {stats['estimated_kb']:.1f} KB")

Note:
    This module is NOT used by default in production. The design tools
    use `fix_js_fallbacks()` from client.py for Alpine.js-specific fixes.
    Use the `inject_js_fallbacks` parameter in design tools to explicitly
    include these vanilla JS fallbacks.
"""

import importlib

# Lazy loading implementation with guard against recursion
_loaded = False
_loading = False  # Guard against recursive import
_module = None


def _ensure_loaded():
    """Load the actual implementation on first access."""
    global _loaded, _loading, _module
    if _loading:
        # Prevent recursion during import
        raise ImportError("Circular import detected in js_fallbacks")
    if not _loaded:
        _loading = True
        try:
            # Use absolute import to avoid recursion
            _module = importlib.import_module("gemini_mcp.js_fallbacks._api")
        except ImportError as e:
            raise ImportError(f"Failed to load js_fallbacks._api: {e}")
        finally:
            _loading = False
        _loaded = True
    return _module


def __getattr__(name: str):
    """Lazy attribute access - loads module on first use."""
    if name in ("_loaded", "_loading", "_module", "_ensure_loaded"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = _ensure_loaded()
    return getattr(module, name)


def __dir__():
    """List available exports for IDE/tooling support."""
    return __all__


__all__ = [
    # Public API functions
    "inject_js_fallbacks",
    "get_js_module",
    "get_js_for_component",
    "detect_needed_modules",
    "get_all_module_names",
    "get_module_info",
    "get_bundle_stats",
    # Types and registries (available after lazy load)
    "JSModule",
    "JS_MODULES",
    "COMPONENT_JS_REQUIREMENTS",
]
