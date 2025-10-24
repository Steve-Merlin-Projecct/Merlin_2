# Automated Archival System

**Version:** 1.0
**Date:** 2025-10-22
**Status:** Production Ready
**Script:** `tools/auto_archive.py`

## Overview

The automated archival system identifies and moves stale documentation files to an archive directory. This keeps the active documentation focused and relevant while preserving historical content.

## Features

### Intelligent Detection
- **Age-based:** Finds files not modified in X days (default: 180)
- **Reference checking:** Skips files referenced in other documents
- **Protected files:** Never archives README.md, CLAUDE.md, CHANGELOG.md
- **Already archived:** Skips files already in archive directories

### Safe Operations
- **Dry-run by default:** Shows what would be archived without moving
- **Execute flag:** Requires explicit `--execute` to move files
- **Preserves structure:** Maintains relative paths in archive
- **Configurable threshold:** Adjust days via `--days` parameter

### Smart Exclusions
Automatically skips:
- Essential files (README.md, CLAUDE.md, etc.)
- Already archived content (paths containing "archive/archived")
- System directories (node_modules, .git, venv, __pycache__)
- Referenced files (linked from other documents)

## Usage

### Basic Commands

**Dry Run (Shows what would be archived):**
```bash
python tools/auto_archive.py
```

**Custom threshold (90 days):**
```bash
python tools/auto_archive.py --days 90
```

**Actually archive files:**
```bash
python tools/auto_archive.py --execute
```

**Specify project root:**
```bash
python tools/auto_archive.py --project-root /workspace
```

### Typical Workflow

```bash
# 1. Check what would be archived (180 days default)
python tools/auto_archive.py

# 2. Review the list of candidates
# Files are shown with reason (age + not referenced)

# 3. If satisfied, execute archival
python tools/auto_archive.py --execute

# 4. Verify files moved to docs/archived/
ls -R docs/archived/
```

## Configuration

### Age Threshold

**Default:** 180 days (6 months)

**Adjustable via `--days` flag:**
- `--days 90` - 3 months
- `--days 180` - 6 months (default)
- `--days 365` - 1 year

**Recommendation:** Use 180 days for most projects

### Protected Files

**Always preserved:**
```python
- README.md
- CLAUDE.md
- CHANGELOG.md
- Any file in docs/archived/ or docs/archive/
```

**Cannot be archived** even if old and unreferenced.

### Skip Directories

**Automatically excluded:**
```python
- node_modules/
- .git/
- venv/
- project_venv/
- __pycache__/
```

## Archive Structure

Files are moved to `docs/archived/` while preserving relative paths:

**Before:**
```
docs/
├── component_docs/
│   └── old-feature/
│       └── guide.md (stale)
└── planning/
    └── old-proposal.md (stale)
```

**After archival:**
```
docs/
├── component_docs/
│   └── old-feature/
│       (empty or removed)
├── planning/
│   (empty or removed)
└── archived/
    ├── component_docs/
    │   └── old-feature/
    │       └── guide.md
    └── planning/
        └── old-proposal.md
```

## Reference Detection

The script checks if files are referenced elsewhere:

**Detects these link formats:**
```markdown
[Link](../path/to/file.md)
[Link](/docs/path/to/file.md)
See: docs/path/to/file.md
```

**Protected if referenced:**
- Even if old, won't archive if linked from other docs
- Prevents breaking links
- Keeps dependency chains intact

**Example:**
```
File: docs/old-api.md (200 days old)
Referenced in: docs/current-guide.md
Result: NOT archived (still referenced)
```

## Output

### Dry Run Output
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

### Execute Output
```bash
$ python tools/auto_archive.py --execute

Scanning for files older than 180 days...

Archiving files...
✓ Archived: docs/planning/2024-q1-roadmap.md
  → docs/archived/planning/2024-q1-roadmap.md

✓ Archived: docs/experiments/failed-approach.md
  → docs/archived/experiments/failed-approach.md

============================================================
ARCHIVAL COMPLETE
Archived: 2 files
```

## Scheduling

### Manual Execution
```bash
# Run quarterly (every 3 months)
python tools/auto_archive.py --execute
```

### Cron Job (Linux/macOS)
```cron
# Run on first day of each quarter at 2am
0 2 1 */3 * cd /workspace && python tools/auto_archive.py --execute >> logs/archival.log 2>&1
```

### GitHub Actions (Automated)
```yaml
# .github/workflows/archive-docs.yml
name: Archive Stale Documentation

on:
  schedule:
    - cron: '0 0 1 */3 *'  # Quarterly
  workflow_dispatch:       # Manual trigger

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Archive stale docs
        run: |
          python tools/auto_archive.py --execute

      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add docs/archived/
          git commit -m "chore(docs): Archive stale documentation" || true
          git push
```

## Integration with Librarian

### Workflow Integration

**Step 1: Validation**
```bash
python tools/validate_metadata.py --all
python tools/validate_location.py --scan-root
```

**Step 2: Metrics**
```bash
python tools/collect_metrics.py --json
# Check: archive_candidates count
```

**Step 3: Archival**
```bash
python tools/auto_archive.py --execute
```

**Step 4: Rebuild Catalog**
```bash
python tools/build_index.py --rebuild
```

### CI/CD Integration

Add to documentation workflow:

```yaml
- name: Check for stale docs
  run: |
    python tools/auto_archive.py > archive-report.txt
    cat archive-report.txt

- name: Upload report
  uses: actions/upload-artifact@v3
  with:
    name: archival-candidates
    path: archive-report.txt
```

## Best Practices

### When to Archive

**Good candidates:**
- Old planning documents (roadmaps, proposals)
- Completed migration guides
- Deprecated feature docs
- Historical meeting notes
- Superseded implementation summaries

**Keep active:**
- Current API documentation
- Active architecture decisions
- Ongoing project documentation
- Frequently referenced guides

### Before Archiving

1. **Review the list** - Dry run first
2. **Check references** - Script does this, but verify
3. **Update links** - If moving manually, update references
4. **Preserve metadata** - Archive preserves file contents
5. **Document reason** - Add note in commit message

### After Archiving

1. **Test site build** - Ensure no broken links
2. **Update index** - Rebuild catalog
3. **Commit changes** - Document what was archived
4. **Announce** - Team notification if significant

## Troubleshooting

### No Files Found

**Issue:** `Would archive: 0 files`

**Causes:**
- All files are recent (< 180 days)
- All old files are referenced
- Already archived

**Solution:** Adjust threshold or check manually

### False Positives

**Issue:** Important file marked for archival

**Causes:**
- File is old but still needed
- Not properly referenced

**Solutions:**
1. Add link to file from active doc
2. Update file modification date: `touch file.md`
3. Move manually to correct location

### Permission Errors

**Issue:** `Permission denied` when archiving

**Solution:**
```bash
# Check file permissions
ls -la docs/

# Fix permissions
chmod 644 docs/**/*.md
```

## Metrics

### Success Metrics

Track these over time:
- Archive candidates count (decreasing)
- Stale docs percentage (< 5% target)
- Active doc count (stable or growing)
- Archive size (growing but controlled)

### Reporting

```bash
# Monthly metrics
python tools/collect_metrics.py --json | jq '.archive_candidates'

# Before/after comparison
python tools/auto_archive.py --days 180
python tools/auto_archive.py --execute
python tools/collect_metrics.py --json
```

## Related Documentation

- Metrics Collection: `tools/collect_metrics.py`
- Validation Scripts: `tools/validate_*.py`
- Librarian System: `tasks/librarian-enhancements/prd.md`
- File Organization: `FILE_ORGANIZATION_STANDARDS.md`

## Support

**Script location:** `tools/auto_archive.py`
**Help:** `python tools/auto_archive.py --help`
**Issues:** Report in project issue tracker

---

**Quick Reference:**

```bash
# Dry run (default)
python tools/auto_archive.py

# Custom threshold
python tools/auto_archive.py --days 90

# Execute archival
python tools/auto_archive.py --execute

# Help
python tools/auto_archive.py --help
```
