---
title: "Prd Tree Enhanced Automation"
type: technical_doc
component: general
status: draft
tags: []
---

# PRD: Enhanced /tree Slash Command with Claude Auto-Launch

## Introduction/Overview

Enhanced `/tree` slash command system that fully automates the parallel development workflow from feature staging to Claude instance initialization. This PRD builds upon the existing `/tree` implementation to add **automatic terminal creation**, **Claude auto-launch**, and **context-aware agent initialization** for each worktree.

**Current Pain Points:**
1. `/tree build` requires manual confirmation (slows workflow)
2. Terminals must be manually created and organized
3. Claude instances must be manually started in each worktree
4. Claude agents don't receive task context automatically
5. Task descriptions are lost after worktree creation
6. No way to reconnect terminals after VS Code restart or terminal closure
7. Slash commands don't load in worktrees until `.claude/commands/` files are copied

**Proposed Solution:**
Fully automated `/tree build` that creates worktrees, copies slash command files, and launches terminals with Claude instances. New `/tree restore` command to reconnect terminals for existing worktrees. Automatic refresh of slash commands so they work in worktrees after Claude restart.

## Goals

1. **Primary Goal**: Zero-confirmation worktree build with automatic Claude initialization
2. **Secondary Goal**: Automatic terminal creation in VS Code panel with Claude running in each
3. **Tertiary Goal**: Context-aware Claude agents that receive task descriptions automatically
4. **Quaternary Goal**: Automatic slash command refresh so `/tree` works in worktrees
5. **Quinary Goal**: Terminal restoration via `/tree restore` for existing worktrees

## User Stories

1. **As a developer**, I want `/tree build` to create worktrees without asking for confirmation, so that I can execute the workflow in a single command.

2. **As a developer**, I want VS Code integrated terminals automatically created for each worktree, so that I don't have to manually manage 10+ terminals.

3. **As a developer**, I want Claude Code to auto-start in each terminal, so that I can immediately begin working without manual initialization.

4. **As a developer**, I want Claude agents to receive the task description automatically, so that they understand their objectives without me having to explain.

5. **As a developer**, I want Claude to possibly ask clarifying questions about the task, so that I can refine the scope before implementation begins.

6. **As a developer**, I want slash commands to work in worktrees after creation, so that I can use `/tree close` and other commands without typing full script paths.

7. **As a developer**, I want to reconnect terminals for existing worktrees after VS Code restarts, so that I can resume work without manual setup.

## Functional Requirements

### MUST 1: Zero-Confirmation Build

**Requirement:** `/tree build` creates all worktrees without user confirmation prompts.

**Implementation:**

1.1. Remove all confirmation prompts from build workflow
- No "Continue with build? (y/n)" prompt
- No "Start Claude instances? (y/n)" prompt
- No "Open terminals? (y/n)" prompt

1.2. Add `--confirm` flag for optional confirmation mode
- Default behavior: Auto-execute
- With flag: Show confirmations (legacy behavior)

1.3. Display progress indicators instead of prompts
```
🚀 Building 5 Worktrees...

[1/5] ✓ api-rate-limiting (2.1s)
[2/5] ✓ websocket-support (1.8s)
[3/5] ✓ dashboard-redesign (2.3s)
[4/5] ✓ email-templates (1.9s)
[5/5] ✓ database-migration (2.4s)

✓ All worktrees created in 10.5s
```

**Files Modified:**
- `.claude/scripts/tree.sh` - `tree_build()` function

### MUST 2: Automatic Terminal Creation in VS Code Panel

**Requirement:** `/tree build` creates integrated terminals in VS Code panel (not tmux windows) as a list view.

**Implementation:**

2.1. Detect VS Code environment
```bash
if [ -n "$VSCODE_IPC_HOOK_CLI" ] || [ -n "$TERM_PROGRAM" = "vscode" ]; then
    USE_VSCODE_TERMINALS=true
fi
```

2.2. Generate VS Code tasks.json for terminal creation
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "🌳 1: api-rate-limiting",
      "type": "shell",
      "command": "cd /workspace/.trees/api-rate-limiting && bash .claude-init.sh",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "dedicated",
        "showReuseMessage": false
      },
      "isBackground": false,
      "problemMatcher": []
    }
  ]
}
```

2.3. Auto-execute terminal creation tasks
```bash
# Generate tasks.json
generate_vscode_tasks

# Execute all tasks to spawn terminals
for task_label in "${TASK_LABELS[@]}"; do
    code --command "workbench.action.tasks.runTask" --args "$task_label" &
done
```

2.4. Terminal layout in VS Code panel
- Each worktree gets dedicated terminal in panel
- Terminals listed vertically in order
- Terminal names: "🌳 N: worktree-name"
- Color coding by task number

**Files Modified:**
- `.claude/scripts/tree.sh` - `tree_build()` function
- `.vscode/worktree-tasks.json` - Generated during build

### MUST 3: Claude Auto-Launch in Each Terminal

**Requirement:** Each terminal automatically starts a Claude Code instance after creation.

**Implementation:**

3.1. Create `.claude-init.sh` startup script in each worktree
```bash
#!/bin/bash
# Auto-generated Claude initialization script
# Worktree: api-rate-limiting
# Created: 2025-10-10

WORKTREE_ROOT="/workspace/.trees/api-rate-limiting"
TASK_CONTEXT="$WORKTREE_ROOT/.claude-task-context.md"

# Display banner
echo "════════════════════════════════════════════════════════"
echo "🌳 Worktree: api-rate-limiting"
echo "📋 Task: Implement API rate limiting and throttling"
echo "════════════════════════════════════════════════════════"
echo ""

# Change to worktree directory
cd "$WORKTREE_ROOT"

# Start Claude with task context
if [ -f "$TASK_CONTEXT" ]; then
    # Read task description
    TASK_DESC=$(grep -A 100 "^## Task Description" "$TASK_CONTEXT" | tail -n +2)

    # Launch Claude with context pre-loaded
    claude --append-system-prompt "You are working in a git worktree dedicated to this task: $TASK_DESC. Your objective is defined in .claude-task-context.md. Read this file and ask clarifying questions before beginning implementation."
else
    # Fallback: Launch Claude without context
    echo "⚠️  Warning: Task context file not found"
    claude
fi
```

3.2. Make init script executable during build
```bash
chmod +x "$WORKTREE_PATH/.claude-init.sh"
```

3.3. VS Code terminal tasks execute init script on creation
- Terminal spawns
- Runs `.claude-init.sh` automatically
- Claude starts with context loaded
- Agent receives task description

**Files Created:**
- `.trees/<worktree-name>/.claude-init.sh` - Per-worktree init script

### MUST 4: Automatic Slash Command Refresh

**Requirement:** Automatically copy `.claude/commands/` files to each worktree during build, so slash commands work after Claude restarts in the worktree.

**Rationale:** Claude Code CLI scans for slash commands at session start from the current working directory. When you start Claude in a worktree, it doesn't find `.claude/commands/` because the worktree is a separate directory. By copying the command files during build and after Claude initialization, slash commands become available in the worktree.

**Implementation:**

4.1. Copy slash command files during worktree creation
```bash
# In tree_build() function, for each worktree created:

copy_slash_commands_to_worktree() {
    local worktree_path=$1

    # Copy .claude directory structure
    if [ -d "$WORKSPACE_ROOT/.claude/commands" ]; then
        mkdir -p "$worktree_path/.claude/commands"
        cp -r "$WORKSPACE_ROOT/.claude/commands/"* "$worktree_path/.claude/commands/"
        print_info "  Copied slash commands to worktree"
    fi

    # Copy scripts too (for command execution)
    if [ -d "$WORKSPACE_ROOT/.claude/scripts" ]; then
        mkdir -p "$worktree_path/.claude/scripts"
        cp -r "$WORKSPACE_ROOT/.claude/scripts/"* "$worktree_path/.claude/scripts/"
    fi
}
```

4.2. Document that slash commands work in worktrees after refresh
```markdown
## Slash Commands in this Worktree

✅ **Slash commands are available!**

The `.claude/commands/` directory has been copied to this worktree.
After Claude starts, all `/tree` commands will work normally:

- `/tree close` - Complete work and generate synopsis
- `/tree status` - Show worktree status
- `/tree restore` - Reconnect terminals (if needed)

**Note:** If commands don't appear:
1. Restart Claude in this worktree (exit and run `bash .claude-init.sh`)
2. Commands will load automatically from `.claude/commands/`
```

4.3. Update `.claude-init.sh` to mention slash commands
```bash
# In .claude-init.sh

echo "════════════════════════════════════════════════════════"
echo "🌳 Worktree: $worktree_name"
echo "📋 Task: $task_description"
echo "════════════════════════════════════════════════════════"
echo ""
echo "✅ Slash commands available after Claude loads:"
echo "   /tree close   - Complete this worktree"
echo "   /tree status  - Show status"
echo "   /tree restore     - Reconnect terminals"
echo ""
echo "📝 Task context loaded in .claude-task-context.md"
echo ""
```

4.4. Handle cases where slash commands don't load immediately
```markdown
## Troubleshooting Slash Commands

If `/tree` commands don't work immediately:

**Cause:** Claude CLI scans for commands at startup. If you started Claude before the files were copied, it won't detect them.

**Solution:**
1. Exit Claude (Ctrl+D or type `exit`)
2. Restart: `bash .claude-init.sh`
3. Slash commands will now be available

**Fallback:** If slash commands still don't work, use the script directly:
```bash
bash .claude/scripts/tree.sh close
bash .claude/scripts/tree.sh status
```
```

**Files Modified:**
- `.claude/scripts/tree.sh` - `tree_build()` calls `copy_slash_commands_to_worktree()`
- `.trees/<worktree-name>/.claude-init.sh` - Display slash command availability
- `.trees/<worktree-name>/PURPOSE.md` - Document slash command usage

**Files Created:**
- `.trees/<worktree-name>/.claude/commands/` - Copied slash command definitions

**Key Insight:**
Once `.claude/commands/` files exist in the worktree, slash commands work normally after Claude restarts. This is a one-time copy operation during build, not a continuous refresh.

### MUST 5: Task Description Storage and Context Loading

**Requirement:** Store task descriptions from `/tree stage` and load them into Claude agent context after initialization.

**Implementation:**

5.1. Enhanced staging file format with descriptions
```
# .trees/.staged-features.txt

# Format: worktree-name|||description
# The description will be loaded into Claude context

api-rate-limiting|||Implement comprehensive API rate limiting with token bucket algorithm. Add per-user and per-IP rate limits. Support configurable limits per endpoint. Include Redis-backed distributed limiting for multi-instance deployments.

websocket-support|||Add WebSocket support for real-time features. Implement connection management, heartbeat mechanism, and message routing. Support authenticated WebSocket connections with JWT tokens.

dashboard-redesign|||Redesign admin dashboard with modern UI components. Use React for frontend. Add data visualization with Chart.js. Implement responsive design for mobile support.
```

5.2. Generate `.claude-task-context.md` in each worktree
```markdown
# Task Context for Claude Agent

## Worktree Information
- **Name**: api-rate-limiting
- **Branch**: task/02-api-rate-limiting
- **Base Branch**: develop/v4.3.1-20251010
- **Created**: 2025-10-10 14:23:45

## Task Description

Implement comprehensive API rate limiting with token bucket algorithm. Add per-user and per-IP rate limits. Support configurable limits per endpoint. Include Redis-backed distributed limiting for multi-instance deployments.

## Scope

This task is focused on adding rate limiting functionality to the API layer. You should:

1. Create rate limiting middleware using token bucket algorithm
2. Implement per-user rate limits (default: 100 req/min)
3. Implement per-IP rate limits (default: 1000 req/min)
4. Add configurable rate limits per endpoint (via environment variables)
5. Integrate Redis for distributed rate limiting across multiple app instances
6. Add rate limit headers to API responses (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
7. Implement graceful degradation if Redis is unavailable
8. Write unit tests and integration tests
9. Update API documentation

## Primary Files

You will likely work on these files:
- `modules/middleware/rate_limiter.py` (new)
- `modules/middleware/throttle.py` (new)
- `app_modular.py` (modifications)
- `tests/test_rate_limiter.py` (new)
- `docs/api/README.md` (documentation)

## Success Criteria

- [ ] Rate limiting middleware implemented with token bucket algorithm
- [ ] Per-user and per-IP rate limits configured
- [ ] Redis integration for distributed limiting
- [ ] Rate limit headers added to responses
- [ ] Graceful Redis failover implemented
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] API documentation updated
- [ ] Code reviewed and approved

## Notes

- This worktree is isolated from main development
- Commit frequently with descriptive messages
- Run tests before marking task complete
- Use `/tree close` when work is finished

## Conflict Warnings

⚠️ **Potential Conflicts:**
- Worktree "logging-middleware" also modifies `app_modular.py`
- Coordinate middleware registration order before merging

## Questions to Answer

Before beginning implementation, please clarify:
1. Should rate limits be configurable at runtime, or only via environment variables?
2. What should the default rate limit be for unauthenticated requests?
3. Should admin users bypass rate limiting?
4. What Redis key naming convention should we use?
5. Should rate limit violations return 429 or 503 status code?
```

5.3. Create context during build from staged descriptions
```bash
# In tree_build() function

generate_task_context() {
    local worktree_name=$1
    local description=$2
    local branch=$3
    local base_branch=$4
    local worktree_path=$5

    # Extract description from staging file (stored with ||| delimiter)
    local task_desc=$(echo "$description" | cut -d'|||' -f2)

    # Generate .claude-task-context.md
    cat > "$worktree_path/.claude-task-context.md" << EOF
# Task Context for Claude Agent

## Worktree Information
- **Name**: $worktree_name
- **Branch**: $branch
- **Base Branch**: $base_branch
- **Created**: $(date +"%Y-%m-%d %H:%M:%S")

## Task Description

$task_desc

## Scope

[Auto-generated scope based on description keywords...]

## Primary Files

[Predicted files based on task description...]

## Success Criteria

- [ ] Core functionality implemented
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed

## Notes

- This worktree is isolated from main development
- Commit frequently with descriptive messages
- Use \`/tree close\` when work is finished

## Questions to Answer

Before beginning implementation, please clarify:
[Auto-generated questions based on description...]
EOF
}
```

5.4. Update `/tree stage` to use enhanced format
```bash
tree_stage() {
    local description="$*"

    if [ -z "$description" ]; then
        print_error "Feature description required"
        echo "Usage: /tree stage [description]"
        return 1
    fi

    # Generate worktree name (slugified)
    local worktree_name=$(slugify "$description")

    # Store with ||| delimiter for description preservation
    echo "${worktree_name}|||${description}" >> "$STAGED_FEATURES_FILE"

    print_success "Feature staged: $worktree_name"
    echo "        Description: $description"
    echo ""
    echo "The description will be loaded into Claude context when built."
}
```

**Files Created:**
- `.trees/<worktree-name>/.claude-task-context.md` - Per-worktree context file

**Files Modified:**
- `.claude/scripts/tree.sh` - `tree_stage()` and `tree_build()` functions
- `.trees/.staged-features.txt` - Enhanced format with descriptions

### MUST 6: Automatic Clarifying Question

**Requirement:** After task description is loaded, Claude agent asks a clarifying question about the task.

**Implementation:**

6.1. Add clarification prompt to Claude initialization
```bash
# In .claude-init.sh script

# Launch Claude with context and instruction to ask clarifying questions
claude --append-system-prompt "You are working in a git worktree dedicated to this task:

$(cat $TASK_CONTEXT)

IMPORTANT: After you receive this context, immediately read the .claude-task-context.md file to understand the full task details, then ask 1-3 clarifying questions to ensure you understand the scope and requirements before beginning implementation. Focus on:
1. Ambiguous requirements that need clarification
2. Technical decisions that aren't specified
3. Edge cases or error handling expectations
4. Integration points with existing code

Wait for user responses before starting implementation."
```

6.2. Example initial agent message (auto-generated)
```
Claude Agent in api-rate-limiting worktree:

I've reviewed the task context for implementing API rate limiting. Before I begin, I have a few clarifying questions:

1. **Rate Limit Configuration**: Should rate limits be configurable at runtime (e.g., via admin API), or only through environment variables at startup?

2. **Authentication Integration**: How should the rate limiter identify users? Should it integrate with the existing authentication middleware, or use a separate user identification mechanism?

3. **Rate Limit Scope**: Should rate limits apply globally to all API endpoints, or should we support per-endpoint customization (e.g., stricter limits on expensive operations)?

4. **Burst Handling**: The description mentions token bucket algorithm. What should the burst capacity be? (e.g., allow up to 2x normal rate for short bursts)

5. **Redis Failover**: When Redis is unavailable, should we fail open (allow all requests) or fail closed (reject requests), or use in-memory fallback?

Please clarify these points so I can implement the solution that best fits your requirements.
```

**Files Modified:**
- `.trees/<worktree-name>/.claude-init.sh` - Add clarification instruction

### MUST 7: Terminal Restoration via `/tree restore`

**Requirement:** Create new integrated terminals in VS Code panel for each existing worktree that doesn't have an active terminal/shell. Launch Claude with context loaded, exactly like during initial build.

**Use Cases:**
1. **VS Code Restart**: After restarting VS Code, all terminals are closed. Use `/tree restore` to reconnect.
2. **Terminal Accidentally Closed**: If you close a worktree terminal, use `/tree restore` to reopen it.
3. **Selective Reconnection**: Only worktrees without active terminals get new terminals (no duplicates).
4. **Session Resume**: Resume work on existing worktrees without rebuilding.

**Implementation:**

7.1. Detect existing worktrees and active terminals
```bash
tree_restore() {
    print_header "Reconnecting Worktree Terminals"

    # Find all existing worktrees
    local worktrees=()
    if [ -d "$TREES_DIR" ]; then
        for dir in "$TREES_DIR"/*/ ; do
            if [ -d "$dir/.git" ] || [ -f "$dir/.git" ]; then
                local name=$(basename "$dir")
                worktrees+=("$name")
            fi
        done
    fi

    if [ ${#worktrees[@]} -eq 0 ]; then
        print_warning "No worktrees found"
        echo "Create worktrees first: /tree build"
        return 0
    fi

    print_info "Found ${#worktrees[@]} worktree(s)"
    echo ""
}
```

7.2. Check for active terminals/shells in each worktree
```bash
has_active_terminal() {
    local worktree_path=$1

    # Check for running Claude processes in this worktree
    if pgrep -f "claude.*$worktree_path" > /dev/null; then
        return 0  # Has active terminal
    fi

    # Check for any shell processes with this working directory
    if lsof +D "$worktree_path" 2>/dev/null | grep -q "bash\|zsh\|sh"; then
        return 0  # Has active shell
    fi

    return 1  # No active terminal
}
```

7.3. Create terminals only for worktrees without active shells
```bash
tree_restore() {
    # ... (continued from 7.1)

    # Filter worktrees that need terminals
    local needs_terminal=()
    for worktree_name in "${worktrees[@]}"; do
        local worktree_path="$TREES_DIR/$worktree_name"

        if has_active_terminal "$worktree_path"; then
            print_info "  ✓ $worktree_name - Terminal already active"
        else
            print_warning "  ⚠ $worktree_name - No active terminal"
            needs_terminal+=("$worktree_name")
        fi
    done

    echo ""

    if [ ${#needs_terminal[@]} -eq 0 ]; then
        print_success "All worktrees have active terminals"
        return 0
    fi

    print_info "Creating terminals for ${#needs_terminal[@]} worktree(s)..."
    echo ""
}
```

7.4. Generate VS Code tasks and launch terminals
```bash
tree_restore() {
    # ... (continued from 7.3)

    # Detect VS Code environment
    if [ -n "$VSCODE_IPC_HOOK_CLI" ] || [ "$TERM_PROGRAM" = "vscode" ]; then
        # Generate tasks.json for terminals
        generate_vscode_pop_tasks "${needs_terminal[@]}"

        # Execute terminal creation tasks
        for worktree_name in "${needs_terminal[@]}"; do
            local task_label="🌳 Pop: $worktree_name"

            if code --command "workbench.action.tasks.runTask" "$task_label" 2>/dev/null; then
                print_success "  Terminal created: $worktree_name"
            else
                print_warning "  Failed to create terminal: $worktree_name"
                print_info "    Manual: cd $TREES_DIR/$worktree_name && ./.claude-init.sh"
            fi

            # Stagger terminal creation to avoid resource spike
            sleep 0.5
        done
    else
        print_warning "VS Code not detected"
        print_info "Run terminals manually:"
        for worktree_name in "${needs_terminal[@]}"; do
            echo "  cd $TREES_DIR/$worktree_name && ./.claude-init.sh"
        done
    fi

    echo ""
    print_success "Terminal reconnection complete"
}
```

7.5. Generate tasks.json for pop operation
```bash
generate_vscode_pop_tasks() {
    local worktree_names=("$@")
    local tasks_file="$WORKSPACE_ROOT/.vscode/worktree-pop-tasks.json"

    mkdir -p "$WORKSPACE_ROOT/.vscode"

    cat > "$tasks_file" << 'TASKHEADER'
{
    "version": "2.0.0",
    "tasks": [
TASKHEADER

    local first=true
    for worktree_name in "${worktree_names[@]}"; do
        local worktree_path="$TREES_DIR/$worktree_name"

        # Add comma separator
        if [ "$first" = false ]; then
            echo "," >> "$tasks_file"
        fi
        first=false

        # Generate task
        cat >> "$tasks_file" << TASKEOF
        {
            "label": "🌳 Pop: $worktree_name",
            "type": "shell",
            "command": "cd $worktree_path && bash .claude-init.sh",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "dedicated",
                "showReuseMessage": false
            },
            "isBackground": false,
            "problemMatcher": []
        }
TASKEOF
    done

    # Close tasks array
    cat >> "$tasks_file" << 'TASKFOOTER'
    ]
}
TASKFOOTER
}
```

7.6. Ensure `.claude-init.sh` exists and is executable
```bash
# In tree_restore(), before creating terminals

for worktree_name in "${needs_terminal[@]}"; do
    local worktree_path="$TREES_DIR/$worktree_name"
    local init_script="$worktree_path/.claude-init.sh"

    # Check if init script exists
    if [ ! -f "$init_script" ]; then
        print_warning "  Missing .claude-init.sh in $worktree_name"
        print_info "  Generating init script..."

        # Generate from template (same as tree_build)
        generate_init_script "$worktree_name" "$worktree_path"
    fi

    # Ensure executable
    chmod +x "$init_script"
done
```

7.7. Load existing task context (if available)
```bash
# .claude-init.sh handles context loading automatically

# If .claude-task-context.md exists, it's loaded
# If not, Claude starts without specific task context

# No changes needed - existing init script already handles this
```

**Example Usage:**

```bash
# After VS Code restart
$ /tree restore

🌳 Reconnecting Worktree Terminals

Found 5 worktree(s)

  ✓ api-rate-limiting - Terminal already active
  ⚠ websocket-support - No active terminal
  ⚠ dashboard-redesign - No active terminal
  ✓ email-templates - Terminal already active
  ⚠ database-migration - No active terminal

Creating terminals for 3 worktree(s)...

  ✓ Terminal created: websocket-support
  ✓ Terminal created: dashboard-redesign
  ✓ Terminal created: database-migration

✓ Terminal reconnection complete
```

**Example VS Code Terminal Panel After `/tree restore`:**

```
TERMINAL (Panel)
├─ 🌳 1: api-rate-limiting (already running)
├─ 🌳 Pop: websocket-support (newly created)
├─ 🌳 Pop: dashboard-redesign (newly created)
├─ 🌳 2: email-templates (already running)
└─ 🌳 Pop: database-migration (newly created)
```

**Files Created:**
- `.vscode/worktree-pop-tasks.json` - Temporary tasks for reconnection

**Files Modified:**
- `.claude/scripts/tree.sh` - Add `tree_restore()` function

**Key Features:**

✅ **No Duplicates**: Only creates terminals for worktrees without active shells
✅ **Context Preserved**: Uses existing `.claude-init.sh` and `.claude-task-context.md`
✅ **Same Experience**: Terminal initialization identical to original build
✅ **Active Detection**: Checks for both Claude processes and shell processes
✅ **Graceful Fallback**: Provides manual commands if VS Code not available
✅ **Staggered Launch**: 0.5s delay between terminals to avoid resource spike

**Edge Cases Handled:**

1. **Missing init script**: Regenerates from template
2. **No VS Code**: Provides manual terminal commands
3. **All terminals active**: Reports success, no action needed
4. **Task execution failure**: Provides manual fallback command
5. **No worktrees exist**: Instructs user to build first

## Technical Implementation Details

### File Structure After Build

```
/workspace/
  .trees/
    api-rate-limiting/
      .claude-init.sh                    # Auto-startup script (MUST 3)
      .claude-task-context.md            # Task context (MUST 5)
      .claude/
        commands/                         # Refreshed slash commands (MUST 4)
          tree.md
          task.md
        scripts/                          # Refreshed scripts (MUST 4)
          tree.sh
      PURPOSE.md                          # Human-readable task doc (existing)
      ... (rest of codebase)

    websocket-support/
      .claude-init.sh
      .claude-task-context.md
      .claude/
        commands/
        scripts/
      PURPOSE.md
      ... (rest of codebase)

    .staged-features.txt                 # Enhanced with descriptions (MUST 5)
    .completed/                           # Synopsis files (existing)
    .archived/                            # Archived completions (existing)

  .claude/
    scripts/
      tree.sh                             # Main tree script (MUST 1, 2, 3, 4)
      refresh-worktree-commands.sh        # Command refresh script (MUST 4)

  .vscode/
    worktree-tasks.json                   # Generated terminal tasks (MUST 2)
```

### Build Workflow Sequence

```
User executes: /tree build

┌─────────────────────────────────────────────────────────────┐
│ 1. Pre-Build Validation (No Confirmation)                   │
│    - Check staged features exist                             │
│    - Verify git state                                        │
│    - Display build plan                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Worktree Creation (MUST 1)                               │
│    - Create each worktree with branch                        │
│    - Generate PURPOSE.md (existing)                          │
│    - Generate .claude-task-context.md (MUST 5)              │
│    - Generate .claude-init.sh (MUST 3)                      │
│    - Progress: [N/Total] ✓ worktree-name (Xs)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Slash Command Refresh (MUST 4)                           │
│    - Copy .claude/commands/ to each worktree                 │
│    - Copy .claude/scripts/ to each worktree                  │
│    - Display: "✓ Slash commands refreshed"                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. VS Code Terminal Generation (MUST 2)                     │
│    - Detect VS Code environment                              │
│    - Generate .vscode/worktree-tasks.json                    │
│    - Create task for each worktree                           │
│    - Task executes: cd <path> && ./.claude-init.sh          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Auto-Execute Terminal Tasks (MUST 2, 3)                  │
│    - Run: code --command workbench.action.tasks.runTask     │
│    - Each task spawns terminal in VS Code panel             │
│    - Terminal executes .claude-init.sh                       │
│    - Claude starts with task context loaded (MUST 5)        │
│    - Agent asks clarifying questions (MUST 6)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Build Summary                                             │
│    - Display completion stats                                │
│    - Show terminal locations                                 │
│    - Provide next steps                                      │
└─────────────────────────────────────────────────────────────┘
```

### Claude Initialization Flow

```
Terminal spawns in VS Code panel
         ↓
Executes .claude-init.sh
         ↓
Changes to worktree directory
         ↓
Displays banner with worktree info
         ↓
Reads .claude-task-context.md
         ↓
Launches Claude with --append-system-prompt
         ↓
Claude receives task context in system prompt
         ↓
Claude reads .claude-task-context.md file
         ↓
Claude analyzes task requirements (MUST 6)
         ↓
Claude asks 1-3 clarifying questions (MUST 6)
         ↓
User responds to questions
         ↓
Claude begins implementation
```

## Implementation Phases

### Phase 1: Core Automation (MUST 1, 4)
**Effort:** 2-3 hours

- Remove confirmation prompts from `/tree build`
- Implement `copy_slash_commands_to_worktree()` function
- Copy `.claude/commands/` and `.claude/scripts/` during build
- Update worktree documentation about slash command availability
- Test with 3-5 worktrees

**Acceptance Criteria:**
- ✓ `/tree build` executes without user input
- ✓ Build completes in <30 seconds for 5 worktrees
- ✓ Slash command files copied to each worktree
- ✓ Commands work in worktree after Claude restart

### Phase 2: Enhanced Staging (MUST 5)
**Effort:** 1-2 hours

- Update staging file format to preserve descriptions (`|||` delimiter)
- Modify `/tree stage` to use new format
- Generate `.claude-task-context.md` during build
- Test description preservation and retrieval

**Acceptance Criteria:**
- ✓ Task descriptions stored in staging file with `|||` delimiter
- ✓ `.claude-task-context.md` generated with full description
- ✓ Context file includes scope, files, success criteria
- ✓ Descriptions survive build process intact

### Phase 3: Claude Auto-Launch (MUST 3, 6)
**Effort:** 3-4 hours

- Create `.claude-init.sh` template generator
- Add clarifying question instruction to system prompt
- Display available commands in init banner
- Test Claude initialization with context
- Verify agent asks questions before implementing

**Acceptance Criteria:**
- ✓ `.claude-init.sh` created in each worktree
- ✓ Claude launches with task context loaded
- ✓ Agent asks clarifying questions automatically
- ✓ Script handles errors gracefully (Claude not in PATH, etc.)
- ✓ Banner displays available script commands

### Phase 4: VS Code Terminal Integration (MUST 2)
**Effort:** 4-5 hours

- Implement VS Code environment detection
- Generate `worktree-tasks.json` during build
- Auto-execute terminal creation tasks
- Test terminal spawning and layout
- Implement staggered launch (0.5s delay)

**Acceptance Criteria:**
- ✓ Terminals created in VS Code panel (not tmux)
- ✓ Terminals listed vertically with tree icons (🌳)
- ✓ Each terminal auto-executes `.claude-init.sh`
- ✓ Terminals properly named and organized
- ✓ Staggered launch prevents resource spike

### Phase 5: Terminal Reconnection (MUST 7)
**Effort:** 3-4 hours

- Implement `tree_restore()` function
- Add active terminal detection (`pgrep`, `lsof`)
- Generate pop-specific VS Code tasks
- Regenerate missing `.claude-init.sh` files
- Test reconnection after VS Code restart

**Acceptance Criteria:**
- ✓ `/tree restore` detects existing worktrees
- ✓ Active terminal detection works correctly
- ✓ Only creates terminals for worktrees without active shells
- ✓ Handles missing init scripts gracefully
- ✓ Same initialization experience as `/tree build`

### Phase 6: Integration & Polish
**Effort:** 2-3 hours

- End-to-end testing of full workflow
- Test `/tree restore` after VS Code restart
- Test selective reconnection (some active, some not)
- Error handling and edge cases
- Documentation updates
- Performance optimization

**Acceptance Criteria:**
- ✓ Full workflow: stage → build → 5 Claude instances running
- ✓ Workflow completes in <60 seconds for 5 worktrees
- ✓ `/tree restore` reconnects only needed terminals
- ✓ Error messages clear and actionable
- ✓ Documentation updated with examples
- ✓ All 7 MUST requirements verified

**Total Estimated Effort:** 15-21 hours

## Success Metrics

1. **Zero Interaction Build**: `/tree build` completes without user input 100% of time
2. **Terminal Creation Speed**: All terminals created in <10 seconds
3. **Claude Launch Success**: 100% of terminals successfully launch Claude
4. **Context Loading Accuracy**: Task descriptions match Claude context 100% of time
5. **Question Quality**: Claude asks relevant clarifying questions 90%+ of time
6. **Terminal Reconnection**: `/tree restore` successfully reconnects all closed terminals
7. **Active Detection Accuracy**: Correctly identifies active vs inactive terminals 95%+ of time
8. **Build Performance**: Complete workflow <60 seconds for 10 worktrees
9. **Pop Performance**: Reconnection workflow <30 seconds for 10 worktrees
10. **User Time Saved**: Reduce setup from 10+ minutes to <1 minute

## Edge Cases & Error Handling

### VS Code Not Detected
```bash
if [ -z "$VSCODE_IPC_HOOK_CLI" ]; then
    print_warning "VS Code not detected. Falling back to tmux windows."
    create_tmux_windows
fi
```

### Claude Not in PATH
```bash
if ! command -v claude &> /dev/null; then
    print_error "Claude Code not found in PATH"
    echo "Install Claude Code or add to PATH"
    echo "Terminal will open without Claude"
    exec bash  # Fallback to regular bash
fi
```

### Task Context File Missing
```bash
if [ ! -f "$TASK_CONTEXT" ]; then
    print_warning "Task context file not found"
    print_info "Creating from PURPOSE.md..."
    generate_context_from_purpose
fi
```

### Slash Commands Still Don't Work
```markdown
## Troubleshooting

If slash commands still don't work after refresh:

1. **Verify files copied**: `ls -la .claude/commands/`
2. **Restart Claude session**: Exit and restart Claude Code
3. **Use local scripts**: `bash .claude/scripts/tree.sh <cmd>`
4. **Check permissions**: `chmod +x .claude/scripts/*.sh`
```

### Terminal Creation Fails
```bash
if ! code --command "workbench.action.tasks.runTask" --args "$task_label"; then
    print_warning "VS Code terminal creation failed for $worktree_name"
    print_info "Manual workaround: Open terminal and run:"
    echo "  cd $worktree_path && ./.claude-init.sh"
fi
```

### Multiple Staged Features With Same Name
```bash
if grep -q "^${worktree_name}|||" "$STAGED_FEATURES_FILE"; then
    print_error "Feature already staged: $worktree_name"
    echo "Use a more specific description or remove existing feature first"
    return 1
fi
```

## Command Reference

### Available Commands

All commands use the `/tree` slash command interface.

**Planning Phase:**
- `/tree stage [description]` - Stage feature for worktree creation
- `/tree list` - Show staged features
- `/tree clear` - Clear all staged features
- `/tree conflict` - Analyze conflicts and suggest merges

**Build Phase:**
- `/tree build` - Create worktrees from staged features (zero-confirmation)

**Active Development:**
- `/tree status` - Show worktree environment status
- `/tree restore` - Reconnect terminals for worktrees without active shells
- `/tree close` - Complete work, generate synopsis (run from within worktree)
- `/tree closedone` - Batch merge and cleanup completed worktrees

**Utilities:**
- `/tree help` - Show detailed help

**Slash Commands in Worktrees:**
After `/tree build`, all worktrees have `.claude/commands/` copied, so slash commands work natively in worktrees after Claude starts.

**Typical Workflow:**
```bash
# In main workspace - stage multiple features
/tree stage Implement API rate limiting
/tree stage Add WebSocket support
/tree stage Redesign dashboard UI

# Review and build
/tree list
/tree build  # Auto-creates terminals with Claude, copies slash commands

# Work in worktree terminals...
# Slash commands work in worktrees!

# After VS Code restart (from main workspace)
/tree restore  # Reconnect closed terminals

# Complete work (from within each worktree)
/tree close  # ✅ Slash command works in worktree!

# Merge all (from main workspace)
/tree closedone
```

**Script Fallback:**
If slash commands don't load in a worktree, use the local script copy:
```bash
bash .claude/scripts/tree.sh close
bash .claude/scripts/tree.sh status
```

## Non-Goals (Out of Scope)

1. **Multi-Workspace Support**: Only single workspace supported
2. **Remote Worktree Creation**: Local filesystem only
3. **Custom Claude Models Per Task**: All use default model
4. **Inter-Agent Communication**: Agents work independently
5. **Automatic Task Prioritization**: User defines task order
6. **Integration with External PM Tools**: Standalone system
7. **Automatic Code Review**: Manual review required
8. **Automatic Merging**: User controls when to merge
9. **Cloud-Based Worktrees**: Local development only
10. **Windows WSL Support**: Linux/macOS only (for now)
11. **Terminal Persistence Across Reboots**: Use `/tree restore` to reconnect
12. **Continuous Slash Command Sync**: One-time copy during build, not continuous sync

## Open Questions

1. **Terminal Color Coding**: Should terminals use different colors per worktree for visual distinction?
   - **Recommendation**: Yes, cycle through 8 ANSI colors based on task number

2. **Claude Session Persistence**: Should Claude conversations persist across terminal restarts?
   - **Recommendation**: No, fresh context on each restart ensures alignment with task state

3. **Context File Updates**: How should users update task context after initial build?
   - **Recommendation**: Direct edit of `.claude-task-context.md`, no auto-sync to avoid overwriting

4. **Terminal Cleanup**: Should `/tree closedone` automatically close VS Code terminals?
   - **Recommendation**: Yes, send close command to terminal after successful merge

5. **Parallel Claude Launch**: Should all Claude instances start simultaneously or staggered?
   - **Recommendation**: Staggered (0.5s delay between launches) to avoid resource spike

6. **Question Response Handling**: Should there be a timeout for clarifying questions?
   - **Recommendation**: No timeout, user proceeds when ready. Agent waits for responses.

7. **Context File Format**: Markdown vs JSON for task context?
   - **Recommendation**: Markdown for human readability and Claude's native format

8. **Slash Command Sync**: Should worktree commands auto-sync when main workspace commands update?
   - **Recommendation**: Manual sync via `/tree refresh` to avoid mid-session disruption

## Dependencies

### Required Tools
- Claude Code CLI (`claude` command)
- VS Code (`code` command for terminal automation)
- Git worktree support (Git 2.5+)
- Bash 4.0+ (for associative arrays)

### Optional Tools
- tmux (fallback if VS Code not available)
- jq (for JSON manipulation)

### VS Code Extensions
- No extensions required (uses built-in terminal and tasks API)

## Testing Strategy

### Unit Tests
- Test slugification of feature descriptions
- Test staging file format parsing
- Test context file generation
- Test init script template generation

### Integration Tests
1. **Full Build Test**: Stage 5 features → Build → Verify terminals created
2. **Context Loading Test**: Verify task descriptions in Claude context
3. **Slash Command Test**: Verify commands work in worktrees after refresh
4. **Error Handling Test**: Verify graceful failure when VS Code unavailable

### Manual Tests
1. **User Experience Test**: Time complete workflow (should be <60s)
2. **Question Quality Test**: Verify Claude asks relevant questions
3. **Terminal Layout Test**: Verify terminals organized properly in panel
4. **Multi-Worktree Test**: Build 10 worktrees, verify all launch successfully

### Performance Tests
- Measure build time for 1, 5, 10, 20 worktrees
- Measure memory usage with all Claude instances running
- Measure terminal creation time

**Performance Targets:**
- 5 worktrees: <30 seconds
- 10 worktrees: <60 seconds
- 20 worktrees: <120 seconds

## Documentation Updates

### Files to Update
1. `tasks/prd-tree-slash-command.md` - Add reference to enhanced automation
2. `.claude/commands/tree.md` - Update command description
3. `README.md` - Add enhanced workflow example
4. `docs/workflows/parallel-development.md` - Document automated workflow

### New Documentation
1. `docs/tree-auto-launch.md` - Explain auto-launch mechanism
2. `docs/troubleshooting-worktrees.md` - Common issues and solutions
3. `.trees/README.md` - Explain worktree structure and files

---

## Summary

This PRD defines 7 MUST-HAVE requirements for enhanced `/tree` slash command automation:

1. **MUST 1**: Zero-confirmation build - `/tree build` executes without prompts
2. **MUST 2**: Automatic VS Code terminal creation in panel (not tmux)
3. **MUST 3**: Claude auto-launch in each terminal with context pre-loaded
4. **MUST 4**: Automatic slash command refresh - copy `.claude/commands/` to worktrees
5. **MUST 5**: Task description storage and context loading into Claude
6. **MUST 6**: Automatic clarifying questions from Claude before implementation
7. **MUST 7**: Terminal reconnection via `/tree restore` for existing worktrees

**Key Innovations:**

✅ **Zero User Input**: Complete worktree creation and Claude initialization in one command
✅ **Context-Aware Agents**: Claude receives task objectives automatically
✅ **Terminal Reconnection**: Resume work after VS Code restart with `/tree restore`
✅ **Slash Commands in Worktrees**: Automatic copy of `.claude/commands/` enables native slash command usage
✅ **Smart Detection**: Only reconnect terminals that are actually closed

**User Impact:**

- **Time Savings**: 10+ minutes → <1 minute for worktree setup
- **Cognitive Load**: No manual terminal management or context explanation
- **Slash Commands Everywhere**: Native `/tree` commands work in both main workspace and worktrees
- **Resume Capability**: Reconnect work environment after restarts with `/tree restore`

**Implementation Scope:**

- 6 implementation phases
- 15-21 hours estimated effort
- Full backward compatibility
- Comprehensive error handling and edge cases

---

**Document Version:** 1.0
**Created:** 2025-10-10
**Updated:** 2025-10-10
**Type:** feature-enhancement
**Status:** Draft
**Priority:** High
**Estimated Effort:** 15-21 hours
**Dependencies:** Existing `/tree` implementation
**Breaking Changes:** None (backwards compatible)
**New Commands:** `/tree restore` for terminal reconnection
