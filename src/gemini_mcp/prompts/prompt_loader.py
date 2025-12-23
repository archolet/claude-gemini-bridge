"""
Dynamic Prompt Template Loader with Hot-Reload Support.

This module provides a thread-safe YAML prompt loader that supports:
- Runtime template loading from YAML files
- Variable substitution with {{variable}} syntax
- Hot-reload without server restart
- Graceful fallback to hardcoded prompts on error
- LRU caching for rendered prompts
"""

from __future__ import annotations

import logging
import os
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None  # type: ignore

from pydantic import ValidationError

from gemini_mcp.prompts.template_schema import (
    CachedSegment,
    CachedTemplate,
    PromptTemplate,
    RenderedCache,
    SegmentTemplate,
    VariablesDict,
    hash_variables,
)

if TYPE_CHECKING:
    from gemini_mcp.prompts.file_watcher import FileWatcher

logger = logging.getLogger(__name__)


class PromptLoadError(Exception):
    """Raised when a prompt template cannot be loaded."""
    pass


class PromptLoader:
    """
    Thread-safe YAML prompt loader with hot-reload support.

    Usage:
        loader = PromptLoader.get_instance()
        prompt = loader.get_prompt("architect", {"theme": "cyberpunk"})

    Features:
        - Singleton pattern for global access
        - File modification tracking for cache invalidation
        - Variable substitution with {{variable}} syntax
        - Conditional sections based on component/theme
        - Fallback to hardcoded prompts on YAML errors
    """

    _instance: Optional["PromptLoader"] = None
    _instance_lock = threading.Lock()

    def __init__(
        self,
        templates_dir: Optional[Path] = None,
        segments_dir: Optional[Path] = None,
        watch: bool = True,
        fallback_to_hardcoded: bool = True,
        poll_interval: float = 2.0,
    ):
        """
        Initialize the prompt loader.

        Args:
            templates_dir: Directory containing agent YAML templates.
                          Defaults to ./templates relative to this file.
            segments_dir: Directory containing reusable segment files.
                         Defaults to ./segments relative to this file.
            watch: Enable file watching for hot-reload.
            fallback_to_hardcoded: Fall back to hardcoded prompts on error.
            poll_interval: Seconds between file modification checks.
        """
        if not YAML_AVAILABLE:
            logger.warning(
                "PyYAML not installed. Prompt loading will fall back to hardcoded prompts. "
                "Install with: pip install PyYAML"
            )

        self._base_dir = Path(__file__).parent

        self._templates_dir = templates_dir or (self._base_dir / "templates")
        self._segments_dir = segments_dir or (self._base_dir / "segments")

        self._watch = watch and YAML_AVAILABLE
        self._fallback = fallback_to_hardcoded
        self._poll_interval = poll_interval

        # Thread-safe caches
        self._lock = threading.RLock()
        self._template_cache: Dict[str, CachedTemplate] = {}
        self._segment_cache: Dict[str, CachedSegment] = {}
        self._rendered_cache: Dict[str, RenderedCache] = {}

        # Per-template locks for fine-grained concurrency
        self._template_locks: Dict[str, threading.RLock] = {}

        # File watcher (lazy initialized)
        self._watcher: Optional["FileWatcher"] = None
        self._watcher_started = False

        # Callbacks for reload events
        self._reload_callbacks: List[Callable[[str], None]] = []

        logger.info(
            f"PromptLoader initialized. "
            f"templates_dir={self._templates_dir}, "
            f"segments_dir={self._segments_dir}, "
            f"watch={self._watch}"
        )

    @classmethod
    def get_instance(
        cls,
        templates_dir: Optional[Path] = None,
        segments_dir: Optional[Path] = None,
        watch: bool = True,
        fallback_to_hardcoded: bool = True,
    ) -> "PromptLoader":
        """
        Get or create the singleton loader instance.

        Thread-safe singleton access. First call initializes with provided params.
        Subsequent calls return the existing instance.
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls(
                        templates_dir=templates_dir,
                        segments_dir=segments_dir,
                        watch=watch,
                        fallback_to_hardcoded=fallback_to_hardcoded,
                    )
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (mainly for testing)."""
        with cls._instance_lock:
            if cls._instance is not None:
                cls._instance.stop_watching()
            cls._instance = None

    def get_prompt(
        self,
        agent_name: str,
        variables: Optional[VariablesDict] = None,
        include_sections: Optional[List[str]] = None,
    ) -> str:
        """
        Get a rendered prompt for the specified agent.

        Args:
            agent_name: Agent identifier (e.g., "architect", "alchemist").
            variables: Variable values for substitution.
                      Missing variables use template defaults.
            include_sections: Conditional section keys to include.

        Returns:
            Rendered prompt string with variables substituted.

        Raises:
            PromptLoadError: If template cannot be loaded and fallback is disabled.
        """
        variables = variables or {}

        try:
            return self._get_from_yaml(agent_name, variables, include_sections)
        except Exception as e:
            logger.warning(f"Failed to load YAML template for {agent_name}: {e}")
            if self._fallback:
                return self._get_hardcoded_fallback(agent_name)
            raise PromptLoadError(f"Cannot load prompt for {agent_name}") from e

    def _get_from_yaml(
        self,
        agent_name: str,
        variables: VariablesDict,
        include_sections: Optional[List[str]] = None,
    ) -> str:
        """Load and render template from YAML file."""
        if not YAML_AVAILABLE:
            raise PromptLoadError("PyYAML not installed")

        # Ensure template-specific lock exists
        template_lock = self._get_template_lock(agent_name)

        with template_lock:
            # Check if cached and not stale
            cached = self._get_cached_template(agent_name)

            if cached is None:
                # Load from file
                cached = self._load_template(agent_name)
                self._template_cache[agent_name] = cached

            # Render with variables
            return self._render_template(
                cached.template,
                variables,
                include_sections,
                agent_name,
            )

    def _get_template_lock(self, agent_name: str) -> threading.RLock:
        """Get or create a lock for a specific template."""
        with self._lock:
            if agent_name not in self._template_locks:
                self._template_locks[agent_name] = threading.RLock()
            return self._template_locks[agent_name]

    def _get_cached_template(self, agent_name: str) -> Optional[CachedTemplate]:
        """
        Get cached template if still valid.

        Returns None if not cached or stale.
        """
        cached = self._template_cache.get(agent_name)
        if cached is None:
            return None

        # Check if file has been modified
        try:
            current_mtime = Path(cached.file_path).stat().st_mtime
            if cached.is_stale(current_mtime):
                logger.info(f"Template {agent_name} is stale, will reload")
                return None
        except OSError:
            # File may have been deleted
            return None

        return cached

    def _load_template(self, agent_name: str) -> CachedTemplate:
        """Load template from YAML file."""
        template_path = self._templates_dir / f"{agent_name}.yaml"

        if not template_path.exists():
            raise PromptLoadError(f"Template file not found: {template_path}")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PromptLoadError(f"Invalid YAML in {template_path}: {e}") from e

        try:
            template = PromptTemplate.model_validate(raw_data)
        except ValidationError as e:
            raise PromptLoadError(f"Template validation failed for {agent_name}: {e}") from e

        # Process includes (segment files)
        if template.includes:
            template = self._process_includes(template)

        file_mtime = template_path.stat().st_mtime

        logger.debug(f"Loaded template {agent_name} from {template_path}")

        return CachedTemplate(
            template=template,
            file_path=str(template_path),
            loaded_at=datetime.now(),
            file_mtime=file_mtime,
        )

    def _process_includes(self, template: PromptTemplate) -> PromptTemplate:
        """Process 'includes' by prepending segment content to system_prompt."""
        included_content = []

        for include_path in template.includes:
            segment_path = self._segments_dir / include_path
            if not segment_path.exists():
                logger.warning(f"Segment file not found: {segment_path}")
                continue

            try:
                segment = self._load_segment(include_path)
                included_content.append(segment.segment.content)
            except Exception as e:
                logger.warning(f"Failed to load segment {include_path}: {e}")

        if included_content:
            # Prepend included segments to system prompt
            separator = "\n\n---\n\n"
            new_prompt = separator.join(included_content) + separator + template.system_prompt
            # Create new template with updated prompt
            template = template.model_copy(update={"system_prompt": new_prompt})

        return template

    def _load_segment(self, segment_name: str) -> CachedSegment:
        """Load a reusable segment file."""
        # Check cache
        if segment_name in self._segment_cache:
            cached = self._segment_cache[segment_name]
            try:
                current_mtime = Path(cached.file_path).stat().st_mtime
                if current_mtime <= cached.file_mtime:
                    return cached
            except OSError:
                pass

        segment_path = self._segments_dir / segment_name

        with open(segment_path, 'r', encoding='utf-8') as f:
            raw_data = yaml.safe_load(f)

        segment = SegmentTemplate.model_validate(raw_data)
        file_mtime = segment_path.stat().st_mtime

        cached_segment = CachedSegment(
            segment=segment,
            file_path=str(segment_path),
            loaded_at=datetime.now(),
            file_mtime=file_mtime,
        )

        self._segment_cache[segment_name] = cached_segment
        return cached_segment

    def _render_template(
        self,
        template: PromptTemplate,
        variables: VariablesDict,
        include_sections: Optional[List[str]],
        agent_name: str,
    ) -> str:
        """
        Render template with variable substitution and conditional sections.

        Supports:
        - Simple substitution: {{variable}}
        - Conditional blocks: {{#if variable}}...{{/if}}
        """
        # Merge provided variables with defaults
        merged_vars = {**template.variables, **variables}

        # Check rendered cache
        cache_key = hash_variables(merged_vars)
        if agent_name in self._rendered_cache:
            cached_render = self._rendered_cache[agent_name].get(cache_key)
            if cached_render:
                return cached_render

        # Start with system prompt
        result = template.system_prompt

        # Process conditional blocks first
        result = self._process_conditionals(result, merged_vars)

        # Then do simple variable substitution
        result = self._substitute_variables(result, merged_vars)

        # Add conditional sections if requested
        if include_sections and template.conditional_sections:
            result = self._append_conditional_sections(
                result, template.conditional_sections, include_sections, merged_vars
            )

        # Cache the rendered result
        if agent_name not in self._rendered_cache:
            self._rendered_cache[agent_name] = RenderedCache()
        self._rendered_cache[agent_name].set(cache_key, result)

        return result

    def _process_conditionals(self, content: str, variables: VariablesDict) -> str:
        """
        Process {{#if variable}}...{{/if}} blocks.

        If variable is truthy (non-empty string, True, etc.), include content.
        Otherwise, remove the block.
        """
        # Pattern: {{#if var_name}}content{{/if}}
        pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'

        def replace_conditional(match: re.Match) -> str:
            var_name = match.group(1)
            inner_content = match.group(2)

            var_value = variables.get(var_name, '')
            # Consider truthy: non-empty string, True, non-zero numbers
            if var_value and var_value != '' and var_value != 'false' and var_value != 'False':
                return inner_content.strip()
            return ''

        # Process recursively in case of nested conditionals
        prev_result = None
        result = content
        while prev_result != result:
            prev_result = result
            result = re.sub(pattern, replace_conditional, result, flags=re.DOTALL)

        return result

    def _substitute_variables(self, content: str, variables: VariablesDict) -> str:
        """Replace {{variable}} with values."""
        def replace_var(match: re.Match) -> str:
            var_name = match.group(1)
            value = variables.get(var_name, '')
            return str(value) if value is not None else ''

        pattern = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
        return re.sub(pattern, replace_var, content)

    def _append_conditional_sections(
        self,
        content: str,
        conditional_sections: Dict[str, Dict[str, str]],
        include_sections: List[str],
        variables: VariablesDict,
    ) -> str:
        """Append conditional sections based on include_sections list."""
        sections_to_add = []

        for section_type in include_sections:
            if section_type in conditional_sections:
                section_dict = conditional_sections[section_type]
                # Check if we have a matching value in variables
                for key, section_content in section_dict.items():
                    # Match key against component_type, theme, etc.
                    if key in variables.values():
                        # Substitute variables in section content too
                        rendered_section = self._substitute_variables(section_content, variables)
                        sections_to_add.append(rendered_section)

        if sections_to_add:
            content = content + "\n\n" + "\n\n".join(sections_to_add)

        return content

    def _get_hardcoded_fallback(self, agent_name: str) -> str:
        """Fall back to hardcoded prompts from agent_prompts.py."""
        # Import here to avoid circular imports
        from gemini_mcp.prompts.agent_prompts import (
            ALCHEMIST_SYSTEM_PROMPT,
            ARCHITECT_SYSTEM_PROMPT,
            CRITIC_SYSTEM_PROMPT,
            PHYSICIST_SYSTEM_PROMPT,
            QUALITY_GUARD_SYSTEM_PROMPT,
            STRATEGIST_SYSTEM_PROMPT,
            VISIONARY_SYSTEM_PROMPT,
        )

        fallbacks = {
            "architect": ARCHITECT_SYSTEM_PROMPT,
            "alchemist": ALCHEMIST_SYSTEM_PROMPT,
            "physicist": PHYSICIST_SYSTEM_PROMPT,
            "strategist": STRATEGIST_SYSTEM_PROMPT,
            "quality_guard": QUALITY_GUARD_SYSTEM_PROMPT,
            "critic": CRITIC_SYSTEM_PROMPT,
            "visionary": VISIONARY_SYSTEM_PROMPT,
        }

        prompt = fallbacks.get(agent_name.lower())
        if prompt is None:
            raise PromptLoadError(f"No fallback prompt for agent: {agent_name}")

        logger.info(f"Using hardcoded fallback for agent: {agent_name}")
        return prompt

    def reload_template(self, agent_name: str) -> bool:
        """
        Force reload a specific template.

        Returns True if reload succeeded, False otherwise.
        """
        template_lock = self._get_template_lock(agent_name)

        with template_lock:
            try:
                # Clear caches
                self._template_cache.pop(agent_name, None)
                if agent_name in self._rendered_cache:
                    self._rendered_cache[agent_name].clear()

                # Load fresh
                cached = self._load_template(agent_name)
                self._template_cache[agent_name] = cached

                logger.info(f"Successfully reloaded template: {agent_name}")

                # Notify callbacks
                for callback in self._reload_callbacks:
                    try:
                        callback(agent_name)
                    except Exception as e:
                        logger.warning(f"Reload callback failed: {e}")

                return True

            except Exception as e:
                logger.error(f"Failed to reload template {agent_name}: {e}")
                return False

    def reload_all(self) -> Dict[str, bool]:
        """
        Reload all templates.

        Returns dict mapping agent names to reload success status.
        """
        results = {}

        with self._lock:
            # Get all known template names
            agent_names = list(self._template_cache.keys())

            # Also check filesystem for new templates
            if self._templates_dir.exists():
                for yaml_file in self._templates_dir.glob("*.yaml"):
                    name = yaml_file.stem
                    if name not in agent_names:
                        agent_names.append(name)

        for agent_name in agent_names:
            results[agent_name] = self.reload_template(agent_name)

        return results

    def start_watching(self) -> None:
        """Start the file watcher for hot-reload."""
        if not self._watch or self._watcher_started:
            return

        try:
            from gemini_mcp.prompts.file_watcher import FileWatcher

            self._watcher = FileWatcher(
                directories=[self._templates_dir, self._segments_dir],
                callback=self._on_file_changed,
                poll_interval=self._poll_interval,
            )
            self._watcher.start()
            self._watcher_started = True
            logger.info("File watcher started for hot-reload")
        except ImportError:
            logger.warning("FileWatcher not available, hot-reload disabled")

    def stop_watching(self) -> None:
        """Stop the file watcher."""
        if self._watcher:
            self._watcher.stop()
            self._watcher = None
            self._watcher_started = False
            logger.info("File watcher stopped")

    def _on_file_changed(self, file_path: Path) -> None:
        """Callback when a watched file changes."""
        logger.info(f"Detected change in: {file_path}")

        if file_path.parent == self._templates_dir:
            agent_name = file_path.stem
            self.reload_template(agent_name)

        elif file_path.parent == self._segments_dir:
            # Segment changed, clear all templates that might include it
            segment_name = file_path.name
            with self._lock:
                self._segment_cache.pop(segment_name, None)
                # Reload all templates (they might include this segment)
                self.reload_all()

    def add_reload_callback(self, callback: Callable[[str], None]) -> None:
        """Add a callback to be notified when templates are reloaded."""
        self._reload_callbacks.append(callback)

    def get_template_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a loaded template (for debugging/monitoring)."""
        cached = self._template_cache.get(agent_name)
        if cached is None:
            return None

        return {
            "name": cached.template.metadata.name,
            "version": cached.template.metadata.version,
            "description": cached.template.metadata.description,
            "file_path": cached.file_path,
            "loaded_at": cached.loaded_at.isoformat(),
            "variables": list(cached.template.variables.keys()),
            "placeholders": cached.template.get_placeholders(),
            "includes": cached.template.includes,
        }

    def list_templates(self) -> List[str]:
        """List all available template names."""
        templates = []
        if self._templates_dir.exists():
            for yaml_file in self._templates_dir.glob("*.yaml"):
                templates.append(yaml_file.stem)
        return sorted(templates)


# Convenience functions for module-level access

_loader: Optional[PromptLoader] = None


def get_loader() -> PromptLoader:
    """Get the global PromptLoader instance."""
    global _loader
    if _loader is None:
        _loader = PromptLoader.get_instance()
    return _loader


def get_prompt(
    agent_name: str,
    variables: Optional[VariablesDict] = None,
    include_sections: Optional[List[str]] = None,
) -> str:
    """
    Get a rendered prompt for the specified agent.

    Convenience function that uses the global loader instance.
    """
    return get_loader().get_prompt(agent_name, variables, include_sections)


def reload_prompt(agent_name: str) -> bool:
    """Reload a specific template."""
    return get_loader().reload_template(agent_name)


def reload_all_prompts() -> Dict[str, bool]:
    """Reload all templates."""
    return get_loader().reload_all()
