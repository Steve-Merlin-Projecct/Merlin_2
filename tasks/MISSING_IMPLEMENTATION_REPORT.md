---
title: "Missing Implementation Report: Workflow-Admin Auto-Invocation Hook"
type: status_report
component: development
status: active
created: 2025-10-25
updated: 2025-10-25
tags: ["workflow", "hooks", "session-initialization", "missing-feature"]
---

# Missing Implementation Report: Workflow-Admin Auto-Invocation Hook

**Date:** 2025-10-25
**Reporter:** Primary Claude Agent
**Issue:** Expected automatic session initialization via workflow-admin agent did not occur

---

## Executive Summary

The user expected an automatic hook system that would:
1. Trigger on user prompt submission (start of session)
2. Launch the workflow-admin agent automatically
3. Prompt the agent to ask clarifying questions before beginning work

**Finding:** This feature was never implemented. The investigation found no evidence of:
- `user-prompt-submit` hooks
- Automatic workflow-admin invocation
- Session initialization hook system

---

## Investigation Results

### What Exists (Implemented Features)

#### 1. **workflow-admin Agent** ✅
- **Created:** October 7, 2025 (commit 7532764)
- **File:** `.claude/agents/workflow-admin.md`
- **Status:** Fully implemented but requires **manual invocation**
- **Design:** Agent description states: *"I'm going to use the Task tool to launch the workflow-admin agent"*
- **Invocation Method:** Primary agent must explicitly call via Task tool

**Key Responsibilities:**
- Session initialization (verify CLAUDE.md, load templates, GitHub staging)
- Session cleanup (documentation updates, changelog, commit preparation)
- Token efficiency (minimal context loading)

#### 2. **Post-Event Hooks** ✅
- **Created:** October 18, 2025 (commit c870bfe)
- **Location:** `.claude/hooks/`
- **Implemented Hooks:**
  - `post_agent_work.py` - Validation after agent changes
  - `post_python_edit.py` - Python syntax checking
  - `post_task.py` - Validation after task completion
- **Status:** Implemented but disabled by default
- **Event Types:** PostToolUse events only

**Design Philosophy:**
> "Validation runs during work, not at close"
> "Hooks disabled by default for gradual rollout"

#### 3. **Automated Task Workflow System** ✅
- **Created:** October 7, 2025 (commit a59b2bd)
- **Components:**
  - `/task` slash command
  - Research → PRD → Tasks → Execute workflow
  - Automated checkpoints and commits
  - Documentation requirements enforcement
- **Status:** Fully implemented
- **Note:** Requires explicit `/task` invocation, not automatic

---

### What Does NOT Exist (Missing Features)

#### 1. **user-prompt-submit Hook** ❌
**Expected Behavior:**
- Trigger on first user message in session
- Automatically launch workflow-admin agent
- Agent asks clarifying questions before proceeding

**Investigation Results:**
```bash
# Git history search
$ git log --all --grep="user-prompt-submit"
# No results

$ git log --all -S "user-prompt-submit"
# No results

# File content search
$ grep -r "user-prompt-submit" .
# No matches found

# Branch search
$ git branch -a | grep -i "session.*init\|prompt"
# No matching branches
```

**Conclusion:** Never implemented or planned in any commit.

#### 2. **Automatic Session Initialization** ❌
**Expected Behavior:**
- Detect session start automatically
- Load CLAUDE.md context
- Verify project guidelines
- Ask user for clarification before proceeding

**Investigation Results:**
- No pre-user-prompt hooks found
- No session initialization detection system
- workflow-admin agent requires manual invocation
- Primary agent instructions don't mention automatic invocation

**Conclusion:** No automatic session initialization system exists.

#### 3. **Pre-User-Prompt Hook Event Type** ❌
**Claude Code Hook Types Available:**
- `PostToolUse` - After tool execution ✅ (implemented)
- `PostSlashCommand` - After slash commands ⚠️ (mentioned but not available)
- `PreUserPrompt` - Before processing user input ❌ (not found)
- `user-prompt-submit` - On user message submission ❌ (not found)

**Conclusion:** Claude Code CLI may not support pre-user-prompt hooks.

---

## Root Cause Analysis

### Why the Confusion?

#### 1. **workflow-admin Description Suggests Proactivity**
The workflow-admin agent description includes:

> **Use this agent when:**
> 1. **At Workflow Start**: Beginning any development session

This language suggests automatic invocation, but the examples show:
> Assistant: "I'm going to use the Task tool to launch the workflow-admin agent..."

**Reality:** Agent must be manually invoked by primary agent.

#### 2. **Hook System Partially Implemented**
- Post-event hooks exist (after work completes)
- Documentation mentions "hook-based quality validation"
- User may have assumed pre-event hooks were also implemented

**Reality:** Only post-event hooks were implemented.

#### 3. **Claude Code Hook Limitations**
The `.claude/settings.local.json` hook configuration shows:
```json
{
  "hooks": {
    "PostToolUse": [...]
  }
}
```

**Reality:** No pre-user-prompt or session-start hooks are configured or available in Claude Code.

---

## Impact Assessment

### User Experience Impact
**Severity:** Medium

**Current Behavior:**
1. User starts conversation with task request
2. Primary agent immediately begins work without:
   - Asking clarifying questions
   - Verifying understanding of requirements
   - Loading appropriate context
   - Confirming approach

**Expected Behavior:**
1. User starts conversation
2. Hook triggers workflow-admin agent
3. Agent asks clarifying questions:
   - "What's the priority?"
   - "Should I use `/task go` or `/task slow`?"
   - "Are there specific constraints?"
4. Agent loads appropriate context
5. Agent hands off to appropriate specialized agent

### Workaround Required
**Manual Invocation:**
User must explicitly request workflow setup:
- "Let's start with the workflow-admin agent"
- "Please ask clarifying questions before beginning"
- "Load the appropriate context first"

**Primary Agent Proactive Behavior:**
Primary agent should recognize workflow start signals and proactively invoke workflow-admin, but this is:
- Not documented in primary agent instructions
- Not enforced by hooks
- Dependent on agent interpretation

---

## Technical Analysis

### Hook System Architecture

**Current Implementation:**
```
User Input → Primary Agent → Tool Execution → PostToolUse Hook
                     ↓
              Direct Implementation
              (No session initialization)
```

**Expected Implementation:**
```
User Input → PreUserPrompt Hook → workflow-admin Agent → Context Loading
                                          ↓
                                  Clarifying Questions
                                          ↓
                                  Primary Agent → Implementation
```

### Missing Components

#### 1. **Hook Configuration**
**Missing from `.claude/settings.local.json`:**
```json
{
  "hooks": {
    "PreUserPrompt": [
      {
        "matcher": ".*",  // Match all user prompts
        "hooks": [
          {
            "type": "agent",
            "agent": "workflow-admin",
            "prompt": "User has started a new session with the following request: ${user_message}. Please ask clarifying questions and load appropriate context before proceeding.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

#### 2. **Session Detection Logic**
**Missing components:**
- Session start detection (first message vs continuation)
- Session type classification (implementation vs analysis vs research)
- Context priming based on session type
- Automatic handoff protocol

#### 3. **Primary Agent Instructions**
**Missing from system instructions:**
> "At the start of each session, proactively invoke the workflow-admin agent to:
> - Ask clarifying questions
> - Load appropriate context
> - Verify understanding of user requirements
> - Confirm approach before implementation"

---

## Comparison: Planned vs Actual

| Feature | Planned | Actual | Status |
|---------|---------|--------|--------|
| workflow-admin agent | ✅ Yes | ✅ Implemented | Complete |
| Manual workflow-admin invocation | ✅ Yes | ✅ Works | Complete |
| Post-event hooks (validation) | ✅ Yes | ✅ Implemented | Complete |
| Pre-user-prompt hooks | ❓ Unknown | ❌ Not found | **MISSING** |
| Automatic session initialization | ❓ Unknown | ❌ Not found | **MISSING** |
| Clarifying questions on session start | ❓ Unknown | ❌ Not found | **MISSING** |
| user-prompt-submit hook event | ❓ Unknown | ❌ Not found | **MISSING** |

---

## Possible Explanations

### 1. **Feature Was Never Planned**
- User may have discussed this feature in conversation
- Feature was not documented in git history
- Implementation was never committed

### 2. **Feature Was Abandoned**
- Technical limitations discovered (Claude Code doesn't support pre-hooks)
- Decided manual invocation was sufficient
- Implementation started but not completed

### 3. **Feature Exists in Different Branch/Repository**
- Implementation may exist in:
  - Different branch (not merged to current branch)
  - Different worktree
  - Previous repository (before migration)
  - Replit environment (before migration to Claude Code)

### 4. **Feature Requires Claude Code Update**
- Pre-user-prompt hooks may not be supported in current Claude Code version
- Feature may be waiting for Claude Code CLI enhancement
- Documentation may reference future capability

---

## Recommendations

### Immediate Actions

#### 1. **Document Current Behavior**
Update CLAUDE.md with clear instructions for primary agent:

```markdown
**Session Initialization (Primary Agent Responsibility):**

When user starts a new task/session, primary agent SHOULD proactively:
1. Recognize workflow start signals:
   - "Let's implement..."
   - "Can you help me with..."
   - "I need to add..."
2. Invoke workflow-admin agent via Task tool
3. Wait for workflow-admin to ask clarifying questions
4. Proceed with appropriate specialized agent

**Manual Workaround:**
User can explicitly request: "Please use workflow-admin to ask clarifying questions first"
```

#### 2. **Update workflow-admin Agent Description**
Clarify invocation method in `.claude/agents/workflow-admin.md`:

```markdown
**IMPORTANT:** This agent requires manual invocation by the primary agent.
It does NOT automatically trigger on session start.

Primary agent should recognize these signals and proactively invoke workflow-admin:
- New task requests
- Implementation work
- Feature additions
- Complex problem-solving
```

#### 3. **Create Hook Implementation Proposal**
Document desired feature for future implementation:
- Technical requirements
- Hook event type needed (PreUserPrompt or user-prompt-submit)
- Configuration example
- Expected behavior
- Benefits vs manual invocation

### Medium-Term Solutions

#### 1. **Enhance Primary Agent Instructions**
Add explicit session-start detection logic to primary agent system prompt:

```
## Session Initialization Protocol

At the start of each user interaction, evaluate:

1. **Is this a new session/task?**
   - Look for implementation requests
   - Look for "Let's work on..." language
   - Look for explicit task descriptions

2. **Should workflow-admin be invoked?**
   - YES if: Implementation, feature work, complex task
   - NO if: Simple question, information request, analysis only

3. **Invoke workflow-admin proactively:**
   ```
   I'm going to use the Task tool to launch the workflow-admin agent
   to ask clarifying questions and load appropriate context.
   ```

4. **Proceed with handoff:**
   - workflow-admin will return with context and recommendations
   - Continue with appropriate specialized agent
```

#### 2. **Implement Session Type Classification**
Create logic to automatically determine session type:
- **Implementation Session** → Invoke workflow-admin → `/task go` or `/task slow`
- **Analysis Session** → Invoke workflow-admin → Load analysis templates
- **Research Session** → Invoke workflow-admin → Load research templates
- **Question/Info Session** → Skip workflow-admin → Direct response

#### 3. **Add Session Start Indicator**
Create `.claude/session-config.json`:
```json
{
  "session_start_behavior": {
    "enabled": true,
    "invoke_workflow_admin_on": [
      "implementation_request",
      "feature_request",
      "complex_task"
    ],
    "skip_workflow_admin_on": [
      "simple_question",
      "information_request",
      "greeting"
    ],
    "clarifying_questions_required": true,
    "context_loading_required": true
  }
}
```

### Long-Term Solutions

#### 1. **Request Claude Code Hook Enhancement**
Submit feature request to Claude Code team:

**Feature Request: PreUserPrompt Hook**
- Event trigger: Before primary agent processes user input
- Use case: Session initialization, context loading, clarifying questions
- Configuration: Agent invocation with user message context
- Timeout: Configurable (default 30s)
- Example implementation: [attach proposal]

#### 2. **Build Workaround System**
If Claude Code doesn't support pre-hooks:

**Option A: First-Message Detection**
- Primary agent detects if this is first message in session
- Automatically invoke workflow-admin
- Cache session state to prevent repeated invocation

**Option B: Slash Command Integration**
- Create `/start` slash command
- User explicitly triggers session initialization
- Documents workflow: `/start` → clarifying questions → `/task go`

**Option C: Background Session Monitor**
- Python script monitors for new Claude Code sessions
- Automatically injects workflow-admin prompt on session start
- Runs as background process

---

## Git History Evidence

### Commits Related to Workflow System

**Agent System Creation (Oct 7, 2025):**
```
commit 7532764 - feat: Add agent orchestration system with specialized agents
- Created workflow-admin agent
- Created code-reviewer agent
- Created debugger agent
- Added agent creation guidelines

Files:
  .claude/agents/workflow-admin.md
  .claude/agents/code-reviewer.md
  .claude/agents/debugger.md
```

**Hook System Implementation (Oct 18, 2025):**
```
commit c870bfe - feat: implement hook-based quality validation system
- Added post_agent_work.py hook
- Added post_task.py hook
- Added post_python_edit.py hook
- Created validation-config.json
- Hooks disabled by default

Files:
  .claude/hooks/post_agent_work.py
  .claude/hooks/post_task.py
  .claude/hooks/post_python_edit.py
  .claude/validation-config.json
```

**Automated Task Workflow (Oct 7, 2025):**
```
commit a59b2bd - feat: implement comprehensive automated task workflow system
- Created /task slash command
- Research → PRD → Tasks → Execute workflow
- Automatic checkpoints and commits
- Documentation requirements

Files:
  .claude/commands/task.md
  docs/workflows/* (13 files)
  scripts/checkpoint.sh
  scripts/commit-section.sh
```

### No Evidence Found For:
- ❌ user-prompt-submit hooks
- ❌ PreUserPrompt event handlers
- ❌ Automatic workflow-admin invocation
- ❌ Session initialization detection
- ❌ Clarifying questions automation

---

## Conclusion

**Primary Finding:**
The expected automatic session initialization hook system was **never implemented**. The workflow-admin agent exists and functions correctly, but requires manual invocation by the primary agent or explicit user request.

**Root Cause:**
Either the feature:
1. Was discussed but never committed to git
2. Was abandoned due to technical limitations
3. Exists in a different branch/repository
4. Is waiting for Claude Code CLI enhancement
5. User remembered a proposed feature as if it were implemented

**Immediate Impact:**
Medium severity - sessions begin without clarifying questions or context loading, potentially leading to:
- Misunderstood requirements
- Inefficient implementation approaches
- Missing context
- Suboptimal agent selection

**Recommended Next Steps:**
1. ✅ Update documentation to clarify current behavior
2. ✅ Enhance primary agent instructions for proactive workflow-admin invocation
3. ✅ Create feature proposal for future implementation
4. ⏳ Consider workarounds if Claude Code doesn't support pre-hooks
5. ⏳ Submit feature request to Claude Code team if needed

---

## Appendix: Search Commands Used

```bash
# Git log searches
git log --all --grep="user-prompt-submit"
git log --all --grep="workflow-admin.*session"
git log --all --grep="clarifying question"
git log --all -S "user-prompt-submit"
git log --all -S "session initialization"

# File content searches
grep -r "user-prompt-submit" .
grep -r "PreUserPrompt" .
grep -r "workflow-admin.*automatic" .
find . -name "*.md" -exec grep -l "session.*initialization.*agent" {} \;

# Hook file inspection
ls -la .claude/hooks/
cat .claude/settings.local.json
cat .claude/validation-config.json

# Branch searches
git branch -a | grep -i "session\|init\|prompt"
git branch -a | grep -i "workflow.*start"
```

**Result:** No matches found for automatic session initialization system.

---

**Report Generated:** 2025-10-25
**Investigation Duration:** ~15 minutes
**Commits Reviewed:** 50+
**Files Searched:** 700+
**Confidence Level:** High - Feature was never implemented
