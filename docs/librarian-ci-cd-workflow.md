---
title: "Librarian Ci Cd Workflow"
type: process
component: general
status: draft
tags: []
---

# Librarian CI/CD Workflow Documentation

**Version:** 1.0
**Date:** 2025-10-22
**Status:** Production Ready
**Workflow File:** `.github/workflows/validate-docs.yml`

## Overview

The Librarian CI/CD workflow provides automated documentation quality validation on GitHub Actions. It runs comprehensive checks on every push and pull request, ensuring documentation standards are maintained across the project.

## Features

### Automated Validation Checks
1. **YAML Frontmatter Validation** - Ensures all markdown files have proper metadata
2. **File Location Compliance** - Verifies files are in correct directories
3. **Broken Link Detection** - Finds internal links that point to non-existent files
4. **Metrics Collection** - Generates documentation coverage reports
5. **Job Summaries** - Creates detailed reports in GitHub Actions UI

### Smart Triggers
The workflow only runs when relevant files change:
- Any markdown file (`**.md`)
- Tools directory (`tools/**`)
- The workflow file itself (`.github/workflows/validate-docs.yml`)

### Rich Reporting
- ✅ Visual pass/fail indicators
- 📊 Metrics dashboard in job summary
- 📁 Downloadable validation reports
- 🔍 Detailed error messages with file paths

## Workflow Structure

### Trigger Events

```yaml
on:
  push:
    branches: ['**']          # All branches
    paths:                    # Only when these change
      - '**.md'
      - 'tools/**'
      - '.github/workflows/validate-docs.yml'

  pull_request:
    branches: ['main', 'develop/**']
    paths:
      - '**.md'
      - 'tools/**'
```

### Jobs

#### Job: `validate-documentation`
**Runs on:** `ubuntu-latest`
**Python version:** `3.11`

**Steps:**

1. **Checkout code**
   - Uses: `actions/checkout@v3`
   - Fetches full history for better analysis

2. **Set up Python**
   - Uses: `actions/setup-python@v4`
   - Installs Python 3.11

3. **Install dependencies**
   - Installs from `tools/requirements.txt`
   - Ensures PyYAML is available

4. **Validate metadata**
   - Runs: `python tools/validate_metadata.py --all`
   - Checks YAML frontmatter on all markdown files
   - Continues on error to collect all issues

5. **Validate file locations**
   - Runs: `python tools/validate_location.py --scan-root`
   - Checks file placement compliance
   - Identifies root directory violations

6. **Check broken links**
   - Runs: `python tools/validate_links.py --all --json`
   - Generates JSON report of broken links
   - Saves to `links_report.json`

7. **Collect metrics**
   - Runs: `python tools/collect_metrics.py`
   - Generates human-readable metrics report

8. **Generate coverage report**
   - Runs: `python tools/collect_metrics.py --json`
   - Extracts key metrics using `jq`
   - Sets environment variables for summary

9. **Upload reports**
   - Uses: `actions/upload-artifact@v3`
   - Always runs (even on failure)
   - Saves: `metrics_report.txt`, `metrics.json`, `links_report.json`

10. **Create job summary**
    - Generates markdown summary in GitHub UI
    - Shows metrics and validation status
    - Always runs (even on failure)

11. **Check for failures**
    - Fails workflow if metadata or location validation failed
    - Link validation failures don't block (informational only)

12. **Success message**
    - Shows success notice if all checks pass

## Usage

### Automatic Execution
The workflow runs automatically on:
```bash
# Push to any branch (if markdown or tools changed)
git push origin feature/my-feature

# Pull request to main or develop branches
gh pr create --base main
```

### Viewing Results

#### In GitHub Actions UI
1. Go to repository on GitHub
2. Click "Actions" tab
3. Find your workflow run
4. Click to see detailed results

#### Job Summary
GitHub automatically generates a rich summary:

```markdown
## 📚 Documentation Validation Results

### 📊 Metrics
- **Total Documents:** 504
- **Metadata Coverage:** 28.97%
- **Root Violations:** 53
- **Broken Links:** 0

### ✅ Validation Checks
- ✅ Metadata validation passed
- ❌ File location validation failed
- ✅ Link validation passed
```

#### Downloading Reports
1. Scroll to bottom of workflow run
2. Find "Artifacts" section
3. Download `documentation-reports.zip`
4. Extract to view detailed reports

### Manual Trigger
You can also run the workflow manually:
1. Go to "Actions" tab
2. Select "Documentation Validation"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

## Validation Details

### 1. Metadata Validation

**Command:** `python tools/validate_metadata.py --all`

**Checks:**
- Required fields present (`title`, `type`, `component`, `status`)
- Field values are valid enums
- YAML is properly formatted
- Metadata block is at file start

**Example output:**
```
Validating: docs/my-guide.md
✓ Passed

Validating: docs/broken.md
✗ Failed
Error: Missing required field: 'title'
Error: Invalid status value: 'wip' (must be: draft, current, deprecated, archived)
```

### 2. Location Validation

**Command:** `python tools/validate_location.py --scan-root`

**Checks:**
- Files are in correct directories per `FILE_ORGANIZATION_STANDARDS.md`
- Root directory has ≤10 files
- Component docs are in `docs/component_docs/<component>/`
- Architecture docs are in `docs/architecture/`

**Example output:**
```
Scanning root directory...
Found 53 violations

VIOLATION: README_OLD.md
  Location: /workspace/README_OLD.md
  Should be in: docs/archive/
  Reason: Old documentation should be archived

Suggested fixes:
  git mv README_OLD.md docs/archive/README_OLD.md
```

### 3. Link Validation

**Command:** `python tools/validate_links.py --all --json`

**Checks:**
- Internal links point to existing files
- Relative paths are correct
- Absolute paths from repo root exist
- Reports line numbers for broken links

**JSON Output:**
```json
{
  "total_files": 504,
  "files_with_broken_links": 0,
  "total_broken_links": 0,
  "broken_links": []
}
```

### 4. Metrics Collection

**Command:** `python tools/collect_metrics.py --json`

**Metrics:**
- Total documentation files
- Total code files
- Metadata coverage percentage
- Stale documents (>90 days old)
- Archive candidates (>180 days old)
- Root directory violations
- Broken links count
- Documentation by component
- Documentation by type

**JSON Output:**
```json
{
  "total_docs": 504,
  "total_code_files": 315,
  "docs_with_metadata": 146,
  "metadata_coverage_pct": 28.97,
  "broken_links_count": 0,
  "stale_docs_count": 0,
  "archive_candidates": 0,
  "root_violations": 53,
  "docs_by_component": {...},
  "docs_by_type": {...}
}
```

## Integration with Pre-Commit Hook

The CI/CD workflow complements the local pre-commit hook:

| Feature | Pre-Commit Hook | CI/CD Workflow |
|---------|----------------|----------------|
| **Runs when** | Before local commit | On push/PR to GitHub |
| **Validates** | Staged files only | All markdown files |
| **Speed** | Fast (local) | Slower (cloud) |
| **Blocking** | Blocks commit | Blocks merge (if configured) |
| **Reports** | Terminal output | GitHub UI + artifacts |
| **Bypass** | `--no-verify` | Admin override |

**Recommended workflow:**
1. Pre-commit hook catches issues early (local)
2. CI/CD provides comprehensive validation (cloud)
3. Both use same validation scripts (consistent)

## Failure Scenarios

### When Metadata Validation Fails

**Symptom:** Red X on workflow, job fails

**Cause:** Markdown files missing required frontmatter

**Fix:**
```bash
# Download reports artifact
# Review metadata_report.txt

# Fix files locally
python tools/validate_metadata.py --fix docs/broken.md

# Commit and push
git add docs/broken.md
git commit -m "fix: Add missing metadata"
git push
```

### When Location Validation Fails

**Symptom:** Red X on workflow, job fails

**Cause:** Files in wrong directories

**Fix:**
```bash
# Download reports artifact
# Review location suggestions

# Move files
git mv wrong-location.md docs/correct-location/

# Commit and push
git add -A
git commit -m "docs: Move files to correct locations"
git push
```

### When Link Validation Fails

**Symptom:** Yellow warning (non-blocking)

**Cause:** Broken internal links

**Fix:**
```bash
# Download links_report.json
# Find broken links with line numbers

# Fix links in files
vi docs/file-with-broken-link.md

# Commit and push
git add docs/file-with-broken-link.md
git commit -m "docs: Fix broken links"
git push
```

## Configuration

### Adjusting Triggers

Edit `.github/workflows/validate-docs.yml`:

```yaml
# Run on all pushes (not just markdown changes)
on:
  push:
    branches: ['**']
  pull_request:
    branches: ['main', 'develop/**']
```

### Changing Python Version

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.12'  # Change here
```

### Adding New Validation

```yaml
- name: Custom validation
  run: |
    python tools/my_custom_validator.py --all
```

### Making Link Validation Blocking

Currently, broken links are informational only. To make them block merges:

```yaml
- name: Check for failures
  if: env.METADATA_FAILED == '1' || env.LOCATION_FAILED == '1' || env.LINKS_FAILED == '1'
  run: |
    echo "::error::Documentation validation failed."
    exit 1
```

## Branch Protection Rules

To enforce validation on pull requests:

1. Go to repository settings
2. Click "Branches"
3. Add rule for `main`
4. Enable "Require status checks to pass"
5. Select "validate-documentation"
6. Save changes

Now PRs can't merge until validation passes.

## Troubleshooting

### Workflow Not Running

**Problem:** Push doesn't trigger workflow

**Causes:**
- Changed files don't match `paths` filter
- Workflow file has syntax errors
- GitHub Actions disabled on repo

**Solution:**
```bash
# Check which files changed
git diff --name-only HEAD~1

# Validate workflow syntax
yamllint .github/workflows/validate-docs.yml

# Check GitHub Actions settings
# Settings → Actions → General → Allow all actions
```

### Python Dependencies Not Installing

**Problem:** Pip install fails

**Causes:**
- `requirements.txt` missing
- Syntax errors in requirements.txt
- PyPI package unavailable

**Solution:**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install PyYAML click  # Explicit install
```

### Metrics Extraction Failing

**Problem:** `jq` commands fail

**Cause:** JSON output format changed

**Solution:**
```bash
# Test locally first
python tools/collect_metrics.py --json | jq '.total_docs'

# Update workflow if field names changed
```

### Slow Workflow

**Problem:** Workflow takes too long

**Solutions:**
- Cache Python dependencies:
  ```yaml
  - uses: actions/cache@v3
    with:
      path: ~/.cache/pip
      key: ${{ runner.os }}-pip-${{ hashFiles('tools/requirements.txt') }}
  ```
- Limit validation to changed files only (advanced)
- Use faster runners (GitHub Enterprise)

## Best Practices

### For Developers

1. **Run pre-commit hook locally** before pushing
2. **Fix issues immediately** if CI fails
3. **Review job summaries** to understand failures
4. **Download artifacts** for detailed analysis
5. **Don't bypass validation** without good reason

### For Maintainers

1. **Monitor metrics trends** over time
2. **Set metadata coverage goals** (e.g., 90%)
3. **Reduce root violations** progressively
4. **Update validation scripts** as standards evolve
5. **Keep workflow dependencies updated**

### For Documentation

1. **Add metadata immediately** when creating docs
2. **Place files correctly** from the start
3. **Test links** before committing
4. **Use validation tools locally** before pushing

## Maintenance

### Updating Workflow

```bash
# Edit workflow
vi .github/workflows/validate-docs.yml

# Test locally (if possible)
act push  # Using nektos/act

# Commit and push
git add .github/workflows/validate-docs.yml
git commit -m "ci: Update documentation validation workflow"
git push
```

### Updating Dependencies

```bash
# Edit requirements
vi tools/requirements.txt

# Test locally
pip install -r tools/requirements.txt
python tools/collect_metrics.py --json

# Commit
git add tools/requirements.txt
git commit -m "build: Update Python dependencies"
git push
```

### Monitoring

Track these metrics over time:
- Metadata coverage percentage (goal: >90%)
- Root directory violations (goal: <10)
- Broken links count (goal: 0)
- Workflow success rate (goal: >95%)

## Related Documentation

- Pre-commit hook: `docs/librarian-pre-commit-hook.md`
- Validation tools: `tools/README.md`
- File organization: `FILE_ORGANIZATION_STANDARDS.md`
- Librarian system: `tasks/librarian-enhancements/prd.md`

## Support

**Workflow issues:** GitHub Actions UI → View logs
**Validation issues:** Download artifacts → Review reports
**Questions:** Team documentation chat
**Bugs:** Project issue tracker

---

**Quick Reference:**

```bash
# View workflow runs
open https://github.com/<org>/<repo>/actions

# Download reports
# Actions → Workflow run → Artifacts → documentation-reports.zip

# Test validation locally
python tools/validate_metadata.py --all
python tools/validate_location.py --scan-root
python tools/validate_links.py --all --json
python tools/collect_metrics.py --json

# Fix issues
python tools/validate_metadata.py --fix <file>
```
