# Manual Worktree Terminal Workflow

## Why Manual Terminals?

Manual terminal creation offers several advantages over automatic terminal generation:

1. **Precise Control**: You decide exactly when and where to open terminals
2. **Flexibility**: Adapt to changing development contexts
3. **Performance**: Reduces overhead of automatic terminal creation
4. **Predictability**: Terminals are created exactly when you want them
5. **Learning**: Understand the underlying workflow better

## Terminal Workflow Steps

### Step 1: Navigate to Worktree
```bash
cd /workspace/.trees/your-worktree-name
```

### Step 2: Open Terminal
```bash
bash .claude-init.sh
```
This initializes the terminal with:
- Automatic task context loading
- Quick Command Reference
- Claude pre-configured for the specific task

### Step 3: Use `/cltr` Command
After the terminal opens, use the `/cltr` command to:
- Load detailed task context
- Prompt Claude for clarifying questions
- Prepare for implementation

### Example Workflow

```bash
# Change to your worktree
cd /workspace/.trees/add-job-analytics-feature

# Open terminal
bash .claude-init.sh

# Inside terminal, launch Claude with context
/cltr
```

## Best Practices

1. **One Terminal per Worktree**: Focus on a single task at a time
2. **Update Context Regularly**: Keep `.claude-task-context.md` current
3. **Use Slash Commands**: Leverage `/tree` commands for workflow management

## Troubleshooting

- **Terminal Doesn't Open**: Check `.claude-init.sh` permissions
- **Claude Not Found**: Install Claude CLI or update PATH
- **No Context File**: The script offers to create a template

## Advanced Usage

### Multiple Terminals
You can open multiple terminals for the same worktree:
```bash
# Terminal 1: Development
cd /workspace/.trees/add-job-analytics-feature
bash .claude-init.sh

# Terminal 2: Testing
cd /workspace/.trees/add-job-analytics-feature
bash .claude-init.sh
```

## Comparison with Automatic Method

### Automatic (VS Code Tasks)
- Generates all 17 terminals on window reload
- Uses `.vscode/tasks.json`
- Configured in `.devcontainer/devcontainer.json`

### Manual Method
- Open terminals as needed
- Full control over terminal creation
- More predictable, less overhead

## Recommended Workflow

1. Stage features with `/tree stage`
2. Build worktrees with `/tree build`
3. Manually open terminals as tasks require
4. Use `/cltr` to load context
5. Implement and track progress

---

**Pro Tip**: The manual method teaches you the underlying process and gives you more granular control over your development environment.
