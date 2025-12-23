"""
DNAStore - Persistent Storage for Design DNA

This module provides persistent storage for Design DNA, enabling:
- Cross-session DNA retrieval ("Use the colors from previous Navbar")
- Project-based DNA organization
- DNA search by component type, theme, or project

Storage Format: JSON file at ~/.gemini-mcp/dna_db.json

Usage:
    store = DNAStore()
    dna_id = store.save("navbar", "cyberpunk", dna, project_id="my-saas")
    dna = store.get(dna_id)
    dna = store.get_latest("navbar", project_id="my-saas")
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from gemini_mcp.orchestration.context import DesignDNA

logger = logging.getLogger(__name__)


@dataclass
class DNAEntry:
    """A stored DNA entry with metadata."""

    dna_id: str
    component_type: str
    theme: str
    project_id: str
    created_at: str  # ISO format
    dna: DesignDNA

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "dna_id": self.dna_id,
            "component_type": self.component_type,
            "theme": self.theme,
            "project_id": self.project_id,
            "created_at": self.created_at,
            "dna": self.dna.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DNAEntry":
        """Create from dictionary."""
        return cls(
            dna_id=data["dna_id"],
            component_type=data["component_type"],
            theme=data["theme"],
            project_id=data["project_id"],
            created_at=data["created_at"],
            dna=DesignDNA.from_dict(data["dna"]),
        )


class DNAStore:
    """
    Persistent storage for Design DNA.

    Stores DNA entries in a JSON file with indices for fast lookup.
    Supports project-based organization and various search criteria.
    """

    VERSION = "1.0"
    DEFAULT_PATH = "~/.gemini-mcp/dna_db.json"

    def __init__(self, db_path: str = DEFAULT_PATH, max_entries: int = 500):
        """
        Initialize DNAStore.

        Args:
            db_path: Path to the JSON database file
            max_entries: Maximum number of entries to keep (LRU eviction)
        """
        self.db_path = Path(db_path).expanduser()
        self.max_entries = max_entries
        self._data: dict[str, Any] = {}
        self._load()

    def _ensure_dir(self) -> None:
        """Ensure the database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        """Load database from disk."""
        self._ensure_dir()

        if self.db_path.exists():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                logger.debug(f"[DNAStore] Loaded {len(self._data.get('entries', {}))} entries")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"[DNAStore] Failed to load database: {e}")
                self._init_empty()
        else:
            self._init_empty()

    def _init_empty(self) -> None:
        """Initialize an empty database."""
        self._data = {
            "version": self.VERSION,
            "entries": {},
            "index": {
                "by_component": {},
                "by_theme": {},
                "by_project": {},
            },
        }

    def _save(self) -> None:
        """Save database to disk."""
        self._ensure_dir()
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            logger.debug(f"[DNAStore] Saved {len(self._data.get('entries', {}))} entries")
        except IOError as e:
            logger.error(f"[DNAStore] Failed to save database: {e}")

    def _generate_id(self) -> str:
        """Generate a unique DNA ID."""
        return f"dna_{uuid.uuid4().hex[:8]}"

    def _add_to_index(
        self, dna_id: str, component_type: str, theme: str, project_id: str
    ) -> None:
        """Add entry to indices."""
        # By component
        if component_type not in self._data["index"]["by_component"]:
            self._data["index"]["by_component"][component_type] = []
        if dna_id not in self._data["index"]["by_component"][component_type]:
            self._data["index"]["by_component"][component_type].append(dna_id)

        # By theme
        if theme not in self._data["index"]["by_theme"]:
            self._data["index"]["by_theme"][theme] = []
        if dna_id not in self._data["index"]["by_theme"][theme]:
            self._data["index"]["by_theme"][theme].append(dna_id)

        # By project
        if project_id not in self._data["index"]["by_project"]:
            self._data["index"]["by_project"][project_id] = []
        if dna_id not in self._data["index"]["by_project"][project_id]:
            self._data["index"]["by_project"][project_id].append(dna_id)

    def _remove_from_index(
        self, dna_id: str, component_type: str, theme: str, project_id: str
    ) -> None:
        """Remove entry from indices."""
        for index_name, key in [
            ("by_component", component_type),
            ("by_theme", theme),
            ("by_project", project_id),
        ]:
            if key in self._data["index"][index_name]:
                ids = self._data["index"][index_name][key]
                if dna_id in ids:
                    ids.remove(dna_id)
                if not ids:
                    del self._data["index"][index_name][key]

    def _evict_oldest(self) -> None:
        """Evict oldest entries if we exceed max_entries."""
        entries = self._data.get("entries", {})
        if len(entries) <= self.max_entries:
            return

        # Sort by created_at
        sorted_entries = sorted(
            entries.items(),
            key=lambda x: x[1].get("created_at", ""),
        )

        # Remove oldest entries
        to_remove = len(entries) - self.max_entries
        for dna_id, entry in sorted_entries[:to_remove]:
            self._remove_from_index(
                dna_id,
                entry["component_type"],
                entry["theme"],
                entry["project_id"],
            )
            del entries[dna_id]

        logger.info(f"[DNAStore] Evicted {to_remove} oldest entries")

    def save(
        self,
        component_type: str,
        theme: str,
        dna: DesignDNA,
        project_id: str = "default",
    ) -> str:
        """
        Save a DNA entry.

        Args:
            component_type: The component type (navbar, hero, etc.)
            theme: The theme used (modern-minimal, cyberpunk, etc.)
            dna: The DesignDNA object to store
            project_id: Project identifier for organization

        Returns:
            The generated dna_id for retrieval
        """
        dna_id = self._generate_id()
        created_at = datetime.now().isoformat()

        entry = DNAEntry(
            dna_id=dna_id,
            component_type=component_type,
            theme=theme,
            project_id=project_id,
            created_at=created_at,
            dna=dna,
        )

        self._data["entries"][dna_id] = entry.to_dict()
        self._add_to_index(dna_id, component_type, theme, project_id)
        self._evict_oldest()
        self._save()

        logger.info(
            f"[DNAStore] Saved DNA: {dna_id} "
            f"(component={component_type}, theme={theme}, project={project_id})"
        )

        return dna_id

    def get(self, dna_id: str) -> Optional[DesignDNA]:
        """
        Get a DNA entry by ID.

        Args:
            dna_id: The DNA ID to retrieve

        Returns:
            DesignDNA object if found, None otherwise
        """
        entry_data = self._data.get("entries", {}).get(dna_id)
        if entry_data:
            entry = DNAEntry.from_dict(entry_data)
            return entry.dna
        return None

    def get_entry(self, dna_id: str) -> Optional[DNAEntry]:
        """
        Get a full DNA entry by ID.

        Args:
            dna_id: The DNA ID to retrieve

        Returns:
            DNAEntry object if found, None otherwise
        """
        entry_data = self._data.get("entries", {}).get(dna_id)
        if entry_data:
            return DNAEntry.from_dict(entry_data)
        return None

    def get_latest(
        self,
        component_type: str,
        project_id: str = "default",
        theme: Optional[str] = None,
    ) -> Optional[DesignDNA]:
        """
        Get the most recent DNA for a component type.

        Args:
            component_type: The component type to search for
            project_id: Project to search in
            theme: Optional theme filter

        Returns:
            Most recent DesignDNA if found, None otherwise
        """
        # Get candidate IDs from indices
        component_ids = set(
            self._data["index"]["by_component"].get(component_type, [])
        )
        project_ids = set(self._data["index"]["by_project"].get(project_id, []))

        # Intersect with theme if provided
        if theme:
            theme_ids = set(self._data["index"]["by_theme"].get(theme, []))
            candidate_ids = component_ids & project_ids & theme_ids
        else:
            candidate_ids = component_ids & project_ids

        if not candidate_ids:
            return None

        # Find most recent
        entries = self._data.get("entries", {})
        latest_id = None
        latest_time = ""

        for dna_id in candidate_ids:
            entry = entries.get(dna_id)
            if entry and entry.get("created_at", "") > latest_time:
                latest_time = entry["created_at"]
                latest_id = dna_id

        if latest_id:
            return self.get(latest_id)
        return None

    def search(
        self,
        component_type: Optional[str] = None,
        theme: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[DNAEntry]:
        """
        Search DNA entries by criteria.

        Args:
            component_type: Filter by component type
            theme: Filter by theme
            project_id: Filter by project
            limit: Maximum results to return

        Returns:
            List of matching DNAEntry objects, sorted by created_at (newest first)
        """
        entries = self._data.get("entries", {})

        # Start with all entries if no filters
        candidate_ids = set(entries.keys())

        # Apply filters
        if component_type:
            component_ids = set(
                self._data["index"]["by_component"].get(component_type, [])
            )
            candidate_ids &= component_ids

        if theme:
            theme_ids = set(self._data["index"]["by_theme"].get(theme, []))
            candidate_ids &= theme_ids

        if project_id:
            project_ids = set(self._data["index"]["by_project"].get(project_id, []))
            candidate_ids &= project_ids

        # Convert to entries and sort
        results = []
        for dna_id in candidate_ids:
            entry_data = entries.get(dna_id)
            if entry_data:
                results.append(DNAEntry.from_dict(entry_data))

        # Sort by created_at (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)

        return results[:limit]

    def delete(self, dna_id: str) -> bool:
        """
        Delete a DNA entry by ID.

        Args:
            dna_id: The DNA ID to delete

        Returns:
            True if deleted, False if not found
        """
        entry_data = self._data.get("entries", {}).get(dna_id)
        if not entry_data:
            return False

        self._remove_from_index(
            dna_id,
            entry_data["component_type"],
            entry_data["theme"],
            entry_data["project_id"],
        )
        del self._data["entries"][dna_id]
        self._save()

        logger.info(f"[DNAStore] Deleted DNA: {dna_id}")
        return True

    def clear_project(self, project_id: str) -> int:
        """
        Delete all DNA entries for a project.

        Args:
            project_id: The project to clear

        Returns:
            Number of entries deleted
        """
        dna_ids = list(self._data["index"]["by_project"].get(project_id, []))
        count = 0

        for dna_id in dna_ids:
            if self.delete(dna_id):
                count += 1

        logger.info(f"[DNAStore] Cleared project {project_id}: {count} entries")
        return count

    def get_stats(self) -> dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage stats
        """
        entries = self._data.get("entries", {})
        return {
            "total_entries": len(entries),
            "max_entries": self.max_entries,
            "components": len(self._data["index"]["by_component"]),
            "themes": len(self._data["index"]["by_theme"]),
            "projects": len(self._data["index"]["by_project"]),
            "db_path": str(self.db_path),
        }

    def list_projects(self) -> list[str]:
        """Get list of all project IDs."""
        return list(self._data["index"]["by_project"].keys())

    def list_components(self, project_id: Optional[str] = None) -> list[str]:
        """
        Get list of component types.

        Args:
            project_id: Filter by project if provided

        Returns:
            List of component type names
        """
        if project_id:
            project_ids = set(self._data["index"]["by_project"].get(project_id, []))
            entries = self._data.get("entries", {})
            components = set()
            for dna_id in project_ids:
                entry = entries.get(dna_id)
                if entry:
                    components.add(entry["component_type"])
            return list(components)
        return list(self._data["index"]["by_component"].keys())


# Global DNAStore instance
_dna_store: Optional[DNAStore] = None


def get_dna_store() -> DNAStore:
    """Get or create the global DNAStore instance."""
    global _dna_store
    if _dna_store is None:
        _dna_store = DNAStore()
    return _dna_store


def reset_dna_store() -> None:
    """Reset the global DNAStore instance."""
    global _dna_store
    _dna_store = None
