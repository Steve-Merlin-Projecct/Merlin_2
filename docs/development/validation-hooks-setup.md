---
title: "Validation Hooks Setup Guide"
type: guide
component: development
status: active
tags: ["hooks", "validation", "setup", "code-quality", "documentation"]
created: 2025-10-17
updated: 2025-10-17
version: 1.0
---

# Validation Hooks Setup Guide

**Purpose:** Instructions for setting up and configuring automatic quality validation hooks that run during development.

**Related Documentation:**
- `docs/development/quality-validation-coordination.md` - Architecture and coordination
- `.claude/hooks/post_agent_work.py` - Quick validation hook
- `.claude/hooks/post_task.py` - Comprehensive validation hook
- `.claude/validation-config.json` - Hook configuration

---

## Overview

This project includes automatic quality validation hooks that run at natural checkpoints during development:

1. **Post-Agent-Work Hook** - Quick validation after agent changes >= threshold
2. **Post-Task Hook** - Comprehensive validation after `/task` completion

**Benefits:**
- ✅ Catch issues immediately (while context is fresh)
- ✅ Automated - no manual commands needed
- ✅ Non-blocking - warnings only, doesn't stop work
- ✅ Context-aware - validates appropriate file types

---

## Quick Start

### 1. Verify Hook Files Exist

```bash
ls -la .claude/hooks/
```

**Expected output:**
- `post_agent_work.py` - Quick validation hook
- `post_task.py` - Comprehensive validation hook
- `post_python_edit.py` - Existing syntax check hook

### 2. Verify Configuration Exists

```bash
cat .claude/validation-config.json
```

**Expected:** Configuration file with thresholds and validation settings

### 3. Enable Hooks (Optional)

Hooks are currently **disabled by default** during initial development. To enable:

**Edit `.claude/settings.local.json` and add:**

```json
{
  "permissions": {
    "allow": ["*"],
    "deny": [],
    "ask": [],
    "defaultMode": "bypassPermissions"
  },
  "statusLine": {
    "type": "command",
    "command": "/workspace/.claude/statusline.sh",
    "padding": 0
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python $(pwd)/.claude/hooks/post_agent_work.py",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

**Note:** The `post_task.py` hook requires PostSlashCommand event (not yet available in Claude Code hooks system). It's implemented for future use.

---

## Hook Behavior

### Post-Agent-Work Hook

**When it runs:**
- After `Edit` or `Write` tool operations
- Only if >= 3 files changed (configurable threshold)

**What it validates:**
- **Python files (.py)**: Black formatting check
- **Markdown files (.md)**: Librarian metadata validation

**Output example:**
```
🔍 Quick validation complete:

  ✅ 2 Python file(s) formatted correctly
  ✅ 2 markdown file(s) validated

✅ All checks passed!
```

**Failure example:**
```
🔍 Quick validation complete:

  ⚠️  2 Python file(s) need formatting
     Run: black modules/email_integration/validator.py tests/test_validator.py
  ⚠️  1 metadata issue(s) found
     docs/api/new-endpoint.md: Missing 'status' field

💡 Consider fixing issues before committing
```

### Post-Task Hook

**When it runs:**
- After `/task` command completes (future - when hook type available)

**What it validates:**
- **Comprehensive code quality**: Black, Flake8, Vulture
- **Comprehensive documentation quality**: Metadata, links, placement

**Output example:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Task Validation Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Files Changed: 6
   • Python: 3 file(s)
   • Markdown: 3 file(s)

🔧 Code Quality:
   ✅ Black: All files formatted correctly
   ✅ Flake8: No linting issues
   💡 Vulture: 2 potential dead code item(s)

📚 Documentation Quality:
   ✅ Metadata: 3/3 files valid
   ✅ Links: All valid

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All validation passed!
   Task output meets quality standards
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Configuration

### Validation Thresholds

Edit `.claude/validation-config.json` to customize:

```json
{
  "post_agent_work": {
    "enabled": true,
    "threshold": {
      "files_changed": 3,        // Minimum files to trigger
      "lines_changed": 50,        // OR minimum lines changed
      "session_minutes": 10       // OR minimum session duration
    },
    "validation": {
      "mode": "warn_only",        // Don't block, just warn
      "show_details": "on_failure", // Show details only if fails
      "timeout_seconds": 10       // Max time for validation
    }
  },
  "post_task": {
    "enabled": true,
    "validation": {
      "mode": "strict",           // Stricter validation
      "show_details": "always",   // Always show full report
      "timeout_seconds": 60       // More time for comprehensive check
    }
  }
}
```

### Adjusting Sensitivity

**To run validation more frequently:**
```json
"threshold": {
  "files_changed": 1,  // Trigger on any file change
  "lines_changed": 10  // OR trigger on 10+ lines
}
```

**To run validation less frequently:**
```json
"threshold": {
  "files_changed": 5,  // Only after 5+ files
  "lines_changed": 100 // OR 100+ lines
}
```

**To disable a hook:**
```json
"post_agent_work": {
  "enabled": false
}
```

---

## Troubleshooting

### Hook Not Running

**Problem:** Validation hook doesn't run after file edits

**Solutions:**

1. **Check if hooks enabled:**
   ```json
   // In .claude/settings.local.json
   "disableAllHooks": false  // Should be false or omitted
   ```

2. **Check threshold:**
   - Hook only runs if >= threshold files changed
   - Check `.claude/validation-config.json`
   - Try changing 1 file to test

3. **Check hook registration:**
   ```bash
   grep -A 10 "hooks" .claude/settings.local.json
   ```

4. **Check hook permissions:**
   ```bash
   ls -l .claude/hooks/post_agent_work.py
   # Should be executable (-rwxr-xr-x)
   ```

### Hook Errors

**Problem:** Hook runs but shows errors

**Check dependencies:**
```bash
# Black installed?
black --version

# Flake8 installed?
flake8 --version

# Librarian tools exist?
ls tools/librarian_validate.py
```

**Check working directory:**
Hook scripts use `Path.cwd()` to find tools. Ensure:
- Running from project root
- `.claude/` directory exists
- `tools/` directory exists

### Slow Validation

**Problem:** Validation takes too long

**Solutions:**

1. **Increase timeout:**
   ```json
   "validation": {
     "timeout_seconds": 30  // Increase from 10
   }
   ```

2. **Reduce scope:**
   - Hook validates recently changed files only
   - Not full project scan
   - Should complete in < 10 seconds typically

3. **Disable slow tools:**
   - Modify hook scripts to skip Vulture (slowest)
   - Comment out link validation (can be slow)

---

## Development Workflow

### With Hooks Enabled

```
Agent works → Changes 3+ files → Hook runs automatically:
  ↓
🔍 Quick validation
  ↓
✅ PASS → Continue working
❌ FAIL → Fix issues (or ignore and commit with issues)
```

### Recommended Workflow

1. **During development:** Hooks provide feedback
2. **Before commit:** Manual check with `/lint` or validation commands
3. **Before push:** Full validation suite
4. **CI/CD:** Automated validation on all files

### Manual Validation (Alternative)

If hooks are disabled or you want manual control:

```bash
# Code quality
black --check .
flake8
vulture --min-confidence 80

# Documentation quality
python tools/librarian_validate.py --all
python tools/validate_links.py --all
```

Or use slash commands:
```
/format  - Auto-format with Black
/lint    - Run Black, Flake8, Vulture
```

---

## Hook Implementation Details

### Post-Agent-Work Hook

**File:** `.claude/hooks/post_agent_work.py`

**How it works:**
1. Receives hook event from Claude Code
2. Checks if tool was Edit/Write
3. Gets list of recently changed files (git diff)
4. Counts changed files vs. threshold
5. If >= threshold:
   - Runs Black on `.py` files
   - Runs librarian_validate on `.md` files
6. Formats and returns results

**Key features:**
- Fast (< 10 second timeout)
- Non-blocking (warn-only mode)
- Only validates changed files
- Graceful error handling (fails open)

### Post-Task Hook

**File:** `.claude/hooks/post_task.py`

**How it works:**
1. Receives hook event after `/task` completes
2. Gets all files changed during task (git diff since task start)
3. Runs comprehensive validation:
   - Black, Flake8, Vulture on `.py` files
   - librarian_validate, link validator on `.md` files
4. Formats detailed report with all results
5. Returns comprehensive summary

**Key features:**
- Comprehensive (60 second timeout)
- Detailed reporting (always show full results)
- Validates all task files
- Still non-blocking (informational only)

---

## Future Enhancements

### When PostSlashCommand Hook Available

Currently Claude Code hooks support:
- PreToolUse, PostToolUse, Notification, UserPromptSubmit
- SessionStart, SessionEnd, Stop, SubagentStop, PreCompact

**Missing:** PostSlashCommand (needed for `/task` hook)

**When available:**
1. Add to `.claude/settings.local.json`:
   ```json
   "PostSlashCommand": [
     {
       "matcher": "task",
       "hooks": [
         {
           "type": "command",
           "command": "python $(pwd)/.claude/hooks/post_task.py",
           "timeout": 90
         }
       ]
     }
   ]
   ```

2. Hook will automatically run after `/task` commands

### Potential Improvements

1. **Pre-commit integration:**
   - Add to `.git/hooks/pre-commit`
   - Block commits with validation failures

2. **Git checkpoint integration:**
   - Validation before creating git checkpoints
   - Only allow clean checkpoints

3. **Status bar integration:**
   - Show validation status in Claude Code status bar
   - Real-time feedback

4. **Configurable file types:**
   - Support other file types (.json, .yml, .sh)
   - Custom validation rules per type

---

## Testing

### Test Post-Agent-Work Hook

1. **Enable hook** (see Configuration section)

2. **Make changes to trigger:**
   ```bash
   # Edit 3+ markdown files
   echo "test" >> docs/test1.md
   echo "test" >> docs/test2.md
   echo "test" >> docs/test3.md
   ```

3. **Use Claude Code to edit a file:**
   - Ask agent to edit any file
   - Hook should run after edit
   - Look for validation output

4. **Expected output:**
   ```
   🔍 Quick validation complete:
   ...
   ```

### Test Post-Task Hook (Manual)

Since PostSlashCommand not available, test manually:

```bash
# Simulate hook input
echo '{"command": "task", "cwd": "$(pwd)"}' | python .claude/hooks/post_task.py
```

**Expected:** Comprehensive validation report

---

## Related Documentation

- **Architecture:** `docs/development/quality-validation-coordination.md`
- **Code Quality Tools:** `docs/development/standards/AUTOMATED_TOOLING_GUIDE.md`
- **Librarian Usage:** `docs/librarian-usage-guide.md`
- **Hooks Source:**
  - `.claude/hooks/post_agent_work.py`
  - `.claude/hooks/post_task.py`
- **Configuration:** `.claude/validation-config.json`

---

## Support

**Questions about hooks?**
- Check Claude Code hooks documentation
- Review `.claude/hooks/` implementations
- Adjust `.claude/validation-config.json` settings

**Issues with validation tools?**
- Black: Check `.black.toml` configuration
- Flake8: Check `.flake8` configuration
- Librarian: See `docs/librarian-usage-guide.md`

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Version:** 1.0
