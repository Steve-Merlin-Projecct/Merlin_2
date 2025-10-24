---
title: "Librarian Tools Reference"
type: reference
component: workflow
status: active
tags: [librarian, tools, documentation, validation]
related:
  - docs/librarian-pre-commit-hook.md
  - docs/librarian-ci-cd-workflow.md
  - docs/automated-archival-system.md
---

# Librarian Tools Reference

**Version:** 1.0
**Last Updated:** 2025-10-24
**Purpose:** Comprehensive reference for all librarian validation and management tools

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Tools](#validation-tools)
   - [validate_metadata.py](#validate_metadatapy)
   - [validate_location.py](#validate_locationpy)
   - [validate_links.py](#validate_linkspy)
   - [librarian_validate.py](#librarian_validatepy)
3. [Search & Discovery Tools](#search--discovery-tools)
   - [build_index.py](#build_indexpy)
   - [query_catalog.py](#query_catalogpy)
4. [Archival Tools](#archival-tools)
   - [auto_archive.py](#auto_archivepy)
   - [librarian_archive.py](#librarian_archivepy)
5. [Metrics & Reporting](#metrics--reporting)
   - [collect_metrics.py](#collect_metricspy)
6. [Integration Workflows](#integration-workflows)
7. [Troubleshooting](#troubleshooting)
8. [Quick Reference](#quick-reference)

---

## Overview

The librarian toolset provides comprehensive documentation management capabilities:

- **Validation**: Ensure metadata, file placement, and links meet standards
- **Search**: Build and query searchable catalog of documentation
- **Archival**: Identify and move stale documentation
- **Metrics**: Track documentation health and coverage

### Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| **Validation** | validate_metadata.py, validate_location.py, validate_links.py, librarian_validate.py | Quality assurance |
| **Search** | build_index.py, query_catalog.py | Discovery and navigation |
| **Archival** | auto_archive.py, librarian_archive.py | Lifecycle management |
| **Metrics** | collect_metrics.py | Health tracking |

---

## Validation Tools

### validate_metadata.py

Validates YAML frontmatter in markdown files against documentation standards.

#### Usage

```bash
# Validate single file
python tools/validate_metadata.py docs/some-file.md

# Validate all files
python tools/validate_metadata.py --all

# Auto-fix missing frontmatter
python tools/validate_metadata.py --all --fix

# Validate and fix specific file
python tools/validate_metadata.py docs/file.md --fix
```

#### Options

| Option | Description |
|--------|-------------|
| `FILE_PATH` | Path to markdown file (optional) |
| `--all` | Validate all markdown files in project |
| `--fix` | Auto-fix files by adding template metadata |
| `--help` | Show help message |

#### What It Validates

**Required Fields:**
- `title` (string) - Document title
- `type` (enum) - Document type (technical_doc, api_spec, architecture, etc.)
- `status` (enum) - Document status (draft, active, review, archived, deprecated)

**Optional Fields:**
- `component` (string) - System component
- `tags` (array) - Topic tags
- `created` (date) - Creation date
- `related` (array) - Related documents

**Validation Rules:**
- YAML frontmatter must start with `---`
- Required fields must be present
- Field types must match schema (string, array, enum)
- Status values: draft, active, review, archived, deprecated
- Type values: technical_doc, api_spec, architecture, process, status_report, guide, reference, tutorial

#### Auto-Fix Behavior

When `--fix` is used on files missing frontmatter:

1. **Infers component** from directory structure:
   - `modules/email/` → `component: email`
   - `docs/component_docs/database/` → `component: database`
   - Falls back to `component: general`

2. **Infers type** from filename patterns:
   - `api` → `api_spec`
   - `architecture`, `design` → `architecture`
   - `guide`, `how-to` → `guide`
   - `status`, `report` → `status_report`
   - `process`, `workflow` → `process`
   - `reference` → `reference`
   - `tutorial` → `tutorial`
   - Default → `technical_doc`

3. **Generates title** from filename:
   - `my-doc-name.md` → `title: "My Doc Name"`

4. **Sets defaults**:
   - `status: draft`
   - `tags: []`

#### Example Output

```bash
$ python tools/validate_metadata.py --all

Scanning 519 markdown files...

✓ /workspace/docs/architecture/system-overview.md: Valid

✗ /workspace/docs/guide.md: Invalid
  Errors:
    - Missing required fields: component
    - Invalid status 'current'. Must be one of: draft, active, review, archived, deprecated

  Warnings:
    - Unexpected fields: modified

✗ /workspace/README.md: Invalid
  Errors:
    - Missing YAML frontmatter (must start with ---)

============================================================
Results: 374 valid, 145 invalid
```

#### Integration

- **Pre-commit hook**: Runs automatically before commits
- **CI/CD**: GitHub Actions workflow validates on push
- **Manual**: Run before catalog rebuild

#### Related Documentation

- Implementation: `tools/validate_metadata.py` (lines 1-420)
- Pre-commit hook: `docs/librarian-pre-commit-hook.md`
- CI/CD workflow: `docs/librarian-ci-cd-workflow.md`

---

### validate_location.py

Validates file placement against `FILE_ORGANIZATION_STANDARDS.md`.

#### Usage

```bash
# Validate single file
python tools/validate_location.py docs/some-file.md

# Scan root directory for violations
python tools/validate_location.py --scan-root

# Validate all files
python tools/validate_location.py --all

# Specify project root
python tools/validate_location.py --scan-root --project-root /workspace
```

#### Options

| Option | Description |
|--------|-------------|
| `FILE_PATH` | Path to file to validate (optional) |
| `--scan-root` | Scan root directory for violations |
| `--all` | Validate all files in project |
| `--project-root PATH` | Project root directory (default: current) |
| `--help` | Show help message |

#### What It Validates

**Root Directory Rules:**
- Max 10 essential files in root
- Allowed: README.md, CLAUDE.md, CHANGELOG.md, LICENSE, .gitignore, etc.
- Violations: Arbitrary .md files, temp files, old docs

**Directory Structure Rules:**
- `docs/` - All documentation
- `tasks/` - Task-specific work
- `modules/` - Module-level docs
- `.claude/` - AI assistant configuration
- `tools/` - Utility scripts

#### Example Output

```bash
$ python tools/validate_location.py --scan-root

Root Directory Violations (53 files):
  - CONVERSION_SUMMARY.md (should be in tasks/)
  - METADATA_WORK_SYNOPSIS.md (should be in tasks/)
  - QUICKSTART.md (should be in docs/)

Recommended Actions:
  1. Move task summaries to tasks/ directory
  2. Move guides to docs/
  3. Archive old documents

Total violations: 53
```

#### Integration

- **Pre-commit hook**: Warns on root directory changes
- **CI/CD**: Reports violations in workflow
- **Manual**: Run quarterly to check compliance

---

### validate_links.py

Validates internal links in markdown files to prevent broken references.

#### Usage

```bash
# Validate single file
python tools/validate_links.py docs/some-file.md

# Validate all files
python tools/validate_links.py --all

# JSON output
python tools/validate_links.py --all --json

# Specify project root
python tools/validate_links.py --all --project-root /workspace
```

#### Options

| Option | Description |
|--------|-------------|
| `FILE_PATH` | Path to markdown file (optional) |
| `--all` | Validate all markdown files |
| `--json` | Output results as JSON |
| `--project-root PATH` | Project root directory |
| `--help` | Show help message |

#### What It Validates

**Link Types Checked:**
- `[text](relative/path.md)` - Relative links
- `[text](/absolute/path.md)` - Absolute links
- `[text](../path.md#anchor)` - Links with anchors
- `[text](path.md)` - Same-directory links

**Validation Rules:**
- Target file exists
- Path is correct (case-sensitive)
- Anchor exists (if specified)
- No circular references

**Excluded:**
- External URLs (`https://`, `http://`)
- Images (`.png`, `.jpg`, etc.)
- Assets (`.pdf`, `.zip`, etc.)

#### Example Output

```bash
$ python tools/validate_links.py --all

Validating links in 519 files...

✓ docs/architecture/system-overview.md: All links valid (12 links)

✗ docs/api/webhook-api.md: Broken links found
  Line 45: [Database Schema](../database/schema.md) - File not found
  Line 78: [Config Guide](config.md#setup) - Anchor #setup not found

✗ README.md: Broken links found
  Line 23: [Quick Start](/docs/QUICKSTART.md) - File not found (moved to docs/QUICK_START.md)

============================================================
Results: 487 valid, 32 with broken links
```

#### Integration

- **Pre-commit hook**: Validates links in staged files
- **CI/CD**: Runs on all documentation changes
- **Manual**: Run after file moves/renames

---

### librarian_validate.py

Unified validation wrapper that runs all validation checks.

#### Usage

```bash
# Run all validations
python tools/librarian_validate.py

# Validate specific files
python tools/librarian_validate.py docs/file1.md docs/file2.md

# Show errors only (no warnings)
python tools/librarian_validate.py --errors-only

# Show summary only
python tools/librarian_validate.py --summary

# Auto-fix issues (not fully implemented)
python tools/librarian_validate.py --fix
```

#### Options

| Option | Description |
|--------|-------------|
| `files` | Specific files to validate (default: all) |
| `--errors-only` | Show only errors, not warnings |
| `--summary` | Show summary only |
| `--fix` | Auto-fix simple issues (partial implementation) |
| `--help` | Show help message |

#### What It Validates

Runs comprehensive checks:
1. **Metadata validation** (via validate_metadata.py)
2. **Location validation** (via validate_location.py)
3. **Link validation** (via validate_links.py)
4. **Cross-checks** (consistency between tools)

#### Example Output

```bash
$ python tools/librarian_validate.py --summary

Running librarian validation suite...

Metadata Validation: 374 valid, 145 invalid
Location Validation: 466 valid, 53 violations
Link Validation: 487 valid, 32 broken links

Overall Status: ⚠️ WARNINGS
Errors: 230
Warnings: 53

Run without --summary for detailed output.
```

#### Integration

- **Pre-commit hook**: Primary validation tool
- **CI/CD**: Comprehensive check in workflow
- **Manual**: Use for full validation before releases

---

## Search & Discovery Tools

### build_index.py

Builds searchable SQLite catalog of documentation with full-text search.

#### Usage

```bash
# Incremental update (default - only changed files)
python tools/build_index.py

# Or explicitly
python tools/build_index.py --incremental

# Full rebuild (all files)
python tools/build_index.py --rebuild

# Custom database path
python tools/build_index.py --db-path /custom/path/catalog.db

# Specify project root
python tools/build_index.py --project-root /workspace
```

#### Options

| Option | Description |
|--------|-------------|
| `--incremental` | Update only changed files (default) |
| `--rebuild` | Rebuild entire catalog from scratch |
| `--db-path PATH` | Database file path (default: tools/librarian_catalog.db) |
| `--project-root PATH` | Project root directory |
| `--help` | Show help message |

#### How It Works

**Incremental Mode (default):**
1. Checks file modification times
2. Indexes only changed files
3. Fast (~1 second for small changes)
4. Use for regular updates

**Rebuild Mode:**
1. Deletes existing catalog
2. Indexes all markdown files
3. Slower (~5-10 seconds for 500 files)
4. Use after:
   - Bulk metadata additions
   - File reorganization
   - Archival operations
   - Database corruption

**Indexing Process:**
1. Scans all `.md` files
2. Extracts YAML frontmatter
3. Indexes full content for search
4. Creates summary from first 200 characters
5. Stores in SQLite with FTS5 full-text index

#### Example Output

```bash
$ python tools/build_index.py --rebuild

Building document catalog...

Processing 519 files...
[████████████████████████████████] 519/519

Completed: 511 indexed, 8 errors

Catalog Statistics:
  Total documents: 511
  Components: 3 (development, documentation, workflow)
  Types: 11
  Database: tools/librarian_catalog.db (2.4 MB)

Build time: 5.2 seconds
```

#### Database Schema

**SQLite tables:**
- `documents` - Full-text indexed content
- `metadata` - YAML frontmatter data
- `fts_documents` - FTS5 virtual table for search

**Storage:**
- Size: ~2-5 MB for 500 documents
- Location: `tools/librarian_catalog.db`
- Format: SQLite 3

#### Integration

- **After metadata changes**: Run incremental update
- **After archival**: Run rebuild
- **After file moves**: Run rebuild
- **Scheduled**: Weekly incremental, monthly rebuild

---

### query_catalog.py

Queries the document catalog with filtering and search capabilities.

#### Usage

```bash
# Keyword search
python tools/query_catalog.py --keywords "database schema"

# Filter by component
python tools/query_catalog.py --component development

# Filter by type
python tools/query_catalog.py --type guide

# Filter by status
python tools/query_catalog.py --status active

# Combined filters
python tools/query_catalog.py --keywords "api" --component email --type technical_doc

# Limit results
python tools/query_catalog.py --keywords "testing" --limit 5

# JSON output
python tools/query_catalog.py --keywords "docker" --json

# Hide summaries (paths only)
python tools/query_catalog.py --keywords "config" --no-summary

# List available values
python tools/query_catalog.py --list-components
python tools/query_catalog.py --list-types
python tools/query_catalog.py --list-statuses
```

#### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--keywords TEXT` | `-k` | Keywords to search (full-text) |
| `--component TEXT` | `-c` | Filter by component |
| `--type TEXT` | `-t` | Filter by document type |
| `--status TEXT` | `-s` | Filter by status |
| `--limit INTEGER` | `-l` | Maximum results (default: 10) |
| `--json` | | Output as JSON |
| `--no-summary` | | Hide content summaries |
| `--list-components` | | List all components |
| `--list-types` | | List all types |
| `--list-statuses` | | List all statuses |
| `--db-path PATH` | | Database file path |
| `--project-root PATH` | | Project root directory |

#### Search Features

**Full-Text Search:**
- Searches file content and metadata
- Ranks by relevance
- Supports multi-word queries
- Case-insensitive

**Filtering:**
- Combine multiple filters
- Exact match on component/type/status
- AND logic (all filters must match)

**Output:**
- Ranked results
- File path
- Summary (first 200 chars)
- Metadata (component, type, status)
- Match highlighting (in some modes)

#### Example Output

```bash
$ python tools/query_catalog.py --keywords "database schema" --limit 3

Searching for: "database schema"

Found 5 results:

1. docs/component_docs/database/schema.md
   Component: database | Type: reference | Status: active

   Complete database schema reference for the automated job
   application system. Includes all 32 tables with relationships,
   constraints, and field descriptions...

2. .claude/commands/db-update.md
   Component: workflow | Type: process | Status: active

   Automated database schema update workflow. Runs schema extraction,
   generates documentation, and validates consistency...

3. tasks/task-01-database-schema-extensions.md
   Component: development | Type: technical_doc | Status: archived

   Database schema extensions task for adding new tables and
   relationships to support...

(Showing 3 of 5 results)
```

#### JSON Output Example

```bash
$ python tools/query_catalog.py --keywords "api" --json | jq
```

```json
{
  "query": "api",
  "total_results": 12,
  "results": [
    {
      "file_path": "docs/api/webhook-api.md",
      "component": "api",
      "type": "api_spec",
      "status": "active",
      "title": "Webhook API",
      "summary": "Complete API specification for webhook endpoints..."
    }
  ]
}
```

#### Integration

- **Command line**: Interactive doc discovery
- **Scripts**: Pipe JSON output for automation
- **IDE integration**: Search from editor
- **Documentation portal**: Backend for search UI

---

## Archival Tools

### auto_archive.py

Age-based archival tool for moving stale documentation.

#### Usage

```bash
# Dry run (default - shows what would be archived)
python tools/auto_archive.py

# Custom threshold (90 days)
python tools/auto_archive.py --days 90

# Actually archive files
python tools/auto_archive.py --execute

# Specify project root
python tools/auto_archive.py --project-root /workspace --execute
```

#### Options

| Option | Description |
|--------|-------------|
| `--days INTEGER` | Age threshold in days (default: 180) |
| `--execute` | Actually archive files (default: dry-run) |
| `--project-root PATH` | Project root directory |
| `--help` | Show help message |

#### How It Works

**Detection Logic:**
1. Scans all `.md` files
2. Checks last modified date
3. If older than threshold (default 180 days):
   - Skip if already in archive/
   - Skip if protected file (README.md, etc.)
   - Skip if referenced in other docs
   - Add to archive candidates

**Protection Rules:**
- Never archives: README.md, CLAUDE.md, CHANGELOG.md
- Skips referenced files (link detection)
- Skips files in archive/ directories
- Skips system directories (.git, node_modules, etc.)

**Archival Process:**
1. Creates `docs/archived/` directory
2. Preserves relative path structure
3. Moves file to archive
4. Original location emptied

#### Example Output

```bash
$ python tools/auto_archive.py

Scanning for files older than 180 days...

Archive candidates:
  docs/planning/2024-q1-roadmap.md
    Reason: Not modified in 245 days and not referenced

  docs/experiments/failed-approach.md
    Reason: Not modified in 312 days and not referenced

============================================================
DRY RUN COMPLETE
Would archive: 2 files

To actually archive these files, run with --execute flag:
  python tools/auto_archive.py --execute
```

#### Integration

- **Quarterly**: Run manually every 3 months
- **Automated**: GitHub Actions (optional)
- **After archival**: Rebuild catalog
- **Metrics**: Track via collect_metrics.py

#### Full Documentation

See: `docs/automated-archival-system.md` for comprehensive guide

---

### librarian_archive.py

Intelligent archival tool with confidence scoring and interactive mode.

#### Usage

```bash
# Dry run with confidence scoring
python tools/librarian_archive.py --dry-run

# Auto-archive high confidence files (≥0.8)
python tools/librarian_archive.py --auto

# Interactive mode (prompt for each)
python tools/librarian_archive.py --interactive

# Custom confidence threshold
python tools/librarian_archive.py --auto --min-confidence 0.9
```

#### Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would be archived with scores |
| `--auto` | Auto-archive high confidence files |
| `--interactive` | Prompt for each file |
| `--min-confidence FLOAT` | Minimum confidence (0.0-1.0, default: 0.8) |
| `--help` | Show help message |

#### Confidence Scoring

Analyzes multiple signals to determine archival confidence:

**Factors (weighted):**
- Age (40%): How long since last modification
- References (30%): How many active docs reference it
- Status (20%): Metadata status field
- Activity (10%): Recent view/edit patterns

**Confidence Levels:**
- **0.9-1.0**: Very high - Safe to auto-archive
- **0.8-0.89**: High - Likely safe
- **0.6-0.79**: Medium - Review recommended
- **0.0-0.59**: Low - Keep active

#### Example Output

```bash
$ python tools/librarian_archive.py --dry-run

Analyzing documentation for archival...

High Confidence (≥0.8):
  docs/planning/2024-q1-roadmap.md (confidence: 0.95)
    - 312 days old
    - 0 references
    - Status: archived

  docs/old-design.md (confidence: 0.87)
    - 245 days old
    - 1 reference (deprecated)
    - Status: deprecated

Medium Confidence (0.6-0.79):
  docs/legacy-api.md (confidence: 0.72)
    - 189 days old
    - 3 references (2 active)
    - Status: deprecated
    - ⚠️ Still referenced by active docs

Would archive: 2 files (confidence ≥0.8)
Review needed: 1 file (confidence 0.6-0.79)
```

#### Integration

- **Quarterly reviews**: Run with --dry-run
- **Automated cleanup**: Use --auto with high threshold
- **Manual curation**: Use --interactive
- **Combined approach**: auto_archive.py for age, this for intelligence

---

## Metrics & Reporting

### collect_metrics.py

Collects comprehensive documentation and codebase metrics.

#### Usage

```bash
# Human-readable output
python tools/collect_metrics.py

# JSON output
python tools/collect_metrics.py --json

# Full report
python tools/collect_metrics.py --report

# Specify project root
python tools/collect_metrics.py --project-root /workspace --json
```

#### Options

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |
| `--report` | Generate full report (default: human-readable) |
| `--project-root PATH` | Project root directory |
| `--help` | Show help message |

#### Metrics Collected

**Documentation:**
- Total markdown files
- Files with metadata (coverage %)
- Files with valid metadata
- Files with invalid metadata
- Average document size
- Total documentation size

**Organization:**
- Root directory violations
- Files in correct locations
- Files needing relocation

**Quality:**
- Broken links count
- Files with broken links
- Link validation rate

**Archival:**
- Archive candidates (by age)
- Stale docs count (>180 days)
- Files already archived

**Components:**
- Files per component
- Coverage per component
- Top components by file count

**Types:**
- Files per type
- Coverage per type
- Type distribution

#### Example Output

**Human-Readable:**
```bash
$ python tools/collect_metrics.py

Documentation Metrics
=====================

Files:
  Total markdown files: 519
  Files with metadata: 374 (72.06%)
  Files with valid metadata: 374
  Files with validation errors: 145

Organization:
  Root directory violations: 53
  Files in correct locations: 466

Quality:
  Broken links: 32 (in 32 files)
  Link validation rate: 93.83%

Archival:
  Archive candidates: 12 (>180 days old)
  Files archived: 120

Components (top 5):
  1. general: 234 files
  2. development: 89 files
  3. documentation: 67 files
  4. workflow: 45 files
  5. email: 23 files

Types (top 5):
  1. technical_doc: 267 files
  2. status_report: 54 files
  3. guide: 32 files
  4. reference: 18 files
  5. process: 12 files
```

**JSON Output:**
```bash
$ python tools/collect_metrics.py --json | jq
```

```json
{
  "documentation": {
    "total_files": 519,
    "files_with_metadata": 374,
    "metadata_coverage": 72.06,
    "valid_metadata": 374,
    "invalid_metadata": 145
  },
  "organization": {
    "root_violations": 53,
    "correct_locations": 466
  },
  "quality": {
    "broken_links": 32,
    "files_with_broken_links": 32,
    "link_validation_rate": 93.83
  },
  "archival": {
    "archive_candidates": 12,
    "files_archived": 120
  },
  "components": {
    "general": 234,
    "development": 89,
    "documentation": 67
  },
  "types": {
    "technical_doc": 267,
    "status_report": 54,
    "guide": 32
  }
}
```

#### Integration

- **CI/CD**: Generate metrics report in workflow
- **Dashboards**: Pipe JSON to monitoring tools
- **Quarterly reviews**: Track trends over time
- **Decision making**: Guide cleanup priorities

---

## Integration Workflows

### Pre-Commit Validation

```bash
# Installed via tools/install_hooks.sh
# Runs automatically before commits

Validations run:
1. Metadata validation (errors block commit)
2. Location check (warnings only)
3. Link validation (errors block commit)
```

See: `docs/librarian-pre-commit-hook.md`

### CI/CD Pipeline

```bash
# GitHub Actions workflow: .github/workflows/validate-docs.yml

Steps:
1. Install dependencies (tools/requirements.txt)
2. Validate metadata (validate_metadata.py --all)
3. Check locations (validate_location.py --scan-root)
4. Validate links (validate_links.py --all)
5. Collect metrics (collect_metrics.py --json)
6. Upload report artifact
```

See: `docs/librarian-ci-cd-workflow.md`

### Documentation Maintenance Cycle

**Monthly:**
```bash
# Update catalog
python tools/build_index.py --incremental

# Check metrics
python tools/collect_metrics.py --report

# Review violations
python tools/validate_location.py --scan-root
```

**Quarterly:**
```bash
# Check for stale docs
python tools/auto_archive.py
python tools/librarian_archive.py --dry-run

# Fix metadata issues
python tools/validate_metadata.py --all

# Rebuild catalog
python tools/build_index.py --rebuild

# Archive if needed
python tools/auto_archive.py --execute

# Update metrics
python tools/collect_metrics.py --json > reports/metrics-$(date +%Y%m%d).json
```

**After Bulk Changes:**
```bash
# Fix metadata
python tools/validate_metadata.py --all --fix

# Validate all
python tools/librarian_validate.py

# Rebuild catalog
python tools/build_index.py --rebuild

# Verify
python tools/query_catalog.py --list-components
```

---

## Troubleshooting

### Common Issues

#### "Module 'yaml' not found"

**Problem:** PyYAML not installed

**Solution:**
```bash
pip install -r tools/requirements.txt
# Or
pip install PyYAML click
```

#### "No files found" in catalog query

**Problem:** Catalog not built or outdated

**Solution:**
```bash
python tools/build_index.py --rebuild
```

#### "Permission denied" on hooks

**Problem:** Hook not executable

**Solution:**
```bash
chmod +x .git/hooks/pre-commit
# Or
bash tools/install_hooks.sh
```

#### High number of validation errors

**Problem:** Mass metadata addition or schema change

**Solution:**
```bash
# Try auto-fix
python tools/validate_metadata.py --all --fix

# Check remaining errors
python tools/validate_metadata.py --all | grep "Errors:" | head -20
```

#### Slow catalog rebuild

**Problem:** Large number of files

**Solution:**
```bash
# Use incremental for daily updates
python tools/build_index.py --incremental

# Only rebuild when necessary
python tools/build_index.py --rebuild
```

---

## Quick Reference

### Essential Commands

```bash
# Daily/Weekly
python tools/build_index.py                    # Update catalog
python tools/validate_metadata.py --all        # Check metadata

# Before Commits
python tools/librarian_validate.py             # Full validation

# After Bulk Changes
python tools/validate_metadata.py --all --fix  # Fix metadata
python tools/build_index.py --rebuild          # Rebuild catalog

# Quarterly Maintenance
python tools/auto_archive.py                   # Check stale docs
python tools/collect_metrics.py --report       # Generate report

# Search & Discovery
python tools/query_catalog.py --keywords "api" # Search docs
python tools/query_catalog.py --list-components # List components
```

### Tool Decision Matrix

| Task | Tool | Command |
|------|------|---------|
| Check metadata | validate_metadata.py | `--all` |
| Fix metadata | validate_metadata.py | `--all --fix` |
| Check file org | validate_location.py | `--scan-root` |
| Check links | validate_links.py | `--all` |
| Full validation | librarian_validate.py | (no args) |
| Build catalog | build_index.py | `--incremental` or `--rebuild` |
| Search docs | query_catalog.py | `--keywords "term"` |
| Check stale | auto_archive.py | (no args) |
| Archive files | auto_archive.py | `--execute` |
| Get metrics | collect_metrics.py | `--json` |

### File Locations

```
tools/
├── validate_metadata.py      # Metadata validation
├── validate_location.py      # File organization
├── validate_links.py         # Link checking
├── librarian_validate.py     # Unified validation
├── build_index.py            # Catalog builder
├── query_catalog.py          # Catalog search
├── auto_archive.py           # Age-based archival
├── librarian_archive.py      # Smart archival
├── collect_metrics.py        # Metrics collection
├── librarian_catalog.db      # Search database (generated)
├── requirements.txt          # Dependencies
└── install_hooks.sh          # Hook installer
```

### Dependencies

```txt
# tools/requirements.txt
PyYAML>=6.0.1              # YAML parsing
click>=8.1.7               # CLI framework (optional)
markdown>=3.5              # Link validation (optional)
scikit-learn>=1.3.2        # Tag suggestions (optional)
```

---

## Related Documentation

1. **Pre-Commit Hook**: `docs/librarian-pre-commit-hook.md`
   - Installation, usage, integration

2. **CI/CD Workflow**: `docs/librarian-ci-cd-workflow.md`
   - GitHub Actions setup, workflow structure

3. **Archival System**: `docs/automated-archival-system.md`
   - Comprehensive archival guide

4. **File Organization**: `FILE_ORGANIZATION_STANDARDS.md`
   - Directory structure rules

5. **Metadata Schema**: `.metadata-schema.md`
   - YAML frontmatter specification

---

**Last Updated:** 2025-10-24
**Version:** 1.0
**Maintained By:** Librarian System
**Feedback:** Report issues via GitHub Issues
