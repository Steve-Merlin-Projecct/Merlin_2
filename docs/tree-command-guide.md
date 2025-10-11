# /tree Command Guide
**Git Worktree Management System with Claude Auto-Launch**

Version: 4.3.1
Last Updated: 2025-10-11
Script Location: `.claude/scripts/tree.sh`

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Command Reference](#command-reference)
4. [Workflow Patterns](#workflow-patterns)
5. [Technical Implementation](#technical-implementation)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## Overview

The `/tree` command system is a comprehensive git worktree automation tool that enables parallel development across multiple feature branches with automatic Claude Code integration.

### Key Features

✅ **Feature Staging** - Queue multiple features for parallel development
✅ **Conflict Detection** - Analyze file conflicts before building worktrees
✅ **Zero-Confirmation Build** - Create worktrees without manual prompts
✅ **Auto-Terminal Creation** - VS Code integrated terminals auto-spawn
✅ **Claude Auto-Launch** - Claude instances start with task context pre-loaded
✅ **Context-Aware Agents** - Claude receives task description and asks clarifying questions
✅ **Slash Command Sync** - Commands work natively in worktrees
✅ **Terminal Restoration** - Reconnect terminals after VS Code restart
✅ **Batch Completion** - Merge and cleanup completed worktrees in bulk

### Architecture

```
/workspace/
├── .trees/                        # Worktree container directory
│   ├── .staged-features.txt       # Staged features queue
│   ├── .completed/                # Completed worktrees awaiting merge
│   ├── .archived/                 # Historical archive
│   ├── .conflict-backup/          # Conflict resolution backups
│   ├── feature-name-1/            # Individual worktree
│   │   ├── .claude-init.sh        # Claude auto-launch script
│   │   ├── .claude-task-context.md # Task description for Claude
│   │   └── .claude/commands/      # Copied slash commands
│   └── feature-name-2/
├── .vscode/
│   └── worktree-tasks.json        # Generated terminal tasks
└── .claude/scripts/tree.sh        # Main script
```

---

## Quick Start

### Basic Workflow (5 steps)

```bash
# 1. Stage features for development
/tree stage Implement API rate limiting
/tree stage Add dashboard analytics view
/tree stage Create user notification system

# 2. Review staged features
/tree list

# 3. Check for conflicts (optional)
/tree conflict

# 4. Build all worktrees (auto-launches Claude in each)
/tree build

# 5. Work in worktrees, then complete
# (In each worktree terminal after work is done)
/tree close

# 6. Merge all completed worktrees back to main
/tree closedone
```

### What Happens During `/tree build`

1. ✅ Creates git worktrees for each staged feature
2. ✅ Generates unique branch names (`feature/<name>`)
3. ✅ Copies `.claude/commands/` and `.claude/scripts/` to worktrees
4. ✅ Creates `.claude-task-context.md` with full task description
5. ✅ Generates `.claude-init.sh` auto-launch script
6. ✅ Creates VS Code `worktree-tasks.json` file
7. ✅ Generates `.vscode/create-worktree-terminals.sh` automation script
8. ⚡ **ONE COMMAND** to launch all terminals: `bash .vscode/create-worktree-terminals.sh`
9. ✅ Claude launches in each terminal with task context pre-loaded
10. ✅ Claude asks 1-3 clarifying questions before starting work

**Result:** ONE command creates 5-10 terminals in VS Code panel, each running Claude with context

**Note:** VS Code devcontainers require manual execution of the terminal creation script due to security restrictions. This is a one-time command that launches all terminals automatically.

---

## Command Reference

### 1. `/tree stage [description]`

**Purpose:** Queue a feature for worktree creation

**Usage:**
```bash
/tree stage Implement user authentication with JWT
/tree stage Add real-time WebSocket notifications
/tree stage Refactor database schema for performance
```

**Behavior:**
- Adds feature to `.trees/.staged-features.txt`
- Uses `|||` delimiter to preserve full description with special characters
- No limit on number of staged features
- Does not create worktree immediately (use `/tree build`)

**File Format:**
```
worktree-name|||Full description with spaces and colons
api-auth|||Implement user authentication with JWT
notifications|||Add real-time WebSocket notifications
```

---

### 2. `/tree list`

**Purpose:** Display all staged features

**Usage:**
```bash
/tree list
```

**Output:**
```
🌳 Staged Features

1. api-auth
   Implement user authentication with JWT

2. notifications
   Add real-time WebSocket notifications

3. db-refactor
   Refactor database schema for performance

Total: 3 features staged
```

**Behavior:**
- Reads from `.trees/.staged-features.txt`
- Shows numbered list with descriptions
- Does not show built worktrees (use `git worktree list`)

---

### 3. `/tree clear`

**Purpose:** Remove all staged features

**Usage:**
```bash
/tree clear
```

**Behavior:**
- Deletes `.trees/.staged-features.txt`
- Does not affect already-built worktrees
- Irreversible operation (no confirmation)

**Use Case:** Reset staging queue when priorities change

---

### 4. `/tree conflict`

**Purpose:** Analyze file conflicts between staged features

**Usage:**
```bash
/tree conflict
```

**Output:**
```
🌳 Conflict Analysis

Analyzing 5 features...

⚠️  CONFLICTS DETECTED

Feature: api-auth
  - Conflicts with: db-refactor
  - Files: src/models/user.py, src/database/schema.sql

Feature: dashboard-update
  - Conflicts with: analytics-view
  - Files: frontend/dashboard.tsx

💡 Recommendations:
  1. Merge api-auth + db-refactor into single worktree
  2. Keep dashboard-update and analytics-view separate
  3. Work on conflicting features sequentially
```

**Technical Details:**
- Creates temporary worktree for each feature
- Attempts merge with main branch
- Detects file-level conflicts
- Provides merge recommendations
- Cleans up temporary worktrees after analysis

**Use Case:** Run before `/tree build` to avoid merge conflicts later

---

### 5. `/tree build`

**Purpose:** Create worktrees for all staged features with full automation

**Usage:**
```bash
/tree build                # Auto-execute (default)
/tree build --confirm      # Show confirmations (legacy mode)
```

**Behavior:**

**Phase 1: Worktree Creation**
- Creates git worktree in `.trees/<feature-name>/`
- Generates branch: `feature/<sanitized-name>`
- Based on current branch or `main`/`master`

**Phase 2: File Setup**
- Copies `.claude/commands/` → worktree
- Copies `.claude/scripts/` → worktree
- Generates `.claude-task-context.md` with task description
- Creates `.claude-init.sh` auto-launch script

**Phase 3: Terminal Automation**
- Detects VS Code environment (`$VSCODE_IPC_HOOK_CLI`)
- Generates `.vscode/worktree-tasks.json`
- Auto-executes tasks via `code --command "workbench.action.tasks.runTask"`
- Staggered launch (0.5s delay between terminals)

**Phase 4: Claude Launch**
- Each terminal runs `.claude-init.sh`
- Claude starts with `--append-system-prompt`
- Task context loaded automatically
- Claude asks 1-3 clarifying questions

**Output:**
```
🌳 Building Worktrees

[1/3] ✓ api-auth (2.1s)
[2/3] ✓ notifications (1.8s)
[3/3] ✓ db-refactor (2.3s)

✓ All worktrees created in 6.2s
✓ Terminals launching...
  Terminal 1: api-auth
  Terminal 2: notifications
  Terminal 3: db-refactor

✓ Build complete! Claude instances starting...
```

**Files Created Per Worktree:**
- `.trees/<name>/.claude-init.sh` (executable)
- `.trees/<name>/.claude-task-context.md`
- `.trees/<name>/.claude/commands/*` (copied)
- `.trees/<name>/.claude/scripts/*` (copied)

**Global Files:**
- `.vscode/worktree-tasks.json` (overwritten each build)

---

### 6. `/tree restore`

**Purpose:** Reconnect terminals for existing worktrees

**Usage:**
```bash
/tree restore
```

**Use Cases:**
- VS Code restarted and terminals closed
- Terminals manually closed
- Want to reopen Claude instances with context

**Behavior:**
- Scans `.trees/` for existing worktrees
- Checks for `.claude-init.sh` (regenerates if missing)
- Creates `worktree-tasks.json` for existing worktrees
- Auto-executes tasks to spawn terminals
- Claude relaunches with original task context

**Output:**
```
🌳 Reconnecting Worktree Terminals

Found 5 worktrees:
  1. api-auth
  2. notifications
  3. db-refactor
  4. dashboard-update
  5. analytics-view

✓ Terminals launching...
  Terminal 1: api-auth
  Terminal 2: notifications
  Terminal 3: db-refactor
  Terminal 4: dashboard-update
  Terminal 5: analytics-view

✓ Restore complete!
```

**Note:** Does NOT recreate worktrees, only reconnects terminals

---

### 7. `/tree close`

**Purpose:** Mark worktree as complete and generate synopsis

**Usage:**
```bash
# Run from WITHIN a worktree terminal
/tree close
```

**Behavior:**
- Detects current worktree path
- Prompts user to describe completed work
- Generates `SYNOPSIS.md` with:
  - Work completed summary
  - Files changed (from git diff)
  - Commit history
  - Timestamp
- Moves worktree to `.trees/.completed/`
- Creates symlink for git to track location

**Output:**
```
🌳 Completing Worktree: api-auth

Describe the work completed in this worktree:
> Implemented JWT authentication with refresh tokens, added middleware, updated user model

✓ Synopsis generated: .trees/.completed/api-auth/SYNOPSIS.md
✓ Worktree marked complete
✓ Ready for merge via /tree closedone
```

**Generated SYNOPSIS.md:**
```markdown
# Worktree Synopsis: api-auth

**Completed:** 2025-10-11 14:32:15
**Branch:** feature/api-auth
**Base Branch:** main

## Work Completed

Implemented JWT authentication with refresh tokens, added middleware, updated user model

## Files Changed

Modified:
- src/auth/jwt_handler.py
- src/middleware/auth.py
- src/models/user.py

New:
- src/auth/refresh_tokens.py
- tests/test_auth.py

## Commit History

1. feat: add JWT token generation
2. feat: implement refresh token logic
3. feat: create auth middleware
4. test: add authentication tests
```

---

### 8. `/tree closedone`

**Purpose:** Batch merge and cleanup all completed worktrees

**Usage:**
```bash
/tree closedone                # Interactive mode
/tree closedone --yes          # Skip confirmations
/tree closedone --dry-run      # Preview without executing
```

**Behavior:**

**Phase 1: Discovery**
- Scans `.trees/.completed/` for worktrees
- Lists all completed features with synopsis

**Phase 2: Merge**
- For each worktree:
  1. Switch to base branch (main/master)
  2. Stash uncommitted changes
  3. Attempt merge with `--no-edit`
  4. On conflict: Abort, backup worktree, continue to next
  5. On success: Remove worktree, delete branch

**Phase 3: Cleanup**
- Successful merges: Branch deleted, worktree removed
- Failed merges: Moved to `.trees/.conflict-backup/`
- Archived metadata: Moved to `.trees/.archived/`

**Output:**
```
🌳 Batch Merge and Cleanup

Found 3 completed worktrees:
  1. api-auth - Implemented JWT authentication
  2. notifications - Added WebSocket notifications
  3. db-refactor - Optimized database queries

Continue? (y/n): y

[1/3] api-auth
  ✓ Merged to main
  ✓ Worktree removed
  ✓ Branch deleted

[2/3] notifications
  ✓ Merged to main
  ✓ Worktree removed
  ✓ Branch deleted

[3/3] db-refactor
  ✗ Merge conflict detected
  ⚠️  Worktree backed up to .conflict-backup/
  ℹ  Resolve manually: cd .trees/.conflict-backup/db-refactor

Summary:
  ✓ Successful: 2
  ✗ Conflicts: 1

Next steps:
  1. Resolve conflicts in .trees/.conflict-backup/
  2. Manually merge: git checkout main && git merge feature/db-refactor
  3. Or discard: rm -rf .trees/.conflict-backup/db-refactor
```

**Conflict Handling:**
- Merge aborted on conflict
- Worktree preserved in `.conflict-backup/`
- User instructions provided
- Other worktrees continue processing

---

### 9. `/tree status`

**Purpose:** Show worktree environment diagnostics

**Usage:**
```bash
/tree status
```

**Output:**
```
🌳 Worktree Environment Status

Environment:
  ✓ VS Code detected
  ✓ Claude Code available
  ✓ Git repository initialized

Directories:
  ✓ .trees/ exists
  ✓ .trees/.completed/ exists
  ✓ .trees/.archived/ exists

Active Worktrees: 5
  - api-auth (feature/api-auth)
  - notifications (feature/notifications)
  - db-refactor (feature/db-refactor)
  - dashboard-update (feature/dashboard-update)
  - analytics-view (feature/analytics-view)

Completed Worktrees: 0

Staged Features: 2
  - payment-integration
  - email-templates

Slash Commands:
  ✓ /tree available in main workspace
  ⚠️  To use in worktrees: restart Claude after build
```

**Checks Performed:**
- VS Code environment detection
- Claude Code CLI availability
- Git repository status
- Directory structure integrity
- Active worktree count
- Completed worktree count
- Staged feature count
- Slash command availability

---

### 10. `/tree refresh`

**Purpose:** Check slash command availability and provide session guidance

**Usage:**
```bash
/tree refresh
```

**Output:**
```
🌳 Slash Command Availability Check

Current Location: /workspace/.trees/api-auth

Slash Commands Status:
  ✓ .claude/commands/ directory exists
  ✓ tree.md found (version 4.3.1)
  ✓ 12 other slash commands available

Session Guidance:
  ✓ Commands work natively in this worktree
  ℹ  If commands not working, restart Claude:
     1. Exit current session (Ctrl+D)
     2. Run: bash .claude-init.sh
     3. Commands will reload

Available Commands:
  /tree, /task, /version, /serve, /test, /format, /lint, /db-check, /db-update, /copywriter, /version-bump
```

**Behavior:**
- Detects current directory (main vs worktree)
- Checks for `.claude/commands/` directory
- Lists available slash commands
- Provides troubleshooting guidance
- Main workspace: Informational only
- Worktree: Validates commands were copied during build

**Use Case:** Debug slash command issues in worktrees

---

### 11. `/tree help`

**Purpose:** Display command reference and typical workflow

**Usage:**
```bash
/tree help
/tree
```

**Output:** Concise command list + workflow example

---

## Workflow Patterns

### Pattern 1: Standard Feature Development

**Scenario:** Develop 3 independent features in parallel

```bash
# Stage features
/tree stage Implement user authentication
/tree stage Add payment integration
/tree stage Create admin dashboard

# Review and build
/tree list
/tree build

# Work in each worktree terminal
# (Claude asks clarifying questions, then implement)

# After each feature is complete (run in worktree)
/tree close

# Merge all completed features
/tree closedone
```

**Timeline:**
- Stage: 2 minutes
- Build: 30 seconds
- Development: Hours/days
- Close: 2 minutes per feature
- Closedone: 5 minutes

---

### Pattern 2: Conflict-Aware Development

**Scenario:** Features might touch the same files

```bash
# Stage features
/tree stage Update user model schema
/tree stage Add user profile page
/tree stage Implement user preferences

# Check conflicts BEFORE building
/tree conflict

# Output shows all 3 conflict on user.py
# Decision: merge into 1 worktree or work sequentially

# Option A: Clear and re-stage as single feature
/tree clear
/tree stage User profile system (model + page + preferences)
/tree build

# Option B: Build separately, handle conflicts during merge
/tree build
# (work on features, expect merge conflicts during closedone)
```

---

### Pattern 3: Session Restoration

**Scenario:** VS Code crashed or terminals closed

```bash
# Before crash: 5 worktrees active with Claude sessions

# After restart:
/tree restore

# All 5 terminals reopen
# Claude relaunches with original task context
# Continue work immediately
```

---

### Pattern 4: Selective Cleanup

**Scenario:** Completed 3 of 5 features, want to merge early

```bash
# Complete 3 features
cd .trees/feature-1 && /tree close
cd .trees/feature-2 && /tree close
cd .trees/feature-3 && /tree close

# Merge completed features
/tree closedone

# Continue working on remaining 2 worktrees
# (feature-4 and feature-5 still active)
```

---

### Pattern 5: Dry-Run Validation

**Scenario:** Test merge safety before executing

```bash
# Preview merge without changes
/tree closedone --dry-run

# Output shows:
# - Which worktrees will merge successfully
# - Which will conflict
# - What will be deleted

# If safe, run for real
/tree closedone --yes
```

---

## Technical Implementation

### Key Technologies

- **Bash Script**: 1,545 lines of shell scripting
- **Git Worktrees**: Native git parallel development
- **VS Code Tasks API**: Terminal automation
- **Claude Code CLI**: `--append-system-prompt` for context injection
- **Heredocs**: Script and config generation

---

### File Generation

#### `.claude-init.sh` Template

```bash
#!/bin/bash
# Auto-generated Claude initialization script

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_CONTEXT="$WORKTREE_ROOT/.claude-task-context.md"

# Display banner
echo "════════════════════════════════════════════════════════"
echo "🌳 Worktree: feature-name"
echo "📋 Task: Feature description"
echo "════════════════════════════════════════════════════════"
echo ""
echo "✅ Slash commands available after Claude loads"
echo "📝 Task context loaded in .claude-task-context.md"
echo ""

# Launch Claude with task context
if [ -f "$TASK_CONTEXT" ]; then
    TASK_DESC=$(cat "$TASK_CONTEXT")
    claude --append-system-prompt "You are working in a git worktree dedicated to this task:

$TASK_DESC

IMPORTANT: After you receive this context, immediately read the .claude-task-context.md file to understand the full task details, then ask 1-3 clarifying questions to ensure you understand the scope and requirements before beginning implementation. Focus on:
1. Ambiguous requirements that need clarification
2. Technical decisions that aren't specified
3. Edge cases or error handling expectations
4. Integration points with existing code

Wait for user responses before starting implementation."
else
    claude
fi
```

---

#### `.claude-task-context.md` Template

```markdown
# Task Context for Claude Agent

## Worktree Information
- **Name**: feature-name
- **Branch**: feature/feature-name
- **Base Branch**: main
- **Created**: 2025-10-11 14:30:00

## Task Description

[Full description from staging]

## Objectives

Implement the following:
1. [Inferred from description]
2. [...]

## Context

This worktree is part of a parallel development workflow. Focus solely on this task. Other features are being developed in separate worktrees.

## Available Commands

- `/tree close` - Mark this worktree complete when done
- `/tree status` - Check environment status
- `/tree refresh` - Verify slash commands available

## Notes

- Ask clarifying questions before starting implementation
- Commit changes regularly (use git directly or git-orchestrator)
- Run tests before marking complete
- Generate comprehensive synopsis when closing
```

---

#### VS Code `worktree-tasks.json` Template

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "🌳 1: feature-name",
      "type": "shell",
      "command": "cd /workspace/.trees/feature-name && bash .claude-init.sh",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "dedicated",
        "showReuseMessage": false,
        "clear": false
      },
      "isBackground": false,
      "problemMatcher": [],
      "runOptions": {
        "runOn": "default"
      }
    }
  ]
}
```

---

### Delimiter Design: `|||` vs `:`

**Problem:** Original `:` delimiter broke on descriptions like "API: Add rate limiting"

**Solution:** Changed to `|||` (triple pipe)

**Format:**
```
worktree-name|||Full description with any characters: colons, pipes, etc.
```

**Parsing:**
```bash
while IFS='|||' read -r name desc; do
    # Skip comments and empty lines
    [[ "$name" =~ ^#.*$ ]] || [ -z "$name" ] && continue

    # Use name and desc
    echo "Name: $name"
    echo "Desc: $desc"
done < .staged-features.txt
```

**Benefits:**
- Supports colons in descriptions
- Unlikely to conflict with natural language
- Easy to parse with IFS

---

### VS Code Terminal Automation

**Detection:**
```bash
if [ -n "$VSCODE_IPC_HOOK_CLI" ] || [ "$TERM_PROGRAM" = "vscode" ]; then
    USE_VSCODE_TERMINALS=true
fi
```

**Task Execution:**
```bash
code --command "workbench.action.tasks.runTask" "🌳 1: feature-name"
```

**Staggered Launch:**
```bash
for task in "${tasks[@]}"; do
    code --command "workbench.action.tasks.runTask" "$task" &
    sleep 0.5  # Prevent resource spike
done
```

**Why 0.5s delay:**
- Prevents spawning 10+ terminals simultaneously
- Reduces memory/CPU spike
- Ensures VS Code processes each request
- Total delay: 0.5s × 10 = 5 seconds (acceptable)

---

### Claude Context Injection

**Method:** `--append-system-prompt` flag

**Why not `--system-prompt`:**
- `--append` preserves Claude's base instructions
- `--system-prompt` replaces entirely (dangerous)

**Token Budget:**
- Task context: ~500 tokens
- Clarification instruction: ~150 tokens
- Total overhead: ~650 tokens per session

**Prompt Engineering:**
```
IMPORTANT: After you receive this context, immediately read the
.claude-task-context.md file to understand the full task details,
then ask 1-3 clarifying questions...
```

**Why ask questions:**
- Prevents Claude from making assumptions
- Encourages thoughtful planning
- Reduces implementation errors
- User can refine scope before work begins

---

### Conflict Detection Algorithm

**Process:**

1. **For each staged feature:**
   - Create temporary worktree in `/tmp/tree-conflict-check-XXXX`
   - Checkout base branch in temp worktree
   - Attempt merge of feature branch

2. **Analyze merge result:**
   - Success: No conflicts
   - Failure: Parse `git status` for conflicting files

3. **Build conflict matrix:**
   ```
   Feature A conflicts with Feature B on: file1.py, file2.js
   Feature B conflicts with Feature C on: config.yaml
   ```

4. **Generate recommendations:**
   - Merge conflicting features into single worktree
   - Work on conflicting features sequentially
   - Review conflict files before building

5. **Cleanup:**
   - Remove temporary worktrees
   - Restore git state

**Limitations:**
- Only detects file-level conflicts (not semantic conflicts)
- Requires features to have branches (doesn't work on fresh features)
- Expensive operation (creates N temporary worktrees)

---

## Troubleshooting

### Problem: Claude doesn't start in terminal

**Symptoms:**
```
⚠️  Warning: Claude Code not found in PATH
Terminal will open without Claude
```

**Cause:** Claude CLI not installed or not in PATH

**Solution:**
```bash
# Check if Claude is installed
which claude

# If not found, install Claude Code CLI
# Or add to PATH in ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/claude"

# Restart terminal
source ~/.bashrc
```

---

### Problem: Slash commands don't work in worktree

**Symptoms:**
```
/tree close
-bash: /tree: command not found
```

**Cause:** Claude session started before commands were copied, or commands not synced

**Solution:**
```bash
# Verify commands exist
ls .claude/commands/tree.md

# If missing, copy manually
cp -r /workspace/.claude/commands /workspace/.trees/feature-name/.claude/

# Restart Claude
exit  # or Ctrl+D
bash .claude-init.sh
```

---

### Problem: VS Code terminals don't auto-create

**Symptoms:**
- `/tree build` completes but no terminals appear

**Cause:** VS Code not detected, or `code` command not in PATH

**Solution:**
```bash
# Check VS Code detection
echo $VSCODE_IPC_HOOK_CLI
echo $TERM_PROGRAM

# Verify code command
which code

# Manual terminal creation
cd .trees/feature-name
bash .claude-init.sh
```

---

### Problem: Git lock file persists

**Symptoms:**
```
Git lock detected, waiting... (attempt 1/5)
Git lock file persists. Please run: rm /workspace/.git/index.lock
```

**Cause:** Interrupted git operation

**Solution:**
```bash
# Remove lock file
rm /workspace/.git/index.lock

# Retry operation
/tree build
```

---

### Problem: Merge conflicts during closedone

**Symptoms:**
```
✗ Merge conflict detected
⚠️  Worktree backed up to .conflict-backup/
```

**Cause:** Feature branch diverged from main with conflicting changes

**Solution:**
```bash
# Option 1: Resolve manually
cd .trees/.conflict-backup/feature-name
git checkout main
git merge feature/feature-name
# (resolve conflicts in editor)
git add .
git commit
git branch -d feature/feature-name
rm -rf /workspace/.trees/.conflict-backup/feature-name

# Option 2: Keep worktree, discard merge
# (work continues in worktree, merge later)

# Option 3: Abandon feature
rm -rf .trees/.conflict-backup/feature-name
git branch -D feature/feature-name
```

---

### Problem: Task context not loading in Claude

**Symptoms:**
- Claude starts but doesn't ask clarifying questions
- No task context displayed

**Cause:** `.claude-task-context.md` file missing or corrupt

**Solution:**
```bash
# Verify file exists
ls -la .claude-task-context.md

# Check contents
cat .claude-task-context.md

# Regenerate manually
/tree restore  # rebuilds init scripts
```

---

### Problem: Too many terminals spawned

**Symptoms:**
- VS Code becomes slow
- System memory high

**Cause:** Built 20+ worktrees simultaneously

**Solution:**
```bash
# Close unused terminals
# (manually in VS Code)

# Reduce worktree count
# Only build what you'll actively work on

# Or increase stagger delay
# Edit tree.sh: sleep 0.5 → sleep 1.0
```

---

## Advanced Usage

### Custom Base Branch

**By default:** `/tree build` uses current branch or main/master

**Override:**
```bash
# Stage features
/tree stage Feature 1
/tree stage Feature 2

# Before building, checkout desired base
git checkout develop

# Build from develop
/tree build
```

**Result:** Worktrees branch from `develop` instead of `main`

---

### Manual Worktree Creation

**If automatic build fails:**

```bash
# Create worktree manually
git worktree add -b feature/custom-name .trees/custom-name main

# Copy slash commands
cp -r .claude/commands .trees/custom-name/.claude/
cp -r .claude/scripts .trees/custom-name/.claude/

# Create init script
cd .trees/custom-name
cat > .claude-init.sh << 'EOF'
#!/bin/bash
claude --append-system-prompt "Your task description here"
EOF
chmod +x .claude-init.sh

# Launch terminal
bash .claude-init.sh
```

---

### Batch Staging from File

**Scenario:** 20+ features pre-planned

**Create `features.txt`:**
```
Implement API rate limiting|||Add Redis-based rate limiting with configurable thresholds
Create user dashboard|||Build responsive dashboard with analytics charts
Add email notifications|||Integrate SendGrid for transactional emails
Refactor auth system|||Migrate to JWT with refresh tokens
```

**Bulk stage:**
```bash
while IFS='|||' read -r name desc; do
    echo "/tree stage $desc"
done < features.txt

# Or append directly to staging file
cat features.txt >> .trees/.staged-features.txt

/tree list
/tree build
```

---

### Integration with Git Orchestrator

**For commits within worktrees:**

```bash
# In worktree terminal, after making changes
# Use git-orchestrator instead of direct git commands

# Checkpoint during work
git-orchestrator "checkpoint_check:Feature Name"

# Section commit when milestone complete
git-orchestrator "commit_section:Feature Implementation Complete"

# Then close worktree
/tree close
```

**Why:**
- Automatic test execution
- Schema automation
- Documentation validation
- Conventional commit messages

**Reference:** See `tasks/git-orchestrator-agent/prd.md`

---

### VS Code Workspace Integration

**Create multi-root workspace:**

`.vscode/worktrees.code-workspace`:
```json
{
  "folders": [
    {
      "name": "Main",
      "path": "/workspace"
    },
    {
      "name": "🌳 Feature 1",
      "path": "/workspace/.trees/feature-1"
    },
    {
      "name": "🌳 Feature 2",
      "path": "/workspace/.trees/feature-2"
    }
  ]
}
```

**Open workspace:**
```bash
code worktrees.code-workspace
```

**Benefits:**
- File explorer shows all worktrees
- Search across all worktrees
- Side-by-side editing
- Integrated git status for each

---

### Archival and History

**Archive structure:**
```
.trees/.archived/
├── 2025-10-11-143052-feature-1/
│   ├── SYNOPSIS.md
│   ├── git-log.txt
│   └── final-diff.patch
├── 2025-10-11-145823-feature-2/
└── ...
```

**Query archive:**
```bash
# Find all archived features
ls -la .trees/.archived/

# Search archive for feature
grep -r "authentication" .trees/.archived/

# Restore archived synopsis
cat .trees/.archived/2025-10-11-143052-api-auth/SYNOPSIS.md
```

---

## Related Documentation

- **PRD:** `tasks/prd-tree-enhanced-automation.md` - Feature requirements and design
- **PRD:** `tasks/prd-claude-aware-worktrees.md` - Original worktree automation concept
- **Script:** `.claude/scripts/tree.sh` - Main implementation (1,545 lines)
- **Git Orchestrator:** `tasks/git-orchestrator-agent/prd.md` - Commit automation

---

## Version History

- **v4.3.1** (2025-10-11): Enhanced automation with Claude auto-launch, terminal restoration
- **v4.3.0** (2025-10-10): Initial /tree command system
- **v4.2.0** (2025-10-09): Worktree strategy planning

---

## Feedback and Issues

**Report issues:**
- GitHub: `https://github.com/anthropics/claude-code/issues`
- Or document in: `docs/tree-command-issues.md`

**Feature requests:**
- Add to: `tasks/tree-enhancements.md`

---

**End of Guide**
