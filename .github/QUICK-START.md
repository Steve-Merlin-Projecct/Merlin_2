# Quick Start: Create New Project

## One Command Setup

```bash
./.github/scripts/create-dev-project.sh <project-name> <language> <project-path>
```

## Examples

### JavaScript Project
```bash
./.github/scripts/create-dev-project.sh my-app javascript ~/projects/my-app
```

### Python Project
```bash
./.github/scripts/create-dev-project.sh my-app python ~/projects/my-app
```

### TypeScript Project
```bash
./.github/scripts/create-dev-project.sh my-app typescript ~/projects/my-app
```

## What Happens

1. ✅ Creates project structure
2. ✅ Generates devcontainer configuration  
3. ✅ Allocates unique port (5100, 5200, 5300...)
4. ✅ Creates VS Code workspace
5. ✅ Initializes git repository
6. ✅ Opens in VS Code
7. ✅ Click "Reopen in Container"
8. ✅ Container builds automatically
9. ✅ Dependencies install automatically
10. ✅ Claude Code CLI launches automatically

## Next Steps

After running the command:
1. **Click "Reopen in Container"** when VS Code prompts
2. **Wait for build** (first time takes 2-5 minutes)
3. **Start coding** - everything is ready!

## Port Allocation

- **Merlin:** 5000 (existing)
- **Your Project:** 5100 (auto-assigned)
- **Next Project:** 5200 (auto-assigned)
- **And so on...**

## Full Documentation

- **Complete Guide:** [docker-devcontainer-setup-guide.md](docker-devcontainer-setup-guide.md)
- **Detailed Usage:** [PROJECT-CREATOR-README.md](PROJECT-CREATOR-README.md)
