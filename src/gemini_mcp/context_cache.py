"""Gemini API Native Context Caching for System Prompts.

Leverages Google's server-side caching to reduce costs and latency
for repeated system prompts. Gemini 3 caches prompts on Google's
infrastructure, providing 75-90% savings on input token costs.

Requirements:
- Minimum 2,048 tokens for caching eligibility
- Cache TTL: 1 hour (default), configurable up to 24 hours
- Only system instructions and few-shot examples are cached
- User content is NOT cached (privacy-safe)

Usage:
    >>> from gemini_mcp.context_cache import GeminiContextCache
    >>> cache = GeminiContextCache(project_id="my-project")
    >>>
    >>> # Create or get cached content
    >>> cached = await cache.get_or_create(
    ...     agent_name="architect",
    ...     system_prompt="You are The Architect...",
    ...     model="gemini-2.5-pro"
    ... )
    >>>
    >>> # Use cached content in API call
    >>> response = await client.generate_content(
    ...     cached_content=cached.name,
    ...     contents=[user_message]
    ... )
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Minimum tokens required for Gemini to cache content
MIN_CACHE_TOKENS = 2048

# Default cache TTL in seconds (1 hour)
DEFAULT_TTL_SECONDS = 3600

# Maximum cache TTL in seconds (24 hours)
MAX_TTL_SECONDS = 86400


@dataclass
class CacheMetrics:
    """Metrics for context cache operations."""

    hits: int = 0
    misses: int = 0
    creates: int = 0
    errors: int = 0
    total_tokens_cached: int = 0
    estimated_savings_usd: float = 0.0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "creates": self.creates,
            "errors": self.errors,
            "hit_rate": round(self.hit_rate, 3),
            "total_tokens_cached": self.total_tokens_cached,
            "estimated_savings_usd": round(self.estimated_savings_usd, 4),
        }


@dataclass
class CachedPrompt:
    """Local tracking of a cached prompt."""

    cache_name: str  # Google's cache resource name
    agent_name: str
    content_hash: str
    token_count: int
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + DEFAULT_TTL_SECONDS)
    hits: int = 0

    @property
    def is_expired(self) -> bool:
        """Check if cache has expired."""
        return time.time() > self.expires_at

    @property
    def ttl_remaining(self) -> float:
        """Get remaining TTL in seconds."""
        return max(0, self.expires_at - time.time())

    def touch(self) -> None:
        """Record a cache hit."""
        self.hits += 1


class GeminiContextCache:
    """Manages Gemini API native context caching for system prompts.

    This class provides server-side caching of system prompts using
    Google's CachedContent API. Caching reduces input token costs
    by 75-90% for repeated prompts.

    Key Features:
    - Automatic content hashing for deduplication
    - Local tracking of remote cache entries
    - Automatic TTL management
    - Metrics collection for cost analysis

    Example:
        >>> cache = GeminiContextCache(
        ...     project_id="my-project",
        ...     location="us-central1"
        ... )
        >>>
        >>> # Get or create cached content
        >>> cached = await cache.get_or_create(
        ...     agent_name="architect",
        ...     system_prompt="You are The Architect...",
        ...     model="gemini-2.5-pro"
        ... )
        >>>
        >>> # cached.cache_name can be used in generate_content calls
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        enabled: bool = True,
    ):
        """Initialize the context cache manager.

        Args:
            project_id: Google Cloud project ID.
            location: Vertex AI location (e.g., "us-central1").
            ttl_seconds: Cache TTL in seconds (1-86400). Default: 3600 (1 hour).
            enabled: Whether caching is enabled. Default: True.
        """
        self.project_id = project_id
        self.location = location
        self.ttl_seconds = min(max(ttl_seconds, 60), MAX_TTL_SECONDS)
        self.enabled = enabled

        # Local cache tracking (content_hash -> CachedPrompt)
        self._local_cache: Dict[str, CachedPrompt] = {}

        # Metrics
        self._metrics = CacheMetrics()

        # Initialize Genai client
        self._client: Optional[genai.Client] = None

        logger.info(
            f"GeminiContextCache initialized: "
            f"project={project_id}, location={location}, "
            f"ttl={ttl_seconds}s, enabled={enabled}"
        )

    def _get_client(self) -> genai.Client:
        """Get or create the Genai client."""
        if self._client is None:
            self._client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location,
            )
        return self._client

    def _hash_content(self, content: str) -> str:
        """Create a hash of the content for deduplication.

        Args:
            content: The content to hash.

        Returns:
            A 16-character hex hash.
        """
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _estimate_tokens(self, content: str) -> int:
        """Estimate token count for content.

        Uses a simple heuristic: ~4 characters per token.
        This is a rough estimate; actual token count may vary.

        Args:
            content: The content to estimate.

        Returns:
            Estimated token count.
        """
        # Simple heuristic: ~4 chars per token (conservative)
        return len(content) // 4

    def _cleanup_expired(self) -> int:
        """Remove expired entries from local cache.

        Returns:
            Number of entries removed.
        """
        expired_keys = [
            key for key, entry in self._local_cache.items()
            if entry.is_expired
        ]
        for key in expired_keys:
            del self._local_cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    async def get_or_create(
        self,
        agent_name: str,
        system_prompt: str,
        model: str,
        few_shot_examples: Optional[str] = None,
    ) -> Optional[CachedPrompt]:
        """Get existing cache or create new one for the prompt.

        Args:
            agent_name: Name of the agent (e.g., "architect", "alchemist").
            system_prompt: The system instruction to cache.
            model: Model name (e.g., "gemini-2.5-pro").
            few_shot_examples: Optional few-shot examples to include.

        Returns:
            CachedPrompt with cache_name if successful, None if caching
            is disabled or content is too short.
        """
        if not self.enabled:
            return None

        # Combine content for hashing
        full_content = system_prompt
        if few_shot_examples:
            full_content += "\n\n" + few_shot_examples

        # Check token count
        estimated_tokens = self._estimate_tokens(full_content)
        if estimated_tokens < MIN_CACHE_TOKENS:
            logger.debug(
                f"Content too short for caching: {estimated_tokens} tokens "
                f"(minimum: {MIN_CACHE_TOKENS})"
            )
            return None

        # Generate content hash
        content_hash = self._hash_content(full_content)

        # Clean up expired entries
        self._cleanup_expired()

        # Check local cache first
        if content_hash in self._local_cache:
            cached = self._local_cache[content_hash]
            if not cached.is_expired:
                cached.touch()
                self._metrics.hits += 1
                logger.debug(
                    f"Cache hit for {agent_name}: {content_hash[:8]}... "
                    f"(hits={cached.hits}, ttl={cached.ttl_remaining:.0f}s)"
                )
                return cached

        # Cache miss - create new cached content
        self._metrics.misses += 1

        try:
            client = self._get_client()

            # Build cached content
            cached_content = types.CachedContent(
                model=model,
                display_name=f"gemini-mcp-{agent_name}-{content_hash[:8]}",
                system_instruction=system_prompt,
                ttl=f"{self.ttl_seconds}s",
            )

            # Create on Google's side
            result = await client.aio.caches.create(config=cached_content)

            # Track locally
            cached_prompt = CachedPrompt(
                cache_name=result.name,
                agent_name=agent_name,
                content_hash=content_hash,
                token_count=estimated_tokens,
                expires_at=time.time() + self.ttl_seconds,
            )
            self._local_cache[content_hash] = cached_prompt

            # Update metrics
            self._metrics.creates += 1
            self._metrics.total_tokens_cached += estimated_tokens

            # Estimate savings (assuming $0.00025 per 1K input tokens)
            self._metrics.estimated_savings_usd += (
                estimated_tokens / 1000 * 0.00025 * 0.75  # 75% savings
            )

            logger.info(
                f"Created cache for {agent_name}: {result.name} "
                f"({estimated_tokens} tokens, ttl={self.ttl_seconds}s)"
            )

            return cached_prompt

        except Exception as e:
            self._metrics.errors += 1
            logger.error(f"Failed to create cache for {agent_name}: {e}")
            return None

    async def delete(self, content_hash: str) -> bool:
        """Delete a cached content entry.

        Args:
            content_hash: Hash of the content to delete.

        Returns:
            True if deleted, False otherwise.
        """
        if content_hash not in self._local_cache:
            return False

        cached = self._local_cache[content_hash]

        try:
            client = self._get_client()
            await client.aio.caches.delete(name=cached.cache_name)
            del self._local_cache[content_hash]
            logger.info(f"Deleted cache: {cached.cache_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache {cached.cache_name}: {e}")
            return False

    async def list_caches(self) -> list[Dict[str, Any]]:
        """List all cached content entries.

        Returns:
            List of cache entry summaries.
        """
        entries = []
        for hash_key, cached in self._local_cache.items():
            entries.append({
                "cache_name": cached.cache_name,
                "agent_name": cached.agent_name,
                "content_hash": hash_key,
                "token_count": cached.token_count,
                "hits": cached.hits,
                "ttl_remaining": round(cached.ttl_remaining),
                "expired": cached.is_expired,
            })
        return entries

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache metrics.

        Returns:
            Dictionary with cache statistics.
        """
        return {
            **self._metrics.to_dict(),
            "active_entries": len(self._local_cache),
            "enabled": self.enabled,
        }

    def clear_local(self) -> int:
        """Clear local cache tracking (does not delete from Google).

        Returns:
            Number of entries cleared.
        """
        count = len(self._local_cache)
        self._local_cache.clear()
        logger.info(f"Cleared {count} local cache entries")
        return count


# Global instance
_context_cache: Optional[GeminiContextCache] = None


def get_context_cache(
    project_id: str,
    location: str = "us-central1",
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    enabled: bool = True,
) -> GeminiContextCache:
    """Get or create the global context cache.

    Args:
        project_id: Google Cloud project ID.
        location: Vertex AI location.
        ttl_seconds: Cache TTL in seconds.
        enabled: Whether caching is enabled.

    Returns:
        The global GeminiContextCache instance.
    """
    global _context_cache
    if _context_cache is None:
        _context_cache = GeminiContextCache(
            project_id=project_id,
            location=location,
            ttl_seconds=ttl_seconds,
            enabled=enabled,
        )
    return _context_cache


def clear_context_cache() -> int:
    """Clear the global context cache.

    Returns:
        Number of entries cleared.
    """
    global _context_cache
    if _context_cache is not None:
        return _context_cache.clear_local()
    return 0
