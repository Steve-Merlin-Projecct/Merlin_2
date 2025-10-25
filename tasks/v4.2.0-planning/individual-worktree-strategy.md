---
title: "Individual Worktree Strategy"
type: technical_doc
component: general
status: draft
tags: []
---

# v4.2.0 Individual Worktree Strategy

**One Worktree Per Task - 13 Parallel Features**

## All 13 Feature Branches

### Task 1: Claude.md Refinement & Agent Creation
**Branch:** `feature/claude-refinement`
**Worktree:** `.trees/claude-refinement`
**Scope:**
- Refine CLAUDE.md instructions
- Create specialized agents
- Develop slash commands

**Files:**
- `CLAUDE.md`
- `.claude/commands/*.md`
- `docs/agent-creation-guide.md`

---

### Task 2: Marketing Content Generation
**Branch:** `feature/marketing-content`
**Worktree:** `.trees/marketing-content`
**Scope:**
- Generate creative sentences for marketing automation roles
- Refine existing content
- Create content quality metrics
- May use specialized agents (after Task 1)

**Files:**
- `modules/content/marketing_automation.py`
- `modules/content/content_library.py`
- `docs/content-generation-guide.md`

---

### Task 3: Script Testing
**Branch:** `feature/script-testing`
**Worktree:** `.trees/script-testing`
**Scope:**
- Create script testing framework
- Build test suite for all scripts
- Integration testing
- E2E automation

**Files:**
- `tests/scripts/`
- `tests/integration/`
- `scripts/test_runner.sh`

---

### Task 4: Template Creation
**Branch:** `feature/template-creation`
**Worktree:** `.trees/template-creation`
**Scope:**
- Source new cover letter examples (10+)
- Source new resume examples (10+)
- Convert to .docx templates
- Define template variables

**Files:**
- `templates/cover_letters/*.docx`
- `templates/resumes/*.docx`
- `docs/template-variables.md`

---

### Task 5: Word.docx Verification
**Branch:** `feature/docx-verification`
**Worktree:** `.trees/docx-verification`
**Scope:**
- Create authenticity metrics
- Verify docx files built correctly
- Automated quality checks
- Perception scoring

**Files:**
- `modules/document_generation/authenticity_metrics.py`
- `modules/document_generation/docx_verifier.py`
- `tests/verification/`

---

### Task 6: Calendly Connection
**Branch:** `feature/calendly`
**Worktree:** `.trees/calendly`
**Scope:**
- Create time suggestion rules
- Integrate Calendly API
- Insert links into application packages
- Timezone handling

**Files:**
- `modules/scheduling/calendly_integration.py`
- `modules/scheduling/time_rules.py`
- `.env.example` (Calendly keys)

---

### Task 7: Dashboard Redesign
**Branch:** `feature/dashboard-redesign`
**Worktree:** `.trees/dashboard-redesign`
**Scope:**
- Complete dashboard redesign
- Node.js + Tailwind CSS
- Real-time monitoring
- UI/UX improvements

**Files:**
- `dashboard/` (new Node.js app)
- `frontend_templates/dashboard_v2.html`
- `static/css/tailwind.config.js`
- `package.json`

---

### Task 8: Database Visualization
**Branch:** `feature/database-viz`
**Worktree:** `.trees/database-viz`
**Scope:**
- Animated database diagrams
- Schema visualization
- Interactive database explorer
- Live connection status

**Files:**
- `frontend_templates/db_visualizer.html`
- `modules/database/visualization.py`
- `static/js/db_animation.js`

---

### Task 9: Gemini Prompt Improvements
**Branch:** `feature/gemini-prompts`
**Worktree:** `.trees/gemini-prompts`
**Scope:**
- Improve Gemini prompts
- Prompt injection protection
- Security testing
- Quality improvements

**Files:**
- `modules/ai_job_description_analysis/prompts.py`
- `modules/ai_job_description_analysis/security.py`
- `tests/security/prompt_injection_tests.py`

---

### Task 10: Librarian (File Organization)
**Branch:** `feature/librarian`
**Worktree:** `.trees/librarian`
**Scope:**
- Create file organization guides
- Plan organization actions
- Document standards
- **Read-only analysis, no changes**

**Files:**
- `docs/file-organization-action-plan.md`
- `docs/file-placement-guide.md`
- `tasks/librarian/analysis.md`

---

### Task 11: Email Refinement
**Branch:** `feature/email-refinement`
**Worktree:** `.trees/email-refinement`
**Scope:**
- Phase 1: Send to personal email
- Phase 2: Send to job description email
- Phase 3: Source email from internet
- Phase 4: Deprecate for BOS

**Files:**
- `modules/email_integration/delivery_v2.py`
- `modules/email_integration/email_sourcing.py`
- `modules/email_integration/bos_transition.py`

---

### Task 12: Streamline GitHub Connection
**Branch:** `feature/github-streamline`
**Worktree:** `.trees/github-streamline`
**Scope:**
- Optimize gh CLI workflow
- Improve git operations
- Better authentication
- Workflow automation

**Files:**
- `.github/workflows/`
- `scripts/github_helper.sh`
- `docs/github-workflow.md`

---

### Task 13: Analytics System
**Branch:** `feature/analytics`
**Worktree:** `.trees/analytics`
**Scope:**
- Recruiter click tracking
- Data visualization
- Insights generation
- Action recommendations

**Files:**
- `modules/analytics/click_tracking.py`
- `modules/analytics/insights.py`
- `modules/database/analytics_tables.py`

---

## Conflict Matrix (13x13)

### 🔴 HIGH CONFLICT (Must Coordinate)

| Task A | Task B | Conflict | Solution |
|--------|--------|----------|----------|
| 1 | 10 | Both modify CLAUDE.md | Task 1 owns CLAUDE.md, Task 10 creates separate doc |
| 2 | 9 | Content uses Gemini prompts | Define prompt API first |
| 4 | 5 | Verification needs templates | Task 4 finishes first OR share test templates |
| 6 | 11 | Calendly link in email | Define application package structure |
| 7 | 8 | Both modify frontend templates | Strict file separation or coordinate |
| 7 | 13 | Analytics shown on dashboard | Define data API first |
| 8 | 13 | DB viz may show analytics | Coordinate UI components |

### 🟡 MODERATE CONFLICT (Coordinate)

| Task A | Task B | Conflict | Solution |
|--------|--------|----------|----------|
| 2 | 4 | Content goes into templates | Define template variables schema |
| 5 | 11 | Both validate output quality | Share QA standards |
| 1 | 12 | Both improve dev workflow | Coordinate tool improvements |

### 🟢 LOW/NO CONFLICT (Independent)

All other combinations can develop in parallel

---

## Worktree Setup Commands

```bash
# Create all 13 worktrees from main:

git worktree add .trees/claude-refinement -b feature/claude-refinement origin/main
git worktree add .trees/marketing-content -b feature/marketing-content origin/main
git worktree add .trees/script-testing -b feature/script-testing origin/main
git worktree add .trees/template-creation -b feature/template-creation origin/main
git worktree add .trees/docx-verification -b feature/docx-verification origin/main
git worktree add .trees/calendly -b feature/calendly origin/main
git worktree add .trees/dashboard-redesign -b feature/dashboard-redesign origin/main
git worktree add .trees/database-viz -b feature/database-viz origin/main
git worktree add .trees/gemini-prompts -b feature/gemini-prompts origin/main
git worktree add .trees/librarian -b feature/librarian origin/main
git worktree add .trees/email-refinement -b feature/email-refinement origin/main
git worktree add .trees/github-streamline -b feature/github-streamline origin/main
git worktree add .trees/analytics -b feature/analytics origin/main
```

## Recommended Merge Order

### Priority Groups (can merge in any order within group)

**Group 1: Foundation (Merge First)**
- Task 1: `feature/claude-refinement`
- Task 10: `feature/librarian`
- Task 12: `feature/github-streamline`

**Group 2: Content & Infrastructure**
- Task 9: `feature/gemini-prompts`
- Task 2: `feature/marketing-content` (after Task 9)
- Task 4: `feature/template-creation`
- Task 3: `feature/script-testing`

**Group 3: Quality & Verification**
- Task 5: `feature/docx-verification` (after Task 4)

**Group 4: Delivery Systems**
- Task 6: `feature/calendly`
- Task 11: `feature/email-refinement`

**Group 5: Monitoring & Analytics (Merge Last)**
- Task 13: `feature/analytics`
- Task 7: `feature/dashboard-redesign`
- Task 8: `feature/database-viz`

## Coordination Requirements

### Before Starting Development

**Create API Contracts:**
```bash
mkdir -p docs/api-contracts/v4.2.0

# Required contracts:
# - template-variables.md (Tasks 2, 4)
# - application-package.md (Tasks 6, 11)
# - analytics-events.md (Tasks 7, 8, 13)
# - gemini-prompts.md (Tasks 2, 9)
# - dashboard-components.md (Tasks 7, 8)
```

### File Ownership Rules

**Exclusive Ownership (only one task can modify):**
- Task 1: `CLAUDE.md`, `.claude/commands/`
- Task 2: `modules/content/marketing_*`
- Task 3: `tests/`
- Task 4: `templates/`
- Task 5: `modules/document_generation/*verif*`
- Task 6: `modules/scheduling/`
- Task 7: `dashboard/`, main dashboard templates
- Task 8: DB visualization components
- Task 9: `modules/ai_job_description_analysis/prompts*`
- Task 10: `docs/file-organization-*`
- Task 11: `modules/email_integration/`
- Task 12: `.github/`, git scripts
- Task 13: `modules/analytics/`

**Shared Files (must coordinate):**
- `frontend_templates/` - Tasks 7, 8 (strict separation)
- `modules/workflow/` - Tasks 6, 11 (package assembly)
- API contract docs - All tasks read, update when needed

### Daily Sync Protocol

**Location:** `/tasks/v4.2.0-planning/daily-sync.md`

**Format:**
```markdown
## 2025-10-08

### Task 1: Claude Refinement (@you)
- Status: In progress
- Files: CLAUDE.md, .claude/commands/analyze.md
- Blockers: None
- Impacts: Task 2 (new agents available soon)

### Task 2: Marketing Content (@you)
- Status: Blocked
- Waiting for: Task 9 (prompt API definition)
- Files: None yet
- Next: Will start once prompts defined
```

## Conflict Resolution Strategy

### When Conflicts Arise

1. **Coordinate in Advance:**
   - Before modifying shared file, post in daily-sync.md
   - Get acknowledgment from other task owner
   - Agree on approach

2. **Define Interface First:**
   - Create API contract document
   - Both tasks implement to contract
   - Update contract if changes needed

3. **Sequential if Necessary:**
   - If tasks can't parallel, merge one first
   - Other task rebases on main
   - Proceed with updated base

4. **Merge Conflict Resolution:**
   - Feature being merged resolves conflicts
   - Test after resolution
   - Document decision in `/docs/decisions/`

### Pre-Merge Checklist

**For Each Feature:**
- [ ] All tests pass in isolation
- [ ] No conflicts with open PRs
- [ ] API contracts updated
- [ ] Documentation complete
- [ ] Code review approved
- [ ] Integration test passed

### Integration Testing

**Before merging to main:**
```bash
# Create test merge branch
git checkout -b test/merge-<feature-name> main
git merge <feature-branch> --no-ff

# Run full test suite
pytest tests/
npm test  # for dashboard/frontend
python -m flake8

# If pass, merge to main
# If fail, fix in feature branch
```

## Work in Progress Tracking

**Worktree Status Script:**

Create `scripts/worktree-status.sh`:
```bash
#!/bin/bash
echo "=== Active Worktrees ==="
git worktree list

echo -e "\n=== Branch Status ==="
for branch in $(git branch | grep feature/); do
  echo -n "$branch: "
  git log -1 --pretty=format:"%s (%ar)" $branch
  echo
done

echo -e "\n=== Conflicts Check ==="
# Check if any open PRs modify same files
```

## Summary

**13 Worktrees Created:**
- ✅ Complete independence
- ✅ Parallel development
- ✅ Isolated testing

**Conflicts Managed Through:**
- API contracts (define interfaces first)
- File ownership (exclusive rights)
- Daily sync (coordinate shared files)
- Merge order (minimize conflicts)

**Success Strategy:**
- Define before develop
- Coordinate shared files
- Test before merge
- Resolve conflicts in feature branch
- Merge in recommended order
