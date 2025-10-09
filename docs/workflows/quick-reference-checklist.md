---
title: Quick Reference Checklist for Agents
created: '2025-10-07'
updated: '2025-10-07'
author: Steve-Merlin-Projecct
type: guide
status: active
tags:
- workflow
- quick
- reference
- checklist
---

# Quick Reference Checklist for Agents
**Version:** 1.0
**Date:** October 6, 2025

## 🎯 Before Starting ANY Work

```
[ ] Is this a TASK or a QUESTION?
    └─ Task indicators: "Create", "Build", "Fix", "Implement", "Add"
    └─ Question indicators: "How", "What", "Why", "Can you explain"

    IF QUESTION → Provide analysis only, ask if they want implementation
    IF TASK → Proceed with 3-phase workflow below
```

---

## 📋 PHASE 1: PRD Creation

```
[ ] Acknowledge: "I've detected this as a task request"
[ ] Create directory: /tasks/[feature-name]/
[ ] Ask clarifying questions (use lettered/numbered lists)
[ ] Wait for user responses
[ ] Generate PRD using template
[ ] Save to: /tasks/[feature-name]/prd.md
[ ] Ask: "Would you like me to proceed with Phase 2: Task Generation?"
[ ] Wait for approval
```

**PRD Must Include:**
- [ ] Overview (problem statement, solution, success criteria)
- [ ] Goals (specific, measurable)
- [ ] User Stories (with acceptance criteria)
- [ ] Functional Requirements (numbered: FR1, FR2, etc.)
- [ ] Non-Goals (scope boundaries)
- [ ] Technical Considerations (architecture, dependencies, security)
- [ ] Success Metrics (quantitative and qualitative)

---

## 📝 PHASE 2: Task Generation

```
[ ] Announce: "Phase 2: Task Generation"
[ ] Read PRD from: /tasks/[feature-name]/prd.md
[ ] Create 4-7 parent tasks
[ ] ⚠️  ALWAYS include Documentation parent task (REQUIRED)
[ ] Break each parent into 3-8 sub-tasks
[ ] Identify all relevant files (implementation + tests)
[ ] Create TodoWrite entries for all tasks (status: pending)
[ ] Save to: /tasks/[feature-name]/tasklist_1.md
[ ] Ask: "Would you like me to proceed with Phase 3: Task Execution?"
[ ] Wait for approval
```

**Standard Parent Tasks:**
1. Setup & Configuration
2. Core Implementation
3. User Interface (if applicable)
4. Integration (if applicable)
5. Testing
6. **Documentation (REQUIRED)**
7. Deployment & Validation (if applicable)

**Documentation Parent Task Must Include:**
- [ ] 5.1 Add inline documentation to all new files
- [ ] 5.2 Create component documentation in /docs/component_docs/[module]/
- [ ] 5.3 Document data flow and integration points
- [ ] 5.4 Add API documentation (if applicable)
- [ ] 5.5 Update related documentation
- [ ] 5.6 Archive outdated documentation
- [ ] 5.7 Update master changelog

---

## ⚙️ PHASE 3: Task Execution

### For Each Sub-Task:

```
[ ] Mark as in_progress in TodoWrite (ONLY ONE at a time)
[ ] Update markdown file (optional visual indicator)
[ ] Execute the work:
    [ ] Write code following project standards
    [ ] Add comprehensive inline documentation
    [ ] Implement error handling
[ ] Mark as completed in TodoWrite IMMEDIATELY
[ ] Update markdown file with [x]
[ ] Check: Are all sub-tasks in parent done?
    └─ NO → Move to next sub-task
    └─ YES → Proceed to Parent Task Completion below
```

### Section Completion (Use Automated Scripts):

**After 3+ tasks (Checkpoint):**
```
[ ] Stage changes: git add .
[ ] Run checkpoint script:
    ./scripts/checkpoint.sh "Section Name" "Completed tasks 1.1-1.3"
[ ] Script automatically: tests → schema automation → checkpoint commit
```

**After ALL tasks in section (Section Commit):**
```
[ ] Stage changes: git add .
[ ] Run section commit script:
    ./scripts/commit-section.sh "Section Name" "feat|fix|docs" "/tasks/feature/prd.md"

[ ] Script automatically handles:
    [ ] Runs full test suite (FAILS if tests fail)
    [ ] Runs database schema automation (if needed)
    [ ] Verifies documentation exists (FAILS if missing)
    [ ] Cleans up temporary files
    [ ] Generates conventional commit message
    [ ] Creates commit
    [ ] Updates version in CLAUDE.md
    [ ] Generates changelog template

[ ] Agent responds to script prompts:
    [ ] Confirm commit creation (y)
    [ ] Open changelog for editing (y)
    [ ] Update changelog with provided template

[ ] Mark section as completed in TodoWrite
[ ] Mark section as completed in markdown [x]

[ ] Move to next section
```

**Scripts are at:** `/workspace/.trees/task-guiding-docs/scripts/`

See [Automatic Checkpoints & Commits Guide](./automatic-checkpoints-commits.md)

---

## 🔄 TodoWrite Synchronization

**CRITICAL RULES:**
```
[ ] ONLY ONE task can be "in_progress" at a time
[ ] Update TodoWrite IMMEDIATELY when status changes (no batching)
[ ] Every TodoWrite entry needs:
    - content: "Imperative form" (e.g., "Create user model")
    - activeForm: "Present continuous" (e.g., "Creating user model")
    - status: "pending" | "in_progress" | "completed"
```

**Sync with Markdown:**
```
When starting a task:
  TodoWrite: status = "in_progress"
  Markdown: - [→] or note "← Currently working"

When completing a task:
  TodoWrite: status = "completed"
  Markdown: - [x]
```

**If Out of Sync:**
```
[ ] Review markdown file to see actual state
[ ] Update TodoWrite to match reality
[ ] Going forward: update BOTH immediately, always
```

---

## 📚 Documentation Checklist

### Inline Documentation (Every File):
```
[ ] File-level docstring (purpose, components, dependencies, related docs)
[ ] Class docstrings (purpose, attributes, usage example, related files)
[ ] Function docstrings:
    [ ] Description
    [ ] Args (type and description)
    [ ] Returns (type and description)
    [ ] Raises (exceptions)
    [ ] Examples
    [ ] Related functions
    [ ] Data processed
[ ] Inline comments for complex logic (explain "why", not "what")
```

### Component Documentation (New Features):
```
[ ] Create: /docs/component_docs/[module]/[feature].md
[ ] Include sections:
    [ ] Overview (purpose, key functionality)
    [ ] Architecture (dependencies, system context)
    [ ] Implementation Files (core files, tests, config)
    [ ] Data Flow (input → processing → output)
    [ ] Database Interactions (tables, queries)
    [ ] API Endpoints (if applicable)
    [ ] Configuration (env vars, settings)
    [ ] Error Handling
    [ ] Security Considerations
    [ ] Performance
    [ ] Testing (coverage, running tests)
    [ ] Usage Examples
    [ ] Troubleshooting
    [ ] Related Documentation
```

---

## 🗄️ Database Schema Changes

**ALWAYS use automation tools:**
```
[ ] Make schema changes to PostgreSQL database
[ ] Run: python database_tools/update_schema.py
[ ] Verify generated files updated:
    - frontend_templates/database_schema.html
    - docs/component_docs/database/*.md
    - database_tools/generated/*.py
[ ] Stage ALL generated files: git add .
[ ] Commit with schema changes

NEVER:
  ❌ Manually edit generated files
  ❌ Skip running automation
```

---

## ⚠️ Common Mistakes to Avoid

```
❌ Implementing code without creating PRD first
❌ Skipping task list generation
❌ Having multiple tasks "in_progress" in TodoWrite
❌ Batching TodoWrite updates instead of immediate
❌ Forgetting to include Documentation parent task
❌ Committing without running tests
❌ Not updating changelog after parent task
❌ Manually editing database schema documentation
❌ Forgetting to archive outdated documentation
❌ Not adding inline documentation to new code
❌ Skipping component documentation for new features
```

---

## 🎓 Questions to Ask Yourself

**Before starting work:**
- [ ] Is this a task or a question?
- [ ] Do I have a PRD?
- [ ] Do I have a task list with Documentation included?
- [ ] Is the user ready for me to start implementing?

**During work:**
- [ ] Do I have exactly ONE task in_progress in TodoWrite?
- [ ] Am I updating both TodoWrite and markdown immediately?
- [ ] Am I adding comprehensive inline documentation?
- [ ] Am I following the project's coding standards?

**Before committing:**
- [ ] Did all tests pass?
- [ ] Did I create/update component documentation?
- [ ] Did I archive any outdated documentation?
- [ ] Did I update the master changelog?
- [ ] Did I update the version number?
- [ ] Is my commit message in conventional format?

**After completing full feature:**
- [ ] Is all documentation complete and accurate?
- [ ] Are all tasks marked completed in TodoWrite?
- [ ] Is the changelog updated?
- [ ] Are all tests passing?

---

## 📞 Quick Links

- [Full Workflow Guide](./automated-task-workflow.md)
- [PRD Template](./prd-generation-guide.md)
- [Task Generation Guide](./task-generation-guide.md)
- [Task Execution Guide](./task-execution-guide.md)
- [Documentation Requirements](./documentation-requirements.md)

---

**Remember:** When in doubt, follow the detailed guides. This checklist is a quick reminder, not a replacement for the full documentation.
