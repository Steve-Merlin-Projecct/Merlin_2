# PRD: Post-Replit Migration Code Cleanup
**Status:** Planning
**Priority:** High
**Feature Branch:** `feature/post-migration-refactoring`
**Version:** 4.0.2

## Executive Summary

Complete systematic cleanup of Replit-related code, documentation, and configurations following the migration to a local/Docker development environment. This includes removing obsolete code, updating documentation, and optimizing the codebase for the new containerized environment.

## Problem Statement

The project has been migrated from Replit to a local Docker/devcontainer environment. While the storage abstraction layer was implemented and basic Replit dependencies removed, **117 files still contain Replit references**. This technical debt includes:

1. **Code remnants** - Functions, imports, and logic specific to Replit's environment
2. **Documentation debt** - Outdated instructions, setup guides, and architecture docs
3. **Configuration artifacts** - Environment-specific settings no longer relevant
4. **Archived content** - Historical files that mention Replit but may still be referenced
5. **Hidden dependencies** - Code that appears generic but was designed for Replit's constraints

## Objectives

### Primary Goals
1. Remove all obsolete Replit-specific code from active codebase
2. Update documentation to reflect Docker/devcontainer environment
3. Identify and refactor code that was "Replit-shaped" but appears generic
4. Optimize code for the new containerized environment
5. Archive historical Replit content appropriately

### Success Criteria
- Zero Replit references in active Python code (`/modules`, `/database_tools`, `/tools`)
- All documentation reflects current Docker environment
- No broken references to removed Replit functionality
- All tests pass after cleanup
- Storage abstraction layer is the only mention of migration context

## Scope Boundaries

### In Scope
- Remove all Replit imports and API calls from active code
- Update documentation to Docker-first approach
- Archive historical Replit migration documents
- Clean environment variables with REPL_ prefix
- Remove Replit-specific configuration files
- Refactor code patterns that worked around Replit limitations
- Update hardcoded Replit URLs to Docker/localhost equivalents
- Clean up Replit-specific error handling and fallback logic

### Out of Scope
- **Changelog history** - Keep Replit mentions for historical accuracy
- **Third-party library documentation** - Not under our control
- **Git commit history rewriting** - Preserve historical record
- **Deep performance optimization** - Only remove constraints, don't rebuild
- **Archived files** - Already in `/archived_files/`, leave as-is
- **Test fixtures** - May reference Replit for testing migration logic

### Grey Areas (Decision Matrix)

| Scenario | Action | Rationale |
|----------|--------|-----------|
| Code works but was "Replit-shaped" | Keep + add TODO comment | Don't fix what isn't broken |
| Works but has obvious Docker improvement | Refactor | Optimize for new environment |
| Works but confusing/misleading | Refactor | Code clarity priority |
| Doesn't work or redundant | Remove | Dead code cleanup |
| Comments mentioning "from Replit" as context | Update to "legacy migration" | Maintain context without confusion |
| Variable names like `old_replit_path` | Keep if functional | Self-documenting legacy code |

### Edge Case Handling

1. **Security Issues Found**: Fix immediately, document in security changelog
2. **Missing Test Coverage**: Add tests before removal if critical path
3. **Broken Dependencies**: Create adapter/shim temporarily, mark for removal
4. **Ambiguous References**: Default to archive, document decision
5. **Performance Regressions**: Keep old code, add feature flag for new

## Evaluation Methodology

### Phase 0: Edge Case Discovery (Pre-Analysis)

**Objective:** Surface all edge cases and ambiguous patterns before main discovery.

#### Activities

1. **Pattern Variation Search:**
   - Search for case variations: `repl.it`, `Repl.it`, `repl-it`, `repl_it`
   - Check for partial references: `REPL`, `repl`, without full "replit"
   - Look for typos: `replt`, `repllit`, `replut`

2. **Context Analysis:**
   - Identify Replit references in comments vs. code
   - Find references in string literals vs. actual imports
   - Locate references in test data vs. production code

3. **Dependency Chain Mapping:**
   - Find indirect Replit dependencies (modules that import Replit modules)
   - Identify configuration cascades (configs that reference other configs)
   - Map environment variable usage chains

4. **File Type Inventory:**
   - List all file types containing "replit" (`.py`, `.md`, `.json`, `.yaml`, `.txt`, etc.)
   - Identify binary files or compressed archives with Replit content
   - Find hidden files (`.replit`, `.env.replit`, etc.)

5. **Historical Context Gathering:**
   - Review git history for Replit-related commits
   - Identify when Replit was introduced vs. when migration started
   - Find any rollback commits or reverted changes

#### Deliverables
- `/tasks/post-migration-refactoring/phase0-edge-cases.md`
- `/tasks/post-migration-refactoring/phase0-patterns.txt`
- `/tasks/post-migration-refactoring/phase0-file-inventory.txt`

### Phase 1: Discovery & Classification (Analysis)

**Objective:** Categorize all Replit references by type and risk level.

#### Classification Categories

**Category A: Obvious Replit Code** (Safe to remove)
- Direct Replit API imports (`from replit import ...`)
- Replit-specific configuration files
- Replit database references (`replit.db`, `replit-py`)
- Replit secrets/environment handling specific to their platform

**Category B: Documentation References** (Update or archive)
- Historical documentation in `/docs/archived/`
- Migration summaries and status files
- Setup instructions for Replit environment
- Changelog entries mentioning Replit

**Category C: Replit-Shaped Code** (Requires analysis)
- Code written to work around Replit limitations
- Storage patterns designed for Replit's filesystem
- Environment variable handling that assumed Replit's secrets
- HTTP/webhook patterns shaped by Replit's networking

**Category D: Optimization Opportunities** (Enhance for Docker)
- File I/O that can be improved without Replit's constraints
- Database connection pooling (previously limited by Replit)
- Background task handling (can use proper async/workers now)
- Resource limits that were Replit-specific

**Category E: Archive Material** (Preserve but isolate)
- Migration documentation (valuable historical record)
- Comparison docs (Replit vs Docker)
- Lessons learned from migration

#### Discovery Tools

1. **Grep Analysis:**
   ```bash
   # Find all Replit references
   grep -r "replit\|Replit\|REPLIT" --include="*.py" --include="*.md" --include="*.json"

   # Find import statements
   grep -r "from replit\|import replit" --include="*.py"

   # Find configuration references
   grep -r "REPL_\|replit\." --include="*.env*" --include="*.json"
   ```

2. **File Pattern Analysis:**
   ```bash
   # Find archived Replit files
   find . -name "*replit*" -type f

   # Find migration-related files
   find . -name "*migration*" -o -name "*MIGRATION*"
   ```

3. **Dependency Analysis:**
   ```bash
   # Check for Replit packages
   grep "replit" pyproject.toml requirements.txt uv.lock
   ```

4. **Code Pattern Detection:**
   - Search for workarounds: `# TODO Replit`, `# FIXME`, `# HACK`
   - Environment checks: `if os.getenv("REPL_ID")`, `if "replit" in ...`
   - Storage patterns: references to `/home/runner/`, persistent storage hacks

### Phase 2: Impact Analysis (Planning)

For each identified item:

1. **Dependency Check:**
   - What code imports/uses this?
   - What documentation references this?
   - Are there tests that depend on this?

2. **Risk Assessment:**
   - **Low Risk:** Pure documentation, obvious dead code
   - **Medium Risk:** Shared utilities, configuration files
   - **High Risk:** Core logic, database operations, API endpoints

3. **Replacement Strategy:**
   - **Remove:** No replacement needed, purely obsolete
   - **Replace:** Docker/modern equivalent exists
   - **Refactor:** Code needs redesign for new environment
   - **Archive:** Historical value, move to `/archived_files/`

### Phase 3: Execution Plan (Implementation)

#### Work Breakdown Structure

**Stream 1: Code Cleanup**
1. Remove Replit package dependencies
2. Remove Replit-specific imports and functions
3. Refactor Replit-shaped code patterns
4. Update environment variable handling
5. Optimize for Docker environment

**Stream 2: Documentation Update**
6. Update CLAUDE.md to remove Replit context
7. Revise setup/deployment guides
8. Update architecture documentation
9. Archive historical migration docs
10. Update inline code comments

**Stream 3: Configuration & Tools**
11. Clean `.env.example` and configuration templates
12. Update CI/CD configurations
13. Remove Replit-specific scripts from `/tools/`
14. Update database connection configurations

**Stream 4: Testing & Validation**
15. Update test fixtures and mocks
16. Remove Replit environment simulation
17. Add Docker environment tests
18. Validate all existing tests pass

**Stream 5: Final Cleanup**
19. Update version to 4.1.0 (minor version bump)
20. Generate final cleanup report
21. Update master changelog
22. Archive this PRD as completed

### Phase 4: Validation (Quality Assurance)

**Validation Checklist:**

- [ ] No `import replit` or `from replit` in active code
- [ ] No Replit environment checks in active code
- [ ] All tests pass: `pytest`
- [ ] All services start: `docker-compose up`
- [ ] Database connections work with new config
- [ ] Storage abstraction layer functions correctly
- [ ] Documentation builds without broken links
- [ ] Code quality checks pass: `/lint`
- [ ] No TODO/FIXME comments about Replit
- [ ] Version bumped and changelog updated

**Automated Checks:**
```bash
# Run as pre-merge validation
./tools/validate_cleanup.sh
```

## File-by-File Evaluation Criteria

For each file containing "replit" references:

### Questions to Ask:

1. **Is this file in active use?**
   - Check git history: last modified date
   - Check imports: is it imported anywhere?
   - Check references: is it mentioned in docs?

2. **What type of Replit reference is this?**
   - Code dependency
   - Documentation/comment
   - Historical/archived content
   - Configuration

3. **What's the correct action?**
   - **DELETE:** Obsolete, no value
   - **ARCHIVE:** Historical value, not needed for operation
   - **UPDATE:** Change Replit references to Docker/modern equivalent
   - **REFACTOR:** Redesign for new environment
   - **KEEP:** Reference is historical context (e.g., changelog)

4. **Are there dependencies on this file?**
   - Run: `grep -r "filename" --include="*.py"`
   - Check import statements
   - Check documentation links

5. **Is there test coverage?**
   - Related test files in `/tests/`
   - Test fixtures that need updating
   - Mocked Replit behavior to remove

## Specific Areas of Focus

### 1. Storage System

**Current State:** Storage abstraction layer implemented
**Action Required:**
- Verify no lingering Replit storage patterns
- Ensure local/Docker storage is default
- Remove any Replit-specific fallback code

### 2. Environment Configuration

**Files to Review:**
- `.env.example`
- `docker-compose.yml`
- `.devcontainer/devcontainer.json`
- `CLAUDE.md` (environment variables section)

**Action Required:**
- Remove `REPL_` prefixed variables
- Update to Docker-first environment variables
- Document container-specific variables

### 3. Database Connections

**Current State:** Environment-aware configuration implemented
**Action Required:**
- Remove Replit database connection fallbacks
- Verify Docker networking works correctly
- Test connection pooling (now unlimited)

### 4. File I/O Patterns

**Areas to Examine:**
- Document generation paths
- Template file handling
- Log file locations
- Temporary file creation

**Action Required:**
- Optimize for containerized filesystem
- Remove Replit path workarounds
- Use standard Docker volume patterns

### 5. Webhook/API Handlers

**Files to Review:**
- `app_modular.py`
- `/modules/webhook_handler/`
- Archived webhook handlers

**Action Required:**
- Remove Replit proxy workarounds
- Optimize for direct Docker networking
- Clean up legacy webhook implementations

## Risk Mitigation

### Backup Strategy
1. Create snapshot before any deletions: `git tag pre-cleanup-snapshot`
2. Work in feature branch: `feature/post-migration-refactoring`
3. Incremental commits with clear messages
4. Keep `/archived_files/` as safety net

### Testing Strategy
1. Run full test suite before starting
2. Run tests after each major category cleanup
3. Manual testing of core workflows
4. Docker container rebuild validation

### Rollback Plan
1. Git revert to `pre-cleanup-snapshot` tag
2. Cherry-pick safe changes if partial rollback needed
3. Document any issues discovered during cleanup

## Deliverables

### Code Changes
1. Cleaned Python codebase (0 Replit imports)
2. Updated configuration files
3. Refactored Replit-shaped code
4. Optimized Docker environment code

### Documentation Updates
1. Updated CLAUDE.md
2. Revised deployment guides
3. Updated architecture documentation
4. Archived migration documentation

### Reports
1. Cleanup execution log
2. Files deleted/modified summary
3. Code optimization improvements
4. Post-cleanup validation report

### Version Update
1. Bump to 4.1.0 (minor version for significant refactor)
2. Update master changelog
3. Tag release: `v4.1.0-post-replit-cleanup`

## Timeline Estimate

**Phase 1: Discovery & Classification** - 2-3 hours
- Automated scanning: 30 min
- Manual classification: 1.5-2 hours
- Documentation: 30 min

**Phase 2: Impact Analysis** - 1-2 hours
- Dependency mapping: 1 hour
- Risk assessment: 30-60 min

**Phase 3: Execution** - 4-6 hours
- Code cleanup: 2-3 hours
- Documentation updates: 1-2 hours
- Configuration cleanup: 1 hour
- Testing: 1 hour

**Phase 4: Validation** - 1 hour
- Test suite execution: 30 min
- Manual validation: 30 min

**Total Estimated Time:** 8-12 hours of focused work

## Next Steps

1. Review and approve this PRD
2. Execute Phase 1: Discovery & Classification
3. Generate detailed file-by-file action plan
4. Begin systematic cleanup in priority order
5. Continuous testing and validation
6. Final review and version bump

## Success Metrics

- **Code Quality:** 0 Replit references in active codebase
- **Test Coverage:** 100% of tests passing post-cleanup
- **Documentation Accuracy:** 100% of setup docs reflect Docker environment
- **Performance:** Measurable improvements from Docker optimization
- **Maintainability:** Reduced technical debt, clearer architecture

## Notes

- This is a refactoring task, NOT a feature addition
- Focus on safety: preserve functionality while removing cruft
- When in doubt, archive rather than delete
- Document all non-obvious decisions
- This cleanup sets foundation for future development in clean Docker environment
