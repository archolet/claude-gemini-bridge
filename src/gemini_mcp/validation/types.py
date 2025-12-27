"""
Shared Validation Types for Gemini MCP Server.

This module contains base types used across all validators:
- ValidationSeverity: Severity levels for issues
- ValidationIssue: Individual validation issue
- ValidationResult: Collection of issues with validity status

All validators should import from this module to avoid duplication.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ValidationSeverity(Enum):
    """
    Severity level for validation issues.

    Used consistently across all validators:
    - CRITICAL: Deployment blocker - must be auto-fixed immediately
    - ERROR: Critical issue that must be fixed (degraded experience)
    - WARNING: Issue that should be addressed (may pass but should fix)
    - INFO: Informational message or suggestion (optional improvements)

    Severity order (highest to lowest): CRITICAL > ERROR > WARNING > INFO
    """

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    @classmethod
    def get_order(cls, severity: "ValidationSeverity") -> int:
        """Get numeric order for severity comparison (higher = more severe)."""
        return {
            cls.INFO: 0,
            cls.WARNING: 1,
            cls.ERROR: 2,
            cls.CRITICAL: 3,
        }.get(severity, 0)


@dataclass
class ValidationIssue:
    """
    A single validation issue.

    Represents an issue found during validation with context
    about its severity, location, and potential fixes.
    """

    severity: ValidationSeverity
    message: str
    line: Optional[int] = None
    suggestion: Optional[str] = None
    location: Optional[str] = None
    rule: Optional[str] = None
    auto_fixable: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "severity": self.severity.value,
            "message": self.message,
        }
        if self.line is not None:
            result["line"] = self.line
        if self.suggestion is not None:
            result["suggestion"] = self.suggestion
        if self.location is not None:
            result["location"] = self.location
        if self.rule is not None:
            result["rule"] = self.rule
        if self.auto_fixable:
            result["auto_fixable"] = self.auto_fixable
        return result


@dataclass
class ValidationResult:
    """
    Result of validation containing all issues found.

    Provides convenience properties for counting errors and warnings,
    and methods for serialization.
    """

    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        """Count of CRITICAL severity issues (deployment blockers)."""
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.CRITICAL)

    @property
    def error_count(self) -> int:
        """Count of ERROR severity issues."""
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of WARNING severity issues."""
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING)

    @property
    def info_count(self) -> int:
        """Count of INFO severity issues."""
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.INFO)

    @property
    def has_blockers(self) -> bool:
        """Check if there are any deployment-blocking issues (CRITICAL)."""
        return self.critical_count > 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "valid": self.valid,
            "critical_count": self.critical_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [i.to_dict() for i in self.issues],
        }

    def merge(self, other: ValidationResult) -> ValidationResult:
        """
        Merge another ValidationResult into this one.

        The resulting validity is AND of both results.
        """
        return ValidationResult(
            valid=self.valid and other.valid,
            issues=self.issues + other.issues,
        )


# Backward compatibility aliases
# AnimationSeverity was a duplicate of ValidationSeverity
AnimationSeverity = ValidationSeverity
