---
title: "Readme Workflows"
type: process
component: general
status: draft
tags: []
---

# /task Command - Workflows & Templates

Complete guide to the enhanced `/task` command system with workflows and templates.

## Directory Structure

```
.claude/
├── commands/
│   └── task.md                    # /task slash command definition
├── workflows/                      # Workflow orchestration guides
│   ├── go-autonomous.mdc          # Autonomous workflow (minimize user time)
│   └── slow-methodical.mdc        # Methodical workflow (user checkpoints)
├── templates/
│   ├── discovery/                 # Discovery phase templates
│   │   ├── standard.mdc           # Standard discovery (for go workflow)
│   │   └── thorough.mdc           # Thorough discovery (for slow workflow)
│   ├── task-phases/               # Implementation phase templates
│   │   ├── create-prd.mdc         # PRD creation template
│   │   ├── generate-tasks.mdc     # Task list generation
│   │   └── process-tasks.mdc      # Task execution guide
│   └── output-types/              # Non-implementation output templates
│       ├── communicate.mdc        # Human-friendly documentation
│       ├── analyze.mdc            # Analysis without implementation
│       └── research.mdc           # Technology research & evaluation
└── README-WORKFLOWS.md            # This file
```

## Command Syntax

```bash
/task [template] [instructions]
```

## Available Templates

### 1. Default (No Template)
**Usage:** `/task [instructions]`

Standard 3-phase workflow with research, PRD, tasks, and execution.

**Best for:** Regular feature implementation

---

### 2. `go` - Autonomous Workflow (Minimize User Time)
**Usage:** `/task go [instructions]`

**Purpose:** Minimize user interruptions and maximize user's valuable time through autonomous execution

**Philosophy:** The user's time is precious. Take whatever time needed for thorough discovery, deep thinking, and quality implementation. The goal is to minimize how much the user needs to be involved, NOT to rush the agent's work.

**Workflow:**
- **Thorough discovery** - Think deeply, research, avoid asking questions
- **Autonomous task generation** - No "Go" checkpoint, make smart decisions
- **Continuous implementation** - No approval between sub-tasks
- **Self-sufficient problem solving** - Find workarounds for errors/blockers when possible

**Workflow Guide:** `/.claude/workflows/go-autonomous.mdc`

**References:**
- Discovery: `/.claude/templates/discovery/standard.mdc`
- PRD Creation: `/.claude/templates/task-phases/create-prd.mdc`
- Task Generation: `/.claude/templates/task-phases/generate-tasks.mdc`
- Task Execution: `/.claude/templates/task-phases/process-tasks.mdc`

**Example:** `/task go Add email validation to the registration form`

---

### 3. `slow` - Methodical Workflow
**Usage:** `/task slow [instructions]`

**Purpose:** Thorough implementation with multiple user review checkpoints

**Workflow:**
- Comprehensive discovery with user review at every step
- PRD creation with user review
- Task generation with user review of parent tasks AND sub-tasks
- Controlled implementation (approval after EACH sub-task)

**Workflow Guide:** `/.claude/workflows/slow-methodical.mdc`

**References:**
- Discovery: `/.claude/templates/discovery/thorough.mdc`
- PRD Creation: `/.claude/templates/task-phases/create-prd.mdc`
- Task Generation: `/.claude/templates/task-phases/generate-tasks.mdc`
- Task Execution: `/.claude/templates/task-phases/process-tasks.mdc`

**Example:** `/task slow Implement the new payment processing system`

---

### 4. `communicate` - Human-Friendly Documentation
**Usage:** `/task communicate [what to document]`

**Purpose:** Create engaging, narrative-driven documentation for humans

**Output Style:**
- Story-driven narrative (not dry facts)
- Personality and emotional authenticity
- Visual elements (charts, progress bars, emojis)
- Conversational tone
- Celebrates wins, acknowledges challenges

**Template Guide:** `/.claude/templates/output-types/communicate.mdc`

**Use Cases:**
- Sprint retrospectives
- Project status reports for stakeholders
- Development journey documentation
- Milestone celebrations
- Daily dev journals

**Example:** `/task communicate Create a summary of this week's development progress`

**Note:** Documentation only - no implementation

---

### 5. `analyze` - Deep Analysis Without Implementation
**Usage:** `/task analyze [what to analyze]`

**Purpose:** Comprehensive analysis and recommendations without coding

**Output:**
- Executive summary
- Current state documentation
- Findings (strengths, weaknesses, opportunities, risks)
- Detailed analysis with evidence
- Actionable recommendations
- Implementation roadmap

**Template Guide:** `/.claude/templates/output-types/analyze.mdc`

**Analysis Types:**
- Performance analysis
- Security review
- Architecture assessment
- Code quality evaluation

**Example:** `/task analyze the authentication system security`

**Note:** Analysis only - no implementation

---

### 6. `research` - Technology Evaluation & Investigation
**Usage:** `/task research [what to research]`

**Purpose:** Comprehensive research with evidence-based recommendations

**Output:**
- Executive summary
- Multiple options evaluated (pros/cons)
- Side-by-side comparison matrix
- Real-world usage examples
- Risk assessment
- Implementation considerations
- Clear recommendations with justification
- Cited sources

**Template Guide:** `/.claude/templates/output-types/research.mdc`

**Research Types:**
- Library/framework comparison
- Best practices investigation
- Feasibility studies
- Technology evaluation

**Example:** `/task research best Python testing frameworks for Flask`

**Note:** Research only - no implementation

---

## File Organization

All workflow and template files are now organized under `.claude/`:

- **Workflows** (`/.claude/workflows/`) - High-level orchestration guides
- **Templates** (`/.claude/templates/`) - Organized by purpose:
  - `discovery/` - Discovery phase templates
  - `task-phases/` - PRD, task generation, execution
  - `output-types/` - Non-implementation outputs (communicate, analyze, research)
- **Tasks** (`/tasks/`) - Actual work (PRDs, task lists for features)

This separation keeps configuration/templates separate from actual project work.

## Quick Reference

### When to Use Each Template

| Situation | Template | Reason |
|-----------|----------|--------|
| Standard feature work | Default = `go` | Autonomous, minimize user time |
| Want to work on other things | `go` | Agent works independently |
| Complex feature, need involvement | `slow` | Collaborative decision-making |
| Learning/understanding process | `slow` | Educational, step-by-step |
| Project status report | `communicate` | Engaging, human-friendly docs |
| Understanding existing code | `analyze` | Analysis without changes |
| Evaluating technologies | `research` | Evidence-based recommendations |

### Communication Styles

| Template | Style |
|----------|-------|
| `go` | Professional, balanced |
| `slow` | Detailed, educational |
| `communicate` | Warm, conversational, story-driven |
| `analyze` | Professional, evidence-based |
| `research` | Comprehensive, well-sourced |

## Examples

```bash
# Standard implementation = `go`
/task Add user profile editing functionality

# Fast implementation
/task go Fix the broken email validation

# Collaborative implementation
/task slow Implement the new payment gateway

# Create engaging report
/task communicate Write a retrospective for this sprint

# Analyze existing code
/task analyze the database query performance

# Research technology options
/task research whether to use REST or GraphQL
```

## Next Steps

1. **Try the templates** - Use them in real workflows
2. **Refine as needed** - Adjust based on experience
3. **Add more templates** - Create additional templates for specific needs
4. **Document learnings** - Update guides based on what works

## Notes

- All templates maintain the core principle of comprehensive inline documentation
- Templates can be combined or adapted as needed
- The `/task` command will automatically detect which template to use based on the first argument
- Templates marked "no implementation" will only create documentation/reports, not modify code
