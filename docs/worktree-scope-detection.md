---
title: "Worktree Scope Detection"
type: technical_doc
component: general
status: draft
tags: []
---

# Worktree Scope Detection System

**Version:** 1.0
**Date:** 2025-10-18
**Status:** Production Ready

## Overview

The Worktree Scope Detection System automatically infers and enforces file boundaries for git worktrees based on feature descriptions. This prevents conflicts, enables parallel development, and provides a special "librarian" worktree for documentation and tooling work.

## Key Features

1. **Automatic Scope Detection**: Infers file patterns from feature descriptions
2. **Soft Enforcement**: Pre-commit hooks warn about out-of-scope changes
3. **Hard Enforcement**: Optional blocking of out-of-scope commits
4. **Librarian Worktree**: Special worktree with inverse scope for docs/tooling
5. **Conflict Detection**: Identifies overlapping scopes across worktrees

## How It Works

### Scope Detection Algorithm

When you create a worktree with `/tree build`, the system:

1. **Analyzes the feature description** for keywords
2. **Matches keywords to file patterns** using predefined mappings
3. **Generates a `.worktree-scope.json` manifest** with include/exclude patterns
4. **Installs a pre-commit hook** for scope enforcement
5. **Updates PURPOSE.md** with detected scope information

### Pattern Mappings

The system recognizes these keywords and maps them to file patterns:

| Keyword | File Patterns |
|---------|---------------|
| `email`, `gmail`, `smtp` | `modules/email_integration/**` |
| `oauth` | `modules/email_integration/*oauth*.py` |
| `document`, `docx`, `template` | `modules/document_generation/**` |
| `resume`, `cover` | `modules/document_generation/*resume*.py`, etc. |
| `database`, `schema`, `migration` | `modules/database/**` |
| `api`, `endpoint`, `route` | `modules/api/**` |
| `dashboard`, `frontend`, `ui` | `frontend_templates/**` |
| `ai`, `gemini`, `llm` | `modules/ai_job_description_analysis/**` |
| `scraping`, `scrape`, `spider` | `modules/scraping/**` |
| `storage`, `s3`, `gcs` | `modules/storage/**` |
| `test`, `pytest` | `tests/**` |
| `doc`, `documentation` | `docs/**` |

**Fallback behavior:** If no keywords match, the system creates a module-specific scope based on the worktree name.

### Scope Manifest Format

Each worktree gets a `.worktree-scope.json` file:

```json
{
  "worktree": "email-oauth-refresh",
  "description": "Email OAuth refresh tokens",
  "scope": {
    "include": [
      "modules/email_integration/**",
      "modules/email_integration/*oauth*.py",
      "tests/test_*email_oauth_refresh*.py",
      "docs/*email-oauth-refresh*.md"
    ],
    "exclude": [
      "**/__pycache__/**",
      "**/*.pyc",
      ".git/**",
      "**/.DS_Store"
    ]
  },
  "enforcement": "soft",
  "created": "2025-10-18T05:04:40+00:00",
  "out_of_scope_policy": "warn"
}
```

## Librarian Worktree

### What is the Librarian?

The librarian worktree is automatically created with **inverse scope** - it can work on files that no other worktree claims.

**Librarian scope includes:**
- Documentation files (`docs/**`, `*.md`)
- Tooling and scripts (`.claude/**`, `tools/**`, `scripts/**`)
- Configuration files (`*.toml`, `*.yaml`, `*.json`)
- GitHub workflows (`.github/**`)
- Task templates (`tasks/**`)

**Librarian scope excludes:**
- All patterns claimed by feature worktrees

### When to Use Librarian

Use the librarian worktree for:
- Updating documentation
- Improving tooling and scripts
- Modifying configuration files
- Creating task templates
- GitHub workflow changes

### Librarian Creation

The librarian is automatically created when you run `/tree build` with feature worktrees:

```bash
/tree stage Email OAuth improvements
/tree stage Dashboard analytics
/tree build

# Creates 3 worktrees:
# 1. email-oauth-improvements (task/01-*)
# 2. dashboard-analytics (task/02-*)
# 3. librarian (task/00-librarian) ← Automatically created
```

## Enforcement Modes

### Soft Enforcement (Default)

**Behavior:** Warns about out-of-scope files but allows commits

```bash
# When committing out-of-scope files:
⚠️  Scope Validation Warning

The following files are outside this worktree's defined scope:
  ⚠  modules/database/schema.py
  ⚠  modules/api/routes.py

✓ Soft enforcement - proceeding with warning
```

**When to use:**
- Default for all worktrees
- Provides flexibility while maintaining awareness
- Allows justified exceptions

### Hard Enforcement

**Behavior:** Blocks commits with out-of-scope files

**Enable by editing `.worktree-scope.json`:**

```json
{
  "enforcement": "hard",
  ...
}
```

**When committing out-of-scope files:**

```bash
❌ Hard enforcement enabled - commit blocked

Options:
  1. Only commit in-scope files
  2. Update .worktree-scope.json to include these files
  3. Change enforcement mode to 'soft'
```

**When to use:**
- Strict parallel development with no cross-contamination
- Team environments with clear boundaries
- Preventing accidental scope creep

### No Enforcement

**Behavior:** Completely disables scope checking

**Enable by editing `.worktree-scope.json`:**

```json
{
  "enforcement": "none",
  ...
}
```

## Conflict Detection

### Automatic Detection

The system automatically checks for scope conflicts after building worktrees:

```bash
/tree build

# Output includes:
🔍 Scope Conflict Detection
✓ No scope conflicts detected
All worktrees have non-overlapping scopes
```

### Manual Detection

Check for conflicts at any time:

```bash
/tree scope-conflicts
```

### Handling Conflicts

If conflicts are detected:

```bash
⚠ Scope conflicts detected

CONFLICTS DETECTED:
  Pattern: modules/email_integration/**
    Owned by: email-oauth-refresh, email-smtp-improvements

Resolution options:
  1. Adjust scope patterns in .worktree-scope.json files
  2. Merge related worktrees
  3. Use enforcement: 'hard' to block conflicting commits
```

**Resolution strategies:**

1. **Refine patterns**: Make scopes more specific
   ```json
   // Before (conflict)
   "include": ["modules/email_integration/**"]

   // After (no conflict)
   "include": ["modules/email_integration/*oauth*.py"]
   ```

2. **Merge worktrees**: Combine related features

3. **Accept overlap**: If intentional, keep soft enforcement

## Usage Examples

### Example 1: Email Feature

```bash
/tree stage Email OAuth refresh token implementation
/tree build

# Generated scope:
# - modules/email_integration/**
# - modules/email_integration/*oauth*.py
# - tests/test_*email_oauth_refresh*.py
```

### Example 2: Dashboard Feature

```bash
/tree stage Dashboard analytics and reporting features
/tree build

# Generated scope:
# - frontend_templates/**
# - tests/test_*dashboard_analytics*.py
```

### Example 3: Database Migration

```bash
/tree stage Database schema migration for user profiles
/tree build

# Generated scope:
# - modules/database/**
# - modules/database/schema*.py
# - modules/database/migrations/**
# - tests/test_*database_schema_migration*.py
```

### Example 4: Working in Librarian

```bash
# After /tree build creates librarian worktree
cd /workspace/.trees/librarian

# Can work on:
vim docs/api-documentation.md           # ✓ In scope
vim .claude/scripts/new-tool.sh          # ✓ In scope
vim tasks/new-task-template.md           # ✓ In scope

# Cannot work on (excluded by feature worktrees):
vim modules/email_integration/gmail.py   # ✗ Out of scope
```

## Customizing Scope

### Manual Scope Adjustment

Edit `.worktree-scope.json` in the worktree:

```json
{
  "scope": {
    "include": [
      "modules/email_integration/**",
      "modules/notifications/**"  // ← Add pattern
    ],
    ...
  }
}
```

### Adding New Pattern Mappings

Edit `.claude/scripts/scope-detector.sh`:

```bash
declare -A SCOPE_PATTERNS=(
    ...
    ["notification"]="modules/notifications/**"  # ← Add mapping
)
```

## Pre-Commit Hook

### How It Works

Each worktree gets a pre-commit hook that:

1. Gets list of staged files
2. Checks each against `.worktree-scope.json`
3. Reports in-scope vs out-of-scope files
4. Allows/blocks based on enforcement mode

### Hook Location

`.git/hooks/pre-commit` in each worktree

### Bypassing the Hook (Not Recommended)

```bash
# Emergency only - defeats the purpose
git commit --no-verify
```

## Troubleshooting

### "No patterns matched" Warning

**Problem:** Feature description didn't match any keywords

**Solution:**
1. Use more descriptive keywords in your feature description
2. Manually edit `.worktree-scope.json` after creation
3. The system creates a fallback scope based on worktree name

### Files Incorrectly Marked Out of Scope

**Problem:** Hook warns about files that should be in scope

**Solution:**
```bash
# Edit .worktree-scope.json
vim .worktree-scope.json

# Add the pattern:
{
  "scope": {
    "include": [
      "modules/your_module/**",
      "path/to/your/files/**"  # ← Add this
    ]
  }
}
```

### Librarian Can't Access Needed Files

**Problem:** Librarian scope excludes files you need

**Solution:**
1. Check if file is claimed by a feature worktree
2. If yes: Work in that feature worktree instead
3. If no: File should be in librarian scope (check `.worktree-scope.json`)

### Want to Disable Scope Checking

**Problem:** Scope checking is too restrictive

**Solution:**
```json
// In .worktree-scope.json
{
  "enforcement": "none"
}
```

## Best Practices

### Do's

✅ **Use descriptive feature names** with relevant keywords
✅ **Review generated scopes** in PURPOSE.md after build
✅ **Keep scopes focused** on the specific feature
✅ **Use librarian** for documentation/tooling changes
✅ **Run scope-conflicts** before starting work
✅ **Adjust scopes** if your work legitimately needs more files

### Don'ts

❌ **Don't disable enforcement** without good reason
❌ **Don't use `--no-verify`** to bypass hooks
❌ **Don't ignore scope warnings** - investigate first
❌ **Don't create overly broad scopes** like `**/*`
❌ **Don't manually edit hook files** - they're generated

## Technical Details

### Components

1. **`scope-detector.sh`**: Core detection and validation logic
2. **`scope-enforcement-hook.sh`**: Pre-commit hook implementation
3. **`tree.sh`**: Integration with worktree workflow
4. **`.worktree-scope.json`**: Scope manifest in each worktree

### Performance

- **Scope detection**: <100ms per worktree
- **Pre-commit validation**: <200ms for typical commits
- **Conflict detection**: <500ms for 10-20 worktrees

### Limitations

1. **Pattern-based matching**: Uses glob patterns, not semantic analysis
2. **Keyword-dependent**: Requires recognizable keywords in descriptions
3. **No dynamic scope**: Scope set at creation time, manual updates needed
4. **Python dependency**: Uses Python for glob matching

## Future Enhancements

Potential improvements:

1. **AI-powered scope inference**: Use LLM to analyze feature descriptions
2. **Dynamic scope adjustment**: Auto-expand scope when needed
3. **Visual scope browser**: Web UI to view/manage scopes
4. **Scope templates**: Pre-defined scopes for common feature types
5. **Cross-worktree analytics**: Track which files change together
6. **Scope inheritance**: Child worktrees inherit parent scope

## Related Documentation

- [Tree Command Guide](tree-command-guide.md)
- [Tree Slash Command](../.claude/commands/tree.md)
- [Tree Closedone Validation](tree-closedone-validation.md)

## Version History

- **1.0** (2025-10-18): Initial implementation with 5-phase system

## Support

For issues or questions:
1. Check `.worktree-scope.json` for current scope
2. Review PURPOSE.md for detected patterns
3. Use `/tree scope-conflicts` to detect overlaps
4. Adjust enforcement mode if needed (`soft`/`hard`/`none`)

---

**Status:** ✅ Production Ready
**Breaking Change:** No (opt-in feature)
**Integration:** Automatic with `/tree build`
