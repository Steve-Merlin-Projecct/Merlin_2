# PRD: Librarian System - Automated File Organization & Documentation Management

**Status:** 📋 Active - Ready for Implementation
**Priority:** High
**Feature Branch:** `task/10-librarian`
**Version:** 1.0.0
**Created:** October 9, 2025
**Author:** Claude Sonnet 4.5

## Executive Summary

Implement a comprehensive librarian system combining intelligent agent-based analysis with automated scripting to manage file organization, documentation indexing, metadata standardization, and archival workflows across 416+ project files. The system will provide sustainable, scalable documentation management and prevent file organization degradation over time.

## Problem Statement

The project has successfully established file organization standards (October 8, 2025 cleanup), but faces ongoing challenges:

1. **Scale Challenge:** 516 total files (416 documentation/code files) require continuous organization maintenance
2. **Metadata Inconsistency:** Three different metadata patterns exist across documentation (structured PRDs, technical docs, minimal/no metadata)
3. **Discovery Gap:** No centralized index or search capability - developers rely on grep/manual navigation
4. **Archive Accumulation:** Tasks directory (5.0MB) contains completed work mixed with active tasks
5. **Manual Maintenance Burden:** Recent cleanup required manual reference tracking, link validation, and file categorization
6. **Sustainability Risk:** Without automation, organization will degrade as project grows

### Current State Metrics
- **Total Files:** 516
- **Catalogable Files:** 416 (.md, .py, .json, .yml)
- **Documentation Files:** 150-200 markdown files
- **Tasks Directory Size:** 5.0MB (needs archival)
- **Metadata Coverage:** ~30% (partial/inconsistent)
- **Automated Tooling:** None (fully manual)

## Objectives

### Primary Goals

1. **Automated Documentation Indexing:** Generate searchable, browsable index of all documentation with metadata-driven navigation
2. **Metadata Standardization:** Establish and enforce YAML frontmatter metadata across all documentation files
3. **Intelligent Archival:** Fully automated archival workflow that moves completed tasks out of `/tasks` to appropriate archive locations
4. **Continuous Validation:** Pre-commit hooks and CI/CD integration to enforce organization standards and detect issues
5. **Strategic Analysis:** Quarterly agent-led audits to identify patterns, gaps, and improvement opportunities

### Secondary Goals

1. Cross-reference tracking and broken link detection
2. Documentation coverage analysis (which components lack docs)
3. Automated metadata generation from git history
4. Tag-based documentation navigation
5. Maintenance burden reduction (80% reduction in manual organization time)

### Success Criteria

- ✅ **100% Documentation Indexed:** All .md files in searchable index with metadata
- ✅ **80%+ Metadata Coverage:** YAML frontmatter in all active documentation
- ✅ **Zero Broken Links:** Automated validation prevents broken internal references
- ✅ **Tasks Directory Clean:** < 2MB (down from 5.0MB), only active tasks remain
- ✅ **Automated Archival:** Completed tasks automatically moved to archive within 24 hours
- ✅ **CI/CD Integration:** Pre-commit hooks prevent organization violations
- ✅ **Quarterly Audits:** Librarian agent provides strategic recommendations every 90 days

## Scope

### In Scope ✅

**Phase 1: Metadata Foundation**
- YAML frontmatter specification for all documentation types
- Metadata extraction from existing files (patterns A, B, C)
- Automated metadata generation from git history (created/updated dates)
- High-priority docs metadata standardization (PRDs, standards, API docs)

**Phase 2: Indexing & Validation**
- `librarian_index.py` - Documentation index generator (JSON + HTML)
- `librarian_validate.py` - File organization and metadata validator
- Cross-reference graph generation
- Broken link detection
- Pre-commit hook integration
- CI/CD pipeline checks

**Phase 3: Librarian Agent**
- `.claude/agents/librarian.md` agent specification
- Comprehensive audit capabilities (all 416+ files)
- Pattern detection and recommendation engine
- Documentation gap analysis
- Quality assessment framework
- Quarterly audit workflow

**Phase 4: Archival Automation**
- `librarian_archive.py` - Fully automated archival workflow
- Intelligent detection of completed tasks (status metadata + date heuristics)
- Archive structure generation (`/docs/archived/tasks/{feature-name}/`)
- Cross-reference preservation during moves
- Automatic README generation for archives
- Index updates post-archival

**Phase 5: Maintenance & Tooling**
- `librarian_metadata.py` - Metadata extraction and enhancement
- Claude Code slash commands (`/librarian` suite)
- Monthly validation runs (automated)
- Quarterly agent audits (scheduled)
- Continuous improvement based on metrics

**Python File Documentation:**
- Establish structured docstring standards (Google/NumPy style)
- Narrative docstrings with embedded metadata sections
- No separate YAML files for Python code

**Archive Strategy:**
- Completed tasks moved to `/docs/archived/tasks/{feature-name}/`
- Templates moved to `/docs/templates/tasks/`
- Git history preserved with `git mv`

**Automation Level:**
- Fully automated archival with smart detection
- Confidence scoring for archival decisions (high confidence = auto, low = review)
- Manual override capability via `--dry-run` and `--interactive` flags

### Out of Scope ❌

- Code quality analysis (separate concern - code-reviewer agent)
- Architectural refactoring (not file organization)
- Module/package reorganization (code structure changes)
- External documentation site generation (future enhancement)
- Multi-repository tracking (single repo only)
- Binary file analysis (images, PDFs - no metadata extraction)

## User Stories

### As a Developer

**Story 1: Finding Documentation**
- **Need:** I want to quickly find relevant documentation without grepping
- **Solution:** Browse generated HTML index with tag filtering and search
- **Acceptance:** Find any doc in < 30 seconds via index

**Story 2: Understanding File Currency**
- **Need:** I want to know if documentation is current or outdated
- **Solution:** All docs have status, version, and updated date in metadata
- **Acceptance:** Metadata clearly shows doc lifecycle state

**Story 3: Adding New Documentation**
- **Need:** I want to create new docs that automatically meet standards
- **Solution:** Pre-commit hook validates metadata, provides template if missing
- **Acceptance:** New docs auto-validated before commit

### As a Maintainer

**Story 4: Archive Management**
- **Need:** I want completed tasks automatically archived without manual work
- **Solution:** Automated archival runs daily, moves completed tasks to archive
- **Acceptance:** Zero manual archival work, tasks directory stays clean

**Story 5: Organization Enforcement**
- **Need:** I want file organization standards enforced automatically
- **Solution:** CI/CD pipeline fails PRs with organization violations
- **Acceptance:** No PRs merged with missing metadata or wrong file placement

**Story 6: Strategic Insights**
- **Need:** I want quarterly reports on documentation health
- **Solution:** Librarian agent generates comprehensive audit reports
- **Acceptance:** Actionable recommendations every quarter

### As a New Contributor

**Story 7: Understanding Project Structure**
- **Need:** I want to understand the documentation landscape quickly
- **Solution:** Visual documentation map with relationships and categories
- **Acceptance:** Understand doc structure in < 10 minutes

**Story 8: Contributing Documentation**
- **Need:** I want clear guidance on where files should go
- **Solution:** Standards doc + automated validation with helpful error messages
- **Acceptance:** Know where to place any new file with confidence

## Functional Requirements

### FR1: Metadata Standard & Implementation
**Priority:** P0 (Critical)

**Requirements:**

1. **YAML Frontmatter Specification:**
   ```yaml
   ---
   title: "Document Title"
   type: "standards|guide|prd|task|reference|api|architecture"
   status: "active|draft|deprecated|archived|completed"
   version: "1.0.0"  # Semantic versioning
   created: "2025-10-09"  # YYYY-MM-DD
   updated: "2025-10-09"  # YYYY-MM-DD
   author: "Author Name|Claude Sonnet X"
   tags: ["tag1", "tag2", "tag3"]  # Searchable keywords
   related:  # Optional
     - "path/to/related/file.md"
   audience: "developers|maintainers|users|all"  # Optional
   maintenance: "active|stable|deprecated"  # Optional
   ---
   ```

2. **Required Fields (All Documentation):**
   - `title`, `type`, `status`, `created`

3. **Recommended Fields:**
   - `version`, `updated`, `author`, `tags`

4. **Python Docstring Standard:**
   ```python
   """
   [Module Name]: [One-line description]

   [Detailed narrative description of module purpose,
   architecture, and key concepts]

   Metadata:
       Type: module|script|tool|test
       Status: active|experimental|deprecated
       Dependencies: key-library-1, key-library-2
       Related: path/to/related/module.py

   Author: [Name]
   Created: YYYY-MM-DD
   Updated: YYYY-MM-DD
   """
   ```

5. **Metadata Migration Strategy:**
   - Extract existing metadata from patterns A, B, C
   - Generate missing metadata from git history
   - Infer `type` from directory location
   - Detect `status` from content keywords ("✅ COMPLETED", "deprecated", etc.)

**Acceptance Criteria:**
- Metadata standard documented in `docs/standards/metadata-standard.md`
- Standard referenced in CLAUDE.md
- Validation rules implemented in `librarian_validate.py`
- 80%+ of active docs have required fields within 2 weeks

---

### FR2: Documentation Indexing System
**Priority:** P0 (Critical)

**Requirements:**

1. **Index Generator (`tools/librarian_index.py`):**
   - Scan all `.md` files recursively (excluding node_modules, .git, project_venv)
   - Extract YAML frontmatter metadata
   - Parse markdown headers for fallback metadata
   - Build hierarchical index structure
   - Generate tag-based navigation
   - Create cross-reference graph (which docs link to which)

2. **Output Formats:**
   - **JSON Index:** `docs/indexes/documentation-index.json`
     ```json
     {
       "generated": "2025-10-09T12:00:00Z",
       "total_files": 150,
       "categories": {
         "standards": [...],
         "guides": [...],
         ...
       },
       "tags": {
         "security": ["file1.md", "file2.md"],
         ...
       },
       "files": [
         {
           "path": "docs/FILE_ORGANIZATION_STANDARDS.md",
           "metadata": {...},
           "references": ["file2.md", "file3.md"],
           "referenced_by": ["file4.md"]
         }
       ]
     }
     ```

   - **HTML Index:** `docs/indexes/documentation-map.html`
     - Browsable interface with filtering by type, status, tags
     - Search functionality (client-side JavaScript)
     - Visual hierarchy tree
     - Link graph visualization (optional - future)

   - **Cross-Reference Graph:** `docs/indexes/cross-references.json`
     - Directed graph of all internal documentation links
     - Used for broken link detection and impact analysis

3. **Index Features:**
   - Type-based categorization
   - Status filtering (active, archived, deprecated)
   - Tag-based search
   - Date-based sorting (most recent, oldest)
   - Metadata completeness indicator (% of fields populated)

4. **Run Modes:**
   - `python tools/librarian_index.py` - Full regeneration
   - `python tools/librarian_index.py --incremental` - Update changed files only
   - `python tools/librarian_index.py --validate` - Check for issues without regenerating

**Acceptance Criteria:**
- Index includes 100% of .md files
- HTML index is browsable and searchable
- JSON index is valid and queryable
- Cross-reference graph is complete
- Index regeneration completes in < 2 minutes
- Incremental updates complete in < 10 seconds

---

### FR3: Validation & Enforcement System
**Priority:** P0 (Critical)

**Requirements:**

1. **Validator Script (`tools/librarian_validate.py`):**

   **Validation Checks:**
   - ✅ **Metadata Completeness:** Required fields present in YAML frontmatter
   - ✅ **File Naming:** Follows conventions (lowercase-with-hyphens for docs)
   - ✅ **File Placement:** Files in correct directories per standards
   - ✅ **Broken Links:** Internal markdown links resolve to existing files
   - ✅ **Cross-References:** Files listed in `related` field exist
   - ✅ **Status Consistency:** Archived files in /docs/archived/, completed tasks in archive
   - ✅ **Date Validity:** Dates follow YYYY-MM-DD format, created <= updated
   - ✅ **Tag Format:** Tags are lowercase, hyphenated, valid keywords

   **Output Modes:**
   - `--summary`: High-level pass/fail counts
   - `--detailed`: Per-file validation results with line numbers
   - `--errors-only`: Only show failures
   - `--fix`: Auto-fix simple issues (date formatting, tag case)

   **Exit Codes:**
   - 0: All validations passed
   - 1: Warnings present (non-blocking)
   - 2: Errors present (blocking)

2. **Pre-Commit Hook Integration:**

   **File:** `.claude/hooks/pre_commit_librarian.py`

   **Behavior:**
   - Run on all staged .md files
   - Validate metadata completeness
   - Check file naming conventions
   - Warn about missing tags
   - Block commit if required fields missing (with helpful message)

   **Example Message:**
   ```
   ❌ Metadata validation failed for: docs/new-feature-guide.md

   Missing required fields:
     - title
     - type
     - status
     - created

   Add YAML frontmatter to the top of your file:

   ---
   title: "Your Document Title"
   type: "guide"
   status: "draft"
   created: "2025-10-09"
   tags: ["feature", "guide"]
   ---

   See docs/standards/metadata-standard.md for details.
   ```

3. **CI/CD Pipeline Integration:**

   **File:** `.github/workflows/librarian-checks.yml`

   ```yaml
   name: Librarian Checks
   on: [pull_request]
   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Validate file organization
           run: python tools/librarian_validate.py --errors-only
         - name: Check for broken links
           run: python tools/librarian_validate.py --links-only
         - name: Update documentation index
           run: python tools/librarian_index.py
         - name: Commit updated index
           if: success()
           run: |
             git config user.name "Librarian Bot"
             git config user.email "librarian@bot"
             git add docs/indexes/
             git commit -m "chore: Update documentation index" || true
   ```

**Acceptance Criteria:**
- Validator detects all specified validation failures
- Pre-commit hook blocks commits with missing metadata
- CI/CD pipeline fails PRs with organization violations
- Helpful error messages guide developers to fix issues
- Auto-fix mode corrects simple issues without manual intervention

---

### FR4: Librarian Agent
**Priority:** P1 (High)

**Requirements:**

1. **Agent Specification (`.claude/agents/librarian.md`):**

   ```markdown
   You are a Librarian Agent specialized in documentation organization,
   file management, and knowledge architecture for software projects.

   **Core Responsibilities:**
   1. Comprehensive file audits (analyze all 416+ project files)
   2. Pattern detection (identify organizational anti-patterns)
   3. Strategic recommendations (reorganization, consolidation)
   4. Documentation gap analysis (missing docs for components)
   5. Quality assessment (completeness, currency, accuracy)

   **Tools Available:** Read, Grep, Glob, Bash, Edit, Write

   **Output Format:**
   Generate structured audit reports with:
   - Executive summary
   - Quantitative metrics
   - Identified patterns (positive and negative)
   - Prioritized recommendations
   - Action plan with estimated effort

   **Analysis Approach:**
   1. Scan all files systematically
   2. Extract metadata and content patterns
   3. Build relationship graph
   4. Identify anomalies and gaps
   5. Compare against standards
   6. Generate actionable recommendations
   ```

2. **Audit Capabilities:**

   **Comprehensive File Audit:**
   - Analyze all 416+ files for organization compliance
   - Identify files without metadata
   - Detect deprecated content not marked as such
   - Find duplicate or near-duplicate content
   - Assess documentation completeness per module

   **Pattern Detection:**
   - Common organizational anti-patterns
   - Emerging file naming inconsistencies
   - Documentation drift from standards
   - Archive candidates (old, completed, unused)

   **Gap Analysis:**
   - Components without documentation
   - Missing API documentation
   - Incomplete test coverage documentation
   - Broken or outdated cross-references

   **Quality Assessment:**
   - Documentation freshness (% updated in last 3 months)
   - Metadata quality score (completeness, accuracy)
   - Link integrity (broken vs. total links ratio)
   - Tag consistency and coverage

3. **Audit Report Format:**

   **File:** `docs/audits/librarian-audit-YYYY-MM-DD.md`

   ```markdown
   # Librarian Audit Report
   **Date:** 2025-10-09
   **Files Analyzed:** 416
   **Duration:** 25 minutes

   ## Executive Summary
   [High-level findings and top 3 recommendations]

   ## Quantitative Metrics
   - Documentation files: 150
   - Metadata coverage: 82% (+15% from last audit)
   - Broken links: 3 (-12 from last audit)
   - Archive candidates: 15 files
   - Documentation gaps: 8 modules

   ## Findings
   ### Positive Patterns
   - [What's working well]

   ### Issues Identified
   - [Priority 1 issues]
   - [Priority 2 issues]

   ## Recommendations
   1. [Top priority recommendation with rationale]
   2. [Second priority...]

   ## Action Plan
   | Action | Effort | Impact | Priority |
   |--------|--------|--------|----------|
   | ... | ... | ... | ... |
   ```

4. **Invocation Methods:**

   - **Slash Command:** `/librarian audit`
   - **Scheduled:** Quarterly (every 90 days)
   - **On-Demand:** After major feature merges
   - **Agent Tool:** `Task(subagent_type="librarian", prompt="...")`

**Acceptance Criteria:**
- Agent analyzes 400+ files in < 30 minutes
- Audit report includes quantitative metrics and actionable recommendations
- Pattern detection identifies at least 3 meaningful insights per audit
- Recommendations are prioritized by impact/effort
- Quarterly audits run automatically (triggered via scheduled task)

---

### FR5: Automated Archival System
**Priority:** P1 (High)

**Requirements:**

1. **Archival Script (`tools/librarian_archive.py`):**

   **Detection Logic (Smart Archival):**

   ```python
   def should_archive(file_path: str, metadata: dict) -> tuple[bool, float, str]:
       """
       Determine if file should be archived.

       Returns:
           (should_archive, confidence, reason)
       """
       confidence = 0.0
       reasons = []

       # Rule 1: Explicit status (highest confidence)
       if metadata.get('status') == 'completed':
           confidence += 0.7
           reasons.append("Status: completed")

       if metadata.get('status') == 'archived':
           confidence += 0.9
           reasons.append("Status: archived")

       # Rule 2: Feature branch merged
       if is_feature_branch_merged(metadata.get('feature_branch')):
           confidence += 0.5
           reasons.append("Feature branch merged")

       # Rule 3: Age + no recent updates
       age_days = days_since_created(metadata.get('created'))
       update_days = days_since_updated(metadata.get('updated'))

       if age_days > 90 and update_days > 60:
           confidence += 0.3
           reasons.append(f"No updates in {update_days} days")

       # Rule 4: Content markers
       content = read_file(file_path)
       if re.search(r'✅\s*COMPLETED', content):
           confidence += 0.4
           reasons.append("Contains completion marker")

       # Rule 5: File location heuristics
       if '/tasks/' in file_path and metadata.get('type') == 'prd':
           if 'prd-' in file_path.lower():
               confidence += 0.2
               reasons.append("PRD in tasks directory")

       # Decision threshold
       should_archive = confidence >= 0.7

       return should_archive, confidence, "; ".join(reasons)
   ```

   **Archive Destination Logic:**

   ```python
   def determine_archive_location(file_path: str, metadata: dict) -> str:
       """Determine appropriate archive location."""

       # PRDs and tasks -> /docs/archived/tasks/{feature-name}/
       if metadata.get('type') in ['prd', 'task']:
           feature = extract_feature_name(metadata, file_path)
           return f"docs/archived/tasks/{feature}/"

       # Migration docs -> /docs/archived/migrations/
       if 'migration' in metadata.get('tags', []):
           return "docs/archived/migrations/"

       # Component-specific -> /docs/archived/component_docs/
       if metadata.get('type') == 'component':
           return "docs/archived/component_docs/"

       # Default
       return "docs/archived/general/"
   ```

   **Archive Operations:**
   - Create archive directory structure
   - Generate archive README with context
   - Move files with `git mv` (preserve history)
   - Update cross-references in archived files
   - Update documentation index
   - Log archival operation

2. **Run Modes:**

   ```bash
   # Dry run (show what would be archived)
   python tools/librarian_archive.py --dry-run

   # Interactive mode (manual approval)
   python tools/librarian_archive.py --interactive

   # Fully automated (confidence >= 0.7)
   python tools/librarian_archive.py --auto

   # Specific feature
   python tools/librarian_archive.py --feature feature-name

   # Force archive specific files
   python tools/librarian_archive.py --force file1.md file2.md
   ```

3. **Archive README Generation:**

   **Auto-generated:** `docs/archived/tasks/{feature-name}/README.md`

   ```markdown
   # Archive: {Feature Name}

   **Archived:** {date}
   **Original Location:** /tasks/{files}
   **Reason:** {archival reason}

   ## Files in This Archive
   - `prd.md` - Product requirements document
   - `cleanup-summary.md` - Implementation summary
   - `references.txt` - File references

   ## Context
   {Extracted from PRD or metadata}

   ## Related Active Documentation
   - [Link to current implementation if applicable]

   ## Branch Status
   - Feature Branch: {branch name}
   - Status: {merged|abandoned|completed}
   - Merge Date: {date}
   ```

4. **Scheduled Execution:**

   **Daily Run (GitHub Actions):**
   ```yaml
   # .github/workflows/librarian-archive.yml
   name: Automated Archival
   on:
     schedule:
       - cron: "0 2 * * *"  # Daily at 2 AM UTC
   jobs:
     archive:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Run archival
           run: python tools/librarian_archive.py --auto
         - name: Commit changes
           run: |
             git config user.name "Librarian Bot"
             git config user.email "librarian@bot"
             git add .
             git commit -m "chore: Automated archival of completed tasks" || true
             git push
   ```

**Acceptance Criteria:**
- Archival script correctly identifies completed tasks (90%+ accuracy)
- Confidence scoring prevents false positives (< 5% error rate)
- Archive structure is logical and discoverable
- Git history preserved for all moved files
- Cross-references updated automatically
- Archive READMEs provide sufficient context
- `/tasks` directory maintained at < 2MB
- Daily automated runs complete without errors

---

### FR6: Metadata Extraction & Enhancement
**Priority:** P2 (Medium)

**Requirements:**

1. **Metadata Tool (`tools/librarian_metadata.py`):**

   **Capabilities:**

   - **Extract Existing Metadata:**
     - Parse Pattern A (structured PRD headers)
     - Parse Pattern B (technical doc headers)
     - Extract embedded metadata from content

   - **Generate Missing Metadata:**
     - `created`: From git history (first commit)
     - `updated`: From git history (last commit)
     - `author`: From git blame (primary contributor)
     - `type`: Infer from directory location
     - `status`: Detect from content markers

   - **Enhance Metadata:**
     - Add missing tags based on content analysis
     - Suggest related files based on cross-references
     - Auto-populate version from git tags

   - **Standardize Metadata:**
     - Convert existing patterns to YAML frontmatter
     - Preserve human-readable markdown headers
     - Normalize date formats
     - Fix common issues (case, formatting)

2. **Operation Modes:**

   ```bash
   # Scan and report metadata coverage
   python tools/librarian_metadata.py --scan

   # Extract metadata from specific file
   python tools/librarian_metadata.py --extract file.md

   # Generate missing metadata for file
   python tools/librarian_metadata.py --generate file.md

   # Batch process all files
   python tools/librarian_metadata.py --batch --type prd

   # Interactive enhancement
   python tools/librarian_metadata.py --enhance file.md --interactive
   ```

3. **Output Format:**

   **Scan Report:**
   ```
   Metadata Coverage Report
   ========================
   Total files analyzed: 150

   Metadata completeness:
   - Full metadata (100%): 45 files (30%)
   - Partial metadata (50-99%): 60 files (40%)
   - Minimal metadata (1-49%): 30 files (20%)
   - No metadata (0%): 15 files (10%)

   Missing fields (top 5):
   1. tags: 90 files
   2. updated: 75 files
   3. version: 70 files
   4. author: 65 files
   5. audience: 120 files

   Recommendations:
   - Run batch generation: python tools/librarian_metadata.py --batch
   - Focus on high-priority docs first (PRDs, standards)
   ```

**Acceptance Criteria:**
- Tool correctly extracts existing metadata patterns (95%+ accuracy)
- Git history metadata generation is accurate
- Type inference matches actual document purpose (90%+ accuracy)
- Batch processing completes without errors
- Enhanced metadata improves discoverability

---

### FR7: Claude Code Integration
**Priority:** P2 (Medium)

**Requirements:**

1. **Slash Commands (`.claude/commands/librarian.md`):**

   ```markdown
   # Librarian Commands

   ## Available Commands

   ### /librarian index
   Regenerate the documentation index.

   Usage: `/librarian index [--incremental]`

   ### /librarian validate
   Validate file organization and metadata.

   Usage: `/librarian validate [--errors-only] [--fix]`

   ### /librarian audit
   Launch librarian agent for comprehensive audit.

   Usage: `/librarian audit`

   ### /librarian archive
   Run interactive archival workflow.

   Usage: `/librarian archive [--dry-run] [--auto]`

   ### /librarian metadata
   Scan or enhance file metadata.

   Usage: `/librarian metadata [--scan] [--enhance <file>]`

   ### /librarian status
   Show librarian system status and metrics.

   Usage: `/librarian status`
   ```

2. **Status Command Output:**

   ```markdown
   ## Librarian System Status

   **Last Index Update:** 2 hours ago
   **Last Validation:** 15 minutes ago (0 errors)
   **Last Archival:** Yesterday at 2:00 AM (3 files archived)
   **Last Agent Audit:** 45 days ago

   ### Metrics
   - Total documentation files: 150
   - Metadata coverage: 82%
   - Broken links: 0
   - Archive candidates: 5 files
   - Tasks directory size: 1.8 MB

   ### Next Scheduled Actions
   - Archival: Tonight at 2:00 AM
   - Validation: Continuous (pre-commit)
   - Agent Audit: In 45 days (2025-11-23)

   ### Quick Actions
   - Run validation: `/librarian validate`
   - Preview archival: `/librarian archive --dry-run`
   - View index: Open `docs/indexes/documentation-map.html`
   ```

**Acceptance Criteria:**
- All slash commands execute correctly
- Status command shows current metrics
- Commands provide helpful output and error messages
- Integration with existing Claude Code workflow

---

## Technical Approach

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Librarian System                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Metadata    │  │   Indexing   │  │  Validation  │    │
│  │  Extraction  │  │    Engine    │  │    Engine    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            │                               │
│                    ┌───────▼────────┐                      │
│                    │  Metadata DB   │                      │
│                    │   (JSON Index)  │                      │
│                    └───────┬────────┘                      │
│                            │                               │
│         ┌──────────────────┼──────────────────┐            │
│         │                  │                  │            │
│  ┌──────▼──────┐  ┌────────▼────────┐  ┌─────▼──────┐    │
│  │  Archival   │  │   Librarian     │  │   Claude   │    │
│  │  Automation │  │     Agent       │  │    Code    │    │
│  └─────────────┘  └─────────────────┘  └────────────┘    │
│         │                  │                  │            │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          │         ┌────────▼────────┐         │
          │         │   Git Repository │         │
          │         │   File System    │         │
          └────────►└──────────────────┘◄────────┘
                            │
                    ┌───────▼────────┐
                    │  CI/CD Pipeline │
                    │  Pre-commit     │
                    └─────────────────┘
```

### Technology Stack

**Language:** Python 3.11+

**Core Libraries:**
- **PyYAML:** YAML frontmatter parsing
- **Markdown:** Markdown parsing and manipulation
- **GitPython:** Git history extraction
- **Jinja2:** HTML template generation (for documentation map)
- **pathlib:** Path manipulation
- **json:** Index storage

**Development Tools:**
- **Black:** Code formatting
- **Flake8:** Linting
- **pytest:** Testing (unit tests for validators)

**CI/CD:**
- **GitHub Actions:** Automated validation and archival
- **Pre-commit hooks:** Local validation

### File Structure

```
/workspace/
├── tools/
│   ├── librarian_index.py          # Index generator
│   ├── librarian_validate.py       # Validator
│   ├── librarian_archive.py        # Archival automation
│   ├── librarian_metadata.py       # Metadata extraction
│   └── librarian_common.py         # Shared utilities
├── .claude/
│   ├── agents/
│   │   └── librarian.md            # Agent specification
│   ├── commands/
│   │   └── librarian.md            # Slash commands
│   └── hooks/
│       └── pre_commit_librarian.py # Pre-commit hook
├── docs/
│   ├── indexes/
│   │   ├── documentation-index.json
│   │   ├── documentation-map.html
│   │   └── cross-references.json
│   ├── audits/
│   │   └── librarian-audit-YYYY-MM-DD.md
│   ├── standards/
│   │   └── metadata-standard.md
│   └── archived/
│       └── tasks/
│           └── {feature-name}/
│               ├── README.md
│               └── [archived files]
├── .github/
│   └── workflows/
│       ├── librarian-checks.yml
│       └── librarian-archive.yml
└── tests/
    └── librarian/
        ├── test_metadata.py
        ├── test_index.py
        ├── test_validate.py
        └── test_archive.py
```

### Data Model

**Documentation Index Structure:**

```json
{
  "generated": "2025-10-09T12:00:00Z",
  "version": "1.0.0",
  "statistics": {
    "total_files": 150,
    "by_type": {"prd": 20, "guide": 45, "api": 15, ...},
    "by_status": {"active": 120, "archived": 25, "deprecated": 5},
    "metadata_coverage": 0.82
  },
  "categories": {
    "standards": [...],
    "guides": [...],
    "prd": [...],
    "api": [...],
    "architecture": [...]
  },
  "tags": {
    "security": ["file1.md", "file2.md"],
    "database": ["file3.md"],
    ...
  },
  "files": [
    {
      "path": "docs/FILE_ORGANIZATION_STANDARDS.md",
      "metadata": {
        "title": "File Organization Standards",
        "type": "standards",
        "status": "active",
        "version": "1.0",
        "created": "2025-10-08",
        "updated": "2025-10-08",
        "tags": ["organization", "standards", "file-management"],
        "author": "Claude Sonnet 4.5"
      },
      "references": ["docs/workflows/branch-review-workflow.md"],
      "referenced_by": ["tasks/file-organization-audit/prd.md"],
      "metadata_completeness": 0.9,
      "last_git_update": "2025-10-08T15:30:00Z"
    }
  ],
  "cross_references": {
    "file1.md": ["file2.md", "file3.md"],
    ...
  }
}
```

### Key Algorithms

#### 1. Archival Confidence Scoring

```python
def calculate_archival_confidence(file_path: str, metadata: dict, content: str) -> float:
    """
    Multi-factor confidence scoring for archival decisions.

    Factors:
    - Status metadata (0.7 weight)
    - Feature branch merge status (0.5 weight)
    - Age and staleness (0.3 weight)
    - Content markers (0.4 weight)
    - Location heuristics (0.2 weight)

    Returns confidence score 0.0 - 1.0
    Threshold for auto-archival: >= 0.7
    """
```

#### 2. Broken Link Detection

```python
def find_broken_links(index: dict) -> list[dict]:
    """
    Detect broken internal links in documentation.

    Algorithm:
    1. Extract all markdown links: [text](path)
    2. Resolve relative paths from file location
    3. Check if target exists in index
    4. Check if target exists on filesystem
    5. Report broken links with context

    Returns list of {file, link, target, line_number}
    """
```

#### 3. Type Inference

```python
def infer_document_type(file_path: str, content: str) -> str:
    """
    Infer document type from location and content.

    Rules:
    - /tasks/ + "# PRD:" -> "prd"
    - /docs/workflows/ -> "guide"
    - /docs/api/ -> "api"
    - /docs/architecture/ -> "architecture"
    - Content analysis for ambiguous cases

    Returns: type string
    """
```

---

## Non-Functional Requirements

### NFR1: Performance
- Index generation: < 2 minutes for 200 files
- Validation: < 30 seconds for full codebase
- Archival: < 10 seconds per file
- Agent audit: < 30 minutes for 400+ files

### NFR2: Reliability
- Zero data loss during archival (git history preserved)
- Graceful failure handling (no partial states)
- Rollback capability for automated operations
- Comprehensive logging for debugging

### NFR3: Maintainability
- Modular design (separate tools for separate concerns)
- Comprehensive test coverage (80%+ for core logic)
- Clear documentation for all scripts
- Version tracking for metadata standards

### NFR4: Scalability
- Handle 1000+ files without performance degradation
- Incremental indexing for large codebases
- Efficient cross-reference graph algorithms
- Caching for repeated operations

### NFR5: Usability
- Helpful error messages with fix suggestions
- Dry-run mode for all destructive operations
- Interactive mode for manual oversight
- Clear documentation and examples

---

## Dependencies

### Internal Dependencies
- Existing file organization standards (`docs/FILE_ORGANIZATION_STANDARDS.md`)
- Git repository structure and history
- Claude Code integration (`.claude/` directory)
- Current documentation patterns

### External Dependencies
- **Python 3.11+:** Runtime environment
- **PyYAML:** YAML parsing
- **GitPython:** Git operations
- **Jinja2:** Template rendering
- **GitHub Actions:** CI/CD automation

### Tool Dependencies
- **Git:** Version control operations
- **grep/rg:** Text searching (fallback for Grep tool)
- **find:** File discovery

---

## Risks & Mitigation

### Risk 1: False Positive Archival
**Impact:** High (important docs accidentally archived)
**Probability:** Medium

**Mitigation:**
- Confidence threshold >= 0.7 for auto-archival
- Manual review mode for confidence 0.5-0.7
- Dry-run mode shows what would be archived
- Rollback capability (git history preserved)
- Weekly review of archived files report

### Risk 2: Metadata Standard Evolution
**Impact:** Medium (backward compatibility issues)
**Probability:** High

**Mitigation:**
- Version metadata standard specification
- Backward compatibility for older metadata formats
- Migration scripts for standard changes
- Deprecation period for removed fields

### Risk 3: Performance Degradation at Scale
**Impact:** Medium (slow operations reduce usability)
**Probability:** Medium

**Mitigation:**
- Incremental indexing mode
- Caching frequently accessed data
- Parallel processing for independent operations
- Performance benchmarks in test suite

### Risk 4: Adoption Resistance
**Impact:** Medium (manual workarounds if not trusted)
**Probability:** Medium

**Mitigation:**
- Gradual rollout (start with validation only)
- Clear value demonstration (time saved metrics)
- Interactive modes for oversight
- Comprehensive documentation and examples

### Risk 5: Git History Corruption
**Impact:** Critical (loss of file history)
**Probability:** Low

**Mitigation:**
- Always use `git mv` for file moves
- Test archival in dry-run first
- Automated backups before operations
- Comprehensive logging of all git operations

---

## Testing Strategy

### Unit Tests

**Metadata Extraction (`tests/librarian/test_metadata.py`):**
- Test YAML frontmatter parsing
- Test metadata inference from content
- Test git history extraction
- Test metadata validation rules

**Indexing (`tests/librarian/test_index.py`):**
- Test file discovery
- Test index generation
- Test cross-reference graph building
- Test incremental updates

**Validation (`tests/librarian/test_validate.py`):**
- Test metadata completeness checks
- Test file naming validation
- Test broken link detection
- Test status consistency checks

**Archival (`tests/librarian/test_archive.py`):**
- Test confidence scoring algorithm
- Test archive location determination
- Test README generation
- Test cross-reference updates

### Integration Tests

**End-to-End Workflows:**
- New file → validation → index update
- Completed task → archival → index update
- Broken link introduced → validation failure → fix
- Metadata missing → validation warning → enhancement

**CI/CD Pipeline:**
- Test pre-commit hooks on sample commits
- Test GitHub Actions workflows
- Test automated archival execution

### Manual Testing

**Librarian Agent:**
- Full audit on actual codebase
- Recommendation quality assessment
- Report usefulness evaluation

**User Experience:**
- Slash command usability
- Error message helpfulness
- Documentation map browsability

---

## Success Metrics

### Immediate Metrics (Post-Implementation)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Metadata Coverage** | 80%+ | % of docs with required fields |
| **Index Completeness** | 100% | All .md files in index |
| **Broken Links** | 0 | Count of broken internal links |
| **Tasks Directory Size** | < 2MB | Down from 5.0MB |
| **Validation Errors** | 0 | In active documentation |

### Ongoing Metrics (Monthly)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Documentation Freshness** | 60%+ | % updated within 3 months |
| **Organization Compliance** | 95%+ | % files following standards |
| **Archival Accuracy** | 90%+ | % correct auto-archival decisions |
| **Manual Organization Time** | < 2 hrs/month | Time spent on manual file organization |

### Quality Metrics (Quarterly)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Documentation Coverage** | 80%+ | % of modules with current docs |
| **Agent Audit Score** | 8.0+ | Librarian assessment (1-10 scale) |
| **Developer Satisfaction** | 4.0+ | Survey rating (1-5 scale) |
| **Metadata Quality** | 85%+ | Completeness × accuracy score |

### ROI Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Time to Find Doc** | ~5 min | < 1 min | Average search time |
| **Organization Time** | ~8 hrs/month | < 2 hrs/month | Manual effort |
| **Broken Link Incidents** | ~2/month | 0 | Issues reported |
| **Archive Backlog** | 5.0MB | < 500KB | Unarchived completed work |

---

## Timeline & Milestones

### Phase 1: Metadata Foundation (Week 1)
**Duration:** 5-7 days
**Owner:** Development team + AI assistance

**Tasks:**
1. Finalize metadata standard specification (1 day)
2. Create `librarian_metadata.py` - extraction tool (2 days)
3. Add metadata to high-priority docs (PRDs, standards, API) (2 days)
4. Document metadata standard in `docs/standards/metadata-standard.md` (1 day)
5. Update CLAUDE.md with metadata guidelines (1 day)

**Deliverables:**
- ✅ `docs/standards/metadata-standard.md`
- ✅ `tools/librarian_metadata.py`
- ✅ 30-40 docs with standardized metadata
- ✅ CLAUDE.md updated with metadata guidelines

**Success Criteria:**
- Metadata standard documented and approved
- Extraction tool handles all 3 existing patterns
- High-priority docs have complete metadata

---

### Phase 2: Indexing & Validation (Week 2)
**Duration:** 5-7 days
**Owner:** Development team + AI assistance

**Tasks:**
1. Create `librarian_index.py` - index generator (2 days)
   - JSON output
   - HTML output with search
   - Cross-reference graph
2. Create `librarian_validate.py` - validator (2 days)
   - Metadata checks
   - File naming checks
   - Broken link detection
3. Generate initial documentation index (1 day)
4. Set up pre-commit hooks (1 day)
5. Add CI/CD integration (1 day)

**Deliverables:**
- ✅ `tools/librarian_index.py`
- ✅ `tools/librarian_validate.py`
- ✅ `docs/indexes/documentation-index.json`
- ✅ `docs/indexes/documentation-map.html`
- ✅ `.claude/hooks/pre_commit_librarian.py`
- ✅ `.github/workflows/librarian-checks.yml`

**Success Criteria:**
- Index includes 100% of .md files
- Validation detects all specified violations
- Pre-commit hooks block invalid commits
- CI/CD pipeline runs successfully

---

### Phase 3: Librarian Agent (Week 2-3)
**Duration:** 7-10 days
**Owner:** AI development team

**Tasks:**
1. Create `.claude/agents/librarian.md` - agent spec (1 day)
2. Test agent on sample file sets (2 days)
3. Perform initial comprehensive audit (1 day)
4. Generate audit report with recommendations (1 day)
5. Review and prioritize recommendations (1 day)
6. Implement high-priority improvements (2-3 days)

**Deliverables:**
- ✅ `.claude/agents/librarian.md`
- ✅ `docs/audits/librarian-audit-2025-10-09.md`
- ✅ Prioritized improvement backlog
- ✅ Implemented high-priority improvements

**Success Criteria:**
- Agent analyzes 400+ files successfully
- Audit report provides actionable insights
- At least 3 high-value recommendations implemented

---

### Phase 4: Archival Automation (Week 3-4)
**Duration:** 7-10 days
**Owner:** Development team + AI assistance

**Tasks:**
1. Create `librarian_archive.py` - archival script (3 days)
   - Confidence scoring algorithm
   - Archive location logic
   - README generation
   - Cross-reference updates
2. Test archival on sample tasks (2 days)
3. Archive completed tasks from /tasks directory (1 day)
4. Move templates to /docs/templates/ (1 day)
5. Set up automated daily archival (1 day)
6. Update indexes (1 day)

**Deliverables:**
- ✅ `tools/librarian_archive.py`
- ✅ Clean /tasks directory (< 2MB)
- ✅ Templates in /docs/templates/tasks/
- ✅ `.github/workflows/librarian-archive.yml`
- ✅ Updated documentation indexes

**Success Criteria:**
- Archival script correctly identifies completed tasks (90%+ accuracy)
- Tasks directory reduced to < 2MB
- All archived files have README context
- Automated archival runs without errors

---

### Phase 5: Claude Code Integration & Polish (Week 4)
**Duration:** 3-5 days
**Owner:** Development team

**Tasks:**
1. Create `.claude/commands/librarian.md` - slash commands (1 day)
2. Implement `/librarian status` command (1 day)
3. Write comprehensive documentation (1 day)
4. Create usage examples (1 day)
5. Final testing and bug fixes (1 day)

**Deliverables:**
- ✅ `.claude/commands/librarian.md`
- ✅ `/librarian` slash command suite
- ✅ Comprehensive user documentation
- ✅ Usage examples and tutorials

**Success Criteria:**
- All slash commands work correctly
- Status command shows accurate metrics
- Documentation is clear and helpful

---

### Phase 6: Maintenance & Monitoring (Ongoing)
**Duration:** Continuous
**Owner:** Development team

**Tasks:**
- Weekly validation runs review
- Monthly archival review (check for false positives)
- Quarterly agent audits
- Continuous metadata improvements
- Standard refinements based on usage

**Deliverables:**
- Monthly health reports
- Quarterly audit reports
- Standard updates as needed

**Success Criteria:**
- Metrics tracked and reported
- Issues identified and addressed promptly
- System evolves with project needs

---

## Deliverables Summary

### Code Deliverables

1. **Tools (5 scripts):**
   - `tools/librarian_index.py`
   - `tools/librarian_validate.py`
   - `tools/librarian_archive.py`
   - `tools/librarian_metadata.py`
   - `tools/librarian_common.py` (shared utilities)

2. **Claude Code Integration:**
   - `.claude/agents/librarian.md`
   - `.claude/commands/librarian.md`
   - `.claude/hooks/pre_commit_librarian.py`

3. **CI/CD Workflows:**
   - `.github/workflows/librarian-checks.yml`
   - `.github/workflows/librarian-archive.yml`

4. **Tests:**
   - `tests/librarian/test_metadata.py`
   - `tests/librarian/test_index.py`
   - `tests/librarian/test_validate.py`
   - `tests/librarian/test_archive.py`

### Documentation Deliverables

1. **Standards:**
   - `docs/standards/metadata-standard.md`
   - `docs/FILE_ORGANIZATION_STANDARDS.md` (updated)

2. **Indexes:**
   - `docs/indexes/documentation-index.json`
   - `docs/indexes/documentation-map.html`
   - `docs/indexes/cross-references.json`

3. **Audits:**
   - `docs/audits/librarian-audit-YYYY-MM-DD.md` (quarterly)

4. **Guides:**
   - `docs/workflows/librarian-usage-guide.md`
   - `docs/workflows/metadata-best-practices.md`

### Operational Deliverables

1. **Clean File Structure:**
   - /tasks directory < 2MB (active tasks only)
   - Templates in /docs/templates/tasks/
   - Completed work in /docs/archived/tasks/{feature}/

2. **Metadata Enhancement:**
   - 80%+ of docs with YAML frontmatter
   - Required fields populated
   - Tags for discoverability

3. **Automated Processes:**
   - Daily archival runs
   - Continuous validation (pre-commit + CI)
   - Quarterly audits

---

## Future Enhancements

### Not in Current Scope - Potential Follow-ups

**Phase 2 Enhancements (3-6 months):**
1. **Documentation Site Generator:**
   - Static site generation from index
   - Advanced search with filters
   - Visual link graph exploration

2. **Advanced Analytics:**
   - Documentation usage tracking
   - Popular vs. unused docs
   - Stale content detection (no access in 6+ months)

3. **Smart Templates:**
   - Context-aware document templates
   - Auto-filled metadata from git/user context
   - Template versioning

4. **Multi-Repository Support:**
   - Unified index across repos
   - Cross-repo link validation
   - Shared documentation discovery

5. **AI-Enhanced Metadata:**
   - LLM-generated summaries for docs without descriptions
   - Automatic tag suggestions from content
   - Related document recommendations

**Phase 3 Enhancements (6-12 months):**
1. **Documentation Quality Scoring:**
   - Readability analysis
   - Completeness scoring
   - Actionable improvement suggestions

2. **Automated Documentation Generation:**
   - Generate API docs from code
   - Auto-update docs from code changes
   - Docstring → markdown conversion

3. **Knowledge Graph:**
   - Semantic relationships between docs
   - Concept clustering
   - Gap analysis (what concepts lack docs)

---

## Approval & Sign-off

**Prepared by:** Claude Sonnet 4.5
**Date:** October 9, 2025
**Review Status:** Ready for implementation
**Approval Required:** User approval to proceed with task generation

---

## Open Questions Resolved

### User Decisions Captured

1. **Python Metadata Scope:**
   - **Decision:** Narrative docstrings with embedded metadata section (not separate YAML)
   - **Rationale:** Keeps code readable, metadata accessible but not intrusive

2. **Archive Strategy:**
   - **Decision:** Move completed tasks to `/docs/archived/tasks/{feature-name}/`
   - **Rationale:** Keep /tasks clean, preserve context in dedicated archives

3. **Automation Level:**
   - **Decision:** Fully automated archival with smart detection
   - **Rationale:** Confidence scoring prevents false positives, dry-run available for review

4. **Implementation Scope:**
   - **Decision:** Full roadmap (all 6 phases)
   - **Rationale:** Comprehensive solution, phased approach manages complexity

---

## Next Steps

1. **User Review & Approval:**
   - Review PRD for completeness
   - Approve scope and approach
   - Confirm timeline is acceptable

2. **Task Generation:**
   - Generate detailed task list from PRD
   - Break down phases into actionable items
   - Assign priorities and dependencies

3. **Implementation Kickoff:**
   - Begin Phase 1: Metadata Foundation
   - Set up development environment
   - Create initial file structure

---

**Ready to proceed with Phase 2: Task Generation?**
