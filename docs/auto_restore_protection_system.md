---
title: "Auto Restore Protection System"
type: technical_doc
component: general
status: draft
tags: []
---

# Auto-Restore Protection System

## Overview

The auto-restore protection system automatically detects and reverts unauthorized changes made by the agent to the protected section of `CLAUDE.md`. It acts as an automated guardian for critical configuration content.

**Note:** This system was migrated from the Replit environment and updated for Claude Code in October 2025.

## How It Works

1. **Monitoring**: Continuously monitors `CLAUDE.md` for changes using SHA256 hashing
2. **Detection**: Identifies when the agent modifies content between protection tags
3. **Restoration**: Automatically reverts changes using a reference file
4. **Logging**: Records all protection actions in the changelog with detailed diffs

## Protection Tags

The protected section is defined by these HTML comments:
- Start: `<!-- critical: do not change anything below this line -->`
- End: `<!-- critical: do not change anything above this line -->`

## Components

### Core Files
- **`tools/monitor_claude_md.py`**: Main monitoring script with full change tracking and auto-restore integration
- **`tools/auto_restore_protection.py`**: Auto-restore protection system that detects and reverts unauthorized changes
- **`tools/sync_protected_content.py`**: Syncs user-made changes to the protected reference file
- **`tools/protected_claude_content.md`**: Reference file containing the correct protected content
- **`tools/test_auto_restore_protection.py`**: Test script to verify auto-restore functionality

### Generated Files
- **`docs/changelogs/claude-md_changelog.md`**: Change log with auto-restore actions and detailed diffs
- **`docs/changelogs/.claude_md_hash`**: File integrity tracking using SHA256

## Usage

### Manual Commands
```bash
# Initialize the monitoring system
python tools/monitor_claude_md.py init

# Run protection check
python tools/monitor_claude_md.py restore

# Check for changes (includes automatic auto-restore)
python tools/monitor_claude_md.py check

# Continuous monitoring (runs in foreground)
python tools/monitor_claude_md.py watch

# Sync user changes to protected reference
python tools/sync_protected_content.py sync

# Force sync (regardless of who made changes)
python tools/sync_protected_content.py force

# Test the complete system
python tools/test_auto_restore_protection.py
```

### Automatic Operation
- Auto-restore runs automatically when agent changes are detected
- No user intervention required
- Actions are logged for transparency

## Entity Tracking

The system tracks four entities:
- **`claude-agent`**: Changes made by the AI agent (Claude Code)
- **`auto-restore-protection`**: Automated restorations by the auto-restore system
- **`content-syncer`**: Reference file updates from user changes
- **`user`**: Manual changes by the human user

## File Protection Options

### Available Protection Methods

1. **Reference File Protection** (Current Implementation)
   - ✅ **Implemented**: Uses `tools/protected_claude_content.md` as reference
   - ✅ **Effective**: Works in Claude Code and standard development environments
   - ✅ **Flexible**: Easy to update protected content
   - ✅ **Portable**: No platform-specific dependencies

2. **File Permissions** (Limited in Replit)
   - ❌ **Not viable**: Agent runs with same permissions as user
   - ❌ **Bypassable**: Agent can change permissions if needed
   
3. **File Attributes** (Requires root access)
   ```bash
   # Would require root access (not available in Replit)
   chattr +i tools/protected_replit_content.md  # Make immutable
   chattr -i tools/protected_replit_content.md  # Remove immutability
   ```

4. **Git Hooks** (Complex implementation)
   - ⚠️ **Complex**: Requires git hook setup
   - ⚠️ **Limited**: Only prevents commits, not file changes

### Recommended Approach

The **reference file method** is the most practical solution for development environments:
- Works with standard file permissions
- Easy to maintain and update
- Transparent operation
- No system-level or root requirements
- Platform-agnostic (works on Linux, macOS, Windows)

## Testing

Run the test suite to verify functionality:
```bash
python tools/test_auto_restore_protection.py
```

The test script:
1. Simulates agent modifications to protected content
2. Verifies auto-restore detection and restoration
3. Tests non-protected content handling
4. Validates change detection system

## Security Features

- **Selective Action**: Only acts on agent modifications
- **Section-Specific**: Only protects designated critical sections
- **Audit Trail**: All actions logged with timestamps
- **Non-Destructive**: Backs up content before restoration
- **Entity Attribution**: Distinguishes between user, agent, and auto-restore changes

## Maintenance

### Updating Protected Content (User Changes)
1. Edit the protected section directly in `CLAUDE.md` (between the critical tags)
2. Run `python tools/sync_protected_content.py sync` to update the reference file
3. The reference file will be automatically used for future restorations

### Updating Protected Content (Manual)
1. Edit `tools/protected_claude_content.md` directly
2. Run `python tools/monitor_claude_md.py check` to verify
3. Content will be used for future restorations

### Monitoring Health
- Check `docs/changelogs/claude-md_changelog.md` for activity
- Verify auto-restore actions are logged correctly with timestamps
- Test system periodically: `python tools/test_auto_restore_protection.py`
- Monitor hash file: `docs/changelogs/.claude_md_hash`

## Limitations

1. **Reference Dependency**: Requires `tools/protected_claude_content.md` to exist
2. **Tag Dependency**: Protection tags in CLAUDE.md must remain in place
3. **Agent Permissions**: Cannot prevent agent from modifying the reference file itself (though agent should be instructed not to)
4. **Real-time**: Only acts after changes are detected, not preventively
5. **Entity Detection**: Currently uses simplified entity detection; can be enhanced with git integration

## Future Enhancements

1. **Multiple Protected Sections**: Support for multiple protected areas with different policies
2. **Granular Protection**: Protect specific lines or patterns rather than entire sections
3. **Whitelist System**: Allow certain types of agent modifications with approval
4. **Notification System**: Desktop/email alerts when auto-restore actions occur
5. **Git Integration**: Enhanced entity detection using git authorship
6. **Pre-commit Hook**: Automatic validation before commits
7. **VS Code Extension**: Real-time protection indicator in the editor
8. **Diff Viewer**: Web interface to review all changes with syntax highlighting

---

## Migration Notes (October 2025)

This system was successfully migrated from Replit to Claude Code with the following changes:
- Renamed `replit.md` → `CLAUDE.md`
- Updated `monitor_replit_md.py` → `monitor_claude_md.py`
- Updated reference file: `protected_replit_content.md` → `protected_claude_content.md`
- Updated changelog: `replit-md_changelog.md` → `claude-md_changelog.md`
- Updated entity names: `replit-agent` → `claude-agent`
- All scripts and paths updated for new naming convention
- System tested and operational in Claude Code environment