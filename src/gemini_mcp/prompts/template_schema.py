"""
Pydantic models for YAML prompt template validation.

This module defines the schema for prompt templates, ensuring type-safety
and validation when loading YAML files.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class TemplateMetadata(BaseModel):
    """Metadata for a prompt template."""

    name: str = Field(..., min_length=1, description="Agent name (e.g., 'architect')")
    version: str = Field(
        default="1.0.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version"
    )
    description: str = Field(default="", description="Human-readable description")
    author: str = Field(default="", description="Template author")
    last_modified: Optional[str] = Field(default=None, description="Last modification date")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")


class ConditionalSection(BaseModel):
    """A conditional section that can be appended based on context."""

    condition_type: str = Field(
        ...,
        description="Type of condition: 'component_specific', 'theme_specific', etc."
    )
    sections: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of condition value to content"
    )


class PromptTemplate(BaseModel):
    """
    Complete prompt template structure.

    A template contains:
    - metadata: Version, description, author info
    - variables: Default values for placeholders
    - system_prompt: The main prompt content
    - conditional_sections: Optional content based on context
    - includes: References to reusable segments
    """

    metadata: TemplateMetadata
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Variable defaults (e.g., {'theme': 'modern-minimal'})"
    )
    system_prompt: str = Field(
        ...,
        min_length=10,
        description="The main system prompt content"
    )
    conditional_sections: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Conditional content sections"
    )
    includes: List[str] = Field(
        default_factory=list,
        description="Paths to segment files to include"
    )
    extends: Optional[str] = Field(
        default=None,
        description="Base template to inherit from"
    )

    @field_validator('system_prompt')
    @classmethod
    def validate_placeholder_syntax(cls, v: str) -> str:
        """
        Validate that placeholder syntax is correct.

        Valid: {{variable_name}}
        Invalid: {variable_name}, {{ variable_name }}
        """
        # Find all double-brace placeholders
        placeholders = re.findall(r'\{\{([^}]+)\}\}', v)

        for placeholder in placeholders:
            # Check for leading/trailing whitespace (not allowed)
            if placeholder != placeholder.strip():
                raise ValueError(
                    f"Placeholder '{{{{ {placeholder} }}}}' has invalid whitespace. "
                    f"Use '{{{{placeholder.strip()}}}}' instead."
                )

            # Check for valid identifier (alphanumeric + underscore)
            clean = placeholder.strip()
            # Allow conditional syntax like #if, /if
            if clean.startswith('#') or clean.startswith('/'):
                continue
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', clean):
                raise ValueError(
                    f"Invalid placeholder name: '{clean}'. "
                    "Use only letters, numbers, and underscores."
                )

        return v

    @model_validator(mode='after')
    def validate_variables_defined(self) -> 'PromptTemplate':
        """
        Ensure all placeholders in system_prompt have defaults defined.

        Skips conditional syntax ({{#if}}, {{/if}}).
        """
        # Extract simple placeholders (not conditionals)
        placeholders = set()
        for match in re.finditer(r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}', self.system_prompt):
            placeholders.add(match.group(1))

        defined_vars = set(self.variables.keys())
        undefined = placeholders - defined_vars

        if undefined:
            raise ValueError(
                f"Undefined variables in system_prompt: {undefined}. "
                f"Add defaults to 'variables' section."
            )

        return self

    def get_placeholders(self) -> List[str]:
        """Extract all placeholder names from the prompt."""
        placeholders = []
        for match in re.finditer(r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}', self.system_prompt):
            name = match.group(1)
            if name not in placeholders:
                placeholders.append(name)
        return placeholders


class SegmentTemplate(BaseModel):
    """
    A reusable prompt segment.

    Segments can be included in multiple templates for DRY (Don't Repeat Yourself).
    """

    metadata: TemplateMetadata
    content: str = Field(
        ...,
        min_length=1,
        description="The segment content"
    )

    @field_validator('metadata')
    @classmethod
    def validate_segment_type(cls, v: TemplateMetadata) -> TemplateMetadata:
        """Ensure metadata indicates this is a segment."""
        if not v.tags:
            v.tags = ['segment']
        elif 'segment' not in v.tags:
            v.tags.append('segment')
        return v


class CachedTemplate(BaseModel):
    """
    Cached template with metadata for invalidation.

    Tracks file modification time for hot-reload support.
    """

    template: PromptTemplate
    file_path: str
    loaded_at: datetime = Field(default_factory=datetime.now)
    file_mtime: float = Field(..., description="File modification time from os.stat")

    class Config:
        arbitrary_types_allowed = True

    def is_stale(self, current_mtime: float) -> bool:
        """Check if file has been modified since load."""
        return current_mtime > self.file_mtime


class CachedSegment(BaseModel):
    """Cached segment with modification tracking."""

    segment: SegmentTemplate
    file_path: str
    loaded_at: datetime = Field(default_factory=datetime.now)
    file_mtime: float


class RenderedCache(BaseModel):
    """
    Cache for rendered (variable-substituted) prompts.

    Uses variable hash as key for efficient lookup.
    """

    cache: Dict[str, str] = Field(
        default_factory=dict,
        description="Hash of variables -> rendered prompt"
    )
    max_size: int = Field(default=100, description="Maximum cache entries")

    def get(self, variables_hash: str) -> Optional[str]:
        """Get cached rendered prompt."""
        return self.cache.get(variables_hash)

    def set(self, variables_hash: str, rendered: str) -> None:
        """Cache a rendered prompt with LRU eviction."""
        if len(self.cache) >= self.max_size:
            # Simple eviction: remove first item (oldest in insertion order)
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        self.cache[variables_hash] = rendered

    def clear(self) -> None:
        """Clear all cached renders."""
        self.cache.clear()


# Type aliases for cleaner code
VariablesDict = Dict[str, Any]
ConditionalSectionsDict = Dict[str, Dict[str, str]]


def hash_variables(variables: VariablesDict) -> str:
    """
    Create a hash key from variables dict for cache lookup.

    Uses sorted keys for consistent ordering.
    """
    import hashlib
    import json

    sorted_str = json.dumps(variables, sort_keys=True, default=str)
    return hashlib.md5(sorted_str.encode()).hexdigest()[:16]
