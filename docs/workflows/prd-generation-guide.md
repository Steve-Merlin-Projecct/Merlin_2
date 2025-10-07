# PRD Generation Guide (Claude Code Optimized)
**Version:** 1.0
**Date:** October 6, 2025
**Environment:** Claude Code

## Overview

This guide defines how to create a Product Requirements Document (PRD) in Claude Code. PRDs are automatically generated as **Phase 1** of the Automated Task Workflow when a task-oriented request is detected.

## When This Guide Applies

This guide is triggered **automatically** when:
- User request is classified as a **Task** (see [Automated Task Workflow](./automated-task-workflow.md#1-intent-detection-task-vs-question))
- Agent begins Phase 1: PRD Creation

## Goal

Generate a detailed, actionable PRD in Markdown format that:
1. Clearly defines the problem and solution
2. Provides sufficient detail for implementation
3. Is understandable by a junior developer
4. Serves as the foundation for task generation

## Process

### Step 1: Acknowledge Task Detection
```
I've detected this as a task request. I'll automatically create a PRD,
generate a task list, and execute the implementation.

Phase 1: PRD Creation

Before I create the PRD, I have some clarifying questions:
```

### Step 2: Ask Clarifying Questions

**Purpose:** Gather sufficient detail to understand the "what" and "why" (not the "how").

**Question Categories:**

1. **Problem/Goal**
   - "What problem does this feature solve for the user?"
   - "What is the main goal we want to achieve?"

2. **Target User**
   - "Who is the primary user of this feature?"
   - "What is their technical skill level?"

3. **Core Functionality**
   - "Can you describe the key actions a user should perform?"
   - "What is the expected outcome?"

4. **User Stories**
   - "As a [user type], I want to [action] so that [benefit]"
   - Provide 2-3 example stories for user to confirm/modify

5. **Acceptance Criteria**
   - "How will we know when this is successfully implemented?"
   - "What defines 'done' for this feature?"

6. **Scope/Boundaries (Non-Goals)**
   - "Are there specific things this feature should NOT do?"
   - "What is explicitly out of scope?"

7. **Data Requirements**
   - "What data does this feature need to display/manipulate?"
   - "Are there database schema changes required?"

8. **Design/UI (if applicable)**
   - "Are there design mockups or UI guidelines?"
   - "What is the desired look and feel?"

9. **Technical Constraints**
   - "Are there specific technologies/libraries to use or avoid?"
   - "Are there performance requirements?"

10. **Edge Cases**
    - "What error conditions should we handle?"
    - "What are potential failure scenarios?"

**Presentation Format:**
- Use **lettered/numbered lists** for easy response
- Group related options together
- Provide 3-4 options per question when applicable

**Example:**
```markdown
1. Authentication method:
   a) Email + password
   b) OAuth (Google/GitHub)
   c) Magic link (passwordless)
   d) Multi-factor authentication

2. Session duration:
   a) 15 minutes
   b) 1 hour
   c) 24 hours
   d) Remember me option

3. Password requirements:
   a) Minimum 8 characters
   b) Minimum 12 characters with complexity
   c) Passphrase (4+ words)
   d) Custom strength rules
```

### Step 3: Generate PRD

Based on user responses, create a comprehensive PRD using the structure below.

### Step 4: Save PRD

**Location:** `/tasks/[feature-name]/prd.md`

**Directory Structure:**
- Create feature directory: `/tasks/[feature-name]/`
- Use kebab-case for directory name
- Be descriptive but concise
- Examples:
  - `/tasks/user-authentication/prd.md`
  - `/tasks/password-reset/prd.md`
  - `/tasks/export-to-pdf/prd.md`

**File Naming:**
- Always name the PRD file `prd.md` (not `prd-[feature-name].md`)
- This keeps the directory structure clean and consistent

### Step 5: Present for Approval

Show the PRD to the user and ask:
```
I've created the PRD and saved it to /tasks/[feature-name]/prd.md.

Would you like me to proceed with Phase 2: Task Generation?
```

Wait for explicit approval before proceeding.

## PRD Structure

### Template

```markdown
# PRD: [Feature Name]

**Version:** 1.0
**Date:** [YYYY-MM-DD]
**Status:** Draft
**Author:** AI Assistant (Claude Code)

## 1. Introduction/Overview

[2-3 paragraphs describing the feature and the problem it solves]

### Problem Statement
[Clear description of the user pain point or business need]

### Proposed Solution
[High-level description of how this feature addresses the problem]

### Success Criteria
[How we measure success - specific, measurable outcomes]

## 2. Goals

Primary objectives for this feature (specific and measurable):

1. [Goal 1 - e.g., "Enable users to reset passwords within 2 minutes"]
2. [Goal 2 - e.g., "Reduce password-related support tickets by 50%"]
3. [Goal 3 - e.g., "Maintain 99.9% uptime for reset functionality"]

## 3. User Stories

### Primary User Stories

**US1:** As a [user type], I want to [action] so that [benefit].

**Acceptance Criteria:**
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

**US2:** As a [user type], I want to [action] so that [benefit].

**Acceptance Criteria:**
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]

[Add more user stories as needed]

### Secondary User Stories
[Optional - lower priority stories that enhance the feature]

## 4. Functional Requirements

### Core Requirements (Must Have)

**FR1:** [Requirement description]
- **Details:** [Additional context or specifications]
- **Validation:** [How to verify this requirement is met]

**FR2:** [Requirement description]
- **Details:** [Additional context]
- **Validation:** [Verification method]

[Continue numbering sequentially]

### Extended Requirements (Should Have)

**FR10:** [Requirement description]
- **Details:** [Additional context]
- **Validation:** [Verification method]

### Optional Requirements (Nice to Have)

**FR20:** [Requirement description]
- **Details:** [Additional context]
- **Validation:** [Verification method]

## 5. Non-Goals (Out of Scope)

Clear boundaries for what this feature will NOT include:

1. [Non-goal 1 - e.g., "Social media authentication (deferred to v2.0)"]
2. [Non-goal 2 - e.g., "Biometric authentication"]
3. [Non-goal 3 - e.g., "Single sign-on (SSO) integration"]

**Rationale:** [Brief explanation of why these are out of scope]

## 6. Design Considerations

### User Experience
- [UI/UX requirements or guidelines]
- [Wireframes or mockups - link to files if available]
- [Interaction patterns to follow]

### Visual Design
- [Style guide references]
- [Component library to use]
- [Accessibility requirements (WCAG level, etc.)]

### User Flow
```
[Step-by-step user flow diagram or description]
1. User clicks "Forgot Password"
2. System displays email input form
3. User enters email and submits
4. System sends reset link
5. User clicks link in email
...
```

## 7. Technical Considerations

### Architecture
- [System components involved]
- [Integration points with existing systems]
- [APIs or services to be created/modified]

### Data Model
- [Database tables/collections affected]
- [New fields or schema changes required]
- [Data migration needs]

### Security Requirements
- [Authentication/authorization requirements]
- [Data encryption needs]
- [Rate limiting/abuse prevention]
- [Audit logging requirements]

### Performance Requirements
- [Response time targets]
- [Concurrent user capacity]
- [Data volume expectations]

### Dependencies
- [External libraries/services required]
- [Internal modules that must be updated]
- [Third-party integrations]

### Technology Stack
- [Programming languages]
- [Frameworks/libraries]
- [Tools and platforms]

## 8. Success Metrics

How success will be measured post-implementation:

### Quantitative Metrics
1. [Metric 1 - e.g., "Password reset completion rate > 95%"]
2. [Metric 2 - e.g., "Average reset time < 3 minutes"]
3. [Metric 3 - e.g., "Support ticket reduction by 50%"]

### Qualitative Metrics
1. [Metric 1 - e.g., "User satisfaction score > 4.5/5"]
2. [Metric 2 - e.g., "Positive feedback on ease of use"]

### Monitoring & Analytics
- [What data to track]
- [How to measure success criteria]
- [Dashboard or reporting requirements]

## 9. Testing Strategy

### Unit Testing
- [Components requiring unit tests]
- [Code coverage target - e.g., 80%+]

### Integration Testing
- [Integration points to test]
- [End-to-end scenarios]

### User Acceptance Testing
- [UAT scenarios]
- [Test users/groups]

### Security Testing
- [Security test cases]
- [Penetration testing requirements]

## 10. Open Questions

Outstanding items needing clarification:

1. **Q:** [Question 1]
   - **Status:** [Open/Resolved]
   - **Owner:** [Who will answer]

2. **Q:** [Question 2]
   - **Status:** [Open/Resolved]
   - **Owner:** [Who will answer]

## 11. Timeline & Milestones

[If applicable - high-level timeline]

- **Phase 1:** [Description] - [Duration estimate]
- **Phase 2:** [Description] - [Duration estimate]
- **Phase 3:** [Description] - [Duration estimate]

**Total Estimated Duration:** [X weeks/months]

## 12. Risks & Mitigation

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [How to mitigate] |
| [Risk 2] | High/Med/Low | High/Med/Low | [How to mitigate] |

## 13. Assumptions

Key assumptions made during PRD creation:

1. [Assumption 1 - e.g., "PostgreSQL database is already configured"]
2. [Assumption 2 - e.g., "SMTP server is available for email sending"]
3. [Assumption 3 - e.g., "Users have verified email addresses"]

## 14. References

- [Link to design mockups]
- [Link to related documentation]
- [Link to competitive analysis]
- [Link to user research]

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | AI Assistant | Initial PRD creation |

```

## PRD Quality Checklist

Before presenting the PRD to the user, verify:

- [ ] All sections are complete and detailed
- [ ] User stories have specific acceptance criteria
- [ ] Functional requirements are numbered and testable
- [ ] Non-goals clearly define scope boundaries
- [ ] Technical considerations address system integration
- [ ] Success metrics are measurable
- [ ] Language is clear and free of jargon (or jargon is explained)
- [ ] Document is formatted for readability
- [ ] Feature directory created at `/tasks/[feature-name]/`
- [ ] File is saved to `/tasks/[feature-name]/prd.md`

## Target Audience

The primary reader is a **junior developer** who will:
1. Understand the feature's purpose
2. Implement the functionality
3. Write tests based on acceptance criteria
4. Validate the solution meets requirements

Therefore:
- Be explicit and unambiguous
- Avoid unexplained jargon
- Provide sufficient context
- Include examples where helpful

## Integration with Automated Workflow

After PRD approval:
1. **Automatic progression to Phase 2:** Task Generation
2. PRD serves as the input for task breakdown
3. Functional requirements map to implementation tasks
4. User stories guide test case creation
5. Success metrics inform validation criteria

## Examples

### Example 1: Simple Feature PRD
See: `/tasks/password-reset/prd.md` (example)

### Example 2: Complex Feature PRD
See: `/tasks/user-dashboard/prd.md` (example)

## Incremental Improvements

After creating several PRDs, consider:

- **Template files:** Save common sections for your project type
- **Checklist expansion:** Add project-specific items to the quality checklist
- **Example library:** Keep completed PRDs as references for similar features
- **Question bank:** Document which clarifying questions work best for your domain

**Evaluate after:** 3-5 PRDs to identify patterns worth capturing

---

**Document Owner:** Development Team
**Related Guides:**
- [Automated Task Workflow](./automated-task-workflow.md)
- [Task Generation Guide](./task-generation-guide.md)
- [Task Execution Guide](./task-execution-guide.md)

**Last Reviewed:** October 6, 2025
