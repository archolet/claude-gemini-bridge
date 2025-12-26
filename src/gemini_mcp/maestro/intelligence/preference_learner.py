"""
MAESTRO Preference Learner - Phase 6.3

Learns user preferences from session history to:
- Pre-fill common choices
- Suggest frequently used themes/components
- Remember project-specific patterns
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class PreferenceType(Enum):
    """Types of learnable preferences."""
    THEME = "theme"
    COMPONENT = "component"
    QUALITY_LEVEL = "quality_level"
    LANGUAGE = "language"
    ACCESSIBILITY = "accessibility"
    DARK_MODE = "dark_mode"


@dataclass
class UserPreference:
    """A learned user preference."""
    preference_type: PreferenceType
    value: str
    frequency: int = 1
    last_used: datetime = field(default_factory=datetime.now)
    confidence: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.preference_type.value,
            "value": self.value,
            "frequency": self.frequency,
            "last_used": self.last_used.isoformat(),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserPreference:
        """Create from dictionary."""
        return cls(
            preference_type=PreferenceType(data["type"]),
            value=data["value"],
            frequency=data.get("frequency", 1),
            last_used=datetime.fromisoformat(data["last_used"]) if "last_used" in data else datetime.now(),
            confidence=data.get("confidence", 0.5),
        )


@dataclass
class PreferencePattern:
    """A pattern of related preferences."""
    name: str
    preferences: dict[str, str] = field(default_factory=dict)
    usage_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "preferences": self.preferences,
            "usage_count": self.usage_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PreferencePattern:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            preferences=data.get("preferences", {}),
            usage_count=data.get("usage_count", 0),
        )


# Default preference patterns for new users
DEFAULT_PATTERNS: dict[str, PreferencePattern] = {
    "corporate": PreferencePattern(
        name="Kurumsal",
        preferences={
            "theme": "corporate",
            "quality_level": "premium",
            "accessibility": "AA",
            "dark_mode": "true",
        }
    ),
    "startup": PreferencePattern(
        name="Startup",
        preferences={
            "theme": "modern-minimal",
            "quality_level": "production",
            "accessibility": "AA",
            "dark_mode": "true",
        }
    ),
    "creative": PreferencePattern(
        name="Yaratıcı",
        preferences={
            "theme": "gradient",
            "quality_level": "high",
            "accessibility": "AA",
            "dark_mode": "true",
        }
    ),
}


class PreferenceLearner:
    """
    Learns and applies user preferences.

    Stores preferences in a JSON file for persistence across sessions.
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """
        Initialize preference learner.

        Args:
            storage_path: Path to store preferences. If None, uses temp directory.
        """
        self._storage_path = storage_path or Path(".gemini/maestro_preferences.json")
        self._preferences: dict[str, UserPreference] = {}
        self._patterns: dict[str, PreferencePattern] = DEFAULT_PATTERNS.copy()
        self._load()

    def _load(self) -> None:
        """Load preferences from storage."""
        if not self._storage_path.exists():
            return

        try:
            data = json.loads(self._storage_path.read_text())

            # Load individual preferences
            for pref_data in data.get("preferences", []):
                pref = UserPreference.from_dict(pref_data)
                key = f"{pref.preference_type.value}:{pref.value}"
                self._preferences[key] = pref

            # Load patterns
            for pattern_data in data.get("patterns", []):
                pattern = PreferencePattern.from_dict(pattern_data)
                self._patterns[pattern.name] = pattern

        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid file, start fresh
            pass

    def _save(self) -> None:
        """Save preferences to storage."""
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "preferences": [p.to_dict() for p in self._preferences.values()],
                "patterns": [p.to_dict() for p in self._patterns.values()
                            if p.usage_count > 0],  # Only save used patterns
                "updated_at": datetime.now().isoformat(),
            }

            self._storage_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        except OSError:
            # Failed to save, continue without persistence
            pass

    def learn(self, preference_type: PreferenceType, value: str) -> None:
        """
        Learn a user preference from their choice.

        Args:
            preference_type: Type of preference
            value: The chosen value
        """
        key = f"{preference_type.value}:{value}"

        if key in self._preferences:
            pref = self._preferences[key]
            pref.frequency += 1
            pref.last_used = datetime.now()
            # Increase confidence with usage
            pref.confidence = min(0.95, pref.confidence + 0.05)
        else:
            self._preferences[key] = UserPreference(
                preference_type=preference_type,
                value=value,
                frequency=1,
                confidence=0.5,
            )

        self._save()

    def learn_from_session(self, session_data: dict[str, Any]) -> None:
        """
        Learn preferences from a completed session.

        Args:
            session_data: Session data with answers and decision
        """
        answers = session_data.get("answers", {})
        decision = session_data.get("decision", {})

        # Learn from specific answers
        preference_mappings = {
            "q_theme_style": PreferenceType.THEME,
            "q_quality_level": PreferenceType.QUALITY_LEVEL,
            "q_accessibility_level": PreferenceType.ACCESSIBILITY,
            "q_dark_mode": PreferenceType.DARK_MODE,
        }

        for question_id, pref_type in preference_mappings.items():
            if question_id in answers:
                answer = answers[question_id]
                if isinstance(answer, list) and answer:
                    self.learn(pref_type, answer[0])
                elif isinstance(answer, str):
                    self.learn(pref_type, answer)

        # Learn from decision parameters
        params = decision.get("parameters", {})
        if "theme" in params:
            self.learn(PreferenceType.THEME, params["theme"])
        if "quality_target" in params:
            self.learn(PreferenceType.QUALITY_LEVEL, params["quality_target"])

    def get_preference(
        self,
        preference_type: PreferenceType,
        min_confidence: float = 0.6
    ) -> UserPreference | None:
        """
        Get the most likely preference for a type.

        Args:
            preference_type: Type to look up
            min_confidence: Minimum confidence threshold

        Returns:
            Most confident preference or None
        """
        candidates = [
            p for p in self._preferences.values()
            if p.preference_type == preference_type and p.confidence >= min_confidence
        ]

        if not candidates:
            return None

        # Sort by confidence * frequency (weighted)
        candidates.sort(
            key=lambda p: p.confidence * (1 + 0.1 * p.frequency),
            reverse=True
        )

        return candidates[0]

    def get_suggestions(
        self,
        preference_type: PreferenceType,
        limit: int = 3
    ) -> list[dict[str, Any]]:
        """
        Get suggested values for a preference type.

        Args:
            preference_type: Type to get suggestions for
            limit: Maximum suggestions

        Returns:
            List of suggestions with confidence scores
        """
        candidates = [
            p for p in self._preferences.values()
            if p.preference_type == preference_type
        ]

        # Sort by confidence and recency
        candidates.sort(
            key=lambda p: (p.confidence, p.last_used),
            reverse=True
        )

        return [
            {
                "value": p.value,
                "confidence": p.confidence,
                "frequency": p.frequency,
                "reason": f"{p.frequency} kez kullanıldı",
            }
            for p in candidates[:limit]
        ]

    def get_pattern_suggestions(self) -> list[dict[str, Any]]:
        """
        Get suggested preference patterns.

        Returns:
            List of pattern suggestions
        """
        # Sort by usage count
        patterns = sorted(
            self._patterns.values(),
            key=lambda p: p.usage_count,
            reverse=True
        )

        return [
            {
                "name": p.name,
                "preferences": p.preferences,
                "usage_count": p.usage_count,
            }
            for p in patterns[:5]
        ]

    def apply_pattern(self, pattern_name: str) -> dict[str, str]:
        """
        Apply a preference pattern.

        Args:
            pattern_name: Name of pattern to apply

        Returns:
            Dictionary of preferences from the pattern
        """
        pattern = self._patterns.get(pattern_name)
        if pattern:
            pattern.usage_count += 1
            self._save()
            return pattern.preferences.copy()
        return {}

    def create_pattern(
        self,
        name: str,
        preferences: dict[str, str]
    ) -> PreferencePattern:
        """
        Create a new preference pattern.

        Args:
            name: Pattern name
            preferences: Dictionary of preferences

        Returns:
            Created pattern
        """
        pattern = PreferencePattern(
            name=name,
            preferences=preferences,
            usage_count=1,
        )
        self._patterns[name] = pattern
        self._save()
        return pattern

    def to_dict(self) -> dict[str, Any]:
        """Convert learner state to dictionary."""
        return {
            "total_preferences": len(self._preferences),
            "patterns_count": len(self._patterns),
            "top_preferences": [
                {"type": p.preference_type.value, "value": p.value, "confidence": p.confidence}
                for p in sorted(
                    self._preferences.values(),
                    key=lambda x: x.confidence,
                    reverse=True
                )[:5]
            ],
        }
