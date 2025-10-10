# Agent Activity Log

**Purpose:** Track primary agent activities to identify opportunities for specialized sub-agent creation.

---

## How to Use This Log

**When to log:**
- After completing each parent task in TodoWrite
- When task complexity exceeds normal patterns
- When you notice repeated workflows
- End of significant work sessions

**What to track:**
- Tool usage patterns and frequencies
- Files and modules accessed
- Context switches between domains
- Decision points and trade-offs made

---

## Session Template

```markdown
## Session: [YYYY-MM-DD HH:MM]

**Task:** [Brief description]

**Context:**
- Workflow: [go/slow/analyze/research/communicate]
- Related PRD/Issue: [Link if applicable]

**Activity Summary:**
- **Tools Used:**
  - Read: X files
  - Edit: Y files
  - Write: Z files
  - Grep: N searches
  - Bash: M commands
  - Other: [List]

- **Files Touched:**
  - Primary modules: [e.g., modules/database/, docs/]
  - File types: [.py, .md, .mdc, etc.]
  - Scope: [Single file / Module / Cross-cutting]

- **Complexity Indicators:**
  - Total tool calls: X
  - File reads: Y
  - Context switches: Z (e.g., backend → frontend → docs)
  - Decision points: N

**Workflow Patterns Observed:**
- [Pattern 1: e.g., "Read schema → Generate model → Write tests"]
- [Pattern 2: e.g., "Search codebase → Analyze → Document findings"]
- [Pattern 3: e.g., "Research library → Compare options → Recommend"]

**Sub-Agent Opportunity Assessment:**

**Potential:** [High / Medium / Low / None]

**Reasoning:**
- Domain-specific expertise: [Yes/No - What domain?]
- Repeated workflow: [Yes/No - What pattern?]
- High context requirements: [Yes/No - What context?]
- Clear boundaries: [Yes/No - What are inputs/outputs?]
- Autonomous execution: [Yes/No - User interaction needed?]

**Candidate Sub-Agent:**
- Name: [e.g., "schema-generator", "api-documenter"]
- Purpose: [One-line description]
- Trigger: [When should this agent be used?]
- Tools needed: [List of tools]
- Context required: [What docs/files to load]

**Notes:**
[Any additional observations or insights]

---
```

## Example Entry

```markdown
## Session: 2025-10-09 06:30

**Task:** Reorganize workflow templates from /tasks to .claude/

**Context:**
- Workflow: Manual organization task
- Related PRD/Issue: claude-refinement worktree

**Activity Summary:**
- **Tools Used:**
  - Read: 12 files
  - Edit: 1 file (task.md - updated all references)
  - Write: 0 files
  - Bash: 8 commands (mkdir, mv operations)
  - Grep: 3 searches
  - TodoWrite: 8 updates

- **Files Touched:**
  - Primary modules: .claude/workflows/, .claude/templates/
  - File types: .mdc, .md
  - Scope: Cross-cutting (config reorganization)

- **Complexity Indicators:**
  - Total tool calls: ~35
  - File reads: 12
  - Context switches: 2 (reading templates → moving files → updating references)
  - Decision points: 3 (directory structure, naming, reference updates)

**Workflow Patterns Observed:**
1. Read multiple related files → Understand structure
2. Create new directory structure → Move files systematically
3. Update all references in dependent files → Verify completeness

**Sub-Agent Opportunity Assessment:**

**Potential:** Medium

**Reasoning:**
- Domain-specific expertise: No - This is general file organization
- Repeated workflow: Yes - File reorganization happens during refactoring
- High context requirements: No - Just needs to understand current structure
- Clear boundaries: Yes - Input: target structure, Output: reorganized files + updated refs
- Autonomous execution: Partial - Might need user approval on structure

**Candidate Sub-Agent:**
- Name: "file-organizer" or "refactor-organizer"
- Purpose: Systematically reorganize files and update all references
- Trigger: When refactoring file structure or consolidating scattered files
- Tools needed: Read, Glob, Grep, Bash (mv, mkdir), Edit
- Context required: Current directory structure, target structure

**Notes:**
This could be combined with the existing "librarian" agent concept from future-agent-ideas.md. Worth considering if this pattern repeats.

---
```

---

## Sub-Agent Evaluation Criteria

### What Makes a Good Sub-Agent Candidate?

Use these criteria to evaluate whether an activity pattern should become a sub-agent:

#### 1. **Domain-Specific Expertise** ⭐ High Priority
- Requires specialized knowledge of a particular system/module
- Benefits from deep context about specific domain
- Examples:
  - Database schema work (needs schema understanding)
  - API integration (needs API docs and patterns)
  - Testing (needs testing framework knowledge)
  - Security reviews (needs security expertise)

#### 2. **Repeated Workflow** ⭐ High Priority
- Same sequence of tools used multiple times
- Predictable pattern that could be automated
- Examples:
  - Read schema → Generate model → Create tests
  - Search codebase → Analyze → Document findings
  - Research library → Compare → Recommend → Document

#### 3. **High Context Requirements** ⭐ Medium Priority
- Needs specific documentation always loaded
- Requires understanding of particular subsystem
- Examples:
  - Needs database schema docs
  - Needs API documentation
  - Needs architecture diagrams
  - Needs specific coding standards

#### 4. **Clear Boundaries** ⭐ High Priority
- Well-defined inputs and outputs
- Scope is contained and predictable
- Examples:
  - Input: Schema changes → Output: Updated models + tests
  - Input: Feature description → Output: API documentation
  - Input: Code module → Output: Test suite

#### 5. **Autonomous Execution** ⭐ Medium Priority
- Can complete task without constant user input
- Makes reasonable decisions based on context
- Examples:
  - Generate documentation from code (autonomous)
  - Create standard CRUD endpoints (autonomous)
  - Format and organize files (autonomous)
  - vs. Architecture decisions (needs user input)

### Scoring Guide

**High Potential (Create Sub-Agent):**
- 4-5 criteria met
- At least 2 "High Priority" criteria
- Workflow repeats 3+ times

**Medium Potential (Consider for Future):**
- 2-3 criteria met
- At least 1 "High Priority" criterion
- Pattern observed 2+ times

**Low Potential (Not Worth Sub-Agent):**
- 0-1 criteria met
- One-off task
- Too much user interaction needed

---

## Current Sub-Agent Candidates

Track potential sub-agents identified through activity logging:

### 1. [Candidate Name]
- **Domain:** [e.g., Database Schema Management]
- **Trigger Pattern:** [When to use]
- **Criteria Met:** [List which of 5 criteria]
- **Frequency Observed:** [How many times seen]
- **Status:** [Proposed / In Development / Implemented]
- **Notes:** [Additional context]

---

## Existing Sub-Agents

Reference existing agents to avoid duplication:

### code-reviewer
- **Purpose:** Enforce CLAUDE.md standards, run automated tools (Black, Flake8, Vulture)
- **Trigger:** After code changes
- **Location:** `.claude/agents/code-reviewer.md`

### debugger
- **Purpose:** Systematic bug investigation through evidence gathering
- **Trigger:** Complex debugging tasks
- **Location:** `.claude/agents/debugger.md`

### workflow-admin
- **Purpose:** Workflow start/end setup, context preparation, GitHub staging
- **Trigger:** Beginning/end of development sessions
- **Location:** `.claude/agents/workflow-admin.md`

---

## Notes

**Remember:**
- Not every repeated task needs a sub-agent
- Sub-agents add complexity - only create when clear value
- Consider whether existing agents could be extended instead
- Document the decision rationale whether you create an agent or not
