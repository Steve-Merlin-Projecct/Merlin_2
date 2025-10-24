---
title: "Readme"
type: technical_doc
component: general
status: draft
tags: []
---

# Librarian Tools

**Purpose:** Validation scripts and automation tools for documentation management

**Version:** 1.0
**Created:** 2025-10-12

---

## Overview

This directory contains Python scripts that enforce documentation standards, build searchable catalogs, and automate maintenance tasks. These tools work in conjunction with the Librarian Agent to provide both deterministic validation and contextual intelligence.

---

## Tools

### Validation Scripts

#### `validate_metadata.py`
**Purpose:** Validate YAML frontmatter in markdown files

**Usage:**
```bash
# Validate single file
python tools/validate_metadata.py docs/some-file.md

# Validate all markdown files
python tools/validate_metadata.py --all

# Auto-fix by adding template
python tools/validate_metadata.py --fix docs/some-file.md
```

**Required YAML fields:**
- `title`: Document title
- `type`: One of [technical_doc, api_spec, architecture, process, status_report]
- `component`: Component name (database, email_integration, etc.)
- `status`: One of [draft, active, review, archived, deprecated]

**Optional fields:**
- `tags`: Array of keywords
- `owner`: Team or person responsible
- `related`: Array of related file paths
- `created`: Creation date
- `updated`: Last update date

---

#### `validate_location.py`
**Purpose:** Check if file placement complies with FILE_ORGANIZATION_STANDARDS.md

**Usage:**
```bash
# Validate single file
python tools/validate_location.py docs/some-file.md

# Scan root directory for violations
python tools/validate_location.py --scan-root

# Check entire project
python tools/validate_location.py --all
```

**Rules enforced:**
- Branch status files → `/docs/git_workflow/branch-status/`
- Migration docs → `/docs/archived/migrations/`
- Test files → `/tests/{unit,integration,e2e}/`
- Root directory → Only essential files allowed

---

#### `validate_links.py`
**Purpose:** Find broken internal links in markdown files

**Usage:**
```bash
# Check single file
python tools/validate_links.py docs/some-file.md

# Check all markdown files
python tools/validate_links.py --all

# Output JSON format
python tools/validate_links.py --all --json
```

**Checks:**
- Relative links resolve to existing files
- Absolute internal links exist
- Skips external URLs (http/https/mailto)

---

### Document Catalog

#### `build_index.py`
**Purpose:** Build searchable SQLite database of all documentation

**Usage:**
```bash
# Build full index
python tools/build_index.py

# Incremental update (only changed files)
python tools/build_index.py --incremental

# Rebuild from scratch
python tools/build_index.py --rebuild
```

**Database location:** `tools/librarian_catalog.db`

**What's indexed:**
- File path and metadata
- Title, type, component, status, tags
- Content summary (first paragraph)
- Word count and timestamps

---

#### `query_catalog.py`
**Purpose:** Search document catalog with filters

**Usage:**
```bash
# Keyword search
python tools/query_catalog.py --keywords "database schema"

# Component filter
python tools/query_catalog.py --component database

# Type filter
python tools/query_catalog.py --type guide

# Combined filters
python tools/query_catalog.py --component email --keywords "oauth" --type technical_doc

# Limit results
python tools/query_catalog.py --keywords "testing" --limit 5
```

**Output:** Formatted list with title, type, component, and summary

---

#### `suggest_tags.py`
**Purpose:** Extract keywords from content for auto-tagging

**Usage:**
```bash
# Suggest tags for file
python tools/suggest_tags.py docs/some-file.md

# Output as YAML array
python tools/suggest_tags.py docs/some-file.md --yaml
```

**Algorithm:** TF-IDF keyword extraction with relevance filtering

---

### Metrics & Reporting

#### `collect_metrics.py`
**Purpose:** Gather quantitative metrics about documentation

**Usage:**
```bash
# Human-readable output
python tools/collect_metrics.py

# JSON output
python tools/collect_metrics.py --json

# Generate full report
python tools/collect_metrics.py --report
```

**Metrics collected:**
- Total docs and code files
- Metadata coverage percentage
- Broken links count
- Stale docs (>90 days)
- Archive candidates (>180 days)
- Root directory violations
- Docs by component and type
- Undocumented modules

---

### Maintenance

#### `auto_archive.py`
**Purpose:** Move stale files to archive automatically

**Usage:**
```bash
# Dry run (default - shows what would be archived)
python tools/auto_archive.py

# Actually move files
python tools/auto_archive.py --execute

# Custom age threshold (days)
python tools/auto_archive.py --days 90
```

**Criteria:** Files not modified in 180 days AND not referenced elsewhere

---

## Pre-commit Hook

**Location:** `tools/hooks/pre-commit`

**Installation:**
```bash
cp tools/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**What it does:**
- Validates metadata in staged markdown files
- Checks file placement compliance
- Detects broken links
- Blocks commit if any check fails

**Bypass (not recommended):**
```bash
git commit --no-verify
```

---

## Dependencies

### Required Python Packages
```txt
pyyaml>=6.0        # YAML frontmatter parsing
click>=8.0         # CLI interface
rich>=13.0         # Pretty console output
```

### Installation
```bash
pip install -r tools/requirements.txt
```

---

## Integration with Librarian Agent

The Librarian Agent uses these scripts as tools to provide contextual intelligence:

### File Placement Advisor
1. Agent receives file description + content preview
2. Runs `validate_location.py` to check obvious violations
3. Applies FILE_ORGANIZATION_STANDARDS decision tree
4. Returns recommended path with rationale

### Discovery Assistant
1. Agent receives natural language query
2. Queries catalog via `query_catalog.py`
3. Ranks results by relevance + recency
4. Returns top 5 with contextual summaries

### Gap Analysis
1. Agent scans `/modules` for components
2. Queries catalog for corresponding docs
3. Assesses complexity and activity
4. Prioritizes gaps and generates recommendations

---

## Testing

### Run All Unit Tests
```bash
pytest tools/tests/
```

### Run Specific Test Suite
```bash
pytest tools/tests/test_validate_metadata.py
pytest tools/tests/test_validate_location.py
pytest tools/tests/test_build_index.py
```

---

## Troubleshooting

### "Module not found" error
**Solution:** Install dependencies
```bash
pip install -r tools/requirements.txt
```

### "Permission denied" on pre-commit hook
**Solution:** Make hook executable
```bash
chmod +x .git/hooks/pre-commit
```

### Catalog queries return no results
**Solution:** Rebuild index
```bash
python tools/build_index.py --rebuild
```

### Pre-commit hook too slow
**Solution:** Run only on staged files (default behavior) or bypass for WIP commits

---

## Development

### Adding a New Tool

1. Create script in `tools/your_tool.py`
2. Add CLI interface using `click`
3. Add comprehensive docstrings
4. Write unit tests in `tools/tests/`
5. Update this README
6. Add to `tools/__init__.py` if needed

### Code Style
- Follow PEP 8
- Use type hints
- Add comprehensive docstrings
- Handle errors gracefully
- Provide helpful error messages

---

## References

- [FILE_ORGANIZATION_STANDARDS.md](/workspace/.trees/librarian-improvements/docs/FILE_ORGANIZATION_STANDARDS.md)
- [Librarian Agent Definition](/workspace/.trees/librarian-improvements/.claude/agents/librarian.md)
- [Librarian Usage Guide](/workspace/.trees/librarian-improvements/docs/librarian-usage-guide.md)
- [PRD: Librarian Enhancements](/workspace/.trees/librarian-improvements/tasks/librarian-enhancements/prd.md)

---

## Changelog

### 2025-10-12 - v1.0
- Initial toolset created
- Validation scripts (metadata, location, links)
- Document catalog system (build, query)
- Metrics collection and reporting
- Pre-commit hook for enforcement
