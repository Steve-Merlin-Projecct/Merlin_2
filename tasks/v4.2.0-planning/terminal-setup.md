---
title: "Terminal Setup"
type: technical_doc
component: general
status: draft
tags: []
---

# Terminal Setup for v4.2.0 Worktrees

## Quick Start

### Option 1: Tmux (Recommended)
Open all 13 worktree terminals in one tmux session:

```bash
./scripts/open-all-terminals.sh
```

**Tmux Navigation:**
- Switch windows: `Ctrl+b` then number (0-13)
- List windows: `Ctrl+b` then `w`
- Detach: `Ctrl+b` then `d`
- Reattach: `tmux attach -t v4.2.0-dev`

### Option 2: VS Code Tasks
Use VS Code Command Palette (`Ctrl+Shift+P`):
1. Type: `Tasks: Run Task`
2. Select: `Open ALL Worktree Terminals`

### Option 3: Manual Terminal Opening
Open individual terminals in VS Code:

```bash
# Task 1: Claude & Agents
cd /workspace/.trees/claude-refinement

# Task 2: Marketing Content
cd /workspace/.trees/marketing-content

# Task 3: Script Testing
cd /workspace/.trees/script-testing

# Task 4: Templates
cd /workspace/.trees/template-creation

# Task 5: Docx Verification
cd /workspace/.trees/docx-verification

# Task 6: Calendly
cd /workspace/.trees/calendly

# Task 7: Dashboard
cd /workspace/.trees/dashboard-redesign

# Task 8: Database Viz
cd /workspace/.trees/database-viz

# Task 9: Gemini Prompts
cd /workspace/.trees/gemini-prompts

# Task 10: Librarian
cd /workspace/.trees/librarian

# Task 11: Email
cd /workspace/.trees/email-refinement

# Task 12: GitHub
cd /workspace/.trees/github-streamline

# Task 13: Analytics
cd /workspace/.trees/analytics
```

## Tmux Window Layout

When using tmux, the session `v4.2.0-dev` has these windows:

| Window | Name | Directory |
|--------|------|-----------|
| 0 | Main | /workspace |
| 1 | Task-01-Claude | .trees/claude-refinement |
| 2 | Task-02-Content | .trees/marketing-content |
| 3 | Task-03-Testing | .trees/script-testing |
| 4 | Task-04-Templates | .trees/template-creation |
| 5 | Task-05-Docx | .trees/docx-verification |
| 6 | Task-06-Calendly | .trees/calendly |
| 7 | Task-07-Dashboard | .trees/dashboard-redesign |
| 8 | Task-08-DbViz | .trees/database-viz |
| 9 | Task-09-Gemini | .trees/gemini-prompts |
| 10 | Task-10-Librarian | .trees/librarian |
| 11 | Task-11-Email | .trees/email-refinement |
| 12 | Task-12-GitHub | .trees/github-streamline |
| 13 | Task-13-Analytics | .trees/analytics |

## Tmux Cheat Sheet

### Basic Commands
```bash
# List sessions
tmux ls

# Attach to session
tmux attach -t v4.2.0-dev

# Kill session (when done)
tmux kill-session -t v4.2.0-dev
```

### Inside Tmux
- **New window:** `Ctrl+b` then `c`
- **Switch window:** `Ctrl+b` then `0-9` or `n`/`p`
- **Rename window:** `Ctrl+b` then `,`
- **Split horizontal:** `Ctrl+b` then `%`
- **Split vertical:** `Ctrl+b` then `"`
- **Navigate panes:** `Ctrl+b` then arrow keys
- **Detach:** `Ctrl+b` then `d`

## Workflow Example

### Start Development Session
```bash
# 1. Open all terminals
./scripts/open-all-terminals.sh

# 2. Navigate to your task
# Press Ctrl+b then 1 (for Task 1)

# 3. Check branch status
git status
git branch --show-current  # Should show task/01-claude-refinement

# 4. Start working
# Make changes, commit, push
```

### End Development Session
```bash
# Detach from tmux (keeps it running)
# Press Ctrl+b then d

# Or kill session when completely done
tmux kill-session -t v4.2.0-dev
```

## VS Code Integration

**Files created:**
- `.vscode/terminals.json` - Terminal definitions (if supported by extension)
- `.vscode/tasks.json` - Run task to open all terminals
- `scripts/open-all-terminals.sh` - Tmux/screen launcher

## Troubleshooting

### Tmux not installed
```bash
# Ubuntu/Debian
sudo apt-get install tmux

# macOS
brew install tmux
```

### Session already exists
```bash
# Kill old session
tmux kill-session -t v4.2.0-dev

# Then recreate
./scripts/open-all-terminals.sh
```

### Wrong directory in terminal
```bash
# Check current directory
pwd

# Navigate to correct worktree
cd /workspace/.trees/<worktree-name>

# Verify branch
git branch --show-current
```

## Tips

1. **Color coding:** Each tmux window is color-coded for easy identification
2. **Persistent sessions:** Tmux survives SSH disconnections
3. **Screen alternative:** Script supports both tmux and screen
4. **VS Code tasks:** Use `Ctrl+Shift+P` → `Tasks: Run Task` for quick access
