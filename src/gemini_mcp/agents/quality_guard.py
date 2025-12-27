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
from gemini_mcp.prompts.prompt_loader import get_prompt
from gemini_mcp.validation import HTMLValidator, CSSValidator, JSValidator, IDValidator
from gemini_mcp.validation.anti_pattern_validator import AntiPatternValidator

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
            "critical_count": self.critical_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": self.issues,
            "auto_fixes_applied": self.auto_fixes_applied,
            "corrected_output": self.corrected_output,
        }

    @property
    def critical_count(self) -> int:
        """Count of CRITICAL severity issues (deployment blockers)."""
        return sum(1 for i in self.issues if i.get("severity") == "critical")

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.get("severity") == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.get("severity") == "warning")

    @property
    def has_blockers(self) -> bool:
        """Check if there are critical issues that block deployment."""
        return self.critical_count > 0


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

        # Enterprise anti-pattern validator (27 patterns across 4 categories)
        self.anti_pattern_validator = AntiPatternValidator()

    @classmethod
    def _default_config(cls) -> AgentConfig:
        """Quality Guard-specific default configuration."""
        return AgentConfig(
            model="gemini-3-pro-preview",
            thinking_level="high",  # Maximum reasoning for thorough quality validation
            temperature=1.0,  # Gemini 3 optimized
            max_output_tokens=8192,
            strict_mode=True,
            auto_fix=True,
        )

    def get_system_prompt(self, variables: dict[str, Any] | None = None) -> str:
        """Return The Quality Guard's system prompt from YAML template."""
        return get_prompt(
            agent_name="quality_guard",
            variables=variables or {},
        )

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

            # Enterprise anti-pattern validation (27 patterns)
            # This runs BEFORE auto-fixes to detect patterns, then applies fixes
            qa_report, html, css, js = self._validate_antipatterns(
                html, css, js, qa_report
            )

            # Apply auto-fixes if enabled
            corrected_html = html
            corrected_css = css
            corrected_js = js

            if self.config.auto_fix and (qa_report.error_count > 0 or qa_report.critical_count > 0):
                corrected_html, fixes_html = self._auto_fix_html(corrected_html)
                corrected_css, fixes_css = self._auto_fix_css(corrected_css)
                corrected_js, fixes_js = self._auto_fix_js(corrected_js)

                qa_report.auto_fixes_applied.extend(fixes_html)
                qa_report.auto_fixes_applied.extend(fixes_css)
                qa_report.auto_fixes_applied.extend(fixes_js)

            # Store corrected output
            qa_report.corrected_output = {
                "html": corrected_html,
                "css": corrected_css,
                "js": corrected_js,
            }

            # Update validation status after fixes (critical and error block deployment)
            qa_report.validation_passed = (
                qa_report.critical_count == 0 and qa_report.error_count == 0
            )

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
                f"Critical: {qa_report.critical_count}, Errors: {qa_report.error_count}, "
                f"Warnings: {qa_report.warning_count}, Fixes: {len(qa_report.auto_fixes_applied)}"
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

    def _validate_antipatterns(
        self, html: str, css: str, js: str, report: QAReport
    ) -> tuple[QAReport, str, str, str]:
        """
        Validate for enterprise anti-patterns and apply auto-fixes.

        This method uses AntiPatternValidator to detect:
        - Accessibility anti-patterns (no-skip-link, heading-skip, etc.)
        - Performance anti-patterns (layout-thrash-loop, sync-xhr, etc.)
        - Styling anti-patterns (fixed-width, no-dark-mode, etc.)
        - Alpine.js anti-patterns (sync-init, x-show without x-cloak, etc.)

        Returns:
            Tuple of (updated_report, fixed_html, fixed_css, fixed_js)
        """
        fixed_html = html
        fixed_css = css
        fixed_js = js

        # Combine all content for comprehensive anti-pattern detection
        combined_content = f"{html}\n{css}\n{js}"

        # First pass: detect and report all anti-patterns
        result = self.anti_pattern_validator.validate(combined_content)

        for issue in result.issues:
            report.issues.append({
                "severity": issue.severity.value,
                "layer": issue.rule.split("/")[0] if issue.rule else "antipattern",
                "message": issue.message,
                "fix": issue.suggestion,
                "rule": issue.rule,
                "auto_fixable": issue.auto_fixable,
            })

        # Second pass: apply auto-fixes if enabled
        if self.config.auto_fix:
            # Auto-fix HTML anti-patterns
            if html:
                fixed_html, html_result = self.anti_pattern_validator.validate_and_fix(html)
                for fix_issue in html_result.issues:
                    if fix_issue.message.startswith("Auto-fixed:"):
                        report.auto_fixes_applied.append(
                            fix_issue.message.replace("Auto-fixed: ", "")
                        )

            # Auto-fix CSS anti-patterns (if any fixable patterns apply)
            if css:
                fixed_css, css_result = self.anti_pattern_validator.validate_and_fix(css)
                for fix_issue in css_result.issues:
                    if fix_issue.message.startswith("Auto-fixed:"):
                        report.auto_fixes_applied.append(
                            fix_issue.message.replace("Auto-fixed: ", "")
                        )

            # Auto-fix JS anti-patterns (if any fixable patterns apply)
            if js:
                fixed_js, js_result = self.anti_pattern_validator.validate_and_fix(js)
                for fix_issue in js_result.issues:
                    if fix_issue.message.startswith("Auto-fixed:"):
                        report.auto_fixes_applied.append(
                            fix_issue.message.replace("Auto-fixed: ", "")
                        )

        # Update validation status if critical or error issues found
        if result.has_blockers or not result.valid:
            report.validation_passed = False

        return report, fixed_html, fixed_css, fixed_js

    def _auto_fix_html(self, html: str) -> tuple[str, list[str]]:
        """Apply auto-fixes to HTML."""
        fixes = []
        fixed = html

        # === BASIC CLEANUP ===

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

        # === ENTERPRISE ACCESSIBILITY FIXES ===

        # Fix 5: Add x-cloak to x-show elements (prevents FOUC)
        if re.search(r'x-show\s*=\s*["\'][^"\']+["\'](?![^>]*x-cloak)', fixed):
            fixed = re.sub(
                r'(x-show\s*=\s*["\'][^"\']+["\'])(?![^>]*x-cloak)([^>]*>)',
                r'\1 x-cloak\2',
                fixed
            )
            fixes.append("Added x-cloak to x-show elements")

        # Fix 6: Add type="button" to buttons without type
        if re.search(r'<button(?![^>]*type\s*=)[^>]*>', fixed):
            fixed = re.sub(
                r'<button(?![^>]*type\s*=)([^>]*)>',
                r'<button type="button"\1>',
                fixed
            )
            fixes.append("Added type='button' to buttons")

        # Fix 7: Add role="alert" to error messages (text-red without role)
        # Only fix simple error patterns, not complex ones
        if re.search(r'class\s*=\s*["\'][^"\']*text-red-[0-9]+[^"\']*["\'][^>]*>(?![^<]*role)', fixed):
            fixed = re.sub(
                r'(class\s*=\s*["\'][^"\']*text-red-[0-9]+[^"\']*["\'])([^>]*>)(?![^<]*role)',
                r'\1 role="alert"\2',
                fixed,
                count=5  # Limit to first 5 to avoid over-fixing
            )
            fixes.append("Added role='alert' to error messages")

        # Fix 8: Add aria-live="polite" to x-text dynamic content
        if re.search(r'x-text\s*=\s*["\'][^"\']+["\'](?![^>]*aria-live)', fixed):
            # Only fix status/feedback areas, not all x-text
            fixed = re.sub(
                r'(<(?:span|div|p)[^>]*)(x-text\s*=\s*["\'][^"\']*(?:status|message|count|total)[^"\']*["\'])(?![^>]*aria-live)([^>]*>)',
                r'\1\2 aria-live="polite"\3',
                fixed,
                flags=re.IGNORECASE
            )
            fixes.append("Added aria-live='polite' to dynamic status text")

        # Fix 9: Add motion-reduce to animated elements
        if re.search(r'animate-(?:spin|bounce|pulse|ping)', fixed):
            if 'motion-reduce:' not in fixed:
                fixed = re.sub(
                    r'(class\s*=\s*["\'][^"\']*)(animate-(?:spin|bounce|pulse|ping))([^"\']*["\'])',
                    r'\1\2 motion-reduce:animate-none\3',
                    fixed
                )
                fixes.append("Added motion-reduce variant to animations")

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

        # ═══════════════════════════════════════════════════════════════════
        # Enterprise CSS Fixes (Phase 7)
        # ═══════════════════════════════════════════════════════════════════

        # Fix 4: Convert arbitrary z-index to semantic scale
        # z-[9999] → z-50, z-[1000] → z-40, etc.
        arbitrary_z_pattern = r'z-\[(\d+)\]'
        arbitrary_z_matches = re.findall(arbitrary_z_pattern, fixed)
        if arbitrary_z_matches:
            def convert_z_index(match):
                value = int(match.group(1))
                if value >= 100:
                    return "z-50"  # Modal backdrop level
                elif value >= 50:
                    return "z-40"  # Fixed elements
                elif value >= 30:
                    return "z-30"  # Sticky headers
                elif value >= 20:
                    return "z-20"  # Dropdowns
                elif value >= 10:
                    return "z-10"  # Raised cards
                else:
                    return "z-0"   # Base level

            fixed = re.sub(arbitrary_z_pattern, convert_z_index, fixed)
            fixes.append(f"Converted {len(arbitrary_z_matches)} arbitrary z-index values to semantic scale")

        # Fix 5: Add prefers-reduced-motion wrapper for animations
        # Only if @keyframes exists but no prefers-reduced-motion check
        if '@keyframes' in fixed and '@media (prefers-reduced-motion' not in fixed:
            # Find all animation-related properties and wrap in media query
            reduced_motion_block = """
/* Reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
"""
            fixed = fixed.rstrip() + "\n" + reduced_motion_block
            fixes.append("Added prefers-reduced-motion media query for accessibility")

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

        # ═══════════════════════════════════════════════════════════════════
        # Enterprise JS Fixes (Phase 7)
        # ═══════════════════════════════════════════════════════════════════

        # Fix 4: Add debounce utility if scroll/resize handlers without debounce
        has_scroll_resize = re.search(r"addEventListener\s*\(\s*['\"](?:scroll|resize)['\"]", fixed)
        has_debounce = 'debounce' in fixed or 'throttle' in fixed
        if has_scroll_resize and not has_debounce:
            debounce_utility = """
  // Enterprise debounce utility for performance
  const debounce = (fn, delay = 100) => {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
  };
"""
            # Insert after 'use strict' or at the beginning
            if "'use strict'" in fixed:
                fixed = fixed.replace("'use strict';", "'use strict';" + debounce_utility, 1)
            else:
                fixed = debounce_utility + fixed
            fixes.append("Added debounce utility for scroll/resize handlers")

        # Fix 5: Add passive: true to scroll/wheel/touch listeners for performance
        passive_pattern = r"addEventListener\s*\(\s*['\"](?:scroll|wheel|touchstart|touchmove)['\"],\s*([^,]+)\s*\)"
        if re.search(passive_pattern, fixed) and 'passive' not in fixed:
            fixed = re.sub(
                passive_pattern,
                r"addEventListener('\1', \2, { passive: true })",
                fixed
            )
            # More precise pattern
            fixed = re.sub(
                r"addEventListener\s*\(\s*['\"](?P<event>scroll|wheel|touchstart|touchmove)['\"],\s*(?P<handler>[^,)]+)\s*\)",
                r"addEventListener('\g<event>', \g<handler>, { passive: true })",
                fixed
            )
            fixes.append("Added passive: true to scroll/touch listeners for performance")

        # Fix 6: Replace inline console.log with conditional logging
        console_log_count = len(re.findall(r'console\.log\s*\(', fixed))
        if console_log_count > 3:
            # Add debug flag pattern
            debug_utility = """
  // Debug logging (set window.DEBUG = true to enable)
  const log = (...args) => window.DEBUG && console.log('[DEBUG]', ...args);
"""
            # Replace console.log with log
            fixed = re.sub(r'\bconsole\.log\s*\(', 'log(', fixed)
            if "'use strict'" in fixed:
                fixed = fixed.replace("'use strict';", "'use strict';" + debug_utility, 1)
            else:
                fixed = debug_utility + fixed
            fixes.append(f"Replaced {console_log_count} console.log calls with conditional debug logging")

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

        Returns a summary dictionary including anti-pattern detection.
        """
        html_result = self.html_validator.validate(html) if html else None
        css_result = self.css_validator.validate(css) if css else None
        js_result = self.js_validator.validate(js) if js else None

        cross_result = None
        if html and js:
            cross_result = self.id_validator.validate(html, js)

        # Anti-pattern validation (runs on all content)
        combined_content = f"{html or ''}\n{css or ''}\n{js or ''}"
        antipattern_result = self.anti_pattern_validator.validate(combined_content)

        total_critical = antipattern_result.critical_count
        total_errors = antipattern_result.error_count
        total_warnings = antipattern_result.warning_count

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
            "valid": total_critical == 0 and total_errors == 0,
            "critical": total_critical,
            "errors": total_errors,
            "warnings": total_warnings,
            "html_valid": html_result.valid if html_result else True,
            "css_valid": css_result.valid if css_result else True,
            "js_valid": js_result.valid if js_result else True,
            "cross_layer_valid": cross_result.valid if cross_result else True,
            "antipattern_valid": antipattern_result.valid,
            "antipattern_count": len(antipattern_result.issues),
        }
