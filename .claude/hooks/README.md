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

### Active Hooks
- `user-prompt-submit-unified.sh` - Main behavioral guidance orchestrator (UserPromptSubmit event)
- `session-start.sh` - Worktree context injection (SessionStart event)
- `pre-tool-use-file-protection.py` - Blocks Edit/Write to protected files (PreToolUse event)
- `post_python_edit.py` - Syntax validation after Python edits (PostToolUse event)

### Hook Modules
- `modules/behavioral_guidance.sh` - Unified behavioral rules (analysis vs implementation)
- `modules/communication_guidance.sh` - Question detection patterns
- `modules/implementation_guidance.sh` - Implementation workflow reminders
- `modules/workflow_reminders.sh` - Optional git/database workflow nudges
- `modules/estimation_guidance.sh` - Token-based estimation enforcement

## Worktree Context Injection

The `session-start.sh` hook automatically detects when Claude Code starts inside a git worktree and injects the task context.

**How it works:**
1. Detects if CWD is inside `/workspace/.trees/*/`
2. Reads `.claude-task-context.md` (created by `/tree build`)
3. Reads `PURPOSE.md` for additional context
4. Injects full context as a system message on session start
5. Provides worktree-specific commands (/tree close, /tree status, etc.)

**Benefits:**
- Agent immediately knows the focused task
- No manual context loading needed
- Enforces worktree isolation and focus
- Only activates in worktrees (silent in main workspace)

**Testing:**
```bash
# Inside worktree - shows context
cd /workspace/.trees/my-feature
.claude/hooks/session-start.sh

# Outside worktree - returns {}
cd /workspace
.claude/hooks/session-start.sh
```

## Token-Based Estimation

The `estimation_guidance.sh` module enforces token-based work estimates instead of time-based estimates.

**Triggers on:**
- "how long", "how much time", "estimate", "duration"
- "timeline", "timeframe", "effort", "scope"
- Any estimation-related keywords

**Enforces:**
- ✓ Estimate ONLY in Claude Sonnet 4.5 tokens
- ✓ Provide ranges (e.g., "40k-60k tokens")
- ✓ Wide estimates acceptable
- ✗ NO time-based estimates (hours, days, weeks)

**Example:**
```bash
User: "How long will this feature take?"
Hook: "📊 ESTIMATION GUIDANCE ACTIVATED
       Estimate ONLY in Claude Sonnet 4.5 tokens..."
Agent: "This feature will require approximately 50,000-75,000 tokens to complete."
```

**Testing:**
```bash
echo '{"userPrompt":"How long will this take?"}' | ./.claude/hooks/modules/estimation_guidance.sh
```

## File Protection System (PreToolUse)

The `pre-tool-use-file-protection.py` hook **blocks Edit/Write operations** on protected hook files BEFORE they execute.

**Hook Event:** PreToolUse (runs before tool executes)
**Protected Files:**
- `.claude/hooks/user-prompt-submit-unified.sh` (main orchestrator)
- All modules in `.claude/hooks/modules/`

**How It Works:**
1. Agent attempts to use Edit or Write tool on a file
2. PreToolUse hook intercepts the operation
3. Hook checks if file is in protected list
4. If protected: **Blocks operation** with exit code 1
5. If not protected: Allows operation (exit code 0)

**Example:**
```python
# Agent tries: Edit(.claude/hooks/behavioral_guidance.sh)
# Hook blocks with:
{
  "hookSpecificOutput": {
    "message": "🚫 FILE PROTECTION: Edit Blocked\n\nPROTECTED FILE: .claude/hooks/modules/behavioral_guidance.sh\n\n❌ OPERATION BLOCKED"
  },
  "shouldProceed": false
}
# Exit code: 1 (prevents Edit from executing)
```

**Why Protected:**
Hook files control agent behavior and must remain stable. Modifications could:
- Break the hook orchestration system
- Create inconsistent agent guidance
- Introduce security vulnerabilities

**Extending Protection:**
To protect additional files, add them to the `PROTECTED_FILES` list in `pre-tool-use-file-protection.py`.

**Testing:**
```bash
./test_pre_tool_use_protection.sh
```

**Benefits over UserPromptSubmit approach:**
- ✅ Blocks at tool execution level (not just prompt detection)
- ✅ Catches all edit attempts (even if user didn't explicitly request)
- ✅ True prevention (not just a warning)
- ✅ Works regardless of how agent decides to edit

## Future Extensions

Potential additional modules:
- Line-level protection (block changes to specific line ranges)
- Security pattern detection
- Test coverage reminders
- Performance pattern validation
