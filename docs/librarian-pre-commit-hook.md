# Librarian Pre-Commit Hook Documentation

**Version:** 1.0
**Date:** 2025-10-22
**Status:** Production Ready

## Overview

The librarian pre-commit hook automatically validates documentation quality before commits, ensuring consistent standards across the project.

## Features

### Automatic Validation
The hook runs three checks on all staged markdown files:

1. **YAML Frontmatter Validation**
   - Ensures required fields exist (`title`, `type`, `component`, `status`)
   - Validates enum values
   - Checks field formatting

2. **File Location Compliance**
   - Verifies files are in correct directories
   - Follows `FILE_ORGANIZATION_STANDARDS.md` rules
   - Suggests correct locations for misplaced files

3. **Broken Link Detection**
   - Finds broken internal links
   - Reports line numbers
   - Skips external URLs (not validated)

### User-Friendly Output
- ✅ Green checkmarks for passing files
- ❌ Red X marks for failing files
- Clear error messages with fix suggestions
- Line numbers for link errors

## Installation

### Quick Install

```bash
# From project root
bash tools/install_hooks.sh
```

### Manual Install

```bash
# Main workspace
cp tools/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Worktree (use git rev-parse to find correct hooks directory)
GIT_DIR=$(git rev-parse --git-dir)
cp tools/hooks/pre-commit "$GIT_DIR/hooks/pre-commit"
chmod +x "$GIT_DIR/hooks/pre-commit"
```

### Verify Installation

```bash
# Check if hook exists
ls -l .git/hooks/pre-commit  # Or $(git rev-parse --git-dir)/hooks/pre-commit

# Test hook manually
bash .git/hooks/pre-commit
```

## Usage

### Normal Workflow
The hook runs automatically:

```bash
# Make changes to markdown files
vi docs/my-document.md

# Stage changes
git add docs/my-document.md

# Commit - hook runs automatically
git commit -m "docs: Add new documentation"

# Output:
# Running documentation validation checks...
# Validating 1 markdown file(s)...
#
# Check 1/3: Validating YAML frontmatter...
#   ✓ docs/my-document.md
#
# Check 2/3: Validating file placement...
#   ✓ docs/my-document.md
#
# Check 3/3: Checking for broken links...
#   ✓ docs/my-document.md
#
# ==========================================
# ✓ All checks passed!
```

### When Validation Fails

```bash
$ git commit -m "docs: Update guide"

Running documentation validation checks...
Validating 1 markdown file(s)...

Check 1/3: Validating YAML frontmatter...
  ✗ docs/my-document.md
    Error: Missing required field: 'title'

Check 2/3: Validating file placement...
  ✓ docs/my-document.md

Check 3/3: Checking for broken links...
  ✗ docs/my-document.md
    Line 15: Broken link: docs/non-existent.md

==========================================
✗ Validation failed

To fix:
  1. Add missing YAML frontmatter (use: python tools/validate_metadata.py --fix <file>)
  2. Move files to correct location (see suggestions above)
  3. Fix broken links

To bypass (not recommended): git commit --no-verify
```

### Bypass Hook (Emergency Only)

```bash
# Skip validation (not recommended)
git commit --no-verify -m "Emergency hotfix"
```

**⚠️ Warning:** Only bypass for urgent fixes. Create follow-up issue to fix validation errors.

## Validation Details

### 1. YAML Frontmatter Validation

**Required fields:**
```yaml
---
title: Document Title
type: guide|reference|howto|architecture|api
component: module-name
status: draft|current|deprecated|archived
---
```

**Optional fields:**
```yaml
created: 2025-01-15
modified: 2025-01-20
related: other-doc.md, another-doc.md
tags: tag1, tag2, tag3
```

**Auto-fix:**
```bash
python tools/validate_metadata.py --fix docs/my-document.md
```

### 2. File Location Compliance

**Rules enforced:**
- Component docs: `docs/component_docs/<component>/`
- Architecture docs: `docs/architecture/`
- API docs: `docs/api/`
- Setup guides: `docs/setup/`
- Root directory: Maximum 10 files

**Check specific file:**
```bash
python tools/validate_location.py docs/my-document.md
```

### 3. Broken Link Detection

**What's checked:**
- Relative links: `[Link](../other-doc.md)`
- Absolute links: `[Link](/docs/guide.md)`
- Anchor links: `[Link](#section)` (basic validation)

**What's skipped:**
- External URLs: `https://example.com`
- Email links: `mailto:user@example.com`
- JavaScript: `javascript:void(0)`

**Check links:**
```bash
python tools/validate_links.py docs/my-document.md --json
```

## Troubleshooting

### Hook Not Running

**Problem:** Commit succeeds without validation
**Solution:**
```bash
# Verify hook exists
ls -l $(git rev-parse --git-dir)/hooks/pre-commit

# If missing, reinstall
bash tools/install_hooks.sh
```

### Python Command Not Found

**Problem:** `python: command not found`
**Solution:**
```bash
# Check Python installation
python3 --version

# Update hook to use python3
sed -i 's/python /python3 /g' $(git rev-parse --git-dir)/hooks/pre-commit
```

### Hook Fails on Valid Files

**Problem:** False positives
**Solution:**
```bash
# Test validation manually
python tools/validate_metadata.py docs/my-document.md
python tools/validate_location.py docs/my-document.md
python tools/validate_links.py docs/my-document.md

# Check for specific errors
# Fix as needed
```

### Slow Hook Performance

**Problem:** Hook takes too long
**Solution:**
- Hook only validates staged files (not entire repo)
- Consider splitting large commits
- For bulk imports, use `--no-verify` then fix separately

## Integration with Worktrees

### Automatic Installation
The `/tree build` command should automatically install hooks in new worktrees.

### Manual Installation in Worktrees
```bash
cd /workspace/.trees/my-worktree
bash /workspace/tools/install_hooks.sh
```

### Worktree-Specific Behavior
- Hook validates against project root's validation scripts
- Works identically in worktrees and main workspace
- Shares same configuration

## Best Practices

### When Creating New Docs
1. Add YAML frontmatter first
2. Place in correct directory
3. Verify links exist
4. Run validation before staging:
   ```bash
   python tools/validate_metadata.py docs/my-doc.md
   python tools/validate_location.py docs/my-doc.md
   python tools/validate_links.py docs/my-doc.md
   ```

### When Editing Existing Docs
1. Preserve existing frontmatter
2. Update `modified` date
3. Check links after renames/moves
4. Test hook before commit:
   ```bash
   git add docs/my-doc.md
   bash $(git rev-parse --git-dir)/hooks/pre-commit
   ```

### When Bypassing Hook
1. Only for emergencies
2. Create follow-up issue immediately
3. Document why bypass was needed
4. Fix validation errors ASAP

## CI/CD Integration

The pre-commit hook complements CI/CD checks:

- **Pre-commit hook:** Fast feedback on local machine
- **CI/CD workflow:** Comprehensive validation on push
- **Both use same validation scripts:** Consistent standards

For CI/CD setup, see: `docs/librarian-ci-cd-workflow.md`

## Maintenance

### Updating Hook
```bash
# Edit source
vi tools/hooks/pre-commit

# Reinstall
bash tools/install_hooks.sh
```

### Adding New Checks
1. Create validation script in `tools/`
2. Add check to `tools/hooks/pre-commit`
3. Update documentation
4. Reinstall hook

### Disabling Hook (Temporary)
```bash
# Rename hook
mv $(git rev-parse --git-dir)/hooks/pre-commit $(git rev-parse --git-dir)/hooks/pre-commit.disabled

# Re-enable
mv $(git rev-parse --git-dir)/hooks/pre-commit.disabled $(git rev-parse --git-dir)/hooks/pre-commit
```

## Related Documentation

- Validation scripts: `tools/README.md`
- File organization: `FILE_ORGANIZATION_STANDARDS.md`
- Librarian system: `tasks/librarian-enhancements/prd.md`
- CI/CD workflow: `docs/librarian-ci-cd-workflow.md`

## Support

**Issues:** Report in project issue tracker
**Questions:** Ask in team chat
**Documentation:** This file and `tools/README.md`

---

**Quick Reference:**

```bash
# Install hook
bash tools/install_hooks.sh

# Test manually
bash $(git rev-parse --git-dir)/hooks/pre-commit

# Fix metadata
python tools/validate_metadata.py --fix <file>

# Bypass (emergency only)
git commit --no-verify
```
