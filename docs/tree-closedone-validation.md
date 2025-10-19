# /tree closedone Validation Feature

**Version:** 1.0
**Date:** 2025-10-17
**Status:** Implemented

## Overview

The `/tree closedone` command now includes validation to ensure all worktrees have been properly closed with `/tree close` before merging. This prevents accidental merges of incomplete work and ensures proper documentation.

## Motivation

### Problems Solved

1. **Accidental Merges:** Users could merge incomplete work without documentation
2. **Lost Context:** Merges without synopsis files lose work descriptions
3. **Incomplete Tracking:** No way to know which worktrees were actually finished
4. **Manual Cleanup:** Users had to manually track which worktrees were ready

### Benefits

- ✅ **Enforced Documentation:** All merged work has synopsis files
- ✅ **Clear Status:** Know exactly which worktrees are ready to merge
- ✅ **Prevented Mistakes:** Catch incomplete work before merging
- ✅ **Better Tracking:** Historical record of what was accomplished

## How It Works

### Default Behavior (Validation Enabled)

When you run `/tree closedone`, the system:

1. **Scans all worktrees** in `.trees/` directory
2. **Checks for synopsis files** in `.trees/.completed/`
3. **Identifies unclosed worktrees** (no synopsis file)
4. **Displays summary** if any unclosed worktrees found
5. **Exits gracefully** without merging

### Example Output

```bash
$ /tree closedone

🌳 /tree closedone - Batch Merge & Cleanup

⚠️  Cannot proceed: 3 worktree(s) have not been closed

The following worktrees need to be closed with '/tree close' before merging:

  • feature-authentication
    Branch: task/01-feature-authentication
    Path: /workspace/.trees/feature-authentication

  • feature-dashboard
    Branch: task/02-feature-dashboard
    Path: /workspace/.trees/feature-dashboard

  • feature-api
    Branch: task/03-feature-api
    Path: /workspace/.trees/feature-api

Options:
  1. Close each worktree: cd /workspace/.trees/<worktree> && /tree close
  2. Use --force to merge all worktrees anyway: /tree closedone --force

💡 Tip: The --force flag will merge all worktrees, but you'll lose
   the structured synopsis and work description for unclosed worktrees.
```

## Usage

### Standard Workflow (Recommended)

```bash
# 1. Complete work in each worktree
cd /workspace/.trees/feature-1
# ... make changes ...
git commit -m "Complete feature 1"

# 2. Close the worktree (creates synopsis)
/tree close
# Prompted to describe work completed
# Synopsis saved to .trees/.completed/

# 3. Repeat for all worktrees
cd /workspace/.trees/feature-2
# ... work ...
/tree close

# 4. Back to main workspace
cd /workspace

# 5. Merge all closed worktrees
/tree closedone
# ✅ Validation passes - all worktrees closed
# Proceeds with merge
```

### Force Merge (Bypass Validation)

Use `--force` when you need to merge everything regardless of close status:

```bash
# Merge all worktrees, even unclosed ones
/tree closedone --force

# Output:
# ⚠️  --force flag used: merging all worktrees regardless of close status
# ... proceeds with merge ...
```

**When to use --force:**
- Emergency situations
- Cleaning up old worktrees
- You don't need synopsis documentation
- Experimental work that doesn't need tracking

**Caution:** Using `--force` means you'll lose the structured synopsis for unclosed worktrees.

### Dry Run Testing

Preview validation without making changes:

```bash
# Check which worktrees would be merged
/tree closedone --dry-run

# Test force merge without executing
/tree closedone --force --dry-run
```

## Technical Details

### Validation Logic

**File:** `.claude/scripts/tree.sh` - `validate_all_worktrees_closed()` function

**Algorithm:**
1. Find all directories in `.trees/` (excluding `.completed`, `.archived`, etc.)
2. Find all synopsis files in `.trees/.completed/` (format: `*-synopsis-*.md`)
3. Extract worktree names from synopsis filenames
4. Compare: Active worktrees vs Closed worktrees
5. Identify unclosed = Active - Closed

**Synopsis File Format:**
```
worktree-name-synopsis-20251017-123456.md
```

Where:
- `worktree-name` = name of the worktree directory
- `20251017-123456` = timestamp (YYYYMMDD-HHMMSS)

### Command Line Options

| Option | Description | Behavior |
|--------|-------------|----------|
| (none) | Standard merge | Validates all closed |
| `--force` | Force merge | Bypasses validation |
| `--dry-run` | Preview only | Shows what would happen |
| `--yes` | Skip confirmation | Auto-confirms prompts |
| `--full-cycle` | Full automation | Includes validation |

### Flag Combinations

```bash
# Safe: Preview with validation
/tree closedone --dry-run

# Safe: Preview force merge
/tree closedone --force --dry-run

# Risky: Force merge without confirmation
/tree closedone --force --yes

# Automated: Full cycle with validation
/tree closedone --full-cycle --yes

# Automated: Full cycle with force
/tree closedone --full-cycle --force --yes
```

## Integration with Existing Workflows

### /tree close

The `/tree close` command creates the synopsis file that validation checks for:

```bash
# In worktree
/tree close

# Creates:
# - .trees/.completed/worktree-name-synopsis-<timestamp>.md
# - Validation will now recognize this worktree as closed
```

### /tree closedone --full-cycle

The `--full-cycle` workflow also uses validation:

```bash
# Full cycle requires all worktrees closed
/tree closedone --full-cycle

# Or force if needed
/tree closedone --full-cycle --force
```

## Error Handling

### No Worktrees

```bash
$ /tree closedone

🌳 /tree closedone - Batch Merge & Cleanup
⚠️  No completed worktrees found (no synopsis files)
```

### All Closed

```bash
$ /tree closedone

🌳 /tree closedone - Batch Merge & Cleanup
ℹ  Discovering completed worktrees...
✓ Found 3 completed worktree(s)

  1. feature-auth (task/01-feature-auth → develop/v4.3.3)
     Commits to merge: 5
  2. feature-dashboard (task/02-feature-dashboard → develop/v4.3.3)
     Commits to merge: 8
  3. feature-api (task/03-feature-api → develop/v4.3.3)
     Commits to merge: 3

Merge 3 completed worktree(s)? (y/n):
```

### Mixed State (Some Closed, Some Not)

```bash
$ /tree closedone

🌳 /tree closedone - Batch Merge & Cleanup

⚠️  Cannot proceed: 2 worktree(s) have not been closed

The following worktrees need to be closed with '/tree close' before merging:

  • feature-incomplete-1
    Branch: task/04-feature-incomplete-1
    Path: /workspace/.trees/feature-incomplete-1

  • feature-incomplete-2
    Branch: task/05-feature-incomplete-2
    Path: /workspace/.trees/feature-incomplete-2

# Note: Closed worktrees (feature-auth, feature-dashboard, feature-api)
# are NOT shown in this list - they're ready to merge
```

## Troubleshooting

### "Cannot proceed" but worktree is finished

**Problem:** You completed work but didn't run `/tree close`

**Solution:**
```bash
cd /workspace/.trees/your-worktree
/tree close
# Describe your work
# Now closedone will recognize it as closed
```

### Need to merge urgently without synopsis

**Problem:** Emergency merge needed, no time for synopsis

**Solution:**
```bash
/tree closedone --force
# Bypasses validation
# Merges everything immediately
```

### Synopsis file exists but still shows as unclosed

**Problem:** Synopsis filename doesn't match worktree name

**Solution:**
Check synopsis filename format:
```bash
ls -la /workspace/.trees/.completed/

# Should be: worktree-name-synopsis-20251017-123456.md
# NOT: synopsis-worktree-name.md or other formats
```

### Want to see what would be merged

**Problem:** Unsure which worktrees are ready

**Solution:**
```bash
# Preview without force
/tree closedone --dry-run
# Shows validation results

# Preview with force
/tree closedone --force --dry-run
# Shows what would be merged
```

## Migration Guide

### For Existing Worktrees

If you have unclosed worktrees from before this feature:

**Option 1: Close them properly (recommended)**
```bash
# For each worktree
cd /workspace/.trees/old-worktree
/tree close
# Document what was done
```

**Option 2: Force merge once**
```bash
# Merge everything this time
/tree closedone --force

# Future worktrees will be validated
```

### For Scripts/Automation

If you have scripts that call `/tree closedone`:

**Update scripts to handle validation:**
```bash
# Before (old behavior)
/tree closedone --yes

# After (with validation)
# Option 1: Ensure all closed first
for worktree in $(ls .trees/); do
    cd .trees/$worktree
    /tree close
done
cd /workspace
/tree closedone --yes

# Option 2: Use force if validation not needed
/tree closedone --force --yes
```

## Best Practices

### Do's

✅ **Always close worktrees** when work is complete
✅ **Write descriptive synopses** for better tracking
✅ **Use --dry-run** to preview merges
✅ **Review validation output** before using --force
✅ **Document in synopsis** what was accomplished

### Don'ts

❌ **Don't use --force habitually** - defeats the purpose
❌ **Don't close worktrees prematurely** - finish work first
❌ **Don't skip synopsis descriptions** - they're valuable documentation
❌ **Don't manually edit synopsis files** - use `/tree close` command
❌ **Don't delete synopsis files** - they're needed for validation

## Performance Impact

- **Validation overhead:** <1 second for 10-20 worktrees
- **No impact on merge time:** Only adds check before merge
- **Minimal disk usage:** Synopsis files are ~1-5KB each

## Future Enhancements

Potential improvements:

1. **Partial Close:** Allow closing subset of files in worktree
2. **Synopsis Templates:** Structured synopsis with sections
3. **Batch Close:** Close multiple worktrees at once
4. **Close Reminders:** Notify when worktree has uncommitted changes
5. **Synopsis Search:** Search across all synopsis files

## Related Documentation

- [Tree Command Guide](/workspace/docs/tree-command-guide.md)
- [Tree Slash Command](/workspace/.claude/commands/tree.md)
- [Full-Cycle Workflow](/workspace/tasks/tree-workflow-full-cycle/prd.md)

## Version History

- **1.0** (2025-10-17): Initial implementation with --force flag

## Support

For issues or questions:
1. Check validation output carefully
2. Use `--dry-run` to preview
3. Review synopsis files in `.trees/.completed/`
4. Try `--force` if validation is incorrect

---

**Status:** ✅ Production Ready
**Breaking Change:** Yes (adds validation by default)
**Mitigation:** Use `--force` flag for old behavior
