---
title: Complete Worktree Management Guide
type: guide
created: 2025-10-21
modified: 2025-10-21
status: current
related: CLAUDE.md, .claude/scripts/tree.sh, tasks/worktree-error-prevention/
---

# Complete Worktree Management Guide

**Version:** 4.3.3
**Last Updated:** 2025-10-21
**Status:** Production Ready with Error Prevention

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Command Reference](#command-reference)
5. [Workflows](#workflows)
6. [Error Prevention System](#error-prevention-system)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)
9. [Advanced Usage](#advanced-usage)

---

## Overview

The worktree management system enables parallel development across multiple isolated feature branches without switching contexts or dealing with stashing.

**Key Benefits:**
- Work on multiple features simultaneously
- No context switching or stashing required
- Isolated development environments
- Automatic scope enforcement
- Built-in error prevention and recovery

**System Files:**
- Script: `.claude/scripts/tree.sh`
- Command: `/tree` (slash command)
- Documentation: `docs/worktrees/`

---

## Quick Start

### Basic Workflow

```bash
# 1. Stage features for development
/tree stage Add user preferences backend
/tree stage Dashboard analytics view
/tree stage Email notification system

# 2. Review staged features
/tree list

# 3. Check for conflicts (optional)
/tree conflict

# 4. Build all worktrees
/tree build

# 5. Work in each worktree
# (Separate terminals/editors for each)

# 6. Complete work
cd .trees/user-preferences-backend
/tree close

# 7. Merge all completed worktrees
/tree closedone
```

### Quick Commands

```bash
/tree stage [description]    # Stage a feature
/tree list                   # Show staged features
/tree build                  # Create all worktrees
/tree build --verbose        # Create with debug output
/tree close                  # Mark feature complete
/tree close incomplete       # Save progress for later
/tree closedone              # Merge all completed
/tree status                 # Check environment status
/tree help                   # Show full help
```

---

## Core Concepts

### Worktrees

A **worktree** is an isolated working directory with its own branch, allowing you to work on multiple features simultaneously.

**Structure:**
```
/workspace/.trees/
├── feature-one/           # Worktree directory
│   ├── .git              # Git metadata (link)
│   ├── PURPOSE.md        # Feature documentation
│   ├── .worktree-scope.json  # Scope configuration
│   └── ...               # Full codebase
└── feature-two/
    └── ...
```

### Development Branches

All worktrees are created from a common development branch:

```
main
└── develop/v4.3.3-worktrees-20251021-143025
    ├── task/01-feature-one
    ├── task/02-feature-two
    └── task/03-feature-three
```

### Scope Enforcement

Each worktree has automatic scope detection to prevent accidental changes outside the feature's scope.

**Example `.worktree-scope.json`:**
```json
{
  "worktree_name": "user-preferences-backend",
  "scope": {
    "include": [
      "modules/user_preferences/**",
      "tests/test_user_preferences.py",
      "docs/user-preferences.md"
    ],
    "exclude": []
  },
  "enforcement": "soft"
}
```

---

## Command Reference

### `/tree stage [description]`

Stage a feature for worktree creation.

**Usage:**
```bash
/tree stage Add user authentication system
/tree stage "Dashboard: Implement real-time analytics"
```

**What it does:**
- Creates entry in `.trees/.staged-features.txt`
- Generates worktree name from description
- Prepares for batch build

### `/tree list`

Show all staged features.

**Example output:**
```
Staged Features:
  1. user-authentication-system
  2. dashboard-implement-real-time-analytics
  3. email-notification-system

Use '/tree build' to create worktrees
```

### `/tree build [options]`

Create worktrees from all staged features.

**Options:**
- `--verbose` / `-v`: Show detailed git command output
- `--confirm`: Prompt before each worktree creation

**What it does:**
1. Runs pre-flight checks (error prevention)
2. Creates development branch
3. Creates worktree for each staged feature
4. Generates PURPOSE.md and scope configuration
5. Copies slash commands to each worktree
6. Installs scope enforcement hooks

**Example:**
```bash
/tree build                    # Standard build
/tree build --verbose          # Debug mode
TREE_VERBOSE=true /tree build  # Verbose via env var
```

### `/tree close [incomplete]`

Complete work in current worktree.

**Usage:**
```bash
/tree close              # Mark feature complete
/tree close incomplete   # Save progress for later
```

**What it does:**
- Generates feature synopsis
- Documents changes and decisions
- Marks worktree as ready for merge (if complete)
- Moves to `.trees/.completed/` or `.trees/.incomplete/`

### `/tree closedone [options]`

Batch merge and cleanup completed worktrees.

**Options:**
- `--yes` / `-y`: Skip confirmation prompts
- `--force`: Merge all worktrees even if not closed
- `--full-cycle`: Complete development cycle (merge → main → version bump)
- `--bump [type]`: Version bump type (patch|minor|major)

**What it does:**
1. Finds all completed worktrees
2. Merges each to development branch
3. Optionally merges develop → main
4. Optionally bumps version
5. Cleans up worktree directories
6. Removes branches

**Example:**
```bash
/tree closedone                    # Standard merge
/tree closedone --yes              # Skip confirmations
/tree closedone --full-cycle       # Full automation
/tree closedone --bump minor       # With version bump
```

### `/tree status`

Show worktree environment status.

**Example output:**
```
Worktree Environment Status

Active Worktrees: 3
├─ user-authentication-system (task/01-user-authentication-system)
├─ dashboard-real-time-analytics (task/02-dashboard-real-time-analytics)
└─ email-notification-system (task/03-email-notification-system)

Completed: 1
Incomplete: 0
```

### `/tree conflict`

Analyze potential conflicts between staged features.

**What it does:**
- Scans staged features for overlapping scopes
- Identifies potential merge conflicts
- Suggests optimal feature combinations

### `/tree refresh`

Check slash command availability and provide session guidance.

**Use when:**
- Slash commands not working after worktree switch
- Need to verify command availability
- Want session reload instructions

---

## Workflows

### Workflow 1: Parallel Feature Development

**Scenario:** Develop 3 unrelated features simultaneously

```bash
# Stage all features
/tree stage User profile page
/tree stage Export analytics data
/tree stage Email templates

# Verify no conflicts
/tree conflict

# Create all worktrees
/tree build

# Work on each feature in parallel
# (Use separate terminal windows/tabs)

# Terminal 1
cd .trees/user-profile-page
# ... implement feature ...
/tree close

# Terminal 2
cd .trees/export-analytics-data
# ... implement feature ...
/tree close

# Terminal 3
cd .trees/email-templates
# ... implement feature ...
/tree close

# Merge all completed features
cd /workspace
/tree closedone --full-cycle
```

### Workflow 2: Incremental Development

**Scenario:** Work on one feature at a time, stage next while working

```bash
# Start first feature
/tree stage Implement user preferences
/tree build
cd .trees/implement-user-preferences

# ... work on feature ...

# While working, stage next feature
/tree stage Dashboard improvements

# Complete current feature
/tree close

# Build next feature
cd /workspace
/tree build
cd .trees/dashboard-improvements

# Repeat...
```

### Workflow 3: Experimental Features

**Scenario:** Try multiple approaches to a problem

```bash
# Stage different approaches
/tree stage "Caching: Redis implementation"
/tree stage "Caching: Memory-based implementation"
/tree stage "Caching: Database-based implementation"

# Build all approaches
/tree build

# Implement each approach
# ... work in parallel ...

# Mark successful approach as complete
cd .trees/caching-redis-implementation
/tree close

# Mark others as incomplete (for reference)
cd .trees/caching-memory-based-implementation
/tree close incomplete

cd .trees/caching-database-based-implementation
/tree close incomplete

# Merge only the complete one
/tree closedone
```

---

## Error Prevention System

**NEW in v4.3.3:** Comprehensive error prevention for `/tree build`

### Pre-Flight Checks

Automatically runs before every build:

1. **Stale Lock Detection**
   - Checks for `index.lock` files
   - Auto-removes locks >60s old with 0 bytes
   - Blocks if active git operation detected

2. **Git Worktree Prune**
   - Syncs git's internal state with filesystem
   - Removes stale worktree references
   - Cleans up orphaned registrations

3. **Orphaned Directory Cleanup**
   - Scans `.trees/` for unregistered directories
   - Validates safety before removal
   - Protects uncommitted changes

### Features

- **Orphaned directory removal:** Auto-detects and removes
- **Orphaned branch cleanup:** Auto-removes branches without worktrees
- **Atomic rollback:** On failure, removes all partial creations
- **Enhanced errors:** Shows actual git error messages
- **Idempotent operations:** Safe to retry failed builds
- **Uncommitted protection:** Won't delete directories with uncommitted work

### Usage

**Standard build (includes all prevention):**
```bash
/tree build
```

**Verbose mode (for debugging):**
```bash
/tree build --verbose
# OR
TREE_VERBOSE=true /tree build
```

**Recovery from failure:**
```bash
/tree build  # Fails with error
# Just retry - auto-cleanup will fix it
/tree build  # Succeeds
```

### Example Output

```
═══════════════════════════════════════════════════════════
PRE-FLIGHT CHECKS
═══════════════════════════════════════════════════════════

Checking for stale locks...
✓ No stale locks detected

Pruning stale worktree references...
✓ No stale references to prune

Checking for orphaned worktree artifacts...
  Found orphaned directory: old-feature
  Removing orphaned directory...
  Orphaned directory removed
✓ Cleaned up 1 orphaned director(y/ies)

═══════════════════════════════════════════════════════════
```

---

## Troubleshooting

### Build Fails: "Path already exists"

**Solution:** Run `/tree build` again (auto-cleanup)

```bash
/tree build
# ❌ Error: Path already exists

/tree build
# ✅ Auto-cleanup removes orphaned path, build succeeds
```

### Build Fails: "Branch already exists"

**Solution:** Run `/tree build` again (auto-cleanup)

```bash
/tree build
# ❌ Error: Branch already exists

/tree build
# ✅ Auto-cleanup removes orphaned branch, build succeeds
```

### Build Fails: Stale Lock

**Solution:** Run `/tree build` again (auto-removes if stale)

```bash
/tree build
# ❌ Error: Git locked

/tree build
# ✅ Auto-removes stale lock (>60s), build succeeds
```

### Slash Commands Not Working

**Solution:** Use refresh command

```bash
/tree refresh
# Shows session guidance and workaround commands
```

**Alternative:** Run script directly
```bash
bash /workspace/.claude/scripts/tree.sh build
```

### See Detailed Errors

**Solution:** Enable verbose mode

```bash
/tree build --verbose
# Shows all git commands and output
```

---

## Best Practices

### 1. Feature Scope

✅ **Good:** "Add user authentication system"
❌ **Bad:** "Fix stuff and update things"

**Why:** Clear scope enables better scope detection and documentation.

### 2. Feature Size

✅ **Good:** 1-3 days of work per feature
❌ **Bad:** Week-long mega-features

**Why:** Smaller features are easier to review, test, and merge.

### 3. Staging Strategy

✅ **Good:** Stage related features together
❌ **Bad:** Stage conflicting features

**Why:** Reduces merge conflicts and complexity.

### 4. Commit Frequently

✅ **Good:** Commit after each logical unit of work
❌ **Bad:** Single massive commit at the end

**Why:** Easier to review, rollback, and understand history.

### 5. Use `/tree close`

✅ **Good:** Document feature with `/tree close`
❌ **Bad:** Manually merge without documentation

**Why:** Generates synopsis, tracks decisions, maintains project history.

### 6. Check Conflicts

✅ **Good:** Run `/tree conflict` before building
❌ **Bad:** Build without checking

**Why:** Identifies potential issues early.

---

## Advanced Usage

### Custom Scope Configuration

Edit `.worktree-scope.json` in worktree:

```json
{
  "worktree_name": "my-feature",
  "scope": {
    "include": [
      "modules/my_feature/**",
      "tests/test_my_feature.py"
    ],
    "exclude": [
      "modules/my_feature/generated/**"
    ]
  },
  "enforcement": "hard"  // "soft" or "hard"
}
```

### Environment Variables

```bash
# Enable verbose mode globally
export TREE_VERBOSE=true

# Custom trees directory
export TREES_DIR=/custom/path/.trees
```

### Batch Operations

```bash
# Stage multiple features from file
while read -r feature; do
  /tree stage "$feature"
done < features.txt

# Build with confirmation
/tree build --confirm

# Close all worktrees
for wt in .trees/*/; do
  cd "$wt" && /tree close && cd -
done
```

---

## Related Documentation

- **Error Prevention:** `tasks/worktree-error-prevention/`
- **Tree Build Error (Resolved):** `docs/troubleshooting/TREE_BUILD_ERROR.md`
- **Worktree Manager README:** `docs/worktrees/README_WORKTREE_MANAGER.md`
- **System Instructions:** `/CLAUDE.md`
- **Documentation Index:** `docs/DOCUMENTATION_INDEX.md`

---

## Support

**Issues?**
1. Check this guide's troubleshooting section
2. Run `/tree build --verbose` for detailed errors
3. Check `/tree status` for environment state
4. Review error documentation in `docs/troubleshooting/`

**Questions?**
1. Read `/tree help` for command reference
2. Check `docs/DOCUMENTATION_INDEX.md` for all documentation
3. Review CLAUDE.md for system policies

---

**Last Updated:** 2025-10-21
**Version:** 4.3.3 (with error prevention)
**Status:** Production Ready
