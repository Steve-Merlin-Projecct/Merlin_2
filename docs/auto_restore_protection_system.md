# Auto-Restore Protection System

## Overview

The auto-restore protection system automatically detects and reverts unauthorized changes made by the agent to the protected section of `replit.md`. It acts as an automated guardian for critical configuration content.

## How It Works

1. **Monitoring**: Continuously monitors `replit.md` for changes
2. **Detection**: Identifies when the agent modifies content between protection tags
3. **Restoration**: Automatically reverts changes using a reference file
4. **Logging**: Records all protection actions in the changelog

## Protection Tags

The protected section is defined by these HTML comments:
- Start: `<!-- critical: do not change anything below this line -->`
- End: `<!-- critical: do not change anything above this line -->`

## Components

### Core Files
- **`tools/monitor_replit_md.py`**: Main monitoring script with auto-restore functionality
- **`tools/protected_replit_content.md`**: Reference file containing the correct protected content
- **`tools/test_auto_restore_protection.py`**: Test script to verify auto-restore functionality

### Generated Files
- **`docs/changelogs/replit-md_changelog.md`**: Change log with auto-restore actions
- **`docs/changelogs/.replit_md_hash`**: File integrity tracking

## Usage

### Manual Commands
```bash
# Run protection check
python tools/monitor_replit_md.py restore

# Check for changes (includes automatic auto-restore)
python tools/monitor_replit_md.py check

# Continuous monitoring
python tools/monitor_replit_md.py watch

# Test the system
python tools/test_auto_restore_protection.py
```

### Automatic Operation
- Auto-restore runs automatically when agent changes are detected
- No user intervention required
- Actions are logged for transparency

## Entity Tracking

The system tracks three entities:
- **`replit-agent`**: Changes made by the AI agent
- **`auto-restore-protection`**: Automated restorations by auto-restore system
- **`user`**: Manual changes by the human user

## File Protection Options

### Available Protection Methods

1. **Reference File Protection** (Current Implementation)
   - ✅ **Implemented**: Uses `tools/protected_replit_content.md` as reference
   - ✅ **Effective**: Works in Replit environment
   - ✅ **Flexible**: Easy to update protected content

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

The **reference file method** is the most practical solution for the Replit environment:
- Works with current permissions
- Easy to maintain and update
- Transparent operation
- No system-level requirements

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

### Updating Protected Content
1. Edit `tools/protected_replit_content.md`
2. Run `python tools/monitor_replit_md.py check` to verify
3. Content will be used for future restorations

### Monitoring Health
- Check `docs/changelogs/replit-md_changelog.md` for activity
- Verify auto-restore actions are logged correctly
- Test system periodically with test script

## Limitations

1. **Reference Dependency**: Requires `tools/protected_replit_content.md` to exist
2. **Tag Dependency**: Protection tags must remain in place
3. **Agent Permissions**: Cannot prevent agent from modifying the reference file itself
4. **Real-time**: Only acts after changes are detected, not preventively

## Future Enhancements

1. **Multiple Protected Sections**: Support for multiple protected areas
2. **Granular Protection**: Protect specific lines rather than entire sections
3. **Whitelist System**: Allow certain types of agent modifications
4. **Notification System**: Alert users when auto-restore actions occur