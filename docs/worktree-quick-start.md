# Worktree Quick Start Guide

## 1. Stage and Build Worktrees

```bash
/tree stage Implement API rate limiting
/tree stage Add dashboard analytics
/tree build
```

## 2. Open Terminal for Each Worktree

For each worktree you want to work on:

1. **Open new terminal**: `Ctrl+Shift+`` (backtick)
2. **Navigate to worktree**: `cd /workspace/.trees/<worktree-name>`
3. **Launch Claude with context**: `bash /workspace/.claude/scripts/cltr.sh`

**Example:**
```bash
cd /workspace/.trees/implement-api-rate-limiting
bash /workspace/.claude/scripts/cltr.sh
```

Claude launches with task context pre-loaded and asks clarifying questions.

## 3. Complete Work

When finished:
```bash
/tree close
```

## 4. Merge All Completed Worktrees

```bash
/tree closedone
```

---

**Optional Alias** (makes it easier):
```bash
echo "alias cltr='bash /workspace/.claude/scripts/cltr.sh'" >> ~/.bashrc
```

Then just type `cltr` instead of the full path.
