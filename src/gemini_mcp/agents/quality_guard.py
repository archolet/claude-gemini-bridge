"""
The Quality Guard - QA & Validation Specialist

The Quality Guard is the final checkpoint in the pipeline:
1. Validates HTML, CSS, and JS outputs
2. Performs cross-layer validation (ID consistency)
3. Applies auto-fixes for common issues
4. Reports validation results with severity levels

This agent uses the validation module for systematic checks.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from gemini_mcp.agents.base import AgentConfig, AgentResult, AgentRole, BaseAgent
from gemini_mcp.prompts import QUALITY_GUARD_SYSTEM_PROMPT
from gemini_mcp.validation import HTMLValidator, CSSValidator, JSValidator, IDValidator

if TYPE_CHECKING:
    from gemini_mcp.client import GeminiClient
    from gemini_mcp.orchestration.context import AgentContext

logger = logging.getLogger(__name__)


@dataclass
class QAReport:
    """Quality assurance report from The Quality Guard."""

    validation_passed: bool
    issues: list[dict] = field(default_factory=list)
    auto_fixes_applied: list[str] = field(default_factory=list)
    corrected_output: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "validation_passed": self.validation_passed,
            "issues": self.issues,
            "auto_fixes_applied": self.auto_fixes_applied,
            "corrected_output": self.corrected_output,
        }

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.get("severity") == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.get("severity") == "warning")


class QualityGuardAgent(BaseAgent):
    """
    The Quality Guard - QA & Validation Specialist.

    Validates all outputs from the Trifecta pipeline and applies auto-fixes.
    """

    role = AgentRole.QUALITY_GUARD

    def __init__(
        self,
        client: "GeminiClient",
        config: Optional[AgentConfig] = None,
    ):
        """
        Initialize The Quality Guard.

        Args:
            client: GeminiClient for API calls (used for complex fixes)
            config: Optional custom configuration
        """
        super().__init__(config)
        self.client = client

        # Initialize validators
        self.html_validator = HTMLValidator(strict_mode=False)
        self.css_validator = CSSValidator(strict_mode=False)
        self.js_validator = JSValidator(strict_mode=False)
        self.id_validator = IDValidator(strict_mode=True)

    @classmethod
    def _default_config(cls) -> AgentConfig:
        """Quality Guard-specific default configuration."""
        return AgentConfig(
            model="gemini-3-pro-preview",
            thinking_level="low",  # Validation - minimal reasoning needed
            thinking_budget=2048,  # Deprecated
            temperature=1.0,  # Gemini 3 optimized
            max_output_tokens=8192,
            strict_mode=True,
            auto_fix=True,
        )

    def get_system_prompt(self) -> str:
        """Return The Quality Guard's system prompt."""
        return QUALITY_GUARD_SYSTEM_PROMPT

    async def execute(self, context: "AgentContext") -> AgentResult:
        """
        Validate and auto-fix pipeline outputs.

        Args:
            context: Pipeline context with HTML/CSS/JS outputs

        Returns:
            AgentResult with QA report and corrected outputs
        """
        import time

        start_time = time.time()

        try:
            # Get outputs to validate
            html = context.html_output or ""
            css = context.css_output or ""
            js = context.js_output or ""

            # Create QA report
            qa_report = QAReport(validation_passed=True)

            # Validate each layer
            qa_report = self._validate_html(html, qa_report)
            qa_report = self._validate_css(css, qa_report)
            qa_report = self._validate_js(js, qa_report)

            # Cross-layer validation
            if html and js:
                qa_report = self._validate_cross_layer(html, js, qa_report)

            # Apply auto-fixes if enabled
            corrected_html = html
            corrected_css = css
            corrected_js = js

            if self.config.auto_fix and qa_report.error_count > 0:
                corrected_html, fixes_html = self._auto_fix_html(html)
                corrected_css, fixes_css = self._auto_fix_css(css)
                corrected_js, fixes_js = self._auto_fix_js(js)

                qa_report.auto_fixes_applied.extend(fixes_html)
                qa_report.auto_fixes_applied.extend(fixes_css)
                qa_report.auto_fixes_applied.extend(fixes_js)

            # Store corrected output
            qa_report.corrected_output = {
                "html": corrected_html,
                "css": corrected_css,
                "js": corrected_js,
            }

            # Update validation status after fixes
            qa_report.validation_passed = qa_report.error_count == 0

            # Create result
            result = AgentResult(
                success=qa_report.validation_passed,
                output=json.dumps(qa_report.to_dict(), indent=2, ensure_ascii=False),
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                warnings=[
                    i["message"] for i in qa_report.issues
                    if i.get("severity") == "warning"
                ],
            )

            # Attach QA report to metadata
            result.metadata = {
                "qa_report": qa_report.to_dict(),
                "corrected_html": corrected_html,
                "corrected_css": corrected_css,
                "corrected_js": corrected_js,
            }

            logger.info(
                f"[Quality Guard] Validation: {qa_report.validation_passed}, "
                f"Errors: {qa_report.error_count}, Warnings: {qa_report.warning_count}, "
                f"Fixes: {len(qa_report.auto_fixes_applied)}"
            )

            return result

        except Exception as e:
            logger.error(f"[Quality Guard] Execution failed: {e}")
            return AgentResult(
                success=False,
                output="",
                agent_role=self.role,
                execution_time_ms=(time.time() - start_time) * 1000,
                errors=[str(e)],
            )

    def _validate_html(self, html: str, report: QAReport) -> QAReport:
        """Validate HTML output."""
        if not html:
            return report

        result = self.html_validator.validate(html)

        for issue in result.issues:
            report.issues.append({
                "severity": issue.severity.value,
                "layer": "html",
                "message": issue.message,
                "fix": issue.suggestion,
            })

        if not result.valid:
            report.validation_passed = False

        return report

    def _validate_css(self, css: str, report: QAReport) -> QAReport:
        """Validate CSS output."""
        if not css:
            return report

        result = self.css_validator.validate(css)

        for issue in result.issues:
            report.issues.append({
                "severity": issue.severity.value,
                "layer": "css",
                "message": issue.message,
                "fix": issue.suggestion,
            })

        if not result.valid:
            report.validation_passed = False

        return report

    def _validate_js(self, js: str, report: QAReport) -> QAReport:
        """Validate JavaScript output."""
        if not js:
            return report

        result = self.js_validator.validate(js)

        for issue in result.issues:
            report.issues.append({
                "severity": issue.severity.value,
                "layer": "js",
                "message": issue.message,
                "fix": issue.suggestion,
            })

        if not result.valid:
            report.validation_passed = False

        return report

    def _validate_cross_layer(self, html: str, js: str, report: QAReport) -> QAReport:
        """Validate cross-layer consistency."""
        result = self.id_validator.validate(html, js)

        for issue in result.issues:
            report.issues.append({
                "severity": issue.severity.value,
                "layer": "cross",
                "message": issue.message,
                "fix": issue.suggestion,
            })

        if not result.valid:
            report.validation_passed = False

        return report

    def _auto_fix_html(self, html: str) -> tuple[str, list[str]]:
        """Apply auto-fixes to HTML."""
        fixes = []
        fixed = html

        # Fix 1: Remove inline styles
        if re.search(r'style=["\'][^"\']+["\']', fixed):
            fixed = re.sub(r'\s*style=["\'][^"\']+["\']', '', fixed)
            fixes.append("Removed inline style attributes")

        # Fix 2: Remove event handlers
        event_handlers = ["onclick", "onmouseover", "onmouseout", "onchange", "onsubmit"]
        for handler in event_handlers:
            pattern = rf'\s*{handler}=["\'][^"\']*["\']'
            if re.search(pattern, fixed, re.IGNORECASE):
                fixed = re.sub(pattern, '', fixed, flags=re.IGNORECASE)
                fixes.append(f"Removed {handler} event handler")

        # Fix 3: Remove <style> tags
        if re.search(r'<style[^>]*>[\s\S]*?</style>', fixed, re.IGNORECASE):
            fixed = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', fixed, flags=re.IGNORECASE)
            fixes.append("Removed <style> tags")

        # Fix 4: Remove <script> tags
        if re.search(r'<script[^>]*>[\s\S]*?</script>', fixed, re.IGNORECASE):
            fixed = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', fixed, flags=re.IGNORECASE)
            fixes.append("Removed <script> tags")

        return fixed.strip(), fixes

    def _auto_fix_css(self, css: str) -> tuple[str, list[str]]:
        """Apply auto-fixes to CSS."""
        fixes = []
        fixed = css

        # Fix 1: Remove HTML tags
        if re.search(r'<[a-z]+', fixed, re.IGNORECASE):
            fixed = re.sub(r'<[^>]+>', '', fixed)
            fixes.append("Removed HTML tags from CSS")

        # Fix 2: Add missing vendor prefixes for backdrop-filter
        if 'backdrop-filter' in fixed and '-webkit-backdrop-filter' not in fixed:
            fixed = re.sub(
                r'(\s*)backdrop-filter:\s*([^;]+);',
                r'\1-webkit-backdrop-filter: \2;\1backdrop-filter: \2;',
                fixed
            )
            fixes.append("Added -webkit-backdrop-filter prefix")

        # Fix 3: Remove excessive !important (keep first 3)
        important_count = len(re.findall(r'!important', fixed))
        if important_count > 3:
            # Replace !important with empty string after first 3
            count = [0]

            def replace_important(match):
                count[0] += 1
                return match.group(0) if count[0] <= 3 else match.group(0).replace('!important', '')

            fixed = re.sub(r'[^;]*!important', replace_important, fixed)
            fixes.append(f"Reduced !important usage from {important_count} to 3")

        return fixed.strip(), fixes

    def _auto_fix_js(self, js: str) -> tuple[str, list[str]]:
        """Apply auto-fixes to JavaScript."""
        fixes = []
        fixed = js

        # Fix 1: Remove import statements
        if re.search(r'^\s*import\s+', fixed, re.MULTILINE):
            fixed = re.sub(r'^\s*import\s+.*$', '', fixed, flags=re.MULTILINE)
            fixes.append("Removed import statements")

        # Fix 2: Remove require statements
        if re.search(r'require\s*\(', fixed):
            fixed = re.sub(r'^\s*(?:const|let|var)\s+\w+\s*=\s*require\s*\([^)]+\)\s*;?', '', fixed, flags=re.MULTILINE)
            fixes.append("Removed require statements")

        # Fix 3: Wrap in IIFE if not wrapped
        is_wrapped = bool(re.search(r'^\s*\(function\s*\(', fixed)) or \
                    bool(re.search(r'^\s*\(\s*\(\s*\)\s*=>', fixed))

        if not is_wrapped and fixed.strip():
            fixed = f"""(function() {{
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {{
    try {{
{self._indent(fixed, 6)}
    }} catch (error) {{
      console.error('Initialization error:', error);
    }}
  }});
}})();"""
            fixes.append("Wrapped code in IIFE with error handling")

        return fixed.strip(), fixes

    def _indent(self, text: str, spaces: int) -> str:
        """Indent all lines by given number of spaces."""
        prefix = " " * spaces
        lines = text.split("\n")
        return "\n".join(prefix + line if line.strip() else line for line in lines)

    def validate_output(self, output: str) -> tuple[bool, list[str]]:
        """
        Validate Quality Guard output (JSON report).
        """
        issues = []

        if not output or not output.strip():
            return True, []

        try:
            data = json.loads(output)
            if "validation_passed" not in data:
                issues.append("Missing 'validation_passed' field in report")
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON report: {e}")

        return len(issues) == 0, issues

    def auto_fix_output(self, output: str) -> str:
        """Quality Guard output is already the final corrected output."""
        return output

    def get_quick_report(self, html: str, css: str, js: str) -> dict:
        """
        Generate a quick validation report without API call.

        Returns a summary dictionary.
        """
        html_result = self.html_validator.validate(html) if html else None
        css_result = self.css_validator.validate(css) if css else None
        js_result = self.js_validator.validate(js) if js else None

        cross_result = None
        if html and js:
            cross_result = self.id_validator.validate(html, js)

        total_errors = 0
        total_warnings = 0

        if html_result:
            total_errors += html_result.error_count
            total_warnings += html_result.warning_count
        if css_result:
            total_errors += css_result.error_count
            total_warnings += css_result.warning_count
        if js_result:
            total_errors += js_result.error_count
            total_warnings += js_result.warning_count
        if cross_result:
            total_errors += cross_result.error_count
            total_warnings += cross_result.warning_count

        return {
            "valid": total_errors == 0,
            "errors": total_errors,
            "warnings": total_warnings,
            "html_valid": html_result.valid if html_result else True,
            "css_valid": css_result.valid if css_result else True,
            "js_valid": js_result.valid if js_result else True,
            "cross_layer_valid": cross_result.valid if cross_result else True,
        }
