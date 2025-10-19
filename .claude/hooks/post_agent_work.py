#!/usr/bin/env python3
"""
Post-Agent-Work Hook - Automatic Quality Validation

This hook runs automatically after the agent completes significant work.
It performs quick validation on changed files to catch issues early.

Hook Event: PostToolUse (after substantial agent activity)
Trigger: After agent changes >= threshold (files/lines/time)
Scope: Files changed in current session
Mode: Warn-only (non-blocking)

Configuration: .claude/settings.local.json
  hooks.post_agent_work.enabled
  hooks.post_agent_work.threshold
  hooks.post_agent_work.validation

Related:
  - docs/development/quality-validation-coordination.md
  - tools/librarian_validate.py
  - .claude/commands/lint.md
"""

import json
import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class ValidationConfig:
    """Validation configuration from settings"""

    def __init__(self, settings: Dict):
        hook_config = settings.get('hooks', {}).get('post_agent_work', {})

        self.enabled = hook_config.get('enabled', True)

        threshold = hook_config.get('threshold', {})
        self.threshold_files = threshold.get('files_changed', 3)
        self.threshold_lines = threshold.get('lines_changed', 50)
        self.threshold_minutes = threshold.get('session_minutes', 10)

        validation = hook_config.get('validation', {})
        self.mode = validation.get('mode', 'warn_only')
        self.show_details = validation.get('show_details', 'on_failure')
        self.timeout = validation.get('timeout_seconds', 10)


def load_settings() -> Dict:
    """Load validation configuration"""
    try:
        # Try validation-config.json first (preferred)
        config_path = Path.cwd() / '.claude' / 'validation-config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)

        # Fallback to settings.local.json
        settings_path = Path.cwd() / '.claude' / 'settings.local.json'
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                # Look for validation_config key
                if 'validation_config' in settings:
                    return settings['validation_config']
                return settings
    except Exception as e:
        print(f"⚠️ Could not load settings: {e}", file=sys.stderr)

    return {}


def get_changed_files(cwd: str) -> Tuple[List[str], List[str]]:
    """
    Get files changed in recent agent activity.

    Returns:
        Tuple of (py_files, md_files)
    """
    try:
        # Get recently changed files (last 15 minutes)
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD@{15 minutes ago}', 'HEAD'],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            # Fallback: use unstaged changes
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=5
            )

        all_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]

        py_files = [f for f in all_files if f.endswith('.py')]
        md_files = [f for f in all_files if f.endswith('.md')]

        return py_files, md_files

    except Exception as e:
        print(f"⚠️ Error detecting changed files: {e}", file=sys.stderr)
        return [], []


def should_run_validation(tool_name: str, settings: Dict, cwd: str) -> Tuple[bool, str]:
    """
    Determine if validation should run based on activity threshold.

    Returns:
        Tuple of (should_run, reason)
    """
    config = ValidationConfig(settings)

    if not config.enabled:
        return False, "Hook disabled in settings"

    # Only run after certain high-impact tools
    high_impact_tools = ['Edit', 'Write', 'Task']
    if tool_name not in high_impact_tools:
        return False, f"Tool {tool_name} not high-impact"

    # Check file change threshold
    py_files, md_files = get_changed_files(cwd)
    total_files = len(py_files) + len(md_files)

    if total_files >= config.threshold_files:
        return True, f"{total_files} files changed (threshold: {config.threshold_files})"

    return False, f"Only {total_files} files changed (threshold: {config.threshold_files})"


def validate_python_files(py_files: List[str], cwd: str, timeout: int) -> Dict:
    """Run Black formatting check on Python files"""
    if not py_files:
        return {'status': 'skipped', 'reason': 'no Python files'}

    try:
        result = subprocess.run(
            ['black', '--check', '--quiet'] + py_files,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            return {
                'status': 'pass',
                'files': len(py_files),
                'message': f"✅ {len(py_files)} Python file(s) formatted correctly"
            }
        else:
            # Count files needing formatting
            needs_formatting = result.stdout.count('would reformat')
            return {
                'status': 'warning',
                'files': len(py_files),
                'issues': needs_formatting,
                'message': f"⚠️  {needs_formatting} Python file(s) need formatting",
                'details': f"Run: black {' '.join(py_files)}"
            }

    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'message': '⏱️ Black validation timeout',
            'files': len(py_files)
        }
    except FileNotFoundError:
        return {
            'status': 'skipped',
            'reason': 'Black not installed',
            'files': len(py_files)
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'⚠️ Black validation error: {e}',
            'files': len(py_files)
        }


def validate_markdown_files(md_files: List[str], cwd: str, timeout: int) -> Dict:
    """Run librarian metadata validation on markdown files"""
    if not md_files:
        return {'status': 'skipped', 'reason': 'no markdown files'}

    try:
        # Check if librarian tool exists
        validator_path = Path(cwd) / 'tools' / 'librarian_validate.py'
        if not validator_path.exists():
            return {
                'status': 'skipped',
                'reason': 'librarian_validate.py not found',
                'files': len(md_files)
            }

        # Run validation on specific files
        result = subprocess.run(
            ['python', str(validator_path), '--errors-only'] + md_files,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # Parse output for errors
        output = result.stdout + result.stderr

        if 'Error' in output or 'FAILED' in output:
            error_count = output.count('Error:')
            return {
                'status': 'warning',
                'files': len(md_files),
                'issues': error_count,
                'message': f"⚠️  {error_count} metadata issue(s) found",
                'details': output[:200] + '...' if len(output) > 200 else output
            }
        else:
            return {
                'status': 'pass',
                'files': len(md_files),
                'message': f"✅ {len(md_files)} markdown file(s) validated"
            }

    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'message': '⏱️ Librarian validation timeout',
            'files': len(md_files)
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'⚠️ Librarian validation error: {e}',
            'files': len(md_files)
        }


def format_validation_report(py_result: Dict, md_result: Dict, show_details: str) -> str:
    """Format validation results as user-friendly report"""
    lines = []
    lines.append("\n🔍 Quick validation complete:")
    lines.append("")

    # Python validation results
    if py_result['status'] == 'pass':
        lines.append(f"  {py_result['message']}")
    elif py_result['status'] == 'warning':
        lines.append(f"  {py_result['message']}")
        if show_details in ['always', 'on_failure']:
            lines.append(f"     {py_result.get('details', '')}")
    elif py_result['status'] == 'skipped':
        pass  # Don't show skipped
    elif py_result['status'] == 'error':
        lines.append(f"  {py_result['message']}")

    # Markdown validation results
    if md_result['status'] == 'pass':
        lines.append(f"  {md_result['message']}")
    elif md_result['status'] == 'warning':
        lines.append(f"  {md_result['message']}")
        if show_details in ['always', 'on_failure']:
            lines.append(f"     {md_result.get('details', '')}")
    elif md_result['status'] == 'skipped':
        pass  # Don't show skipped
    elif md_result['status'] == 'error':
        lines.append(f"  {md_result['message']}")

    # Summary
    has_warnings = (
        py_result['status'] == 'warning' or
        md_result['status'] == 'warning'
    )
    has_errors = (
        py_result['status'] == 'error' or
        md_result['status'] == 'error'
    )

    lines.append("")
    if has_errors:
        lines.append("⚠️  Validation encountered errors (non-blocking)")
    elif has_warnings:
        lines.append("💡 Consider fixing issues before committing")
    else:
        lines.append("✅ All checks passed!")

    return '\n'.join(lines)


def main():
    """Hook entry point"""
    try:
        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())

        tool_name = hook_input.get('tool_name', '')
        cwd = hook_input.get('cwd', os.getcwd())

        # Load settings
        settings = load_settings()

        # Check if validation should run
        should_run, reason = should_run_validation(tool_name, settings, cwd)

        if not should_run:
            # Skip validation - no output
            print(json.dumps({}))
            sys.exit(0)

        # Get configuration
        config = ValidationConfig(settings)

        # Get changed files
        py_files, md_files = get_changed_files(cwd)

        if not py_files and not md_files:
            # No files to validate
            print(json.dumps({}))
            sys.exit(0)

        # Run validation
        py_result = validate_python_files(py_files, cwd, config.timeout)
        md_result = validate_markdown_files(md_files, cwd, config.timeout)

        # Format report
        report = format_validation_report(py_result, md_result, config.show_details)

        # Return results
        response = {
            "hookSpecificOutput": {
                "message": report
            }
        }

        print(json.dumps(response))
        sys.exit(0)

    except Exception as e:
        # On error, allow operation but log
        error_response = {
            "hookSpecificOutput": {
                "message": f"⚠️ Post-agent-work validation hook error: {e}\n(Validation skipped)"
            }
        }
        print(json.dumps(error_response))
        sys.exit(0)


if __name__ == "__main__":
    main()
