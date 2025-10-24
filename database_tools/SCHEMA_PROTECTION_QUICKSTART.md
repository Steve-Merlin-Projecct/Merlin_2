---
title: "Schema Protection Quickstart"
type: technical_doc
component: database
status: draft
tags: []
---

# Database Schema Protection - Quick Start

## ✅ What's Implemented

The database schema protection system is **fully operational** in Claude Code using PreToolUse hooks.

## 🛡️ How It Works

**Automatic Protection**: Claude Code hooks intercept Edit/Write operations on protected files and block manual edits.

**Protected Files**:
- `frontend_templates/database_schema.html`
- `database_tools/docs/database_schema.json`
- `database_tools/docs/database_schema.md`
- `database_tools/generated/models.py`
- `database_tools/generated/schemas.py`
- `database_tools/generated/crud.py`
- `database_tools/generated/routes.py`

## 🔧 Required Workflow

When you need to modify the database schema:

```bash
# 1. Make changes to PostgreSQL database schema
# 2. Run automation
python database_tools/update_schema.py

# 3. Review and commit
git add .
git commit -m "Update database schema"
```

## 📋 Configuration Files

1. **Hook Script**: `database_tools/claude_schema_protection.py`
2. **Hook Config**: `.claude/settings.local.json`
3. **Automation**: `database_tools/enforce_automation.py`

## ✨ Key Features

- ✅ **Blocks Claude's direct edits** to protected files (via Edit/Write tools)
- ✅ **Allows Read operations** (viewing files is OK)
- ✅ **Automation scripts bypass hooks** (use Python I/O, not Claude tools)
- ✅ **Shows schema status** in error messages
- ✅ **Provides clear guidance** on what to do

## 🧠 How It Works

The hook **only sees Claude's tool calls**, not Python's file operations:

| Who/What | Method | Hook Intercepts? |
|----------|--------|------------------|
| Claude (direct) | Edit/Write tool | ✅ YES - Blocks it |
| Claude | Read tool | ✅ YES - Allows it |
| Claude | Bash tool | ✅ YES - Allows it |
| Python script | `open()` file I/O | ❌ NO - Bypasses entirely |

**Result**: Claude can't manually edit protected files, but automation scripts can.

## 🧪 Testing

Test the hook manually:

```bash
# Should BLOCK (edit to protected file)
echo '{
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "database_tools/generated/models.py"
  }
}' | python database_tools/claude_schema_protection.py

# Should ALLOW (read operation)
echo '{
  "tool_name": "Read",
  "tool_input": {
    "file_path": "database_tools/generated/models.py"
  }
}' | python database_tools/claude_schema_protection.py
```

## 📚 Full Documentation

See [Claude Code Schema Protection](../docs/development/CLAUDE_CODE_SCHEMA_PROTECTION.md) for complete details.

## 🔄 Migration from Replit

| Aspect | Replit | Claude Code |
|--------|--------|-------------|
| Method | Git pre-commit hooks | PreToolUse hooks |
| When | Before git commit | Before Claude's Edit/Write |
| Config | `.git/hooks/pre-commit` | `.claude/settings.local.json` |
| Scope | Blocks commits | Blocks tool calls only |

## ⚙️ Maintenance

### Add Protected File
Edit `database_tools/claude_schema_protection.py`:
```python
PROTECTED_FILES = [
    'your/new/file.py',  # Add here
    ...
]
```

**Note**: You don't need to whitelist automation scripts. They use Python `open()` which bypasses hooks entirely.

## 🚨 What You'll See

If you try to manually edit a protected file:

```
🛡️  DATABASE SCHEMA PROTECTION

❌ BLOCKED: Manual edit to auto-generated file
📁 File: database_tools/generated/models.py
🔧 Tool: Edit

⚠️  This file is auto-generated from the PostgreSQL schema.
   Manual edits will be overwritten and cause inconsistencies.

✅ REQUIRED WORKFLOW:
   1. Make changes to PostgreSQL database schema
   2. Run: python database_tools/update_schema.py
   3. Review and commit generated files

📊 SCHEMA STATUS: Up to date
```

---

**Status**: ✅ Active and Protecting
**Last Updated**: 2025-10-06
**Environment**: Claude Code
