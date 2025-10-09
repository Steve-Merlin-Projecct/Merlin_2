---
title: Workflow Examples
created: '2025-10-07'
updated: '2025-10-07'
author: Steve-Merlin-Projecct
type: guide
status: active
tags:
- workflow
---

# Workflow Examples

This directory contains complete worked examples demonstrating the Automated Task Workflow from start to finish.

## Purpose

These examples show:
- How to write a comprehensive PRD
- How to break down a PRD into tasks
- How to execute tasks with proper TodoWrite-Markdown synchronization
- How to create documentation
- How to commit with conventional format
- How to update changelogs

## Available Examples

### Email Validation System

**Location:** `./email-validation/`

**Complexity:** Medium (representative of typical feature)

**Demonstrates:**
- PRD creation with user stories and functional requirements
- Task breakdown into 7 parent tasks with ~40 sub-tasks
- Database schema changes with automation
- Backend + frontend integration
- Comprehensive testing strategy
- Documentation requirements (inline + component docs)
- Complete execution example showing TodoWrite-Markdown sync

**Files:**
- `prd.md` - Complete Product Requirements Document
- `tasklist_1.md` - Full task list with all parent and sub-tasks
- `execution-example.md` - Step-by-step execution showing how to complete Task 1.0

**Best Used For:**
- Understanding PRD structure and depth
- Seeing realistic task breakdown patterns
- Learning TodoWrite-Markdown synchronization
- Understanding documentation requirements
- Reference when creating your own PRDs and tasks

## How to Use These Examples

### For Creating PRDs:

1. Read `email-validation/prd.md` to see structure
2. Note the level of detail in each section
3. Use as template for your own PRDs
4. Adapt sections based on your feature type

### For Task Generation:

1. Review `email-validation/tasklist_1.md`
2. See how PRD requirements map to tasks
3. Note the standard parent task pattern:
   - Setup & Configuration
   - Core Implementation
   - Integration
   - Testing
   - **Documentation (REQUIRED)**
   - Deployment
4. Observe sub-task granularity (15-60 min per task)

### For Task Execution:

1. Read `email-validation/execution-example.md`
2. Follow the TodoWrite-Markdown sync pattern
3. Note the commit workflow:
   - All sub-tasks done → Run tests → Commit → Update changelog
4. See documentation creation in action
5. Understand the "same response" sync pattern

## Key Patterns to Notice

### PRD Pattern:
```
Problem Statement
  ↓
Goals (measurable)
  ↓
User Stories (with acceptance criteria)
  ↓
Functional Requirements (detailed, numbered)
  ↓
Technical Considerations
  ↓
Success Metrics
```

### Task List Pattern:
```
Parent Task 1.0 Setup
  Sub-tasks 1.1, 1.2, 1.3...
Parent Task 2.0 Core Implementation
  Sub-tasks 2.1, 2.2, 2.3...
...
Parent Task N.0 Documentation (REQUIRED)
  Sub-tasks N.1, N.2, N.3...
```

### Execution Pattern:
```
For each sub-task:
  1. Mark in_progress (TodoWrite + Markdown, same response)
  2. Do the work
  3. Mark completed (TodoWrite + Markdown, same response)

When parent task complete:
  1. Run tests
  2. Create/update documentation
  3. Update changelog
  4. Commit with conventional format
  5. Mark parent completed (TodoWrite + Markdown)
```

## Common Questions

**Q: How detailed should PRDs be?**
A: See the email-validation PRD. It has ~2000 words covering all aspects. This is appropriate for a medium-complexity feature.

**Q: How many sub-tasks should each parent have?**
A: See the task list. Most parents have 3-8 sub-tasks. Each sub-task is 15-60 minutes of work.

**Q: When do I create documentation?**
A: See execution example Task 1.0. Documentation is created as part of parent task completion, before committing.

**Q: How do I keep TodoWrite and Markdown synced?**
A: See execution example. Update both in the SAME agent response, always. Never split across multiple messages.

**Q: What gets committed together?**
A: All sub-tasks in a parent task. After all sub-tasks are done and tests pass, commit the entire parent task's changes at once.

## Future Examples

Additional examples may be added for:
- Simple feature (1-2 parent tasks)
- Complex feature (10+ parent tasks, multiple task lists)
- Bug fix workflow
- Refactoring workflow
- Integration project

For now, email-validation provides a representative example of typical feature development.

---

**Related Documentation:**
- [Automated Task Workflow](../automated-task-workflow.md)
- [PRD Generation Guide](../prd-generation-guide.md)
- [Task Generation Guide](../task-generation-guide.md)
- [Task Execution Guide](../task-execution-guide.md)
- [TodoWrite-Markdown Sync Guide](../todowrite-markdown-sync.md)
