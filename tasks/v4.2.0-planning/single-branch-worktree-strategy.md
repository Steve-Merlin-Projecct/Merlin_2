---
title: "Single Branch Worktree Strategy"
type: technical_doc
component: general
status: draft
tags: []
---

# v4.2.0 Single Branch Worktree Strategy

**Development Branch:** `develop/v4.2.0`
**All worktrees work on the SAME branch**
**Merge conflicts handled AFTER completion**

## Strategy

All 13 tasks work simultaneously on `develop/v4.2.0` branch. Each worktree is a different working directory pointing to the same branch. When done, merge conflicts will be resolved during integration to main.

## Create Development Branch & Worktrees

### Step 1: Create Development Branch
```bash
git checkout -b develop/v4.2.0 origin/main
git push origin develop/v4.2.0
```

### Step 2: Create All 13 Worktrees (Same Branch)
```bash
# All worktrees point to develop/v4.2.0 branch
git worktree add .trees/claude-refinement develop/v4.2.0
git worktree add .trees/marketing-content develop/v4.2.0
git worktree add .trees/script-testing develop/v4.2.0
git worktree add .trees/template-creation develop/v4.2.0
git worktree add .trees/docx-verification develop/v4.2.0
git worktree add .trees/calendly develop/v4.2.0
git worktree add .trees/dashboard-redesign develop/v4.2.0
git worktree add .trees/database-viz develop/v4.2.0
git worktree add .trees/gemini-prompts develop/v4.2.0
git worktree add .trees/librarian develop/v4.2.0
git worktree add .trees/email-refinement develop/v4.2.0
git worktree add .trees/github-streamline develop/v4.2.0
git worktree add .trees/analytics develop/v4.2.0
```

## Worktree Task Assignments

### Task 1: Claude.md Refinement & Agent Creation
**Worktree:** `.trees/claude-refinement`
**Scope:**
- Refine CLAUDE.md instructions
- Create specialized agents
- Develop slash commands

**Primary Files:**
- `CLAUDE.md`
- `.claude/commands/*.md` (new)
- `docs/agent-creation-guide.md` (new)

**⚠️ Conflict Warnings:**
- 🔴 **HIGH:** Task 10 also modifies CLAUDE.md
- **Resolution Note:** Expect merge conflict in CLAUDE.md - resolve by combining both improvements

---

### Task 2: Marketing Content Generation
**Worktree:** `.trees/marketing-content`
**Scope:**
- Generate creative sentences for marketing automation roles
- Refine existing content library
- Content quality metrics

**Primary Files:**
- `modules/content/marketing_automation_content.py` (new)
- `modules/content/content_library.py` (modified)
- `docs/content-generation-guide.md` (new)

**⚠️ Conflict Warnings:**
- 🟡 **MEDIUM:** Task 9 modifies Gemini prompts used for content generation
- 🟡 **MEDIUM:** Task 4 may expect certain template variables from content
- **Resolution Note:** Check prompt compatibility and template variable schema alignment

---

### Task 3: Script Testing
**Worktree:** `.trees/script-testing`
**Scope:**
- Create script testing framework
- Build test suite
- Integration & E2E testing

**Primary Files:**
- `tests/scripts/` (new)
- `tests/integration/` (modified)
- `tests/e2e/` (new)
- `scripts/test_runner.sh` (new)

**⚠️ Conflict Warnings:**
- 🟢 **LOW:** Tests may need updates if other tasks change code, but no file conflicts expected
- **Resolution Note:** Update tests after other tasks merge if needed

---

### Task 4: Template Creation
**Worktree:** `.trees/template-creation`
**Scope:**
- Source new cover letter examples (10+)
- Source new resume examples (10+)
- Convert to .docx templates

**Primary Files:**
- `templates/cover_letters/*.docx` (new)
- `templates/resumes/*.docx` (new)
- `docs/template-variables.md` (new)

**⚠️ Conflict Warnings:**
- 🟡 **MEDIUM:** Task 5 may modify templates for verification
- 🟡 **MEDIUM:** Task 2 content must match template variable expectations
- **Resolution Note:** Ensure template variables documented before Task 2/5 completion

---

### Task 5: Word.docx Verification
**Worktree:** `.trees/docx-verification`
**Scope:**
- Create authenticity metrics
- Verify docx files built correctly
- Automated quality checks

**Primary Files:**
- `modules/document_generation/authenticity_metrics.py` (new)
- `modules/document_generation/docx_verifier.py` (new)
- `tests/verification/` (new)

**⚠️ Conflict Warnings:**
- 🟡 **MEDIUM:** Task 4 creates templates this task verifies
- 🟡 **MEDIUM:** Task 11 email delivery may use verification
- **Resolution Note:** Coordinate with Task 4 on template format

---

### Task 6: Calendly Connection
**Worktree:** `.trees/calendly`
**Scope:**
- Create time suggestion rules
- Integrate Calendly API
- Insert links into application packages

**Primary Files:**
- `modules/scheduling/calendly_integration.py` (new)
- `modules/scheduling/time_suggestion_engine.py` (new)
- `modules/workflow/` (modified - package assembly)
- `.env.example` (modified - add Calendly keys)

**⚠️ Conflict Warnings:**
- 🔴 **HIGH:** Task 11 also modifies `modules/workflow/` for email delivery
- 🟡 **MEDIUM:** Application package structure affects multiple tasks
- **Resolution Note:** Expect conflict in workflow files - merge both Calendly link insertion and email delivery logic

---

### Task 7: Dashboard Redesign
**Worktree:** `.trees/dashboard-redesign`
**Scope:**
- Complete dashboard redesign
- Node.js + Tailwind CSS
- Real-time monitoring

**Primary Files:**
- `dashboard/` (new - Node.js app)
- `frontend_templates/dashboard_v2.html` (new)
- `static/css/tailwind.config.js` (new)
- `package.json` (new)

**⚠️ Conflict Warnings:**
- 🔴 **HIGH:** Task 8 also creates frontend visualization
- 🔴 **HIGH:** Task 13 creates analytics components for dashboard
- 🟡 **MEDIUM:** May conflict on `frontend_templates/` directory
- **Resolution Note:** Expect conflicts in frontend_templates/ - merge all dashboard components together

---

### Task 8: Database Visualization
**Worktree:** `.trees/database-viz`
**Scope:**
- Animated database diagrams
- Schema visualization
- Interactive database explorer

**Primary Files:**
- `frontend_templates/db_visualizer.html` (new)
- `modules/database/visualization.py` (new)
- `static/js/db_animation.js` (new)

**⚠️ Conflict Warnings:**
- 🔴 **HIGH:** Task 7 also modifies `frontend_templates/`
- 🟡 **MEDIUM:** Task 13 may show analytics in DB viz
- **Resolution Note:** Expect frontend template conflicts - integrate DB viz into dashboard

---

### Task 9: Gemini Prompt Improvements
**Worktree:** `.trees/gemini-prompts`
**Scope:**
- Improve Gemini prompts
- Prompt injection protection
- Security testing

**Primary Files:**
- `modules/ai_job_description_analysis/prompts.py` (modified)
- `modules/ai_job_description_analysis/security.py` (new)
- `tests/security/prompt_injection_tests.py` (new)

**⚠️ Conflict Warnings:**
- 🟡 **MEDIUM:** Task 2 uses these prompts for content generation
- **Resolution Note:** Ensure improved prompts work with content generation system

---

### Task 10: Librarian (File Organization Planning)
**Worktree:** `.trees/librarian`
**Scope:**
- Create file organization guides
- Plan organization actions
- Document standards
- **READ-ONLY ANALYSIS - No file moves**

**Primary Files:**
- `docs/file-organization-action-plan.md` (new)
- `docs/file-placement-guide.md` (new)
- `tasks/librarian/file-analysis.md` (new)

**⚠️ Conflict Warnings:**
- 🔴 **HIGH:** Task 1 also modifies CLAUDE.md
- **Resolution Note:** If both modify CLAUDE.md, merge file organization section with agent improvements

---

### Task 11: Email Refinement
**Worktree:** `.trees/email-refinement`
**Scope:**
- Phase 1: Send to personal email
- Phase 2: Send to job description email
- Phase 3: Source email from internet
- Phase 4: Deprecate for BOS

**Primary Files:**
- `modules/email_integration/delivery_v2.py` (modified)
- `modules/email_integration/email_sourcing.py` (new)
- `modules/email_integration/bos_transition.py` (new)
- `modules/workflow/email_application_api.py` (modified)

**⚠️ Conflict Warnings:**
- 🔴 **HIGH:** Task 6 also modifies `modules/workflow/` for Calendly
- 🟡 **MEDIUM:** Task 5 verification may be used in email quality checks
- **Resolution Note:** Expect workflow file conflicts - merge Calendly links and email delivery together

---

### Task 12: Streamline GitHub Connection
**Worktree:** `.trees/github-streamline`
**Scope:**
- Optimize gh CLI workflow
- Improve git operations
- Better authentication
- Workflow automation

**Primary Files:**
- `.github/workflows/` (modified)
- `scripts/github_helper.sh` (new)
- `docs/github-workflow.md` (modified)

**⚠️ Conflict Warnings:**
- 🟡 **MEDIUM:** Task 1 may add GitHub-related slash commands
- 🟢 **LOW:** Mostly independent infrastructure
- **Resolution Note:** Minor conflicts possible in .github/ - merge workflow improvements

---

### Task 13: Analytics System
**Worktree:** `.trees/analytics`
**Scope:**
- Recruiter click tracking
- Data visualization
- Insights generation
- Action recommendations

**Primary Files:**
- `modules/analytics/click_tracking.py` (new)
- `modules/analytics/recruiter_insights.py` (new)
- `modules/database/analytics_tables.py` (new)
- Frontend components for dashboard integration

**⚠️ Conflict Warnings:**
- 🔴 **HIGH:** Task 7 creates dashboard where analytics will be shown
- 🟡 **MEDIUM:** Task 8 DB viz may show analytics data
- **Resolution Note:** Expect dashboard integration conflicts - merge analytics components into dashboard

---

## Low Priority Tasks (Backlog - v4.3.0+)

**Not included in v4.2.0:**

### Task 20: Cloud Deployment Preparation
- Database migration to cloud
- Infrastructure as Code
- Deployment automation
- **Defer to:** v4.3.0

### Task 21: Job Application Bots
- Automated application system
- Anti-detection mechanisms
- Credential management
- **Defer to:** v4.3.0 or v5.0.0

### Task 22: Multi-Platform Scraping
- New Apify APIs
- Additional job platforms
- **Defer to:** v4.3.0

### Task 23: Industry Website Scrapers
- Message board scraping
- Industry-specific sources
- **Defer to:** v4.3.0

### Task 24: Algorithm Improvements
- Ongoing optimization
- **Continuous:** Add to backlog

**Rationale:** Focus v4.2.0 on content generation, delivery, and monitoring improvements. Infrastructure expansion comes later.

---

## Workflow Process

### 1. Work Independently in Worktrees
Each worktree is isolated. Make changes without worrying about others.

```bash
cd .trees/claude-refinement
# Make changes
git add .
git commit -m "feat: add specialized agents"
git pull --rebase  # Get others' changes
git push
```

### 2. Pull Frequently to Stay Updated
```bash
# In any worktree
git pull --rebase origin develop/v4.2.0
```

### 3. When Conflicts Occur
Git will notify you during pull/push. Resolve in your worktree:

```bash
# After pull shows conflicts
git status  # See conflicted files
# Edit files, resolve conflicts
git add <resolved-files>
git rebase --continue
git push
```

### 4. Final Integration (After All Tasks Complete)

When all 13 tasks are done on `develop/v4.2.0`:

```bash
# Merge develop to main
git checkout main
git merge develop/v4.2.0 --no-ff

# If conflicts, resolve them
# This is expected for:
# - CLAUDE.md (Tasks 1 & 10)
# - modules/workflow/ (Tasks 6 & 11)
# - frontend_templates/ (Tasks 7 & 8)
# - Dashboard components (Tasks 7, 8, 13)

git add <resolved-files>
git commit
git push origin main

# Tag release
git tag v4.2.0
git push origin v4.2.0
```

---

## Conflict Resolution Strategy

### Expected Major Conflicts

1. **CLAUDE.md** (Tasks 1 & 10)
   - Both modify same file
   - **Resolution:** Combine agent instructions + file organization sections

2. **modules/workflow/** (Tasks 6 & 11)
   - Both modify application package workflow
   - **Resolution:** Merge Calendly link insertion + email delivery logic

3. **frontend_templates/** (Tasks 7 & 8 & 13)
   - All create dashboard/visualization components
   - **Resolution:** Integrate all components into unified dashboard

4. **Gemini prompts** (Tasks 2 & 9)
   - Both modify prompt system
   - **Resolution:** Use improved prompts for content generation

### Conflict Handling Rules

**During Development:**
- Pull frequently: `git pull --rebase`
- Resolve conflicts as they come
- Communicate in `/tasks/v4.2.0-planning/daily-sync.md`

**At Final Merge:**
- Expect conflicts (it's OK!)
- Resolve by combining functionality
- Test after resolution
- Document decisions

---

## Daily Sync Document

**Location:** `/tasks/v4.2.0-planning/daily-sync.md`

**Format:**
```markdown
## 2025-10-08

### Task 1: Claude Refinement
- Progress: Added 3 specialized agents
- Files: CLAUDE.md, .claude/commands/
- Pushed: Yes
- Issues: None

### Task 6: Calendly
- Progress: API integration complete
- Files: modules/workflow/email_application_api.py
- Pushed: Yes
- Issues: Modified workflow file - may conflict with Task 11

### Task 11: Email
- Progress: Phase 1 complete
- Files: modules/workflow/email_application_api.py
- Pushed: Not yet
- Issues: Need to pull Task 6 changes first
```

---

## Worktree Status Checker

Create `scripts/worktree-status.sh`:

```bash
#!/bin/bash
echo "=== Worktree Status on develop/v4.2.0 ==="
echo ""

for tree in .trees/*/; do
    name=$(basename $tree)
    cd $tree
    status=$(git status --short | wc -l)
    ahead=$(git rev-list --count origin/develop/v4.2.0..HEAD 2>/dev/null || echo 0)
    behind=$(git rev-list --count HEAD..origin/develop/v4.2.0 2>/dev/null || echo 0)

    echo "📁 $name:"
    echo "   Uncommitted: $status files"
    echo "   Ahead: $ahead commits | Behind: $behind commits"
    cd - > /dev/null
    echo ""
done
```

---

## Setup Commands Summary

```bash
# 1. Create development branch
git checkout -b develop/v4.2.0 origin/main
git push origin develop/v4.2.0

# 2. Create all worktrees on same branch
git worktree add .trees/claude-refinement develop/v4.2.0
git worktree add .trees/marketing-content develop/v4.2.0
git worktree add .trees/script-testing develop/v4.2.0
git worktree add .trees/template-creation develop/v4.2.0
git worktree add .trees/docx-verification develop/v4.2.0
git worktree add .trees/calendly develop/v4.2.0
git worktree add .trees/dashboard-redesign develop/v4.2.0
git worktree add .trees/database-viz develop/v4.2.0
git worktree add .trees/gemini-prompts develop/v4.2.0
git worktree add .trees/librarian develop/v4.2.0
git worktree add .trees/email-refinement develop/v4.2.0
git worktree add .trees/github-streamline develop/v4.2.0
git worktree add .trees/analytics develop/v4.2.0

# 3. Start working in any worktree
cd .trees/claude-refinement
# Make changes, commit, push
```

---

## Success Criteria

**v4.2.0 Complete When:**
- ✅ All 13 tasks completed on `develop/v4.2.0`
- ✅ Conflicts resolved during integration
- ✅ All tests pass
- ✅ `develop/v4.2.0` merged to `main`
- ✅ Tagged as `v4.2.0`

**Timeline:** 4-6 weeks with parallel development

---

**Ready to create worktrees? This is the correct strategy per your request!**
