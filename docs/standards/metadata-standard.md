---
title: "Documentation Metadata Standard"
type: "standards"
status: "active"
version: "1.0.0"
created: "2025-10-09"
updated: "2025-10-09"
author: "Claude Sonnet 4.5"
tags: ["metadata", "standards", "documentation", "yaml"]
related:
  - "docs/FILE_ORGANIZATION_STANDARDS.md"
  - "docs/workflows/librarian-usage-guide.md"
audience: "developers"
maintenance: "active"
---

# Documentation Metadata Standard

**Purpose:** Define comprehensive YAML frontmatter metadata standard for all project documentation
**Version:** 1.0.0
**Status:** Active
**Last Updated:** October 9, 2025

## Overview

This standard defines the metadata format for all documentation files (.md) in the project. Metadata enables automated indexing, validation, searchability, and organization maintenance through the librarian system.

**Key Principles:**
1. **Machine-Readable:** YAML frontmatter enables programmatic querying
2. **Human-Friendly:** Metadata is visible and understandable
3. **Progressive Enhancement:** Required fields are minimal, optional fields add value
4. **Backward Compatible:** Existing docs can migrate gradually

---

## YAML Frontmatter Specification

### Complete Example

```yaml
---
title: "Document Title"
type: "guide"
status: "active"
version: "1.2.0"
created: "2025-10-09"
updated: "2025-10-09"
author: "Claude Sonnet 4.5"
tags: ["security", "api", "authentication"]
related:
  - "docs/component_docs/security/security_overview.md"
  - "docs/api/authentication.md"
audience: "developers"
maintenance: "stable"
feature_branch: "feature/oauth-integration"
review_date: "2026-01-09"
supersedes: "docs/archived/old-auth-guide.md"
---
```

### Field Definitions

#### Required Fields

**1. `title`**
- **Type:** String
- **Description:** Human-readable document title
- **Format:** Title case, descriptive
- **Example:** `"File Organization Standards"`
- **Validation:** Must be non-empty, max 100 characters

**2. `type`**
- **Type:** String (enum)
- **Description:** Document classification
- **Allowed Values:**
  - `"standards"` - Standards and specifications
  - `"guide"` - How-to guides and tutorials
  - `"prd"` - Product Requirements Documents
  - `"task"` - Task lists and execution plans
  - `"reference"` - Reference documentation
  - `"api"` - API documentation
  - `"architecture"` - Architecture and design docs
  - `"decision"` - Architecture Decision Records (ADR)
  - `"process"` - Process and workflow documentation
  - `"changelog"` - Change logs and release notes
  - `"audit"` - Audit reports
  - `"template"` - Document templates
- **Example:** `"guide"`
- **Validation:** Must be one of allowed values

**3. `status`**
- **Type:** String (enum)
- **Description:** Document lifecycle state
- **Allowed Values:**
  - `"draft"` - Work in progress, not ready for use
  - `"active"` - Current and actively maintained
  - `"stable"` - Complete and stable, minimal changes expected
  - `"deprecated"` - Superseded, not recommended for new usage
  - `"archived"` - Historical, no longer maintained
  - `"completed"` - Task/project completed (for tasks/PRDs)
- **Example:** `"active"`
- **Validation:** Must be one of allowed values

**4. `created`**
- **Type:** Date string
- **Description:** Date document was created
- **Format:** `YYYY-MM-DD` (ISO 8601)
- **Example:** `"2025-10-09"`
- **Validation:** Valid date, format YYYY-MM-DD
- **Auto-Generation:** Can be extracted from git history (first commit)

#### Recommended Fields

**5. `version`**
- **Type:** String (semantic version)
- **Description:** Document version
- **Format:** `"MAJOR.MINOR.PATCH"` (semantic versioning)
- **Example:** `"1.2.0"`
- **Validation:** Must match semver pattern (optional)
- **Guidelines:**
  - Major: Breaking changes, complete rewrites
  - Minor: Significant additions, new sections
  - Patch: Corrections, clarifications, minor updates

**6. `updated`**
- **Type:** Date string
- **Description:** Date of last significant update
- **Format:** `YYYY-MM-DD` (ISO 8601)
- **Example:** `"2025-10-09"`
- **Validation:** Valid date, >= created date
- **Auto-Generation:** Can be extracted from git history (last commit)

**7. `author`**
- **Type:** String
- **Description:** Primary author or creator
- **Format:** Name or "Claude [Model]"
- **Examples:** `"John Doe"`, `"Claude Sonnet 4.5"`
- **Validation:** Non-empty string
- **Auto-Generation:** Can be extracted from git blame (primary contributor)

**8. `tags`**
- **Type:** Array of strings
- **Description:** Searchable keywords for categorization
- **Format:** Lowercase, hyphenated, 2-4 words per tag
- **Example:** `["security", "authentication", "oauth", "api"]`
- **Validation:** Each tag: lowercase, hyphens only, 2-30 characters
- **Guidelines:**
  - Use 3-6 tags per document
  - Include technical topics (e.g., "database", "api")
  - Include functional areas (e.g., "security", "testing")
  - Avoid overly generic tags (e.g., "documentation")

#### Optional Fields

**9. `related`**
- **Type:** Array of strings (file paths)
- **Description:** Related documentation files
- **Format:** Relative paths from project root
- **Example:**
  ```yaml
  related:
    - "docs/api/authentication.md"
    - "docs/component_docs/security/security_overview.md"
  ```
- **Validation:** Each path should exist (warning if not)
- **Guidelines:** Link to 2-5 most relevant related docs

**10. `audience`**
- **Type:** String (enum)
- **Description:** Target audience
- **Allowed Values:**
  - `"developers"` - Software developers
  - `"maintainers"` - Project maintainers
  - `"users"` - End users
  - `"all"` - All audiences
- **Example:** `"developers"`
- **Default:** `"developers"` (if omitted)

**11. `maintenance`**
- **Type:** String (enum)
- **Description:** Maintenance commitment level
- **Allowed Values:**
  - `"active"` - Actively updated as project evolves
  - `"stable"` - Maintained but infrequent updates
  - `"deprecated"` - No longer maintained
- **Example:** `"stable"`
- **Guidelines:**
  - `"active"` for core standards, frequently changing docs
  - `"stable"` for reference docs, established guides
  - `"deprecated"` for docs being phased out

**12. `feature_branch`**
- **Type:** String
- **Description:** Associated feature branch (for PRDs/tasks)
- **Format:** Branch name
- **Example:** `"feature/oauth-integration"`
- **Validation:** Should match git branch naming convention
- **Usage:** Primarily for PRDs and task documents

**13. `review_date`**
- **Type:** Date string
- **Description:** Next scheduled review date
- **Format:** `YYYY-MM-DD`
- **Example:** `"2026-04-09"`
- **Usage:** Set review dates for critical docs (quarterly/annually)

**14. `supersedes`**
- **Type:** String or array of strings
- **Description:** Previous version(s) this document replaces
- **Format:** File paths or document titles
- **Example:** `"docs/archived/old-authentication-guide.md"`
- **Usage:** Track documentation evolution

**15. `depends_on`**
- **Type:** Array of strings
- **Description:** Hard dependencies (must read first)
- **Format:** File paths
- **Example:**
  ```yaml
  depends_on:
    - "docs/project_overview/README.md"
    - "docs/standards/coding-standards.md"
  ```
- **Usage:** Prerequisites for understanding this document

---

## Document Type Guidelines

### Standards (`type: "standards"`)

**Purpose:** Define rules, specifications, and requirements

**Required Metadata:**
- `title`, `type`, `status`, `created`, `version`

**Recommended Metadata:**
- `updated`, `author`, `tags`, `maintenance`, `review_date`

**Example:**
```yaml
---
title: "API Design Standards"
type: "standards"
status: "active"
version: "2.1.0"
created: "2024-06-15"
updated: "2025-10-09"
tags: ["api", "standards", "rest", "design"]
maintenance: "active"
review_date: "2026-01-09"
---
```

---

### Guides (`type: "guide"`)

**Purpose:** How-to documentation, tutorials, walkthroughs

**Required Metadata:**
- `title`, `type`, `status`, `created`

**Recommended Metadata:**
- `updated`, `tags`, `related`, `audience`, `depends_on`

**Example:**
```yaml
---
title: "Getting Started with Email Integration"
type: "guide"
status: "active"
created: "2025-07-15"
updated: "2025-10-01"
tags: ["email", "oauth", "gmail", "tutorial"]
audience: "developers"
related:
  - "docs/component_docs/gmail_oauth_integration.md"
  - "docs/api/email-api.md"
---
```

---

### PRDs (`type: "prd"`)

**Purpose:** Product Requirements Documents

**Required Metadata:**
- `title`, `type`, `status`, `created`, `version`, `feature_branch`

**Recommended Metadata:**
- `updated`, `author`, `tags`, `related`

**Special Status Values:**
- `"draft"` - In development
- `"active"` - Approved, ready for implementation
- `"completed"` - Implementation finished

**Example:**
```yaml
---
title: "Librarian System - Automated File Organization"
type: "prd"
status: "active"
version: "1.0.0"
created: "2025-10-09"
updated: "2025-10-09"
author: "Claude Sonnet 4.5"
tags: ["file-organization", "automation", "documentation", "metadata"]
feature_branch: "task/10-librarian"
related:
  - "tasks/tasks-prd-librarian-system.md"
  - "docs/FILE_ORGANIZATION_STANDARDS.md"
---
```

---

### Tasks (`type: "task"`)

**Purpose:** Task lists, execution plans, checklists

**Required Metadata:**
- `title`, `type`, `status`, `created`, `feature_branch`

**Recommended Metadata:**
- `updated`, `related` (link to PRD)

**Example:**
```yaml
---
title: "Task List: Librarian System Implementation"
type: "task"
status: "in_progress"
created: "2025-10-09"
updated: "2025-10-09"
feature_branch: "task/10-librarian"
related:
  - "tasks/prd-librarian-system.md"
---
```

---

### API Documentation (`type: "api"`)

**Purpose:** API endpoint documentation, reference

**Required Metadata:**
- `title`, `type`, `status`, `created`, `version`

**Recommended Metadata:**
- `updated`, `tags`, `related`

**Example:**
```yaml
---
title: "Database API Documentation"
type: "api"
status: "active"
version: "2.5.0"
created: "2024-08-01"
updated: "2025-09-15"
tags: ["api", "database", "rest", "endpoints"]
related:
  - "docs/component_docs/database/database_schema.md"
---
```

---

### Architecture (`type: "architecture"`)

**Purpose:** System design, architecture documentation

**Required Metadata:**
- `title`, `type`, `status`, `created`, `version`

**Recommended Metadata:**
- `updated`, `author`, `tags`, `review_date`

**Example:**
```yaml
---
title: "Storage Architecture"
type: "architecture"
status: "stable"
version: "2.0.0"
created: "2025-06-30"
updated: "2025-07-15"
tags: ["architecture", "storage", "design", "cloud"]
review_date: "2026-01-30"
---
```

---

## Python Code Metadata Standard

### Module-Level Docstring Format

```python
"""
[Module Name]: [One-line description]

[Detailed narrative description of module purpose, key concepts,
architecture decisions, and usage patterns. 2-4 paragraphs.]

Metadata:
    Type: module|script|tool|test
    Status: active|experimental|deprecated
    Dependencies: library1, library2, library3
    Related: path/to/related/module.py

Author: [Name or "Claude Sonnet X"]
Created: YYYY-MM-DD
Updated: YYYY-MM-DD

Example:
    Basic usage example::

        from module import ClassName
        instance = ClassName()
        instance.method()
"""
```

### Complete Example

```python
"""
Librarian Common Utilities: Shared utilities for librarian tools

This module provides common functionality used across all librarian tools
including YAML frontmatter parsing, git history extraction, markdown link
detection, and file discovery operations. It serves as the foundation for
the metadata extraction, indexing, validation, and archival systems.

The module emphasizes robust error handling and provides both low-level
primitives and high-level convenience functions for working with
documentation files.

Metadata:
    Type: module
    Status: active
    Dependencies: PyYAML, GitPython, pathlib
    Related: tools/librarian_index.py, tools/librarian_validate.py

Author: Claude Sonnet 4.5
Created: 2025-10-09
Updated: 2025-10-09

Example:
    Extract YAML frontmatter from a markdown file::

        from librarian_common import extract_frontmatter

        metadata = extract_frontmatter('docs/guide.md')
        print(metadata.get('title'))
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, List

# ... module code ...
```

### Class and Function Docstrings

**Use Google-style docstrings for all classes and functions:**

```python
def extract_frontmatter(file_path: str) -> Optional[Dict]:
    """
    Extract YAML frontmatter from a markdown file.

    Parses the YAML frontmatter block (delimited by ---) from the beginning
    of a markdown file and returns it as a dictionary. Returns None if no
    frontmatter is found.

    Args:
        file_path: Path to markdown file (absolute or relative)

    Returns:
        Dictionary containing parsed YAML frontmatter, or None if not found

    Raises:
        FileNotFoundError: If file does not exist
        yaml.YAMLError: If frontmatter is invalid YAML
        ValueError: If file is not a .md file

    Example:
        >>> extract_frontmatter('docs/guide.md')
        {'title': 'User Guide', 'type': 'guide', 'status': 'active'}

        >>> extract_frontmatter('docs/no-metadata.md')
        None
    """
    # Implementation...
```

---

## Migration Guide

### Migrating Existing Documentation

**Pattern A → YAML Frontmatter (Structured PRDs)**

**Before:**
```markdown
# PRD: Feature Name
**Status:** ✅ COMPLETED
**Priority:** High
**Version:** 1.0.0
**Created:** October 8, 2025
```

**After:**
```markdown
---
title: "Feature Name"
type: "prd"
status: "completed"
version: "1.0.0"
created: "2025-10-08"
tags: ["feature-name", "category"]
---

# PRD: Feature Name
**Status:** ✅ COMPLETED
**Priority:** High
**Version:** 1.0.0
**Created:** October 8, 2025

[Keep existing visible metadata for human readers]
```

**Pattern B → YAML Frontmatter (Technical Docs)**

**Before:**
```markdown
# Component Name
## Overview
This component handles...
```

**After:**
```markdown
---
title: "Component Name"
type: "reference"
status: "active"
created: "2024-06-15"  # from git history
updated: "2025-09-20"  # from git history
tags: ["component", "system-area"]
---

# Component Name
## Overview
This component handles...
```

**Pattern C → YAML Frontmatter (Minimal Docs)**

**Before:**
```markdown
# Quick Start Guide
Here's how to get started...
```

**After:**
```markdown
---
title: "Quick Start Guide"
type: "guide"
status: "active"
created: "2025-01-15"  # from git history
tags: ["quickstart", "tutorial"]
audience: "developers"
---

# Quick Start Guide
Here's how to get started...
```

### Automated Migration

**Use the metadata extraction tool:**

```bash
# Scan existing metadata coverage
python tools/librarian_metadata.py --scan

# Extract and convert Pattern A/B/C
python tools/librarian_metadata.py --batch

# Generate missing metadata from git history
python tools/librarian_metadata.py --generate-all

# Interactive enhancement (review suggested metadata)
python tools/librarian_metadata.py --enhance docs/guide.md --interactive
```

---

## Validation Rules

### Required Field Validation

1. **Title:** Non-empty, max 100 characters
2. **Type:** Must be one of allowed enum values
3. **Status:** Must be one of allowed enum values
4. **Created:** Valid date in YYYY-MM-DD format

### Optional Field Validation

5. **Version:** If present, should match semver pattern (lenient)
6. **Updated:** If present, must be >= created date
7. **Tags:** Each tag lowercase, hyphens only, 2-30 characters
8. **Related:** Each path should exist (warning if not)
9. **Audience:** If present, must be one of allowed enum values
10. **Dates:** All dates in YYYY-MM-DD format

### Content Consistency Validation

11. **Status vs. Location:** `status: "archived"` should be in /docs/archived/
12. **Type vs. Location:** `type: "prd"` should be in /tasks/ or /docs/archived/tasks/
13. **Completed Tasks:** `status: "completed"` should trigger archival suggestion

---

## Best Practices

### Choosing Tags

**Good Tags:**
- Specific technical topics: `"authentication"`, `"database"`, `"api"`
- Functional areas: `"security"`, `"testing"`, `"deployment"`
- Specific technologies: `"oauth"`, `"postgresql"`, `"docker"`

**Avoid:**
- Overly generic: `"documentation"`, `"code"`, `"project"`
- Redundant with type: `"guide"` when type is already "guide"
- Too many tags: 3-6 is optimal

### Setting Status Appropriately

- **`"draft"`**: Incomplete, do not use for implementation
- **`"active"`**: Current best practice, use this
- **`"stable"`**: Complete, unlikely to change
- **`"deprecated"`**: Superseded, migration guide should exist
- **`"archived"`**: Historical only, in /docs/archived/
- **`"completed"`**: For tasks/PRDs only, work is done

### Version Numbering

- **Documentation:**
  - v1.0.0: Initial complete version
  - v1.1.0: New sections added
  - v1.0.1: Typos, clarifications
  - v2.0.0: Major restructure

- **PRDs:**
  - v1.0.0: Approved for implementation
  - v1.1.0: Scope additions during implementation
  - v2.0.0: Major scope change (rare)

### Related Files

- Link to 2-5 most relevant documents
- Prefer direct dependencies over distant relations
- Include both prerequisites (depends_on) and related topics
- Keep links current (update when files move)

---

## Common Patterns

### New Feature Documentation Set

**PRD:**
```yaml
---
title: "Feature X Implementation"
type: "prd"
status: "active"
version: "1.0.0"
feature_branch: "feature/feature-x"
tags: ["feature-x", "category"]
related: ["tasks/tasks-prd-feature-x.md"]
---
```

**Task List:**
```yaml
---
title: "Task List: Feature X"
type: "task"
status: "in_progress"
feature_branch: "feature/feature-x"
related: ["tasks/prd-feature-x.md"]
---
```

**Guide (After Completion):**
```yaml
---
title: "Feature X User Guide"
type: "guide"
status: "active"
tags: ["feature-x", "tutorial"]
related:
  - "docs/api/feature-x-api.md"
  - "docs/component_docs/feature-x-architecture.md"
audience: "developers"
---
```

---

## Troubleshooting

### Validation Errors

**Error: "Missing required field: title"**
- Add YAML frontmatter block with title field

**Error: "Invalid type value: 'documentation'"**
- Use one of allowed type values (guide, reference, api, etc.)

**Error: "Invalid date format"**
- Use YYYY-MM-DD format (e.g., "2025-10-09")

**Error: "Updated date before created date"**
- Check date values, updated must be >= created

**Warning: "Related file not found: docs/missing.md"**
- Update related path or remove if file was deleted

### Best Practice Violations

**Warning: "No tags specified"**
- Add 3-6 relevant tags for discoverability

**Warning: "Document in archive but status is 'active'"**
- Update status to "archived" for files in /docs/archived/

**Warning: "PRD has status 'completed' but still in /tasks"**
- Run archival tool to move to /docs/archived/tasks/

---

## Tools Support

### Validation

```bash
# Validate all documentation
python tools/librarian_validate.py

# Validate specific file
python tools/librarian_validate.py docs/guide.md

# Auto-fix simple issues
python tools/librarian_validate.py --fix
```

### Metadata Enhancement

```bash
# Scan metadata coverage
python tools/librarian_metadata.py --scan

# Extract existing metadata patterns
python tools/librarian_metadata.py --extract docs/guide.md

# Generate missing metadata
python tools/librarian_metadata.py --generate docs/guide.md

# Interactive enhancement
python tools/librarian_metadata.py --enhance docs/guide.md --interactive
```

### Indexing

```bash
# Generate documentation index
python tools/librarian_index.py

# View in browser
open docs/indexes/documentation-map.html

# Query programmatically
python -c "import json; print(json.load(open('docs/indexes/documentation-index.json')))"
```

---

## Version History

### v1.0.0 (2025-10-09)
- Initial metadata standard specification
- YAML frontmatter schema defined
- Python docstring metadata format established
- Migration guide for existing patterns
- Validation rules specified
- Tool support documented

---

## References

- [YAML Specification](https://yaml.org/spec/)
- [Semantic Versioning](https://semver.org/)
- [ISO 8601 Date Format](https://en.wikipedia.org/wiki/ISO_8601)
- [Google Style Python Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [File Organization Standards](../FILE_ORGANIZATION_STANDARDS.md)

---

## Questions or Feedback

For questions about this standard or to propose changes:
1. Review this document and examples
2. Check tool documentation (`docs/workflows/librarian-usage-guide.md`)
3. Run validation to see specific issues
4. Propose changes via PR with rationale

**Maintained by:** Project maintainers and librarian system
**Review Schedule:** Quarterly (next review: 2026-01-09)
