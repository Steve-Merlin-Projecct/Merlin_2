---
title: "Claude Code Notes"
type: technical_doc
component: general
status: draft
tags: []
---

# Claude Code in Devcontainers

## Auto-Update Warning (Expected Behavior)

If you see this warning in the Claude Code status bar:
```
✗ Auto-update failed · Try claude doctor or npm i -g @anthropic-ai/claude-code
```

**This is expected and can be safely ignored.**

### Why This Happens

Claude Code attempts to auto-update itself, but in devcontainer environments:
- The CLI is installed in `/usr/lib/node_modules/` with root ownership
- The `vscode` user doesn't have write permissions to update global npm packages
- This is by design for security and container isolation

### What This Means

- ✅ Claude Code is working perfectly
- ✅ All features are fully functional
- ✅ You can continue working normally
- ⚠️ Auto-updates are disabled (expected in containers)

### How to Update Claude Code

When you need to update Claude Code, rebuild your devcontainer:

1. Press `Cmd/Ctrl + Shift + P`
2. Select "Dev Containers: Rebuild Container"
3. The latest version will be installed during rebuild

Or manually update the version in `.devcontainer/devcontainer.json`:

```json
"postCreateCommand": "npm install -g @anthropic-ai/claude-code@latest"
```

### Alternative: Suppress the Warning

The warning appears in Claude Code's built-in UI and cannot be disabled through configuration. However, it's purely informational and doesn't affect functionality.

## Container Detection

The statusline script automatically detects when running in a container by checking:
- `/.dockerenv` file (Docker)
- `/run/.containerenv` file (Podman)
- `$REMOTE_CONTAINERS` environment variable (VS Code)
- `$CODESPACES` environment variable (GitHub Codespaces)

This ensures the statusline displays appropriate information for your environment.
