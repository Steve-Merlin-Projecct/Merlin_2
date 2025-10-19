---
title: "Quality Validation Coordination Guide"
type: guide
component: development
status: active
tags: ["validation", "code-quality", "documentation", "librarian", "workflow"]
created: 2025-10-17
updated: 2025-10-17
version: 1.0
---

# Quality Validation Coordination Guide

**Purpose:** Defines how code quality tools (Black, Flake8, Vulture) and documentation quality tools (Librarian) coordinate to provide comprehensive project quality validation without overlap or confusion.

**Integration Point:** `/tree close` slash command (worktree closure validation)

---

## Architecture Overview

### Parallel Validation Systems

The project employs **two independent quality validation systems** that operate on different file types and quality dimensions:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Project Quality Validation                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
         ┌──────────▼─────────┐  ┌─────▼──────────────┐
         │ Code Quality Stack │  │ Documentation      │
         │                    │  │ Quality Stack      │
         └──────────┬─────────┘  └─────┬──────────────┘
                    │                   │
         ┌──────────▼─────────┐  ┌─────▼──────────────┐
         │ Target: .py files  │  │ Target: .md files  │
         │ Tools: Black,      │  │ Tools: librarian_* │
         │        Flake8,     │  │ Agent: librarian   │
         │        Vulture     │  │                    │
         │ Agent: code-       │  │                    │
         │        reviewer    │  │                    │
         └────────────────────┘  └────────────────────┘
```

### Separation of Concerns

| Aspect | Code Quality Stack | Documentation Quality Stack |
|--------|-------------------|----------------------------|
| **File Types** | `.py`, `.pyi` | `.md`, YAML frontmatter |
| **Focus** | Syntax, style, complexity, dead code | Metadata, organization, structure, cross-refs |
| **Tools** | Black, Flake8, Vulture | librarian_validate, librarian_metadata, librarian_index |
| **Agent** | code-reviewer | librarian |
| **Config Files** | `.black.toml`, `.flake8`, `.vulture.toml` | `docs/standards/metadata-standard.md`, `FILE_ORGANIZATION_STANDARDS.md` |
| **When to Use** | After code changes | After doc changes, file moves, metadata updates |

---

## Tool Responsibilities

### Code Quality Tools

**Black (Formatter)**
- **Purpose:** Enforce consistent Python code formatting
- **Config:** `.black.toml`
- **Scope:** All `.py` files except excluded directories
- **Exclusions:** `.git`, `.cache`, `archived_files`, `storage`, `__pycache__`
- **Integration:** `/format` slash command, code-reviewer agent

**Flake8 (Linter)**
- **Purpose:** Style guide enforcement (PEP 8), error detection
- **Config:** `.flake8`
- **Scope:** All `.py` files except excluded directories
- **Ignores:** E203, W503 (Black compatibility)
- **Integration:** `/lint` slash command, code-reviewer agent

**Vulture (Dead Code Detector)**
- **Purpose:** Find unused code (functions, variables, imports)
- **Config:** `.vulture.toml`
- **Scope:** All `.py` files except excluded directories
- **Threshold:** 80% confidence minimum
- **Integration:** `/lint` slash command, code-reviewer agent

**code-reviewer Agent**
- **Purpose:** Comprehensive code review combining automated tools + manual analysis
- **Runs:** Black, Flake8, Vulture automatically before manual review
- **Scope:** Security, performance, CLAUDE.md compliance, Flask/SQLAlchemy patterns
- **When:** After significant code changes, before PR merge

### Documentation Quality Tools

**librarian_validate.py**
- **Purpose:** Validate YAML frontmatter, file placement, naming conventions
- **Standards:** `docs/standards/metadata-standard.md`, `FILE_ORGANIZATION_STANDARDS.md`
- **Scope:** All `.md` files in `/docs`, `/tasks`, `.claude/`
- **Checks:**
  - Required metadata fields (title, type, status, created)
  - Valid enum values (type, status)
  - Date format (YYYY-MM-DD)
  - File naming conventions
  - Location compliance

**librarian_metadata.py**
- **Purpose:** Extract, generate, enhance YAML frontmatter
- **Capabilities:**
  - Scan all docs for existing metadata patterns
  - Generate metadata from git history (dates, authors)
  - Suggest tags via TF-IDF analysis
  - Batch metadata updates

**librarian_index.py**
- **Purpose:** Build searchable catalog of all documentation
- **Output:** SQLite database + HTML index
- **Indexed:** File path, metadata, content summary, word count
- **Query:** By keywords, component, type, status, tags

**librarian_archive.py**
- **Purpose:** Automated archival of completed/stale files
- **Logic:** Status metadata + date heuristics
- **Actions:** Move to archive, update cross-refs, generate archive README

**librarian Agent**
- **Purpose:** Strategic documentation audits and real-time assistance
- **Runs:** Validation tools, then provides analysis and recommendations
- **Scope:** File organization, metadata compliance, documentation gaps, link health
- **When:** Quarterly audits, on-demand for file placement advice

---

## Coordination Mechanisms

### 1. Exclusion Pattern Alignment

**All tools MUST exclude the same directories to avoid conflicts:**

```toml
# Common exclusion pattern (applied to all tools)
EXCLUDE_DIRS = [
    ".git",
    ".cache",
    "archived_files",
    "storage",
    "__pycache__"
]
```

**Current Status:** ✅ Aligned across Black, Flake8, Vulture
**Action Required:** Ensure librarian tools respect same exclusions

### 2. File Type Routing

**Clear file type ownership prevents overlap:**

| File Extension | Validation System | Tools |
|---------------|------------------|-------|
| `.py`, `.pyi` | Code Quality | Black, Flake8, Vulture |
| `.md` | Documentation Quality | librarian_validate, librarian_metadata |
| `.json`, `.yml` | Configuration | Manual review (no auto-validation) |
| `.sh`, scripts | Manual review | shellcheck (future consideration) |

**Rule:** Each file type has ONE authoritative validation system

### 3. Worktree-Specific Validation (Integration Point)

**`/tree close` Slash Command Integration**

The `/tree close` command should run **context-aware validation** based on worktree purpose:

```yaml
# Conceptual validation routing in /tree close

IF worktree purpose contains "documentation|librarian|docs":
  RUN documentation quality validation:
    - python tools/librarian_validate.py --worktree-files
    - python tools/validate_links.py --worktree-files

ELIF worktree purpose contains "feature|bug|module":
  RUN code quality validation:
    - black --check .
    - flake8
    - vulture --min-confidence 80

ELSE:
  RUN both validation suites (hybrid worktree)
```

**Benefits:**
- **Fast:** Only validates changed files in current worktree
- **Relevant:** Runs appropriate tools for work type
- **Non-blocking:** Developers work freely, validation at close
- **Comprehensive:** Nothing merges without passing validation

**Implementation Note:**
This worktree (`librarian-improvements`) should run ONLY documentation quality validation on close, since it's focused on librarian system improvements.

### 4. CI/CD Pipeline Parallelism

**Both validation systems run in parallel for full project coverage:**

```yaml
# .github/workflows/quality-validation.yml (conceptual)

name: Quality Validation
on: [push, pull_request]

jobs:
  code-quality:
    name: Code Quality (Python)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Black formatting check
        run: black --check .
      - name: Flake8 linting
        run: flake8
      - name: Vulture dead code check
        run: vulture --min-confidence 80

  docs-quality:
    name: Documentation Quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Metadata validation
        run: python tools/librarian_validate.py --all
      - name: Link validation
        run: python tools/validate_links.py --all
      - name: Generate index
        run: python tools/librarian_index.py
```

**Benefits:**
- Parallel execution (faster)
- Independent failure (one system can pass while other fails)
- Clear error attribution (know which system found issues)

### 5. Cross-Reference Documentation

**Each system's documentation references the other for clarity:**

**In Code Quality Docs (`AUTOMATED_TOOLING_GUIDE.md`):**
> For documentation organization and metadata validation, see Librarian System (`docs/librarian-usage-guide.md`)

**In Documentation Quality Docs (`librarian-usage-guide.md`):**
> For Python code quality and formatting, see Automated Tooling Guide (`docs/development/standards/AUTOMATED_TOOLING_GUIDE.md`)

**Current Status:** ⚠️ Needs implementation
**Action Required:** Add cross-references to both guides

---

## Developer Workflows

### Workflow 1: Code Changes Only

**Scenario:** Developer modifies Python files in `/modules`

```bash
# During development (optional)
/format                    # Auto-format with Black

# Before commit (optional)
/lint                      # Run all code quality tools

# At worktree close (automatic via /tree close)
black --check .
flake8
vulture --min-confidence 80
```

**Validation:** Code quality tools only
**Skip:** Documentation quality tools (no .md changes)

### Workflow 2: Documentation Changes Only

**Scenario:** Developer updates documentation in `/docs`

```bash
# During development (optional)
python tools/librarian_validate.py docs/myfile.md

# Before commit (optional)
python tools/validate_links.py docs/myfile.md

# At worktree close (automatic via /tree close)
python tools/librarian_validate.py --worktree-files
python tools/validate_links.py --worktree-files
```

**Validation:** Documentation quality tools only
**Skip:** Code quality tools (no .py changes)

### Workflow 3: Mixed Changes (Code + Docs)

**Scenario:** Developer modifies both Python files and documentation

```bash
# At worktree close (automatic via /tree close)
# Run BOTH validation suites
black --check .
flake8
vulture --min-confidence 80
python tools/librarian_validate.py --worktree-files
python tools/validate_links.py --worktree-files
```

**Validation:** Both systems run
**Optimization:** Could run in parallel for speed

### Workflow 4: Agent-Assisted Review

**Scenario:** Developer wants comprehensive review before merge

**For code changes:**
```bash
# Invoke code-reviewer agent
# Agent automatically runs: Black, Flake8, Vulture
# Then provides: Security analysis, performance review, CLAUDE.md compliance
```

**For documentation changes:**
```bash
# Invoke librarian agent
# Agent automatically runs: librarian_validate, link validation
# Then provides: Organization analysis, metadata recommendations, gap identification
```

**Rule:** Use the agent matching your change type

---

## Configuration Files

### Code Quality Configurations

**`.black.toml`**
```toml
[tool.black]
line-length = 120
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.cache
  | archived_files
  | storage
  | __pycache__
)/
'''
```

**`.flake8`**
```ini
[flake8]
max-line-length = 120
exclude = .git,__pycache__,archived_files,.cache,storage
ignore = E203,W503
```

**`.vulture.toml`**
```toml
[tool.vulture]
min_confidence = 80
exclude = ["archived_files", ".cache", "__pycache__", "storage"]
```

### Documentation Quality Configurations

**`docs/standards/metadata-standard.md`**
- YAML frontmatter specification
- Required/recommended fields
- Valid enum values (type, status)
- Date format standards

**`FILE_ORGANIZATION_STANDARDS.md`**
- Directory structure rules
- File naming conventions
- Placement decision trees
- Archive policies

---

## Integration with `/tree close`

### Current Implementation Gap

**Status:** `/tree close` exists but doesn't run validation
**Opportunity:** Add validation as final gate before worktree closure

### Proposed Enhancement

**Add to `/tree close` workflow:**

1. **Detect worktree purpose** (from branch name, PURPOSE.md, or manual config)
2. **Identify changed files** (`git diff --name-only main...HEAD`)
3. **Route to appropriate validation:**
   - `.py` files changed → Code quality validation
   - `.md` files changed → Documentation quality validation
   - Both → Run both suites
4. **Report results** with clear pass/fail status
5. **Block close on failure** (optional, or warn-only mode)

### Example Output

```
🌳 Closing worktree: librarian-improvements
📊 Detecting validation requirements...

Changed files:
  - docs/librarian-usage-guide.md
  - tools/librarian_validate.py
  - .claude/agents/librarian.md

📚 Running documentation quality validation...

✅ Metadata validation: PASS (3/3 files)
✅ Link validation: PASS (0 broken links)
✅ File placement: PASS (all files correctly located)

🎉 Validation passed! Safe to close worktree.
```

### Implementation Note for This Worktree

**This worktree (`librarian-improvements`) should validate:**
- ✅ Documentation quality (librarian_validate, link validation)
- ❌ Code quality (skip Black/Flake8/Vulture for .py changes in tools/)

**Rationale:** These Python files are documentation *tools*, not application code. They follow different quality standards (less stringent than Flask modules).

**Future Consideration:** Create separate validation profile for tool scripts vs. application code.

---

## Best Practices

### DO ✅

1. **Use the right tool for the job**
   - Code changes → code-reviewer agent + Black/Flake8/Vulture
   - Doc changes → librarian agent + librarian_validate

2. **Run validation before `/tree close`**
   - Catch issues early, don't wait for close gate

3. **Keep exclusion patterns synchronized**
   - All tools should skip same directories

4. **Respect tool boundaries**
   - Don't mix concerns (code quality ≠ doc quality)

5. **Use agents for comprehensive review**
   - Tools catch mechanical issues
   - Agents provide strategic analysis

### DON'T ❌

1. **Don't run both validation systems on same files**
   - Wastes time, creates confusion

2. **Don't bypass validation to "save time"**
   - Technical debt compounds quickly

3. **Don't create overlapping validation**
   - If one tool already checks it, don't add another

4. **Don't hardcode worktree validation logic**
   - Make it configurable/detectable

5. **Don't use wrong agent for file type**
   - code-reviewer for .py, librarian for .md

---

## Troubleshooting

### Problem: Both validation systems fail on same commit

**Diagnosis:** Mixed code and documentation changes
**Solution:** Fix both sets of issues, or split into separate commits

### Problem: Validation passes locally, fails in CI/CD

**Diagnosis:** Environment differences (missing tools, version mismatches)
**Solution:**
- Check tool versions match (Black, Flake8, Vulture)
- Verify exclusion patterns consistent
- Run CI validation locally: `act` (GitHub Actions local runner)

### Problem: `/tree close` too slow with validation

**Diagnosis:** Running full project scan instead of worktree-specific validation
**Solution:**
- Use `--worktree-files` or `--changed-only` flags
- Only validate files modified in current worktree
- Run validation suites in parallel

### Problem: Unclear which validation system to use

**Diagnosis:** Hybrid file type (e.g., Python docstrings with documentation)
**Solution:**
- Python files → Code quality validation (Black/Flake8)
- Markdown files → Documentation quality validation (librarian)
- Docstrings → Code quality (part of Python file)

---

## Future Enhancements

### Potential Improvements

1. **Unified Validation Command**
   ```bash
   scripts/validate_all.sh --worktree-only --parallel
   ```

2. **Validation Profiles**
   ```yaml
   # .validation-profiles.yml
   application-code:
     tools: [black, flake8, vulture]
     strict: true

   tool-scripts:
     tools: [black, flake8]
     strict: false

   documentation:
     tools: [librarian_validate, link_validator]
     strict: true
   ```

3. **Pre-commit Hook Integration**
   - Fast validation on staged files only
   - File type routing (like worktree close)
   - Optional (not required for commit)

4. **Continuous Validation Dashboard**
   - Track validation metrics over time
   - Identify validation failure hotspots
   - Measure code/doc quality trends

5. **Auto-fix Capabilities**
   - Black already auto-formats
   - Add librarian auto-fix for metadata (--fix flag exists)
   - Link validation auto-update (fix broken relative paths)

---

## Related Documentation

- **Code Quality:** `docs/development/standards/AUTOMATED_TOOLING_GUIDE.md`
- **Documentation Quality:** `docs/librarian-usage-guide.md`
- **Librarian Agent:** `.claude/agents/librarian.md`
- **Code Reviewer Agent:** `.claude/agents/code-reviewer.md`
- **Metadata Standard:** `docs/standards/metadata-standard.md`
- **File Organization:** `FILE_ORGANIZATION_STANDARDS.md`

---

## Maintenance

**Review Frequency:** Quarterly (align with librarian audits)
**Last Updated:** 2025-10-17
**Owner:** Development team
**Version:** 1.0

**Changelog:**
- 2025-10-17: Initial creation, defined coordination architecture
