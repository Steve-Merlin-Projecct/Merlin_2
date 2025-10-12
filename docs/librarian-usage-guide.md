---
title: "Librarian System Usage Guide"
type: guide
component: documentation
status: active
tags: ["librarian", "documentation", "validation", "workflow"]
created: 2025-10-12
updated: 2025-10-12
---

# Librarian System Usage Guide

**Version:** 1.0
**Last Updated:** 2025-10-12

## Overview

The Librarian System provides **automated documentation management** with real-time assistance for file operations. It combines validation scripts, document catalog search, and an intelligent agent to enforce standards and improve documentation quality.

---

## Quick Start

### For Developers

**Before creating a documentation file:**
```bash
# Ask librarian where to put it (via agent or follow decision tree)
# See "File Placement Decision Tree" below
```

**After creating/modifying documentation:**
```bash
# Validate your changes
python tools/validate_metadata.py your-file.md
python tools/validate_location.py your-file.md
python tools/validate_links.py your-file.md
```

**Finding documentation:**
```bash
# Search the catalog
python tools/query_catalog.py --keywords "database schema"
python tools/query_catalog.py --component email --type guide
```

---

## System Components

### 1. Validation Scripts

#### Metadata Validation (`validate_metadata.py`)
**Purpose:** Ensure all markdown files have proper YAML frontmatter

**Usage:**
```bash
# Validate single file
python tools/validate_metadata.py docs/myfile.md

# Validate all files
python tools/validate_metadata.py --all

# Auto-fix missing metadata
python tools/validate_metadata.py docs/myfile.md --fix
```

**Required YAML fields:**
```yaml
---
title: "Document Title"
type: technical_doc  # or api_spec, architecture, process, status_report, guide
component: module_name
status: active  # or draft, review, archived, deprecated
tags: ["keyword1", "keyword2"]  # optional but recommended
---
```

**Valid types:**
- `technical_doc` - Technical documentation
- `api_spec` - API specifications
- `architecture` - Architecture documents
- `process` - Process/workflow documentation
- `status_report` - Status reports and summaries
- `guide` - How-to guides
- `reference` - Reference documentation
- `tutorial` - Tutorials

**Valid statuses:**
- `draft` - Work in progress
- `active` - Current, maintained documentation
- `review` - Under review
- `archived` - Historical, not actively maintained
- `deprecated` - Outdated, replaced by newer docs

---

#### Location Validation (`validate_location.py`)
**Purpose:** Check if files are in correct locations per FILE_ORGANIZATION_STANDARDS.md

**Usage:**
```bash
# Validate single file
python tools/validate_location.py docs/myfile.md

# Scan root directory for violations
python tools/validate_location.py --scan-root

# Validate all files
python tools/validate_location.py --all
```

**Key placement rules:**
- Branch status files → `/docs/git_workflow/branch-status/`
- Migration docs → `/docs/archived/migrations/`
- Test files → `/tests/{unit,integration,e2e}/`
- Scripts → `/scripts/`
- Root directory → Only essential files (README.md, CLAUDE.md, etc.)

---

#### Link Validation (`validate_links.py`)
**Purpose:** Find broken internal links

**Usage:**
```bash
# Check single file
python tools/validate_links.py docs/myfile.md

# Check all files
python tools/validate_links.py --all

# JSON output for automation
python tools/validate_links.py --all --json
```

---

#### Metrics Collection (`collect_metrics.py`)
**Purpose:** Gather statistics about documentation health

**Usage:**
```bash
# Human-readable report
python tools/collect_metrics.py

# JSON output
python tools/collect_metrics.py --json
```

**Metrics reported:**
- Total documents and code files
- Metadata coverage percentage
- Stale docs (>90 days old)
- Archive candidates (>180 days old)
- Root directory violations
- Documentation by component/type/status
- Undocumented modules

---

### 2. Document Catalog System

#### Building the Catalog (`build_index.py`)
**Purpose:** Create searchable SQLite database of all documentation

**Usage:**
```bash
# Build catalog (incremental update - recommended)
python tools/build_index.py

# Rebuild from scratch
python tools/build_index.py --rebuild
```

**When to run:**
- After adding new documentation files
- After significant doc changes
- Weekly as routine maintenance

**What's indexed:**
- File path and metadata
- Title, type, component, status, tags
- Content summary (first paragraph)
- Word count and timestamps

---

#### Searching the Catalog (`query_catalog.py`)
**Purpose:** Find relevant documentation quickly

**Usage:**
```bash
# Keyword search
python tools/query_catalog.py --keywords "database schema"

# Filter by component
python tools/query_catalog.py --component email

# Filter by type
python tools/query_catalog.py --type guide

# Combined search
python tools/query_catalog.py --keywords "oauth" --component email --type technical_doc

# Limit results
python tools/query_catalog.py --keywords "testing" --limit 5

# List available filters
python tools/query_catalog.py --list-components
python tools/query_catalog.py --list-types
python tools/query_catalog.py --list-statuses
```

---

### 3. Helper Tools

#### Tag Suggestion (`suggest_tags.py`)
**Purpose:** Auto-suggest tags based on content

**Usage:**
```bash
# Suggest tags for a file
python tools/suggest_tags.py docs/myfile.md

# Output as YAML (ready to paste)
python tools/suggest_tags.py docs/myfile.md --yaml
```

**Algorithm:** TF-IDF keyword extraction with technical keyword boosting

---

#### Auto-Archival (`auto_archive.py`)
**Purpose:** Move stale files to archive automatically

**Usage:**
```bash
# Dry run (see what would be archived)
python tools/auto_archive.py

# Actually archive files
python tools/auto_archive.py --execute

# Custom age threshold
python tools/auto_archive.py --days 90
```

**Criteria for archival:**
- Not modified in 180 days (default)
- Not referenced in other active documents
- Not in essential directories

---

## Workflows

### Workflow 1: Creating a New Documentation File

**Step 1: Determine file type and location**

Use the decision tree:

```
What am I documenting?

├─ Branch/feature completion?
│  → /docs/git_workflow/branch-status/feature-<name>.md
│
├─ API specification?
│  → /docs/api/<name>-api.md
│
├─ Architecture/design?
│  → /docs/architecture/<name>.md
│
├─ How-to guide?
│  → /docs/Guides/<name>.md
│
├─ Component documentation?
│  → /docs/component_docs/<component>/<name>.md
│
├─ Migration/historical?
│  → /docs/archived/migrations/<name>.md
│
└─ Other?
   → /docs/<category>/<name>.md
```

**Step 2: Create file with metadata**

```yaml
---
title: "Clear Descriptive Title"
type: guide  # or technical_doc, api_spec, etc.
component: relevant_component
status: draft  # start as draft
tags: []  # use suggest_tags.py to generate
created: 2025-10-12
---

# Content starts here
```

**Step 3: Use tag suggester**

```bash
python tools/suggest_tags.py docs/myfile.md --yaml
# Copy suggested tags to your frontmatter
```

**Step 4: Validate before committing**

```bash
python tools/validate_metadata.py docs/myfile.md
python tools/validate_location.py docs/myfile.md
python tools/validate_links.py docs/myfile.md
```

**Step 5: Update status when complete**

Change `status: draft` to `status: active` when ready

---

### Workflow 2: Finding Relevant Documentation

**Option A: Catalog Search (Fastest)**

```bash
# Search by topic
python tools/query_catalog.py --keywords "authentication oauth"

# Filter by component
python tools/query_catalog.py --component email --keywords "sending"

# Find all guides
python tools/query_catalog.py --type guide
```

**Option B: Grep (More flexible)**

```bash
# Search content
grep -r "OAuth implementation" docs/

# Find specific component docs
find docs/component_docs/email -name "*.md"
```

**Option C: Ask Librarian Agent**

Invoke librarian agent with natural language query:
```
"How do I add OAuth to a new integration?"
"Where is the email sending logic documented?"
"Best practices for testing?"
```

---

### Workflow 3: Maintaining Documentation Quality

**Weekly:**
```bash
# Check for violations
python tools/validate_metadata.py --all
python tools/validate_location.py --scan-root
python tools/validate_links.py --all

# Update catalog
python tools/build_index.py

# Review metrics
python tools/collect_metrics.py
```

**Monthly:**
```bash
# Find archive candidates
python tools/auto_archive.py  # dry run

# Review and execute
python tools/auto_archive.py --execute
```

**Quarterly:**
```bash
# Request full librarian audit (via agent)
# Agent generates comprehensive report with recommendations
```

---

## Pre-commit Hook

**Automatic validation on every commit**

The pre-commit hook validates:
1. YAML frontmatter completeness
2. File location compliance
3. Broken internal links

**Install:**
```bash
cp tools/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Bypass (not recommended):**
```bash
git commit --no-verify
```

---

## CI/CD Integration

**GitHub Actions workflow** validates documentation on every push/PR:

- Metadata validation
- File location checking
- Broken link detection
- Metrics reporting

See `.github/workflows/validate-docs.yml`

---

## File Placement Decision Tree

```
┌─────────────────────────────────────────────┐
│ "Where should this file go?"                │
└─────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ What type of file?     │
        └────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    .md file    .py file     .sh file
        │            │            │
        │            │            └─► /scripts/
        │            │
        │            └──► Is it a test?
        │                      │
        │                 ┌────┴─────┐
        │                 │          │
        │                Yes        No
        │                 │          │
        │             /tests/    /modules/ or /scripts/
        │
        └──► What's being documented?
                     │
        ┌────────────┼────────────────┬────────────┐
        │            │                │            │
        ▼            ▼                ▼            ▼
   Branch        API spec      Architecture   Component
   status                                      specific
        │            │                │            │
        ▼            ▼                ▼            ▼
   /docs/       /docs/api/    /docs/architecture/ /docs/component_docs/
   git_workflow/                                   <component>/
   branch-status/
```

---

## Common Questions

### Q: Do I need metadata for every markdown file?
**A:** Yes, all markdown files in `/docs` should have YAML frontmatter. Use `--fix` flag to auto-generate templates.

### Q: How do I know which component to use?
**A:** Run `python tools/query_catalog.py --list-components` to see existing components. If your component isn't listed, create a new one.

### Q: What if validation fails but I need to commit urgently?
**A:** You can bypass with `git commit --no-verify`, but fix violations ASAP.

### Q: How often should I rebuild the catalog?
**A:** Run `build_index.py` after significant doc changes or weekly for maintenance.

### Q: Can I have multiple components in one doc?
**A:** Use the primary component in metadata. Add other components as tags.

### Q: What's the difference between `archived` status and `/docs/archived/` location?
**A:**
- **Status `archived`**: Doc is historical but might be referenced
- **Location `/docs/archived/`**: Doc is no longer actively maintained
- Usually both apply together

---

## Best Practices

### DO:
- ✅ Add metadata to all new markdown files
- ✅ Run validation before committing
- ✅ Use meaningful, descriptive tags
- ✅ Update `status` field when doc state changes
- ✅ Search catalog before creating duplicate docs
- ✅ Keep titles clear and specific

### DON'T:
- ❌ Create files in root directory (except essentials)
- ❌ Skip validation to "save time"
- ❌ Use generic titles like "Documentation" or "Guide"
- ❌ Leave docs with `draft` status permanently
- ❌ Forget to rebuild catalog after adding docs

---

## Troubleshooting

### Problem: Validation fails on frontmatter
**Solution:**
```bash
python tools/validate_metadata.py myfile.md --fix
# This generates a template based on file path/content
```

### Problem: Can't find the right documentation
**Solution:**
```bash
# Try multiple search approaches
python tools/query_catalog.py --keywords "your topic"
python tools/query_catalog.py --component relevant_component
grep -r "specific term" docs/
```

### Problem: Pre-commit hook is too slow
**Solution:** Hook only validates staged files. If still slow:
```bash
# Skip hook for WIP commits
git commit --no-verify -m "WIP: work in progress"
# Fix and recommit properly later
```

### Problem: Catalog search returns no results
**Solution:**
```bash
# Rebuild catalog
python tools/build_index.py --rebuild
```

---

## Reference

### File Organization Standards
See: `/docs/FILE_ORGANIZATION_STANDARDS.md`

### Librarian Agent Definition
See: `/.claude/agents/librarian.md`

### Tool README
See: `/tools/README.md`

### PRD & Implementation
See: `/tasks/librarian-enhancements/`

---

## Support

**Issues with tools:** Check tool help text
```bash
python tools/<tool>.py --help
```

**Questions about file placement:** Consult FILE_ORGANIZATION_STANDARDS.md or ask librarian agent

**Found a bug:** Create issue in project issue tracker
