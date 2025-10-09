---
title: Automated Task Workflow Documentation
created: '2025-10-07'
updated: '2025-10-07'
author: Steve-Merlin-Projecct
type: guide
status: active
tags:
- workflow
---

# Automated Task Workflow Documentation
**Version:** 1.0
**Date:** October 6, 2025
**Environment:** Claude Code

## Overview

This directory contains the complete documentation for the Automated Task Workflow system in Claude Code. This system automatically guides the agent through a structured process for implementing features:

```
User Task Request → PRD Creation → Task Generation → Task Execution → Completion
```

## Documentation Files

### 1. [Automated Task Workflow](./automated-task-workflow.md)
**Main workflow orchestration document**

- Intent detection (Task vs Question classification)
- Three-phase workflow (PRD → Tasks → Execution)
- TodoWrite integration
- File structure and organization
- Commit protocol and versioning
- Future enhancement notes (specialized agent)

**Use this when:** Understanding the complete end-to-end workflow

### 2. [PRD Generation Guide](./prd-generation-guide.md)
**Phase 1: Product Requirements Document creation**

- Clarifying questions framework
- PRD structure and template
- Quality checklist
- Examples and patterns

**Use this when:** Creating a new PRD for a feature request

### 3. [Task Generation Guide](./task-generation-guide.md)
**Phase 2: Task list creation with TodoWrite integration**

- Task breakdown methodology
- TodoWrite dual-tracking system
- File identification
- Common task patterns
- Multiple task list management

**Use this when:** Breaking down a PRD into actionable tasks

### 4. [Task Execution Guide](./task-execution-guide.md)
**Phase 3: Implementation with automation**

- Execution protocol
- TodoWrite status management (one-in-progress rule)
- Test & commit workflow
- Code quality standards
- Database schema change handling
- Hooks integration (future)

**Use this when:** Implementing tasks from a task list

## Quick Start

### For the Agent

When a user makes a request:

1. **Classify the request:**
   - Task? → Trigger automated workflow
   - Question? → Provide analysis only

2. **If Task, follow the phases:**
   - **Phase 1:** Create PRD ([guide](./prd-generation-guide.md))
   - **Phase 2:** Generate tasks ([guide](./task-generation-guide.md))
   - **Phase 3:** Execute tasks ([guide](./task-execution-guide.md))

3. **Use TodoWrite throughout:**
   - Create todos for all tasks
   - Update status in real-time
   - Only ONE task `in_progress` at a time

4. **Commit after each parent task:**
   - Run tests first
   - Use conventional commit format
   - Update changelog and version

### For the User

**To trigger the workflow:**
Use task-oriented language:
- "Create a password reset feature"
- "Implement email validation"
- "Fix the database connection timeout"

**To get analysis instead:**
Use question language:
- "How does authentication work?"
- "What would you recommend for caching?"
- "Can you explain the database schema?"

**To monitor progress:**
- TodoWrite shows real-time progress
- Task list file shows complete hierarchy
- Changelog tracks completed work

## File Structure

All workflow-related files are organized in `/tasks/[feature-name]/`:

```
/tasks/
└── [feature-name]/              # e.g., user-authentication
    ├── prd.md                   # Product Requirements Document
    ├── tasklist_1.md            # Primary task list
    ├── tasklist_2.md            # Additional tasks (if needed)
    └── notes.md                 # Optional implementation notes
```

**After completion**, entire directory moves to:
```
/docs/archived/[subdirectory]/[feature-name]/
```

## Key Principles

### 1. **Automatic Workflow Trigger**
- Agent detects task requests automatically
- No manual invocation needed
- User can override with qualifier phrases ("Just analyze...")

### 2. **TodoWrite Integration**
- Dual tracking: Markdown file + TodoWrite API
- Real-time status updates
- Only ONE task `in_progress` at a time
- Immediate status updates (no batching)

### 3. **Test-Driven Commits**
- Always run tests before committing
- Only commit when parent task complete
- Use conventional commit format
- Update changelog and version

### 4. **Code Quality**
- Comprehensive inline documentation
- Error handling and edge cases
- Test coverage for all new code
- Follow project coding standards

### 5. **Database Schema Automation**
- Never manually edit generated files
- Always run `database_tools/update_schema.py` after schema changes
- Commit generated documentation

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Request                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Intent Detection    │
              │  (Task vs Question)  │
              └──────────┬───────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
  ┌────────────┐                 ┌──────────────┐
  │  Question  │                 │     Task     │
  │  Analysis  │                 │   Workflow   │
  └────────────┘                 └──────┬───────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │   Phase 1: PRD   │
                              │   - Questions    │
                              │   - Generation   │
                              │   - Approval     │
                              └─────────┬────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │ Phase 2: Tasks   │
                              │ - Breakdown      │
                              │ - TodoWrite      │
                              │ - Approval       │
                              └─────────┬────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │ Phase 3: Execute │
                              │ - Implement      │
                              │ - Test           │
                              │ - Commit         │
                              └─────────┬────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │    Complete      │
                              │  - Changelog     │
                              │  - Archive       │
                              └──────────────────┘
```

## TodoWrite Status Flow

```
┌─────────────┐
│   pending   │  ← Task created, not started
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  in_progress    │  ← Currently working (ONLY ONE allowed)
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│  completed  │  ← Task finished
└─────────────┘
```

## Commit Flow (Parent Task Complete)

```
┌──────────────────────┐
│ All sub-tasks done?  │
└──────┬───────────────┘
       │ YES
       ▼
┌──────────────────────┐
│   Run test suite     │
└──────┬───────────────┘
       │
       ▼
  ┌─────────────┐
  │ Tests pass? │
  └──┬─────┬────┘
     │     │
     NO    YES
     │     │
     │     ▼
     │  ┌──────────────┐
     │  │  Stage files │
     │  └──────┬───────┘
     │         │
     │         ▼
     │  ┌──────────────┐
     │  │   Commit     │
     │  └──────┬───────┘
     │         │
     │         ▼
     │  ┌──────────────────┐
     │  │ Update changelog │
     │  └──────┬───────────┘
     │         │
     │         ▼
     │  ┌────────────────────┐
     │  │ Mark parent done   │
     │  └────────────────────┘
     │
     ▼
┌──────────────────────┐
│ Create fix task      │
│ Debug & re-test      │
└──────────────────────┘
```

## Incremental Improvements

As you use this workflow, consider these practical enhancements:

**After 2-3 Features:**
- Add pre-commit hook to automatically run tests
- Create bash aliases for frequently used commands
- Document common patterns you discover

**After 5+ Features:**
- Build a template library for common PRD sections
- Create reusable task patterns (database changes, API endpoints, etc.)
- Track actual vs estimated task durations

**After 10+ Features:**
- Review and update clarifying questions based on what works
- Optimize task breakdown based on learned patterns
- Consider custom slash commands for repetitive workflows

**Keep It Simple:** Focus on small improvements that save time, not complex automation

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-06 | Initial documentation creation for Claude Code environment |

## Related Documentation

- [CLAUDE.md](../../CLAUDE.md) - Project instructions and standards
- [Database Schema Automation](../component_docs/database/database_schema_automation.md)
- [Git Workflow](../git_workflow/GIT_KNOWLEDGE.md)
- [Coding Standards](../development/standards/CODING_STANDARDS.md)

## Support

For questions or issues with the workflow:
1. Check troubleshooting sections in individual guides
2. Review examples in guides
3. Consult related documentation
4. Discuss with project administrator

---

**Document Owner:** Development Team
**Last Reviewed:** October 6, 2025
**Next Review:** After 10 completed features using this workflow

## Complete Documentation Index

1. **[README.md](./README.md)** - This file, overview and quick start
2. **[automated-task-workflow.md](./automated-task-workflow.md)** - Main workflow orchestration
3. **[prd-generation-guide.md](./prd-generation-guide.md)** - Phase 1: PRD creation
4. **[task-generation-guide.md](./task-generation-guide.md)** - Phase 2: Task breakdown
5. **[task-execution-guide.md](./task-execution-guide.md)** - Phase 3: Implementation
6. **[documentation-requirements.md](./documentation-requirements.md)** - Inline and component docs
7. **[todowrite-markdown-sync.md](./todowrite-markdown-sync.md)** - Synchronization guide
8. **[quick-reference-checklist.md](./quick-reference-checklist.md)** - One-page agent checklist
9. **[examples/](./examples/)** - Worked examples (email validation system)
