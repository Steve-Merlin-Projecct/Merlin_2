---
title: "Prd Claude Aware Worktrees"
type: technical_doc
component: general
status: draft
tags: []
---

# PRD: Claude-Aware Worktree Automation

## Introduction/Overview

Enhanced worktree creation system that provides automatic purpose context to Claude Code instances and auto-launches Claude in integrated terminals. This solves the problem of Claude instances not knowing what task they should be working on when started in a worktree, and automates the workflow of opening terminals and starting Claude for each parallel development task.

## Goals

1. **Primary Goal**: Automatically pass purpose context to Claude instances when they start in a worktree
2. **Secondary Goal**: Auto-create VS Code integrated terminals that launch Claude Code on startup
3. **Tertiary Goal**: Eliminate manual setup steps for parallel development workflow

## User Stories

1. **As a developer**, I want Claude to automatically know what task it's working on when I start it in a worktree, so that I don't have to manually explain the context every time.

2. **As a developer**, I want VS Code to automatically create terminals for each worktree, so that I don't have to manually create them.

3. **As a developer**, I want Claude Code to auto-start in each worktree terminal, so that I can immediately begin working on tasks.

4. **As a developer**, I want task descriptions and scope automatically loaded from PURPOSE.md or PRD files, so that Claude has complete context.

5. **As a developer**, I want a startup script I can customize per worktree, so that different tasks can have different initialization logic.

## Functional Requirements

### 1. purpose context Passing

1.1. Create `.claude-purpose-context.md` file in each worktree root with:
   - Task description and scope
   - Primary files to work on
   - Conflict warnings
   - Status checklist

1.2. Create `.claude/init.sh` startup script that:
   - Reads purpose context from `.claude-purpose-context.md`
   - Uses `claude --append-system-prompt` to inject context
   - Sets working directory to worktree root
   - Displays welcome message with task information

1.3. Modify `create-worktree-batch.sh` to:
   - Generate `.claude-purpose-context.md` from task description
   - Create `.claude/init.sh` with proper permissions
   - Copy Claude settings to worktree if needed

### 2. Integrated Terminal Automation

2.1. Generate `.vscode/terminals.json` with entries for each worktree:
   - Terminal name: Task number and description
   - Working directory: Worktree path
   - Color coding for visual distinction
   - Profile with auto-run command

2.2. Create terminal profile that executes on startup:
   - Changes to worktree directory
   - Sources `.claude/init.sh`
   - Launches Claude Code with purpose context

2.3. Support VS Code "Restore Terminals" feature:
   - Terminals persist across VS Code restarts
   - Auto-reconnect to running Claude sessions

### 3. purpose context File Format

3.1. `.claude-purpose-context.md` structure:
```markdown
# Task: [Description]

**Worktree:** [name]
**Branch:** [branch-name]
**Status:** In Progress

## Objective
[What needs to be accomplished]

## Scope
[Detailed scope from task list]

## Primary Files
- [List of files to work on]

## Conflict Warnings
- [Potential conflicts with other tasks]

## Success Criteria
- [ ] [Checklist item 1]
- [ ] [Checklist item 2]

## Notes
[Additional context, links, references]
```

### 4. Claude Startup Script

4.1. `.claude/init.sh` template:
```bash
#!/bin/bash
# Claude Code Auto-Startup for [Task Name]

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASK_CONTEXT="$WORKTREE_ROOT/.claude-purpose-context.md"

# Display task information
if [ -f "$TASK_CONTEXT" ]; then
    echo "================================"
    echo "Claude Code - purpose context Loaded"
    echo "================================"
    head -10 "$TASK_CONTEXT"
    echo ""
fi

# Launch Claude with purpose context
if [ -f "$TASK_CONTEXT" ]; then
    CONTEXT=$(cat "$TASK_CONTEXT")
    claude --append-system-prompt "You are working on this specific task: $CONTEXT. Focus on this task and its objectives. Refer to .claude-purpose-context.md for details."
else
    claude
fi
```

### 5. Batch Creation Enhancements

5.1. Update `create-worktree-batch.sh` to:
   - Parse task descriptions from input file
   - Generate `.claude-purpose-context.md` for each worktree
   - Create `.claude/init.sh` startup scripts
   - Generate updated `.vscode/terminals.json`
   - Create shell script to open all Claude sessions

5.2. Support additional metadata in task file:
```
# tasks.txt format
worktree-name:Task Description:primary-file1.py,primary-file2.py:conflict-with-task-5
```

## Non-Goals (Out of Scope)

1. Browser-based terminal management (VS Code only)
2. Support for non-VS Code editors
3. Automatic Claude model selection per task
4. Inter-task communication or coordination
5. Automatic merging or conflict resolution
6. Task progress tracking beyond checklist
7. Integration with external project management tools

## Design Considerations

### File Structure
```
.trees/
  claude-refinement/
    .claude/
      init.sh                    # Auto-startup script
      settings.local.json        # Claude settings (copied from main)
    .claude-purpose-context.md      # purpose context for Claude
    PURPOSE.md                      # Human-readable task doc (existing)
    ... (rest of worktree files)
```

### VS Code Integration
```json
{
  "terminals": [
    {
      "name": "🌳 Task 1: Claude & Agents",
      "cwd": "${workspaceFolder}/.trees/claude-refinement",
      "color": "terminal.ansiBlue",
      "profile": {
        "command": "/bin/bash",
        "args": ["-c", "source .claude/init.sh"]
      }
    }
  ]
}
```

### purpose context Template
```markdown
# Task: Claude.md Refinement & Agent Creation

**Worktree:** claude-refinement
**Branch:** task/01-claude-refinement
**Status:** In Progress
**Created:** 2025-10-09

## Objective
Refine CLAUDE.md instructions, create specialized agents, and develop slash commands for improved development workflow.

## Scope
- Update CLAUDE.md with clearer instructions
- Create specialized agents in .claude/agents/
- Develop custom slash commands in .claude/commands/
- Document agent usage patterns

## Primary Files
- CLAUDE.md
- .claude/commands/*.md (new)
- docs/agent-creation-guide.md (new)

## Conflict Warnings
- 🔴 HIGH: Task 10 (Librarian) also modifies CLAUDE.md
- Resolution: Coordinate changes, merge carefully

## Success Criteria
- [ ] CLAUDE.md instructions clear and comprehensive
- [ ] 3+ specialized agents created
- [ ] 5+ custom slash commands implemented
- [ ] Agent usage documented

## Notes
- Reference existing .claude/commands/ for format
- Test agents with real workflows before documenting
```

## Technical Considerations

### Claude CLI Integration
- Use `--append-system-prompt` to inject purpose context
- Context limited to ~1000 tokens (keep concise)
- Format context as markdown for readability
- Option to use `--settings` for per-worktree Claude config

### VS Code Terminal Profiles
- Requires VS Code 1.70+ for terminal profiles
- `terminals.json` is non-standard, may need `.vscode/settings.json`
- Alternative: Use tasks.json with "runOn": "folderOpen"
- Terminals may need manual activation first time

### Startup Script Permissions
- Must be executable: `chmod +x .claude/init.sh`
- Must handle case where Claude not in PATH
- Should work in both bash and zsh
- Needs proper error handling if context file missing

### Context File Synchronization
- purpose context should match PURPOSE.md content
- Consider symlinking vs copying
- Update mechanism when task scope changes
- Git ignore vs commit decision

### Performance Impact
- Auto-starting 13+ Claude instances could be heavy
- Consider staggered startup or on-demand launch
- Memory usage: ~500MB per Claude instance
- Alternative: Launch only when terminal activated

## Success Metrics

1. **Context Awareness**: 100% of Claude sessions know their task immediately
2. **Startup Time**: Terminal + Claude launch < 5 seconds per worktree
3. **User Actions**: Reduce manual setup from 13 steps to 1 (run script)
4. **Accuracy**: purpose context matches intended scope 100% of time
5. **Adoption**: Developers use automated terminals vs manual 90%+ of time

## Open Questions

1. **Auto-Launch Timing**: Launch Claude immediately on terminal open, or wait for user command?
   - Immediate may be too aggressive (13 instances at once)
   - On-demand requires user to know command
   - **Decision**: Wait for user command, provide helper script

2. **Context File Location**: `.claude-purpose-context.md` in root, or `.claude/task-context.md`?
   - Root is more visible
   - .claude/ is more organized
   - **Decision**: Root for visibility, symlink to .claude/ for organization

3. **Terminal Profile Method**: Use terminals.json, tasks.json, or settings.json?
   - terminals.json is unofficial but simple
   - tasks.json is official but for build tasks
   - settings.json with terminal profiles is official and flexible
   - **Decision**: Use settings.json with terminal.integrated.profiles

4. **Claude Session Persistence**: Should Claude sessions persist across terminal restarts?
   - Pros: Maintains conversation history
   - Cons: May not reflect updated context
   - **Decision**: Use `--continue` flag for optional persistence

5. **Context Update Mechanism**: How to update purpose context after worktree creation?
   - Manual edit of .claude-purpose-context.md
   - Re-run creation script with --update flag
   - Separate update-context.sh script
   - **Decision**: Manual edit + update-context.sh helper

6. **Multi-Worktree Coordination**: Should Claude instances know about other tasks?
   - Helpful for conflict awareness
   - Could be confusing or distracting
   - Large context overhead
   - **Decision**: No, keep each Claude focused on its task only

---

**Document Version:** 1.0
**Created:** 2025-10-09
**Type:** feature
**Status:** Draft
**Branch:** task/00-worktree-manager
**Worktree:** .trees/worktree-manager
