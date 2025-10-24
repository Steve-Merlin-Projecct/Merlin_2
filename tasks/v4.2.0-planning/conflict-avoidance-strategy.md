---
title: "Conflict Avoidance Strategy"
type: technical_doc
component: general
status: draft
tags: []
---

# v4.2.0 Conflict Avoidance & Merge Strategy

**Version:** 4.2.0
**Created:** October 8, 2025

## Overview

With 7 parallel feature branches and 13 tasks, conflicts are inevitable. This document provides the strategy to minimize and resolve them.

## Three-Layer Defense Strategy

### Layer 1: Prevention (Design Phase)
### Layer 2: Detection (Development Phase)
### Layer 3: Resolution (Merge Phase)

---

## Layer 1: Prevention (Before Code)

### 1.1 API Contract System

**Create contracts BEFORE development starts:**

**Location:** `/docs/api-contracts/v4.2.0/`

#### Template Variable Schema
```yaml
# template-variables.yaml
cover_letter_variables:
  - {name: "candidate_name", type: "string", required: true}
  - {name: "company_name", type: "string", required: true}
  - {name: "role_title", type: "string", required: true}
  - {name: "marketing_expertise", type: "array<string>", source: "content_ai"}
  - {name: "calendly_link", type: "url", source: "calendly_integration"}

resume_variables:
  - {name: "candidate_name", type: "string", required: true}
  - {name: "skills", type: "array<string>", source: "content_ai"}
  - {name: "experience", type: "array<object>", source: "content_ai"}
```

**Owners:**
- Feature 2 (Content AI): Produces `marketing_expertise`, `skills`, `experience`
- Feature 3 (Templates): Consumes all variables
- Feature 4 (Calendly): Produces `calendly_link`

#### Application Package Structure
```json
{
  "application_package_v2": {
    "cover_letter": {"source": "feature/template-verification"},
    "resume": {"source": "feature/template-verification"},
    "calendly_link": {"source": "feature/calendly-integration"},
    "tracking_pixel": {"source": "feature/dashboard-analytics"},
    "delivery": {"source": "feature/email-system-v2"}
  }
}
```

#### Analytics Event Schema
```json
{
  "recruiter_click_event": {
    "event_id": "uuid",
    "job_id": "foreign_key",
    "click_type": "enum[resume, cover_letter, calendly, linkedin]",
    "timestamp": "datetime",
    "ip_address": "string",
    "user_agent": "string"
  }
}
```

#### UI Component Registry
```markdown
# Dashboard Components

## Owned by feature/dashboard-analytics:
- `/dashboard/components/ClickMap.tsx`
- `/dashboard/components/JobPipeline.tsx`
- `/dashboard/components/MetricsCard.tsx`

## Shared (coordinate changes):
- `/frontend_templates/base.html` (layout only)
- `/static/css/tailwind.config.js` (additive only)
```

### 1.2 File Ownership Assignment

| Feature | Owns (Full Control) | Shared (Coordinate) | Read-Only (No Touch) |
|---------|---------------------|---------------------|----------------------|
| **Claude Tools** | `.claude/`, `CLAUDE.md`, docs/agent-* | - | All code |
| **Content AI** | `modules/content/`, AI prompts | template-variables.yaml | Templates |
| **Templates** | `templates/`, verification modules | template-variables.yaml | Content modules |
| **Calendly** | `modules/scheduling/calendly_*` | application-package.json | Email modules |
| **Email** | `modules/email_integration/` | application-package.json | Calendly modules |
| **Dashboard** | `frontend_templates/`, `dashboard/` | analytics-events.yaml | Backend modules |
| **Testing** | `tests/` | - | All modules (read) |

### 1.3 CLAUDE.md Coordination

**Problem:** Feature 1 modifies CLAUDE.md, Feature 1 (Librarian) also wants to update it

**Solution - Section Ownership:**
```markdown
# CLAUDE.md Structure

## Section 1: Overview (Feature 1: Claude Tools)
## Section 2: Communication Guide (Feature 1: Claude Tools)
## Section 3: Agent Usage (Feature 1: Claude Tools)
## Section 4: File Organization (Feature 1: Librarian - separate doc)
## Section 5: External Dependencies (Feature 1: Claude Tools)
```

**Librarian creates:** `/docs/file-organization-action-plan.md` (separate file)

---

## Layer 2: Detection (During Development)

### 2.1 Pre-Commit Conflict Detection

**Create:** `.git/hooks/pre-commit-conflict-check.sh`

```bash
#!/bin/bash
# Check if modified files are "owned" by current branch

BRANCH=$(git branch --show-current)
MODIFIED=$(git diff --cached --name-only)

case $BRANCH in
  feature/claude-dev-tools)
    ALLOWED="^\.claude/|^CLAUDE\.md|^docs/agent-"
    ;;
  feature/content-ai-system)
    ALLOWED="^modules/content/|^modules/ai_job_description_analysis/"
    ;;
  feature/template-verification)
    ALLOWED="^templates/|^modules/document_generation/.*verif"
    ;;
  # ... other branches
esac

for file in $MODIFIED; do
  if ! echo "$file" | grep -qE "$ALLOWED|^docs/api-contracts/"; then
    echo "⚠️  WARNING: $file not in your feature's ownership area"
    echo "   Coordinate with team before modifying shared files"
    exit 1
  fi
done
```

### 2.2 Daily Sync Document

**Location:** `/tasks/v4.2.0-planning/daily-status.md`

```markdown
# Daily Development Status

## 2025-10-08

### Feature 1: Claude Tools (@dev1)
- Status: In progress
- Files modified: .claude/commands/analyze.md, CLAUDE.md
- Blockers: None
- Affects: All (new slash command available)

### Feature 2: Content AI (@dev2)
- Status: Blocked - waiting for template variable schema
- Files modified: None yet
- Blockers: Need template-variables.yaml from API contract
- Affects: Feature 3

### Feature 3: Templates (@dev3)
- Status: In progress
- Files modified: templates/cover_letter_v2.docx
- Blockers: None
- Affects: Feature 2 (need to publish variable schema today)
```

### 2.3 Automated Conflict Alerts

**GitHub Action:** `.github/workflows/conflict-detector.yml`

```yaml
name: Detect Potential Conflicts

on:
  pull_request:
    branches: [main]

jobs:
  conflict-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check modified files against ownership matrix
        run: |
          # Compare PR files with other open PRs
          # Alert if same files modified in multiple PRs
          # Require coordination comment before merge
```

---

## Layer 3: Resolution (At Merge Time)

### 3.1 Merge Sequence (CRITICAL!)

**NEVER merge out of order!**

```bash
# Phase 1: Foundation FIRST
git merge feature/claude-dev-tools  # Must be first

# Phase 2: Content & Templates (parallel OK after API contract)
git merge feature/content-ai-system
git merge feature/template-verification

# Phase 3: Delivery (coordinate timing)
git merge feature/calendly-integration
git merge feature/email-system-v2

# Phase 4: Monitoring LAST
git merge feature/dashboard-analytics

# Ongoing: Testing (anytime, no conflicts)
git merge feature/testing-system
```

### 3.2 Pre-Merge Integration Test

**Before merging to main, create integration branch:**

```bash
# Test merge locally first
git checkout -b test/merge-preview main
git merge feature/X --no-ff

# Run full test suite
pytest tests/
python -m flake8
npm run test  # for dashboard

# If tests pass, merge to main
# If tests fail, fix in feature branch, retest

# Delete test branch
git branch -D test/merge-preview
```

### 3.3 Conflict Resolution Protocol

**If merge conflict occurs:**

1. **Identify Conflict Type:**
   - Code logic conflict → Feature owner resolves
   - Design decision conflict → Team decides, document in API contract
   - File ownership conflict → Should not happen (prevention failed)

2. **Resolution Owner:**
   - Feature being merged IN resolves conflicts
   - Not the person doing the merge

3. **Resolution Process:**
   ```bash
   # Feature owner fixes conflicts in their branch
   git checkout feature/X
   git merge main  # Pull in latest
   # Resolve conflicts
   git commit
   git push

   # Then merger retries
   git checkout main
   git merge feature/X  # Should be clean now
   ```

4. **Document Decision:**
   - Add to `/docs/api-contracts/v4.2.0/decisions.md`
   - Explain why conflict occurred
   - Document resolution for future reference

### 3.4 Rollback Strategy

**If merge breaks main:**

```bash
# Immediate rollback
git revert -m 1 <merge-commit-hash>
git push origin main

# Fix in feature branch
git checkout feature/X
# Fix issue
git commit
git push

# Retry merge later
```

**If multiple features broken:**

```bash
# Reset to last known good state
git reset --hard <tag-before-4.2.0>
git push origin main --force  # DANGEROUS: Only if coordinated

# Re-merge features one by one, testing each
```

---

## Specific Conflict Scenarios & Solutions

### Scenario 1: CLAUDE.md Collision
**Features:** 1 (Claude Tools) + 1 (Librarian)

**Solution:**
- Claude Tools owns CLAUDE.md modifications
- Librarian creates `/docs/file-organization-action-plan.md`
- If CLAUDE.md needs file org section, Claude Tools adds it referencing Librarian's doc

### Scenario 2: Template Variable Mismatch
**Features:** 2 (Content AI) + 3 (Templates)

**Solution:**
1. Feature 3 publishes variable schema in `/docs/api-contracts/v4.2.0/template-variables.yaml`
2. Feature 2 implements to that schema
3. Any schema changes require updating contract + both features

### Scenario 3: Application Package Structure
**Features:** 4 (Calendly) + 5 (Email)

**Solution:**
1. Define package structure in `/docs/api-contracts/v4.2.0/application-package.json`
2. Calendly adds `calendly_link` field
3. Email consumes package structure
4. Both coordinate on package assembly order

### Scenario 4: Frontend Template Conflicts
**Features:** 6 (Dashboard) redesigns, others may add components

**Solution:**
1. Dashboard creates new template files (`dashboard_v2.html`)
2. Old templates remain until Dashboard merged
3. After Dashboard merge, other features use new templates
4. Component isolation: separate files per feature's UI

### Scenario 5: Database Schema Changes
**Multiple features** may add tables

**Solution:**
1. Each feature creates its own migration file
2. Migrations numbered sequentially: `001_calendly.sql`, `002_analytics.sql`
3. No feature modifies another's migrations
4. Shared table changes go through API contract decision

---

## Communication Channels

### Sync Meetings (Optional)
- **Daily standup** (async): Post in `/tasks/v4.2.0-planning/daily-status.md`
- **Weekly sync** (if conflicts arise): Discuss coordination

### Conflict Escalation
1. **Level 1:** Post in daily-status.md, coordinate directly
2. **Level 2:** Document in API contract, seek consensus
3. **Level 3:** Create integration test branch, resolve together

### Documentation
- **API Contracts:** `/docs/api-contracts/v4.2.0/`
- **Daily Status:** `/tasks/v4.2.0-planning/daily-status.md`
- **Decisions Log:** `/docs/api-contracts/v4.2.0/decisions.md`
- **Conflict Resolutions:** `/docs/api-contracts/v4.2.0/conflicts-resolved.md`

---

## Success Checklist

**Before Starting Development:**
- [ ] API contracts defined
- [ ] File ownership assigned
- [ ] Pre-commit hooks installed
- [ ] Daily status doc created
- [ ] All devs understand merge sequence

**During Development:**
- [ ] Daily status updates posted
- [ ] Shared files coordinated before modifying
- [ ] API contracts updated when designs change
- [ ] Tests passing in isolation

**Before Merging:**
- [ ] Integration test passed
- [ ] Code review approved
- [ ] No conflicts with open PRs
- [ ] Documentation complete
- [ ] Merge sequence followed

**After Merging:**
- [ ] Main branch tests pass
- [ ] Other features notified of changes
- [ ] API contracts updated if needed

---

## Tools & Automation

### Scripts to Create

1. **`scripts/check-ownership.sh`** - Verify file ownership before commit
2. **`scripts/integration-test.sh`** - Test merge preview locally
3. **`scripts/conflict-report.sh`** - Show potential conflicts with other PRs
4. **`scripts/merge-sequence.sh`** - Enforce merge order

### GitHub Actions

1. **Ownership Checker** - Alert on shared file modifications
2. **Integration Tester** - Test merge with main before PR approval
3. **Merge Order Enforcer** - Block merges that skip sequence

---

## Summary

**Three Rules to Avoid Conflicts:**

1. **Define Before Develop** - API contracts first, code second
2. **Own Your Files** - Stick to ownership matrix, coordinate shared files
3. **Merge in Sequence** - Follow phase order strictly

**If conflicts occur:**
- Feature owner resolves in their branch
- Document decision in API contract
- Retest before merging to main

With this strategy, 7 parallel features can develop smoothly and merge cleanly.
