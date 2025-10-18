# Claude Code Hooks

This directory contains hooks that execute at specific events during Claude Code sessions.

## Hook Architecture

### Main Hook: `user-prompt-submit.sh`
- **Event**: UserPromptSubmit (runs when user submits a prompt)
- **Purpose**: Orchestrates validation checks through modular hook components
- **Flow**: Reads JSON input → Calls modules → Combines responses → Outputs JSON

### Hook Modules

#### 1. Communication Guidance (`modules/communication_guidance.sh`)
**Purpose**: Detect question patterns and enforce analysis-first behavior

**Triggers on**:
- Question words: what, how, why, which, should, "can you explain"
- Recommendation requests: recommend, suggestion, options, best practice
- Evaluation requests: trade-off, pros and cons, compare, assess

**Response**: Reminds agent to provide analysis only, ask for permission before implementation

#### 2. Implementation Guidance (`modules/implementation_guidance.sh`)
**Purpose**: Detect workflow patterns and remind agent of proper procedures

**Triggers on**:
- **Git operations**: commit, push, merge, pull request
  - Reminds: Use git-orchestrator agent via Task tool
- **Database schema changes**: schema, alter table, add column
  - Reminds: Use database_tools/update_schema.py workflow

**Response**: Project-specific workflow reminders from CLAUDE.md

## Adding New Hook Modules

1. Create new module in `modules/` directory:
```bash
#!/bin/bash
set -euo pipefail

# Read hook input
HOOK_INPUT=$(cat)
USER_PROMPT=$(echo "$HOOK_INPUT" | jq -r '.userPrompt // ""')

# Your detection logic here
if [[ condition ]]; then
    echo "Your guidance message"
else
    echo ""
fi
```

2. Make executable: `chmod +x modules/your_module.sh`

3. Add call in `user-prompt-submit.sh`:
```bash
if [[ -f "$HOOKS_DIR/modules/your_module.sh" ]]; then
    YOUR_GUIDANCE=$(echo "$HOOK_INPUT" | "$HOOKS_DIR/modules/your_module.sh")
fi
```

4. Combine into output message

## Hook Input Format

Hooks receive JSON via stdin:
```json
{
  "userPrompt": "User's message text",
  "cwd": "/workspace/path",
  "conversationId": "uuid",
  "messageId": "uuid"
}
```

## Hook Output Format

Hooks output JSON to stdout:
```json
{
  "hookSpecificOutput": {
    "message": "Guidance text shown to agent"
  }
}
```

Or empty JSON if no guidance needed:
```json
{}
```

## Testing Hooks

Test individual modules:
```bash
echo '{"userPrompt":"How do we implement this?"}' | .claude/hooks/modules/communication_guidance.sh
```

Test full hook:
```bash
echo '{"userPrompt":"Please commit these changes"}' | .claude/hooks/user-prompt-submit.sh
```

## Design Principles

1. **Modular**: Each concern is a separate module
2. **Composable**: Main hook combines module outputs
3. **Non-blocking**: Hooks provide guidance, don't prevent actions
4. **Clear messaging**: Output explains WHY guidance is given
5. **Project-aligned**: Enforces patterns from CLAUDE.md

## Current Hooks

- `user-prompt-submit.sh` - Main orchestrator hook
- `modules/communication_guidance.sh` - Question detection
- `modules/implementation_guidance.sh` - Workflow reminders
- `post_python_edit.py` - Syntax validation after Python edits

## Future Extensions

Potential additional modules:
- File protection (block changes to specific files/lines)
- Security pattern detection
- Documentation requirement checks
- Test coverage reminders
- Performance pattern validation
