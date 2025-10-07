# TodoWrite-Markdown Synchronization Guide
**Version:** 1.0
**Date:** October 6, 2025
**Environment:** Claude Code

## Purpose

This guide provides a simple, foolproof method for keeping TodoWrite and Markdown task lists perfectly synchronized.

## The Core Problem

We maintain task status in **two places**:
1. **TodoWrite tool** - Real-time progress in Claude Code UI
2. **Markdown file** - Persistent task list in `/tasks/[feature-name]/tasklist_1.md`

**Without proper sync:**
- TodoWrite shows different progress than markdown
- User loses trust in task tracking
- Hard to recover from desync state

## The Simple Solution: Same-Response Updates

**RULE:** Always update TodoWrite and Markdown **in the same response**.

Never do this separately. Treat them as a single atomic operation.

## Sync Pattern

Every status change follows this exact pattern:

```
┌─────────────────────────────────┐
│  1. Update TodoWrite            │
│  2. Update Markdown (same msg)  │
│  3. Verify sync                 │
└─────────────────────────────────┘
```

**Key:** Steps 1 and 2 happen in the **same agent response** to the user.

## Pattern 1: Starting a Task

When marking a task as `in_progress`:

```markdown
**Starting Task 1.1**

Updating TodoWrite status to in_progress...
```

```json
{
  "content": "Create User model with authentication fields",
  "activeForm": "Creating User model with authentication fields",
  "status": "in_progress"
}
```

**And updating markdown file:** (same response)

```markdown
- [ ] 1.0 Set up authentication infrastructure
  - [→] 1.1 Create User model with authentication fields
  - [ ] 1.2 Create migration file for users table
```

**Verification:**
✅ TodoWrite shows `in_progress`
✅ Markdown shows `[→]` or similar indicator
✅ Only ONE task is `in_progress` globally

## Pattern 2: Completing a Sub-Task

When marking a sub-task as `completed`:

```markdown
**Completed Task 1.1**

Updating TodoWrite status to completed...
```

```json
{
  "content": "Create User model with authentication fields",
  "activeForm": "Creating User model with authentication fields",
  "status": "completed"
}
```

**And updating markdown file:** (same response)

```markdown
- [ ] 1.0 Set up authentication infrastructure
  - [x] 1.1 Create User model with authentication fields
  - [ ] 1.2 Create migration file for users table
```

**Verification:**
✅ TodoWrite shows `completed`
✅ Markdown shows `[x]`
✅ Both updated together

## Pattern 3: Completing a Parent Task

When all sub-tasks are done and parent task is complete:

```markdown
**Completed Parent Task 1.0**

All sub-tasks complete, tests passed, changes committed.

Updating TodoWrite status to completed...
```

```json
{
  "content": "Set up authentication infrastructure",
  "activeForm": "Setting up authentication infrastructure",
  "status": "completed"
}
```

**And updating markdown file:** (same response)

```markdown
- [x] 1.0 Set up authentication infrastructure
  - [x] 1.1 Create User model with authentication fields
  - [x] 1.2 Create migration file for users table
  - [x] 1.3 Run database migration
```

**Verification:**
✅ TodoWrite parent task: `completed`
✅ Markdown parent task: `[x]`
✅ All sub-tasks also complete in both systems

## Pattern 4: Starting Next Task

After completing one task, immediately start next:

```markdown
**Moving to Task 1.2**

Updating TodoWrite to mark Task 1.2 as in_progress...
```

```json
{
  "content": "Create migration file for users table",
  "activeForm": "Creating migration file for users table",
  "status": "in_progress"
}
```

**And updating markdown file:** (same response)

```markdown
- [ ] 1.0 Set up authentication infrastructure
  - [x] 1.1 Create User model with authentication fields
  - [→] 1.2 Create migration file for users table  ← Now working on this
  - [ ] 1.3 Run database migration
```

**Verification:**
✅ Previous task (`1.1`) is `completed` in both systems
✅ New task (`1.2`) is `in_progress` in both systems
✅ Only ONE task is `in_progress` globally

## What "Same Response" Means

**Example of CORRECT sync** (in one agent message):

```markdown
I've completed adding the User model. Let me update the task status.

[TodoWrite tool call here marking task completed]

I've also updated the markdown task list to show task 1.1 as complete:

[Edit tool call here updating markdown file]

Task 1.1 is now complete. Moving on to task 1.2...
```

**Example of INCORRECT sync** (split across messages):

```markdown
MESSAGE 1:
I've completed the User model.

[TodoWrite tool call marking completed]

MESSAGE 2 (later):
Let me also update the markdown file...

[Edit tool call updating markdown]
```

❌ This creates a window where systems are out of sync.

## Visual Sync Checklist

Before moving to next task, verify:

```
TodoWrite Status     Markdown Status     Synced?
─────────────────────────────────────────────────
pending             [ ]                 ✅ Yes
in_progress         [→] or note         ✅ Yes
completed           [x]                 ✅ Yes

pending             [x]                 ❌ NO - FIX!
completed           [ ]                 ❌ NO - FIX!
in_progress         [x]                 ❌ NO - FIX!
```

## Recovering From Desync

If you discover systems are out of sync:

**Step 1: Identify Ground Truth**
- Read the markdown file to see actual implementation state
- Check git history to see what was actually committed
- Determine which system has the accurate status

**Step 2: Update Both to Match Truth**

```markdown
I've detected that TodoWrite and markdown are out of sync. Let me fix this.

Based on the actual state of the code and commits, task 1.1 is complete
but task 1.2 is still pending.

Updating TodoWrite to match reality...
```

```json
{
  "todos": [
    {
      "content": "Create User model",
      "activeForm": "Creating User model",
      "status": "completed"
    },
    {
      "content": "Create migration file",
      "activeForm": "Creating migration file",
      "status": "pending"
    }
  ]
}
```

**And updating markdown file:**

```markdown
- [ ] 1.0 Set up authentication infrastructure
  - [x] 1.1 Create User model with authentication fields
  - [ ] 1.2 Create migration file for users table
```

**Step 3: Establish Sync Going Forward**
```markdown
Systems are now synchronized. Going forward, I'll update both in the same
response to prevent future desync.
```

## Common Mistakes and Fixes

### Mistake 1: Updating Only TodoWrite

**Wrong:**
```markdown
Completed task 1.1!

[TodoWrite tool call]

[Forgets to update markdown]
```

**Right:**
```markdown
Completed task 1.1!

[TodoWrite tool call]

[Edit tool call to update markdown]

Both systems updated.
```

### Mistake 2: Batching Updates

**Wrong:**
```markdown
Completed tasks 1.1, 1.2, and 1.3.

[TodoWrite tool call marking all three complete]

[Edit tool call updating markdown for all three]
```

**Right:**
```markdown
Completed task 1.1.

[TodoWrite tool call for 1.1]
[Edit tool call for 1.1]

Moving to 1.2...
[Work on 1.2]

Completed task 1.2.

[TodoWrite tool call for 1.2]
[Edit tool call for 1.2]

[Etc.]
```

### Mistake 3: Multiple Tasks In-Progress

**Wrong:**
```json
{
  "todos": [
    {"content": "Task 1.1", "status": "in_progress"},
    {"content": "Task 1.2", "status": "in_progress"}
  ]
}
```

**Right:**
```json
{
  "todos": [
    {"content": "Task 1.1", "status": "completed"},
    {"content": "Task 1.2", "status": "in_progress"}
  ]
}
```

Only ONE task should ever be `in_progress`.

## Best Practices

1. **Use consistent notation in markdown:**
   - `[ ]` = pending
   - `[→]` or `[ ] ... ← Currently working` = in_progress
   - `[x]` = completed

2. **Always announce updates:**
   ```markdown
   Updating task status to completed in both TodoWrite and markdown...
   ```

3. **Make both tool calls in same message:**
   - TodoWrite tool call
   - Edit tool call
   - No messages in between

4. **Verify after every update:**
   ```markdown
   ✅ Task 1.1 marked complete in TodoWrite
   ✅ Task 1.1 marked complete in markdown [x]
   ✅ Task 1.2 marked in_progress in TodoWrite
   ✅ Task 1.2 marked in_progress in markdown [→]
   ```

5. **Check ONE-in-progress rule:**
   After any status change, verify only one task is `in_progress`

## Quick Reference

**Every time you change task status:**

```
┌─────────────────────────────────────────┐
│ Same Agent Response:                    │
│                                         │
│ 1. [TodoWrite tool call]                │
│ 2. [Edit tool call to markdown]         │
│ 3. Verify both updated                  │
│                                         │
│ NO messages between tool calls          │
└─────────────────────────────────────────┘
```

**Forbidden:**
```
Response 1: Update TodoWrite
Response 2: Update markdown later     ← DON'T DO THIS
```

**Correct:**
```
Response 1: Update BOTH TodoWrite and markdown
```

---

**Remember:** Treat TodoWrite + Markdown as a **single atomic operation**. They are always updated together, in the same response, every time.

