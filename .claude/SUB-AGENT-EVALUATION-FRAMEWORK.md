# Sub-Agent Evaluation Framework

**Purpose:** Systematic framework for evaluating whether a task pattern should become a specialized sub-agent.

---

## Evaluation Process

### Step 1: Pattern Recognition
Identify the activity pattern from agent activity logs or current work.

**Questions to answer:**
- What task is being performed?
- What tools are being used?
- What domain knowledge is required?
- How often does this pattern occur?

### Step 2: Criteria Assessment
Score the pattern against 5 key criteria (detailed below).

### Step 3: Cost-Benefit Analysis
Evaluate whether creating a sub-agent provides clear value.

### Step 4: Decision & Documentation
Document the decision and rationale (whether yes or no).

---

## The 5 Criteria

### 1. Domain-Specific Expertise ⭐ High Priority

**Question:** Does this task require specialized knowledge of a particular system, module, or domain?

**Scoring:**
- ✅ **Yes (2 points):** Task requires deep understanding of specific domain
  - Examples: Database schema work, API integration, security reviews
- ⚠️ **Partial (1 point):** Some domain knowledge helpful but not critical
  - Examples: Code formatting, file organization
- ❌ **No (0 points):** General-purpose task, no special expertise needed
  - Examples: Simple file operations, basic documentation

**Why this matters:**
- Sub-agents can load domain-specific context automatically
- Builds expertise over time through consistent context
- Reduces cognitive load on primary agent

---

### 2. Repeated Workflow ⭐ High Priority

**Question:** Is this the same sequence of steps/tools used multiple times?

**Scoring:**
- ✅ **Yes (2 points):** Clear, repeatable pattern observed 3+ times
  - Examples: Schema → Model → Test workflow, Research → Compare → Recommend
- ⚠️ **Partial (1 point):** Similar pattern with variations, seen 2 times
  - Examples: Different types of analysis with similar structure
- ❌ **No (0 points):** One-off task or highly variable workflow
  - Examples: Unique feature implementation

**Why this matters:**
- Automation value increases with repetition
- Consistent patterns are easier to codify
- Reduces redundant decision-making

---

### 3. High Context Requirements ⭐ Medium Priority

**Question:** Does this task always need specific documentation or knowledge loaded?

**Scoring:**
- ✅ **Yes (2 points):** Always requires same context files/docs
  - Examples: Needs database schema, API specs, architecture diagrams
- ⚠️ **Partial (1 point):** Sometimes needs context, varies by task
  - Examples: Might need different module docs depending on feature
- ❌ **No (0 points):** Minimal context needed, uses general knowledge
  - Examples: Simple refactoring, basic code cleanup

**Why this matters:**
- Sub-agents can pre-load required context automatically
- Saves tokens by loading only relevant context
- Enables context priming strategy

---

### 4. Clear Boundaries ⭐ High Priority

**Question:** Are inputs/outputs well-defined with predictable scope?

**Scoring:**
- ✅ **Yes (2 points):** Clear inputs → predictable outputs, contained scope
  - Examples:
    - Input: Schema changes → Output: Models + Tests
    - Input: API spec → Output: Documentation
- ⚠️ **Partial (1 point):** Generally bounded but some variability
  - Examples: Code review (scope varies by change size)
- ❌ **No (0 points):** Open-ended, unpredictable scope
  - Examples: "Improve the system architecture"

**Why this matters:**
- Well-bounded tasks are easier to delegate
- Clear scope enables autonomous execution
- Predictable outputs ensure quality

---

### 5. Autonomous Execution ⭐ Medium Priority

**Question:** Can this task be completed without constant user interaction?

**Scoring:**
- ✅ **Yes (2 points):** Can complete end-to-end autonomously
  - Examples: Generate docs from code, create CRUD endpoints, run tests
- ⚠️ **Partial (1 point):** Needs occasional user input/approval
  - Examples: Needs approval on design choices, user selects option
- ❌ **No (0 points):** Requires continuous user collaboration
  - Examples: Architecture decisions, requirement gathering

**Why this matters:**
- Autonomous agents minimize user time
- Reduces context switching for user
- Enables parallel work (user does other things)

---

## Scoring Matrix

### Total Score Interpretation

**Score: 8-10 points → HIGH PRIORITY**
- Create sub-agent immediately
- Clear, high-value automation opportunity
- Meets most/all criteria

**Score: 5-7 points → MEDIUM PRIORITY**
- Consider for sub-agent
- Evaluate based on frequency
- May wait to see if pattern strengthens

**Score: 0-4 points → LOW PRIORITY**
- Not worth sub-agent overhead
- Better handled by primary agent
- Document decision to avoid reconsideration

### Quick Decision Matrix

| Criteria Met | Score Range | Decision |
|--------------|-------------|----------|
| 4-5 criteria (including 2+ High Priority) | 8-10 | Create sub-agent |
| 3 criteria (including 1+ High Priority) | 5-7 | Consider, wait for more data |
| 0-2 criteria | 0-4 | Don't create sub-agent |

---

## Evaluation Template

```markdown
## Sub-Agent Evaluation: [Agent Name]

**Date:** [YYYY-MM-DD]
**Evaluator:** [Who is evaluating]
**Pattern Source:** [Activity log session or observation]

### Task Pattern Description
[Describe what the agent would do]

### Criteria Scoring

#### 1. Domain-Specific Expertise
- **Score:** [0/1/2]
- **Rationale:** [Why this score?]
- **Domain:** [If applicable, what domain?]

#### 2. Repeated Workflow
- **Score:** [0/1/2]
- **Rationale:** [Why this score?]
- **Frequency:** [How many times observed?]
- **Pattern:** [Describe the workflow]

#### 3. High Context Requirements
- **Score:** [0/1/2]
- **Rationale:** [Why this score?]
- **Context Needed:** [List required docs/files]

#### 4. Clear Boundaries
- **Score:** [0/1/2]
- **Rationale:** [Why this score?]
- **Inputs:** [What does agent receive?]
- **Outputs:** [What does agent produce?]

#### 5. Autonomous Execution
- **Score:** [0/1/2]
- **Rationale:** [Why this score?]
- **User Interaction:** [How much needed?]

### Total Score: [X/10]

### Decision: [CREATE / CONSIDER / DON'T CREATE]

### Rationale
[Explain the decision based on scoring and other factors]

### Next Steps
- [ ] [If CREATE: Design agent interface]
- [ ] [If CREATE: Create agent file]
- [ ] [If CREATE: Test agent]
- [ ] [If CONSIDER: Track pattern for X more occurrences]
- [ ] [If DON'T CREATE: Document why to prevent future reconsideration]

---
```

---

## Cost-Benefit Analysis

### Benefits of Creating Sub-Agent

**Quantifiable:**
- Reduced token usage (pre-loaded context)
- Faster execution (specialized focus)
- Consistent quality (domain expertise)
- Parallel work (user can multitask)

**Qualitative:**
- Reduced cognitive load on primary agent
- Better separation of concerns
- Easier to improve specific workflows
- Clearer responsibilities

### Costs of Creating Sub-Agent

**Initial:**
- Time to design and create agent
- Time to test and refine
- Documentation effort

**Ongoing:**
- Maintenance when patterns change
- Complexity in deciding when to use
- Potential confusion if poorly scoped

### Break-Even Analysis

**Questions to ask:**
- How many times must this pattern occur to justify creation?
- Is the task complex enough to warrant specialization?
- Will this pattern continue or is it temporary?
- Could existing agents be extended instead?

**Rule of Thumb:**
- Pattern repeats 3+ times → worth considering
- Pattern repeats 5+ times → strong candidate
- Pattern is critical path → consider even if less frequent

---

## Alternative Solutions

Before creating a sub-agent, consider alternatives:

### 1. Enhance Existing Agent
Could an existing agent be extended to handle this?
- Example: Extend code-reviewer to also check security

### 2. Create Template/Guide
Would a template or guide document suffice?
- Example: Task workflow templates instead of workflow agent

### 3. Slash Command
Would a custom slash command work better?
- Example: `/schema-update` command vs. schema agent

### 4. Context Priming File
Could context priming solve this?
- Example: Load specific docs instead of creating agent

### 5. Primary Agent with Good Prompts
Can primary agent handle this with clear instructions?
- Example: Detailed guidelines in CLAUDE.md

---

## Examples of Good vs. Bad Candidates

### ✅ Good Sub-Agent Candidates

**Database Schema Generator**
- Domain expertise: ✅ (database schemas)
- Repeated workflow: ✅ (every schema change)
- Context requirements: ✅ (schema docs always needed)
- Clear boundaries: ✅ (schema → models/tests)
- Autonomous: ✅ (can generate without user input)
- **Score: 10/10 → CREATE**

**API Documentation Generator**
- Domain expertise: ✅ (API design patterns)
- Repeated workflow: ✅ (every new endpoint)
- Context requirements: ✅ (API specs, examples)
- Clear boundaries: ✅ (code → docs)
- Autonomous: ✅ (can document from code)
- **Score: 10/10 → CREATE**

### ⚠️ Maybe Sub-Agent Candidates

**Code Reviewer** (Already exists!)
- Domain expertise: ⚠️ (general code quality)
- Repeated workflow: ✅ (after every change)
- Context requirements: ✅ (CLAUDE.md standards)
- Clear boundaries: ⚠️ (varies by change size)
- Autonomous: ✅ (can review without user)
- **Score: 7/10 → CONSIDER (exists as sub-agent)**

**File Organizer**
- Domain expertise: ❌ (general file operations)
- Repeated workflow: ⚠️ (occasional refactoring)
- Context requirements: ❌ (minimal)
- Clear boundaries: ✅ (structure → organized files)
- Autonomous: ⚠️ (might need approval)
- **Score: 4/10 → DON'T CREATE**

### ❌ Bad Sub-Agent Candidates

**Feature Implementer**
- Domain expertise: ❌ (varies by feature)
- Repeated workflow: ❌ (each feature unique)
- Context requirements: ⚠️ (varies widely)
- Clear boundaries: ❌ (scope varies greatly)
- Autonomous: ❌ (needs constant user input)
- **Score: 1/10 → DON'T CREATE**

**General Helper**
- Domain expertise: ❌ (too broad)
- Repeated workflow: ❌ (no consistent pattern)
- Context requirements: ❌ (varies)
- Clear boundaries: ❌ (unclear scope)
- Autonomous: ❌ (depends on task)
- **Score: 0/10 → DON'T CREATE**

---

## Integration with Activity Logging

**Workflow:**
1. Log activities in `agent-activity-log.md`
2. Notice patterns after 2-3 occurrences
3. Use this framework to evaluate
4. Document decision
5. If creating agent, design and implement
6. Track agent usage and effectiveness

**Continuous Improvement:**
- Review agent effectiveness quarterly
- Sunset agents that aren't used
- Merge agents with overlapping responsibilities
- Refine agent scope based on usage patterns

---

## Decision Archive

Track all evaluation decisions to prevent re-evaluation of rejected ideas.

### Agents Created
- [Agent name] - [Date] - [Brief description]

### Agents Rejected
- [Idea name] - [Date] - [Score: X/10] - [Reason not created]

### Agents Under Consideration
- [Idea name] - [Current score] - [Waiting for X more occurrences]

---

## Notes

**Key Principles:**
- Sub-agents should have clear, focused purposes
- Don't create agents for temporary needs
- Prefer extending existing agents over creating new ones
- Document decisions (yes or no) to prevent repeated evaluation
- Regularly review and refine existing agents
