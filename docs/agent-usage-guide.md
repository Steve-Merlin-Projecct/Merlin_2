# Agent Usage Guide
Last Updated: October 6, 2025

## Overview
This guide documents when and how to use specialized agents in Claude Code, including decision criteria, performance patterns, and lessons learned from real-world usage.

## Available Specialized Agents

### 1. General-Purpose Agent
**Capabilities:** Complex research, code searches, multi-step autonomous tasks
**Tools Available:** All tools (Read, Write, Edit, Grep, Glob, Bash, etc.)

**Use When:**
- Performing open-ended searches requiring multiple rounds of grep/glob
- Researching complex questions across many files
- Not confident you'll find the right match in first few tries
- Task requires autonomous decision-making and iteration

**Avoid When:**
- Reading specific known file paths
- Searching for specific class definitions (use Glob instead)
- Searching within 2-3 specific files (use Read instead)
- Simple, direct tasks with clear execution path

### 2. Workflow-Admin Agent
**Capabilities:** Session management, context preparation, GitHub operations
**Tools Available:** Glob, Grep, Read, NotebookEdit, SlashCommand

**Use When:**
- **Session Start:** Beginning development work that needs CLAUDE.md context loaded
- **Session End:** Completing work, updating docs, staging GitHub changes
- **Context Preparation:** Verifying CLAUDE.md instructions are active
- **Task Setup:** Loading task templates from `/tasks` directory
- **GitHub Staging:** Preparing changes for commit

**Avoid When:**
- Already in middle of active development session
- Just doing quick file edits or reviews
- CLAUDE.md context already loaded and active

### 3. Statusline-Setup Agent
**Capabilities:** Configure Claude Code status line settings
**Tools Available:** Read, Edit

**Use When:**
- User requests status line customization
- Need to configure status line display format

### 4. Output-Style-Setup Agent
**Capabilities:** Create and configure Claude Code output styles
**Tools Available:** Read, Write, Edit, Glob, Grep

**Use When:**
- User requests custom output formatting
- Need to create new output style templates

### 5. Git-Orchestrator Agent
**Capabilities:** Autonomous git operations management (checkpoints, section commits, validation, error recovery)
**Tools Available:** Bash, Read, Grep, Glob
**Model:** Haiku (fast, efficient for structured operations)

**Use When:**
- **After completing 3+ sub-tasks** in a section (checkpoint)
- **After completing all section tasks** (section commit)
- **End of work session** (save progress)
- **Before switching sections** (preserve work)

**Avoid When:**
- No uncommitted changes exist
- Just starting work (nothing to commit yet)
- Making quick file edits without task context

**Integration:**
- **Invoked by primary agent** with context (section name, summary, files changed)
- **Autonomous validation:** Tests, schema automation, documentation checks
- **Structured responses:** JSON format for programmatic handling
- **Error recovery:** Creates checkpoint fallback when commit fails

**Invocation Patterns:**
```
checkpoint_check:Section Name
commit_section:Full Section Name
```

**Response Handling:**
- **"success":** Continue to next task/section
- **"failed":** Surface blocking issues to user
- **"skipped":** No action needed, continue

**See:** [Primary Agent Git Integration Guide](../workflows/primary-agent-git-integration.md)

---

### 6. Debugger Agent
**Capabilities:** Systematic bug analysis through evidence gathering (investigation only, NO fixes)
**Tools Available:** All tools (Read, Write, Edit, Grep, Glob, Bash, etc.)
**Model:** Opus (for deep analytical thinking)

**Use When:**
- Complex bugs with unclear root cause requiring systematic investigation
- Memory issues (corruption, segfaults, leaks)
- Concurrency problems (race conditions, deadlocks)
- Performance bottlenecks needing detailed profiling
- Logic errors requiring state transition analysis
- Bug requires extensive evidence collection before diagnosis

**Avoid When:**
- Bug is obvious and can be fixed directly
- Simple syntax errors or typos
- Well-understood issues with known solutions
- User wants immediate fix (debugger only analyzes, doesn't implement)

**Critical Protocols:**
- **TodoWrite Required:** Every debug modification MUST be tracked
- **Cleanup Mandatory:** ALL debug statements and test files MUST be removed before final report
- **Evidence-First:** Minimum 10+ debug statements before forming hypotheses
- **No Implementation:** Provides analysis and fix strategy only, never implements fixes

**Debug Statement Format:**
```python
print("[DEBUGGER:module.function:line] variable_name=value")
```

**Test File Naming:**
```
test_debug_<issue>_<timestamp>.ext
```

**Final Deliverable:**
- Root cause (one sentence)
- Evidence (key debug output)
- Fix strategy (high-level approach)
- Confirmation all debug code removed

## Decision Framework

### Question to Ask: "Can I complete this task directly with 1-3 tool calls?"
- **YES** → Use direct tools
- **NO** → Consider if agent would add value

### Question to Ask: "Will this require iterative searching/exploration?"
- **YES** → General-purpose agent likely helpful
- **NO** → Use direct tools

### Question to Ask: "Am I starting/ending a development session?"
- **YES** → Use workflow-admin agent
- **NO** → Continue with current approach

### Question to Ask: "Is this a complex bug requiring systematic investigation?"
- **YES** → Consider debugger agent for evidence-based analysis
- **NO** → Fix directly or use general-purpose agent

### Question to Ask: "Have I completed 3+ tasks or a full section?"
- **YES** → Use git-orchestrator for checkpoint/section commit
- **NO** → Continue working on tasks

## Performance Patterns

### Agent Advantages
- **Autonomous iteration:** Can refine searches without user back-and-forth
- **Token efficiency:** Exploratory work happens in agent context, not main conversation
- **Parallel execution:** Multiple agents can run simultaneously on independent tasks
- **Complex decision trees:** Agent can make autonomous choices during research

### Agent Disadvantages
- **Latency overhead:** Launching agent + waiting for completion adds time
- **Reduced visibility:** User doesn't see intermediate search steps
- **Communication barrier:** Agent can't ask clarifying questions mid-task
- **Overkill risk:** Simple tasks become slower with agent overhead

## Real-World Examples

### Example 1: SSH Script Review (Direct Approach Chosen)
**Task:** Review setup_ssh.sh file for Replit relevance
**Approach:** Direct Read + Glob tools
**Reasoning:**
- Known file type (shell script)
- Single file review
- Straightforward analysis
**Result:** 2 tool calls, ~900 tokens, immediate results
**Agent Alternative:** Would add unnecessary overhead for simple task

### Example 2: Replit Cleanup Project (Workflow-Admin Appropriate)
**Task:** "Start working on cleaning up Replit-specific code"
**Approach:** Workflow-admin agent to begin session
**Reasoning:**
- Major development session starting
- Needs CLAUDE.md context loaded
- Should verify task templates available
- Will involve GitHub staging when complete
**Expected Benefit:** Proper context preparation prevents errors later

### Example 3: Finding All Database References (General-Purpose Appropriate)
**Task:** "Find all files that reference the old database connection method"
**Approach:** General-purpose agent for exploration
**Reasoning:**
- Don't know exact search patterns needed
- May need multiple rounds of grep with different patterns
- Might need to follow references across files
- Uncertain scope (could be 5 files or 50)
**Expected Benefit:** Agent can iterate autonomously without multiple user prompts

### Example 4: Intermittent Database Connection Failures (Debugger Agent Appropriate)
**Task:** "The application randomly loses database connection after 2-3 hours of runtime"
**Approach:** Debugger agent for systematic investigation
**Reasoning:**
- Intermittent issue with unclear root cause
- Could be connection pooling, timeout settings, or resource leaks
- Needs evidence collection across time periods
- Requires tracking connection lifecycle and state transitions
- Multiple hypotheses need systematic elimination
**Expected Benefit:** Evidence-based diagnosis prevents guessing and implementing wrong fixes
**Agent Process:**
1. Adds debug statements to connection pool manager, timeout handlers, cleanup routines
2. Creates isolated test file to reproduce connection lifecycle
3. Runs application with debug logging over extended period
4. Analyzes patterns in connection failures
5. Delivers root cause + fix strategy (e.g., "Connection pool exhaustion due to missing close() calls in error paths")
6. Removes all debug code before final report

## Teachable Moments Log

### Session: October 6, 2025

#### Moment 1: SSH Script Review
**Context:** User asked to review setup_ssh.sh for Replit migration relevance
**Decision:** Used direct Read/Glob tools
**Lesson:** Simple file reviews don't benefit from agent overhead. Direct tools provide faster, more transparent results.
**Metrics:** 2 tool calls, immediate completion, clear reasoning visible to user

---

## Guidelines for Documenting New Insights

When adding new teachable moments or patterns, include:

1. **Context:** What was the task/request?
2. **Decision:** Which approach was chosen (agent vs. direct)?
3. **Reasoning:** Why was that choice optimal?
4. **Metrics:** Tool calls, tokens used, time considerations
5. **Alternative:** What would the other approach have looked like?
6. **Lesson:** What principle or pattern does this illustrate?

## Best Practices

1. **Default to direct tools** for straightforward tasks
2. **Use workflow-admin proactively** at session boundaries
3. **Delegate to general-purpose** when exploration scope is uncertain
4. **Use debugger agent** for complex bugs requiring evidence-based diagnosis
5. **Run agents in parallel** when tasks are independent
6. **Communicate agent usage** to user with clear reasoning
7. **Document patterns** that emerge from real usage
8. **Update this guide** as new insights emerge

## Debugger Agent Best Practices

When using the debugger agent:
- **Clear bug description:** Provide symptoms, frequency, and any error messages
- **Reproduction steps:** Share how to trigger the issue if known
- **Environment context:** Mention runtime environment, data volumes, concurrent users
- **Accept analysis-only output:** Remember the agent won't implement fixes
- **Verify cleanup:** Ensure all debug code is removed before merging
- **Follow-up implementation:** After receiving root cause + fix strategy, implement the fix separately

## Questions for Consideration

- Is the task scope well-defined or exploratory?
- How many tool calls would direct approach require?
- Does the task benefit from autonomous iteration?
- Is this a session boundary (start/end)?
- Would parallel agent execution provide value?
- Is transparency more important than efficiency for this task?