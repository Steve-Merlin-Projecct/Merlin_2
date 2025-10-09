# v4.2.0 Feature Branch & Worktree Strategy

**Version:** 4.2.0
**Created:** October 8, 2025

## Executive Summary

**9 Feature Branches** organized into **4 Development Phases** with clear merge sequencing to avoid conflicts.

## Feature Branch Structure

### Phase 1: Foundation (Sequential) - Merge First

#### Feature 1: Claude Development Tools
**Branch:** `feature/claude-dev-tools`
**Worktree:** `.trees/claude-tools`
**Tasks:** #1, #10, #13
**Priority:** P0 - MUST complete first

**Scope:**
- Refine CLAUDE.md with improved instructions
- Create specialized agents (content, testing, deployment)
- Develop slash commands for common workflows
- Streamline GitHub connection (gh CLI optimization)
- Librarian: Create file organization action plan

**Files Modified:**
- `CLAUDE.md`
- `.claude/commands/*.md` (new slash commands)
- `docs/agent-creation-guide.md` (new)
- `docs/file-organization-action-plan.md` (new, from Librarian)
- `.github/` (GitHub connection improvements)

**Conflicts:** None (foundation work)
**Estimated Time:** 2-3 days

---

### Phase 2: Content & Templates (Parallel) - Merge Second

#### Feature 2: Content Generation System
**Branch:** `feature/content-ai-system`
**Worktree:** `.trees/content-ai`
**Tasks:** #2, #9
**Priority:** P0
**Dependencies:** Feature 1 (may use specialized agents)

**Scope:**
- Marketing automation content generation (specialist/manager roles)
- Refine existing content library
- Gemini prompt improvements (quality + injection protection)
- Create content generation agents (if Phase 1 complete)
- Establish content quality metrics

**Files Modified:**
- `modules/ai_job_description_analysis/` (Gemini prompts)
- `modules/content/` (content generation)
- `modules/content/marketing_automation_content.py` (new)
- `docs/content-generation-guide.md` (new)
- Security: Prompt injection tests

**Conflicts:**
- 🟡 With Feature 3 (template variables must align)
- Solution: Define variable schema in API contract first

**Estimated Time:** 4-5 days

---

#### Feature 3: Template & Verification System
**Branch:** `feature/template-verification`
**Worktree:** `.trees/templates`
**Tasks:** #4, #5
**Priority:** P0
**Dependencies:** None (can parallel with Feature 2)

**Scope:**
- Source new cover letter examples (10+ templates)
- Source new resume examples (10+ templates)
- Convert to .docx templates with variables
- Create docx verification metrics (authenticity scoring)
- Build automated template testing

**Files Modified:**
- `templates/cover_letters/*.docx` (new templates)
- `templates/resumes/*.docx` (new templates)
- `modules/document_generation/template_verifier.py` (new)
- `modules/document_generation/authenticity_metrics.py` (new)
- `tests/templates/` (verification tests)

**Conflicts:**
- 🟡 With Feature 2 (variable schema coordination)
- Solution: Document template variables in shared spec

**Estimated Time:** 5-6 days

---

### Phase 3: Delivery Systems (Parallel) - Merge Third

#### Feature 4: Calendly Integration
**Branch:** `feature/calendly-integration`
**Worktree:** `.trees/calendly`
**Tasks:** #6
**Priority:** P1
**Dependencies:** None

**Scope:**
- Create time suggestion rules (based on job posting, availability)
- Integrate Calendly API
- Insert Calendly links into application packages
- Handle timezone conversions
- Track scheduling analytics

**Files Modified:**
- `modules/scheduling/calendly_integration.py` (new)
- `modules/scheduling/time_suggestion_engine.py` (new)
- `modules/workflow/` (add Calendly to package)
- `modules/database/` (scheduling tracking tables)
- `.env.example` (Calendly API key)

**Conflicts:**
- 🟡 With Feature 5 (both modify application package)
- Solution: Calendly adds link, Email delivers package - coordinate API

**Estimated Time:** 3-4 days

---

#### Feature 5: Email System Refinement
**Branch:** `feature/email-system-v2`
**Worktree:** `.trees/email`
**Tasks:** #11
**Priority:** P1
**Dependencies:** Feature 4 (Calendly link in email)

**Scope:**
- **Phase 1:** Send test to personal email
- **Phase 2:** Send to job description email
- **Phase 3:** Source email from internet research
- **Phase 4:** Deprecate in favor of BOS (apply-on-site)

**Files Modified:**
- `modules/email_integration/email_delivery.py`
- `modules/email_integration/email_sourcing.py` (new)
- `modules/email_integration/bos_transition.py` (new)
- `modules/workflow/email_application_api.py`
- Deprecation: Email system phaseout plan

**Conflicts:**
- 🟡 With Feature 4 (application package structure)
- Solution: Define package schema, coordinate timing

**Estimated Time:** 4-5 days (phased rollout)

---

### Phase 4: Monitoring & Analytics (Coordinated Parallel) - Merge Last

#### Feature 6: Dashboard & Analytics System
**Branch:** `feature/dashboard-analytics`
**Worktree:** `.trees/dashboard`
**Tasks:** #7, #8, #13
**Priority:** P1
**Dependencies:** None (but benefits from earlier features' data)

**Scope:**
- **Dashboard Redesign:** Node.js + Tailwind CSS
- **Database Visualization:** Animated schema diagrams
- **Analytics:** Recruiter click tracking and insights
- Real-time monitoring
- Performance metrics

**Files Modified:**
- `frontend_templates/` (complete redesign)
- `dashboard/` (new Node.js app)
- `modules/analytics/click_tracking.py` (new)
- `modules/analytics/recruiter_insights.py` (new)
- `modules/database/analytics_tables.py` (new)
- `static/` (Tailwind CSS)

**Conflicts:**
- 🔴 Internal: Tasks 7, 8, 13 all touch frontend
- Solution: COMBINE into single feature OR strict component isolation

**Estimated Time:** 6-8 days

---

### Ongoing: Quality Assurance

#### Feature 7: Testing Infrastructure
**Branch:** `feature/testing-system`
**Worktree:** `.trees/testing`
**Tasks:** #3
**Priority:** P1
**Dependencies:** None (supports all features)

**Scope:**
- Script testing framework
- Integration test suite
- E2E test automation
- Performance testing
- Test coverage reporting

**Files Modified:**
- `tests/` (all test directories)
- `tests/integration/` (script tests)
- `tests/e2e/` (end-to-end tests)
- `.github/workflows/` (CI/CD test automation)
- `scripts/test_runner.sh` (new)

**Conflicts:**
- 🟢 None (tests don't conflict with features)
- Supports: All features by providing test coverage

**Estimated Time:** Ongoing (parallel with all features)

---

## Worktree Setup Commands

```bash
# Phase 1: Foundation (sequential)
git worktree add .trees/claude-tools -b feature/claude-dev-tools origin/main

# Phase 2: Content & Templates (parallel, after Phase 1)
git worktree add .trees/content-ai -b feature/content-ai-system origin/main
git worktree add .trees/templates -b feature/template-verification origin/main

# Phase 3: Delivery (parallel, after Phase 2)
git worktree add .trees/calendly -b feature/calendly-integration origin/main
git worktree add .trees/email -b feature/email-system-v2 origin/main

# Phase 4: Monitoring (after Phase 3)
git worktree add .trees/dashboard -b feature/dashboard-analytics origin/main

# Ongoing: Testing (parallel with all)
git worktree add .trees/testing -b feature/testing-system origin/main
```

## Merge Sequence (Critical!)

### Round 1: Foundation
```bash
# Merge Feature 1 FIRST
git checkout main
git merge feature/claude-dev-tools --no-ff
git push origin main
```

### Round 2: Content & Templates
```bash
# Merge Features 2 & 3 (parallel possible after API contract)
git merge feature/content-ai-system --no-ff
git merge feature/template-verification --no-ff
git push origin main
```

### Round 3: Delivery
```bash
# Merge Features 4 & 5 (coordinate timing)
git merge feature/calendly-integration --no-ff
git merge feature/email-system-v2 --no-ff
git push origin main
```

### Round 4: Monitoring
```bash
# Merge Feature 6 last
git merge feature/dashboard-analytics --no-ff
git push origin main
```

### Ongoing: Testing
```bash
# Merge testing improvements continuously
git merge feature/testing-system --no-ff
```

## Conflict Avoidance Strategy

### 1. API Contracts (Before Parallel Work)

**Define First:**
- Template variable schema
- Application package structure
- Analytics event schema
- UI component interfaces

**Document Location:** `/docs/api-contracts/v4.2.0/`

### 2. File Ownership Matrix

| Feature | Primary Files | Shared Files | Read-Only Files |
|---------|--------------|--------------|-----------------|
| Claude Tools | `.claude/`, `CLAUDE.md` | - | All others |
| Content AI | `modules/content/`, Gemini prompts | Template vars | Templates |
| Templates | `templates/`, verification | Template vars | Content modules |
| Calendly | `modules/scheduling/` | Workflow package | - |
| Email | `modules/email_integration/` | Workflow package | - |
| Dashboard | `frontend_templates/`, `dashboard/` | Analytics schema | - |
| Testing | `tests/` | - | All modules (read) |

### 3. Communication Protocol

**Daily Sync (Async):**
- Post updates in shared doc: `/tasks/v4.2.0-planning/daily-status.md`
- Flag blockers immediately

**Conflict Resolution:**
- If two features modify same file: coordinate before committing
- If design decision affects multiple features: document in API contract
- If merge conflict occurs: feature owner resolves, not merger

### 4. Integration Testing

**Before Merging to Main:**
1. Feature passes all tests in isolation
2. Integration test in local merge (test/merge-preview)
3. Code review approval
4. Final test in main branch

**Integration Branch (Optional):**
```bash
# Create integration test branch
git checkout -b integration/v4.2.0 main
git merge feature/A
git merge feature/B
# Test combined features
# Delete branch after validation
```

## Risk Mitigation

### High-Risk Conflicts

**CLAUDE.md** (Feature 1 + Librarian):
- Solution: Feature 1 owns CLAUDE.md, Librarian creates separate plan doc

**Frontend Templates** (Dashboard + DB Viz):
- Solution: Component isolation - separate files or strict div boundaries

**Application Package** (Calendly + Email):
- Solution: Define package structure contract first

### Rollback Strategy

**Per Feature:**
```bash
git revert -m 1 <merge-commit-hash>
```

**Full v4.2.0 Rollback:**
```bash
git reset --hard <pre-4.2.0-tag>
```

## Low Priority Features (Backlog)

Not included in v4.2.0 core scope:

20. **Cloud Deployment Prep** → v4.3.0
21. **Bot Application System** → v4.3.0 or v5.0.0
22. **Multi-Platform Scraping** → v4.3.0
23. **Industry Website Scrapers** → v4.3.0
24. **Algorithm Improvements** → Ongoing/v4.3.0

**Rationale:** Focus v4.2.0 on core delivery improvements, save infrastructure expansion for next version.

## Success Metrics

**v4.2.0 Complete When:**
- ✅ All 7 features merged to main
- ✅ Integration tests pass
- ✅ No critical bugs
- ✅ Documentation complete
- ✅ Ready for production deployment

**Timeline:** 4-6 weeks (with parallel development)

---

**Next Steps:**
1. Create detailed PRDs for each feature
2. Set up worktrees
3. Define API contracts
4. Begin Phase 1 (Foundation)
