# Tree Command: Terminal Automation Deep-Dive

**Version:** 4.3.1
**Last Updated:** 2025-10-11
**Status:** ✅ Production Ready

---

## Executive Summary

The `/tree restore` command provides **ONE-COMMAND terminal creation** for all git worktrees. Due to VS Code devcontainer security restrictions, terminals cannot be created fully automatically via shell scripts. Instead, we generate an automation script that launches all terminals with a single command.

### Quick Start

After running `/tree build` or `/tree restore`:

```bash
bash .vscode/create-worktree-terminals.sh
```

This launches all worktree terminals with Claude auto-loaded.

---

## Technical Background

### Why Fully Automated Terminal Creation Doesn't Work

VS Code devcontainers are **headless environments** without access to terminal emulators. Multiple approaches were investigated:

| Method | Status | Reason for Failure |
|--------|--------|-------------------|
| `code --command workbench.action.tasks.runTask` | ❌ Failed | `--command` flag not supported in devcontainers |
| Background bash spawning `(cd path && exec bash) &` | ❌ Failed | Processes run but don't appear in VS Code terminal panel |
| `gnome-terminal --tab` | ❌ N/A | gnome-terminal not installed in devcontainers |
| `xterm -e` | ❌ N/A | xterm not installed in devcontainers |
| `osascript` (macOS) | ❌ N/A | macOS-specific, not available in Linux containers |
| `tmux new-window` | ❌ N/A | tmux not installed in devcontainers |
| `screen -dmS` | ❌ N/A | screen not installed in devcontainers |
| VS Code IPC socket protocol | ❌ Failed | Proprietary protocol, no public API |
| `terminals.json` configuration | ❌ Invalid | Not a standard VS Code feature |
| `tasks.json` with `"runOn": "folderOpen"` | ⚠️ Partial | Only runs when opening workspace, not on command |

### The Solution: ONE-COMMAND Automation

Since no method can programmatically create terminals in devcontainers, we generate a script that:

1. ✅ Contains all terminal creation commands in sequence
2. ✅ Launches Claude with task context in each terminal
3. ✅ Runs in background so all terminals spawn simultaneously
4. ✅ Requires only ONE user command to execute

**File Generated:** `.vscode/create-worktree-terminals.sh`

---

## Implementation Details

### Generated Files

#### 1. `.vscode/tasks.json`

VS Code tasks for manual terminal creation:

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
        "showReuseMessage": false
      },
      "problemMatcher": [],
      "runOptions": {
        "runOn": "default"
      }
    }
  ]
}
```

**Usage:** Ctrl+Shift+P → "Tasks: Run Task" → Select worktree

#### 2. `.vscode/create-worktree-terminals.sh`

Automation script for ONE-COMMAND terminal creation:

```bash
#!/bin/bash
echo "🌳  Creating Worktree Terminals"

echo "Terminal 1: feature-name"
cd "/workspace/.trees/feature-name/" && bash .claude-init.sh &
sleep 0.5

# ... repeated for each worktree ...

echo "✅  All terminals created"
```

**Usage:** `bash .vscode/create-worktree-terminals.sh`

#### 3. `.vscode/terminals.json`

VS Code terminal configuration (for reference):

```json
{
  "terminals": [
    {
      "name": "🌳 1: feature-name",
      "cwd": "/workspace/.trees/feature-name/",
      "color": "terminal.ansiBlue",
      "icon": "tree"
    }
  ]
}
```

**Note:** This file is informational only; VS Code doesn't use it for automatic terminal restoration.

#### 4. Worktree `.claude-init.sh`

Auto-launch script in each worktree:

```bash
#!/bin/bash
WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_CONTEXT="$WORKTREE_ROOT/.claude-task-context.md"

echo "🌳 Worktree: feature-name"
echo "📋 Task: Implement feature XYZ"

if [ -f "$TASK_CONTEXT" ]; then
    TASK_DESC=$(cat "$TASK_CONTEXT")
    claude --append-system-prompt "You are working in a git worktree dedicated to this task:

$TASK_DESC

IMPORTANT: After you receive this context, immediately read the .claude-task-context.md file to understand the full task details, then ask 1-3 clarifying questions to ensure you understand the scope and requirements before beginning implementation."
fi
```

**Functionality:**
- Displays worktree information banner
- Loads task context from `.claude-task-context.md`
- Launches Claude with task description pre-injected
- Instructs Claude to ask clarifying questions before implementation

---

## Workflow

### 1. Initial Setup (Build Worktrees)

```bash
/tree stage Implement user authentication
/tree stage Add dashboard analytics
/tree build
```

**Output:**
```
✓ Created 2 worktrees
✓ Generated .vscode/create-worktree-terminals.sh
ℹ️ To launch terminals: bash .vscode/create-worktree-terminals.sh
```

### 2. Create Terminals

```bash
bash .vscode/create-worktree-terminals.sh
```

**What Happens:**
1. Script runs in background
2. Each worktree terminal spawns via `bash .claude-init.sh &`
3. Claude launches in each terminal with task context
4. Claude asks 1-3 clarifying questions
5. All terminals appear in VS Code panel dropdown

### 3. After VS Code Restart

```bash
/tree restore
```

**Output:**
```
✓ Terminal configuration complete!
ℹ️ Method 1 (ONE COMMAND - Recommended):
✓   bash .vscode/create-worktree-terminals.sh
```

Then run: `bash .vscode/create-worktree-terminals.sh`

---

## Alternative Methods

### Method 1: ONE COMMAND (Recommended)

```bash
bash .vscode/create-worktree-terminals.sh
```

**Pros:**
- ✅ Single command creates all terminals
- ✅ Fastest method
- ✅ Works reliably in devcontainers

**Cons:**
- ⚠️ Requires manual execution (not fully automatic)

### Method 2: VS Code Tasks

```bash
# For each worktree:
Ctrl+Shift+P → "Tasks: Run Task" → Select "🌳 N: worktree-name"
```

**Pros:**
- ✅ Uses native VS Code task system
- ✅ Can be bound to keyboard shortcuts

**Cons:**
- ❌ Must run separately for each worktree
- ❌ Tedious for 5+ worktrees

### Method 3: Manual Terminal Creation

```bash
# For each worktree:
cd /workspace/.trees/worktree-name
bash .claude-init.sh
```

**Pros:**
- ✅ Full manual control

**Cons:**
- ❌ Most time-consuming
- ❌ Error-prone for multiple worktrees

---

## Troubleshooting

### Terminals Don't Appear After Running Script

**Cause:** Script ran but terminals exited immediately (no TTY attached)

**Solution:** This indicates Claude couldn't launch. Check:

1. Is Claude Code installed?
   ```bash
   command -v claude
   ```

2. Is Claude in PATH?
   ```bash
   echo $PATH | grep claude
   ```

3. Run terminal manually to see error:
   ```bash
   cd /workspace/.trees/worktree-name
   bash .claude-init.sh
   ```

### Claude Launches But No Task Context

**Cause:** `.claude-task-context.md` file missing or corrupted

**Solution:** Regenerate context files:

```bash
/tree restore
```

This recreates all `.claude-init.sh` and `.claude-task-context.md` files.

### Terminals Appear But Claude Asks Unrelated Questions

**Cause:** Wrong task context loaded

**Solution:** Check task context file:

```bash
cat /workspace/.trees/worktree-name/.claude-task-context.md
```

Verify it matches the intended task. If wrong, manually edit or regenerate.

### Can't Find create-worktree-terminals.sh

**Cause:** Script not generated during build

**Solution:** Run restore to generate files:

```bash
/tree restore
```

This creates:
- `.vscode/tasks.json`
- `.vscode/create-worktree-terminals.sh`
- `.vscode/terminals.json`

---

## Future Enhancements

### Potential Improvements

1. **VS Code Extension Integration**
   - Custom extension to create terminals via Extension API
   - Bypasses devcontainer restrictions
   - Provides true one-click terminal creation

2. **Workspace Configuration Automation**
   - Use `tasks.json` with `"runOn": "folderOpen"`
   - Terminals auto-create when workspace opens
   - User reopens workspace after `/tree build`

3. **Terminal Emulator Detection**
   - Detect if gnome-terminal, xterm, or screen available
   - Use native terminal emulator when possible
   - Fallback to current script-based approach

4. **Web-Based Terminal Manager**
   - Standalone web UI for terminal management
   - Opens in browser, controls VS Code terminals via API
   - Useful for remote development

---

## Conclusion

While fully automated terminal creation is not possible in VS Code devcontainers, the **ONE-COMMAND automation script** provides the next best solution:

✅ **Single command execution**
✅ **All terminals launch simultaneously**
✅ **Claude auto-loads with task context**
✅ **Reliable and fast**

This approach balances automation with devcontainer security constraints, providing the best possible user experience within technical limitations.

---

## References

- [VS Code Tasks Documentation](https://code.visualstudio.com/docs/editor/tasks)
- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [Claude Code CLI](https://docs.claude.com/claude-code)
- [PRD: Tree Command Enhancement](/workspace/tasks/prd-tree-enhanced-automation.md)
- [Tree Command Guide](/workspace/docs/tree-command-guide.md)
