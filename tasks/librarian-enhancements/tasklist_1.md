# Task List: Librarian Agent Enhancement System

**Project:** Librarian Enhancements
**PRD:** [prd.md](./prd.md)
**Created:** 2025-10-12
**Status:** Ready for execution

---

## Parent Task 1: Script Foundation

**Goal:** Build deterministic validation and data collection scripts
**Effort:** 1 week
**Dependencies:** None

### Sub-tasks

#### 1.1: Create tools directory structure
- [ ] Create `/workspace/tools/` directory
- [ ] Create `/workspace/tools/hooks/` subdirectory
- [ ] Add `tools/__init__.py`
- [ ] Add README.md documenting tool usage

#### 1.2: Implement metadata validation script
- [ ] Create `tools/validate_metadata.py`
- [ ] Define required YAML fields (title, type, component, status)
- [ ] Parse YAML frontmatter with error handling
- [ ] Validate field presence and format
- [ ] Output: ValidationResult with errors/suggestions
- [ ] Add CLI interface with `--all` and `--fix` flags
- [ ] Write unit tests

#### 1.3: Implement file location validation script
- [ ] Create `tools/validate_location.py`
- [ ] Define rules from FILE_ORGANIZATION_STANDARDS.md
- [ ] Implement decision tree logic
- [ ] Check file against placement rules
- [ ] Suggest correct location for violations
- [ ] Add CLI interface with `--scan-root` flag
- [ ] Write unit tests

#### 1.4: Implement link validation script
- [ ] Create `tools/validate_links.py`
- [ ] Extract markdown links using regex
- [ ] Skip external URLs (http/https)
- [ ] Resolve relative paths
- [ ] Check if targets exist
- [ ] Report broken links with line numbers
- [ ] Add CLI interface with `--all` flag
- [ ] Write unit tests

#### 1.5: Implement metrics collection script
- [ ] Create `tools/collect_metrics.py`
- [ ] Count total docs and code files
- [ ] Calculate metadata coverage percentage
- [ ] Find broken links count
- [ ] Identify stale docs (>90 days)
- [ ] Find archive candidates (>180 days)
- [ ] Count root directory violations
- [ ] Group docs by component and type
- [ ] Find undocumented modules
- [ ] Output JSON and human-readable formats
- [ ] Write unit tests

---

## Parent Task 2: Document Catalog System

**Goal:** Build searchable index of all documentation
**Effort:** 1 week
**Dependencies:** Parent Task 1 (validation scripts)

### Sub-tasks

#### 2.1: Design catalog database schema
- [ ] Create SQLite schema definition
- [ ] Define `document_catalog` table
- [ ] Add indexes for component, type, status
- [ ] Create migration script if needed
- [ ] Document schema in README

#### 2.2: Implement catalog builder
- [ ] Create `tools/build_index.py`
- [ ] Scan all markdown files recursively
- [ ] Extract YAML frontmatter metadata
- [ ] Generate content summaries (first paragraph)
- [ ] Count words for complexity assessment
- [ ] Store file timestamps
- [ ] Handle missing metadata gracefully
- [ ] Implement incremental update mode
- [ ] Add CLI interface
- [ ] Write unit tests

#### 2.3: Implement catalog query interface
- [ ] Create `tools/query_catalog.py`
- [ ] Support keyword search
- [ ] Support component filter
- [ ] Support type filter
- [ ] Support status filter
- [ ] Support combined filters
- [ ] Format output (title, type, component, summary)
- [ ] Add sorting options (relevance, date)
- [ ] Add CLI interface
- [ ] Write unit tests

#### 2.4: Implement tag suggestion script
- [ ] Create `tools/suggest_tags.py`
- [ ] Implement TF-IDF keyword extraction
- [ ] Filter by relevance threshold
- [ ] Suggest 3-7 tags per document
- [ ] Handle code blocks (exclude from analysis)
- [ ] Add CLI interface
- [ ] Write unit tests

#### 2.5: Build initial catalog from existing docs
- [ ] Run `build_index.py` on entire `/docs` directory
- [ ] Verify catalog completeness
- [ ] Generate baseline metrics report
- [ ] Document catalog statistics

---

## Parent Task 3: Librarian Agent Enhancement

**Goal:** Add contextual intelligence workflows to librarian agent
**Effort:** 1 week
**Dependencies:** Parent Task 2 (document catalog)

### Sub-tasks

#### 3.1: Update librarian agent definition
- [ ] Read current `.claude/agents/librarian.md`
- [ ] Add "File Placement Advisor" workflow section
- [ ] Add "Discovery Assistant" workflow section
- [ ] Add "Tools Usage" section (how to invoke scripts)
- [ ] Document integration patterns
- [ ] Add examples of each workflow

#### 3.2: Implement file placement advisor workflow
- [ ] Define advisor invocation pattern
- [ ] Workflow: Analyze description/content preview
- [ ] Workflow: Run validate_location.py
- [ ] Workflow: Apply FILE_ORGANIZATION_STANDARDS decision tree
- [ ] Workflow: Check git context (branch, recent commits)
- [ ] Workflow: Return path + rationale
- [ ] Add example use cases
- [ ] Test with sample file requests

#### 3.3: Implement discovery assistant workflow
- [ ] Define discovery invocation pattern
- [ ] Workflow: Extract keywords from natural language query
- [ ] Workflow: Query document catalog
- [ ] Workflow: Rank results by relevance + recency
- [ ] Workflow: Generate brief summaries
- [ ] Workflow: Return top 5 with ratings
- [ ] Add example queries
- [ ] Test with sample queries

#### 3.4: Enhance gap analysis workflow
- [ ] Workflow: Scan `/modules` for components
- [ ] Workflow: Query catalog for corresponding docs
- [ ] Workflow: Assess code complexity (LOC, file count)
- [ ] Workflow: Check git activity (commit frequency)
- [ ] Workflow: Prioritize gaps (complexity × activity)
- [ ] Workflow: Generate recommendations with locations
- [ ] Add to librarian agent definition
- [ ] Test with current codebase

#### 3.5: Update CLAUDE.md with librarian policies
- [ ] Add "File Creation Policy" section
- [ ] Require librarian consultation before creating docs
- [ ] Add examples of consulting librarian
- [ ] Document when to use librarian vs direct tools
- [ ] Add to "Git Operations Policy" section equivalent

---

## Parent Task 4: Automation & Enforcement

**Goal:** Automate standards enforcement and maintenance
**Effort:** 1 week
**Dependencies:** Parent Task 1 (validation scripts)

### Sub-tasks

#### 4.1: Create pre-commit hook
- [ ] Create `tools/hooks/pre-commit` script
- [ ] Get staged markdown files
- [ ] Run validate_metadata.py on each
- [ ] Run validate_location.py on each
- [ ] Run validate_links.py on each
- [ ] Exit with error if any check fails
- [ ] Provide clear error messages with fix suggestions
- [ ] Make hook executable
- [ ] Add installation instructions to README

#### 4.2: Install pre-commit hook
- [ ] Copy hook to `.git/hooks/pre-commit`
- [ ] Set executable permissions
- [ ] Test with intentional violation
- [ ] Verify hook blocks commit
- [ ] Document in README

#### 4.3: Create CI/CD documentation validation workflow
- [ ] Create `.github/workflows/validate-docs.yml`
- [ ] Add job: validate-metadata (all files)
- [ ] Add job: check-broken-links (all files)
- [ ] Add job: generate-coverage-report
- [ ] Trigger on push and pull_request
- [ ] Test workflow in PR

#### 4.4: Implement automated archival script
- [ ] Create `tools/auto_archive.py`
- [ ] Find files not modified in 180 days
- [ ] Check if files are referenced elsewhere
- [ ] Compute appropriate archive path
- [ ] Implement dry-run mode (default)
- [ ] Implement actual move functionality
- [ ] Update catalog after archival
- [ ] Add CLI interface
- [ ] Write unit tests

#### 4.5: Test enforcement mechanisms
- [ ] Test pre-commit hook with violations
- [ ] Test pre-commit hook with valid files
- [ ] Verify CI/CD workflow runs
- [ ] Test archival script with old files
- [ ] Document test results

---

## Parent Task 5: Cleanup & Initial Rollout

**Goal:** Clean up existing violations and establish baseline
**Effort:** 1 week
**Dependencies:** All previous tasks

### Sub-tasks

#### 5.1: Audit root directory violations
- [ ] Run `validate_location.py --scan-root`
- [ ] Document all 19 violations
- [ ] Determine correct location for each file
- [ ] Create issue list for manual review

#### 5.2: Move root directory files to correct locations
- [ ] Move BRANCH_STATUS.md → /docs/git_workflow/branch-status/
- [ ] Move COMPLETION_SUMMARY.md → appropriate location
- [ ] Move DASHBOARD_V2_HANDOFF.md → /docs/
- [ ] Move DEPLOYMENT_CHECKLIST.md → /docs/deployment/
- [ ] Move FILES_SUMMARY.md → /docs/ or archive
- [ ] Move FUTURE_TASKS_RATE_LIMITING.md → /docs/future-tasks/
- [ ] Move IMPLEMENTATION_* files → /docs/ or archive
- [ ] Move LIBRARIAN_HANDOFF.md → /docs/
- [ ] Move MERGE_CHECKLIST.md → /docs/git_workflow/
- [ ] Continue for all 19 violations
- [ ] Update any links to moved files
- [ ] Verify no broken links remain

#### 5.3: Add metadata to existing documentation
- [ ] Run `validate_metadata.py --all` to find missing metadata
- [ ] Generate metadata templates with suggest_tags.py
- [ ] Add YAML frontmatter to files missing metadata
- [ ] Prioritize active documentation first
- [ ] Verify metadata with validation script

#### 5.4: Rebuild document catalog with clean data
- [ ] Run `build_index.py` to rebuild full catalog
- [ ] Verify all active docs are indexed
- [ ] Run `collect_metrics.py` for baseline report
- [ ] Document "before" vs "after" metrics

#### 5.5: Create librarian usage guide
- [ ] Create `/docs/librarian-usage-guide.md`
- [ ] Document how to consult librarian for file placement
- [ ] Document how to use discovery assistant
- [ ] Document how to run validation scripts manually
- [ ] Add examples and common scenarios
- [ ] Link from CLAUDE.md

#### 5.6: Generate rollout summary
- [ ] Document all changes made
- [ ] Create metrics comparison (before/after)
- [ ] List files moved and why
- [ ] Document new workflows and tools
- [ ] Add to project changelog

---

## Parent Task 6: Documentation & Training

**Goal:** Document new system and train team
**Effort:** 3-4 days
**Dependencies:** Parent Task 5 (cleanup complete)

### Sub-tasks

#### 6.1: Create comprehensive tool documentation
- [ ] Document each script in `tools/README.md`
- [ ] Add usage examples for each tool
- [ ] Document common workflows
- [ ] Add troubleshooting section
- [ ] Include CLI reference

#### 6.2: Update project documentation
- [ ] Update CLAUDE.md with librarian policies
- [ ] Update FILE_ORGANIZATION_STANDARDS.md if needed
- [ ] Create librarian-usage-guide.md
- [ ] Add to docs/README.md index
- [ ] Cross-link related docs

#### 6.3: Create visual aids
- [ ] Create flowchart: "Where should my file go?"
- [ ] Create flowchart: "How to use librarian agent"
- [ ] Create diagram: Script vs Agent responsibilities
- [ ] Add to documentation

#### 6.4: Write changelog entry
- [ ] Add to `docs/changelogs/master-changelog.md`
- [ ] Document all features added
- [ ] Document breaking changes (if any)
- [ ] Document migration steps for team

#### 6.5: Create team training materials
- [ ] Quick start guide for developers
- [ ] Common scenarios and solutions
- [ ] FAQ section
- [ ] Video walkthrough (optional)

---

## Testing Checklist

### Unit Tests
- [ ] Test validate_metadata.py with valid/invalid YAML
- [ ] Test validate_location.py with various file types
- [ ] Test validate_links.py with broken/valid links
- [ ] Test build_index.py with sample documents
- [ ] Test query_catalog.py with various filters
- [ ] Test suggest_tags.py with sample content
- [ ] Test collect_metrics.py output format
- [ ] Test auto_archive.py in dry-run mode

### Integration Tests
- [ ] Test pre-commit hook blocks violations
- [ ] Test pre-commit hook allows valid commits
- [ ] Test CI/CD workflow runs successfully
- [ ] Test librarian agent file placement workflow
- [ ] Test librarian agent discovery workflow
- [ ] Test end-to-end: Create file → validate → commit

### Acceptance Tests
- [ ] Verify root directory: 29 files → 10 files
- [ ] Verify pre-commit hook: 100% catch rate for violations
- [ ] Verify catalog contains all active documentation
- [ ] Verify discovery finds relevant docs in <5 results
- [ ] Verify all moved files have correct metadata

---

## Success Criteria

**Must achieve:**
1. ✅ Root directory reduced to 10 essential files
2. ✅ Pre-commit hook installed and functional
3. ✅ Document catalog built and queryable
4. ✅ Librarian agent has new workflows documented
5. ✅ All active docs have valid metadata
6. ✅ Zero broken links in active documentation

**Nice to have:**
- CI/CD validation workflow active
- Auto-archival script tested (dry-run)
- Team training materials created
- Baseline metrics report generated

---

## Notes

- **Autonomous execution:** Following "go" workflow - implement without approval between sub-tasks
- **Error handling:** If blocked, document issue and continue with next task
- **Testing:** Run tests after each parent task completion
- **Commits:** Commit after each parent task with descriptive message
