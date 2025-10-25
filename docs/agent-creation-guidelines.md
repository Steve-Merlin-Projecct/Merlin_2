---
title: "Agent Creation Guidelines"
type: guide
component: general
status: draft
tags: []
---

# Agent Creation Guidelines
*How to Build Effective Claude Code Agents*

## The Goldilocks Principle of Agent Detail

### Too Little Detail ❌
```markdown
- Check for security vulnerabilities
- Review authentication
- Verify input validation
```
**Problem:** Agent has no actionable guidance. Will provide vague feedback like "consider adding security measures."

### Too Much Detail ❌
```markdown
1. Run command: grep -r "API_KEY\s*=" . --include="*.py"
2. If found, check if value contains [a-zA-Z0-9]{20,}
3. If yes, create issue with title "Hardcoded API key found"
```
**Problem:** Too rigid. Agent becomes a script executor, not an intelligent reviewer. Can't adapt to context.

### Just Right ✅
```markdown
### API Key Security

**Principles:**
- API keys must NEVER be hardcoded in source code
- All sensitive credentials must use environment variables
- Keys should be validated at startup, fail fast if missing

**What to Check:**
- Search for hardcoded keys: patterns like `API_KEY = "abc123"`, `token = "sk-..."`
- Verify environment variable usage: `os.getenv('API_KEY')`, `os.environ['TOKEN']`
- Check .env file not committed (in .gitignore)

**Project-Specific:**
- `WEBHOOK_API_KEY`: Used for API authentication, must be in .env
- `GEMINI_API_KEY`: Google AI integration, check rate limiting exists
- `GMAIL_OAUTH_TOKEN`: Should use refresh tokens, not hardcoded

**Example Good:**
```python
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not configured")
```

**Example Bad:**
```python
api_key = "AIzaSyB1234567890abcdef"  # 🚨 CRITICAL
```
```

---

## The Formula for Effective Agents

```
Ideal Detail = Principles + Context + Patterns + Examples + Project-Specifics
```

### Components Explained:

#### 1. **Principles** (The "Why")
- Core concept behind the guideline
- Enables intelligent application to novel situations
- Agent understands intent, not just pattern matching

**Example:**
```markdown
**Principles:**
- SQL injection occurs when untrusted data is concatenated into queries
- Parameterized queries separate code from data
- ORMs like SQLAlchemy provide built-in parameterization
```

#### 2. **Context** (Project-Specific Application)
- How this applies to THIS project
- Specific attack surfaces in YOUR codebase
- Why this matters given your architecture

**Example:**
```markdown
**Project Context:**
- Job scraping module processes untrusted external data
- AI module receives job posting content from third parties
- PostgreSQL database accessed via SQLAlchemy ORM
```

#### 3. **Patterns** (What to Look For)
- Concrete code patterns to search for
- Red flags (dangerous patterns)
- Green flags (safe patterns)

**Example:**
```markdown
**Detection Patterns:**
Red Flags:
- String concatenation: `f"SELECT * FROM users WHERE id={user_id}"`
- String formatting: `"SELECT * FROM users WHERE name = '%s'" % username`

Green Flags:
- ORM usage: `session.query(User).filter_by(id=user_id)`
- Text with params: `session.execute(text("... WHERE id = :id"), {"id": user_id})`
```

#### 4. **Examples** (Good vs Bad Code)
- Side-by-side comparisons
- Clear annotations
- Explanation of why one is better

**Example:**
```markdown
**Safe Pattern:**
```python
# ✅ Good: ORM automatically parameterizes
user = session.query(User).filter_by(id=user_id).first()
```

**Unsafe Pattern:**
```python
# 🚨 CRITICAL: String concatenation enables SQL injection
query = f"SELECT * FROM users WHERE id = {user_id}"
```
```

#### 5. **Project-Specifics** (Your Actual Code)
- Actual modules, APIs, integrations
- Specific files or functions to review
- Team-specific conventions from CLAUDE.md

**Example:**
```markdown
**Project-Specific Checks:**
- `modules/scraping/processor.py`: Verify job data sanitized
- `modules/database/models.py`: All queries use SQLAlchemy ORM
- `modules/ai_job_description_analysis/`: Check Gemini API input validation
```

---

## Quality Tests for Agent Detail

Before finalizing an agent section, ask:

### ✅ Decision Test
**Can the agent make an independent decision?**
- ❌ "Check security"
- ✅ "Search for API keys matching patterns: `API_KEY = "..."`, `token = "sk-..."`, check if in .env"

### ✅ Explanation Test
**Can the agent explain the specific issue?**
- ❌ "Security risk found"
- ✅ "SQL injection risk via string concatenation in job_processor.py:156 where untrusted scraped data is inserted"

### ✅ Fix Test
**Can the agent suggest a concrete fix?**
- ❌ "Improve security"
- ✅ "Replace string concatenation with SQLAlchemy ORM: `session.add(Job(title=job_title))`"

### ✅ Project Test
**Is it tailored to THIS project?**
- ❌ "Check authentication"
- ✅ "Verify WEBHOOK_API_KEY used for Flask API routes, Gmail OAuth token uses refresh pattern"

---

## Recommended Structure Per Agent Capability

```markdown
### [Capability Name]

**Project Context:**
- Why this matters for YOUR project
- Specific risks or requirements in YOUR codebase
- Architectural decisions from CLAUDE.md

**Principles:**
- Core concept or best practice
- Why this approach is recommended
- What problems it prevents

**What to Check:**
- Specific patterns to search for
- Files or modules to review
- Red flags and green flags

**Project-Specific:**
- Your actual modules/APIs/integrations
- Team conventions from CLAUDE.md
- Specific tools or workflows to verify

**Examples:**
```language
# ✅ Good: [explanation]
[code example]

# 🚨 Bad: [explanation]
[code example]
```

**When Issues Found:**
- Severity classification (🔴 Critical, 🟡 Warning, 🟢 Suggestion)
- Required remediation steps
- Reference to CLAUDE.md or documentation
```

---

## Agent Capability Hierarchy

### Level 1: Generic Knowledge (Baseline)
**What:** Universal best practices (OWASP, SOLID, PEP 8)
**Detail Level:** Brief mention, assume agent has base knowledge
**Example:** "Follow OWASP Top 10 guidelines"

### Level 2: Technology-Specific (Stack Alignment)
**What:** Flask, SQLAlchemy, PostgreSQL patterns
**Detail Level:** Moderate - key patterns and anti-patterns
**Example:** "Use SQLAlchemy ORM for queries, avoid raw SQL string concatenation"

### Level 3: Project-Specific (Critical)
**What:** YOUR architecture, modules, conventions
**Detail Level:** High - explicit policies from CLAUDE.md
**Example:** "Verify database schema changes followed automation workflow: never manually edit `database_tools/generated/`"

### Level 4: Module-Specific (Expert)
**What:** Individual module patterns
**Detail Level:** Very High - specific files, functions, integrations
**Example:** "In `modules/ai_job_description_analysis/`, verify Gemini API calls include rate limiting wrapper and input sanitization per LLM injection prevention protocol"

---

## Common Pitfalls to Avoid

### ❌ Pitfall 1: Treating Agent Like a Checklist
```markdown
- [ ] Check for SQL injection
- [ ] Check for XSS
- [ ] Check for CSRF
```
**Why Bad:** Agent will just mark checkboxes, not provide intelligent review

**Better:**
```markdown
### SQL Injection Prevention
[Principles, Context, Patterns, Examples, Project-Specifics as shown above]
```

### ❌ Pitfall 2: Writing a Script
```markdown
1. Run: grep -r "password" .
2. If found, flag as security issue
3. Count occurrences
```
**Why Bad:** Agent becomes rigid executor, can't adapt or understand context

**Better:**
```markdown
**What to Check:**
- Search for hardcoded credentials in patterns like `password = "..."`, `secret = "..."`
- Verify all sensitive values use environment variables
- Consider context: test fixtures with dummy passwords are acceptable
```

### ❌ Pitfall 3: Being Too Abstract
```markdown
Ensure code follows security best practices and maintains high quality standards.
```
**Why Bad:** No actionable guidance, agent will give vague feedback

**Better:**
```markdown
### Security Review Focus Areas
[Specific sections for: API Key Security, SQL Injection, XSS Prevention, etc.]
Each with Principles, Patterns, Examples, Project-Specifics
```

### ❌ Pitfall 4: Ignoring Project Context
```markdown
### Security Review
- Check OWASP Top 10
- Verify input validation
- Review authentication
```
**Why Bad:** Generic advice that doesn't leverage knowledge of YOUR project

**Better:**
```markdown
### Security Review for Job Application System

**Attack Surfaces:**
1. Job scraping (untrusted data from Apify)
2. AI analysis (LLM injection via job descriptions)
3. Gmail integration (OAuth token management)
4. PostgreSQL database (32 tables with relationships)

[Then specific guidance for each]
```

---

## Example: Transforming Generic to Ideal Detail

### Before (Generic):
```markdown
### Code Quality Review
- Check for code smells
- Verify clean code principles
- Ensure maintainability
```

### After (Ideal Detail):
```markdown
### Code Quality & Maintainability

**Project Context:**
- Flask microservice with modular architecture (`/modules` directory)
- Python 3.11 codebase following PEP 8
- Automated quality tools: Black, Flake8, Vulture
- Strict documentation requirements per CLAUDE.md

**Principles:**
- Functions should do one thing well (Single Responsibility)
- Code should be self-documenting with clear naming
- Complexity should be minimal (cyclomatic complexity < 10)
- Duplication should be eliminated (DRY principle)

**What to Check:**

**Function Length:**
- Red flag: Functions > 50 lines (usually doing too much)
- Green flag: Focused functions < 30 lines with single purpose
- Project note: Document generation functions may be longer due to template processing

**Naming Conventions:**
- Functions: `snake_case`, verbs (e.g., `process_job_application()`)
- Classes: `PascalCase`, nouns (e.g., `JobProcessor`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_ATTEMPTS`)
- Module imports: Prefer explicit over wildcard (`from x import y` not `from x import *`)

**Code Duplication:**
- Search for repeated logic across modules
- Especially check: database connection patterns, error handling, API calls
- Project-specific: Document generation has intentional template duplication (acceptable)

**Documentation Requirements (CLAUDE.md):**
- ALL new functions must have docstrings
- Docstrings must include: purpose, args, returns, raises
- Inline comments for complex logic
- Module-level docstrings explaining purpose and relationships

**Examples:**

✅ **Good:**
```python
def validate_job_posting(posting_data: dict) -> bool:
    """
    Validate scraped job posting data before database insertion.

    Args:
        posting_data: Dictionary containing job title, company, description

    Returns:
        True if valid, False otherwise

    Raises:
        ValueError: If required fields missing
    """
    required_fields = ['title', 'company']
    return all(field in posting_data for field in required_fields)
```

🚨 **Bad:**
```python
def process(d):  # No docstring, unclear name, unclear type
    if d['t'] and d['c']:  # Cryptic key names
        # 50 lines of complex logic with no comments
        return True
```

**When Found:**
- 🔴 Critical: Missing docstrings on public functions (CLAUDE.md violation)
- 🟡 Warning: Functions > 50 lines, cyclomatic complexity > 10
- 🟢 Suggestion: Consider extracting helper functions, improving naming
```

---

## The "Teach to Fish" Philosophy

**Goal:** Give the agent enough knowledge to make intelligent decisions, not a script to execute.

**Analogy:**
- ❌ Script: "If you see X, say Y"
- ✅ Agent: "Understand X is dangerous because Z, look for patterns A/B/C, consider context, suggest specific fix"

**How to Test:**
Present the agent section to someone unfamiliar with the topic. Can they:
1. Understand WHY it matters?
2. Identify the issue in code?
3. Explain the risk?
4. Suggest a specific fix?

If yes → Good detail level
If no → Add more Principles, Context, Examples

---

## Agent Creation Checklist

When building or enhancing an agent capability:

- [ ] **Principles defined**: Core concepts explained
- [ ] **Project context**: How it applies to THIS codebase
- [ ] **Patterns specified**: Concrete red flags and green flags
- [ ] **Examples provided**: Good vs bad code snippets
- [ ] **Project-specifics**: Actual modules, APIs, CLAUDE.md policies
- [ ] **Severity levels**: How to classify issues (🔴🟡🟢)
- [ ] **Remediation steps**: Specific fixes, not vague suggestions
- [ ] **References**: Links to CLAUDE.md or documentation
- [ ] **Passes 4 tests**: Decision, Explanation, Fix, Project

---

## Summary: The Formula

```
Effective Agent Capability =
  Principles (Why) +
  Context (Your Project) +
  Patterns (What to Find) +
  Examples (Show Don't Tell) +
  Project-Specifics (Actual Code)
```

**Key Insight:** An agent should be knowledgeable enough to make informed decisions independently, but not so prescriptive that it can't adapt to novel situations. Think expert consultant, not checklist executor.
