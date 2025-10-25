---
title: "Worktree Quick Start"
type: technical_doc
component: general
status: draft
tags: []
---

# Worktree Quick Start Guide

## 1. Stage and Build Worktrees

```bash
/tree stage [description]
/tree stage [description]
/tree build
```

## 2. Open Terminal for Each Worktree

For each worktree you want to work on:

1. **Open new terminal**: `Ctrl+Shift+`` (backtick)
2. **Navigate to worktree**: `cd /workspace/.trees/<worktree-name>`
3. **Launch Claude with context**: `cltr`

**Example:**
```bash
cd /workspace/.trees/implement-api-rate-limiting
cltr
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
