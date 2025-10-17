# PRD: Librarian Agent Enhancement System

**Status:** Active
**Priority:** P1
**Effort:** 3-4 weeks
**Owner:** Platform Team
**Created:** 2025-10-12

---

## Problem Statement

The current librarian agent operates in **audit-only mode** (quarterly reports), but development agents need **real-time assistance** with:

1. **File placement decisions** - Where to create new files per FILE_ORGANIZATION_STANDARDS.md
2. **Document discovery** - Finding relevant files without extensive grep/glob iterations
3. **Standards enforcement** - Preventing violations before they occur

**Evidence of Problem:**
- 29 markdown files in root directory (should be ~10)
- Files like `BRANCH_STATUS.md`, `COMPLETION_SUMMARY.md` violate standards
- Agents spend significant time searching for relevant documentation
- Standards violations discovered reactively (quarterly audits)

---

## Goals & Success Criteria

### Primary Goals
1. **Prevent file placement violations** at creation time (not after)
2. **Reduce document discovery time** by 30%+
3. **Enforce standards automatically** via pre-commit validation

### Success Metrics
- Root directory files: 29 → 10 (66% reduction)
- Standards violations: <5 per month
- Agent grep/glob iterations: 30% reduction
- Pre-commit hook blocks violations: 100% catch rate

---

## Solution Overview

Implement a **hybrid MIS (Management Information Systems) approach** with three layers:

### Layer 1: Scripts (Deterministic Operations)
Fast, rule-based validation and data collection:
- Metadata validation (YAML frontmatter)
- File location validation (against standards)
- Link validation (broken link detection)
- Document catalog indexing
- Metrics collection

### Layer 2: Librarian Agent (Contextual Intelligence)
Judgment-based operations using scripts as tools:
- File placement recommendations (content analysis)
- Intelligent document discovery (semantic search)
- Gap analysis and prioritization
- Audit report generation

### Layer 3: Automation (Enforcement)
- Pre-commit hooks (block violations)
- CI/CD checks (documentation coverage)
- Scheduled archival (stale file cleanup)

---

## Detailed Requirements

### Phase 1: Script Foundation (Week 1)

#### R1.1: Metadata Validation Script
**Purpose:** Validate YAML frontmatter in markdown files

**Required fields:**
```yaml
---
title: string
type: [technical_doc, api_spec, architecture, process, status_report]
component: [database, email_integration, scraping, etc.]
status: [draft, active, review, archived, deprecated]
tags: [array of keywords]
owner: string (optional)
related: [array of file paths] (optional)
created: date (optional)
updated: date (optional)
---
```

**Output:** Pass/fail with specific errors and suggestions

**Usage:**
```bash
python tools/validate_metadata.py <file_path>
python tools/validate_metadata.py --all
python tools/validate_metadata.py --fix <file_path>  # Auto-add template
```

---

#### R1.2: File Location Validation Script
**Purpose:** Check if file placement complies with FILE_ORGANIZATION_STANDARDS.md

**Rules from standards:**
- Branch status files → `/docs/git_workflow/branch-status/`
- Migration docs → `/docs/archived/migrations/`
- Test files → `/tests/unit/` or `/tests/integration/` or `/tests/e2e/`
- Module code → `/modules/<module-name>/`
- Scripts → `/scripts/`
- Root → Only essential files (README, CLAUDE.md, app_modular.py, etc.)

**Output:** Pass/fail with suggested correct location

**Usage:**
```bash
python tools/validate_location.py <file_path>
python tools/validate_location.py --scan-root  # Find root violations
```

---

#### R1.3: Link Validation Script
**Purpose:** Find broken internal links in markdown files

**Checks:**
- Relative links resolve to existing files
- Absolute links within project exist
- Skip external URLs (http/https)

**Output:** List of broken links with source file and line numbers

**Usage:**
```bash
python tools/validate_links.py <file_path>
python tools/validate_links.py --all
```

---

#### R1.4: Document Catalog Builder
**Purpose:** Build searchable index of all documentation

**Database schema (SQLite):**
```sql
CREATE TABLE document_catalog (
    id TEXT PRIMARY KEY,
    file_path TEXT UNIQUE,
    title TEXT,
    type TEXT,
    component TEXT,
    status TEXT,
    tags TEXT,  -- JSON array
    content_summary TEXT,
    word_count INTEGER,
    last_modified INTEGER,  -- Unix timestamp
    created INTEGER
);

CREATE INDEX idx_component ON document_catalog(component);
CREATE INDEX idx_type ON document_catalog(type);
CREATE INDEX idx_status ON document_catalog(status);
```

**Indexing logic:**
- Extract metadata from YAML frontmatter
- Generate summary from first paragraph
- Count words for complexity assessment
- Store file timestamps

**Usage:**
```bash
python tools/build_index.py  # Rebuild entire index
python tools/build_index.py --incremental  # Update changed files only
```

---

#### R1.5: Metrics Collection Script
**Purpose:** Gather quantitative metrics for reports

**Metrics collected:**
```python
{
    'total_docs': int,
    'total_code_files': int,
    'docs_with_metadata': int,
    'metadata_coverage_pct': float,
    'broken_links_count': int,
    'stale_docs_count': int,  # >90 days
    'archive_candidates': int,  # >180 days
    'root_violations': int,
    'avg_doc_age_days': float,
    'docs_by_component': dict,
    'docs_by_type': dict,
    'undocumented_modules': list
}
```

**Usage:**
```bash
python tools/collect_metrics.py --json
python tools/collect_metrics.py --human-readable
```

---

### Phase 2: Document Catalog & Query (Week 2)

#### R2.1: Catalog Query Script
**Purpose:** Search document catalog with filters

**Query capabilities:**
```bash
# Keyword search
python tools/query_catalog.py --keywords "database schema"

# Component filter
python tools/query_catalog.py --component database --type guide

# Status filter
python tools/query_catalog.py --status active

# Combined
python tools/query_catalog.py --component email --keywords "oauth" --type technical_doc
```

**Output format:**
```
Found 3 documents:

1. docs/component_docs/gmail_oauth_integration.md
   Type: technical_doc | Component: email_integration
   Summary: Gmail OAuth 2.0 integration setup and configuration...

2. docs/api/email-api.md
   Type: api_spec | Component: email_integration
   Summary: REST API for email operations including OAuth...

3. docs/integrations/oauth-setup.md
   Type: guide | Component: security
   Summary: General OAuth 2.0 setup guide for all integrations...
```

---

#### R2.2: Tag Suggestion Script
**Purpose:** Extract keywords from content for auto-tagging

**Algorithm:**
- TF-IDF keyword extraction
- Filter by relevance threshold
- Suggest 3-7 tags per document

**Usage:**
```bash
python tools/suggest_tags.py <file_path>
# Output: [postgresql, docker, configuration, connection]
```

---

### Phase 3: Librarian Agent Enhancement (Week 3)

#### R3.1: File Placement Advisor
**Purpose:** Recommend file location based on content and context

**Agent workflow:**
1. Analyze description/content preview
2. Run `validate_location.py` for obvious violations
3. Apply decision tree from FILE_ORGANIZATION_STANDARDS.md
4. Check git context (branch name, recent commits)
5. Return recommended path with rationale

**Integration pattern:**
```
Agent needs to create file
  ↓
Agent invokes librarian with description + preview
  ↓
Librarian analyzes context
  ↓
Returns: "/docs/git_workflow/branch-status/feature-name.md"
  ↓
Agent creates file at recommended location
```

**Update CLAUDE.md:**
```markdown
**File Creation Policy:**
Before creating documentation files, consult librarian for placement:
1. Describe file purpose
2. Provide content preview (first 100 chars)
3. Follow librarian's recommended location
```

---

#### R3.2: Discovery Assistant
**Purpose:** Help agents find relevant documentation quickly

**Agent workflow:**
1. Receive natural language query
2. Extract keywords and concepts
3. Query document catalog (via `query_catalog.py`)
4. Rank results by relevance + recency
5. Generate brief summaries
6. Return top 5 with contextual explanations

**Example:**
```
Query: "How do I handle database schema changes?"

Agent returns:
1. docs/database-schema-workflow.md ⭐⭐⭐⭐⭐
   → Step-by-step workflow using automated tools

2. database_tools/README.md ⭐⭐⭐⭐
   → Overview of schema automation tools

3. CLAUDE.md (Database Schema Management section) ⭐⭐⭐⭐
   → Policy: Always use automated tools

4. docs/component_docs/database/database_schema_automation.md ⭐⭐⭐
   → Technical details of automation system

5. database_tools/update_schema.py ⭐⭐
   → Source code for schema automation
```

---

#### R3.3: Gap Analysis Enhancement
**Purpose:** Identify documentation gaps with prioritization

**Agent workflow:**
1. Scan `/modules` for all components
2. Query catalog for corresponding docs
3. Assess code complexity (file count, LOC)
4. Check git activity (recent commits)
5. Prioritize gaps by impact (complexity × activity)
6. Generate recommendations

**Output:**
```markdown
## Documentation Gaps

### Priority P0 (Critical)
- **modules/analytics/** - No documentation found
  - Complexity: High (15 files, 3,200 LOC)
  - Activity: Very active (23 commits last month)
  - Recommendation: Create architecture overview + API docs
  - Suggested location: /docs/component_docs/analytics/

### Priority P1 (High)
- **modules/realtime/** - Minimal documentation
  - Has: Basic README (50 words)
  - Missing: Integration guide, WebSocket API docs
  - Activity: Moderate (8 commits last month)
```

---

### Phase 4: Automation & Enforcement (Week 4)

#### R4.1: Pre-commit Hook
**Purpose:** Block commits that violate standards

**Hook script (`.git/hooks/pre-commit`):**
```bash
#!/bin/bash
# Run validation on all staged markdown files

STAGED_MD=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$')

if [ -n "$STAGED_MD" ]; then
    echo "Validating staged markdown files..."

    for file in $STAGED_MD; do
        # Check 1: Metadata
        python tools/validate_metadata.py "$file" || exit 1

        # Check 2: Location
        python tools/validate_location.py "$file" || exit 1

        # Check 3: Links
        python tools/validate_links.py "$file" || exit 1
    done

    echo "✓ All checks passed"
fi

exit 0
```

**Installation:**
```bash
cp tools/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

#### R4.2: CI/CD Documentation Check
**Purpose:** Fail builds if documentation standards violated

**GitHub Actions workflow:**
```yaml
name: Documentation Validation

on: [push, pull_request]

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate metadata
        run: python tools/validate_metadata.py --all
      - name: Check broken links
        run: python tools/validate_links.py --all
      - name: Generate coverage report
        run: python tools/collect_metrics.py --report
```

---

#### R4.3: Automated Archival
**Purpose:** Move stale files to archive automatically

**Script logic:**
```python
def find_archive_candidates():
    """Files not modified in 180 days + not referenced"""
    cutoff = datetime.now() - timedelta(days=180)
    candidates = []

    for doc in get_all_docs():
        if doc.last_modified < cutoff and not is_referenced(doc):
            candidates.append(doc)

    return candidates

def auto_archive(dry_run=True):
    """Move to appropriate archive location"""
    for doc in find_archive_candidates():
        archive_path = compute_archive_path(doc)
        if not dry_run:
            move_file(doc.path, archive_path)
            update_catalog(doc, archive_path)
```

**Scheduling (cron):**
```bash
# Run weekly
0 0 * * 0 cd /workspace && python tools/auto_archive.py --dry-run
```

---

## Implementation Plan

### Week 1: Script Foundation
- [ ] Create `tools/` directory structure
- [ ] Implement validation scripts (R1.1, R1.2, R1.3)
- [ ] Implement catalog builder (R1.4)
- [ ] Implement metrics collection (R1.5)
- [ ] Test all scripts independently

### Week 2: Document Catalog
- [ ] Design SQLite schema
- [ ] Implement catalog builder with incremental updates
- [ ] Implement query script (R2.1)
- [ ] Implement tag suggestion (R2.2)
- [ ] Build initial catalog from existing docs

### Week 3: Librarian Agent
- [ ] Update `.claude/agents/librarian.md` with new capabilities
- [ ] Implement file placement advisor workflow (R3.1)
- [ ] Implement discovery assistant workflow (R3.2)
- [ ] Enhance gap analysis (R3.3)
- [ ] Update CLAUDE.md with usage guidelines

### Week 4: Automation
- [ ] Create pre-commit hook (R4.1)
- [ ] Create CI/CD workflow (R4.2)
- [ ] Implement auto-archival script (R4.3)
- [ ] Test enforcement mechanisms
- [ ] Documentation and rollout

### Week 5: Cleanup & Rollout
- [ ] Clean up root directory (move 19 files)
- [ ] Add metadata to all existing docs
- [ ] Generate baseline metrics report
- [ ] Team training on new workflows

---

## Technical Specifications

### Technology Stack
- **Python 3.11** - Script language
- **SQLite** - Document catalog database
- **YAML** - Metadata format
- **Bash** - Pre-commit hooks

### File Structure
```
/workspace/
├── tools/
│   ├── validate_metadata.py
│   ├── validate_location.py
│   ├── validate_links.py
│   ├── build_index.py
│   ├── query_catalog.py
│   ├── suggest_tags.py
│   ├── collect_metrics.py
│   ├── auto_archive.py
│   ├── hooks/
│   │   └── pre-commit
│   └── librarian_catalog.db  (SQLite)
│
├── .claude/agents/librarian.md  (updated)
├── CLAUDE.md  (updated with policies)
└── docs/
    ├── FILE_ORGANIZATION_STANDARDS.md  (existing)
    └── librarian-usage-guide.md  (new)
```

---

## Dependencies

### Python Packages
```txt
pyyaml>=6.0        # YAML frontmatter parsing
sqlalchemy>=2.0    # Optional ORM for catalog
click>=8.0         # CLI interface
rich>=13.0         # Pretty console output
```

### External Dependencies
- Git (for pre-commit hooks)
- SQLite (included in Python)

---

## Testing Strategy

### Unit Tests
- Test each validation script with valid/invalid inputs
- Test catalog builder with sample documents
- Test query functionality with various filters

### Integration Tests
- Test pre-commit hook with real commits
- Test librarian agent workflows end-to-end
- Test CI/CD validation pipeline

### Acceptance Tests
- Validate 100% catch rate for standards violations
- Measure discovery time reduction
- Verify root directory cleanup success

---

## Risks & Mitigations

### Risk 1: Performance Impact
**Risk:** Catalog building/querying may be slow with 400+ files
**Mitigation:** Use incremental updates, SQLite indexes, cache results

### Risk 2: False Positives in Validation
**Risk:** Scripts may incorrectly flag valid files
**Mitigation:** Extensive testing, whitelist mechanism, manual override option

### Risk 3: Adoption Resistance
**Risk:** Team may bypass pre-commit hooks
**Mitigation:** Clear documentation, training, make hooks helpful not punitive

### Risk 4: Metadata Maintenance Burden
**Risk:** Keeping metadata up-to-date may be tedious
**Mitigation:** Auto-suggestion scripts, template generation, periodic audits

---

## Future Enhancements (Post-MVP)

### Phase 5: Advanced Features
- Full-text search with ranking algorithm
- Recommendation engine ("Documents similar to this")
- Usage analytics (track what docs are accessed)
- Auto-generated documentation from code
- Integration with external documentation tools

### Phase 6: Intelligence Layer
- LLM-powered semantic search
- Auto-generated summaries
- Intelligent tag suggestions using embeddings
- Predictive gap analysis

---

## Appendix

### References
- [FILE_ORGANIZATION_STANDARDS.md](/workspace/.trees/librarian-improvements/docs/FILE_ORGANIZATION_STANDARDS.md)
- [Current Librarian Agent](/workspace/.trees/librarian-improvements/.claude/agents/librarian.md)
- [Analysis Report (2025-10-12)](/workspace/.trees/librarian-improvements/docs/analysis/librarian-analysis-2025-10-12.md)

### Glossary
- **MIS**: Management Information Systems
- **Catalog**: Searchable database of documentation metadata
- **Frontmatter**: YAML metadata at top of markdown files
- **Standards**: Rules defined in FILE_ORGANIZATION_STANDARDS.md
