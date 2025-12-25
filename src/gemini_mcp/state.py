"""
Design State Management Module for Gemini MCP.

This module handles:
1. Automatic persistence of design artifacts (HTML, CSS, JSON) to disk.
2. Project state tracking (manifests).
3. Draft management for iterative workflows.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Default location for temporary designs
# Users can override this via env var GEMINI_DRAFT_DIR
DEFAULT_DRAFT_DIR = os.environ.get("GEMINI_DRAFT_DIR", "./temp_designs")


@dataclass
class DesignArtifact:
    """Represents a generated design asset."""
    id: str
    type: str  # 'html', 'css', 'json', 'meta'
    path: str
    created_at: str
    component_type: str
    model_used: str


class DraftManager:
    """Manages separate draft files for generated designs."""

    def __init__(self, root_dir: str = DEFAULT_DRAFT_DIR):
        self.root = Path(root_dir).resolve()
        self._ensure_root()
        logger.info(f"DraftManager initialized at {self.root}")

    def _ensure_root(self):
        """Ensure root directory exists."""
        self.root.mkdir(parents=True, exist_ok=True)

    def _get_project_dir(self, project_name: str) -> Path:
        """Get or create project-specific directory."""
        project_dir = self.root / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    def save_artifact(
        self,
        content: Any,
        extension: str,
        project_name: str = "default",
        component_type: str = "unknown",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save a design artifact to disk.
        Returns the absolute path to the saved file.
        """
        project_dir = self._get_project_dir(project_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a unique filename
        # e.g., 20251223_143000_hero_v1.html
        filename = f"{timestamp}_{component_type}.{extension}"
        file_path = project_dir / filename

        # Write content
        try:
            if extension == "json" or isinstance(content, (dict, list)):
                with open(file_path, "w", encoding="utf-8") as f:
                    # If content is string but ext is json, try to parse first to pretty print
                    if isinstance(content, str):
                        try:
                            content = json.loads(content)
                        except:
                            pass
                    json.dump(content, f, indent=2, ensure_ascii=False)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(str(content))
            
            # If metadata provided, save sidecar file
            if metadata:
                meta_path = file_path.with_suffix(".meta.json")
                with open(meta_path, "w", encoding="utf-8") as f:
                    # Enforce timestamp in metadata
                    metadata["saved_at"] = timestamp
                    metadata["original_file"] = str(file_path)
                    json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved artifact: {file_path}")
            
            # Update project manifest
            self._update_manifest(project_name, {
                "id": f"{timestamp}_{component_type}",
                "type": extension,
                "path": str(file_path),
                "created_at": timestamp,
                "component_type": component_type,
                "model_used": metadata.get("model_used", "unknown") if metadata else "unknown"
            })

            return str(file_path)

        except Exception as e:
            logger.error(f"Failed to save artifact {filename}: {e}")
            return ""

    def _update_manifest(self, project_name: str, artifact_info: Dict):
        """Update the project's manifest.json file."""
        project_dir = self._get_project_dir(project_name)
        manifest_path = project_dir / "manifest.json"

        manifest = {"project": project_name, "artifacts": [], "last_updated": ""}
        
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                logger.warning(f"Corrupt manifest at {manifest_path}, creating new one.")

        # Add new artifact
        manifest["artifacts"].append(artifact_info)
        manifest["last_updated"] = datetime.now().isoformat()

        # Write back
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    def list_drafts(self, project_name: str = "default") -> List[Dict]:
        """List all drafts for a project."""
        project_dir = self._get_project_dir(project_name)
        manifest_path = project_dir / "manifest.json"
        
        if not manifest_path.exists():
            return []
            
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("artifacts", [])
        except Exception:
            return []

    def get_latest_draft(self, project_name: str = "default", component_type: str = "") -> Optional[Dict]:
        """Get the most recent draft for a specific component."""
        drafts = self.list_drafts(project_name)
        if not drafts:
            return None
            
        # Filter by component if requested
        if component_type:
            drafts = [d for d in drafts if d.get("component_type") == component_type]
            
        if not drafts:
            return None
            
        # Sort by creation time (descending)
        drafts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return drafts[0]

# Global instance
draft_manager = DraftManager()
