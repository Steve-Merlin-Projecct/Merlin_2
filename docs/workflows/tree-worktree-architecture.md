# /tree Worktree Architecture

**Purpose**: Understanding the `.trees/` directory structure and why it's gitignored

---

## 📂 Directory Structure

```
/workspace/
├── .git/                          # Main git repository
├── .trees/                        # Worktree workspace (GITIGNORED)
│   ├── .staged-features.txt       # Pending feature plans
│   ├── .completed/                # Finished worktree synopsis files
│   ├── .archived/                 # Historical completion records
│   ├── .conflict-backup/          # Merge conflict backups
│   ├── dashboard-completion/      # Active worktree directory
│   ├── user-preferences/          # Active worktree directory
│   └── launch-all-claude.sh       # Helper scripts
├── .claude/
│   └── scripts/
│       └── tree.sh                # /tree command implementation
└── tasks/
    └── prd-tree-slash-command.md  # PRD documentation
```

---

## 🎯 What is `.trees/`?

The `.trees/` directory is a **local workspace management system** for git worktrees. It provides:

1. **Feature Staging Area**: Plan multiple worktrees before creating them
2. **Worktree Storage**: Houses git worktree working directories
3. **Completion Tracking**: Stores synopsis files from finished work
4. **Conflict Resolution**: Backup files during merge conflicts
5. **Workflow Automation**: Scripts and state files for the `/tree` system

---

## 🚫 Why Is It Gitignored?

### **1. Temporary/Ephemeral Data**

`.staged-features.txt` is a planning scratchpad:
```
# Example staging file
dashboard-completion:Fix database and add analytics view
user-preferences:Backend logic and job matching algorithm
```

- **Purpose**: Temporary planning before worktree creation
- **Lifecycle**: Created → Used → Cleared after build
- **Why Not Commit**: Different developers plan different features

### **2. Worktree Directories Are Git Repositories**

```bash
.trees/dashboard-completion/  # This is a git worktree
├── .git                      # Points to main repo
├── app_modular.py           # Working files
└── modules/
```

- **Problem**: Git can't track git repos inside git repos
- **Solution**: The worktree's CHANGES get committed (when merged), not the worktree itself
- **Analogy**: Like a build directory - the output is committed, not the build artifacts

### **3. Machine-Specific Paths**

Worktree metadata contains local paths:
```
# .git/worktrees/dashboard-completion/gitdir
/workspace/.trees/dashboard-completion/.git
```

- **Issue**: Paths differ per machine/developer
- **Solution**: Each developer manages their own `.trees/` locally

### **4. Workflow State, Not Source Code**

`.completed/` synopsis files are temporary:
```
.trees/.completed/
└── dashboard-completion-synopsis-20251010.md
```

- **Purpose**: Handoff documentation between worktree and main
- **Lifecycle**: Created at worktree close → Used for merge → Archived
- **Why Not Commit**: The actual code changes are what matters, not the handoff notes

---

## ✅ What DOES Get Committed?

### **From Worktrees:**
- ✅ Actual code changes (when merged to main/develop)
- ✅ New features implemented
- ✅ Documentation updates
- ✅ Test files

### **From `/tree` System:**
- ✅ `/tree` command script (`.claude/scripts/tree.sh`)
- ✅ PRD documentation (`tasks/prd-tree-slash-command.md`)
- ✅ Architecture docs (this file!)
- ✅ Workflow guides

---

## 🔄 Workflow Lifecycle

### **1. Planning Phase** (`.staged-features.txt`)
```bash
/tree stage Add user preferences
/tree stage Dashboard completion
/tree list  # Review staged features
```
**State**: Local planning file, not committed

### **2. Build Phase** (Worktree directories)
```bash
/tree build  # Creates worktrees in .trees/
```
**State**: Working directories created, isolated branches

### **3. Development Phase** (Inside worktrees)
```bash
cd .trees/user-preferences
# Make changes, commit to feature branch
git add . && git commit -m "Add user preferences API"
```
**State**: Changes committed to feature branch (tracked by git)

### **4. Completion Phase** (Synopsis generation)
```bash
/tree close  # Generates synopsis in .completed/
```
**State**: Temporary handoff doc, not committed

### **5. Merge Phase** (Integration to main)
```bash
/tree closedone  # Merges all completed worktrees
```
**State**:
- ✅ Code changes merged to main (COMMITTED)
- ✅ Worktree removed from `.trees/` (DELETED)
- ✅ Synopsis moved to `.archived/` (LOCAL ONLY)

---

## 📊 Comparison: What's Tracked vs. What's Not

| Item | Location | Git Tracked? | Why/Why Not |
|------|----------|--------------|-------------|
| **Staging plans** | `.trees/.staged-features.txt` | ❌ No | Temporary planning scratchpad |
| **Worktree directories** | `.trees/feature-name/` | ❌ No | Git repos can't contain git repos |
| **Code changes in worktree** | Feature branch | ✅ Yes | The actual work - tracked on branch |
| **Merged code** | Main/develop branch | ✅ Yes | Final integrated code |
| **Synopsis files** | `.trees/.completed/` | ❌ No | Temporary handoff docs |
| **Conflict backups** | `.trees/.conflict-backup/` | ❌ No | Temporary merge resolution files |
| **/tree command** | `.claude/scripts/tree.sh` | ✅ Yes | Tool itself is source code |
| **PRD docs** | `tasks/prd-*.md` | ✅ Yes | Design documentation |

---

## 🏗️ Analogy: Build System

Think of `.trees/` like a build system:

### **Source Code (Committed)**
```
src/
├── app.py
├── models.py
└── utils.py
```

### **Build Directory (Gitignored)**
```
build/
├── temp_files/
├── intermediate_objects/
└── build_logs.txt
```

### **Build Output (Committed)**
```
dist/
└── app.exe  # Or deployed code
```

**Similarly for `/tree`:**

| Build System | /tree System |
|--------------|--------------|
| `src/` | Main git branches (main, develop) |
| `build/` | `.trees/` directory |
| `dist/` | Merged code in main branch |
| Build artifacts | Worktree scaffolding |
| Final binary | Integrated feature code |

---

## 🔐 Security Considerations

**Why gitignoring `.trees/` is important:**

1. **Credentials**: Worktrees might temporarily contain API keys during development
2. **Local Paths**: Could expose system structure
3. **Work-in-Progress**: Incomplete features shouldn't be in main repo
4. **Backup Files**: May contain sensitive merge conflict data

---

## 🎯 Design Principles

The `.trees/` architecture follows these principles:

### **1. Separation of Concerns**
- **Planning** (staging) ≠ **Execution** (worktrees) ≠ **Integration** (merging)
- Each phase has its own storage

### **2. Local-First Workflow**
- Developers manage their own worktree workspace
- No coordination needed for personal planning

### **3. Clean Git History**
- Only final, merged code in git history
- No workflow scaffolding clutter

### **4. Ephemeral State**
- Temporary files are automatically cleaned up
- Only permanent artifacts (code) are kept

---

## 🛠️ Advanced: When You MIGHT Want to Track `.trees/`

**Generally don't, but consider if:**

❓ **Scenario**: Team wants shared worktree templates
- **Solution**: Create separate `worktree-templates/` directory (committed)
- **Keep**: `.trees/` still gitignored for actual instances

❓ **Scenario**: Want to backup staging plans
- **Solution**: Use `/tree list` to export, save to `tasks/planned-features.md`
- **Keep**: `.trees/.staged-features.txt` gitignored

❓ **Scenario**: Need to share synopsis files
- **Solution**: Copy important ones to `docs/handoffs/` before archiving
- **Keep**: `.trees/.completed/` gitignored

---

## 📚 Related Documentation

- **PRD**: `tasks/prd-tree-slash-command.md` - Full specification
- **Implementation**: `.claude/scripts/tree.sh` - Command source code
- **Usage**: Run `/tree help` for command reference

---

## ✅ Summary

**`.trees/` is gitignored because:**

1. ✅ It's **workflow state**, not source code
2. ✅ Worktree directories are **separate git repos**
3. ✅ Paths are **machine-specific**
4. ✅ Files are **temporary/ephemeral**
5. ✅ The **real work** (code changes) is tracked on feature branches

**What matters in git:**
- 📝 The code you write in worktrees (committed on branches)
- 🔀 The merged code in main/develop (permanent)
- 🛠️ The tools themselves (`/tree` command, PRDs)
- 📖 The documentation you create

**`.trees/` is your personal workshop - the products of that workshop (code) are what you ship.**

---

*Last Updated: October 10, 2025*
*Part of the /tree Worktree Management System*
