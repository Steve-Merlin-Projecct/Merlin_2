---
title: Documentation Index
type: reference
created: 2025-10-21
modified: 2025-10-21
status: current
related: README.md, CLAUDE.md, docs/worktrees/WORKTREE_COMPLETE_GUIDE.md
---

# Documentation Index

**Last Updated:** 2025-10-21
**Librarian Operations:** Documentation organization and consolidation

---

## Quick Start

- **Project README:** [/README.md](../README.md)
- **Quick Start Guide:** [/QUICKSTART.md](../QUICKSTART.md)
- **System Instructions:** [/CLAUDE.md](../CLAUDE.md)

---

## Core Documentation

### Architecture
- System Overview: [`architecture/system-overview.md`](architecture/system-overview.md)
- Component Documentation: [`architecture/`](architecture/)
- Database Configuration: [`database-connection-guide.md`](database-connection-guide.md)

### Setup & Configuration
- Environment Setup: [`setup/`](setup/)
- Database Setup: [`database-connection-guide.md`](database-connection-guide.md)
- Docker Configuration: [`/.devcontainer/`](../.devcontainer/)

### API Documentation
- API Overview: [`api/`](api/)
- Database API: [`api/database/`](api/database/)
- Webhook API: [`api/webhooks/`](api/webhooks/)

---

## Implementation Documentation

### Implementation Guides
- [Dashboard Implementation Plan](implementation/DASHBOARD_IMPLEMENTATION_PLAN.md)
- [Implementation Quick Reference](implementation/IMPLEMENTATION_QUICK_REFERENCE.md)
- [Implementation Summary](implementation/IMPLEMENTATION_SUMMARY.md)
- [Implementation Visual Guide](implementation/IMPLEMENTATION_VISUAL_GUIDE.md)
- [Implementation Files Reference](implementation/IMPLEMENTATION-FILES.md)
- [Integration Summary](implementation/INTEGRATION-SUMMARY.md)

### Specific Feature Implementations
- [503 Retry Implementation](implementation/503_RETRY_IMPLEMENTATION.md)
- [Multi-Tier Validation](implementation/MULTI_TIER_VALIDATION_IMPLEMENTATION.md)
- [Analysis Summary](implementation/ANALYSIS_SUMMARY.md)
- [Prompt Analysis Findings](implementation/PROMPT_ANALYSIS_FINDINGS.md)

---

## Testing Documentation

### Test Reports
- [Test Failure Analysis](testing/TEST_FAILURE_ANALYSIS.md)
- [Gemini Integration Test Report](testing/GEMINI_INTEGRATION_TEST_REPORT.md)
- [End-to-End Flow Findings](testing/END_TO_END_FLOW_FINDINGS_REPORT.md)
- [Comprehensive Testing Report](testing/comprehensive-testing-report.md)
- [Testing Strategy](testing/testing-strategy.md)
- [Testing Summary](testing/TESTING-SUMMARY.md)

### Phase Guides
- [Phase 3: Resilience & Storage Guide](testing/phase-3-resilience-storage-guide.md)
- [Phase 4: Dashboard & Analytics Guide](testing/phase-4-dashboard-analytics-guide.md)
- [Phase 5: Integration & E2E Guide](testing/phase-5-integration-e2e-guide.md)
- [Phases 3-4-5 Quick Reference](testing/PHASES-3-4-5-QUICK-REFERENCE.md)
- [Review Reminder](testing/REVIEW-REMINDER.md)

---

## Troubleshooting & Solutions

### Error Resolution
- [Worktree Build Error (RESOLVED)](troubleshooting/TREE_BUILD_ERROR.md)
- [Dashboard Access Fixed](troubleshooting/DASHBOARD_ACCESS_FIXED.md)
- [Migration Fix Documentation](troubleshooting/MIGRATION_FIX_DOCUMENTATION.md)
- [Airplay Conflict Solution](troubleshooting/SOLUTION_AIRPLAY_CONFLICT.md)
- [Hash and Replace Verified](troubleshooting/HASH_AND_REPLACE_VERIFIED.md)

### Common Issues
- Database connection issues: See [database-connection-guide.md](database-connection-guide.md)
- Worktree errors: See [troubleshooting/TREE_BUILD_ERROR.md](troubleshooting/TREE_BUILD_ERROR.md)
- Docker network issues: Run `python diagnose_docker_network.py`

---

## Worktree Documentation

### Worktree Management
- [Worktree Manager README](worktrees/README_WORKTREE_MANAGER.md)
- [Next Worktree Package](worktrees/NEXT_WORKTREE_PACKAGE.md)
- [Worktree Completion Package](worktrees/WORKTREE-COMPLETION-PACKAGE.md)
- [Worktree Tasks Pending Review](worktrees/WORKTREE_TASKS_PENDING_REVIEW.md)
- [Worktree Names Archive](worktrees/WORKTREE_NAMES_arhcive.md)

### Worktree Commands
- `/tree build` - Create worktrees from staged features
- `/tree build --verbose` - Create with detailed output
- `/tree close` - Complete work and generate synopsis
- `/tree closedone` - Batch merge and cleanup
- `/tree status` - Show worktree environment status

See: [CLAUDE.md](../CLAUDE.md) for full worktree documentation

---

## Project Reports

### Completion Reports
- [Completion Report](reports/COMPLETION_REPORT.md)
- [Phase 6 Summary](reports/PHASE6_SUMMARY.md)
- [Phase 1 Complete](reports/PHASE_1_COMPLETE.md)
- [Final Summary](reports/FINAL_SUMMARY.md)
- [Expansion Summary](reports/EXPANSION_SUMMARY.md)
- [Autonomous Execution Report](reports/AUTONOMOUS_EXECUTION_REPORT.md)

---

## Additional Documentation

### User Guides
- [UI Guide](UI_GUIDE.md)
- [README Implementation](README_IMPLEMENTATION.md)
- [README Completion Status](README_COMPLETION_STATUS.md)

### Code Quality
- Black configuration: [/.black.toml](../.black.toml)
- Flake8 configuration: [/.flake8](../.flake8)
- Vulture configuration: [/.vulture.toml](../.vulture.toml)
- Code quality standards: [`code-quality-standards.md`](code-quality-standards.md)

---

## Task Documentation

Task-specific documentation can be found in [`/tasks/`](../tasks/):
- Each task has its own directory with PRD, implementation notes, and testing docs
- Recent example: [`tasks/worktree-error-prevention/`](../tasks/worktree-error-prevention/)

---

## External Resources

### Dependencies
- Flask: https://flask.palletsprojects.com/
- PostgreSQL: https://www.postgresql.org/docs/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Google Gemini AI: https://ai.google.dev/docs

### Project Tools
- Apify (Job Scraping): https://apify.com/
- Docker: https://docs.docker.com/

---

## Documentation Organization

**Root Level:**
- `README.md` - Project overview and quick start
- `QUICKSTART.md` - Getting started guide
- `CLAUDE.md` - System instructions and policies

**`/docs/` Directory:**
- `architecture/` - System design and architecture
- `api/` - API documentation and references
- `setup/` - Setup and configuration guides
- `testing/` - Test documentation and strategies
- `implementation/` - Implementation guides and summaries
- `reports/` - Project completion reports
- `troubleshooting/` - Error resolution and fixes
- `worktrees/` - Worktree management documentation

**`/tasks/` Directory:**
- Task-specific PRDs, implementation notes, and testing docs

---

## Maintenance Notes

**Last Organization:** 2025-10-21
**Organized By:** Librarian Operations

**Changes Made:**
1. Moved 32 loose documentation files from root to organized directories
2. Created logical structure: implementation/, reports/, testing/, troubleshooting/, worktrees/
3. Updated CLAUDE.md with worktree error prevention documentation (v4.3.3)
4. Created this index for easy navigation

**Kept in Root:**
- README.md (primary project documentation)
- QUICKSTART.md (quick start guide)
- CLAUDE.md (system instructions)

---

## How to Update This Index

When adding new documentation:
1. Place files in appropriate `/docs/` subdirectory
2. Update the relevant section in this index
3. Add a brief description
4. Update "Last Updated" date at top
5. Note changes in "Maintenance Notes" section
