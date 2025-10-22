---
title: Token Budget Management Guide
type: guide
created: 2025-10-21
modified: 2025-10-21
status: current
related: DOCUMENTATION_INDEX.md, .claude/templates/
---

# Token Budget Management Guide

**Version:** 1.0.0
**Last Updated:** 2025-10-21
**Audience:** Users invoking AI agents for autonomous work

---

## Table of Contents

1. [Overview](#overview)
2. [Why Token Budgets Matter](#why-token-budgets-matter)
3. [Setting Effective Budgets](#setting-effective-budgets)
4. [Budget Enforcement Strategies](#budget-enforcement-strategies)
5. [Instruction Templates](#instruction-templates)
6. [Common Pitfalls](#common-pitfalls)
7. [Case Studies](#case-studies)
8. [Best Practices](#best-practices)

---

## Overview

Token budgets control how much work an autonomous agent can perform before stopping. Without proper constraints, agents may:
- Exceed intended scope
- Create overly comprehensive documentation
- Spend tokens on nice-to-have features instead of essentials
- Deliver late with cost overruns

This guide provides proven strategies for keeping agents within budget while maximizing value delivered.

---

## Why Token Budgets Matter

### The Problem

**Example: Librarian Operations (2025-10-21)**
- **Budget:** 50,000 tokens
- **Actual:** 112,000 tokens (224% over budget)
- **Why:** No enforcement mechanisms

**What happened:**
- Agent created 1,185 lines of new documentation
- Comprehensive 600-line worktree guide
- Complete README rewrite (258 lines)
- Detailed 600+ line synopsis

**What was needed:**
- File organization (essential)
- Simple index (essential)
- Brief synopsis (essential)

### The Impact

**Budget overruns cause:**
1. **Cost surprises** - API usage costs exceed expectations
2. **Time delays** - Takes longer than planned
3. **Scope creep** - Agent does more than needed
4. **Opportunity cost** - Tokens spent on documentation instead of features

**With proper budgets:**
1. **Predictable costs** - Know what you'll spend
2. **Focused work** - Agent does essentials first
3. **Clear tradeoffs** - Understand what fits in budget
4. **User control** - Decide when to expand scope

---

## Setting Effective Budgets

### Budget Sizing Framework

**Task complexity guidelines:**

| Task Type | Token Range | Example |
|-----------|-------------|---------|
| Trivial | 1k - 5k | Rename files, update version numbers |
| Simple | 5k - 15k | Organize files, create simple index |
| Medium | 15k - 30k | Implement small feature, write tests |
| Complex | 30k - 75k | Implement feature + tests + docs |
| Large | 75k - 150k | Multiple features, comprehensive work |

**Librarian operations sizing:**
- File organization only: 10k - 15k tokens
- Organization + simple index: 15k - 25k tokens
- Organization + comprehensive docs: 50k - 100k tokens

### Budget Allocation Method

**Break down by subtask:**

```
Total Budget: 50,000 tokens

Allocation:
- Survey & planning:        5,000 tokens  (10%)
- File organization:       15,000 tokens  (30%)
- Documentation index:     10,000 tokens  (20%)
- Update existing files:   10,000 tokens  (20%)
- Synopsis & reporting:     5,000 tokens  (10%)
- Buffer (20%):             5,000 tokens  (10%)
```

**Why this works:**
- Forces prioritization of subtasks
- Identifies if scope fits in budget
- Allows graceful degradation (skip low-priority items)
- Buffer handles unexpected complexity

### Progressive Budget Pattern

**For uncertain scope:**

```
Phase 1 (15k tokens): Survey and organize files
→ Report results, ask to continue

Phase 2 (15k tokens): Create documentation index
→ Report results, ask to continue

Phase 3 (15k tokens): Update README and CLAUDE.md
→ Report results, ask to continue

Phase 4 (5k tokens): Create synopsis
→ Deliver final results
```

**Benefits:**
- User maintains control at each phase
- Can stop early if satisfied
- Can redirect if priorities change
- Never exceeds total budget

---

## Budget Enforcement Strategies

### Strategy 1: Hard Token Limits ⭐⭐⭐⭐⭐

**Most effective for preventing overruns**

```markdown
Token budget: 50,000 HARD LIMIT

ENFORCEMENT:
- Check token usage after every major operation
- At 45,000 tokens: STOP all work immediately
- Create brief synopsis (bullet points, max 50 lines)
- Report final token usage
- Do NOT exceed 50,000 tokens under any circumstances
```

**Why it works:**
- Clear, measurable threshold
- Automatic enforcement
- Leaves buffer for synopsis
- No ambiguity

**Implementation:**
```markdown
SYSTEM RULE:
After completing each subtask:
1. Estimate tokens used so far
2. If >45k tokens used: STOP and wrap up
3. If >40k tokens used: Report "Approaching limit (40k/50k)"
4. If <40k tokens: Continue to next task
```

### Strategy 2: Checkpoint Reporting ⭐⭐⭐⭐

**Good for maintaining user control**

```markdown
Token budget: 50,000 tokens

CHECKPOINTS:
Every 10,000 tokens used:
1. STOP work
2. Report: "Token usage: [X]/50,000"
3. Summarize: "Completed: [list of tasks]"
4. Ask: "Continue with next phase?"
5. Wait for user approval

Do not proceed without explicit "continue" from user.
```

**Why it works:**
- User can redirect if going off-track
- Early warning of budget issues
- Allows scope adjustment mid-stream
- Prevents silent overruns

**Example output:**
```
Token usage: 20,000/50,000 (40%)

Completed:
✓ Organized 32 documentation files
✓ Created directory structure (6 categories)
✓ Moved files to appropriate locations

Next phase: Create documentation index (estimated 10k tokens)
Continue? (yes/no)
```

### Strategy 3: Output Size Constraints ⭐⭐⭐⭐

**Good for preventing scope creep**

```markdown
Token budget: 50,000 tokens

OUTPUT LIMITS:
- Any single new file: 150 lines maximum
- Total new documentation: 300 lines maximum
- Synopsis: Bullet-point format, 50 lines maximum
- Edits to existing files: Minimal changes only

PROHIBITION:
Do NOT create comprehensive guides, detailed walkthroughs,
or multi-section documentation unless explicitly requested.
```

**Why it works:**
- Prevents over-engineering documentation
- Forces concise communication
- Reserves tokens for actual work
- Easy to measure compliance

**Token savings:**
- 600-line guide → 150-line guide = ~15k tokens saved
- 600-line synopsis → 50-line synopsis = ~20k tokens saved
- Total savings: ~35k tokens

### Strategy 4: Scope Definition ⭐⭐⭐⭐⭐

**Most important for setting expectations**

```markdown
SCOPE (what to do):
- Organize loose documentation files into logical structure
- Create simple documentation index (bullet list format)
- Update CLAUDE.md version number
- Brief synopsis (executive summary, <100 lines)

OUT OF SCOPE (what NOT to do):
- Do NOT create comprehensive new guides
- Do NOT rewrite existing files
- Do NOT create detailed walkthroughs
- Do NOT expand beyond file organization

APPROVAL REQUIRED:
- Any new file >100 lines
- Rewriting any existing file
- Adding tasks not listed in scope
```

**Why it works:**
- Crystal clear boundaries
- Explicitly lists prohibited actions
- Requires approval for expansions
- Prevents interpretation drift

### Strategy 5: Approval Gates ⭐⭐⭐

**Good for high-value operations**

```markdown
APPROVAL REQUIRED BEFORE:
1. Creating any new file >100 lines
   → Stop, describe proposed file, estimate tokens, wait for approval

2. Rewriting any existing file
   → Stop, explain why rewrite needed vs edit, wait for approval

3. Expanding scope beyond original instructions
   → Stop, describe proposed expansion, wait for approval

PROCESS:
- Stop work immediately when gate encountered
- Describe what you want to do
- Estimate token cost
- Wait for explicit "approved" from user
- If no approval, skip and continue with original scope
```

**Why it works:**
- User controls high-token operations
- Prevents expensive surprises
- Allows informed decisions
- Maintains original scope by default

### Strategy 6: Template-Based Output ⭐⭐⭐

**Good for reducing token usage**

```markdown
DOCUMENTATION FORMAT:
Use templates and stubs instead of comprehensive docs.

Synopsis template (saves 40k tokens):
---
## Synopsis
**Tokens:** [used]/[budget]
**Status:** [complete/incomplete]

### Completed
- [Task 1]: [brief description]
- [Task 2]: [brief description]

### Delivered
- [File 1]: [purpose]
- [File 2]: [purpose]

### Issues
[None or brief list]
---

Index template (saves 10k tokens):
---
## Documentation Index
- **Category 1**
  - [File 1]: [one-line description]
  - [File 2]: [one-line description]
- **Category 2**
  - [File 3]: [one-line description]
---
```

**Why it works:**
- Provides structure without verbose prose
- Forces conciseness
- Covers essential information
- Reduces token usage by 70-80%

---

## Instruction Templates

### Template 1: File Organization (Minimal)

```markdown
Task: Organize documentation files

Token budget: 15,000 HARD LIMIT
Check usage every 5k tokens and report.
STOP at 14k tokens to deliver synopsis.

SCOPE:
- Move loose .md files from root to appropriate docs/ subdirectories
- Create directory structure: implementation/, reports/, testing/, etc.
- Create simple index (bullet list, max 100 lines)

OUTPUT:
- Brief synopsis (bullet points, max 50 lines)

PROHIBITIONS:
- Do NOT create new comprehensive documentation
- Do NOT rewrite existing files
- Do NOT create files >100 lines

STOP CONDITIONS:
- At 14k tokens: Stop and deliver synopsis
- When scope complete: Stop and deliver synopsis
```

**Expected result:**
- Files organized (essential)
- Simple index (navigable)
- Brief report
- 10k-15k tokens used

### Template 2: Documentation with Checkpoints

```markdown
Task: [description]

Token budget: 50,000 tokens

CHECKPOINT REPORTING:
Every 10,000 tokens:
1. STOP work
2. Report token usage: "[X]/50,000"
3. List completed tasks
4. Ask: "Continue?"
5. Wait for user response

PHASES:
Phase 1 (10k): [specific task]
Phase 2 (15k): [specific task]
Phase 3 (15k): [specific task]
Phase 4 (10k): [specific task]

HARD STOP: 50,000 tokens (no exceptions)

At 45k tokens: Begin wrapping up, create synopsis
```

**Expected result:**
- User maintains control
- Can redirect between phases
- Never exceeds budget
- Clear progress visibility

### Template 3: Comprehensive Work with Controls

```markdown
Task: [description]

Token budget: 75,000 tokens

ALLOCATION:
- Phase 1 (15k): [task]
- Phase 2 (25k): [task]
- Phase 3 (20k): [task]
- Synopsis (10k): Report
- Buffer (5k): Unexpected issues

OUTPUT LIMITS:
- New files: 200 lines maximum each
- Total new documentation: 500 lines maximum
- Synopsis: Executive summary format, 150 lines max

APPROVAL GATES:
Before creating files >150 lines:
- Stop and describe proposed file
- Estimate token cost
- Wait for approval

ENFORCEMENT:
- Check tokens after each phase
- Report usage at phase boundaries
- STOP at 70k tokens to deliver synopsis
```

**Expected result:**
- Comprehensive work within budget
- User approves large expenditures
- Prioritized deliverables
- Controlled scope

### Template 4: Minimal Viable (Strict)

```markdown
Task: [description]

Token budget: 25,000 HARD LIMIT

SCOPE:
[Single clearly defined task]

CONSTRAINTS:
- Create NO new files >50 lines
- Edit existing files minimally
- Use bullet-point format for all outputs
- Link to existing docs instead of duplicating

SYNOPSIS:
Deliver as bullet list (20 lines max):
- Completed: [list]
- Files modified: [list]
- Issues: [list]

STOP at 23k tokens.
```

**Expected result:**
- Absolute minimum viable work
- Maximum efficiency
- Guaranteed under budget
- Quick turnaround

---

## Common Pitfalls

### Pitfall 1: Vague Instructions

❌ **Bad:**
```
"Perform 50,000 tokens worth of work"
```

**Why it fails:**
- Agent interprets "worth" subjectively
- No clear scope boundaries
- No enforcement mechanism
- Leads to comprehensive over-delivery

✅ **Good:**
```
"Organize documentation files. Budget: 50k tokens.
Stop at 45k to deliver synopsis. Do NOT create new
comprehensive documentation."
```

### Pitfall 2: No Enforcement

❌ **Bad:**
```
"Token budget: 50,000 tokens. Try to stay within budget."
```

**Why it fails:**
- "Try" is not enforceable
- No consequences for exceeding
- Agent prioritizes completeness over budget
- No checkpoints or stops

✅ **Good:**
```
"Token budget: 50,000 HARD LIMIT.
Check usage every 10k tokens.
STOP at 45k tokens regardless of completion status.
Report final usage."
```

### Pitfall 3: Scope Ambiguity

❌ **Bad:**
```
"Organize documentation and improve it where needed."
```

**Why it fails:**
- "Improve" is unlimited scope
- "Where needed" is subjective
- Agent will create comprehensive improvements
- No boundaries

✅ **Good:**
```
"Organize documentation files into logical structure.
Do NOT create new documentation.
Do NOT rewrite existing files.
Create simple index only (bullet list)."
```

### Pitfall 4: Output Size Not Specified

❌ **Bad:**
```
"Create a synopsis of the work done."
```

**Why it fails:**
- No length constraint
- Agent creates comprehensive report
- Can consume 20k-40k tokens
- Leaves no budget for actual work

✅ **Good:**
```
"Create synopsis: Bullet-point format, 50 lines maximum.
Include: completed tasks, files modified, issues encountered."
```

### Pitfall 5: No Progressive Disclosure

❌ **Bad:**
```
"Organize files, create documentation, update README,
write guides. Budget: 50k tokens."
```

**Why it fails:**
- All tasks equal priority
- Agent may spend all tokens on first task
- No user control over execution
- Can't redirect mid-stream

✅ **Good:**
```
"Phase 1 (15k): Organize files, report status, ask to continue.
Phase 2 (15k): Create index, report status, ask to continue.
Phase 3 (15k): Update README, report status, ask to continue.
Phase 4 (5k): Synopsis."
```

### Pitfall 6: Assuming Self-Monitoring

❌ **Bad:**
```
"Keep track of your token usage and stay within 50k."
```

**Why it fails:**
- Agents don't automatically track tokens
- No explicit checkpoints
- No stop conditions
- Relies on agent self-awareness

✅ **Good:**
```
"After each major operation:
1. Estimate tokens used
2. Report: 'Tokens: [X]/50,000'
3. If >45k: STOP and wrap up
4. If >40k: Report approaching limit"
```

---

## Case Studies

### Case Study 1: Librarian Operations

**Original Instructions:**
```
"Use the librarian agent to begin librarian operations.
Perform 50,000 tokens worth of work, max, then stop.
Create a synopsis of work done and report issues."
```

**What Happened:**
- 112,000 tokens used (224% over budget)
- Created comprehensive 600-line guides
- Rewrote README completely
- Detailed 600+ line synopsis

**Problems:**
1. ❌ "Worth of work" too vague
2. ❌ No enforcement mechanism
3. ❌ No output size limits
4. ❌ No scope definition
5. ❌ No checkpoints

**What Should Have Been:**
```
Task: Organize documentation files

Token budget: 50,000 HARD LIMIT
Check tokens every 10k, report usage.
STOP at 45k tokens.

SCOPE:
- Move loose .md files to docs/ subdirectories
- Create simple index (bullet list, 100 lines max)
- Update CLAUDE.md version number only

OUT OF SCOPE:
- Do NOT create comprehensive guides
- Do NOT rewrite existing files
- Do NOT create documentation >100 lines

SYNOPSIS:
Bullet-point format, 50 lines maximum:
- Files organized: [count]
- Index created: [yes/no]
- Issues: [none/list]

ENFORCEMENT:
At 45k tokens: STOP immediately, deliver synopsis
```

**Expected Result with Corrected Instructions:**
- 15k tokens: File organization
- 10k tokens: Simple index
- 5k tokens: CLAUDE.md update
- 5k tokens: Brief synopsis
- 15k tokens: Buffer
- **Total: 50k tokens (budget met)**

### Case Study 2: Feature Implementation (Success)

**Instructions:**
```
Task: Implement user authentication feature

Token budget: 75,000 tokens

ALLOCATION:
- Phase 1 (20k): Research & design
  → Stop, report findings, ask to continue
- Phase 2 (30k): Implementation
  → Stop, report progress, ask to continue
- Phase 3 (15k): Tests
  → Stop, report results, ask to continue
- Phase 4 (10k): Documentation & synopsis

APPROVAL GATES:
- Before implementing: Show design, get approval
- Before major refactors: Explain, get approval

OUTPUT LIMITS:
- New files: 300 lines max each
- Documentation: 200 lines max
- Synopsis: 100 lines max

STOP at 72k tokens.
```

**Result:**
- Phase 1: 18k tokens (research & design approved)
- Phase 2: 28k tokens (implementation completed)
- Phase 3: 14k tokens (tests passing)
- Phase 4: 9k tokens (docs & synopsis)
- **Total: 69k tokens (under budget)**

**Why It Worked:**
1. ✅ Clear phase boundaries
2. ✅ User approval at gates
3. ✅ Token allocation by phase
4. ✅ Output size limits
5. ✅ Hard stop condition

---

## Best Practices

### 1. Start Conservative

**First time working with agent:**
- Set budget 50% higher than estimated
- Use checkpoint reporting every 10k tokens
- Add approval gates for >100 line files
- Learn agent's token usage patterns

**Once calibrated:**
- Tighten budget to actual usage
- Reduce checkpoint frequency
- Remove unnecessary gates

### 2. Allocate by Priority

**High priority (60% of budget):**
- Core functionality
- Essential documentation
- Critical fixes

**Medium priority (30% of budget):**
- Nice-to-have features
- Additional documentation
- Refactoring

**Low priority (10% buffer):**
- Polish
- Extra examples
- Unexpected complexity

**If budget tight:** Cut low priority items first.

### 3. Use Templates for Repetitive Tasks

**Create organization-specific templates:**

```markdown
# Template: File Organization Task

Token budget: [X] HARD LIMIT
Stop at [X-5k] to deliver synopsis.

SCOPE:
- Organize files in [directory]
- Create index in [location]
- [Specific task 3]

PROHIBITIONS:
- No new files >100 lines
- No comprehensive documentation
- No rewrites

SYNOPSIS: Bullet format, 50 lines max
```

**Save templates in:** `.claude/templates/task-budgets/`

**Benefits:**
- Consistent enforcement
- Proven patterns
- Easy to reuse
- Faster task setup

### 4. Review and Adjust

**After each agent task:**
1. Compare estimated vs actual tokens
2. Identify where overruns occurred
3. Update budget allocation
4. Tighten constraints if needed

**Maintain log:**
```
Task: File organization
Estimated: 15k tokens
Actual: 22k tokens
Reason: Created comprehensive index instead of simple
Fix: Add "simple bullet list, max 100 lines" to next instruction
```

### 5. Progressive Scope Expansion

**Instead of:**
```
"Implement feature X with tests and documentation. 75k tokens."
```

**Use:**
```
Phase 1 (25k): Implement core feature
→ If under budget and working: Continue to Phase 2
Phase 2 (25k): Add tests
→ If under budget and passing: Continue to Phase 3
Phase 3 (25k): Add documentation
```

**Benefits:**
- Delivers working feature even if budget tight
- Prioritizes functionality over documentation
- User can stop at any phase
- Graceful degradation

### 6. Separate Research from Implementation

**Research tasks (lower budget):**
```
Task: Research authentication approaches
Budget: 15k tokens

DELIVERABLE:
- 3 approaches evaluated
- Pros/cons for each
- Recommendation
- Bullet format, 100 lines max
```

**Implementation tasks (higher budget):**
```
Task: Implement [approved approach] from research
Budget: 60k tokens

REFERENCE: research-authentication.md
DELIVERABLE:
- Working implementation
- Tests
- Basic documentation
```

**Why separate:**
- Research cheaper than implementation
- Can change direction after research
- Doesn't waste implementation budget on wrong approach

### 7. Use Token Tracking Comments

**In long tasks, agent should comment progress:**

```
# After organizing files (15k tokens used)
# Creating index (25k tokens used)
# Updating CLAUDE.md (30k tokens used)
# Creating synopsis (35k tokens used)
```

**Benefits:**
- Visibility into token spending
- Can identify inefficiencies
- Helps calibrate future estimates

---

## Quick Reference

### Essential Budget Elements Checklist

Every agent task should have:

- [ ] **Explicit budget number** (e.g., "50,000 tokens")
- [ ] **Hard stop condition** (e.g., "STOP at 45k")
- [ ] **Scope definition** (what to do)
- [ ] **Out-of-scope list** (what NOT to do)
- [ ] **Output size limits** (e.g., "max 100 lines per file")
- [ ] **Synopsis format** (e.g., "bullet points, 50 lines")
- [ ] **Checkpoint frequency** (e.g., "report every 10k")

### Token Budget by Task Type

| Task | Recommended Budget | Notes |
|------|-------------------|-------|
| File organization | 10k - 20k | Simple, mechanical |
| Simple documentation | 15k - 30k | Index, summaries |
| Small feature | 30k - 50k | Single module |
| Medium feature | 50k - 100k | Multiple modules |
| Large feature | 100k - 200k | System-wide changes |
| Comprehensive docs | 40k - 80k | Multiple guides |
| Research | 10k - 30k | Investigation only |
| Refactoring | 40k - 100k | Depends on scope |

### Enforcement Strength Comparison

| Strategy | Effectiveness | Complexity | User Burden |
|----------|---------------|------------|-------------|
| Hard limit at X tokens | ⭐⭐⭐⭐⭐ | Low | Low |
| Checkpoint every Xk | ⭐⭐⭐⭐ | Low | Medium |
| Output size limits | ⭐⭐⭐⭐ | Low | Low |
| Scope definition | ⭐⭐⭐⭐⭐ | Medium | Low |
| Approval gates | ⭐⭐⭐ | Medium | High |
| Templates | ⭐⭐⭐ | Medium | Low |

**Recommended combination:**
- Hard limit (essential)
- Scope definition (essential)
- Output size limits (highly recommended)
- Checkpoints OR approval gates (choose one)

---

## Appendix: Example Instructions

### Example A: Minimal File Organization

```markdown
Task: Organize documentation files

Token budget: 15,000 HARD LIMIT
STOP at 14,000 tokens.

SCOPE:
1. Move loose .md files from root to docs/ subdirectories
2. Create simple index: bullet list of files by category

PROHIBITIONS:
- No new files >50 lines
- No comprehensive documentation
- No file rewrites

DELIVERABLE:
Synopsis (bullet format, 30 lines):
- Files moved: [count]
- Categories: [list]
- Index location: [path]
```

### Example B: Feature with Tests

```markdown
Task: Implement email validation feature

Token budget: 50,000 tokens
Check usage every 15k, report progress.

PHASES:
1. (15k) Implementation
   - Add validation function
   - Integrate with existing code
   - Report status → continue?

2. (15k) Tests
   - Unit tests for validator
   - Integration tests
   - Report test results → continue?

3. (10k) Documentation
   - Update relevant docs
   - Add code comments
   - Report completion → continue?

4. (10k) Synopsis & wrap-up

LIMITS:
- New files: 200 lines max
- Docs: 150 lines max
- Synopsis: 100 lines max

STOP at 48k tokens.
```

### Example C: Research Task

```markdown
Task: Research caching strategies for job scraping

Token budget: 20,000 tokens
STOP at 18,000 tokens.

DELIVERABLE:
Report (markdown, 200 lines max):

## Approaches Evaluated
- [Approach 1]: [summary]
- [Approach 2]: [summary]
- [Approach 3]: [summary]

## Comparison
[Table comparing approaches]

## Recommendation
[Which to use and why - 50 words]

## Implementation Estimate
[Token estimate for chosen approach]

FORMAT: Bullet lists and tables, minimal prose.
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial release based on librarian operations analysis |

---

**Related Documentation:**
- [Worktree Complete Guide](worktrees/WORKTREE_COMPLETE_GUIDE.md)
- [Documentation Index](DOCUMENTATION_INDEX.md)
- [Task Workflow Templates](../.claude/templates/)

**Feedback:** If you discover additional effective patterns, update this guide.
