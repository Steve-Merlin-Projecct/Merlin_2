---
description: Start the 3-phase task workflow (PRD → Tasks → Execution)
---

You are about to begin the Automated Task Workflow for implementing a new feature or solving a problem.

**Your task:** {{TASK_DESCRIPTION}}

---

## Phase 0: Research (Automatic)

Follow the [Research Phase Guide](/workspace/.trees/task-guiding-docs/docs/workflows/research-phase-guide.md).

**Steps:**
1. Determine research depth (Level 1/2/3 based on task complexity)
2. Execute time-boxed research (2/5/15 minutes max)
3. Document findings in `/tasks/[feature-name]/research.md` (or `/tasks/research-[timestamp].md` if name unclear)
4. Present **Options A/B/C** based on findings
5. Wait for user to select approach
6. Use research + chosen approach to inform clarifying questions

**Remember:**
- Research is automatic, not optional
- Time-boxed: stop when limit reached or sufficient info gathered
- Always present options as A/B/C for easy selection
- Research informs better clarifying questions

---

## Phase 1: Create PRD (After Research)

Follow the [PRD Generation Guide](/workspace/.trees/task-guiding-docs/docs/workflows/prd-generation-guide.md).

**Steps:**
1. Acknowledge this as a task request
2. Create directory: `/tasks/[feature-name]/`
3. Ask clarifying questions (use lettered/numbered lists for easy response)
4. Wait for user responses
5. Generate comprehensive PRD following the template
6. Save to `/tasks/[feature-name]/prd.md`
7. Ask: "Would you like me to proceed with Phase 2: Task Generation?"
8. Wait for approval

**Remember:**
- Ask questions about: problem, goals, user stories, acceptance criteria, scope, data requirements, technical constraints
- Provide multiple-choice options where possible
- Use the PRD template structure from the guide

---

## Phase 2: Generate Tasks (After PRD Approval)

Follow the [Task Generation Guide](/workspace/.trees/task-guiding-docs/docs/workflows/task-generation-guide.md).

**Steps:**
1. Analyze PRD functional requirements
2. Create 4-7 high-level parent tasks
3. **ALWAYS include Documentation parent task (REQUIRED)**
4. Break each parent into 3-8 sub-tasks
5. Identify all relevant files (implementation + tests)
6. Create TodoWrite entries for all tasks
7. Save to `/tasks/[feature-name]/tasklist_1.md`
8. Ask: "Would you like me to proceed with Phase 3: Task Execution?"
9. Wait for approval

**Remember:**
- Documentation parent task is REQUIRED
- Follow common parent task patterns (Setup, Core, Testing, Documentation, etc.)
- Each sub-task should be 15-60 minutes of work

---

## Phase 3: Execute Tasks (After Task List Approval)

Follow the [Task Execution Guide](/workspace/.trees/task-guiding-docs/docs/workflows/task-execution-guide.md).

**For each sub-task:**
1. Mark as `in_progress` in TodoWrite AND markdown (same response)
2. Execute the work with comprehensive inline documentation
3. Mark as `completed` in TodoWrite AND markdown (same response)

**When all sub-tasks in parent are done:**
1. Run full test suite
2. Create/update component documentation
3. Update master changelog
4. Commit with conventional format
5. Update version in CLAUDE.md
6. Mark parent as `completed` in TodoWrite AND markdown

**Remember:**
- Only ONE task `in_progress` at a time
- Update TodoWrite and markdown in SAME response (never separately)
- See [TodoWrite-Markdown Sync Guide](/workspace/.trees/task-guiding-docs/docs/workflows/todowrite-markdown-sync.md)

---

## Quick Reference

- [Quick Reference Checklist](/workspace/.trees/task-guiding-docs/docs/workflows/quick-reference-checklist.md)
- [Documentation Requirements](/workspace/.trees/task-guiding-docs/docs/workflows/documentation-requirements.md)
- [Complete Workflow Guide](/workspace/.trees/task-guiding-docs/docs/workflows/automated-task-workflow.md)
- [Example: Email Validation](/workspace/.trees/task-guiding-docs/docs/workflows/examples/email-validation/)

---

**Now begin Phase 1: Ask clarifying questions about the task.**
