"""Few-shot examples subpackage.

Provides lazy-loaded example dictionaries for component, bad, corporate,
and section chain examples.

This package is structured for lazy loading - examples are not loaded
at import time, only when accessed.
"""

from ._loader import LazyDict

__all__ = ["LazyDict"]
