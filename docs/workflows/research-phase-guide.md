# Research Phase Guide
**Version:** 1.0
**Date:** October 6, 2025
**Environment:** Claude Code

## Overview

The Research Phase happens **automatically before PRD creation** to understand the existing codebase, identify integration points, and inform better clarifying questions. Research depth adapts to task complexity.

## When Research Happens

```
User: /task [description]
  ↓
PHASE 0: Research (automatic)
  ↓
PHASE 1: PRD Creation (informed by research)
  ↓
PHASE 2: Task Generation
  ↓
PHASE 3: Task Execution
```

## Research Depth Levels

### Level 1: Quick Scan (1-2 minutes)
**When:** Simple, isolated features with minimal dependencies

**What to find:**
- Does similar functionality already exist?
- What's the relevant module directory?
- What's the primary programming language/framework?

**Methods:**
- Search for keywords in file names
- Quick grep for similar patterns
- Check project structure

**Example:** Adding a new validation rule to existing validator

---

### Level 2: Moderate Research (3-5 minutes)
**When:** Features that integrate with existing systems

**What to find:**
- Which files/modules will be affected?
- What's the current architecture pattern?
- What dependencies exist?
- Are there similar implementations to reference?

**Methods:**
- Read relevant module READMEs
- Examine existing similar features
- Check database schema for related tables
- Review API endpoints in same domain

**Example:** Adding email validation system (our example feature)

---

### Level 3: Deep Research (10-15 minutes)
**When:** Complex features, major refactors, or cross-cutting concerns

**What to find:**
- Complete system architecture
- All integration points and dependencies
- Design patterns and conventions
- Performance implications
- Security considerations
- Data flow across multiple modules

**Methods:**
- Read architectural documentation
- Trace code flow through multiple modules
- Review related PRDs/tasks from archives
- Check for design decisions in docs/decisions/
- Examine test patterns

**Example:** Refactoring authentication system, adding multi-tenant support

---

## Research Process

### Step 1: Determine Research Depth

**Automatic classification based on keywords:**

**Level 1 indicators:**
- "Add validation rule"
- "Fix bug in [specific function]"
- "Update field in [table]"
- "Add endpoint to existing API"

**Level 2 indicators:**
- "Implement [new feature]"
- "Add [integration] with [external system]"
- "Create [new module/service]"
- Most typical feature requests

**Level 3 indicators:**
- "Refactor [major component]"
- "Migrate from [X] to [Y]"
- "Add [cross-cutting concern]" (auth, logging, caching)
- "Redesign [architecture]"

### Step 2: Execute Research

**For all levels, check:**
```
[ ] Project structure (ls -la, tree)
[ ] Relevant module directories
[ ] Similar existing features
[ ] Database schema (if data-related)
[ ] Configuration files
```

**Level 2 adds:**
```
[ ] Related module documentation
[ ] Integration points
[ ] Dependency analysis
[ ] API contracts/interfaces
```

**Level 3 adds:**
```
[ ] Architectural documentation
[ ] Design decision records
[ ] Cross-module data flow
[ ] Performance/security implications
[ ] Historical context (git history, archived tasks)
```

### Step 3: Document Findings

**Create:** `/tasks/research-[timestamp].md` or `/tasks/[feature-name]/research.md` (if feature name is clear)

**Template:**

```markdown
# Research: [Feature Name]

**Date:** 2025-10-06
**Research Depth:** Level 2
**Time Spent:** 4 minutes

## Task Description
[User's original request]

## Research Questions
1. Does similar functionality exist?
2. What modules will be affected?
3. What's the current architecture pattern?
4. What dependencies are involved?

## Findings

### Existing Similar Features
- **Location:** modules/validation/
- **Pattern:** Validator classes with validate() method
- **Notable:** Already uses email-validator library for basic format checking

### Affected Files/Modules
- `modules/validation/` - Core validation logic
- `modules/database/models.py` - User model updates needed
- `static/js/` - Frontend validation integration
- `database_tools/migrations/` - New tables

### Current Architecture
- **Pattern:** Service-oriented with Flask blueprints
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Frontend:** Vanilla JavaScript with fetch API
- **Cache:** Redis available but not heavily used

### Dependencies
- **Existing:** email-validator (basic format only)
- **Need to add:** dnspython (for MX record checks)
- **Redis:** Already configured, can use for caching

### Integration Points
- User registration form (frontend)
- User model (database)
- Email sending service (downstream dependency)

### Constraints/Considerations
- Must maintain < 200ms response time (user-facing validation)
- DNS queries can be slow - need caching strategy
- Privacy: don't log email addresses (GDPR)

### Similar Implementations (References)
- `modules/validation/password_validator.py` - Similar validation pattern
- `modules/scraping/data_validator.py` - Similar async validation approach

## Recommended Approach

Based on research, recommend:

**Option A: Extend Existing Validator** (recommended)
- Pros: Follows established pattern, reuses infrastructure
- Cons: None significant
- Effort: Medium

**Option B: Create Separate Email Service**
- Pros: Better separation of concerns
- Cons: Adds complexity, duplicate validation code
- Effort: High

**Option C: Use Third-Party Service (ZeroBounce, etc.)**
- Pros: More comprehensive validation
- Cons: Costs money, external dependency, slower
- Effort: Medium

## Questions for User

Based on research, I have these clarifying questions:

1. **Validation depth:** Which approach do you prefer?
   a) Option A: Extend existing validator (faster, follows pattern)
   b) Option B: Separate service (more isolated)
   c) Option C: Third-party service (more comprehensive but costs $)

2. **DNS validation:** DNS checks can be slow. How should we handle timeouts?
   a) 100ms timeout, fallback to format-only validation
   b) 500ms timeout, show loading indicator to user
   c) Skip DNS validation entirely (format-only)

3. **Disposable emails:** Should we block disposable email providers?
   a) Yes, block completely (10minutemail.com, etc.)
   b) Allow but warn user
   c) No restrictions

[Continue with more clarifying questions...]

## Next Steps

1. Get user responses to clarifying questions above
2. Create PRD based on chosen approach (Option A recommended)
3. Proceed with task generation

---

**Research completed. Ready to ask clarifying questions.**
```

### Step 4: Present Options to User

After research, present findings as **easy-to-select options**:

```markdown
I've completed research on implementing email validation. Here's what I found:

## Existing System
- Validation module exists at `modules/validation/`
- Currently uses basic email-validator library (format only)
- Pattern: Validator classes with validate() method

## Recommended Approaches

**Option A: Extend Existing Validator** ⭐ (Recommended)
- Follows established pattern in `modules/validation/password_validator.py`
- Reuses infrastructure (Redis cache, validation framework)
- Moderate effort

**Option B: Create Separate Email Service**
- Better isolation, independent from validation module
- More complexity, potential code duplication
- Higher effort

**Option C: Third-Party Service (ZeroBounce)**
- Most comprehensive (mailbox verification, reputation check)
- External dependency, costs ~$0.001 per validation
- Medium effort to integrate

Which approach would you like to take?

---

I also have clarifying questions about:
1. DNS validation timeout strategy
2. Disposable email handling
3. International email support (IDN)

[Present each with a/b/c options]

Would you like me to proceed with clarifying questions based on your chosen approach?
```

## Managing Research Depth

**Automatic depth selection based on complexity indicators:**

```python
def determine_research_depth(task_description: str) -> int:
    """
    Determines research depth (1-3) based on task complexity.

    Returns:
        1: Quick scan (1-2 min)
        2: Moderate research (3-5 min)
        3: Deep research (10-15 min)
    """
    task_lower = task_description.lower()

    # Level 3: Deep research needed
    deep_keywords = ['refactor', 'migrate', 'redesign', 'architecture',
                     'multi-tenant', 'authentication', 'authorization',
                     'security', 'performance optimization']
    if any(keyword in task_lower for keyword in deep_keywords):
        return 3

    # Level 1: Quick scan sufficient
    quick_keywords = ['fix bug', 'update field', 'add validation',
                      'typo', 'update text', 'change color']
    if any(keyword in task_lower for keyword in quick_keywords):
        return 1

    # Level 2: Default for most features
    return 2
```

**Time limits:**
- Level 1: 2 minute max
- Level 2: 5 minute max
- Level 3: 15 minute max

**Stop research when:**
- Time limit reached
- Sufficient information gathered to ask good clarifying questions
- User signals to move on

## Research Output Format

**Save to:**
- If feature name clear: `/tasks/[feature-name]/research.md`
- If not clear yet: `/tasks/research-[timestamp].md` (move later after PRD created)

**Always include:**
1. Research depth level used
2. Key findings (existing code, patterns, dependencies)
3. **Recommended approaches with Options A/B/C**
4. Clarifying questions informed by research

## Integration with Workflow

**Updated workflow:**

```
/task [description]
  ↓
1. Determine research depth (1-3)
  ↓
2. Execute research (time-boxed)
  ↓
3. Document findings
  ↓
4. Present options (A/B/C) to user
  ↓
5. Ask clarifying questions (informed by research + chosen option)
  ↓
6. Create PRD
  ↓
7. Generate tasks
  ↓
8. Execute
```

## Example: Research → Clarifying Questions Flow

**User:** `/task implement email validation`

**Agent:**
```
Starting Research Phase (Level 2)...

[Searches codebase for 2-3 minutes]

Research complete! Findings saved to /tasks/email-validation/research.md

## Key Findings:
- Existing validation module at modules/validation/
- Similar pattern in password_validator.py we can follow
- Redis cache available but underutilized
- DNS queries will need timeout handling

## Recommended Approaches:

**Option A: Extend Existing Validator** ⭐
- Follows established patterns
- Moderate effort

**Option B: Separate Service**
- More isolated
- Higher effort

**Option C: Third-Party Service**
- Most comprehensive
- Requires budget approval

Which approach would you like? (A/B/C)
```

**User:** A

**Agent:**
```
Great! I'll proceed with Option A (extend existing validator).

Now I have clarifying questions based on this approach:

1. DNS validation timeout?
   a) 100ms timeout, fallback to format-only
   b) 500ms timeout, show loading indicator

2. Disposable email handling?
   a) Block completely
   b) Allow with warning
   c) No restrictions

3. Caching strategy?
   a) 24-hour cache (recommended based on existing Redis setup)
   b) 1-hour cache
   c) No caching

[etc...]
```

This gives you **three opportunities for clarification:**
1. **Before research:** Initial task description
2. **After quick research:** Choose approach (A/B/C)
3. **After approach chosen:** Detailed questions informed by research + chosen approach

---

**Does this research phase structure work for you?**
- Automatic depth detection
- Time-boxed (don't waste time)
- Options-based decisions (easy A/B/C selection)
- Research findings documented
- Informs better clarifying questions
