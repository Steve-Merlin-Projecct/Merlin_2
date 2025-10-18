# Worktree Context Auto-Injection Hook

## Overview

The `session-start.sh` hook automatically loads worktree task context when Claude Code starts inside a git worktree, eliminating manual context loading and ensuring agents stay focused on their assigned tasks.

## How It Works

### Detection Logic
```bash
# Worktrees are located at: /workspace/.trees/worktree-name/
if [[ $PWD == /workspace/.trees/* ]]; then
    # Extract worktree name and load context
fi
```

### Context Sources

The hook reads two files created by `/tree build`:

1. **`.claude-task-context.md`** - Primary task information
   - Worktree name and branch
   - Task description
   - Scope and success criteria
   - Available slash commands

2. **`PURPOSE.md`** - Additional context
   - Detailed objective
   - In-scope and out-of-scope items
   - Implementation notes

### What Gets Injected

When Claude starts in a worktree, it receives:

```
📋 WORKTREE TASK CONTEXT (from .claude-task-context.md):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Task Context for Claude Agent

## Worktree Information
- Name: my-feature
- Branch: feature/my-feature
- Base Branch: develop/v4.3.3-worktrees-20251017-044814
- Created: 2025-10-17 04:48:51

## Task Description
Implement user authentication system with OAuth 2.0

[Full context...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 WORKTREE PURPOSE (from PURPOSE.md):
[Additional context...]

🔧 WORKTREE WORKFLOW COMMANDS:
- /tree close           - Complete this feature
- /tree close incomplete - Save for next cycle
- /tree status          - Show status

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 AGENT INSTRUCTIONS:

You have been provided the worktree task context above. Before beginning implementation:

1. READ and ANALYZE the task description, scope, and success criteria carefully
2. IDENTIFY any ambiguous requirements, missing details, or unclear expectations
3. ASK the user 2-4 specific, targeted questions about:
   - Technical decisions that aren't specified in the context
   - Ambiguous requirements that need clarification
   - Edge cases or error handling expectations
   - Integration points with existing code
   - Any constraints or preferences for implementation approach

DO NOT ask generic questions like 'Do you understand?' or 'What would you like to start with?'
Instead, ask SPECIFIC questions based on gaps or ambiguities you identified in the context.

After the user answers your questions, proceed with implementation.
```

**User Interaction Flow:**
1. User starts Claude in worktree → Hook runs automatically
2. Hook displays full task context → Agent receives context
3. Agent analyzes context for gaps/ambiguities
4. Agent asks 2-4 SPECIFIC questions based on actual task details
5. User answers clarifying questions
6. Agent proceeds with implementation with full clarity

**Example Agent Questions (good):**
- "The task mentions OAuth 2.0 - should we use authorization code flow or client credentials?"
- "Where should we store the OAuth tokens - database or session storage?"
- "What should happen if token refresh fails - redirect to login or show error?"

**Example Generic Questions (bad):**
- "Do you understand the task?"
- "What would you like to start with?"
- "Are there any questions?"

## Integration with `/tree build`

### Worktree Creation Flow

```bash
# User stages features
/tree stage Add user authentication
/tree stage Implement dashboard

# Build creates worktrees with context files
/tree build

# For each worktree, creates:
├── .claude-task-context.md  ← Read by hook
├── PURPOSE.md                ← Read by hook
└── .claude-init.sh           ← Launches Claude
```

### Context File Generation

The `/tree build` command (in `.claude/scripts/tree.sh`) generates context:

```bash
# From tree.sh lines 1406-1437
generate_task_context() {
    cat > "$worktree_path/.claude-task-context.md" << EOF
# Task Context for Claude Agent

## Worktree Information
- **Name**: $worktree_name
- **Branch**: $branch
- **Base Branch**: $base_branch
- **Created**: $(date +%Y-%m-%d %H:%M:%S)

## Task Description
$description

[Additional sections...]
EOF
}
```

## Benefits

### 1. Zero Manual Overhead
- No need to read context files manually
- Agent immediately knows its focused task
- Context loads before first interaction

### 2. Enforces Worktree Isolation
- Agent stays focused on single feature
- Reduces context switching
- Parallel development without interference

### 3. Consistency Across Sessions
- Same context every time Claude starts
- Survives terminal restarts
- Works with `/tree restore` command

### 4. Silent in Main Workspace
- Only activates inside `/workspace/.trees/*/`
- Returns empty `{}` in main workspace
- No interference with regular development

## Testing

### Test Inside Worktree
```bash
cd /workspace/.trees/my-feature
.claude/hooks/session-start.sh
# Output: Full context JSON with task details
```

### Test Outside Worktree
```bash
cd /workspace
.claude/hooks/session-start.sh
# Output: {}
```

### Test with Actual Session
```bash
# Inside worktree
cd /workspace/.trees/my-feature
claude

# Hook runs automatically on session start
# Agent receives task context immediately
```

## Configuration

Hook is registered in `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "session-start.sh"
          }
        ]
      }
    ]
  }
}
```

## Architecture

```
Session Start
     ↓
session-start.sh
     ↓
Detect: Is CWD in /workspace/.trees/*?
     ↓
     ├─ No  → Return {}
     ↓
     └─ Yes → Extract worktree name
               ↓
               Read .claude-task-context.md
               ↓
               Read PURPOSE.md
               ↓
               Format context message
               ↓
               Return JSON with context
               ↓
               Claude displays to agent
               ↓
               Agent begins with full task knowledge
```

## Future Enhancements

Potential improvements:

1. **Task Progress Tracking**
   - Read incomplete tasks from previous sessions
   - Show completed milestones

2. **Related File Hints**
   - Suggest relevant files to read
   - Based on task description keywords

3. **Dependency Detection**
   - Warn if worktree is behind base branch
   - Suggest rebase if needed

4. **Custom Instructions**
   - Per-worktree behavioral overrides
   - Task-specific coding standards

## Troubleshooting

### Hook Not Running
```bash
# Verify hook is registered
cat .claude/settings.json | grep SessionStart

# Verify hook is executable
ls -la .claude/hooks/session-start.sh

# Test manually
.claude/hooks/session-start.sh
```

### Context Not Loading
```bash
# Check context files exist
ls -la .claude-task-context.md PURPOSE.md

# Check file contents
cat .claude-task-context.md
```

### Wrong Worktree Detected
```bash
# Verify current directory
pwd
# Should be: /workspace/.trees/worktree-name

# Check worktree name extraction
basename $(pwd)
```

## Related Documentation

- Hook system: `.claude/hooks/README.md`
- Worktree workflow: `docs/tree-command-guide.md`
- Tree command: `.claude/commands/tree.md`
- Worktree architecture: `docs/workflows/tree-worktree-architecture.md`