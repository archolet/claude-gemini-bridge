"""Lazy loading utilities for few-shot examples.

Provides LazyDict class that loads data only on first access,
reducing memory footprint at module import time.
"""

from __future__ import annotations

from typing import Any, Callable, Iterator, Mapping


class LazyDict(Mapping[str, Any]):
    """Dict-like wrapper that loads data on first access.

    Implements the Mapping protocol to be fully compatible with dict usage
    patterns while deferring the actual data loading until first access.

    Example:
        >>> examples = LazyDict(lambda: {"key": "value"})
        >>> # Data not loaded yet
        >>> examples["key"]  # Now data is loaded
        'value'
    """

    __slots__ = ("_loader", "_cache")

    def __init__(self, loader_func: Callable[[], dict[str, Any]]) -> None:
        """Initialize with a loader function.

        Args:
            loader_func: A callable that returns the dict data when invoked.
                        Will be called only once on first access.
        """
        self._loader = loader_func
        self._cache: dict[str, Any] | None = None

    def _ensure_loaded(self) -> dict[str, Any]:
        """Load data if not already loaded."""
        if self._cache is None:
            self._cache = self._loader()
        return self._cache

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self._ensure_loaded()[key]

    def __contains__(self, key: object) -> bool:
        """Check if key exists."""
        return key in self._ensure_loaded()

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        return iter(self._ensure_loaded())

    def __len__(self) -> int:
        """Return number of items."""
        return len(self._ensure_loaded())

    def get(self, key: str, default: Any = None) -> Any:
        """Get item with default."""
        return self._ensure_loaded().get(key, default)

    def keys(self):
        """Return keys view."""
        return self._ensure_loaded().keys()

    def values(self):
        """Return values view."""
        return self._ensure_loaded().values()

    def items(self):
        """Return items view."""
        return self._ensure_loaded().items()

    @property
    def is_loaded(self) -> bool:
        """Check if data has been loaded."""
        return self._cache is not None

    def __repr__(self) -> str:
        """Return repr string."""
        status = "loaded" if self._cache is not None else "not loaded"
        count = len(self._cache) if self._cache is not None else "?"
        return f"<LazyDict({status}, {count} items)>"
