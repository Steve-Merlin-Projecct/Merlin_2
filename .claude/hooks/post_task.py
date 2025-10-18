#!/usr/bin/env python3
"""
Post-Task Hook - Comprehensive Quality Validation

This hook runs automatically after /task command completes.
It performs comprehensive validation on all files changed during the task.

Hook Event: PostSlashCommand (after /task completion)
Trigger: After any /task command completes
Scope: All files changed during task execution
Mode: Comprehensive validation (more thorough than post-agent-work)

Configuration: .claude/settings.local.json
  hooks.post_task.enabled
  hooks.post_task.validation

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


class ValidationConfig:
    """Validation configuration from settings"""

    def __init__(self, settings: Dict):
        hook_config = settings.get('hooks', {}).get('post_task', {})

        self.enabled = hook_config.get('enabled', True)

        validation = hook_config.get('validation', {})
        self.mode = validation.get('mode', 'strict')
        self.show_details = validation.get('show_details', 'always')
        self.timeout = validation.get('timeout_seconds', 60)


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


def get_task_changed_files(cwd: str) -> Tuple[List[str], List[str]]:
    """
    Get all files changed during task execution.

    Looks for files changed since task started (approximation: last 30 minutes).

    Returns:
        Tuple of (py_files, md_files)
    """
    try:
        # Try to get files changed in current session
        # This captures more than just immediate changes
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD@{30 minutes ago}', 'HEAD'],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            # Fallback: use all uncommitted changes
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
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
        print(f"⚠️ Error detecting task files: {e}", file=sys.stderr)
        return [], []


def validate_python_comprehensive(py_files: List[str], cwd: str, timeout: int) -> Dict:
    """
    Run comprehensive Python validation: Black, Flake8, Vulture.

    Returns dict with status, results for each tool.
    """
    if not py_files:
        return {'status': 'skipped', 'reason': 'no Python files'}

    results = {
        'black': None,
        'flake8': None,
        'vulture': None
    }

    # Black formatting check
    try:
        result = subprocess.run(
            ['black', '--check', '--diff'] + py_files,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout // 3
        )

        if result.returncode == 0:
            results['black'] = {
                'status': 'pass',
                'message': '✅ Black: All files formatted correctly'
            }
        else:
            needs_formatting = len([f for f in py_files if f in result.stdout])
            results['black'] = {
                'status': 'warning',
                'message': f'⚠️  Black: {needs_formatting} file(s) need formatting',
                'fix': f'black {" ".join(py_files)}'
            }
    except subprocess.TimeoutExpired:
        results['black'] = {'status': 'error', 'message': '⏱️ Black: Timeout'}
    except FileNotFoundError:
        results['black'] = {'status': 'skipped', 'message': 'Black not installed'}
    except Exception as e:
        results['black'] = {'status': 'error', 'message': f'Black error: {e}'}

    # Flake8 linting
    try:
        result = subprocess.run(
            ['flake8'] + py_files,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout // 3
        )

        if result.returncode == 0:
            results['flake8'] = {
                'status': 'pass',
                'message': '✅ Flake8: No linting issues'
            }
        else:
            issue_count = len(result.stdout.strip().split('\n'))
            results['flake8'] = {
                'status': 'warning',
                'message': f'⚠️  Flake8: {issue_count} issue(s) found',
                'details': result.stdout[:300] + '...' if len(result.stdout) > 300 else result.stdout
            }
    except subprocess.TimeoutExpired:
        results['flake8'] = {'status': 'error', 'message': '⏱️ Flake8: Timeout'}
    except FileNotFoundError:
        results['flake8'] = {'status': 'skipped', 'message': 'Flake8 not installed'}
    except Exception as e:
        results['flake8'] = {'status': 'error', 'message': f'Flake8 error: {e}'}

    # Vulture dead code detection
    try:
        result = subprocess.run(
            ['vulture', '--min-confidence', '80'] + py_files,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout // 3
        )

        if not result.stdout.strip():
            results['vulture'] = {
                'status': 'pass',
                'message': '✅ Vulture: No dead code detected'
            }
        else:
            issue_count = len(result.stdout.strip().split('\n'))
            results['vulture'] = {
                'status': 'info',
                'message': f'💡 Vulture: {issue_count} potential dead code item(s)',
                'details': result.stdout[:300] + '...' if len(result.stdout) > 300 else result.stdout
            }
    except subprocess.TimeoutExpired:
        results['vulture'] = {'status': 'error', 'message': '⏱️ Vulture: Timeout'}
    except FileNotFoundError:
        results['vulture'] = {'status': 'skipped', 'message': 'Vulture not installed'}
    except Exception as e:
        results['vulture'] = {'status': 'error', 'message': f'Vulture error: {e}'}

    # Determine overall status
    has_warnings = any(r and r.get('status') == 'warning' for r in results.values())
    has_errors = any(r and r.get('status') == 'error' for r in results.values())

    return {
        'status': 'warning' if has_warnings else ('error' if has_errors else 'pass'),
        'results': results,
        'files': len(py_files)
    }


def validate_markdown_comprehensive(md_files: List[str], cwd: str, timeout: int) -> Dict:
    """
    Run comprehensive markdown validation: metadata, links, placement.

    Returns dict with status, results for each check.
    """
    if not md_files:
        return {'status': 'skipped', 'reason': 'no markdown files'}

    results = {
        'metadata': None,
        'links': None
    }

    validator_path = Path(cwd) / 'tools' / 'librarian_validate.py'
    link_validator_path = Path(cwd) / 'tools' / 'validate_links.py'

    # Metadata validation
    if validator_path.exists():
        try:
            result = subprocess.run(
                ['python', str(validator_path)] + md_files,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout // 2
            )

            output = result.stdout + result.stderr

            if 'Error' in output or 'FAILED' in output:
                error_count = output.count('Error:')
                results['metadata'] = {
                    'status': 'warning',
                    'message': f'⚠️  Metadata: {error_count} issue(s) found',
                    'details': output[:300] + '...' if len(output) > 300 else output
                }
            else:
                results['metadata'] = {
                    'status': 'pass',
                    'message': f'✅ Metadata: {len(md_files)} file(s) validated'
                }
        except subprocess.TimeoutExpired:
            results['metadata'] = {'status': 'error', 'message': '⏱️ Metadata: Timeout'}
        except Exception as e:
            results['metadata'] = {'status': 'error', 'message': f'Metadata error: {e}'}
    else:
        results['metadata'] = {'status': 'skipped', 'message': 'librarian_validate.py not found'}

    # Link validation
    if link_validator_path.exists():
        try:
            result = subprocess.run(
                ['python', str(link_validator_path)] + md_files,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout // 2
            )

            output = result.stdout + result.stderr

            if 'broken' in output.lower() or 'error' in output.lower():
                results['links'] = {
                    'status': 'warning',
                    'message': '⚠️  Links: Broken links detected',
                    'details': output[:200] + '...' if len(output) > 200 else output
                }
            else:
                results['links'] = {
                    'status': 'pass',
                    'message': '✅ Links: All valid'
                }
        except subprocess.TimeoutExpired:
            results['links'] = {'status': 'error', 'message': '⏱️ Links: Timeout'}
        except Exception as e:
            results['links'] = {'status': 'error', 'message': f'Links error: {e}'}
    else:
        results['links'] = {'status': 'skipped', 'message': 'validate_links.py not found'}

    # Determine overall status
    has_warnings = any(r and r.get('status') == 'warning' for r in results.values())
    has_errors = any(r and r.get('status') == 'error' for r in results.values())

    return {
        'status': 'warning' if has_warnings else ('error' if has_errors else 'pass'),
        'results': results,
        'files': len(md_files)
    }


def format_comprehensive_report(
    py_result: Dict,
    md_result: Dict,
    py_files: List[str],
    md_files: List[str],
    show_details: str
) -> str:
    """Format comprehensive validation report"""
    lines = []
    lines.append("\n" + "━" * 50)
    lines.append("📊 Task Validation Complete")
    lines.append("━" * 50)

    # Files summary
    lines.append(f"\n📝 Files Changed: {len(py_files) + len(md_files)}")
    if py_files:
        lines.append(f"   • Python: {len(py_files)} file(s)")
    if md_files:
        lines.append(f"   • Markdown: {len(md_files)} file(s)")

    # Python validation results
    if py_result['status'] != 'skipped':
        lines.append("\n🔧 Code Quality:")
        for tool_name, tool_result in py_result.get('results', {}).items():
            if tool_result:
                lines.append(f"   {tool_result.get('message', '')}")
                if show_details == 'always' and 'details' in tool_result:
                    for detail_line in tool_result['details'].split('\n')[:5]:
                        lines.append(f"      {detail_line}")
                if 'fix' in tool_result:
                    lines.append(f"      Fix: {tool_result['fix']}")

    # Markdown validation results
    if md_result['status'] != 'skipped':
        lines.append("\n📚 Documentation Quality:")
        for check_name, check_result in md_result.get('results', {}).items():
            if check_result:
                lines.append(f"   {check_result.get('message', '')}")
                if show_details == 'always' and 'details' in check_result:
                    for detail_line in check_result['details'].split('\n')[:5]:
                        lines.append(f"      {detail_line}")

    # Overall summary
    lines.append("\n" + "━" * 50)

    has_warnings = (
        py_result.get('status') == 'warning' or
        md_result.get('status') == 'warning'
    )
    has_errors = (
        py_result.get('status') == 'error' or
        md_result.get('status') == 'error'
    )

    if has_errors:
        lines.append("❌ Validation completed with errors")
        lines.append("   Some validation checks failed to run")
    elif has_warnings:
        lines.append("⚠️  Issues found - please review")
        lines.append("   Fix issues before committing (recommended)")
    else:
        lines.append("✅ All validation passed!")
        lines.append("   Task output meets quality standards")

    lines.append("━" * 50 + "\n")

    return '\n'.join(lines)


def main():
    """Hook entry point"""
    try:
        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())

        command = hook_input.get('command', '')
        cwd = hook_input.get('cwd', os.getcwd())

        # Only run after /task commands
        if not command.startswith('task'):
            print(json.dumps({}))
            sys.exit(0)

        # Load settings
        settings = load_settings()
        config = ValidationConfig(settings)

        if not config.enabled:
            print(json.dumps({}))
            sys.exit(0)

        # Get changed files
        py_files, md_files = get_task_changed_files(cwd)

        if not py_files and not md_files:
            # No files changed during task
            response = {
                "hookSpecificOutput": {
                    "message": "\n✅ Task complete (no file changes detected)\n"
                }
            }
            print(json.dumps(response))
            sys.exit(0)

        # Run comprehensive validation
        py_result = validate_python_comprehensive(py_files, cwd, config.timeout)
        md_result = validate_markdown_comprehensive(md_files, cwd, config.timeout)

        # Format report
        report = format_comprehensive_report(
            py_result,
            md_result,
            py_files,
            md_files,
            config.show_details
        )

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
                "message": f"⚠️ Post-task validation hook error: {e}\n(Validation skipped)\n"
            }
        }
        print(json.dumps(error_response))
        sys.exit(0)


if __name__ == "__main__":
    main()
